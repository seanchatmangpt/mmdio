"""Tests for the OCEL access layer's handling of inconsistent logs."""
import sqlite3

import pytest

import opql.ocel.ocelimport
import opql.ocel.ocellog
from opql.exceptions import OPQLDataError

LOG_JSON = {
    "objectTypes": [{"name": "item", "attributes": []}],
    "eventTypes": [{"name": "A", "attributes": []}],
    "objects": [{"id": "i1", "type": "item", "attributes": [], "relationships": []}],
    "events": [{"id": "e1", "type": "A", "time": "2024-01-01T10:00:00+00:00",
                "attributes": [], "relationships": []}],
}


# 12 events on one object, alternating type, timestamps increasing with the
# number. Twelve matters: it is where lexicographic and chronological order
# diverge, because "e9" sorts after "e11".
LAGLEAD_LOG_JSON = {
    "objectTypes": [{"name": "item", "attributes": []}],
    "eventTypes": [{"name": "A", "attributes": []}, {"name": "B", "attributes": []}],
    "objects": [{"id": "o1", "type": "item", "attributes": [], "relationships": []}],
    "events": [{"id": f"e{i}", "type": ("A" if i % 2 else "B"),
                "time": f"2024-01-{i:02d}T10:00:00+00:00", "attributes": [],
                "relationships": [{"objectId": "o1", "qualifier": "uses"}]}
               for i in range(1, 13)],
}


# Same shape, except e2 touches o1 under two qualifiers. order-management does
# this 78 times, so it is ordinary data rather than a pathological case.
DUP_QUALIFIER_LOG_JSON = {
    "objectTypes": [{"name": "item", "attributes": []}],
    "eventTypes": [{"name": "A", "attributes": []}],
    "objects": [{"id": "o1", "type": "item", "attributes": [], "relationships": []}],
    "events": [{"id": f"e{i}", "type": "A",
                "time": f"2024-01-{i:02d}T10:00:00+00:00", "attributes": [],
                "relationships": [{"objectId": "o1", "qualifier": "uses"}]
                + ([{"objectId": "o1", "qualifier": "also_uses"}] if i == 2 else [])}
               for i in range(1, 5)],
}


@pytest.fixture
def log():
    raw = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES,
                          check_same_thread=False)
    opql.ocel.ocelimport.load_json_dict(LOG_JSON, raw)
    return opql.ocel.ocellog.OCELLog(raw), raw


@pytest.fixture
def laglead_log():
    raw = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES,
                          check_same_thread=False)
    opql.ocel.ocelimport.load_json_dict(LAGLEAD_LOG_JSON, raw)
    return opql.ocel.ocellog.OCELLog(raw), raw


@pytest.fixture
def dup_qualifier_log():
    raw = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES,
                          check_same_thread=False)
    opql.ocel.ocelimport.load_json_dict(DUP_QUALIFIER_LOG_JSON, raw)
    return opql.ocel.ocellog.OCELLog(raw), raw


def test_delete_object_of_unmapped_type_raises_data_error(log):
    """An object whose type has no object_map_type row has no attribute table to
    delete from. That used to build an OCELObject that came back None and then
    crash on .getType(); it must report the inconsistency instead."""
    ocel, raw = log
    raw.execute("INSERT INTO object (ocel_id, ocel_type) VALUES ('ghost', 'nosuchtype')")

    with pytest.raises(OPQLDataError, match="nosuchtype"):
        ocel.deleteObject("ghost")


def test_delete_event_of_unmapped_type_raises_data_error(log):
    """Same for events."""
    ocel, raw = log
    raw.execute("INSERT INTO event (ocel_id, ocel_type) VALUES ('ghost', 'nosuchtype')")

    with pytest.raises(OPQLDataError, match="nosuchtype"):
        ocel.deleteEvent("ghost")


def test_delete_of_unknown_id_is_a_no_op(log):
    """Deleting something that was never there stays silent — only a type the
    log cannot resolve is an integrity problem."""
    ocel, _ = log

    ocel.deleteObject("does_not_exist")
    ocel.deleteEvent("does_not_exist")


def test_delete_removes_the_entity_and_its_attribute_row(log):
    """The ordinary path still works after the guard."""
    ocel, raw = log

    ocel.deleteObject("i1")
    assert not ocel.objectExists("i1")
    assert raw.execute("SELECT COUNT(*) FROM object_item WHERE ocel_id='i1'").fetchone()[0] == 0

    ocel.deleteEvent("e1")
    assert not ocel.eventExists("e1")
    assert raw.execute("SELECT COUNT(*) FROM event_A WHERE ocel_id='e1'").fetchone()[0] == 0


def test_olag_orders_by_time_not_by_event_id(laglead_log):
    """olag used to sort (id, timestamp) tuples, which orders on the id string:
    stepping back from e12 returned e9, because "e9" > "e11" lexicographically."""
    ocel, _ = laglead_log

    assert [ocel.olaglead("e12", "o1", lag=True, offset=k) for k in range(3)] \
        == ["e11", "e10", "e9"]


def test_olead_orders_by_time_not_by_event_id(laglead_log):
    """Same defect in the other direction: stepping forward from e1 returned
    e10, the lexicographically smallest id rather than the next event."""
    ocel, _ = laglead_log

    assert [ocel.olaglead("e1", "o1", lag=False, offset=k) for k in range(3)] \
        == ["e2", "e3", "e4"]


def test_olaglead_filters_by_event_type(laglead_log):
    """Odd-numbered events are type A. Type filtering applies before the offset,
    so offsets step through matching events only."""
    ocel, _ = laglead_log

    assert [ocel.olaglead("e12", "o1", lag=True, offset=k, etype="A") for k in range(3)] \
        == ["e11", "e9", "e7"]


def test_olaglead_returns_none_at_the_boundaries(laglead_log):
    """Nothing before the first event, nothing after the last, and an offset
    past the end falls off rather than wrapping."""
    ocel, _ = laglead_log

    assert ocel.olaglead("e1", "o1", lag=True) is None
    assert ocel.olaglead("e12", "o1", lag=False) is None
    assert ocel.olaglead("e2", "o1", lag=True, offset=99) is None
    assert ocel.olaglead("nonexistent", "o1", lag=True) is None
    assert ocel.olaglead(None, "o1", lag=True) is None
    assert ocel.olaglead("e2", None, lag=True) is None


def test_olaglead_counts_an_event_once_per_object_not_once_per_qualifier(dup_qualifier_log):
    """event_object is keyed on (event, object, qualifier), so relating e2 to o1
    under two qualifiers stores two rows. That is one neighbouring event, and the
    offset must step over it once: olag from e4 used to yield e3, e2, e2."""
    ocel, _ = dup_qualifier_log

    assert [ocel.olaglead("e4", "o1", lag=True, offset=k) for k in range(3)] \
        == ["e3", "e2", "e1"]
    assert [ocel.olaglead("e1", "o1", lag=False, offset=k) for k in range(3)] \
        == ["e2", "e3", "e4"]


def test_olaglead_skips_relations_pointing_at_deleted_events(laglead_log):
    """A relation row can name an event the log does not contain — not via
    deleteEvent, which cascades, but via a supplied sqlite log, whose FOREIGN KEY
    declarations sqlite never enforces. Dereferencing it used to crash on None.
    Simulated with a direct INSERT because no importer produces one."""
    ocel, raw = laglead_log

    ocel.deleteEvent("e11")
    raw.execute("INSERT INTO event_object VALUES ('e11','o1','uses')")

    assert ocel.olaglead("e12", "o1", lag=True) == "e10"
