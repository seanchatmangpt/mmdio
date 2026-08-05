import datetime
import json
import logging
import re
import sqlite3
import warnings
from pathlib import Path

logger = logging.getLogger(__name__)

def index_exists(target_db, table_name, index_name):
    exists_q = (f"SELECT * FROM sqlite_master WHERE type= 'index'"
                f" and tbl_name = '{table_name}' and name = '{index_name}';")
    res = target_db.execute(exists_q)
    val = res.fetchall()
    return bool(val)

def create_index_if_not_exists(target_db, table_name, index_name, index_field):
    if not index_exists(target_db, table_name, index_name):
        index_q = f"CREATE INDEX {index_name} ON {table_name} {index_field};"
        target_db.execute(index_q)

def create_index(target_db):
    indices = [
        # e2o index
        ("event_object","idx_eo_ocel_source_target","(ocel_event_id,ocel_object_id)"),
        # e2o index the other way round: the one above leads with ocel_event_id,
        # so looking up "which events touch this object" could only scan it.
        ("event_object","idx_eo_ocel_object","(ocel_object_id)"),
        # o2o index
        ("object_object", "idx_oo_ocel_source_target", "(ocel_source_id, ocel_target_id)"),
        # ditto for the reverse direction of o2o
        ("object_object", "idx_oo_ocel_target", "(ocel_target_id)"),
        # e index
        ("event","idx_ev_ocel_id","(ocel_id)"),
        # o index
        ("object", "idx_ob_ocel_id", "(ocel_id)")
        # deliberately NOT indexing (ocel_type, ocel_id) on event/object: it makes
        # the candidate scan seek instead of scan, but it also hands the planner a
        # way to drive the e2o join from "every object of this type" rather than
        # from the bound id, which measured 15x slower on order-management. ANALYZE
        # does not recover it. Benchmark before adding it back.
    ]

    # event table index
    event_tbl_query = ("SELECT name FROM sqlite_master WHERE type='table'"
                       " AND name LIKE 'event_%' AND NOT name == 'event_map_type'  AND NOT name == 'event_object'")
    res = target_db.execute(event_tbl_query)
    ev_tables = res.fetchall()

    for ev_tbl in ev_tables:
        ev_tbl = ev_tbl[0]
        indices.append((ev_tbl,f"idx_{ev_tbl}_ocel_id","(ocel_id)"))

    # object table index
    object_tbl_query = ("SELECT name FROM sqlite_master WHERE type='table'"
                        " AND name LIKE 'object_%' AND NOT name == 'object_map_type'  AND NOT name == 'object_object'")
    res = target_db.execute(object_tbl_query)
    ob_tables = res.fetchall()

    for ob_tbl in ob_tables:
        ob_tbl = ob_tbl[0]
        indices.append((ob_tbl, f"idx_{ob_tbl}_ocel_id", "(ocel_id)"))

    # create all indices
    for idx in indices:
        create_index_if_not_exists(target_db, idx[0], idx[1], idx[2])

def map_type_slug(full_name: str):
    # regex that matches valid sqlite3 column names
    column_name_pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    if re.match(column_name_pattern, full_name):
        return full_name

    slugged = "".join(re.findall("[a-zA-Z]+", full_name))
    return slugged


def ts_to_dt(timestamp: str) -> datetime.datetime:
    """Parse an ISO 8601 timestamp string. See convert_timestamp for why
    fromisoformat comes first and why naive results are rejected."""
    try:
        parsed = datetime.datetime.fromisoformat(timestamp)
        if parsed.tzinfo is not None:
            return parsed
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        return datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")

def attribute_slag(full_name):
    # TODO: this needs a vastly bigger symbolspace. probably better to just regex match on characters,
    #  numbers and underscores and use only that.
    rmap = {" ": "",
            "(": "",
            ")": "",
            "-": ""}
    rval = full_name
    for k in rmap:
        rval = rval.replace(k, rmap[k])
    return rval


JSONOCEL_DATATYPE_STRING = "string"
JSONOCEL_DATATYPE_TIME = "time"
JSONOCEL_DATATYPE_INTEGER = "integer"
JSONOCEL_DATATYPE_FLOAT = "float"
JSONOCEL_DATATYPE_BOOLEAN = "boolean"
SQL_DATATYPE_TEXT = "TEXT"
SQL_DATATYPE_TIMESTAMP = "TIMESTAMP"
SQL_DATATYPE_INTEGER = "INTEGER"
SQL_DATATYPE_REAL = "REAL"
SQL_DATATYPE_BOOLEAN = "INTEGER"
json_to_sqlite_datatypes = {JSONOCEL_DATATYPE_STRING: SQL_DATATYPE_TEXT,
                            JSONOCEL_DATATYPE_TIME: SQL_DATATYPE_TIMESTAMP,
                            JSONOCEL_DATATYPE_INTEGER: SQL_DATATYPE_INTEGER,
                            JSONOCEL_DATATYPE_FLOAT: SQL_DATATYPE_REAL,
                            JSONOCEL_DATATYPE_BOOLEAN: SQL_DATATYPE_BOOLEAN}

TIME_EPOCH_STR = "1970-01-01T00:00:00.000Z"
EPOCH_TS = ts_to_dt(TIME_EPOCH_STR)


def statements_create_tables_general():
    statements = []

    logger.info("Generating general table structure")

    # create object_map_type
    omt = "CREATE TABLE \"object_map_type\" (`ocel_type` TEXT, `ocel_type_map` TEXT, PRIMARY KEY(`ocel_type`))"
    statements.append(omt)

    # create event_map_type
    emt = "CREATE TABLE \"event_map_type\" (`ocel_type`	TEXT, `ocel_type_map` TEXT, PRIMARY KEY(`ocel_type`))"
    statements.append(emt)

    # create event
    ev = """
        CREATE TABLE "event" 
        (`ocel_id`	TEXT, 
        `ocel_type`	TEXT, 
        PRIMARY KEY(`ocel_id`), 
        FOREIGN KEY(`ocel_type`) REFERENCES `event_map_type`(`ocel_type`))
        """
    statements.append(ev)

    # create object
    ob = """
        CREATE TABLE "object" 
        (`ocel_id` TEXT, 
        `ocel_type` TEXT, 
        FOREIGN KEY(`ocel_type`) REFERENCES `object_map_type`(`ocel_type`), 
        PRIMARY KEY(`ocel_id`))
        """
    statements.append(ob)

    # create eo
    eo = """
        CREATE TABLE "event_object" 
        (`ocel_event_id` TEXT, 
        `ocel_object_id` TEXT, 
        `ocel_qualifier` TEXT, 
        PRIMARY KEY(`ocel_event_id`,`ocel_object_id`,`ocel_qualifier`), 
        FOREIGN KEY(`ocel_event_id`) REFERENCES `event`(`ocel_id`), 
        FOREIGN KEY(`ocel_object_id`) REFERENCES `object`(`ocel_id`))
        """
    statements.append(eo)

    # create oo
    oo = """
        CREATE TABLE "object_object" 
        (`ocel_source_id`	TEXT, 
        `ocel_target_id` TEXT, 
        `ocel_qualifier` TEXT, 
        PRIMARY KEY(`ocel_source_id`,`ocel_target_id`,`ocel_qualifier`), 
        FOREIGN KEY(`ocel_source_id`) REFERENCES `object`(`ocel_id`), 
        FOREIGN KEY(`ocel_target_id`) REFERENCES `object`(`ocel_id`))
        """
    statements.append(oo)

    return statements

def statements_create_tables_event(jsoc: dict) -> (dict, list[str]):
    """
    :param jsoc: json dictionary of ocel 2.0 log
    :return: a dictionary of attribute types and a list of create table
    statements for each event's table
    """
    # store types of attributes here for correct format on insertion later
    event_attribute_type = {}

    event_tbl_statements = []

    # create event_*
    for event in jsoc["eventTypes"]:
        name_slug = map_type_slug(event["name"])

        attrib_map = {}

        for attribute in event["attributes"]:
            attrib_map[attribute["name"]] = json_to_sqlite_datatypes[attribute["type"]]

        event_attribute_type[event["name"]] = attrib_map

        attribs = [f"{attribute_slag(key)} {attrib_map[key]}," for key in attrib_map]
        attrib_str = " \n ".join(attribs)

        event_q = f"""
            CREATE TABLE "event_{name_slug}" 
            (ocel_id TEXT, 
            ocel_time TIMESTAMP, 
            {attrib_str}
            PRIMARY KEY(ocel_id))
            """

        event_tbl_statements.append(event_q)

    return event_attribute_type, event_tbl_statements


def statements_create_tables_object(jsoc: dict) -> (dict, list[str]):
    """
    :param jsoc: json dictionary of ocel 2.0 log
    :return: a dictionary of attribute types and a list of create table statements for each object's table
    """
    # store types of attributes here for correct format on insertion later
    object_attribute_type = {}

    # create object_*
    object_tbl_statements = []
    for object_dict in jsoc["objectTypes"]:
        name_slug = map_type_slug(object_dict["name"])

        attrib_map = {}

        for attribute in object_dict["attributes"]:
            attrib_map[attribute["name"]] = json_to_sqlite_datatypes[attribute["type"]]

        object_attribute_type[object_dict["name"]] = attrib_map

        attribs = [f"{attribute_slag(key)} {attrib_map[key]}," for key in attrib_map]
        attrib_str = " \n ".join(attribs)

        # TODO a bit weird that this has a foreign key on ocel_id of object
        #  but events have primary key on ocel id in ocel2-p2p,
        # order-management has no keys defined whatsoever, container logistics same as ocel2-p2p
        object_q = f"""
            CREATE TABLE "object_{name_slug}" 
            (ocel_id TEXT, 
            ocel_time TIMESTAMP, 
            {attrib_str}
            ocel_changed_field TEXT, 
            FOREIGN KEY(ocel_id) REFERENCES object(ocel_id))
            """

        object_tbl_statements.append(object_q)

    return object_attribute_type, object_tbl_statements

def statements_map_type(entity_dicts:list[dict], map_type: str):
    statements = []
    for entity_dict in entity_dicts:
        oname = entity_dict["name"]
        oslug = map_type_slug(oname)
        insert_q = f"""
            INSERT INTO {map_type}_map_type (ocel_type,ocel_type_map)
            VALUES('{oname}','{oslug}');
            """
        statements.append(insert_q)

    return statements

def format_value(val, attr_type):
    if attr_type in (SQL_DATATYPE_TEXT, SQL_DATATYPE_TIMESTAMP):
        return "'" + str(val) + "'"
    else:
        return str(val)

def statements_objects(object_dicts: list[dict], object_attribute_type: dict) -> list[str]:
    statements = []

    for object_dict in object_dicts:
        ocel_id = object_dict["id"]
        ocel_type = object_dict["type"]

        init_event_q = f"""
            INSERT INTO object (ocel_id, ocel_type)
            VALUES('{ocel_id}', '{ocel_type}');
            """

        statements.append(init_event_q)

        # collect all attribute values with timestamp 0 for
        attributes = object_dict["attributes"]

        initial_values = [attr for attr in attributes if ts_to_dt(attr["time"]) == EPOCH_TS]

        col_names = [map_type_slug(attr["name"]) for attr in initial_values]
        col_names += ["ocel_time", "ocel_id"]
        col_name_str = ",".join(col_names)

        typemap = object_attribute_type[ocel_type]

        vals = [format_value(attr["value"], typemap[attr["name"]]) for attr in initial_values]
        vals += ["'" + TIME_EPOCH_STR + "'", f"'{ocel_id}'"]
        vals_str = ",".join(vals)

        # insert initialization row
        init_insert_q = f"""
            INSERT INTO object_{map_type_slug(object_dict["type"])} ({col_name_str})
            VALUES({vals_str});
            """

        statements.append(init_insert_q)

        # now updated values
        value_updates = [attr for attr in attributes if ts_to_dt(attr["time"]) != EPOCH_TS]

        for val_update in value_updates:
            col_names = [map_type_slug(val_update["name"]), "ocel_time", "ocel_changed_field", "ocel_id"]
            col_name_str = ",".join(col_names)

            vals = [format_value(val_update["value"], typemap[val_update["name"]]), "'" + val_update["time"] + "'",
                    "'" + map_type_slug(val_update["name"]) + "'", f"'{ocel_id}'"]
            val_str = ",".join(vals)

            update_q = f"""
                INSERT INTO object_{map_type_slug(object_dict["type"])} ({col_name_str})
                VALUES({val_str});
                """

            statements.append(update_q)

        for oo_rel in object_dict["relationships"]:
            ocel_target_id = oo_rel["objectId"]
            ocel_qualifier = oo_rel["qualifier"]

            eo_insert_q = f"""
                INSERT INTO object_object (ocel_source_id, ocel_target_id, ocel_qualifier)
                VALUES('{ocel_id}','{ocel_target_id}','{ocel_qualifier}');
                """

            statements.append(eo_insert_q)

    return statements

def load_json_str(js_str: str, target_db):
    load_json_dict(json.loads(js_str), target_db)

def load_json_dict(jsoc: dict, target_db):
    logger.info("Loading from JSON")
    starttime = datetime.datetime.now()
    # new_db = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
    target_db.execute("BEGIN TRANSACTION")

    # TODO: i don't think the standard does any concrete definition of this mapping,
    #  except for mentioning it can be the identity function. in the case of the provided example logs however,
    #  it is clearly not just the identity

    def execute_statements(statements: list[str]):
        for statement in statements:
            target_db.execute(statement)

    execute_statements(statements_create_tables_general())

    event_attribute_type, event_tbl_statements = statements_create_tables_event(jsoc)
    object_attribute_type, object_tbl_statements = statements_create_tables_object(jsoc)

    execute_statements(event_tbl_statements)
    execute_statements(object_tbl_statements)

    object_map_statements = statements_map_type(jsoc["objectTypes"], "object")
    event_map_statements = statements_map_type(jsoc["eventTypes"], "event")

    execute_statements(object_map_statements)
    execute_statements(event_map_statements)

    object_statements = statements_objects(jsoc["objects"], object_attribute_type)
    execute_statements(object_statements)

    for event in jsoc["events"]:
        ocel_id = event["id"]
        ocel_type = event["type"]

        init_event_q = f"""
            INSERT INTO event (ocel_id, ocel_type)
            VALUES('{ocel_id}', '{ocel_type}');
            """

        target_db.execute(init_event_q)

        # collect all attribute values with timestamp 0 for
        attributes = event["attributes"]

        initial_values = list(attributes)

        # TODO i guess standard will just fill up not specified columns with null values
        col_names = [map_type_slug(attr["name"]) for attr in initial_values]
        col_names += ["ocel_time", "ocel_id"]

        col_name_str = ",".join(col_names)

        typemap = event_attribute_type[ocel_type]

        vals = [format_value(attr["value"], typemap[attr["name"]]) for attr in initial_values]
        vals += [ "'" + event["time"] + "'", f"'{ocel_id}'"]
        vals_str = ",".join(vals)

        # insert initialization row
        init_insert_q = f"""
            INSERT INTO event_{map_type_slug(event["type"])} ({col_name_str})
            VALUES({vals_str});
            """

        target_db.execute(init_insert_q)

        # insert eo
        for object_relationship in event["relationships"]:
            object_id = object_relationship["objectId"]
            qualifier = object_relationship["qualifier"]

            vals_str = ",".join([f"'{ocel_id}'", f"'{object_id!s}'", f"'{qualifier}'"])

            eo_insert_q = f"""
                INSERT INTO event_object (ocel_event_id, ocel_object_id, ocel_qualifier)
                VALUES({vals_str});
                """

            target_db.execute(eo_insert_q)


    target_db.execute("END TRANSACTION")

    create_index(target_db)
    sanity_check_timestamps(target_db)
    logger.info(f"Loading done in {datetime.datetime.now() - starttime}")

def load_json_file(js_filepath, target_db):
    with Path(js_filepath).open() as jsonocel_file:
        jsoc = json.load(jsonocel_file)
        load_json_dict(jsoc, target_db)


def make_inmemory_db():
    target_db = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
    return target_db

# taken and adapted from webpy who, as it seems, had the same problem
# with pythons sqlite3 datetime conversions being buggy
# TODO: give these some more graceful and expressive error handling in case
#  a timestamp does not correspond to expected format
# TODO: there is potential merit in converting these to utility functions
def adapt_datetime_iso(date_time: datetime.datetime) -> str:
    """
    Convert a Python datetime.datetime into a ISO 8601 date string. Also works with timezone-aware datetime!
    >>> adapt_datetime_iso(datetime.datetime(2023, 4, 5, 6, 7, 8, 9))
    '2023-04-05T06:07:08.000009'
    """
    return date_time.isoformat(timespec='milliseconds')


def convert_timestamp(time_stamp: bytes) -> datetime.datetime:
    """
    Convert an ISO 8601 formatted bytestring to a datetime.datetime object.
    >>> convert_timestamp(b'2023-04-05T06:07:08.000009Z')
    datetime.datetime(2023, 4, 5, 6, 7, 8, 9, tzinfo=datetime.timezone.utc)

    fromisoformat first: it is implemented in C and handles both the fractional
    and non-fractional forms. The strptime pair below used to try the fractional
    format first, so every timestamp in a log without sub-second precision cost a
    raised ValueError plus two full strptime passes — this converter runs once per
    timestamp read out of sqlite, which made it one of the hottest functions in
    the engine.

    The strptime formats stay as a fallback so nothing that parsed before stops
    parsing. Naive results are rejected: both strptime formats require %z, so a
    timestamp without an offset never used to get in, and letting one in now
    would trade an import-time failure for a TypeError when olaglead compares it
    against an aware one.
    """
    decoded = time_stamp.decode("utf-8")
    try:
        parsed = datetime.datetime.fromisoformat(decoded)
        if parsed.tzinfo is not None:
            return parsed
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(decoded, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        return datetime.datetime.strptime(decoded, "%Y-%m-%dT%H:%M:%S%z")


sqlite3.register_adapter(datetime.datetime, adapt_datetime_iso)
sqlite3.register_converter("timestamp", convert_timestamp)


def sanity_check_timestamps(target_db):
    """Sample timestamps from event tables and warn about format issues."""
    event_tbl_query = ("SELECT name FROM sqlite_master WHERE type='table'"
                       " AND name LIKE 'event_%' AND NOT name == 'event_map_type' AND NOT name == 'event_object'")
    tables = target_db.execute(event_tbl_query).fetchall()

    for (table_name,) in tables:
        rows = target_db.execute(f"SELECT ocel_time FROM {table_name} LIMIT 10").fetchall()
        for (ts_raw,) in rows:
            if ts_raw is None:
                continue
            ts = str(ts_raw)
            # check for naive timestamps (no timezone)
            try:
                datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
                warnings.warn(
                    f"Timestamp '{ts}' in {table_name} has no timezone info. "
                    f"This will cause errors when comparing with timezone-aware timestamps.",
                    stacklevel=2,
                )
                return
            except ValueError:
                pass
            # check it parses at all
            try:
                ts_to_dt(ts)
            except ValueError:
                warnings.warn(
                    f"Timestamp '{ts}' in {table_name} does not match expected ISO 8601 format "
                    f"(YYYY-MM-DDTHH:MM:SS[.f]{{+|-}}HH:MM).",
                    stacklevel=2,
                )
                return


def loadSQLITE(path: str, target_db):
    # PARSE_DECLTYPES should make sure we get actual datetime object back when querying for such
    # HOWEVER, we don't do this. python sqlite3 datetime converters are FUBR.
    # using them will raise errors because it cannot correctly handle stuff like timezones etc.
    # while https://bugs.python.org/issue43831 states it has been fixed, it crashed with the same
    # value error in python 3.12, so this is probably a regression and the converters are deprecated
    # so no future fix is to be expected


    old_db = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES,)
    query = "".join(line for line in old_db.iterdump())
    target_db.executescript(query)

    create_index(target_db)
    sanity_check_timestamps(target_db)

