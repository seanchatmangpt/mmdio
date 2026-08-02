# Review Report — Reviewer 1 (Milestone M1: ggen Pack & Ontology Configuration)

## Verdict: REQUEST_CHANGES

---

## 1. Observation

A review was performed on the Milestone M1 implementation changes in `packs/mmdio-pack/pack.toml`, `packs/mmdio-pack/ontology.ttl`, and the 11 Tera templates in `packs/mmdio-pack/templates/`.

### 1.1 Verified Claims & Checks

- **Frontmatter Target Paths**: All 9 engine templates in `packs/mmdio-pack/templates/` have frontmatter `to:` directives updated to emit first-class Python files under `src/mmdio/engine/` (`detect_patterns.py`, `enums.py`, `fixtures.py`, `models.py`, `parser_registry.py`, `supported.py`, `render.py`, `render_dispatch.py`, `schemas.py`). Zero legacy `_generated_*` filenames remain.
- **Internal Imports**: Internal template imports in `generated_fixtures.py.tmpl`, `generated_models.py.tmpl`, `generated_oracle_tests.py.tmpl`, and `generated_render_dispatch.py.tmpl` correctly reference `mmdio.engine.models`, `mmdio.engine.enums`, `mmdio.engine.render`, and `mmdio.engine.parser`.
- **RDF Triples Expansion**: `ontology.ttl` was expanded with `mer:PythonEnum` and `mer:EnumMember` triples for all 7 domain token enums (`NodeShape`, `MessageType`, `RelationshipType`, `CardinityType`, `TaskStatus`, `C4Level`, `ParticipantType`), and module predicates (`mer:pythonModelModule`, `mer:pythonTransformerModule`, `mer:pythonRenderModule`) were updated to `mmdio.engine.*`.
- **Dry-Run Execution**: Running `uv run ggen sync run --dry-run` exits with code 0 and reports 0 SPARQL law gate violations across all 10 gates (`packs/mmdio-pack/gates/*.rq`).

### 1.2 Identified Issue / Defect

- **Runtime `NameError` in Precipitated `src/mmdio/engine/models.py`**:
  Executing `uv run python -c "import mmdio.engine.models"` fails with:
  ```
  Traceback (most recent call last):
    File "<string>", line 1, in <module>
    File "/Users/sac/mmdio/src/mmdio/engine/models.py", line 216, in <module>
      C4Diagram |
      ^^^^^^^^^
  NameError: name 'C4Diagram' is not defined
  ```

---

## 2. Findings

### [Major] Finding 1: `generated_models.py.tmpl` generates undefined class references in `MermaidDiagram` union

- **What**: Precipitating `src/mmdio/engine/models.py` generates a `MermaidDiagram` discriminated union that references `C4Diagram`, `ClassDiagram`, `ERDiagram`, `FlowchartDiagram`, `GanttChart`, `GitGraph`, `Mindmap`, `SequenceDiagram`, `StateDiagram`, and `XYChartDiagram`, none of which are defined in `models.py`.
- **Where**: `packs/mmdio-pack/templates/generated_models.py.tmpl` (lines 28–36) and precipitated output `src/mmdio/engine/models.py` (line 216).
- **Why**: The `union_models` SPARQL query in `generated_models.py.tmpl` is:
  ```sparql
  union_models: |
    PREFIX mer: <https://seanchatmangpt.github.io/ontology/mermaid#>
    SELECT ?internalId ?modelModule ?modelClass WHERE {
      ?type a mer:DiagramType ;
            mer:pythonInternalId ?internalId ;
            mer:pythonSupport true ;
            mer:pythonModelModule ?modelModule ;
            mer:pythonModelClass ?modelClass .
    } ORDER BY ?internalId
  ```
  This query selects `?modelClass` for all 15 diagram types that have `mer:pythonSupport true`, even though only 5 diagram types (`kanban`, `timeline`, `block`, `pie`, `sankey`) have `mer:hasModel` / `mer:PythonModel` class definitions in `ontology.ttl`. Consequently, `generated_models.py.tmpl` emits `MermaidDiagram = (BlockDiagram | C4Diagram | ...)` referencing 10 ungenerated/undefined classes, breaking any Python attempt to import `mmdio.engine.models`.

- **Suggestion**: Update the `union_models` SPARQL query in `generated_models.py.tmpl` to join `mer:hasModel` so that `MermaidDiagram` only includes top-level model classes that are actually defined in `ontology.ttl` and generated in `models.py`:
  ```sparql
  union_models: |
    PREFIX mer: <https://seanchatmangpt.github.io/ontology/mermaid#>
    SELECT DISTINCT ?modelClass WHERE {
      ?type mer:pythonSupport true ;
            mer:hasModel ?model .
      ?model a mer:PythonModel ;
             mer:isTopLevel true ;
             mer:className ?modelClass .
    } ORDER BY ?modelClass
  ```

---

## 3. Logic Chain

1. Requirements dictate that Tera templates must cleanly emit valid first-class Python engine modules under `src/mmdio/engine/`.
2. `generated_models.py.tmpl` was updated to consolidate the `MermaidDiagram` discriminated union at the bottom of `src/mmdio/engine/models.py`.
3. The `union_models` query in `generated_models.py.tmpl` queries `?type mer:pythonSupport true` rather than models that exist in `ontology.ttl`.
4. As a result, 10 undefined model classes are emitted in the `MermaidDiagram` union statement.
5. Importing `src/mmdio/engine/models.py` in Python raises `NameError: name 'C4Diagram' is not defined`.
6. Therefore, the template changes in `generated_models.py.tmpl` render the precipitated engine output unimportable, requiring a fix before approval.

---

## 4. Caveats

- `ggen sync run --dry-run` passes all 10 SPARQL law gates because law gates only validate RDF model shapes and metadata, not Python runtime AST importability.
- No integrity violations or intentional shortcuts were detected in the worker's changes.

---

## 5. Conclusion

The Milestone M1 configuration updates for `pack.toml`, `ontology.ttl`, and frontmatter directives in `templates/` are structurally sound and well-organized. However, due to the `union_models` SPARQL query flaw in `generated_models.py.tmpl` causing runtime `NameError` upon importing `mmdio.engine.models`, the overall verdict is **`REQUEST_CHANGES`**.

---

## 6. Verification Method

To verify the requested fix:

1. **Update `generated_models.py.tmpl`**: Apply the `union_models` SPARQL query fix.
2. **Re-precipitate Engine**: Run `rm -f ggen.lock && uv run ggen sync run`.
3. **Verify Python Importability**:
   ```bash
   uv run python -c "import mmdio.engine.models; print(mmdio.engine.models.MermaidDiagram)"
   ```
   *Expected result*: Clean import without `NameError`.
4. **Verify Dry-Run Gate Pass**:
   ```bash
   uv run ggen sync run --dry-run --format json
   ```
   *Expected result*: Exit code 0 with 0 SPARQL law gate violations.
