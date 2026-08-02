# Review Report — Reviewer 2 (Milestone M1: ggen Pack & Ontology Configuration)

**Verdict**: REQUEST_CHANGES

---

## 1. Observation

A detailed examination of the implementation delivered for Milestone M1 (`packs/mmdio-pack/`, `src/mmdio/engine/`) against the requirements in `PROJECT.md`, `SCOPE.md`, and `ORIGINAL_REQUEST.md` revealed the following exact observations:

### 1.1 `ggen sync run --dry-run` and SPARQL Law Gates
- Command executed: `uv run ggen sync run --dry-run --format json`
- Output: Exit code `0`, `0` violations reported across all 10 SPARQL law gates (`010` through `100`).
- Target paths: Template frontmatter `to:` directives correctly re-target all generated files to `src/mmdio/engine/*.py` (e.g. `models.py`, `enums.py`, `parser_registry.py`, `render_dispatch.py`, `render.py`, `schemas.py`, `fixtures.py`, `supported.py`, `detect_patterns.py`), eliminating legacy `_generated_*` filenames.

### 1.2 Python Runtime & Import Errors
- Command executed: `uv run python -c "import mmdio.engine.models"`
- Output: `NameError: name 'C4Diagram' is not defined`
- Line reference: `src/mmdio/engine/models.py:216`
- Stack trace:
  ```
  ERROR src/mmdio/engine/__init__.py
  src/mmdio/engine/__init__.py:9: in <module>
      from mmdio.engine.models import (
  src/mmdio/engine/models.py:216: in <module>
      C4Diagram |
  E   NameError: name 'C4Diagram' is not defined
  ```

### 1.3 Missing Ontology Facts in `packs/mmdio-pack/ontology.ttl`
- RDF query for `mer:PythonModel` instances across the graph yielded only 12 models across 5 diagram types (`block`, `kanban`, `pie`, `sankey`, `timeline`).
- `ontology.ttl` is missing `mer:PythonModel` and `mer:PythonField` triples for the remaining 10 diagram types (`c4`, `class`, `er`, `flowchart`, `gantt`, `git`, `mindmap`, `sequence`, `state`, `xychart`), despite complete RDF snippets existing in `EXPANSION_RDF_SNIPPETS.md`.

### 1.4 Test Suite Status
- Command executed: `uv run pytest`
- Output: `Exit Code 1` (0 tests passed, 1 collection error in `src/mmdio/engine/__init__.py`).

---

## 2. Logic Chain

1. **Premise**: `PROJECT.md` and `SCOPE.md` require precipitating first-class Python engine modules (`src/mmdio/engine/models.py`, etc.) directly from `ontology.ttl` and Tera templates, supporting all 15 diagram types.
2. **Template Behavior**: `generated_models.py.tmpl` contains two queries:
   - `models`: Queries `?type mer:hasModel ?model . ?model a mer:PythonModel`.
   - `union_models`: Queries `?type a mer:DiagramType ; mer:pythonSupport true ; mer:pythonModelClass ?modelClass`.
3. **Inconsistency Cause**: `ontology.ttl` has `mer:pythonModelClass "C4Diagram"` on `mer:Type_c4Diagram`, so `union_models` returns `C4Diagram` (and 9 other model class names). However, because `ontology.ttl` lacks the `mer:hasModel mer:Model_C4Diagram` and `mer:Model_C4Diagram a mer:PythonModel` triples from `EXPANSION_RDF_SNIPPETS.md`, the `models` query returns nothing for `C4Diagram`.
4. **Precipitation Failure**: When `ggen sync run` generates `src/mmdio/engine/models.py`, `class C4Diagram(BaseModel): ...` is NEVER rendered, but `MermaidDiagram = ( ... | C4Diagram | ... )` is rendered at the bottom of the file.
5. **Runtime Failure**: Python evaluates `models.py` sequentially upon import. When it hits line 216 (`C4Diagram |`), it raises `NameError: name 'C4Diagram' is not defined`.
6. **Cascade**: Because `src/mmdio/engine/__init__.py` imports `models.py`, all `mmdio.engine` imports fail, breaking the entire `pytest` test harness.

---

## 3. Findings

### [Critical] Finding 1: Incomplete RDF Ontology Expansion in `packs/mmdio-pack/ontology.ttl` Causes `NameError: name 'C4Diagram' is not defined` & Unimportable Engine Code
- **What**: `packs/mmdio-pack/ontology.ttl` only contains `mer:PythonModel` and `mer:PythonField` triples for 5 diagram types (`block`, `kanban`, `pie`, `sankey`, `timeline`). The RDF triples for the remaining 10 diagram types (`c4`, `class`, `er`, `flowchart`, `gantt`, `git`, `mindmap`, `sequence`, `state`, `xychart`) in `EXPANSION_RDF_SNIPPETS.md` were NOT merged into `ontology.ttl`.
- **Where**: `packs/mmdio-pack/ontology.ttl`, `src/mmdio/engine/models.py`
- **Why**: `generated_models.py.tmpl` generates the `MermaidDiagram` discriminated union using all 15 `mer:DiagramType` entries with `mer:pythonSupport true`. But because `mer:PythonModel` triples for 10 of those diagram types are missing from `ontology.ttl`, `models.py` emits `MermaidDiagram = (BlockDiagram | C4Diagram | ClassDiagram | ...)` referencing model classes that are never defined in `models.py`.
- **Impact**: Importing `mmdio.engine` or any module within `src/mmdio/engine/` immediately raises `NameError: name 'C4Diagram' is not defined`. Running `uv run pytest` fails completely during test collection (0 tests pass, 1 collection error).
- **Suggestion**: Merge all RDF triples from `EXPANSION_RDF_SNIPPETS.md` into `packs/mmdio-pack/ontology.ttl`, ensuring all 15 diagram AST models and their child models are fully declared in RDF. Re-run `uv run ggen sync run` and verify `uv run pytest` collects and executes without `NameError`.

### [Major] Finding 2: SPARQL Gate 010 Does Not Validate Presence of `mer:hasModel` / `mer:PythonModel`
- **What**: SPARQL gate `010_python_support_complete.rq` checks properties like `mer:pythonModelModule` and `mer:pythonModelClass`, but does NOT verify that `mer:hasModel` points to a valid `mer:PythonModel`.
- **Where**: `packs/mmdio-pack/gates/010_python_support_complete.rq`
- **Why**: As a result of this gap in Gate 010, `ggen sync run --dry-run` passed all 10 gates with 0 violations despite 10 diagram types lacking RDF model definitions.
- **Suggestion**: Add a UNION clause to Gate 010 verifying `FILTER NOT EXISTS { ?type mer:hasModel ?m }`.

---

## 4. Verified Claims Matrix

| Claim | Method | Result | Notes |
|-------|--------|--------|-------|
| `ggen sync run --dry-run` completes with exit code 0 | `uv run ggen sync run --dry-run --format json` | PASS | Exit code 0, 0 gate violations |
| 10 SPARQL gates pass rdflib evaluation | Python script with `rdflib.Graph` | PASS | 0 violations across 10 gate queries |
| Frontmatter target paths re-targeted to `src/mmdio/engine/` | `grep -n "^to:" packs/mmdio-pack/templates/*.tmpl` | PASS | All 9 engine templates target `src/mmdio/engine/*.py` |
| Consolidated `generated_models.py.tmpl` | Inspect template & generated `models.py` | FAIL | Emits `MermaidDiagram` with undefined class names |
| Precipitated Python engine code is importable | `uv run python -c "import mmdio.engine.models"` | FAIL | `NameError: name 'C4Diagram' is not defined` |
| Pytest suite executes cleanly | `uv run pytest` | FAIL | Exit code 1, collection error on `models.py` |

---

## 5. Coverage Gaps

- **Missing RDF Model Facts**: 10 of 15 diagram types lack `mer:PythonModel` and `mer:PythonField` triples in `packs/mmdio-pack/ontology.ttl`. High risk until `EXPANSION_RDF_SNIPPETS.md` is fully merged into `ontology.ttl`.

---

## 6. Unverified Items

- **Node-based Mermaid Oracle verification**: Unverified for M1 because `pytest` suite cannot collect due to `models.py` import failure.

---

## 7. Caveats

- Gate evaluation alone (`ggen sync run --dry-run`) is insufficient to verify Python code validity; actual module import and test suite execution (`pytest`) are necessary steps for verification.

---

## 8. Conclusion

While template frontmatter re-targeting and gate query structure updates were correctly completed, Milestone M1 cannot be approved in its current state due to incomplete RDF ontology expansion in `packs/mmdio-pack/ontology.ttl`, which renders the precipitated Python engine broken and unimportable.

---

## 9. Verification Method

To verify the required fix after Worker updates `ontology.ttl`:

1. **Verify `models.py` generation & imports**:
   ```bash
   uv run ggen sync run
   uv run python -c "import mmdio.engine.models; print('models imported successfully!')"
   ```

2. **Verify all engine module imports**:
   ```bash
   uv run python -c "
   import importlib
   for mod in ['mmdio.engine.enums', 'mmdio.engine.supported', 'mmdio.engine.detect_patterns', 'mmdio.engine.schemas', 'mmdio.engine.fixtures', 'mmdio.engine.parser_registry', 'mmdio.engine.models', 'mmdio.engine.render', 'mmdio.engine.render_dispatch']:
       importlib.import_module(mod)
   print('All engine modules import cleanly!')
   "
   ```

3. **Verify Dry-Run & Gate Pass**:
   ```bash
   uv run ggen sync run --dry-run --format json
   ```

4. **Verify Pytest Collection**:
   ```bash
   uv run pytest --co
   ```
