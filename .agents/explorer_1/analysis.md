# Codebase Structure & Shadow Modules Analysis

## Executive Summary
This report analyzes the `mmdio` codebase (`/Users/sac/mmdio/src/mmdio/`), focusing on AST models, token enums, parser registries, render dispatchers, hand-written shadow modules, derived files, import paths, public APIs, and target landing locations for ggen-precipitated code.

Currently, `mmdio` operates with a **hybrid shadow architecture** where domain logic and AST models are split across three distinct module paradigms:
1. **Shared Hand-written Shadow Modules** (`src/mmdio/engine/models.py`, `parser.py`, `render.py`) covering 11 original diagram types.
2. **Type-Scoped Hand-written Shadow Modules** (`src/mmdio/engine/types/*.py`) covering 4 batch-1 diagram types (`block`, `kanban`, `timeline`, `xychart`).
3. **ggen Derived/Precipitated Modules** (`src/mmdio/engine/_generated_*.py` and `src/mmdio/_generated_detect_patterns.py`) generated from `packs/mmdio-pack/ontology.ttl` and `src/mmdio/engine/registry.ttl`.

---

## 1. Codebase File Structure Map

```
src/mmdio/
├── __init__.py                       # Package entry point; exports detect_diagram_type
├── _generated_detect_patterns.py        # GENERATED: Regex patterns for diagram type detection
├── api.py                            # REST API (FastAPI)
├── cli.py                            # Typer CLI application ("mmdio fire")
├── detect.py                         # Diagram detector using _generated_detect_patterns.py
└── engine/                           # Core Mermaid engine
    ├── __init__.py                   # Package re-exports for models, parsers, render, ops, registry
    ├── models.py                     # HAND-WRITTEN SHADOW: 11 AST models + Enums
    ├── parser.py                     # HAND-WRITTEN SHADOW: 11 Lark transformers & MermaidParser
    ├── render.py                     # HAND-WRITTEN SHADOW: 11 render functions & render_diagram dispatcher
    ├── ops.py                        # Hand-written diagram operations (merge, diff, validate_topology)
    ├── registry.py                   # Pure-Python RDF registry reader (using rdflib)
    ├── registry.ttl                  # Upstream Mermaid diagram ontology (39 diagram types)
    ├── grammars/                     # 15 Lark grammars (.lark)
    │   ├── block.lark, c4.lark, class_diagram.lark, er.lark, flowchart.lark, gantt.lark,
    │   ├── git.lark, kanban.lark, mindmap.lark, pie.lark, sankey.lark, sequence.lark,
    │   └── state.lark, timeline.lark, xychart.lark
    ├── types/                        # TYPE-SCOPED SHADOW MODULES (Batch 1 types)
    │   ├── __init__.py
    │   ├── block_models.py, block_parser.py, block_render.py
    │   ├── kanban_models.py, kanban_parser.py, kanban_render.py
    │   ├── timeline_models.py, timeline_parser.py, timeline_render.py
    │   └── xychart_models.py, xychart_parser.py, xychart_render.py
    └── _generated_*.py               # GGEN DERIVED / PRECIPITATED FILES
        ├── _generated_enums.py           # Generated StrEnum classes
        ├── _generated_fixtures.py        # Generated fixture builders (example_*())
        ├── _generated_models.py          # Generated MermaidDiagram discriminated union type
        ├── _generated_parser_registry.py # Generated GENERATED_TRANSFORMERS & GENERATED_GRAMMAR_FILES
        ├── _generated_pydantic_models.py # Generated Pydantic AST models (5 RDF-modeled types)
        ├── _generated_render_bodies.py   # Generated render functions (5 RDF-modeled types)
        ├── _generated_render_dispatch.py # Generated GENERATED_RENDER_DISPATCH mapping
        ├── _generated_schemas.py        # Generated JSON Schema definitions
        └── _generated_supported.py      # Generated GENERATED_PYTHON_SUPPORTED set
```

---

## 2. Comprehensive Inventory of Shadow Modules, AST Models, Enums, and Registries

### A. Hand-Written Shadow Modules

#### 1. `src/mmdio/engine/models.py` (775 lines)
Hand-written Pydantic `BaseModel` definitions and Enums for 11 diagram types:
- **Enums**:
  - `NodeShape` (`rectangle`, `circle`, `ellipse`, `diamond`, `hexagon`, `parallelogram`, `trapezoid`, `document`, `cylinder`, `subroutine`)
  - `MessageType` (`sync`, `async`, `return`, `autonumber`)
  - `RelationshipType` (`inheritance`, `realization`, `composition`, `aggregation`, `association`, `dependency`, `link`)
  - `CardinityType` (`one_to_one`, `one_to_many`, `many_to_one`, `many_to_many`, `many_to_many_marked`)
  - `TaskStatus` (`active`, `done`, `milestone`, `crit`, `active_crit`, `done_crit`)
  - `C4Level` (`C1`, `C2`, `C3`, `C4`)
  - `ParticipantType` (`actor`, `participant`, `autonumber`)
- **AST Models**:
  - `FlowchartDiagram`, `FlowchartNode`, `FlowchartEdge`
  - `SequenceDiagram`, `SequenceParticipant`, `SequenceMessage`
  - `ClassDiagram`, `ClassDefinition`, `ClassMember`, `ClassMethod`, `ClassRelationship`
  - `StateDiagram`, `State`, `Transition`
  - `ERDiagram`, `Entity`, `EntityAttribute`, `ERRelationship`
  - `GanttChart`, `GanttTask`
  - `PieChart`, `PieSlice`
  - `GitGraph`, `GitCommit`, `GitBranch`
  - `C4Diagram`, `C4Element`, `C4Relationship`
  - `Mindmap`, `MindmapNode`
  - `SankeyDiagram`, `SankeyFlow`
- **Imports from derived**:
  - Line 774: `from ._generated_models import MermaidDiagram`

#### 2. `src/mmdio/engine/parser.py` (894 lines)
Hand-written `Lark` parse-tree Transformers and top-level parser dispatcher:
- **Transformers**: `FlowchartTransformer`, `SequenceTransformer`, `ClassTransformer`, `StateTransformer`, `ERTransformer`, `GanttTransformer`, `PieTransformer`, `GitTransformer`, `C4Transformer`, `MindmapTransformer`, `SankeyTransformer`.
- **Classes**: `MermaidParser`, `ParsingError`.
- **Functions**: `parse_mermaid`, `parse_flowchart`, `parse_sequence`, `parse_class`, `parse_state`, `parse_er`, `parse_gantt`, `parse_pie`, `parse_git`, `parse_c4`, `parse_mindmap`, `parse_sankey`.
- **Imports from derived**:
  - Line 659: `from ._generated_parser_registry import GENERATED_TRANSFORMERS, GENERATED_GRAMMAR_FILES`

#### 3. `src/mmdio/engine/render.py` (625 lines)
Hand-written diagram render functions:
- **Functions**: `render_diagram`, `render_flowchart`, `render_sequence`, `render_class`, `render_state`, `render_er`, `render_gantt`, `render_pie`, `render_git`, `render_c4`, `render_mindmap`, `render_sankey`.
- **Imports from derived**:
  - Line 624: `from ._generated_render_dispatch import GENERATED_RENDER_DISPATCH`

#### 4. Type-Scoped Shadow Modules in `src/mmdio/engine/types/`
- **Block**: `block_models.py` (`Block`, `Connection`, `BlockDiagram`), `block_parser.py` (`BlockTransformer`), `block_render.py` (`render_block`)
- **Kanban**: `kanban_models.py` (`KanbanCard`, `KanbanSection`, `KanbanDiagram`), `kanban_parser.py` (`KanbanTransformer`), `kanban_render.py` (`render_kanban`)
- **Timeline**: `timeline_models.py` (`TimelineEvent`, `TimelineDiagram`), `timeline_parser.py` (`TimelineTransformer`), `timeline_render.py` (`render_timeline`)
- **XYChart**: `xychart_models.py` (`XYAxisValue`, `XYAxis`, `DataSeries`, `XYChartDiagram`), `xychart_parser.py` (`XYChartTransformer`), `xychart_render.py` (`render_xychart`)

---

### B. Derived / Precipitated Files (`_generated_*.py`)

| Derived File | Generator Template in `packs/mmdio-pack/templates/` | Primary Contents & Purpose |
|--------------|-----------------------------------------------------|----------------------------|
| `src/mmdio/_generated_detect_patterns.py` | `generated_detect_patterns.py.tmpl` | `GENERATED_DETECT_PATTERNS` tuple list mapping regex to diagram type ID |
| `src/mmdio/engine/_generated_enums.py` | `generated_enums.py.tmpl` | `StrEnum` classes derived from `mer:PythonEnum` facts |
| `src/mmdio/engine/_generated_fixtures.py` | `generated_fixtures.py.tmpl` | `example_*()` builder functions for tests |
| `src/mmdio/engine/_generated_models.py` | `generated_models_union.py.tmpl` | `MermaidDiagram` discriminated union type |
| `src/mmdio/engine/_generated_parser_registry.py` | `generated_parser_registry.py.tmpl` | `GENERATED_TRANSFORMERS` & `GENERATED_GRAMMAR_FILES` dictionaries |
| `src/mmdio/engine/_generated_pydantic_models.py` | `generated_models.py.tmpl` | Generated Pydantic `BaseModel` classes for ontology-defined types (`Block`, `BlockDiagram`, `Connection`, `KanbanCard`, `KanbanDiagram`, `KanbanSection`, `PieChart`, `PieSlice`, `SankeyDiagram`, `SankeyFlow`, `TimelineDiagram`, `TimelineEvent`) |
| `src/mmdio/engine/_generated_render_bodies.py` | `generated_render_bodies.py.tmpl` | Generated render functions (`render_block`, `render_kanban`, `render_pie`, `render_sankey`, `render_timeline`) |
| `src/mmdio/engine/_generated_render_dispatch.py` | `generated_render_dispatch.py.tmpl` | `GENERATED_RENDER_DISPATCH` dictionary mapping model class to render fn |
| `src/mmdio/engine/_generated_schemas.py` | `generated_schemas.py.tmpl` | `GENERATED_JSON_SCHEMAS` dict of JSON Schema definitions |
| `src/mmdio/engine/_generated_supported.py` | `generated_python_supported.py.tmpl` | `GENERATED_PYTHON_SUPPORTED` frozenset of 15 supported diagram type IDs |

---

## 3. Public APIs and Module Dependencies

### Public API Surface
1. **`mmdio` (top-level package)**:
   - `mmdio.detect_diagram_type(text: str) -> str`
2. **`mmdio.engine`**:
   - **AST Models**: `MermaidDiagram`, `FlowchartDiagram`, `FlowchartNode`, `FlowchartEdge`, `SequenceDiagram`, `SequenceParticipant`, `SequenceMessage`, `ClassDiagram`, `ClassDefinition`, `ClassMember`, `ClassMethod`, `ClassRelationship`, `StateDiagram`, `State`, `Transition`, `ERDiagram`, `Entity`, `EntityAttribute`, `ERRelationship`, `GanttChart`, `GanttTask`, `PieChart`, `PieSlice`, `GitGraph`, `GitCommit`, `GitBranch`, `C4Diagram`, `C4Element`, `C4Relationship`, `Mindmap`, `MindmapNode`, `SankeyDiagram`, `SankeyFlow`, `BlockDiagram`, `KanbanDiagram`, `TimelineDiagram`, `XYChartDiagram`.
   - **Enums**: `NodeShape`, `MessageType`, `RelationshipType`, `CardinityType`, `TaskStatus`, `C4Level`, `ParticipantType`.
   - **Parsing**: `parse_mermaid`, `parse_flowchart`, `parse_sequence`, `parse_class`, `parse_state`, `parse_er`, `parse_gantt`, `parse_pie`, `parse_git`, `parse_c4`, `parse_mindmap`, `parse_sankey`, `MermaidParser`, `ParsingError`.
   - **Rendering**: `render_diagram(diagram: MermaidDiagram) -> str`.
   - **Operations**: `merge`, `diff`, `validate_topology`.
   - **Registry**: `list_diagram_types`, `get_upstream_source`, `is_python_supported`, `DiagramTypeInfo`, `UpstreamSource`.

### Import Dependency Graph

```
mmdio.__init__
└── mmdio.detect
    └── mmdio._generated_detect_patterns

mmdio.engine.__init__
├── mmdio.engine.models
│   └── mmdio.engine._generated_models (circular via late import)
│       ├── mmdio.engine.models (11 diagram models)
│       └── mmdio.engine.types.*_models (4 diagram models)
├── mmdio.engine.parser
│   ├── mmdio.detect
│   ├── mmdio.engine.models
│   └── mmdio.engine._generated_parser_registry (circular via late import)
│       ├── mmdio.engine.parser (11 transformers)
│       └── mmdio.engine.types.*_parser (4 transformers)
├── mmdio.engine.render
│   ├── mmdio.engine.models
│   └── mmdio.engine._generated_render_dispatch (circular via late import)
│       ├── mmdio.engine.models / render (11 render fns)
│       └── mmdio.engine.types.*_render (4 render fns)
├── mmdio.engine.ops
│   └── mmdio.engine.models
└── mmdio.engine.registry
    ├── mmdio.engine.registry.ttl
    └── mmdio.engine._generated_supported
```

---

## 4. Current vs Target Derived File Landing Locations

### Current Landing Locations
Derived files generated by `ggen` currently land at:
- `src/mmdio/_generated_detect_patterns.py`
- `src/mmdio/engine/_generated_enums.py`
- `src/mmdio/engine/_generated_fixtures.py`
- `src/mmdio/engine/_generated_models.py`
- `src/mmdio/engine/_generated_parser_registry.py`
- `src/mmdio/engine/_generated_pydantic_models.py`
- `src/mmdio/engine/_generated_render_bodies.py`
- `src/mmdio/engine/_generated_render_dispatch.py`
- `src/mmdio/engine/_generated_schemas.py`
- `src/mmdio/engine/_generated_supported.py`

### Target Landing Locations (A = μ(O) Unification)
Under Requirement R1 and R2 of the original request, derived files must land directly in first-class Python source paths under `src/mmdio/engine/` without shadow duplication:

1. **AST Models & Model Union**: Precipitate directly into `src/mmdio/engine/models.py` (or a first-class `models.py` generated directly from `ontology.ttl`).
2. **Enums**: Precipitate into `src/mmdio/engine/enums.py`.
3. **Parser Registry & Transformers**: Precipitate into `src/mmdio/engine/parser_registry.py` or first-class `parser.py`.
4. **Render Dispatch & Bodies**: Precipitate into `src/mmdio/engine/render_dispatch.py` or first-class `render.py`.
5. **Detection Patterns**: Precipitate into `src/mmdio/detect_patterns.py` or directly into `detect.py`.
6. **Elimination of Shadow Files**: Remove `src/mmdio/engine/types/*` and eliminate the `_generated_*` file prefix in favor of clean, first-class Python module paths.

---

## 5. Verification Evidence

1. **`uv run pytest -W ignore`**: Passes 32 out of 32 tests (100% pass rate).
2. **`ggen sync run --dry-run`**: Executes all 10 SPARQL law gates (`010_python_support_complete.rq` through `100_classname_globally_unique.rq`) cleanly with exit code 0.
