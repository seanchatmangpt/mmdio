"""Design for Combinatorial Maximalism (DFCM) for planning-document projection.

DFCM enumerates the complete reversible projection design space for one admitted
PlanningGraph and gives every candidate an explicit disposition.  It does not
actuate, authorize, execute a planner, or mutate a world.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from itertools import product
import json
import math
from typing import Any, Iterable

from .model import PlanningEdgeKind, PlanningGraph, PlanningNodeKind


DFCM_SCHEMA = "mmdio.planning-dfcm/1"
DFCM_CLAIM_CEILING = "COMBINATORIAL_PLANNING_DOCUMENT_DESIGN_SPACE_ONLY"


class DFCMStatus(StrEnum):
    """Disposition of one candidate in the reversible design space."""

    ADMITTED = "ADMITTED"
    REFUSED = "REFUSED"


@dataclass(frozen=True, slots=True)
class DFCMAxis:
    """One finite dimension in a bounded combinatorial design space."""

    name: str
    values: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("MMDIO-DFCM-001 axis name must be non-empty")
        if not self.values or any(not str(value).strip() for value in self.values):
            raise ValueError("MMDIO-DFCM-001 axis values must be non-empty")
        if len(self.values) != len(set(self.values)):
            raise ValueError("MMDIO-DFCM-001 axis values must be unique")


@dataclass(frozen=True, slots=True)
class DFCMCandidate:
    """One point in a bounded Cartesian product."""

    coordinates: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        names = [name for name, _ in self.coordinates]
        if not names or len(names) != len(set(names)):
            raise ValueError("MMDIO-DFCM-002 candidate coordinates must name unique axes")

    def canonical_dict(self) -> dict[str, str]:
        return {name: value for name, value in sorted(self.coordinates)}

    def digest(self) -> str:
        payload = json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class ProjectionContract:
    """Independent semantic contract for one Mermaid projection family."""

    name: str
    diagram_type: str


PROJECTION_CONTRACTS: tuple[ProjectionContract, ...] = (
    ProjectionContract("topology", "flowchart"),
    ProjectionContract("summary", "mindmap"),
    ProjectionContract("states", "stateDiagram-v2"),
    ProjectionContract("requirements", "requirement"),
    ProjectionContract("timeline", "timeline"),
    ProjectionContract("schedule", "gantt"),
    ProjectionContract("value-flow", "sankey"),
    ProjectionContract("interactions", "sequence"),
)

PROJECTION_AXIS = DFCMAxis(
    "projection", tuple(contract.name for contract in PROJECTION_CONTRACTS)
)


@dataclass(frozen=True, slots=True)
class DFCMCell:
    """Evidence-bearing disposition of one planning projection candidate."""

    candidate: DFCMCandidate
    diagram_type: str
    status: DFCMStatus
    reason_code: str
    reason: str
    evidence: dict[str, Any]

    @property
    def projection_name(self) -> str:
        return self.candidate.canonical_dict()["projection"]

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate.canonical_dict(),
            "candidate_digest": self.candidate.digest(),
            "diagram_type": self.diagram_type,
            "status": self.status.value,
            "reason_code": self.reason_code,
            "reason": self.reason,
            "evidence": _canonical(self.evidence),
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )

    def digest(self) -> str:
        return sha256(self.canonical_json().encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class PlanningDFCMMatrix:
    """Complete projection design space for one exact PlanningGraph."""

    formalism: str
    subject: str
    planning_digest: str
    axes: tuple[DFCMAxis, ...]
    cells: tuple[DFCMCell, ...]

    @property
    def admitted(self) -> tuple[DFCMCell, ...]:
        return tuple(cell for cell in self.cells if cell.status == DFCMStatus.ADMITTED)

    @property
    def refused(self) -> tuple[DFCMCell, ...]:
        return tuple(cell for cell in self.cells if cell.status == DFCMStatus.REFUSED)

    @property
    def candidate_count(self) -> int:
        return len(self.cells)

    @property
    def admitted_count(self) -> int:
        return len(self.admitted)

    @property
    def refused_count(self) -> int:
        return len(self.refused)

    def verify_complete(self) -> None:
        expected = enumerate_candidates(self.axes)
        observed = tuple(cell.candidate for cell in self.cells)
        if observed != expected:
            raise ValueError("MMDIO-DFCM-008 design-space enumeration is incomplete or reordered")
        if self.admitted_count + self.refused_count != self.candidate_count:
            raise ValueError("MMDIO-DFCM-008 every candidate must be ADMITTED or REFUSED")

    def verify_documents(self, documents: Iterable[Any]) -> None:
        """Cross-check DFCM admission against independently manufactured documents."""
        expected = {
            (cell.projection_name, cell.diagram_type)
            for cell in self.admitted
        }
        observed = {
            (str(document.name), str(document.diagram_type))
            for document in documents
        }
        if observed != expected:
            raise ValueError(
                "MMDIO-DFCM-009 manufactured documents do not equal DFCM admissions; "
                f"expected={sorted(expected)!r} observed={sorted(observed)!r}"
            )

    def canonical_dict(self) -> dict[str, Any]:
        self.verify_complete()
        return {
            "schema": DFCM_SCHEMA,
            "formalism": self.formalism,
            "subject": self.subject,
            "planning_digest": self.planning_digest,
            "axes": [
                {"name": axis.name, "values": list(axis.values)}
                for axis in self.axes
            ],
            "candidate_count": self.candidate_count,
            "admitted_count": self.admitted_count,
            "refused_count": self.refused_count,
            "cells": [cell.canonical_dict() for cell in self.cells],
            "claim_ceiling": DFCM_CLAIM_CEILING,
            "authority": "non-actuating",
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )

    def digest(self) -> str:
        return sha256(self.canonical_json().encode()).hexdigest()

    def markdown(self) -> str:
        lines = [
            f"# DFCM Projection Matrix — {self.subject}",
            "",
            f"- Formalism: `{self.formalism}`",
            f"- Planning digest: `{self.planning_digest}`",
            f"- DFCM digest: `{self.digest()}`",
            f"- Candidates: `{self.candidate_count}`",
            f"- Admitted: `{self.admitted_count}`",
            f"- Refused: `{self.refused_count}`",
            f"- Claim ceiling: `{DFCM_CLAIM_CEILING}`",
            "",
            "| Projection | Mermaid type | Disposition | Reason |",
            "|---|---|---|---|",
        ]
        for cell in self.cells:
            reason = cell.reason.replace("|", "/").replace("\n", " ")
            lines.append(
                f"| `{cell.projection_name}` | `{cell.diagram_type}` | "
                f"`{cell.status.value}` | `{cell.reason_code}` {reason} |"
            )
        return "\n".join(lines) + "\n"


@dataclass(frozen=True, slots=True)
class PlanningDFCMCorpus:
    """Aggregate DFCM evidence for one subject per planning formalism."""

    matrices: tuple[PlanningDFCMMatrix, ...]

    def verify(self) -> None:
        if not self.matrices:
            raise ValueError("MMDIO-DFCM-010 corpus must contain at least one matrix")
        keys = [(matrix.formalism, matrix.planning_digest) for matrix in self.matrices]
        if len(keys) != len(set(keys)):
            raise ValueError("MMDIO-DFCM-010 duplicate DFCM matrix subject")
        for matrix in self.matrices:
            matrix.verify_complete()

    @property
    def candidate_count(self) -> int:
        return sum(matrix.candidate_count for matrix in self.matrices)

    @property
    def admitted_count(self) -> int:
        return sum(matrix.admitted_count for matrix in self.matrices)

    @property
    def refused_count(self) -> int:
        return sum(matrix.refused_count for matrix in self.matrices)

    def canonical_dict(self) -> dict[str, Any]:
        self.verify()
        return {
            "schema": "mmdio.planning-dfcm-corpus/1",
            "matrices": [
                matrix.canonical_dict()
                for matrix in sorted(
                    self.matrices, key=lambda item: (item.formalism, item.planning_digest)
                )
            ],
            "candidate_count": self.candidate_count,
            "admitted_count": self.admitted_count,
            "refused_count": self.refused_count,
            "claim_ceiling": DFCM_CLAIM_CEILING,
            "authority": "non-actuating",
        }

    def digest(self) -> str:
        payload = json.dumps(
            self.canonical_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        return sha256(payload.encode()).hexdigest()


def enumerate_candidates(axes: tuple[DFCMAxis, ...]) -> tuple[DFCMCandidate, ...]:
    """Enumerate a finite Cartesian product in deterministic axis order."""
    if not axes:
        raise ValueError("MMDIO-DFCM-003 at least one design axis is required")
    names = [axis.name for axis in axes]
    if len(names) != len(set(names)):
        raise ValueError("MMDIO-DFCM-003 axis names must be unique")
    return tuple(
        DFCMCandidate(tuple(zip(names, values, strict=True)))
        for values in product(*(axis.values for axis in axes))
    )


def generate_planning_dfcm(subject: PlanningGraph) -> PlanningDFCMMatrix:
    """Enumerate all eight projection candidates and disposition each independently."""
    subject.validate()
    formalism_axis = DFCMAxis("formalism", (subject.formalism,))
    axes = (formalism_axis, PROJECTION_AXIS)
    contracts = {contract.name: contract for contract in PROJECTION_CONTRACTS}
    cells: list[DFCMCell] = []
    for candidate in enumerate_candidates(axes):
        projection = candidate.canonical_dict()["projection"]
        contract = contracts[projection]
        admitted, reason_code, reason, evidence = _evaluate(subject, projection)
        cells.append(
            DFCMCell(
                candidate=candidate,
                diagram_type=contract.diagram_type,
                status=DFCMStatus.ADMITTED if admitted else DFCMStatus.REFUSED,
                reason_code=reason_code,
                reason=reason,
                evidence=evidence,
            )
        )
    matrix = PlanningDFCMMatrix(
        formalism=subject.formalism,
        subject=subject.subject,
        planning_digest=subject.digest(),
        axes=axes,
        cells=tuple(cells),
    )
    matrix.verify_complete()
    return matrix


def generate_dfcm_corpus(subjects: Iterable[PlanningGraph]) -> PlanningDFCMCorpus:
    corpus = PlanningDFCMCorpus(tuple(generate_planning_dfcm(subject) for subject in subjects))
    corpus.verify()
    return corpus


def _evaluate(
    subject: PlanningGraph, projection: str
) -> tuple[bool, str, str, dict[str, Any]]:
    if projection == "topology":
        return True, "MMDIO-DFCM-A01", "canonical topology is always projectable", {
            "nodes": len(subject.nodes),
            "edges": len(subject.edges),
        }

    if projection == "summary":
        count = len(subject.nodes)
        return (
            count > 0,
            "MMDIO-DFCM-A02" if count else "MMDIO-DFCM-R02",
            "typed planning nodes are present" if count else "no typed planning nodes are present",
            {"nodes": count},
        )

    if projection == "states":
        state_ids = {
            node.id
            for node in subject.nodes
            if node.kind in {PlanningNodeKind.STATE, PlanningNodeKind.GOAL}
        }
        kinds = {
            PlanningEdgeKind.TRANSITION,
            PlanningEdgeKind.PROBABILISTIC,
            PlanningEdgeKind.TEMPORAL,
            PlanningEdgeKind.CAUSAL,
        }
        transitions = sum(
            1
            for edge in subject.edges
            if edge.source in state_ids and edge.target in state_ids and edge.kind in kinds
        )
        return (
            transitions > 0,
            "MMDIO-DFCM-A03" if transitions else "MMDIO-DFCM-R03",
            "explicit state-to-state transitions are present"
            if transitions
            else "no explicit state-to-state transition is present",
            {"state_nodes": len(state_ids), "eligible_transitions": transitions},
        )

    if projection == "requirements":
        count = sum(
            1
            for node in subject.nodes
            if node.kind in {PlanningNodeKind.GOAL, PlanningNodeKind.CONSTRAINT}
        )
        return (
            count > 0,
            "MMDIO-DFCM-A04" if count else "MMDIO-DFCM-R04",
            "goal or constraint semantics are present"
            if count
            else "no goal or constraint semantics are present",
            {"requirements": count},
        )

    if projection == "timeline":
        count = sum(
            1
            for node in subject.nodes
            if node.kind in {PlanningNodeKind.EVENT, PlanningNodeKind.PROCESS}
            or "time" in node.attributes
        )
        return (
            count > 0,
            "MMDIO-DFCM-A05" if count else "MMDIO-DFCM-R05",
            "temporal observations are present"
            if count
            else "no event, process, or explicit time observation is present",
            {"temporal_nodes": count},
        )

    if projection == "schedule":
        count = sum(
            1
            for node in subject.nodes
            if node.kind in {PlanningNodeKind.ACTION, PlanningNodeKind.PROCESS}
            and ("start" in node.attributes or "duration" in node.attributes)
        )
        return (
            count > 0,
            "MMDIO-DFCM-A06" if count else "MMDIO-DFCM-R06",
            "scheduled or durative work is present"
            if count
            else "no action/process carries start or duration evidence",
            {"scheduled_nodes": count},
        )

    if projection == "value-flow":
        count = 0
        for edge in subject.edges:
            for key in ("probability", "value", "weight"):
                value = edge.attributes.get(key)
                if (
                    isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    and math.isfinite(float(value))
                    and float(value) >= 0
                ):
                    count += 1
                    break
        return (
            count > 0,
            "MMDIO-DFCM-A07" if count else "MMDIO-DFCM-R07",
            "non-negative probability/value/weight flow is present"
            if count
            else "no non-negative probability/value/weight relation is present",
            {"weighted_edges": count},
        )

    if projection == "interactions":
        count = sum(
            1
            for node in subject.nodes
            if node.kind == PlanningNodeKind.ACTION
            and node.attributes.get("actor")
            and node.attributes.get("target_actor")
        )
        return (
            count > 0,
            "MMDIO-DFCM-A08" if count else "MMDIO-DFCM-R08",
            "actor-to-actor action evidence is present"
            if count
            else "no action identifies both actor and target_actor",
            {"interaction_actions": count},
        )

    raise ValueError(f"MMDIO-DFCM-004 unknown planning projection {projection!r}")


def _canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _canonical(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, set):
        return sorted((_canonical(item) for item in value), key=repr)
    if isinstance(value, StrEnum):
        return value.value
    return value
