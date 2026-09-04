# 19: Port the slice loop — write the 4 skills

**Type:** task
**Blocked by:** 08 (07, 11 resolved)
**Status:** blocked

## Question

Nothing to decide — ticket 07 settled the shape, this writes it. Same relation 14 has to 06.
Blocked by ticket 08 only because `spec-feature` writes screen specs: if 08 collapses
`experience-screens` into it, the body changes.

Write four skills into `skills/`, each `SKILL.md` under the 140-line ceiling (ticket 03),
dir name == `name:` exactly (ticket 04), `data.phase` declared by the flows not the name:

- **`spec-feature`** — the global `grilling` skill for the interview, then writes
  `_concept/experience/features/<group>/<slug>.md` + `_concept/experience/screens/<slug>/`,
  with IN/OUT/DEFER as an `## Out of Scope` section of the spec. Freezes
  `_concept/dossiers/<feature_slug>/`. Absorbs `to-spec`.
- **`build-plan`** — vertical slices with blocking edges (absorbs `to-tickets`), writing
  `_implementation/slices/<id>/plan.md`. Carries the anti-horizontal nudge from
  `plan-vertical` and the wide-refactor exception from `to-tickets`.
- **`build-implement`** — names `tdd` and `code-review`, nothing else; test / recap /
  refactor / commit as steps; freezes the slice dossier. mp's `implement` is 15 lines — the
  ceiling here is how much `_concept/` awareness genuinely has to be said.
- **`build-branch`** — branch + worktree at the start, merge / PR / keep / discard at the
  end; names `resolving-merge-conflicts`.

Also in scope:

- **Shrink `contracts/slice_loop.md`** to the slug rule + freeze lifecycle. Delete the tier
  gate and its pinned refuse message (tier is depth now), the context-isolation section (ADR
  0005), and most of the handoff-frontmatter table (one file per side).
- **Delete `contracts/plans.md`.** `PLANS.md`-the-artifact is ticket 18's call.
- Record final line counts per skill and anything that had to differ from ticket 07's shape.
