"""Regression tests for the WHEN clause (eval/clause/when.py)."""

import sqlite3

import pandas
import pytest

import opql.lang.querysolver
import opql.ocel.ocelimport
import opql.ocel.ocellog
import opql.SQLITEResolver

# Two accounts, each with a balance attribute that changes once.
# acc1: balance 100 at epoch, 200 at 2024-01-02  → 2 candidate timestamps
# acc2: balance  50 at epoch, 150 at 2024-01-03  → 2 candidate timestamps
# balance > 0 is always true, so all 4 (object, timestamp) pairs are valid.
WHEN_LOG = {
    "objectTypes": [
        {"name": "account", "attributes": [{"name": "balance", "type": "float"}]}
    ],
    "eventTypes": [],
    "objects": [
        {
            "id": "acc1",
            "type": "account",
            "attributes": [
                {"name": "balance", "time": "1970-01-01T00:00:00.000Z", "value": 100.0},
                {"name": "balance", "time": "2024-01-02T00:00:00.000Z", "value": 200.0},
            ],
            "relationships": [],
        },
        {
            "id": "acc2",
            "type": "account",
            "attributes": [
                {"name": "balance", "time": "1970-01-01T00:00:00.000Z", "value": 50.0},
                {"name": "balance", "time": "2024-01-03T00:00:00.000Z", "value": 150.0},
            ],
            "relationships": [],
        },
    ],
    "events": [],
}


# One order whose price crosses 3000 twice, in a down-then-up shape.
# Candidate timestamps are exactly the four version stamps (the first is at
# epoch, which when.py always adds anyway), of which two satisfy price > 3000.
THRESHOLD_LOG = {
    "objectTypes": [
        {"name": "order", "attributes": [{"name": "price", "type": "float"}]}
    ],
    "eventTypes": [],
    "objects": [
        {
            "id": "ord1",
            "type": "order",
            "attributes": [
                {"name": "price", "time": "1970-01-01T00:00:00.000Z", "value": 1000.0},
                {"name": "price", "time": "2024-01-02T00:00:00.000Z", "value": 3500.0},
                {"name": "price", "time": "2024-01-03T00:00:00.000Z", "value": 2000.0},
                {"name": "price", "time": "2024-01-04T00:00:00.000Z", "value": 4000.0},
            ],
            "relationships": [],
        },
    ],
    "events": [],
}


@pytest.fixture(scope="module")
def when_log():
    db = sqlite3.connect(
        ":memory:", detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False
    )
    opql.ocel.ocelimport.load_json_dict(WHEN_LOG, db)
    return opql.ocel.ocellog.OCELLog(db)


@pytest.fixture(scope="module")
def threshold_log():
    db = sqlite3.connect(
        ":memory:", detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False
    )
    opql.ocel.ocelimport.load_json_dict(THRESHOLD_LOG, db)
    return opql.ocel.ocellog.OCELLog(db)


def _run(log, query_str):
    q = opql.lang.querysolver.scan_query(query_str)
    return opql.SQLITEResolver.resolve_query(log, q)


def test_when_processes_all_contexts(when_log):
    """WHEN must iterate over every input context, not just the first one.

    Regression for DIV-01: `return` was inside the outer for-loop in
    when.py, causing all contexts after the first to be silently dropped.
    With two objects and two valid timestamps each, the result must have
    4 rows, not 2.
    """
    result = _run(
        when_log,
        """
        PATTERN O(acc:"account")
        WHEN acc["balance"@ts] > 0 AS ts
        RETURN acc["ocel_id"] AS acc_id, ts AS ts
        """,
    )

    assert isinstance(result, pandas.DataFrame), f"Expected DataFrame, got: {result}"
    assert result.shape == (4, 2), (
        f"Expected 4 rows (2 objects x 2 timestamps each), got {result.shape}. "
        "If this is 2 rows the early-return bug is present."
    )

    # Both objects must appear in the output.
    acc_ids = set(result.iloc[:, 0])
    assert "acc1" in acc_ids, "acc1 missing — only first context was processed"
    assert "acc2" in acc_ids, "acc2 missing — only first context was processed"


def test_when_emits_one_row_per_matching_timestamp_only(threshold_log):
    """Non-matching candidate timestamps must not produce rows of their own.

    The record has four candidate timestamps, two of which satisfy the
    predicate. Per eval_wC (standard sec. 09), a record with at least one
    match takes the match branch exclusively: one row per matching
    timestamp, and nothing at all for the rejected candidates.

    2 rows  → correct.
    4 rows  → the None binding is being emitted per rejected candidate
              instead of per input record.
    1 row   → only the first crossing is reported.
    """
    result = _run(
        threshold_log,
        """
        PATTERN O(ord:"order")
        WHEN ord["price"@t] > 3000 AS t
        RETURN ord["ocel_id"] AS oid, t AS t
        """,
    )

    assert isinstance(result, pandas.DataFrame), f"Expected DataFrame, got: {result}"
    assert result.shape == (2, 2), (
        f"Expected 2 rows (one per crossing), got {result.shape}. "
        "4 rows means rejected candidates are emitting None rows."
    )

    assert bool(result["t"].notna().all()), (
        "A None binding leaked into a record that has matching timestamps; "
        "the two eval_wC branches are not mutually exclusive."
    )

    stamps = set(pandas.to_datetime(result["t"], utc=True))
    assert stamps == {
        pandas.Timestamp("2024-01-02", tz="UTC"),
        pandas.Timestamp("2024-01-04", tz="UTC"),
    }, f"Wrong crossings reported: {stamps}"


def test_when_binds_none_once_when_nothing_matches(threshold_log):
    """With no matching timestamp the record survives with a single None.

    Complement of the test above: same four candidates, none satisfying the
    predicate. The record is padded rather than dropped, exactly once —
    4 rows here would again mean per-candidate None emission.
    """
    result = _run(
        threshold_log,
        """
        PATTERN O(ord:"order")
        WHEN ord["price"@t] > 9000 AS t
        RETURN ord["ocel_id"] AS oid, t AS t
        """,
    )

    assert isinstance(result, pandas.DataFrame), f"Expected DataFrame, got: {result}"
    assert result.shape == (1, 2), (
        f"Expected 1 None-padded row, got {result.shape}. "
        "0 rows means the record was dropped instead of padded."
    )
    assert result["oid"].iloc[0] == "ord1"
    assert bool(
        result["t"].isna().all()
    ), f"Expected t to be None, got {result['t'].iloc[0]}"


# Regression: when_s.filter was populated by the visitor but never read, so a
# WHEN guard was a no-op. Rows without the guard: 2 matching + 0 None-padded.
@pytest.mark.parametrize("guard, expected_rows", [
    ("SUBJECTTO 1 == 2", 0),
    ("ST 1 == 2", 0),
    ("SUBJECTTO 1 == 1", 2),
    ("SUBJECTTO NOT isnone(t)", 2),
    ("SUBJECTTO isnone(t)", 0),
])
def test_when_subjectto_filters_rows(threshold_log, guard, expected_rows):
    result = _run(threshold_log, f"""
        PATTERN O(ord:"order")
        WHEN ord["price"@t] > 3000 AS t
        {guard}
        RETURN ord["ocel_id"] AS oid, t AS t
    """)
    assert isinstance(result, pandas.DataFrame), f"Expected DataFrame, got: {result}"
    assert result.shape[0] == expected_rows


def test_when_subjectto_sees_none_binding(threshold_log):
    """The guard runs after the fan-out, so it can select the None-padded row."""
    result = _run(threshold_log, """
        PATTERN O(ord:"order")
        WHEN ord["price"@t] > 9000 AS t
        SUBJECTTO isnone(t)
        RETURN ord["ocel_id"] AS oid, t AS t
    """)
    assert result.shape == (1, 2)
    assert bool(result["t"].isna().all())
