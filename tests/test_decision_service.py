from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from mmdio.decide.models import DecisionRefusal, DecisionStatus, RefusalCode
from mmdio.decide.service import DecisionService


@dataclass
class Outcome:
    observation: int
    value: float
    termination: bool
    info: dict[str, Any]


class CounterDomain:
    def __init__(self, *, limit: int = 2) -> None:
        self.limit = limit
        self.state = 0

    def reset(self) -> int:
        self.state = 0
        return self.state

    def step(self, action: str) -> Outcome:
        assert action == "advance"
        self.state += 1
        return Outcome(
            observation=self.state,
            value=1.0,
            termination=self.state >= self.limit,
            info={"state": self.state},
        )


class CounterSolver:
    def __init__(self, *, domain_factory: Any, **_: Any) -> None:
        self.domain_factory = domain_factory
        self.solved = False

    def __enter__(self) -> CounterSolver:
        return self

    def __exit__(self, *_: Any) -> None:
        return None

    def solve(self) -> None:
        assert isinstance(self.domain_factory(), CounterDomain)
        self.solved = True

    def sample_action(self, observation: int) -> str:
        assert self.solved
        assert observation >= 0
        return "advance"


class FakeBackend:
    def list_domains(self) -> list[str]:
        return ["Counter"]

    def list_solvers(self) -> list[str]:
        return ["CounterSolver"]

    def load_domain(self, name: str) -> type[Any]:
        if name != "Counter":
            raise DecisionRefusal(RefusalCode.DOMAIN_UNKNOWN, name)
        return CounterDomain

    def load_solver(self, name: str) -> type[Any]:
        if name != "CounterSolver":
            raise DecisionRefusal(RefusalCode.SOLVER_UNKNOWN, name)
        return CounterSolver

    def match_solvers(self, domain: Any) -> list[type[Any]]:
        return [CounterSolver] if isinstance(domain, CounterDomain) else []


def test_catalog_and_match_are_deterministic() -> None:
    service = DecisionService(FakeBackend())

    assert service.catalog().as_dict() == {
        "domains": ("Counter",),
        "solvers": ("CounterSolver",),
    }
    match = service.match("Counter", domain_arguments={"limit": 3})
    assert match.compatible_solvers == ("CounterSolver",)
    assert "compatible" in service.match_mermaid("Counter")


def test_solve_emits_terminal_mermaid_and_stable_receipt() -> None:
    service = DecisionService(FakeBackend())

    first = service.solve("Counter", domain_arguments={"limit": 2}, max_steps=5)
    second = service.solve("Counter", domain_arguments={"limit": 2}, max_steps=5)

    assert first.status is DecisionStatus.SOLVED
    assert first.terminal is True
    assert len(first.steps) == 2
    assert first.mermaid.startswith("stateDiagram-v2\n")
    assert first.mermaid.endswith("S2 --> [*]\n")
    assert first.receipt_sha256 == second.receipt_sha256
    assert first.trajectory_sha256 == second.trajectory_sha256


def test_solve_is_bounded_when_goal_not_reached() -> None:
    result = DecisionService(FakeBackend()).solve(
        "Counter",
        domain_arguments={"limit": 5},
        max_steps=2,
    )

    assert result.status is DecisionStatus.BOUNDED
    assert result.terminal is False
    assert len(result.steps) == 2


def test_incompatible_solver_fails_closed() -> None:
    with pytest.raises(DecisionRefusal) as captured:
        DecisionService(FakeBackend()).solve("Counter", solver="Other")

    assert captured.value.code is RefusalCode.SOLVER_INCOMPATIBLE


def test_invalid_step_bound_is_refused() -> None:
    with pytest.raises(DecisionRefusal) as captured:
        DecisionService(FakeBackend()).solve("Counter", max_steps=0)

    assert captured.value.code is RefusalCode.INVALID_ARGUMENTS
