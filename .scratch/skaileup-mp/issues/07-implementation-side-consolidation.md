# 07: Implementation-side consolidation — 16 slice skills to ~6

**Type:** grilling
**Blocked by:** None (02, 04, 12 resolved)
**Status:** resolved

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

**16 skills / 4,166 lines → 4 skills**: `spec-feature` · `build-plan` · `build-implement` ·
`build-branch`. The mechanism is ticket 02's find, applied literally — mp's `implement` is
**15 lines that name `tdd` and `code-review`** instead of restating them. Every one of the
16 that survives, survives as a *step inside* one of the four, and the four name global
skills rather than re-teaching them.

### Disposition of all 16

| old skill | fate |
|---|---|
| `concept-slice-brainstorm` · `-align` · `-scope-feature` | steps inside **`spec-feature`** (the interview is the global `grilling` skill) |
| `concept-slice-design-feature` | **is** `spec-feature` |
| `impl-plan-brainstorm` · `-align` | steps inside **`build-plan`** |
| `impl-plan-plan-vertical` | **is** `build-plan` (absorbs `to-tickets`: vertical slices + blocking edges) |
| `impl-plan-supervised` | **dies** |
| `impl-slice-implement` | **is** `build-implement` |
| `impl-slice-test` · `-recap` · `-refactor` · `-commit` | steps inside **`build-implement`** |
| `impl-slice-implement-page` | **dies** |
| `impl-slice-git-prepare` · `-git-finish` | **`build-branch`** |

**The two absorbed mp skills are not new skills.** `to-spec` *is* `spec-feature` and
`to-tickets` *is* `build-plan` — the ticket asked whether they replace or sit beside the
existing pair, and the answer is that the split mp makes once (interview, then synthesise
without interviewing) is the only split the concept side needs. `grilling` stays a global
install and is called by name, so four grill-shaped skills collapse to zero.

**`impl-plan-supervised` dies with its 4-status protocol** (`DONE` / `DONE_WITH_CONCERNS` /
`NEEDS_CONTEXT` / `BLOCKED`). It is ceremony over a subagent's return value, and ticket 09
already kept `agent_patterns.md` — re-scoped to agent dispatch — as the place that documents
dispatch once. What is genuinely lost is its spec-review-before-code-review ordering; that
survives as one line of `build-implement`, not as an orchestrator.

**`impl-slice-implement-page` dies outright.** It was never a step but an alternative *unit
of work* — every feature on one page, outside-in — and a page is a horizontal grouping in a
map whose whole discipline is the vertical slice. "Start from the Storybook page composition
if one exists" survives as one line.

### What `build-implement` calls by name

**`tdd` and `code-review`, and nothing else.** `quality-test-{unit,integration,e2e}` stay
**flow nodes after the slice** rather than calls from inside — otherwise every slice drags
the whole test pyramid, and ticket 17 loses the freedom to reshape them.

### Tier stops gating the loop

`slice_loop.md`'s table routes each tier to a different *entry skill* (mvp →
`plan-vertical`, simple → `align`, standard/complex → `brainstorm`) behind a pinned refuse
message and iron-law §7. With one entry skill per side there is nothing to route to, so
**tier becomes depth inside the skill** — how many grilling rounds, how much dossier —
and the table, the refuse message and the refusal branch leave all four skills. Ticket 10
inherits the consequence: the flows stop branching by tier at the slice loop.

### Dossiers: two, one file each, and one is renamed

Ticket 05 fixed **slice = impl-side only**, so `_concept/slices/<id>/` was misnamed.
Concept-side becomes **`_concept/dossiers/<feature_slug>/`** — named for working state, clear
of both `slices` (now impl-only) and `_concept/experience/features/` (the permanent spec).
`_implementation/slices/<id>/` keeps its name, now correct by definition.

**The per-phase handoff directory goes.** One file per side (`feature.md`, `plan.md` +
`progress.yaml`), because ADR 0005 made these boundaries warm — the intermediate handoffs
existed to cross a `/clear` that no longer happens. Freezing stays: `spec-feature` freezes
the feature dossier, `build-implement` freezes the slice dossier.

### `spec-feature` writes screens, and that collides with ticket 08

`design-feature` writes both `_concept/experience/features/<group>/<slug>.md` **and**
`_concept/experience/screens/<slug>/<screen>.md` — the same tree `experience-screens` owns
in ticket 08's half. `spec-feature` **keeps both**: a feature spec without its screens is not
implementable, and per-feature screens are why the loop exists. Ticket 08 gets the boundary:
`experience-screens` covers screens *not* reached by a feature loop (the whole-app pass), or
it collapses into `spec-feature` there.

### Contracts handed over by ticket 09

- **`contracts/slice_loop.md` survives, shrunk** — 3 of the 4 new skills read it in-body,
  clearing ticket 09's two-reader bar. It keeps the **slug rule** and the **freeze
  lifecycle**; it loses the **tier gate** (above), the **context isolation** section (ADR
  0005 owns it, and `/clear` is not `-mp` vocabulary), and most of the **handoff frontmatter**
  table, which now describes one file per side.
- **`contracts/plans.md` is deleted.** But `PLANS.md`-the-artifact is **not** this ticket's
  to kill: it has **9 in-body readers**, only 2 in this cluster — the rest are
  `impl-build-{scaffold,foundation,infrastructure}` and three `ops-*`. Handed to ticket 18.

### Ticket 06's Storybook handoff, corrected

Ticket 06 asked this ticket to confirm that `build-foundation` covers
`mockup-component-storybook-setup`. **It does not.** `build-foundation` only *themes a
Storybook that already exists* ("only if `prototype/storybook/` exists AND Storybook is
installed", `10_impl-build/02_foundation/SKILL.md:74-75`), while the setup skill **scaffolds
a standalone Storybook project**. Different artifacts, so moving it into `build-foundation`
loses the step. **Scaffolding becomes a step inside `mockup-storybook`** (ticket 14) — the
standalone Storybook is a mockup artifact. **`storybook-types` dies** as decided.

### Ticket 12's handoff

**`impl-quality-debug-handoff` (314 lines) is deleted** — zero flow references, `-mp` has no
`agents/`, and ticket 12 already ruled that `handoff` does not become a skill. Its sibling
`debug-self-verify` (305, also flow-orphaned) goes to ticket 17 rather than being ruled here.

### Two tickets graduated

- **Ticket 17 — the `quality` domain** (13 skills / 2,833 lines). Held out of this ticket:
  29 skills is more than one session, and only the call-by-name list above was needed here.
- **Ticket 18 — architecture + build** (11 skills / 2,706 lines). **Nobody owned these.**
  The map's ticket set covered the mockup domains, the slice loops, the concept half and the
  contracts, and `09_impl-architecture` + `10_impl-build` fell between them, visible only as
  the "port itself, per domain" fog.

### Facts found while resolving

- **Flow-orphaned skills** (referenced by zero flow): `impl-build-generate`,
  `impl-quality-{debug-handoff,debug-self-verify,standards-sync,test-plan}`,
  `mockup-walkthrough-{lit,migrate-elements}`, `ops-{add-feature,eval-concept,eval-feature,eval-product}`.
- `contracts/slice_loop.md` is *mentioned* by 10 files but 9 of them are the skills this
  ticket collapses — the same ~2.5× inflation ticket 09 measured between mentions and readers.

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
