# Comprehensive Analysis: ggen Pack & Gates Specification in `mmdio`

## 1. Overview & Core Mathematical Framework: $A = \mu(O)$

The `mmdio` engine architecture is designed around ontology-driven code generation, formalized by the precipitation equation:

$$A = \mu(O)$$

Where:
- **$O$ (Ontology / RDF Knowledge Graph)**: The unified RDF graph formed by merging:
  1. `src/mmdio/engine/registry.ttl`: Upstream-pinned definitions for all 39 Mermaid diagram types in Mermaid 11.16.0 (defining `mer:DiagramType`, `mer:diagramId`, `mer:displayName`, detector/definition/renderer paths).
  2. `packs/mmdio-pack/ontology.ttl`: Python implementation metadata (`mer:pythonSupport`, `mer:pythonInternalId`, `mer:pythonModelClass`, `mer:grammarFile`, `mer:detectPattern`) and the field-shape matrix (`mer:PythonModel`, `mer:PythonField`, `mer:PythonEnum`, `mer:EnumMember`).
- **$\mu$ (Precipitation Function / Generator Mapping)**: The transformation pipeline executed by the `ggen` CLI tool (`version 26.8.2`), which:
  1. Validates $O$ against 10 SHACL-like SPARQL Law Gates in `packs/mmdio-pack/gates/`.
  2. Executes SPARQL queries declared in Jinja2 template frontmatter (`packs/mmdio-pack/templates/*.tmpl`).
  3. Projects query results into first-class Python source code and documentation.
- **$A$ (Artifacts / Precipitated Modules)**: The set of 12 derived target files landed directly in `src/mmdio/`, `src/mmdio/engine/`, `tests/`, and `docs/`.

---

## 2. Currently Generated vs Intended Code Generation

### A. Currently Generated Code ($A$)
All generated files carry the header `"""GENERATED FILE — do not edit by hand. Regenerate with ggen sync run."""` and are produced by `ggen sync run`:

| Target Path | Generating Template | RDF Source / SPARQL Logic | Content Summary |
|---|---|---|---|
| `src/mmdio/engine/_generated_enums.py` | `generated_enums.py.tmpl` | `mer:PythonEnum`, `mer:EnumMember` | `StrEnum` classes (e.g. `KanbanSection`, etc.) |
| `src/mmdio/engine/_generated_pydantic_models.py` | `generated_models.py.tmpl` | `mer:PythonModel`, `mer:PythonField` | Pydantic `BaseModel` classes with discriminators and field shapes for Kanban, Timeline, Block, Pie, Sankey |
| `src/mmdio/engine/_generated_models.py` | `generated_models_union.py.tmpl` | `mer:DiagramType` with `mer:pythonSupport true` | `MermaidDiagram` discriminated union type across all supported diagram model classes |
| `src/mmdio/engine/_generated_parser_registry.py` | `generated_parser_registry.py.tmpl` | `mer:DiagramType` (transformers & grammars) | `GENERATED_TRANSFORMERS` dict and `GENERATED_GRAMMAR_FILES` dict |
| `src/mmdio/engine/_generated_render_bodies.py` | `generated_render_bodies.py.tmpl` | `mer:PythonModel`, `mer:PythonField` | Pure-python render functions (`render_kanban`, `render_timeline`, `render_block`, `render_pie`, `render_sankey`) |
| `src/mmdio/engine/_generated_render_dispatch.py` | `generated_render_dispatch.py.tmpl` | `mer:DiagramType` (models & renderers) | `GENERATED_RENDER_DISPATCH` dict mapping model class -> render function |
| `src/mmdio/engine/_generated_schemas.py` | `generated_schemas.py.tmpl` | `mer:PythonModel`, `mer:PythonField` | `GENERATED_JSON_SCHEMAS` mapping diagram ID -> JSON Schema dict |
| `src/mmdio/engine/_generated_supported.py` | `generated_python_supported.py.tmpl` | `mer:DiagramType` (`mer:diagramId`) | `GENERATED_PYTHON_SUPPORTED` `frozenset` of canonical diagram IDs |
| `src/mmdio/_generated_detect_patterns.py` | `generated_detect_patterns.py.tmpl` | `mer:DiagramType` (`mer:detectPattern`) | `GENERATED_DETECT_PATTERNS` regex list |
| `src/mmdio/engine/_generated_fixtures.py` | `generated_fixtures.py.tmpl` | `mer:PythonModel`, `mer:fieldExampleValue` | `example_{id}()` fixture builders for top-level diagram models |
| `tests/test_oracle_generated.py` | `generated_oracle_tests.py.tmpl` | Top-level `mer:PythonModel`s | `TestOracle{ClassName}` test suite against Node.js Mermaid oracle |
| `docs/diagram_status.md` | `generated_status_table.md.tmpl` | All 39 `mer:DiagramType`s | Markdown support status table |

### B. Intended Architecture & Legacy Hand-written Code
- **Original Hand-written Modules**: `src/mmdio/engine/models.py`, `parser.py`, `render.py`.
  - Historically contained hand-written Pydantic models for the original 11 diagram types (`FlowchartDiagram`, `SequenceDiagram`, `ClassDiagram`, `StateDiagram`, `ERDiagram`, `GanttChart`, `PieChart`, `GitGraph`, `C4Diagram`, `Mindmap`, `SankeyDiagram`).
  - To fulfill Requirement R1 ("First-Class ggen Code Derivation without shadow duplication"), wiring glue and structural model declarations precipitate from RDF into `_generated_*` files, which are directly re-exported by `models.py`, `parser.py`, and `render.py`.

---

## 3. Analysis of all 10 SPARQL Law Gates (`packs/mmdio-pack/gates/`)

All 10 gates are executed by `ggen` prior to template rendering. A gate passes when its SPARQL query returns 0 rows (empty violation set).

```
packs/mmdio-pack/gates/
├── 010_python_support_complete.rq
├── 020_no_duplicate_internal_id.rq
├── 030_field_shape_closed_vocabulary.rq
├── 040_field_order_gapless.rq
├── 050_render_format_present_for_list_fields.rq
├── 060_render_nesting_depth_limit.rq
├── 070_enum_class_exists_for_enum_fields.rq
├── 080_scalar_example_value_present.rq
├── 090_field_pytype_resolves.rq
└── 100_classname_globally_unique.rq
```

### Detailed Gate Specifications:

1. **`010_python_support_complete.rq` (Completeness Gate)**
   - *Target*: `mer:DiagramType` with `mer:pythonSupport true`.
   - *Validation*: Every supported type MUST have all 9 required predicates: `pythonInternalId`, `pythonModelModule`, `pythonModelClass`, `pythonTransformerModule`, `pythonTransformerClass`, `pythonRenderModule`, `pythonRenderFunction`, `grammarFile`, `detectPattern`.
   - *Failure Impact*: Missing metadata causes template compilation/rendering failures in downstream dispatchers.

2. **`020_no_duplicate_internal_id.rq` (Unique Internal ID Gate)**
   - *Target*: `mer:pythonInternalId` values.
   - *Validation*: Ensures `COUNT(?type) <= 1` for each `internalId`.
   - *Failure Impact*: Internal ID collisions corrupt parser and detection lookup dictionaries.

3. **`030_field_shape_closed_vocabulary.rq` (Field Shape Matrix Gate)**
   - *Target*: `mer:PythonField`.
   - *Validation*: `mer:fieldKind` MUST be in `{"scalar-required", "scalar-optional", "list", "nested-ref", "union-type", "literal-default", "enum"}`.
   - *Failure Impact*: Prevents unhandled field kinds from slipping into model, render, and schema templates.

4. **`040_field_order_gapless.rq` (Field Ordering Gate)**
   - *Target*: `mer:PythonModel` field lists.
   - *Validation*: Checks that `MIN(?order) == 1` and `MAX(?order) == COUNT(?order)` for each model.
   - *Failure Impact*: Non-contiguous field ordering leads to broken code generation in Jinja loops.

5. **`050_render_format_present_for_list_fields.rq` (Render Format Gate)**
   - *Target*: `mer:PythonField` with `fieldKind "list"`.
   - *Validation*: Ensures every list field carries a `mer:fieldRenderFormat` f-string specification.
   - *Failure Impact*: List rendering would lack formatting logic and produce empty or malformed Mermaid output.

6. **`060_render_nesting_depth_limit.rq` (Nesting Depth Gate)**
   - *Target*: Nested `list` fields on `mer:PythonModel`.
   - *Validation*: Refuses schemas with 3 or more levels of nested list fields (`topModel -> list -> model2 -> list -> model3 -> list`).
   - *Failure Impact*: The template unrolls up to 2 levels (`_r1`, `_r2`). A 3rd level would result in silent truncation or unrendered inner elements.

7. **`070_enum_class_exists_for_enum_fields.rq` (Enum Existence Gate)**
   - *Target*: `mer:PythonField` with `fieldKind "enum"`.
   - *Validation*: Verifies that `mer:fieldPyType` references a valid `mer:PythonEnum` containing at least 1 `mer:enumMember`.
   - *Failure Impact*: Prevents `NameError` in generated model Python modules due to missing Enum classes.

8. **`080_scalar_example_value_present.rq` (Fixture Seed Gate)**
   - *Target*: `mer:PythonField` of kind `scalar-required` or `enum`.
   - *Validation*: Ensures a non-empty `mer:fieldExampleValue` exists for every required scalar or enum field.
   - *Failure Impact*: Ensures fixture builders generate valid, executable AST instances without missing required arguments.

9. **`090_field_pytype_resolves.rq` (PyType Resolution Gate)**
   - *Target*: `mer:PythonField` of kind `list` or `nested-ref`.
   - *Validation*: Confirms that `mer:fieldPyType` matches an existing `mer:PythonModel` `className`.
   - *Failure Impact*: Prevents invalid Python type annotations and unresolvable model references.

10. **`100_classname_globally_unique.rq` (Class Name Uniqueness Gate)**
    - *Target*: `mer:PythonModel` class names.
    - *Validation*: Ensures `COUNT(?model) <= 1` for each `mer:className`.
    - *Failure Impact*: Prevents class redefinition collisions in flat module namespaces (`_generated_pydantic_models.py`).

---

## 4. Template Projection Rules (`packs/mmdio-pack/templates/`)

Each template maps SPARQL query projections onto target code structures:

1. **`generated_enums.py.tmpl`**:
   - Queries `mer:PythonEnum` and `mer:EnumMember`.
   - Emits `class <EnumClassName>(StrEnum): <MemberName> = "<MemberValue>"`.
   - Rationale: Uses `StrEnum` (Python 3.11+) so f-string interpolation yields bare value tokens without `ClassName.` prefix.

2. **`generated_models.py.tmpl`**:
   - Queries `mer:PythonModel` and `mer:PythonField`.
   - Emits Pydantic `BaseModel` definitions with discriminator `type: Literal["<diagramId>"] = "<diagramId>"`.
   - Maps field shapes:
     - `scalar-required` / `nested-ref` / `union-type` / `enum` -> `<fieldName>: <fieldPyType> = Field(...)`
     - `scalar-optional` -> `<fieldName>: Optional[<fieldPyType>] = Field(default=None, ...)`
     - `list` -> `<fieldName>: List[<fieldPyType>] = Field(default_factory=list, ...)`
     - `literal-default` -> `<fieldName>: <fieldPyType> = Field(default=<fieldDefault>, ...)`

3. **`generated_models_union.py.tmpl`**:
   - Queries all python-supported diagram types.
   - Generates `MermaidDiagram = TypeA | TypeB | ...` union.

4. **`generated_parser_registry.py.tmpl`**:
   - Queries `transformerModule`, `transformerClass`, `grammarFile`.
   - Instantiates `GENERATED_TRANSFORMERS` and `GENERATED_GRAMMAR_FILES` maps.

5. **`generated_render_bodies.py.tmpl`**:
   - Queries models and fields to build `render_<diagramId>(d) -> str`.
   - Unrolls loops for `_r1` (level 1 list) and `_r2` (level 2 list) using `fieldRenderFormat` f-strings.

6. **`generated_render_dispatch.py.tmpl`**:
   - Maps `<ModelClass>: <render_function>` in `GENERATED_RENDER_DISPATCH`.

7. **`generated_detect_patterns.py.tmpl`**:
   - Builds `GENERATED_DETECT_PATTERNS = [(r"<pattern>", "<id>"), ...]`. Excludes `flowchart` via `FILTER(?internalId != "flowchart")` as flowchart is the default fallback.

8. **`generated_fixtures.py.tmpl`**:
   - Builds `example_<diagramId>()` functions populating models from `mer:fieldExampleValue`.

9. **`generated_oracle_tests.py.tmpl`**:
   - Builds `TestOracle<ClassName>` test cases invoking `validate_mermaid_source(render_<id>(example_<id>()))`.

---

## 5. Vocabulary Gaps & Caveats

1. **Recursive ASTs (Mindmap)**:
   - `MindmapNode` is self-referential (`children: List["MindmapNode"]`). Gate `060_render_nesting_depth_limit.rq` prevents recursive fields from being represented in the 2-level unrolled render template. Mindmap remains hand-written.
2. **Conditional Format Logic (Block Diagram Connections)**:
   - Connection rendering in hand-written code branches on whether `label` is present. The `fieldRenderFormat` vocabulary currently supports one static format string per list field.
3. **String Sanitization (Sankey Diagram)**:
   - Hand-written Sankey rendering strips commas from labels/identifiers (`replace(',', '')`). Template formats assume pre-sanitized input.
4. **Header Line Inlining vs Separate Line (Pie Chart)**:
   - Hand-written `render_pie` inlines `title` into `pie title X`, whereas template emits `pie\ntitle X`. Both are valid Mermaid syntax accepted by mermaid-js.
