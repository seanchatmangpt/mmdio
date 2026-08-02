# mmdio Product Requirements Document

## Vision

Establish mmdio as a **pure-Python reference implementation** of the Mermaid diagram specification, achieving feature parity with the upstream mermaid-js parser across all real, production-grade diagram types.

**Success metric:** All 39 diagram types from the upstream mermaid-js catalog (v11.16.0, commit f0ffb41c...) are parseable and renderable in mmdio, validated against real upstream mermaid-js via the test oracle.

## Current State

- **Implemented:** 11 diagram types (flowchart, sequence, classDiagram, stateDiagram, er, gantt, pie, gitGraph, c4, mindmap, sankey)
- **Baseline:** Lark EBNF grammars, Pydantic models, parser/render round-trip, oracle validation working
- **Missing:** 28 diagram types (kanban, timeline, xychart, block, packet, requirements, zenuml, quad, message sequence variants, info, architecture, and others)

## Requirements

### R1: Full Diagram Type Coverage

**Requirement:** Implement parsing and rendering for all 39 diagram types catalogued in the upstream mermaid-js ontology (stored in `src/mmdio/engine/registry.ttl`).

**Acceptance Criteria:**
- Each diagram type has a `.lark` grammar file under `src/mmdio/engine/grammars/`
- Each type has corresponding Pydantic model classes in the engine
- `registry.ttl` marks each type with `mer:pythonSupport true` and a valid `mer:grammarPath`
- Oracle test validates at least one sample per type against real mermaid.js 11.16.0
- All 39 types return `is_python_supported(type_id) == True`

### R2: Grammar Fidelity

**Requirement:** Grammars accurately reflect the real upstream Mermaid syntax, not simplified or aspirational versions.

**Acceptance Criteria:**
- Each grammar is ported from real mermaid-js source (Jison/Langium definitions)
- Grammar passes oracle validation: rendered output parses under real `mermaid.detectType()`
- No grammar accepts invalid syntax (false positives)
- LALR/reduce-reduce conflicts resolved (like Gantt fix in commit b84d9f2)

### R3: API Consistency

**Requirement:** All diagram types expose a consistent AST → render → source round-trip.

**Acceptance Criteria:**
- All types follow the `MermaidDiagram` base model pattern
- All types are renderable via `render_diagram(diagram_instance)`
- Render output re-parses to equivalent AST (round-trip stability)
- Type-specific operations (e.g., `merge` for flowchart, `validate_topology`) extend the base without breaking it

### R4: Test Coverage

**Requirement:** Oracle validation proves correctness against the real parser.

**Acceptance Criteria:**
- `tests/test_oracle_roundtrip.py` includes at least one passing test per diagram type
- Each test constructs a sample AST → renders → validates against mermaid.js 11.16.0
- Tests gracefully skip if Node.js unavailable (no failures in pure-Python CI)
- Coverage report shows all 39 types with ≥ 1 passing oracle test

### R5: Pure Python Distribution

**Requirement:** Shipped package has zero runtime JavaScript or Node.js dependencies.

**Acceptance Criteria:**
- `pip install mmdio` works on any Python 3.13+ system without npm
- Core `detect_diagram_type()` has zero heavy dependencies
- Full engine available via `pip install 'mmdio[all]'` with only `lark`, `pydantic`, `rdflib`
- Node-based oracle remains dev/test-only (not shipped)

### R6: Documentation

**Requirement:** Clear, actionable documentation for each diagram type.

**Acceptance Criteria:**
- README lists all 39 types with implementation status
- Each diagram type has example syntax in the grammar file comments
- Architecture guide explains the AST → grammar → render pipeline
- Implementation guide outlines how to add a new type (for future variants)

## Timeline & Phasing

### Phase 1: High-Volume Types (Weeks 1-2)
Kanban, timeline, xychart, block — these are newer, real-world common types.

### Phase 2: Specialized Formal Types (Weeks 3-4)
Packet, requirements, zenuml, quad — domain-specific, more structured syntax.

### Phase 3: Message & Interaction Types (Weeks 5-6)
Message sequence chart variants, info, architecture, and others — derived or less common.

### Phase 4: Edge Cases & Variants (Week 7)
Capture any missed types, stress-test round-trip stability, finalize coverage.

## Success Criteria (Hard Stop)

1. ✓ All 39 diagram types listed in `registry.ttl` have `mer:pythonSupport true`
2. ✓ All 39 types have `.lark` files and corresponding Pydantic models
3. ✓ All 39 types pass oracle validation (real mermaid-js parse roundtrip)
4. ✓ Full test suite passes (coverage ≥ 95% on engine code)
5. ✓ `pip install 'mmdio[all]'` works, core import works without [all]

## Out of Scope

- **Performance optimization:** Prioritize correctness; optimize after all types work
- **Custom Mermaid extensions:** Stick to the standard 39 types from upstream
- **JavaScript code generation:** mmdio generates Mermaid source, not JS
- **SVG/image rendering:** Oracle validates syntax; rendering to SVG stays optional

## Open Questions / Future Work

1. **Variants:** Some types (e.g., graph layouts: TD, LR, RL, BT) are layout modifiers, not separate types. Clarify inheritance model.
2. **Deprecated types:** Mermaid-js has deprecated syntax in some types (e.g., old class diagram syntax). Decide: support both or align with current upstream only?
3. **Performance gates:** Once all types work, consider optimization (AST caching, grammar compilation, etc.)

## Related Documents

- [Architecture Requirements Document (ARD)](ARD.md)
- [Registry & Provenance](../src/mmdio/engine/registry.ttl)
- [ggen mermaid-pack (upstream source)](https://github.com/seanchatmangpt/ggen/tree/main/packs/mermaid-pack)
