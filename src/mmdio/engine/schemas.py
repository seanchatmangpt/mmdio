"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`."""

from mmdio.engine.models import (
    C4Diagram,
    ClassDiagram,
    ERDiagram,
    FlowchartDiagram,
    GanttChart,
    GitGraph,
    Mindmap,
    PieChart,
    SankeyDiagram,
    SequenceDiagram,
    StateDiagram,
)

GENERATED_JSON_SCHEMAS = {
    "c4": C4Diagram.model_json_schema(),
    "class": ClassDiagram.model_json_schema(),
    "er": ERDiagram.model_json_schema(),
    "flowchart": FlowchartDiagram.model_json_schema(),
    "gantt": GanttChart.model_json_schema(),
    "git": GitGraph.model_json_schema(),
    "mindmap": Mindmap.model_json_schema(),
    "pie": PieChart.model_json_schema(),
    "sankey": SankeyDiagram.model_json_schema(),
    "sequence": SequenceDiagram.model_json_schema(),
    "state": StateDiagram.model_json_schema(),
}

GENERATED_SCHEMA_ALIASES = {
    "classDiagram": "class",
    "gitGraph": "git",
    "stateDiagram": "state",
}


def schema_for_type(diagram_type: str) -> dict[str, object]:
    """Return the generated JSON schema for a canonical or parser type ID."""
    schema_key = GENERATED_SCHEMA_ALIASES.get(diagram_type, diagram_type)
    try:
        return GENERATED_JSON_SCHEMAS[schema_key]
    except KeyError as exc:
        raise ValueError(f"Unsupported diagram type: {diagram_type}") from exc
