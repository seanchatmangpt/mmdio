# End-to-End Test Infrastructure: `mmdio`

## 1. Test Philosophy & Principles

The testing architecture for `mmdio` follows an **opaque-box, requirement-driven test philosophy**.
- **Opaque-Box Verification**: Tests validate external behavior and contract fulfillment rather than internal implementation details. High-level AST construction, diagram rendering, and diagram parsing are tested against standard inputs and observable outputs.
- **Requirement-Driven**: Every test case directly traces back to project requirements (R1, R2, R3) and features (F1, F2, F3, F4) defined in `PROJECT.md` and `ORIGINAL_REQUEST.md`.
- **Zero Shadow Dependencies**: Tests interact strictly with first-class precipitated derived code under `src/mmdio/engine/` (`models.py`, `parser.py`, `render.py`, `enums.py`, etc.), ensuring complete elimination of legacy shadow modules.
- **Upstream Oracle Validation**: All rendered Mermaid diagrams are validated against the official Node.js `mermaid` parser (`mermaid@11.16.0`) via the oracle script `tests/oracle/verify_mermaid.mjs`.

---

## 2. Feature Inventory & Coverage Mapping

The project's four primary features (F1–F4) map across a 4-Tier E2E testing framework:

| Feature ID | Feature Name | Description | Target Milestones | Coverage Goal (Tiers 1–4) |
|------------|--------------|-------------|-------------------|---------------------------|
| **F1** | ggen Pack & Ontology Expansion | Expand `ontology.ttl` & Tera templates to support 15 diagram types and emit to first-class Python engine paths. | M1 | **Tier 1**: Ontology field shapes, 15 diagram model types, gapless field ordering.<br>**Tier 2**: Enum bounds, 3-level nesting limits (Gate 060), example value presence.<br>**Tier 3**: Ontology fixtures ↔ Renderer dispatch integration.<br>**Tier 4**: Complete ggen sync pipeline execution. |
| **F2** | Shadow Module Removal & First-Class Code Precipitation | Replace legacy shadow modules (`_generated_*`, legacy `models.py`/`parser.py`/`render.py`, `types/`) with unified engine code. | M2 | **Tier 1**: Clean imports from `mmdio.engine.*`, zero `_generated_` imports in API/CLI.<br>**Tier 2**: Discriminator resolution, `StrEnum` direct string formatting without `.value`.<br>**Tier 3**: Lark parser ↔ Pydantic model ↔ Renderer roundtrips.<br>**Tier 4**: REST API & CLI diagram processing workflows. |
| **F3** | Pytest Harness & Warning Resolution | Configure `pyproject.toml` and pytest fixtures so `uv run pytest` runs 100% cleanly without warnings. | M3 | **Tier 1**: Clean execution of unit test suite with zero warning escalations.<br>**Tier 2**: Starlette & Pydantic V2 warning suppression verification.<br>**Tier 3**: Parallel execution harness compatibility (`pytest-xdist`).<br>**Tier 4**: Continuous testing pipeline execution. |
| **F4** | Final E2E Oracle & Gate Validation | Validate 100% gate pass rate across 10 SPARQL gates and 100% pytest pass rate against Node Mermaid 11.16.0. | M4 | **Tier 1**: Roundtrip AST -> Render -> Oracle for all 15 supported diagram types.<br>**Tier 2**: Syntax parsing error handling, invalid diagram source detection.<br>**Tier 3**: SPARQL gates validation matched with Python parser/render capability.<br>**Tier 4**: Real-world application scenarios (C4, Sequence, ER, Kanban, etc.). |

---

## 3. Test Architecture & Harness Components

```
+-----------------------------------------------------------------------------------+
|                                 Pytest Test Runner                                |
|                                 `uv run pytest`                                  |
+------------------------------------------+----------------------------------------+
                                           |
                    +----------------------+----------------------+
                    |                                             |
                    v                                             v
     +------------------------------+              +------------------------------+
     |   Node Mermaid JS Oracle     |              |    ggen SPARQL Law Gates     |
     | tests/oracle/verify_mermaid  |              |   packs/mmdio-pack/gates/    |
     |       (mermaid@11.16.0)      |              |          (10 Gates)          |
     +--------------+---------------+              +--------------+---------------+
                    |                                             |
                    v                                             v
     +------------------------------+              +------------------------------+
     | Node CLI: `mermaid.detectType` |            |  `rdflib` SPARQL Engine /    |
     | Returns 0 (pass) / 1 (fail)  |              |    `ggen sync run` Check     |
     +------------------------------+              +------------------------------+
```

### 3.1 Runner Invocation
- **Standard Command**: `uv run pytest tests/e2e/`
- **Full Test Suite Command**: `uv run pytest`
- **Environment**: Pure Python 3.11+ environment managed via `uv`.

### 3.2 Oracle Harness (`tests/oracle/verify_mermaid.mjs`)
- **Engine**: Node.js running `mermaid@11.16.0` (pinned in `tests/oracle/package.json`).
- **Initialization Protocol**:
  ```javascript
  await mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'strict',
    htmlLabels: false,
    flowchart: { defaultRenderer: 'dagre-wrapper' },
    architecture: { randomize: false }
  });
  ```
- **Validation Semantics**: Uses `mermaid.detectType(source)` on temporary `.mmd` files.
- **Pass/Fail Semantics**:
  - **Pass**: Exit Code `0`, stdout contains `SUCCESS: Detected diagram type: <type>`.
  - **Fail**: Exit Code `1`, stderr contains `PARSE_ERROR: <details>`.

### 3.3 ggen SPARQL Gate Verification
- **Location**: `packs/mmdio-pack/gates/*.rq`
- **Gates Validated** (10 total):
  1. `010_python_support_complete.rq`: All supported diagram types have required predicates.
  2. `020_no_duplicate_internal_id.rq`: `pythonInternalId` is globally unique.
  3. `030_field_shape_closed_vocabulary.rq`: `fieldKind` strictly belongs to closed vocabulary.
  4. `040_field_order_gapless.rq`: `fieldOrder` integers are 1-indexed and gapless.
  5. `050_render_format_present_for_list_fields.rq`: List fields provide render format string.
  6. `060_render_nesting_depth_limit.rq`: Nesting depth of list fields <= 2 levels.
  7. `070_enum_class_exists_for_enum_fields.rq`: Enum fields map to non-empty enum classes.
  8. `080_scalar_example_value_present.rq`: Required scalar & enum fields provide example values.
  9. `090_field_pytype_resolves.rq`: List/nested-ref `fieldPyType` resolves to model className.
  10. `100_classname_globally_unique.rq`: `className` is globally unique across models.

---

## 4. Real-World Application Scenarios (Tier 4) Mapping

Tier 4 tests exercise full multi-step real-world scenarios across the entire pipeline:

| Scenario ID | Application Domain | Workflow Steps | Verification Gate |
|-------------|--------------------|----------------|-------------------|
| `T4-E2E-01` | Microservice Architecture C4 | Parse C4 diagram -> mutate AST -> render -> oracle validation. | Node Oracle (`c4Context`) |
| `T4-E2E-02` | E-Commerce Sequence Diagram | Construct sequence AST -> render -> parse back to AST -> oracle validation. | Node Oracle (`sequence`) |
| `T4-E2E-03` | Database Schema Migration ER | Parse ER diagram -> export JSON Schema -> re-render -> oracle validation. | Node Oracle (`erDiagram`) |
| `T4-E2E-04` | Sprint Planning Kanban Board | Load Kanban fixture -> modify section state -> render -> oracle validation. | Node Oracle (`kanban`) |
| `T4-E2E-05` | CI/CD Release Git Graph | Construct GitGraph AST (branches, commits, tags) -> render -> oracle validation. | Node Oracle (`gitGraph`) |
| `T4-E2E-06` | Quarterly Roadmap Timeline | Parse Timeline diagram -> add milestone event -> render -> oracle validation. | Node Oracle (`timeline`) |
| `T4-E2E-07` | Server Metrics XY Chart | Construct XYChart AST (bar & line series) -> render -> oracle validation. | Node Oracle (`xychart`) |
| `T4-E2E-08` | Infrastructure Grid Block Diagram | Construct Block diagram AST (grid layout) -> render -> oracle validation. | Node Oracle (`block`) |
| `T4-E2E-09` | ggen Sync & Gate Validation Pipeline | Execute `ggen sync run` -> verify 10 SPARQL gates -> run pytest suite. | 10 SPARQL Gates & Pytest |
| `T4-E2E-10` | REST API Roundtrip Render Service | POST Mermaid text to API endpoints -> receive AST & re-rendered text -> oracle validation. | HTTP 200 & Node Oracle |

---

## 5. Supported Diagram Types & Fixture Inventory

`tests/e2e/conftest.py` provides sample diagram text fixtures for all 15 supported diagram types:

| # | Pytest Fixture Name | Diagram Type | Key Header / Keyword |
|---|---------------------|--------------|----------------------|
| 1 | `sample_flowchart_source` | Flowchart | `flowchart TD` |
| 2 | `sample_sequence_source` | Sequence | `sequenceDiagram` |
| 3 | `sample_class_source` | Class Diagram | `classDiagram` |
| 4 | `sample_state_source` | State Diagram | `stateDiagram-v2` |
| 5 | `sample_er_source` | ER Diagram | `erDiagram` |
| 6 | `sample_gantt_source` | Gantt Chart | `gantt` |
| 7 | `sample_pie_source` | Pie Chart | `pie` |
| 8 | `sample_git_source` | Git Graph | `gitGraph` |
| 9 | `sample_c4_source` | C4 Diagram | `C4Context` |
| 10 | `sample_mindmap_source` | Mindmap | `mindmap` |
| 11 | `sample_sankey_source` | Sankey Diagram | `sankey-beta` |
| 12 | `sample_kanban_source` | Kanban Board | `kanban` |
| 13 | `sample_timeline_source` | Timeline | `timeline` |
| 14 | `sample_xychart_source` | XY Chart | `xychart-beta` |
| 15 | `sample_block_source` | Block Diagram | `block-beta` |

---

## 6. Coverage & Verification Thresholds

To achieve full verification under `PROJECT.md` M4 completion criteria:
- **Pytest Pass Rate**: 100% (0 failures, 0 errors).
- **Deprecation Warnings**: 0 unhandled warnings (`filterwarnings = ["error", ...]`).
- **SPARQL Law Gates Pass Rate**: 100% (10 out of 10 gates return zero violations).
- **Node Oracle Validation**: 100% of sample diagram text fixtures pass `verify_mermaid.mjs` execution.
