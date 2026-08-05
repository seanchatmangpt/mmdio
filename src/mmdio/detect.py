"""Detect all registered Mermaid diagram types without a false fallback."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Final

# Parser-internal IDs are retained for the original deep parsers. Explicit
# profile variants remain distinct canonical IDs. Specific variants precede
# their base syntax.
_PATTERNS: Final[tuple[tuple[str, str], ...]] = (
    ("classDiagram-v2", r"^\s*classDiagram-v2\b"),
    ("stateDiagram-v2", r"^\s*stateDiagram-v2\b"),
    ("flowchart-v2", r"^\s*flowchart-v2\b"),
    ("flowchart-elk", r"^\s*flowchart-elk\b"),
    ("railroad-abnf", r"^\s*railroad-abnf(?:-beta)?\b"),
    ("railroad-ebnf", r"^\s*railroad-ebnf(?:-beta)?\b"),
    ("railroad-peg", r"^\s*railroad-peg(?:-beta)?\b"),
    ("radar", r"^\s*radar(?:-beta)?\b"),
    ("sankey", r"^\s*sankey(?:-beta)?\b"),
    ("treemap", r"^\s*treemap(?:-beta)?\b"),
    ("venn", r"^\s*venn(?:-beta)?\b"),
    ("xychart", r"^\s*xychart(?:-beta)?\b"),
    ("block", r"^\s*block(?:-beta)?\b"),
    ("treeView", r"^\s*treeView(?:-beta)?\b"),
    ("architecture", r"^\s*architecture(?:-beta)?\b"),
    ("eventmodeling", r"^\s*eventmodeling(?:-beta)?\b"),
    ("ishikawa", r"^\s*ishikawa(?:-beta)?\b"),
    ("wardley", r"^\s*wardley(?:-beta)?\b"),
    ("cynefin", r"^\s*cynefin(?:-beta)?\b"),
    ("railroad", r"^\s*railroad(?:-beta)?\b"),
    ("packet", r"^\s*packet(?:-beta)?\b"),
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
    ("pie", r"^\s*pie\b"),
    ("quadrantChart", r"^\s*quadrantChart\b"),
    ("requirement", r"^\s*requirementDiagram\b"),
    ("sequence", r"^\s*sequenceDiagram\b"),
    ("state", r"^\s*stateDiagram\b"),
    ("timeline", r"^\s*timeline\b"),
    ("swimlane", r"^\s*swimlane\b"),
    ("zenuml", r"^\s*zenuml\b"),
)


def try_detect_diagram_type(text: str) -> str | None:
    """Return the detected parser/canonical ID, or ``None`` when unknown."""
    if not isinstance(text, str) or not text.strip():
        return None
    for diagram_type, pattern in _PATTERNS:
        if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            return diagram_type
    return None


def detect_diagram_type(text: str) -> str:
    """Return the detected ID; unknown input is refused, never flowchart."""
    result = try_detect_diagram_type(text)
    if result is None:
        raise ValueError("MMDIO-TYPE-002: source does not match a registered diagram header")
    return result


def main() -> None:
    """Read Mermaid source from stdin or files and print the detected type."""
    filenames = sys.argv[1:]
    if not filenames:
        try:
            sys.stdout.write(f"{detect_diagram_type(sys.stdin.read())}\n")
        except ValueError as exc:
            sys.stderr.write(f"{exc}\n")
            raise SystemExit(2) from exc
        return
    for filename in filenames:
        path = Path(filename)
        if not path.exists():
            sys.stderr.write(f"Error: file not found: {filename}\n")
            continue
        try:
            diagram_type = detect_diagram_type(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            sys.stderr.write(f"{filename}: {exc}\n")
            continue
        sys.stdout.write(f"{filename}: {diagram_type}\n")


if __name__ == "__main__":
    main()
