"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`."""

GENERATED_DETECT_PATTERNS = [
    (r"^\s*sequenceDiagram\b", "sequence"),
    (r"^\s*classDiagram(?:-v2)?\b", "class"),
    (r"^\s*stateDiagram(?:-v2)?\b", "state"),
    (r"^\s*erDiagram\b", "er"),
    (r"^\s*gantt\b", "gantt"),
    (r"^\s*pie\b", "pie"),
    (r"^\s*gitGraph\b", "git"),
    (r"^\s*C4(?:Context|Container|Component|Dynamic|Deployment|Diagram)\b", "c4"),
    (r"^\s*mindmap\b", "mindmap"),
    (r"^\s*sankey-beta\b", "sankey"),
]
