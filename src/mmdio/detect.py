"""Detect Mermaid diagram types from source text."""

from __future__ import annotations

import re
import sys

_PATTERN_TYPES: tuple[tuple[str, str], ...] = (
    (r"^\s*sequenceDiagram\b", "sequence"),
    (r"^\s*classDiagram(?:-v2)?\b", "class"),
    (r"^\s*stateDiagram(?:-v2)?\b", "state"),
    (r"^\s*state\s+", "state"),
    (r"^\s*erDiagram\b", "er"),
    (r"^\s*gantt\b", "gantt"),
    (r"^\s*pie(?:\s+chart|\s+title|\s|$)", "pie"),
    (r"^\s*gitGraph\b", "git"),
    (r"^\s*C4(?:Context|Container|Component|Dynamic|Deployment|Diagram)\b", "c4"),
    (r"^\s*mindmap\b", "mindmap"),
    (r"^\s*sankey-beta\b", "sankey"),
    (r"^\s*(?:graph|flowchart)\b", "flowchart"),
)


def detect_diagram_type(text: str) -> str:
    """Return the internal diagram type, defaulting to ``flowchart``."""
    if not isinstance(text, str) or not text.strip():
        return "flowchart"

    source = text.strip()
    for pattern, diagram_type in _PATTERN_TYPES:
        if re.search(pattern, source, re.IGNORECASE):
            return diagram_type
    return "flowchart"


def run_tests() -> bool:
    """Run the historical inline detection smoke cases."""
    cases = (
        ("graph TD\n  A --> B", "flowchart"),
        ("flowchart LR\n  A --> B", "flowchart"),
        ("sequenceDiagram\n  A->>B: Hello", "sequence"),
        ("classDiagram-v2\n  class A", "class"),
        ("stateDiagram-v2\n  [*] --> A", "state"),
        ("erDiagram\n  CUSTOMER", "er"),
        ("gantt\n  title Project", "gantt"),
        ("pie title Data", "pie"),
        ("gitGraph\n  commit", "git"),
        ("C4Context\n  Person(user)", "c4"),
        ("mindmap\n  root", "mindmap"),
        ("sankey-beta\n  A,B,10", "sankey"),
        ("", "flowchart"),
    )
    return all(detect_diagram_type(source) == expected for source, expected in cases)


if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)
