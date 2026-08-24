# Formal Planning Documents

`mmdio.planning` turns admitted formal-planning subjects into receipt-bearing Mermaid documentation without making Mermaid the semantic authority or an actuation path.

## Planning languages

| Formalism | Planning semantics |
|---|---|
| PDDL | deterministic actions, preconditions, effects, state, goals, constraints |
| PPDDL | PDDL plus probability-bearing outcomes and policies under uncertainty |
| PDDL+ / TPDDL | actions plus time, processes, continuous state, and autonomous events |
| RDDL | relational stochastic state transitions, observations, decisions, and rewards |
| POWL 2.0 | partial-order plans, concurrency, choice, loops, atoms, and silent structure |

The canonical documentation seam is:

```text
native planning AST / solver subject
        ↓
formalism-specific lowering
        ↓
PlanningGraph
        ↓
mmdio.planning
        ↓
Mermaid views + plan.md + receipts + manifest
```

Native planning systems remain authoritative for their language-specific semantics. `PlanningGraph` is the bounded canonical carrier for documentation projection. Mermaid is a generated I/O surface.

## Generated documents

`generate_planning_documents()` emits every view justified by information present in the exact planning graph:

| Document | Mermaid type | Emission rule |
|---|---|---|
| topology | `flowchart` | always |
| summary | `mindmap` | graph contains nodes |
| states | `stateDiagram-v2` | explicit state-to-state transitions exist |
| requirements | `requirement` | goals or constraints exist |
| timeline | `timeline` | processes, events, or explicit time markers exist |
| schedule | `gantt` | actions/processes carry start or duration metadata |
| value-flow | `sankey` | non-negative numeric probability/value/weight edges exist |
| interactions | `sequence` | actions carry explicit `actor` and `target_actor` metadata |

Missing semantics are not invented to make a diagram prettier. In particular, a POWL partial order remains partial: `mmdio` does not create edges between concurrent nodes.

## Bundle

```text
planning-docs/
├── planning-graph.json
├── plan.md
├── manifest.json
├── diagrams/
│   ├── topology.flowchart.mmd
│   └── ... every applicable projection
└── receipts/
    └── <projection>.receipt.json
```

Each projection receipt binds the formalism, exact subject, canonical planning digest, Mermaid diagram type, and exact document bytes. The claim ceiling is `PLANNING_DOCUMENT_PROJECTION_ONLY`.

## CLI

The primary package CLI exposes planning-document manufacture directly:

```sh
mmdio planning examples/planning/enterprise.ppddl.json \
  --output /tmp/mmdio-planning
```

The dependency-light module entrypoint is equivalent:

```sh
python -m mmdio.planning project examples/planning/enterprise.ppddl.json \
  --output /tmp/mmdio-planning
```

Both commands only manufacture documentation artifacts. Planner execution, GymAct world execution, and consequential authority remain outside `mmdio`.

## AutoFDE-Lab integration

AutoFDE-Lab should lower its authoritative PDDL/TPDDL/RDDL domain objects and POWL 2.0 AST into `PlanningGraph`; PPDDL probability-bearing outcomes map to `probabilistic` edges. This keeps parser ownership with the planning runtime while giving every planning family the same human-readable I/O plane.

For enterprise use, one subject can therefore expose deterministic topology, uncertainty, autonomous events, schedule, value flow, requirements, partial order, and actor interaction without collapsing those semantics into one fake universal planning language.
