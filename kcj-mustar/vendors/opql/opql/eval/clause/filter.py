import logging

import opql.lang.query
import opql.ocel.ocellog

logger = logging.getLogger(__name__)


# Removes the entities bound to the filtered symbols from the log, along with
# every E2O/O2O relation they participate in (deleteEvent/deleteObject purge
# the relation tables). Objects left without any relations afterwards
# deliberately stay in the log: deciding what happens to orphans is up to the
# user, not the engine (standard section 09, FILTER Clause Evaluation).
def do_filter(ocel: opql.ocel.ocellog.OCELLog,
              filter: opql.lang.query.Filter,
              candidate_endpoints):
    for symbolic_name in filter.entities_to_remove:
        bound_ids: set[str] = set()
        for ce in candidate_endpoints:
            value = ce.lookupSymbol(symbolic_name)
            if value is None:
                continue
            if not isinstance(value, str):
                logger.warning("FILTER %s: bound value %r is not an entity id,"
                               " skipping", symbolic_name, value)
                continue
            bound_ids.add(value)

        if not bound_ids:
            logger.warning("FILTER %s: no entities bound to this symbol,"
                           " nothing to remove", symbolic_name)

        for entity_id in bound_ids:
            if ocel.eventExists(entity_id):
                ocel.deleteEvent(entity_id)
            elif ocel.objectExists(entity_id):
                ocel.deleteObject(entity_id)
            else:
                # either already removed by an earlier deletion in this FILTER
                # run, or bound to something that is not an entity id (e.g. a
                # relation qualifier - filtering relations is not supported yet)
                logger.debug("FILTER: %r is not a known event or object id,"
                             " skipping", entity_id)
