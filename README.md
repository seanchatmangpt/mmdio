# mmdio

**Typed, receipt-bearing Mermaid I/O for the complete 39-type mmdio catalog.**

`mmdio` admits Mermaid source into explicit Pydantic document classes, preserves a lossless concrete syntax tree, canonicalizes deterministically, renders without semantic loss, issues tamper-evident receipts, and replays the exact admitted subject.

## What is executable

The capability registry contains 39 types. Every type has:

- an explicit Python document class;
- exact header detection with no unknown-to-flowchart fallback;
- lossless line and token spans;
- deterministic canonical rendering;
- JSON Schema;
- receipt verification and replay;
- a first-party example executed against Mermaid JavaScript `11.16.0` in CI.

The original eleven domain-specific Pydantic ASTs remain available as additional projections. They are no longer the support ceiling.

## Python

```python
from mmdio import issue_receipt, parse_document, render_document, verify_receipt

source = """cynefin-beta
  clear
    "Apply known fix"
"""

document = parse_document(source)
assert document.type == "cynefin"
assert render_document(document) == source

receipt = issue_receipt(document)
assert verify_receipt(receipt) == document
```

`parse_mermaid(source)` and `parse_document(source, diagram_type=...)` both return the uniform all-dialect document contract. `parse_structured_mermaid(source)` explicitly requests one of the optional legacy deep AST projections and requires its Lark grammar to admit the source.

## CLI

```sh
mmdio types
mmdio detect architecture.mmd
mmdio parse architecture.mmd
mmdio validate architecture.mmd --receipt architecture.receipt.json
mmdio format architecture.mmd --check
mmdio replay architecture.receipt.json
mmdio diff left.mmd right.mmd
mmdio merge base.mmd left.mmd right.mmd
mmdio schema cynefin
```

All machine-facing commands emit deterministic JSON. Refusals carry stable `MMDIO-*` codes and exit with a non-zero status.

## REST API

```sh
uvicorn mmdio.api:app
```

Primary routes:

- `GET /health`
- `GET /v1/capabilities`
- `POST /v1/detect`
- `POST /v1/parse`
- `POST /v1/canonicalize`
- `POST /v1/validate`
- `POST /v1/diff`
- `POST /v1/merge`
- `POST /v1/receipts/verify`

## Capability families

| Family | Registered types |
|---|---|
| Graph and architecture | `flowchart`, `flowchart-v2`, `flowchart-elk`, `swimlane`, `block`, `architecture`, `treeView`, `c4` |
| Software and data | `classDiagram`, `classDiagram-v2`, `stateDiagram`, `stateDiagram-v2`, `sequence`, `er`, `requirement`, `gitGraph`, `zenuml` |
| Planning and narrative | `gantt`, `timeline`, `journey`, `kanban`, `mindmap`, `eventmodeling` |
| Quantitative | `pie`, `quadrantChart`, `xychart`, `sankey`, `radar`, `treemap`, `venn` |
| Analysis and strategy | `ishikawa`, `wardley`, `cynefin` |
| Protocol and grammar | `packet`, `railroad`, `railroad-ebnf`, `railroad-abnf`, `railroad-peg`, `info` |

## Verification

```sh
PYTHONPATH=src python scripts/verify_universal_projection.py
PYTHONPATH=src pytest
node tests/oracle/catalog_oracle.mjs _oracle/mermaid
```

The JavaScript oracle is a development verifier, not an ambient execution authority. The Python runtime does not invoke Node. CI pins Mermaid `11.16.0`; ZenUML is registered through its official Mermaid plugin package.

## Architecture

```text
Mermaid source
→ typed admission/refusal
→ exact 39-class lossless CST
→ canonical render
→ SHA-256 receipt
→ replay

                         ↘ Mermaid 11.16.0 JS oracle in validation only
```

See [All-diagram capabilities](docs/all-diagram-capabilities.md) for the claim boundary and verifier design.
