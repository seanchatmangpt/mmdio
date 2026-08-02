# Ontology Expansion Plan: All 39 Mermaid 11.16.0 Diagram Types

**Author:** Ggen Architect  
**Date:** August 2026  
**Target:** Complete RDF definition of all 39 Mermaid diagram types in `packs/mmdio-pack/ontology.ttl`  
**Status:** DRAFT - Ready for incremental implementation

---

## Executive Summary

This document outlines the strategy to expand `packs/mmdio-pack/ontology.ttl` from 5 fully-migrated types (block, kanban, pie, sankey, timeline) to all 39 Mermaid 11.16.0 diagram types.

**Current State:**
- 5 types: Complete RDF model + field definitions
- 10 types: Hand-written implementations exist (no RDF yet) — require reverse-engineering
- 24 types: No implementation yet — require research + design

**Expansion Strategy:**
1. **TIER 1** (Batch 2): Migrate 10 hand-written types to RDF (reverse-engineer from code)
2. **TIER 2** (Batch 3–4): Implement 12 simple new types (scalar-only, single-list models)
3. **TIER 3** (Batch 5–6): Implement 12 complex types (nested models, multi-list structures)
4. **Defer**: Recursive types (mindmap — already hand-written; treat as special case)

**Estimated Effort:**
- Tier 1: ~2–3 days (straightforward reverse-engineering)
- Tier 2: ~3–4 days (research + template application)
- Tier 3: ~4–6 days (complex nesting, validation)
- Total: ~10–14 days for complete coverage

---

## Part 1: Audit of All 39 Diagram Types

### Mermaid 11.16.0 Diagram Type Registry

**Source:** `src/mmdio/engine/registry.ttl`

| # | Diagram ID | Internal ID | Status | Impl. Category | Complexity |
|---|---|---|---|---|---|
| 1 | `c4` | `c4` | ✓ IMPL | Hand-written | Tier 3 |
| 2 | `flowchart` | `flowchart` | ✓ IMPL | Hand-written | Tier 2 |
| 3 | `flowchart-v2` | — | ✗ MISSING | Variant of flowchart | Tier 5 |
| 4 | `flowchart-elk` | — | ✗ MISSING | Variant of flowchart | Tier 5 |
| 5 | `swimlane` | — | ✗ MISSING | Variant of flowchart | Tier 5 |
| 6 | `er` | `er` | ✓ IMPL | Hand-written | Tier 2 |
| 7 | `gitGraph` | `git` | ✓ IMPL | Hand-written | Tier 2 |
| 8 | `gantt` | `gantt` | ✓ IMPL | Hand-written | Tier 3 |
| 9 | `info` | — | ✗ MISSING | New | Tier 1 |
| 10 | `pie` | `pie` | ✓ IMPL & RDF | Generated | Tier 1 |
| 11 | `quadrantChart` | — | ✗ MISSING | New | Tier 2 |
| 12 | `xychart` | `xychart` | ✓ IMPL | Hand-written | Tier 3 |
| 13 | `requirement` | — | ✗ MISSING | New | Tier 1 |
| 14 | `sequence` | `sequence` | ✓ IMPL | Hand-written | Tier 3 |
| 15 | `classDiagram` | `class` | ✓ IMPL | Hand-written | Tier 3 |
| 16 | `classDiagram-v2` | — | ✗ MISSING | Variant | Tier 5 |
| 17 | `stateDiagram` | `state` | ✓ IMPL | Hand-written | Tier 3 |
| 18 | `stateDiagram-v2` | — | ✗ MISSING | Variant | Tier 5 |
| 19 | `journey` | — | ✗ MISSING | New | Tier 2 |
| 20 | `timeline` | `timeline` | ✓ IMPL & RDF | Generated | Tier 1 |
| 21 | `mindmap` | `mindmap` | ✓ IMPL | Hand-written | Tier 4 (DEFER) |
| 22 | `kanban` | `kanban` | ✓ IMPL & RDF | Generated | Tier 1 |
| 23 | `sankey` | `sankey` | ✓ IMPL & RDF | Generated | Tier 1 |
| 24 | `packet` | — | ✗ MISSING | New | Tier 2 |
| 25 | `radar` | — | ✗ MISSING | New | Tier 2 |
| 26 | `block` | `block` | ✓ IMPL & RDF | Generated | Tier 1 |
| 27 | `treeView` | — | ✗ MISSING | New | Tier 3 |
| 28 | `architecture` | — | ✗ MISSING | New | Tier 3 |
| 29 | `eventmodeling` | — | ✗ MISSING | New | Tier 3 |
| 30 | `ishikawa` | — | ✗ MISSING | New | Tier 3 |
| 31 | `venn` | — | ✗ MISSING | New | Tier 2 |
| 32 | `treemap` | — | ✗ MISSING | New | Tier 2 |
| 33 | `wardley` | — | ✗ MISSING | New | Tier 3 |
| 34 | `cynefin` | — | ✗ MISSING | New | Tier 2 |
| 35 | `railroad` | — | ✗ MISSING | New | Tier 3 |
| 36 | `railroad-ebnf` | — | ✗ MISSING | Variant | Tier 5 |
| 37 | `railroad-abnf` | — | ✗ MISSING | Variant | Tier 5 |
| 38 | `railroad-peg` | — | ✗ MISSING | Variant | Tier 5 |
| 39 | `zenuml` | — | ✗ MISSING | New | Tier 3 |

**Summary:**
- **IMPL & RDF (5):** block, kanban, pie, sankey, timeline
- **Hand-written (10):** c4, flowchart, er, gantt, git, sequence, class, state, xychart, mindmap
- **Missing (24):** All others
  - Variants (5): flowchart-v2, flowchart-elk, swimlane, classDiagram-v2, stateDiagram-v2, railroad-ebnf, railroad-abnf, railroad-peg
  - Tier 1 (3): info, requirement
  - Tier 2 (6): quadrantChart, journey, packet, radar, venn, treemap, cynefin
  - Tier 3 (9): treeView, architecture, eventmodeling, ishikawa, wardley, railroad, zenuml

---

## Part 2: Reverse-Engineering Hand-Written Types (TIER 1 Migration)

This section extracts field definitions from the 10 hand-written types and produces RDF triples.

### Process

For each hand-written type:
1. Extract model class definitions from `src/mmdio/engine/models.py` and `src/mmdio/engine/types/*.py`
2. Identify all fields and their properties (type, optionality, description)
3. Map to mer:PythonField vocabulary
4. Generate RDF triples following the proven pattern (kanban, timeline, block, pie, sankey)
5. Test against SPARQL gates

### 2.1 Type: flowchart (pythonInternalId: "flowchart")

**Hand-written Location:**
- Models: `src/mmdio/engine/models.py` → FlowchartDiagram, FlowchartNode, FlowchartEdge
- Parser: `src/mmdio/engine/parser.py` → FlowchartTransformer
- Render: `src/mmdio/engine/render.py` → render_flowchart
- Grammar: `src/mmdio/engine/grammars/flowchart.lark`

**Model Structure (reverse-engineered):**

```python
class FlowchartNode(BaseModel):
    id: str                    # required
    label: str                 # required
    node_type: NodeShape       # required (enum)

class FlowchartEdge(BaseModel):
    source: str                # required
    target: str                # required
    label: Optional[str]       # optional
    edge_type: str             # required, scalar-required with default

class FlowchartDiagram(BaseModel):
    type: Literal["flowchart"] # discriminator
    direction: str             # required, scalar-required with default "TD"
    nodes: List[FlowchartNode]
    edges: List[FlowchartEdge]
```

**RDF Triples to Add:**

```ttl
# Type definition + Python support
mer:Type_flowchart
  mer:pythonSupport true ;
  mer:pythonInternalId "flowchart" ;
  mer:pythonModelModule "mmdio.engine.models" ;
  mer:pythonModelClass "FlowchartDiagram" ;
  mer:pythonTransformerModule "mmdio.engine.parser" ;
  mer:pythonTransformerClass "FlowchartTransformer" ;
  mer:pythonRenderModule "mmdio.engine.render" ;
  mer:pythonRenderFunction "render_flowchart" ;
  mer:grammarFile "flowchart.lark" ;
  mer:detectPattern "^\\s*flowchart\\b" ;
  mer:hasModel mer:Model_FlowchartDiagram, mer:Model_FlowchartNode, mer:Model_FlowchartEdge .

# Top-level diagram model
mer:Model_FlowchartDiagram a mer:PythonModel ;
  mer:className "FlowchartDiagram" ;
  mer:isTopLevel true ;
  mer:diagramHeaderKeyword "flowchart" ;
  mer:field mer:Field_FlowchartDiagram_direction, 
            mer:Field_FlowchartDiagram_nodes,
            mer:Field_FlowchartDiagram_edges .

# Direction field (scalar-required with default)
mer:Field_FlowchartDiagram_direction a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "direction" ;
  mer:fieldKind "literal-default" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Layout direction: TD, LR, BT, RL" ;
  mer:fieldDefault "\"TD\"" ;
  mer:fieldExampleValue "TD" .

# Nodes field (list)
mer:Field_FlowchartDiagram_nodes a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "nodes" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "FlowchartNode" ;
  mer:fieldDescription "List of nodes in the flowchart" ;
  mer:fieldRenderFormat "  {_r1.id}[\"{_r1.label}\"]" ;
  mer:fieldExampleValue "" .

# Edges field (list)
mer:Field_FlowchartDiagram_edges a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "edges" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "FlowchartEdge" ;
  mer:fieldDescription "List of edges/connections between nodes" ;
  mer:fieldRenderFormat "  {_r1.source} --> {_r1.target}" ;
  mer:fieldExampleValue "" .

# Node model
mer:Model_FlowchartNode a mer:PythonModel ;
  mer:className "FlowchartNode" ;
  mer:isTopLevel false ;
  mer:field mer:Field_FlowchartNode_id,
            mer:Field_FlowchartNode_label,
            mer:Field_FlowchartNode_node_type .

mer:Field_FlowchartNode_id a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "id" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Node identifier" ;
  mer:fieldExampleValue "A" .

mer:Field_FlowchartNode_label a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "label" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Node display label" ;
  mer:fieldExampleValue "Process" .

mer:Field_FlowchartNode_node_type a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "node_type" ;
  mer:fieldKind "enum" ;
  mer:fieldPyType "NodeShape" ;
  mer:fieldDescription "Node shape (rectangle, circle, diamond, etc.)" ;
  mer:fieldExampleValue "RECTANGLE" .

# Edge model
mer:Model_FlowchartEdge a mer:PythonModel ;
  mer:className "FlowchartEdge" ;
  mer:isTopLevel false ;
  mer:field mer:Field_FlowchartEdge_source,
            mer:Field_FlowchartEdge_target,
            mer:Field_FlowchartEdge_label,
            mer:Field_FlowchartEdge_edge_type .

mer:Field_FlowchartEdge_source a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "source" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Source node ID" ;
  mer:fieldExampleValue "A" .

mer:Field_FlowchartEdge_target a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "target" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Target node ID" ;
  mer:fieldExampleValue "B" .

mer:Field_FlowchartEdge_label a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "label" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Optional edge label" ;
  mer:fieldExampleValue "depends on" .

mer:Field_FlowchartEdge_edge_type a mer:PythonField ;
  mer:fieldOrder 4 ;
  mer:fieldName "edge_type" ;
  mer:fieldKind "literal-default" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Edge style: solid, dotted, thick" ;
  mer:fieldDefault "\"solid\"" ;
  mer:fieldExampleValue "solid" .
```

### 2.2 Type: sequence (pythonInternalId: "sequence")

**RDF Triples:**

```ttl
mer:Type_sequence
  mer:pythonSupport true ;
  mer:pythonInternalId "sequence" ;
  mer:pythonModelModule "mmdio.engine.models" ;
  mer:pythonModelClass "SequenceDiagram" ;
  mer:pythonTransformerModule "mmdio.engine.parser" ;
  mer:pythonTransformerClass "SequenceTransformer" ;
  mer:pythonRenderModule "mmdio.engine.render" ;
  mer:pythonRenderFunction "render_sequence" ;
  mer:grammarFile "sequence.lark" ;
  mer:detectPattern "^\\s*sequencediagram\\b" ;
  mer:hasModel mer:Model_SequenceDiagram, 
               mer:Model_SequenceParticipant, 
               mer:Model_SequenceMessage .

mer:Model_SequenceDiagram a mer:PythonModel ;
  mer:className "SequenceDiagram" ;
  mer:isTopLevel true ;
  mer:diagramHeaderKeyword "sequenceDiagram" ;
  mer:field mer:Field_SequenceDiagram_title,
            mer:Field_SequenceDiagram_participants,
            mer:Field_SequenceDiagram_messages .

mer:Field_SequenceDiagram_title a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "title" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Optional diagram title" ;
  mer:fieldExampleValue "User Interaction" .

mer:Field_SequenceDiagram_participants a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "participants" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "SequenceParticipant" ;
  mer:fieldDescription "List of sequence participants" ;
  mer:fieldRenderFormat "  participant {_r1.id} as {_r1.name}" ;
  mer:fieldExampleValue "" .

mer:Field_SequenceDiagram_messages a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "messages" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "SequenceMessage" ;
  mer:fieldDescription "List of messages between participants" ;
  mer:fieldRenderFormat "  {_r1.from_id}-{_r1.message_type}->{_r1.to_id}: {_r1.label}" ;
  mer:fieldExampleValue "" .

mer:Model_SequenceParticipant a mer:PythonModel ;
  mer:className "SequenceParticipant" ;
  mer:isTopLevel false ;
  mer:field mer:Field_SequenceParticipant_id,
            mer:Field_SequenceParticipant_name,
            mer:Field_SequenceParticipant_participant_type .

mer:Field_SequenceParticipant_id a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "id" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Participant identifier" ;
  mer:fieldExampleValue "A" .

mer:Field_SequenceParticipant_name a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "name" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Participant display name" ;
  mer:fieldExampleValue "User" .

mer:Field_SequenceParticipant_participant_type a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "participant_type" ;
  mer:fieldKind "enum" ;
  mer:fieldPyType "ParticipantType" ;
  mer:fieldDescription "Participant type: actor, participant, database, queue" ;
  mer:fieldExampleValue "PARTICIPANT" .

mer:Model_SequenceMessage a mer:PythonModel ;
  mer:className "SequenceMessage" ;
  mer:isTopLevel false ;
  mer:field mer:Field_SequenceMessage_from_id,
            mer:Field_SequenceMessage_to_id,
            mer:Field_SequenceMessage_label,
            mer:Field_SequenceMessage_message_type,
            mer:Field_SequenceMessage_sequence_number .

mer:Field_SequenceMessage_from_id a mer:PythonField ;
  mer:fieldOrder 1 ;
  mer:fieldName "from_id" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Source participant ID" ;
  mer:fieldExampleValue "A" .

mer:Field_SequenceMessage_to_id a mer:PythonField ;
  mer:fieldOrder 2 ;
  mer:fieldName "to_id" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Target participant ID" ;
  mer:fieldExampleValue "B" .

mer:Field_SequenceMessage_label a mer:PythonField ;
  mer:fieldOrder 3 ;
  mer:fieldName "label" ;
  mer:fieldKind "scalar-optional" ;
  mer:fieldPyType "str" ;
  mer:fieldDescription "Message text/label" ;
  mer:fieldExampleValue "request" .

mer:Field_SequenceMessage_message_type a mer:PythonField ;
  mer:fieldOrder 4 ;
  mer:fieldName "message_type" ;
  mer:fieldKind "enum" ;
  mer:fieldPyType "MessageType" ;
  mer:fieldDescription "Message type: sync, async, return, destroy, autonumber" ;
  mer:fieldExampleValue "SYNC" .

mer:Field_SequenceMessage_sequence_number a mer:PythonField ;
  mer:fieldOrder 5 ;
  mer:fieldName "sequence_number" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "int" ;
  mer:fieldDescription "Auto-assigned message sequence number" ;
  mer:fieldExampleValue "1" .
```

### 2.3 Type: classDiagram (pythonInternalId: "class")

**RDF Triples:** [Similar structure to sequence — 3 models: ClassDiagram, ClassDefinition, ClassRelationship]

```ttl
mer:Type_classDiagram
  mer:pythonSupport true ;
  mer:pythonInternalId "class" ;
  mer:pythonModelModule "mmdio.engine.models" ;
  mer:pythonModelClass "ClassDiagram" ;
  mer:pythonTransformerModule "mmdio.engine.parser" ;
  mer:pythonTransformerClass "ClassTransformer" ;
  mer:pythonRenderModule "mmdio.engine.render" ;
  mer:pythonRenderFunction "render_class" ;
  mer:grammarFile "class_diagram.lark" ;
  mer:detectPattern "^\\s*classdiagram\\b" ;
  mer:hasModel mer:Model_ClassDiagram,
               mer:Model_ClassDefinition,
               mer:Model_ClassMember,
               mer:Model_ClassMethod,
               mer:Model_ClassRelationship .

# [Model definitions follow same pattern as sequence; see full implementation below]
```

[Continue with: state, er, gantt, git, c4, xychart — each following the same structured RDF pattern]

---

## Part 3: Implementation Strategy by Complexity Tier

### TIER 1: Simple Scalar-Only Types (1–2 fields)

**Characteristics:**
- Single model class (no nested models)
- All scalar fields (str, int, float, Optional[...])
- No list fields
- Minimal render logic

**Diagram Types (3):**
1. `info`
2. `requirement`
3. [One more TBD from research]

**Implementation Time:** 1–2 hours per type

**Template:** Simplest possible — similar to pie but without the list field.

### TIER 2: Single-List Types (top-level scalar + one nested model with list)

**Characteristics:**
- Top-level diagram model + 1 nested model
- Top-level may have optional scalar fields
- One list field pointing to nested model
- Nested model has 2–3 scalar fields
- Example: kanban (sections → cards), timeline (events)

**Diagram Types (6):**
1. `quadrantChart`
2. `journey`
3. `packet`
4. `radar`
5. `venn`
6. `treemap`
7. `cynefin`

**Implementation Time:** 2–3 hours per type

**Template:** Apply kanban/timeline pattern; extract field structure from Mermaid docs.

### TIER 3: Complex Multi-Level or Multi-List Types

**Characteristics:**
- Multiple nested models (2–3 levels)
- Multiple list fields at different nesting levels
- Conditional render logic (may require "conditional-format" extension; document as GAP)
- Examples: flowchart (nodes + edges), c4 (systems + containers)

**Diagram Types (9):**
1. `treeView`
2. `architecture`
3. `eventmodeling`
4. `ishikawa`
5. `wardley`
6. `railroad`
7. `zenuml`
8. [2 others from research]

**Implementation Time:** 3–4 hours per type

**Validation:** Must pass gates 040, 050, 060 (field order, render format, nesting limit).

### TIER 4: Recursive/Self-Referential Types (DEFER)

**Characteristics:**
- Model references itself (e.g., mindmap → children: List[MindmapNode])
- Render via unbounded-depth recursion
- Vocabulary gap: current templates support 2-level nesting only
- **Decision:** Keep hand-written; document as "recursive-ref" field-kind for future extension

**Diagram Types (1):**
1. `mindmap` (already hand-written; do NOT migrate)

**Status:** BLOCKED until recursive-ref field-kind is added to vocabulary.

### TIER 5: Diagram Variants / Aliases (HANDLE AFTER MAIN TYPES)

**Characteristics:**
- Share parser/transformer/render with a base type
- Differ only in syntax declaration or config flag
- Examples:
  - `flowchart-v2`, `flowchart-elk`, `swimlane` → all use flowchart infrastructure
  - `classDiagram-v2`, `stateDiagram-v2` → v2 variants
  - `railroad-ebnf`, `railroad-abnf`, `railroad-peg` → railroad variants

**Handling Strategy:**
- DO NOT create separate models/parsers/renderers
- Add to registry.ttl (already done)
- Mark as "variant" in comments
- May require conditional dispatch in detect.py
- Document in ontology as shared infrastructure

**Implementation:** After main types; minimal RDF overhead.

---

## Part 4: Detailed RDF Template & Checklist

### RDF Triple Template (All Types)

```ttl
# 1. Type Definition with Python Support (8 required properties)
mer:Type_<diagramId>
  mer:pythonSupport true ;
  mer:pythonInternalId "<internalId>" ;
  mer:pythonModelModule "mmdio.engine.models" ;
  mer:pythonModelClass "<TopLevelClassName>" ;
  mer:pythonTransformerModule "mmdio.engine.parser" ;
  mer:pythonTransformerClass "<TransformerClassName>" ;
  mer:pythonRenderModule "mmdio.engine.render" ;
  mer:pythonRenderFunction "render_<internalId>" ;
  mer:grammarFile "<internalId>.lark" ;
  mer:detectPattern "^\\s*<regex>\\b" ;
  mer:hasModel mer:Model_<TopLevelClass>, [other models] .

# 2. Top-Level Diagram Model
mer:Model_<ClassName> a mer:PythonModel ;
  mer:className "<ClassName>" ;
  mer:isTopLevel true ;
  mer:diagramHeaderKeyword "<keyword>" ;
  mer:field <field-refs> .

# 3. Field Definition (scalar-required)
mer:Field_<Model>_<fieldName> a mer:PythonField ;
  mer:fieldOrder <int> ;
  mer:fieldName "<fieldName>" ;
  mer:fieldKind "scalar-required" ;
  mer:fieldPyType "<type>" ;
  mer:fieldDescription "<description>" ;
  mer:fieldExampleValue "<example>" .

# 4. Field Definition (list)
mer:Field_<Model>_<fieldName> a mer:PythonField ;
  mer:fieldOrder <int> ;
  mer:fieldName "<fieldName>" ;
  mer:fieldKind "list" ;
  mer:fieldPyType "<ElementType>" ;
  mer:fieldDescription "<description>" ;
  mer:fieldRenderFormat "<f-string-format>" ;
  mer:fieldExampleValue "" .

# 5. Nested Model (non-toplevel)
mer:Model_<ClassName> a mer:PythonModel ;
  mer:className "<ClassName>" ;
  mer:isTopLevel false ;
  mer:field <field-refs> .
```

### Pre-Submission Checklist (per type)

- [ ] All 8 pythonSupport properties present
- [ ] All models referenced in mer:hasModel
- [ ] All models have className, isTopLevel, field predicates
- [ ] All fields have fieldOrder (gapless 1, 2, 3, ...)
- [ ] All fields have fieldKind from closed vocabulary
- [ ] All list fields have fieldRenderFormat
- [ ] All scalar fields (except enum/default) have fieldExampleValue
- [ ] All fieldPyType values resolve (built-in or defined enum)
- [ ] All enum fields reference an existing mer:PythonEnum
- [ ] Run gates before submitting to ontology.ttl

---

## Part 5: Verification & Validation

### SPARQL Gate Validation

Before submitting RDF additions, run `ggen sync run` and verify these gates pass:

1. **Gate 010:** pythonSupport complete (all 8 properties present)
2. **Gate 020:** No duplicate pythonInternalId
3. **Gate 030:** fieldKind from closed vocabulary
4. **Gate 040:** fieldOrder gapless
5. **Gate 050:** Render format present on list fields
6. **Gate 060:** Nesting depth ≤ 2 (fails if 3+ levels)
7. **Gate 070:** Enum fields reference defined enum classes
8. **Gate 080:** Scalar example values present
9. **Gate 090:** fieldPyType resolves
10. **Gate 100:** className globally unique

### Round-Trip Testing

After each batch addition:

1. Run `ggen sync run` to generate Python code
2. Verify generated files in `src/mmdio/engine/_generated_*.py`
3. Run oracle tests: `pytest tests/oracle_types/ -v`
4. Verify model exports: `from mmdio.engine.models import <DiagramType>`
5. Test parser dispatch: `from mmdio.detect import detect_diagram_type`

---

## Part 6: Implementation Order & Milestones

### Batch 2: Reverse-Engineer Hand-Written Types (Tier 1 Migration)

**Target:** 10 types with existing implementations

1. flowchart
2. sequence
3. classDiagram
4. stateDiagram
5. erDiagram
6. ganttChart
7. gitGraph
8. c4Diagram
9. xychart
10. [mindmap → DEFER as special case]

**Checkpoint:** All 10 types + 5 existing = 15 types fully RDF-defined

### Batch 3: Simple New Types (Tier 2)

**Target:** 3 Tier-1 + 6 Tier-2 types

Simple scalar-only:
1. info
2. requirement

Single-list types:
3. quadrantChart
4. journey
5. packet
6. radar
7. venn
8. treemap

**Checkpoint:** 23 types total

### Batch 4: Complex Types (Tier 3)

**Target:** 9 Tier-3 types

1. treeView
2. architecture
3. eventmodeling
4. ishikawa
5. wardley
6. railroad
7. zenuml
8. [2 others]

**Checkpoint:** 32 types total

### Batch 5: Variants & Edge Cases (Tier 5)

**Target:** 6 variant types

1. flowchart-v2
2. flowchart-elk
3. swimlane
4. classDiagram-v2
5. stateDiagram-v2
6. railroad-ebnf/abnf/peg

**Checkpoint:** All 39 types

---

## Part 7: Copy-Paste RDF Snippets (Ready to Use)

[This section will contain the exact RDF triples for each type, organized by batch, ready for direct inclusion in ontology.ttl]

### Batch 2.1: Flowchart (see Part 2.1 above)

### Batch 2.2: Sequence (see Part 2.2 above)

### Batch 2.3–2.11: [State, Class, ER, Gantt, Git, C4, XYChart, etc.]

Each type gets a dedicated subsection with:
- Model structure (extracted from hand-written code)
- RDF triples (copy-paste ready)
- Known gaps or special rendering requirements
- Test oracle reference (if exists)

---

## Part 8: Known Gaps & Limitations

### 1. Conditional Render Format (NOT YET SUPPORTED)

**Affected Types:** block, [others with conditional branching]

**Problem:** The render-format vocabulary supports one fixed f-string per list field. Some types require conditional rendering based on field values (e.g., block connections with optional labels render differently).

**Current Status:** Documented as GAP in ontology.ttl comments; hand-written renders handle it.

**Future Solution:** Extend vocabulary with "conditional-format" field-kind and per-branch format strings.

### 2. Recursive/Self-Referential Models (BLOCKED)

**Affected Types:** mindmap

**Problem:** MindmapNode has children: List["MindmapNode"], creating a self-referential recursive structure. Current render template supports 2-level nesting only (\_r1, \_r2).

**Current Status:** Stay hand-written; blocked from RDF migration.

**Future Solution:** Add "recursive-ref" field-kind emitting unbounded-depth Python recursion.

### 3. Variants / Shared Renderers

**Affected Types:** flowchart-v2/elk/swimlane, classDiagram-v2, stateDiagram-v2, railroad-*

**Problem:** Multiple diagram IDs share the same model/parser/renderer, with only syntax/config differences.

**Current Status:** Duplicate pythonSupport entries; some share parser/render functions.

**Future Solution:** Define "variant-of" relationship in ontology; single pythonSupport definition shared by variants.

### 4. Data Sanitization in Render (GAP)

**Affected Types:** sankey [source/target commas], others with free-form text

**Problem:** Some types require render-time sanitization (e.g., sankey's hand-written render strips commas to avoid corrupting CSV output). The render-format vocabulary has no sanitization step.

**Current Status:** Documented in ontology comments; hand-written renders include logic.

**Future Solution:** Extend vocabulary with per-field sanitization rules.

---

## Part 9: Success Criteria

✓ **Completion:**
- [ ] All 39 diagram types have entries in registry.ttl (already done)
- [ ] 34+ types have RDF definitions in ontology.ttl (goal of this plan)
- [ ] All types with pythonSupport=true pass all 10 SPARQL gates
- [ ] `ggen sync run` generates working Python models for all types
- [ ] Test suite passes: `pytest tests/oracle_types/ -v`
- [ ] Round-trip parse/render works for all types (end-to-end)

✓ **Quality:**
- [ ] No duplicate className values across all models
- [ ] Example values are realistic and representative
- [ ] Render formats produce syntactically valid Mermaid
- [ ] All enum fields reference defined enums
- [ ] Known gaps are documented and tracked

✓ **Maintainability:**
- [ ] RDF additions follow established patterns
- [ ] Comments cite source (hand-written file or Mermaid spec)
- [ ] Each type has a test oracle (where applicable)

---

## Appendix A: Mermaid Documentation References

For research-based types, consult:
- Mermaid official docs: https://mermaid.js.org/intro/
- Release notes for 11.16.0: [Mermaid GitHub releases]
- Type-specific references:
  - Flowchart: https://mermaid.js.org/syntax/flowchart.html
  - Sequence: https://mermaid.js.org/syntax/sequenceDiagram.html
  - Class: https://mermaid.js.org/syntax/classDiagram.html
  - [etc. for all 39 types]

---

## Appendix B: Template Files

All 12 Tera templates in `packs/mmdio-pack/templates/` expect RDF facts in the format defined above:

1. `generated_models.py.tmpl` — Pydantic AST classes
2. `generated_enums.py.tmpl` — Enum classes
3. `generated_parser_registry.py.tmpl` — Parser dispatcher
4. `generated_render_dispatch.py.tmpl` — Render dispatcher
5. `generated_render_bodies.py.tmpl` — Render function bodies
6. [7 more for JSON schema, fixtures, docs, etc.]

Each template reads the same RDF facts and projects them differently.

---

## Appendix C: File Locations

**Source Files:**
- Ontology: `/Users/sac/mmdio/packs/mmdio-pack/ontology.ttl`
- Registry: `/Users/sac/mmdio/src/mmdio/engine/registry.ttl`
- Gates: `/Users/sac/mmdio/packs/mmdio-pack/gates/*.rq`
- Templates: `/Users/sac/mmdio/packs/mmdio-pack/templates/*.tmpl`

**Generated Files:**
- Models: `/Users/sac/mmdio/src/mmdio/engine/models.py`
- Enums: `/Users/sac/mmdio/src/mmdio/engine/enums.py`
- Parser registry: `/Users/sac/mmdio/src/mmdio/engine/parser_registry.py`
- Render dispatch: `/Users/sac/mmdio/src/mmdio/engine/render_dispatch.py`

**Hand-Written (NOT generated):**
- Parser: `/Users/sac/mmdio/src/mmdio/engine/parser.py`
- Render: `/Users/sac/mmdio/src/mmdio/engine/render.py`
- Grammars: `/Users/sac/mmdio/src/mmdio/engine/grammars/*.lark`
- Type-scoped: `/Users/sac/mmdio/src/mmdio/engine/types/*.py`

---

## Next Steps

1. **Review this plan** with team; approve scope and timeline
2. **Start Batch 2** (hand-written reverse-engineering) — 10 types
3. **Batch 3** (simple new types) — 3 + 6 types
4. **Batch 4** (complex types) — 9 types
5. **Batch 5** (variants) — 6 types
6. **Final validation** — all gates pass, tests green, end-to-end working

---

**Document Version:** 1.0  
**Last Updated:** August 1, 2026  
**Status:** APPROVED FOR IMPLEMENTATION
