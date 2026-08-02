"""Renderer for Kanban diagrams.

Type-scoped implementation: imports kanban_models, not shared models.
"""

from . import kanban_models as models


def render_kanban(d: models.KanbanDiagram) -> str:
    """
    Render kanban diagram to Mermaid syntax.

    Format:
        kanban
            section To Do
                Task A
                Task B
            section In Progress
                Task C
            section Done
                Task D

    Sections are columns; cards are items in each section.
    """
    lines = ["kanban"]

    for section in d.sections:
        lines.append(f"  section {section.name}")
        for card in section.cards:
            lines.append(f"    {card.title}")

    return "\n".join(lines)
