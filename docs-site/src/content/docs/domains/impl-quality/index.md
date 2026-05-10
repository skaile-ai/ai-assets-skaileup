---
title: "impl-quality"
description: "test-{plan,unit,integration,e2e} · eval-code · audit · ready · standards-* · debug-{self-verify, handoff}"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`impl-quality/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/impl-quality/DOMAIN.md)
:::


# impl-quality

Covers all quality assurance concerns: test planning, unit/integration/e2e tests, code evaluation, audits, readiness checks, standards enforcement, and debug handoffs. Phase 1 stub — see SKILL_GRAPH.md §1.

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

- See `../SKILL_GRAPH.md` for the catalog-level view.


## Skills in this domain

- [impl-quality-audit](./impl-quality-audit/) — Static code audit. Launches three parallel sub-agents for logic errors, UI/UX issues, and security concerns. Also checks _concept/ structure
- [impl-quality-debug-handoff](./impl-quality-debug-handoff/) — Use when the user is stuck on a bug and wants to hand off to a fresh agent (or themselves after /clear). Produces a self-contained markdown 
- [impl-quality-debug-self-verify](./impl-quality-debug-self-verify/) — Use when the user is stuck on a bug and wants the AI to autonomously verify whether a fix worked. Produces a self-runnable verification prot
- [impl-quality-eval-code](./impl-quality-eval-code/) — Code quality evaluator. Verifies build passes, then dispatches three parallel sub-agents for logic errors, security vulnerabilities, and UI/
- [impl-quality-ready](./impl-quality-ready/) — Pre-flight readiness check before E2E testing. Verifies that each feature has a concept doc, screen spec, data model entry, brand tokens, an
- [impl-quality-standards-discover](./impl-quality-standards-discover/) — Use when analyzing an existing codebase to extract conventions, patterns, and standards. Triggered when user says 'discover standards', 'ana
- [impl-quality-standards-inject](./impl-quality-standards-inject/) — Use before dispatching a skill to load applicable codebase standards. Called by orchestrator or as first step in standalone skill execution.
- [impl-quality-standards-sync](./impl-quality-standards-sync/) — Use when pushing proven project standards back to profiles, or syncing profile standards into a project. Triggered by 'sync standards', 'upd
- [impl-quality-test-e2e](./impl-quality-test-e2e/) — End-to-end browser testing. Reads screen specs, features, and data model from _concept/. Uses agent-browser to test every user journey, take
- [impl-quality-test-integration](./impl-quality-test-integration/) — Use when you need integration tests that verify API endpoints, data flow, and cross-feature interactions against a real database. Reads feat
- [impl-quality-test-plan](./impl-quality-test-plan/) — Use when you need a comprehensive test plan derived from concept specs. Generates test scenarios per feature covering happy paths, error sta
- [impl-quality-test-unit](./impl-quality-test-unit/) — Use when you need unit test files generated from feature specs. Reads existing source code patterns and feature requirements, then produces 
