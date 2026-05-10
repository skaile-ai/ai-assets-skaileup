---
title: "impl-slice"
description: "Per-slice impl loop — runs N times: implement · test · recap · refactor · commit (scratch handoffs in _slice/<id>/)"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`impl-slice/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/impl-slice/DOMAIN.md)
:::


# impl-slice

Executes the per-slice implementation loop (repeated N times): implement, test, recap, refactor, and commit, with scratch handoffs stored in _slice/<id>/. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **impl-slice-git-prepare** (`git-prepare/`) — Prepares the git repository for a supervised implementation run: initializes git if needed, creates the implementation branch, optionally sets up a worktree.
- **impl-slice-implement** (`implement/`) — Journey-first feature orchestrator with TDD Guard; walks user journeys outside-in (hero → vital → hygiene), writes failing journey e2e tests first, delegates page-by-page implementation.
- **impl-slice-test** (`test/`) — Per-slice usability gate: runs manual checks plus automated tests from `plan.md`, captures user observations, emits a Done/NeedsMoreWork/Blocked decision.
- **impl-slice-recap** (`recap/`) — Mandatory recap step after the test gate: 1-3 sentence summary, ASCII diagram of feature flow, files-touched list, and outcome-vs-plan comparison.
- **impl-slice-refactor** (`refactor/`) — Forced-simplification pass that proposes 1-3 SMALLEST-IMPROVEMENT candidates preserving behavior; only subtractions, simplifications, clarifications.
- **impl-slice-commit** (`commit/`) — Verifies all 3 predecessor handoffs, decomposes the working tree into 1-N atomic commits with user approval, lands the commits, and clears slice scratch.
- **impl-slice-finish** (`finish/`) — Controlled branch completion after supervised implementation: presents merge / PR / keep / discard options with explicit confirmation.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.


## Skills in this domain

- [impl-slice-commit](./impl-slice-commit/) — Use when a slice has been recapped and refactored and is ready to land. Verifies all 3 predecessor handoffs (test, recap, refactor), invento
- [impl-slice-finish](./impl-slice-finish/) — Use when ending an implementation branch after all per-slice work is committed. Presents four options: merge to main, create pull request, k
- [impl-slice-git-prepare](./impl-slice-git-prepare/) — Prepare the git repository for a supervised implementation run. Initializes git if needed, creates the implementation branch, and optionally
- [impl-slice-implement](./impl-slice-implement/) — Use when implementing a single slice planned by impl-plan/plan-vertical. Reads _slice/impl/<slice_id>/plan.md, walks the vertical decomposit
- [impl-slice-implement-page](./impl-slice-implement-page/) — Page-level feature implementation with TDD Guard. Implements all features within one page using outside-in TDD: writes failing page tests, t
- [impl-slice-recap](./impl-slice-recap/) — Use when a slice has passed the per-slice test gate and needs the mandatory recap step. Produces a 1-3 sentence 'what was built' summary, an
- [impl-slice-refactor](./impl-slice-refactor/) — Use when a slice has been recapped and you need a forced-simplification pass. Proposes 1-3 SMALLEST-IMPROVEMENT candidates that preserve beh
- [impl-slice-test](./impl-slice-test/) — Use when a slice's implement step has finished and you need a per-slice usability gate before proceeding to recap. Runs manual checks + auto
