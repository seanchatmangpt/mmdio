# mmdio Architecture Requirements Document

## Overview

This document defines the technical architecture for completing mmdio's support for all 39 Mermaid diagram types. It describes the implementation pipeline, grammar design patterns, AST model conventions, and integration points.

## Diagram Type Inventory

**Current (11 implemented):**
flowchart, sequence, classDiagram, stateDiagram, er, gantt, pie, gitGraph, c4, mindmap, sankey

**Remaining (28 to implement):**
kanban, timeline, xychart, block, packet, requirements, zenuml, quad, message sequence (variants), info, architecture, graph layout variants, and others catalogued in `registry.ttl` as `mer:Type_*`.

**Data source:** `src/mmdio/engine/registry.ttl` (39 instances of `mer:DiagramType`, each with `diagramId`, `displayName`, `sourceUrl` pinned to mermaid-js commit f0ffb41c, MIT license).

## Implementation Pipeline

### Step 1: Grammar Extraction (Per Type)

**Input:** Real mermaid-js source (Jison .jisonlex/.jison or Langium grammar)

**Process:**
1. Read upstream grammar from mermaid-js repo at pinned commit f0ffb41c
2. Identify terminal symbols, production rules, operator precedence
3. Port to Lark EBNF (adjusting for Lark's syntax, removing Node.js-specific code)
4. Validate grammar loads without LALR conflicts (use `python -m mmdio.engine.parser` to test)

**Output:** `src/mmdio/engine/grammars/{diagram_id}.lark`

**Reference:** See `src/mmdio/engine/grammars/flowchart.lark` for pattern. Existing 11 grammars are proven templates.

### Step 2: Pydantic AST Models (Per Type)

**Pattern:** Discriminated union at base, type-specific classes below.

Example:
```python
class MermaidDiagram(BaseModel):
    type: Literal["flowchart", "sequence", ...]
    # Common fields if any

class FlowchartDiagram(MermaidDiagram):
    type: Literal["flowchart"]
    nodes: list[FlowchartNode]
    edges: list[FlowchartEdge]

class KanbanDiagram(MermaidDiagram):
    type: Literal["kanban"]
    sections: list[KanbanSection]  # new model
    cards: list[KanbanCard]         # new model
```

**Naming:** Use `{DiagramId}Diagram`, `{DiagramId}Element` (singular), `{DiagramId}Item` for consistency.

**Location:** `src/mmdio/engine/models.py` (add new classes, extend discriminated unions).

**Validation:** Pydantic validates type constraints; Lark validates syntax.

### Step 3: Parser Implementation (Per Type)

**Pattern:** One parser function per type, following existing pattern.

```python
def parse_kanban(source: str) -> KanbanDiagram:
    """Parse Kanban diagram source."""
    parser = MermaidParser("kanban")
    tree = parser.parse(source)
    return _build_kanban_ast(tree)

def _build_kanban_ast(tree) -> KanbanDiagram:
    # Transform Lark tree to Pydantic model
    sections = [_build_section(s) for s in tree.find_data("section")]
    cards = [_build_card(c) for c in tree.find_data("card")]
    return KanbanDiagram(sections=sections, cards=cards)
```

**Location:** `src/mmdio/engine/parser.py` (add type-specific parse functions).

**Error handling:** Raise `ParsingError` with source location on failure.

### Step 4: Render Implementation (Per Type)

**Pattern:** Convert Pydantic AST back to Mermaid source syntax.

```python
def _render_kanban(diagram: KanbanDiagram) -> str:
    lines = ["kanban"]
    for section in diagram.sections:
        lines.append(f"  section {section.name}")
        for card in section.cards:
            lines.append(f"    {card.title}")
    return "\n".join(lines)
```

**Location:** `src/mmdio/engine/render.py` (add to `render_diagram()` dispatcher).

**Round-trip guarantee:** `parse(render(ast))` should yield equivalent AST (modulo whitespace/comments).

### Step 5: Oracle Test (Per Type)

**Pattern:** One parametrized test class per type.

```python
class TestOracleKanban(OracleTestBase):
    def test_kanban_simple(self):
        diagram = KanbanDiagram(
            sections=[
                KanbanSection(name="To Do", cards=[
                    KanbanCard(title="Task 1")
                ])
            ]
        )
        rendered = render_diagram(diagram)
        self.assert_oracle_validates(rendered, "kanban")
```

**Location:** `tests/test_oracle_roundtrip.py` (add test class).

**Validation:** Oracle script (`tests/oracle/verify_mermaid.mjs`) calls real mermaid-js `detectType()`.

### Step 6: Registry Update

**Action:** Update `src/mmdio/engine/registry.ttl` for each implemented type.

```turtle
mer:Type_kanban
  mer:pythonSupport true ;
  mer:grammarPath "src/mmdio/engine/grammars/kanban.lark" .
```

**Automation:** ggen's `mmdio-pack/templates/registry.ttl.tmpl` regenerates this via `ggen sync run`.

## Grammar Design Patterns

### Terminal Symbols

Follow Lark conventions; leverage existing terminals where possible:

```lark
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
STRING: /"(?:\\.|[^"\\])*"/
       | /'(?:\\.|[^'\\])*'/
NUMBER: /\d+(\.\d+)?/
WS: /\s+/
%ignore WS
%ignore /%%.*$/m  // Mermaid comment syntax
```

### Production Rules

Use lowercase for rules, UPPERCASE for terminals:

```lark
diagram: "kanban"i statement*
statement: section_stmt | card_stmt
section_stmt: "section"i section_name
card_stmt: card_title (":" card_attrs)?
```

### Reduce/Reduce Conflict Resolution

**Prevention:**
- Use type-specific keywords (e.g., "milestone"i vs "task_milestone")
- Avoid overlapping terminal sets in alternative rules
- Use lookahead/context to disambiguate if needed

**Testing:** Run `python -m mmdio.engine.parser` after each grammar change to catch conflicts early.

## Pydantic Model Conventions

### Base Classes

```python
class MermaidDiagram(BaseModel):
    """Base for all diagram types."""
    type: str
    # Override per type

class MermaidElement(BaseModel):
    """Base for diagram-type-specific elements."""
    pass
```

### Discriminated Unions

```python
DiagramUnion = Annotated[
    Flowchart | Sequence | Kanban | ...,
    Field(discriminator="type")
]
```

### Optional Fields

Mark non-required fields as `Optional[T] = None` or `T | None = None`.

### Constraints

Use `Field(description="...", min_length=1)` for validation:

```python
class KanbanCard(BaseModel):
    title: str = Field(min_length=1, description="Card title, non-empty")
    priority: int = Field(ge=1, le=5, default=3)
```

## Error Handling

### ParsingError

Raised by parsers when grammar/Lark parsing fails:

```python
class ParsingError(Exception):
    def __init__(self, message: str, source: str, line: int, col: int):
        self.message = message
        self.source = source
        self.line = line
        self.col = col
```

### Validation Errors

Pydantic raises `ValidationError` on model constraint violations. Catch and re-raise as `ParsingError` if needed for consistent API.

## Testing Strategy

### Unit Tests (Per Type)

- Grammar parses valid syntax
- Grammar rejects invalid syntax
- AST models construct correctly
- Round-trip (parse → render → parse) is stable

### Oracle Tests (Per Type)

- Rendered output validates under real mermaid.js 11.16.0
- Test samples represent typical usage (at least one per type)
- Tests skip gracefully if Node.js unavailable

### Integration Tests

- All 39 types importable and usable together
- `detect_diagram_type()` returns correct type for all samples
- Core `detect.py` still has zero heavy dependencies

## Performance Considerations

**Current state:** Not optimized; focus on correctness.

**Future (post-phase 4):**
- Profile grammar compilation time (Lark lazy-loads)
- Measure AST construction overhead (Pydantic validation)
- Consider caching parsed grammars if initialization is slow

**No premature optimization in phase 1-4.**

## CI/CD Integration

### Pre-Commit

- `ruff` linting (existing)
- Lark grammar syntax check (new: `python -m mmdio.engine.parser`)
- Pyright type checking on new models

### CI Pipeline

- `pytest tests/test_import.py tests/test_oracle_roundtrip.py` (all 39 types)
- Oracle tests skip if Node unavailable; full suite passes regardless
- Coverage report for engine code (target ≥ 95%)

## Deployment & Release

### Package Updates

1. All grammar files under `src/mmdio/engine/grammars/` packaged via `uv_build` include glob
2. `registry.ttl` updated via ggen sync (reflects `mer:pythonSupport` status)
3. `pyproject.toml` version bumped (minor or major depending on breaking changes)

### Backwards Compatibility

- Existing 11 types remain unchanged in API
- New types added as new model classes (no overloads)
- Parser/render signatures stable

## Parallel Implementation Strategy

**Agent Model:** One agent per 2-3 diagram types (max 15 agents for 28 types).

**Per Agent:**
- Grammar extraction & porting (Step 1)
- AST model design (Step 2)
- Parser implementation (Step 3)
- Render implementation (Step 4)
- Oracle test (Step 5)
- Registry update (Step 6)

**Synchronization points:**
- After grammar extraction (review for conflicts before parsing)
- After AST models (review for discriminated union consistency)
- After all types complete (full test suite + integration test)

## Dependencies

- **Build:** uv, Python 3.13+
- **Runtime:** lark>=1.1.0, pydantic>=2.0.0 (for [all] extra)
- **Test:** pytest>=8.3.4, rdflib (for registry tests)
- **Dev/Oracle (not shipped):** Node.js, npm, mermaid@11.16.0, @mermaid-js/mermaid-cli@11.16.0

## Open Technical Questions

1. **Layout Modifiers:** Flowchart supports `graph TD | LR | RL | BT`. Model this as variants or inheritance?
2. **Comment Handling:** Should AST preserve Mermaid comments (`%% ...`) or discard them?
3. **Whitespace Normalization:** Round-trip render — preserve original formatting or normalize to canonical style?
4. **Error Recovery:** Should parser attempt recovery on mild syntax errors, or fail fast?

## Related Documentation

- [Product Requirements Document (PRD)](PRD.md)
- [Registry & Ontology](../src/mmdio/engine/registry.ttl)
- [Existing Grammars](../src/mmdio/engine/grammars/)
- [Gantt Grammar Fix (commit b84d9f2)](https://github.com/seanchatmangpt/mmdio/commit/b84d9f2)
- [ggen mermaid-pack reference](https://github.com/seanchatmangpt/ggen/tree/main/packs/mermaid-pack)
