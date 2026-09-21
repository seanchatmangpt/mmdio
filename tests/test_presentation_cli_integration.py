# Copyright (c) 2026 Sean Chatman
"""Primary Typer CLI integration for semantic presentation projection."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from typer.testing import CliRunner

from mmdio.cli import app

if TYPE_CHECKING:
    from pathlib import Path


runner = CliRunner()


def test_primary_cli_generates_slidev_projection(tmp_path: Path) -> None:
    source = tmp_path / "graph.json"
    source.write_text(
        json.dumps(
            {
                "formalism": "pddl",
                "subject": "presentation-cli",
                "nodes": [{"id": "goal", "kind": "goal", "label": "Done", "attributes": {}}],
                "edges": [],
                "metadata": {},
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "deck"

    result = runner.invoke(app, ["presentation", str(source), "--output", str(output)])

    assert result.exit_code == 0, result.stdout
    assert "PRESENTATION_PROJECTION_ONLY backend=slidev files=3" in result.stdout
    assert (output / "slides.md").exists()
    assert (output / "package.json").exists()
    assert (output / "presentation-manifest.json").exists()
