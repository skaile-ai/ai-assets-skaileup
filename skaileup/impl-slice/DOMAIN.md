---
name: impl-slice
description: "Per-slice impl loop — runs N times: implement · test · recap · refactor · commit (scratch handoffs in _slice/<id>/)"
metadata:
  stage: alpha
  type: domain
---

# impl-slice

Executes one feature slice end-to-end: outside-in TDD implementation → usability gate → recap → forced simplification → atomic commits. Runs N times (once per slice) inside the `impl-plan` → `impl-slice` loop.

## Skills

- **impl-slice-git-prepare** (`git-prepare/`) — One-time setup: initializes git, creates the implementation branch, optionally sets up a worktree. Writes `.git/` and `.gitignore`.
- **impl-slice-implement** (`implement/`) — Journey-first feature orchestrator; reads `_slice/impl/<id>/plan.md`, writes failing e2e tests first, implements UI + logic + data, persists resume state to `_slice/impl/<id>/progress.json`.
- **impl-slice-test** (`test/`) — Per-slice usability gate; runs manual checks + automated tests from `plan.md`, captures observations, emits Done/NeedsMoreWork/Blocked to `_slice/impl/<id>/test.md`.
- **impl-slice-recap** (`recap/`) — Mandatory post-test summary: 1-3 sentences, ASCII feature-flow diagram, files-touched list, outcome-vs-plan. Writes `_slice/impl/<id>/recap.md`.
- **impl-slice-refactor** (`refactor/`) — Forced-simplification pass; proposes 1-3 smallest-improvement candidates (subtractions/simplifications only, no additions), requires user approval. Writes `_slice/impl/<id>/refactor.md`.
- **impl-slice-commit** (`commit/`) — Verifies the three predecessor handoffs (test, recap, refactor), decomposes working tree into atomic commits with user approval, then deletes `_slice/impl/<id>/` on success.
- **impl-slice-finish** (`finish/`) — Branch closeout: merge to main, open PR, keep branch, or discard. Refuses if any `_slice/impl/<id>/` scratch dirs remain.

## When to Use

- `impl-plan/plan-vertical` has produced a `plan.md` and the agent is ready to implement a specific slice.
- Project is `standard-app` or `complex-app` tier (multi-slice build).
- A previous slice run was interrupted and `_slice/impl/<id>/progress.json` exists (resume path).
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

Each phase reads the prior phase's scratch file from `_slice/impl/<slice_id>/`. Scratch is deleted on commit; truth lives in the committed codebase.

## Cross-references

- `../impl-plan/` — produces the `plan.md` that `impl-slice-implement` reads.
- `../impl-quality/` — project-wide quality gates (distinct from per-slice `impl-slice-test`).
- `../contracts/iron_laws.md` — user-approval requirement before any code edit (Iron Law §8).
- See `../../../docs/devlog/SKILL_GRAPH.md` for the collection-level view.
