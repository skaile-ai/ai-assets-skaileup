# Recon: ticket 10 — flows and tiers

Evidence only; nothing decided. Paths relative to `ai-assets-skaileup` unless prefixed
`forge-concept/` (`/Users/matthias/devBench/SKAILEdev/forge/forge-concept`).

## Facts

### F1 — There are 17 flow YAMLs, not 21

**17**, corroborated by `skaile.yaml:291` (`# ── flows (17) ──`), `verify_flows.py:53-77` (`TIER_FLOWS` 4 + `SLICE_FLOWS` **3** + `VARIANT_FLOWS` 5 + `SHARED_FLOWS` 5), and map.md's ticket-15 line. Ticket 11 says 19; two flows were deleted in `6d753c3` / `738b49e` (`skaileup-impl`, `skaileup-impl-standalone`), so 19 and 21 are pre-deletion counts.
The keep-set "4 tiers + 2 slice loops + 5 shared (11)" also undercounts: slice flows are **3** (`skaileup-slice` wraps the other two) → 12, and the 5 **variant** flows (`cli`, `concept-only`, `concept-reverse`, `implementation`, `stepwise`) are unaccounted for.

### F2 — Inventory (all 17)

| flow | v | nodes | edges | node kinds | edge types | `data.phase` present on | `requires:` |
|---|---|---|---|---|---|---|---|
| `appbuilder-mvp` | 2.0.0 | 14 | 10 | group 3, skill 11 | flow 9, optional 1 | groups only | 12 |
| `appbuilder-simple` | 2.0.0 | 16 | 13 | group 3, skill 10, sub-flow 3 | flow 11, parallel 2 | groups + sub-flows | 14 |
| `appbuilder-standard` | 2.0.0 | 25 | 20 | group 6, skill 11, sub-flow 6, router 2 | flow 10, optional 8, parallel 2 | groups + sub-flows | 18 |
| `appbuilder-complex` | 2.0.0 | 30 | 29 | group 3, skill 19, sub-flow 6, router 2 | flow 18, optional 9, parallel 2 | groups + sub-flows | 27 |
| `appbuilder-cli` | 2.0.0 | 11 | 7 | group 3, skill 5, sub-flow 3 | flow 7 | groups + sub-flows | 9 |
| `skaileup-concept-only` | 2.0.0 | 19 | 17 | group 2, skill 15, sub-flow 2 | flow 8, optional 9 | groups + sub-flows | 20 |
| `skaileup-concept-reverse` | 2.0.0 | 10 | 8 | group 1, skill 9 | optional 8 | group only | 13 |
| `skaileup-implementation` | 2.0.0 | 7 | 3 | group 3, sub-flow 4 | flow 3 | groups + sub-flows | 5 |
| `skaileup-stepwise` | 2.0.0 | 9 | 10 | skill 8, sub-flow 1 | flow 6, optional 3, **review-loop 1** | **8 skill nodes** | 12 |
| `skaileup-slice` | 2.0.0 | 2 | 1 | sub-flow 2 | flow 1 | **none** | 3 |
| `skaileup-slice-concept` | 2.0.0 | 4 | 3 | skill 4 | flow 3 | none | 5 |
| `skaileup-slice-impl` | 2.0.0 | 13 | 12 | skill 13 | flow 10, optional 2 | none | 14 |
| `concept-discovery` | 2.0.0 | 3 | 2 | skill 3 | optional 2 | none | 4 |
| `architecture` | 2.0.0 | 4 | 3 | skill 4 | optional 2, flow 1 | none | 5 |
| `impl-build-setup` | 2.0.0 | 6 | 5 | skill 6 | flow 4, optional 1 | none | 8 |
| `mockup-feedback` | 2.0.0 | 4 | 3 | skill 4 | optional 3 | none | 5 |
| `quality-gate` | 2.0.0 | 8 | 7 | skill 8 | flow 3, optional 4 | none | 9 |

175 nodes (24 group / 130 skill / 27 sub-flow / 4 router), 153 edges. All 17 share the same
top-level keys: `id · version · name · description · meta · requires · globals · entry ·
nodes · edges`. **No flow declares `modes:`, `tier_presets:`, `artifact_handoff:` or
`next_flows:`** — those live only in `contracts/flows.md:160,172,193` +
`asset_frontmatter.md:329`, both deleted by 09. `requires:` = 130 `skill:` + 27 `flow:` + 26
`contract:`, checked only by `verify_flows.py:24-27` set-equality against the node graph.

### F3 — `data.phase` is on containers, not on work

122/130 skill nodes and 4/4 routers carry **no** `data.phase`; 24/24 groups and 25/27
sub-flows do. The 8 exceptions are all `skaileup-stepwise` (the one tier-shaped flow with no
group nodes); the 2 phase-less sub-flows are `skaileup-slice`'s children. Ticket 04's
"declare `phase` on every node" is new practice, not a port — `phaseForNode`
(`forge-concept/shared/flow-phases.ts:35-41`) name-prefix-falls-back for 122 of 130 today.

### F4 — The 6 flows `forge-concept` names

`forge-concept/tests/integration/skaileup-flows.test.ts:29-36` **and**
`forge-concept/templates/dev/skaile.yaml:10-15` list the same six verbatim:
`appbuilder-{mvp,simple,standard,complex}` · `skaileup-slice-{concept,impl}`.
`skaileup-slice`/`-impl` also appear as **unit-test fixtures only**
(`test/unit/flow-extended.test.ts:14-15,39-40`, `flow-extended-state.test.ts:13,55`).
The integration test also names two *skills* — `concept-brief`, `concept-goals`
(`:38`); `concept-goals` dies in 08, so the acceptance test breaks on a skill name before a
flow name.

### F5 — Live vs inert reads on the flow/tier surface

| key | site | live? |
|---|---|---|
| `globals.research_depth` | `forge-concept/server/api/pipeline/profiles.get.ts:33` → `OnboardingWizard.vue:473,535` | **LIVE** |
| `meta.onboarding.{input_style,placeholder,fields}` | `profiles.get.ts:34-38` | **LIVE** — declared by 3 flows only (`concept-only`, `concept-reverse`, `stepwise`); other 14 default to `structured` |
| `meta.icon`, `name`, `description` | `profiles.get.ts:30-32` | **LIVE** (flow id becomes the profile key) |
| `meta.category` | `forge-concept/server/utils/flow-manager.ts:146-150` | read, **every branch dead** — the 6 category values in use are `cli · full-stack · prototype · concept · incremental · maintenance`; the code branches only on `implementation` / `evaluation` / `quality`, so all 17 fall through to `skaileup-conceptualization` |
| `globals.approval_mode` · `subagent_mode` · `verbosity` | — | **0 readers** anywhere (forge-concept, platform, collection) |
| `globals.concept_depth` + `parameters.concept_depth` | 3 flows declare, `${concept_depth}` threaded in 5 node params | **0 readers** — no SKILL.md, no `.py`, no forge-concept code reads it; grep for `concept_depth` in skill bodies returns nothing |
| `${...}` interpolation generally (`mode: '${templates}'`, `'${goals}'`, `'${e2e}'`, `'${ops_tail}'`, `'${infrastructure}'`, `'${data_setup}'`) | 9 node params | **no resolver exists** in forge-concept or the collection |
| router `condition` strings | 4 routers, 9 routes | never evaluated (ticket 01) |
| `tier_presets` / `modes` | `contracts/flows.md`, `asset_frontmatter.md` only | **0 flows declare either** |
| `scope.yaml` `tier` | 11 SKILL.md read it; 2 `validator.py` whitelist it | **LIVE in the collection, 0 reads in forge-concept** |

`forge-concept` has **zero** reads of `tier` as a project concept; its only `tier` hits are
the store-catalog asset tier (`store-catalog/assets.get.ts:7`,
`forge-common/src/runtime/types/catalog.ts:40,65,93,99`) — unrelated community/verified axis.

### F6 — `tier` writers and readers in the collection

Writer: `00_skaileup-orchestrator/scope/scope-project/SKILL.md:198-214` →
`_concept/_meta/scope.yaml` (`shape · tier · flow_to_run · reasoning · signals · override ·
chosen_at · chosen_by`); two-stage rule `:142-148` (shape short-circuit) + `:154-160` (sizing).
11 SKILL.md read `scope.yaml`: `scope-project` · `skaileup` · `skaileup-build` · the four
`08_concept-slice/*` · `09_impl-architecture/02_templates-select` · the three `11_impl-plan/*`.
Hard gates that **refuse to run** on tier: `11_impl-plan/02_align/SKILL.md:147,149,175-187`,
`03_plan-vertical/SKILL.md:184,210`, whitelisted in `02_align/validator.py:48` /
`03_plan-vertical/validator.py:52`. `templates-select/SKILL.md:118` = soft weighting
(default `appbuilder-standard`).

### F7 — The `spec-feature`-loop gap (08's first handoff)

`08-concept-side-consolidation.md:92-93` names `skaileup-concept-only` +
`skaileup-concept-reverse`. Verified: neither has a `skaileup-slice*` sub-flow node or any
`concept-slice-*` skill node. `concept-only`'s per-feature surface is `features` → `screens` →
optional `screens-technical`/`components` (all four die or narrow in 08); `concept-reverse` is
9 optional nodes with no loop. **A third flow is in the same position: `appbuilder-simple`** —
`features` → `screens`, delegating only `skaileup-slice-impl` (impl half), never the concept
half. `appbuilder-mvp` has neither `screens` nor any slice flow.

### F8 — The behaviors/features order (08's second handoff)

The gate: `03_experience/02_behaviors/SKILL.md:3` (*"Use when features are approved…"*),
`:65`, and `:81` (*"No approved features found. Run the `features` skill first."*).
Three flows carry `experience-behaviors`, and **they do not agree**:

| flow | edge | order |
|---|---|---|
| `appbuilder-complex` | `e-journeys-behaviors`, `e-behaviors-features` | behaviors **before** features |
| `appbuilder-standard` | `e-journeys-behaviors-opt` (`type: optional`), `e-behaviors-opt-features` | behaviors **before** features |
| `skaileup-concept-only` | `e-features-behaviors` (`type: optional`) | behaviors **after** features ✓ |

Ticket 08 named only `appbuilder-complex`; `appbuilder-standard` has the same inversion.
Both inverted edges *into* `features` are `type: flow` (they order the engine, per 15); the
`optional` edges into `behaviors-opt` / `behaviors` order nothing.

### F9 — The `cli` demotion surface

Readers of `cli` / `appbuilder-cli` that would break:

| site | what it does |
|---|---|
| `scope-project/validator.py:24,29,31` | `ALLOWED_VARIANTS`, `ALLOWED_SHAPES` incl. `cli`, `SHAPE_TO_ROUTE["cli"]="appbuilder-cli"` |
| `scope-project/tests/test_validator.py:29,70,78,84-86,159-163` | 6 assertions on the cli route |
| `11_impl-plan/{02_align/validator.py:46-48, 03_plan-vertical/validator.py:50-52}` | `appbuilder-cli` in `ALLOWED_TIERS` |
| `flows/_meta/verify_flows.py:59` | `VARIANT_FLOWS` membership |
| `scope-project/SKILL.md:31,33,37,107-108,126,146,178`; `examples/appbuilder-cli.scope.yaml:2-9` | interview options, Stage-0 rule, worked example |

Nothing in `forge-concept` reads it. The landing site exists — `contracts/profiles/cli-tool.yaml`, with its own `features: commands/` mapping — but **`contracts/profiles/*.yaml` has zero in-body readers**: `contracts/DOMAIN.md:36` claims "Read by `impl-architecture-techstack`", and that skill actually reads `09_impl-architecture/templates/*/TEMPLATE.md` (`01_techstack/SKILL.md:138,318`). Meanwhile a live `project_type` axis with a `cli-tool` value already exists: `contracts/schemas/onboarding-profile-v1.yaml:18` → `01_concept/04_grounding/01_onboard/SKILL.md:30,264` → `03_seeds/SKILL.md:101,115,222,262`. `appbuilder-cli`'s own node params (`project_type: cli`, `skip_ui_shell: true`) are inert (F5).

### F10 — Node → post-consolidation mapping

69 distinct skills across 130 node instances. 88 SKILL.md exist; **19 are on zero flows**; **0 flow refs dangle**. (`skaile.yaml` declares 86 — missing `impl-quality-review-feature`, `impl-slice-git-finish`, `ops-trace`, declaring nonexistent `impl-slice-finish`; block dead per 01.)

| old node skill | fate | source |
|---|---|---|
| `concept-brief`; `-goals`, `-comparable` absorbed | `concept-brief` | 08:78 |
| `concept-grounding-onboard`; `-seeds` absorbed | `concept-onboard` | 08:78 |
| `concept-grounding-research`; `design-inspiration` absorbed | `concept-research` | 08:78 |
| `design-brand-visual` | `design-brand` | 08 |
| `design-brand-voice` | **DEAD** | 08:78 |
| `experience-journeys` · `experience-behaviors` | unchanged names | 08 |
| `experience-screens` | `experience-shell` (narrowed to `shell.md` + shared patterns) | 08:63-65 |
| `experience-screens-technical` · `experience-components` | **DEAD** (capability → `spec-feature`) | 08:71,78,81 |
| `product-spec-features` | `spec-featuresets` | 08:66 |
| `concept-slice-design-feature`; `-brainstorm`/`-align`/`-scope-feature` are steps | `spec-feature` | 07:43-44 |
| `impl-plan-plan-vertical`; `-brainstorm`/`-align` are steps | `build-plan` | 07:45-46 |
| `impl-slice-implement`; `-test`/`-recap`/`-refactor`/`-commit` are steps | `build-implement` | 07:48-49 |
| `impl-slice-{git-prepare,git-finish}` | `build-branch` | 07:51 |
| `impl-plan-supervised` · `impl-slice-implement-page` | **DEAD** | 07:47,50 |
| `mockup-walkthrough-{astro,static-html}` | `mockup-walkthrough` (renderer = `references/`) | 06/14 |
| `mockup-component-storybook` | `mockup-storybook` | 06/14 |
| `mockup-feedback-annotate` \| `-{triage,patch,apply}` | `mockup-annotate` \| `mockup-feedback` | 06/14 |
| `mockup-walkthrough-{framework,text}` · `mockup-component-isolated-html` | **DEAD** | 06 |
| `ops-project-{overview,subsystem-map,integration,review}` | **OUT OF SCOPE** (stay in old repo) | map |

## Nodes with no mapping — live flow nodes with no `-mp` name yet

| node skill | node instances | flows | blocked on |
|---|---|---|---|
| `skaileup-scope-scope-project` | **7** (most-used skill in the collection) | mvp, simple, standard, complex, cli, concept-only, stepwise | **no ticket owns it.** Not in 08's 19-skill concept set, not in 07/17/18/21. It is the writer of the artifact this ticket is deciding the schema of. |
| `impl-architecture-{techstack,templates-select,system,datamodel}` | 10 | architecture, mvp, concept-reverse, stepwise | 18 |
| `impl-build-{scaffold,foundation,infrastructure,migrate,seed,docs}` | 10 | impl-build-setup, mvp, stepwise | 18 |
| `impl-quality-{test-unit,test-integration,test-e2e}` | 8 | quality-gate, cli, mvp, simple | 17 — 07 pinned them as flow nodes *after* the slice, so 10 cannot place them until 17 says 3 skills or 1 |
| `impl-quality-{ready,review-feature,audit,eval-code}` | 6 | quality-gate, slice-impl, complex | 17 |
| `impl-quality-{standards-discover,standards-inject}` | 2 | concept-reverse | 17 (`standards-inject` may be a contract) |
| `ops-{review,sync,trace}` · `ops-reverse-engineer` | 6 | quality-gate, concept-only, concept-reverse | 21 (08 pre-ruled `reverse-engineer` → `experience-shell` + `spec-feature` loop) |

**8 of 17 flows** cannot have their node set written today: `quality-gate`, `architecture`, `impl-build-setup`, `appbuilder-mvp`, `appbuilder-cli`, `skaileup-implementation`, `skaileup-stepwise`, `skaileup-concept-reverse` — four of them (`architecture`, `impl-build-setup`, `quality-gate`, `skaileup-implementation`) are **100%** unmapped nodes.

## Open questions for the human

1. **Can this ticket be resolved before 17/18/21?** Four flows are 100% unmapped nodes.
   Is 10 the full flow list, or the tier/slice half plus a deferred building-block half?
2. **Who owns `skaileup-scope-scope-project`?** 7× entry node, sole writer of `scope.yaml`,
   claimed by no ticket. Its two-stage rule (F6) *is* what tier-reduction rewrites. Does 10
   rewrite it, or does it need its own ticket?
3. **If `concept_depth` has no reader (F5), what does "fold `simple` into `concept_depth`" fold into?** It is a string threaded by `${}` with no resolver, into node `parameters` nothing reads, for skills that never mention the word. Is the target a *new* live read (skill body branching on tier from `01_meta/scope.yaml`, per 08's "no `parameters:` blocks"), or is `simple` simply deleted?
4. **What is `cli` demoting *to*?** `contracts/profiles/cli-tool.yaml` has zero readers,
   while a live `project_type: cli-tool` axis already exists (F9). Is the demotion "revive
   `profiles/`", or "`project_type` was always the axis and the tier was the duplicate"?
5. **Do the 5 variant flows survive at all?** They are 5 of 17, named by `forge-concept`
   nowhere (F4), and two of them need a `spec-feature` loop bolted on (F7). If tiers go to 3,
   is the variant set 0 — or is `stepwise`'s just-in-time shape what `concept_depth` was for?
6. **The behaviors inversion is in two flows, not one (F8).** Reorder both, or is
   `standard`'s `optional`-edge version already a no-op the engine ignores?
7. **`meta.onboarding` is live and only 3 flows declare it (F5).** Both non-default `input_style` values (`concept-reverse` = `repo`, `stepwise` = `freeform`) sit on variant flows. If variants go, the wizard is structured-only — acceptable, or does `input_style` move onto a tier?

## Post-resolution delta (2026-09-05)

Everything above predates the resolution. Where the halves disagree, this is later. Facts
measured while resolving, none of which the recon had.

### D1 — The flow list is an unfiltered user menu

`profiles.get.ts:10` turns **every** loaded flow into an onboarding profile keyed by flow id;
`OnboardingWizard.vue:41` renders `v-for="(prof, id) in profilesData.profiles"` with **no
filter**. F5 recorded `meta.icon`/`onboarding` as live but not the consequence: today's 17
flows are 17 project-start cards, including the six "shared building blocks" and the three
slice flows. This is what settled the sub-flow question.

### D2 — `standard` and `complex` are the same flow after the port

Identical six sub-flow refs. Skill sets differ by exactly eight names — `design-brand-voice`,
`impl-quality-audit`, `impl-quality-eval-code`, `mockup-walkthrough-framework`, and the four
`ops-project-*` — **all** deleted by 08/17/06 or out of scope. The recon's F2 table counted
nodes but never diffed the sets.

### D3 — Two mvp steps are unrunnable, not merely unneeded

- `mockup-walkthrough-text` gates on `_concept/experience/screens/` holding ≥1 screen with
  `00_layout/shell.md` **Required** (`SKILL.md:132,162-163`), stated failure at `:124`.
  `appbuilder-mvp` has **no skill that writes a screen**. Node `mock-text` has never run.
- `impl-build-foundation:95-98` lists `03_brand/tokens.json` under *"Hard gates (all must
  exist)"*; ticket 18 merges it into `build-scaffold`; mvp has no brand node.

F10 mapped `mockup-walkthrough-text` → DEAD without noticing its consumer flow had no producer.

### D4 — Routers are live and interactive

Correcting the recon's inherited "not actually routing anything". `condition` strings are
never evaluated, but `route-choice.post.ts` persists the user's pick, `computeUnchosenSkips`
(`flow-route-choice.ts`) prunes unchosen branches so the join unblocks, and
`useFlowState.ts:165` exposes it. Manual routing, not conditional.

### D5 — Group nodes are load-bearing, and group phase wins

`flow-layout.ts:87-93` draws swimlanes from group geometry;
`(n.parentNode && groupPhase.get(n.parentNode)) || phaseForNode(n)` means the **group's** phase
overrides the node's own; `FlowGraph.vue:218` positions lanes. F3 measured where `data.phase`
sits but not that deleting groups costs the lane rendering.

### D6 — `data.parameters` has exactly one live read host-wide

`parameters.flow`, the sub-flow child-id fallback (`flow-manager.ts:475`,
`shared/flow-extended.ts:52`). Nothing else. This is what decided the 17-vs-08 contradiction.

### D7 — The host honours exactly one edge type

`run.post.ts:62` and `flow-extended-state.ts:48` both filter `e.type === "flow"`. `optional`,
`parallel`, `review-loop` are inert — so `stepwise`'s self-edge with `max_iterations: 50` and
an `exit_condition` is decoration, and iteration has **never** been machine-expressed:
`appbuilder-standard:11-12` carries it as a comment.

### D8 — A flow's `requires:` is confirmed live

`workspaces/core/src/manifest.ts:428-431` reads `.flow.yaml` as a whole-doc manifest
(`wholeDoc` regex) and turns the block into the catalog entry's deps.

### D9 — The acceptance test was already broken

`skaileup-flows.test.ts:38` asserts on skills `["concept-brief", "concept-goals"]`;
ticket 08 deleted `concept-goals`. F4 recorded the line; the consequence is that the map's
destination sentence ("that test with one repo URL changed") is false independently of
anything ticket 10 decided.
