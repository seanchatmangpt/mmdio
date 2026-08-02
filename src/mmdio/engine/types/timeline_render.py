"""Render function for Timeline diagrams.

Type-scoped renderer for timeline syntax.
"""

from . import timeline_models


def render_timeline(diagram: timeline_models.TimelineDiagram) -> str:
    """
    Render timeline diagram to Mermaid syntax.

    Args:
        diagram: TimelineDiagram AST

    Returns:
        str: Valid Mermaid timeline syntax

    Format:
        timeline
            title My Timeline
            2024-01-01 : Event 1
            2024-02-15 : Event 2
    """
    lines = ["timeline"]

    if diagram.title:
        lines.append(f"    title {diagram.title}")

    for event in diagram.events:
        # Escape special characters in description if needed
        desc = event.description.replace('"', '\\"')
        lines.append(f"    {event.time} : {desc}")

    return "\n".join(lines)
