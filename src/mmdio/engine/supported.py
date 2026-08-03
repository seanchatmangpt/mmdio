"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`."""

GENERATED_PYTHON_SUPPORTED = frozenset({
    "c4",
    "classDiagram",
    "er",
    "flowchart",
    "gantt",
    "gitGraph",
    "mindmap",
    "pie",
    "sankey",
    "sequence",
    "stateDiagram",
})
GENERATED_INTERNAL_SUPPORTED = frozenset({
    "c4",
    "class",
    "er",
    "flowchart",
    "gantt",
    "git",
    "mindmap",
    "pie",
    "sankey",
    "sequence",
    "state",
})
SUPPORTED_TYPES = GENERATED_PYTHON_SUPPORTED


def is_supported(diagram_type: str) -> bool:
    """Return whether a canonical or parser-internal type is executable."""
    return diagram_type in GENERATED_PYTHON_SUPPORTED or diagram_type in GENERATED_INTERNAL_SUPPORTED
