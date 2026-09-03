# 07: Implementation-side consolidation — 16 slice skills to ~6

**Type:** grilling
**Blocked by:** None (02, 04, 12 resolved)
**Status:** ready

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

## Note from ticket 06

Two pieces of the mockup domain were handed to the build side; this ticket has to catch them.

- **Storybook configuration lands in `build-foundation`**, which already "configures Storybook
  with brand theme if present". `mockup-component-storybook-setup` (171 lines) is not ported —
  it duplicates work the build domain does anyway. Confirm `build-foundation` genuinely covers
  it, or the setup step is lost rather than moved.
- **`mockup-component-storybook-types` (183 lines) dies as a mockup skill** — replacing
  placeholder types with `model.json`-generated interfaces is schema-driven codegen against the
  real data model, and it is PostXL-only. Decide here whether that is a step inside a build
  skill or nothing at all.
- The **line drawn was artifact, not tool**: Storybook is named in 9 `SKILL.md` outside the
  mockup domain, so "it mentions Storybook" never decided placement. Story *authoring* stayed
  in `mockup-`; anything that configures the real project moved to `build-`.

## Handed over by ticket 09

Ticket 09 pruned the contracts layer but deliberately left two impl-side files to this
ticket rather than pre-empt the slice consolidation on stale counts:

- **`contracts/slice_loop.md`** (73 lines) — 1 in-body reader.
- **`contracts/plans.md`** (86 lines) — 1 in-body reader.

Ticket 09's bar: a contract earns its place only if **more than one skill reads it in-body**,
or a machine does. Both currently fail it. **Default is deletion** — fold each into the one
skill that reads it. They survive only if this ticket's consolidation gives one a second
reader, in which case it is promoted back into `contracts/`.

Also settled by 09, so do not re-litigate: `iron_laws.md` and `golden_principles.md` survive
as machine-enforced gates, and this is *not* in tension with ticket 03's removal of
`MUST`/`NEVER` blocks — those were skill-body prose; these have `requires` and `ops-review`
as the check behind them.
