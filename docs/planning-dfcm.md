# Planning DFCM

`mmdio.planning` applies **Design for Combinatorial Maximalism (DFCM)** to the planning-document surface.

The objective is not to emit the largest possible pile of diagrams. The objective is to enumerate the complete bounded reversible design space, admit every projection justified by the canonical planning graph, and explicitly refuse every projection that lacks the required semantics.

For one planning subject the projection space is:

```text
formalism
    ×
{ topology,
  summary,
  states,
  requirements,
  timeline,
  schedule,
  value-flow,
  interactions }
```

For the five admitted planning formalism families, the crown therefore evaluates:

```text
5 formalisms × 8 projection families = 40 candidates
```

## DFCM law

Every candidate receives exactly one disposition:

```text
ADMITTED
REFUSED
```

There is no silent omission.

An admitted candidate must correspond one-to-one with a manufactured Mermaid document and its receipt. A refused candidate produces a typed refusal artifact containing the exact candidate coordinates, reason code, semantic evidence, and deterministic digest.

The independent DFCM specification cross-checks the actual Mermaid projector. Drift between predicted admission and manufactured documents is `MMDIO-DFCM-009` and fails the crown.

## Bundle

A planning bundle now includes both the successful projections and evidence for the rejected alternatives:

```text
planning-docs/
├── planning-graph.json
├── plan.md
├── manifest.json
├── dfcm.json
├── dfcm.md
├── diagrams/
│   └── <admitted projection>.<mermaid type>.mmd
├── receipts/
│   └── <admitted projection>.receipt.json
└── refusals/
    └── <refused projection>.refusal.json
```

For every subject:

```text
len(receipts) + len(refusals) = 8
```

Across the five-formalism crown:

```text
Σ candidates = 40
Σ admitted + Σ refused = 40
```

## Reversibility and authority

DFCM operates only in the graph/design domain. It enumerates candidate documentation projections and records their standing.

It does **not**:

- execute a planner;
- authorize a plan;
- mutate a GymAct world;
- call an external consequential API;
- infer missing planning semantics;
- turn Mermaid into execution authority.

The DFCM claim ceiling is:

```text
COMBINATORIAL_PLANNING_DOCUMENT_DESIGN_SPACE_ONLY
```

The existing document claim ceiling remains:

```text
PLANNING_DOCUMENT_PROJECTION_ONLY
```

This preserves the separation:

```text
SELECT / explore candidate projection space
        ↓
CONSTRUCT admitted Mermaid projections + refusal evidence
        ↓
NO DO authority
```

## Why this matters for planning systems

A deterministic PDDL subject may justify topology and state views while refusing stochastic value flow. A PDDL+ subject may justify timeline and schedule while refusing actor interaction. A POWL subject may preserve partial order without inventing temporal or probabilistic semantics.

DFCM makes those boundaries inspectable. The absence of a diagram is no longer ambiguous: it is a mechanically explained refusal tied to the exact planning graph.
