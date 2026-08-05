import opql.eval.clause.filter as filter_impl
import opql.eval.clause.keep as keep_impl
import opql.eval.clause.pattern as pattern_impl
import opql.eval.clause.when as when_impl
import opql.lang.query
import opql.ocel.ocellog


def clause_filter(ocel: opql.ocel.ocellog.OCELLog, filter: opql.lang.query.Filter, candidate_endpoints):
    return filter_impl.do_filter(ocel, filter, candidate_endpoints)

def clause_keep(ocel: opql.ocel.ocellog.OCELLog, projection: opql.lang.query.Projection, candidate_endpoints):
    return keep_impl.do_keep(ocel, projection, candidate_endpoints)

def clause_pattern(ocel: opql.ocel.ocellog.OCELLog,
            graph_startpoints,
            graph: opql.lang.query.Graph,
            candidate_endpoints):
    return pattern_impl.do_graph(ocel, graph_startpoints, graph, candidate_endpoints)

def clause_when(ocel, candidate_endpoints, when_clause):
    return when_impl.do_when(ocel, candidate_endpoints, when_clause)


