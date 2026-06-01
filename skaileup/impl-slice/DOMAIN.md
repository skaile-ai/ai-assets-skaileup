---
name: impl-slice
description: "Per-slice impl loop — runs N times: implement · test · recap · refactor · commit (phase handoffs in _implementation/slices/<id>/, frozen on commit)"
metadata:
  stage: alpha
  type: domain
---

# impl-slice

Executes one feature slice end-to-end: outside-in TDD implementation → usability gate → recap → forced simplification → atomic commits. Runs N times (once per slice) inside the `impl-plan` → `impl-slice` loop.

## Skills

- **impl-slice-git-prepare** (`git-prepare/`) — One-time setup: initializes git, creates the implementation branch, optionally sets up a worktree. Writes `.git/` and `.gitignore`.
- **impl-slice-implement** (`implement/`) — Journey-first feature orchestrator; reads `_implementation/slices/<id>/plan.md`, writes failing e2e tests first, implements UI + logic + data, persists resume state to `_implementation/slices/<id>/progress.json`.
- **impl-slice-test** (`test/`) — Per-slice usability gate; runs manual checks + automated tests from `plan.md`, captures observations, emits Done/NeedsMoreWork/Blocked to `_implementation/slices/<id>/test.md`.
- **impl-slice-recap** (`recap/`) — Mandatory post-test summary: 1-3 sentences, ASCII feature-flow diagram, files-touched list, outcome-vs-plan. Writes `_implementation/slices/<id>/recap.md`.
- **impl-slice-refactor** (`refactor/`) — Forced-simplification pass; proposes 1-3 smallest-improvement candidates (subtractions/simplifications only, no additions), requires user approval. Writes `_implementation/slices/<id>/refactor.md`.
- **impl-slice-commit** (`commit/`) — Verifies the three predecessor handoffs (test, recap, refactor), decomposes working tree into atomic commits with user approval, then freezes `_implementation/slices/<id>/` on success (writes index.md, keeps the dossier, removes only progress.json).
- **impl-slice-finish** (`finish/`) — Branch closeout: merge to main, open PR, keep branch, or discard. Refuses if any `_implementation/slices/<id>/` is not yet frozen (missing index.md).

## When to Use

- `impl-plan/plan-vertical` has produced a `plan.md` and the agent is ready to implement a specific slice.
- Project is `standard-app` or `complex-app` tier (multi-slice build).
- A previous slice run was interrupted and `_implementation/slices/<id>/progress.json` exists (resume path).
- All slices are committed and the branch needs to be closed out (`impl-slice-finish`).

## When NOT to Use

- `mvp` or `simple-app` tier — use `impl-build/` one-shot skills instead.
- Project-wide regression testing — use `impl-quality/test-{unit,integration,e2e}` instead of `impl-slice-test`.
- No `plan.md` exists yet — run `impl-plan/plan-vertical` first.

## Sequence

```
[once]  git-prepare
[×N]    implement → test → recap → refactor → commit
[once]  finish
```

Each phase reads the prior phase's handoff from `_implementation/slices/<slice_id>/`. On commit the slice is **frozen, not deleted**: an `index.md` is written and the handoffs are kept as permanent per-feature documentation (only the transient `progress.json` is removed). Truth lives in the committed codebase; the dossier is the decision record.

## Cross-references

- `../impl-plan/` — produces the `plan.md` that `impl-slice-implement` reads.
- `../impl-quality/` — project-wide quality gates (distinct from per-slice `impl-slice-test`).
- `../contracts/iron_laws.md` — user-approval requirement before any code edit (Iron Law §8).
- See `../../../docs/devlog/SKILL_GRAPH.md` for the collection-level view.
