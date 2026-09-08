# Design Docs Aren't the Source Code Either

A playground case study for `mmdio`: what follows if code is a regenerable projection, but natural-language design documents are not accepted as the semantic root of truth either?

This playground starts from Kushnir et al., **Design Docs Are All You Need: An AI-native Machine-Learning Performance Tool** (arXiv:2609.05364, submitted 2026-09-04), then explicitly crosses an attribution boundary into the `mmdio`/ggen architecture.

- Paper: https://arxiv.org/abs/2609.05364
- Comparison diagram: [`paper-to-ontology.mmd`](paper-to-ontology.mmd)
- `mmdio` canonical Mermaid registry: [`../../src/mmdio/engine/registry.ttl`](../../src/mmdio/engine/registry.ttl)

## Thesis

The paper makes a consequential inversion:

**design docs → regenerated code**

instead of:

**design docs → incremental mutation of yesterday's implementation**

The next inversion explored here is:

**ontology / admitted semantic graph → regenerated projections**

instead of:

**natural-language prose → authoritative semantics**

The research question is therefore:

> If code is not the durable artifact, why should prose be?

## 1. What the paper actually establishes

The following claims belong to the paper, not to `mmdio`.

### Incremental-generation debt

For a specification `S_t` and generator `G`, a clean build is:

`C_t = G(S_t)`

The paper contrasts that with the normal incremental case in which the next generator also receives the prior implementation. It defines the resulting debt as the distance between an incrementally patched implementation and the implementation that would have been generated from the current specification alone.

The proposed remedy is full regeneration: treat natural-language design documents as the durable artifact and code as a regenerable build product.

### Regeneration architecture

The paper's reported system can be summarized as:

1. natural-language design documents,
2. a machine-discovered dependency DAG,
3. dependency-ordered traversal,
4. specialized coding sub-agents,
5. a regenerated implementation,
6. generated tests,
7. reconciliation against hand-built reference models,
8. replacement of the previous build only after reconciliation.

The authors state that humans edit the docs rather than the generated implementation.

### Enablers reported by the paper

- bounded design documents as generation units;
- a dependency DAG rather than an undifferentiated prompt pile;
- dynamic model routing, including stronger models for foundational abstractions and cheaper models downstream;
- worked examples / concrete traces to constrain semantics left ambiguous by prose;
- complete regeneration instead of incremental maintenance;
- generated code treated as disposable output;
- a small, stable symbolic IR beneath fast-changing modeled systems.

The paper reports that SMART contains 50 design docs and about 9,000 lines of specification prose. A clean regeneration reportedly takes 1.5–3 hours and about USD 100 using Claude Code.

### The paper's own semantic pressure point

The paper explicitly motivates worked examples because a concrete trace can disambiguate semantics that prose alone leaves unclear. That is evidence for a constraint on prose-as-authority: natural language is useful, but it is not self-disambiguating.

## 2. Attribution fence

The paper does **not** establish the remainder of this playground.

In particular, do not attribute these claims or mechanisms to Kushnir et al.:

- public ontologies as the semantic source of truth;
- a canonical capability graph;
- formal admission before manufacture;
- ggen precipitation from RDF/Turtle;
- SELECT / CONSTRUCT / DO separation;
- BRCE or zero-unreceipted-actuation;
- receipt-bound authority and replay;
- the Chatman Equation `A = μ(O*)`;
- deterministic ontology-driven software manufacture.

Those are the extension being tested here.

## 3. The `mmdio` extension

`mmdio` already contains a concrete upstream candidate that is stronger than prose: `src/mmdio/engine/registry.ttl` is the canonical Mermaid diagram-type registry, while the repository's original ggen architecture requires domain surfaces to precipitate from that registry rather than survive as hand-written shadow copies.

That suggests a stronger correspondence:

**public ontology → canonical graph → admission → manufacture → runtime → authorized actuation → receipt → replay**

Natural language remains valuable, but as a projection, query surface, explanation, or proposal against the graph—not as ambient semantic authority.

### Chatman Equation

`A = μ(O*)`

where:

- `O` is observed input and may be partial, stale, ambiguous, or unauthoritative;
- `O*` is the admitted, aligned, grounded, bounded semantic subject;
- `μ` is lawful manufacture;
- `A` is the manufactured artifact.

For this comparison:

- the paper makes design docs the durable `S` from which code is rebuilt;
- the `mmdio` extension asks whether ontology + formal admission can manufacture a stronger `O*` before generation begins;
- generated implementation, documentation, diagrams, tests, and APIs are projections of the admitted semantic subject rather than competing semantic roots.

## 4. Authority is a separate axis from generation

A generator being able to construct an artifact does not imply authority to perform effects.

The extension therefore separates:

- **SELECT** — choose or rank a lawful possibility;
- **CONSTRUCT** — manufacture a candidate artifact or intent;
- **DO** — actuate an effect through an explicit authority boundary.

The BRCE rule explored here is: **zero unreceipted actuation**.

Raw prose, ontology input, a planner/model response, a proof, a generated artifact, or a hook does not gain ambient DO authority merely by existing. A hook may manufacture an intent; actuation must still cross the authority boundary and produce a receipt.

## 5. Paper → `mmdio` correspondence

| Paper mechanism | `mmdio` / ggen continuation | Boundary |
| --- | --- | --- |
| Natural-language design docs | Natural-language projection over canonical semantics | Prose is not admitted merely because it is written |
| Dependency DAG | Canonical semantic/capability graph | Dependency shape must be derived or admitted |
| Worked examples | Examples + executable verification subjects | Examples constrain semantics; they do not own it |
| Minimal symbolic IR | Public ontology + bounded project ontology/registry | Vocabulary must preserve required distinctions |
| Sub-agent orchestration | Query → ggen manufacture | Planner/generator output has no ambient authority |
| Full regeneration | Disposable generated projections | Generated files are not hand-edited semantic roots |
| Generated tests | Verification evidence | Passing tests are evidence, not DO authority |
| Reference reconciliation | Formal admission + independent verifier | Admission and verification remain distinct |
| Replacement build | Release after receipts | Construction does not imply release or actuation |

The intended long-form correspondence is:

**graph → query → ggen → formal admission → runtime → BRCE → receipt → replay → release**

## 6. Combinatorial-maximalist interpretation

Regeneration removes a major source of historical coupling: yesterday's implementation no longer constrains today's design merely because it already exists.

Design for Combinatorial Maximalism pushes that further. Before irreversible selection, preserve the maximal reversible set of lawful possibilities bounded by:

- ontology,
- capability,
- authority,
- cost,
- evidence.

A failed projection is topology information, not proof that the entire graph is invalid. Unsupported is not refused; unknown is not admitted; construction is not actuation.

## 7. Operational experiment for `mmdio`

This playground proposes a falsifiable progression rather than declaring a crown:

1. Represent a bounded capability family in RDF/Turtle.
2. Derive the capability/dependency graph from the canonical representation.
3. Admit or refuse every candidate projection with explicit reasons.
4. Use ggen to manufacture Mermaid/code/docs from the admitted subject.
5. Verify generated Mermaid against the existing parser/oracle boundary.
6. Change only the canonical semantic source.
7. Regenerate from a clean output directory.
8. Prove that generated projections converge without hand-editing them.
9. If the generated subject can request an effect, route the request through the existing authority/receipt boundary rather than granting generation ambient DO authority.
10. Replay from the receipt and exact semantic subject.

### Evidence ladder

- `UNKNOWN`: proposition has not been observed.
- `PARTIAL_ALIVE`: some correspondence has executable evidence, but not the complete admitted subject.
- `ALIVE`: the exact admitted subject has been observed executing the stated contract.
- `BLOCKED`: a required transition cannot currently be executed.
- `BUILD_BROKEN`: the implementation exists but its required build/verification path fails.
- `UNSUPPORTED`: the current ontology/capability surface does not represent the requested case.

This README is a research projection. Its existence is **not** evidence that the full ontology → manufacture → authority → receipt chain is ALIVE.

## 8. Falsifiers

The stronger thesis should be rejected or narrowed if any of these survives serious attempts at repair:

1. **Semantic insufficiency** — the ontology/admission layer cannot preserve required semantics without making uncontrolled prose authoritative again.
2. **Non-reproducible manufacture** — clean regeneration depends on opaque historical implementation state or unbound model state in a way that prevents defensible replay.
3. **Projection divergence** — independently regenerated artifacts representing the same admitted subject disagree semantically beyond declared nondeterminism.
4. **Authority collapse** — generated artifacts can actuate effects without crossing the explicit authority/receipt boundary.
5. **Receipt insufficiency** — a receipt cannot bind the exact semantic subject, manufacturer/toolchain, authority decision, consequence, and replay identity required by the claim.
6. **Cost inversion** — full regeneration is more expensive, slower, or less reliable than bounded incremental manufacture for the target change regime after equivalent verification is included.

## 9. Why this belongs in `playground/`

This is deliberately not a new production ontology, runtime path, or ggen pack yet. It is a bounded research bridge between an independently published 2026 regeneration architecture and `mmdio`'s existing ontology/ggen direction.

Promotion out of `playground/` requires executable evidence against an exact admitted subject. Until then, the useful claim is narrower:

> The paper independently supports treating generated code as a disposable projection. `mmdio` supplies a concrete place to test the next inversion: whether the durable semantic artifact can move from prose to admitted machine-readable ontology without losing expressive power, verification, or governed actuation.

## Reference

Samuel Kushnir, Kimia Noorbakhsh, Kavya Sreedhar, Liqun Cheng, Ming Liu, Parthasarathy Ranganathan, Mohammad Alizadeh, Fred Kjolstad, and Suvinay Subramanian. *Design Docs Are All You Need: An AI-native Machine-Learning Performance Tool*. arXiv:2609.05364, submitted September 4, 2026. https://arxiv.org/abs/2609.05364
