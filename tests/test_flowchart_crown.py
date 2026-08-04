from __future__ import annotations

from copy import deepcopy

import pytest

from mmdio.flowchart_crown import (
    FlowchartRefusal,
    RefusalCode,
    crown,
    parse_flowchart,
    receipt_json,
    render_flowchart,
    verify_receipt,
)


SOURCE = """\
flowchart LR
  review["Review evidence"]
  admit["Admit subject"]
  receipt["Issue receipt"]
  review -->|bounded| admit
  admit --> receipt
"""


def test_crown_roundtrips_and_replays() -> None:
    receipt = crown(SOURCE)

    assert receipt["standing"] == "ALIVE"
    assert receipt["execution"]["semantic_equal"] is True
    assert receipt["execution"]["replay"] == "REPLAY_MATCH"
    assert receipt["execution"]["actuation"] is False
    assert receipt["claim_ceiling"] == "BOUNDED_FLOWCHART_SEMANTIC_ROUNDTRIP_ONLY"

    verify_receipt(receipt)
    assert receipt_json(receipt) == receipt_json(crown(SOURCE))


def test_input_order_does_not_change_semantic_identity() -> None:
    reordered = """\
graph LR
  receipt["Issue receipt"]
  admit["Admit subject"]
  review["Review evidence"]
  admit --> receipt
  review -->|bounded| admit
"""
    left = crown(SOURCE)
    right = crown(reordered)

    assert left["subject"]["canonical_sha256"] == right["subject"]["canonical_sha256"]
    assert left["rendered"] == right["rendered"]
    assert left["graph"] == right["graph"]


def test_direction_alias_is_canonicalized() -> None:
    graph = parse_flowchart('graph TB\n  a["A"]\n')
    assert graph.direction == "TD"
    assert render_flowchart(graph).startswith("flowchart TD\n")


@pytest.mark.parametrize(
    ("source", "code"),
    [
        ('flowchart LR\n  a["A"]\n  a["Again"]\n', RefusalCode.DUPLICATE_NODE),
        ('flowchart LR\n  a["A"]\n  a --> b\n', RefusalCode.DANGLING_EDGE),
        (
            'flowchart LR\n  a["A"]\n  b["B"]\n  a --> b\n  a --> b\n',
            RefusalCode.DUPLICATE_EDGE,
        ),
        ('flowchart LR\n  a{"Decision"}\n', RefusalCode.UNSUPPORTED_STATEMENT),
        ('sequenceDiagram\n  A->>B: hello\n', RefusalCode.HEADER_REQUIRED),
    ],
)
def test_typed_refusals(source: str, code: RefusalCode) -> None:
    with pytest.raises(FlowchartRefusal) as caught:
        crown(source)
    assert caught.value.code == code


def test_tampered_receipt_is_refused() -> None:
    receipt = crown(SOURCE)
    tampered = deepcopy(receipt)
    tampered["graph"]["nodes"][0]["label"] = "Changed after receipt"

    with pytest.raises(FlowchartRefusal) as caught:
        verify_receipt(tampered)

    assert caught.value.code == RefusalCode.RECEIPT_TAMPERED
