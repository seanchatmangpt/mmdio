"""mmdio CLI."""

import typer
from rich import print as rprint

from mmdio.decide.cli import app as decide_app

app = typer.Typer(name="mmdio", no_args_is_help=True)
app.add_typer(
    decide_app,
    name="decide",
    help="Match, solve, visualize, and receipt formal decision problems.",
)


@app.command()
def fire(name: str = "Chell") -> None:
    """Fire portal gun."""
    rprint(f"[bold red]Alert![/bold red] {name} fired [green]portal gun[/green] :boom:")
