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

**Read the ticket's brief first.** `.scratch/skaileup-mp/briefs/<NN>-*.md` holds the measured
evidence for a ticket — counts, readers, greps, quoted contradictions — so the session starts at
the tensions instead of re-deriving the facts. Briefs record findings, never answers; a brief that
reads like a resolution has overstepped. Some carry a **`## Post-08 delta`** section: everything
above it predates ADR 0007, and where the halves disagree the delta is later. A ticket with no
brief is not a problem — gather what the question needs and leave one behind.

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
   **Amended by ticket 29:** the flow contract holds, but "top-level `requires:` drives
   transitive install" does **not** — `@skaile/workspaces` 0.48.1 resolves a manifest's
   transitive deps for `bundle` only, so a flow installs its own YAML and nothing else. A
   workspace lists every skill it wants; the `requires:` block is exact and unread.
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

- [13: A triage on-ramp and a durable record of rejected scope](issues/13-triage-onramp-and-scope-memory.md):
  **Both halves resolve to "no new skill", for opposite reasons.** **The triage on-ramp is
  refused — the inbox is upstream.** `ai-assets-skaileup` has 1 issue (closed), `-mp` has 0;
  the 500-issue / 43-`user-feedback` queue is on `platform` + `workspaces`, repos that *have*
  `_concept/` but are not skaileup-driven and are **already triaged with mp's globally-installed
  `/triage`** and its own five labels. The one skaileup-shaped channel — forge-concept's
  per-document comment API (`concept-comment-store.ts`, threads anchored to a `documentId` on a
  `_concept/` file) — **is read by nothing**, so it is a *register* entry, not a missing skill.
  `-mp` instead holds an **intake rule** (`/triage` globally, then enter at `spec-feature` or
  `build-plan`) with **no home today** — recorded as a requirement on the router, in the fog
  patch that owns it. **`mockup-feedback-triage` collapses into nothing** because there is
  nothing to collapse into; ticket 06's fold stands and the two-things-named-triage collision
  never arises. **Two ticket premises were wrong:** "every flow starts from a project brief" is
  false — **no** flow starts at a brief, 7 of 9 addressable flows enter at `scope-project` and
  `skaileup-concept-reverse` enters at `ops-reverse-engineer` (`.flow.yaml:43`); and
  `ops-add-feature` is a real partial on-ramp that is unreachable (**zero flows**) and gated the
  wrong way (hard-gates on `discovery/brief.md`, `:53-55`) — ticket 21 already re-points it.
  **The second half was closed too early, and this ticket splits it in two.** Ticket 05's noun
  stands (a refusal *is* a decision record marked rejected, no `.out-of-scope/`), but that ruling
  described an artifact **nothing produced**: no `-mp` skill wrote a decision record at all, and
  in the old collection 12 skills write the two logs and **none writes a refusal**. So —
  **the reader stays absent, deliberately: `-mp` ships no re-litigation guard**, and the record
  is documentation a human consults, not a check that fires (mp's `.out-of-scope/` earns its keep
  at *read* time, `OUT-OF-SCOPE.md:74-76`, and that step no longer exists once triage is refused);
  **the writer is supplied here** — `spec-feature` step 4 appends an OUT clearing the three-test
  gate to `10_blueprint/decisions.md` with Status `rejected` (`SKILL.md:61-64`), because
  `## Out of Scope` is one feature's and **freezes with its dossier** while re-litigation is
  cross-feature. Two contract defects blocked that writer and are fixed rather than swept, since
  a path check can neither invent a status nor choose which log a refusal binds to: **`rejected`
  added to the Status enum** (`domain_model.md:87-91`) with the collision spelled out — it is
  *the choice was refused*, **not** the "rejected alternatives" of *Options considered* — and the
  **decision-log paths corrected to `10_blueprint/decisions.md` + `11_build/decisions.md`**
  (`:9` and `:75-76`, which also disagreed with each other). **Accepted residue:** the three-test
  gate is narrow, so most refusals fail it and stay in a frozen per-feature dossier. **Flagged,
  not fixed:** `CONTEXT.md:100-101` says three decision-record levels, the contract gives paths
  for two. To **ticket 16**: `mockup-feedback`'s **journey branch has no target of that shape**
  (`triage.py:29-31` wants `<subdir>/<value>.md`; `04_journeys/` holds one `stories.yaml`) — a
  dead branch, not a stale string; plus `domain_model.md`'s remaining pre-0007 *glossary* paths
  and its phantom `skaileup-domain-model` skill (`:133`).

- [17: The `quality` domain — 13 skills, and which of them still have a job](issues/17-quality-domain.md):
  **13 skills / 2,833 lines → 4** — `quality-review` · `quality-test` · `quality-e2e` ·
  `quality-standards`. The through-line: this domain has **four globally-installed competitors**
  (`code-review`, `tdd`, `diagnosing-bugs`, `improve-codebase-architecture`, all four verified
  present), and they own *how to look at code* — so nothing that survives here is review
  technique. **`quality-review` is ticket 07's `implement` mechanism inverted**: it does not
  restate the review, it hands `code-review` the two inputs `code-review`'s own body says it
  must ask a human for (fixed point from `commits[]`/`source_files[]`, spec from
  `05_features/`), then adds the four things no global skill has — the **security** and **a11y**
  axes, the **AC-ledger honesty check**, never-review-as-the-implementer, and `refactor.md` as
  context. **`audit` dies** — its whole-repo scope is `improve-codebase-architecture`'s and its
  Phase 2 is `ops-review`'s **by its own admission twice over** (`audit:52` sends you to
  `review` for the work `audit:127-131` then performs); it was also the only "review" skill that
  **edits code**. **`eval-code` dies as a skill, survives as two lines** — build+test is
  `build-implement`'s in this map's model, its `scaffold` scope is `build-scaffold`'s done-check
  (→ 18), and its verdict artifact — **the domain's only artifact with a real reader** — is
  inherited. `appbuilder-complex` was running **the same three sub-agents three times over the
  same code**. **The test trio splits at the tool, not the level**: `test-unit`+`test-integration`
  are the same five-phase machine and today's per-tier subsets (`{u}`/`{u,e}`/`{u,i}`/`{u,i,e}`)
  are what a **set-valued parameter** looks like — same argument ticket 06 used on the renderer —
  while **e2e is a different tool** (`agent-browser`, platform gate, journeys from
  `stories.yaml`). **The gate cost lands on the intersection, not the union** — integration's
  `model.json`+`.env.example` become a check at the step that needs them (ticket 03's rule)
  rather than frontmatter that blocks `appbuilder-mvp`. The 24%/40% vitest boilerplate drops.
  **The debug pair dies whole** — four collisions with `diagnosing-bugs`, not a nuance: it
  elicits the hypothesis **before any command is inventoried** (the named forbidden move), *"save
  for later"* is an accepted terminal state so it can complete having run nothing, and **both its
  schema and its `validator.py` make the red signal optional**; its four real additions are
  artifact and interview mechanics, and `_debug/` has no home in ADR 0007. **`standards-inject`
  was always a contract** — zero in-body callers out of 95, writes nothing, and its five steps
  are `agent_patterns.md § Standards Injection` **step for step**; its auto-wrap
  (`modes.standards.inject_skill`) is in the block ticket 15 found has no reader in any host, and
  the artifact's two real readers **read `index.yml` directly, never through it**.
  **`standards-sync` dies** on two fictional inputs (`cf__shared/profiles.json`; the prefix has
  not existed since the migration). Its schema contradiction **needed no ruling — ADR 0007
  already documents `applies_to` + `keywords`**. **`ready` leaves `quality`** without ambiguity
  (`Never load: Source code`, `WRITES (none)`) and is the **fourth** thing checking the same
  `_concept/` integrity → merge-or-keep to **21**, law 6 to **22**. **`test-plan` dies** — zero
  flows, two `Optional` readers that never branch, and its AC accounting is the `.ac.md` ledger's,
  upstream and unread. **The ledger gets a home, shrunk to the join** (ticket 19's handoff):
  `11_build/acceptance-criteria/<featureset>/<feature>.ac.md`, rows citing `AC-n` + the spec
  instead of **copying the EARS line verbatim**, created by `build-plan`, flipped by
  `build-implement` + `quality-e2e`. **One verdict artifact, not two** —
  `11_build/reviews/<feature_slug>.yaml`; `review/<slug>.yaml` and `audit-report.md` had 0
  readers each. **Ticket 08's other two placements go to 21** — drawn on the *writer* rather than
  the artifact's shape, `quality.yaml`/`eval-concept.yaml` are `ops`-written, which is also why
  08's shape-drawn list of three missed `eval-code.yaml` and `review/<slug>.yaml`.
  `evaluator.md` survives on four readers (three of them 21's); `evaluate-contract` does not port;
  `analysis_checklists.md` becomes one skill's `references/`. Graduated **23** (write the four,
  plus three authorised edits to landed skills).

- [20: Who writes a feedback session — the annotate → triage seam](issues/20-feedback-session-writer.md):
  **Neither of the ticket's two writers — the standalone path simply did not work, and all
  three faults were inside files `-mp` owns.** `type="module"` on the injected tag **blocks
  the overlay entirely over `file://`** (module scripts are CORS-fetched, a `file://` origin is
  opaque, and the overlay has zero `import`/`export`) — against a renderer whose stated promise
  is *"a stakeholder can open `index.html` from a shared folder"*, so **the Download branch was
  never reachable the documented way**. Sharper than the brief: `annotations` was in-memory
  while `SESSION_ID` persisted, and a walkthrough is many pages with iframe-only navigation
  interception, so **the array emptied on every link click** — five annotated screens yielded
  one. And the documented rename guaranteed stem ≠ `sessionId`, so **every round read as
  unapplied forever**. Rulings: **the browser path is supported and the iframe branch is kept
  correct but unused** (forge-concept has no listener, no route, no store; "iframe only" would
  hang `-mp`'s feedback half on an unbuilt feature in a fenced repo, and the stakeholder who
  annotates is the one who cannot be given a login). **The overlay owns the id and the
  filename** — zero code ever read the stem, five call sites read the field — and the
  human-readable name becomes a **`label` inside the file**, asked for by `mockup-feedback`'s
  new **adopt** step, which takes the download from any path and files it itself (gate
  **hard → soft**: a hard gate refused the skill in exactly the case adoption handles).
  **`index.json` deleted** — no reader, no writer, no schema; a registry of gitignored files a
  skill must remember to append to is stale by construction, which is why it was already empty.
  Both riders ruled: **`specRef.feature` routing deleted** (no producer — `resolveTarget` and
  `walkthrough_renderer.md` both lack it; a router key with no producer reads as coverage),
  **journey re-pointed at `stories.yaml`** — and, found while doing it, `apply.py` anchors on
  literal markdown headings and its **no-removes path appends to end-of-file** (`:58-61`), so
  aimed at YAML that is silent corruption: journey annotations resolve but are **`needs_manual`,
  never patched**. Annotations on `index.html` are **unresolved by design** (`data-spec-index`
  only). Landed **uncommitted** in `-mp` — a ticket-16 session is live in the same tree, and the
  two changesets are interleaved in `mockup-{annotate,feedback}/SKILL.md`. All harnesses green;
  the 0007 path sweep stays **16**'s, with `triage.py`'s paths now named constants for it.

- [16: CI and validation — what replaces the DSL validators](issues/16-ci-and-validation.md):
  **Nothing ports; one script replaces all seven, and its first run found six defects no ticket
  had counted.** `scripts/check.py` + `scripts/test_check.py` (28 cases) + one Actions job,
  commit `e1fbfb4` on `-mp` `main`, not pushed. Three of the seven validated things tickets 03/09
  deleted, one gates frontmatter fields ticket 01 showed nothing reads, one validates a *target
  project* so nothing here can run it, and the pre-commit hook **was never installed in any
  checkout** — no repo in the eight-repo ecosystem has an active hook, so **Actions only, one job,
  landing now** rather than when the collection is populated. `verify_flows.py`'s rules survive
  rewritten: its three hard deps (`skaile.yaml`'s `assets:` block, a hardcoded flow registry, the
  two-level layout) are all things `-mp` removed on purpose. **The bar is that the failure mode is
  silent** — a loud failure needs no validator. **`flow.schema.json` is deleted, not narrowed**
  (ticket 15's ruling executed): it invented `gate` and `review-loop`, required `position` nothing
  reads, and was `additionalProperties: false` at 27 sites against a `looseObject` runtime. Its one
  live rule, the `data.phase` enum, is four lines of Python — but the decisive argument is
  **expressiveness, not size**: the sharpest flow rule (an edge without `type: flow` orders
  nothing) is a property of the *graph*, so the check is **reachability from `entry` along
  flow-typed edges**, one assertion subsuming ticket 15's untyped edge, the `review-loop` no-op and
  a disconnected subgraph. **The legal top-level path set is parsed out of
  `concept_structure.md`'s fenced tree, never restated** — contract and check cannot drift.
  **`requires:` exactness earns its keep despite no runtime reader for exactness**: a *missing*
  entry means the skill is never installed and forge-concept runs the node with a generic prompt
  while reporting `satisfied: true` — a live silent failure, not a house rule. Refusals with
  consequences: **`lint_concept.py`** dies twice over (it validates someone else's repo; and its
  model half judges the *derived* `postxl-schema.json` by PostXL conventions that invert
  `golden_principles.md:13,23` — the ticket-06 category error, now sharper since
  `concept_structure.md:183-187` makes PostXL one of **four** formats) → its live half is prose in
  an `ops-` skill, **21**'s to place, and **ticket 09 kept `golden_principles.md` because a machine
  read it, which was this linter** → **22**. **`ac_lib.py`** follows the ledger ticket 19 found has
  no home in 0007 → **17**, with 09's shrink aimed at the wrong half (it kept the EARS section no
  code reads; `ac_lib` validates ledger *structure*). **`validator_lib.py` does not port and
  per-skill validators are not a standing cost** — `-mp` had already converged, all three shipped
  validators are self-contained, so `audit.py`'s `stage: stable ⇒ validator.py` rule dies with its
  premise. Swept: the 10/10 stale prerequisite paths + their body prose, `domain_model.md`'s
  glossary paths and its phantom `skaileup-domain-model` (now the global `domain-modeling`), and
  **`contracts/README.md` rewritten wholesale** — it still described the old repo's `cf/`+`saxe/`.
  **The citation check was the one addition beyond the ticket's four questions and paid for itself
  on the first run**: three of its six finds appear in no brief. Found while indexing:
  **`evaluator.md` has zero readers in `-mp`** — not ruled, it is 17/21's. Ticket 13's journey
  branch was **ruled by the concurrent ticket-20 session on better evidence** (journey → whole
  `stories.yaml`; **`feature`** is the dead branch — no renderer emits `data-spec-feature`); this
  ticket did only the path half. **Residue:** four files are interleaved with that live session and
  **left uncommitted** for it to land; `mockup-annotate/validator.py` stays at the skill root
  (approved for the move, then not done — that session has the file open); and the flow half has
  **no live subject**, so ticket **10** should expect to adjust the reachability model when real
  flows land.

- [21: The `ops` domain — eight skills nobody owned](issues/21-ops-domain.md):
  **8 skills / 2,207 lines → 1 in `ops`, 1 renamed out, 1 handed to `quality`, 5 dead.**
  `ops-review` absorbs **`ops-sync` + `ops-trace` + `ready` + `audit` Phase 2** — four
  implementations of one check. `ops-sync`'s only stated difference is *"every change is
  previewed"* (a step, not a boundary), and **ADR 0007 killed two of its three remaining jobs**:
  its group-alignment check matches a shape that no longer exists, and the feature↔screen drift
  it repairs is largely unreachable once W1 made `spec-feature` sole writer of both trees.
  **`ops-eval-concept` dies with zero callers of any kind** (181 lines; its one mention is a list
  of who reads a contract), **`ops-eval-feature` dies** into `quality-review`'s AC-honesty check,
  and **`ops-eval-product` survives as `quality-release`** — the only skill that closes the loop
  back to `brief.md` + `goals.md`. **Ticket 17 resolved before this ticket's note could reach it**,
  so those two were owned by nobody and are ruled outright here rather than bounced to a closed
  ticket. **`ops-add-feature` dies into ~4 lines of `spec-feature`**: the five-artifact cascade
  (+162 lines of `cascade_rules.md`) is the multi-writer pattern ticket 08 dissolved, so what
  replaces it is *naming which skill to re-run*; only the blast-radius grill and a
  *"preserve existing `screens:`/`data_entities:`"* data-loss guard carry.
  **`ops-reverse-engineer` becomes `concept-reverse`**, a thin orchestrator on ticket 02's
  mechanism — it keeps validate, repo discovery and its own confidence grading and *calls* the
  five writers instead of restating their templates; the ~210 lines of stack detection are the
  one thing no other skill owns → `references/detection/`. It leaves `ops` because it **writes**
  `_concept/`, which ticket 04's line never covered. **`ops` survives as a one-skill domain** — a
  domain is a name segment, not a folder, and a prefix is mandatory anyway — but **ticket 04's
  `quality`/`ops` line is now blurred and recorded as a live tension**: ADR 0007 folded
  `_implementation/` into `11_build/`, so the merged `ops-review` reads the build half and
  `git ls-files`, and 17 hit the same line from the other side. `quality-review` / `ops-review`
  is not a collision but that line stated in the names. **This ticket's own first answer was
  wrong and 17's placement won**: a twelfth root `12_review/` was minted on the finding that
  `review-coverage.ts:135-146` **unions three files by feature id**, then withdrawn — all three
  were under `_implementation/`, which ADR 0007 already renames to `11_build/`, so the host's fix
  stays **one prefix** rather than a re-homing. → `11_build/review.yaml` + `11_build/trace.yaml`;
  `01_meta/` is ruled out by 0007's own read direction. Accepted oddity: a concept-only project
  grows an `11_build/` holding one review. **`contracts/evaluator.md` survives on a basis 17
  could not have had** — it kept the file on four readers, three of them the `ops-eval-*` this
  ticket deletes; the three that remain (`ops-review`, `quality-review`, `quality-release`) still
  clear ticket 09's bar. Two defects → ticket 23: its header names five readers, four dead, and
  17's pinned *"`approve` ⇒ zero critical and zero high"* uses a severity vocabulary the contract
  does not have (`blocking|warning`). **Register: two entries change, no new constraint** —
  `phaseForSkill`'s four hardcoded names reduce to one that still exists, and the review-surface
  entry **downgrades from a redesign to a prefix change**. **Graduated 26** (port the concept
  side — 08's nine plus `concept-reverse` and `ops-review`), which **empties the
  port-per-domain fog patch**: every domain is now sized and every port has a ticket.

- [18: Architecture + build — the eleven skills nobody owned](issues/18-architecture-and-build.md):
  **11 skills / 2,706 lines → 5** — `architecture-{techstack,system,datamodel}` ·
  `build-{scaffold,database}`. **`architecture` stays a domain**: every flow that declares a
  phase puts it in `conceptualization` and build in `implementation`, and
  `skaileup-concept-only` runs the whole block without ever reaching build. **One rule did most
  of the work — ADR 0009: stack-specific knowledge lives in a template; a skill is stack-neutral
  or it is not a skill.** It kills `generate` (25% vendor tokens, zero flows, its STEP 3/5 *is*
  `template-postxl`'s `## Codegen`) and `infrastructure` (which admits the NestJS assumption in
  its own body while wearing a stack-neutral name), and **re-grounds ticket 06's
  `storybook-types` ruling**, whose "PostXL-only" criterion would also have condemned
  `template-postxl`. **The mass was never in the skills:** `templates/` is 3,799 lines to the
  eleven skills' 2,706 and **`-mp` had no `templates/` at all** — it becomes a root asset kind
  beside `skills/`/`flows/`/`contracts/`/`profiles/`, dir name == template id, **no line
  ceiling** (03's 140 governs instruction, not reference data). **The skill↔template contract was
  broken for every key any skill extracts — 0/7 across all eleven names**, so `foundation`'s
  "ask the user if the profile is missing a section" branch **fired on every run**; the fix types
  the seam — **atoms** in template frontmatter, **recipes** as named sections cited by heading,
  and no skill names either unless it exists. **`PLANS.md` dies, and so does project-level
  `progress.yaml`** (ADR 0010): the nine readers were three disclaimers, one different file and
  one existence test; order is the flow graph and status is duplication, and **0007 gives
  `11_build/` no slot for either**. Residue re-homed — `## Raw Description` is an *answer* for
  `onboarding.yaml`, Source Artifacts is recomputed not stored, the backlog note goes to 21.
  `templates-select` folds into `techstack` (it **no-ops when `techstack` did its job**, behind a
  second checkpoint over the same field); `scaffold`+`foundation` merge; `migrate`+`seed` merge
  (3% and 8% per-ORM, and seed was written by **three** skills today). **`foundation`'s Storybook
  step gated on the mockup project to theme the app's** — it dies, and the built app gets no
  Storybook from this collection. **`impl-build-docs` was never a build skill** — `agent-framework/`
  source paths, "relative from monorepo root", an `ai-resource-loader` exclusion: it is *this*
  repo's doc tooling misfiled, which also **narrows the "docs site" fog patch** to
  `generate-skill-pages.mjs` alone. `preview_compatibility.md` is claimed but **relocated to
  `templates/`** — its seven readers are templates, not skills, so it fails 09's contracts bar.
  `prog-expert-*` stops being a `MUST`: `skaile.yaml` has **no dependency mechanism**, so the
  cross-collection dep is not expressible. **`architecture-datamodel` gains
  `10_blueprint/glossary.md`**, a 0007 tree entry nothing wrote. Landed in `-mp` (`5dcdab8`): **ADR
  0009 + 0010**, `docs/adr/README.md` (which was also **missing 0007**), and `CONTEXT.md` gaining
  the **datamodel / database** pair. Graduated **24** (port the templates) and **25** (write the 5),
  **strictly ordered** — skills that read atoms cannot land before the atoms exist. To **10**:
  the two sub-flows go 11 nodes → 5 and their `type: optional` edges order nothing. To **16**:
  `-mp`'s `profiles/` still carry pre-0007 paths, plus a template-atom check. **21 resolved
  concurrently and absorbs both of this ticket's handoffs**: it deletes `ops-add-feature`, so the
  backlog note dies with it, and its merged `ops-review` has no PLAN-DRIFT indicator to port.
  ADR 0010 leaves the **per-slice** `progress.yaml` alone — only the project-level file dies.

- [22: The iron laws describe a pipeline that no longer runs](issues/22-iron-laws-re-rule.md):
  **`contracts/iron_laws.md` deleted — ADR 0008.** The ticket asked which of two contradicting
  things was wrong, laws 3+4 or `spec-feature`'s soft gates. **Neither. Both dependencies
  survive and both moved downstream, and both are already gated where they moved to** — a screen
  *spec* is prose plus `elements:` and consumes no tokens, *rendering* does
  (`mockup-walkthrough:15`, `mockup-storybook:15`, hard); a screen spec becomes buildable at
  `build-plan`, which is where the datamodel is gated (`:16`). The laws named the wrong step, so
  re-cutting them would write down nothing not already declared — which is what killed the file
  rather than amending it. **Three findings, in weight order.** (1) **The genre was already
  ruled out by the collection's own vocabulary**: `CONTEXT.md` defines a gate as *"stated at the
  step it binds"*, and a central register is what that forbids — settled at ticket 05, never
  applied here. (2) **Ticket 09's machine-enforced premise fails twice over, not once**: the
  prose does not enforce the gates and **neither does the frontmatter** —
  `parseSkillRequirements` reads `fm.metadata ?? {}` with no root fallback
  (`resolver/src/parser.ts:45-46`, identical in the deployed `@skaile/workspaces@0.48.1` bundle)
  and **no `-mp` skill has a `metadata:` key**, while `validator.ts:81` joins against the
  *project* root and no `-mp` path carries `_concept/`. So **ticket 19's demotion of two gates to
  soft changed nothing observable — `spec-feature`'s two *hard* gates are equally unenforced** →
  new ticket **27**. (3) **The reader evidence is a completed experiment, not a mid-port count**:
  0 in-body readers in `-mp`, and across the old collection's 95 skills over the file's whole
  life the six path laws were cited **zero times** — all 84 references named law 7, 8 or 9. *The
  half that was cited is the half no `gate:` field can hold.* **Every law had a home already**:
  1 and 5 are live hard gates (5's `mock` skill was a phantom name, nothing more), 7 and 9 are
  verbatim in `agent_patterns.md`, **8 is stated at all three of its steps** (correcting the
  brief, which had it homeless), 6's own second clause is satisfied by `build-plan:13-16` +
  `build-implement:13-15`. **Both tables die**: the Rationalization Defense is *the pre-ADR-0003
  form of a `MUST`/`NEVER` block*, its one live row already at `build-implement:35-39`, two rows
  restating law 9 a third and fourth time, one pointing at a `prototype` **flow** that has never
  existed. **The ruling is narrow — a gate register, not every zero-reader contract.**
  `agent_patterns.md` and `golden_principles.md` are *also* 0-reader in `-mp`, so reader count
  alone was never the bar; the distinguishing fact is that `-mp` holds **8 of ~30 skills**, so
  their readers are **unbuilt, not absent**. Both are **kept on notice** using the disposition
  `evaluator.md` already carries in `contracts/README.md` — a row naming the tickets that would
  read it, dying with them — a pattern that has already paid off once (17 found `evaluator.md`
  four readers). On `golden_principles` **ticket 16's handoff inverted the expected answer**:
  `lint_concept.py` *was* ADR 0004's machine, it is deleted, and it **contradicted** the contract
  it enforced (`:13,23` snake_case semantic layer vs the linter's PascalCase against the
  *derived* PostXL schema) — **content sound, reader wrong**, the inverse of `iron_laws`.
  **What is removed without replacement:** nothing says a screen spec written before the datamodel
  is revisited when it lands. `build-plan:16`'s soft gate is **not a surface** — soft is excluded
  from `satisfied` (`validator.ts:149`), never warned on, and the one route that would fetch the
  report has **zero callers** → to **25** with law 2, and until 25 lands the loss is real. ADR
  0004 gains a partial-supersession note (append, never edit — 19's precedent with 0006);
  `contracts/README.md` loses one row, which makes its "Thirteen files" sentence true;
  `scripts/check.py` green at 8 skills / 0 errors. Handed off: **27** (new, blocked on 16's path
  sweep committing — fixing nesting first would turn four dead gates into live wrong ones, the
  bug class ticket 14 already fixed once), **25** (law 2 + law 4's residue + `golden_principles`),
  **26** (`agent_patterns` on notice with five stale sites; `golden_principles`' second reader,
  since 21 put `ops-review` in that port).

- [27: Every skill's gates are invisible to the only reader](issues/27-frontmatter-shape-repair.md):
  **The machine layer moves under `metadata:` and every declared path gains the `_concept/`
  prefix — ADR 0011.** Proven against the deployed `@skaile/workspaces@0.48.1` bundle, not the
  source: `mockup-walkthrough` parsed **0 gates and reported `satisfied: true`** on an empty
  project before, **4 gates and `false`** after. Three readers, three silent failures —
  `parser.ts:45-46` (no root fallback), `requires-graph.ts:236-238` (early return), and
  `validator.ts:81` (joins the *project* root, so an unprefixed path resolves one level too
  high). **Fixing the reader instead was rejected on sequencing, not merit** — one line in
  `parser.ts` beats a nesting nobody wants, but it means a `@skaile/workspaces` release and a
  forge-concept bump mid-migration → register entry, the successor effort's cheapest item.
  `name`/`description`/`version` stay at the root, which `discover.ts:705-719` normalises both
  ways. **`artifacts.requires[]` drops `gate:`** — decided not by deadness but by **divergence**:
  three of eight skills declared a soft artifact with no matching entry in the block that
  actually gates. **Soft gates keep the declaration and gain a sentence at their step**, since
  soft renders nowhere for a human. **`docs/skill-template.md` was the origin** — it showed the
  root shape and stated the opposite of the truth about `gate:`; every skill written since
  inherited it, so it is fixed with them, as are both worked examples (plus the pre-0007 paths
  16's sweep missed). `check.py` gains a rule per break, each with a test (31, up from 28).
  Also: ticket 16's stranded path sweep committed as `e63316c` (it was this ticket's blocker),
  and ADR 0008's missing index row restored. To **23-26**: write the nesting and the prefix from
  the start; `check.py` fails the build otherwise.

- [10: Flows and tiers](issues/10-flows-and-tiers.md):
  **17 flows → 4, and `tier` retires: a flow *is* the tier.** They were 1:1 all along
  (`scope.yaml.flow_to_run` was the mapping), so they collapse into one word — `scope.yaml`
  records **`flow:`**, the eleven `tier` readers read `flow`, `CONTEXT.md` loses **Tier** and
  **Flow** absorbs the sizing sense. Forced by measurement: **`appbuilder-standard` and
  `appbuilder-complex` reference the identical six sub-flows and differ by exactly eight skill
  names**, every one of which tickets 08/17/06 delete or the map rules out of scope — after the
  port `complex` has no content, so keeping it meant a byte-identical copy or inventing scope
  to defend a name. Survivors: **`appbuilder-mvp` (9 nodes) · `appbuilder-standard` (27) ·
  `skaileup-concept-only` (14) · `skaileup-concept-reverse` (9)**. **The flow list is an
  unfiltered user menu** — `profiles.get.ts:10` turns *every* loaded flow into an onboarding
  profile and `OnboardingWizard.vue:41` renders them with no filter, so the six "shared
  building blocks" were 6 project-start cards; they **inline**, deleting the `sub-flow` kind
  (27 of 175 nodes), and `skaileup-slice-{concept,impl}` go with them (after ticket 07
  slice-concept is **one node**). Asked to check the smaller size, **two mvp steps turned out
  unrunnable, not merely unneeded**: its mockup node hard-gates on screens
  (`SKILL.md:132,162-163`) in a flow with **no screen writer** — dropped; and `build-scaffold`
  would inherit `foundation`'s hard gate on `tokens.json` in a flow with no brand node — the
  brand step **becomes conditional** (→ 25). mvp keeps **no data layer** by choice. **One
  forced reordering: the mockup moves after the `spec-feature` loop** — W1 made `spec-feature`
  the sole screen writer, so in today's order the mockup renders one shell; plus `features`
  before `behaviors` in **two** flows, not the one 08 named. **Three host corrections:**
  routers are **live and interactive** (`route-choice.post.ts` persists the pick,
  `computeUnchosenSkips` prunes branches — manual routing, not conditional; `-mp` still ships
  zero), **group nodes are load-bearing** (`flow-layout.ts:87-93` draws swimlanes and **group
  phase overrides node phase**), and a flow's **`requires:` is confirmed live**
  (`workspaces/core/src/manifest.ts:428-431`). **17's `parameters:` ruling is overturned** —
  `data.parameters` has **one** live read host-wide (`parameters.flow`), so `quality-test`
  reads `flow` from `scope.yaml` instead (→ 23). Deleted as decoration: `meta.category` (all
  six values fall through), `globals.{approval_mode,subagent_mode,verbosity,concept_depth}`
  (0 readers), every `${...}` (**no resolver exists**). **The loop stays out of the graph** —
  the host honours **only `type: flow`** edges and iteration has never been machine-expressed
  (`appbuilder-standard:11-12` is a comment), so it lives in the skill bodies; ticket 12's
  rejection of `boundary:` is the precedent. **`skaileup-scope-scope-project` was owned by no
  ticket** despite being the 7× entry node — ruled here, renamed **`concept-scope`**, stripped
  of flow choice, schema `flow · project_type · reasoning · signals · chosen_at` (→ 26).
  **`cli` demotes to `project_type`, not to a tier** — `contracts/profiles/*.yaml` had **zero**
  in-body readers while `project_type: cli-tool` was already live, so the tier was the
  duplicate; this also gives ticket 18's relocated `profiles/` its first reader. Variants:
  `concept-only` + `concept-reverse` survive (both **gain the `spec-feature` loop**, without
  which neither writes a screen); **`skaileup-implementation` dies** (100% sub-flow + group)
  and **`stepwise` dies** (pacing is what ticket 12 moved into warm/cold boundaries), costing
  `input_style: freeform` its only user. **The map's destination line was already false** —
  the acceptance test asserts on `concept-goals`, which 08 deleted, so it needs more than a
  repo URL change; editing its arrays is an **acceptance-harness** edit, inside this map,
  unlike the host *behaviour* changes in the register. Graduated **28** (write the four flow
  YAMLs) and **29** (the acceptance run).

- [24: Port the templates — 7 × TEMPLATE.md into `templates/`](issues/24-port-templates.md):
  `templates/` exists at the repo root as a **fourth asset kind** (4,603 lines / 9 files), dir
  name == template id. The typed seam is **16 atoms, not ADR 0009's nine** — the ADR's
  parenthetical omitted the five Storybook keys ticket 14 needs plus `env_setup_command` and
  `project_structure`, both of which `build-scaffold` extracted by name. All 16 are **7/7**,
  verified twice (literal grep + YAML parse); every template declares every atom with a value or
  an explicit `null`, so no skill needs a missing-key branch — the exact defect ticket 18 found
  in `foundation`. **The nulls are answers, not gaps**: `env_setup_command` is null 7/7 (no
  scaffolder emits `.env.example`; the contents are recipe material), `lint_command` null on the
  four bun stacks (`nuxi init` / `sv create --no-add-ons` install no linter), and
  `component_library` null on the two minimal stacks *is* the branch a storybook skill should
  take. Every atom traces to prose — asserted values not in the source got a grounding line.
  `impl-build-generate` is absorbed whole into `template-postxl`'s `## Codegen`, four-level
  cascade as a table with the check that makes level 2 real (count `<<<<<<< Custom` markers
  before and after). `## Seed` added 7/7 — `impl-build-seed`'s per-ORM layouts were written down
  nowhere else. `preview_compatibility.md` ports to `templates/`, its seven readers being the
  templates themselves. **Ticket 24 found its own premise half-wrong**: the
  `preview_compatibility → walkthrough_renderer` row was never in `-mp`'s `contracts/README.md`
  (ticket 16 rewrote that file wholesale) — what was missing was the *pointer*, now a "What is
  not here" entry recording the fold that never happened. Full atom matrix lives in
  `templates/README.md`, the one place tickets 25 and 16 both read. Unblocks 25.

- [23: Port the `quality` domain — write the 5 skills](issues/23-port-quality-domain.md):
  Five skills at 61–89 lines — `quality-{review,test,e2e,standards,release}` — plus the three
  out-of-domain edits ticket 17 authorised but did not make: `build-plan` writes the `.ac.md`
  ledger, `build-implement` flips its rows, `contracts/acceptance_criteria.md` drops 253 → 91
  and down to the join. **The port found two defects in the ledger the decision tickets could
  not see**, both at the seam with the host: the markdown table shape 17 inherited **parses as
  zero criteria** (`review-coverage.ts:83-92` matches `- [PASS|FAIL|x|X| ] <text>` line by
  line, so the coverage page silently reports every feature untested) — it is checkbox lines
  now, with `feature:` required in frontmatter or the id falls back to the *featureset*
  directory; and the verdict tokens are **`approved` / `changes-requested`**, the only two
  `review-coverage.ts:158-162` accepts. 17 pinned the rule, not the token. **The severity clash
  resolved toward the contract, not away from it**: `evaluator.md` now carries four levels
  (`critical|high|medium|low`) and *defines* blocking as critical-or-high, because severity does
  two jobs — the boundary picks the verdict, the ordering ranks the fix list, and two values
  cannot do the second. The contract had already contradicted itself (its bottom band cited
  "any critical finding", a value its flag shape lacked); law 6 survives word for word, so
  ticket 22's territory is untouched, and the host reads `severity` as a free string. Three
  notes forward: **`check.py` is stricter than the reader it protects** — it rejects any
  prerequisite path outside `_concept/`, so no skill can declare a `package.json` gate even
  though `validator.ts:81` resolves it, and every source-exists gate lives at its step instead;
  `contracts/{artifact_frontmatter,feedback_loop}.md` are **still on pre-0007 paths**, missed by
  ticket 16's sweep; and `CONTEXT.md` has no words for *finding*, *verdict* or *severity*, now
  used by three skills. Register: `11_build/reviews/` is a **second** host change beyond the
  ADR 0007 prefix — the host walks `_implementation/review/`, singular.

- [26: Port the concept side — write the 10 skills](issues/26-port-concept-side.md):
  Twelve skills, 926 lines, **62–107 each** — the whole concept half plus ticket 10's late
  `concept-scope` and the `spec-feature` blast-radius edit. **`ops-review` took fallback zero**:
  ~900 source lines from four skills fit in **107 of 140 as a single file**, no
  `references/checks.md` and no split. The reason generalises and is the ticket's real finding —
  they were four implementations of *one walk over one tree*, and their bulk was **restating
  contracts that already own the rules** (`evaluator.md`, `golden_principles.md`,
  `artifact_frontmatter.md`, `feedback_loop.md`, `concept_structure.md`); twelve steps sequencing
  four contracts is the whole skill. **The 140 ceiling is not under pressure from merge size, it
  is under pressure from restating contracts.** `CONTEXT.md`'s live conflict was not `tier`
  (already retired by `ac056b2`) but **Profile**, defined as "a project's type" with
  `_Avoid_: project type` against ticket 10's pinned machine key — split into **Project type**
  (what is built, word matching the key) and **Profile** (the asset describing one), the same
  move ADR 0005 made for *template*. **`profiles/*.yaml` rewritten 483 → 97**: `concept-scope`
  is their first reader and they declared an entirely different artifact tree.
  **`contracts/grill_bank.md` is dead** — its nine pillars are already inlined at
  `spec-feature:42-54` where they bind, and ticket 09 handed the rest to "the absorbed `grilling`
  skill", which turned out to be a global install, not a `-mp` asset. Four notes forward:
  **`11_build/review.yaml` sits one letter from ticket 17's `11_build/reviews/<slug>.yaml`**
  (21 and 17 never saw each other — worth a rename ticket); `contracts/artifact_frontmatter.md`
  is **wholly** pre-0007, missed by sweep `e63316c`; `contracts/README.md`'s "no reader yet" rows
  for `golden_principles.md` / `evaluator.md` are now false; and `05_features/featuresets.md` is
  caught by `mockup-walkthrough`'s glob as a phantom manifest feature. Register, latent → live:
  seven skills declare `inputs_optional`, so the host writes to
  `_concept/_grounding/<skillId>/input.json` (`validator.ts:107`), a directory ADR 0007
  abolished — nothing breaks because **no skill body names that path**, deliberately. The
  workaround is the silence; the fix is the host's.

- [25: Port architecture + build — write the 5 skills](issues/25-port-architecture-and-build.md):
  **11 skills / 2,706 lines → 5 / 422**, each 74–90 against the 140 ceiling, no `references/`
  needed at all. **Ticket 24's seam held**: eight of the sixteen atoms are read, **no atom
  outside the list was wanted**, no template id appears in any skill body, and every `null` is
  taken as a branch stated at the step rather than as a missing key to ask about — the defect
  ticket 18 found in `foundation` cannot recur. Nine recipe sections cited by heading. The dying
  sweep leaves nothing stranded: `generate` verified absorbed at `template-postxl:613`, and
  `docs` + `doc_tracking.md` confirmed to be **this repo's own Starlight tooling** misfiled
  under `impl-build`. **`infrastructure` had exactly one stack-neutral idea worth keeping** —
  the *provider seam* (interface + real + in-memory, so a slice builds before credentials
  exist), now `architecture-system` step 5; its five-layer bottom-up order is deliberately not
  carried, because `build-plan` already rules layer-first decomposition out. Two defects fixed
  rather than ported, both the same class: `build-scaffold`'s brand gate is **conditional**
  (`appbuilder-mvp` has no `design-brand` node, so the inherited hard gate would refuse on every
  run there) and it cuts `build/<app-slug>` **only when `build-branch` did not** (mvp has no
  branch node). Three deviations from ticket 18's shape: the tie-break is written in flow names
  now that `tier` is dead; **`project_type` comes from `01_meta/scope.yaml`, not
  `onboarding.yaml`** — ticket 10's note predates the landed `concept-scope`, which writes it
  there; and **`10_blueprint/glossary.md` is reconciled, not authored**, because
  `contracts/domain_model.md` forbids a dedicated write-the-glossary pass — one entry per model
  name and enum vocabulary, updated in place, renaming the model to match an existing term. It
  still becomes the writer ADR 0007 left that file without. Nothing for the forge-concept
  register: no constraint here traced to how the host reads anything.

- [28: Write the four flow YAMLs](issues/28-write-the-flows.md):
  Four files, node and edge counts exactly ticket 10's — `appbuilder-mvp` 9 · `-standard` 27 ·
  `skaileup-concept-only` 14 · `-concept-reverse` 9, three group nodes each, `type: flow` edges
  only, no `sub-flow` and no `router`. **The cover is exact both ways**: the flows name 29
  distinct skills, the repo holds 29, no orphan and no phantom — the first end-to-end proof the
  domain set closes. `requires:` `contract:` sets are the **computed union of what each flow's
  node skills actually cite**, grepped rather than asserted (mvp drops five, `concept-only`
  drops two — it has no data layer). **One shape decision ticket 10 left implicit turned out
  load-bearing: skill nodes carry no `position`.** `flow-layout.ts:53-65` pulls positioned nodes
  out of the lane computation and returns early with `lanes: []` when none remain, so an
  all-positioned flow makes the group-phase override at `:87-93` — ticket 10's whole reason for
  keeping group nodes — **unreachable**. Authoring geometry would have deleted the mechanism the
  rule exists to protect. Flagged not deviated: the two concept flows carry an **empty
  `implementation` group** because the rule says three per flow; it is inert (`phasesPresent`
  filters on nodes) and one line to drop. `quality-standards` is phased `conceptualization` in
  `concept-reverse` — ticket 10 never assigned it, and `phaseForSkill` would have guessed
  `review` off the substring `quality`, which is exactly why every node declares `phase`.
  **The bigger finding is what `check.py` does not check.** Every flow shape rule ticket 10
  fixed was verified *by hand* here, because the script enforces almost none of them: no
  deleted-key check at all (`meta.category`, the four dead `globals`, `${...}`,
  `data.parameters` — which still has a live host read — and `data.writes` all pass); working
  `sub-flow` and `router` branches, so "skill+group only" is unenforced; three-groups-per-flow
  unenforced; **and the group-phase-vs-node-phase agreement, the "one table so they cannot
  disagree" property, is precisely what is not checked** — both validate against the enum
  independently and the group silently wins. `contract:` refs are checked for existence, not
  exactness. Graduated **32** to close these. Harness edits made and left uncommitted in
  `forge-concept` (the test's `REPO`/`FLOWS`/`SKILLS` and `templates/dev/skaile.yaml`);
  **ticket 29 must push `-mp` `main` first** — the suite installs over SSH from GitHub and
  **self-skips when the repo is unreachable, so a missing push reads as a skip, not a failure.**

- [30: The post-port contract sweep — what four ports found and none owned](issues/30-post-port-contract-sweep.md):
  All nine items fixed, and **the re-run found eleven more — 32 files edited in total**, which is
  the ticket's real result: the nine were only what four sessions happened to trip over.
  `artifact_frontmatter.md`, `feedback_loop.md` and `seed_data.md` rewritten onto ADR 0007, and
  each carried more than paths — dead writers (`impl-slice-commit`, `ops-reverse-engineer`,
  `ops-trace`), a `stories.yaml` shown as JSON, an `## Event Emission` section whose only content
  pointed at a nonexistent file. `tech_stack_skill` documented with its readers and the rule that
  its legal values are `templates/` directory names. **`feature-map.json` wins** the separator
  disagreement on the tiebreaker the ticket named: the landed `architecture-datamodel` writes it
  hyphenated at three sites and `ops-review` reads that. **The pattern the re-run exposes is
  sharper than any single fix: ticket 16's sweep updated the skills and left the contracts those
  skills read.** `walkthrough_renderer.md` was **wholly pre-0007 at 26 sites**, the largest find;
  `elements_block.md` at 9 (plus a hard `MUST` in vocabulary ADR 0003 retired);
  `agent_patterns.md` at 5; both walkthrough fixture trees entirely pre-0007 *while their
  SKILL.md calls the snapshot "what correct output looks like"*; `mockup-annotate`'s two
  manifests at 32 sites each, missed by `e63316c` which updated the HTML sitting beside them.
  **One live bug, not a stale path**: both `mockup-walkthrough` validators default
  `project_root` to `source_root.parent.parent`, correct only for the two-segment
  `experience/screens` — under 0007's one-segment `07_screens` they resolved a level too high, so
  **every `data-spec-screen source missing` check was inert against a real tree**. Reverting the
  fix reproduces three failures. Item 6 was half phantom: the `evaluator.md` row a port session
  had already fixed. Register correction: ticket 26 recorded that nothing breaks from the host's
  hardcoded `input.json` path because **no skill body names it** — two sites did, and
  `agent_patterns.md` spelled it with the wrong directory *and* the wrong filename, so it
  disagreed with the host as well as with 0007. The premise is only now true. Graduated **33**
  (`docs/examples/` carries 14 pre-0007 paths and one example is superseded outright).

- [33: `docs/examples/` is frozen against a tree that no longer exists](issues/33-docs-examples-disposition.md):
  Both worked ports **deleted**, `WHY.md` kept with a dated header, `README.md` gone —
  `docs/examples/` is one file. The astro example was superseded *measurably*: its
  `references/scaffold/` is **byte-identical** to the landed skill's (`diff -r` empty) and its
  `specs-json.md` differs in **exactly ten lines, all of them pre-0007 paths**, so freezing it
  would have preserved nothing else. The `concept-brief` port failed the ticket's own
  before/after test on a fact the ticket did not have: **there is no "before" in this repo** —
  the 289-line source lives in the old collection, so `docs/examples/` held two *after* halves.
  And its drift ran past paths: it hands off to `research`, `design-brand-visual` and
  `product-spec-features`, **three skill names none of which exist**, and writes a `complexity`
  scale ticket 10 retired. A dated header would have left a reader free to copy a dead skill
  name out of a file kept as a model of good practice. **The reason it drifted unnoticed is
  structural and worth carrying: `check.py` globs `skills/` and `contracts/` and never looks at
  `docs/`, so skill prose living under `docs/` has no CI behind it.** `WHY.md` survives because
  it is the one artifact the landed collection cannot reproduce — the measurements, the
  44%-removable table, the per-section counts across 88 skills, and the constraint-transformation
  table showing eight `MUST`/`NEVER` lines becoming positive statements at the step they bind. A
  landed skill demonstrates the *after*; only this demonstrates the *move*. Swept in passing: the
  two `RENDERER.md` opening sentences ticket 30 missed, still on `_concept/mockup-walkthrough/`
  while their own `SKILL.md` was already right — the first sentence a renderer-branch agent reads.

- [32: `check.py` passes flows that break every rule ticket 10 fixed](issues/32-check-py-enforces-the-flow-shape.md):
  All seven gaps closed plus two rules the list did not have. `check.py` **471 → 728**,
  `test_check.py` **31 → 59** cases, one negative fixture per rule — and **every new rule passed
  all four landed flows on the first run**, so the gate was fitted to the shape the collection
  actually ships rather than the flows fitted to the gate. Each rule was also smoke-tested by
  mutating a real flow one way at a time, so none is a no-op. **Gap 4 was the one that mattered
  and it needed a rule nobody had stated**: a skill node's `data.phase` must agree with its
  group's, and making that airtight requires *a skill node to declare `parentNode` at all* —
  without a parent there is no group phase to disagree with, so the check would have had a hole
  the size of "author forgot the container". `${...}` is caught on the file's **raw text**, not
  the parsed tree, because an interpolation can sit in any string. Two rules added from findings
  rather than from the list: **a skill node may not carry `position`** (ticket 28's discovery —
  authoring geometry drops the node from the lane computation and silently deletes the very
  override gap 4 protects), and `placeholder` may not sit beside a non-`freeform` `input_style`.
  **The `_concept/` prerequisite ban narrows to an allowlist rather than being kept or dropped.**
  Kept, it is stricter than the reader it protects — `validator.ts:81` resolves a `package.json`
  gate correctly, and a check whose stated bar is "the failure mode is quiet" was blocking a
  declaration with no failure mode behind it; ticket 23 paid for that. Dropped, the obvious
  relaxation reopens the class this repo actually bleeds: `experience/screens/foo.md` is a
  **pre-0007 concept path**, not a project-root file, and a blanket rule passes it as one —
  ticket 30 swept 32 files of that shape. So the unknown stays banned, the known becomes
  declarable, and extending the list is a deliberate edit. Nothing landed changes; it removes a
  trap rather than unblocking anything. **ADR 0011 carries a dated amendment and
  `docs/skill-template.md` is updated**, so the rule is not documented one way and enforced
  another. Register: banning `data.writes` leaves `resolveNodeFolders` with nothing —
  `flow-manager.ts:361` falls through at `:368` to `getArtifactsProducibleBySkill` → the artifact
  contract → **`artifacts.yaml`, unreachable as deployed**. Ticket 10's deletion and ticket 01's
  finding compose into a dead node-folder surface for the whole collection.

- [29: The acceptance run — install `-mp` and get the flows loading green](issues/29-acceptance-run.md):
  **The destination is reached: `forge-concept` installs `-mp` from GitHub and loads all four
  flows, every node skill deployed** — the integration suite is 4/4 with no skip, `check.py`
  29 skills · 4 flows · 0 errors, `test_check.py` 61/61. Opt-in is one `sources:` URL plus one
  explicit dependency line per asset (`skill:*` throws inside `skaile.yaml` — CLI-only sugar).
  **Two of four flows resolved on the first run**, and the cause is a rule nothing had written
  down: **a flow's asset identity is its `name:`, slugified — never its `id:`**
  (`core/manifest.ts` `fromFlowYamlContent` → `scanDirectory`'s `slugifyAssetName`).
  `Appbuilder MVP` resolved by accident of title case; `Concept Only` and `Reverse Engineer a
  Codebase` resolved as `concept-only` / `reverse-engineer-a-codebase` and silently never
  installed. The old collection satisfied the rule by a convention it never stated (every flow
  titled the Title Case of its id). Both flows retitled and **`check.py` now mirrors
  `slugifyAssetName`** so it cannot regress (`-mp` `dc8dfea`). Second finding, bigger:
  **a flow's `requires:` provisions nothing** in the version the host runs — `bundleDeps`
  returns `undefined` for `kind !== "bundle"` in `@skaile/workspaces` 0.48.1, so installing a
  flow deploys the `.flow.yaml` alone with `missing: []`. Measured on both collections, so it
  is a version fact, not an `-mp` defect (the monorepo's `main` has widened it, unreleased).
  The map's premise 3 and ticket 01's "`requires:` drives transitive install" are therefore
  **wrong as deployed**; the test workspace and `templates/dev/skaile.yaml` now list all 29
  skills explicitly, and the suite asserts the cover the host cannot report. Register: an
  already-cloned source is **not refetched on install**, so a fresh workspace resolved against
  a stale checkout even after the fix was pushed.

- [31: `review.yaml` and `reviews/` are one letter apart](issues/31-review-yaml-collision.md):
  the collision is resolved by **deleting one side**, not renaming either. `11_build/review.yaml`
  — the whole-project verdict — had **zero readers** anywhere (not the host, not a skill, not a
  flow's `requires:`), while `reviews/<feature_slug>.yaml` has two and is the tree-idiomatic
  shape (every per-thing collection here is a plural directory). The sharper reason is a
  distinction the tree now carries: a code review is **decided** and cannot be re-derived, so it
  earns a file; a tree audit is **recomputed** every run, so a copy on disk can only be stale.
  `ops-review` writes `trace.yaml` alone and delivers the verdict as the report. Nothing durable
  replaces it — an echo into `decisions.md` was refused as the same category error elsewhere.
  Generalised and gated: `concept_structure.md`'s Naming section now bans siblings differing
  only by plural, and `check.py:check_tree_names` enforces it over the contract's own fenced
  tree (verified firing and silent). **`-mp` did not bend to the host**: the host reads
  `review/` singular *and* `acceptance_criteria` with an underscore, and the tree is uniformly
  hyphenated — so the register entry grows from one path edit to three rather than importing
  two names this ticket exists to call wrong.

## Not yet specified

- **The five absorbed skills' actual bodies** — what a skaileup-flavoured `to-spec` /
  `to-tickets` / router / `grilling` / `research` says once it knows about `_concept/`.
  Blocked on knowing which skills they replace. Ticket 04 fixed their *names*
  (`spec-*` / `build-*` / `skaileup` / `concept-*`), not their contents. **Ticket 08 placed
  three of them**: `research` and `to-questionnaire` are steps inside `concept-research` and
  `concept-onboard`, and `to-spec` is `spec-feature` (ticket 07) — so what is left here is the
  router and `grilling`. **Ticket 13 added a requirement to the router**: it must carry the
  intake rule for work the collection did not create — call the global `/triage`, then enter at
  `spec-feature` (a new or changed feature) or `build-plan` (a defect against built code).
  Ticket 13 refused a triage *skill*; the sentence still has to live somewhere, and `CONTEXT.md`
  is glossary-only so it cannot be there. ~~Ticket 09 handed `contracts/grill_bank.md` here — it
  survives only if the absorbed `grilling` skill claims it.~~ **Closed by ticket 26: dead.** Its
  nine pillars are already inlined at `spec-feature:42-54` where they bind, and the "absorbed
  `grilling` skill" it was waiting on turned out to be a **global install, not a `-mp` asset** —
  which is also the answer to half of what is left in this patch.
- **The docs site.** `docs/` is a Starlight site that renders every SKILL.md. Port, regenerate,
  or drop. **Narrowed by ticket 18 to `docs/scripts/generate-skill-pages.mjs` alone** — two
  Starlight sites were inside this patch, and the other one (`impl-build-docs`, which maintains a
  *target project's* docs) turned out to be this repo's own tooling misfiled under `impl-build`
  and does not port. What breaks the collection's site is **not** frontmatter pruning (it reads
  `name`, `description`, `metadata.stage|version|tags`, all surviving) but that it renders a page
  per `DOMAIN.md` — **ticket 05 deletes all 16** — and hard-links `contracts/asset_frontmatter.md`,
  which ticket 09 deleted. **Ticket 33 added a reason to decide rather than defer this:
  `check.py` globs `skills/` and `contracts/` and never looks at `docs/`, so anything
  skill-shaped living there has no CI behind it — which is how two worked examples drifted onto
  a dead tree and three dead skill names unnoticed.
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
  `stage: alpha`, `do_not_invoke: true`) and the **four** skills that read it:
  `ops-project-overview` · `ops-project-subsystem-map` · `ops-project-integration` ·
  `ops-project-review`. (Corrected 2026-09-05 by ticket 21, which rules four while this entry
  named two.) Ruled out by ticket 09 on the same argument as `15_demo`: a meta-concept spanning
  several products is a different product from the app-building collection. Stays in the old
  repo. **Cutting them dangles a flow:** those four are the only `ops-*` nodes in
  `appbuilder-complex.flow.yaml` (`:304-344`, edges `:506-523`), so that flow's tail needs
  repair — **ticket 10's**, noted there.
- **A general triage on-ramp for work the collection did not create** — ruled by
  [13: A triage on-ramp and a durable record of rejected scope](issues/13-triage-onramp-and-scope-memory.md),
  which the ticket itself asked to be closed either way rather than left as fog. The inbox is
  upstream: skaileup's own repos hold 1 closed issue and 0, while the real queue sits on
  `platform` + `workspaces` and is already triaged with mp's globally-installed `/triage`. `-mp`
  keeps the *rule* (global `/triage`, then `spec-feature` or `build-plan`) as a router
  requirement, not a skill. Returns only if a skaileup-built app grows an inbox of its own.

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
    `addEventListener("message")` repo-wide, so the iframe writer ticket 20 weighed is a new host
    feature (listener + accumulator + session boundary + write path), not a wiring change.
    **Ticket 20 ruled the browser path supported instead**, so this constrains nothing today; it
    returns if a host ever wants the walkthrough embedded. The overlay's postMessage branch is
    kept correct and unused against that day, and **the host must invent the session boundary**:
    the overlay posts one message per annotation and never signals the end of a round.
  - **The review surface reads pre-0007 paths** — `server/utils/review-coverage.ts:98` locates
    feature docs under `experience/features/<NN_group>/`, both the old root *and* the
    `<NN_group>` shape ticket 08 removed; `app/pages/review.vue:22` names
    `_implementation/trace.yaml`, a root 0007 absorbed into `11_build/`. **A project on the
    `-mp` tree loses the review surface until the host is updated.** **Downgraded by ticket 21**
    from the sharpest entry here to a mechanical one: with `11_build/` chosen over a new root
    (17's placement, adopted), the fix is **`_implementation/` → `_concept/11_build/`** across
    `review-coverage.ts:109,122,130` and `review.vue:21-22`, plus `findConceptPath`'s
    `experience/features/<NN_group>/` → `05_features/<featureset>/`. `buildCoverageReport` unions
    three files by feature id — `trace.yaml` (ticket 21), `acceptance-criteria/` and
    `reviews/<slug>.yaml` (ticket 17) — and all three now sit under that one prefix.
    **Widened by ticket 31 from one edit to three, all in the same two files:** the host reads
    `_implementation/review/` (**singular**, `review-coverage.ts:131`) and
    `_implementation/acceptance_criteria` (**underscore**, `:122`), while `-mp`'s tree is
    uniformly hyphenated and plural-for-collections. Ticket 31 kept `-mp` internally consistent
    and let the host move, so the successor change is the prefix swap **plus** `review/` →
    `reviews/` and `acceptance_criteria` → `acceptance-criteria`. Also: `review.yaml` no longer
    exists to port — nothing in the host ever read it.
  - **The host already has a `_concept/` intake channel the collection ignores** — a
    per-document comment API (`server/api/comments/[...document].{get,post}.ts` over
    `server/utils/concept-comment-store.ts`, 137 lines) giving any authenticated viewer
    threaded comments anchored to a `documentId` on a `_concept/` file. **No skill reads it.**
    The inverse shape of every other entry here — not a constraint that forced a workaround,
    but a capability nothing takes — and the fact ticket 13's refusal turned on, since it was
    the one channel where a skaileup-specific triage could have beaten mp's.

  - **`parseSkillRequirements` reads `metadata` with no root-level fallback**
    (`resolver/src/parser.ts:45-46`; `discovery/src/requires-graph.ts:236-238` is the same
    shape). `version` is already normalised both ways one file over
    (`discovery/src/discover.ts:705-719`), so the asymmetry is an oversight, not a design.
    **The cheapest entry in this register**: one line makes root-level frontmatter work for
    every skill forever and retires the `metadata:` nesting ADR 0011 imposed. Ticket 27 nested
    instead, because a `@skaile/workspaces` release plus a forge-concept bump mid-migration is
    exactly what this map defers.
  - **The input dialog's path is hardcoded to a directory ADR 0007 abolished** —
    `resolver/src/validator.ts:107` reads `_concept/_grounding/<skillId>/input.json`, where the
    tree now says `02_grounding/`. Both ends are the host's, so no skill declares it and nothing
    breaks today; the first `-mp` skill with `inputs_optional` inherits the clash. Found by
    ticket 27, which could not verify that declaration for want of a skill that makes one.

  - **The host validates no flow and cannot report a missing skill.** `validateFlow` /
    `FlowManifestSchema` have **zero call sites** in forge-concept — its only gate is
    `loadFlowsFromDir`'s truthy `id`/`nodes`/`edges`, so a flow file faces no schema
    enforcement from the acceptance target at all. Worse, a `data.skill` that resolves to
    nothing does not raise: `run.post.ts:78-80` falls back to a generic
    `Run skill ${skillId}` prompt and the node runs with no body, while
    `requirements.get.ts:37-48` returns a **fabricated `satisfied: true`** with zero unmet
    requirements. Ticket 16 responded by making the collection self-validating, which is the
    right answer for this map but leaves the host silently green on a broken install.

  - **`phaseForSkill` hardcodes `ops-eval*`, `ops-review`, `ops-sync`**
    (`shared/flow-phases.ts:23-24`). Inert while `-mp` declares `data.phase` per node, since
    `phaseForNode` prefers the explicit value — but it is a name-level coupling that binds again
    if the phase-per-node rule is ever dropped. **Narrowed by ticket 21:** of the four names,
    only `ops-review` still exists, and its lane (`review`) is still right.

  - **Authored node geometry disables the swimlanes.** `app/utils/flow-layout.ts:53-65` — a
    flow whose nodes all carry `position` returns `lanes: []`, so the group-phase override at
    `:87-93` never runs. The collection has to *withhold* geometry to get the feature, which is
    the opposite of what authoring a layout implies. Found by ticket 28, which withheld it.
  - **Group rects always render at the origin.** `app/components/FlowGraph.vue:214-232` looks
    group positions up in `layout.positions`, which is filled only for `renderable` nodes — and
    a group is never renderable. With the entry above, the group `style:` geometry ticket 28
    writes has **no live reader on either path**.
  - **Repo-onboarding extras are gated on a hardcoded profile id.**
    `OnboardingWizard.vue:525` tests `selectedProfile === "reverse_engineer"`, but the profile
    key *is* the flow id (`profiles.get.ts`), so for `skaileup-concept-reverse` the `branch` and
    `context` fields are collected from the user and then dropped. Found by ticket 28.
  - **`meta:` vs `metadata:` on a flow.** forge-concept reads `flow.meta.{icon,onboarding}`;
    platform's `validateFlow` declares them under `metadata`. `-mp` writes `meta:` because the
    acceptance target is forge-concept; platform validates looseObject and reads no icon, so
    nothing breaks — but the two hosts disagree about where a flow's presentation lives, and
    ticket 15's question about the two flow implementations is where that belongs.

  - **A flow's asset identity is its `name:`, slugified — `id:` is never consulted.**
    `core/manifest.ts` `fromFlowYamlContent` takes `meta.name ?? meta.id ?? stem`, and
    `scanDirectory`'s `add()` slugifies it. So the human title of a flow is load-bearing
    machine data, while `id:` — the thing the loader, the profiles endpoint and every
    document call the flow — is not. `-mp` conforms (ticket 29 retitled two flows and gated
    the rule in `check.py`); the question of whether the installer should key on `id:` is the
    successor effort's.
  - **A flow's `requires:` provisions nothing.** `bundleDeps` in `@skaile/workspaces` 0.48.1
    opens `if (kind !== "bundle") return undefined`, so a flow candidate carries no deps and
    installing one deploys the `.flow.yaml` alone — silently, with `missing: []`. The
    monorepo's `main` has already widened this to flows (`manifestDeps`); until that version
    reaches forge-concept, every workspace duplicates the flow's skill list by hand. Found by
    ticket 29 on both collections.
  - **An already-cloned source is not refetched on install.** `~/.skaile/cache/sources/<host>/
    <org>/<repo>` is cloned once; a later `install()` in a *fresh* workspace reuses whatever
    commit is there, so a just-pushed fix reads as still-broken until the cache is fetched by
    hand. Ticket 29 hit it between pushing `dc8dfea` and re-running the suite.

  - **Banning `data.writes` leaves node folders with no source.** `flow-manager.ts:361` reads
    `data.writes`, else falls through at `:368` to `getArtifactsProducibleBySkill`, which resolves
    through the artifact contract to **`artifacts.yaml` — unreachable as deployed** (ticket 01).
    Ticket 10 deleted `data.writes` as decoration with zero readers, which was true of the *flow*
    side; composed with ticket 01's finding it makes `resolveNodeFolders` dead for the whole
    collection. Inert for ticket 29. Found by ticket 32 while writing the ban.
