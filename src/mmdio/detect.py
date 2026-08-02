"""
Mermaid diagram type detection module.

Detects the diagram type from Mermaid text input by pattern matching
on the first line(s). Supports flowchart, sequence, class, state, ER,
Gantt, pie, git, C4, mindmap, and sankey diagrams.
"""

import re
from typing import Optional


def detect_diagram_type(text: str) -> str:
    """
    Detect the Mermaid diagram type from input text.

    Analyzes the first line(s) of the input text to determine which
    Mermaid diagram type is being used. Matching is case-insensitive.

    Args:
        text: Mermaid diagram text

    Returns:
        One of: "flowchart", "sequence", "class", "state", "er",
        "gantt", "pie", "git", "c4", "mindmap", "sankey".
        Defaults to "flowchart" if type cannot be detected.
    """
    if not text or not isinstance(text, str):
        return "flowchart"

    # Strip leading/trailing whitespace and convert to lowercase for matching
    first_lines = text.strip().lower()

    # Define detection patterns (order matters—check more specific patterns first)
    patterns = [
        (r"^\s*sequencediagram\b", "sequence"),
        (r"^\s*classDiagram\b", "class"),
        (r"^\s*classDiagram-v2\b", "class"),
        (r"^\s*stateDiagram(-v2)?\b", "state"),
        (r"^\s*state\s+", "state"),
        (r"^\s*erDiagram\b", "er"),
        (r"^\s*erDiagram\b", "er"),
        (r"^\s*gantt\b", "gantt"),
        (r"^\s*pie\s+", "pie"),
        (r"^\s*pie\s+chart\b", "pie"),
        (r"^\s*gitGraph\b", "git"),
        (r"^\s*gitgraph\b", "git"),
        (r"^\s*c4context\b", "c4"),
        (r"^\s*c4diagram\b", "c4"),
        (r"^\s*mindmap\b", "mindmap"),
        (r"^\s*sankey-beta\b", "sankey"),
        (r"^\s*graph\b", "flowchart"),
        (r"^\s*flowchart\b", "flowchart"),
    ]

    for pattern, diagram_type in patterns:
        if re.search(pattern, first_lines, re.IGNORECASE):
            return diagram_type

    # Default to flowchart if no pattern matches
    return "flowchart"


# ============================================================================
# Inline Unit Tests
# ============================================================================

def run_tests():
    """Run inline tests for diagram type detection."""
    tests = [
        # Flowchart tests
        ("graph TD\n  A --> B", "flowchart", "graph TD"),
        ("graph LR\n  A[Start]", "flowchart", "graph LR"),
        ("GRAPH LR\n  A --> B", "flowchart", "GRAPH LR (uppercase)"),
        ("flowchart TD\n  A --> B", "flowchart", "flowchart TD"),
        ("FLOWCHART\n  A --> B", "flowchart", "FLOWCHART (uppercase)"),
        ("  graph TD\n  A --> B", "flowchart", "graph with leading space"),

        # Sequence Diagram tests
        ("sequenceDiagram\n  A->>B: Hello", "sequence", "sequenceDiagram"),
        ("SEQUENCEDIAGRAM\n  A->>B", "sequence", "SEQUENCEDIAGRAM (uppercase)"),
        ("  sequenceDiagram\n", "sequence", "sequenceDiagram with space"),

        # Class Diagram tests
        ("classDiagram\n  class A", "class", "classDiagram"),
        ("CLASSDIAGRAM\n  class A", "class", "CLASSDIAGRAM (uppercase)"),
        ("classDiagram-v2\n  class A", "class", "classDiagram-v2"),

        # State Diagram tests
        ("stateDiagram\n  [*] --> A", "state", "stateDiagram"),
        ("stateDiagram-v2\n  [*] --> A", "state", "stateDiagram-v2"),
        ("STATE\n  [*]", "state", "state (uppercase)"),
        ("state A\n  [*]", "state", "state A"),
        ("STATEDIAGRAM\n", "state", "STATEDIAGRAM (uppercase)"),

        # ER Diagram tests
        ("erDiagram\n  CUSTOMER", "er", "erDiagram"),
        ("ERDIAGRAM\n  CUSTOMER", "er", "ERDIAGRAM (uppercase)"),

        # Gantt tests
        ("gantt\n  title Project", "gantt", "gantt"),
        ("GANTT\n  title", "gantt", "GANTT (uppercase)"),

        # Pie Chart tests
        ("pie chart\n  title Data", "pie", "pie chart"),
        ("PIE\n  title", "pie", "PIE (uppercase)"),
        ("pie title test", "pie", "pie title"),

        # Git Graph tests
        ("gitGraph\n  commit id: 'initial'", "git", "gitGraph"),
        ("GITGRAPH\n  commit", "git", "GITGRAPH (uppercase)"),

        # C4 Diagram tests
        ("C4Context\n  Person(user)", "c4", "C4Context"),
        ("c4diagram\n  System(sys)", "c4", "c4diagram"),
        ("C4DIAGRAM\n", "c4", "C4DIAGRAM (uppercase)"),

        # Mindmap tests
        ("mindmap\n  root", "mindmap", "mindmap"),
        ("MINDMAP\n  root", "mindmap", "MINDMAP (uppercase)"),

        # Sankey tests
        ("sankey-beta\n  A,B,10", "sankey", "sankey-beta"),
        ("SANKEY-BETA\n  A,B,10", "sankey", "SANKEY-BETA (uppercase)"),

        # Default/edge cases
        ("", "flowchart", "empty string"),
        ("   \n  \n", "flowchart", "whitespace only"),
        ("some random text", "flowchart", "unrecognized text"),
        ("# Comment only", "flowchart", "comment only"),
    ]

    passed = 0
    failed = 0

    for text, expected, description in tests:
        result = detect_diagram_type(text)
        if result == expected:
            passed += 1
            print(f"✓ {description}")
        else:
            failed += 1
            print(f"✗ {description}: expected '{expected}', got '{result}'")

    print(f"\n{passed}/{len(tests)} tests passed")
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
