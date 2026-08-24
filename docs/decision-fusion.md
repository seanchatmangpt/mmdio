# mmdio Decision Fusion

## Purpose

This bounded integration fuses three surfaces around one typed service:

```text
scikit-decide domain + solver registry
→ mmdio.decide.DecisionService
→ Typer (`mmdio decide ...`)
→ FastMCP (`mmdio-decision-mcp`)
→ deterministic Mermaid projections
→ SHA-256 receipt
```

Typer and FastMCP do not implement independent decision semantics. They project the same service contract.

## Runtime boundary

scikit-decide 1.1.0 publishes platform wheels through CPython 3.12. The mmdio core remains compatible with Python 3.13, but the `decision` extra is admitted only on Python 3.12 until upstream publishes a CPython 3.13 wheel.

```bash
uv sync --python 3.12 --extra decision
```

A Python 3.13 installation can still import and use the mmdio core. Attempting to invoke the scikit-decide backend without the compatible extra returns the typed refusal `MMDIO-DECIDE-001`.

## CLI

```bash
mmdio decide catalog
mmdio decide match Maze
mmdio decide match Maze --mermaid
mmdio decide solve Maze --solver Astar --max-steps 100
mmdio decide solve Maze --solver Astar --mermaid
```

Domain and solver constructor arguments are JSON objects:

```bash
mmdio decide solve DOMAIN \
  --domain-arguments '{"width": 10}' \
  --solver-arguments '{"quiet": true}'
```

## FastMCP

```bash
mmdio-decision-mcp
```

The default transport is stdio. The server exposes:

- `decision_catalog`
- `decision_match`
- `decision_match_mermaid`
- `decision_solve`

## Standing and claim ceiling

A successful run establishes only:

```text
REGISTERED_DOMAIN_SOLVER_MATCH_AND_BOUNDED_ROLLOUT_ONLY
```

It does not establish that every scikit-decide domain or solver is constructible with default arguments, that a sampled policy is globally optimal, or that the generated Mermaid projection has standing outside the captured trajectory.

## Refusals

| Code | Boundary |
|---|---|
| `MMDIO-DECIDE-001` | optional runtime dependency unavailable |
| `MMDIO-DECIDE-002` | unknown registered domain |
| `MMDIO-DECIDE-003` | unknown registered solver |
| `MMDIO-DECIDE-004` | malformed arguments or invalid rollout bound |
| `MMDIO-DECIDE-005` | solver/domain incompatibility |
| `MMDIO-DECIDE-006` | domain construction failure |
| `MMDIO-DECIDE-007` | solve or rollout failure |
| `MMDIO-DECIDE-008` | deterministic serialization failure |
