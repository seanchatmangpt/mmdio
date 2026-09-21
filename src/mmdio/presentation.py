# Copyright (c) 2026 Sean Chatman
"""Deterministic Slidev projection for receipt-bearing planning bundles."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mmdio.planning.bundle import PlanningDocumentationBundle


PRESENTATION_SCHEMA = "mmdio.slidev-presentation/1"
PRESENTATION_CLAIM_CEILING = "SEMANTIC_PRESENTATION_PROJECTION_ONLY"
GENERATOR_CAPABILITY = "UNSUPPORTED(ggen-marketplace,generic-planning-to-slidev)"
SLIDEV_PRIOR_ART = "ggen-marketplace/packs/slidev-iaas-paas-saas-pack"
SLIDEV_CLI_VERSION = "^0.49.0"
SLIDEV_THEME_VERSION = "^0.25.0"
VUE_VERSION = "^3.4.0"


@dataclass(frozen=True, slots=True)
class SlidevPresentation:
    """One powerless Slidev projection of an exact admitted planning bundle."""

    bundle: PlanningDocumentationBundle

    def verify(self) -> None:
        """Verify that the deck remains bound to the exact planning/DFCM subject."""
        self.bundle.verify()
        if not self.bundle.documents:
            message = "MMDIO-PRESENT-001 presentation requires at least one admitted document"
            raise ValueError(message)

    def slides_markdown(self) -> str:
        """Render deterministic Slidev Markdown from admitted DFCM projections only."""
        self.verify()
        matrix = self.bundle.dfcm_matrix()
        title = self.bundle.graph.subject
        lines = [
            "---",
            "theme: default",
            f"title: {json.dumps(title, ensure_ascii=False)}",
            "info: |",
            "  Deterministic mmdio projection of one exact planning graph.",
            f"  Claim ceiling: {PRESENTATION_CLAIM_CEILING}.",
            "highlighter: shiki",
            "transition: slide-left",
            "mdc: true",
            "---",
            "",
            f"# {title}",
            "",
            "Semantic presentation projection",
            "",
            f"- Formalism: `{self.bundle.graph.formalism}`",
            f"- Planning digest: `{self.bundle.graph.digest()}`",
            f"- DFCM digest: `{matrix.digest()}`",
            f"- Admitted views: `{matrix.admitted_count}`",
            f"- Refused views retained as evidence: `{matrix.refused_count}`",
            f"- Claim ceiling: `{PRESENTATION_CLAIM_CEILING}`",
            "",
        ]
        receipts_by_name = {receipt.document_name: receipt for receipt in self.bundle.receipts}
        for document in self.bundle.documents:
            receipt = receipts_by_name[document.name]
            lines.extend(
                (
                    "---",
                    "layout: default",
                    "---",
                    "",
                    f"# {document.name.replace('-', ' ').title()}",
                    "",
                    f"Diagram type: `{document.diagram_type}`",
                    "",
                    "```mermaid",
                    document.content.rstrip("\n"),
                    "```",
                    "",
                    (f'<div class="pt-4 text-xs opacity-50">receipt {receipt.digest()}</div>'),
                    "",
                )
            )
        lines.extend(
            (
                "---",
                "layout: section",
                "---",
                "",
                "# Evidence boundary",
                "",
                "This deck is a projection, not authority.",
                "",
                f"- Planning subject: `{self.bundle.graph.digest()}`",
                f"- DFCM closure: `{matrix.digest()}`",
                f"- Claim ceiling: `{PRESENTATION_CLAIM_CEILING}`",
                "- Slide rendering does not authorize SELECT, CONSTRUCT, or DO.",
                "- Refused DFCM projections remain refused; the deck cannot promote them.",
                "",
            )
        )
        return "\n".join(lines)

    def package_json(self) -> str:
        """Return a minimal Slidev project manifest using the marketplace precedent."""
        self.verify()
        package = {
            "name": _package_name(self.bundle.graph.subject),
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "slidev",
                "build": "slidev build",
                "export": "slidev export",
            },
            "dependencies": {
                "@slidev/cli": SLIDEV_CLI_VERSION,
                "@slidev/theme-default": SLIDEV_THEME_VERSION,
                "vue": VUE_VERSION,
            },
        }
        return json.dumps(package, sort_keys=True, indent=2, ensure_ascii=False) + "\n"

    def manifest(self) -> dict[str, object]:
        """Return the exact evidence identity for this presentation projection."""
        self.verify()
        slides = self.slides_markdown()
        matrix = self.bundle.dfcm_matrix()
        return {
            "schema": PRESENTATION_SCHEMA,
            "backend": "slidev",
            "subject": self.bundle.graph.subject,
            "formalism": self.bundle.graph.formalism,
            "planning_digest": self.bundle.graph.digest(),
            "dfcm_digest": matrix.digest(),
            "slides_sha256": sha256(slides.encode()).hexdigest(),
            "document_receipts": [
                {
                    "document_name": receipt.document_name,
                    "diagram_type": receipt.diagram_type,
                    "receipt_sha256": receipt.digest(),
                }
                for receipt in self.bundle.receipts
            ],
            "claim_ceiling": PRESENTATION_CLAIM_CEILING,
            "authority": "none",
            "manufacture": {
                "implementation": "HANDWRITTEN_PROJECTION_ADAPTER",
                "generator_capability": GENERATOR_CAPABILITY,
                "prior_art": SLIDEV_PRIOR_ART,
            },
        }

    def manifest_json(self) -> str:
        """Serialize the presentation evidence manifest deterministically."""
        return json.dumps(self.manifest(), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def generate_slidev_presentation(bundle: PlanningDocumentationBundle) -> SlidevPresentation:
    """Manufacture a powerless Slidev projection from one exact planning bundle."""
    presentation = SlidevPresentation(bundle=bundle)
    presentation.verify()
    return presentation


def write_slidev_presentation(
    presentation: SlidevPresentation,
    output_dir: str | Path,
) -> tuple[Path, ...]:
    """Write deterministic Slidev projection files without running Node or actuating."""
    presentation.verify()
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)

    paths = (
        root / "slides.md",
        root / "package.json",
        root / "presentation-manifest.json",
    )
    paths[0].write_text(presentation.slides_markdown(), encoding="utf-8")
    paths[1].write_text(presentation.package_json(), encoding="utf-8")
    paths[2].write_text(presentation.manifest_json(), encoding="utf-8")
    return paths


def _package_name(subject: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", subject.lower()).strip("-")
    if not value:
        value = "mmdio"
    return f"{value}-deck"
