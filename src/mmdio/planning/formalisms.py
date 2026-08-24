"""Canonical planning-formalism registry for Mermaid documentation projection."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FormalismProfile:
    """One admitted formal-planning language family."""

    id: str
    title: str
    description: str


PROFILES: dict[str, FormalismProfile] = {
    "pddl": FormalismProfile(
        id="pddl",
        title="PDDL",
        description="Deterministic actions, preconditions, effects, state, goals, and constraints.",
    ),
    "ppddl": FormalismProfile(
        id="ppddl",
        title="PPDDL",
        description="PDDL planning with probability-bearing outcomes and policies under uncertainty.",
    ),
    "pddl+": FormalismProfile(
        id="pddl+",
        title="PDDL+ / Temporal PDDL",
        description="Actions plus time, durative processes, continuous state, and autonomous events.",
    ),
    "rddl": FormalismProfile(
        id="rddl",
        title="RDDL",
        description="Relational stochastic state transitions, observations, actions, and reward structure.",
    ),
    "powl-2.0": FormalismProfile(
        id="powl-2.0",
        title="POWL 2.0",
        description="Partial-order plans with concurrency, choice, loops, atoms, and silent structure.",
    ),
}

ALIASES: dict[str, str] = {
    "tpddl": "pddl+",
    "pddlplus": "pddl+",
    "powl": "powl-2.0",
    "powl2": "powl-2.0",
}


def normalize_formalism(value: str) -> str:
    """Return the canonical formalism identifier or refuse an unknown language."""
    candidate = value.strip().lower()
    candidate = ALIASES.get(candidate, candidate)
    if candidate not in PROFILES:
        supported = ", ".join(PROFILES)
        raise ValueError(
            f"MMDIO-PLAN-004 unsupported planning formalism {value!r}; supported: {supported}"
        )
    return candidate
