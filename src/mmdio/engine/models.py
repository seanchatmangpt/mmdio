"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`."""
from __future__ import annotations
from typing import List,Literal,Optional
from pydantic import AliasChoices,BaseModel,ConfigDict,Field
from mmdio.engine.enums import *  # noqa: F401,F403

class FlowchartNode(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    id:str=Field(...)
    label:str=Field(...)
    shape:NodeShape=Field(default=NodeShape.RECTANGLE,validation_alias=AliasChoices("shape","node_type"))

class FlowchartEdge(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    source:str=Field(...)
    target:str=Field(...)
    label:Optional[str]=Field(default=None)
    style:Optional[str]=Field(default=None,validation_alias=AliasChoices("style","edge_type"))

class FlowchartDiagram(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    type:Literal["flowchart"]="flowchart"
    direction:str=Field(default="TB")
    nodes:List[FlowchartNode]=Field(default_factory=list)
    edges:List[FlowchartEdge]=Field(default_factory=list)

class SequenceParticipant(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    id:str=Field(...)
    name:str=Field(...)
    type:ParticipantType=Field(default=ParticipantType.PARTICIPANT,validation_alias=AliasChoices("type","participant_type"))

class SequenceMessage(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    from_participant:str=Field(...,validation_alias=AliasChoices("from_participant","from_id"))
    to_participant:str=Field(...,validation_alias=AliasChoices("to_participant","to_id"))
    label:str=Field(...)
    type:MessageType=Field(default=MessageType.SYNC,validation_alias=AliasChoices("type","message_type"))
    sequence_number:Optional[int]=Field(default=None)

class SequenceDiagram(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    type:Literal["sequence"]="sequence"
    participants:List[SequenceParticipant]=Field(default_factory=list)
    messages:List[SequenceMessage]=Field(default_factory=list)
    title:Optional[str]=Field(default=None)

class ClassMember(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    name:str=Field(...)
    type:Optional[str]=Field(default=None)
    visibility:str=Field(default="+")

class ClassMethod(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    name:str=Field(...)
    signature:Optional[str]=Field(default=None)
    return_type:Optional[str]=Field(default=None,validation_alias=AliasChoices("return_type","type"))
    visibility:str=Field(default="+")

class ClassDefinition(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    name:str=Field(...)
    members:List[ClassMember]=Field(default_factory=list)
    methods:List[ClassMethod]=Field(default_factory=list)
    is_interface:bool=Field(default=False)
    is_abstract:bool=Field(default=False)

class ClassRelationship(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    from_class:str=Field(...)
    to_class:str=Field(...)
    type:RelationshipType=Field(default=RelationshipType.ASSOCIATION,validation_alias=AliasChoices("type","relation_type"))
    label:Optional[str]=Field(default=None)

class ClassDiagram(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    type:Literal["class"]="class"
    classes:List[ClassDefinition]=Field(default_factory=list)
    relationships:List[ClassRelationship]=Field(default_factory=list)

class State(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    id:str=Field(...)
    label:str=Field(...)
    is_initial:bool=Field(default=False)
    is_final:bool=Field(default=False)
    entry_action:Optional[str]=Field(default=None)
    exit_action:Optional[str]=Field(default=None)

class Transition(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    from_state:str=Field(...)
    to_state:str=Field(...)
    event:Optional[str]=Field(default=None)
    action:Optional[str]=Field(default=None)
    guard:Optional[str]=Field(default=None)

class StateDiagram(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    type:Literal["state"]="state"
    states:List[State]=Field(default_factory=list)
    transitions:List[Transition]=Field(default_factory=list)
    root_state:Optional[str]=Field(default=None)

class EntityAttribute(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    name:str=Field(...)
    type:Optional[str]=Field(default=None)
    is_key:bool=Field(default=False)
    is_nullable:bool=Field(default=True)

class Entity(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    name:str=Field(...)
    attributes:List[EntityAttribute]=Field(default_factory=list)

class ERRelationship(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    from_entity:str=Field(...)
    to_entity:str=Field(...)
    cardinality:CardinityType=Field(default=CardinityType.ONE_TO_MANY)
    label:Optional[str]=Field(default=None)

class ERDiagram(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    type:Literal["er"]="er"
    entities:List[Entity]=Field(default_factory=list)
    relationships:List[ERRelationship]=Field(default_factory=list)
    title:Optional[str]=Field(default=None)

class GanttTask(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    id:str=Field(...)
    title:str=Field(...)
    start_date:str=Field(...)
    end_date:str=Field(...)
    status:TaskStatus=Field(default=TaskStatus.ACTIVE)
    dependencies:List[str]=Field(default_factory=list)
    milestone:bool=Field(default=False)

class GanttChart(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    type:Literal["gantt"]="gantt"
    tasks:List[GanttTask]=Field(default_factory=list)
    title:Optional[str]=Field(default=None)

class PieSlice(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    label:str=Field(...)
    value:float=Field(...)

class PieChart(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    type:Literal["pie"]="pie"
    title:Optional[str]=Field(default=None)
    slices:List[PieSlice]=Field(default_factory=list)

class GitCommit(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    id:str=Field(...)
    message:str=Field(...)
    tag:Optional[str]=Field(default=None)
    branch_points:List[str]=Field(default_factory=list)

class GitBranch(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    name:str=Field(...)
    commit_ids:List[str]=Field(default_factory=list,validation_alias=AliasChoices("commit_ids","commits"))
    is_main:bool=Field(default=False)

class GitGraph(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    type:Literal["git"]="git"
    commits:List[GitCommit]=Field(default_factory=list)
    branches:List[GitBranch]=Field(default_factory=list)

class C4Element(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    id:str=Field(...)
    name:str=Field(...)
    level:C4Level=Field(...)
    description:Optional[str]=Field(default=None)
    technology:Optional[str]=Field(default=None)
    element_type:str=Field(default="generic")

class C4Relationship(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    from_element:str=Field(...,validation_alias=AliasChoices("from_element","from_id"))
    to_element:str=Field(...,validation_alias=AliasChoices("to_element","to_id"))
    description:str=Field(...)
    technology:Optional[str]=Field(default=None)

class C4Diagram(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    type:Literal["c4"]="c4"
    elements:List[C4Element]=Field(default_factory=list)
    relationships:List[C4Relationship]=Field(default_factory=list)
    title:Optional[str]=Field(default=None)

class MindmapNode(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    id:str=Field(...)
    label:str=Field(...)
    children:List[MindmapNode]=Field(default_factory=list)

class Mindmap(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    type:Literal["mindmap"]="mindmap"
    root:MindmapNode=Field(...)
    title:Optional[str]=Field(default=None)
    nodes:List[MindmapNode]=Field(default_factory=list)

class SankeyFlow(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    source:str=Field(...)
    target:str=Field(...)
    value:float=Field(...)
    label:Optional[str]=Field(default=None)

class SankeyDiagram(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    type:Literal["sankey"]="sankey"
    flows:List[SankeyFlow]=Field(default_factory=list)
    title:Optional[str]=Field(default=None)

MindmapNode.model_rebuild()
MermaidDiagram=FlowchartDiagram|SequenceDiagram|ClassDiagram|StateDiagram|ERDiagram|GanttChart|PieChart|GitGraph|C4Diagram|Mindmap|SankeyDiagram
