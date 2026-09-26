# Copyright (c) 2026 Sean Chatman
"""Adversarial and boundary courts for the Slidev presentation projection.

Every collaborator is real: real planning graphs, real bundles, real DFCM matrices, real
files on disk. Each test names the falsifier it guards.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import re
from typing import TYPE_CHECKING

import pytest

from mmdio.planning import (
    PlanningEdge,
    PlanningEdgeKind,
    PlanningNode,
    PlanningNodeKind,
    generate_planning_bundle,
    graph,
)
from mmdio.planning.dfcm import generate_planning_dfcm
from mmdio.planning.receipts import receipt_for
from mmdio.presentation import (
    NPM_NAME_MAX_LENGTH,
    PRESENTATION_FILES,
    SlidevPresentation,
    generate_slidev_presentation,
    verify_written_slidev_presentation,
    write_slidev_presentation,
)

if TYPE_CHECKING:
    from pathlib import Path

    from mmdio.planning.model import PlanningGraph

FORMALISMS = ("pddl", "ppddl", "pddl+", "rddl", "powl-2.0")


def _graph(
    subject: str = "hardening",
    *,
    label: str = "Done",
    formalism: str = "pddl",
    reverse: bool = False,
) -> PlanningGraph:
    nodes = [
        PlanningNode("start", PlanningNodeKind.STATE, "Start"),
        PlanningNode("act", PlanningNodeKind.ACTION, "Act"),
        PlanningNode("goal", PlanningNodeKind.GOAL, label),
    ]
    edges = [
        PlanningEdge("start", "act", PlanningEdgeKind.PRECONDITION, "pre"),
        PlanningEdge("act", "goal", PlanningEdgeKind.EFFECT, "eff"),
    ]
    if reverse:
        nodes.reverse()
        edges.reverse()
    return graph(formalism=formalism, subject=subject, nodes=nodes, edges=edges)


def _slide_separators(markdown: str) -> int:
    """Count Slidev slide separators outside fenced code (the real Slidev split rule)."""
    count = 0
    fenced = False
    for line in markdown.splitlines():
        if re.match(r"^\s{0,3}(```|~~~)", line):
            fenced = not fenced
            continue
        if not fenced and line == "---":
            count += 1
    return count


# --- malformed subject: slide/frontmatter/HTML/Vue injection -------------------------------


@pytest.mark.parametrize(
    "subject",
    [
        "x\n---\nlayout: cover\n---\n# injected",
        "<script>alert(1)</script>",
        "{{ $slidev.nav.next() }}",
        "`code` *bold* [link](http://e) # h | t",
        "line\r\nbreak\u2028separator",
        "Plan f\u00fcr Gr\u00f6\u00dfe\u0085next",
    ],
)
def test_hostile_subject_cannot_add_slides_or_markup(subject: str) -> None:
    benign = generate_slidev_presentation(generate_planning_bundle(_graph("benign")))
    hostile = generate_slidev_presentation(generate_planning_bundle(_graph(subject)))

    markdown = hostile.slides_markdown()
    assert _slide_separators(markdown) == _slide_separators(benign.slides_markdown())
    lines = markdown.split("\n")
    heading = next(line for line in lines if line.startswith("# "))
    body = heading[2:]
    for forbidden in "<>{}`*_[]#|\\~$&\"'^=!:\r\u2028":
        assert forbidden not in body
    # Slidev renders the headmatter title as Markdown too: it must be the same inert line,
    # carried as a single ASCII JSON-quoted scalar.
    title_line = next(line for line in lines if line.startswith("title: "))
    assert title_line.isascii()
    assert json.loads(title_line.removeprefix("title: ")) == body
    # the manifest still names the exact, unescaped subject
    assert hostile.manifest()["subject"] == subject


# Slidev 0.49 @slidev/parser extracts the first slide's headmatter with this exact pattern.
SLIDEV_HEADMATTER = re.compile(r"^---.*\r?\n([\s\S]*?)---")


@pytest.mark.parametrize(
    "subject",
    ["a---b", "----", "x\n---\nlayout: cover", "semantic-platform", "a--b", "\\---"],
)
def test_headmatter_survives_slidev_extraction(subject: str) -> None:
    deck = generate_slidev_presentation(generate_planning_bundle(_graph(subject)))
    markdown = deck.slides_markdown()
    headmatter = SLIDEV_HEADMATTER.match(markdown)
    assert headmatter is not None
    block = headmatter.group(1)
    assert block.endswith("mdc: true\n")
    title_line = next(line for line in block.split("\n") if line.startswith("title: "))
    title = json.loads(title_line.removeprefix("title: "))
    heading = next(line for line in markdown.split("\n") if line.startswith("# "))
    assert title == heading[2:]
    assert "-" not in subject or "-" in title


def test_benign_subject_heading_is_unchanged() -> None:
    deck = generate_slidev_presentation(generate_planning_bundle(_graph("semantic-platform")))
    assert "# semantic-platform" in deck.slides_markdown().splitlines()


# --- malformed document content: mermaid fence break-out ----------------------------------


def test_content_that_terminates_the_mermaid_fence_is_refused() -> None:
    bundle = generate_planning_bundle(_graph())
    first = bundle.documents[0]
    forged = dataclasses.replace(first, content=first.content + "\n```\n---\n# forged slide\n")
    # Rebind receipts so only the fence guard (not the receipt court) can refuse it.
    receipts = tuple(receipt_for(bundle.graph, doc) for doc in (forged, *bundle.documents[1:]))
    rebound = dataclasses.replace(
        bundle, documents=(forged, *bundle.documents[1:]), receipts=receipts
    )
    with pytest.raises(ValueError, match="MMDIO-PRESENT-002"):
        SlidevPresentation(bundle=rebound).slides_markdown()


@pytest.mark.parametrize("formalism", FORMALISMS)
@pytest.mark.parametrize("label", ["```", "~~~", "a\n```\n---\n# x", "```mermaid"])
def test_backtick_labels_never_break_generated_fences(formalism: str, label: str) -> None:
    deck = generate_slidev_presentation(
        generate_planning_bundle(_graph(label=label, formalism=formalism))
    )
    markdown = deck.slides_markdown()
    fences = [line for line in markdown.splitlines() if re.match(r"^\s{0,3}(```|~~~)", line)]
    assert len(fences) == 2 * len(deck.bundle.documents)
    assert _slide_separators(markdown) == 2 * len(deck.bundle.documents) + 4


# --- wrong digest / stale subject / tampered receipt ---------------------------------------


def test_tampered_document_bytes_are_refused() -> None:
    bundle = generate_planning_bundle(_graph())
    first = bundle.documents[0]
    forged = dataclasses.replace(first, content=first.content + "\n%% forged\n")
    tampered = dataclasses.replace(bundle, documents=(forged, *bundle.documents[1:]))
    with pytest.raises(ValueError, match="MMDIO-PLAN-008"):
        generate_slidev_presentation(tampered)


def test_receipt_for_a_different_document_is_refused() -> None:
    bundle = generate_planning_bundle(_graph())
    swapped = (bundle.receipts[1], bundle.receipts[0], *bundle.receipts[2:])
    with pytest.raises(ValueError, match="MMDIO-PLAN-008"):
        generate_slidev_presentation(dataclasses.replace(bundle, receipts=swapped))


def test_stale_dfcm_matrix_from_another_subject_is_refused() -> None:
    bundle = generate_planning_bundle(_graph("current"))
    stale = generate_planning_dfcm(_graph("previous"))
    with pytest.raises(ValueError, match="MMDIO-DFCM-011"):
        generate_slidev_presentation(dataclasses.replace(bundle, dfcm=stale))


def test_bundle_rebound_to_a_different_graph_is_refused() -> None:
    bundle = generate_planning_bundle(_graph("current"))
    with pytest.raises(ValueError, match="MMDIO-PLAN-007"):
        generate_slidev_presentation(dataclasses.replace(bundle, graph=_graph("other")))


def test_empty_document_set_is_refused() -> None:
    bundle = generate_planning_bundle(_graph())
    with pytest.raises(ValueError, match="MMDIO-DFCM-009"):
        generate_slidev_presentation(dataclasses.replace(bundle, documents=(), receipts=()))


def test_dropped_receipt_is_refused() -> None:
    bundle = generate_planning_bundle(_graph())
    with pytest.raises(ValueError, match="MMDIO-PLAN-009"):
        generate_slidev_presentation(dataclasses.replace(bundle, receipts=bundle.receipts[:-1]))


# --- replay mismatch on written files ------------------------------------------------------


def test_written_projection_replays_byte_identically(tmp_path: Path) -> None:
    deck = generate_slidev_presentation(generate_planning_bundle(_graph()))
    write_slidev_presentation(deck, tmp_path / "deck")
    verify_written_slidev_presentation(deck, tmp_path / "deck")

    manifest = json.loads((tmp_path / "deck" / "presentation-manifest.json").read_text("utf-8"))
    slides = (tmp_path / "deck" / "slides.md").read_bytes()
    assert manifest["slides_sha256"] == hashlib.sha256(slides).hexdigest()


@pytest.mark.parametrize("name", PRESENTATION_FILES)
def test_edited_written_file_fails_replay(tmp_path: Path, name: str) -> None:
    deck = generate_slidev_presentation(generate_planning_bundle(_graph()))
    write_slidev_presentation(deck, tmp_path)
    target = tmp_path / name
    target.write_text(target.read_text("utf-8") + " ", encoding="utf-8")
    with pytest.raises(ValueError, match=f"MMDIO-PRESENT-003 presentation replay mismatch: {name}"):
        verify_written_slidev_presentation(deck, tmp_path)


def test_missing_written_file_fails_replay(tmp_path: Path) -> None:
    deck = generate_slidev_presentation(generate_planning_bundle(_graph()))
    write_slidev_presentation(deck, tmp_path)
    (tmp_path / "package.json").unlink()
    with pytest.raises(ValueError, match="MMDIO-PRESENT-003 presentation file missing"):
        verify_written_slidev_presentation(deck, tmp_path)


def test_projection_of_another_subject_fails_replay(tmp_path: Path) -> None:
    written = generate_slidev_presentation(generate_planning_bundle(_graph("one")))
    other = generate_slidev_presentation(generate_planning_bundle(_graph("two")))
    write_slidev_presentation(written, tmp_path)
    with pytest.raises(ValueError, match="MMDIO-PRESENT-003"):
        verify_written_slidev_presentation(other, tmp_path)


# --- duplicate delivery / reordering -------------------------------------------------------


def test_duplicate_delivery_is_idempotent(tmp_path: Path) -> None:
    deck = generate_slidev_presentation(generate_planning_bundle(_graph()))
    write_slidev_presentation(deck, tmp_path)
    first = {name: (tmp_path / name).read_bytes() for name in PRESENTATION_FILES}
    write_slidev_presentation(deck, tmp_path)
    second = {name: (tmp_path / name).read_bytes() for name in PRESENTATION_FILES}
    assert first == second


def test_node_and_edge_reordering_yields_identical_deck() -> None:
    forward = generate_slidev_presentation(generate_planning_bundle(_graph()))
    backward = generate_slidev_presentation(generate_planning_bundle(_graph(reverse=True)))
    assert forward.render() == backward.render()


def test_render_matches_individual_accessors() -> None:
    deck = generate_slidev_presentation(generate_planning_bundle(_graph()))
    files = deck.render()
    assert files.slides_markdown == deck.slides_markdown()
    assert files.package_json == deck.package_json()
    assert files.manifest_json == deck.manifest_json()


# --- unauthorized action: the projection never claims authority ----------------------------


@pytest.mark.parametrize("formalism", FORMALISMS)
def test_every_formalism_projects_powerlessly(formalism: str) -> None:
    deck = generate_slidev_presentation(generate_planning_bundle(_graph(formalism=formalism)))
    manifest = deck.manifest()
    assert manifest["authority"] == "none"
    assert manifest["claim_ceiling"] == "SEMANTIC_PRESENTATION_PROJECTION_ONLY"
    receipts = [item["receipt_sha256"] for item in manifest["document_receipts"]]
    assert receipts == [receipt.digest() for receipt in deck.bundle.receipts]
    for receipt in receipts:
        assert f"receipt {receipt}" in deck.slides_markdown()
    package = json.loads(deck.package_json())
    assert set(package["scripts"]) == {"dev", "build", "export"}
    assert "postinstall" not in package["scripts"]
    assert "preinstall" not in package["scripts"]


# --- npm package-name boundary -------------------------------------------------------------


@pytest.mark.parametrize(
    ("subject", "expected"),
    [
        ("Semantic Platform", "semantic-platform-deck"),
        ("日本語", "mmdio-deck"),
        ("---", "mmdio-deck"),
    ],
)
def test_package_name_normalization(subject: str, expected: str) -> None:
    deck = generate_slidev_presentation(generate_planning_bundle(_graph(subject)))
    assert json.loads(deck.package_json())["name"] == expected


def test_overlong_subject_yields_valid_bounded_npm_name() -> None:
    long_a = "a" * 400
    long_b = "a" * 399 + "b"
    name_a = json.loads(
        generate_slidev_presentation(generate_planning_bundle(_graph(long_a))).package_json()
    )["name"]
    name_b = json.loads(
        generate_slidev_presentation(generate_planning_bundle(_graph(long_b))).package_json()
    )["name"]
    for name in (name_a, name_b):
        assert len(name) <= NPM_NAME_MAX_LENGTH
        assert re.fullmatch(r"[a-z0-9][a-z0-9-]*-deck", name)
    assert name_a != name_b
