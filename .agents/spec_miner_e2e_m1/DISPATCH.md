## 2026-08-01T20:23:24Z
You are spec_miner_e2e_m1 (teamwork_preview_spec_miner).
Your working directory is /Users/sac/mmdio/.agents/spec_miner_e2e_m1. Create this directory if it doesn't exist.

Your mission is to perform comprehensive spec mining for the E2E Testing Track of project mmdio.

Instructions:
1. Read /Users/sac/mmdio/.agents/ORIGINAL_REQUEST.md and /Users/sac/mmdio/PROJECT.md.
2. Examine the 10 SPARQL law gates in packs/mmdio-pack/gates/*.rq.
3. Examine the Node Mermaid oracle harness at tests/oracle/verify_mermaid.mjs.
4. Examine existing tests in tests/ and configuration files (pyproject.toml, packs/mmdio-pack/pack.toml, packs/mmdio-pack/ontology.ttl).
5. Document all specifications, diagram types, token enums, law gates, oracle interfaces, and error conditions.
6. Formulate detailed test inventories for the 4-tier E2E testing methodology:
   - Tier 1: Feature Coverage (>=5 tests per feature across R1, R2, R3, F1-F4)
   - Tier 2: Boundary & Corner Cases (>=5 tests per feature: invalid syntax, empty inputs, edge shape limits, deprecation warnings)
   - Tier 3: Cross-Feature Pairwise Combinations (interactions between diagram parsing, rendering, gate validation, oracle verification)
   - Tier 4: Real-World Scenarios (complete E2E workflow diagram generation, AST roundtrip, gate validation, oracle verification)
7. Write your analysis to /Users/sac/mmdio/.agents/spec_miner_e2e_m1/spec_analysis.md and create /Users/sac/mmdio/.agents/spec_miner_e2e_m1/handoff.md summarizing your findings.
8. Report back when finished.
