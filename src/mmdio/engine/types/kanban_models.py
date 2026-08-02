"""Pydantic AST models for Kanban diagrams.

Type-scoped implementation: models here are NOT registered in shared models.py.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class KanbanCard(BaseModel):
    """Represents a card/task in a Kanban section."""

    title: str = Field(..., description="Card title/task name")


class KanbanSection(BaseModel):
    """Represents a section (column) in a Kanban board."""

    name: str = Field(..., description="Section name (e.g., To Do, In Progress)")
    cards: List[KanbanCard] = Field(
        default_factory=list,
        description="Cards in this section"
    )


class KanbanDiagram(BaseModel):
    """
    Represents a Kanban Diagram (task board).

    Kanban diagrams visualize workflow with columns (sections) and cards.
    Used for project management, task tracking, and workflow visualization.

    Attributes:
        type: Discriminator field, always "kanban"
        sections: List of sections (columns) with their cards
    """

    type: Literal["kanban"] = "kanban"
    sections: List[KanbanSection] = Field(
        default_factory=list,
        description="List of Kanban sections/columns"
    )
