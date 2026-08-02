"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`."""

from enum import StrEnum

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

class MessageType(StrEnum):
    SYNC = "sync"
    ASYNC = "async"
    RETURN = "return"
    AUTONUMBER = "autonumber"

class RelationshipType(StrEnum):
    INHERITANCE = "inheritance"
    REALIZATION = "realization"
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"
    ASSOCIATION = "association"
    DEPENDENCY = "dependency"
    LINK = "link"

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

class TaskStatus(StrEnum):
    ACTIVE = "active"
    DONE = "done"
    MILESTONE = "milestone"
    CRIT = "crit"
    ACTIVE_CRIT = "active_crit"
    DONE_CRIT = "done_crit"

class C4Level(StrEnum):
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"
    C4 = "C4"

class ParticipantType(StrEnum):
    ACTOR = "actor"
    PARTICIPANT = "participant"
    AUTONUMBER = "autonumber"
    DATABASE = "database"
    QUEUE = "queue"
