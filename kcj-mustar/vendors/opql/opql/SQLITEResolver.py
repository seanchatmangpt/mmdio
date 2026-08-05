import datetime
import logging

import pandas

import opql.eval.clause.filter
import opql.eval.clause.keep
import opql.eval.clause.pattern
import opql.eval.expression.tree
import opql.eval.querycontext
import opql.lang.query
import opql.ocel.ocellog
import opql.util

logger = logging.getLogger(__name__)



def _projection_item_name(item: opql.lang.query.ProjectionItem) -> str:
    """Column heading for one RETURN item: the AS alias, else the expression text.

    Section 10 of the standard: "optional AS aliases (omitting AS yields a column
    name from the expression's string representation)". Every expression node
    implements __str__ for exactly this, so `e["cost"]` and `olag(e,o)` come back
    spelled the way they were written.
    """
    return item.tag if item.tag else str(item.evaluatable)


def _column_names(endpoint, depth: int, projection) -> list[str]:
    """Headings for the `depth` values a result row carries.

    Read off the context chain rather than off the projection items, because
    RETURN * projects values the pattern bound, which have no projection item at
    all. do_keep already binds every projected value under the name this needs
    (keep.py), so the chain is the one place where both kinds of binding are
    named the same way.

    `endpoint` is None when nothing matched: there is no chain then, so the
    projection items answer instead — an empty result still deserves correctly
    named columns. That cannot cover RETURN *, whose width is only known from a
    row, and the caller handles that case before getting here.
    """
    if endpoint is None:
        return [_projection_item_name(item) for item in projection.ctx_expansions]

    names = []
    ctx = endpoint
    for i in range(depth):
        # a value's name lives on its parent: "I am my parents symbol"
        symbol = ctx.parent.childrenSymbol if ctx.parent is not None else None
        # unnamed bindings should not exist, but a None heading would collapse
        # several columns into one key and be unselectable, so fall back to the
        # position rather than propagate it
        names.append(symbol if symbol is not None else str(depth - 1 - i))
        if ctx.parent is None:
            break
        ctx = ctx.parent

    names.reverse()
    return names


def project(ocel, root_context, candidate_endpoints, projection, filter):
    keep_startpoints = candidate_endpoints
    new_endpoints = []
    for endpoint in candidate_endpoints:
        resulting_endpoints = opql.eval.clause.keep.do_keep(ocel, projection, endpoint)
        new_endpoints += resulting_endpoints

    if filter:
        new_endpoints = [endpoint for endpoint in new_endpoints
                         if opql.eval.expression.tree.evaluate_graphexpression(ocel, endpoint, filter)]

    if projection.order:
        for order_item in reversed(projection.order):
            decorated = [(opql.eval.expression.tree.evaluate_graphexpression(ocel, endpoint, order_item.expression),
                          i,
                          endpoint)
                         for i, endpoint in enumerate(new_endpoints)]

            reverse_order = order_item.direction == opql.lang.query.OrderDirection.DESC

            # handle None types
            exclude_from_ordering = [item for item in decorated if item[0] is None]
            decorated = [item for item in decorated if item[0] is not None]

            decorated.sort(reverse=reverse_order)

            rlist = exclude_from_ordering + decorated
            decorated = rlist

            new_endpoints = [endpoint for val, i, endpoint in decorated]

    if not projection.wildcard and keep_startpoints:
        new_root_children_name = keep_startpoints[0].childrenSymbol

        new_root_children = []
        for ksp in keep_startpoints:
            new_root_children += ksp.children

        root_context.childrenSymbol = new_root_children_name
        root_context.children = new_root_children

        for child_ctx in root_context.children:
            child_ctx.parent = root_context

    if projection.distinct:
        distinct_results = set()

        to_prune = []
        to_keep = []

        for endpoint in new_endpoints:
            val_tpl = endpoint.getValueTuple()

            if val_tpl in distinct_results:
                to_prune.append(endpoint)
            else:
                distinct_results.add(val_tpl)
                to_keep.append(endpoint)

        new_endpoints = to_keep

        # TODO actually prune

    if (projection.limit
            and len(new_endpoints) > projection.limit):
        new_endpoints = new_endpoints[0:projection.limit]

        # to_prune = new_endpoints[projection.limit:]
        # print("TODO: prune context after limit clause!")

    return new_endpoints


def solve(ocel: opql.ocel.ocellog.OCELLog,
          query: opql.lang.query.FullQuery):
    if not sanity_check(query):
        return None

    return resolve_query(ocel, query)


def sanity_check(query: opql.lang.query.FullQuery):
    # print("TODO implement sanity check")

    # TODO check that all target values of bins are of same datatype (and as such comparable)
    # check that lower bound a and upper bound b of bins satisfy a <= b

    return True


def resolve_query(ocel: opql.ocel.ocellog.OCELLog,
                  query: opql.lang.query.FullQuery,
                  root_context=None,
                  keep_context=False):
    if not root_context:
        root_context = opql.eval.querycontext.QueryContext()

    # store root context name so it can be restored later
    root_ctx_cs = root_context.childrenSymbol

    candidate_endpoints = [root_context]

    # list of tuples: (clause,elapsed time)
    runtimes = []

    for graphOrFilter in query.graphsAndFilters:
        # remember where we started
        if isinstance(graphOrFilter, opql.lang.query.Graph):
            start = datetime.datetime.now()

            # TODO explicit copy necessary here?
            graph_startpoints = candidate_endpoints[:]
            candidate_endpoints = opql.eval.clause_pattern(ocel,
                                                          graph_startpoints,
                                                          graphOrFilter,
                                                          candidate_endpoints)

            runtimes.append(
                (graphOrFilter, datetime.datetime.now() - start)
            )
        elif isinstance(graphOrFilter, opql.lang.query.Filter):
            start = datetime.datetime.now()

            opql.eval.clause_filter(ocel, graphOrFilter, candidate_endpoints)
            root_context.clearChildren()
            candidate_endpoints = [root_context]

            runtimes.append(
                (graphOrFilter, datetime.datetime.now() - start)
            )
        elif isinstance(graphOrFilter, opql.lang.query.Keep):
            start = datetime.datetime.now()

            keep_rule: opql.lang.query.Keep = graphOrFilter
            projection = keep_rule.projection

            candidate_endpoints = project(ocel, root_context, candidate_endpoints, projection, keep_rule.filter)

            runtimes.append(
                (graphOrFilter, datetime.datetime.now() - start)
            )
        elif isinstance(graphOrFilter, opql.lang.query.When):
            # TODO: refactor this to when.py
            start = datetime.datetime.now()

            # when is a bit of a special case since it receives the unevaluated expression as function argument
            # and then tries to find all points in time where that expression becomes true
            candidate_endpoints = opql.eval.clause_when(ocel, candidate_endpoints, graphOrFilter)

            runtimes.append(
                (graphOrFilter, datetime.datetime.now() - start)
            )


    # result tree similar to contexttree
    # go from rootcontext
    # keep current context depth -what for again?
    # evaluate thing(list of evaluateables, current depth)
    # and add these as children to previous result

    # evaluate thing:
    # get current depth (or max depth?)
    # if thing is down the line: fan out tree, start with
    # if thing to look up is upwards: just look it up

    return_start = datetime.datetime.now()
    #
    # Return Ocel
    #

    if query.return_rule.ocel:
        logger.debug(f"Return elapsed: {datetime.datetime.now() - return_start}")
        return ocel.dbconnection


    #
    # Return Tabular Data
    #

    projection = query.return_rule.projection
    filter = query.return_rule.filter
    candidate_endpoints = project(ocel, root_context, candidate_endpoints, projection, filter)

    returnrows = []
    if candidate_endpoints is None:
        return pandas.DataFrame()

    lookup_depth = 0
    if projection.wildcard:
        lookup_endpoint = root_context

        if not candidate_endpoints:
            # * projects whatever the enclosing clauses bound, and the only record
            # of that is a matched row. With none, the table's width is unknown —
            # previously this indexed into the empty list and raised IndexError.
            return pandas.DataFrame()

        iter_point = candidate_endpoints[0]
        while iter_point != lookup_endpoint:
            lookup_depth += 1
            iter_point = iter_point.parent
    else:
        lookup_depth = len(query.return_rule.projection.ctx_expansions)

    # for endpoint in candidate_endpoints:
    #     returnvalues: list = []
    #     for returnstatement in query.return_rule.projection.ctx_expansions:
    #         rval = opql.query_expression.evaluate_graphexpression(ocel, endpoint, returnstatement.evaluatable)
    #         returnvalues.append(rval)
    #
    #     returnrows.append(returnvalues)
    for endpoint in candidate_endpoints:
        returnvalues: list = []

        rv_idx = 0
        val_ctx = endpoint
        while rv_idx < lookup_depth:
            rval = val_ctx.contextEntity

            returnvalues.append(rval)

            val_ctx = val_ctx.parent
            rv_idx += 1

        returnvalues.reverse()
        returnrows.append(returnvalues)

    cols = _column_names(candidate_endpoints[0] if candidate_endpoints else None,
                         lookup_depth, projection)

    df = pandas.DataFrame(returnrows, columns=cols)

    if not keep_context:
        root_context.clearChildren()
        # needed because doing graph matching will rename this to whatever symbol was matched
        root_context.childrenSymbol = root_ctx_cs

    if logger.isEnabledFor(logging.DEBUG):
        for rtt in runtimes:
            logger.debug(f"{rtt[0]} elapsed: {rtt[1]}")
        logger.debug(f"Return elapsed: {datetime.datetime.now() - return_start}")

    return df
