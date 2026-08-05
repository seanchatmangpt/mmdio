"""GENERATED FILE — do not edit by hand. Regenerate with `ggen sync run`.

Public surface projected from the mmdio ontology. All 39 registered Mermaid
families admit through the lossless document facade; the original deep AST
adapters remain available for compatibility.
"""

from __future__ import annotations

from mmdio.engine.documents import *  # noqa: F403
from mmdio.engine.documents import DOCUMENT_CLASS_BY_TYPE
from mmdio.engine.enums import (
    C4Level,
    CardinityType,
    MessageType,
    NodeShape,
    ParticipantType,
    RelationshipType,
    TaskStatus,
)
from mmdio.engine.facade import (
    parse_mermaid,
    parse_structured_mermaid,
    render_diagram,
    schema_for_type,
)
from mmdio.engine.models import (
    C4Diagram,
    C4Element,
    C4Relationship,
    ClassDefinition,
    ClassDiagram,
    ClassMember,
    ClassMethod,
    ClassRelationship,
    ERDiagram,
    ERRelationship,
    Entity,
    EntityAttribute,
    FlowchartDiagram,
    FlowchartEdge,
    FlowchartNode,
    GanttChart,
    GanttTask,
    GitBranch,
    GitCommit,
    GitGraph,
    MermaidDiagram,
    Mindmap,
    MindmapNode,
    PieChart,
    PieSlice,
    SankeyDiagram,
    SankeyFlow,
    SequenceDiagram,
    SequenceMessage,
    SequenceParticipant,
    State,
    StateDiagram,
    Transition,
)
from mmdio.engine.ops import diff, merge, validate_topology
from mmdio.engine.render_dispatch import render_model
from mmdio.engine.schemas import schema_for_type as structured_schema_for_type
from mmdio.engine.supported import SUPPORTED_TYPES, is_supported
from mmdio.engine.universal import (
    CATALOG,
    DiagramSpec,
    DiagramType,
    DocumentDiff,
    DocumentError,
    MermaidDocument,
    MermaidStatement,
    MermaidToken,
    MergeResult,
    OracleProfile,
    StatementKind,
    TokenKind,
    capability_json,
    capability_records,
    canonicalize_source,
    detect_document_type,
    diff_documents,
    document_schema_for_type,
    issue_receipt,
    merge_documents,
    parse_document,
    parse_many,
    render_document,
    verify_receipt,
)

_PARSER_EXPORTS = frozenset(
    {
        "MermaidParser",
        "ParsingError",
        "parse_c4",
        "parse_class",
        "parse_er",
        "parse_flowchart",
        "parse_gantt",
        "parse_git",
        "parse_mindmap",
        "parse_pie",
        "parse_sankey",
        "parse_sequence",
        "parse_state",
    }
)


def __getattr__(name: str) -> object:
    """Load optional Lark-backed parser symbols only when requested."""
    if name in _PARSER_EXPORTS:
        from importlib import import_module

        return getattr(import_module("mmdio.engine.parser"), name)
    raise AttributeError(name)


__all__ = [
    "C4Diagram",
    "C4Element",
    "C4Level",
    "C4Relationship",
    "CATALOG",
    "CardinityType",
    "ClassDefinition",
    "ClassDiagram",
    "ClassMember",
    "ClassMethod",
    "ClassRelationship",
    "DiagramSpec",
    "DiagramType",
    "DocumentDiff",
    "DocumentError",
    "ERDiagram",
    "ERRelationship",
    "Entity",
    "EntityAttribute",
    "FlowchartDiagram",
    "FlowchartEdge",
    "FlowchartNode",
    "GanttChart",
    "GanttTask",
    "GitBranch",
    "GitCommit",
    "GitGraph",
    "MermaidDiagram",
    "MermaidDocument",
    "MermaidStatement",
    "MermaidToken",
    "MergeResult",
    "MessageType",
    "Mindmap",
    "MindmapNode",
    "NodeShape",
    "OracleProfile",
    "ParticipantType",
    "PieChart",
    "PieSlice",
    "RelationshipType",
    "SUPPORTED_TYPES",
    "SankeyDiagram",
    "SankeyFlow",
    "SequenceDiagram",
    "SequenceMessage",
    "SequenceParticipant",
    "State",
    "StateDiagram",
    "StatementKind",
    "TaskStatus",
    "TokenKind",
    "Transition",
    "canonicalize_source",
    "capability_json",
    "capability_records",
    "detect_document_type",
    "diff",
    "diff_documents",
    "document_schema_for_type",
    "is_supported",
    "issue_receipt",
    "merge",
    "merge_documents",
    "parse_document",
    "parse_many",
    "parse_mermaid",
    "parse_structured_mermaid",
    "render_diagram",
    "render_document",
    "render_model",
    "schema_for_type",
    "structured_schema_for_type",
    "validate_topology",
    "verify_receipt",
]
__all__ += sorted(_PARSER_EXPORTS)
__all__ += sorted(cls.__name__ for cls in DOCUMENT_CLASS_BY_TYPE.values())
