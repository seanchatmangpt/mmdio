import logging

import opql.eval.expression.tree
import opql.eval.querycontext
import opql.lang.query
import opql.ocel.ocellog
from opql import SQLITEResolver

logger = logging.getLogger(__name__)


def is_in_bin(bin: opql.lang.query.BinningInterval, value):
    # TODO properly check somewhere that binning interval limits (a,b) actually fulfill a < b
    if bin.begin is not opql.lang.query.BinningInfinity.NEGATIVE_INFINITY:
        if bin.include_begin and value < bin.begin:
            return False

        if not bin.include_begin and value <= bin.begin:
            return False

    if bin.end is not opql.lang.query.BinningInfinity.POSITIVE_INFINITY:
        if bin.include_end and value > bin.end:
            return False

        if not bin.include_end and value >= bin.end:
            return False

    return True


def bin_value(binning: list[opql.lang.query.BinningInterval], value):
    for interval in binning:
        if is_in_bin(interval, value):
            return interval.target

    return None

def expand_ctx(ocel, context_ep, expansion: opql.lang.query.ProjectionItem):
    ctx_evaluated = None

    if isinstance(expansion.evaluatable, opql.lang.query.SubQuery):
        sq_evaluatable: opql.lang.query.SubQuery = expansion.evaluatable
        if sq_evaluatable.materialized:
            ctx_evaluated = SQLITEResolver.resolve_query(ocel, sq_evaluatable.query, context_ep, False)
        else:
            ctx_evaluated = sq_evaluatable.query
    elif isinstance(expansion.evaluatable, opql.lang.query.Expression):
        ctx_evaluated = opql.eval.expression(ocel, context_ep, expansion.evaluatable)
    else:
        # TODO: this _should_ never happen  -print meaningful error message. we need proper logging
        pass

    # TODO: this will get very long for non-materialized subqueries and very weird for materialized ones.
    #  add edge case that always stuffs the return statement of the subquery here? probably least bad option.
    context_ep.childrenSymbol = expansion.tag if expansion.tag else str(expansion.evaluatable)

    # if it's a solitary value, make this a list to unify handling of results
    if not isinstance(ctx_evaluated, list):
        ctx_evaluated = [ctx_evaluated]

    for value in ctx_evaluated:
        new_ctx_ep = opql.eval.querycontext.QueryContext()
        new_ctx_ep.parent = context_ep

        if expansion.binning:
            value = bin_value(expansion.binning, value)
        new_ctx_ep.contextEntity = value

        context_ep.children.append(new_ctx_ep)


def do_keep(ocel: opql.ocel.ocellog.OCELLog, projection: opql.lang.query.Projection, context):
    ctx_eps = [context]

    for expansion in projection.ctx_expansions:
        new_children = []

        for ctx_ep in ctx_eps:
            expand_ctx(ocel, ctx_ep, expansion)

            new_children += ctx_ep.children

        ctx_eps = new_children


    return ctx_eps