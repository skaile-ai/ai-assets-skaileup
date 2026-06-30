# Skaileup Skill Collection

## What This Is

All `skaileup-*` skills for the concept, build, and quality pipelines. Extracted from `ai-assets/` as a standalone submodule.

**GitHub:** `github.com/skaile-ai/ai-assets-skaileup`

## Documentation

- **Starlight site** at [`docs/`](./docs/) — `npm run docs` (or `cd docs && npm install && npm run dev`). Every SKILL.md is rendered as its own page with frontmatter + body, plus pages for the mental model, slice loops, tiers, flows, and the contracts reference layer.
- **[`CONTRIBUTING.md`](./CONTRIBUTING.md)** — skill-authoring guide for the `skaile` CLI.
- **[`docs/devlog/`](./docs/devlog/)** — plans, specs, design notes, and the improvement backlog.

## Structure

Skills are organized into 17 domains in three groups (Concept, Implementation, Meta).
**Domain and skill folders carry a two-digit `NN_` run-order prefix** so an alphabetical
listing reads in flow order; the prefix is stripped from `name:` (see *Naming Convention*).
User-facing skill domains live under `skaileup/`. System/meta assets (contracts, flows, CI scripts) live under `skaileup/`.

### Concept  (`skaileup/`)
```
01_concept/                  01_brief · 02_goals · 03_comparable · 04_grounding/{01_onboard,02_research,03_seeds,04_contracts}
02_design/                   01_brand-visual · 02_brand-voice · 03_inspiration
03_experience/               01_journeys · 02_behaviors · 03_screens · 04_screens-technical · 05_components
04_product-spec/             01_features (with EARS acceptance criteria)
05_mockup-walkthrough/       pick-one renderers: 01_a_text · 01_b_static-html · 01_c_astro · 01_d_lit · 01_e_framework
06_mockup-component/         pick-one: 01_a_isolated-html · 01_b_storybook/{01_setup..06_orchestrator}
07_mockup-feedback/          01_annotate → 02_triage → 03_patch → 04_apply
08_concept-slice/            per-feature concept loop (standard/complex): 01_brainstorm · 02_align · 03_scope-feature · 04_design-feature  → _concept/slices/<id>/
```

### Implementation  (`skaileup/`)
```
09_impl-architecture/        01_techstack · 02_templates-select · 03_system · 04_datamodel + templates/ (7 template-* assets, unnumbered)
10_impl-build/               one-time: 01_scaffold · 02_foundation · 03_infrastructure · 04_migrate · 05_seed · 06_generate · 07_docs
11_impl-plan/                01_brainstorm · 02_align · 03_plan-vertical · 04_supervised
12_impl-slice/               per-slice loop: 01_git-prepare · 02_implement · 03_implement-page · 04_test · 05_recap · 06_refactor · 07_commit · 08_git-finish  → _implementation/slices/<id>/
13_impl-quality/             01_test-plan · 02_eval-code · 03_audit · 04..06_test-{unit,integration,e2e} · 07_ready · 08..10_standards-{discover,inject,sync} · 11_12_debug-{self-verify,handoff}
```

### Meta — user-facing  (`skaileup/`)
```
00_skaileup-orchestrator/    base orchestrators (skills/{skaileup,skaileup-build}) · agents/ (SOULs) · scope/ · flows/ — pipeline entry (internals not numbered)
14_ops/                      cross-cutting: 01..04_project-{overview,subsystem-map,integration,review} · 05..07_eval-{concept,feature,product} · 08_review · 09_sync · 10_add-feature · 11_reverse-engineer
```

### Meta — system assets  (`skaileup/`)
```
skaileup/contracts/          shared reference layer (every skill reads) — unnumbered
skaileup/contracts/scripts/  CI scripts (pre-commit hook · verify_artifacts.py · validator_lib.py)
skaileup/contracts/tests/    contract fixtures (elements_block_examples.md)
skaileup/flows/              self-contained flow YAMLs (graph + requires: manifest) + docs, per app-type — unnumbered
skaileup/flows/_meta/        verify_flows.py · test_verify.py · deferred_skills.yaml
docs/devlog/                 plans, specs, design notes, improvement backlog
```

The collection-agnostic lab skills (validate · judge · improve · learn · report · compile-validators · archive · validate-elements-block) live in github.com/skaile-ai/ai-assets-skill-development.

## Skill Structure

Every skill lives in its own directory:

```
my-skill/
├── SKILL.md        ← YAML frontmatter + DSL body (the agent prompt)
├── CLI.md          ← Optional: CLI invocation docs
├── references/     ← Optional: reference material loaded on demand
├── scripts/        ← Optional: helper scripts
├── tests/          ← Optional: test manifest + fixtures (consumed by lab/validate in ai-assets-skill-development)
└── validator.py    ← Optional: compiled MUST/NEVER validator
```

The DSL grammar is documented in [`skaileup/contracts/skill_grammar.md`](./skaileup/contracts/skill_grammar.md):
`ROLE / READS / WRITES / REFERENCES / REQUIRES / INPUT / STEP / RUN / OUTPUT / EMIT / CHECKPOINT / IF / ELSE / UNTIL / MUST / NEVER / CHECKLIST / PROCEDURE / PATTERNS`.

The frontmatter schema is documented in [`skaileup/contracts/asset_frontmatter.md`](./skaileup/contracts/asset_frontmatter.md). It follows the [agentskills.io](https://agentskills.io/specification) spec — `name` and `description` at root, everything else under `metadata:`.

## Project Artifacts (what skills write)

Skills do not write into this collection — they write into the **target project**.
The canonical output tree is defined in
[`skaileup/contracts/concept_structure.md`](./skaileup/contracts/concept_structure.md)
and the id↔path registry in
[`skaileup/contracts/artifacts.yaml`](./skaileup/contracts/artifacts.yaml). In brief:

```
_concept/                 concept truth (durable)
├── _meta/scope.yaml      chosen tier — gates linear vs. per-feature slice loop
├── _grounding/           research · onboarding · seeds · standards
├── discovery/            brief · goals · comparable · brand/
├── experience/           journeys · features/<NN_group>/ · screens/<NN_group>/
├── mockup-walkthrough/   · mockup-component/ · _feedback/
├── slices/<id>/          per-feature concept dossier (frozen, kept): brainstorm · align · scope-feature · index
└── blueprint/            techstack · architecture · datamodel/

_implementation/          impl truth (durable ledgers)
├── PLANS.md · progress.json · decisions.md · git-state.json
└── slices/<id>/          per-feature impl dossier (frozen, kept): brainstorm · align · plan · test · recap · refactor · index
```

**Slice dossiers are frozen, not deleted** — see *Two-Group Architecture* below. The
**general (non-slice) artifacts** (brief, goals, brand, journeys, blueprint) are produced
once per project; only per-feature work lives under `slices/<id>/`.

## Contracts

Shared contracts live in [`skaileup/contracts/`](./skaileup/contracts/). **Every skill reads from here.** The non-negotiable constraints (iron laws + golden principles) and shared schemas (semantic types, frontmatter, EARS acceptance criteria) live there.

## Naming Convention

**Folders carry an ordering prefix; `name:` does not.** Each domain and skill
directory is prefixed with a two-digit run-order number (`NN_`) so an alphabetical
listing reads in the order the flows run the skills. Mutually-exclusive **alternative**
skills (pick-one sets) share one slot number and add a letter: `NN_<letter>_<name>`.

The skill's `name:` is the **domain-relative path with each segment's `NN_` / `NN_<letter>_`
prefix stripped and `/` replaced by `-`** — so names are stable regardless of ordering
edits, and every flow/`artifacts.yaml` reference is unaffected by renumbering.

| Path | `name:` |
|---|---|
| `skaileup/01_concept/01_brief/SKILL.md` | `concept-brief` |
| `skaileup/01_concept/04_grounding/01_onboard/SKILL.md` | `concept-grounding-onboard` |
| `skaileup/02_design/01_brand-visual/SKILL.md` | `design-brand-visual` |
| `skaileup/03_experience/03_screens/SKILL.md` | `experience-screens` |
| `skaileup/05_mockup-walkthrough/01_c_astro/SKILL.md` | `mockup-walkthrough-astro` (alternative; `01_c_` stripped) |
| `skaileup/09_impl-architecture/01_techstack/SKILL.md` | `impl-architecture-techstack` |
| `skaileup/09_impl-architecture/templates/template-postxl/TEMPLATE.md` | `template-postxl` (template assets are **not** numbered — `tech_stack_skill` resolves them by directory name at runtime) |
| `skaileup/06_mockup-component/01_b_storybook/SKILL.md` | `mockup-component-storybook` |

**Exception — base orchestrator skills:** Skills inside `skaileup/00_skaileup-orchestrator/skills/` keep their short names (`skaileup`, `skaileup-build`). The orchestrator's internal `scope/`, `skills/`, `agents/`, `flows/` subdirs are structural and are **not** numbered.

**Not numbered:** `contracts/` and `flows/` (reference/system layers, not pipeline steps) and `09_impl-architecture/templates/` + its `template-*` assets (resolved by directory name at runtime).

> **Note.** Number prefixes are *ordering metadata only* — strip `NN_` and an optional `NN_<letter>_` from each path segment to recover `name:`. `CONTRIBUTING.md` § Naming Conventions matches this.

## Two-Group Architecture

The collection is shaped by one observation: **the work of figuring out a product and the work of building it have the same rhythm.** Each side benefits from a per-feature loop when the product is too big to design or build in one pass. The result is the same shape on both halves — `concept-slice/` on one side, `impl-slice/` on the other.

```
                    user input  /  existing repo
                              │
                              ▼
                    ╔═════════════════════╗
                    ║    skaileup-base    ║   routes user, runs flows
                    ╚══════════╤══════════╝
                               │
                               ▼
                    ┌──────────────────────────────────────────┐
                    │ skaileup/skaileup-orchestrator/scope/... │   2-3 questions →
                    └────────────────────┬─────────────────────┘   tier + flow
                                 │
              ┌──────────────────┴──────────────────┐
              ▼                                     ▼
   ╔═══════════════════════════╗        ╔══════════════════════════╗
   ║          CONCEPT          ║        ║      IMPLEMENTATION      ║
   ╚═══════════════════════════╝        ╚══════════════════════════╝
   linear (appbuilder-mvp/simple) OR                   one-time setup +
   high-level + slice loop ↻                slice loop ↻
                                                          │
                                                          ▼
                  ╔══════════════════════════╗
                  ║           META           ║
                  ║  skaileup · ops · lab ·  ║
                  ║  contracts               ║
                  ╚══════════════════════════╝
```

Both slice loops follow the same five-phase shape with `/clear` between every phase: brainstorm → align → (scope-feature | plan-vertical) → (design-feature | implement → test → recap → refactor → commit). Phases read from the prior phase's handoff file in `_concept/slices/<id>/` or `_implementation/slices/<id>/`. **No phase carries the whole slice in context** — that's how big apps stay buildable past the dumb-zone (~100k tokens).

The slice dossier is **frozen on commit, not deleted** (Suggestion-B organization): the terminator (`concept-slice-design-feature` / `impl-slice-commit`) writes an `index.md` and **keeps** the phase handoffs as permanent per-feature documentation under `_concept/slices/<id>/` and `_implementation/slices/<id>/`. Truth still lives in code (impl-slice) or in the canonical `_concept/experience/...` artifacts (concept-slice); the dossier is the decision record beside it. The **general (non-slice) part** — brief, goals, brand, journeys, datamodel, techstack, architecture — lives in its phase folders and is not per-slice. Only the impl side's transient `progress.json` is removed on freeze.

## Flows

**Each flow is its own install manifest — there are no separate bundles.** A
`<name>.flow.yaml` carries a top-level `requires:` block that lists everything
provisioned when the flow is installed: the contracts its skills read plus every
skill its nodes run. Installing the flow yields a runnable workspace (flow +
skills + contracts). Install *all* assets, or just one flow's dependencies:

```
$ skaile add skill:*                    # install every skill (whole collection)
$ skaile add flow:appbuilder-standard          # OR provision exactly appbuilder-standard's deps
```

The `requires:` refs use the npm-style scoped ref grammar
`kind:@publisher/name[#version]` (`@` = scope sigil, `#` = version sigil; per
`workspaces/.../2026-06-02-scoped-asset-ref-grammar.md`). The `contract:` and
`skill:` kinds appear, plus `flow:` when a flow delegates a loop to a **sub-flow
node** (e.g. the standard/complex tiers delegate their per-feature loop to the
unified `skaileup-slice` flow instead of inlining it):

```yaml
# inside appbuilder-standard.flow.yaml, above globals:
requires:
  - contract:@skaile-ai/shared-contracts        # shared reference layer
  - contract:@skaile-ai/implementation-contract # domain contract its skills cite
  - skill:@skaile-ai/concept-goals              # …every skill its nodes run
  # …exactly the flow's own node skills, no more
  - flow:@skaile-ai/skaileup-slice              # …plus any flow a sub-flow node delegates to
```

The `requires:` set is **exact and self-contained**: its `skill:` refs equal
exactly the skills the flow's own nodes run, and its `flow:` refs equal exactly
the flows its sub-flow nodes delegate to — **no inheritance, no extras**. A
delegated loop's skills are provided transitively by the sub-flow's own manifest,
so the parent does not re-list them. (This replaced the old inheriting
`*.bundle.yaml` files, which dragged in "tier-shape extra" skills a flow never ran.)

**Contracts.** Two layers, listed directly in each flow's `requires:`:
the shared `skaileup/contracts/` reference layer (registered as
`shared-contracts`, read by every skill — so every flow lists it), plus the
domain contracts a flow's skills actually reference (`implementation-contract`
for `impl-build-docs`; `meta-concept-contract` for the `ops-project-*` suite).

**Installing a flow provisions its deps; running it is a separate act** — two
interchangeable ways:

1. **skaile workspace flow engine** (the flow connector) executes a `.flow.yaml` directly:
   ```
   $ skaile run flow:appbuilder-standard       # engine drives the flow node-by-node
   ```
2. **The orchestrator** (`skaileup` / `skaileup-build`) **understands the flow files** and
   guides/executes the same path conversationally — used when no flow engine is present, or
   when you want a human-in-the-loop run.

Either way the flow plus the skills and contracts in its `requires:` must already
be installed (install everything, or just `skaile add flow:<name>`).

Flows live under `skaileup/flows/<app-type>/`:

```
skaileup/flows/
├── appbuilder-mvp/
│   ├── appbuilder-mvp.flow.yaml      ← graph + requires: manifest
│   └── appbuilder-mvp.md             ← human doc
├── appbuilder-simple/
│   ├── appbuilder-simple.flow.yaml
│   └── appbuilder-simple.md
... (appbuilder-standard, appbuilder-complex, skaileup-slice{,-concept,-impl},
    skaileup-impl, skaileup-implementation, skaileup-concept-only, skaileup-concept-reverse)
└── _meta/
    ├── verify_flows.py
    ├── test_verify.py
    └── deferred_skills.yaml
```

`skaileup/flows/_meta/verify_flows.py` is the single guard: it validates each
flow against `flow.schema.json` and enforces that every flow's `requires:` skill
set **exactly** matches its node-skill set (no missing, no extra) and that its
`contract:` refs resolve in `skaile.yaml`. `test_verify.py` covers it.

## Reorganization Status

The collection underwent two reorganizations:

### Phase 0 (2026-04, complete)
- [x] Domain extraction from ai-assets
- [x] Domain merges (onboard+research→grounding, standards→quality) and splits (blueprint→architecture+datamodel)
- [x] Skill-level directory renames to `skaileup-<domain>-<function>` pattern
- [x] SKILL.md `name:` frontmatter updates
- [x] New domain: `skaileup-build-supervised/` (extracted from build)
- [x] Cross-domain moves: sync→concept-ops, compile-validators→lab, implement→skaileup base

### Phase 1 (2026-05-07, this branch)
- [x] 14 `skaileup-*` domains migrated to the new two-group structure (Concept + Implementation + Meta)
- [x] 16 new top-level domains scaffolded with stub DOMAIN.md
- [x] All ~70 SKILL.md files moved to new homes; `name:` frontmatter updated
- [x] Stack profiles promoted from `skaileup-quality/profiles/` to `impl-architecture/templates/`
- [x] Bulk path-reference update across READS/WRITES/REFERENCES + validator.py imports
- [x] DOMAIN.md content authored (Phase 2)
- [x] Validator creation for skills that lack them (Phase 2)

### Phase 2 — collection quality remediation (2026-05, complete)
The 2026-05-10 collection review backlog has been worked through across five commits (`Phase 1`–`Phase 5` in git history): frontmatter completed on all skills (`version`/`stage`), `user_inputs` → `prerequisites` migration, templates demoted out of the skill model, DOMAIN.md files authored, descriptions normalized, and CI gates added (frontmatter audit, bundle↔flow drift, pre-commit hook).

### Phase 3 — SKILL_GRAPH migration (2026-05-30, complete)
Tracked in [`docs/devlog/SKILL_GRAPH.md`](./docs/devlog/SKILL_GRAPH.md). All 11 deferred tier-flow skills are built; [`skaileup/flows/_meta/deferred_skills.yaml`](./skaileup/flows/_meta/deferred_skills.yaml) is now empty and the flow verifier emits no deferred-skill warnings:

- `concept-goals`, `concept-comparable` (`concept/`), `design-inspiration` (`design/`) — high-level concept pass for standard/complex tiers.
- `impl-architecture-templates-select` — runtime selector over the 7 `template-*` reference assets; writes `tech_stack_skill`.
- `mockup-walkthrough-astro` / `-lit` / `-framework` and the `mockup-feedback-{annotate,triage,patch,apply}` cluster — walkthrough renderers + feedback loop.

### Phase 4 — slice dossiers as durable documentation (2026-06-01, complete)
Slice artifacts moved under the side they belong to and are now **frozen, not deleted**:

- `_slice/concept/<id>/` → `_concept/slices/<id>/`; `_slice/impl/<id>/` → `_implementation/slices/<id>/`.
- The terminators (`concept-slice-design-feature`, `impl-slice-commit`) write an `index.md` and keep the phase handoffs as permanent per-feature documentation; `impl-slice-commit` removes only the transient `progress.json`. `impl-slice-git-finish` gates on "every slice frozen (has index.md)".
- Contracts updated (`artifacts.yaml` slice ids → `durable` + new `slice-{concept,impl}-index`; `concept_structure.md` documents `slices/`). The orchestrators now route standard/complex tiers into the per-feature slice loops and assist within them.
