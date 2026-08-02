"""Pydantic models for Timeline diagrams.

Type-scoped models for timeline AST representation.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class TimelineEvent(BaseModel):
    """Represents an event in a timeline."""

    time: str = Field(..., description="Event time/date (e.g., 2024-01-01, January, Q1)")
    description: str = Field(
        ...,
        description="Event description or label"
    )


class TimelineDiagram(BaseModel):
    """
    Represents a Timeline diagram.

    Timeline diagrams visualize events along a time axis, useful for project
    schedules, historical events, or sequential milestones.

    Attributes:
        type: Discriminator field, always "timeline"
        title: Optional timeline title
        events: List of timeline events with time and description
    """

    type: Literal["timeline"] = "timeline"
    title: Optional[str] = Field(
        default=None,
        description="Optional timeline title"
    )
    events: List[TimelineEvent] = Field(
        default_factory=list,
        description="List of timeline events"
    )
