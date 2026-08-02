## 2026-08-01T20:25:55Z
You are Worker 1 for Milestone M1 (ggen Pack & Ontology Configuration).
Your working directory is: /Users/sac/mmdio/.agents/worker_m1_1

Please read:
1. /Users/sac/mmdio/.agents/ORIGINAL_REQUEST.md
2. /Users/sac/mmdio/PROJECT.md
3. /Users/sac/mmdio/.agents/sub_orch_m1/SCOPE.md
4. /Users/sac/mmdio/.agents/explorer_m1_1/handoff.md
5. /Users/sac/mmdio/.agents/explorer_m1_2/handoff.md
6. /Users/sac/mmdio/.agents/explorer_m1_3/handoff.md

Your task is to implement all changes required for Milestone M1:

1. Update `packs/mmdio-pack/pack.toml`:
   - Add explicit `[targets]` configuration for template outputs.
   - Update pack description.

2. Update `packs/mmdio-pack/ontology.ttl`:
   - Update `mer:pythonModelModule`, `mer:pythonTransformerModule`, `mer:pythonRenderModule` for `kanban`, `timeline`, `xychart`, and `block` to point to first-class engine modules (`"mmdio.engine.models"`, `"mmdio.engine.parser"`, `"mmdio.engine.render"`).
   - Add `mer:PythonEnum` and `mer:EnumMember` triples for the 7 domain token enums (`NodeShape`, `MessageType`, `RelationshipType`, `CardinityType`, `TaskStatus`, `C4Level`, `ParticipantType`).
   - Expand `mer:hasModel` shapes for remaining supported diagram types as needed. Ensure all 10 SPARQL gates pass cleanly with 0 violations.

3. Update all Tera templates in `packs/mmdio-pack/templates/`:
   - Update frontmatter `to:` target directives to output directly to first-class Python modules under `src/mmdio/engine/` (`models.py`, `enums.py`, `parser_registry.py`, `render_dispatch.py`, `render.py`, `schemas.py`, `fixtures.py`, `supported.py`, `detect_patterns.py`) instead of `_generated_*` shadow filenames.
   - Update internal import statements inside `.tmpl` files (`generated_fixtures.py.tmpl`, `generated_models.py.tmpl`, `generated_oracle_tests.py.tmpl`, `generated_render_dispatch.py.tmpl`, etc.) to import from first-class engine modules instead of `_generated_*` shadow modules.
   - Append `MermaidDiagram` discriminated union generation loop to `generated_models.py.tmpl` (consolidating `generated_models_union.py.tmpl`).

4. Build & Gate Verification:
   - Run `ggen sync run --dry-run` and verify it completes with exit code 0 and passes all 10 law gates in `packs/mmdio-pack/gates/`.
   - Run `ggen sync run` to precipitate the first-class engine files.
