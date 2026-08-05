# All-diagram capabilities

## Claim

`mmdio` executes the complete 39-type catalog as typed, lossless concrete syntax documents. Each admitted document binds:

- canonical diagram identity;
- an exact generated Pydantic class;
- source line, indentation, lexical category, token, and column spans;
- canonical source bytes and SHA-256 identity;
- deterministic render, receipt, and replay.

This is not a claim that all Mermaid dialects share one domain ontology. The universal CST preserves every reversible source possibility. Dialect-specific semantic projections may be layered above it without changing the carrier identity.

## Admission

Unknown headers are refused as `MMDIO-TYPE-002`; they are never coerced to flowchart. A declared type that conflicts with detected syntax is refused as `MMDIO-TYPE-003`, except for admitted profiles:

- `flowchart-v2`;
- `flowchart-elk`;
- `swimlane`;
- `classDiagram-v2`;
- `stateDiagram-v2`.

Profiles bind a distinct mmdio capability identity to syntax parsed by a canonical Mermaid family. For example, `flowchart-elk` uses ordinary flowchart syntax with the ELK renderer configuration; swimlanes are expressed as flowchart subgraphs.

## JavaScript oracle

The exact-head workflow checks out the upstream Mermaid source tag `mermaid@11.16.0`. It extracts the first-party example for each native dialect, executes `mermaid.parse`, sends the same bytes through the Python CLI, and verifies canonical replay.

ZenUML is not silently treated as a built-in Mermaid grammar. The oracle installs and registers `@mermaid-js/mermaid-zenuml@0.2.3`, matching Mermaid's documented plugin boundary.

The oracle is validation-only. JavaScript output has no ambient authority to mutate the repository or execute mmdio operations.

## Generated correspondence

```text
registry.ttl
× ontology.ttl
× universal-capabilities.ttl
→ generated documents.py
→ supported.py
→ engine public surface
→ Python fixtures and refusal tests
→ Mermaid JavaScript oracle
→ exact-head workflow receipt
```

`ggen sync run` remains the canonical regeneration command. When `ggen` is unavailable, authored source and projections must be changed together and `scripts/verify_universal_projection.py` must prove exact set equality. Absence of the `ggen` executable must never be reported as a regeneration success.

## Falsifiers

The all-diagram claim is false if any of these occurs:

1. the registry, capability ontology, supported set, or document-class map differs from 39;
2. a registered header falls through to another type;
3. canonical render changes an admitted source statement;
4. a receipt or source mutation verifies;
5. Mermaid `11.16.0` refuses a claimed first-party fixture;
6. ZenUML passes without its official plugin being registered;
7. the exact workflow head differs from the pull-request head.
