"""Typer projection of the shared mmdio decision service."""

from __future__ import annotations

from typing import Annotated, Any
import json

import typer

from mmdio.decide.models import DecisionRefusal
from mmdio.decide.service import DecisionService

app = typer.Typer(
    name="decide",
    help="Match, solve, visualize, and receipt scikit-decide problems.",
    no_args_is_help=True,
)


def get_service() -> DecisionService:
    """Return the default decision service; isolated for test substitution."""
    return DecisionService()


def _object(value: str, option: str) -> dict[str, Any]:
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError as error:
        raise typer.BadParameter(f"{option} must be valid JSON: {error.msg}") from error
    if not isinstance(decoded, dict):
        raise typer.BadParameter(f"{option} must decode to a JSON object")
    return decoded


def _emit(payload: Any) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))


def _refuse(error: DecisionRefusal) -> None:
    _emit(error.as_dict())
    raise typer.Exit(code=3)


@app.command("catalog")
def catalog() -> None:
    """List registered scikit-decide domains and solvers."""
    try:
        _emit(get_service().catalog().as_dict())
    except DecisionRefusal as error:
        _refuse(error)


@app.command("match")
def match(
    domain: Annotated[str, typer.Argument(help="Registered scikit-decide domain name")],
    domain_arguments: Annotated[
        str,
        typer.Option("--domain-arguments", help="Domain constructor arguments as JSON"),
    ] = "{}",
    mermaid: Annotated[
        bool,
        typer.Option("--mermaid", help="Emit a Mermaid compatibility flowchart"),
    ] = False,
) -> None:
    """Find registered solvers compatible with a domain."""
    try:
        arguments = _object(domain_arguments, "--domain-arguments")
        service = get_service()
        if mermaid:
            typer.echo(service.match_mermaid(domain, domain_arguments=arguments), nl=False)
        else:
            _emit(service.match(domain, domain_arguments=arguments).as_dict())
    except DecisionRefusal as error:
        _refuse(error)


@app.command("solve")
def solve(
    domain: Annotated[str, typer.Argument(help="Registered scikit-decide domain name")],
    solver: Annotated[
        str | None,
        typer.Option("--solver", help="Compatible solver; defaults to the first deterministic match"),
    ] = None,
    domain_arguments: Annotated[
        str,
        typer.Option("--domain-arguments", help="Domain constructor arguments as JSON"),
    ] = "{}",
    solver_arguments: Annotated[
        str,
        typer.Option("--solver-arguments", help="Solver constructor arguments as JSON"),
    ] = "{}",
    max_steps: Annotated[
        int,
        typer.Option("--max-steps", min=1, help="Maximum rollout transitions"),
    ] = 100,
    mermaid: Annotated[
        bool,
        typer.Option("--mermaid", help="Emit only the Mermaid rollout projection"),
    ] = False,
) -> None:
    """Solve and execute a bounded, receipt-bearing rollout."""
    try:
        result = get_service().solve(
            domain,
            solver=solver,
            domain_arguments=_object(domain_arguments, "--domain-arguments"),
            solver_arguments=_object(solver_arguments, "--solver-arguments"),
            max_steps=max_steps,
        )
        if mermaid:
            typer.echo(result.mermaid, nl=False)
        else:
            _emit(result.as_dict())
    except DecisionRefusal as error:
        _refuse(error)
