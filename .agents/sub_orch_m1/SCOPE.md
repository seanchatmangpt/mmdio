# Scope: Milestone M1 (ggen Pack & Ontology Configuration)

## Architecture & Goal
- Update `packs/mmdio-pack/pack.toml` and Tera templates in `packs/mmdio-pack/templates/` so that ggen output targets first-class Python modules in `src/mmdio/engine/` (`models.py`, `enums.py`, `parser_registry.py`, `render_dispatch.py`, `render.py`, `parser.py`, `schemas.py`, `fixtures.py`, `supported.py`, `detect_patterns.py`) instead of shadow `_generated_*` filenames.
- Expand RDF ontology facts in `packs/mmdio-pack/ontology.ttl` for complete model/token/parser/renderer representation.
- Ensure `ggen sync run --dry-run` completes with exit code 0 and passes all 10 law gates in `packs/mmdio-pack/gates/`.

## Work Breakdown / Iteration Loop
- **Iteration 1**:
  - Explorer: Investigate `packs/mmdio-pack/pack.toml`, `packs/mmdio-pack/ontology.ttl`, `packs/mmdio-pack/templates/`, `packs/mmdio-pack/gates/`, and `src/mmdio/engine/registry.ttl`. Identify all required template target updates and ontology expansions.
  - Worker: Apply changes to `pack.toml`, `ontology.ttl`, templates.
  - Reviewers (2): Review changes for completeness, accuracy, and adherence to `PROJECT.md` contracts.
  - Challengers (2): Verify dry-run output and gate assertions.
  - Forensic Auditor (1): Perform integrity audit on changes.

## Status
| Step | Status |
|------|--------|
| Iteration 1 Gate | FAIL (auditor_1 INTEGRITY VIOLATION) |
| Iteration 2 Gate | FAIL (challenger_1_r2_gen2 REJECT: pytest test_f2_06 & oracle failures) |
| Iteration 3 Survey & Investigation | IN_PROGRESS |
| Iteration 3 Implementation | PLANNED |
| Iteration 3 Review, Challenge & Audit | PLANNED |

