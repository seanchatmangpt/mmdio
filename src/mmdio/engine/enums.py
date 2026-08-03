"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

Source: packs/mmdio-pack/templates/generated_enums.py.tmpl
Derived from: packs/mmdio-pack/ontology.ttl (mer:PythonEnum / mer:EnumMember)

Each enum's member VALUE is chosen, where possible, to already equal the
Mermaid render token for that member (see the field-shape vocabulary
comment in ontology.ttl) — so fields typed with these enums render
correctly via plain f-string substitution, no separate token lookup.
Where a real diagram type needs token != label, that enum's ontology
comment says so explicitly rather than leaving it to be discovered.

Uses enum.StrEnum (3.11+), not `class X(str, Enum)`: on Python 3.11+ the
latter's f-string/str() output changed to "ClassName.MEMBER" instead of
the plain value (confirmed by direct test against this project's Python
3.13 runtime — a real bug caught by the enum verification probe, not a
theoretical concern). StrEnum is the only mixin that still formats as the
bare string value, which the render-body template's f-string substitution
depends on.
"""

from enum import StrEnum



class C4Level(StrEnum):


    C1 = "C1"

    C2 = "C2"

    C3 = "C3"

    C4 = "C4"



class CardinityType(StrEnum):


    ONE_TO_ONE = "one_to_one"

    ONE_TO_MANY = "one_to_many"

    MANY_TO_ONE = "many_to_one"

    MANY_TO_MANY = "many_to_many"

    MANY_TO_MANY_MARKED = "many_to_many_marked"

    ZERO_OR_ONE = "zero_or_one"

    ONE = "one"

    ZERO_OR_MANY = "zero_or_many"

    MANY = "many"



class MessageType(StrEnum):


    SYNC = "sync"

    ASYNC = "async"

    RETURN = "return"

    AUTONUMBER = "autonumber"



class NodeShape(StrEnum):


    RECTANGLE = "rectangle"

    CIRCLE = "circle"

    ELLIPSE = "ellipse"

    DIAMOND = "diamond"

    HEXAGON = "hexagon"

    PARALLELOGRAM = "parallelogram"

    TRAPEZOID = "trapezoid"

    DOCUMENT = "document"

    CYLINDER = "cylinder"

    SUBROUTINE = "subroutine"



class ParticipantType(StrEnum):


    ACTOR = "actor"

    PARTICIPANT = "participant"

    AUTONUMBER = "autonumber"

    DATABASE = "database"

    QUEUE = "queue"



class RelationshipType(StrEnum):


    INHERITANCE = "inheritance"

    REALIZATION = "realization"

    COMPOSITION = "composition"

    AGGREGATION = "aggregation"

    ASSOCIATION = "association"

    DEPENDENCY = "dependency"

    LINK = "link"



class TaskStatus(StrEnum):


    ACTIVE = "active"

    DONE = "done"

    MILESTONE = "milestone"

    CRIT = "crit"

    ACTIVE_CRIT = "active_crit"

    DONE_CRIT = "done_crit"



