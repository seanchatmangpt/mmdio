"""Parser for Kanban diagrams.

Type-scoped implementation: imports kanban_models, not shared models.
"""

from pathlib import Path

from lark import Lark, Transformer, v_args

from . import kanban_models as models


def _load_grammar() -> str:
    """Load kanban grammar from file."""
    grammar_file = Path(__file__).parent.parent / "grammars" / "kanban.lark"
    return grammar_file.read_text(encoding="utf-8")


class KanbanTransformer(Transformer):
    """Transform kanban parse tree to KanbanDiagram."""

    def section_name(self, items: list) -> str:
        """Extract section name from pattern."""
        if items:
            return str(items[0]).strip()
        return ""

    def section_stmt(self, items: list) -> tuple:
        """Mark as section statement."""
        # After "section" keyword, we have the name
        section_name = str(items[0]).strip() if items else ""
        return ("section", section_name)

    def card_stmt(self, items: list) -> tuple:
        """Mark as card statement."""
        # The card content is just text
        card_title = str(items[0]).strip() if items else ""
        return ("card", card_title)

    def statement(self, items: list):
        """Pass through statement."""
        if items:
            return items[0]
        return None

    def diagram(self, items: list) -> models.KanbanDiagram:
        """Build kanban diagram from flat statement list."""
        sections = []
        current_section = None

        for item in items:
            if item is None:
                continue
            if isinstance(item, tuple):
                stmt_type, value = item
                if stmt_type == "section":
                    # Start a new section
                    current_section = models.KanbanSection(name=value, cards=[])
                    sections.append(current_section)
                elif stmt_type == "card":
                    # Only add card if it doesn't start with "section"
                    if not value.lower().startswith("section "):
                        if current_section is not None:
                            card = models.KanbanCard(title=value)
                            current_section.cards.append(card)
                    else:
                        # This is actually a section line that wasn't recognized
                        # Extract the section name
                        section_name = value[8:].strip()  # Remove "section " prefix
                        current_section = models.KanbanSection(name=section_name, cards=[])
                        sections.append(current_section)

        return models.KanbanDiagram(sections=sections)

    def start(self, items: list) -> models.KanbanDiagram:
        """Entry point: return diagram."""
        if items and isinstance(items[0], models.KanbanDiagram):
            return items[0]
        return models.KanbanDiagram(sections=[])


def parse_kanban(source: str) -> models.KanbanDiagram:
    """
    Parse kanban diagram source code.

    Args:
        source: Kanban diagram source as string

    Returns:
        KanbanDiagram AST

    Raises:
        lark.exceptions.LarkError: On parsing failure
    """
    grammar = _load_grammar()
    # Use Earley parser which is more flexible with ambiguous grammars
    parser = Lark(grammar, parser="earley", start="start")
    tree = parser.parse(source)
    # Apply transformer after parsing
    transformer = KanbanTransformer()
    return transformer.transform(tree)
