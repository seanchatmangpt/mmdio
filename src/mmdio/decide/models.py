"""Typed contracts for the mmdio decision-intelligence boundary."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class DecisionStatus(StrEnum):
    """Standing of a bounded decision run."""

    SOLVED = "SOLVED"
    BOUNDED = "BOUNDED"
    REFUSED = "REFUSED"


class RefusalCode(StrEnum):
    """Stable refusal identifiers for the scikit-decide fusion."""

    DEPENDENCY_UNAVAILABLE = "MMDIO-DECIDE-001"
    DOMAIN_UNKNOWN = "MMDIO-DECIDE-002"
    SOLVER_UNKNOWN = "MMDIO-DECIDE-003"
    INVALID_ARGUMENTS = "MMDIO-DECIDE-004"
    SOLVER_INCOMPATIBLE = "MMDIO-DECIDE-005"
    DOMAIN_CONSTRUCTION_FAILED = "MMDIO-DECIDE-006"
    SOLVE_FAILED = "MMDIO-DECIDE-007"
    SERIALIZATION_FAILED = "MMDIO-DECIDE-008"


class DecisionRefusal(ValueError):
    """A fail-closed, machine-readable refusal."""

    def __init__(
        self,
        code: RefusalCode,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(f"{code.value}: {message}")

    def as_dict(self) -> dict[str, Any]:
        """Return a stable JSON-compatible refusal payload."""
        return {
            "status": DecisionStatus.REFUSED.value,
            "code": self.code.value,
            "message": str(self),
            "details": self.details,
        }


@dataclass(frozen=True)
class DecisionCatalog:
    """Registered scikit-decide domains and solvers."""

    domains: tuple[str, ...]
    solvers: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return asdict(self)


@dataclass(frozen=True)
class DecisionMatch:
    """Compatible solvers for an instantiated domain."""

    domain: str
    compatible_solvers: tuple[str, ...]
    domain_arguments: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return asdict(self)


@dataclass(frozen=True)
class DecisionStep:
    """One observed transition in a bounded rollout."""

    index: int
    observation: Any
    action: Any
    next_observation: Any
    value: Any
    termination: bool
    info: Any

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return asdict(self)


@dataclass(frozen=True)
class DecisionRun:
    """Receipt-bearing result of solve plus bounded rollout."""

    schema: str
    status: DecisionStatus
    domain: str
    solver: str
    domain_arguments: dict[str, Any]
    solver_arguments: dict[str, Any]
    initial_observation: Any
    steps: tuple[DecisionStep, ...]
    terminal: bool
    max_steps: int
    mermaid: str
    input_sha256: str
    trajectory_sha256: str
    mermaid_sha256: str
    receipt_sha256: str
    claim_ceiling: str

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload
