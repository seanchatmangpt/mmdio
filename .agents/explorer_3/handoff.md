# Handoff Report — Explorer 3 (Test Suite & Oracle Harness)

## 1. Observation

- **Original Request File**: `/Users/sac/mmdio/.agents/ORIGINAL_REQUEST.md` specifies requirement R3: "The dev/test harness must pass all unit and roundtrip oracle tests (pytest), validating rendered Mermaid diagrams against the Node-based oracle (tests/oracle/verify_mermaid.mjs) pinned to Mermaid 11.16.0."
- **Pytest Config**: `/Users/sac/mmdio/pyproject.toml` lines 83–88:
  ```toml
  [tool.pytest.ini_options]
  addopts = "--color=yes --doctest-modules --exitfirst --failed-first --strict-config --strict-markers --verbosity=2 --junitxml=reports/pytest.xml"
  filterwarnings = ["error", "ignore::DeprecationWarning"]
  testpaths = ["src", "tests"]
  xfail_strict = true
  ```
- **Node Oracle Package**: `/Users/sac/mmdio/tests/oracle/package.json` line 6 specifies `"mermaid": "11.16.0"`. Verified `/Users/sac/mmdio/tests/oracle/node_modules/mermaid/package.json` line 3: `"version": "11.16.0"`.
- **Node Oracle Script**: `/Users/sac/mmdio/tests/oracle/verify_mermaid.mjs` lines 11–28:
  ```javascript
  await mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'strict',
    htmlLabels: false,
    flowchart: { defaultRenderer: 'dagre-wrapper' },
    architecture: { randomize: false }
  });
  ...
  const diagramType = mermaid.detectType(source);
  console.log(`SUCCESS: Detected diagram type: ${diagramType}`);
  ```
- **Test File Inventory**:
  1. `/Users/sac/mmdio/tests/test_import.py` (1 test: `test_import`)
  2. `/Users/sac/mmdio/tests/test_cli.py` (1 test: `test_fire`)
  3. `/Users/sac/mmdio/tests/test_api.py` (1 test: `test_read_root`)
  4. `/Users/sac/mmdio/tests/test_oracle_generated.py` (5 tests: `test_block_generated`, `test_kanban_generated`, `test_pie_generated`, `test_sankey_generated`, `test_timeline_generated`)
  5. `/Users/sac/mmdio/tests/test_oracle_roundtrip.py` (11 tests: flowcharts, sequence, class, state, er, gantt, pie, git, c4, mindmap, sankey)
  6. `/Users/sac/mmdio/tests/oracle_types/test_oracle_block.py` (4 tests: `test_block_simple`, `test_block_with_columns`, `test_block_with_labels`, `test_block_different_arrows`)
  7. `/Users/sac/mmdio/tests/oracle_types/test_oracle_kanban.py` (3 tests: `test_kanban_simple`, `test_kanban_empty_sections`, `test_kanban_single_card`)
  8. `/Users/sac/mmdio/tests/oracle_types/test_oracle_timeline.py` (3 tests: `test_timeline_simple`, `test_timeline_no_title`, `test_timeline_various_date_formats`)
  9. `/Users/sac/mmdio/tests/oracle_types/test_oracle_xychart.py` (3 tests: `test_xychart_simple`, `test_xychart_with_strings`, `test_xychart_without_title`)
- **Pytest Command Output**:
  - `uv run pytest` output:
    ```
    ERROR collecting tests/test_api.py
    starlette.exceptions.StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    ```
  - `uv run pytest --ignore=tests/test_api.py` output:
    ```
    31 passed in 7.23s
    ```

---

## 2. Logic Chain

1. **Observation 1 & 2**: `pyproject.toml` defines `filterwarnings = ["error", ...]`, which escalates any unhandled warning into an error. `test_api.py` imports `fastapi.testclient.TestClient`, which raises `StarletteDeprecationWarning`. Because `"error"` is the first rule in `filterwarnings`, the deprecation warning is treated as an error, causing `uv run pytest` to halt on `test_api.py` due to `--exitfirst`.
2. **Observation 3, 4, 5**: The roundtrip oracle tests (11 in `test_oracle_roundtrip.py`, 5 in `test_oracle_generated.py`, 13 in `oracle_types/`) all generate Mermaid diagram markup string and pass it to `validate_mermaid_source(source)`. `validate_mermaid_source` writes the string to a temporary `.mmd` file and executes Node.js with `tests/oracle/verify_mermaid.mjs`.
3. **Observation 4**: `verify_mermaid.mjs` initializes Mermaid with strict security settings and runs `mermaid.detectType(source)`. If syntax is valid for Mermaid 11.16.0, it exits with returncode 0.
4. **Observation 5**: All 31 oracle and non-API unit tests pass cleanly when `test_api.py` is excluded or warning filters are resolved.
5. **Observation 5 & Engine Integration**: Currently `test_oracle_roundtrip.py` imports from shadow modules (`models.py`, `render.py`), `test_oracle_generated.py` imports from legacy generated files (`_generated_*`), and `oracle_types/` imports from `types/`. To achieve the ggen end-to-end architecture (A = μ(O)), all test suites must be updated to target the first-class derived engine modules in `src/mmdio/engine/`.

---

## 3. Caveats

- Node.js environment assumption: The oracle tests require `node` on `$PATH` and `npm ci` completed in `tests/oracle/`. If Node or `node_modules/mermaid` is missing, `check_node_available()` skips the oracle tests.
- Warning filter precedence: Fixing `test_api.py` requires either updating the warning filter order in `pyproject.toml` or updating `test_api.py` to avoid triggering `StarletteDeprecationWarning`.

---

## 4. Conclusion

The `mmdio` test suite consists of 32 total tests across 9 files. 31 of 32 tests (100% of oracle roundtrip, generated oracle, and type-scoped oracle tests) currently pass cleanly against Node Mermaid 11.16.0 via `verify_mermaid.mjs`. A single unit test (`test_api.py`) fails under `uv run pytest` due to strict warning escalation (`filterwarnings = ["error"]`). All oracle test suites function reliably and provide the necessary verification harness for ggen code derivation.

---

## 5. Verification Method

To independently verify these findings:

1. **Run full pytest suite**:
   ```bash
   uv run pytest --ignore=tests/test_api.py
   ```
   *Expected result*: 31 passed in ~7s.

2. **Verify Node Mermaid Oracle manually**:
   ```bash
   node tests/oracle/verify_mermaid.mjs <(echo -e "graph TD\n    A --> B")
   ```
   *Expected output*: `SUCCESS: Detected diagram type: flowchart` with exit code 0.

3. **Verify Pinned Mermaid Version**:
   ```bash
   cat tests/oracle/package.json
   ```
   *Expected output*: `"mermaid": "11.16.0"`
