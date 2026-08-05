"""Bounded semantic crown for the canonical Mermaid flowchart profile.

This module is authored source. It deliberately does not edit or depend on the
generated multi-dialect parser/model projections. The admitted profile is small:

* ``flowchart|graph`` with TD/TB/T/LR/RL/BT direction;
* explicit rectangle nodes: ``id[\"label\"]``;
* solid directed edges, optionally labelled;
* comments beginning with ``%%`` and blank lines.

Everything else is a typed refusal. The narrow profile is sufficient to prove
parse -> canonical graph -> lower -> lift -> semantic comparison -> receipt ->
replay without claiming universal Mermaid equivalence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, Mapping


_HEADER_RE = re.compile(r"^(?:flowchart|graph)\s+(TD|TB|T|BT|LR|RL)$", re.IGNORECASE)
_NODE_RE = re.compile(
    r'^(?P<id>[A-Za-z_][A-Za-z0-9_]*)\s*\[\s*"(?P<label>(?:\\.|[^"\\])*)"\s*\]$'
)
_EDGE_RE = re.compile(
    r"^(?P<source>[A-Za-z_][A-Za-z0-9_]*)\s*-->"
    r"(?:\|(?P<label>[^|\r\n]+)\|)?\s*"
    r"(?P<target>[A-Za-z_][A-Za-z0-9_]*)$"
)


class RefusalCode(StrEnum):
    """Stable refusal identifiers for the bounded flowchart profile."""

    EMPTY_INPUT = "MMDIO-FLOW-001"
    HEADER_REQUIRED = "MMDIO-FLOW-002"
    UNSUPPORTED_STATEMENT = "MMDIO-FLOW-003"
    DUPLICATE_NODE = "MMDIO-FLOW-004"
    DANGLING_EDGE = "MMDIO-FLOW-005"
    DUPLICATE_EDGE = "MMDIO-FLOW-006"
    EMPTY_LABEL = "MMDIO-FLOW-007"
    RECEIPT_TAMPERED = "MMDIO-FLOW-008"
    RECEIPT_SCHEMA = "MMDIO-FLOW-009"


class FlowchartRefusal(ValueError):
    """Typed refusal with a stable machine-readable code."""

    def __init__(self, code: RefusalCode, message: str, *, line: int | None = None) -> None:
        self.code = code
        self.line = line
        prefix = f"{code.value}"
        if line is not None:
            prefix += f":line={line}"
        super().__init__(f"{prefix}: {message}")


@dataclass(frozen=True, order=True)
class Node:
    """Canonical rectangle node."""

    id: str
    label: str

    def as_dict(self) -> dict[str, str]:
        return {"id": self.id, "label": self.label, "shape": "rectangle"}


@dataclass(frozen=True, order=True)
class Edge:
    """Canonical solid directed edge."""

    source: str
    target: str
    label: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {
            "source": self.source,
            "target": self.target,
            "label": self.label,
            "edge_type": "solid",
        }


@dataclass(frozen=True)
class CanonicalFlowchart:
    """Canonical graph authority for the bounded profile."""

    direction: str
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "profile": "mmdio.flowchart.rectangle-solid/1",
            "direction": self.direction,
            "nodes": [node.as_dict() for node in self.nodes],
            "edges": [edge.as_dict() for edge in self.edges],
        }


def _decode_json_string(raw: str, *, line: int) -> str:
    try:
        value = json.loads(f'"{raw}"')
    except json.JSONDecodeError as error:
        raise FlowchartRefusal(
            RefusalCode.UNSUPPORTED_STATEMENT,
            f"invalid JSON-style node label escape: {error.msg}",
            line=line,
        ) from error
    if not isinstance(value, str) or not value.strip():
        raise FlowchartRefusal(
            RefusalCode.EMPTY_LABEL,
            "node labels must contain non-whitespace text",
            line=line,
        )
    if "\n" in value or "\r" in value:
        raise FlowchartRefusal(
            RefusalCode.UNSUPPORTED_STATEMENT,
            "multi-line node labels are outside the admitted profile",
            line=line,
        )
    return value


def _normalize_direction(direction: str) -> str:
    normalized = direction.upper()
    if normalized in {"T", "TB", "TD"}:
        return "TD"
    return normalized


def parse_flowchart(text: str) -> CanonicalFlowchart:
    """Parse and admit the bounded flowchart profile."""

    meaningful: list[tuple[int, str]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("%%"):
            continue
        meaningful.append((line_number, stripped))

    if not meaningful:
        raise FlowchartRefusal(RefusalCode.EMPTY_INPUT, "no Mermaid statements were observed")

    header_line, header = meaningful[0]
    header_match = _HEADER_RE.fullmatch(header)
    if header_match is None:
        raise FlowchartRefusal(
            RefusalCode.HEADER_REQUIRED,
            "first statement must be 'flowchart <direction>' or 'graph <direction>'",
            line=header_line,
        )

    nodes: dict[str, Node] = {}
    edges: set[Edge] = set()

    for line_number, statement in meaningful[1:]:
        node_match = _NODE_RE.fullmatch(statement)
        if node_match is not None:
            node_id = node_match.group("id")
            if node_id in nodes:
                raise FlowchartRefusal(
                    RefusalCode.DUPLICATE_NODE,
                    f"node {node_id!r} is declared more than once",
                    line=line_number,
                )
            nodes[node_id] = Node(
                id=node_id,
                label=_decode_json_string(node_match.group("label"), line=line_number),
            )
            continue

        edge_match = _EDGE_RE.fullmatch(statement)
        if edge_match is not None:
            label = edge_match.group("label")
            if label is not None:
                label = label.strip()
                if not label:
                    raise FlowchartRefusal(
                        RefusalCode.EMPTY_LABEL,
                        "edge labels must contain non-whitespace text",
                        line=line_number,
                    )
            edge = Edge(
                source=edge_match.group("source"),
                target=edge_match.group("target"),
                label=label,
            )
            if edge in edges:
                raise FlowchartRefusal(
                    RefusalCode.DUPLICATE_EDGE,
                    f"edge {edge.source!r} -> {edge.target!r} is duplicated",
                    line=line_number,
                )
            edges.add(edge)
            continue

        raise FlowchartRefusal(
            RefusalCode.UNSUPPORTED_STATEMENT,
            "only explicit rectangle nodes and solid directed edges are admitted",
            line=line_number,
        )

    for edge in edges:
        missing = [node_id for node_id in (edge.source, edge.target) if node_id not in nodes]
        if missing:
            raise FlowchartRefusal(
                RefusalCode.DANGLING_EDGE,
                f"edge references undeclared node(s): {', '.join(sorted(missing))}",
            )

    return CanonicalFlowchart(
        direction=_normalize_direction(header_match.group(1)),
        nodes=tuple(sorted(nodes.values())),
        edges=tuple(sorted(edges)),
    )


def canonical_json(graph: CanonicalFlowchart) -> str:
    """Serialize the canonical graph deterministically."""

    return json.dumps(graph.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def semantic_digest(graph: CanonicalFlowchart) -> str:
    """Bind the canonical graph identity."""

    return hashlib.sha256(canonical_json(graph).encode("utf-8")).hexdigest()


def render_flowchart(graph: CanonicalFlowchart) -> str:
    """Lower the canonical graph to canonical Mermaid text."""

    lines = [f"flowchart {graph.direction}"]
    for node in graph.nodes:
        lines.append(f"  {node.id}[{json.dumps(node.label, ensure_ascii=False)}]")
    for edge in graph.edges:
        if edge.label is None:
            lines.append(f"  {edge.source} --> {edge.target}")
        else:
            lines.append(f"  {edge.source} -->|{edge.label}| {edge.target}")
    return "\n".join(lines) + "\n"


def crown(text: str) -> dict[str, Any]:
    """Execute parse, admission, lowering, lifting, comparison, and receipt."""

    graph = parse_flowchart(text)
    rendered = render_flowchart(graph)
    lifted = parse_flowchart(rendered)
    if lifted != graph:
        raise AssertionError("canonical lower/lift replay diverged")

    graph_json = canonical_json(graph)
    receipt: dict[str, Any] = {
        "schema": "mmdio.flowchart-crown-receipt/1",
        "standing": "ALIVE",
        "profile": "mmdio.flowchart.rectangle-solid/1",
        "subject": {
            "input_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "canonical_sha256": hashlib.sha256(graph_json.encode("utf-8")).hexdigest(),
            "rendered_sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
        },
        "graph": graph.as_dict(),
        "rendered": rendered,
        "execution": {
            "parsed": True,
            "admitted": True,
            "lowered": True,
            "lifted": True,
            "semantic_equal": True,
            "replay": "REPLAY_MATCH",
            "actuation": False,
        },
        "evidence_axes": {
            "observed": True,
            "admitted": True,
            "executed": True,
            "changed": False,
            "verified": True,
            "inferred": False,
            "refused": False,
            "blocked": False,
            "unsupported": False,
        },
        "claim_ceiling": "BOUNDED_FLOWCHART_SEMANTIC_ROUNDTRIP_ONLY",
    }
    receipt["receipt_sha256"] = _receipt_digest(receipt)
    return receipt


def _receipt_digest(receipt: Mapping[str, Any]) -> str:
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    payload = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _graph_from_mapping(value: Mapping[str, Any]) -> CanonicalFlowchart:
    try:
        if value["profile"] != "mmdio.flowchart.rectangle-solid/1":
            raise KeyError("profile")
        direction = str(value["direction"])
        nodes = tuple(
            sorted(Node(id=str(item["id"]), label=str(item["label"])) for item in value["nodes"])
        )
        edges = tuple(
            sorted(
                Edge(
                    source=str(item["source"]),
                    target=str(item["target"]),
                    label=None if item.get("label") is None else str(item["label"]),
                )
                for item in value["edges"]
            )
        )
    except (KeyError, TypeError) as error:
        raise FlowchartRefusal(
            RefusalCode.RECEIPT_SCHEMA,
            "receipt graph does not match the canonical carrier",
        ) from error
    return CanonicalFlowchart(direction=direction, nodes=nodes, edges=edges)


def verify_receipt(receipt: Mapping[str, Any]) -> None:
    """Independently verify identity, lowering, lifting, and replay."""

    if receipt.get("schema") != "mmdio.flowchart-crown-receipt/1":
        raise FlowchartRefusal(RefusalCode.RECEIPT_SCHEMA, "unknown receipt schema")
    if receipt.get("receipt_sha256") != _receipt_digest(receipt):
        raise FlowchartRefusal(RefusalCode.RECEIPT_TAMPERED, "receipt digest mismatch")

    graph_value = receipt.get("graph")
    subject = receipt.get("subject")
    rendered = receipt.get("rendered")
    if not isinstance(graph_value, Mapping) or not isinstance(subject, Mapping):
        raise FlowchartRefusal(RefusalCode.RECEIPT_SCHEMA, "graph and subject objects are required")
    if not isinstance(rendered, str):
        raise FlowchartRefusal(RefusalCode.RECEIPT_SCHEMA, "rendered Mermaid text is required")

    graph = _graph_from_mapping(graph_value)
    canonical_hash = hashlib.sha256(canonical_json(graph).encode("utf-8")).hexdigest()
    rendered_hash = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    if subject.get("canonical_sha256") != canonical_hash:
        raise FlowchartRefusal(RefusalCode.RECEIPT_TAMPERED, "canonical graph digest mismatch")
    if subject.get("rendered_sha256") != rendered_hash:
        raise FlowchartRefusal(RefusalCode.RECEIPT_TAMPERED, "rendered text digest mismatch")
    if render_flowchart(graph) != rendered:
        raise FlowchartRefusal(RefusalCode.RECEIPT_TAMPERED, "rendered projection is noncanonical")
    if parse_flowchart(rendered) != graph:
        raise FlowchartRefusal(RefusalCode.RECEIPT_TAMPERED, "lifted graph diverges")


def receipt_json(receipt: Mapping[str, Any]) -> str:
    """Serialize a receipt deterministically for replay comparison."""

    return json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
