import enum


class Expression:
    """Base class for all expression nodes."""
    pass


class BinaryExpr(Expression):
    """A binary operation: left op right.
    op is a string: '+', '-', '*', '/', '%', '^',
    '==', '!=', '<', '>', '<=', '>=', 'AND', 'XOR', 'OR'
    """
    def __init__(self, op: str, left: 'Expression', right: 'Expression'):
        self.op = op
        self.left = left
        self.right = right

    def __str__(self):
        return f'({self.left} {self.op} {self.right})'


class UnaryExpr(Expression):
    """A unary operation: op operand.
    op is one of: '+', '-', 'NOT'
    """
    def __init__(self, op: str, operand: 'Expression'):
        self.op = op
        self.operand = operand

    def __str__(self):
        return f'({self.op} {self.operand})'


class AtomicExpr(Expression):
    """A leaf value: int, float, str, datetime, timedelta, bool, None,
    ValueReference, or Function."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value) if self.value is not None else 'None'



def _tagged(tag, type_) -> str:
    """The `tag:"type"` interior shared by events, objects and relations.

    Both halves are optional in the grammar, and `type` is held unquoted
    (visitR_name strips the quotes), so the quotes go back on here.

    Anonymous elements are given a synthetic tag by the visitor (`__ev0` and
    friends). Those are dropped again: SYMBOLICNAME must start with a letter,
    so a leading underscore cannot be something the writer typed, and printing
    one would yield a rendering that no longer parses.
    """
    res = tag if tag is not None and not tag.startswith('_') else ''
    if type_ is not None:
        res += f':"{type_}"'
    return res


class GraphObject:
    def __init__(self):
        self.tag = None
        self.type = None

    def __str__(self):
        return f"O({_tagged(self.tag, self.type)})"


class GraphEvent:
    def __init__(self):
        self.tag = None
        self.type = None

    def __str__(self):
        return f"E({_tagged(self.tag, self.type)})"


class GraphRelationDirection(enum.Enum):
    RIGHT = 1
    LEFT = 2
    ANY = 3


class GraphRelation:
    def __init__(self):
        self.tag = None
        self.type = None
        self.direction = None

    def __str__(self):
        interior = f"[{_tagged(self.tag, self.type)}]"
        if self.direction is GraphRelationDirection.RIGHT:
            return f"-{interior}->"
        if self.direction is GraphRelationDirection.LEFT:
            return f"<-{interior}-"
        return f"-{interior}-"


class ValueReference:
    def __init__(self):
        self.name = None
        self.property = None
        self.timestamp = None

    def __str__(self):
        if self.property is None:
            return self.name
        res_str = f'{self.name}["{self.property}"'
        if self.timestamp:
            res_str += f'@{self.timestamp}'
        res_str += ']'
        return res_str


class FunctionArgument:
    def __init__(self):
        self.arg = None

    def __str__(self):
        res = self.arg.__str__()

        if res:
            return res

        return "FARG"


class Function:
    def __init__(self):
        self.name: str | None = None
        self.arguments = []

    def __str__(self):
        res = self.name + "("

        if self.arguments:
            res += self.arguments[0].__str__()

        for i in range(1, len(self.arguments)):
            res += "," + self.arguments[i].__str__()

        return res + ")"


def _subject_to(filter_) -> str:
    """The optional trailing SUBJECTTO of a clause."""
    return f" SUBJECTTO {filter_}" if filter_ is not None else ''


class Graph:
    def __init__(self):
        self.tag = None
        self.patterns = []
        self.filter = None

    def __str__(self):
        # patterns is a list of comma-separated graphs, each a flat alternation
        # of nodes and relations that concatenate without separators
        graphs = ", ".join("".join(str(element) for element in graph) for graph in self.patterns)
        return f"PATTERN {graphs}{_subject_to(self.filter)}"


class Filter:
    def __init__(self):
        self.entities_to_remove: list = []

    def __str__(self):
        return f"FILTER {', '.join(self.entities_to_remove)}"


class When:
    def __init__(self):
        self.expression = None
        self.name = None
        self.filter = None

    def __str__(self):
        return f"WHEN {self.expression} AS {self.name}{_subject_to(self.filter)}"


class OrderDirection(enum.Enum):
    ASC = 0
    DESC = 1


class OrderItem:
    def __init__(self):
        self.expression = None
        self.direction = None

    def __str__(self):
        if self.direction is None:
            return str(self.expression)
        return f"{self.expression} {self.direction.name}"


class BinningInfinity(enum.Enum):
    NEGATIVE_INFINITY = 0
    POSITIVE_INFINITY = 1

    def __str__(self):
        return "-inf" if self is BinningInfinity.NEGATIVE_INFINITY else "inf"


class BinningInterval:
    def __init__(self):
        self.begin = None
        self.end = None
        self.include_begin = False
        self.include_end = False

        self.target = None

    def __str__(self):
        open_br = '[' if self.include_begin else '('
        close_br = ']' if self.include_end else ')'
        # an interval target is an int, a float or a string; only the last is quoted
        target = f'"{self.target}"' if isinstance(self.target, str) else str(self.target)
        return f"{open_br}{self.begin}, {self.end}{close_br} AS {target}"


class ProjectionItem:
    def __init__(self):
        self.tag = None
        self.evaluatable = None
        self.binning: list[BinningInterval] | None = None

    def __str__(self):
        res = str(self.evaluatable)
        if self.tag is not None:
            res += f" AS {self.tag}"
        if self.binning:
            res += f" BINNED({', '.join(str(interval) for interval in self.binning)})"
        return res


class Projection:
    def __init__(self):
        # wildcard denotes whether to keep context up until here
        self.wildcard = False
        self.distinct = False
        self.ctx_expansions: list[tuple] = []

        # expressions evaluating to numbers for ordering
        self.order: list[OrderItem] = []

        # integer "row" limit
        self.limit = None

    def __str__(self):
        # the wildcard may stand alone or lead a list of items
        items = (['*'] if self.wildcard else []) + [str(item) for item in self.ctx_expansions]
        res = "DISTINCT " if self.distinct else ''
        res += ", ".join(items)
        if self.order:
            res += f" ORDERBY {', '.join(str(item) for item in self.order)}"
        if self.limit is not None:
            res += f" LIMIT {self.limit}"
        return res


class Keep:
    def __init__(self):
        self.projection = None
        self.filter = None

    def __str__(self):
        return f"KEEP {self.projection}{_subject_to(self.filter)}"


class Return:
    def __init__(self):
        self.ocel: bool = False
        self.projection = None
        self.filter = None

    def __str__(self):
        if self.ocel:
            return "RETURN OCEL"
        return f"RETURN {self.projection}{_subject_to(self.filter)}"


class SubQuery:
    def __init__(self):
        self.materialized = True
        self.query: FullQuery | None = None

    def __str__(self):
        prefix = '' if self.materialized else "NOT MATERIALIZED "
        return f"{prefix}({self.query})"


class FullQuery:
    def __init__(self):
        self.graphsAndFilters = []
        self.return_rule = []

    def __str__(self):
        """Canonical single-line OPQL for this query.

        This is what names an unaliased RETURN item whose expression is an
        inline subquery, e.g. `count(PATTERN E(a)-[]-O(b) RETURN b)`, so it has
        to come back as something the reader can parse again. Whitespace and
        the writer's choice of optional tokens are not preserved.
        """
        clauses = [str(clause) for clause in self.graphsAndFilters]
        clauses.append(str(self.return_rule))
        return " ".join(clauses)
