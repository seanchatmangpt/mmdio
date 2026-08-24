"""Standalone CLI for deterministic planning-document projection."""

from __future__ import annotations

import argparse

from .bundle import generate_planning_bundle
from .io import write_planning_bundle
from .jsonio import load_planning_graph


def main(argv: list[str] | None = None) -> int:
    """Execute the bounded planning-document CLI."""
    parser = argparse.ArgumentParser(prog="python -m mmdio.planning")
    subparsers = parser.add_subparsers(dest="command", required=True)

    project = subparsers.add_parser(
        "project",
        help="generate every applicable Mermaid planning document",
    )
    project.add_argument("graph", help="canonical PlanningGraph JSON file")
    project.add_argument("--output", "-o", required=True, help="output directory")

    args = parser.parse_args(argv)
    if args.command != "project":
        return 2

    subject = load_planning_graph(args.graph)
    bundle = generate_planning_bundle(subject)
    written = write_planning_bundle(bundle, args.output)
    print(bundle.manifest_json(), end="")
    print(f"PLANNING_DOCUMENT_PROJECTION_ONLY files={len(written)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
