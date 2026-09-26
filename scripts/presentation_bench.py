#!/usr/bin/env python3
# Copyright (c) 2026 Sean Chatman
"""Deterministic timing benchmark for the Slidev presentation projection.

Measures, per chain-graph size N, the best-of-``--repeats`` wall time (garbage collection
disabled, as ``timeit`` does; the minimum is the least load-sensitive estimator on a shared
machine) of:

- ``bundle_verify``: one ``PlanningDocumentationBundle.verify()`` (the admission floor);
- ``render``: ``SlidevPresentation.render()`` (verify once + render three files);
- ``write``: ``write_slidev_presentation`` to a real temporary directory;
- ``replay``: ``verify_written_slidev_presentation`` against the written files.

The regression bound is machine-independent: ``write / bundle_verify`` must stay under
``--max-ratio`` for every size of at least ``--min-gated-size`` chain states (below that,
fixed file-system overhead dominates and the ratio is noise). A projection that re-verifies
the bundle once per rendered file (the pre-hardening shape) costs roughly five verifications
and exceeds the bound (interleaved best-of-5 on arm64: 7.4x-7.8x at 400-1000 states for that
shape versus 1.1x-2.2x after hardening; bound 3.5x).
"""

from __future__ import annotations

import argparse
import gc
import json
import platform
import sys
import tempfile
import time
from typing import TYPE_CHECKING

from mmdio.planning import (
    PlanningEdge,
    PlanningEdgeKind,
    PlanningNode,
    PlanningNodeKind,
    generate_planning_bundle,
    graph,
)
from mmdio.presentation import (
    generate_slidev_presentation,
    verify_written_slidev_presentation,
    write_slidev_presentation,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from mmdio.planning.model import PlanningGraph

SCHEMA = "mmdio.presentation-benchmark/1"
DEFAULT_SIZES = (10, 100, 400, 1000)
DEFAULT_MAX_RATIO = 3.5
DEFAULT_MIN_GATED_SIZE = 400


def chain(size: int) -> PlanningGraph:
    """Return a deterministic state chain of ``size`` nodes ending in one goal."""
    nodes = [PlanningNode(f"n{i}", PlanningNodeKind.STATE, f"State {i}") for i in range(size)]
    nodes.append(PlanningNode("goal", PlanningNodeKind.GOAL, "Goal"))
    edges = [
        PlanningEdge(
            f"n{i}",
            f"n{i + 1}" if i + 1 < size else "goal",
            PlanningEdgeKind.TRANSITION,
            "step",
        )
        for i in range(size)
    ]
    return graph(formalism="pddl", subject=f"bench-{size}", nodes=nodes, edges=edges)


def _best_seconds(actions: dict[str, Callable[[], object]], repeats: int) -> dict[str, float]:
    """Time every action once per round, interleaved, and keep each action's best round.

    Interleaving exposes every stage to the same machine load, so the stage ratios the bound
    uses stay stable on a shared machine even when absolute times drift.
    """
    samples: dict[str, list[float]] = {name: [] for name in actions}
    enabled = gc.isenabled()
    gc.disable()
    try:
        for _ in range(repeats):
            for name, action in actions.items():
                start = time.perf_counter()
                action()
                samples[name].append(time.perf_counter() - start)
    finally:
        if enabled:
            gc.enable()
    return {name: min(values) for name, values in samples.items()}


def measure(sizes: tuple[int, ...], repeats: int) -> list[dict[str, object]]:
    """Measure every stage for every size; return one row per size."""
    rows: list[dict[str, object]] = []
    for size in sizes:
        bundle = generate_planning_bundle(chain(size))
        deck = generate_slidev_presentation(bundle)
        with tempfile.TemporaryDirectory() as directory:
            write_slidev_presentation(deck, directory)  # warm file system + caches
            best = _best_seconds(
                {
                    "verify": bundle.verify,
                    "render": deck.render,
                    "write": lambda d=deck, o=directory: write_slidev_presentation(d, o),
                    "replay": lambda d=deck, o=directory: verify_written_slidev_presentation(d, o),
                },
                repeats,
            )
        rows.append(
            {
                "chain_states": size,
                "nodes": size + 1,
                "documents": len(bundle.documents),
                "slides_bytes": len(deck.render().slides_markdown.encode()),
                "bundle_verify_s": round(best["verify"], 6),
                "render_s": round(best["render"], 6),
                "write_s": round(best["write"], 6),
                "replay_s": round(best["replay"], 6),
                "write_over_verify": round(best["write"] / best["verify"], 3),
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    """Run the benchmark, print a JSON receipt, and enforce the regression bound."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sizes", default=",".join(map(str, DEFAULT_SIZES)))
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--max-ratio", type=float, default=DEFAULT_MAX_RATIO)
    parser.add_argument("--min-gated-size", type=int, default=DEFAULT_MIN_GATED_SIZE)
    args = parser.parse_args(argv)
    sizes = tuple(int(item) for item in args.sizes.split(",") if item)
    rows = measure(sizes, args.repeats)
    gated = [row for row in rows if int(row["chain_states"]) >= args.min_gated_size]
    if not gated:
        parser.error("no measured size reaches --min-gated-size; the bound would be vacuous")
    worst = max(float(row["write_over_verify"]) for row in gated)
    receipt = {
        "schema": SCHEMA,
        "python": platform.python_version(),
        "machine": platform.machine(),
        "repeats": args.repeats,
        "max_ratio": args.max_ratio,
        "min_gated_size": args.min_gated_size,
        "worst_write_over_verify": worst,
        "verdict": "PASS" if worst <= args.max_ratio else "REGRESSION",
        "rows": rows,
        "authority": "none",
    }
    sys.stdout.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return 0 if receipt["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
