# Scope: E2E Testing Track

## Architecture
- Requirement-driven, opaque-box E2E test harness exercising `mmdio` CLI/package, `ggen` 10 SPARQL law gates (`packs/mmdio-pack/gates/`), and Node Mermaid 11.16.0 oracle (`tests/oracle/verify_mermaid.mjs`).

## Feature Inventory
| # | Feature | Description | Requirement | Tier 1 Goals | Tier 2 Goals | Tier 3 Goals | Tier 4 Goals |
|---|---------|-------------|-------------|--------------|--------------|--------------|--------------|
| 1 | ggen Ontology & Pack Law Gates | 10 SPARQL law gates validation via ggen sync run | R1, R2, F1 | >=5 tests | >=5 tests | pairwise | scenario |
| 2 | Pure Python Model & Parser Precipitation | First-class engine models, parser, render, detect | R1, R2, F2 | >=5 tests | >=5 tests | pairwise | scenario |
| 3 | Pytest Harness & Warning Cleanliness | Clean pytest pass, zero deprecation warnings | R2, F3 | >=5 tests | >=5 tests | pairwise | scenario |
| 4 | Mermaid 11.16.0 Oracle & Diagram Roundtrip | Render & parse validation against Node oracle | R3, F4 | >=5 tests | >=5 tests | pairwise | scenario |

## Milestones
| # | Name | Scope | Dependencies | Status | Subagent Conv ID |
|---|------|-------|-------------|--------|------------------|
| M1 | Spec Mining & Requirement Mapping | Map requirements, gate definitions, oracle harness | none | DONE | 338fc77b-299c-483f-95f2-c2f1a3be3438 |
| M2 | E2E Test Infra & Harness Setup | Create TEST_INFRA.md and test runner integration | M1 | IN_PROGRESS | |
| M3 | Tier 1 & Tier 2 E2E Test Suite | Implement >=5 tests/feature for Tier 1 & Tier 2 | M2 | PLANNED | |
| M4 | Tier 3 & Tier 4 E2E Test Suite | Implement pairwise & real-world application scenarios | M3 | PLANNED | |
| M5 | Test Suite Audit & TEST_READY.md | Verification gate, audit pass, publish TEST_READY.md | M4 | PLANNED | |

## Interface Contracts
### E2E Test Harness ↔ Project mmdio
- Test command: `uv run pytest`
- Gate command: `ggen sync run` (or ggen CLI check)
- Oracle verification: `tests/oracle/verify_mermaid.mjs` (Node Mermaid 11.16.0)
