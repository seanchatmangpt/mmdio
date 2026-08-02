# Project Plan — mmdio ggen-driven end-to-end architecture

## Overview
Transform `mmdio` into a ggen-driven end-to-end architecture ($A = \mu(O)$), unifying the codebase so that AST models, token enums, parser registries, and render dispatchers precipitate directly from `registry.ttl` as first-class Python source code without shadow duplication.

## Strategy & Workflow
1. **Phase 0: Survey** (3 Explorers in parallel)
   - Explorer 1: Map current codebase, shadow modules (`models.py`, `parser.py`, `render.py`), derived files, and import structures.
   - Explorer 2: Examine `src/mmdio/engine/registry.ttl`, `packs/mmdio-pack/`, templates, and law gates in `packs/mmdio-pack/gates/`.
   - Explorer 3: Audit existing test harness (`uv run pytest`, `tests/oracle/verify_mermaid.mjs`, law gates, ggen sync execution).

2. **Phase 1: Decomposition & Track Setup**
   - Synthesize survey reports into `PROJECT.md § Feature Inventory` and milestone architecture.
   - Spawn E2E Testing Track Orchestrator in parallel to build requirement-driven test suite & `TEST_READY.md`.
   - Spawn Sub-orchestrators for implementation milestones.

3. **Phase 2: Implementation & Verification**
   - Monitor milestone sub-orchestrators (Explorer -> Worker -> Reviewer -> Challenger -> Forensic Auditor).
   - Final milestone: 100% E2E test suite pass + Tier 5 adversarial coverage hardening.

4. **Phase 3: Final Acceptance & Sentinel Reporting**
   - Ensure 100% gate pass rate across all 10 law gates upon `ggen sync run`.
   - Ensure `uv run pytest` passes 100%.
   - Ensure zero shadow/duplicate model files.
   - Send final completion report to Sentinel.
