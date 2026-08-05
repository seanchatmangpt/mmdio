import enum
import logging

from opql.exceptions import OPQLEvalError

logger = logging.getLogger(__name__)


class ContextEvent:
    def __init__(self, ocel_id: str | None = None, ocel_type: str | None = None):
        self.ocel_id = ocel_id
        self.ocel_type = ocel_type

    def __str__(self):
        return f"E(id: {self.ocel_id}, type: {self.ocel_type})"


class ContextObject:
    def __init__(self, ocel_id: str | None = None, ocel_type: str | None = None):
        self.ocel_id = ocel_id
        self.ocel_type = ocel_type

    def __str__(self):
        return f"O(id: {self.ocel_id}, type: {self.ocel_type})"


class ContextRelationDirection(enum.Enum):
    RIGHT = 1
    LEFT = 2
    ANY = 3


class ContextOORelation:
    def __init__(self, ocel_qualifier, direction: ContextRelationDirection):
        self.ocel_qualifier = ocel_qualifier
        self.direction = direction

    def __str__(self):
        return f"-[OO qualifier: {self.ocel_qualifier}, direction: {self.direction}]-"


class ContextEORelation:
    def __init__(self, ocel_qualifier, direction: ContextRelationDirection):
        self.ocel_qualifier = ocel_qualifier
        self.direction = direction

    def __str__(self):
        return f"-[EO qualifier: {self.ocel_qualifier}, direction: {self.direction}]-"


class ContextGraphBegin:
    def __init__(self):
        # Full representation is something that contains event and object ids and their relations
        self.fullrep = None

    def __str__(self):
        r = self.fullrep
        return f"Graph E:{r.events} O:{r.objects} EO:{r.eo_relations} OO:{r.oo_relations}"


class ContextGraphEnd:
    def __init__(self):
        self.start: ContextGraphBegin | None = None


class ResultGraph:
    def __init__(self, internal_id):
        self.internal_id = internal_id
        self.events = set()
        self.objects = set()
        self.eo_relations = set()
        self.oo_relations = set()

# adds
    def add_to_graph(self, graph_to_add):
        self.events |= graph_to_add.events
        self.objects |= graph_to_add.objects
        self.eo_relations |= graph_to_add.eo_relations
        self.oo_relations |= graph_to_add.oo_relations

    def __str__(self):
        return self.internal_id


class QueryContext:
    def __init__(self, parent=None, context_entity=None, children_symbol=None, children: list | None = None):
        # default arguments are only evaluated once when reading definition so defining [] as default argument will
        # lead to VERY wrong behaviour (one global list of children that will be shared among all QueryContext objects)
        self.children: list[QueryContext] = children if children else []

        self.parent: QueryContext | None = parent

        # ocel entity or relation - I am my parents symbol!
        self.contextEntity = context_entity
        # ocel_id for event/object or triple (ocel_id, ocel_id

        # context that holds first occurrence of this entity - None if this is where the variable was introduced
        self.first_occurrence = None

        # the symbolic name the entries in children list all refer to - if provided
        self.childrenSymbol = children_symbol

    def __str__(self):
        return f"QueryContext type:{type(self.contextEntity)} children: {self.childrenSymbol} {len(self.children)} "

    # symbol is whatever string is used to refer to said entity
    # return the corresponding context entity
    def lookupSymbol(self, symbol: str):
        # no parent means we reached context root without finding anything
        if self.parent is None:
            return None

        if self.parent.childrenSymbol == symbol:
            return self.contextEntity

        return self.parent.lookupSymbol(symbol)

    # same as lookupSymbol, but returns the QueryContext instead of the ContextEntity itself
    def lookupContext(self, symbol: str):
        # no parent means we reached context root without finding anything
        if self.parent is None:
            return None

        if self.parent.childrenSymbol == symbol:
            return self

        return self.parent.lookupContext(symbol)

    def getCandidates(self):
        if not self.children:
            return [self]

        cand_list = []
        for child in self.children:
            cand_list += child.getCandidates()

        return cand_list

    def clearChildren(self):
        for child in self.children:
            child.parent = None

        self.children = []

    # generates a map with all symbolic names and their respective bound values for this given context endpoint
    def getValueMap(self):
        val_map = {}
        current_ctx = self

        while current_ctx.parent is not None:
            val_map[current_ctx.parent.childrenSymbol] = current_ctx.contextEntity

            current_ctx = current_ctx.parent

        return val_map

    def getValueTuple(self):
        val_tpl_list = ()
        current_ctx = self

        while current_ctx.parent is not None:
            val_tpl = (current_ctx.parent.childrenSymbol, current_ctx.contextEntity)
            val_tpl_list += val_tpl

            current_ctx = current_ctx.parent

        return val_tpl_list

# will go up to length steps upwards in context to retrieve events and objects and their relations
def get_bound_entities(context, length):
    event_ids = set()
    object_ids = set()

    eo_relations = set()
    oo_relations = set()

    ctx_count = 0

    ctx_iterator: QueryContext = context
    last_context = None
    while ctx_count < length:
        if isinstance(ctx_iterator.contextEntity, ContextEvent):
            event_ids.add(ctx_iterator.contextEntity.ocel_id)

        elif isinstance(ctx_iterator.contextEntity, ContextObject):
            object_ids.add(ctx_iterator.contextEntity.ocel_id)

        elif isinstance(ctx_iterator.contextEntity, ContextOORelation):
            rel = ctx_iterator.contextEntity
            source = None
            target = None
            if rel.direction == ContextRelationDirection.RIGHT:
                source = ctx_iterator.parent.contextEntity.ocel_id
                target = last_context.contextEntity.ocel_id
            elif rel.direction == ContextRelationDirection.ANY:
                raise OPQLEvalError("ANY direction should never be bound to a resolved context")
            else:  # left
                source = last_context.contextEntity.ocel_id
                target = ctx_iterator.parent.contextEntity.ocel_id
            oo_relations.add((source, target, rel.ocel_qualifier))

        elif isinstance(ctx_iterator.contextEntity, ContextEORelation):
            rel = ctx_iterator.contextEntity
            source = None
            target = None
            if rel.direction == ContextRelationDirection.RIGHT:
                source = ctx_iterator.parent.contextEntity.ocel_id
                target = last_context.contextEntity.ocel_id
            elif rel.direction == ContextRelationDirection.ANY:
                raise OPQLEvalError("ANY direction should never be bound to a resolved context")
            else:  # left
                source = last_context.contextEntity.ocel_id
                target = ctx_iterator.parent.contextEntity.ocel_id
            eo_relations.add((source, target, rel.ocel_qualifier))

        ctx_count += 1
        last_context = ctx_iterator
        ctx_iterator = ctx_iterator.parent

    return event_ids, object_ids, eo_relations, oo_relations
