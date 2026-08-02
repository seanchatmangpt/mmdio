# BRIEFING — 2026-08-01T20:25:00Z

## Mission
Investigate ggen pack configuration (`packs/mmdio-pack/pack.toml`) and Tera templates in `packs/mmdio-pack/templates/` to determine how to update output paths and templates to output directly to first-class Python modules in `src/mmdio/engine/`.

## 🔒 My Identity
- Archetype: explorer
- Roles: Explorer 1 for Milestone M1
- Working directory: /Users/sac/mmdio/.agents/explorer_m1_1
- Original parent: 5ec836a6-9600-45e4-b443-7a8e6d651f19
- Milestone: M1 (ggen Pack & Ontology Configuration)

## 🔒 Key Constraints
- Read-only investigation — do NOT implement changes in project source code. Write reports/findings to working directory only.

## Current Parent
- Conversation ID: 5ec836a6-9600-45e4-b443-7a8e6d651f19
- Updated: 2026-08-01T20:25:00Z

## Investigation State
- **Explored paths**: `packs/mmdio-pack/pack.toml`, `packs/mmdio-pack/templates/*.tmpl`, `src/mmdio/engine/*.py`, `src/mmdio/detect.py`, `tests/test_oracle_generated.py`, `packs/mmdio-pack/gates/*.rq`
- **Key findings**:
  1. `pack.toml` currently holds pack metadata; template target output paths are specified via YAML frontmatter `to:` in 12 Tera templates.
  2. 10 of 12 templates emit shadow `_generated_*` filenames under `src/mmdio/engine/_generated_*.py` and `src/mmdio/_generated_detect_patterns.py`.
  3. Hand-written modules (`models.py`, `parser.py`, `render.py`) and consumers (`detect.py`, `registry.py`) import these `_generated_*` shadow files.
  4. Updating `to:` target paths in template frontmatter and `pack.toml` target configuration will redirect precipitation directly to first-class modules (`models.py`, `enums.py`, `parser_registry.py`, `render_dispatch.py`, `render.py`, `schemas.py`, `fixtures.py`, `supported.py`, `detect_patterns.py`).
  5. Internal template imports in `generated_fixtures.py.tmpl`, `generated_models.py.tmpl`, `generated_oracle_tests.py.tmpl`, `generated_render_dispatch.py.tmpl` must be updated from `_generated_*` to first-class module names.
- **Unexplored areas**: None for this subtask scope.

## Key Decisions Made
- Mapped all 12 templates to their target first-class Python modules in `src/mmdio/engine/`.
- Detailed template syntax, frontmatter `to:` changes, header updates, and internal import adjustments required.

## Artifact Index
- DISPATCH.md — Log of dispatch instructions
- BRIEFING.md — Working memory index
- progress.md — Liveness heartbeat and step tracker
- handoff.md — Comprehensive investigation report
