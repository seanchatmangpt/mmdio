# Handoff Report — Explorer 1 (Milestone M1: ggen Pack & Ontology Configuration)

## 1. Observation

### 1.1 Current `packs/mmdio-pack/pack.toml`
Located at `/Users/sac/mmdio/packs/mmdio-pack/pack.toml` (5 lines):
```toml
[pack]
name = "mmdio-pack"
version = "0.1.0"
description = "Generates Python wiring glue (model union, parser/grammar registration, render dispatch, python-support set, detect patterns) for mmdio diagram types from RDF facts layered onto mermaid-pack's registry.ttl. Never generates AST field definitions or parsing/rendering logic — those stay hand-authored per diagram type."
```
- **Finding**: `pack.toml` currently defines top-level pack metadata. It lacks an explicit `[targets]` configuration table mapping templates to their destination files. Instead, ggen 26.8.2 reads the target destination path from the `to:` field in the YAML frontmatter of each `.tmpl` file in `packs/mmdio-pack/templates/`.

---

### 1.2 Current Target Paths in `packs/mmdio-pack/templates/`
Running `ggen sync run --dry-run` against the repository yields 12 template output targets:

| # | Template File | Current Frontmatter `to:` Target Path | Current Category |
|---|---------------|---------------------------------------|------------------|
| 1 | `generated_detect_patterns.py.tmpl` | `"src/mmdio/_generated_detect_patterns.py"` | Shadow file |
| 2 | `generated_enums.py.tmpl` | `"src/mmdio/engine/_generated_enums.py"` | Shadow file |
| 3 | `generated_fixtures.py.tmpl` | `"src/mmdio/engine/_generated_fixtures.py"` | Shadow file |
| 4 | `generated_models.py.tmpl` | `"src/mmdio/engine/_generated_pydantic_models.py"` | Shadow file |
| 5 | `generated_models_union.py.tmpl` | `"src/mmdio/engine/_generated_models.py"` | Shadow file |
| 6 | `generated_oracle_tests.py.tmpl` | `"tests/test_oracle_generated.py"` | Test artifact |
| 7 | `generated_parser_registry.py.tmpl` | `"src/mmdio/engine/_generated_parser_registry.py"` | Shadow file |
| 8 | `generated_python_supported.py.tmpl` | `"src/mmdio/engine/_generated_supported.py"` | Shadow file |
| 9 | `generated_render_bodies.py.tmpl` | `"src/mmdio/engine/_generated_render_bodies.py"` | Shadow file |
| 10 | `generated_render_dispatch.py.tmpl` | `"src/mmdio/engine/_generated_render_dispatch.py"` | Shadow file |
| 11 | `generated_schemas.py.tmpl` | `"src/mmdio/engine/_generated_schemas.py"` | Shadow file |
| 12 | `generated_status_table.md.tmpl` | `"docs/diagram_status.md"` | Documentation |

---

### 1.3 Internal Imports and References within `.tmpl` Files
Several Tera template files hard-code internal Python import statements referencing the shadow `_generated_*` file paths:

1. **`packs/mmdio-pack/templates/generated_fixtures.py.tmpl`**:
   - Line 17: `from mmdio.engine._generated_pydantic_models import (`
   - Line 44: `from mmdio.engine._generated_enums import *`

2. **`packs/mmdio-pack/templates/generated_models.py.tmpl`**:
   - Line 43: `from mmdio.engine._generated_enums import *`

3. **`packs/mmdio-pack/templates/generated_oracle_tests.py.tmpl`**:
   - Line 34: `from mmdio.engine._generated_fixtures import (`
   - Line 39: `from mmdio.engine._generated_render_bodies import (`

4. **`packs/mmdio-pack/templates/generated_render_dispatch.py.tmpl`**:
   - Line 22: `from {{ row.modelModule }} import {{ row.modelClass }}`
   - Line 23: `from {{ row.renderModule }} import {{ row.renderFunction }}`
   (Depends on RDF facts `mer:pythonModelModule` and `mer:pythonRenderModule` in `packs/mmdio-pack/ontology.ttl`).

---

### 1.4 Downstream Consumer Imports in `src/mmdio/` and `tests/`
Searching for `_generated_` across the codebase reveals where hand-written modules currently depend on generated shadow files:
- `src/mmdio/detect.py:13`: `from mmdio._generated_detect_patterns import GENERATED_DETECT_PATTERNS`
- `src/mmdio/engine/registry.py:38`: `from ._generated_supported import GENERATED_PYTHON_SUPPORTED`
- `src/mmdio/engine/parser.py:659`: `from ._generated_parser_registry import GENERATED_TRANSFORMERS, GENERATED_GRAMMAR_FILES`
- `src/mmdio/engine/render.py:624`: `from ._generated_render_dispatch import GENERATED_RENDER_DISPATCH`
- `src/mmdio/engine/models.py:774`: `from ._generated_models import MermaidDiagram`
- `tests/test_oracle_generated.py:20`: `from mmdio.engine._generated_fixtures import (...)`
- `tests/test_oracle_generated.py:33`: `from mmdio.engine._generated_render_bodies import (...)`

---

## 2. Logic Chain

1. **From Observation 1.1 & 1.2**: ggen uses the `to:` directive in template frontmatter to decide where files precipitate. The current configuration emits 10 shadow files (`_generated_*`), which contradicts Requirement R1 ("all derived code lands in standard, first-class python paths (src/mmdio/engine/)").
2. **From Observation 1.2 & PROJECT.md contracts**: To eliminate shadow files, each template's `to:` frontmatter target must be changed from `_generated_*` to first-class Python modules under `src/mmdio/engine/`:
   - `generated_detect_patterns.py.tmpl` $\rightarrow$ `src/mmdio/engine/detect_patterns.py`
   - `generated_enums.py.tmpl` $\rightarrow$ `src/mmdio/engine/enums.py`
   - `generated_fixtures.py.tmpl` $\rightarrow$ `src/mmdio/engine/fixtures.py`
   - `generated_models.py.tmpl` $\rightarrow$ `src/mmdio/engine/models.py`
   - `generated_parser_registry.py.tmpl` $\rightarrow$ `src/mmdio/engine/parser_registry.py`
   - `generated_python_supported.py.tmpl` $\rightarrow$ `src/mmdio/engine/supported.py`
   - `generated_render_bodies.py.tmpl` $\rightarrow$ `src/mmdio/engine/render.py`
   - `generated_render_dispatch.py.tmpl` $\rightarrow$ `src/mmdio/engine/render_dispatch.py`
   - `generated_schemas.py.tmpl` $\rightarrow$ `src/mmdio/engine/schemas.py`
3. **From Observation 1.2 (`generated_models_union.py.tmpl`)**: Previously, `generated_models_union.py.tmpl` emitted `_generated_models.py` which imported models from both hand-written `models.py` and `_generated_pydantic_models.py`. In the first-class architecture, all AST model classes and the `MermaidDiagram` discriminated union precipitate directly into `src/mmdio/engine/models.py`. Therefore:
   - `generated_models.py.tmpl` should be updated to generate both all `BaseModel` AST classes and the `MermaidDiagram` discriminated union at the bottom.
   - `generated_models_union.py.tmpl` can be consolidated into `generated_models.py.tmpl` (or updated to target `models.py` if kept separate).
4. **From Observation 1.3**: Simply changing `to:` targets without updating internal template imports will cause immediate Python `ImportError` exceptions upon generation (e.g. `fixtures.py` trying to import `_generated_pydantic_models`). Thus, all internal template imports must be updated to reference `mmdio.engine.models`, `mmdio.engine.enums`, `mmdio.engine.render`, etc.
5. **From Observation 1.4**: Consumer modules in `src/mmdio/` (`detect.py`, `registry.py`, `parser.py`, `render.py`, `models.py`) and `tests/` (`test_oracle_generated.py`) will import directly from first-class engine modules (`detect_patterns`, `supported`, `parser_registry`, `render_dispatch`, `models`, `fixtures`, `render`).

---

## 3. Caveats

1. **SPARQL Gate Independence**: Evaluation of the 10 SPARQL gates in `packs/mmdio-pack/gates/` was verified. The gates query RDF triples in `src/mmdio/engine/registry.ttl` and `packs/mmdio-pack/ontology.ttl`. None of the SPARQL queries check file paths on disk, so changing `to:` targets in template frontmatter will not break gate validation.
2. **Template Consolidation for `models.py`**: `generated_models.py.tmpl` currently generates AST models, while `generated_models_union.py.tmpl` generates the `MermaidDiagram` union. If both templates target `src/mmdio/engine/models.py`, ggen will overwrite one with the other. The union generation loop must be appended to `generated_models.py.tmpl` so a single template emits `models.py`.
3. **Mindmap & Custom Renderer Handling**: As noted in `ontology.ttl`, recursive types (such as `MindmapNode`) use custom handling. Standard diagram renderers generated into `render.py` handle top-level header and structure generation.

---

## 4. Conclusion & Recommendations

### 4.1 Recommended `pack.toml` Update
Update `/Users/sac/mmdio/packs/mmdio-pack/pack.toml` to include an explicit `[targets]` section listing all template-to-first-class-module mappings and update the description:

```toml
[pack]
name = "mmdio-pack"
version = "0.1.0"
description = "Generates first-class Python engine modules (models, enums, parser_registry, render_dispatch, render, schemas, fixtures, supported, detect_patterns) for mmdio diagram types directly from RDF facts."

[targets]
detect_patterns = "src/mmdio/engine/detect_patterns.py"
enums = "src/mmdio/engine/enums.py"
fixtures = "src/mmdio/engine/fixtures.py"
models = "src/mmdio/engine/models.py"
parser_registry = "src/mmdio/engine/parser_registry.py"
supported = "src/mmdio/engine/supported.py"
render = "src/mmdio/engine/render.py"
render_dispatch = "src/mmdio/engine/render_dispatch.py"
schemas = "src/mmdio/engine/schemas.py"
oracle_tests = "tests/test_oracle_generated.py"
diagram_status = "docs/diagram_status.md"
```

---

### 4.2 Required Template Adjustments (`packs/mmdio-pack/templates/`)

#### 1. `generated_detect_patterns.py.tmpl`
- **Frontmatter**: Change `to: "src/mmdio/_generated_detect_patterns.py"` $\rightarrow$ `to: "src/mmdio/engine/detect_patterns.py"`.
- **Header**: Change `Source: packs/mmdio-pack/templates/generated_detect_patterns.py.tmpl` docstring reference.

#### 2. `generated_enums.py.tmpl`
- **Frontmatter**: Change `to: "src/mmdio/engine/_generated_enums.py"` $\rightarrow$ `to: "src/mmdio/engine/enums.py"`.

#### 3. `generated_fixtures.py.tmpl`
- **Frontmatter**: Change `to: "src/mmdio/engine/_generated_fixtures.py"` $\rightarrow$ `to: "src/mmdio/engine/fixtures.py"`.
- **Imports inside template**:
  - `before`: `from mmdio.engine._generated_pydantic_models import (`
  - `after`: `from mmdio.engine.models import (`
  - `before`: `from mmdio.engine._generated_enums import *`
  - `after`: `from mmdio.engine.enums import *`

#### 4. `generated_models.py.tmpl`
- **Frontmatter**: Change `to: "src/mmdio/engine/_generated_pydantic_models.py"` $\rightarrow$ `to: "src/mmdio/engine/models.py"`.
- **Imports inside template**:
  - `before`: `from mmdio.engine._generated_enums import *`
  - `after`: `from mmdio.engine.enums import *`
- **Union addition**: Append `MermaidDiagram` union generation loop to bottom of template:
  ```jinja2
  MermaidDiagram = (
  {% for model in models %}{% if model.isTopLevel %}    {{ model.className }} |
  {% endif %}{% endfor %}
  )
  """Union type for all supported Mermaid diagram types."""
  ```

#### 5. `generated_models_union.py.tmpl`
- **Action**: Retain or consolidate into `generated_models.py.tmpl`. (If retained, update `to:` to point to `models.py` or consolidate into `generated_models.py.tmpl`).

#### 6. `generated_oracle_tests.py.tmpl`
- **Frontmatter**: `to: "tests/test_oracle_generated.py"` (remains same file path).
- **Imports inside template**:
  - `before`: `from mmdio.engine._generated_fixtures import (`
  - `after`: `from mmdio.engine.fixtures import (`
  - `before`: `from mmdio.engine._generated_render_bodies import (`
  - `after`: `from mmdio.engine.render import (`

#### 7. `generated_parser_registry.py.tmpl`
- **Frontmatter**: Change `to: "src/mmdio/engine/_generated_parser_registry.py"` $\rightarrow$ `to: "src/mmdio/engine/parser_registry.py"`.

#### 8. `generated_python_supported.py.tmpl`
- **Frontmatter**: Change `to: "src/mmdio/engine/_generated_supported.py"` $\rightarrow$ `to: "src/mmdio/engine/supported.py"`.

#### 9. `generated_render_bodies.py.tmpl`
- **Frontmatter**: Change `to: "src/mmdio/engine/_generated_render_bodies.py"` $\rightarrow$ `to: "src/mmdio/engine/render.py"`.

#### 10. `generated_render_dispatch.py.tmpl`
- **Frontmatter**: Change `to: "src/mmdio/engine/_generated_render_dispatch.py"` $\rightarrow$ `to: "src/mmdio/engine/render_dispatch.py"`.

#### 11. `generated_schemas.py.tmpl`
- **Frontmatter**: Change `to: "src/mmdio/engine/_generated_schemas.py"` $\rightarrow$ `to: "src/mmdio/engine/schemas.py"`.

#### 12. `generated_status_table.md.tmpl`
- **Frontmatter**: `to: "docs/diagram_status.md"` (remains unchanged).

---

## 5. Verification Method

1. **Dry-Run Target Path Verification**:
   Run `ggen sync run --dry-run` from `/Users/sac/mmdio`.
   Confirm that the `skipped` / `written` list in the JSON output lists first-class module target paths under `src/mmdio/engine/` (`models.py`, `enums.py`, `parser_registry.py`, `render_dispatch.py`, `render.py`, `schemas.py`, `fixtures.py`, `supported.py`, `detect_patterns.py`) and zero `_generated_*` paths.
2. **SPARQL Law Gate Verification**:
   Confirm in the `ggen sync run --dry-run` output that all 10 SPARQL gates in `packs/mmdio-pack/gates/` pass with exit code 0 and 0 gate violations.
3. **Pytest Harness Verification**:
   Run `uv run pytest` from `/Users/sac/mmdio` to verify all tests pass against the new module structure.
