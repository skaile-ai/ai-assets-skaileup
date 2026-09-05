# Map: skaileup → skaileup-mp

## Destination

`ai-assets-skaileup-mp` exists as a sibling repo + submodule under `ai-assets/`: the same
product domains as today (design, features/featureset, components, mockups-via-Storybook),
rebuilt as a **smaller, clearer** skillset — roughly 9 domains and ~30 skills instead of
17 and 95 — with a common domain vocabulary borrowed from the mattpocock skills.

**Done when one real project installs `-mp` and its flows load green.** Not "complete";
installed-and-loading. The existing `forge-concept` integration test
(`tests/integration/skaileup-flows.test.ts`) is that test with one repo URL changed.

## Notes

**This map carries execution.** Wayfinder's plan-don't-do default is overridden: the
destination is the migrated repo itself, so tickets that build it are in scope, not just
tickets that decide it. Decision tickets still come first — don't port ahead of the shape.

**Skills every session should consult:** `grilling` + `domain-modeling` by default;
`writing-for-agents` for anything that edits a SKILL.md; `prototype` and `research` where
the ticket type says so.

**forge-concept is deferred, not immutable.** Every ticket here treats the host as fixed,
because changing it mid-migration would make the migration untestable — but that is a
*sequencing* decision, not a permanent boundary. When a ticket hits a constraint that exists
only because forge-concept reads something a particular way, **record it in the forge-concept
register under Out of scope**, with the source site, rather than recording only the workaround.
Once `-mp` loads green that register is the input to a **successor effort with its own map and
tickets**, asking the opposite question: what should the host read, given the collection we now
have. Do not open that effort from inside this one, and do not soften a ruling here on the
grounds that the host might change later.

**Settled at charting** (premises, not ticket resolutions — every ticket below assumes these):

1. **New sibling repo**, not a branch or in-place rewrite. Old collection keeps running untouched.
2. **No cutover.** `-mp` is built in parallel; other projects opt in on demand via `skaile.yaml`.
3. **Thin machine spine.** ~~Keep `contracts/artifacts.yaml`, flow YAMLs, and the iron laws —
   `forge-concept` reads them at runtime.~~ **Amended by ticket 01:** flow YAMLs and skill
   `name:` are live contracts, but `artifacts.yaml` is **unreachable as deployed** (read only
   under `--link`; the default copy install leaves the recursive search finding nothing, and
   forge-concept silently falls back to session completion). Keep the flow contract and the
   `name:` contract; whether `artifacts.yaml` survives is now an open question in ticket 09.
   The DSL grammar still goes — nothing outside the collection reads it.
4. **Skill bodies are rewritten, not copied.** Prose + `references/` for the long tail; the
   machine layer is *ported*, not rewritten. ~~A short `MUST`/`NEVER` block.~~ **Amended by
   ticket 03:** no `MUST`/`NEVER` block — constraints are stated positively at the step they
   bind, and a hard guardrail survives as a named failure with a check behind it. Ceiling
   **140 lines** (mp's measured max); both ports came in under 110.
5. **Rename freely.** No alias map; the old repo stays available for anything still on old names.
6. **Absorb, don't fork.** mp's pipeline-shaping ideas (`grilling`, `to-spec`, `to-tickets`,
   an `ask-matt`-style router, `research`) become skaileup-named skills that know about
   `_concept/`. The domain-neutral ones (`tdd`, `code-review`, `prototype`) stay global installs.
7. **Targets to hit:** ~9 domains · mockup 17 → ~6 skills · slice clusters 16 → ~6 ·
   tiers 5 → 3 · contracts 29 → spine-only.

## Decisions so far

<!-- one line per closed ticket -->

- [01: What the machine layer's public API actually is](issues/01-machine-layer-public-api.md):
  **Skill `name:` is the whole identity** — directory paths, `NN_` prefixes and domain foldering
  are free to change (95/95 skills already have `name:` ≠ parent dir). One `name` fills four
  roles: install path, flow `data.skill`, `produced_by`, grounding input path. Flow contract is
  real (`<id>.flow.yaml` in dir `<id>`, `id`+`nodes`+`edges`, top-level `requires:` drives
  transitive install). **`artifacts.yaml` is unreachable as deployed** and `skaile.yaml`'s
  `assets:` block is dead — newer workspaces *throws* on it. Frontmatter actually read:
  `version`, `artifacts.requires[].id`, `prerequisites.*`, `requires`; everything else is docs.
  Catch: forge-concept lanes key off **name prefixes** (`concept-`/`design-`/`experience-`/
  `product-spec-`/`mockup-`/`impl-`/`quality`) and `data.phase`.
  Findings: `research/01-machine-layer-public-api.md` on branch `research/machine-layer-api`.
- [02: Mine the remaining mattpocock skills for ideas](issues/02-mine-remaining-mp-skills.md):
  9 ABSORB / 7 REFERENCE / 1 SKIP; `domain-modeling` already ported into
  `contracts/domain_model.md`. mp measures 25 skills / 2,945 lines, `SKILL.md` **max 140**,
  frontmatter 4 keys, **zero uppercase MUST/NEVER anywhere**. `implement` (15 lines) composes
  `tdd` + `code-review` rather than restating them — the concrete mechanism for 16 → 6.
  Findings: `research/02-mp-skills-mined.md` on branch `research/mp-skills-mined`.

- [03: Skill body shape — settled by prototype](issues/03-skill-body-shape.md):
  Shape holds on the worst case — `concept-brief` 289 → **80**, `mockup-walkthrough-astro`
  1,133 → **110**, ceiling **140**. **Premise 4 amended: no `MUST`/`NEVER` block** — all 13
  re-expressed positively at the step they bind; hard guardrails survive as named failures
  with a check behind them. The DSL loses nothing: `CHECKLIST` restated `validator.py`,
  `ROLE/READS/WRITES` restated frontmatter, and **`EMIT` is read by no code at all**. The
  astro skill's bulk was **duplication of `contracts/walkthrough_renderer.md`**, not length —
  ~200 lines of STEP 2 already existed in the contract. Collection-wide, **44% (10,784 of
  24,646 lines) is mechanically removable** before rewriting any prose: frontmatter 18%,
  code fences 9%, the ten boilerplate sections 16%. Template + both ports:
  `prototype/` on branch `prototype/skill-body-shape`.

- [04: Naming scheme and the domain set](issues/04-naming-and-domain-set.md):
  **The tree is flat and the domain lives in the name, not the filesystem.**
  `skills/<name>/SKILL.md`, **dir name == `name:` character for character** (today 95/95
  skills have `name:` != parent dir), no `NN_` anywhere — order lives in the flow graph.
  Root hoists to `skills/` · `flows/` · `contracts/` · `docs/`. Nine domains, carried as the
  first name segment: **`concept · design · experience · spec · mockup · architecture ·
  build · quality · ops`** (`discovery`→`concept`, `product-spec`→`spec`). `concept-slice`
  lands in **`spec`** (it authors feature + screen specs); `impl-plan` + `impl-slice` land in
  **`build`**. The **`quality`/`ops` line is the artifact under inspection** — `quality`
  checks `src/`, `ops` checks `_concept/`. Names are **`domain-skill`, 2 segments default,
  3 for a genuine sub-cluster, never 4** (today: 53×3, 28×4). **`featureset` is a level in
  the vocabulary**, not a domain or skill boundary. **All absorbed mp skills take a domain
  prefix** — the argument is collision, not taste: a bare `research` clobbers the global mp
  install at the same path. **The lane constraint was weaker than charted:** `phaseForNode`
  (`forge-concept/shared/flow-phases.ts:35-41`) takes explicit `data.phase` first and only
  falls back to name prefixes, so **`-mp` flows declare `phase` on every node** and the
  domain set was chosen on merit; `spec-`/`build-` break their old lanes, accepted and
  recorded. Also dead: the renderer-name-must-end-with-its-subfolder rule
  (`flow-manager.ts:412-422`) is reached only through the unreachable `artifacts.yaml`.

- [05: The shared domain vocabulary (CONTEXT.md)](issues/05-domain-glossary.md):
  **Two vocabularies, never one** — `CONTEXT.md` is the *collection's* language
  (hand-written, 139 lines, glossary-only, zero paths, drafted at
  `.scratch/skaileup-mp/CONTEXT.md`); the *project's* language keeps the word
  **glossary** and stays a generated artifact. **All 16 `DOMAIN.md` files die** — every
  job they do is duplicated by something machine-read, and ticket 04's flat tree removed
  their folders. **asset** (shipped by this repo) vs **artifact** (written into a
  project); **`output` retires as a noun**. **slice = vertical slice, impl-side only** —
  the concept-side thing is a **feature dossier**, with `dossier` the noun for both.
  **featureset replaces feature group** as a straight rename (the word appears **0 times**
  today). **profile = project type only** — "tech stack profile" becomes **template**,
  which makes ticket 10's `cli` tier→profile demotion consistent. **`phase` is a machine
  contract**, so ticket 12's concept is a **session boundary**. **seed scenario**, not the
  phantom "seed mode". From mp: **`vertical slice` only** — `tracer bullet` is a second
  word for one concept, `deep module`/`seam` stay `codebase-design`'s. **Decision records
  at three levels, one 3-test gate** (collection · design-time · build-time), `-mp` gains
  its own seeded from tickets 01–04. **`decisions.yaml` was never decisions** — it held
  onboarding *answers*; it merges with `profile.yaml` into one **`onboarding.yaml`**.
  `_concept/` tree renaming: principle only, folder list waits on tickets 08/09.

- [06: Mockup domain — 17 skills to ~6](issues/06-mockup-domain.md):
  **17 → 4** — `mockup-walkthrough` · `mockup-storybook` · `mockup-annotate` · `mockup-feedback`
  (~6,597 lines → ~450 + `references/`). **Two renderers survive, `static-html` + `astro`** —
  the only two with `validator.py` + fixtures, and astro is ticket 03's port. `framework` dies
  because rendering in the chosen stack *is* building the app (`build-scaffold` does it better,
  and a mockup that is the app drifts); `lit` dies on 1 flow ref and no tests; `text` dies as a
  fourth renderer axis nested inside a renderer. **The difference is `references/<renderer>/`,
  not a parameter** — and the `items[]` id-derivation rule moves into
  `contracts/walkthrough_renderer.md`. **The renderer choice moves to data**: tier default
  (mvp/simple → static-html, standard/complex → astro) overridden in `onboarding.yaml`, so the
  flow's two optional sibling nodes (`mock-astro` "via router" / `mock-static-fallback`
  "router default") collapse to one node — ticket 10 inherits that. **Feedback 4 → 2, split at
  the multi-day human wait**: `annotate` | `triage→patch→apply`; `triage` was never a skill
  (98 lines wrapping a deterministic `triage.py`). **Storybook splits by artifact, not tool** —
  config to `build-foundation` (which already does it), story authoring to one `mockup-storybook`
  composing components→pages→journeys; `types` dies as datamodel codegen (PostXL-only).
  `isolated-html` dropped (returns as a `references/` renderer if the no-Node view is missed);
  **`migrate-elements` does not port** (backfill for pre-`elements:` specs; `-mp` writes the
  block from the start). **`elements:` stays — 9 readers.** To ticket 09: keep
  `walkthrough_renderer.md` (grown) + `elements_block.md`, fold `preview_compatibility.md` in.

- [09: Prune the contracts layer](issues/09-contracts-prune.md):
  **28 contracts / 5,663 lines → 14 files**; `artifacts.yaml` (~1,000), `flows.md` (588) and
  `asset_frontmatter.md` (530) deleted before any rewriting. **One rule settled the registry
  question: machine-read data lives where forge-concept already reliably looks** — `SKILL.md`
  frontmatter resolved via `name:`. That drops **`artifacts.yaml`** (reviving it costs an
  out-of-scope forge-concept edit) and **keeps `inputs_optional` in frontmatter** (moving it
  to a sibling `inputs.yaml` costs the same out-of-scope edit) — the map's own boundary cutting
  both ways; concept-side frontmatter stays ~15 lines vs mp's 4–6, accepted. **The bar: a
  reader consults the contract at a step in its body**; naming it in `REQUIRED BACKGROUND` or
  `REFERENCES` is a citation, and ticket 03 deletes both blocks. Raw counts were inflated ~2.5×
  — `frontmatter.md` shows 86 refs, 13 real readers — so **deciding on raw counts would have
  kept three of the largest dead files**. Two of the ticket's own premises were wrong:
  **`agent_patterns.md` does not die with the DSL** (9 in-body readers, 4th highest; re-scoped
  to agent dispatch, absorbs `subagent_dispatch.md`), and **`iron_laws` + `golden_principles`
  are not in tension with ticket 03** — its amendment killed `MUST`/`NEVER` *skill-body prose*,
  while these document machine-enforced gates, and **`requires` is exactly the "check behind a
  named failure" ticket 03 demanded**. **`flows.md` had zero readers** — the largest contract in
  the layer, mentioned only by `contracts/README.md` and `DOMAIN.md`; `flow.schema.json` survives
  as the flow contract's machine form, **pending ticket 15**. **Two frontmatter contracts become
  one:** `frontmatter.md` → **`artifact_frontmatter.md`** (ticket 05's asset/artifact split made
  explicit in the filename), `asset_frontmatter.md` deleted (0 in-body readers; its whole
  read-set is ticket 01's five fields, a 20-line table for the skill template). DSL trio dies;
  **ticket 03's replacement template goes to `docs/`, not `contracts/`** — no runtime reader.
  **`profiles/` survives but leaves `contracts/`** for the repo root (project-type data, not a
  contract). `CONTRACT.md`+`README.md` merge; `preview_compatibility`→`walkthrough_renderer`;
  `doc_tracking`→`build-docs`; `wireframe_conventions`→`mockup-walkthrough/references/`;
  `acceptance_criteria` shrinks to the EARS grammar — **but corrected 2026-09-05 (brief 16,
  re-verified): `ac_lib.py` does not validate EARS.** It validates ledger structure and names
  EARS once, in an error string (`ac_lib.py:108`). The actual EARS regex exists in **two copied
  `validator.py` files** (`11_impl-plan/02_align`, `08_concept-slice/02_align`), both in skills
  ticket 07 collapsed, and matches only the `WHEN…SHALL` form. So this contract was kept for a
  reader that does not read it — **re-ruling handed to ticket 16**. Same pass:
  **`lint_concept.py` contradicts `golden_principles.md`**, the contract ticket 09 kept it for —
  the contract mandates snake_case semantic entities and calls `model.json` canonical
  (`golden_principles.md:13,23,83`), while the linter opens **`postxl-schema.json`** and errors
  unless models are **PascalCase** (`lint_concept.py:346,365`); `model.json` appears nowhere in
  it. Ticket 09's machine-reader argument holds only if one of the two is rewritten → ticket 16. **Four files handed off rather than ruled**
  — `slice_loop`+`plans`→07, `phase_procedures`→12, `grill_bank`→absorbed-skills fog,
  `scripts/`→**ticket 16** — each defaulting to deletion unless that ticket gives it a reader.

- [11: Create the repo and its skeleton](issues/11-create-repo-skeleton.md):
  **`github.com/skaile-ai/ai-assets-skaileup-mp` exists** (skeleton `93e9d0e`), added as a
  submodule at `ai-assets/ai-assets-skaileup-mp` (super-repo `cb629fb`, straight to `main`).
  **Public, not private** — the ticket's "matching the existing repo" was wrong about the
  existing repo. Skeleton is `skills/` + `flows/` (both empty, each with the rule stated in
  its README) · `contracts/` at ticket 09's 14 survivors · `profiles/` hoisted to the root ·
  `CONTEXT.md` verbatim · `docs/skill-template.md` + both ports in `docs/examples/` ·
  `docs/adr/0001-0004`. **The spine did not come across unchanged** — the ticket predates
  ticket 09, so the skeleton starts at 09's answer rather than re-doing its deletions: no
  `artifacts.yaml`, no `schemas/`, no `scripts/`. **`flows/` is deliberately empty** (ticket
  10 owns the set; 19 stale flows in a repo whose test is "flows load green" is worse than
  none) and **`.github/` waits for ticket 16**. `skaile.yaml` ships no `assets:` block and no
  manifest — glob discovery. Three contract fold-ins
  (`preview_compatibility`→`walkthrough_renderer`, `subagent_dispatch`→`agent_patterns`,
  `CONTRACT`→`README`) are content work left to the rewrite tickets; sources stay in the old repo.

- [15: Flow format vs platform's flow-execution](issues/15-flow-format-vs-platform.md):
  **Platform did not fork the format — one schema, in `@skaile/workspaces`, but only *one* host
  calls it. Corrected 2026-09-05 (brief 16, re-verified):** the three `validateFlow` call sites
  are **all platform's** (`flow-start.service.ts:87`, `run-group.route.ts:558`,
  `run-group.handler.ts:109`); **forge-concept has zero** — its only gate is `loadFlowsFromDir`'s
  truthy `id`/`nodes`/`edges`. (A naive grep for `validateFlow` matches `invalidateFlowCache`,
  which forge-concept *does* call ten times; that is how this got attributed.) The zod schema
  (`workspaces/.../types/src/manifests/index.ts`) also declares **no edge `type` and the word
  `phase` zero times** — so ticket 15's "the engine takes dependencies from
  `edges.filter(e => e.type === "flow")`" is a *runtime* behaviour with **no schema behind it**,
  and `flow.schema.json`'s `phase` enum (4 sites) is **the only machine check anywhere** of
  ticket 04's every-node-declares-phase rule. That is an argument for porting the phase enum,
  against this ticket's "narrowed or not at all" — **ruling handed to ticket 16**, which owns the
  validators. Unchanged by the correction:
  `flowExecution.model.json` is the per-node *execution record*, orthogonal to authoring.
  **All 17 skaileup flows validate green** against it, and 0.48.1 vs 2.0.0 declare identical
  fields — no skew. **Platform is not a file host**: `loadAllFlows`/`loadFlowsFromDir` have zero
  call sites there, flows live in the DB as `filesJson['flow.json']`, imported by hand, org
  seeding removed — so **the acceptance target does not move**, forge-concept's
  `skaileup-flows.test.ts` stays the test and platform importability is free. The contract is
  therefore not an intersection, but the two required-sets differ (loader: `id`+`nodes`+`edges`;
  validator: `id`+`name`) → **ship all four**. **The stale artefact is ours:**
  `contracts/flow.schema.json` invents a `gate` node kind and a `review-loop` edge type no engine
  implements (0 and 1 uses), requires `position` nothing reads (dagre computes it), and is
  `additionalProperties: false` against a `looseObject` runtime — ticket 09's "keep a machine
  form" stands, but this file **ports narrowed or not at all**. **The sharpest rule is not
  platform's:** the engine takes dependencies from `edges.filter(e => e.type === "flow")`, so an
  edge with any other type — or **no `type`** — orders nothing (verified; `skaileup-stepwise`'s
  one `review-loop` edge is already a no-op). Platform adds exactly three checks: unique node
  ids, no dangling endpoints, no self-loops. **`data.phase` is a closed three-value enum**
  (`conceptualization|implementation|review`) — ticket 04 had the precedence right, not the
  vocabulary; the nine domains name skills, not phases. `assetSearchDirs` already covers a flat
  `<root>/flows/`. Ticket 16 gains four cheap checks; `modes`/`tier_presets`/`artifact_handoff`
  have no reader anywhere. Findings: `research/15-flow-format-vs-platform.md`.

- [12: Phase-boundary policy — replace the hardcoded `/clear`](issues/12-phase-boundary-policy.md):
  **The tree does not port as a tree — two of its five options do not exist in the host that
  matters.** forge-concept keeps **one long-lived agent process per concept**
  (`concept-agent.ts:174`) and a node run is just another prompt into it
  (`flows/nodes/[nodeId]/run.post.ts:83`): no `/clear`, **no `/compact` at all**, only a manual
  "Clear conversation" button. So the old rule was Claude-Code vocabulary describing a click the
  primary host may never make, and **`-mp` names no slash command anywhere** — ticket 05's
  discipline on `phase`, same reason. Five options become **two named cases**: **warm boundary**
  (continue is the default) and **cold resume** (the artifact is the whole input; days later,
  possibly another person). **Answers are fixed per site, not derived at runtime** —
  brainstorm→align **warm** (mp's own worked example), align→scope/plan **warm**,
  scope→design-feature **cold**, implement→test→recap **warm**, commit→next-slice **cold**; the
  tree survives as reasoning in **ADR 0005**. **The dumb-zone guard had to survive as a soft
  gate** — the fixed answers contradict the old "no phase carries the whole slice" claim, so
  warm is a default, not a promise, and it carries **no number** (two hosts, two windows).
  **The seven sites were mostly a deletion problem**: 2 are `DOMAIN.md`, 2 are `SOUL.md` (no
  `agents/` in `-mp`), 1 is the old `CLAUDE.md` — the ~3 survivors point at **one section in
  ticket 07's loop contract** rather than restate it, which is how one answer got copied seven
  times. **The engine writes a handoff of its own** (`run.post.ts:59-75` builds
  `## Context from Prior Nodes` from flow-type edges) — a second channel beside the dossier, so:
  a node's summary names the dossier file it wrote and never restates its content. **`handoff`
  does not become a skill** (portability only, map premise 6) — its two rules do.
  **`phase_procedures.md` dies by name**: `emit_lifecycle` dead, `read_predecessor` → the
  boundary section (it *is* cold resume), `draft_checkpoint_write` → `agent_patterns.md`.
  **Rejected: `boundary:` as edge data** — ticket 15 showed the engine reads `type` alone and the
  schema is loose, so the key would validate and be read by nobody. `debug-handoff` → ticket 07,
  flagged lean-delete.

- [07: Implementation-side consolidation — 16 slice skills to ~6](issues/07-implementation-side-consolidation.md):
  **16 skills / 4,166 lines → 4** — `spec-feature` · `build-plan` · `build-implement` ·
  `build-branch`. The mechanism is ticket 02's find applied literally: mp's `implement` is
  **15 lines that name `tdd` and `code-review`** instead of restating them, so every survivor
  survives as a *step inside* one of the four. **The two absorbed mp skills are not new
  skills** — `to-spec` *is* `spec-feature`, `to-tickets` *is* `build-plan`; the one split mp
  makes (interview, then synthesise without interviewing) is the only split the concept side
  needs, and with `grilling` a global install called by name, **four grill-shaped skills
  collapse to zero**. **`impl-plan-supervised` dies** with its 4-status protocol (ceremony
  over a subagent return value; ticket 09 already kept `agent_patterns.md` for dispatch), and
  **`implement-page` dies outright** — it was an alternative *unit of work*, a page being a
  horizontal grouping in a map whose discipline is the vertical slice. **`build-implement`
  names exactly `tdd` + `code-review`**; the test pyramid stays **flow nodes after the slice**
  so ticket 17 keeps the freedom to reshape it. **Tier stops gating entry and becomes depth**
  inside the skill — with one entry skill per side there is nothing left to route to, which
  deletes `slice_loop`'s tier table, its pinned refuse message, and a fan-out reason from
  ticket 10. **Dossiers stay two but shrink to one file each**, and the concept one is renamed
  **`_concept/dossiers/<feature_slug>/`** (ticket 05 made `slice` impl-only); the per-phase
  handoff files existed to cross a `/clear` ADR 0005 no longer makes. **`spec-feature` writes
  screens**, which hands ticket 08 a boundary: `experience-screens` covers the whole-app pass
  or collapses into it. Contracts: **`slice_loop.md` survives shrunk** (slug + freeze; 3 of 4
  new skills read it), **`plans.md` deleted** — but `PLANS.md`-the-artifact has **9 in-body
  readers**, only 2 in this cluster, so it goes to ticket 18. **Ticket 06's Storybook premise
  was wrong**: `build-foundation` only *themes* an existing Storybook, so **scaffolding goes
  to `mockup-storybook`** (ticket 14), and `debug-handoff` is deleted per ticket 12.
  Graduated **17** (quality), **18** (architecture + build — eleven skills no ticket owned)
  and **19** (write the four).

- [14: Port the mockup domain — write the 4 skills](issues/14-port-mockup-domain.md):
  **17 skills / 6,597 lines → 4 skills / 344 lines of `SKILL.md` + 469 of `references/`** —
  `mockup-walkthrough` (91) · `mockup-storybook` (89) · `mockup-annotate` (78) ·
  `mockup-feedback` (86), all under ticket 03's 140 ceiling, dir == `name:`, no MUST/NEVER.
  Committed `ce0e118`..`f5ea080` on `-mp` `main`, not pushed. **Ticket 06 was wrong about
  `preview_compatibility.md`** — it is 292 lines of per-framework base-path recipes for a
  *scaffolded app* behind the workspace preview proxy, seven readers, all
  `09_impl-architecture/templates/template-*/TEMPLATE.md` and **none in the mockup domain**,
  so it is *not* folded into `walkthrough_renderer.md`: **ticket 18 must claim it or it is
  lost**. `walkthrough_renderer.md` 414 → 446 (absorbs `items[]` id derivation as a
  first-class section, per-renderer copies gone); `elements_block.md` across unchanged.
  **`validator.py` is a *step* of the skill, not test infrastructure**, so it and its fixtures
  ship inside `references/<renderer>/tests/` rather than a top-level `tests/` that would
  pre-empt ticket 16; all five harnesses re-pointed and green. But **the walkthrough harnesses
  do not test the renderers** — they `cp expected/ → rendered/` and validate that, by their own
  headers; only `mockup-feedback`'s apply tests are real integration tests. Four latent bugs
  fixed in the port: the **annotation overlay 404'd on every page but `index.html`** (bare
  `src=` resolved against the nested page's own directory — that is the entire annotatable
  surface); every renderer **hard-gated on `design/tokens.json`, which nothing writes** (brand
  tokens land in `discovery/brand/tokens.json` — a gate that could never pass);
  `patches.schema.json` was **missing `target-promotion`** while `03_patch` emits it and apply
  validates against it; and the "preserved intent" step **cited devlog fields that do not
  exist** (`target_paths`, `patch_summary`) — including in ticket 03's landed astro port, so
  anything else in `-mp` inheriting those names is wrong the same way. Storybook stack
  resolution **asks for six values the templates carry four of**
  (`story_extension`/`component_library`/`icon_library` are in no `TEMPLATE.md`) → ticket 18.
  `05_types` did not port, as ticket 06 ruled; nor did the storybook validator's
  `_concept/experience/4_storybook` target, which nothing writes.

- [08: Concept-side consolidation](issues/08-concept-side-consolidation.md):
  **19 skills → 9, and the artifact tree becomes one numbered root.** Survivors:
  `concept-brief` (absorbs `goals`+`comparable`) · `concept-onboard` (+`seeds`, +mp's
  `to-questionnaire`) · `concept-research` (+`design-inspiration`, +mp's `research`) ·
  `design-brand` · `experience-journeys` · `experience-behaviors` · `experience-shell` ·
  `spec-featuresets` · `spec-feature`. **The screens boundary is W1: the loop owns screens,
  the whole-app skill owns only the shell** — one writer per artifact, which dissolves a
  collision the two writers cannot see today (`design-feature`'s scan looks for a slug segment
  that `screens/<NN_group>/` does not have). `spec-feature` becomes the sole writer of screen
  specs and of `elements:`. **`goals`/`comparable` were already flags twice over and neither
  flag is read** — `metadata.parameters` in no code path, both discovery edges `type: optional`
  (ticket 15: orders nothing) — so folding them moves prose, not behaviour; the cost is the
  flow node, which was the only real UI affordance for a deep pass. **`.allium` dies**: its
  grammar file `references/allium-subset.md` is cited as *"the constructs you may use"* and
  **does not exist** — ticket 03's `EMIT` finding one domain over; the artifact survives as
  markdown state tables (4 real readers). **`design-brand-voice` does not port** (`behavioral.md`:
  zero readers collection-wide) and **`experience-components` dies** — both its readers were
  deleted by ticket 06, and it writes *inside* `screens/`, which every surviving renderer globs
  as `screens/**/*.md` excluding only `00_layout/`, so component specs are **rendered as
  screens** today. **The tree: one root.** `_implementation/` is absorbed as `11_build/`;
  `_concept/` stays because **forge-concept resolves the literal string in four source sites**
  (`project.ts:112`, `artifact-contract.ts:187-188`/`:208-209`,
  `api/concepts/[...name].post.ts:43`) — a neutral root is a forge-concept edit the map rules
  out. **First level numbered, nothing below**: `AppSidebar.vue:332-338` sorts `localeCompare`
  on the raw name, so the filename is the tree's only ordering mechanism, and the host already
  strips `NN_` before display in three components. Number what the collection fixes, leave what
  the project grows — this reverses ADR 0002 at one level *because the artifact tree has no
  flow graph to carry order*, which is the same principle, not an exception. `01_meta` ·
  `02_grounding` · `03_brand` · `04_journeys` · `05_features` · `06_behaviors` · `07_screens` ·
  `08_dossiers` · `09_mockup` · `10_blueprint` · `11_build`, with `brief/goals/comparable.md`
  as root files. **Sequence is dependency order, not the flows'** — `appbuilder-complex` runs
  `behaviors` before `features` while `behaviors`' own gate reads *"when features are
  approved"*. Also: **`concept.yaml` dies** (ticket 09's registry argument, one level down),
  `_seeds`+`_standards` → `02_grounding/`, the mockup family's five top-level names → one with
  **the renderer out of the path**, hyphenated filenames fixing three live writer/reader
  spelling splits, and **no `parameters:` blocks** (tier read from `01_meta/scope.yaml`).
  Recorded as **ADR 0007**; `contracts/concept_structure.md` rewritten 434 → 202 lines.
  Handed off: **10** (two flows need a `spec-feature` loop; the behaviors/features order),
  **16** (every written path resolves to a real top-level entry), **17** (the inspection
  outputs land under `11_build/`), **19** (writes `spec-feature`). Graduated **21** — `14_ops/`
  is 12 skills and **no ticket owned 8 of them** (2,207 lines, four on zero flows).

- [19: Port the slice loop — write the 4 skills](issues/19-port-slice-loop.md):
  **16 skills / 4,166 lines → 4 skills / 284 lines of `SKILL.md`** — `spec-feature` (83) ·
  `build-plan` (78) · `build-implement` (65) · `build-branch` (58), commit `3b21cfe` on `-mp`
  `main`, not pushed. No `references/` at all: the four spend their lines calling `grilling`,
  `tdd`, `code-review` and `resolving-merge-conflicts` and citing five contracts, which is
  ticket 02's mechanism carried the whole way. Written against **ADR 0007's tree, not this
  ticket's body** — the ticket predates 08. Two things the renumbering forced beyond
  find-and-replace: **`_concept/` is no longer read-only to the build side** (`11_build/` *is*
  `_concept/`, so the five old "NEVER modify `_concept/`" lines were describing a boundary that
  moved — `build-implement` states the real one, the slice dossier plus the back-link), and the
  **acceptance-criteria ledger has no home and does not port** (`_implementation/acceptance_criteria/`
  is not a top-level entry in 0007, and minting a twelfth here would decide 0007 again) →
  **ticket 17**. Three deviations from ticket 07's shape. **`slice_id` is no longer
  `feature_slug`:** 07 kept a slug rule whose impl clause says `slice_id := feature_slug`
  (one dossier per feature) while also making `build-plan` *be* `to-tickets` and
  `concept_structure.md` calling the dossier "one vertical slice's" — so the slug now derives
  from the slice's own title, one dossier per slice, with `feature` and `blocked_by` in
  `plan.md` frontmatter and **dependency order in the edges, not an `NN_` prefix** (which is
  also what 0007 requires below level one). **The anti-horizontal nudge is not embedded
  verbatim** in every `plan.md` behind a pinned exact-string validator: ticket 03 puts a
  constraint at the step it binds, so the cutting rule sits in `build-plan` and the
  finish-one-row-first rule in `build-implement` — two rules at their two readers, not one
  block copied into each artifact. **`git-state.yaml` does not port** — `git branch` and
  `git worktree list` already hold branch and worktree, and what is genuinely lost is
  `git-finish`'s remembered merge-vs-PR preference, judged not worth a file. `spec-feature`
  writes its dossier **once, at the end** — warm boundaries (ADR 0005) left the concept side
  with no intermediate file at all, so writing it *is* freezing it. **`build-implement` is 65
  against mp's 15**, and the port names which lines are `_concept/`-awareness and which three
  (the `plan.md` gate, the recap, the forced simplification pass) are discipline this ticket
  required as steps — flagged as the least defensible lines in the four. `contracts/slice_loop.md`
  **73 → 49** (slug + freeze + a four-line pointer at ADR 0005, which asked the contract to
  host that section); tier table, pinned refuse message, `/clear` section and handoff-frontmatter
  table gone. `contracts/plans.md` was never in `-mp` — "delete" was a no-port. ADR 0006's two
  dossier paths marked **superseded by 0007** rather than edited. Found while writing: **the four
  mockup skills are stale against ADR 0007** — `mockup-walkthrough` writes
  `_concept/mockup-walkthrough/<renderer>/` and reads `experience/screens/`,
  `discovery/brand/tokens.json`, `_meta/scope.yaml`; ticket 14 landed before 08 and 08's handoff
  list does not name it, so `-mp` today has four skills on the old tree and four on the new →
  **ticket 16**, as a scheduled repair, not a validator finding. Same for the pre-0007 paths still
  in `artifact_frontmatter.md`, `feedback_loop.md`, `acceptance_criteria.md` and
  `agent_patterns.md`, which is why the four new skills cite those for *shape* and
  `concept_structure.md` for *paths*. **`iron_laws.md` §§ 3, 4, 6 now describe a pipeline that
  does not run** — 3 and 4 gate screens on brand tokens and the data model, but `spec-feature`
  writes screens inside the feature loop before `10_blueprint/` exists; 6 names the `ready`
  skill. Ticket 09 kept the file for its machine-enforced gates; at least two of them no longer
  gate anything. **Worth a ticket.** `contracts/README.md` is stale wholesale (it still describes
  the *old* repo — `cf/`+`saxe/`, `scripts/`, `DOMAIN.md`); only the two rows this change touched
  were fixed, since ticket 09 gave the `CONTRACT`+`README` merge to the rewrite tickets and none
  of them has claimed it by name.

## Not yet specified

- **The port itself, per domain.** **Mockup is done** (ticket 14) and **the slice loop is
  done** (ticket 19). **The concept side is now sized — 9 skills, ticket 08** — and needs its own
  port ticket; the quality and architecture/build ports wait on their own decision tickets
  (17, 18), and the `ops` domain on ticket 21. Each is a rewrite-from-the-model pass, one
  ticket per domain group.
- **The five absorbed skills' actual bodies** — what a skaileup-flavoured `to-spec` /
  `to-tickets` / router / `grilling` / `research` says once it knows about `_concept/`.
  Blocked on knowing which skills they replace. Ticket 04 fixed their *names*
  (`spec-*` / `build-*` / `skaileup` / `concept-*`), not their contents. **Ticket 08 placed
  three of them**: `research` and `to-questionnaire` are steps inside `concept-research` and
  `concept-onboard`, and `to-spec` is `spec-feature` (ticket 07) — so what is left here is the
  router and `grilling`. **Ticket 09 handed
  `contracts/grill_bank.md` here** (0 in-body readers) — it survives only if the absorbed
  `grilling` skill claims it, otherwise it is deleted.
- **The docs site.** `docs/` is a Starlight site that renders every SKILL.md. Port, regenerate,
  or drop — depends on how much frontmatter survives.
- **Opt-in mechanics and the acceptance test.** How a project points at `-mp`
  (`skaile.yaml` deps, lockfiles), and which project plays the "flows load green" role.
- **What carries over from the old repo besides skills** — `docs/devlog/`, git history,
  the improvement backlog.

## Out of scope

- **`15_demo` (7 skills) + the `contract-migration` and `p2p-intake` flows** — domain demos,
  not part of the app-building collection. They belong in a different repo.
- **Cutting `forge-concept` over to `-mp`** — ruled out by the parallel/opt-in decision.
  The map still maps what `forge-concept` reads (see the machine-layer research ticket) so
  `-mp` doesn't break it blindly, but switching it is a later, separate effort.
- **Archiving or renaming the old repo.** Same reason.
- **The multi-product umbrella feature** — `14_ops/contracts/CONTRACT.md` (314 lines,
  `stage: alpha`, `do_not_invoke: true`) and the `ops-project-overview` /
  `ops-project-subsystem-map` skills that read it. Ruled out by ticket 09 on the same argument
  as `15_demo`: a meta-concept spanning several products is a different product from the
  app-building collection. Stays in the old repo.
- **Every forge-concept change — deferred to a successor effort, with a register.** This map
  rules host edits out for sequencing (see Notes), so each ticket below accepted a workaround
  instead. Each entry names the site that forced it, so a later map starts from the list rather
  than rediscovering it:
  - **`artifacts.yaml` is unreachable as deployed** — read only under `--link`
    (`artifact-contract.ts:138`); the default copy install leaves the recursive search finding
    nothing and forge-concept silently falls back to session completion. Ticket 01 found it;
    ticket 09 killed the registry rather than fix the reader.
  - **Input-dialog specs stay in skill frontmatter** — moving them to a sibling `inputs.yaml`
    needs a new frontmatter reader. Ticket 09 accepted the consequence.
  - **The artifact root must be the literal `_concept/`** — resolved in four source sites
    (`project.ts:112`, `artifact-contract.ts:187-188`/`:208-209`,
    `api/concepts/[...name].post.ts:43`), so ticket 08 could not choose a neutral name.
  - **Ordering lives in `NN_` filename prefixes** because `AppSidebar.vue:332-338` sorts
    `localeCompare` on the raw name. ADR 0007 numbers the first level to satisfy a sort, not a
    semantics.
  - **Nothing writes a feedback session** — forge-concept has **zero**
    `addEventListener("message")` repo-wide, so the iframe writer ticket 20 is weighing is a new
    host feature, not a wiring change.
  - **The review surface reads pre-0007 paths** — `server/utils/review-coverage.ts:98` locates
    feature docs under `experience/features/<NN_group>/`, both the old root *and* the
    `<NN_group>` shape ticket 08 removed; `app/pages/review.vue:22` names
    `_implementation/trace.yaml`, a root 0007 absorbed into `11_build/`. **A project on the
    `-mp` tree loses the review surface until the host is updated** — the sharpest entry here,
    because it degrades a feature rather than merely constraining a choice.
  - **`phaseForSkill` hardcodes `ops-eval*`, `ops-review`, `ops-sync`**
    (`shared/flow-phases.ts:23-24`). Inert while `-mp` declares `data.phase` per node, since
    `phaseForNode` prefers the explicit value — but it is a name-level coupling that binds again
    if the phase-per-node rule is ever dropped.
