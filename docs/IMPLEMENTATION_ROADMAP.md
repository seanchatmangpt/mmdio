# mmdio Implementation Roadmap: 28 Remaining Diagram Types

## Overview

This roadmap identifies and groups the 28 remaining diagram types for implementation. Groups reflect technical similarity and dependency order, enabling parallel work.

**Source of truth:** `src/mmdio/engine/registry.ttl` (39 `mer:DiagramType` instances from mermaid-js v11.16.0, commit f0ffb41c).

## Diagram Types by Category

### Group A: Modern/High-Priority Types (Weeks 1-2)

These are newer, real-world common types with clear, documented syntax.

#### A1: Kanban
- **mermaid-js source:** Newer addition (recent versions)
- **Syntax:** Sections → Cards with swim lanes
- **Complexity:** Medium (section nesting, card properties)
- **Upstream grammar:** Jison or Langium definition in mermaid-js repo
- **Sample:** "kanban\n  section To Do\n    Task 1\n    Task 2"

#### A2: Timeline
- **mermaid-js source:** Time-series events diagram
- **Syntax:** Timeline title → dated entries
- **Complexity:** Low-Medium (date parsing, chronological ordering)
- **Sample:** "timeline\n  2022-01-01 : Event A\n  2022-01-02 : Event B"

#### A3: XYChart
- **mermaid-js source:** Scatter plot, line chart, bar chart
- **Syntax:** `xychart-beta` or `xyChart`, axes, data series
- **Complexity:** Medium (data aggregation, axis scaling)
- **Sample:** "xychart-beta\n  x-axis [1, 2, 3]\n  y-axis \"Values\" 0 → 100\n  line-series [10, 20, 30]"

#### A4: Block Diagram
- **mermaid-js source:** Hierarchical block/module composition
- **Syntax:** Blocks, connections, nested blocks
- **Complexity:** Medium (tree structure, edge routing)
- **Sample:** "block-beta\n  block A\n    block B\n      ...\n  A --> B"

### Group B: Domain-Specific Formal Types (Weeks 3-4)

Specialized diagram types with structured, well-defined syntax.

#### B1: Packet Diagram
- **mermaid-js source:** Packet/frame structure visualization
- **Syntax:** Blocks → fields with bit offsets, labels
- **Complexity:** Medium (bit-level granularity, endianness)
- **Sample:** "packet-beta\n  0-7 : Header | 8-15 : Payload | ..."

#### B2: Requirements Diagram
- **mermaid-js source:** Requirement specifications, traceability
- **Syntax:** Requirement IDs, properties (risk, verification method), relationships
- **Complexity:** Medium (structured metadata, cross-references)
- **Sample:** "requirement\n  id: REQ-001\n  text: System shall...\n  risk: High"

#### B3: ZenUML (Sequence Diagram Alternative)
- **mermaid-js source:** Compact sequence diagram notation
- **Syntax:** Actor → method calls, returns, nested interactions
- **Complexity:** Medium (similar to sequence, but different syntax)
- **Sample:** "zenuml\n  Alice->Bob: message\n  Bob->Alice: return"

#### B4: Quad Chart
- **mermaid-js source:** 2×2 quadrant diagram
- **Syntax:** Four sections, each with items/labels
- **Complexity:** Low-Medium (fixed 4-quadrant grid)
- **Sample:** "quadrant-chart\n  title Prioritization\n  Q1: High Value, Low Effort\n  ..."

### Group C: Interaction & Graph Layout Variants (Weeks 5-6)

Message/sequence diagram variants and layout modifiers for existing types.

#### C1: Message Sequence Chart Variants
- **mermaid-js source:** MSC-based diagrams (formal notation)
- **Syntax:** Actors, messages, combined fragments
- **Complexity:** High (formal trace semantics, combined fragments)
- **Sample:** "msc\n  alice, bob;\n  alice->bob : msg1;"

#### C2: Info Diagram
- **mermaid-js source:** Information/metadata display
- **Syntax:** Key-value pairs, hierarchical sections
- **Complexity:** Low (simple structure)
- **Sample:** "info\n  Version\n    1.0.0\n  License\n    MIT"

#### C3: Architecture Diagram
- **mermaid-js source:** System architecture, components, containers
- **Syntax:** Components, systems, relationships (possibly C4-derived)
- **Complexity:** Medium (similar to C4 but potentially different model)
- **Sample:** "architecture\n  system WebServer\n  system Database\n  WebServer --> Database"

#### C4: Layout Modifiers
- **mermaid-js source:** Flowchart/graph layout directives (TD, LR, RL, BT, Neutral)
- **Syntax:** `graph TD | LR | RL | BT | ...` (already in flowchart grammar, but separate type ID?)
- **Complexity:** Low (parsing already exists; may be discriminated by direction)
- **Note:** Clarify: are these separate diagram types or variants of "flowchart"? Check registry.

### Group D: Minor/Specialized Types (Weeks 7+)

Less common or edge-case diagram types.

#### D1-D8: Other Catalog Types
Review `registry.ttl` for additional types not listed above. Examples may include:
- Burndown/burnup charts
- Sankey diagram variants
- Live Sequence Chart (LSC)
- Other domain-specific variants

**Action:** Query registry for all `mer:DiagramType` instances, cross-reference with implementation checklist below.

## Implementation Checklist

### Per Type Template

```markdown
- [ ] Type ID: {diagram_id}
- [ ] Grammar extracted from upstream (commit f0ffb41c)
- [ ] Lark grammar created: src/mmdio/engine/grammars/{diagram_id}.lark
  - [ ] No LALR conflicts (`python -m mmdio.engine.parser` passes)
  - [ ] Linting passes (`ruff check`)
- [ ] Pydantic models created in src/mmdio/engine/models.py
  - [ ] Discriminated union updated
  - [ ] All properties documented
  - [ ] Type checking passes (`pyright`)
- [ ] Parser function added to src/mmdio/engine/parser.py
  - [ ] parse_{diagram_id}() function
  - [ ] AST builder helpers
  - [ ] Error handling
- [ ] Render function added to src/mmdio/engine/render.py
  - [ ] _render_{diagram_id}() function
  - [ ] Round-trip stable (parse → render → parse)
- [ ] Oracle test added to tests/test_oracle_roundtrip.py
  - [ ] Test class TestOracle{DiagramId}
  - [ ] test_{diagram_id}_simple() test method
  - [ ] Sample passes real mermaid.js validation
- [ ] Registry updated
  - [ ] mer:pythonSupport true
  - [ ] mer:grammarPath set to grammar file path
- [ ] Documentation added
  - [ ] Grammar file has example in comments
  - [ ] README lists type with ✓ status

**Dependencies:** None between types (can implement in parallel).
```

## Parallel Implementation Strategy

### Agent Dispatch Model

**Batch 1 (Group A: 4 types, Weeks 1-2)**
- Agent A1: Kanban + Timeline
- Agent A2: XYChart + Block

**Batch 2 (Group B: 4 types, Weeks 3-4)**
- Agent B1: Packet + Requirements
- Agent B2: ZenUML + Quad

**Batch 3 (Group C: 3-4 types, Weeks 5-6)**
- Agent C1: Message Sequence + Info
- Agent C2: Architecture + Layout Variants

**Batch 4 (Group D: remaining, Week 7+)**
- Discovery: Query registry, identify any untracked types
- Dispatch 1-2 agents per undiscovered type

### Synchronization

After each batch:
1. Merge all changes into `src/mmdio/engine/`
2. Run full test suite: `pytest tests/test_import.py tests/test_oracle_roundtrip.py`
3. Update registry via `ggen sync run` (if ggen mmdio-pack integration active)
4. Review diagnostics (Pyright, ruff, type checking)

### Final Verification (Week 8)

```bash
# All 39 types should report support
uv run python -c "
from mmdio.engine.registry import list_diagram_types, is_python_supported
types = list_diagram_types()
supported = [t['id'] for t in types if is_python_supported(t['id'])]
print(f'Total: {len(types)}, Supported: {len(supported)}')
assert len(supported) == 39, f'Expected 39, got {len(supported)}'
"

# All oracle tests pass
uv run pytest tests/test_oracle_roundtrip.py -v

# Core import still works without [all]
pip install -e . && python -c "from mmdio import detect_diagram_type"

# Full install works
pip install -e ".[all]" && python -c "from mmdio.engine.registry import list_diagram_types"
```

## Risk Mitigation

### Grammar Conflicts

**Risk:** LALR reduce/reduce collisions like Gantt (commit b84d9f2).

**Mitigation:**
- Test each grammar immediately after creation
- Run `python -m mmdio.engine.parser` to catch conflicts early
- Review similar upstream grammars for conflict resolution patterns

### Round-Trip Instability

**Risk:** Parse → render → parse yields different AST (e.g., due to whitespace/comment loss).

**Mitigation:**
- Explicit oracle test for each type (validates render output parses)
- Normalize whitespace in render (canonical form)
- Document which features (comments, formatting) are preserved vs. discarded

### Incomplete Type Specification

**Risk:** Upstream grammar is ambiguous or under-documented.

**Mitigation:**
- Reference actual mermaid-js rendered examples (check mermaid-js demo site)
- Run rendered samples through ggen's mermaid-pack oracle to understand expected behavior
- Communicate ambiguities in grammar comments

### Dependency Version Drift

**Risk:** mermaid-js 11.16.0 grammar differs from current version; future mermaid versions introduce incompatibilities.

**Mitigation:**
- Commit hash pinned in registry: `f0ffb41c1ee1ff667b528e86c3b082249726eeef`
- Oracle tests always validate against pinned mermaid-js 11.16.0 (hardcoded in `package.json`)
- Document pinning strategy in README

## Success Metrics

- ✓ All 39 diagram types listed in registry
- ✓ All 39 types have `mer:pythonSupport true`
- ✓ All 39 types have `.lark` grammar files
- ✓ All 39 types pass oracle validation
- ✓ Coverage ≥ 95% on engine code
- ✓ `pip install mmdio[all]` succeeds and all types are importable
- ✓ Core import `from mmdio import detect_diagram_type` works without [all]

## Timeline Summary

| Weeks | Effort | Group | Types | Status |
|-------|--------|-------|-------|--------|
| 1-2 | Batch 1 (4 agents) | A | 4 (Kanban, Timeline, XYChart, Block) | Parallel |
| 3-4 | Batch 2 (2 agents) | B | 4 (Packet, Requirements, ZenUML, Quad) | Parallel |
| 5-6 | Batch 3 (2 agents) | C | 3-4 (Message Sequence, Info, Architecture, Variants) | Parallel |
| 7+ | Batch 4 (1-2 agents) | D | Remaining (discovery phase) | Sequential discovery → Parallel impl |
| 8 | Integration + Verification | All | 39 types | Full test suite |

**Total: ~7 weeks solo, ~2-3 weeks with max parallelism (4-6 agents across batches).**

## See Also

- [Product Requirements Document (PRD)](PRD.md)
- [Architecture Requirements Document (ARD)](ARD.md)
- [Real-Time Mermaid-JS Grammar Reference](https://github.com/mermaid-js/mermaid/tree/f0ffb41c/packages/mermaid/src/parsing/mermaid)
- [mermaid-js Diagram Examples](https://mermaid.js.org/intro/)
