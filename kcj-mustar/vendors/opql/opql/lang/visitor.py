import datetime
import logging

import opql.lang.query
import opql.util
from opql.exceptions import OPQLParseError
from opql.lang.grammar.OPQLParser import OPQLParser
from opql.lang.grammar.OPQLVisitor import OPQLVisitor

logger = logging.getLogger(__name__)


class Visitor(OPQLVisitor):
    def __init__(self):
        self.running_event_id = opql.util.RunningId("__ev", 0)
        self.running_object_id = opql.util.RunningId("__ob", 0)
        self.running_relation_id = opql.util.RunningId("__rel", 0)
        self.running_graph_id = opql.util.RunningId("__gr", 0)

    # Visit a parse tree produced by OPQLParser#r_EO_PROPERTY.
    def visitR_eoProperty(self, ctx:OPQLParser.R_eoPropertyContext):
        valref = opql.lang.query.ValueReference()
        valref.name = ctx.SYMBOLICNAME().getText()
        valref.property = ctx.STRING().getText()[1:-1]

        if ctx.r_propertyTimestamp():
            valref.timestamp = self.visitR_propertyTimestamp(ctx.r_propertyTimestamp())

        return valref

    def visitR_duration(self, ctx:OPQLParser.R_durationContext):
        days = int(ctx.INT(0).getText())
        hours = int(ctx.INT(1).getText())
        minutes = int(ctx.INT(2).getText())

        seconds = 0
        if ctx.FLOAT():
            seconds = float(ctx.FLOAT().getText())
        elif ctx.INT(3):
            seconds = int(ctx.INT(3).getText())
        else:
            logger.warning("Failed to parse seconds in duration literal; defaulting to 0")

        rv = datetime.timedelta(days=days,hours=hours,minutes=minutes,seconds=seconds)
        return rv


    # Visit a parse tree produced by OPQLParser#r_TIMESTAMP.
    def visitR_timestamp(self, ctx:OPQLParser.R_timestampContext):
        time_stamp = ctx.STRING().getText()[1:-1]
        try:
            rv = datetime.datetime.strptime(time_stamp, "%Y-%m-%dT%H:%M:%S.%f%z")
        except ValueError:
            rv = datetime.datetime.strptime(time_stamp, "%Y-%m-%dT%H:%M:%S%z")
        return rv

    # Visit a parse tree produced by OPQLParser#r_PROPERTYTIMESTAMP.
    def visitR_propertyTimestamp(self, ctx:OPQLParser.R_propertyTimestampContext):
        # reference to some event
        if ctx.SYMBOLICNAME():
            return ctx.SYMBOLICNAME().getText()

        # if not a symbolic name, try to parse datetime from string
        if ctx.r_timestamp():
            timestamp = self.visitR_timestamp(ctx.r_timestamp())

            return timestamp

        raise OPQLParseError("Failed to parse property timestamp")

    # Visit a parse tree produced by OPQLParser#r_RV_FUNCTION_ARG.
    def visitR_rvFunctionArg(self, ctx:OPQLParser.R_rvFunctionArgContext):
        f_arg = opql.lang.query.FunctionArgument()
        if ctx.r_expression():
            f_arg.arg = self.visitR_expression(ctx.r_expression())
        elif ctx.r_fullquery():
            f_arg.arg = self.visitR_fullquery(ctx.r_fullquery())

        return f_arg

    # Visit a parse tree produced by OPQLParser#r_RV_FUNCTION.
    def visitR_rvFunctionCall(self, ctx:OPQLParser.R_rvFunctionCallContext):
        queryfunction = opql.lang.query.Function()
        queryfunction.name = ctx.SYMBOLICNAME().getText()
        queryfunction.arguments = [self.visitR_rvFunctionArg(f_arg) for f_arg in ctx.r_rvFunctionArg()]

        return queryfunction

    def visitR_patternRule(self, ctx:OPQLParser.R_patternRuleContext):
        graph = opql.lang.query.Graph()
        graph.patterns = self.visitR_graphPatternList(ctx.r_graphPatternList())

        # if ctx.SYMBOLICNAME():
        #     graph.tag = ctx.SYMBOLICNAME().getText()

        if ctx.r_propositionalRule():
            graph.filter = self.visitR_propositionalRule(ctx.r_propositionalRule())

        return graph

    def visitR_constantBool(self, ctx:OPQLParser.R_constantBoolContext):
        if ctx.getText() == "True":
            return True
        if ctx.getText() == "False":
            return False

        raise OPQLParseError(f"Unrecognized boolean literal: {ctx.getText()!r}")

    # Visit a parse tree produced by OPQLParser#r_VALUE_TYPE.
    def visitR_valueType(self, ctx:OPQLParser.R_valueTypeContext):
        if ctx.r_eoProperty():
            return self.visitR_eoProperty(ctx.r_eoProperty())

        if ctx.r_timestamp():
            return self.visitR_timestamp(ctx.r_timestamp())

        if ctx.r_duration():
            return self.visitR_duration(ctx.r_duration())

        if ctx.STRING():
            return ctx.STRING().getText()[1:-1]

        # r_valueType : (r_eoProperty | r_int | r_constantBool | NONE_TKN
        if ctx.r_constantBool():
            return self.visitR_constantBool(ctx.r_constantBool())

        if ctx.NONE_TKN():
            return None

        if ctx.SYMBOLICNAME():
            val_ref = opql.lang.query.ValueReference()
            val_ref.name = ctx.SYMBOLICNAME().getText()
            return val_ref

        if ctx.INT():
            return int(ctx.INT().getText())

        if ctx.FLOAT():
            return float(ctx.FLOAT().getText())

        if ctx.r_rvFunctionCall():
            return self.visitR_rvFunctionCall(ctx.r_rvFunctionCall())

        raise OPQLParseError(f"Failed to parse value type: {ctx.getText()!r}")

    def visitR_cte(self, ctx:OPQLParser.R_cteContext):
        tag = None
        if ctx.SYMBOLICNAME():
            tag = ctx.SYMBOLICNAME().getText()

        evaluatable = self.visitR_subquery(ctx.r_subquery())

        return tag, evaluatable

    def visitR_subquery(self, ctx:OPQLParser.R_subqueryContext):
        cte = opql.lang.query.SubQuery()

        if ctx.NOT_MATERIALIZED_TKN():
            cte.materialized = False
        else:
            cte.materialized = True

        cte.query = self.visitR_fullquery(ctx.r_fullquery())

        return cte

    # r_expression dispatch — ANTLR does not generate a base visitR_expression when
    # labeled alternatives are used; callers go through self.visit(ctx) which
    # dispatches to the correct visitR_ex* method.
    def visitR_expression(self, ctx):
        return self.visit(ctx)

    def visitR_exUnary(self, ctx: OPQLParser.R_exUnaryContext):
        op = '+' if ctx.PLUS() else '-'
        operand = self.visit(ctx.r_expression())
        return opql.lang.query.UnaryExpr(op, operand)

    def visitR_exPower(self, ctx: OPQLParser.R_exPowerContext):
        left = self.visit(ctx.r_expression(0))
        right = self.visit(ctx.r_expression(1))
        return opql.lang.query.BinaryExpr('^', left, right)

    def visitR_exMulDiv(self, ctx: OPQLParser.R_exMulDivContext):
        left = self.visit(ctx.r_expression(0))
        right = self.visit(ctx.r_expression(1))
        if ctx.ASTERISK():
            op = '*'
        elif ctx.DIV():
            op = '/'
        else:
            op = '%'
        return opql.lang.query.BinaryExpr(op, left, right)

    def visitR_exAddSub(self, ctx: OPQLParser.R_exAddSubContext):
        left = self.visit(ctx.r_expression(0))
        right = self.visit(ctx.r_expression(1))
        op = '+' if ctx.PLUS() else '-'
        return opql.lang.query.BinaryExpr(op, left, right)

    def visitR_exCompare(self, ctx: OPQLParser.R_exCompareContext):
        left = self.visit(ctx.r_expression(0))
        right = self.visit(ctx.r_expression(1))
        op = self.visitR_compareSign(ctx.r_compareSign())
        return opql.lang.query.BinaryExpr(op, left, right)

    def visitR_exNot(self, ctx: OPQLParser.R_exNotContext):
        operand = self.visit(ctx.r_expression())
        return opql.lang.query.UnaryExpr('NOT', operand)

    def visitR_exAnd(self, ctx: OPQLParser.R_exAndContext):
        left = self.visit(ctx.r_expression(0))
        right = self.visit(ctx.r_expression(1))
        return opql.lang.query.BinaryExpr('AND', left, right)

    def visitR_exXor(self, ctx: OPQLParser.R_exXorContext):
        left = self.visit(ctx.r_expression(0))
        right = self.visit(ctx.r_expression(1))
        return opql.lang.query.BinaryExpr('XOR', left, right)

    def visitR_exOr(self, ctx: OPQLParser.R_exOrContext):
        left = self.visit(ctx.r_expression(0))
        right = self.visit(ctx.r_expression(1))
        return opql.lang.query.BinaryExpr('OR', left, right)

    def visitR_exGrouped(self, ctx: OPQLParser.R_exGroupedContext):
        return self.visit(ctx.r_expression())

    def visitR_exAtomic(self, ctx: OPQLParser.R_exAtomicContext):
        value = self.visitR_valueType(ctx.r_valueType())
        return opql.lang.query.AtomicExpr(value)

    def visitR_compareSign(self, ctx: OPQLParser.R_compareSignContext):
        if ctx.EQUAL_TO():
            return '=='
        if ctx.LE():
            return '<='
        if ctx.GE():
            return '>='
        if ctx.GT():
            return '>'
        if ctx.LT():
            return '<'
        if ctx.NOT_EQUAL():
            return '!='
        raise OPQLParseError(f"Unrecognized comparison operator: {ctx.getText()!r}")

    def visitR_propositionalRule(self, ctx:OPQLParser.R_propositionalRuleContext):
        if ctx.r_expression():
            return self.visitR_expression(ctx.r_expression())

        return None

    def visitR_returnRule(self, ctx:OPQLParser.R_returnRuleContext):
        ret_rule = opql.lang.query.Return()

        if ctx.OCEL_TKN():
            ret_rule.ocel = True
            return ret_rule

        if ctx.r_projection():
            ret_rule.projection = self.visitR_projection(ctx.r_projection())

        if not ctx.r_projection():
            raise OPQLParseError("RETURN statement requires a projection or OCEL token")

        if ctx.r_propositionalRule():
            ret_rule.filter = self.visitR_propositionalRule(ctx.r_propositionalRule())

        return ret_rule

    # Visit a parse tree produced by OPQLParser#r_FILTER_RULE.
    def visitR_filterRule(self, ctx:OPQLParser.R_filterRuleContext):
        filter_s = opql.lang.query.Filter()
        filter_s.entities_to_remove = [symname_ctx.getText() for symname_ctx in ctx.SYMBOLICNAME()]
        return filter_s

    def visitR_whenRule(self, ctx:OPQLParser.R_whenRuleContext):
        when_s = opql.lang.query.When()
        when_s.expression = self.visitR_expression(ctx.r_expression())

        when_s.name = ctx.SYMBOLICNAME().getText()

        if ctx.r_propositionalRule():
            when_s.filter = self.visitR_propositionalRule(ctx.r_propositionalRule())

        return when_s


    # Visit a parse tree produced by OPQLParser#r_SNAME.
    def visitR_sname(self, ctx:OPQLParser.R_snameContext):
        tag = None
        if ctx.SYMBOLICNAME():
            tag = ctx.SYMBOLICNAME().getText()
        evaluatable = self.visitR_expression(ctx.r_expression())

        return tag, evaluatable

    # Visit a parse tree produced by OPQLParser#r_ORDER_ITEM.
    def visitR_orderItem(self, ctx:OPQLParser.R_orderItemContext):
        oi = opql.lang.query.OrderItem()
        oi.expression = self.visitR_expression(ctx.r_expression())
        oi.direction = None
        if ctx.ASC_TKN():
            oi.direction = opql.lang.query.OrderDirection.ASC
        if ctx.DESC_TKN():
            oi.direction = opql.lang.query.OrderDirection.DESC

        return oi

    # Visit a parse tree produced by OPQLParser#r_ORDER.
    def visitR_order(self, ctx:OPQLParser.R_orderContext):
        return [self.visitR_orderItem(oi_ctx) for oi_ctx in ctx.r_orderItem()]

    # Visit a parse tree produced by OPQLParser#r_LIMIT.
    def visitR_limit(self, ctx:OPQLParser.R_limitContext):
        return int(ctx.INT().getText())

    # Visit a parse tree produced by OPQLParser#r_INTERVAL_LIMIT.
    def visitR_intervalLimit(self, ctx:OPQLParser.R_intervalLimitContext):
        if ctx.NEG_INF_TKN():
            return opql.lang.query.BinningInfinity.NEGATIVE_INFINITY

        if ctx.POS_INF_TKN():
            return opql.lang.query.BinningInfinity.POSITIVE_INFINITY

        if ctx.FLOAT():
            return float(ctx.FLOAT().getText())

        if ctx.INT():
            return int(ctx.INT().getText())

        raise OPQLParseError(f"Failed to parse interval limit: {ctx.getText()!r}")

    # Visit a parse tree produced by OPQLParser#r_INTERVAL_TARGET.
    def visitR_intervalTarget(self, ctx:OPQLParser.R_intervalTargetContext):
        if ctx.FLOAT():
            return float(ctx.FLOAT().getText())
        if ctx.INT():
            return int(ctx.INT().getText())
        if ctx.STRING():
            return ctx.getText()[1:-1]

        raise OPQLParseError(f"Failed to parse interval target: {ctx.getText()!r}")

    # Visit a parse tree produced by OPQLParser#r_BIN_INTERVAL.
    def visitR_binningInterval(self, ctx:OPQLParser.R_binningIntervalContext):
        bin_int = opql.lang.query.BinningInterval()
        bin_int.include_begin = bool(ctx.LEFT_SBR())
        bin_int.include_end = bool(ctx.RIGHT_SBR())
        bin_int.begin = self.visitR_intervalLimit(ctx.r_intervalLimit(0))
        bin_int.end = self.visitR_intervalLimit(ctx.r_intervalLimit(1))
        bin_int.target = self.visitR_intervalTarget(ctx.r_intervalTarget())
        return bin_int

    # Visit a parse tree produced by OPQLParser#r_BINNING.
    def visitR_binning(self, ctx:OPQLParser.R_binningContext):
        return [self.visitR_binningInterval(bin_interval) for bin_interval in ctx.r_binningInterval()]

    # Visit a parse tree produced by OPQLParser#r_PROJECTION_ITEM.
    def visitR_projectionItem(self, ctx:OPQLParser.R_projectionItemContext):
        #  r_cte | r_sname r_binning? ;
        pi = opql.lang.query.ProjectionItem()

        if ctx.r_sname():
            pi.tag, pi.evaluatable = self.visitR_sname(ctx.r_sname())
            if ctx.r_binning():
                pi.binning = self.visitR_binning(ctx.r_binning())
        elif ctx.r_cte():
            pi.tag, pi.evaluatable = self.visitR_cte(ctx.r_cte())

        return pi

    # Visit a parse tree produced by OPQLParser#r_PROJECTION.
    def visitR_projection(self, ctx:OPQLParser.R_projectionContext):
        projection = opql.lang.query.Projection()
        projection.wildcard = bool(ctx.ASTERISK())
        projection.distinct = bool(ctx.DISTINCT_TKN())
        projection.ctx_expansions = [self.visitR_projectionItem(pi_ctx) for pi_ctx in ctx.r_projectionItem()]

        if ctx.r_order():
            projection.order = self.visitR_order(ctx.r_order())

        if ctx.r_limit():
            projection.limit = self.visitR_limit(ctx.r_limit())

        return projection

    # Visit a parse tree produced by OPQLParser#r_KEEP_RULE.
    def visitR_keepRule(self, ctx:OPQLParser.R_keepRuleContext):
        keep_r = opql.lang.query.Keep()
        keep_r.projection = self.visitR_projection(ctx.r_projection())

        if ctx.r_propositionalRule():
            keep_r.filter = self.visitR_propositionalRule(ctx.r_propositionalRule())

        return keep_r

    # Visit a parse tree produced by OPQLParser#r_CONTEXT_RULE.
    def visitR_contextRule(self, ctx:OPQLParser.R_contextRuleContext):
        if ctx.r_patternRule():
            return self.visitR_patternRule(ctx.r_patternRule())
        elif ctx.r_filterRule():
            return self.visitR_filterRule(ctx.r_filterRule())
        elif ctx.r_keepRule():
            return self.visitR_keepRule(ctx.r_keepRule())
        elif ctx.r_whenRule():
            return self.visitR_whenRule(ctx.r_whenRule())
        else:
            raise OPQLParseError("Unknown clause type in context rule")

    def visitR_entryPoint(self, ctx:OPQLParser.R_entryPointContext):
        return self.visitR_fullquery(ctx.r_fullquery())

    # Visit a parse tree produced by OPQLParser#r_FULLQUERY.
    def visitR_fullquery(self, ctx: OPQLParser.R_fullqueryContext):
        fullquery: opql.lang.query.FullQuery = opql.lang.query.FullQuery()

        fullquery.graphsAndFilters = [self.visitR_contextRule(ctx_r) for ctx_r in ctx.r_contextRule()]
        fullquery.return_rule = self.visitR_returnRule(ctx.r_returnRule())
        return fullquery

    # Visit a parse tree produced by OPQLParser#r_GRAPH.
    def visitR_graph(self, ctx: OPQLParser.R_graphContext):
        resultlist = []

        if ctx.r_event():
            resultlist.append(self.visitR_event(ctx.r_event()))

        if ctx.r_object():
            resultlist.append(self.visitR_object(ctx.r_object()))

        if ctx.r_relationAny():
            resultlist.append(self.visitR_relationAny(ctx.r_relationAny()))
        elif ctx.r_relationLd():
            resultlist.append(self.visitR_relationLd(ctx.r_relationLd()))
        elif ctx.r_relationRd():
            resultlist.append(self.visitR_relationRd(ctx.r_relationRd()))

        graphctx = ctx.r_graph()
        if graphctx:
            resultlist.extend(self.visitR_graph(graphctx))

        if ctx.r_graphWithoutEvent():
            resultlist.extend(self.visitR_graphWithoutEvent(ctx.r_graphWithoutEvent()))

        return resultlist

    # Visit a parse tree produced by OPQLParser#r_GRAPH_WITHOUT_EVENT.
    def visitR_graphWithoutEvent(self, ctx: OPQLParser.R_graphWithoutEventContext):
        resultlist = [self.visitR_object(ctx.r_object())]

        if ctx.r_relationAny():
            resultlist.append(self.visitR_relationAny(ctx.r_relationAny()))
        elif ctx.r_relationLd():
            resultlist.append(self.visitR_relationLd(ctx.r_relationLd()))

        if ctx.r_graph():
            resultlist.extend(self.visitR_graph(ctx.r_graph()))

        return resultlist

    # Visit a parse tree produced by OPQLParser#r_GRAPHPATTERNLIST.
    def visitR_graphPatternList(self, ctx: OPQLParser.R_graphPatternListContext):
        resultlist = []
        g = ctx.r_graph()
        for graph in g:
            result_graph = self.visitR_graph(graph)
            #TODO: is checking for None correct here?
            if result_graph is not None:
                resultlist.append(result_graph)

        return resultlist

    # Visit a parse tree produced by OPQLParser#r_EVENT.
    def visitR_event(self, ctx: OPQLParser.R_eventContext):
        event = opql.lang.query.GraphEvent()

        if ctx.r_tag():
            event.tag = self.visitR_tag(ctx.r_tag())
        else:
            event.tag = self.running_event_id.get_next_id()

        if ctx.r_name():
            event.type = self.visitR_name(ctx.r_name())

        return event

    # Visit a parse tree produced by OPQLParser#r_OBJECT.
    def visitR_object(self, ctx: OPQLParser.R_objectContext):
        object = opql.lang.query.GraphObject()

        if ctx.r_tag():
            object.tag = self.visitR_tag(ctx.r_tag())
        else:
            object.tag = self.running_object_id.get_next_id()

        if ctx.r_name():
            object.type = self.visitR_name(ctx.r_name())

        # return self.visitChildren(ctx)
        return object

    # Visit a parse tree produced by OPQLParser#r_RELATION.
    def visitR_relationAny(self, ctx: OPQLParser.R_relationAnyContext):
        relation = opql.lang.query.GraphRelation()

        relation.tag = self.visitR_tag(ctx.r_tag()) if ctx.r_tag() else self.running_relation_id.get_next_id()

        if ctx.r_name():
            relation.type = self.visitR_name(ctx.r_name())

        relation.direction = opql.lang.query.GraphRelationDirection.ANY
        return relation

    def visitR_relationLd(self, ctx: OPQLParser.R_relationLdContext):
        relation = opql.lang.query.GraphRelation()

        relation.tag = self.visitR_tag(ctx.r_tag()) if ctx.r_tag() else self.running_relation_id.get_next_id()

        if ctx.r_name():
            relation.type = self.visitR_name(ctx.r_name())

        relation.direction = opql.lang.query.GraphRelationDirection.LEFT
        return relation

    def visitR_relationRd(self, ctx:OPQLParser.R_relationRdContext):
        relation = opql.lang.query.GraphRelation()

        relation.tag = self.visitR_tag(ctx.r_tag()) if ctx.r_tag() else self.running_relation_id.get_next_id()

        if ctx.r_name():
            relation.type = self.visitR_name(ctx.r_name())

        relation.direction = opql.lang.query.GraphRelationDirection.RIGHT
        return relation

    # Visit a parse tree produced by OPQLParser#r_NAME.
    def visitR_name(self, ctx: OPQLParser.R_nameContext):
        # removes leading and trailing quotes "
        return ctx.getText()[1:-1]

    # Visit a parse tree produced by OPQLParser#r_TAG.
    def visitR_tag(self, ctx: OPQLParser.R_tagContext):
        return ctx.getText()


