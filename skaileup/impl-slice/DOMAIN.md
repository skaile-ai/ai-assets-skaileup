---
name: impl-slice
description: "Per-slice impl loop — runs N times: implement · test · recap · refactor · commit (scratch handoffs in _slice/<id>/)"
metadata:
  stage: alpha
  type: domain
---

# impl-slice

Executes the per-slice implementation loop (repeated N times): implement, test, recap, refactor, and commit, with scratch handoffs stored in _slice/<id>/.

## Skills

- **impl-slice-git-prepare** (`git-prepare/`) — Prepares the git repository for a supervised implementation run: initializes git if needed, creates the implementation branch, optionally sets up a worktree.
- **impl-slice-implement** (`implement/`) — Journey-first feature orchestrator with TDD Guard; walks user journeys outside-in (hero → vital → hygiene), writes failing journey e2e tests first, delegates page-by-page implementation.
- **impl-slice-test** (`test/`) — Per-slice usability gate: runs manual checks plus automated tests from `plan.md`, captures user observations, emits a Done/NeedsMoreWork/Blocked decision.
- **impl-slice-recap** (`recap/`) — Mandatory recap step after the test gate: 1-3 sentence summary, ASCII diagram of feature flow, files-touched list, and outcome-vs-plan comparison.
- **impl-slice-refactor** (`refactor/`) — Forced-simplification pass that proposes 1-3 SMALLEST-IMPROVEMENT candidates preserving behavior; only subtractions, simplifications, clarifications.
- **impl-slice-commit** (`commit/`) — Verifies all 3 predecessor handoffs, decomposes the working tree into 1-N atomic commits with user approval, lands the commits, and clears slice scratch.
- **impl-slice-finish** (`finish/`) — Controlled branch completion after supervised implementation: presents merge / PR / keep / discard options with explicit confirmation.

## Cross-references

- See `../../../docs/devlog/SKILL_GRAPH.md` for the catalog-level view.
