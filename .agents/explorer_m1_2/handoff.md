# Handoff Report: Explorer 2 — Ontology & Registry Investigation (Milestone M1)

**Agent ID**: `explorer_m1_2`  
**Working Directory**: `/Users/sac/mmdio/.agents/explorer_m1_2`  
**Parent Conversation ID**: `5ec836a6-9600-45e4-b443-7a8e6d651f19`  
**Date**: 2026-08-02T03:25:30Z  

---

## 1. Observation

### 1.1 Registry Facts (`src/mmdio/engine/registry.ttl`)
- **Total Lines**: 513 lines of Turtle RDF.
- **Classes Defined**:
  - `mer:DiagramType` (Line 9)
  - `mer:Diagram` (Line 10)
  - `mer:UpstreamRelease` (Line 11)
  - `mer:RendererSource` (Line 12)
  - `mer:AuthorityClass` (Line 13) with instances `mer:Normative`, `mer:Observational`, `mer:Reconciliation`
- **Properties Defined**:
  - `mer:diagramId`, `mer:displayName`, `mer:syntaxDeclaration`, `mer:detectorPath`, `mer:definitionPath`, `mer:rendererPath`, `mer:rendererAlternativePath`, `mer:rendererNotes`, `mer:sourceUrl`, `mer:sourceConfidence`, `mer:upstreamRelease`, `mer:outputPath`, `mer:sourceText`, `mer:diagramType`, `mer:authorityClass`, `mer:generated`, `mer:sourceGraphHash`, `mer:generationIndex`, `mer:standingCeiling`.
- **Diagram Types**: Exactly 39 `mer:DiagramType` subjects are catalogued from upstream Mermaid 11.16.0 (`mer:Mermaid_11_16_0`, commit `f0ffb41c1ee1ff667b528e86c3b082249726eeef`).
- **Normative Architecture Diagrams**: 3 `mer:Diagram` instances (`mer:Diagram_RendererArchitecture`, `mer:Diagram_RendererResolution`, `mer:Diagram_AuthorityState`).

### 1.2 Ontology Facts (`packs/mmdio-pack/ontology.ttl`)
- **Total Lines**: 598 lines of Turtle RDF.
- **Schema & Vocabulary Classes**:
  - `mer:PythonModel` (Line 82)
  - `mer:PythonField` (Line 83)
  - `mer:PythonEnum` (Line 84)
  - `mer:EnumMember` (Line 85)
- **Properties Defined**:
  - Python Integration: `mer:pythonSupport`, `mer:pythonInternalId`, `mer:pythonModelModule`, `mer:pythonModelClass`, `mer:pythonTransformerModule`, `mer:pythonTransformerClass`, `mer:pythonRenderModule`, `mer:pythonRenderFunction`, `mer:grammarFile`, `mer:detectPattern` (Lines 20–29).
  - Model/Field/Enum Shape: `mer:hasModel`, `mer:hasEnum`, `mer:enumClassName`, `mer:enumMember`, `mer:enumMemberName`, `mer:enumMemberValue`, `mer:enumMemberOrder`, `mer:className`, `mer:isTopLevel`, `mer:diagramHeaderKeyword`, `mer:field`, `mer:fieldOrder`, `mer:fieldName`, `mer:fieldKind`, `mer:fieldPyType`, `mer:fieldDescription`, `mer:fieldRenderFormat`, `mer:fieldExampleValue`, `mer:fieldDefault` (Lines 86–104).
- **Supported Python Diagram Types**:
  - Exactly 15 diagram types are annotated with `mer:pythonSupport true` + all 9 required metadata predicates:
    1. `flowchart` (`mer:Type_flowchart`)
    2. `sequence` (`mer:Type_sequence`)
    3. `class` (`mer:Type_classDiagram`)
    4. `state` (`mer:Type_stateDiagram`)
    5. `er` (`mer:Type_er`)
    6. `gantt` (`mer:Type_gantt`)
    7. `pie` (`mer:Type_pie`)
    8. `git` (`mer:Type_gitGraph`)
    9. `c4` (`mer:Type_c4`)
    10. `mindmap` (`mer:Type_mindmap`)
    11. `sankey` (`mer:Type_sankey`)
    12. `kanban` (`mer:Type_kanban`)
    13. `timeline` (`mer:Type_timeline`)
    14. `xychart` (`mer:Type_xychart`)
    15. `block` (`mer:Type_block`)
- **AST Model Shapes (`mer:hasModel`)**:
  - Exactly 5 diagram types currently have complete AST field-shape matrices in `ontology.ttl`:
    1. `kanban`: `Model_KanbanDiagram` (top-level), `Model_KanbanSection`, `Model_KanbanCard` (3 models, 4 fields)
    2. `timeline`: `Model_TimelineDiagram` (top-level), `Model_TimelineEvent` (2 models, 4 fields)
    3. `block`: `Model_BlockDiagram` (top-level), `Model_Block`, `Model_Connection` (3 models, 9 fields)
    4. `pie`: `Model_PieChart` (top-level), `Model_PieSlice` (2 models, 4 fields)
    5. `sankey`: `Model_SankeyDiagram` (top-level), `Model_SankeyFlow` (2 models, 4 fields)
  - Total: 12 `mer:PythonModel` individuals and 25 `mer:PythonField` individuals.
- **Legacy Module References in `ontology.ttl`**:
  - Lines 448–495: `kanban`, `timeline`, `xychart`, and `block` specify module paths pointing to `mmdio.engine.types.*`:
    - `mer:pythonModelModule "mmdio.engine.types.kanban_models"`
    - `mer:pythonTransformerModule "mmdio.engine.types.kanban_parser"`
    - `mer:pythonRenderModule "mmdio.engine.types.kanban_render"`
- **Token Enums**:
  - 0 `mer:PythonEnum` or `mer:EnumMember` individuals exist in `ontology.ttl` currently.
  - `src/mmdio/engine/models.py` defines 7 token enums: `NodeShape`, `MessageType`, `RelationshipType`, `CardinityType`, `TaskStatus`, `C4Level`, `ParticipantType`.

### 1.3 SPARQL Law Gates & Execution Status
- All 10 SPARQL law gates in `packs/mmdio-pack/gates/` were executed against `registry.ttl` + `ontology.ttl` using `rdflib`:
  - `010_python_support_complete.rq`: **0 violations**
  - `020_no_duplicate_internal_id.rq`: **0 violations**
  - `030_field_shape_closed_vocabulary.rq`: **0 violations**
  - `040_field_order_gapless.rq`: **0 violations**
  - `050_render_format_present_for_list_fields.rq`: **0 violations**
  - `060_render_nesting_depth_limit.rq`: **0 violations**
  - `070_enum_class_exists_for_enum_fields.rq`: **0 violations**
  - `080_scalar_example_value_present.rq`: **0 violations**
  - `090_field_pytype_resolves.rq`: **0 violations**
  - `100_classname_globally_unique.rq`: **0 violations**
- `uv run ggen sync run --dry-run` completes with **exit code 0** and 100% skipped (content identical across all 12 generated output paths).

---

## 2. Logic Chain

1. **Premise 1 (Module Layout Contract)**: `PROJECT.md` Section "Architecture" and `SCOPE.md` state that all ggen output must target first-class Python modules in `src/mmdio/engine/` (`models.py`, `enums.py`, `parser_registry.py`, `render_dispatch.py`, `render.py`, `parser.py`, `schemas.py`, `fixtures.py`, `supported.py`, `detect_patterns.py`), eliminating legacy shadow paths under `src/mmdio/engine/types/`.
2. **Step 1 (Module Path Correction)**: In `packs/mmdio-pack/ontology.ttl`, lines 451–491, four diagram types (`kanban`, `timeline`, `xychart`, `block`) set `mer:pythonModelModule`, `mer:pythonTransformerModule`, and `mer:pythonRenderModule` to `mmdio.engine.types.*`. These predicates must be updated to `"mmdio.engine.models"`, `"mmdio.engine.parser"`, and `"mmdio.engine.render"` so that precipitation targets the unified first-class engine files.
3. **Step 2 (AST Model Representation Expansion)**: Currently, only 5 diagram types (`pie`, `timeline`, `kanban`, `sankey`, `block`) have `mer:hasModel` shapes in `ontology.ttl`. The remaining 10 supported types (`flowchart`, `sequence`, `class`, `state`, `er`, `gantt`, `git`, `c4`, `mindmap`, `xychart`) lack `mer:hasModel` facts. Expanding `mer:hasModel` shapes for these types allows `generated_models.py.tmpl`, `generated_render_bodies.py.tmpl`, `generated_fixtures.py.tmpl`, `generated_schemas.py.tmpl`, and `generated_oracle_tests.py.tmpl` to generate code for them automatically.
4. **Step 3 (Token Enum Triples)**: When field shapes are added for diagram types that use token enums (e.g. `NodeShape` on flowchart nodes, `MessageType` on sequence messages, `RelationshipType` on class relationships), Gate 070 (`070_enum_class_exists_for_enum_fields.rq`) requires that every field with `mer:fieldKind "enum"` has a corresponding `mer:PythonEnum` with `mer:enumClassName` matching `fieldPyType` and at least one `mer:enumMember`. Therefore, adding `mer:PythonEnum` and `mer:EnumMember` triples for the 7 domain enums is required.
5. **Step 4 (Template & Gate Compatibility)**: Gate 060 enforces a strict 2-level list nesting depth limit (`top-level model -> list field -> element model -> list field`). Any added model shape must respect this limit. Tree structures like `mindmap` (self-referential `MindmapNode`) exceed 2-level unrolling and must either remain on hand-written AST/render logic or use a dedicated `recursive-ref` field kind.

---

## 3. Caveats

1. **Recursive AST Models (`mindmap`)**:
   - `MindmapNode` is self-referential (`children: List["MindmapNode"]`). A fixed 2-level unroll template cannot render arbitrary depth trees. As documented in `ontology.ttl` line 583, `mindmap` is deliberately omitted from `mer:hasModel` unrolling.
2. **Conditional Rendering Branching (`block`)**:
   - Hand-written `block_render.py` formats connections differently depending on whether `connection.label` is present. `mer:fieldRenderFormat` currently supports only one static f-string per field.
3. **String Sanitization in Render Formats (`sankey`)**:
   - Hand-written `sankey` renderer strips commas from source/target strings (`s.replace(',', '')`). F-string template substitution does not perform inline string replacement.
4. **Unimplemented Upstream Types**:
   - 24 of the 39 catalogued diagram types in `registry.ttl` are intentionally un-implemented in Python (`mer:pythonSupport false` / omitted).

---

## 4. Conclusion

1. **Current State Assessment**:
   - `src/mmdio/engine/registry.ttl` is accurate, authoritative, and complete for all 39 Mermaid 11.16.0 diagram types.
   - `packs/mmdio-pack/ontology.ttl` is 100% valid against all 10 law gates, but currently contains legacy `mmdio.engine.types.*` module paths for 4 types and lacks `mer:hasModel` shapes for 10 supported diagram types and `mer:PythonEnum` triples for domain enums.
2. **Actionable Recommendations for M1 Configuration**:
   - **Recommendation A**: Update `mer:pythonModelModule`, `mer:pythonTransformerModule`, and `mer:pythonRenderModule` in `packs/mmdio-pack/ontology.ttl` for `kanban`, `timeline`, `xychart`, and `block` to point to `"mmdio.engine.models"`, `"mmdio.engine.parser"`, and `"mmdio.engine.render"`.
   - **Recommendation B**: Populate `mer:PythonEnum` and `mer:EnumMember` triples for the 7 domain enums (`NodeShape`, `MessageType`, `RelationshipType`, `CardinityType`, `TaskStatus`, `C4Level`, `ParticipantType`) in `ontology.ttl`.
   - **Recommendation C**: Add `mer:hasModel` shapes for the remaining supported diagram types in `ontology.ttl`, adhering to Gate 040 (gapless field ordering), Gate 060 (2-level depth limit), Gate 080 (example values), and Gate 090 (resolving pyTypes).

---

## 5. Verification Method

To independently verify all findings and gate assertions:

1. **Run Law Gate SPARQL Verification**:
   ```bash
   uv run python -c "
   import glob
   from rdflib import Graph
   g = Graph()
   g.parse('src/mmdio/engine/registry.ttl', format='turtle')
   g.parse('packs/mmdio-pack/ontology.ttl', format='turtle')
   for gf in sorted(glob.glob('packs/mmdio-pack/gates/*.rq')):
       with open(gf) as f:
           res = g.query(f.read())
       print(f'{gf}: {len(res)} violations')
   "
   ```
   *Expected output*: 0 violations across all 10 gate queries.

2. **Run ggen Dry-Run**:
   ```bash
   uv run ggen sync run --dry-run
   ```
   *Expected output*: Clean run with exit code 0 and closure graph hash generated.

3. **Run Full Test Suite**:
   ```bash
   uv run pytest
   ```
   *Expected output*: All unit and oracle tests pass.
