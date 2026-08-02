"""Oracle test for Kanban diagrams.

Validates kanban diagram rendering against real mermaid-js parser.
"""

import sys
from pathlib import Path

# Add parent test directory to path to import validate_mermaid_source
test_dir = Path(__file__).parent.parent
sys.path.insert(0, str(test_dir))

from test_oracle_roundtrip import validate_mermaid_source

# Import type-scoped kanban implementations
from mmdio.engine.types import kanban_models
from mmdio.engine.types.kanban_render import render_kanban


class TestOracleKanban:
    """Test kanban diagram rendering against mermaid-js."""

    def test_kanban_simple(self) -> None:
        """Test simple kanban with sections and cards."""
        diagram = kanban_models.KanbanDiagram(
            sections=[
                kanban_models.KanbanSection(
                    name="To Do",
                    cards=[
                        kanban_models.KanbanCard(title="Task A"),
                        kanban_models.KanbanCard(title="Task B"),
                    ]
                ),
                kanban_models.KanbanSection(
                    name="In Progress",
                    cards=[
                        kanban_models.KanbanCard(title="Task C"),
                    ]
                ),
                kanban_models.KanbanSection(
                    name="Done",
                    cards=[
                        kanban_models.KanbanCard(title="Task D"),
                    ]
                ),
            ]
        )
        source = render_kanban(diagram)
        validate_mermaid_source(source)

    def test_kanban_empty_sections(self) -> None:
        """Test kanban with empty sections."""
        diagram = kanban_models.KanbanDiagram(
            sections=[
                kanban_models.KanbanSection(name="To Do", cards=[]),
                kanban_models.KanbanSection(name="Done", cards=[]),
            ]
        )
        source = render_kanban(diagram)
        validate_mermaid_source(source)

    def test_kanban_single_card(self) -> None:
        """Test kanban with single card."""
        diagram = kanban_models.KanbanDiagram(
            sections=[
                kanban_models.KanbanSection(
                    name="In Progress",
                    cards=[
                        kanban_models.KanbanCard(title="Only Task"),
                    ]
                ),
            ]
        )
        source = render_kanban(diagram)
        validate_mermaid_source(source)
