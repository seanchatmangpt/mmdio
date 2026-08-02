"""Detect Mermaid diagram types from source text."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Final

# Values are parser-internal IDs for executable diagrams and canonical registry
# IDs for registered-but-unsupported diagrams. More-specific variants must
# precede their base syntax.
_PATTERNS: Final[tuple[tuple[str, str], ...]] = (
    ("classDiagram-v2", r"^\s*classDiagram-v2\b"),
    ("state", r"^\s*stateDiagram-v2\b"),
    ("flowchart-v2", r"^\s*flowchart-v2\b"),
    ("flowchart-elk", r"^\s*flowchart-elk\b"),
    ("radar", r"^\s*radar(?:-beta)?\b"),
    ("sankey", r"^\s*sankey(?:-beta)?\b"),
    ("treemap", r"^\s*treemap(?:-beta)?\b"),
    ("venn", r"^\s*venn(?:-beta)?\b"),
    ("xychart", r"^\s*xychart(?:-beta)?\b"),
    ("block", r"^\s*block(?:-beta)?\b"),
    ("c4", r"^\s*C4(?:Context|Container|Component|Dynamic|Deployment|Diagram)\b"),
    ("class", r"^\s*classDiagram\b"),
    ("er", r"^\s*erDiagram\b"),
    ("flowchart", r"^\s*(?:flowchart|graph)\b"),
    ("gantt", r"^\s*gantt\b"),
    ("git", r"^\s*gitGraph\b"),
    ("info", r"^\s*info\b"),
    ("journey", r"^\s*journey\b"),
    ("kanban", r"^\s*kanban\b"),
    ("mindmap", r"^\s*mindmap\b"),
    ("packet", r"^\s*packet\b"),
    ("pie", r"^\s*pie\b"),
    ("quadrantChart", r"^\s*quadrantChart\b"),
    ("requirement", r"^\s*requirementDiagram\b"),
    ("sequence", r"^\s*sequenceDiagram\b"),
    ("state", r"^\s*stateDiagram\b"),
    ("timeline", r"^\s*timeline\b"),
    ("treeView", r"^\s*treeView\b"),
    ("architecture", r"^\s*architecture\b"),
    ("eventmodeling", r"^\s*eventmodeling\b"),
    ("ishikawa", r"^\s*ishikawa\b"),
    ("wardley", r"^\s*wardley\b"),
    ("cynefin", r"^\s*cynefin\b"),
    ("railroad-abnf", r"^\s*railroad-abnf\b"),
    ("railroad-ebnf", r"^\s*railroad-ebnf\b"),
    ("railroad-peg", r"^\s*railroad-peg\b"),
    ("railroad", r"^\s*railroad\b"),
    ("swimlane", r"^\s*swimlane\b"),
    ("zenuml", r"^\s*zenuml\b"),
)


def detect_diagram_type(text: str) -> str:
    """Return the parser ID for executable syntax or its canonical type ID.

    Unknown input preserves the legacy flowchart fallback. Registered but
    unsupported syntax is returned by canonical ID so the parser can refuse it
    explicitly instead of silently treating it as a flowchart.
    """
    if not isinstance(text, str) or not text.strip():
        return "flowchart"

    for diagram_type, pattern in _PATTERNS:
        if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            return diagram_type
    return "flowchart"


def main() -> None:
    """Read Mermaid source from stdin or files and print the detected type."""
    filenames = sys.argv[1:]
    if not filenames:
        sys.stdout.write(f"{detect_diagram_type(sys.stdin.read())}\n")
        return

    for filename in filenames:
        path = Path(filename)
        if not path.exists():
            sys.stderr.write(f"Error: file not found: {filename}\n")
            continue
        diagram_type = detect_diagram_type(path.read_text(encoding="utf-8"))
        sys.stdout.write(f"{filename}: {diagram_type}\n")


if __name__ == "__main__":
    main()
