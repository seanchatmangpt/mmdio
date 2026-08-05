import pytest

import opql.lang.query
import opql.lang.querysolver


def test_anonymous_object_gets_auto_tag():
    # Regression: visitor previously assigned to `object.get` instead of `object.tag`,
    # leaving anonymous objects with no tag and making them unreachable via lookupSymbol.
    query = opql.lang.querysolver.scan_query("PATTERN O() RETURN 0")
    pattern: list = query.graphsAndFilters[0].patterns[0]
    go: opql.lang.query.GraphObject = pattern[0]
    assert go.tag is not None


def test_anonymous_event_gets_auto_tag():
    query = opql.lang.querysolver.scan_query("PATTERN E() RETURN 0")
    pattern: list = query.graphsAndFilters[0].patterns[0]
    ge: opql.lang.query.GraphEvent = pattern[0]
    assert ge.tag is not None


# Queries covering every clause and modifier that the AST printer has to spell.
ROUNDTRIP_QUERIES = [
    'PATTERN E(a:"Approve")-[]-O(s:"material") RETURN count(PATTERN E(a)-[]-O(m:"material") RETURN m)',
    'PATTERN O(o)-[r:"qual"]->O(p) RETURN *',
    'PATTERN O(o)<-[q]-O(b) RETURN o',
    "PATTERN E() RETURN 0",
    "PATTERN O()-[]-E() RETURN 1",
    'PATTERN E(e:"A") KEEP e AS k SUBJECTTO e["cost"] > 5 RETURN DISTINCT k["ocel_id"], count(k) LIMIT 10',
    'PATTERN O(a)-[q]-O(b), E(c)-[]-O(d) SUBJECTTO a["x"] == 1 FILTER a, b RETURN a',
    'PATTERN E(e:"A") RETURN e["cost"] BINNED((0, 10] AS "low", (10, inf) AS "high")',
    'PATTERN E(e:"A") RETURN e["cost"] BINNED([-inf, 0.5) AS 1)',
    'PATTERN E(e:"A") WHEN e["cost"] AS w RETURN w ORDERBY w DESC, e["ocel_time"] ASC',
    'KEEP (PATTERN E(e:"A") RETURN e["cost"]) AS costs RETURN avg(costs)',
    'KEEP NOT MATERIALIZED (PATTERN E(e:"A") RETURN e["cost"]) AS costs RETURN avg(costs)',
    'PATTERN E(e:"A") RETURN OCEL',
    'PATTERN E(e:"A") RETURN *, e["cost"] AS c',
    'PATTERN E(a:"A")-[]-O(o) RETURN o["p"@a] AS v',
]


@pytest.mark.parametrize("query_str", ROUNDTRIP_QUERIES)
def test_str_renders_parseable_opql(query_str):
    """str(FullQuery) must come back as OPQL that parses to the same thing.

    An unaliased RETURN item is named after its expression's string
    representation, so a subquery argument reaches FullQuery.__str__ and lands
    in a column heading. Rendering is normalising, not verbatim - whitespace
    and optional tokens are not preserved - so the fixed point is checked one
    render in rather than against the source.
    """
    rendered = str(opql.lang.querysolver.scan_query(query_str))
    assert rendered == str(opql.lang.querysolver.scan_query(rendered))


def test_anonymous_tags_are_not_rendered():
    # The visitor names anonymous elements __ev0/__ob0/__rel0. SYMBOLICNAME cannot
    # start with an underscore, so printing one produces unparseable output.
    rendered = str(opql.lang.querysolver.scan_query("PATTERN O()-[]-E() RETURN 1"))
    assert "_" not in rendered
    assert rendered == "PATTERN O()-[]-E() RETURN 1"


def test_unaliased_subquery_aggregate_is_not_an_object_repr():
    # Regression: FullQuery had no __str__, so an inline subquery argument fell
    # back to object.__repr__ and put a memory address in the column heading.
    query = opql.lang.querysolver.scan_query(
        'PATTERN E(e:"A") RETURN count(PATTERN E(x:"A") RETURN x["cost"])'
    )
    name = str(query.return_rule.projection.ctx_expansions[0].evaluatable)
    assert "object at 0x" not in name
    assert name == 'count(PATTERN E(x:"A") RETURN x["cost"])'


def test_distinct_unaliased_subqueries_get_distinct_names():
    # A placeholder rendering would collapse these into one unselectable column.
    query = opql.lang.querysolver.scan_query(
        'PATTERN E(e:"A") RETURN count(PATTERN E(x:"A") RETURN x["cost"]),'
        ' count(PATTERN E(y:"A")-[]-O(o) RETURN o)'
    )
    names = [str(item.evaluatable) for item in query.return_rule.projection.ctx_expansions]
    assert len(set(names)) == 2
