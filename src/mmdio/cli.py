"""mmdio command-line interface."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

import typer

from mmdio.engine import (
    DocumentError,
    capability_records,
    canonicalize_source,
    detect_document_type,
    diff_documents,
    document_schema_for_type,
    issue_receipt,
    merge_documents,
    parse_document,
    verify_receipt,
)

app = typer.Typer(
    no_args_is_help=True,
    help=(
        "Parse, validate, canonicalize, receipt, and replay all registered "
        "Mermaid dialects."
    ),
)


def _read(path: Path | None) -> str:
    if path is None or str(path) == "-":
        return sys.stdin.read()
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise typer.BadParameter(str(exc), param_hint="PATH") from exc


def _emit(value: object) -> None:
    typer.echo(json.dumps(value, indent=2, sort_keys=True, default=str))


def _fail(exc: DocumentError) -> None:
    typer.echo(
        json.dumps({"standing": "REFUSED", "code": exc.code, "message": str(exc)}),
        err=True,
    )
    raise typer.Exit(code=2)


@app.command("types")
def list_types() -> None:
    """List all 39 executable diagram capabilities."""
    _emit({"count": len(capability_records()), "types": capability_records()})


@app.command()
def detect(
    path: Annotated[
        Path | None,
        typer.Argument(help="Mermaid file or '-' for stdin"),
    ] = None,
) -> None:
    """Detect one registered diagram type."""
    try:
        diagram_type = detect_document_type(_read(path))
    except DocumentError as exc:
        _fail(exc)
    _emit({"standing": "ALIVE", "diagram_type": diagram_type.value})


@app.command()
def parse(
    path: Annotated[
        Path | None,
        typer.Argument(help="Mermaid file or '-' for stdin"),
    ] = None,
    diagram_type: Annotated[
        str | None,
        typer.Option("--type", help="Declare a profile type"),
    ] = None,
) -> None:
    """Parse source into its exact lossless typed document."""
    try:
        document = parse_document(_read(path), diagram_type)
    except DocumentError as exc:
        _fail(exc)
    _emit(document.model_dump(mode="json"))


@app.command()
def validate(
    path: Annotated[
        Path | None,
        typer.Argument(help="Mermaid file or '-' for stdin"),
    ] = None,
    diagram_type: Annotated[
        str | None,
        typer.Option("--type", help="Declare a profile type"),
    ] = None,
    receipt: Annotated[
        Path | None,
        typer.Option("--receipt", help="Write a deterministic receipt"),
    ] = None,
) -> None:
    """Validate structure and optionally write a replay receipt."""
    try:
        document = parse_document(_read(path), diagram_type)
        evidence = issue_receipt(document)
    except DocumentError as exc:
        _fail(exc)
    if receipt is not None:
        receipt.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    _emit(
        {
            "standing": "ALIVE",
            "diagram_type": str(document.type),
            "source_sha256": document.source_sha256,
            "receipt_sha256": evidence["receipt_sha256"],
        }
    )


@app.command()
def format(
    path: Annotated[
        Path | None,
        typer.Argument(help="Mermaid file or '-' for stdin"),
    ] = None,
    check: Annotated[
        bool,
        typer.Option("--check", help="Refuse when canonical output differs"),
    ] = False,
    in_place: Annotated[
        bool,
        typer.Option("--in-place", help="Replace PATH atomically"),
    ] = False,
) -> None:
    """Canonicalize line endings, trailing whitespace, and final newline."""
    source = _read(path)
    try:
        canonical = canonicalize_source(source)
        parse_document(canonical)
    except DocumentError as exc:
        _fail(exc)
    if check and canonical != source:
        typer.echo("MMDIO-FORMAT-001: source is not canonical", err=True)
        raise typer.Exit(code=1)
    if in_place:
        if path is None or str(path) == "-":
            raise typer.BadParameter("--in-place requires a file path")
        temporary = path.with_suffix(path.suffix + ".mmdio.tmp")
        temporary.write_text(canonical, encoding="utf-8")
        temporary.replace(path)
    else:
        typer.echo(canonical, nl=False)


@app.command()
def replay(receipt: Annotated[Path, typer.Argument(help="Receipt JSON file")]) -> None:
    """Verify and replay canonical Mermaid source from a receipt."""
    try:
        carrier = json.loads(receipt.read_text(encoding="utf-8"))
        document = verify_receipt(carrier)
    except (OSError, json.JSONDecodeError) as exc:
        typer.echo(f"MMDIO-RECEIPT-001: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    except DocumentError as exc:
        _fail(exc)
    typer.echo(document.source, nl=False)


@app.command("diff")
def diff_command(
    left: Annotated[Path, typer.Argument(help="Left Mermaid file")],
    right: Annotated[Path, typer.Argument(help="Right Mermaid file")],
) -> None:
    """Diff two documents of the same registered type."""
    try:
        result = diff_documents(parse_document(_read(left)), parse_document(_read(right)))
    except DocumentError as exc:
        _fail(exc)
    _emit(result.model_dump(mode="json"))


@app.command("merge")
def merge_command(
    base: Annotated[Path, typer.Argument(help="Base Mermaid file")],
    left: Annotated[Path, typer.Argument(help="Left Mermaid file")],
    right: Annotated[Path, typer.Argument(help="Right Mermaid file")],
) -> None:
    """Execute a bounded conflict-safe three-way source merge."""
    try:
        result = merge_documents(
            parse_document(_read(base)),
            parse_document(_read(left)),
            parse_document(_read(right)),
        )
    except DocumentError as exc:
        _fail(exc)
    _emit(result.model_dump(mode="json"))


@app.command()
def schema(
    diagram_type: Annotated[str, typer.Argument(help="Canonical or internal type ID")],
) -> None:
    """Print the JSON Schema for any registered document type."""
    try:
        value = document_schema_for_type(diagram_type)
    except DocumentError as exc:
        _fail(exc)
    _emit(value)


if __name__ == "__main__":
    app()
