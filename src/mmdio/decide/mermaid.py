"""Deterministic Mermaid projections for decision catalogs and rollouts."""

from __future__ import annotations

import json
from typing import Any, Iterable

from mmdio.decide.models import DecisionMatch, DecisionStep

_MAX_LABEL = 96


def _label(value: Any) -> str:
    rendered = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    if len(rendered) > _MAX_LABEL:
        rendered = f"{rendered[: _MAX_LABEL - 3]}..."
    return rendered.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def match_to_mermaid(result: DecisionMatch) -> str:
    """Render a domain-to-compatible-solvers flowchart."""
    lines = ["flowchart LR", f'  domain["Domain: {_label(result.domain)}"]']
    if not result.compatible_solvers:
        lines.append('  none["No compatible solver"]')
        lines.append("  domain -->|refused| none")
        return "\n".join(lines) + "\n"

    for index, solver in enumerate(result.compatible_solvers):
        node = f"solver_{index}"
        lines.append(f'  {node}["Solver: {_label(solver)}"]')
        lines.append(f"  domain -->|compatible| {node}")
    return "\n".join(lines) + "\n"


def rollout_to_mermaid(initial_observation: Any, steps: Iterable[DecisionStep]) -> str:
    """Render a bounded rollout as a Mermaid state diagram."""
    step_list = list(steps)
    lines = ["stateDiagram-v2", f'  state "{_label(initial_observation)}" as S0', "  [*] --> S0"]
    for step in step_list:
        target = f"S{step.index + 1}"
        lines.append(f'  state "{_label(step.next_observation)}" as {target}')
        lines.append(f'  S{step.index} --> {target}: {_label(step.action)}')
    if step_list and step_list[-1].termination:
        lines.append(f"  S{step_list[-1].index + 1} --> [*]")
    return "\n".join(lines) + "\n"
