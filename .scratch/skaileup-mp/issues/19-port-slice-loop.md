# 19: Port the slice loop — write the 4 skills

**Type:** task
**Blocked by:** 08 (07, 11 resolved)
**Status:** resolved

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

## Answer

**Written and committed in `ai-assets-skaileup-mp`** — one commit, `3b21cfe`, on `main`, not
pushed. **16 skills / 4,166 lines → 4 skills / 284 lines**, all well under ticket 03's 140
ceiling, `name:` == directory, no `MUST`/`NEVER` anywhere.

| skill | SKILL.md | ported from | source lines |
|---|---|---|---|
| `spec-feature` | **83** | `concept-slice/{brainstorm,align,scope-feature,design-feature}` + mp `to-spec` | 944 |
| `build-plan` | **78** | `impl-plan/{brainstorm,align,plan-vertical}` + mp `to-tickets` | 876 |
| `build-implement` | **65** | `impl-slice/{implement,test,recap,refactor,commit}` | 1,478 |
| `build-branch` | **58** | `impl-slice/{git-prepare,git-finish}` | 342 |

The remaining 526 source lines are `impl-plan-supervised` and `impl-slice-implement-page`,
which ticket 07 killed outright.

### The stale-path correction

Every path came from `contracts/concept_structure.md`, not from this ticket's body. What
changed against the body: `_concept/experience/features/<group>/<slug>.md` →
`05_features/<featureset>/<feature_slug>.md`; `_concept/experience/screens/<slug>/` →
`07_screens/<feature_slug>/`; `_concept/dossiers/` → `08_dossiers/`; `_implementation/slices/`
→ `11_build/slices/`. Also `_concept/_meta/scope.yaml` → `01_meta/scope.yaml`,
`blueprint/` → `10_blueprint/`, `discovery/brand/tokens.json` → `03_brand/tokens.json`,
`experience/journeys/stories.yaml` → `04_journeys/stories.yaml`.

Two consequences the rename forced, beyond find-and-replace:

- **`_concept/` is no longer read-only to the build side.** Five of the old skills say
  "NEVER modify `_concept/` files" — but `11_build/` now *is* `_concept/`, and so is the
  back-link `impl-slice-commit` writes into the feature spec. `build-implement` states the
  real rule instead: it writes the slice dossier and the back-link, and rewrites nothing else
  under the root.
- **The acceptance-criteria ledger has no home and does not port.**
  `impl-plan-plan-vertical` wrote `_implementation/acceptance_criteria/<group>/<slug>.ac.md`;
  ADR 0007's tree has no such entry, and inventing `11_build/acceptance_criteria/` would be a
  twelfth top-level kind decided here. Criteria live in the feature spec in EARS and
  `build-plan` maps each to a test in the slice that satisfies it. **Handed to ticket 17** —
  per-criterion pass/fail tracking is a quality artifact, and ticket 09 already flagged
  `contracts/acceptance_criteria.md` for re-ruling at ticket 16.

### What had to differ from ticket 07's shape

1. **`slice_id` is no longer `feature_slug`.** Ticket 07 kept the old slug rule, whose impl
   clause reads `slice_id := feature_slug` verbatim — one slice dossier per feature. But it
   also made `build-plan` *be* `to-tickets`, and `concept_structure.md` describes
   `11_build/slices/<slice_id>/` as "one vertical slice's dossier". A feature decomposes into
   several slices, so the two cannot both hold. **Ruling: `slice_id` derives from the
   slice's own title**, one dossier per slice, and `plan.md` frontmatter carries `feature` and
   `blocked_by`. `feature_slug` keeps its three jobs on the concept side. Dependency order
   lives in the edges, not in a `NN_` prefix — which is also what ADR 0007's "nothing numbered
   below the first level" requires.
2. **The anti-horizontal nudge is not embedded verbatim in the output.** `plan-vertical`
   pinned an exact-string block inside every `plan.md` and had a validator check it. There is
   no validator, and ticket 03 rules that a constraint is stated at the step it binds — so the
   decomposition rule is in `build-plan` step 2 (cut them vertical) and the completion rule in
   `build-implement` step 2 (finish one row before starting the next). Two different rules at
   their two different readers, rather than one block copied into every artifact.
3. **`git-state.yaml` does not port, and the finish-preference memory goes with it.** Branch
   and worktree are things `git branch --show-current` and `git worktree list` already know;
   caching them in an artifact is the environment restated. What is genuinely lost is
   `git-finish`'s `preferences` block (last-chosen merge vs PR, squash, base branch). Judged
   not worth a file: `build-branch` asks once per close, and merge and discard still require
   the typed word.
4. **`contracts/slice_loop.md` gained a paragraph it was not asked for.** The ticket says
   shrink to slug + freeze, and ADR 0005 says the warm/cold answers live in "one section of
   the slice-loop contract" that skills point at. Both are honoured by a four-line
   `## Session boundaries` that points at ADR 0005 and states nothing itself. 73 → 49 lines;
   the tier table, the pinned refuse message, the `/clear` context-isolation section and the
   six-key handoff-frontmatter table are all gone. `contracts/plans.md` was never in `-mp`, so
   "delete" was a no-port.
5. **`spec-feature` writes the dossier once, at the end.** Ticket 07 said one file per side.
   With the loop's internal boundaries warm (ADR 0005), the concept side has no intermediate
   file at all — the brainstorm/align/scope notes live in the session and land as
   `08_dossiers/<feature_slug>/index.md` when the spec does. Writing it *is* freezing it. The
   build side keeps two: `plan.md` (written by `build-plan`) plus transient `progress.yaml`,
   with `index.md` added on freeze.
6. **`build-implement` is 65 lines against mp's 15.** The 50 that are not mp: loading the
   plan and the spec and the screens (1), the `blocked_by`-unfrozen refusal (1), the
   `_concept/` write boundary and the back-link (2), the dossier freeze (1), the
   spec-review-before-code-review line ADR 0006 promised (1) — and the three steps this ticket
   required as steps rather than skills: the `plan.md` gate, the recap, and the forced
   simplification pass. Those three are the least defensible lines in the port. They are one
   paragraph each rather than the 771 source lines they replace, but they are discipline, not
   `_concept/`-awareness, and a later reading may find they belong in `tdd`'s loop or nowhere.

### Questions this surfaced for other tickets

- **The four mockup skills are stale against ADR 0007, and nothing flags it.**
  `mockup-walkthrough` writes `_concept/mockup-walkthrough/<renderer>/` and reads
  `experience/screens/`, `discovery/brand/tokens.json`, `_meta/scope.yaml`,
  `_grounding/onboarding/onboarding.yaml`, `_feedback/devlog.md` — every one of them a
  pre-0007 path. Ticket 14 landed before ticket 08, and ticket 08's handoff list does not name
  it. The repo is internally inconsistent today: four skills on the old tree, four on the new.
  **Ticket 16** owns "every written path resolves to a real top-level entry" and will catch it,
  but this is a repair pass someone has to schedule, not a validator finding.
- **Four contracts still carry pre-0007 paths in their examples**, so my skills cite them for
  *shape* and cite `concept_structure.md` for *paths*: `artifact_frontmatter.md` (its section
  headers are literally `## experience/features/<group>/<feature>.md`), `feedback_loop.md`,
  `acceptance_criteria.md`, `agent_patterns.md`. That split works but it is a trap for the next
  author. Same ticket-16 sweep.
- **`contracts/README.md` is wholesale stale** — it describes the *old* repo (a `cf/`+`saxe/`
  archive, `scripts/`, `DOMAIN.md`) and its table lists six contracts that no longer exist while
  omitting six that do. I made the two edits my change required (dropped `plans.md`, added
  `slice_loop.md`) and left the rest, because ticket 09 assigned the `CONTRACT`+`README` merge
  to the rewrite tickets and rewriting it here would pre-empt whichever one claims it. It should
  be claimed explicitly rather than by whoever notices last.
- **`iron_laws.md` §§ 3, 4 and 6 do not survive ticket 08's boundary.** Law 3 and law 4 gate
  `experience/screens/` on brand tokens and on the data model; `spec-feature` now writes screens
  inside the feature loop, before `10_blueprint/` exists on most tiers. Law 6 names the `ready`
  skill, which is ticket 17's to keep or kill. The four new skills do not cite iron_laws;
  ticket 09 kept the file for its machine-enforced gates, and at least two of those gates now
  describe a pipeline that no longer runs. **Worth a ticket** — either the laws are re-cut
  against ADR 0007 or the file loses the argument ticket 09 kept it on.
- **ADR 0006's dossier paths were stale.** I appended a supersession note pointing at ADR 0007
  rather than editing the decision text, since an ADR records what was decided when.
