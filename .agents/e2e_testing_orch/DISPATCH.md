# Dispatch Instructions

## 2026-08-02T03:23:06Z

You are the E2E Testing Track Orchestrator for project mmdio.
Working directory: /Users/sac/mmdio/.agents/e2e_testing_orch
Parent conversation ID: 6de8ecac-903b-46e8-a7b9-a9fd81e64328

Your mission:
1. Read /Users/sac/mmdio/.agents/ORIGINAL_REQUEST.md and /Users/sac/mmdio/PROJECT.md.
2. Initialize SCOPE.md, BRIEFING.md, and progress.md in your working directory.
3. Design and build a comprehensive requirement-driven, opaque-box E2E test suite covering all requirements (R1, R2, R3) and features in PROJECT.md.
4. Follow the 4-tier test case methodology (Tier 1: Feature Coverage >=5 per feature, Tier 2: Boundary & Corner Cases >=5 per feature, Tier 3: Cross-Feature Combinations, Tier 4: Real-World Scenarios).
5. Create TEST_INFRA.md and publish TEST_READY.md at project root (/Users/sac/mmdio/TEST_READY.md) when the test harness & cases are fully established.
6. Dispatch test_writer or worker subagents as needed to implement test cases in tests/.
7. Report progress and completion back via send_message to orchestrator.
