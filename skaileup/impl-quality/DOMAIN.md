---
name: impl-quality
description: "test-{plan,unit,integration,e2e} · eval-code · audit · ready · standards-* · debug-{self-verify, handoff}"
metadata:
  stage: alpha
  type: domain
---

# impl-quality

Covers all quality assurance concerns: test planning, unit/integration/e2e tests, code evaluation, audits, readiness checks, standards enforcement, and debug handoffs.

## Skills

- **impl-quality-test-plan** (`test-plan/`) — Comprehensive test plan derived from concept specs; generates per-feature scenarios for happy paths, error states, edge cases, and permissions, mapped to seed data.
- **impl-quality-test-unit** (`test-unit/`) — Generates unit test files from feature specs; one test file per feature with cases mapped to requirements, following existing source patterns.
- **impl-quality-test-integration** (`test-integration/`) — Integration tests that verify API endpoints, data flow, and cross-feature interactions against a real database.
- **impl-quality-test-e2e** (`test-e2e/`) — End-to-end browser testing using agent-browser; runs every user journey, takes screenshots, and validates database records.
- **impl-quality-eval-code** (`eval-code/`) — Code quality evaluator: verifies build, then dispatches three parallel sub-agents for logic errors, security vulnerabilities, and UI/UX code concerns.
- **impl-quality-audit** (`audit/`) — Static code audit with three parallel sub-agents (logic, UI/UX, security); also checks `_concept/` structure integrity.
- **impl-quality-ready** (`ready/`) — Pre-flight readiness check before E2E testing; verifies each feature has concept doc, screen spec, data model entry, brand tokens, and tech stack.
- **impl-quality-standards-discover** (`standards-discover/`) — Analyzes an existing codebase to extract conventions, patterns, and standards.
- **impl-quality-standards-inject** (`standards-inject/`) — Loads applicable codebase standards before dispatching a skill; reads `_concept/_standards/index.yml` and returns matched standards.
- **impl-quality-standards-sync** (`standards-sync/`) — Pushes proven project standards back to profiles, or syncs profile standards into a project.
- **impl-quality-debug-self-verify** (`debug-self-verify/`) — Produces a self-runnable verification protocol (test commands + expected outputs + success criteria) the AI executes without using the user as a test loop.
- **impl-quality-debug-handoff** (`debug-handoff/`) — Produces a self-contained markdown summary (bug, attempts, hypothesis, suggested next steps) pasteable into a fresh chat with no prior context.

## Cross-references

- See `../../../docs/devlog/SKILL_GRAPH.md` for the catalog-level view.
