"""JSON lifting and lowering for canonical planning graphs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .model import PlanningEdge, PlanningEdgeKind, PlanningGraph, PlanningNode, PlanningNodeKind, graph


def planning_graph_from_dict(payload: Mapping[str, Any]) -> PlanningGraph:
    """Lift a JSON-compatible canonical carrier into a validated planning graph."""
    try:
        nodes = tuple(
            PlanningNode(
                id=str(node["id"]),
                kind=PlanningNodeKind(str(node["kind"])),
                label=str(node["label"]),
                attributes=dict(node.get("attributes", {})),
            )
            for node in payload.get("nodes", [])
        )
        edges = tuple(
            PlanningEdge(
                source=str(edge["source"]),
                target=str(edge["target"]),
                kind=PlanningEdgeKind(str(edge["kind"])),
                label=None if edge.get("label") is None else str(edge["label"]),
                attributes=dict(edge.get("attributes", {})),
            )
            for edge in payload.get("edges", [])
        )
        return graph(
            formalism=str(payload["formalism"]),
            subject=str(payload["subject"]),
            nodes=nodes,
            edges=edges,
            metadata=dict(payload.get("metadata", {})),
        )
    except (KeyError, TypeError, ValueError) as error:
        if isinstance(error, ValueError) and str(error).startswith("MMDIO-PLAN-"):
            raise
        raise ValueError("MMDIO-PLAN-010 malformed canonical planning graph carrier") from error


def planning_graph_from_json(text: str) -> PlanningGraph:
    """Lift canonical planning JSON."""
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError("MMDIO-PLAN-010 planning graph JSON must be an object")
    return planning_graph_from_dict(payload)


def load_planning_graph(path: str | Path) -> PlanningGraph:
    """Load a canonical planning graph from disk."""
    return planning_graph_from_json(Path(path).read_text(encoding="utf-8"))
