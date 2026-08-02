# Analysis & Verification Report: Python Import Collection & Verification

**Investigator**: Explorer 3 (Milestone M1 - Iteration 2)  
**Working Directory**: `/Users/sac/mmdio/.agents/explorer_m1_3_r2`  
**Target Focus**: Verification of `src/mmdio/engine/models.py`, `src/mmdio/engine/render_dispatch.py`, `uv run pytest`, and `ggen sync run --dry-run`.

---

## 1. Observation

### Observation 1.1: SPARQL Query & Model Set Mismatch in Templates
- `packs/mmdio-pack/templates/generated_models.py.tmpl`:
  - Query `models` (lines 5-13): Selects class definitions for diagram types that possess `mer:hasModel` RDF triples in `packs/mmdio-pack/ontology.ttl`. Currently in `ontology.ttl`, only **5 diagram types** (`block`, `kanban`, `pie`, `sankey`, `timeline`) have `mer:hasModel` triples.
  - Query `union_models` (lines 28-36): Selects diagram types where `mer:pythonSupport true` is set, returning **15 class names** (including 10 diagram types without `mer:hasModel` triples: `C4Diagram`, `ClassDiagram`, `ERDiagram`, `FlowchartDiagram`, `GanttChart`, `GitGraph`, `Mindmap`, `SequenceDiagram`, `StateDiagram`, `XYChartDiagram`).
  - Output effect: Lines 75-79 emit:
    ```python
    MermaidDiagram = (
        BlockDiagram | C4Diagram | ClassDiagram | ERDiagram | FlowchartDiagram | GanttChart | GitGraph | KanbanDiagram | Mindmap | PieChart | SankeyDiagram | SequenceDiagram | StateDiagram | TimelineDiagram | XYChartDiagram
    )
    ```
    Since `C4Diagram`, `ClassDiagram`, etc., are not defined in the body, Python execution of `models.py` fails with:
    `NameError: name 'C4Diagram' is not defined`.

### Observation 1.2: Render Dispatcher Missing Exports in Render Module
- `packs/mmdio-pack/templates/generated_render_dispatch.py.tmpl`:
  - Query `rows` (lines 5-15): Queries all 15 diagram types where `mer:pythonSupport true`.
  - Output effect: Emits imports for models and render functions for all 15 types:
    ```python
    from mmdio.engine.models import BlockDiagram
    from mmdio.engine.render import render_block
    from mmdio.engine.models import C4Diagram
    from mmdio.engine.render import render_c4
    ...
    ```
  - Running direct import `uv run python -c "from mmdio.engine.models import BlockDiagram"` triggers `mmdio.engine.__init__.py` -> `render_dispatch.py` -> `from mmdio.engine.render import render_block`, raising:
    `ImportError: cannot import name 'render_block' from 'mmdio.engine.render'` (because `render.py` generated from `generated_render_bodies.py.tmpl` only generates render functions for models with `mer:hasModel`).

### Observation 1.3: Pytest Warning Filter Failure
- `pyproject.toml` line 85:
  ```toml
  [tool.pytest.ini_options]
  filterwarnings = ["error", "ignore::DeprecationWarning"]
  ```
- Running `uv run pytest` fails during collection of `tests/test_api.py`:
  `starlette.exceptions.StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`
- Because `filterwarnings = ["error", ...]` treats any unhandled warning as an error, `StarletteDeprecationWarning` halts `pytest` collection before any tests run.

---

## 2. Logic Chain

1. **Root Cause of Import Failure (`NameError` / `ImportError`)**:
   - `ontology.ttl` sets `mer:pythonSupport true` for 15 diagram types to satisfy Gate 010.
   - However, only 5 diagram types currently have `mer:hasModel` facts.
   - `generated_models.py.tmpl` (via `union_models`) and `generated_render_dispatch.py.tmpl` (via `rows`) query `mer:pythonSupport true`, assuming all 15 models exist.
   - `generated_models.py.tmpl` (via `models`) and `generated_render_bodies.py.tmpl` (via `models`) query `mer:hasModel`, defining only 5 models and 5 render functions.
   - When `ggen sync run` precipitates files:
     - `models.py` contains undefined identifiers in `MermaidDiagram` (`NameError`).
     - `render_dispatch.py` attempts to import non-existent render functions from `render.py` (`ImportError`).

2. **Root Cause of Pytest Failure**:
   - `test_api.py` imports `fastapi.testclient.TestClient`, which raises `StarletteDeprecationWarning`.
   - `pyproject.toml` sets `filterwarnings = ["error", "ignore::DeprecationWarning"]`. Custom subclass warnings like `StarletteDeprecationWarning` are not caught by `ignore::DeprecationWarning`, turning into errors.

3. **Requirement Synthesis**:
   - To achieve 100% clean import collection, test suite execution, and law gate validation:
     1. SPARQL queries across `generated_models.py.tmpl` and `generated_render_dispatch.py.tmpl` must be synchronized with `mer:hasModel` availability (or `ontology.ttl` must supply `mer:hasModel` facts for all supported types).
     2. `pyproject.toml` must ignore `StarletteDeprecationWarning`.

---

## 3. Caveats

- **Read-Only Scope**: Per subagent constraints, Explorer 3 performed investigation and verification analysis without modifying source/pack files directly.
- **Verification Commands**: The verification commands below test both dry-run gate validation and active module import collection.

---

## 4. Conclusion & Recommended Fixes

### Conclusion
`src/mmdio/engine/models.py` and `src/mmdio/engine/render_dispatch.py` fail Python import collection following `ggen sync run` due to a structural query mismatch between `union_models`/`rows` (which assume 15 models) and `models` (which define only 5 models). Additionally, `uv run pytest` fails on collection due to `StarletteDeprecationWarning` handling.

### Recommended Fixes

1. **Synchronize Template Queries**:
   - In `packs/mmdio-pack/templates/generated_models.py.tmpl`, filter `union_models` by `mer:hasModel`:
     ```sparql
     union_models: |
       PREFIX mer: <https://seanchatmangpt.github.io/ontology/mermaid#>
       SELECT ?internalId ?modelModule ?modelClass WHERE {
         ?type a mer:DiagramType ;
               mer:pythonInternalId ?internalId ;
               mer:pythonSupport true ;
               mer:hasModel ?model ;
               mer:pythonModelModule ?modelModule ;
               mer:pythonModelClass ?modelClass .
         ?model a mer:PythonModel ;
                mer:isTopLevel true .
       } ORDER BY ?internalId
     ```
   - In `packs/mmdio-pack/templates/generated_render_dispatch.py.tmpl`, filter `rows` by `mer:hasModel`:
     ```sparql
     rows: |
       PREFIX mer: <https://seanchatmangpt.github.io/ontology/mermaid#>
       SELECT ?internalId ?modelModule ?modelClass ?renderModule ?renderFunction WHERE {
         ?type a mer:DiagramType ;
               mer:pythonInternalId ?internalId ;
               mer:pythonSupport true ;
               mer:hasModel ?model ;
               mer:pythonModelModule ?modelModule ;
               mer:pythonModelClass ?modelClass ;
               mer:pythonRenderModule ?renderModule ;
               mer:pythonRenderFunction ?renderFunction .
         ?model a mer:PythonModel ;
                mer:isTopLevel true .
       } ORDER BY ?internalId
     ```

2. **Update Pytest Warning Filter in `pyproject.toml`**:
   ```toml
   [tool.pytest.ini_options]
   filterwarnings = [
     "error",
     "ignore::DeprecationWarning",
     "ignore::starlette.exceptions.StarletteDeprecationWarning",
   ]
   ```

---

## 5. Verification Method

To independently verify clean import collection, test suite execution, and dry-run gate validation:

1. **Verify Python Engine Import Collection**:
   ```bash
   uv run python -c "import mmdio.engine.models; import mmdio.engine.render_dispatch"
   ```
   *Expected result*: Exit Code `0` with no `NameError` or `ImportError`.

2. **Verify Pytest Test Suite Pass**:
   ```bash
   uv run pytest
   ```
   *Expected result*: Exit Code `0` with 100% test cases passing and 0 collection errors.

3. **Verify ggen Law Gate Dry-Run**:
   ```bash
   uv run ggen sync run --dry-run
   ```
   *Expected result*: Exit Code `0` passing all 10 SPARQL law gates.

4. **Verify End-to-End Precipitation & Verification Pipeline**:
   ```bash
   uv run ggen sync run && uv run python -c "import mmdio.engine.models; import mmdio.engine.render_dispatch" && uv run pytest
   ```
   *Expected result*: Exit Code `0` across generation, import, and test collection.
