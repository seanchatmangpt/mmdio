"""Focused crown tests for receipt-bearing formal-planning documentation."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

import pytest

from mmdio.planning import (
    PlanningEdge,
    PlanningEdgeKind,
    PlanningNode,
    PlanningNodeKind,
    generate_planning_bundle,
    generate_planning_documents,
    graph,
    normalize_formalism,
    planning_graph_from_json,
    verify_receipt,
    write_planning_bundle,
)
from mmdio.planning.__main__ import main
from mmdio.planning.projections import project_flowchart


def test_formalism_registry_normalizes_autofde_aliases() -> None:
    assert normalize_formalism("PDDL") == "pddl"
    assert normalize_formalism("PPDDL") == "ppddl"
    assert normalize_formalism("TPDDL") == "pddl+"
    assert normalize_formalism("RDDL") == "rddl"
    assert normalize_formalism("POWL") == "powl-2.0"
    with pytest.raises(ValueError, match="MMDIO-PLAN-004"):
        normalize_formalism("imaginary")


def test_canonical_identity_is_order_independent() -> None:
    nodes = (
        PlanningNode("a", PlanningNodeKind.STATE, "A"),
        PlanningNode("b", PlanningNodeKind.STATE, "B"),
    )
    edge = PlanningEdge("a", "b", PlanningEdgeKind.TRANSITION)
    left = graph(
        formalism="pddl",
        subject="identity",
        nodes=nodes,
        edges=(edge,),
        metadata={"b": 2, "a": 1},
    )
    right = graph(
        formalism="pddl",
        subject="identity",
        nodes=reversed(nodes),
        edges=(edge,),
        metadata={"a": 1, "b": 2},
    )
    assert left.canonical_json() == right.canonical_json()
    assert left.digest() == right.digest()


def test_topology_refuses_dangling_edges_and_invalid_probability() -> None:
    with pytest.raises(ValueError, match="MMDIO-PLAN-003"):
        graph(
            formalism="pddl",
            subject="dangling",
            nodes=(PlanningNode("a", PlanningNodeKind.STATE, "A"),),
            edges=(PlanningEdge("a", "missing", PlanningEdgeKind.TRANSITION),),
        )
    with pytest.raises(ValueError, match="MMDIO-PLAN-005"):
        graph(
            formalism="ppddl",
            subject="probability",
            nodes=(
                PlanningNode("a", PlanningNodeKind.ACTION, "A"),
                PlanningNode("b", PlanningNodeKind.STATE, "B"),
            ),
            edges=(
                PlanningEdge(
                    "a",
                    "b",
                    PlanningEdgeKind.PROBABILISTIC,
                    attributes={"probability": 1.1},
                ),
            ),
        )


def test_pddl_generates_topology_summary_and_requirements() -> None:
    subject = graph(
        formalism="pddl",
        subject="deployment",
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
    documents = {document.name: document for document in generate_planning_documents(subject)}
    assert set(documents) == {"topology", "summary", "requirements"}
    assert documents["topology"].content.startswith("flowchart LR\n")
    assert "precondition" in documents["topology"].content
    assert documents["summary"].content.startswith("mindmap\n")
    requirement = documents["requirements"].content
    assert requirement.startswith("requirementDiagram\n")
    assert "designConstraint control" in requirement
    assert "verifymethod: test" in requirement


def test_ppddl_preserves_probability_schedule_and_actor_interaction() -> None:
    subject = graph(
        formalism="ppddl",
        subject="migration",
        nodes=(
            PlanningNode(
                "migrate",
                PlanningNodeKind.ACTION,
                "Migrate workload",
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
                "success",
                {"probability": 0.94},
            ),
            PlanningEdge(
                "migrate",
                "degraded",
                PlanningEdgeKind.PROBABILISTIC,
                "degraded",
                {"probability": 0.06},
            ),
        ),
    )
    documents = {document.name: document for document in generate_planning_documents(subject)}
    assert set(documents) == {"topology", "summary", "schedule", "value-flow", "interactions"}
    assert "p=0.94" in documents["topology"].content
    assert documents["value-flow"].content.startswith("sankey\n")
    assert '"Migrate workload","Success",0.94' in documents["value-flow"].content
    assert "dateFormat X" in documents["schedule"].content
    assert documents["interactions"].content.startswith("sequenceDiagram\n")
    assert "Platform" in documents["interactions"].content
    assert "Cloud" in documents["interactions"].content


def test_pddl_plus_preserves_process_event_time_and_duration() -> None:
    subject = graph(
        formalism="pddl+",
        subject="capacity",
        nodes=(
            PlanningNode("grow", PlanningNodeKind.PROCESS, "Demand growth", {"start": 0, "duration": 60}),
            PlanningNode("threshold", PlanningNodeKind.EVENT, "Threshold crossed", {"time": 60}),
            PlanningNode("scale", PlanningNodeKind.ACTION, "Scale", {"start": 60, "duration": 15}),
        ),
        edges=(
            PlanningEdge("grow", "threshold", PlanningEdgeKind.TEMPORAL),
            PlanningEdge("threshold", "scale", PlanningEdgeKind.CAUSAL),
        ),
    )
    documents = {document.name: document for document in generate_planning_documents(subject)}
    assert set(documents) == {"topology", "summary", "timeline", "schedule"}
    assert documents["timeline"].content.startswith("timeline\n")
    assert "60 : Threshold crossed" in documents["timeline"].content
    assert "Demand growth :p1, 0, 60s" in documents["schedule"].content


def test_rddl_generates_state_and_value_flow_views() -> None:
    subject = graph(
        formalism="rddl",
        subject="demand",
        nodes=(
            PlanningNode("d0", PlanningNodeKind.STATE, "Demand t"),
            PlanningNode("d1", PlanningNodeKind.STATE, "Demand t plus 1"),
            PlanningNode("profit", PlanningNodeKind.REWARD, "Profit"),
        ),
        edges=(
            PlanningEdge(
                "d0",
                "d1",
                PlanningEdgeKind.PROBABILISTIC,
                "transition",
                {"probability": 0.7},
            ),
            PlanningEdge("d1", "profit", PlanningEdgeKind.REWARD, attributes={"value": 100}),
        ),
    )
    documents = {document.name: document for document in generate_planning_documents(subject)}
    assert set(documents) == {"topology", "summary", "states", "value-flow"}
    assert documents["states"].content.startswith("stateDiagram-v2\n")
    assert "p=0.7" in documents["states"].content
    assert '"Demand t plus 1","Profit",100' in documents["value-flow"].content


def test_powl_projection_does_not_invent_order_between_concurrent_nodes() -> None:
    subject = graph(
        formalism="powl",
        subject="release",
        nodes=(
            PlanningNode("edit", PlanningNodeKind.ACTION, "Editing"),
            PlanningNode("vfx", PlanningNodeKind.ACTION, "VFX"),
            PlanningNode("release", PlanningNodeKind.ACTION, "Release"),
        ),
        edges=(
            PlanningEdge("edit", "release", PlanningEdgeKind.PRECEDENCE),
            PlanningEdge("vfx", "release", PlanningEdgeKind.PRECEDENCE),
        ),
    )
    rendered = project_flowchart(subject)
    assert "edit -->|precedence| release" in rendered
    assert "vfx -->|precedence| release" in rendered
    assert "edit -->|precedence| vfx" not in rendered
    assert "vfx -->|precedence| edit" not in rendered


def test_bundle_receipts_markdown_and_filesystem_replay(tmp_path: Path) -> None:
    subject = graph(
        formalism="pddl",
        subject="bundle",
        nodes=(PlanningNode("goal", PlanningNodeKind.GOAL, "Done"),),
        edges=(),
    )
    bundle = generate_planning_bundle(subject)
    bundle.verify()
    assert bundle.manifest()["planning_digest"] == subject.digest()
    assert bundle.manifest()["claim_ceiling"] == "PLANNING_DOCUMENT_PROJECTION_ONLY"
    assert "```mermaid" in bundle.markdown()
    for document, receipt in zip(bundle.documents, bundle.receipts, strict=True):
        verify_receipt(subject, document, receipt)
    tampered = replace(bundle.documents[0], content=bundle.documents[0].content + "%% tampered\n")
    with pytest.raises(ValueError, match="MMDIO-PLAN-008"):
        verify_receipt(subject, tampered, bundle.receipts[0])

    written = write_planning_bundle(bundle, tmp_path)
    assert tmp_path / "planning-graph.json" in written
    assert tmp_path / "plan.md" in written
    assert tmp_path / "manifest.json" in written
    assert (tmp_path / "diagrams" / "topology.flowchart.mmd").exists()
    assert (tmp_path / "receipts" / "topology.receipt.json").exists()


def test_json_lift_and_cli_project(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    payload = {
        "formalism": "TPDDL",
        "subject": "cli",
        "nodes": [
            {
                "id": "process",
                "kind": "process",
                "label": "Demand growth",
                "attributes": {"start": 0, "duration": 10},
            },
            {
                "id": "event",
                "kind": "event",
                "label": "Threshold",
                "attributes": {"time": 10},
            },
        ],
        "edges": [
            {
                "source": "process",
                "target": "event",
                "kind": "temporal",
                "label": None,
                "attributes": {},
            }
        ],
        "metadata": {},
    }
    subject = planning_graph_from_json(json.dumps(payload))
    assert subject.formalism == "pddl+"

    source = tmp_path / "graph.json"
    source.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "output"
    assert main(["project", str(source), "--output", str(output)]) == 0
    assert (output / "plan.md").exists()
    assert (output / "diagrams" / "timeline.timeline.mmd").exists()
    assert "PLANNING_DOCUMENT_PROJECTION_ONLY" in capsys.readouterr().out


def test_flowchart_labels_remain_inert_data() -> None:
    subject = graph(
        formalism="pddl",
        subject="security",
        nodes=(PlanningNode("x", PlanningNodeKind.STATE, 'click x javascript:alert("x")'),),
        edges=(),
    )
    rendered = project_flowchart(subject)
    assert rendered.startswith("flowchart LR\n")
    assert "\nclick " not in rendered
    assert '\\"x\\"' in rendered
