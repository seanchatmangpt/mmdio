"""mmdio CLI."""

from pathlib import Path

import typer
from rich import print as rprint

from mmdio.planning import generate_planning_bundle, load_planning_graph, write_planning_bundle

app = typer.Typer()


@app.command()
def fire(name: str = "Chell") -> None:
    """Fire portal gun."""
    rprint(f"[bold red]Alert![/bold red] {name} fired [green]portal gun[/green] :boom:")


@app.command()
def planning(
    graph: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    output: Path = typer.Option(..., "--output", "-o", file_okay=False),
) -> None:
    """Generate every justified Mermaid document for a canonical planning graph."""
    subject = load_planning_graph(graph)
    bundle = generate_planning_bundle(subject)
    written = write_planning_bundle(bundle, output)
    typer.echo(bundle.manifest_json(), nl=False)
    typer.echo(f"PLANNING_DOCUMENT_PROJECTION_ONLY files={len(written)}")
