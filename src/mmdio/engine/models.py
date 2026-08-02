"""
Comprehensive Pydantic BaseModel definitions for all 11 Mermaid diagram types.

This module defines the AST representation for the mmdio engine, providing
strongly-typed models for parsing, validating, and manipulating Mermaid diagrams
programmatically.

Each diagram type has:
- A discriminator field `type: Literal["diagram_name"]` for union type matching
- Comprehensive docstrings explaining the diagram's semantics
- Nested models for contained elements (nodes, edges, messages, etc.)
- Proper type hints with Optional, List, and Enum where appropriate
"""

from enum import Enum
from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Enums for diagram-specific types
# ============================================================================


class NodeShape(str, Enum):
    """Flowchart node shape types."""
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


class MessageType(str, Enum):
    """Sequence diagram message types."""
    SYNC = "sync"           # Solid line with filled arrowhead
    ASYNC = "async"         # Dashed line with open arrowhead
    RETURN = "return"       # Dashed line with open arrowhead, return indication
    AUTONUMBER = "autonumber"  # Automatically numbered


class RelationshipType(str, Enum):
    """Class diagram relationship types."""
    INHERITANCE = "inheritance"        # --^
    REALIZATION = "realization"        # --|>
    COMPOSITION = "composition"        # --*
    AGGREGATION = "aggregation"        # --o
    ASSOCIATION = "association"        # -->
    DEPENDENCY = "dependency"          # ..>
    LINK = "link"                      # --


class CardinityType(str, Enum):
    """ER diagram cardinality types."""
    ONE_TO_ONE = "one_to_one"              # |o--o|
    ONE_TO_MANY = "one_to_many"            # |o--}|
    MANY_TO_ONE = "many_to_one"            # }|--o|
    MANY_TO_MANY = "many_to_many"          # }o--o{
    MANY_TO_MANY_MARKED = "many_to_many_marked"  # }|--{|


class TaskStatus(str, Enum):
    """Gantt chart task status types."""
    ACTIVE = "active"
    DONE = "done"
    MILESTONE = "milestone"
    CRIT = "crit"
    ACTIVE_CRIT = "active_crit"
    DONE_CRIT = "done_crit"


class C4Level(str, Enum):
    """C4 diagram context levels."""
    C1 = "C1"  # System context
    C2 = "C2"  # Container diagram
    C3 = "C3"  # Component diagram
    C4 = "C4"  # Code-level diagram


class ParticipantType(str, Enum):
    """Sequence diagram participant types."""
    ACTOR = "actor"
    PARTICIPANT = "participant"
    AUTONUMBER = "autonumber"


# ============================================================================
# 1. FLOWCHART / GRAPH DIAGRAM
# ============================================================================


class FlowchartNode(BaseModel):
    """Represents a node in a flowchart/graph diagram."""
    id: str = Field(..., description="Unique identifier for the node")
    label: str = Field(..., description="Display label/text for the node")
    shape: NodeShape = Field(
        default=NodeShape.RECTANGLE,
        description="Visual shape of the node"
    )

    class Config:
        use_enum_values = False


class FlowchartEdge(BaseModel):
    """Represents an edge/link in a flowchart/graph diagram."""
    source: str = Field(..., description="ID of the source node")
    target: str = Field(..., description="ID of the target node")
    label: Optional[str] = Field(
        default=None,
        description="Optional label on the edge"
    )
    style: Optional[str] = Field(
        default=None,
        description="Style attributes (e.g., 'solid', 'dashed', 'dotted')"
    )

    class Config:
        use_enum_values = False


class FlowchartDiagram(BaseModel):
    """
    Represents a Flowchart/Graph diagram.

    Flowcharts are directed graphs with typed nodes (shapes) and labeled edges.
    Used for process flows, algorithms, decision trees, and general digraphs.

    Attributes:
        type: Discriminator field, always "flowchart"
        direction: Flow direction (TB=top-to-bottom, LR=left-to-right, etc.)
        nodes: List of nodes with IDs, labels, and shapes
        edges: List of edges connecting nodes with optional labels/styles
    """
    type: Literal["flowchart"] = "flowchart"
    direction: str = Field(
        default="TB",
        description="Flow direction (TB, BT, LR, RL)"
    )
    nodes: List[FlowchartNode] = Field(
        default_factory=list,
        description="List of nodes in the flowchart"
    )
    edges: List[FlowchartEdge] = Field(
        default_factory=list,
        description="List of edges connecting nodes"
    )


# ============================================================================
# 2. SEQUENCE DIAGRAM
# ============================================================================


class SequenceParticipant(BaseModel):
    """Represents a participant in a sequence diagram."""
    id: str = Field(..., description="Unique identifier for the participant")
    name: str = Field(..., description="Display name of the participant")
    type: ParticipantType = Field(
        default=ParticipantType.PARTICIPANT,
        description="Type of participant (actor, participant)"
    )

    class Config:
        use_enum_values = False


class SequenceMessage(BaseModel):
    """Represents a message exchange between participants."""
    from_participant: str = Field(..., description="Source participant ID")
    to_participant: str = Field(..., description="Target participant ID")
    label: str = Field(..., description="Message label/text")
    type: MessageType = Field(
        default=MessageType.SYNC,
        description="Message type (sync, async, return)"
    )
    sequence_number: Optional[int] = Field(
        default=None,
        description="Optional auto-number sequence"
    )

    class Config:
        use_enum_values = False


class SequenceDiagram(BaseModel):
    """
    Represents a Sequence diagram (interaction diagram).

    Sequence diagrams show message exchanges (calls, returns, events) between
    participants over time. Used for modeling interactions, protocols, and
    communication flows.

    Attributes:
        type: Discriminator field, always "sequence"
        participants: List of actors/objects involved
        messages: List of message exchanges in sequence order
        title: Optional title/description
    """
    type: Literal["sequence"] = "sequence"
    participants: List[SequenceParticipant] = Field(
        default_factory=list,
        description="List of participants in the sequence"
    )
    messages: List[SequenceMessage] = Field(
        default_factory=list,
        description="List of messages in temporal order"
    )
    title: Optional[str] = Field(
        default=None,
        description="Optional sequence diagram title"
    )


# ============================================================================
# 3. CLASS DIAGRAM
# ============================================================================


class ClassMember(BaseModel):
    """Represents an attribute/member of a class."""
    name: str = Field(..., description="Member name")
    type: Optional[str] = Field(
        default=None,
        description="Type annotation (e.g., 'int', 'str', 'List[String]')"
    )
    visibility: str = Field(
        default="+",
        description="Visibility modifier (+public, -private, #protected, ~package)"
    )


class ClassMethod(BaseModel):
    """Represents a method/operation of a class."""
    name: str = Field(..., description="Method name")
    signature: Optional[str] = Field(
        default=None,
        description="Full method signature including parameters"
    )
    return_type: Optional[str] = Field(
        default=None,
        description="Return type annotation"
    )
    visibility: str = Field(
        default="+",
        description="Visibility modifier (+public, -private, #protected, ~package)"
    )


class ClassDefinition(BaseModel):
    """Represents a class or interface definition."""
    name: str = Field(..., description="Class/interface name")
    members: List[ClassMember] = Field(
        default_factory=list,
        description="List of class attributes/members"
    )
    methods: List[ClassMethod] = Field(
        default_factory=list,
        description="List of class methods/operations"
    )
    is_interface: bool = Field(
        default=False,
        description="Whether this is an interface (not a class)"
    )
    is_abstract: bool = Field(
        default=False,
        description="Whether this is an abstract class"
    )


class ClassRelationship(BaseModel):
    """Represents a relationship between two classes."""
    from_class: str = Field(..., description="Source class name")
    to_class: str = Field(..., description="Target class name")
    type: RelationshipType = Field(
        default=RelationshipType.ASSOCIATION,
        description="Type of relationship"
    )
    label: Optional[str] = Field(
        default=None,
        description="Optional relationship label"
    )

    class Config:
        use_enum_values = False


class ClassDiagram(BaseModel):
    """
    Represents a Class diagram (structural relationships).

    Class diagrams show the static structure of classes, interfaces, and their
    relationships (inheritance, composition, association, etc.). Used for
    modeling object-oriented systems and architectural design.

    Attributes:
        type: Discriminator field, always "class"
        classes: List of class/interface definitions
        relationships: List of relationships between classes
    """
    type: Literal["class"] = "class"
    classes: List[ClassDefinition] = Field(
        default_factory=list,
        description="List of class definitions"
    )
    relationships: List[ClassRelationship] = Field(
        default_factory=list,
        description="List of relationships between classes"
    )


# ============================================================================
# 4. STATE DIAGRAM
# ============================================================================


class State(BaseModel):
    """Represents a state in a state diagram."""
    id: str = Field(..., description="Unique identifier for the state")
    label: str = Field(..., description="Display label for the state")
    is_initial: bool = Field(
        default=False,
        description="Whether this is the initial state"
    )
    is_final: bool = Field(
        default=False,
        description="Whether this is a final/accepting state"
    )
    entry_action: Optional[str] = Field(
        default=None,
        description="Action to perform on entry (UML entry action)"
    )
    exit_action: Optional[str] = Field(
        default=None,
        description="Action to perform on exit (UML exit action)"
    )


class Transition(BaseModel):
    """Represents a transition between states."""
    from_state: str = Field(..., description="Source state ID")
    to_state: str = Field(..., description="Target state ID")
    event: Optional[str] = Field(
        default=None,
        description="Event that triggers the transition"
    )
    action: Optional[str] = Field(
        default=None,
        description="Action executed during the transition"
    )
    guard: Optional[str] = Field(
        default=None,
        description="Guard condition [condition]"
    )


class StateDiagram(BaseModel):
    """
    Represents a State Diagram (behavior/FSM).

    State diagrams model the behavior of entities as a set of states and
    transitions. Used for modeling state machines, workflows, and protocols.

    Attributes:
        type: Discriminator field, always "state"
        states: List of states with initial/final markers
        transitions: List of transitions with events and actions
        root_state: Optional ID of the root composite state
    """
    type: Literal["state"] = "state"
    states: List[State] = Field(
        default_factory=list,
        description="List of states"
    )
    transitions: List[Transition] = Field(
        default_factory=list,
        description="List of transitions between states"
    )
    root_state: Optional[str] = Field(
        default=None,
        description="Optional root state for composite states"
    )


# ============================================================================
# 5. ER (ENTITY-RELATIONSHIP) DIAGRAM
# ============================================================================


class EntityAttribute(BaseModel):
    """Represents an attribute of an entity."""
    name: str = Field(..., description="Attribute name")
    type: Optional[str] = Field(
        default=None,
        description="Data type (e.g., 'int', 'varchar(255)', 'date')"
    )
    is_key: bool = Field(
        default=False,
        description="Whether this is a primary key"
    )
    is_nullable: bool = Field(
        default=True,
        description="Whether this attribute can be NULL"
    )


class Entity(BaseModel):
    """Represents an entity in an ER diagram."""
    name: str = Field(..., description="Entity/table name")
    attributes: List[EntityAttribute] = Field(
        default_factory=list,
        description="List of attributes/columns"
    )


class ERRelationship(BaseModel):
    """Represents a relationship between entities."""
    from_entity: str = Field(..., description="Source entity name")
    to_entity: str = Field(..., description="Target entity name")
    cardinality: CardinityType = Field(
        default=CardinityType.ONE_TO_MANY,
        description="Cardinality constraint"
    )
    label: Optional[str] = Field(
        default=None,
        description="Optional relationship label"
    )

    class Config:
        use_enum_values = False


class ERDiagram(BaseModel):
    """
    Represents an Entity-Relationship (ER) diagram.

    ER diagrams model the structure of databases, showing entities (tables),
    attributes (columns), and relationships (foreign keys) between entities.
    Used for database schema design and documentation.

    Attributes:
        type: Discriminator field, always "er"
        entities: List of entities/tables
        relationships: List of relationships with cardinality
    """
    type: Literal["er"] = "er"
    entities: List[Entity] = Field(
        default_factory=list,
        description="List of entities"
    )
    relationships: List[ERRelationship] = Field(
        default_factory=list,
        description="List of relationships between entities"
    )


# ============================================================================
# 6. GANTT CHART
# ============================================================================


class GanttTask(BaseModel):
    """Represents a task in a Gantt chart."""
    id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title/description")
    start_date: str = Field(
        ...,
        description="Start date (YYYY-MM-DD format)"
    )
    end_date: str = Field(
        ...,
        description="End date or duration (YYYY-MM-DD or D for days)"
    )
    status: TaskStatus = Field(
        default=TaskStatus.ACTIVE,
        description="Task completion status"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="List of task IDs this task depends on"
    )
    milestone: bool = Field(
        default=False,
        description="Whether this is a milestone (zero-duration)"
    )

    class Config:
        use_enum_values = False


class GanttChart(BaseModel):
    """
    Represents a Gantt Chart (timeline/schedule).

    Gantt charts show task scheduling, dependencies, and progress over time.
    Used for project management, planning, and progress tracking.

    Attributes:
        type: Discriminator field, always "gantt"
        tasks: List of tasks with dates and dependencies
        title: Optional chart title
    """
    type: Literal["gantt"] = "gantt"
    tasks: List[GanttTask] = Field(
        default_factory=list,
        description="List of tasks in the chart"
    )
    title: Optional[str] = Field(
        default=None,
        description="Optional Gantt chart title"
    )


# ============================================================================
# 7. PIE CHART
# ============================================================================


class PieSlice(BaseModel):
    """Represents a slice in a pie chart."""
    label: str = Field(..., description="Slice label")
    value: float = Field(
        ...,
        description="Numeric value (percentage, count, or amount)"
    )


class PieChart(BaseModel):
    """
    Represents a Pie Chart.

    Pie charts show proportional composition as a circular statistical graphic
    divided into slices. Used for showing part-to-whole relationships.

    Attributes:
        type: Discriminator field, always "pie"
        title: Optional chart title
        slices: List of slices with labels and values
    """
    type: Literal["pie"] = "pie"
    title: Optional[str] = Field(
        default=None,
        description="Optional pie chart title"
    )
    slices: List[PieSlice] = Field(
        default_factory=list,
        description="List of pie slices"
    )


# ============================================================================
# 8. GIT GRAPH
# ============================================================================


class GitCommit(BaseModel):
    """Represents a commit in a git graph."""
    id: str = Field(..., description="Commit hash/ID")
    message: str = Field(..., description="Commit message")
    tag: Optional[str] = Field(
        default=None,
        description="Optional tag/version label"
    )
    branch_points: List[str] = Field(
        default_factory=list,
        description="Branch IDs that start from this commit"
    )


class GitBranch(BaseModel):
    """Represents a branch in a git graph."""
    name: str = Field(..., description="Branch name (main, develop, feature/X)")
    commit_ids: List[str] = Field(
        default_factory=list,
        description="Ordered list of commit IDs on this branch"
    )
    is_main: bool = Field(
        default=False,
        description="Whether this is the main/master branch"
    )


class GitGraph(BaseModel):
    """
    Represents a Git Graph (version control history).

    Git graphs show commit history, branching, merging, and tags. Used for
    visualizing repository structure and collaboration workflows.

    Attributes:
        type: Discriminator field, always "git"
        commits: List of commits with IDs and messages
        branches: List of branches and their commits
    """
    type: Literal["git"] = "git"
    commits: List[GitCommit] = Field(
        default_factory=list,
        description="List of commits"
    )
    branches: List[GitBranch] = Field(
        default_factory=list,
        description="List of branches"
    )


# ============================================================================
# 9. C4 DIAGRAM (CONTEXT MAPPING)
# ============================================================================


class C4Element(BaseModel):
    """Represents an element in a C4 diagram."""
    id: str = Field(..., description="Unique element identifier")
    name: str = Field(..., description="Element name")
    level: C4Level = Field(
        ...,
        description="C4 context level (C1-C4)"
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of the element's role/responsibility"
    )
    technology: Optional[str] = Field(
        default=None,
        description="Technology/implementation (e.g., 'Java Spring Boot')"
    )
    element_type: str = Field(
        default="generic",
        description="Element type (system, container, component, person)"
    )

    class Config:
        use_enum_values = False


class C4Relationship(BaseModel):
    """Represents a relationship between C4 elements."""
    from_element: str = Field(..., description="Source element ID")
    to_element: str = Field(..., description="Target element ID")
    description: str = Field(..., description="Relationship description")
    technology: Optional[str] = Field(
        default=None,
        description="Technology/protocol used (e.g., 'HTTP REST')"
    )


class C4Diagram(BaseModel):
    """
    Represents a C4 Model Diagram (architecture context mapping).

    C4 diagrams show software architecture at different levels of abstraction:
    C1 (System Context), C2 (Containers), C3 (Components), C4 (Code). Used for
    communicating architecture to different stakeholders.

    Attributes:
        type: Discriminator field, always "c4"
        elements: List of architectural elements
        relationships: List of relationships between elements
        title: Optional diagram title
    """
    type: Literal["c4"] = "c4"
    elements: List[C4Element] = Field(
        default_factory=list,
        description="List of C4 elements"
    )
    relationships: List[C4Relationship] = Field(
        default_factory=list,
        description="List of relationships between elements"
    )
    title: Optional[str] = Field(
        default=None,
        description="Optional C4 diagram title"
    )


# ============================================================================
# 10. MINDMAP
# ============================================================================


class MindmapNode(BaseModel):
    """Represents a node in a mindmap tree."""
    id: str = Field(..., description="Unique node identifier")
    label: str = Field(..., description="Node label/text")
    children: List["MindmapNode"] = Field(
        default_factory=list,
        description="Child nodes (hierarchical tree structure)"
    )


# Allow recursive definition
MindmapNode.model_rebuild()


class Mindmap(BaseModel):
    """
    Represents a Mindmap (hierarchical tree visualization).

    Mindmaps show hierarchical organization of ideas, topics, or concepts
    radiating from a central root node. Used for brainstorming, organization,
    and hierarchical knowledge representation.

    Attributes:
        type: Discriminator field, always "mindmap"
        root: Root node of the mindmap tree
        title: Optional mindmap title
    """
    type: Literal["mindmap"] = "mindmap"
    root: MindmapNode = Field(..., description="Root node of the mindmap")
    title: Optional[str] = Field(
        default=None,
        description="Optional mindmap title"
    )


# ============================================================================
# 11. SANKEY DIAGRAM
# ============================================================================


class SankeyFlow(BaseModel):
    """Represents a flow/path in a Sankey diagram."""
    source: str = Field(..., description="Source node identifier")
    target: str = Field(..., description="Target node identifier")
    value: float = Field(
        ...,
        description="Flow value (determines width/thickness of flow)"
    )
    label: Optional[str] = Field(
        default=None,
        description="Optional flow label"
    )


class SankeyDiagram(BaseModel):
    """
    Represents a Sankey Diagram (flow visualization).

    Sankey diagrams show flows of quantities (energy, money, data, etc.)
    between sources and targets, with flow width proportional to quantity.
    Used for understanding system flows and energy transformations.

    Attributes:
        type: Discriminator field, always "sankey"
        flows: List of flows between nodes
        title: Optional diagram title
    """
    type: Literal["sankey"] = "sankey"
    flows: List[SankeyFlow] = Field(
        default_factory=list,
        description="List of flows in the diagram"
    )
    title: Optional[str] = Field(
        default=None,
        description="Optional Sankey diagram title"
    )


# ============================================================================
# UNION TYPE FOR ALL DIAGRAMS
# ============================================================================


MermaidDiagram = (
    FlowchartDiagram
    | SequenceDiagram
    | ClassDiagram
    | StateDiagram
    | ERDiagram
    | GanttChart
    | PieChart
    | GitGraph
    | C4Diagram
    | Mindmap
    | SankeyDiagram
)
"""Union type for all supported Mermaid diagram types. Use with Pydantic discriminated unions."""
