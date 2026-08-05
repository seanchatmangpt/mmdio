import datetime
import logging
import re

from opql.exceptions import OPQLDataError, OPQLTypeError

logger = logging.getLogger(__name__)

_VALID_ENTITY_TYPES = frozenset({"object", "event"})
_IDENTIFIER_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def _check_entity_type(t: str) -> str:
    if t not in _VALID_ENTITY_TYPES:
        raise ValueError(f"Invalid entity type: {t!r}")
    return t


def _check_identifier(name: str) -> str:
    if not _IDENTIFIER_RE.match(name):
        raise ValueError(f"Invalid SQL identifier: {name!r}")
    return name


def _build_optional_where(filters: list[tuple[str, object]]) -> tuple[str, list]:
    """Build a parameterized WHERE clause from (column, value) pairs, skipping None values.

    Returns ("", []) when no active filters — caller can safely append to any query.
    """
    active = [(col, val) for col, val in filters if val is not None]
    if not active:
        return "", []
    clause = " WHERE " + " AND ".join(f"{col}=?" for col, _ in active)
    return clause, [val for _, val in active]


class OCELEntity:
    # ocel_type is required: the only constructors are OCELLog.getEvent/getObject,
    # which must resolve the type anyway to pick map_type. Passing it makes
    # getType() free and turns "the caller already knows this" into an invariant.
    def __init__(self, ocel_id: str, map_type: str, dbconnection, ocel_type: str):
        self.dbconnection = dbconnection
        self.ocel_id = ocel_id
        self.map_type = map_type
        self.ocel_type = ocel_type


class OCELObject(OCELEntity):
    def getType(self) -> str:
        return self.ocel_type

    def getPropertyValue(self, property: str, version: datetime.datetime):
        # TODO: brutish hack to fix querying for properties
        if not isinstance(version, datetime.datetime):
            raise OPQLTypeError(f"Invalid timestamp type: expected datetime, got {type(version).__name__}")

        prop_timestamp = version + datetime.timedelta(milliseconds=1)
        prop = _check_identifier(property)
        map_t = _check_identifier(self.map_type)

        select_q = f"""
        SELECT {prop} FROM object_{map_t}
        WHERE ocel_id=? AND {prop} IS NOT NULL AND ocel_time <= ?
        ORDER BY ocel_time DESC LIMIT 1
        """

        try:
            res = self.dbconnection.execute(
                select_q,
                (self.ocel_id, prop_timestamp.isoformat(timespec='milliseconds'))
            )
            value_row = res.fetchone()

            if value_row is None:
                return None

            value = value_row[0]
            return value
        except Exception as e:
            logger.exception("Database query failed: %s", select_q)
            raise OPQLDataError(f"Database query failed for object '{self.ocel_id}'") from e

    def getFullHistory(self):
        map_t = _check_identifier(self.map_type)
        select_q = f"""
                SELECT ocel_time FROM object_{map_t}
                WHERE ocel_id=?
                ORDER BY ocel_time ASC
                """

        try:
            res = self.dbconnection.execute(select_q, (self.ocel_id,))

            vals = res.fetchall()
            return [row[0] for row in vals]
        except Exception as e:
            logger.exception("Database query failed: %s", select_q)
            raise OPQLDataError(f"Database query failed for object '{self.ocel_id}'") from e

    def getAttributeHistory(self, attribute: str):
        map_t = _check_identifier(self.map_type)
        select_q = f"""
                  SELECT ocel_time FROM object_{map_t}
                  WHERE ocel_id=? AND ocel_changed_field=?
                  ORDER BY ocel_time ASC
                  """

        try:
            res = self.dbconnection.execute(select_q, (self.ocel_id, attribute))

            vals = res.fetchall()
            return [row[0] for row in vals]
        except Exception as e:
            logger.exception("Database query failed: %s", select_q)
            raise OPQLDataError(f"Database query failed for object '{self.ocel_id}'") from e


class OCELEvent(OCELEntity):
    def getType(self) -> str:
        return self.ocel_type

    def getPropertyValue(self, property: str):
        # self.map_type is already the event_map_type lookup result the caller
        # resolved when constructing us — re-querying it per property access was
        # the single hottest redundant statement in the engine.
        prop = _check_identifier(property)
        map_t = _check_identifier(self.map_type)
        prop_q = f"SELECT {prop} FROM event_{map_t} WHERE ocel_id=?"
        res = self.dbconnection.execute(prop_q, (self.ocel_id,))
        row = res.fetchone()
        propval = row[0]
        return propval


class OCELLog:
    def __init__(self, dbconnection):
        self.dbpath = ""
        self.dbconnection = dbconnection
        # type->map-table lookups are constant for the log's lifetime: types are
        # fixed at import and FILTER only ever deletes instances, never types.
        # Memoized here to kill the per-row re-scans of {event,object}_map_type.
        self._map_type_cache: dict[str, dict[str, str]] = {}
        # id->type maps, bulk-loaded on first use (one query per entity kind
        # instead of one per id). Unlike the map-type cache these DO go stale on
        # deletion, so delete{Event,Object} evict from them.
        self._entity_type_cache: dict[str, dict[str, str]] = {}
        # id->ocel_time for events, same deal. Events have exactly one timestamp
        # each; objects are versioned and deliberately excluded. None means "not
        # loaded yet", which an empty log would otherwise be indistinguishable from.
        self._event_time_cache: dict[str, datetime.datetime] | None = None

    def numObjects(self) -> int:
        res = self.dbconnection.execute("SELECT COUNT(*) FROM object")
        num_objects = res.fetchone()[0]
        return num_objects

    def numEvents(self) -> int:
        res = self.dbconnection.execute("SELECT COUNT(*) FROM event")
        num_events = res.fetchone()[0]
        return num_events

    def types(self, type: str):
        t = _check_entity_type(type)
        return self.dbconnection.execute(f"SELECT ocel_type FROM {t}_map_type")

    def objectTypes(self):
        return self.types("object")

    def eventTypes(self):
        return self.types("event")

    # only here to avoid copy pasta
    def _mapType(self, type: str) -> dict[str, str]:
        """ocel_type -> table suffix for the given entity kind, memoized.

        Private, and returns the live cache: every caller wants a single suffix,
        which mapTypeOf() hands back as an (immutable) string. Exposing the dict
        would mean either copying it on every lookup or letting a caller's
        mutation silently corrupt every later getEvent/getObject.
        """
        t = _check_entity_type(type)

        cached = self._map_type_cache.get(t)
        if cached is None:
            res = self.dbconnection.execute(f"SELECT ocel_type, ocel_type_map FROM {t}_map_type")
            cached = {entry[0]: entry[1] for entry in res}
            self._map_type_cache[t] = cached

        return cached

    def mapTypeOf(self, type: str, ocel_type: str | None) -> str | None:
        """Table suffix for one ocel_type, or None if the log has no such type."""
        if ocel_type is None:
            return None
        return self._mapType(type).get(ocel_type)

    def objectMapTypeOf(self, ocel_type: str | None) -> str | None:
        return self.mapTypeOf("object", ocel_type)

    def eventMapTypeOf(self, ocel_type: str | None) -> str | None:
        return self.mapTypeOf("event", ocel_type)

    def _entityTypes(self, type: str) -> dict[str, str]:
        """id -> ocel_type for every entity of the given kind, loaded in one query.

        The pattern matcher probes types once per candidate row; doing that as
        individual SELECTs dominated the query count. Loaded lazily so logs that
        are never type-probed pay nothing.

        Returns the live cache, not a copy: this is on the hot path and every
        caller is read-only (see getObjectType/getEventType/objectExists/
        eventExists). Mutating the result corrupts the cache — don't. Same
        reasoning as _mapType(), which is private for exactly this reason.
        """
        t = _check_entity_type(type)

        cached = self._entity_type_cache.get(t)
        if cached is None:
            res = self.dbconnection.execute(f"SELECT ocel_id, ocel_type FROM {t}")
            cached = {row[0]: row[1] for row in res.fetchall()}
            self._entity_type_cache[t] = cached

        return cached

    def _eventTimes(self) -> dict[str, datetime.datetime]:
        """ocel_id -> ocel_time for every event, loaded in one query.

        ocel_time is not a column of `event`; it sits in the per-type
        event_<map> tables, one row per event. Reading it per event is what made
        olaglead quadratic — it needs the timestamp of every event sharing an
        object, for every row. UNIONing the type tables once and keeping the
        result resident replaces all of that with dict lookups.

        Objects are deliberately not covered: object_<map> is versioned, so an
        object has a timestamp per revision rather than one timestamp.
        """
        if self._event_time_cache is None:
            # sorted for a deterministic statement, which the SQL-count tests pin
            suffixes = sorted(set(self._mapType("event").values()))
            times: dict[str, datetime.datetime] = {}
            if suffixes:
                union = " UNION ALL ".join(
                    f"SELECT ocel_id, ocel_time FROM event_{_check_identifier(s)}"
                    for s in suffixes)
                res = self.dbconnection.execute(union)
                times = {row[0]: row[1] for row in res.fetchall()}
            self._event_time_cache = times

        return self._event_time_cache

    def _forgetEntity(self, type: str, ocel_id: str) -> None:
        """Drop a deleted entity from the id->type and id->time caches."""
        t = _check_entity_type(type)
        cached = self._entity_type_cache.get(t)
        if cached is not None:
            cached.pop(ocel_id, None)
        if t == "event" and self._event_time_cache is not None:
            self._event_time_cache.pop(ocel_id, None)

    def getObjectType(self, ocel_id) -> str | None:
        return self._entityTypes("object").get(ocel_id)

    def getEventType(self, ocel_id) -> str | None:
        return self._entityTypes("event").get(ocel_id)

    def objectExists(self, ocel_id: str):
        """str ids only. The SQL this replaced compared against a TEXT column, so
        sqlite's affinity rules quietly coerced an int probe (5 matched '5');
        dict lookup does not. Callers are expected to have a real id in hand —
        FILTER discards non-str bindings before it gets here."""
        return ocel_id in self._entityTypes("object")

    def eventExists(self, ocel_id: str):
        """str ids only, same as objectExists."""
        return ocel_id in self._entityTypes("event")

    def getObject(self, ocel_id: str) -> OCELObject | None:
        ot = self.getObjectType(ocel_id)
        map_type = self.objectMapTypeOf(ot)

        if ot is None or map_type is None:
            return None

        return OCELObject(ocel_id, map_type, self.dbconnection, ot)

    def getEvent(self, ocel_id: str) -> OCELEvent | None:
        et = self.getEventType(ocel_id)
        map_type = self.eventMapTypeOf(et)

        if et is None or map_type is None:
            return None

        return OCELEvent(ocel_id, map_type, self.dbconnection, et)

    def getEventIdsByType(self, ocel_type: str) -> list[str]:
        res = self.dbconnection.execute(
            "SELECT ocel_id FROM event WHERE ocel_type=?", (ocel_type,)
        )
        rval = res.fetchall()
        return [row[0] for row in rval]

    def getObjectIdsByType(self, ocel_type: str) -> list[str]:
        res = self.dbconnection.execute(
            "SELECT ocel_id FROM object WHERE ocel_type=?", (ocel_type,)
        )
        rval = res.fetchall()
        return [row[0] for row in rval]

    def getEventIds(self) -> list[str]:
        res = self.dbconnection.execute("SELECT ocel_id FROM event")
        rval = res.fetchall()
        return [row[0] for row in rval]

    def getObjectIds(self) -> list[str]:
        res = self.dbconnection.execute("SELECT ocel_id FROM object")
        rval = res.fetchall()
        return [row[0] for row in rval]

    def getOORelations(self,
                       source_id: str | None, source_type: str | None,
                       target_id: str | None, target_type: str | None,
                       qualifier: str | None) -> list[(str, str, str, str, str)]:
        base_q = """
        SELECT ocel_source_id, toB.ocel_type AS ocel_source_type,
        ocel_target_id, toA.ocel_type AS ocel_target_type,
        ocel_qualifier
        FROM object_object tOO
        INNER JOIN object toA on tOO.ocel_target_id = toA.ocel_id
        INNER JOIN object toB on tOO.ocel_source_id = toB.ocel_id
        """

        # *_type params only filter when at least one primary id/qualifier is also given —
        # preserve original behaviour where passing only source_type returns all rows.
        if source_id or target_id or qualifier:
            where, params = _build_optional_where([
                ("ocel_source_id", source_id),
                ("ocel_source_type", source_type),
                ("ocel_target_id", target_id),
                ("ocel_target_type", target_type),
                ("ocel_qualifier", qualifier),
            ])
            res = self.dbconnection.execute(base_q + where, params)
        else:
            res = self.dbconnection.execute(base_q)

        rval = res.fetchall()
        return [(row[0], row[1], row[2], row[3], row[4]) for row in rval]

    def getEORelations(self,
                       event_id: str | None, event_type: str | None,
                       object_id: str | None, object_type: str | None,
                       qualifier: str | None) -> list[(str, str, str, str, str)]:
        base_q = """
        SELECT ocel_event_id, tEv.ocel_type AS ocel_event_type,
        ocel_object_id, tOb.ocel_type AS ocel_object_type,
        ocel_qualifier
        FROM event_object tEO
        INNER JOIN event tEv on tEO.ocel_event_id = tEv.ocel_id
        INNER JOIN object tOb on tEO.ocel_object_id = tOb.ocel_id
        """

        # *_type params only filter when at least one primary id/qualifier is also given —
        # preserve original behaviour where passing only event_type returns all rows.
        if event_id or object_id or qualifier:
            where, params = _build_optional_where([
                ("ocel_event_id", event_id),
                ("ocel_event_type", event_type),
                ("ocel_object_id", object_id),
                ("ocel_object_type", object_type),
                ("ocel_qualifier", qualifier),
            ])
            res = self.dbconnection.execute(base_q + where, params)
        else:
            res = self.dbconnection.execute(base_q)

        rval = res.fetchall()
        return [(row[0], row[1], row[2], row[3], row[4]) for row in rval]

    def deleteObject(self, object_id: str):
        if not self.objectExists(object_id):
            return

        # delete object from object_<typemap>. The type is read straight from the
        # id->type map: building an OCELObject here only to call getType() on it
        # meant dereferencing a getObject() that returns None for a type with no
        # map_type row, which crashed with a bare AttributeError.
        obj_type = self.getObjectType(object_id)
        map_type = self.objectMapTypeOf(obj_type)
        if map_type is None:
            raise OPQLDataError(
                f"Cannot delete object '{object_id}': its type {obj_type!r} has no "
                f"entry in object_map_type")
        tablename = "object_" + _check_identifier(map_type)

        self.dbconnection.execute(f"DELETE FROM {tablename} WHERE ocel_id=?", (object_id,))

        # delete object from eo relations
        self.deleteEORelation(None, object_id, None)

        # delete object from oo relations
        self.deleteOORelation(object_id, None, None)
        self.deleteOORelation(None, object_id, None)

        # delete object from object table
        self.dbconnection.execute("DELETE FROM object WHERE ocel_id=?", (object_id,))

        self._forgetEntity("object", object_id)

    def deleteEvent(self, event_id: str):
        if not self.eventExists(event_id):
            return

        ev_type = self.getEventType(event_id)
        map_type = self.eventMapTypeOf(ev_type)
        if map_type is None:
            raise OPQLDataError(
                f"Cannot delete event '{event_id}': its type {ev_type!r} has no "
                f"entry in event_map_type")
        tablename = "event_" + _check_identifier(map_type)

        self.dbconnection.execute(f"DELETE FROM {tablename} WHERE ocel_id=?", (event_id,))

        # delete event from eo relations
        self.deleteEORelation(event_id, None, None)

        # delete event from event table
        self.dbconnection.execute("DELETE FROM event WHERE ocel_id=?", (event_id,))

        self._forgetEntity("event", event_id)

    def deleteEORelation(self, event_id: str | None, object_id: str | None, qualifier: str | None):
        where, params = _build_optional_where([
            ("ocel_event_id", event_id),
            ("ocel_object_id", object_id),
            ("ocel_qualifier", qualifier),
        ])
        self.dbconnection.execute("DELETE FROM event_object" + where, params)

    def deleteOORelation(self, source_id: str | None, target_id: str | None, qualifier: str | None):
        where, params = _build_optional_where([
            ("ocel_source_id", source_id),
            ("ocel_target_id", target_id),
            ("ocel_qualifier", qualifier),
        ])
        self.dbconnection.execute("DELETE FROM object_object" + where, params)

    # returns id of next/previous event w.r.t object id
    def olaglead(self,
                 event_id: str | None,
                 object_id: str | None,
                 lag: bool = True,
                 offset: int = 0,
                 etype: None | str = None):

        if event_id is None or object_id is None:
            return None

        times = self._eventTimes()

        ev_timestamp = times.get(event_id)
        if ev_timestamp is None:
            return None

        # DISTINCT because event_object has PRIMARY KEY(event, object, qualifier):
        # one event may relate to the same object under several qualifiers, which
        # is one event, not several. Without it those rows each became an entry
        # and the offset counted the same neighbour twice — olag past e4 gave
        # e3, e2, e2 instead of e3, e2, e1. order-management has 78 such pairs.
        q = """
        SELECT DISTINCT ocel_event_id
        FROM event_object tEO
        WHERE tEO.ocel_object_id == ?
        """

        res = self.dbconnection.execute(q, (object_id,))
        rval = res.fetchall()

        types = self._entityTypes("event")

        # (timestamp, id), so that sorting orders by time. This used to be
        # (id, timestamp), which silently ordered lexicographically by event id:
        # olag past "e11" would hand back "e9".
        events_w_dates = []
        for row in rval:
            neighbour_id = row[0]
            ts = times.get(neighbour_id)
            if ts is None:
                # A relation row can name an event the log does not contain. Not
                # from deleteEvent, which does cascade into event_object, nor from
                # the json importer, which derives the rows from each event's own
                # relationship list: it comes from a supplied sqlite log, which
                # loadSQLITE replays verbatim and whose FOREIGN KEY declarations
                # sqlite does not enforce (no PRAGMA foreign_keys anywhere).
                # Nothing sensible to order a dangling id by, so it drops out.
                continue
            # named rather than inlined: folding a conditional expression into a
            # larger `and` reads as though the ternary covers the whole condition
            on_the_right_side = (ts < ev_timestamp) if lag else (ts > ev_timestamp)
            if on_the_right_side and (etype is None or types.get(neighbour_id) == etype):
                events_w_dates.append((ts, neighbour_id))

        events_w_dates.sort(reverse=lag)

        if not events_w_dates:
            return None

        # offset goes into nirvana
        if offset >= len(events_w_dates):
            return None

        return events_w_dates[offset][1]
