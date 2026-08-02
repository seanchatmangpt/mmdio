## 2026-08-02T07:55:02Z
<USER_REQUEST>
You are Worker 2 for Milestone M1 (Iteration 2 Remediation).
Your working directory is: /Users/sac/mmdio/.agents/worker_m1_2

Please read:
1. /Users/sac/mmdio/.agents/ORIGINAL_REQUEST.md
2. /Users/sac/mmdio/PROJECT.md
3. /Users/sac/mmdio/.agents/sub_orch_m1/SCOPE.md
4. Forensic Auditor Evidence Report: /Users/sac/mmdio/.agents/auditor_m1_1_gen2/handoff.md
5. Explorer 1 Iteration 2 Report: /Users/sac/mmdio/.agents/explorer_m1_1_r2/handoff.md
6. Explorer 2 Iteration 2 Report: /Users/sac/mmdio/.agents/explorer_m1_2_r2/handoff.md
7. Explorer 3 Iteration 2 Report: /Users/sac/mmdio/.agents/explorer_m1_3_r2/handoff.md

Your task is to remediate the Iteration 1 failure:

1. Update `packs/mmdio-pack/templates/generated_models.py.tmpl`:
   - Update `union_models` SPARQL query to join `mer:hasModel ?model . ?model a mer:PythonModel ; mer:isTopLevel true .` so that `MermaidDiagram` discriminated union only includes classes that exist.

2. Update `packs/mmdio-pack/templates/generated_render_dispatch.py.tmpl`:
   - Update `rows` SPARQL query to join `mer:hasModel ?model . ?model a mer:PythonModel ; mer:isTopLevel true .` so that render dispatch only imports existing model classes and render functions.

3. Expand RDF triples in `packs/mmdio-pack/ontology.ttl`:
   - Merge missing RDF model triples from `/Users/sac/mmdio/EXPANSION_RDF_SNIPPETS.md` into `packs/mmdio-pack/ontology.ttl` so that all 15 supported diagram types have complete `mer:hasModel` shapes.

4. Re-lock & Precipitate:
   - Run `rm -f ggen.lock && uv run ggen sync run` to lock and generate all first-class engine modules under `src/mmdio/engine/`.

5. Verification:
   - Run `uv run python -c "import mmdio.engine.models; import mmdio.engine.render_dispatch"` to verify clean Python importability.
   - Run `uv run ggen sync run --dry-run --format json` to verify exit code 0 and 0 gate violations across all 10 SPARQL law gates.
   - Run `uv run pytest` to verify clean test collection.

DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Write your detailed handoff report to `/Users/sac/mmdio/.agents/worker_m1_2/handoff.md` and send a message back when complete.
</USER_REQUEST>
