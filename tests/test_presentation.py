"""Tests for deterministic Slidev presentation projection."""

from __future__ import annotations

import json
from pathlib import Path

from mmdio.planning import generate_planning_bundle, load_planning_graph
from mmdio.presentation import (
    PRESENTATION_CLAIM_CEILING,
    generate_slidev_presentation,
    write_slidev_presentation,
)


def _source(path: Path) -> Path:
    path.write_text(
        json.dumps(
            {
                "formalism": "pddl",
                "subject": "semantic-platform",
                "nodes": [
                    {"id": "start", "kind": "state", "label": "Start", "attributes": {}},
                    {"id": "goal", "kind": "goal", "label": "Done", "attributes": {}},
                ],
                "edges": [
                    {
                        "source": "start",
                        "target": "goal",
                        "kind": "transition",
                        "label": "verify",
                        "attributes": {},
                    }
                ],
                "metadata": {},
            }
        ),
        encoding="utf-8",
    )
    return path


def test_slidev_projection_binds_exact_planning_and_dfcm_identity(tmp_path: Path) -> None:
    graph = load_planning_graph(_source(tmp_path / "graph.json"))
    bundle = generate_planning_bundle(graph)

    first = generate_slidev_presentation(bundle)
    second = generate_slidev_presentation(bundle)

    assert first.slides_markdown() == second.slides_markdown()
    assert first.manifest_json() == second.manifest_json()

    manifest = first.manifest()
    assert manifest["planning_digest"] == graph.digest()
    assert manifest["dfcm_digest"] == bundle.dfcm_matrix().digest()
    assert manifest["claim_ceiling"] == PRESENTATION_CLAIM_CEILING
    assert manifest["authority"] == "none"
    assert len(manifest["document_receipts"]) == len(bundle.documents)
    assert "This deck is a projection, not authority." in first.slides_markdown()


def test_slidev_projection_writes_minimal_project(tmp_path: Path) -> None:
    graph = load_planning_graph(_source(tmp_path / "graph.json"))
    presentation = generate_slidev_presentation(generate_planning_bundle(graph))

    output = tmp_path / "deck"
    written = write_slidev_presentation(presentation, output)

    assert {path.name for path in written} == {
        "slides.md",
        "package.json",
        "presentation-manifest.json",
    }
    package = json.loads((output / "package.json").read_text(encoding="utf-8"))
    assert package["scripts"]["build"] == "slidev build"
    assert "@slidev/cli" in package["dependencies"]
