"""Deterministic filesystem projection for planning-document bundles."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .bundle import PlanningDocumentationBundle


def write_planning_bundle(
    bundle: PlanningDocumentationBundle,
    output_dir: str | Path,
) -> tuple[Path, ...]:
    """Write canonical graph, plan book, Mermaid views, receipts, and manifest."""
    bundle.verify()
    root = Path(output_dir)
    diagrams_dir = root / "diagrams"
    receipts_dir = root / "receipts"
    diagrams_dir.mkdir(parents=True, exist_ok=True)
    receipts_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []

    graph_path = root / "planning-graph.json"
    graph_path.write_text(
        json.dumps(bundle.graph.canonical_dict(), sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    written.append(graph_path)

    markdown_path = root / "plan.md"
    markdown_path.write_text(bundle.markdown(), encoding="utf-8")
    written.append(markdown_path)

    for document, receipt in zip(bundle.documents, bundle.receipts, strict=True):
        diagram_path = diagrams_dir / f"{document.name}.{document.diagram_type}.mmd"
        diagram_path.write_text(document.content, encoding="utf-8")
        written.append(diagram_path)

        receipt_path = receipts_dir / f"{document.name}.receipt.json"
        receipt_path.write_text(
            json.dumps(asdict(receipt), sort_keys=True, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(receipt_path)

    manifest_path = root / "manifest.json"
    manifest_path.write_text(bundle.manifest_json(), encoding="utf-8")
    written.append(manifest_path)

    return tuple(written)
