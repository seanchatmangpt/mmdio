# Adversarial Challenge Handoff Report — E2E Test Suite (`tests/e2e/`)

## 1. Observation

Direct empirical observations from executing tests and adversarial harnesses:

1. **Pytest Execution Output**:
   - Running `uv run pytest tests/e2e/test_tier1_feature_coverage.py -o addopts=""` resulted in **9 FAILED test cases out of 36**:
     - `test_f2_06_render_module_dispatches_correctly`: `ValidationError` on `FlowchartNode` (missing required field `node_type`).
     - `test_f2_08_detect_patterns_module_matching`: `detect_diagram_type("kanban\n Todo")` returned `'flowchart'` instead of `'kanban'`.
     - `test_f3_05_pydantic_v2_instantiation_warning_free`: `ValidationError` on `FlowchartNode` (missing required field `node_type`).
     - `test_f4_01_flowchart_oracle_roundtrip`: `ValidationError` on `FlowchartNode` (`shape` passed instead of `node_type`).
     - `test_f4_02_sequence_oracle_roundtrip`: `ValidationError` on `SequenceParticipant` (`type` passed instead of `participant_type`).
     - `test_f4_04_state_oracle_roundtrip`: `ValidationError` on `StateTransition` (`from_state`/`to_state` passed instead of `source`/`target`).
     - `test_f4_05_er_oracle_roundtrip`: `ValidationError` on `ERAttribute` (`type` passed instead of `attr_type`).
     - `test_f4_07_pie_oracle_roundtrip`: `AssertionError` (`"pie title"` not found because `render_pie` emits `pie\ntitle ...`).
     - `test_f4_09_c4_oracle_roundtrip`: `ValidationError` on `C4Element` (`level` passed instead of `type`).
   - Running `uv run pytest tests/e2e/test_tier2_boundary_corner.py -k "not test_f1_valid_ontology_passes_all_gates"` resulted in **1 FAILED test case**:
     - `test_f2_max_nesting_depth_recursive_mindmap`: `AssertionError: assert 'Level 1' in 'mindmap'`.

2. **Flawed Node Oracle Verification (`tests/oracle/verify_mermaid.mjs`)**:
   - `verify_mermaid.mjs` uses `mermaid.detectType(source)` on line 22 instead of `mermaid.parse(source)`.
   - Empirically tested with `.agents/challenger_e2e_m5_1/challenge_harness.py` and Node CLI:
     - `flowchart TD\n  A --->>> B` (corrupted syntax) -> `mermaid.detectType()` returns `'flowchart-v2'`, exit code `0`, `SUCCESS: Detected diagram type: flowchart-v2`.
     - Calling `await mermaid.parse('flowchart TD\n  A --->>> B')` throws a syntax parse error: `Parse error on line 2: ... Expecting 'AMP', 'COLON', ... got 'TAGEND'`.
     - Out of 8 corrupted diagram payloads with valid headers, **6 were falsely certified as SUCCESS by the Node oracle**.

3. **SPARQL Law Gate 060 Performance Explosion**:
   - `060_render_nesting_depth_limit.rq` performs an unindexed 3-way join across `mer:PythonModel` list fields. In `rdflib`, this query takes > 40 seconds to evaluate during `test_sparql_gates_verification` and `test_f1_valid_ontology_passes_all_gates`, hanging standard `uv run pytest` execution.

4. **Harness Stress & Concurrency**:
   - `validate_mermaid_source` correctly creates and deletes temporary `.mmd` files in `tempfile.gettempdir()`. Multi-threaded concurrency testing (20 concurrent requests across 8 threads) showed zero file descriptor leaks or file collisions.

---

## 2. Logic Chain

1. **In-place Test Failures Invalidate Test Integrity**:
   - The test suite in `tests/e2e/test_tier1_feature_coverage.py` contains 9 test cases that crash at runtime with Pydantic `ValidationError` or string match `AssertionError`.
   - These failures stem from using out-of-date field names (e.g. `shape` vs `node_type`, `type` vs `participant_type`, `from_state` vs `source`, `type` vs `attr_type`) in test instantiations.
   - Therefore, the test suite is not cleanly passing `uv run pytest`.

2. **Tautological Oracle Validation**:
   - `TEST_INFRA.md` claims that all rendered diagrams are validated against the official Node.js Mermaid parser.
   - However, `verify_mermaid.mjs` uses `mermaid.detectType()`, which only matches regex keywords on the first header line and ignores the rest of the diagram body.
   - As proven empirically by `.agents/challenger_e2e_m5_1/challenge_harness.py`, `validate_mermaid_source` passes corrupted diagram body syntax without error.
   - Consequently, the E2E roundtrip tests (F4) provide false positive assurance: they do NOT verify whether rendered Mermaid syntax is actually valid syntax according to Mermaid 11.16.0.

3. **SPARQL Gate Performance Degrades Harness**:
   - Gate 060 (`060_render_nesting_depth_limit.rq`) lacks join constraints in `rdflib`, causing Cartesian join explosion that stalls the test suite execution.

---

## 3. Caveats

- The Python Lark parser (`MermaidParser`) correctly raises `ParsingError` on invalid inputs when explicitly invoked.
- Tier 3 (`test_tier3_pairwise_combinations.py`) and Tier 4 (`test_tier4_real_world_scenarios.py`) pass 100% of their test cases, but their oracle calls rely on the same flawed `mermaid.detectType()` oracle.
- No code modification of production files was performed (per critic role constraints).

---

## 4. Conclusion

**VERDICT: REJECT**

The E2E test suite in `tests/e2e/` is **REJECTED** due to:
1. **Broken Test Cases**: 9 test failures in `test_tier1_feature_coverage.py` and 1 failure in `test_tier2_boundary_corner.py`.
2. **False-Positive Node Oracle**: `verify_mermaid.mjs` uses `mermaid.detectType()` instead of `mermaid.parse()`, allowing corrupted diagram text to pass validation.
3. **SPARQL Gate Query Bottleneck**: Gate 060 query causes severe performance degradation in `rdflib`.

---

## 5. Verification Method

To independently verify these findings:

1. **Verify Test Failures**:
   ```bash
   uv run pytest tests/e2e/test_tier1_feature_coverage.py -k "not sparql" -o addopts="" --tb=short
   uv run pytest tests/e2e/test_tier2_boundary_corner.py -k "test_f2_max_nesting_depth_recursive_mindmap" -o addopts=""
   ```

2. **Verify Node Oracle False-Positive Defect**:
   ```bash
   mkdir -p scratch
   printf "flowchart TD\n  A --->>> B\n" > scratch/bad_flowchart.mmd
   node tests/oracle/verify_mermaid.mjs scratch/bad_flowchart.mmd
   # Output will report "SUCCESS: Detected diagram type: flowchart-v2" and exit code 0.
   ```

3. **Verify Empirical Challenge Harness**:
   ```bash
   uv run python .agents/challenger_e2e_m5_1/challenge_harness.py
   ```
