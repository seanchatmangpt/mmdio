"""FastMCP projection of the shared mmdio decision service."""

from __future__ import annotations

from typing import Any

from mmdio.decide.service import DecisionService


def create_server(service: DecisionService | None = None) -> Any:
    """Create a FastMCP server exposing the exact Typer decision service."""
    try:
        from fastmcp import FastMCP
    except ImportError as error:
        raise RuntimeError("FastMCP is unavailable; install mmdio[decision]") from error

    decision_service = service or DecisionService()
    server = FastMCP("mmdio-decision")

    @server.tool
    def decision_catalog() -> dict[str, Any]:
        """List registered scikit-decide domains and solvers."""
        return decision_service.catalog().as_dict()

    @server.tool
    def decision_match(
        domain: str,
        domain_arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return solvers compatible with a registered domain."""
        return decision_service.match(
            domain,
            domain_arguments=domain_arguments,
        ).as_dict()

    @server.tool
    def decision_match_mermaid(
        domain: str,
        domain_arguments: dict[str, Any] | None = None,
    ) -> str:
        """Render compatible solvers as a Mermaid flowchart."""
        return decision_service.match_mermaid(domain, domain_arguments=domain_arguments)

    @server.tool
    def decision_solve(
        domain: str,
        solver: str | None = None,
        domain_arguments: dict[str, Any] | None = None,
        solver_arguments: dict[str, Any] | None = None,
        max_steps: int = 100,
    ) -> dict[str, Any]:
        """Solve and return a receipt-bearing bounded rollout."""
        return decision_service.solve(
            domain,
            solver=solver,
            domain_arguments=domain_arguments,
            solver_arguments=solver_arguments,
            max_steps=max_steps,
        ).as_dict()

    return server


def main() -> None:
    """Run the FastMCP server over the default stdio transport."""
    create_server().run()
