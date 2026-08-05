import logging

import opql.lang.query
import opql.ocel.ocellog
from opql.eval.querycontext import QueryContext
from opql.exceptions import OPQLEvalError

logger = logging.getLogger(__name__)


# returns a list of possible binding contexts
def resolve_event_single(ocel: opql.ocel.ocellog.OCELLog,
                         context: QueryContext,
                         event: opql.lang.query.GraphEvent) -> list[str]:
    context_event = context.lookupSymbol(event.tag)
    if context_event is not None:
        return [context_event]

        # no such event known in context, could be "anything"
    if event.type is not None:
        # look up events of said type
        candidate_event_ids = ocel.getEventIdsByType(event.type)
        return candidate_event_ids

    # could be any event
    candidate_event_ids = ocel.getEventIds()
    return candidate_event_ids


def resolve_object_single(ocel: opql.ocel.ocellog.OCELLog,
                          context: QueryContext,
                          g_object: opql.lang.query.GraphObject) -> list[str]:
    context_object = context.lookupSymbol(g_object.tag)
    if context_object is not None:
        return [context_object]

    # no such object known in context, could be "anything"
    if g_object.type is not None:
        # look up events of said type
        candidate_object_ids = ocel.getObjectIdsByType(g_object.type)
        return candidate_object_ids

    # could be any event
    candidate_object_ids = ocel.getObjectIds()
    return candidate_object_ids


def resolve_relation(ocel: opql.ocel.ocellog.OCELLog,
                     context: QueryContext,
                     lh_entity: str,
                     relation: opql.lang.query.GraphRelation,
                     endpoint: opql.lang.query.GraphEvent | opql.lang.query.GraphObject) -> list[(str, str)]:
    # TODO: handle tagged relations!
    # check if entry is pinned to any symbolic name already, will greatly reduce result list

    lh_etype = ocel.getEventType(lh_entity)
    lh_otype = ocel.getObjectType(lh_entity)

    endpoint_id = None

    endpoint_cto = context.lookupSymbol(endpoint.tag)
    if endpoint_cto:
        if isinstance(endpoint_cto, str):
            endpoint_id = endpoint_cto
        else:
            logger.warning("Unexpected type for resolved context symbol: %s; treating as unbound",
                           type(endpoint_cto).__name__)

    if lh_otype is not None and isinstance(endpoint, opql.lang.query.GraphObject):
        result = []
        # notice that these are two if statements, not if-elif.
        # this is because an ANY direction relation must have both directions as result!
        if relation.direction == opql.lang.query.GraphRelationDirection.LEFT \
                or relation.direction == opql.lang.query.GraphRelationDirection.ANY:
            lh_result = ocel.getOORelations(source_id=endpoint_id, source_type=endpoint.type,
                                          target_id=lh_entity, target_type=lh_otype,
                                          qualifier=relation.type)
            # context object is of source_id and source_type since the relation is in reverse / left direction
            tf_res = [(resultrow[-1], resultrow[0]) for resultrow in lh_result]
            result += tf_res

        if (relation.direction == opql.lang.query.GraphRelationDirection.RIGHT or
                relation.direction == opql.lang.query.GraphRelationDirection.ANY):
            rh_result = ocel.getOORelations(source_id=lh_entity, source_type=lh_otype,
                                            target_id=endpoint_id, target_type=endpoint.type,
                                            qualifier=relation.type)
            tf_res = [(resultrow[-1],resultrow[2]) for resultrow in rh_result]
            result += tf_res

        return result

    elif lh_etype is not None and isinstance(endpoint, opql.lang.query.GraphObject):
        if relation.direction == opql.lang.query.GraphRelationDirection.LEFT:
            # objects pointing at events are illegal by definition
            return []
        elif (relation.direction == opql.lang.query.GraphRelationDirection.RIGHT or
              relation.direction == opql.lang.query.GraphRelationDirection.ANY):
            result = ocel.getEORelations(event_id=lh_entity, event_type=lh_etype,
                                         object_id=endpoint_id, object_type=endpoint.type,
                                         qualifier=relation.type)

            tf_res = [(resultrow[-1], resultrow[2]) for resultrow in result]
            return tf_res

    elif lh_otype is not None and isinstance(endpoint, opql.lang.query.GraphEvent):
        if relation.direction == opql.lang.query.GraphRelationDirection.RIGHT:
            # objects pointing at events are illegal by definition
            return []
        elif (relation.direction == opql.lang.query.GraphRelationDirection.LEFT or
              relation.direction == opql.lang.query.GraphRelationDirection.ANY):
            result = ocel.getEORelations(event_id=endpoint_id, event_type=endpoint.type,
                                         object_id=lh_entity, object_type=lh_otype,
                                         qualifier=relation.type)
            tf_res = [(resultrow[-1], resultrow[0]) for resultrow in result]
            return tf_res

    return []

# generates further candidates for given context(entity) and relationship entity pair
def generate_candidates(ocel,
                        context: QueryContext,
                        rel_entity_pair: tuple) -> list[QueryContext]:
    relation = rel_entity_pair[0]
    endpoint = rel_entity_pair[1]

    #   generate new candidates from all current candidates
    candidate = context

    new_candidates = resolve_relation(ocel, candidate, candidate.contextEntity, relation, endpoint)

    # could not generate any matching patterns - this is a dead end
    if not new_candidates:
        return []

    candidate.childrenSymbol = relation.tag

    # first, extract relations from new candidates as new context entity
    rel_names = {rel_ent[0] for rel_ent in new_candidates}

    relations_with_children = {}
    for r in rel_names:
        relations_with_children[r] = []

    for rel_ent in new_candidates:
        relations_with_children[rel_ent[0]].append(rel_ent[1])

    endpoint_candidates = []
    new_children = []
    # second, add entities that are connected via each relation to context tree
    for key in relations_with_children:
        # create relation context
        rel_context = QueryContext(parent=candidate,
                                                          context_entity=key,
                                                          children_symbol=endpoint.tag,
                                                          children=[])

        children_ctx_entities = relations_with_children[key]

        children_ctx = [QueryContext(parent=rel_context,
                                                            context_entity=ctx_entity,
                                                            children_symbol=None,
                                                            children=[])
                        for ctx_entity in children_ctx_entities]
        # add children to relation context and parent them to it
        rel_context.children = children_ctx

        # finally add subtree to parent
        new_children.append(rel_context)

        # and add leaves as new candidates
        endpoint_candidates += children_ctx

    # copying while setting this new list is of
    # IMMENSE importance since the previous approach lead to all contexts referencing the same list somehow
    candidate.children = new_children

    if not endpoint_candidates:
        raise OPQLEvalError(f"No endpoint candidates generated despite non-empty relation list: {new_candidates}")

    return endpoint_candidates


def find_children(ocel,
                  context: QueryContext,
                  rel_entity_pairs) -> list[QueryContext]:
    assert rel_entity_pairs

    next_pair = rel_entity_pairs[0]

    new_candidates: list[QueryContext] = generate_candidates(ocel, context, next_pair)

    # if there are no other relations to resolve, return.
    # also return if there are no new candidates generated,
    # essentially meaning that this context binding is not solvable
    if not new_candidates or len(rel_entity_pairs) <= 1:
        return new_candidates

    further_rel_ent_pairs = rel_entity_pairs[1:]

    endpoints: list[QueryContext] = []
    for ctx_candidate in new_candidates:
        candidate_endpoints = find_children(ocel, ctx_candidate, further_rel_ent_pairs)

        if not candidate_endpoints:
            # this candidate is a dead end, remove.
            ctx_candidate.parent.children.remove(ctx_candidate)
            # also remove parent reference to
            ctx_candidate.parent = None

            # do next candidate without adding to legitimate endpoints
            continue

        endpoints += candidate_endpoints

    return endpoints
    # find children with all generated context ends
    # get those that didn't return None
    # return these. or return None if none had valid children

    # do tail recursion


def check_cand_ctx(ocel, candidate_ctxs: list, rel_entity_pairs, resulting_endpoints):
    for candidate_ctx in candidate_ctxs:
        endpoints = find_children(ocel, candidate_ctx, rel_entity_pairs)

        if not endpoints:
            if candidate_ctx.parent:
                candidate_ctx.parent.children.remove(candidate_ctx)
            candidate_ctx.parent = None
        else:
            resulting_endpoints += endpoints

def find_pattern_candidates(ocel, context, pattern):
    if len(pattern) == 0:
        return [context]

    pattern_head = pattern[0]

    candidates = []
    if isinstance(pattern_head, opql.lang.query.GraphEvent):
        candidates = resolve_event_single(ocel, context, pattern_head)
    elif isinstance(pattern_head, opql.lang.query.GraphObject):
        candidates = resolve_object_single(ocel, context, pattern_head)
    else:
        raise OPQLEvalError(f"Unknown pattern head node type: {type(pattern_head).__name__}")

    if pattern_head.tag:
        context.childrenSymbol = pattern_head.tag

    if not candidates:
        return []

    context.children = [QueryContext(parent=context, context_entity=candidate)
                        for candidate in candidates]

    # pattern is [entity, rel, entity, rel, ...]; [1::2] = relations, [2::2] = following entities
    rel_entity_pairs = list(zip(pattern[1::2], pattern[2::2], strict=True))

    if not rel_entity_pairs:
        return context.children

    current_candidates: list[QueryContext] = context.children

    resulting_endpoints = []

    for candidate_ctx in current_candidates:
        endpoints = find_children(ocel, candidate_ctx, rel_entity_pairs)

        if not endpoints:
            if candidate_ctx.parent:
                candidate_ctx.parent.children.remove(candidate_ctx)
            candidate_ctx.parent = None
            continue

        resulting_endpoints += endpoints

    return resulting_endpoints
