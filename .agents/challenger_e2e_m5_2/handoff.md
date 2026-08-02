# Handoff Report — E2E Test Suite Adversarial Challenge

## Verdict: REJECT

---

## 1. Observation

### 1.1 Node Mermaid Oracle Implementation
In `/Users/sac/mmdio/tests/oracle/verify_mermaid.mjs`, line 22:
```javascript
22:   const diagramType = mermaid.detectType(source);
23:   console.log(`SUCCESS: Detected diagram type: ${diagramType}`);
24:   process.exit(0);
```

### 1.2 Oracle Execution on Corrupted Diagram Inputs
When executing our empirical audit script (`.agents/challenger_e2e_m5_2/scratch/empirical_oracle_audit.py`), 9 out of 10 syntactically corrupted diagram sources were ACCEPTED as valid by `verify_mermaid.mjs`:

1. `flowchart TD\n  A -->` (Truncated edge syntax) -> Output: `SUCCESS: Detected diagram type: flowchart-v2` (Exit code: 0)
2. `flowchart TD\n  A[Unclosed label` (Unclosed node bracket) -> Output: `SUCCESS: Detected diagram type: flowchart-v2` (Exit code: 0)
3. `sequenceDiagram\n  actor Alice\n  Alice-->Bob invalid syntax` (Malformed sequence message) -> Output: `SUCCESS: Detected diagram type: sequence` (Exit code: 0)
4. `pie title Broken Pie\n  "Category 1" : not_a_number` (Non-numeric pie value) -> Output: `SUCCESS: Detected diagram type: pie` (Exit code: 0)
5. `C4Context\n  Person(unclosed_macro` (Malformed C4 macro) -> Output: `SUCCESS: Detected diagram type: c4` (Exit code: 0)
6. `mindmap\n  root((Unclosed` (Unclosed mindmap root node) -> Output: `SUCCESS: Detected diagram type: mindmap` (Exit code: 0)
7. `erDiagram\n  CUSTOMER ||--invalid_cardinality ORDER : places` (Invalid ER cardinality) -> Output: `SUCCESS: Detected diagram type: er` (Exit code: 0)
8. `gantt\n  dateFormat INVALID_DATE_FORMAT\n  section Test\n  Task1 : a1, invalid-date, 30d` (Invalid gantt syntax) -> Output: `SUCCESS: Detected diagram type: gantt` (Exit code: 0)
9. `gitGraph\n  invalidGitCommand` (Invalid git graph statement) -> Output: `SUCCESS: Detected diagram type: gitGraph` (Exit code: 0)

Only 1 sample (`invalidDiagramHeaderType\n  A -> B`) failed because `mermaid.detectType` could not match the header string.

### 1.3 Intended Parse Behavior with `mermaid.parse()`
When executing `await mermaid.parse(source)` against the same 10 corrupted diagram sources, 9 out of 10 properly raised parse errors and exited with code 1. For example:
- `flowchart TD\n  A -->` -> `PARSE_ERROR: Parse error on line 3: ...lowchart TD  A --> ---------------------^ Expecting 'AMP', 'COLON', ... got 'EOF'`
- `sequenceDiagram\n  actor Alice\n  Alice-->Bob invalid syntax` -> `PARSE_ERROR: Parse error on line 3: ...->Bob invalid syntax -----------------------^ Expecting 'TXT', got 'NEWLINE'`

### 1.4 Test Infra & Harness Observations
- `tests/e2e/conftest.py` line 71: `validate_mermaid_source()` asserts `result.returncode == 0`. Because `verify_mermaid.mjs` returns exit code `0` on corrupted diagram text, `validate_mermaid_source()` returns success instead of failing.
- Temp File Leakage: `validate_mermaid_source()` cleans up temporary files in `finally: os.unlink(temp_path)`. Tested over 20 invocations, zero leaked files were detected.
- SPARQL Law Gates: `verify_sparql_gates()` evaluates all 10 gate `.rq` files in `packs/mmdio-pack/gates/`. Injected invalid RDF triples (e.g. invalid `fieldKind`) were correctly detected by Gate 030 (`030_field_shape_closed_vocabulary.rq`).
- Stress Limits: 500-node flowchart diagram rendered and passed oracle validator within timeout (15s).

---

## 2. Logic Chain

1. **Premise 1 (Requirement)**: An E2E test suite oracle must provide genuine validation of rendered Mermaid diagram syntax, ensuring that invalid, corrupted, or malformed diagram text fails the test suite.
2. **Observation 1**: `tests/oracle/verify_mermaid.mjs` calls `mermaid.detectType(source)`.
3. **Observation 2**: `mermaid.detectType(source)` only performs keyword pattern matching on diagram headers (e.g., matching `flowchart`, `sequenceDiagram`, `pie`). It does NOT perform syntax parsing.
4. **Observation 3 (Empirical Result)**: When presented with 10 syntactically corrupted diagram sources across flowchart, sequence, pie, C4, mindmap, ER, gantt, and gitGraph diagram types, `verify_mermaid.mjs` exited with status `0` ("SUCCESS") for 9 out of 10 cases.
5. **Deduction 1**: The test suite's claims of 100% oracle pass rate across E2E tests are false positives for diagram syntax validity. Invalid diagram rendering output from `render_diagram()` would pass all E2E test assertions completely unnoticed.
6. **Observation 4 (Remediation Proof)**: Replacing `mermaid.detectType(source)` with `await mermaid.parse(source)` in the Node oracle script causes Node to parse the entire diagram syntax and correctly reject all 9 syntactically malformed diagrams with exit code 1.
7. **Conclusion**: The E2E test suite in `tests/e2e/` fails to meet basic assertion genuineness and negative failure criteria. Verdict: **REJECT**.

---

## 3. Caveats

- The SPARQL law gates (`verify_sparql_gates()`) and Python AST model validations are functional and genuine.
- Temporary file cleanup and high-volume diagram stress tests operate as expected without memory leaks or crashes.
- The failure is isolated to `tests/oracle/verify_mermaid.mjs` and its downstream usage in `validate_mermaid_source()` in `tests/e2e/conftest.py`.

---

## 4. Conclusion

**Verdict: REJECT**

The E2E test suite in `tests/e2e/` relies on a flawed oracle harness (`tests/oracle/verify_mermaid.mjs`) that uses `mermaid.detectType()` instead of `mermaid.parse()`. As empirically demonstrated, 90% of syntactically corrupted diagrams are falsely accepted as valid by the oracle. 

### Actionable Remediation Required:
1. Update `tests/oracle/verify_mermaid.mjs` to call `await mermaid.parse(source)` instead of `mermaid.detectType(source)`.
2. Re-run `uv run pytest tests/e2e/` to ensure all generated and rendered diagram fixtures pass full syntax parsing.

---

## 5. Verification Method

To independently reproduce and verify this finding:

1. Run the empirical audit script:
   ```bash
   uv run python .agents/challenger_e2e_m5_2/scratch/empirical_oracle_audit.py
   ```
2. Observe output showing 9 out of 10 corrupted test cases passing the current oracle (`verify_mermaid.mjs`).
3. Direct execution check against Node oracle with corrupted flowchart string:
   ```bash
   node tests/oracle/verify_mermaid.mjs <(echo -e "flowchart TD\n  A -->")
   ```
   **Expected broken result**: Exits 0 with `SUCCESS: Detected diagram type: flowchart-v2`.
   **Expected fixed result**: Exits 1 with `PARSE_ERROR: Parse error on line 3...`.
