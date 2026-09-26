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
NPM_NAME_MAX_LENGTH = 214
PRESENTATION_FILES = ("slides.md", "package.json", "presentation-manifest.json")
# Characters Slidev's Markdown, MDC, KaTeX, HTML and Vue template layers can interpret. Entity
# escaping is not enough: markdown-it decodes ``&#123;`` back to ``{`` before Vue compiles the
# slide, so these are removed from the rendered subject line (the manifest keeps the exact
# subject).
_ACTIVE_CHARS = frozenset("<>{}`*_[]#|\\~$&\"'^=!:")
_HYPHEN_RUN = re.compile(r"-{3,}")
_FENCE_BREAK = re.compile(r"(?m)^[ \t]{0,3}(`{3,}|~{3,})")


@dataclass(frozen=True, slots=True)
class SlidevPresentationFiles:
    """The three rendered projection files, produced under one verification."""

    slides_markdown: str
    package_json: str
    manifest_json: str

    def by_name(self) -> dict[str, str]:
        """Return file name to exact content."""
        return dict(
            zip(
                PRESENTATION_FILES,
                (self.slides_markdown, self.package_json, self.manifest_json),
                strict=True,
            )
        )


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
        for document in self.bundle.documents:
            if _FENCE_BREAK.search(document.content):
                message = (
                    "MMDIO-PRESENT-002 document content would terminate its Slidev mermaid "
                    f"fence: {document.name!r}"
                )
                raise ValueError(message)

    def render(self) -> SlidevPresentationFiles:
        """Verify once and render every projection file from that single verification."""
        self.verify()
        slides = self._slides()
        manifest = _dumps(self._manifest(slides))
        return SlidevPresentationFiles(
            slides_markdown=slides,
            package_json=self._package(),
            manifest_json=manifest,
        )

    def slides_markdown(self) -> str:
        """Render deterministic Slidev Markdown from admitted DFCM projections only."""
        self.verify()
        return self._slides()

    def _slides(self) -> str:
        matrix = self.bundle.dfcm_matrix()
        title = self.bundle.graph.subject
        lines = [
            "---",
            "theme: default",
            f"title: {_frontmatter_scalar(_inert_inline(title))}",
            "info: |",
            "  Deterministic mmdio projection of one exact planning graph.",
            f"  Claim ceiling: {PRESENTATION_CLAIM_CEILING}.",
            "highlighter: shiki",
            "transition: slide-left",
            "mdc: true",
            "---",
            "",
            f"# {_inert_inline(title)}",
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
        return self._package()

    def _package(self) -> str:
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
        return _dumps(package)

    def manifest(self) -> dict[str, object]:
        """Return the exact evidence identity for this presentation projection."""
        self.verify()
        return self._manifest(self._slides())

    def _manifest(self, slides: str) -> dict[str, object]:
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
        return _dumps(self.manifest())


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
    files = presentation.render()
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, content in files.by_name().items():
        path = root / name
        path.write_text(content, encoding="utf-8")
        paths.append(path)
    return tuple(paths)


def verify_written_slidev_presentation(
    presentation: SlidevPresentation,
    output_dir: str | Path,
) -> None:
    """Replay the projection and refuse any written file whose bytes differ."""
    files = presentation.render()
    root = Path(output_dir)
    for name, expected in files.by_name().items():
        path = root / name
        if not path.is_file():
            message = f"MMDIO-PRESENT-003 presentation file missing: {name}"
            raise ValueError(message)
        if path.read_bytes() != expected.encode("utf-8"):
            message = f"MMDIO-PRESENT-003 presentation replay mismatch: {name}"
            raise ValueError(message)


def _dumps(value: object) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def _frontmatter_scalar(text: str) -> str:
    r"""Return a YAML double-quoted scalar that cannot end Slidev's headmatter early.

    Slidev also renders the headmatter ``title`` through Markdown into a Vue template, so callers
    pass the already inert inline form of the subject; the manifest keeps the exact subject.

    Slidev extracts the first slide's frontmatter with ``/^---.*\r?\n([\s\S]*?)---/``: the
    first ``---`` anywhere, even inside a quoted value, closes it. Runs of three or more hyphens
    are therefore written as ``\u002d`` escapes, which YAML decodes back to the same inert line.
    """
    encoded = json.dumps(text, ensure_ascii=True)
    return _HYPHEN_RUN.sub(lambda match: "\\u002d" * len(match.group()), encoded)


def _inert_inline(text: str) -> str:
    """Render untrusted subject text as one inert line for Slidev.

    Collapses line breaks (which could open new Slidev slides or headmatter) and replaces every
    character Slidev's Markdown/MDC/KaTeX/HTML/Vue layers could interpret with a space.
    """
    cleaned = "".join(" " if char in _ACTIVE_CHARS else char for char in text)
    return " ".join(cleaned.split()) or "mmdio"


def _package_name(subject: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", subject.lower()).strip("-")
    if not value:
        value = "mmdio"
    suffix = "-deck"
    if len(value) + len(suffix) > NPM_NAME_MAX_LENGTH:
        digest = sha256(subject.encode()).hexdigest()[:12]
        keep = NPM_NAME_MAX_LENGTH - len(suffix) - len(digest) - 1
        value = f"{value[:keep].rstrip('-')}-{digest}"
    return f"{value}{suffix}"
