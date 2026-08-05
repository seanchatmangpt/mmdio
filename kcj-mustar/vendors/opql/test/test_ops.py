import datetime

import opql.lang.query
import opql.lang.querysolver
import opql.ocel.ocelimport
import opql.SQLITEResolver
from opql.ocel.ocelimport import make_inmemory_db

# import OPQL.ocellog
#
#
# def test_filter():
#     #TODO do this
#     query = """
#     PATTERN E(event:"Create Goods Receipt")-[nextref]-O(whatever)
#     SUBJECTTO event["ocel_time"] > ["2022-05-25T08:41:35.000Z"] AND event["ocel_time"] < ["2022-08-25T08:41:35.000Z"]
#     RETURN
#     event["ocel_id"], event["ocel_time"], event["ocel_type"], event["resource"],
#     whatever["ocel_id"], whatever["ocel_type"]
#     """
#
#     query_filter = """
#     PATTERN E(event:"Create Goods Receipt")-[nextref]-O(whatever)
#     SUBJECTTO event["ocel_time"] < ["2022-05-25T08:41:35.000Z"]
#     FILTER event
#     PATTERN E(event:"Create Goods Receipt")-[nextref]-O(whatever)
#     SUBJECTTO event["ocel_time"] > ["2022-08-25T08:41:35.000Z"]
#     FILTER event
#     PATTERN E(event:"Create Goods Receipt")-[nextref]-O(whatever)
#     RETURN event["ocel_id"], event["ocel_time"], event["ocel_type"], event["resource"],
#     whatever["ocel_id"], whatever["ocel_type"]
#     """
#
#     # result of query and query filter should be the same
#
#     query_struct = OPQL.querysolver.scan_query(query)
#     # result = OPQL.SQLITEResolver.resolve_query(log, query_struct)


empty_log_json = """
{
    "objectTypes": [],
    "eventTypes": [], 
    "objects": [], 
    "events": []
}
"""

log_sqlite = make_inmemory_db()
empty_log = opql.ocel.ocelimport.load_json_str(empty_log_json, log_sqlite)

def test_date_extraction():
    # hour/second return raw stored components (no tz conversion); second() is int, not float
    result = _run(empty_log, """
        KEEP 6 AS sunday_idx, T("2022-11-06T13:45:03.500+02:00") AS dts
        RETURN dayOfWeek(dts,"+00:00") == sunday_idx AS dow,
               day(dts,"+00:00") ==  6 AS day,
               month(dts,"+00:00") == 11 AS month,
               year(dts,"+00:00") == 2022 AS year,
               hour(dts,"+00:00") == 13 AS hour,
               minute(dts,"+00:00") == 45 AS minute,
               second(dts,"+00:00") == 3 AS second
    """)
    for col in range(7):
        assert _val(result, col), f"column {col} was not True"

def test_duration_eval():
    result = _run(empty_log, "RETURN D(3,2,7,2.445) AS duration_test, D(3,2,7,5) AS duration_test4")
    assert _val(result, 0) == datetime.timedelta(days=3, hours=2, minutes=7, seconds=2.445)
    assert _val(result, 1) == datetime.timedelta(days=3, hours=2, minutes=7, seconds=5)

def test_correct_arithmetics():
    # 5+10*2 == 25 with correct precedence; left-to-right would give 30
    result = _run(empty_log, "RETURN 5+10*2")
    assert _val(result) == 25


# --- helpers ---

def _run(log, query_str):
    query = opql.lang.querysolver.scan_query(query_str)
    return opql.SQLITEResolver.resolve_query(log, query)


def _val(df, col=0, row=0):
    # positional, so it does not depend on how the resolver names columns
    return df.iloc[row, col]


def _get_literal(expression):
    """Extract the scalar value from a single-literal expression (no operators)."""
    assert isinstance(expression, opql.lang.query.AtomicExpr), \
        f"Expected AtomicExpr, got {type(expression)}"
    return expression.value


def _parse_keep_return(query_str):
    """Parse a query and return the AST."""
    return opql.lang.querysolver.scan_query(query_str)


# --- numeric type tests ---

def test_multidigit_int_in_expression():
    q = _parse_keep_return("KEEP 42 AS x RETURN x AS y")
    keep_expr = q.graphsAndFilters[0].projection.ctx_expansions[0].evaluatable
    assert _get_literal(keep_expr) == 42
    assert isinstance(_get_literal(keep_expr), int)


def test_large_int_in_expression():
    q = _parse_keep_return("KEEP 1000 AS x RETURN x AS y")
    keep_expr = q.graphsAndFilters[0].projection.ctx_expansions[0].evaluatable
    assert _get_literal(keep_expr) == 1000
    assert isinstance(_get_literal(keep_expr), int)


def test_zero_int():
    q = _parse_keep_return("KEEP 0 AS x RETURN x AS y")
    keep_expr = q.graphsAndFilters[0].projection.ctx_expansions[0].evaluatable
    assert _get_literal(keep_expr) == 0
    assert isinstance(_get_literal(keep_expr), int)


def test_float_in_expression():
    q = _parse_keep_return("KEEP 3.14 AS x RETURN x AS y")
    keep_expr = q.graphsAndFilters[0].projection.ctx_expansions[0].evaluatable
    assert abs(_get_literal(keep_expr) - 3.14) < 1e-9
    assert isinstance(_get_literal(keep_expr), float)


def test_multidigit_float():
    q = _parse_keep_return("KEEP 123.456 AS x RETURN x AS y")
    keep_expr = q.graphsAndFilters[0].projection.ctx_expansions[0].evaluatable
    assert abs(_get_literal(keep_expr) - 123.456) < 1e-9


def test_limit_multidigit():
    q = _parse_keep_return("KEEP 1 AS x RETURN x AS y ORDERBY x LIMIT 10")
    assert q.return_rule.projection.limit == 10


def test_limit_large():
    q = _parse_keep_return("KEEP 1 AS x RETURN x AS y ORDERBY x LIMIT 999")
    assert q.return_rule.projection.limit == 999


def test_duration_multidigit_fields():
    q = _parse_keep_return("KEEP D(30, 24, 60, 2.5) AS dur RETURN dur AS d")
    keep_expr = q.graphsAndFilters[0].projection.ctx_expansions[0].evaluatable
    dur = _get_literal(keep_expr)
    assert isinstance(dur, datetime.timedelta)
    assert dur == datetime.timedelta(days=30, hours=24, minutes=60, seconds=2.5)


def test_duration_integer_seconds():
    q = _parse_keep_return("KEEP D(3, 2, 7, 5) AS dur RETURN dur AS d")
    keep_expr = q.graphsAndFilters[0].projection.ctx_expansions[0].evaluatable
    dur = _get_literal(keep_expr)
    assert isinstance(dur, datetime.timedelta)
    assert dur == datetime.timedelta(days=3, hours=2, minutes=7, seconds=5)


def test_multiplication_sign_parsed():
    q = _parse_keep_return("KEEP 5*2 AS x RETURN x AS y")
    keep_expr = q.graphsAndFilters[0].projection.ctx_expansions[0].evaluatable
    assert isinstance(keep_expr, opql.lang.query.BinaryExpr)
    assert keep_expr.op == '*'

