"""Lark transformer and parser for Timeline diagrams.

Type-scoped parser for timeline syntax.
"""

from pathlib import Path

from lark import Lark, Transformer

from . import timeline_models


class TimelineTransformer(Transformer):
    """Transform timeline parse tree to TimelineDiagram."""

    def timeline_title(self, items: list) -> str:
        """Extract timeline title from TITLE_TEXT terminal."""
        title_text = str(items[0]).strip()
        return title_text

    def event(self, items: list) -> timeline_models.TimelineEvent:
        """Build a timeline event from EVENT_TIME and EVENT_DESC terminals."""
        # items[0] is the EVENT_TIME token, items[1] is EVENT_DESC token
        time_val = str(items[0]).strip()
        description_val = str(items[1]).strip()
        return timeline_models.TimelineEvent(time=time_val, description=description_val)

    def diagram(self, items: list) -> timeline_models.TimelineDiagram:
        """Build timeline diagram."""
        title = None
        events = []
        for item in items:
            if isinstance(item, str):
                title = item
            elif isinstance(item, timeline_models.TimelineEvent):
                events.append(item)
        return timeline_models.TimelineDiagram(title=title, events=events)

    def start(self, items: list) -> timeline_models.TimelineDiagram:
        """Handle start rule."""
        if items and isinstance(items[0], timeline_models.TimelineDiagram):
            return items[0]
        return timeline_models.TimelineDiagram()


def _get_timeline_parser() -> Lark:
    """Load and cache the timeline Lark parser."""
    grammar_path = Path(__file__).parent.parent / "grammars" / "timeline.lark"
    with open(grammar_path, encoding="utf-8") as f:
        grammar_text = f.read()
    return Lark(grammar_text, parser="lalr", transformer=TimelineTransformer(), start="start")


_timeline_parser_cache = None


def parse_timeline(source: str) -> timeline_models.TimelineDiagram:
    """Parse a timeline diagram from Mermaid source.

    Args:
        source: Timeline diagram source code as a string

    Returns:
        TimelineDiagram: Parsed timeline AST

    Raises:
        lark.exceptions.LarkError: If parsing fails
    """
    global _timeline_parser_cache
    if _timeline_parser_cache is None:
        _timeline_parser_cache = _get_timeline_parser()
    return _timeline_parser_cache.parse(source)
