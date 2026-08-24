from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from typer.testing import CliRunner

from mmdio.cli import app
from mmdio.decide.models import DecisionCatalog, DecisionMatch

runner = CliRunner()


@dataclass
class FakeRun:
    mermaid: str = "stateDiagram-v2\n  [*] --> S0\n"

    def as_dict(self) -> dict[str, Any]:
        return {"status": "SOLVED", "receipt_sha256": "a" * 64, "mermaid": self.mermaid}


class FakeService:
    def catalog(self) -> DecisionCatalog:
        return DecisionCatalog(domains=("Counter",), solvers=("CounterSolver",))

    def match(self, domain: str, **_: Any) -> DecisionMatch:
        return DecisionMatch(
            domain=domain,
            compatible_solvers=("CounterSolver",),
            domain_arguments={},
        )

    def match_mermaid(self, domain: str, **_: Any) -> str:
        return f'flowchart LR\n  domain["{domain}"]\n'

    def solve(self, *_: Any, **__: Any) -> FakeRun:
        return FakeRun()


def test_decide_catalog_uses_shared_service(monkeypatch: Any) -> None:
    monkeypatch.setattr("mmdio.decide.cli.get_service", FakeService)

    result = runner.invoke(app, ["decide", "catalog"])

    assert result.exit_code == 0
    assert '"Counter"' in result.stdout
    assert '"CounterSolver"' in result.stdout


def test_decide_match_can_emit_mermaid(monkeypatch: Any) -> None:
    monkeypatch.setattr("mmdio.decide.cli.get_service", FakeService)

    result = runner.invoke(app, ["decide", "match", "Counter", "--mermaid"])

    assert result.exit_code == 0
    assert result.stdout.startswith("flowchart LR")


def test_decide_solve_can_emit_receipt_or_mermaid(monkeypatch: Any) -> None:
    monkeypatch.setattr("mmdio.decide.cli.get_service", FakeService)

    receipt = runner.invoke(app, ["decide", "solve", "Counter"])
    mermaid = runner.invoke(app, ["decide", "solve", "Counter", "--mermaid"])

    assert receipt.exit_code == 0
    assert '"receipt_sha256"' in receipt.stdout
    assert mermaid.exit_code == 0
    assert mermaid.stdout.startswith("stateDiagram-v2")


def test_bad_json_is_a_cli_usage_error(monkeypatch: Any) -> None:
    monkeypatch.setattr("mmdio.decide.cli.get_service", FakeService)

    result = runner.invoke(
        app,
        ["decide", "match", "Counter", "--domain-arguments", "[]"],
    )

    assert result.exit_code == 2
    assert "must decode to a JSON object" in result.output
