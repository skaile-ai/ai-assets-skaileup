---
title: "impl-quality"
description: "test-{plan,unit,integration,e2e} · eval-code · audit · ready · standards-* · debug-{self-verify, handoff}"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`skaileup/impl-quality/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/impl-quality/DOMAIN.md)
:::


# impl-quality

Produces test artifacts, code evaluations, and debug outputs that gate each impl-slice before commit. Agents call into this domain to verify correctness, enforce standards, and unblock stuck bugs.

## Skills

- **impl-quality-test-plan** (`test-plan/`) — Reads `_concept/experience/features/` and writes `_concept/testing/test_plan.md` with per-feature scenarios (happy path, error states, edge cases, permissions).
- **impl-quality-test-unit** (`test-unit/`) — Reads feature specs + `_concept/testing/test_plan.md`, writes one unit test file per feature following existing source patterns.
- **impl-quality-test-integration** (`test-integration/`) — Generates API endpoint and cross-feature integration tests against a real database from feature specs and data model.
- **impl-quality-test-e2e** (`test-e2e/`) — Runs every user journey via agent-browser, writes `e2e-screenshots/**/*.png` and optional `e2e-test-report.md`.
- **impl-quality-eval-code** (`eval-code/`) — Verifies build then dispatches three parallel sub-agents (logic, security, UI/UX); writes `_implementation/eval-code.json`.
- **impl-quality-audit** (`audit/`) — Static audit via three parallel sub-agents; also checks `_concept/` structure integrity; writes optional `audit-report.md`.
- **impl-quality-ready** (`ready/`) — Read-only pre-flight check: every feature must have concept doc, screen spec, data model entry, brand tokens, and tech stack before E2E can run.
- **impl-quality-standards-discover** (`standards-discover/`) — Analyzes an existing codebase; writes one `.md` per convention to `_concept/_standards/{domain}/` and generates `_concept/_standards/index.yml`.
- **impl-quality-standards-inject** (`standards-inject/`) — Reads `_concept/_standards/index.yml` and returns matched standards to the calling skill before execution.
- **impl-quality-standards-sync** (`standards-sync/`) — Pushes proven project standards back to shared profiles, or pulls profile standards into `_concept/_standards/`.
- **impl-quality-debug-self-verify** (`debug-self-verify/`) — Writes `_debug/<id>/protocol.md`: test commands + expected outputs + success criteria the AI runs autonomously.
- **impl-quality-debug-handoff** (`debug-handoff/`) — Writes `_debug/<id>/handoff.md`: bug description, attempts, hypothesis, and next steps pasteable into a fresh chat.

## When to Use

- After each impl-slice commit: run `eval-code` (scope `feature`) to gate the slice.
- Before E2E: run `ready` to surface missing concept artifacts, then `test-plan` if no plan exists.
- When onboarding to an existing repo: run `standards-discover` first, then `standards-inject` wraps subsequent skills automatically.
- When stuck on a bug past two attempts: pick `debug-self-verify` (autonomous fix loop) or `debug-handoff` (escalate to new context).

## When NOT to Use

- Do not call `test-e2e` before `ready` passes — it will fail on missing specs.
- Do not use `audit` as a substitute for `eval-code`; audit is structural/static, eval-code runs the build and tests.
- Standards skills are no-ops when `_concept/_standards/` does not exist; run `standards-discover` first on legacy repos.

## Sequence

```
standards-discover (once, existing repos)
    └── standards-inject (wraps every skill call)

test-plan → test-unit → test-integration → ready → test-e2e
                                              └── eval-code (scope: full)

audit (ad-hoc or pre-release)
debug-self-verify | debug-handoff (on-demand)
```

## Cross-references

- `../impl-slice/` — quality gates are checkpoints inside the slice loop.
- `../contracts/concept_structure.md` — canonical `_concept/` paths all skills read from.
- `../impl-architecture/` — tech stack and data model that test-plan and test-unit depend on.


## Skills in this domain

- [impl-quality-audit](./impl-quality-audit/) — Use before e2e testing or after significant code changes to run a static audit. Launches three parallel sub-agents for logic errors, UI/UX i
- [impl-quality-debug-handoff](./impl-quality-debug-handoff/) — Use when the user is stuck on a bug and wants to hand off to a fresh agent (or themselves after /clear). Produces a self-contained markdown 
- [impl-quality-debug-self-verify](./impl-quality-debug-self-verify/) — Use when the user is stuck on a bug and wants the AI to autonomously verify whether a fix worked. Produces a self-runnable verification prot
- [impl-quality-eval-code](./impl-quality-eval-code/) — Use when a pipeline checkpoint is reached (after scaffold, after each feature group, or before release) to evaluate code quality. Verifies b
- [impl-quality-ready](./impl-quality-ready/) — Use before E2E testing to verify all features are complete enough to test. Checks each feature for concept doc, screen spec, data model entr
- [impl-quality-standards-discover](./impl-quality-standards-discover/) — Use when analyzing an existing codebase to extract conventions, patterns, and standards. Triggered when user says 'discover standards', 'ana
- [impl-quality-standards-inject](./impl-quality-standards-inject/) — Use before dispatching a skill to load applicable codebase standards. Called by orchestrator or as first step in standalone skill execution.
- [impl-quality-standards-sync](./impl-quality-standards-sync/) — Use when pushing proven project standards back to profiles, or syncing profile standards into a project. Triggered by 'sync standards', 'upd
- [impl-quality-test-e2e](./impl-quality-test-e2e/) — Use when all features are implemented and you need full end-to-end browser testing. Reads screen specs, features, and data model from _conce
- [impl-quality-test-integration](./impl-quality-test-integration/) — Use when you need integration tests that verify API endpoints, data flow, and cross-feature interactions against a real database. Reads feat
- [impl-quality-test-plan](./impl-quality-test-plan/) — Use when you need a comprehensive test plan derived from concept specs. Generates test scenarios per feature covering happy paths, error sta
- [impl-quality-test-unit](./impl-quality-test-unit/) — Use when you need unit test files generated from feature specs. Reads existing source code patterns and feature requirements, then produces 
