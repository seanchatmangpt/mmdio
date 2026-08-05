import logging

import opql.eval.expression
import opql.eval.query_pattern
import opql.eval.querycontext
import opql.lang.query
import opql.ocel.ocellog
from opql.exceptions import OPQLEvalError

logger = logging.getLogger(__name__)


def prune(context, depth):
    if depth <= 0:
        return

    deadends = []
    for ctx in context.children:
        # first prune children
        if depth > 1:
            prune(ctx, depth - 1)

            # if no children left
            if not ctx.children:
                deadends.append(ctx)

    for deadend in deadends:
        deadend.parent = None
        context.children.remove(deadend)


def do_graph(ocel: opql.ocel.ocellog.OCELLog,
             graph_startpoints,
             graph: opql.lang.query.Graph,
             candidate_endpoints):
    context_length = 0
    new_endpoints = candidate_endpoints[:]
    for pattern in graph.patterns:
        context_length += len(pattern)
        endpoints = []
        for context in new_endpoints:
            endpoints += opql.eval.query_pattern.find_pattern_candidates(ocel, context, pattern)

        new_endpoints = endpoints

    if not new_endpoints:
        return []

    subject_to: opql.lang.query.Expression = graph.filter

    if subject_to:
        endpoints = []
        for candidate_context in new_endpoints:
            if opql.eval.expression(ocel, candidate_context, subject_to):
                endpoints.append(candidate_context)
            else:
                # remove ctx
                if candidate_context.parent:
                    candidate_context.parent.children.remove(candidate_context)
                    candidate_context.parent = None
                else:
                    raise OPQLEvalError("Tried to remove context node that has no parent")

        for stp in graph_startpoints:
            prune(stp, context_length)

        new_endpoints = endpoints

    if not new_endpoints:
        return []

    return new_endpoints
