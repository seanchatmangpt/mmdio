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
from mmdio.engine._generated_enums import *  # noqa: F401,F403 — enum classes referenced by fieldPyType below


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



class Connection(BaseModel):

    """Connection — generated from packs/mmdio-pack/ontology.ttl."""




    source: str = Field(..., description="Source block ID")



    target: str = Field(..., description="Target block ID")



    arrow_type: str = Field(default="-->", description="Arrow type (-->, <--, <-->, ===, --x, o--)")



    label: Optional[str] = Field(default=None, description="Optional connection label")



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



class TimelineDiagram(BaseModel):

    """TimelineDiagram — generated from packs/mmdio-pack/ontology.ttl."""


    type: Literal["timeline"] = "timeline"



    title: Optional[str] = Field(default=None, description="Optional timeline title")



    events: List[TimelineEvent] = Field(default_factory=list, description="List of timeline events")



class TimelineEvent(BaseModel):

    """TimelineEvent — generated from packs/mmdio-pack/ontology.ttl."""




    time: str = Field(..., description="Event time/date (e.g., 2024-01-01, January, Q1)")



    description: str = Field(..., description="Event description or label")



