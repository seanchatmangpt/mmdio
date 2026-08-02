# Comprehensive Specification Mining & E2E Testing Inventory: `mmdio`

**Module**: `spec_miner_e2e_m1`  
**Target Project**: `mmdio` (Mermaid Diagrams as Universal IO)  
**Date**: 2026-08-01  
**Architecture Axiom**: $A = \mu(O)$ (Codebase AST models, token enums, parser registries, and render dispatchers precipitate directly from RDF ontologies via ggen without shadow duplication).

---

## 1. Executive Summary & Architectural Axiom

`mmdio` is designed to provide pure Python AST models, parsers, and renderers for Mermaid diagram types. The architecture follows the core axiom **$A = \mu(O)$**:
- **$O$ (Ontology)**: Single source of truth in `src/mmdio/engine/registry.ttl` (upstream Mermaid registry) layered with `packs/mmdio-pack/ontology.ttl` (Python metadata, field-shape matrix, and enums).
- **$\mu$ (Precipitation Function)**: `ggen` CLI (version 26.8.2) evaluating 10 SPARQL law gates (`packs/mmdio-pack/gates/*.rq`) and Tera templates (`packs/mmdio-pack/templates/*.tmpl`).
- **$A$ (Artifacts/Codebase)**: Derived first-class Python modules written directly to `src/mmdio/engine/` (`models.py`, `enums.py`, `parser_registry.py`, `render_dispatch.py`, `render.py`, `parser.py`, `schemas.py`, `fixtures.py`, `supported.py`, `detect_patterns.py`).

### Key Mandates
1. **R1. First-Class ggen Code Derivation**: Zero hand-written shadow modules (`_generated_*` or legacy shadow types in `src/mmdio/engine/types/`). All code is emitted into first-class Python module locations.
2. **R2. Pure Python Conformance & Zero Runtime Node Dependencies**: The shipped package is pure Python. Node.js is strictly a development/testing oracle dependency.
3. **R3. Test Oracle Roundtrip Validation**: Pytest harness validates rendered Mermaid text against Node.js `mermaid.detectType()` pinned to `mermaid@11.16.0`.

---

## 2. Diagram Types & AST Models Inventory

Across `registry.ttl` and `ontology.ttl`, 15 diagram types are supported in `mmdio` (11 core types + 4 batch 1 types). In addition, upstream `registry.ttl` defines additional diagram types.

### 2.1 Supported Diagram Types Matrix

| # | Diagram Type | `pythonInternalId` | `diagramId` | Discriminator | Top-Level Model Class | Diagram Header Keyword | Grammar File | Detect Pattern |
|---|--------------|-------------------|-------------|---------------|----------------------|-----------------------|--------------|----------------|
| 1 | Flowchart | `flowchart` | `flowchart` | `"flowchart"` | `FlowchartDiagram` | `flowchart` | `flowchart.lark` | `^\s*flowchart\b` |
| 2 | Sequence | `sequence` | `sequence` | `"sequence"` | `SequenceDiagram` | `sequenceDiagram` | `sequence.lark` | `^\s*sequencediagram\b` |
| 3 | Class Diagram | `class` | `classDiagram` | `"class"` | `ClassDiagram` | `classDiagram` | `class_diagram.lark` | `^\s*classdiagram\b` |
| 4 | State Diagram | `state` | `stateDiagram` | `"state"` | `StateDiagram` | `stateDiagram` | `state.lark` | `^\s*statediagram(-v2)?\b` |
| 5 | ER Diagram | `er` | `er` | `"er"` | `ERDiagram` | `erDiagram` | `er.lark` | `^\s*erdiagram\b` |
| 6 | Gantt Chart | `gantt` | `gantt` | `"gantt"` | `GanttChart` | `gantt` | `gantt.lark` | `^\s*gantt\b` |
| 7 | Pie Chart | `pie` | `pie` | `"pie"` | `PieChart` | `pie` | `pie.lark` | `^\s*pie\s+` |
| 8 | Git Graph | `git` | `gitGraph` | `"git"` | `GitGraph` | `gitGraph` | `git.lark` | `^\s*gitgraph\b` |
| 9 | C4 Diagram | `c4` | `c4` | `"c4"` | `C4Diagram` | `C4Context` / `C4Container` | `c4.lark` | `^\s*c4(context\|diagram)\b` |
| 10| Mindmap | `mindmap` | `mindmap` | `"mindmap"` | `Mindmap` | `mindmap` | `mindmap.lark` | `^\s*mindmap\b` |
| 11| Sankey Diagram | `sankey` | `sankey` | `"sankey"` | `SankeyDiagram` | `sankey-beta` | `sankey.lark` | `^\s*sankey-beta\b` |
| 12| Kanban Board | `kanban` | `kanban` | `"kanban"` | `KanbanDiagram` | `kanban` | `kanban.lark` | `^\s*kanban\b` |
| 13| Timeline | `timeline` | `timeline` | `"timeline"` | `TimelineDiagram` | `timeline` | `timeline.lark` | `^\s*timeline\b` |
| 14| XY Chart | `xychart` | `xychart` | `"xychart"` | `XYChartDiagram` | `xychart-beta` | `xychart.lark` | `^\s*xychart(-beta)?\b` |
| 15| Block Diagram | `block` | `block` | `"block"` | `BlockDiagram` | `block-beta` | `block.lark` | `^\s*block(-beta)?\b` |

*Note on Mismatched IDs*: For backward compatibility, `pythonInternalId` differs from upstream `diagramId` for three types:
- `classDiagram` -> `pythonInternalId`: `"class"`
- `stateDiagram` -> `pythonInternalId`: `"state"`
- `gitGraph` -> `pythonInternalId`: `"git"`

---

## 3. Token Enums & Python Runtime Requirements

### 3.1 Token Enums Specification

All token enums are derived from `mer:PythonEnum` and `mer:EnumMember` subjects in `ontology.ttl`.

| Enum Class | Member Name | Member Value | Diagram Type | Notes |
|------------|-------------|--------------|--------------|-------|
| `NodeShape` | `RECTANGLE` | `"rectangle"` | Flowchart | Default shape |
| | `CIRCLE` | `"circle"` | Flowchart | |
| | `ELLIPSE` | `"ellipse"` | Flowchart | |
| | `DIAMOND` | `"diamond"` | Flowchart | Decision node |
| | `HEXAGON` | `"hexagon"` | Flowchart | |
| | `PARALLELOGRAM` | `"parallelogram"` | Flowchart | |
| | `TRAPEZOID` | `"trapezoid"` | Flowchart | |
| | `DOCUMENT` | `"document"` | Flowchart | |
| | `CYLINDER` | `"cylinder"` | Flowchart | Database |
| | `SUBROUTINE` | `"subroutine"` | Flowchart | |
| `MessageType` | `SYNC` | `"sync"` | Sequence | Solid line, filled arrow |
| | `ASYNC` | `"async"` | Sequence | Dashed line, open arrow |
| | `RETURN` | `"return"` | Sequence | Return arrow |
| | `AUTONUMBER` | `"autonumber"` | Sequence | Auto-numbered |
| `RelationshipType` | `INHERITANCE` | `"inheritance"` | Class | `--^` |
| | `REALIZATION` | `"realization"` | Class | `--\|>` |
| | `COMPOSITION` | `"composition"` | Class | `--*` |
| | `AGGREGATION` | `"aggregation"` | Class | `--o` |
| | `ASSOCIATION` | `"association"` | Class | `-->` |
| | `DEPENDENCY` | `"dependency"` | Class | `..>` |
| | `LINK` | `"link"` | Class | `--` |
| `CardinityType` | `ONE_TO_ONE` | `"one_to_one"` | ER | `\|o--o\|` |
| | `ONE_TO_MANY` | `"one_to_many"` | ER | `\|o--}\|` |
| | `MANY_TO_ONE` | `"many_to_one"` | ER | `}\|--o\|` |
| | `MANY_TO_MANY` | `"many_to_many"` | ER | `}o--o{` |
| | `MANY_TO_MANY_MARKED` | `"many_to_many_marked"` | ER | `}\|--{\|` |
| `TaskStatus` | `ACTIVE` | `"active"` | Gantt | |
| | `DONE` | `"done"` | Gantt | |
| | `MILESTONE` | `"milestone"` | Gantt | |
| | `CRIT` | `"crit"` | Gantt | Critical path |
| | `ACTIVE_CRIT` | `"active_crit"` | Gantt | |
| | `DONE_CRIT` | `"done_crit"` | Gantt | |
| `C4Level` | `C1` | `"C1"` | C4 | System Context |
| | `C2` | `"C2"` | C4 | Container |
| | `C3` | `"C3"` | C4 | Component |
| | `C4` | `"C4"` | C4 | Code |
| `ParticipantType` | `ACTOR` | `"actor"` | Sequence | |
| | `PARTICIPANT` | `"participant"` | Sequence | |
| | `AUTONUMBER` | `"autonumber"` | Sequence | |

### 3.2 Python Runtime Requirement: `enum.StrEnum` vs `(str, Enum)`
- **Behavioral Difference**: In Python 3.11+, using `class MyEnum(str, Enum)` causes `f"{MyEnum.FOO}"` or `str(MyEnum.FOO)` to produce `"MyEnum.FOO"` instead of `"foo"`.
- **Mandate**: All enum classes generated by ggen MUST inherit from `enum.StrEnum` (Python 3.11+ standard library). This guarantees direct f-string rendering produces bare string values (`"foo"`) without requiring explicit `.value` calls.

---

## 4. SPARQL Law Gates Specification

The 10 SPARQL law gates in `packs/mmdio-pack/gates/` enforce strict ontology integrity during `ggen sync run`.

| Gate # | File Name | Target Entity / Subject | Rule & Validation Logic | Error Condition if Violated |
|--------|-----------|------------------------|-------------------------|-----------------------------|
| **010** | `010_python_support_complete.rq` | `mer:DiagramType` with `mer:pythonSupport true` | Every supported diagram type must have all 9 required predicates: `pythonInternalId`, `pythonModelModule`, `pythonModelClass`, `pythonTransformerModule`, `pythonTransformerClass`, `pythonRenderModule`, `pythonRenderFunction`, `grammarFile`, `detectPattern`. | Returns missing predicate name and diagram type. |
| **020** | `020_no_duplicate_internal_id.rq` | `mer:DiagramType` | `mer:pythonInternalId` must be globally unique across all supported diagram types. | Returns duplicate `internalId` and count (>1). |
| **030** | `030_field_shape_closed_vocabulary.rq` | `mer:PythonField` | `mer:fieldKind` must belong to the closed vocabulary: `scalar-required`, `scalar-optional`, `list`, `nested-ref`, `union-type`, `literal-default`, `enum`. | Returns field name and invalid `fieldKind`. |
| **040** | `040_field_order_gapless.rq` | `mer:PythonModel` | `mer:fieldOrder` integers for a model must start at 1 and be strictly contiguous/gapless up to total field count. | Returns model name, min order, max order, and field count mismatch. |
| **050** | `050_render_format_present_for_list_fields.rq` | `mer:PythonField` | Every field of kind `list` must provide a non-empty `mer:fieldRenderFormat` f-string snippet. | Returns field URI and field name missing format string. |
| **060** | `060_render_nesting_depth_limit.rq` | `mer:PythonModel` & `mer:PythonField` | Nesting of `list` fields from top-level model cannot exceed 2 levels (`f1` list -> `f2` list -> `f3` list is forbidden). | Returns top model and violating 3-level field chain (`f1`, `f2`, `f3`). |
| **070** | `070_enum_class_exists_for_enum_fields.rq` | `mer:PythonField` | Every field of kind `enum` must specify a `mer:fieldPyType` that maps to a defined `mer:PythonEnum` with >=1 `mer:enumMember`. | Returns field URI and missing enum class name. |
| **080** | `080_scalar_example_value_present.rq` | `mer:PythonField` | Every field of kind `scalar-required` or `enum` must provide a non-empty `mer:fieldExampleValue`. | Returns field URI, field name, and kind lacking example value. |
| **090** | `090_field_pytype_resolves.rq` | `mer:PythonField` | Every field of kind `list` or `nested-ref` must specify a `mer:fieldPyType` matching a valid `mer:PythonModel` `className`. | Returns field URI, field name, and unresolvable `fieldPyType`. |
| **100** | `100_classname_globally_unique.rq` | `mer:PythonModel` | `mer:className` must be globally unique across all models (prevents class redefinition collisions in unified namespace). | Returns duplicate `className` and collision count (>1). |

---

## 5. Node Mermaid Oracle Interface Specification

The development and testing harness validates generated Mermaid strings against an upstream Node.js oracle.

### 5.1 Harness File & Dependencies
- **Script Location**: `tests/oracle/verify_mermaid.mjs`
- **Package Configuration**: `tests/oracle/package.json`
- **Pinned Dependency**: `mermaid@11.16.0`

### 5.2 Oracle Execution Protocol
- **Command Line**: `node tests/oracle/verify_mermaid.mjs <path_to_mmd_file>`
- **Initialization Settings**:
  ```javascript
  await mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'strict',
    htmlLabels: false,
    flowchart: { defaultRenderer: 'dagre-wrapper' },
    architecture: { randomize: false }
  });
  ```
- **Verification Logic**: Uses `mermaid.detectType(source)` to parse and validate syntax without DOM rendering dependencies.
- **Exit Codes & Output**:
  - **Exit Code 0**: `SUCCESS: Detected diagram type: <detected_type>`
  - **Exit Code 1**: `PARSE_ERROR: <error_message>`

---

## 6. Error Conditions, Boundary Limits & Known Gaps

1. **Mindmap Unbounded Self-Reference Gap**:
   - `MindmapNode` is recursive (`children: List["MindmapNode"]`).
   - Gate 060 limits `list` nesting depth to 2 levels.
   - *Impact*: Mindmap cannot be fully auto-generated by current Tera templates (`render-body` fixed unroll). Mindmap remains hand-written or requires a `recursive-ref` field kind.
2. **Block Connection Label Branching Gap**:
   - In hand-written `block_render.py`, connection rendering branches on whether `label` is set (`source --> target` vs `source -- label --> target`).
   - The Tera template format vocabulary assumes 1 fixed f-string per list field.
   - *Impact*: Auto-generated `render_block()` emits unlabeled connection format only.
3. **Sankey Comma Escaping Gap**:
   - Hand-written `render_sankey()` sanitizes commas (`flow.source.replace(',', '')`) to avoid CSV syntax corruption.
   - Render format template has no string sanitization function.
   - *Impact*: Slices/flows containing literal commas corrupt Sankey syntax if not escaped.
4. **Pytest Warning Escalation**:
   - `pyproject.toml` sets `filterwarnings = ["error", "ignore::DeprecationWarning"]`.
   - Any unhandled warning during `uv run pytest` escalates to a test error.

---

## 7. Features Discovered & Edge Cases Tables

## Features Discovered
| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Architecture | $A = \mu(O)$ Precipitation | Deriving Python modules directly from RDF facts using ggen CLI 26.8.2 | `registry.ttl`, `ontology.ttl`, `templates/*.tmpl` | First-class Python files in `src/mmdio/engine/` | Gate failure on invalid RDF; template rendering error | `PROJECT.md`, `ORIGINAL_REQUEST.md`, `pack.toml` |
| 2 | Code Generation | Unified Discriminated AST Union | `MermaidDiagram` discriminated union combining all top-level AST models | Pydantic model definitions | `MermaidDiagram` Annotated Union with `Field(discriminator='type')` | Pydantic ValidationError on mismatched discriminator | `generated_models_union.py.tmpl` |
| 3 | Code Generation | StrEnum Token Generation | Generating Python 3.11+ `StrEnum` classes for diagram tokens | `mer:PythonEnum` facts in `ontology.ttl` | `enums.py` / `_generated_enums.py` | Import failure if member missing | `generated_enums.py.tmpl`, `ontology.ttl` |
| 4 | Detection | Regex Pattern Detection | Detecting diagram type from input Mermaid text string | Raw Mermaid text string | `pythonInternalId` string (e.g. `"flowchart"`, `"sequence"`) | Fallback to `"flowchart"` on unrecognized input | `src/mmdio/detect.py`, `generated_detect_patterns.py.tmpl` |
| 5 | Parsing | Lark Grammar Parsing & Transformation | Parsing Mermaid text into Pydantic AST models via Lark grammars | Mermaid text string | Pydantic AST model instance | `LarkError` / `UnexpectedToken` / `UnexpectedCharacters` | `src/mmdio/engine/parser.py`, `grammars/*.lark` |
| 6 | Rendering | Type-Dispatched Diagram Rendering | Converting Pydantic AST model into valid Mermaid syntax text | Pydantic AST model instance | Mermaid text string | `ValueError` for unsupported diagram model | `src/mmdio/engine/render.py`, `generated_render_dispatch.py.tmpl` |
| 7 | Quality Gate | 10 SPARQL Law Gates Verification | Pre-generation validation of ontology structure and consistency | SPARQL queries in `gates/*.rq` | Gate pass/fail status report | ggen sync run exit code 1 on query match | `packs/mmdio-pack/gates/*.rq` |
| 8 | Oracle Verification | Node.js Mermaid Oracle Harness | Validating rendered Mermaid strings with Node `mermaid.detectType()` | Temporary `.mmd` file path | Exit code 0 + success message | Exit code 1 + `PARSE_ERROR` output | `tests/oracle/verify_mermaid.mjs`, `test_oracle_roundtrip.py` |
| 9 | Fixture Generation | Ontology-Driven Fixtures | Auto-generating example AST instances for test fixtures | `mer:fieldExampleValue` in `ontology.ttl` | Example AST model instances | SyntaxError if example value incompatible with type | `generated_fixtures.py.tmpl`, `test_oracle_generated.py` |
| 10 | Schema Generation | JSON Schema Export | Exporting Pydantic AST models to JSON Schema format | `mer:PythonModel` facts | JSON Schema dictionary/file | Pydantic schema generation error | `generated_schemas.py.tmpl` |

## Edge Cases
| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Detection | Empty string or whitespace-only input | Falls back to `"flowchart"` default without raising error |
| 2 | Detection | Mixed-case headers (e.g. `SeQuEnCeDiAgRaM`) | Case-insensitive regex matches `"sequence"` correctly |
| 3 | Rendering | List field containing empty list `[]` | Render format skips body, outputs diagram header only |
| 4 | Enums | `str, Enum` vs `StrEnum` in f-strings on Python 3.13 | `str, Enum` formats as `"NodeShape.RECTANGLE"`; `StrEnum` formats as `"rectangle"` |
| 5 | Nesting | 3-level list nesting in ontology | Caught by Gate 060 (`060_render_nesting_depth_limit.rq`), preventing ggen sync |
| 6 | Enums | Enum field with no members in ontology | Caught by Gate 070 (`070_enum_class_exists_for_enum_fields.rq`) |
| 7 | Field Order | Field order starting at 0 or skipping a number | Caught by Gate 040 (`040_field_order_gapless.rq`) |
| 8 | Parsing | Unrecognized shape or arrow syntax in Lark | Raises Lark `UnexpectedToken` / `ParseError` |
| 9 | Oracle Harness | Syntax error in rendered Mermaid output | Node oracle returns exit code 1 with `PARSE_ERROR`, failing pytest assertion |
| 10 | Model Union | ClassName collision across two diagram types | Caught by Gate 100 (`100_classname_globally_unique.rq`), refusing code generation |

---

## 8. 4-Tier E2E Testing Inventory & Methodology

To ensure total test coverage across all features, specifications, and edge cases, we establish a **4-Tier E2E Test Inventory** containing **95 comprehensive test specifications**.

---

### Tier 1: Feature Coverage Inventory (35 Test Specs)
*Goal: >=5 test cases for each core project requirement and feature (R1, R2, R3, F1, F2, F3, F4).*

| Test ID | Target Feature | Description / Scope | Test Inputs | Expected Outputs / Assertion |
|---------|---------------|---------------------|-------------|------------------------------|
| `T1-R1-01` | R1 (ggen Derivation) | Verify first-class `models.py` imports without legacy `_generated_*` imports | Python import statements | All models imported cleanly from `mmdio.engine.models` |
| `T1-R1-02` | R1 (ggen Derivation) | Verify `enums.py` contains all 7 `StrEnum` classes | `mmdio.engine.enums` inspection | `NodeShape`, `MessageType`, `RelationshipType`, `CardinityType`, `TaskStatus`, `C4Level`, `ParticipantType` exist |
| `T1-R1-03` | R1 (ggen Derivation) | Verify `parser_registry.py` maps all 15 diagram types | Registry dictionary inspection | 15 parser transformers registered |
| `T1-R1-04` | R1 (ggen Derivation) | Verify `render_dispatch.py` dispatches to all 15 render functions | Dispatcher function call | Renders correct Mermaid text for each model type |
| `T1-R1-05` | R1 (ggen Derivation) | Verify complete elimination of `src/mmdio/engine/types/` legacy folder | Directory scan | Directory does not exist or contains no shadow models |
| `T1-R2-01` | R2 (Pure Python) | Verify mmdio package runs parser without Node.js | Lark parser on flowchart text | Returns `FlowchartDiagram` AST without subprocess calls |
| `T1-R2-02` | R2 (Pure Python) | Verify mmdio renderer runs in pure Python | `FlowchartDiagram` AST | Returns Mermaid text string without subprocess calls |
| `T1-R2-03` | R2 (Pure Python) | Verify all 10 SPARQL gates pass cleanly during ggen sync | `ggen sync run` execution | Exit code 0, 100% gate pass rate |
| `T1-R2-04` | R2 (Pure Python) | Verify zero non-standard runtime dependencies in `pyproject.toml` | Dependencies inspection | Pure Python dependencies (`lark`, `pydantic`, `rdflib`) |
| `T1-R2-05` | R2 (Pure Python) | Verify CLI `mmdio detect` operates in pure Python | CLI invocation with input file | Output matches detected type, exit code 0 |
| `T1-R3-01` | R3 (Oracle Validation)| Oracle validation for Flowchart diagram | Generated `FlowchartDiagram` | Node oracle returns exit code 0, detected: `flowchart` |
| `T1-R3-02` | R3 (Oracle Validation)| Oracle validation for Sequence diagram | Generated `SequenceDiagram` | Node oracle returns exit code 0, detected: `sequence` |
| `T1-R3-03` | R3 (Oracle Validation)| Oracle validation for Class diagram | Generated `ClassDiagram` | Node oracle returns exit code 0, detected: `classDiagram` |
| `T1-R3-04` | R3 (Oracle Validation)| Oracle validation for State diagram | Generated `StateDiagram` | Node oracle returns exit code 0, detected: `stateDiagram` |
| `T1-R3-05` | R3 (Oracle Validation)| Oracle validation for ER diagram | Generated `ERDiagram` | Node oracle returns exit code 0, detected: `erDiagram` |
| `T1-F1-01` | F1 (Ontology Expansion)| Verify `ontology.ttl` contains all 15 model definitions | SPARQL query on `ontology.ttl` | 15 `mer:DiagramType` subjects with `mer:pythonSupport true` |
| `T1-F1-02` | F1 (Ontology Expansion)| Verify `pack.toml` emits to `src/mmdio/engine/` paths | `pack.toml` file parsing | All 12 template output targets land in `src/mmdio/engine/` |
| `T1-F1-03` | F1 (Ontology Expansion)| Verify Tera templates generate gapless field orders | ggen evaluation | Gate 040 passes with zero violations |
| `T1-F1-04` | F1 (Ontology Expansion)| Verify `generated_fixtures.py` builds all 15 diagram fixtures | Module import & execution | 15 fixture builder functions return valid AST instances |
| `T1-F1-05` | F1 (Ontology Expansion)| Verify `generated_schemas.py` exports JSON Schema for all models | Module import & execution | Valid JSON schema dictionary emitted |
| `T1-F2-01` | F2 (Shadow Cleanup)| Verify absence of `_generated_` imports in `src/mmdio/api.py` | AST/Grep search | Zero `_generated_` imports found |
| `T1-F2-02` | F2 (Shadow Cleanup)| Verify absence of `_generated_` imports in `src/mmdio/cli.py` | AST/Grep search | Zero `_generated_` imports found |
| `T1-F2-03` | F2 (Shadow Cleanup)| Verify top-level `MermaidDiagram` discriminated union import | `from mmdio.engine.models import MermaidDiagram` | Imports successfully, contains all 15 types |
| `T1-F2-04` | F2 (Shadow Cleanup)| Verify `detect_patterns.py` precipitation to first-class engine | File existence & import | `src/mmdio/engine/detect_patterns.py` exists and imports |
| `T1-F2-05` | F2 (Shadow Cleanup)| Verify `supported.py` exports `SUPPORTED_DIAGRAM_TYPES` set | Module import | Set contains all 15 internal diagram IDs |
| `T1-F3-01` | F3 (Pytest Harness)| Run full pytest suite with zero warnings | `uv run pytest` | 100% pass rate, exit code 0, 0 warning errors |
| `T1-F3-02` | F3 (Pytest Harness)| Verify `pyproject.toml` filterwarnings configuration | `pyproject.toml` inspection | `filterwarnings = ["error", "ignore::DeprecationWarning"]` |
| `T1-F3-03` | F3 (Pytest Harness)| Verify `test_api.py` passes without Starlette warnings | `pytest tests/test_api.py` | Pass without raising warning exceptions |
| `T1-F3-04` | F3 (Pytest Harness)| Verify `test_cli.py` test suite execution | `pytest tests/test_cli.py` | Pass with exit code 0 |
| `T1-F3-05` | F3 (Pytest Harness)| Verify `test_oracle_generated.py` executes all 15 generated tests | `pytest tests/test_oracle_generated.py` | 15 test classes execute and pass against oracle |
| `T1-F4-01` | F4 (Final E2E)| E2E roundtrip parsing & rendering for Kanban | Kanban Mermaid text | Parse AST -> Render text -> Oracle valid |
| `T1-F4-02` | F4 (Final E2E)| E2E roundtrip parsing & rendering for Timeline | Timeline Mermaid text | Parse AST -> Render text -> Oracle valid |
| `T1-F4-03` | F4 (Final E2E)| E2E roundtrip parsing & rendering for XYChart | XYChart Mermaid text | Parse AST -> Render text -> Oracle valid |
| `T1-F4-04` | F4 (Final E2E)| E2E roundtrip parsing & rendering for Block | Block Mermaid text | Parse AST -> Render text -> Oracle valid |
| `T1-F4-05` | F4 (Final E2E)| Full test suite pass across all 4 tiers | `uv run pytest` | All test modules green |

---

### Tier 2: Boundary & Corner Cases Inventory (35 Test Specs)
*Goal: >=5 boundary/edge test cases per feature (invalid syntax, empty inputs, edge shape limits, deprecation warnings).*

| Test ID | Feature Area | Corner Case Description | Test Input | Expected Behavior |
|---------|--------------|-------------------------|------------|-------------------|
| `T2-SYN-01` | Syntax Parsing | Empty string input to `detect_diagram_type` | `""` | Returns `"flowchart"` default without error |
| `T2-SYN-02` | Syntax Parsing | Whitespace-only string input | `"\n  \t  \n"` | Returns `"flowchart"` default |
| `T2-SYN-03` | Syntax Parsing | Malformed Mermaid syntax header | `"invalid_header_xyz\nfoo"` | `detect_diagram_type` returns `"flowchart"`; Lark parser raises `ParseError` |
| `T2-SYN-04` | Syntax Parsing | Truncated diagram syntax | `"flowchart TD\n  A -->"` | Lark parser raises `UnexpectedToken` |
| `T2-SYN-05` | Syntax Parsing | Unmatched brackets in node labels | `"flowchart TD\n  A[Unmatched label"` | Lark parser raises `UnexpectedToken` |
| `T2-AST-01` | AST Limits | Flowchart with zero nodes and zero edges | `FlowchartDiagram(direction="TB", nodes=[], edges=[])` | Renders `"flowchart TB\n"`, validated by oracle |
| `T2-AST-02` | AST Limits | Sequence diagram with 100 participants | `SequenceDiagram` with 100 `SequenceParticipant` items | Renders valid sequence diagram, passes oracle |
| `T2-AST-03` | AST Limits | Pie chart slice with 0.0 value | `PieSlice(label="Zero", value=0.0)` | Renders `"    \"Zero\" : 0.0"`, passes oracle |
| `T2-AST-04` | AST Limits | Special characters in node labels (quotes, newlines) | `FlowchartNode(id="A", label='Line 1\n"Quoted"')` | Properly escaped in rendered output |
| `T2-AST-05` | AST Limits | Non-ASCII / Unicode characters in labels | Node labels with Japanese/Emoji (`"処理 (Process) 🚀"`) | Correctly encoded UTF-8 output, passes oracle |
| `T2-ENUM-01` | Enums | `StrEnum` direct f-string formatting | `f"{NodeShape.RECTANGLE}"` | Outputs `"rectangle"`, NOT `"NodeShape.RECTANGLE"` |
| `T2-ENUM-02` | Enums | Invalid enum string instantiation | `NodeShape("invalid_shape")` | Raises `ValueError` |
| `T2-ENUM-03` | Enums | Comparison between `StrEnum` and string literal | `NodeShape.RECTANGLE == "rectangle"` | Evaluates to `True` |
| `T2-ENUM-04` | Enums | All enum members have non-empty example values | Gate 080 check on all enum fields | Gate 080 returns 0 violations |
| `T2-ENUM-05` | Enums | Enum class resolution check | Gate 070 check on all enum fields | Gate 070 returns 0 violations |
| `T2-GATE-01` | Law Gates | Violation of Gate 010 (missing detectPattern) | Ontology with `pythonSupport true` lacking `detectPattern` | Gate 010 query returns violating diagram type |
| `T2-GATE-02` | Law Gates | Violation of Gate 020 (duplicate internalId) | Ontology with two types using internalId `"flowchart"` | Gate 020 query returns `"flowchart"` with count 2 |
| `T2-GATE-03` | Law Gates | Violation of Gate 030 (invalid fieldKind) | Ontology with `fieldKind "custom-kind"` | Gate 030 query returns violating field |
| `T2-GATE-04` | Law Gates | Violation of Gate 040 (gap in fieldOrder) | Model with fields ordered 1, 3 (missing 2) | Gate 040 query returns violating model |
| `T2-GATE-05` | Law Gates | Violation of Gate 060 (3-level list nesting) | Model chain with 3 nested list fields | Gate 060 query returns violating chain |
| `T2-ORCL-01` | Oracle | Non-existent file path passed to oracle | `node verify_mermaid.mjs /path/does/not/exist.mmd` | Node oracle exits code 1 with file read error |
| `T2-ORCL-02` | Oracle | Invalid Mermaid syntax file passed to oracle | `.mmd` file with `"invalid syntax content"` | Node oracle exits code 1 with `PARSE_ERROR` |
| `T2-ORCL-03` | Oracle | Temporary file cleanup verification | Call `validate_mermaid_source(src)` | Temp `.mmd` file deleted after function returns |
| `T2-ORCL-04` | Oracle | Large diagram source string (1MB) | Large generated flowchart | Oracle processes within 10s timeout, exits code 0 |
| `T2-ORCL-05` | Oracle | Concurrent oracle process execution | `pytest-xdist` running multiple oracle tests in parallel | No temporary file collisions or lock race conditions |
| `T2-WARN-01` | Warnings | Starlette deprecation warning filter test | Import `mmdio.api` and trigger request | Warning ignored or handled, pytest passes |
| `T2-WARN-02` | Warnings | Pydantic V2 deprecation warning check | Instantiate models with `Config` | No `PydanticDeprecatedSince20` warning emitted |
| `T2-WARN-03` | Warnings | Lark regex escape deprecation check | Parse complex grammars | No `SyntaxWarning` / `DeprecationWarning` from Lark |
| `T2-WARN-04` | Warnings | Unused import warning check | Run `ruff check` on engine modules | 0 unused import warnings |
| `T2-WARN-05` | Warnings | Missing docstring warning check | Run `ruff check` on engine public API | 0 missing docstring warnings |

---

### Tier 3: Cross-Feature Pairwise Combinations Inventory (15 Test Specs)
*Goal: Validate interactions between diagram parsing, rendering, gate validation, and oracle verification.*

| Test ID | Component A | Component B | Combination Scenario | Expected Result |
|---------|-------------|-------------|----------------------|-----------------|
| `T3-PAIR-01` | Pattern Detector | Lark Parser | Detect diagram type from raw text, then dispatch to matching Lark parser | Correct AST model instantiated for all 15 types |
| `T3-PAIR-02` | Lark Parser | Render Dispatcher | Parse raw Mermaid text to AST, then pass AST to `render_diagram()` | Rendered Mermaid text string produced |
| `T3-PAIR-03` | Render Dispatcher | Node Oracle | Render AST model to text string, then pass text to Node oracle | Node oracle validates syntax, exits code 0 |
| `T3-PAIR-04` | Ontology Fixtures | Render Dispatcher | Load auto-generated fixture, pass to `render_diagram()` | Rendered string matches expected diagram header |
| `T3-PAIR-05` | Ontology Fixtures | Node Oracle | Load auto-generated fixture, render, and validate with oracle | All 15 ontology fixtures pass oracle validation |
| `T3-PAIR-06` | Pydantic Discriminator | Parser Registry | Parse JSON object with `type: "kanban"` into `MermaidDiagram` union | Instantiates `KanbanDiagram` AST model |
| `T3-PAIR-07` | StrEnum Token | Render Dispatcher | Set `FlowchartNode.shape = NodeShape.DIAMOND`, render diagram | Emits `{_r1.id}{_r1.shape}` as `A{Start}` in Mermaid text |
| `T3-PAIR-08` | JSON Schema | Pydantic Model | Export JSON schema from `models.py`, validate model instance against schema | AST model instance validates against exported schema |
| `T3-PAIR-09` | CLI Command | Pattern Detector | Invoke `mmdio detect sample.mmd` via CLI | CLI prints detected type name, exit code 0 |
| `T3-PAIR-10` | REST API | Render Dispatcher | Post AST JSON payload to `/render` endpoint | API returns rendered Mermaid text string |
| `T3-PAIR-11` | SPARQL Gate 010 | Parser Registry | Run Gate 010, verify all pass types are registered in `parser_registry.py` | 1-to-1 match between gate pass types and registered parsers |
| `T3-PAIR-12` | SPARQL Gate 050 | Render Dispatcher | Verify all `list` fields passing Gate 050 render formatted lines | Renders expected list element lines |
| `T3-PAIR-13` | SPARQL Gate 080 | Fixture Builder | Verify fields passing Gate 080 seed fixture builder correctly | Fixtures contain valid example values for required fields |
| `T3-PAIR-14` | Lark Transformer | Pydantic Model | Transform Lark parse tree into Pydantic model with strict validation | Model fields match parsed tree tokens |
| `T3-PAIR-15` | Node Oracle | Pytest Harness | Run full `test_oracle_roundtrip.py` via `pytest -n auto` | Parallel execution succeeds across all CPU cores |

---

### Tier 4: Real-World Scenarios Inventory (10 Test Specs)
*Goal: Complete end-to-end workflow diagram generation, AST roundtrip, gate validation, and oracle verification.*

| Test ID | Real-World Scenario | Description & Workflow Steps | Input Payload | Verification Criteria |
|---------|---------------------|------------------------------|---------------|-----------------------|
| `T4-E2E-01` | Microservice Architecture C4 Diagram | 1. Parse C4 Mermaid text -> `C4Diagram` AST.<br>2. Modify AST (add database container).<br>3. Render AST to Mermaid text.<br>4. Validate with Node oracle. | C4 System Context text with 5 elements, 4 relationships | Oracle detects `c4Context`, AST roundtrip preserves all elements |
| `T4-E2E-02` | E-Commerce Order Processing Sequence | 1. Construct `SequenceDiagram` AST (Customer, API, Payment, DB).<br>2. Render diagram.<br>3. Parse rendered text back to AST.<br>4. Validate rendered text with oracle. | Sequence diagram with 6 sync/async messages, autonumber | Oracle detects `sequence`, AST equality verified |
| `T4-E2E-03` | Database Schema Migration ER Diagram | 1. Parse ER diagram text with 8 entities & foreign keys.<br>2. Export AST to JSON Schema.<br>3. Render back to Mermaid text.<br>4. Validate with oracle. | ER text with attributes, primary keys, cardinalities | Oracle detects `erDiagram`, JSON schema valid |
| `T4-E2E-04` | Sprint Planning Kanban Board | 1. Generate `KanbanDiagram` AST from ontology fixture.<br>2. Move card from "To Do" to "In Progress" section.<br>3. Render updated AST.<br>4. Validate with oracle. | Kanban diagram with 4 sections, 12 cards | Oracle detects `kanban`, card moved in rendered text |
| `T4-E2E-05` | CI/CD Release Git Graph | 1. Construct `GitGraph` AST (main, develop, feature branches, commits, tags).<br>2. Render diagram.<br>3. Validate with oracle. | GitGraph with 3 branches, 8 commits, 2 tags | Oracle detects `gitGraph`, syntax valid |
| `T4-E2E-06` | Quarterly Project Roadmap Timeline | 1. Parse Timeline Mermaid text.<br>2. Add Q4 milestone event.<br>3. Render AST to text.<br>4. Validate with oracle. | Timeline text with 4 time sections and events | Oracle detects `timeline`, new event present |
| `T4-E2E-07` | Server Metrics XY Chart | 1. Construct `XYChartDiagram` AST (bar-series CPU, line-series Memory).<br>2. Render diagram.<br>3. Validate with oracle. | XYChart with x-axis categories, 2 data series | Oracle detects `xychart`, syntax valid |
| `T4-E2E-08` | Kubernetes Cluster Infrastructure Block | 1. Construct `BlockDiagram` AST with columns=4, 8 blocks, 6 connections.<br>2. Render diagram.<br>3. Validate with oracle. | Block diagram with grid layout & connections | Oracle detects `block`, syntax valid |
| `T4-E2E-09` | Complete ggen Sync & Test Pipeline | 1. Execute `ggen sync run`.<br>2. Assert 10 SPARQL law gates pass.<br>3. Run `uv run pytest`.<br>4. Assert 100% test pass rate. | Repository workspace state | Exit code 0 for ggen sync and pytest |
| `T4-E2E-10` | REST API Roundtrip Render Service | 1. Start FastAPI app.<br>2. POST raw Mermaid text to `/detect` and `/render`.<br>3. Receive AST JSON and rendered Mermaid string.<br>4. Validate rendered text with oracle. | Multi-diagram payload (Flowchart, Sequence, Pie) | HTTP 200 OK, valid rendered Mermaid output |

---

## 9. Verification & Handoff Summary

The specification analysis is complete. The handoff report is documented in `/Users/sac/mmdio/.agents/spec_miner_e2e_m1/handoff.md`.
