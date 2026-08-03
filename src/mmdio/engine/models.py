"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`."""
from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from mmdio.engine.enums import *  # noqa: F401,F403


class C4Diagram(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: Literal["c4"] = "c4"
    elements: List[C4Element] = Field(default_factory=list, description="")
    relationships: List[C4Relationship] = Field(default_factory=list, description="")
    title: Optional[str] = Field(default=None, description="")


class C4Element(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(..., description="")
    name: str = Field(..., description="")
    level: C4Level = Field(..., description="")
    description: Optional[str] = Field(default=None, description="")
    technology: Optional[str] = Field(default=None, description="")
    element_type: str = Field(default="generic", description="")


class C4Relationship(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_element: str = Field(..., description="", validation_alias=AliasChoices("from_element", "from_id"))
    to_element: str = Field(..., description="", validation_alias=AliasChoices("to_element", "to_id"))
    description: str = Field(..., description="")
    technology: Optional[str] = Field(default=None, description="")


class ClassDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str = Field(..., description="")
    members: List[ClassMember] = Field(default_factory=list, description="")
    methods: List[ClassMethod] = Field(default_factory=list, description="")
    is_interface: bool = Field(default=False, description="")
    is_abstract: bool = Field(default=False, description="")


class ClassDiagram(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: Literal["class"] = "class"
    classes: List[ClassDefinition] = Field(default_factory=list, description="")
    relationships: List[ClassRelationship] = Field(default_factory=list, description="")


class ClassMember(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str = Field(..., description="")
    type: Optional[str] = Field(default=None, description="")
    visibility: str = Field(default="+", description="")


class ClassMethod(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str = Field(..., description="")
    signature: Optional[str] = Field(default=None, description="")
    return_type: Optional[str] = Field(default=None, description="", validation_alias=AliasChoices("return_type", "type"))
    visibility: str = Field(default="+", description="")


class ClassRelationship(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_class: str = Field(..., description="")
    to_class: str = Field(..., description="")
    type: RelationshipType = Field(default=RelationshipType.ASSOCIATION, description="", validation_alias=AliasChoices("type", "relation_type"))
    label: Optional[str] = Field(default=None, description="")


class ERDiagram(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: Literal["er"] = "er"
    entities: List[Entity] = Field(default_factory=list, description="")
    relationships: List[ERRelationship] = Field(default_factory=list, description="")
    title: Optional[str] = Field(default=None, description="")


class ERRelationship(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_entity: str = Field(..., description="")
    to_entity: str = Field(..., description="")
    cardinality: CardinityType = Field(default=CardinityType.ONE_TO_MANY, description="")
    label: Optional[str] = Field(default=None, description="")


class Entity(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str = Field(..., description="")
    attributes: List[EntityAttribute] = Field(default_factory=list, description="")


class EntityAttribute(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str = Field(..., description="")
    type: Optional[str] = Field(default=None, description="")
    is_key: bool = Field(default=False, description="")
    is_nullable: bool = Field(default=True, description="")


class FlowchartDiagram(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: Literal["flowchart"] = "flowchart"
    direction: str = Field(default="TB", description="")
    nodes: List[FlowchartNode] = Field(default_factory=list, description="")
    edges: List[FlowchartEdge] = Field(default_factory=list, description="")


class FlowchartEdge(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    source: str = Field(..., description="")
    target: str = Field(..., description="")
    label: Optional[str] = Field(default=None, description="")
    style: Optional[str] = Field(default=None, description="", validation_alias=AliasChoices("style", "edge_type"))


class FlowchartNode(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(..., description="")
    label: str = Field(..., description="")
    shape: NodeShape = Field(default=NodeShape.RECTANGLE, description="", validation_alias=AliasChoices("shape", "node_type"))


class GanttChart(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: Literal["gantt"] = "gantt"
    tasks: List[GanttTask] = Field(default_factory=list, description="")
    title: Optional[str] = Field(default=None, description="")


class GanttTask(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(..., description="")
    title: str = Field(..., description="")
    start_date: str = Field(..., description="")
    end_date: str = Field(..., description="")
    status: TaskStatus = Field(default=TaskStatus.ACTIVE, description="")
    dependencies: List[str] = Field(default_factory=list, description="")
    milestone: bool = Field(default=False, description="")


class GitBranch(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str = Field(..., description="")
    commit_ids: List[str] = Field(default_factory=list, description="", validation_alias=AliasChoices("commit_ids", "commits"))
    is_main: bool = Field(default=False, description="")


class GitCommit(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(..., description="")
    message: str = Field(..., description="")
    tag: Optional[str] = Field(default=None, description="")
    branch_points: List[str] = Field(default_factory=list, description="")


class GitGraph(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: Literal["git"] = "git"
    commits: List[GitCommit] = Field(default_factory=list, description="")
    branches: List[GitBranch] = Field(default_factory=list, description="")


class Mindmap(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: Literal["mindmap"] = "mindmap"
    root: MindmapNode = Field(..., description="")
    title: Optional[str] = Field(default=None, description="")
    nodes: List[MindmapNode] = Field(default_factory=list, description="")


class MindmapNode(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(..., description="")
    label: str = Field(..., description="")
    children: List[MindmapNode] = Field(default_factory=list, description="")


class PieChart(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: Literal["pie"] = "pie"
    title: Optional[str] = Field(default=None, description="")
    slices: List[PieSlice] = Field(default_factory=list, description="")


class PieSlice(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    label: str = Field(..., description="")
    value: float = Field(..., description="")


class SankeyDiagram(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: Literal["sankey"] = "sankey"
    flows: List[SankeyFlow] = Field(default_factory=list, description="")
    title: Optional[str] = Field(default=None, description="")


class SankeyFlow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    source: str = Field(..., description="")
    target: str = Field(..., description="")
    value: float = Field(..., description="")
    label: Optional[str] = Field(default=None, description="")


class SequenceDiagram(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: Literal["sequence"] = "sequence"
    participants: List[SequenceParticipant] = Field(default_factory=list, description="")
    messages: List[SequenceMessage] = Field(default_factory=list, description="")
    title: Optional[str] = Field(default=None, description="")


class SequenceMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_participant: str = Field(..., description="", validation_alias=AliasChoices("from_participant", "from_id"))
    to_participant: str = Field(..., description="", validation_alias=AliasChoices("to_participant", "to_id"))
    label: str = Field(..., description="")
    type: MessageType = Field(default=MessageType.SYNC, description="", validation_alias=AliasChoices("type", "message_type"))
    sequence_number: Optional[int] = Field(default=None, description="")


class SequenceParticipant(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(..., description="")
    name: str = Field(..., description="")
    type: ParticipantType = Field(default=ParticipantType.PARTICIPANT, description="", validation_alias=AliasChoices("type", "participant_type"))


class State(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(..., description="")
    label: str = Field(..., description="")
    is_initial: bool = Field(default=False, description="")
    is_final: bool = Field(default=False, description="")
    entry_action: Optional[str] = Field(default=None, description="")
    exit_action: Optional[str] = Field(default=None, description="")


class StateDiagram(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: Literal["state"] = "state"
    states: List[State] = Field(default_factory=list, description="")
    transitions: List[Transition] = Field(default_factory=list, description="")
    root_state: Optional[str] = Field(default=None, description="")


class Transition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    from_state: str = Field(..., description="")
    to_state: str = Field(..., description="")
    event: Optional[str] = Field(default=None, description="")
    action: Optional[str] = Field(default=None, description="")
    guard: Optional[str] = Field(default=None, description="")


MindmapNode.model_rebuild()

MermaidDiagram = (C4Diagram | ClassDiagram | ERDiagram | FlowchartDiagram | GanttChart | GitGraph | Mindmap | PieChart | SankeyDiagram | SequenceDiagram | StateDiagram)
