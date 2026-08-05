import datetime
import logging

import opql.eval.expression.function
import opql.eval.expression.value
import opql.eval.querycontext
import opql.lang.query
import opql.ocel.ocellog
import opql.SQLITEResolver
from opql.exceptions import OPQLEvalError, OPQLTypeError

logger = logging.getLogger(__name__)

def get_all_objects(expr: opql.lang.query.Expression) -> list:
    if isinstance(expr, opql.lang.query.AtomicExpr):
        val = expr.value
        if (isinstance(val, opql.lang.query.ValueReference)
                and val.property is not None and val.timestamp is not None):
            return [val]
        return []
    if isinstance(expr, opql.lang.query.UnaryExpr):
        return get_all_objects(expr.operand)
    if isinstance(expr, opql.lang.query.BinaryExpr):
        return get_all_objects(expr.left) + get_all_objects(expr.right)
    return []


def evaluate_expression(ocel, context, expr: opql.lang.query.Expression):
    if isinstance(expr, opql.lang.query.AtomicExpr):
        return _evaluate_atomic(ocel, context, expr)

    if isinstance(expr, opql.lang.query.UnaryExpr):
        val = evaluate_expression(ocel, context, expr.operand)
        if expr.op == 'NOT':
            return not val
        if expr.op == '-':
            return -val
        return val  # unary '+'

    if isinstance(expr, opql.lang.query.BinaryExpr):
        op = expr.op

        # short-circuit boolean operators
        if op == 'AND':
            lval = evaluate_expression(ocel, context, expr.left)
            if not lval:
                return False
            return bool(evaluate_expression(ocel, context, expr.right))

        if op == 'OR':
            lval = evaluate_expression(ocel, context, expr.left)
            if lval:
                return True
            return bool(evaluate_expression(ocel, context, expr.right))

        lval = evaluate_expression(ocel, context, expr.left)
        rval = evaluate_expression(ocel, context, expr.right)

        if op == 'XOR':
            return bool(lval) != bool(rval)

        if op == '+':
            return lval + rval
        if op == '-':
            return lval - rval
        if op == '*':
            return lval * rval
        if op == '/':
            return lval / rval
        if op == '%':
            return lval % rval
        if op == '^':
            return lval ** rval

        # comparison operators
        if lval is None or rval is None:
            return None
        if not (isinstance(lval, type(rval))
                or (isinstance(lval, int | float) and isinstance(rval, int | float))):
            raise OPQLTypeError(f"Cannot compare {type(lval).__name__} and {type(rval).__name__}")
        if op == '==':
            return lval == rval
        if op == '!=':
            return lval != rval
        if op == '<':
            return lval < rval
        if op == '>':
            return lval > rval
        if op == '<=':
            return lval <= rval
        if op == '>=':
            return lval >= rval

        raise OPQLEvalError(f"Unknown binary operator: {op!r}")

    raise OPQLEvalError(f"Unknown expression type: {type(expr).__name__}")


def _evaluate_atomic(ocel, context, atom: opql.lang.query.AtomicExpr):
    val = atom.value

    if isinstance(val, str | int | float | bool | datetime.datetime | datetime.timedelta):
        return val

    if val is None:
        return None

    if isinstance(val, opql.lang.query.ValueReference):
        result = opql.eval.expression.value.get_value(ocel, context, val)

        if isinstance(result, opql.lang.query.FullQuery):
            result = opql.SQLITEResolver.resolve_query(
                ocel, result, root_context=opql.eval.querycontext.QueryContext())
        
        return result

    if isinstance(val, opql.lang.query.FullQuery):
        return opql.SQLITEResolver.resolve_query(
            ocel, val, root_context=opql.eval.querycontext.QueryContext())

    if isinstance(val, opql.lang.query.FullQuery):
        return val

    if isinstance(val, opql.lang.query.Function):
        args = []
        for f_arg in val.arguments:
            if isinstance(f_arg.arg, opql.lang.query.Expression):
                arg_val = evaluate_expression(ocel, context, f_arg.arg)
                if isinstance(arg_val, opql.lang.query.FullQuery):
                    arg_val = opql.SQLITEResolver.resolve_query(
                        ocel, arg_val.query, root_context=opql.eval.querycontext.QueryContext())
                args.append(arg_val)
            elif isinstance(f_arg.arg, opql.lang.query.FullQuery):
                subquery: opql.lang.query.FullQuery = f_arg.arg
                if len(subquery.return_rule.projection.ctx_expansions) != 1:
                    raise OPQLEvalError("Subquery passed as function argument must return exactly one column")
                subquery_dataframe = opql.SQLITEResolver.resolve_query(
                    ocel, subquery, root_context=context)
                args.append(subquery_dataframe)
            else:
                raise OPQLEvalError(f"Unknown function argument type: {type(f_arg.arg).__name__}")
        return opql.eval.expression.function.evaluate_function(
            ocel, context, val.name, args)

    raise OPQLEvalError(f"Failed to determine value of {val!r}")


# alias used by callers that still reference evaluate_graphexpression
evaluate_graphexpression = evaluate_expression
