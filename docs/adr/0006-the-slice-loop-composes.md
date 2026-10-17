# 0006 — The slice loop is four skills, and they compose rather than restate

**Status:** accepted

## Context

The old collection covers brainstorm → align → scope → design → plan → implement → test →
recap → refactor → commit → finish with **16 skills across three clusters** —
`08_concept-slice` (4), `11_impl-plan` (4), `12_impl-slice` (8) — **4,166 lines**.

The mattpocock collection covers comparable ground with `grilling` → `to-spec` →
`to-tickets` → `implement`. Its `implement` is **15 lines**, and it spends them naming `tdd`
and `code-review` rather than explaining either. That is the whole difference: the old
collection restates at every phase what the phase before it already established, and each
restatement is a skill.

Three facts sharpened the shape:

- **Four of the 16 are the same interview run four times** — brainstorm and align on both
  sides. `grilling` is a global install; a skill that re-teaches interviewing competes with it.
- **ADR 0005 made the boundaries inside each loop warm.** The per-phase handoff files
  (`brainstorm.md` → `align.md` → `scope.md`) existed to survive a `/clear` that no longer
  happens.
- **Tier routed to a different *entry skill* per tier** (`slice_loop.md`'s table: mvp →
  `plan-vertical`, simple → `align`, standard/complex → `brainstorm`), behind a pinned refuse
  message. That table only means something while there is more than one entry.

## Decision

**Four skills: `spec-feature` · `build-plan` · `build-implement` · `build-branch`.**

- **`spec-feature`** calls the global `grilling` skill, then writes the feature spec and its
  screen specs. `to-spec` *is* this skill; the one split mp makes — interview, then synthesise
  without interviewing — is the only split the concept side needs.
- **`build-plan`** is `to-tickets`: vertical slices with blocking edges.
- **`build-implement`** names **`tdd` and `code-review`, and nothing else**. Test, recap,
  refactor and commit are steps in it.
- **`build-branch`** is the bookend: branch and worktree at the start, merge / PR / keep /
  discard at the end. It names `resolving-merge-conflicts`.

**The test pyramid stays outside.** `quality-test-{unit,integration,e2e}` are flow nodes
after the slice, not calls from inside `build-implement` — a slice should not drag the whole
pyramid, and the quality domain keeps the freedom to reshape them.

**Two skills die outright rather than merge.** `impl-plan-supervised` (a subagent
orchestrator with a four-status protocol) is ceremony over a return value, and dispatch is
already documented once in `agent_patterns.md`. `impl-slice-implement-page` is an alternative
*unit of work* — every feature on one page, outside-in — and a page is a horizontal grouping.

**Tier becomes depth, not routing.** One entry skill per side, and tier decides how many
grilling rounds and how much dossier.

**Dossiers stay two, one file each.** A **feature dossier** at `_concept/dossiers/<slug>/` and
a **slice dossier** at `_implementation/slices/<id>/`, matching the vocabulary's rule that a
slice is impl-side only.

## Consequences

- `contracts/slice_loop.md` shrinks to the slug rule and the freeze lifecycle. Its tier gate
  and refuse message go with tier-as-routing; its context-isolation section is ADR 0005's.
- `contracts/plans.md` is deleted. `PLANS.md` itself has readers in the build and ops domains
  and is decided there, not here. **Decided by [0010](./0010-no-plan-file-and-no-status-file.md):
  it does not port, and neither does a project-level `progress.yaml`.** The per-slice
  `progress.yaml` this ADR deletes on freeze is untouched by that.
- `spec-feature` writes into the screens tree, so a whole-app screens skill has to justify
  itself against it or collapse into it.
- The flows lose a fan-out reason: no tier branch at the slice loop, and no node for the two
  skills that died.
- A four-skill loop cannot hide a phase. Anything the old loop enforced by making a step a
  skill — spec review before code review, a forced simplification pass, a usability gate —
  now survives only as a line inside one of the four, or not at all. That is the trade this
  ADR makes: fewer seams, and the discipline stated where it binds rather than staged.

**Paths superseded by [0007](./0007-one-numbered-artifact-tree.md).** The two dossiers kept
their names and their two-ness; their locations moved with the tree —
`08_dossiers/<feature_slug>/` and `11_build/slices/<slice_id>/`, both inside `_concept/`.
`contracts/concept_structure.md` is the authority.
