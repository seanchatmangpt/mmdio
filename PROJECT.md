# Project: mmdio ggen-driven end-to-end architecture (A = μ(O))

## Architecture
- Single source of truth: `src/mmdio/engine/registry.ttl` + `packs/mmdio-pack/ontology.ttl`.
- Precipitation function $\mu$: `ggen` CLI 26.8.2 evaluating 10 SPARQL law gates in `packs/mmdio-pack/gates/` and Tera templates in `packs/mmdio-pack/templates/`.
- Derived first-class Python source code target: `src/mmdio/engine/` (first-class derived modules: `models.py`, `enums.py`, `parser_registry.py`, `render_dispatch.py`, `render.py`, `parser.py`, `schemas.py`, `fixtures.py`, `supported.py`, `detect_patterns.py`).
- Elimination of shadow duplication: Remove legacy `_generated_*` prefixed files, legacy `models.py`/`parser.py`/`render.py` shadow modules, and `src/mmdio/engine/types/` shadow folder.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | ggen Pack & Ontology Expansion | Expand `ontology.ttl` & Tera templates to support all diagram types and output to first-class Python paths without `_generated_*` prefix | M1 | survey |
| 2 | Shadow Module Removal & First-Class Code Precipitation | Replace hand-written `models.py`, `parser.py`, `render.py`, and `types/` with first-class ggen-precipitated derived code in `src/mmdio/engine/` | M2 | survey |
| 3 | Pytest Harness & Warning Resolution | Fix warning filter / starlette deprecation in `test_api.py` / `pyproject.toml` so `uv run pytest` passes 100% cleanly | M3 | survey |
| 4 | Final E2E Oracle & Gate Validation | Verify 100% gate pass rate across 10 SPARQL gates, 100% pytest pass rate against Node Mermaid 11.16.0 oracle, and Tier 5 adversarial coverage hardening | M4 | survey |

## Milestones
| # | Name | Scope | Dependencies | Status | Subagent Conv ID |
|---|------|-------|-------------|--------|------------------|
| M1 | ggen Pack & Ontology Configuration | Update `pack.toml` and templates to emit first-class Python paths under `src/mmdio/engine/` and expand ontology facts | none | IN_PROGRESS | 5ec836a6-9600-45e4-b443-7a8e6d651f19 |
| M2 | First-Class ggen Engine Precipitation & Shadow Cleanup | Remove shadow files (`_generated_*`, legacy `models.py`, `parser.py`, `render.py`, `types/`) and precipitate unified engine code | M1 | PLANNED | |
| M3 | Test Suite & Deprecation Fixes | Resolve warning escalation in `test_api.py` / `pyproject.toml` and update test imports to first-class engine paths | M2 | PLANNED | |
| M4 | Final E2E Test Suite Pass & Adversarial Hardening | Validate 100% law gate pass rate (`ggen sync run`), 100% pytest oracle pass rate (`uv run pytest`), and Tier 5 adversarial checks | M3 | PLANNED | |

## Interface Contracts
### `src/mmdio/engine/` ↔ Consumer Modules (`src/mmdio/`, `tests/`)
- `src/mmdio/engine/models.py`: Defines Pydantic AST models (`FlowchartDiagram`, `SequenceDiagram`, etc.) and `MermaidDiagram` discriminated union.
- `src/mmdio/engine/enums.py`: Defines `StrEnum` token enums (`NodeShape`, `MessageType`, etc.).
- `src/mmdio/engine/parser.py`: Defines `MermaidParser` and Lark transformer registry.
- `src/mmdio/engine/render.py`: Defines `render_diagram` dispatcher and type-specific render functions.
- `src/mmdio/engine/supported.py`: Defines `SUPPORTED_DIAGRAM_TYPES` and capabilities.

## Code Layout
- `packs/mmdio-pack/pack.toml`: ggen pack manifest specifying template outputs and law gates.
- `packs/mmdio-pack/ontology.ttl`: RDF metadata and model shapes.
- `packs/mmdio-pack/gates/*.rq`: 10 SPARQL law gates.
- `packs/mmdio-pack/templates/*.tmpl`: 12 Tera templates.
- `src/mmdio/engine/`: First-class derived Python source modules.
- `tests/`: Pytest test suite and Node Mermaid oracle harness (`tests/oracle/verify_mermaid.mjs`).
