## 2026-08-01T20:23:17Z
You are Explorer 1 for Milestone M1 (ggen Pack & Ontology Configuration).
Your working directory is: /Users/sac/mmdio/.agents/explorer_m1_1
Your task is to investigate `packs/mmdio-pack/pack.toml` and Tera templates in `packs/mmdio-pack/templates/`.

Please read:
1. /Users/sac/mmdio/.agents/ORIGINAL_REQUEST.md
2. /Users/sac/mmdio/PROJECT.md
3. /Users/sac/mmdio/.agents/sub_orch_m1/SCOPE.md

Investigate:
- What targets and output paths are currently defined in `packs/mmdio-pack/pack.toml`?
- How are output paths currently pointing to `_generated_*` shadow filenames?
- How should `pack.toml` and the Tera templates in `packs/mmdio-pack/templates/` be updated so that ggen precipitation outputs directly to first-class Python modules in `src/mmdio/engine/` (such as `models.py`, `enums.py`, `parser_registry.py`, `render_dispatch.py`, `render.py`, `parser.py`, `schemas.py`, `fixtures.py`, `supported.py`, `detect_patterns.py`) instead of shadow `_generated_*` filenames?
- Are there any template syntax, header, or import path adjustments needed inside the `.tmpl` files?

Write your detailed findings and recommendations to `/Users/sac/mmdio/.agents/explorer_m1_1/handoff.md` and send a message back when complete.
