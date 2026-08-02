# Original User Request

## 2026-08-02T03:18:37Z

Implement the ggen-driven end-to-end architecture in mmdio (A = μ(O)), unifying the codebase so that all AST models, token enums, parser registries, and render dispatchers precipitate directly from registry.ttl as first-class Python source code without shadow duplication.

Working directory: /Users/sac/mmdio
Integrity mode: development

## Requirements

### R1. First-Class ggen Code Derivation
The codebase must execute 100% of domain logic through ggen-precipitated modules. Remove hand-written shadow modules (models.py, parser.py, render.py) and replace them with first-class derived Python files generated directly from src/mmdio/engine/registry.ttl and packs/mmdio-pack/.

### R2. Pure Python Conformance & Zero Runtime Node Dependencies
The shipped mmdio Python package must be pure Python with zero runtime JS/Node dependencies, passing all law gates in packs/mmdio-pack/gates/ upon ggen sync run.

### R3. Test Oracle Roundtrip Validation
The dev/test harness must pass all unit and roundtrip oracle tests (pytest), validating rendered Mermaid diagrams against the Node-based oracle (tests/oracle/verify_mermaid.mjs) pinned to Mermaid 11.16.0.

## Acceptance Criteria

### Verification & Test Suite
- [ ] ggen sync run completes cleanly with exit code 0 and 100% gate pass rate across all 10 law gates in packs/mmdio-pack/gates/.
- [ ] uv run pytest passes 100% of test cases without deprecation warnings or import errors.
- [ ] Zero duplicate/shadow model files (models.py, _generated_*) exist; all derived code lands in standard, first-class python paths (src/mmdio/engine/).
