# 07: Implementation-side consolidation — 16 slice skills to ~6

**Type:** grilling
**Blocked by:** 12 (02, 04 resolved)
**Status:** blocked

## Question

The three slice clusters — `08_concept-slice` (4), `11_impl-plan` (4), `12_impl-slice` (8) —
are 16 skills covering brainstorm → align → scope → design → plan → implement → test → recap
→ refactor → commit → git-finish. mp covers comparable ground with `grilling` → `to-spec` →
`to-tickets` → `implement` (which drives `tdd` and `code-review` internally), roughly 5.

Settled: map 16 → ~6, keeping the per-feature dossier (`_concept/slices/<id>/`,
`_implementation/slices/<id>/`) and the vertical-slice discipline; drop the ceremony.

Decide:

- The ~6 surviving skills, and for each of the 16, whether it merges, becomes a step inside
  another skill, or dies.
- Where the absorbed `to-spec` / `to-tickets` land: do they *replace* `plan-vertical` and the
  align/scope pair, or sit beside them?
- Whether the two dossiers (concept-side and impl-side) stay separate or become one.
- What happens to the `04_supervised` orchestrator and its 4-status subagent protocol —
  mp has no equivalent and `implement` just does the work.
- `git-prepare` / `commit` / `git-finish`: keep as skills, or fold into `implement`?
- Whether `13_impl-quality` (13 skills: test-plan, eval-code, audit, unit/integration/e2e,
  ready, standards ×3, debug ×2, review-feature) is part of this consolidation or its own
  ticket. Read ticket 02's findings on how mp composes `tdd` + `code-review` first.

## Answer

_(pending)_
