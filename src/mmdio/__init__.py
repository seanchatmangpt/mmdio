"""mmdio: Mermaid diagrams as typed, receipt-bearing universal I/O."""

from __future__ import annotations

from mmdio.detect import detect_diagram_type
from mmdio.engine import (
    CATALOG,
    DiagramType,
    DocumentError,
    MermaidDocument,
    capability_records,
    canonicalize_source,
    detect_document_type,
    diff_documents,
    issue_receipt,
    merge_documents,
    parse_document,
    parse_mermaid,
    render_diagram,
    render_document,
    verify_receipt,
)

__all__ = [
    "CATALOG",
    "DiagramType",
    "DocumentError",
    "MermaidDocument",
    "capability_records",
    "canonicalize_source",
    "detect_diagram_type",
    "detect_document_type",
    "diff_documents",
    "issue_receipt",
    "merge_documents",
    "parse_document",
    "parse_mermaid",
    "render_diagram",
    "render_document",
    "verify_receipt",
]
