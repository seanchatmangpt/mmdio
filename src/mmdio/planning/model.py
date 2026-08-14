"""Typed canonical planning graph used by mmdio planning-document projections."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
import json
import math
from typing import Any, Iterable

from .formalisms import normalize_formalism


class PlanningNodeKind(StrEnum):
    """Semantic node kinds shared by the admitted planning profiles."""

    STATE = "state"
    ACTION = "action"
    PROCESS = "process"
    EVENT = "event"
    GOAL = "goal"
    CONSTRAINT = "constraint"
    FLUENT = "fluent"
    REWARD = "reward"
    CHOICE = "choice"
    OBSERVATION = "observation"
    SILENT = "silent"


class PlanningEdgeKind(StrEnum):
    """Semantic relation kinds shared by the admitted planning profiles."""

    PRECONDITION = "precondition"
    EFFECT = "effect"
    TRANSITION = "transition"
    PRECEDENCE = "precedence"
    CAUSAL = "causal"
    PROBABILISTIC = "probabilistic"
    TEMPORAL = "temporal"
    DEPENDENCY = "dependency"
    OBSERVATION = "observation"
    REWARD = "reward"


@dataclass(frozen=True, slots=True)
class PlanningNode:
    """One typed planning object."""

    id: str
    kind: PlanningNodeKind
    label: str
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PlanningEdge:
    """One typed planning relation."""

    source: str
    target: str
    kind: PlanningEdgeKind
    label: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PlanningGraph:
    """Canonical, non-actuating planning interchange subject."""

    formalism: str
    subject: str
    nodes: tuple[PlanningNode, ...]
    edges: tuple[PlanningEdge, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Refuse malformed identity, topology, and bounded numeric semantics."""
        if not self.subject.strip():
            raise ValueError("MMDIO-PLAN-001 planning subject must be non-empty")
        if self.formalism != normalize_formalism(self.formalism):
            raise ValueError("MMDIO-PLAN-004 planning formalism must be canonical")

        ids = [node.id for node in self.nodes]
        if any(not node_id.strip() for node_id in ids):
            raise ValueError("MMDIO-PLAN-002 planning node id must be non-empty")
        if len(ids) != len(set(ids)):
            raise ValueError("MMDIO-PLAN-002 duplicate planning node id")

        known = set(ids)
        for edge in self.edges:
            if edge.source not in known or edge.target not in known:
                raise ValueError(
                    "MMDIO-PLAN-003 planning edge references an unknown node: "
                    f"{edge.source!r}->{edge.target!r}"
                )
            probability = edge.attributes.get("probability")
            if probability is not None:
                if not _finite_number(probability) or not 0 <= float(probability) <= 1:
                    raise ValueError("MMDIO-PLAN-005 probability must be finite and within [0, 1]")

        for node in self.nodes:
            for key in ("start", "duration", "time"):
                value = node.attributes.get(key)
                if value is not None and not _finite_number(value):
                    raise ValueError(f"MMDIO-PLAN-006 {key} must be a finite number")
            duration = node.attributes.get("duration")
            if duration is not None and float(duration) < 0:
                raise ValueError("MMDIO-PLAN-006 duration must be non-negative")

    def canonical_dict(self) -> dict[str, Any]:
        """Return the order-independent canonical planning carrier."""
        return {
            "formalism": self.formalism,
            "subject": self.subject,
            "nodes": [
                {
                    "id": node.id,
                    "kind": node.kind.value,
                    "label": node.label,
                    "attributes": _canonical(node.attributes),
                }
                for node in sorted(self.nodes, key=lambda item: (item.id, item.kind.value, item.label))
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "kind": edge.kind.value,
                    "label": edge.label,
                    "attributes": _canonical(edge.attributes),
                }
                for edge in sorted(
                    self.edges,
                    key=lambda item: (
                        item.source,
                        item.target,
                        item.kind.value,
                        item.label or "",
                        json.dumps(_canonical(item.attributes), sort_keys=True, separators=(",", ":")),
                    ),
                )
            ],
            "metadata": _canonical(self.metadata),
        }

    def canonical_json(self) -> str:
        """Serialize the canonical planning carrier deterministically."""
        return json.dumps(
            self.canonical_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )

    def digest(self) -> str:
        """Return the SHA-256 identity of the canonical planning subject."""
        return sha256(self.canonical_json().encode()).hexdigest()


def graph(
    *,
    formalism: str,
    subject: str,
    nodes: Iterable[PlanningNode],
    edges: Iterable[PlanningEdge],
    metadata: dict[str, Any] | None = None,
) -> PlanningGraph:
    """Construct, normalize, validate, and return a canonical planning graph."""
    result = PlanningGraph(
        formalism=normalize_formalism(formalism),
        subject=subject,
        nodes=tuple(nodes),
        edges=tuple(edges),
        metadata=dict(metadata or {}),
    )
    result.validate()
    return result


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _canonical(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, set):
        items = [_canonical(item) for item in value]
        return sorted(items, key=lambda item: json.dumps(item, sort_keys=True))
    if isinstance(value, StrEnum):
        return value.value
    return value
