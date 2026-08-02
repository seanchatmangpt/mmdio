"""Pydantic models for Block diagrams (type-scoped)."""

from typing import Literal, Optional, List
from pydantic import BaseModel, Field


class Block(BaseModel):
    """Represents a block/node in a block diagram."""
    id: str = Field(..., description="Block identifier")
    label: str = Field(..., description="Block label text")


class Connection(BaseModel):
    """Represents a connection/edge between blocks."""
    source: str = Field(..., description="Source block ID")
    target: str = Field(..., description="Target block ID")
    arrow_type: str = Field(
        default="-->",
        description="Arrow type (-->, <--, <-->, ===, --x, o--)"
    )
    label: Optional[str] = Field(
        default=None,
        description="Optional connection label"
    )


class BlockDiagram(BaseModel):
    """
    Represents a Block Diagram.

    Block diagrams show blocks/components and their connections.
    Used for architecture, system design, and process flow visualization.

    Attributes:
        type: Discriminator field, always "block"
        columns: Optional column count for layout
        blocks: List of blocks in the diagram
        connections: List of connections between blocks
    """
    type: Literal["block"] = "block"
    columns: Optional[int] = Field(
        default=None,
        description="Optional column count for layout"
    )
    blocks: List[Block] = Field(
        default_factory=list,
        description="List of blocks in the diagram"
    )
    connections: List[Connection] = Field(
        default_factory=list,
        description="List of connections between blocks"
    )
