## 2026-08-02T07:50:10Z

You are test_writer_tier4_m4 (teamwork_preview_test_writer).
Your working directory is /Users/sac/mmdio/.agents/test_writer_tier4_m4. Create this directory if it doesn't exist.

Context files:
- /Users/sac/mmdio/.agents/ORIGINAL_REQUEST.md
- /Users/sac/mmdio/PROJECT.md
- /Users/sac/mmdio/.agents/spec_miner_e2e_m1/spec_analysis.md
- /Users/sac/mmdio/TEST_INFRA.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your Mission:
1. Create tests/e2e/test_tier4_real_world_scenarios.py implementing Tier 4 Real-World Application Scenario tests (>=10 test cases):
   - Scenario 1: Microservices Architecture C4 Context Diagram (parse, AST modify, render, oracle verify).
   - Scenario 2: Git Feature Branch & Release Workflow (parse, AST modify, render, oracle verify).
   - Scenario 3: Complex Project Gantt Schedule with Milestones and Dependencies.
   - Scenario 4: E-Commerce Database Entity-Relationship Schema.
   - Scenario 5: Agile Sprint Kanban Project Board with Card Columns.
   - Scenario 6: Product Roadmap Timeline with Milestones.
   - Scenario 7: Financial Data XY Chart (bar & line series).
   - Scenario 8: Enterprise System Sequence Diagram with Autonumber & Participants.
   - Scenario 9: Supply Chain Sankey Flow Network.
   - Scenario 10: Multi-Module Software Class Hierarchy with Inheritance & Associations.
2. Run `uv run pytest tests/e2e/test_tier4_real_world_scenarios.py` to verify all test cases pass.
3. Document your results in /Users/sac/mmdio/.agents/test_writer_tier4_m4/handoff.md and report completion.
