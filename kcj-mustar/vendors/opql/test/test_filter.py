import copy
import sqlite3

import pytest

import opql.lang.querysolver
import opql.ocel.ocelimport
import opql.ocel.ocellog
import opql.SQLITEResolver

# Three events of type "A", each connected to exactly one unique object.
# Filtering one event must remove the event and all relations it participates
# in. The then-orphaned object stays in the log (deliberately: what happens
# to orphans is the user's decision, see standard section 09).
FILTER_LOG_JSON = {
    "objectTypes": [
        {"name": "item", "attributes": []}
    ],
    "eventTypes": [
        {"name": "A", "attributes": []}
    ],
    "objects": [
        {"id": "o1", "type": "item", "attributes": [], "relationships": []},
        {"id": "o2", "type": "item", "attributes": [], "relationships": []},
        {"id": "o3", "type": "item", "attributes": [], "relationships": []},
    ],
    "events": [
        {
            "id": "e1",
            "type": "A",
            "time": "2024-01-01T10:00:00+00:00",
            "attributes": [],
            "relationships": [{"objectId": "o1", "qualifier": "item"}]
        },
        {
            "id": "e2",
            "type": "A",
            "time": "2024-01-02T10:00:00+00:00",
            "attributes": [],
            "relationships": [{"objectId": "o2", "qualifier": "item"}]
        },
        {
            "id": "e3",
            "type": "A",
            "time": "2024-01-03T10:00:00+00:00",
            "attributes": [],
            "relationships": [{"objectId": "o3", "qualifier": "item"}]
        },
    ]
}


def make_log(log_json):
    db = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES,
                         check_same_thread=False)
    opql.ocel.ocelimport.load_json_dict(log_json, db)
    return opql.ocel.ocellog.OCELLog(db)


# function scope on purpose: FILTER mutates the log
@pytest.fixture
def filter_log():
    return make_log(FILTER_LOG_JSON)


def _run(log, query_str):
    query = opql.lang.querysolver.scan_query(query_str)
    return opql.SQLITEResolver.resolve_query(log, query)


FILTER_E2_QUERY = """
PATTERN E(e:"A")-[]-O(o:"item")
SUBJECTTO e["ocel_id"] == "e2"
FILTER e
RETURN OCEL
"""


def test_filter_removes_event(filter_log):
    assert filter_log.numEvents() == 3
    assert filter_log.numObjects() == 3

    result = _run(filter_log, FILTER_E2_QUERY)
    assert isinstance(result, sqlite3.Connection)

    assert filter_log.numEvents() == 2
    assert not filter_log.eventExists("e2")
    assert filter_log.eventExists("e1")
    assert filter_log.eventExists("e3")


def test_filter_removes_relations_of_deleted_event(filter_log):
    """Nothing may dangle: every relation the deleted event participated in
    is removed with it."""
    _run(filter_log, FILTER_E2_QUERY)

    assert filter_log.getEORelations(event_id="e2", event_type=None,
                                     object_id=None, object_type=None,
                                     qualifier=None) == []
    assert filter_log.getEORelations(event_id=None, event_type=None,
                                     object_id="o2", object_type=None,
                                     qualifier=None) == []


def test_filter_keeps_orphaned_object(filter_log):
    """Deleting e2 leaves o2 without any relation. The orphan stays in the
    log: removing it (or not) is the user's decision, the engine must not
    cascade."""
    _run(filter_log, FILTER_E2_QUERY)

    assert filter_log.numObjects() == 3
    assert filter_log.objectExists("o2")


def test_filter_object_directly():
    """FILTER on an object symbol removes the object and its relations;
    the event it was related to survives (no cascade in either direction)."""
    log = make_log(FILTER_LOG_JSON)

    _run(log, """
        PATTERN E(e:"A")-[]-O(o:"item")
        SUBJECTTO o["ocel_id"] == "o2"
        FILTER o
        RETURN OCEL
    """)

    assert not log.objectExists("o2")
    assert log.numObjects() == 2
    assert log.eventExists("e2")
    assert log.numEvents() == 3
    assert log.getEORelations(event_id="e2", event_type=None,
                              object_id=None, object_type=None,
                              qualifier=None) == []


def test_filter_multiple_symbols(filter_log):
    """FILTER e, o removes both bound entities in one clause."""
    _run(filter_log, """
        PATTERN E(e:"A")-[]-O(o:"item")
        SUBJECTTO e["ocel_id"] == "e2"
        FILTER e, o
        RETURN OCEL
    """)

    assert not filter_log.eventExists("e2")
    assert not filter_log.objectExists("o2")
    assert filter_log.numEvents() == 2
    assert filter_log.numObjects() == 2


def test_filter_keeps_other_entities_relations():
    """An object related to a deleted event AND a surviving event keeps
    exactly the relation to the survivor."""
    log_json = copy.deepcopy(FILTER_LOG_JSON)
    log_json["objects"].append(
        {"id": "o_shared", "type": "item", "attributes": [], "relationships": []})
    # o_shared is connected to e1 AND e2; filtering e2 keeps the e1 relation
    log_json["events"][0]["relationships"].append(
        {"objectId": "o_shared", "qualifier": "item"})
    log_json["events"][1]["relationships"].append(
        {"objectId": "o_shared", "qualifier": "item"})
    log = make_log(log_json)

    _run(log, FILTER_E2_QUERY)

    assert not log.eventExists("e2")
    assert log.objectExists("o_shared")
    assert log.numObjects() == 4        # nothing object-side is ever deleted
    rels = log.getEORelations(event_id=None, event_type=None,
                              object_id="o_shared", object_type=None,
                              qualifier=None)
    assert [(r[0], r[2]) for r in rels] == [("e1", "o_shared")]


def test_filter_removes_oo_relations_of_deleted_object():
    """Deleting an object also removes its object-to-object relations, in
    both directions; the partner objects survive."""
    log_json = copy.deepcopy(FILTER_LOG_JSON)
    # o2 -> o1 and o3 -> o2
    log_json["objects"][1]["relationships"].append(
        {"objectId": "o1", "qualifier": "oo_out"})
    log_json["objects"][2]["relationships"].append(
        {"objectId": "o2", "qualifier": "oo_in"})
    log = make_log(log_json)

    _run(log, """
        PATTERN E(e:"A")-[]-O(o:"item")
        SUBJECTTO o["ocel_id"] == "o2"
        FILTER o
        RETURN OCEL
    """)

    assert not log.objectExists("o2")
    assert log.objectExists("o1")
    assert log.objectExists("o3")
    assert log.getOORelations(source_id=None, source_type=None,
                              target_id=None, target_type=None,
                              qualifier=None) == []
