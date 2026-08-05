import sqlite3

import pandas
import pytest

import opql.lang.querysolver
import opql.ocel.ocelimport
import opql.ocel.ocellog
import opql.SQLITEResolver

# Minimal OCEL 2.0 JSON log with events that have a numeric "cost" attribute.
# Three events of type "A" with costs 10, 20, 30.
# One object of type "item" linked to all three events.
SAMPLE_LOG_JSON = {
    "objectTypes": [
        {
            "name": "item",
            "attributes": []
        }
    ],
    "eventTypes": [
        {
            "name": "A",
            "attributes": [
                {"name": "cost", "type": "float"}
            ]
        }
    ],
    "objects": [
        {
            "id": "obj1",
            "type": "item",
            "attributes": [],
            "relationships": []
        }
    ],
    "events": [
        {
            "id": "ev1",
            "type": "A",
            "time": "2024-01-01T10:00:00+00:00",
            "attributes": [{"name": "cost", "value": 10.0}],
            "relationships": [{"objectId": "obj1", "qualifier": "item"}]
        },
        {
            "id": "ev2",
            "type": "A",
            "time": "2024-01-02T10:00:00+00:00",
            "attributes": [{"name": "cost", "value": 20.0}],
            "relationships": [{"objectId": "obj1", "qualifier": "item"}]
        },
        {
            "id": "ev3",
            "type": "A",
            "time": "2024-01-03T10:00:00+00:00",
            "attributes": [{"name": "cost", "value": 30.0}],
            "relationships": [{"objectId": "obj1", "qualifier": "item"}]
        }
    ]
}


@pytest.fixture(scope="module")
def sample_log():
    db = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES,
                         check_same_thread=False)
    opql.ocel.ocelimport.load_json_dict(SAMPLE_LOG_JSON, db)
    return opql.ocel.ocellog.OCELLog(db)


def _run(log, query_str):
    query = opql.lang.querysolver.scan_query(query_str)
    return opql.SQLITEResolver.resolve_query(log, query)


def _val(df, col=0, row=0):
    """Get a scalar from the result DataFrame by positional index.

    Positional on purpose: these tests care about the values, not the headings,
    and iloc keeps them independent of how columns are named.
    """
    return df.iloc[row, col]



# ---------- eager CTE (default) ----------

def test_eager_cte_avg(sample_log):
    result = _run(sample_log, """
        KEEP (PATTERN E(e:"A") RETURN e["cost"]) AS costs
        RETURN avg(costs) AS avg_cost
    """)
    assert isinstance(result, pandas.DataFrame)
    assert _val(result) == pytest.approx(20.0)


def test_eager_cte_count(sample_log):
    result = _run(sample_log, """
        KEEP (PATTERN E(e:"A") RETURN e["cost"]) AS costs
        RETURN count(costs) AS n
    """)
    assert _val(result) == 3


def test_eager_cte_stddev(sample_log):
    result = _run(sample_log, """
        KEEP (PATTERN E(e:"A") RETURN e["cost"]) AS costs
        RETURN stddev(costs) AS sd
    """)
    assert _val(result) == pytest.approx(10.0)


def test_eager_cte_multiple_agg(sample_log):
    """Referencing the same CTE in multiple aggregation functions."""
    result = _run(sample_log, """
        KEEP (PATTERN E(e:"A") RETURN e["cost"]) AS costs
        RETURN avg(costs) AS a, count(costs) AS n
    """)
    assert _val(result, 0) == pytest.approx(20.0)
    assert _val(result, 1) == 3


# ---------- explicit MATERIALIZED ----------

def test_materialized_cte_avg(sample_log):
    result = _run(sample_log, """
        KEEP MATERIALIZED (PATTERN E(e:"A") RETURN e["cost"]) AS costs
        RETURN avg(costs) AS avg_cost
    """)
    assert _val(result) == pytest.approx(20.0)


def test_materialized_cte_count(sample_log):
    result = _run(sample_log, """
        KEEP MATERIALIZED (PATTERN E(e:"A") RETURN e["cost"]) AS costs
        RETURN count(costs) AS n
    """)
    assert _val(result) == 3


# ---------- NOT MATERIALIZED (lazy) ----------

def test_lazy_cte_avg(sample_log):
    result = _run(sample_log, """
        KEEP NOT MATERIALIZED (PATTERN E(e:"A") RETURN e["cost"]) AS costs
        RETURN avg(costs) AS avg_cost
    """)
    assert _val(result) == pytest.approx(20.0)


def test_lazy_cte_count(sample_log):
    result = _run(sample_log, """
        KEEP NOT MATERIALIZED (PATTERN E(e:"A") RETURN e["cost"]) AS costs
        RETURN count(costs) AS n
    """)
    assert _val(result) == 3


def test_lazy_cte_multiple_agg(sample_log):
    """Lazy CTE referenced multiple times — each reference re-executes."""
    result = _run(sample_log, """
        KEEP NOT MATERIALIZED (PATTERN E(e:"A") RETURN e["cost"]) AS costs
        RETURN avg(costs) AS a, count(costs) AS n
    """)
    assert _val(result, 0) == pytest.approx(20.0)
    assert _val(result, 1) == 3


# ---------- inline subquery comparison ----------

def test_cte_matches_inline_subquery(sample_log):
    """CTE result should match an equivalent inline subquery in a function."""
    cte_result = _run(sample_log, """
        KEEP (PATTERN E(e:"A") RETURN e["cost"]) AS costs
        RETURN avg(costs) AS avg_cost
    """)

    inline_result = _run(sample_log, """
        RETURN avg(PATTERN E(e:"A") RETURN e["cost"]) AS avg_cost
    """)

    assert _val(cte_result) == pytest.approx(_val(inline_result))


def test_lazy_cte_matches_inline_subquery(sample_log):
    """Lazy CTE result should also match an equivalent inline subquery."""
    cte_result = _run(sample_log, """
        KEEP NOT MATERIALIZED (PATTERN E(e:"A") RETURN e["cost"]) AS costs
        RETURN avg(costs) AS avg_cost
    """)

    inline_result = _run(sample_log, """
        RETURN avg(PATTERN E(e:"A") RETURN e["cost"]) AS avg_cost
    """)

    assert _val(cte_result) == pytest.approx(_val(inline_result))


# ---------- CTE result shape ----------

def test_cte_single_column(sample_log):
    """A CTE returning one column should produce correct results."""
    result = _run(sample_log, """
        KEEP (PATTERN E(e:"A") RETURN e["cost"]) AS costs
        RETURN count(costs) AS n
    """)
    assert result.shape == (1, 1)


def test_cte_with_wildcard(sample_log):
    """CTE alongside wildcard KEEP to retain previous context."""
    result = _run(sample_log, """
        KEEP 42 AS x
        KEEP *, (PATTERN E(e:"A") RETURN e["cost"]) AS costs
        RETURN x, avg(costs) AS a
    """)
    assert _val(result, 0) == 42
    assert _val(result, 1) == pytest.approx(20.0)
