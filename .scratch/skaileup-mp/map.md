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

## Not yet specified

- **The port itself, per domain.** Can't be sized until the inventory tickets (Mockup domain
  consolidation / Concept-side consolidation / Implementation-side consolidation) land. Likely
  several tickets, one per domain group, each a rewrite-from-the-model pass.
- **The five absorbed skills' actual bodies** — what a skaileup-flavoured `to-spec` /
  `to-tickets` / router / `grilling` / `research` says once it knows about `_concept/`.
  Blocked on knowing which skills they replace. Ticket 04 fixed their *names*
  (`spec-*` / `build-*` / `skaileup` / `concept-*`), not their contents.
- **CI and validation.** `verify_flows.py`, `verify_artifacts.py`, the pre-commit hook and
  `validate_skill_rules.py` all validate DSL that's going away. What replaces them, if anything.
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
