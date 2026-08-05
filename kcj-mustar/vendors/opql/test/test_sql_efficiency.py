"""Regression tests pinning SQL round-trip counts for known N+1 hotspots.

These guard the metadata-caching wins in the OCEL access layer: lookups that are
constant for a log's lifetime must happen O(1) times, not once per result row.
If a refactor reintroduces a per-row lookup, the assert here fails loudly
instead of silently regressing performance.

The counting harness wraps dbconnection.execute and tallies normalized SQL.
"""
import collections
import sqlite3

import pytest

import opql.lang.querysolver
import opql.ocel.ocelimport
import opql.ocel.ocellog
import opql.SQLITEResolver

# Small log: 4 events of type "A", one object, enough rows that a per-row
# re-scan would show up as count == 4 rather than the cached count == 1.
EFF_LOG_JSON = {
    "objectTypes": [
        {"name": "item", "attributes": [{"name": "size", "type": "float"}]}
    ],
    "eventTypes": [
        {"name": "A", "attributes": [{"name": "cost", "type": "float"}]},
    ],
    "objects": [
        {
            "id": "i1", "type": "item",
            "attributes": [
                {"name": "size", "value": 5.0, "time": "1970-01-01T00:00:00.000+00:00"},
            ],
            "relationships": []
        },
    ],
    "events": [
        {"id": f"e{i}", "type": "A", "time": f"2024-01-0{i}T10:00:00+00:00",
         "attributes": [{"name": "cost", "value": float(i * 10)}],
         "relationships": [{"objectId": "i1", "qualifier": "uses"}]}
        for i in range(1, 5)
    ],
}


def _norm(sql: str) -> str:
    return " ".join(sql.split())


class _CountingConn:
    """Wraps a sqlite3 connection, tallying execute() calls by normalized SQL."""
    def __init__(self, inner):
        self._inner = inner
        self.counts = collections.Counter()

    def execute(self, sql, *args, **kwargs):
        self.counts[_norm(sql)] += 1
        return self._inner.execute(sql, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._inner, name)


_EVENT_MAP_SCAN = _norm("SELECT ocel_type, ocel_type_map FROM event_map_type")
_OBJECT_MAP_SCAN = _norm("SELECT ocel_type, ocel_type_map FROM object_map_type")


def _scaling_statements(counts, rows) -> dict[str, int]:
    """Statements issued at least once per result row.

    This is the load-bearing check, and it is deliberately not pinned to any SQL
    text: a reintroduced per-row lookup shows up here no matter how it is
    spelled, whereas asserting that a specific string is absent silently becomes
    a tautology as soon as that string is edited or deleted.

    Exactly one statement is allowed to scale with the row count today (fetching
    the projected attribute, or the per-row edge lookup in a linked pattern).
    Removing those is the next tier of work; until then they are the floor, and
    anything joining them is a regression.
    """
    assert rows > 1, "a single-row result cannot distinguish per-row from O(1)"
    return {sql: n for sql, n in counts.items() if n >= rows}


@pytest.fixture
def counting_log():
    raw = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES,
                          check_same_thread=False)
    opql.ocel.ocelimport.load_json_dict(EFF_LOG_JSON, raw)
    conn = _CountingConn(raw)
    return opql.ocel.ocellog.OCELLog(conn), conn


def _run(log, query_str):
    query = opql.lang.querysolver.scan_query(query_str)
    return opql.SQLITEResolver.resolve_query(log, query)


def test_event_map_type_scanned_once_not_per_row(counting_log):
    """The event map table feeds getEvent(); its full scan must be memoized,
    so it runs exactly once regardless of how many event rows are returned.

    Exactly once, not at-most-once: at-most-once would also pass if the scan
    stopped happening at all, which would mean this test no longer covers the
    path it was written for.
    """
    log, conn = counting_log
    res = _run(log, 'PATTERN E(e:"A") RETURN e["cost"]')
    assert res.shape[0] == 4  # four event rows, so a per-row scan would be 4x
    assert conn.counts[_EVENT_MAP_SCAN] == 1


def test_object_map_type_memoized_across_repeated_lookups(counting_log):
    """Same guarantee for the object map table, exercised through getObject().

    Not driven by a query on purpose: pattern matching only reads structure, so
    it resolves object *types* but never constructs an OCELObject, and object
    attribute projection currently yields None without touching the map table
    (OCELObject.getPropertyValue takes a required `version` the projection path
    does not pass). A query-driven assertion here would therefore be vacuous.
    """
    log, conn = counting_log
    for _ in range(4):
        assert log.getObject("i1") is not None
    assert conn.counts[_OBJECT_MAP_SCAN] == 1


def test_pattern_matching_issues_no_per_row_metadata_queries(counting_log):
    """Pattern matching probes "is this id an event or an object?" per candidate.
    Those must come from the bulk id->type maps, so the only statement allowed to
    scale with the row count is the per-row edge lookup itself."""
    log, conn = counting_log
    res = _run(log, 'PATTERN E(e:"A")-[]-O(o:"item") RETURN e, o')
    rows = res.shape[0]
    assert rows == 4

    scaling = _scaling_statements(conn.counts, rows)
    assert len(scaling) == 1, f"expected only the edge lookup to scale, got {scaling}"
    assert "FROM event_object" in next(iter(scaling))

    # both bulk id->type loads happened, once each
    assert conn.counts[_norm("SELECT ocel_id, ocel_type FROM event")] == 1
    assert conn.counts[_norm("SELECT ocel_id, ocel_type FROM object")] == 1


def test_event_property_access_does_not_relookup_map_type(counting_log):
    """OCELEvent already holds its map_type from construction; reading a property
    must not re-query event_map_type for it. Asserted as "only the attribute
    fetch scales with the row count", so any per-row metadata lookup fails here
    whatever SQL it is written as."""
    log, conn = counting_log
    res = _run(log, 'PATTERN E(e:"A") RETURN e["cost"]')
    rows = res.shape[0]
    assert rows == 4

    scaling = _scaling_statements(conn.counts, rows)
    assert len(scaling) == 1, f"expected only the attribute fetch to scale, got {scaling}"
    assert "FROM event_A" in next(iter(scaling))

    # constant overhead is small and constant: candidate scan, bulk types,
    # map-type scan. If that budget grows, something started scaling.
    assert sum(conn.counts.values()) == rows + 3


def test_map_type_lookup_returns_the_table_suffix(counting_log):
    """The map-type cache is reachable only as a single suffix per type, so
    there is no dict for a caller to mutate and no copy to pay for."""
    log, _ = counting_log

    assert log.eventMapTypeOf("A") == "A"
    assert log.objectMapTypeOf("item") == "item"
    assert log.eventMapTypeOf("nonexistent") is None
    assert log.eventMapTypeOf(None) is None


def test_type_cache_is_evicted_on_delete(counting_log):
    """The id->type map goes stale on deletion (unlike the map-type cache), so
    FILTER-driven deletes must evict. Guards against a cache that would keep
    reporting deleted entities as existing."""
    log, _ = counting_log

    assert log.eventExists("e1")           # populate the cache first
    assert log.getEventType("e1") == "A"
    log.deleteEvent("e1")
    assert not log.eventExists("e1")
    assert log.getEventType("e1") is None

    assert log.objectExists("i1")
    log.deleteObject("i1")
    assert not log.objectExists("i1")
    assert log.getObjectType("i1") is None
