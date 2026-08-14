"""Primary Typer CLI integration for planning-document manufacture."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mmdio.cli import app


runner = CliRunner()


def test_primary_cli_generates_planning_bundle(tmp_path: Path) -> None:
    source = tmp_path / "graph.json"
    source.write_text(
        json.dumps(
            {
                "formalism": "pddl",
                "subject": "primary-cli",
                "nodes": [
                    {"id": "goal", "kind": "goal", "label": "Done", "attributes": {}}
                ],
                "edges": [],
                "metadata": {},
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "bundle"
    result = runner.invoke(app, ["planning", str(source), "--output", str(output)])
    assert result.exit_code == 0, result.stdout
    assert "PLANNING_DOCUMENT_PROJECTION_ONLY" in result.stdout
    assert (output / "plan.md").exists()
    assert (output / "diagrams" / "topology.flowchart.mmd").exists()
