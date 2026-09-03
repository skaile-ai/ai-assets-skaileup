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
  `acceptance_criteria` shrinks to the EARS grammar. **Four files handed off rather than ruled**
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

## Not yet specified

- **The port itself, per domain.** The mockup domain has graduated (ticket 14); the
  concept-side and implementation-side ports still can't be sized until tickets 07 and 08
  land. Each is a rewrite-from-the-model pass, one ticket per domain group.
- **The five absorbed skills' actual bodies** — what a skaileup-flavoured `to-spec` /
  `to-tickets` / router / `grilling` / `research` says once it knows about `_concept/`.
  Blocked on knowing which skills they replace. Ticket 04 fixed their *names*
  (`spec-*` / `build-*` / `skaileup` / `concept-*`), not their contents. **Ticket 09 handed
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
- **Making `artifacts.yaml` reachable, and moving input-dialog specs to a sibling
  `inputs.yaml`.** Both are forge-concept edits (`artifact-contract.ts:138` and a new frontmatter
  reader), which this map already rules out. Ticket 09 accepted the consequences of *not* doing
  either — the registry dies, the dialog spec stays in frontmatter. If forge-concept is ever
  touched, the `inputs.yaml` move returns as its own effort.
