"""mmdio CLI."""

from pathlib import Path

import typer
from rich import print as rprint

from mmdio.planning import generate_planning_bundle, load_planning_graph, write_planning_bundle
from mmdio.presentation import generate_slidev_presentation, write_slidev_presentation

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


@app.command()
def presentation(
    graph: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    output: Path = typer.Option(..., "--output", "-o", file_okay=False),
) -> None:
    """Project an exact planning/DFCM bundle into a powerless Slidev deck."""
    subject = load_planning_graph(graph)
    bundle = generate_planning_bundle(subject)
    deck = generate_slidev_presentation(bundle)
    written = write_slidev_presentation(deck, output)
    typer.echo(deck.manifest_json(), nl=False)
    typer.echo(f"PRESENTATION_PROJECTION_ONLY backend=slidev files={len(written)}")
