"""Executable all-dialect CST, receipt, and refusal contracts."""

from __future__ import annotations

import json

import pytest

from mmdio.engine import (
    CATALOG,
    DocumentError,
    capability_records,
    issue_receipt,
    parse_document,
    render_document,
    verify_receipt,
)
from mmdio.engine.documents import DOCUMENT_CLASS_BY_TYPE

SAMPLES = {
    "c4": "C4Context\n",
    "flowchart": "flowchart TD\n",
    "flowchart-v2": "flowchart-v2 TD\n",
    "flowchart-elk": "flowchart-elk TD\n",
    "swimlane": "swimlane\n",
    "er": "erDiagram\n",
    "gitGraph": "gitGraph\n",
    "gantt": "gantt\n",
    "info": "info\n",
    "pie": "pie\n",
    "quadrantChart": "quadrantChart\n",
    "xychart": "xychart-beta\n",
    "requirement": "requirementDiagram\n",
    "sequence": "sequenceDiagram\n",
    "classDiagram": "classDiagram\n",
    "classDiagram-v2": "classDiagram-v2\n",
    "stateDiagram": "stateDiagram\n",
    "stateDiagram-v2": "stateDiagram-v2\n",
    "journey": "journey\n",
    "timeline": "timeline\n",
    "mindmap": "mindmap\n",
    "kanban": "kanban\n",
    "sankey": "sankey-beta\n",
    "packet": "packet-beta\n",
    "radar": "radar-beta\n",
    "block": "block-beta\n",
    "treeView": "treeView-beta\n",
    "architecture": "architecture-beta\n",
    "eventmodeling": "eventmodeling-beta\n",
    "ishikawa": "ishikawa-beta\n",
    "venn": "venn-beta\n",
    "treemap": "treemap-beta\n",
    "wardley": "wardley-beta\n",
    "cynefin": "cynefin-beta\n",
    "railroad": "railroad-beta\n",
    "railroad-ebnf": "railroad-ebnf-beta\n",
    "railroad-abnf": "railroad-abnf-beta\n",
    "railroad-peg": "railroad-peg-beta\n",
    "zenuml": "zenuml\n",
}


def test_exactly_39_executable_document_classes() -> None:
    assert len(CATALOG) == len(capability_records()) == len(DOCUMENT_CLASS_BY_TYPE) == 39
    assert {record["diagram_type"] for record in capability_records()} == set(SAMPLES)


@pytest.mark.parametrize(("diagram_type", "source"), SAMPLES.items(), ids=SAMPLES)
def test_each_type_parses_renders_receipts_and_replays(
    diagram_type: str,
    source: str,
) -> None:
    document = parse_document(source)
    assert str(document.type) == diagram_type
    assert type(document) is DOCUMENT_CLASS_BY_TYPE[document.type]
    assert render_document(document) == source
    assert document.statements[0].tokens
    receipt = issue_receipt(document)
    assert verify_receipt(receipt) == document
    assert json.loads(json.dumps(receipt, sort_keys=True)) == receipt


def test_profile_type_can_bind_native_mermaid_source() -> None:
    document = parse_document("flowchart LR\n  A --> B\n", "flowchart-elk")
    assert str(document.type) == "flowchart-elk"


def test_unknown_source_is_refused_without_flowchart_fallback() -> None:
    with pytest.raises(DocumentError, match="MMDIO-TYPE-002"):
        parse_document("not a registered mermaid diagram\n")


def test_conflicting_declared_type_is_refused() -> None:
    with pytest.raises(DocumentError, match="MMDIO-TYPE-003"):
        parse_document("pie\n  \"A\": 1\n", "sequence")


def test_tampered_receipt_is_refused() -> None:
    receipt = issue_receipt(parse_document("timeline\n  2026 : ALIVE\n"))
    receipt["canonical_source"] = "timeline\n  2026 : tampered\n"
    with pytest.raises(DocumentError, match="MMDIO-RECEIPT-002"):
        verify_receipt(receipt)


def test_all_type_diff_and_bounded_merge() -> None:
    from mmdio.engine import diff_documents, merge_documents

    base = parse_document("timeline\n  2026 : base\n")
    left = parse_document("timeline\n  2026 : left\n")
    right = parse_document("timeline\n  2026 : base\n")
    difference = diff_documents(base, left)
    assert difference.changed
    assert any("left" in line for line in difference.unified_diff)
    merged = merge_documents(base, left, right)
    assert merged.selected == "left"
    assert merged.source == left.source


def test_divergent_merge_is_refused() -> None:
    from mmdio.engine import merge_documents

    base = parse_document("timeline\n  2026 : base\n")
    left = parse_document("timeline\n  2026 : left\n")
    right = parse_document("timeline\n  2026 : right\n")
    with pytest.raises(DocumentError, match="MMDIO-MERGE-002"):
        merge_documents(base, left, right)
