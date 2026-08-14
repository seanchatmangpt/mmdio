"""DFCM laws for formal-planning documentation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mmdio.planning import (
    DFCMAxis,
    DFCMStatus,
    PlanningDFCMCorpus,
    PlanningEdge,
    PlanningEdgeKind,
    PlanningNode,
    PlanningNodeKind,
    enumerate_candidates,
    generate_planning_bundle,
    generate_planning_dfcm,
    generate_planning_documents,
    graph,
    write_planning_bundle,
)


def _requirements_subject():
    return graph(
        formalism="pddl",
        subject="dfcm-requirements",
        nodes=(
            PlanningNode("ready", PlanningNodeKind.STATE, "Ready"),
            PlanningNode("deploy", PlanningNodeKind.ACTION, "Deploy"),
            PlanningNode("goal", PlanningNodeKind.GOAL, "Healthy"),
            PlanningNode("control", PlanningNodeKind.CONSTRAINT, "Authorized"),
        ),
        edges=(
            PlanningEdge("ready", "deploy", PlanningEdgeKind.PRECONDITION),
            PlanningEdge("deploy", "goal", PlanningEdgeKind.EFFECT),
            PlanningEdge("control", "goal", PlanningEdgeKind.DEPENDENCY),
        ),
    )


def test_dfcm_cartesian_engine_enumerates_every_candidate_once() -> None:
    axes = (
        DFCMAxis("formalism", ("pddl", "ppddl")),
        DFCMAxis("projection", ("topology", "summary", "states")),
    )
    candidates = enumerate_candidates(axes)
    assert len(candidates) == 6
    assert len({candidate.digest() for candidate in candidates}) == 6
    assert [candidate.canonical_dict() for candidate in candidates] == [
        {"formalism": "pddl", "projection": "topology"},
        {"formalism": "pddl", "projection": "summary"},
        {"formalism": "pddl", "projection": "states"},
        {"formalism": "ppddl", "projection": "topology"},
        {"formalism": "ppddl", "projection": "summary"},
        {"formalism": "ppddl", "projection": "states"},
    ]


def test_dfcm_dispositions_all_eight_planning_projection_candidates() -> None:
    subject = _requirements_subject()
    matrix = generate_planning_dfcm(subject)
    matrix.verify_complete()
    assert matrix.candidate_count == 8
    assert matrix.admitted_count == 3
    assert matrix.refused_count == 5
    assert {cell.projection_name for cell in matrix.admitted} == {
        "topology",
        "summary",
        "requirements",
    }
    assert {cell.status for cell in matrix.cells} == {
        DFCMStatus.ADMITTED,
        DFCMStatus.REFUSED,
    }
    assert all(cell.reason_code.startswith("MMDIO-DFCM-") for cell in matrix.cells)


def test_dfcm_is_independent_spec_and_must_equal_manufactured_documents() -> None:
    subject = graph(
        formalism="ppddl",
        subject="dfcm-uncertainty",
        nodes=(
            PlanningNode(
                "migrate",
                PlanningNodeKind.ACTION,
                "Migrate",
                {"start": 0, "duration": 30, "actor": "Platform", "target_actor": "Cloud"},
            ),
            PlanningNode("success", PlanningNodeKind.STATE, "Success"),
            PlanningNode("degraded", PlanningNodeKind.STATE, "Degraded"),
        ),
        edges=(
            PlanningEdge(
                "migrate",
                "success",
                PlanningEdgeKind.PROBABILISTIC,
                attributes={"probability": 0.9},
            ),
            PlanningEdge(
                "migrate",
                "degraded",
                PlanningEdgeKind.PROBABILISTIC,
                attributes={"probability": 0.1},
            ),
        ),
    )
    matrix = generate_planning_dfcm(subject)
    documents = generate_planning_documents(subject)
    matrix.verify_documents(documents)
    assert {cell.projection_name for cell in matrix.admitted} == {
        document.name for document in documents
    }

    with pytest.raises(ValueError, match="MMDIO-DFCM-009"):
        matrix.verify_documents(documents[:-1])


def test_dfcm_bundle_manufactures_evidence_for_admitted_and_refused_cells(
    tmp_path: Path,
) -> None:
    bundle = generate_planning_bundle(_requirements_subject())
    bundle.verify()
    matrix = bundle.dfcm_matrix()
    manifest = bundle.manifest()
    assert manifest["dfcm"]["digest"] == matrix.digest()
    assert manifest["dfcm"]["candidate_count"] == 8

    written = write_planning_bundle(bundle, tmp_path)
    assert tmp_path / "dfcm.json" in written
    assert tmp_path / "dfcm.md" in written
    assert (tmp_path / "dfcm.json").exists()
    assert (tmp_path / "dfcm.md").exists()

    refusal_files = sorted((tmp_path / "refusals").glob("*.refusal.json"))
    receipt_files = sorted((tmp_path / "receipts").glob("*.receipt.json"))
    assert len(refusal_files) == matrix.refused_count
    assert len(receipt_files) == matrix.admitted_count
    assert len(refusal_files) + len(receipt_files) == matrix.candidate_count

    refusal = json.loads(refusal_files[0].read_text(encoding="utf-8"))
    assert refusal["status"] == "REFUSED"
    assert refusal["candidate"]["formalism"] == "pddl"
    assert refusal["candidate"]["projection"]


def test_dfcm_corpus_closes_five_formalisms_over_forty_projection_cells() -> None:
    subjects = (
        graph(
            formalism="pddl",
            subject="pddl",
            nodes=(PlanningNode("s", PlanningNodeKind.STATE, "S"),),
            edges=(),
        ),
        graph(
            formalism="ppddl",
            subject="ppddl",
            nodes=(
                PlanningNode("a", PlanningNodeKind.ACTION, "A"),
                PlanningNode("s", PlanningNodeKind.STATE, "S"),
            ),
            edges=(
                PlanningEdge(
                    "a",
                    "s",
                    PlanningEdgeKind.PROBABILISTIC,
                    attributes={"probability": 1.0},
                ),
            ),
        ),
        graph(
            formalism="pddl+",
            subject="pddl+",
            nodes=(
                PlanningNode(
                    "p",
                    PlanningNodeKind.PROCESS,
                    "P",
                    {"start": 0, "duration": 1},
                ),
                PlanningNode("e", PlanningNodeKind.EVENT, "E", {"time": 1}),
            ),
            edges=(PlanningEdge("p", "e", PlanningEdgeKind.TEMPORAL),),
        ),
        graph(
            formalism="rddl",
            subject="rddl",
            nodes=(
                PlanningNode("s0", PlanningNodeKind.STATE, "S0"),
                PlanningNode("s1", PlanningNodeKind.STATE, "S1"),
            ),
            edges=(PlanningEdge("s0", "s1", PlanningEdgeKind.TRANSITION),),
        ),
        graph(
            formalism="powl",
            subject="powl",
            nodes=(
                PlanningNode("a", PlanningNodeKind.ACTION, "A"),
                PlanningNode("b", PlanningNodeKind.ACTION, "B"),
            ),
            edges=(PlanningEdge("a", "b", PlanningEdgeKind.PRECEDENCE),),
        ),
    )
    matrices = tuple(generate_planning_dfcm(subject) for subject in subjects)
    corpus = PlanningDFCMCorpus(matrices)
    corpus.verify()
    assert corpus.candidate_count == 40
    assert corpus.admitted_count + corpus.refused_count == 40
    assert corpus.canonical_dict()["authority"] == "non-actuating"


def test_dfcm_digest_and_markdown_are_deterministic() -> None:
    subject = _requirements_subject()
    left = generate_planning_dfcm(subject)
    right = generate_planning_dfcm(subject)
    assert left.canonical_json() == right.canonical_json()
    assert left.digest() == right.digest()
    assert left.markdown() == right.markdown()
    assert "DFCM Projection Matrix" in left.markdown()
