# Codebase Analysis: Test Suite & Oracle Harness

## Executive Summary
This analysis details the test suite, oracle verification harness, pytest configuration, pass/fail expectations, and engine module interactions in `mmdio`. The codebase currently includes **32 test cases** across **9 test modules**, categorized into unit tests, generated oracle tests, roundtrip oracle tests, and type-scoped oracle tests. Oracle verification relies on a Node.js script (`tests/oracle/verify_mermaid.mjs`) leveraging pinned **Mermaid 11.16.0** to validate generated diagram syntax using `mermaid.detectType()`.

---

## 1. Test Suite Inventory & Structure

The repository contains 9 test python files and 1 Node oracle verification harness script:

| Test File | Category | Test Count | Target Modules / Purpose | Current Status |
|-----------|----------|------------|--------------------------|----------------|
| `tests/test_import.py` | Unit Test | 1 | `mmdio.__name__` basic import sanity | PASSED |
| `tests/test_cli.py` | Unit Test | 1 | `mmdio.cli.app` via `typer.testing.CliRunner` | PASSED |
| `tests/test_api.py` | Unit Test | 1 | `mmdio.api.app` via `fastapi.testclient.TestClient` | ERROR (warning filter) |
| `tests/test_oracle_generated.py` | Generated Oracle | 5 | Ontology-derived fixtures & renderers (`_generated_fixtures`, `_generated_render_bodies`) | PASSED (5/5) |
| `tests/test_oracle_roundtrip.py` | Roundtrip Oracle | 11 | Main 11 diagram types (`mmdio.engine.models`, `mmdio.engine.render`) | PASSED (11/11) |
| `tests/oracle_types/test_oracle_block.py` | Type-Scoped Oracle | 4 | `block_models`, `block_render` (simple, columns, labels, arrows) | PASSED (4/4) |
| `tests/oracle_types/test_oracle_kanban.py` | Type-Scoped Oracle | 3 | `kanban_models`, `kanban_render` (simple, empty sections, single card) | PASSED (3/3) |
| `tests/oracle_types/test_oracle_timeline.py` | Type-Scoped Oracle | 3 | `timeline_models`, `timeline_render` (simple, no title, date formats) | PASSED (3/3) |
| `tests/oracle_types/test_oracle_xychart.py` | Type-Scoped Oracle | 3 | `xychart_models`, `xychart_render` (simple, with strings, without title) | PASSED (3/3) |
| **Total** | | **32** | | **31 Passed, 1 Error** |

---

## 2. Node Mermaid Oracle Harness Analysis

### 2.1 Dependencies & Version Pinning
- Location: `tests/oracle/package.json`
- Pinned Dependency: `"mermaid": "11.16.0"` (`"type": "module"`)
- Local Installation: `tests/oracle/node_modules/mermaid` (verified version `11.16.0`)

### 2.2 Verification Script (`tests/oracle/verify_mermaid.mjs`)
- File path argument: `process.argv[2]` (path to temporary `.mmd` file)
- Initialization:
  ```javascript
  await mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'strict',
    htmlLabels: false,
    flowchart: { defaultRenderer: 'dagre-wrapper' },
    architecture: { randomize: false }
  });
  ```
- Validation core:
  Calls `mermaid.detectType(source)`. This detects and validates diagram syntax without requiring DOM rendering capabilities or browser emulation.
- Exit behavior:
  - Exit code `0` on successful type detection (stdout: `SUCCESS: Detected diagram type: <type>`)
  - Exit code `1` on parse error or missing file parameter (stderr: `PARSE_ERROR: <message>`)

### 2.3 Python Subprocess Execution & Availability Guard
- Helper functions: `check_node_available()` and `validate_mermaid_source(mmd_source: str)` defined in `tests/test_oracle_roundtrip.py` (and re-implemented in `tests/oracle_types/test_oracle_timeline.py`).
- Availability Guard:
  Checks `shutil.which("node")` and existence of `tests/oracle/node_modules/mermaid`. If unavailable, tests are skipped using `pytestmark = pytest.mark.skipif(...)`.
- Execution flow:
  1. Creates temporary file `NamedTemporaryFile(suffix='.mmd', delete=False)`.
  2. Executes `subprocess.run(['node', oracle_script_path, temp_path], capture_output=True, text=True, timeout=10)`.
  3. Asserts returncode `0`, including stdout/stderr/source in failure message if non-zero.
  4. Unlinks temporary file in `finally:` block.

---

## 3. Pytest Invocation & Configuration Analysis

### 3.1 `pyproject.toml` Settings
- `testpaths = ["src", "tests"]`
- `addopts = "--color=yes --doctest-modules --exitfirst --failed-first --strict-config --strict-markers --verbosity=2 --junitxml=reports/pytest.xml"`
- `filterwarnings = ["error", "ignore::DeprecationWarning"]`
- `xfail_strict = true`

### 3.2 Analysis of Current Test Failure
- Running `uv run pytest` fails during test collection on `tests/test_api.py`.
- Cause: `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`
- Reason for failure: `pyproject.toml` configures `filterwarnings = ["error", ...]`. Python warning filters match top-to-bottom. The leading `"error"` turns `StarletteDeprecationWarning` into an unhandled exception before `ignore::DeprecationWarning` is evaluated. Coupled with `--exitfirst`, pytest halts immediately.
- Resolution verification: Running `uv run pytest --ignore=tests/test_api.py` results in **31 passed in 7.23s**.

---

## 4. Test Harness Interaction with Derived Engine Files

### 4.1 Current Engine Import Layout
Currently, tests import from three separate locations in `src/mmdio/engine`:
1. **Shadow hand-written modules**: `test_oracle_roundtrip.py` imports `from mmdio.engine import models, render` (`models.py`, `render.py`).
2. **Generated legacy modules**: `test_oracle_generated.py` imports from `_generated_fixtures.py` and `_generated_render_bodies.py`.
3. **Type-scoped submodules**: `oracle_types/` tests import from `mmdio.engine.types.<type>_models` and `mmdio.engine.types.<type>_render`.

### 4.2 Target ggen End-to-End Architecture (A = μ(O)) Requirements
According to `ORIGINAL_REQUEST.md`:
- Hand-written shadow modules (`models.py`, `parser.py`, `render.py`) and temporary generated prefixes (`_generated_*`) must be removed and unified.
- Derived code must land in standard, first-class python paths (`src/mmdio/engine/`).
- The test harness (`test_oracle_roundtrip.py`, `test_oracle_generated.py`, and `oracle_types/`) must be updated to import AST models, parser registries, and render dispatchers directly from the first-class derived engine modules in `src/mmdio/engine/`.
