"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`."""

from mmdio.engine.models import C4Diagram
from mmdio.engine.models import ClassDiagram
from mmdio.engine.models import ERDiagram
from mmdio.engine.models import FlowchartDiagram
from mmdio.engine.models import GanttChart
from mmdio.engine.models import GitGraph
from mmdio.engine.models import Mindmap
from mmdio.engine.models import PieChart
from mmdio.engine.models import SankeyDiagram
from mmdio.engine.models import SequenceDiagram
from mmdio.engine.models import StateDiagram

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
