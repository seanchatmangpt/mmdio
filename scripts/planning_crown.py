#!/usr/bin/env python3
"""Manufacture a five-formalism planning-document oracle corpus and receipt summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mmdio.planning import (
    PlanningEdge,
    PlanningEdgeKind,
    PlanningNode,
    PlanningNodeKind,
    generate_planning_bundle,
    graph,
    write_planning_bundle,
)


def subjects():
    """Return bounded fixtures spanning every admitted planning formalism and document view."""
    yield graph(
        formalism="pddl",
        subject="Deterministic enterprise change",
        nodes=(
            PlanningNode("ready", PlanningNodeKind.STATE, "Change ready"),
            PlanningNode("deploy", PlanningNodeKind.ACTION, "Deploy change"),
            PlanningNode("goal", PlanningNodeKind.GOAL, "Service healthy"),
            PlanningNode("control", PlanningNodeKind.CONSTRAINT, "Change is authorized"),
        ),
        edges=(
            PlanningEdge("ready", "deploy", PlanningEdgeKind.PRECONDITION),
            PlanningEdge("deploy", "goal", PlanningEdgeKind.EFFECT),
            PlanningEdge("control", "goal", PlanningEdgeKind.DEPENDENCY),
        ),
    )
    yield graph(
        formalism="ppddl",
        subject="Probabilistic workload migration",
        nodes=(
            PlanningNode("migrate", PlanningNodeKind.ACTION, "Migrate workload", {"start": 0, "duration": 30, "actor": "Platform", "target_actor": "Cloud"}),
            PlanningNode("success", PlanningNodeKind.STATE, "Migration success"),
            PlanningNode("degraded", PlanningNodeKind.STATE, "Migration degraded"),
        ),
        edges=(
            PlanningEdge("migrate", "success", PlanningEdgeKind.PROBABILISTIC, "success", {"probability": 0.94}),
            PlanningEdge("migrate", "degraded", PlanningEdgeKind.PROBABILISTIC, "degraded", {"probability": 0.06}),
        ),
    )
    yield graph(
        formalism="pddl+",
        subject="Autonomic capacity control",
        nodes=(
            PlanningNode("grow", PlanningNodeKind.PROCESS, "Demand growth", {"start": 0, "duration": 60}),
            PlanningNode("threshold", PlanningNodeKind.EVENT, "Capacity threshold crossed", {"time": 60}),
            PlanningNode("scale", PlanningNodeKind.ACTION, "Scale capacity", {"start": 60, "duration": 15}),
        ),
        edges=(
            PlanningEdge("grow", "threshold", PlanningEdgeKind.TEMPORAL),
            PlanningEdge("threshold", "scale", PlanningEdgeKind.CAUSAL),
        ),
    )
    yield graph(
        formalism="rddl",
        subject="Stochastic demand policy",
        nodes=(
            PlanningNode("demand_t", PlanningNodeKind.STATE, "Demand t"),
            PlanningNode("demand_next", PlanningNodeKind.STATE, "Demand t plus 1"),
            PlanningNode("profit", PlanningNodeKind.REWARD, "Profit"),
        ),
        edges=(
            PlanningEdge("demand_t", "demand_next", PlanningEdgeKind.PROBABILISTIC, "transition", {"probability": 0.7}),
            PlanningEdge("demand_next", "profit", PlanningEdgeKind.REWARD, "expected value", {"value": 100}),
        ),
    )
    yield graph(
        formalism="powl-2.0",
        subject="Partial-order release plan",
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


def main(argv: list[str] | None = None) -> int:
    """Generate the corpus and emit one machine-readable crown receipt."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)

    receipt = {
        "schema": "mmdio.planning-crown/1",
        "claim": "FIVE_FORMALISM_RECEIPT_BEARING_MERMAID_PROJECTION_ONLY",
        "subjects": [],
    }
    for subject in subjects():
        bundle = generate_planning_bundle(subject)
        path = root / subject.formalism.replace("+", "plus").replace(".", "_")
        write_planning_bundle(bundle, path)
        receipt["subjects"].append(
            {
                "formalism": subject.formalism,
                "planning_digest": subject.digest(),
                "documents": [document.diagram_type for document in bundle.documents],
                "manifest": bundle.manifest(),
            }
        )

    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
