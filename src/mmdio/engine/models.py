"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

Source: packs/mmdio-pack/templates/generated_models.py.tmpl
Derived from: packs/mmdio-pack/ontology.ttl (mer:PythonModel / mer:PythonField)

Every diagram-type AST model is a projection of the same (type, field)
matrix — see the field-shape vocabulary comment at the top of
packs/mmdio-pack/ontology.ttl before editing the source facts.
"""

from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from mmdio.engine.enums import *  # noqa: F401,F403 — enum classes referenced by fieldPyType below


class Block(BaseModel):

    """Block — generated from packs/mmdio-pack/ontology.ttl."""




    id: str = Field(..., description="Block identifier")



    label: str = Field(..., description="Block label text")



class BlockDiagram(BaseModel):

    """BlockDiagram — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["block"] = "block"



    columns: Optional[int] = Field(default=None, description="Optional column count for layout")



    blocks: List[Block] = Field(default_factory=list, description="List of blocks in the diagram")



    connections: List[Connection] = Field(default_factory=list, description="List of connections between blocks")



class C4Diagram(BaseModel):

    """C4Diagram — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["c4"] = "c4"



    title: Optional[str] = Field(default=None, description="Diagram title")



    level: C4Level = Field(..., description="C4 level (C1, C2, C3, C4)")



    elements: List[C4Element] = Field(default_factory=list, description="Systems, containers, or components")



    relationships: List[C4Relationship] = Field(default_factory=list, description="Relationships between elements")



class C4Element(BaseModel):

    """C4Element — generated from packs/mmdio-pack/ontology.ttl."""




    id: str = Field(..., description="Element identifier")



    name: str = Field(..., description="Element name")



    description: Optional[str] = Field(default=None, description="Element description")



    type: str = Field(..., description="Element type (System, Person, Container, etc.)")



class C4Relationship(BaseModel):

    """C4Relationship — generated from packs/mmdio-pack/ontology.ttl."""




    source: str = Field(..., description="Source element ID")



    target: str = Field(..., description="Target element ID")



    label: Optional[str] = Field(default=None, description="Relationship description")



class ClassDefinition(BaseModel):

    """ClassDefinition — generated from packs/mmdio-pack/ontology.ttl."""




    name: str = Field(..., description="Class/interface name")



    members: List[ClassMember] = Field(default_factory=list, description="List of class members")



    methods: List[ClassMethod] = Field(default_factory=list, description="List of class methods")



class ClassDiagram(BaseModel):

    """ClassDiagram — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["class"] = "class"



    classes: List[ClassDefinition] = Field(default_factory=list, description="List of class definitions")



    relationships: List[ClassRelationship] = Field(default_factory=list, description="List of relationships between classes")



class ClassMember(BaseModel):

    """ClassMember — generated from packs/mmdio-pack/ontology.ttl."""




    name: str = Field(..., description="Member name")



    type: Optional[str] = Field(default=None, description="Type annotation")



    visibility: str = Field(default="+", description="Visibility modifier (+, -, #, ~)")



class ClassMethod(BaseModel):

    """ClassMethod — generated from packs/mmdio-pack/ontology.ttl."""




    name: str = Field(..., description="Method name")



    signature: Optional[str] = Field(default=None, description="Full method signature")



    return_type: Optional[str] = Field(default=None, description="Return type annotation")



    visibility: str = Field(default="+", description="Visibility modifier")



class ClassRelationship(BaseModel):

    """ClassRelationship — generated from packs/mmdio-pack/ontology.ttl."""




    from_class: str = Field(..., description="Source class name")



    to_class: str = Field(..., description="Target class name")



    type: RelationshipType = Field(..., description="Type of relationship")



    label: Optional[str] = Field(default=None, description="Optional relationship label")



class Connection(BaseModel):

    """Connection — generated from packs/mmdio-pack/ontology.ttl."""




    source: str = Field(..., description="Source block ID")



    target: str = Field(..., description="Target block ID")



    arrow_type: str = Field(default="-->", description="Arrow type (-->, <--, <-->, ===, --x, o--)")



    label: Optional[str] = Field(default=None, description="Optional connection label")



class DataSeries(BaseModel):

    """DataSeries — generated from packs/mmdio-pack/ontology.ttl."""




    series_type: str = Field(..., description="Series type: line, bar, scatter, bubble")



    values: List[float | str] = Field(default_factory=list, description="Series data values")



class ERAttribute(BaseModel):

    """ERAttribute — generated from packs/mmdio-pack/ontology.ttl."""




    name: str = Field(..., description="Attribute name")



    attr_type: str = Field(..., description="Attribute type (int, string, etc.)")



class ERDiagram(BaseModel):

    """ERDiagram — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["er"] = "er"



    entities: List[EREntity] = Field(default_factory=list, description="List of entities")



    relationships: List[ERRelationship] = Field(default_factory=list, description="List of entity relationships")



class EREntity(BaseModel):

    """EREntity — generated from packs/mmdio-pack/ontology.ttl."""




    name: str = Field(..., description="Entity name")



    attributes: List[ERAttribute] = Field(default_factory=list, description="Entity attributes")



class ERRelationship(BaseModel):

    """ERRelationship — generated from packs/mmdio-pack/ontology.ttl."""




    entity_a: str = Field(..., description="First entity name")



    entity_b: str = Field(..., description="Second entity name")



    cardinality_a: str = Field(..., description="Cardinality of entity_a side")



    cardinality_b: str = Field(..., description="Cardinality of entity_b side")



    relation_type: RelationshipType = Field(..., description="Type of relationship")



class FlowchartDiagram(BaseModel):

    """FlowchartDiagram — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["flowchart"] = "flowchart"



    direction: str = Field(default="TD", description="Layout direction: TD, LR, BT, RL")



    nodes: List[FlowchartNode] = Field(default_factory=list, description="List of nodes in the flowchart")



    edges: List[FlowchartEdge] = Field(default_factory=list, description="List of edges/connections between nodes")



class FlowchartEdge(BaseModel):

    """FlowchartEdge — generated from packs/mmdio-pack/ontology.ttl."""




    source: str = Field(..., description="Source node ID")



    target: str = Field(..., description="Target node ID")



    label: Optional[str] = Field(default=None, description="Optional edge label")



    edge_type: str = Field(default="solid", description="Edge style: solid, dotted, thick")



class FlowchartNode(BaseModel):

    """FlowchartNode — generated from packs/mmdio-pack/ontology.ttl."""




    id: str = Field(..., description="Node identifier")



    label: str = Field(..., description="Node display label")



    node_type: NodeShape = Field(default=NodeShape.RECTANGLE, description="Node shape (rectangle, circle, diamond, etc.)")



class GanttChart(BaseModel):

    """GanttChart — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["gantt"] = "gantt"



    title: Optional[str] = Field(default=None, description="Chart title")



    date_format: str = Field(default="YYYY-MM-DD", description="Date format (YYYY-MM-DD, etc.)")



    tasks: List[GanttTask] = Field(default_factory=list, description="List of tasks")



class GanttDependency(BaseModel):

    """GanttDependency — generated from packs/mmdio-pack/ontology.ttl."""




    task_id: str = Field(..., description="ID of dependent task")



class GanttTask(BaseModel):

    """GanttTask — generated from packs/mmdio-pack/ontology.ttl."""




    id: str = Field(..., description="Task identifier")



    title: str = Field(..., description="Task title/name")



    status: TaskStatus = Field(..., description="Task status (active, done, milestone, crit, etc.)")



    start_date: str = Field(..., description="Task start date")



    end_date: str = Field(..., description="Task end date")



    dependencies: List[GanttDependency] = Field(default_factory=list, description="Task dependencies")



class GitBranch(BaseModel):

    """GitBranch — generated from packs/mmdio-pack/ontology.ttl."""




    name: str = Field(..., description="Branch name")



class GitCommit(BaseModel):

    """GitCommit — generated from packs/mmdio-pack/ontology.ttl."""




    id: str = Field(..., description="Commit identifier (hash)")



    message: Optional[str] = Field(default=None, description="Commit message")



class GitGraph(BaseModel):

    """GitGraph — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["git"] = "git"



    main_branch: str = Field(default="main", description="Main branch name")



    commits: List[GitCommit] = Field(default_factory=list, description="List of commits")



class KanbanCard(BaseModel):

    """KanbanCard — generated from packs/mmdio-pack/ontology.ttl."""




    title: str = Field(..., description="Card title/task name")



class KanbanDiagram(BaseModel):

    """KanbanDiagram — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["kanban"] = "kanban"



    sections: List[KanbanSection] = Field(default_factory=list, description="List of Kanban sections/columns")



class KanbanSection(BaseModel):

    """KanbanSection — generated from packs/mmdio-pack/ontology.ttl."""




    name: str = Field(..., description="Section name (e.g., To Do, In Progress)")



    cards: List[KanbanCard] = Field(default_factory=list, description="Cards in this section")



class Mindmap(BaseModel):

    """Mindmap — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["mindmap"] = "mindmap"



    root: MindmapNode = Field(..., description="Root node of the mindmap tree")



    title: Optional[str] = Field(default=None, description="Optional mindmap title")



class MindmapNode(BaseModel):

    """MindmapNode — generated from packs/mmdio-pack/ontology.ttl."""




    id: str = Field(..., description="Unique node identifier")



    label: str = Field(..., description="Node label/text")



class PieChart(BaseModel):

    """PieChart — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["pie"] = "pie"



    title: Optional[str] = Field(default=None, description="Optional chart title")



    slices: List[PieSlice] = Field(default_factory=list, description="List of pie slices")



class PieSlice(BaseModel):

    """PieSlice — generated from packs/mmdio-pack/ontology.ttl."""




    label: str = Field(..., description="Slice label")



    value: float = Field(..., description="Numeric value (percentage, count, or amount)")



class SankeyDiagram(BaseModel):

    """SankeyDiagram — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["sankey"] = "sankey"



    flows: List[SankeyFlow] = Field(default_factory=list, description="List of flows in the diagram")



class SankeyFlow(BaseModel):

    """SankeyFlow — generated from packs/mmdio-pack/ontology.ttl."""




    source: str = Field(..., description="Source node identifier")



    target: str = Field(..., description="Target node identifier")



    value: float = Field(..., description="Flow value (determines width/thickness of flow)")



class SequenceDiagram(BaseModel):

    """SequenceDiagram — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["sequence"] = "sequence"



    title: Optional[str] = Field(default=None, description="Optional diagram title")



    participants: List[SequenceParticipant] = Field(default_factory=list, description="List of sequence participants")



    messages: List[SequenceMessage] = Field(default_factory=list, description="List of messages between participants")



class SequenceMessage(BaseModel):

    """SequenceMessage — generated from packs/mmdio-pack/ontology.ttl."""




    from_id: str = Field(..., description="Source participant ID")



    to_id: str = Field(..., description="Target participant ID")



    label: Optional[str] = Field(default=None, description="Message text/label")



    message_type: MessageType = Field(..., description="Message type: sync, async, return, autonumber")



    sequence_number: int = Field(..., description="Auto-assigned message sequence number")



class SequenceParticipant(BaseModel):

    """SequenceParticipant — generated from packs/mmdio-pack/ontology.ttl."""




    id: str = Field(..., description="Participant identifier")



    name: str = Field(..., description="Participant display name")



    participant_type: ParticipantType = Field(..., description="Participant type: actor, participant")



class StateDiagram(BaseModel):

    """StateDiagram — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["state"] = "state"



    initial_state: Optional[str] = Field(default=None, description="Initial state identifier")



    states: List[StateNode] = Field(default_factory=list, description="List of states")



    transitions: List[StateTransition] = Field(default_factory=list, description="List of transitions between states")



class StateNode(BaseModel):

    """StateNode — generated from packs/mmdio-pack/ontology.ttl."""




    id: str = Field(..., description="State identifier")



    label: Optional[str] = Field(default=None, description="State display label")



class StateTransition(BaseModel):

    """StateTransition — generated from packs/mmdio-pack/ontology.ttl."""




    source: str = Field(..., description="Source state ID")



    target: str = Field(..., description="Target state ID")



    label: Optional[str] = Field(default=None, description="Transition label/trigger")



class TimelineDiagram(BaseModel):

    """TimelineDiagram — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["timeline"] = "timeline"



    title: Optional[str] = Field(default=None, description="Optional timeline title")



    events: List[TimelineEvent] = Field(default_factory=list, description="List of timeline events")



class TimelineEvent(BaseModel):

    """TimelineEvent — generated from packs/mmdio-pack/ontology.ttl."""




    time: str = Field(..., description="Event time/date (e.g., 2024-01-01, January, Q1)")



    description: str = Field(..., description="Event description or label")



class XYAxis(BaseModel):

    """XYAxis — generated from packs/mmdio-pack/ontology.ttl."""




    label: Optional[str] = Field(default=None, description="Axis label")



    values: List[float | str] = Field(default_factory=list, description="Axis values or tick marks")



    range_min: Optional[float] = Field(default=None, description="Minimum range (y-axis)")



    range_max: Optional[float] = Field(default=None, description="Maximum range (y-axis)")



class XYChartDiagram(BaseModel):

    """XYChartDiagram — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["xychart"] = "xychart"



    title: Optional[str] = Field(default=None, description="Chart title")



    x_axis: XYAxis = Field(..., description="X-axis configuration")



    y_axis: XYAxis = Field(..., description="Y-axis configuration")



    series: List[DataSeries] = Field(default_factory=list, description="Data series to plot")




MermaidDiagram = (
    BlockDiagram |

    C4Diagram |

    ClassDiagram |

    ERDiagram |

    FlowchartDiagram |

    GanttChart |

    GitGraph |

    KanbanDiagram |

    Mindmap |

    PieChart |

    SankeyDiagram |

    SequenceDiagram |

    StateDiagram |

    TimelineDiagram |

    XYChartDiagram


)
"""Union type for all supported Mermaid diagram types. Use with Pydantic discriminated unions."""

# Legacy class aliases for backwards compatibility
Entity = EREntity
EntityAttribute = ERAttribute
State = StateNode
Transition = StateTransition


