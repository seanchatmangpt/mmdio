from __future__ import annotations

from dataclasses import dataclass
import sys
from types import SimpleNamespace
from typing import Any

from mmdio.decide.mcp import create_server
from mmdio.decide.models import DecisionCatalog, DecisionMatch


class FakeFastMCP:
    def __init__(self, name: str) -> None:
        self.name = name
        self.tools: dict[str, Any] = {}

    def tool(self, function: Any) -> Any:
        self.tools[function.__name__] = function
        return function


@dataclass
class FakeRun:
    def as_dict(self) -> dict[str, Any]:
        return {"status": "SOLVED", "receipt_sha256": "b" * 64}


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


def test_fastmcp_tools_project_the_same_service(monkeypatch: Any) -> None:
    monkeypatch.setitem(sys.modules, "fastmcp", SimpleNamespace(FastMCP=FakeFastMCP))

    server = create_server(FakeService())

    assert set(server.tools) == {
        "decision_catalog",
        "decision_match",
        "decision_match_mermaid",
        "decision_solve",
    }
    assert server.tools["decision_catalog"]()["domains"] == ("Counter",)
    assert server.tools["decision_match"]("Counter")["compatible_solvers"] == (
        "CounterSolver",
    )
    assert server.tools["decision_solve"]("Counter")["status"] == "SOLVED"
