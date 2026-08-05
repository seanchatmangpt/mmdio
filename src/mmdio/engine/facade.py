"""Public all-dialect facade with explicit optional deep-AST projections."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from mmdio.engine.universal import (
    DiagramType,
    MermaidDocument,
    detect_document_type,
    document_schema_for_type,
    parse_document,
    render_document,
)

_DEEP_PROJECTION = {
    DiagramType.C4: "c4",
    DiagramType.CLASS: "class",
    DiagramType.CLASS_V2: "class",
    DiagramType.ER: "er",
    DiagramType.FLOWCHART: "flowchart",
    DiagramType.GANTT: "gantt",
    DiagramType.GIT_GRAPH: "git",
    DiagramType.MINDMAP: "mindmap",
    DiagramType.PIE: "pie",
    DiagramType.SANKEY: "sankey",
    DiagramType.SEQUENCE: "sequence",
    DiagramType.STATE: "state",
    DiagramType.STATE_V2: "state",
}


def parse_mermaid(text: str) -> MermaidDocument:
    """Parse every registered type through the uniform lossless CST contract."""
    return parse_document(text)


def parse_structured_mermaid(text: str) -> Any:
    """Parse through an optional deep transformer; requires the ``all`` extra."""
    diagram_type = detect_document_type(text)
    internal_id = _DEEP_PROJECTION.get(diagram_type)
    if internal_id is None:
        raise ValueError(f"No deep semantic projection for {diagram_type.value}")
    parser = import_module("mmdio.engine.parser")
    return getattr(parser, f"parse_{internal_id}")(text)


def render_diagram(diagram: Any) -> str:
    """Render either a universal document or an explicit legacy deep AST."""
    if isinstance(diagram, MermaidDocument):
        return render_document(diagram)
    return import_module("mmdio.engine.render").render_diagram(diagram)


def schema_for_type(diagram_type: str) -> dict[str, Any]:
    """Return a deep schema where present, otherwise the universal schema."""
    try:
        return import_module("mmdio.engine.schemas").schema_for_type(diagram_type)
    except (ModuleNotFoundError, ValueError):
        return document_schema_for_type(diagram_type)
