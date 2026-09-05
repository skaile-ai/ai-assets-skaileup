# Brief — 18: Architecture + build

Evidence for the grilling ticket. **Nothing here is a resolution.** Every question closes in
conversation; this file only makes the conversation fast.

Measured against `skaileup/` on branch `wayfinder/map`, 2026-09-05.

---

## The eleven

`flows (node)` = flows that name the skill in a `data.skill:` node. `flows (reach)` = including
the parent flows that consume the `architecture` / `impl-build-setup` sub-flows, minus parents
that pass `skip`. `stack%` = body lines naming a concrete stack/tool token, over body lines.

| # | name | lines (fm/body) | flows (node) | flows (reach) | reads | writes | contracts read in-body | stack% | zero-flow |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `impl-architecture-techstack` | 328 (75/253) | `architecture`, `appbuilder-mvp`, `skaileup-stepwise` | 8 | `discovery/brief.md`; `templates/*/TEMPLATE.md`; ?features, ?`_grounding/overview/user_input.json`, ?`_grounding/research/onboarding.md` | `blueprint/techstack.md` (full stack + `tech_stack_skill`) | `concept_structure`, `frontmatter` | 1% | — |
| 2 | `impl-architecture-templates-select` | 223 (41/182) | `architecture`, `appbuilder-mvp` | 5 (skipped by `skaileup-implementation`, `skaileup-concept-only`) | `blueprint/techstack.md`; `templates/template-*/TEMPLATE.md`; ?`_meta/scope.yaml` | `blueprint/techstack.md` — **one frontmatter field**, `tech_stack_skill` | `concept_structure`, `frontmatter`, `templates/DOMAIN.md` | 5% | — |
| 3 | `impl-architecture-system` | 279 (66/213) | `architecture`, `skaileup-concept-reverse` | 5 (skipped by `appbuilder-simple`, `appbuilder-cli`) | brief, features, techstack; ?behaviors `.allium`, ?grounding | `blueprint/architecture.md` (6 sections + `apps/custom_modules/protocols/external_integrations` frontmatter) | `concept_structure`, `frontmatter`, `semantic_types` | 0% | — |
| 4 | `impl-architecture-datamodel` | 373 (75/298) | `architecture`, `skaileup-concept-reverse`, `skaileup-stepwise` | 8 | brief, features, techstack; ?stories.yaml, ?architecture.md, ?behaviors, ?patterns.md | `blueprint/datamodel/{model.dbml,model.json,seed.json,feature_map.json}` + feedback loop into feature `data_entities[]` | `concept_structure`, `semantic_types`, `golden_principles`, `feedback_loop`, `seed_data` | 0% | — |
| 5 | `impl-build-scaffold` | 234 (55/179) | `impl-build-setup`, `appbuilder-mvp`, `skaileup-stepwise` | 7 | techstack + `templates/<tech_stack_skill>/TEMPLATE.md`, brief, model.json; ?architecture.md, ?seed.json | `<app-slug>/`; `_implementation/{PLANS.md,progress.yaml,decisions.md}`; git branch | `concept_structure`, `plans`, `domain_model`, `seed_data`, `iron_laws` | 0% | — |
| 6 | `impl-build-foundation` | 279 (59/220) | `impl-build-setup`, `skaileup-stepwise` | 6 | techstack + TEMPLATE.md, `brand/tokens.json`; ?identity.md, ?`screens/00_layout/shell.md`, ?architecture.md, ?seed.json | theme file, auth files, layout + nav, seed file, Storybook theme; `_implementation/progress.yaml` | `concept_structure`, `iron_laws` | 0% | — |
| 7 | `impl-build-infrastructure` | 238 (49/189) | `impl-build-setup` | 4 (skipped by `appbuilder-simple`) | `blueprint/architecture.md` (hard), techstack, features | `backend/libs/**`, `backend/apps/**`, `docker-compose.yml`, `.env.example`; `progress.yaml` | `concept_structure` (+ two `references/` files **that do not exist**) | 1% (11 lines carry NestJS-shaped paths) | — |
| 8 | `impl-build-migrate` | 169 (38/131) | `impl-build-setup`, `skaileup-stepwise` | 6 | `model.dbml`, `model.json`, techstack, `semantic_types.md` | stack-specific migration files | `semantic_types` | 3% | — |
| 9 | `impl-build-seed` | 190 (42/148) | `impl-build-setup` | 5 | `seed.json`, `model.json`, techstack, `seed_data.md`, `semantic_types.md`, existing migrations | per-scenario seed scripts + entry point | `seed_data`, `semantic_types` | 2% | — |
| 10 | `impl-build-generate` | 139 (34/105) | **none** | **0** | `postxl-schema.json` (hard), `postxl-lock.json`, `model.json` | `src/` (regenerated), `postxl-schema.json`, prisma migrations | none | **25%** | **ZERO-FLOW** |
| 11 | `impl-build-docs` | 254 (22/232) | `impl-build-setup` | 5 | `git diff`, `docs/src/content/docs/**` `_sources` frontmatter, the source files those name | `docs/src/content/docs/**` (target project's Starlight pages) | `concept_structure`, `doc_tracking` | 6% | — |

**Zero-flow list: exactly one — `impl-build-generate`.** No `data.skill:` node, no `requires:`
entry in any flow. Its only mentions outside its own directory are `10_impl-build/DOMAIN.md`
(dying, ticket 05) and `contracts/flows.md` line 78 (deleted, ticket 09). It has **no reader
after this repo's own prune**.

Near-misses worth naming beside it:
- `impl-build-infrastructure` and `impl-build-seed` reach only through `impl-build-setup`, and
  `appbuilder-simple` passes `infrastructure: skip` — infra runs in 4 of 10 flows.
- `impl-architecture-templates-select` reaches 5, and **two of its six sub-flow consumers pass
  `templates: skip`** (`skaileup-implementation`, `skaileup-concept-only`).

### Aux assets that would have to port with them

`09_impl-architecture/`: 3 `validator.py` (91 / 78 / 128), 3 `CLI.md` (16/16/19), 3 `references/`
(52 / 184 / 223), `DOMAIN.md` (48), **`templates/` — 7 × `TEMPLATE.md`, 3,799 lines**.
`10_impl-build/`: `07_docs/CLI.md` (33), `DOMAIN.md` (50), `agents/skaileup-implement/`
(SOUL + agent.yaml — no `agents/` in `-mp`), `contracts/implementation-contract/CONTRACT.md`
(104), `contracts/subagent_dispatch.md` (117 — ticket 09 folds it into `agent_patterns.md`).

`infrastructure` cites `references/layer_patterns.md` and `references/dependency_mapping.md`
in its `REFERENCES` block. **Neither file exists on disk.**

---

## Q1 — `architecture` as its own domain, or folded into `build`

### What the four write into `_concept/blueprint/`, and who reads it

| writer | artifact | downstream readers (SKILL.md count) | of which run **before any code** |
|---|---|---|---|
| `techstack` | `blueprint/techstack.md` | 29 | `experience-screens`, `experience-screens-technical`, `experience-components`, `mockup-walkthrough-text`, `mockup-walkthrough-framework`, `mockup-component-storybook` (orchestrator), `ops-eval-concept` — **7 concept-side** |
| `templates-select` | `blueprint/techstack.md` → `tech_stack_skill` only | same file; the field is resolved by `scaffold`, `foundation`, `design`, mockup + storybook skills | mockup + storybook resolve it pre-code |
| `system` | `blueprint/architecture.md` | 9 | `experience-screens`, `experience-screens-technical` — **2 concept-side** |
| `datamodel` | `model.dbml` (5) · `model.json` (25) · `seed.json` (20) · `feature_map.json` (5) | 25 for `model.json` | `experience-screens`, `-technical`, `experience-components`, `concept-slice-design-feature`, `mockup-component-storybook-{components,types}`, `design-brand-voice`, `mockup-walkthrough-text` — **8 concept-side on `seed.json`, 7 on `model.json`** |

The blueprint is not a build input that happens to be written early. It is **read across the
whole concept half**: screens, components, walkthroughs, storybook and the per-feature concept
dossier all consume it.

### The flows: separate lanes, and `data.phase` says so unanimously

Every flow that declares a phase for the architecture block declares **`conceptualization`**;
every flow that declares one for the build block declares **`implementation`**. No exception:

| flow | architecture node | build node |
|---|---|---|
| `appbuilder-simple` | `phase: conceptualization` (L184) | `phase: implementation` (L199) |
| `appbuilder-standard` | `phase: conceptualization` (L314) | `phase: implementation` (L328) |
| `appbuilder-complex` | `phase: conceptualization` (L360) | `phase: implementation` (L374) |
| `appbuilder-cli` | `phase: conceptualization` (L125) | `phase: implementation` (L141) |
| `skaileup-implementation` | `phase: conceptualization` (L89) | `phase: implementation` (L105) |
| `skaileup-concept-only` | `phase: conceptualization` (L257) | *(no build block at all)* |
| `appbuilder-mvp` | `techstack` + `templates` → `parentNode: g-conceptualization` | `scaffold` → `parentNode: g-implementation` |
| `skaileup-stepwise` | `techstack` L87, `datamodel` L98 → `phase: conceptualization` | `scaffold` L110, `foundation` L121, `migrate` L132 → `phase: implementation` |

**`skaileup-concept-only` runs the whole `architecture` sub-flow and never reaches a build
node.** That is the strongest single fact on this question: architecture is reachable without
build, but no flow reaches build without architecture.

Two contradictions inside the same evidence, both worth putting to the human:

1. **`appbuilder-standard` labels the group against its own node.** The container
   `g-architecture` carries `phase: implementation` (L101); the `architecture` node inside it
   carries `phase: conceptualization` (L314). Per ticket 04's `phaseForNode`, explicit
   `data.phase` wins, so the node is right and the group label is decorative and wrong.
2. **`skaileup-concept-reverse` declares no `phase` on its `impl-architecture-system` /
   `-datamodel` nodes**, only `parentNode: g-conceptualization`. With no `data.phase`, the
   fallback is the **name prefix** — and `impl-` reads as implementation, contradicting the
   group. Renaming to `architecture-*` in `-mp` removes the trap; leaving them under `build-*`
   re-creates it.

### The architecture flow's declared order is mostly fiction

Ticket 15: the engine takes dependencies from `edges.filter(e => e.type === "flow")`. In
`architecture.flow.yaml`:

```
e-techstack-templates      type: optional   → orders nothing
e-templates-arch-system    type: optional   → orders nothing
e-arch-system-datamodel    type: flow       → the only real dependency
```

So at engine level the block is three unordered roots plus `datamodel` depending on
`arch-system`. Same pattern in `impl-build-setup`: `e-foundation-infra-opt` is `optional`, so
`foundation` orders nothing — the real chain is `scaffold→foundation` and
`infra-opt→migrate→seed→docs`, two disconnected components.

### One ordering contradiction the domain question inherits

`experience-screens` reads `blueprint/techstack.md`, `architecture.md`, `model.json` and
`seed.json` — all `gate: soft`. In `appbuilder-standard` the `screens` node (L213) runs
**before** the `architecture` sub-flow (L303); same in `skaileup-concept-only` (screens L219,
architecture L253). `skaileup-stepwise` inverts it (techstack + datamodel first). So the
blueprint's concept-side readers currently run before its writers in 2 of 3 flows that have
both, degrading through soft gates.

---

## Q2 — `PLANS.md` (the crux)

### What the contract says it is

`contracts/plans.md` (deleted by ticket 07; the artifact handed here): *"a **lean scope + phase
plan**, not a status tracker and not a decision log. It answers two questions only: what is in
scope for this session, and what are the phases, in order."* Its own table already exiles
status → `progress.yaml`/`concept.yaml`, decisions → the ADR logs, vocabulary → `glossary.md`,
per-slice detail → `align.md`.

Its Implementation-Plan template has three sections: **Scope** (one paragraph, in/out),
**Source Artifacts** (a pointer list — features dir, techstack.md, datamodel/, screens/,
glossary.md, brand tokens, with counts), **Phases** (1 scaffold · 2 foundation · 3
infrastructure · 4 migrate→seed · 5 per-feature slice loop · 6 e2e→deploy).

**That Phases list is `impl-build-setup.flow.yaml` written in prose.** Node-for-node.

### Per-reader table

Verdict column answers only the ticket's test: is what this reader takes from `PLANS.md`
**status** (now `progress.yaml`), **order** (now the flow graph), or **neither**?

| # | reader | site | what it actually does | verdict |
|---|---|---|---|---|
| 1 | `impl-build-scaffold` | `WRITES` L116; `REFERENCES` L122; STEP 9 L198; Common-Mistakes L234 | **Creator.** "Create `_implementation/PLANS.md` (scope + source artifacts + ordered phases — NO checkboxes; status lives in progress.yaml)". Writes it in the same session as `progress.yaml` + `decisions.md`. | **order** (Phases = the flow) + **neither** (Scope, Source Artifacts) |
| 2 | `impl-build-foundation` | L228 | Reads nothing. The string appears inside a parenthetical on a `progress.yaml` write: *"(progress.yaml is the completion source of truth; **PLANS.md carries no checkboxes**)"*. | **not a reader** — a status disclaimer |
| 3 | `impl-build-infrastructure` | L238 | Reads nothing. Checklist item: *"progress.yaml updated (completion source of truth; **PLANS.md carries no status**)"*. | **not a reader** — a status disclaimer |
| 4 | `impl-plan-plan-vertical` | L163 (`REFERENCES`), L189 (`MUST`) | Reads nothing. L163 disambiguates the per-slice `plan.md` from the project-level file; L189 is a boundary: *"never write to a project-wide path — the project-level PLANS.md is **owned by a different skill**"*. Collapsed into `build-plan` by ticket 07. | **not a reader** — an ownership fence |
| 5 | `impl-slice-git-prepare` | L79 (`READS`), L110 (STEP 3) | Reads **existence only**: `? _implementation/PLANS.md — detect if resuming`; STEP 3 *"IF branch `implement/<app-slug>` already exists → Check if `_implementation/PLANS.md` exists → resuming mode"*. Collapsed into `build-branch` by ticket 07. | **status** — and `progress.yaml` and this skill's own `git-state.yaml` both already carry it |
| 6 | `concept-brief` | L170 | Reads **content no other artifact holds**: *"If raw_description is provided (free-form text field or **PLANS.md `## Raw Description` section**): extract as many fields as possible from it (app name, pitch, audience, problem, hero flow, comparables, success criteria)"*. | **neither** — and see the gap below |
| 7 | `ops-review` | Context-Budget L100, `READS` L118, STEP entropy L200 | `? PLANS.md — concept progress plan`; entropy indicator *"PLANS.md progress out of sync with actual `_concept/` state → **PLAN DRIFT**"*; `references/checks.md:116` and `references/gardening.md:18,26` add the gardening fix ("update checkboxes to match observed state"). | **status** — and it is a *drift check on duplicated status*, i.e. the failure mode the progress.yaml split was made to remove |
| 8 | `ops-add-feature` | L273 | **Writes**: *"IF no → note the feature in PLANS.md as **implementation backlog**"*. | **neither** — a backlog / scope queue |
| 9 | `ops-project-review` | L44, L84, L86–90 | Reads the **meta-concept** `PLANS.md` at the umbrella root — checklist items on the *subsystem status table*, *cross-product journeys*, *roadmap milestones*, *decisions section*. Governed by `14_ops/contracts/CONTRACT.md` §"PLANS.md Format" (L247). | **different artifact** — the multi-product umbrella `PLANS.md`, which the map lists **out of scope** |

### What the table adds up to

- **Three of the nine (2, 3, 4) do not read it.** They *mention* it, twice to say it carries no
  status and once to say it belongs to someone else. Ticket 07's "9 in-body readers" is a
  grep count, and — exactly as ticket 09 found for `frontmatter.md` (86 refs, 13 real readers)
  — the raw count overstates.
- **One (9) is a different file** at a different root, owned by the out-of-scope umbrella.
- **Two (5, 7) take status**, which `progress.yaml` covers by construction; (7) exists *only*
  because status is duplicated.
- **Order is covered exactly.** The Phases list is the flow graph, and the flow graph is a
  live contract (ticket 01) while the prose list is not.
- **The residue is three sites, all "neither", all the same shape: scope.**
  - `scaffold`'s **Scope** paragraph + **Source Artifacts** pointer list (a derivable
    inventory of what the build reads, with counts).
  - `concept-brief`'s **`## Raw Description`** — free-form product text, an *input* channel.
  - `ops-add-feature`'s **implementation backlog** note.

### Two facts that sharpen the residue

1. **`## Raw Description` is not in the contract.** `contracts/plans.md` defines only
   `## Concept Plan` / `## Implementation Plan` with Scope + Phases (+ Source Artifacts).
   `concept-brief` reads a section the schema never defined — the one genuinely-neither
   reader is reading an undocumented section. Ticket 05 also renamed this category: user-
   supplied text is an **answer**, and answers merge into `onboarding.yaml`.
2. **Everything else is already registered elsewhere.** `artifacts.yaml` (dying) lists
   `impl-plans` alongside `impl-progress`, `impl-decisions`, `impl-git-state` — `PLANS.md` is
   the only one of the four whose content is not machine-read anywhere.

### Non-skill sites (not among the nine, but they die or move with it)

`skaileup` + `skaileup-build` orchestrator SKILL.md (~20 refs incl. `MUST create or resume
PLANS.md before any work` and `MUST update PLANS.md at every checkpoint` — the latter directly
contradicts `contracts/plans.md`'s "never track completion here"); three `SOUL.md` (no
`agents/` in `-mp`); `conceptualization-contract/CONTRACT.md` §"PLANS.md (Concept Phase)";
`implementation-contract/CONTRACT.md` §"PLANS.md (Implementation Phase)";
`impl-quality-ready/references/report_templates.md:58`; `contracts/skill_grammar.md:170`
(the DSL's optional step name, "for tracking in PLANS.md" — DSL dies).

In `-mp` today `PLANS.md` survives only as two stale mentions: `contracts/README.md:55` (a row
for the deleted `plans.md`) and `docs/adr/0006`'s note that it "has readers in the build and
ops domains".

---

## Q3 — `impl-build-generate` (139 lines, zero flows)

**What it is.** A PostXL regeneration + merge-conflict skill, not a codegen authoring skill.
Hard gate: `postxl-schema.json` in the project root. Workflow: pre-flight → sync `model.json`
into `postxl-schema.json` → `$ pnpm run generate` → **four-level conflict cascade** (auto-
overwrite generated-only / preserve `<<<<<<< Custom` blocks / `pnpm run generate --diff`
intelligent merge on ejected files / escalate) → `$ pnpm prisma migrate dev` → build → commit.

**Is it PostXL-only?** Yes, unambiguously: hard-gated on `postxl-schema.json`, banner *"This
skill is specific to the **PostXL** tech stack… requires `@postxl/cli`"*, `pnpm`-pinned commands,
`postxl-lock.json`. 25% of body lines name a concrete tool — 5× to 25× every other skill here.

**Was it the home `mockup-component-storybook-types` should have had?** The evidence says no —
they share only "PostXL":

| | `impl-build-generate` | `mockup-component-storybook-types` (183 lines) |
|---|---|---|
| input | `postxl-schema.json` (project root) | `_concept/blueprint/datamodel/model.json` |
| tool | `pnpm run generate` + `prisma migrate dev` | `pxl types --output …` |
| target | the **application** `src/` | `_concept/prototype/storybook/src/types/` — a **concept-side mockup artifact** |
| job | keep generated code in sync, resolve merges | replace placeholder story types, make the Storybook project compile |

Different input, different tool, different artifact, different half of the tree.

**The fact that reframes the question.** All seven templates already carry a `## Codegen`
section. `template-postxl/TEMPLATE.md:567-595` holds the whole thing: when to run
`pnpm run generate`, why `postxl-schema.json` is the source of truth, the five generated
output locations, and the `pnpm prisma generate` pairing. `generate`'s 105 body lines add, over
that: the four-level conflict cascade and the custom-block preservation rule.

---

## Q4 — the Storybook split, confirmed from the build side

**`10_impl-build/02_foundation/SKILL.md:74-75`, verbatim:**

```
5. **Storybook brand config** — configure Storybook theme decorator with brand tokens
   (only if `prototype/storybook/` exists)
```

**The step it describes — Phase 5, L213-217, the whole of it:**

```
# ── Phase 5: Storybook Brand Config ──────────────────────────────
STEP 5: Configure Storybook (if exists)
IF \_concept/prototype/storybook/ exists AND Storybook is installed - Configure Storybook
theme with brand tokens (background, fonts, colors) - Create theme decorator wrapping all
stories with brand CSS variables - Set up viewport presets from shell spec's responsive
breakpoints
Commit: `foundation: configure Storybook with brand theme`
```

Five lines. No `npx storybook init`, no `.storybook/main.*`, no addon resolution, no
dependency install. **`foundation` does not scaffold Storybook — ticket 07's correction to
ticket 06 holds from this side.** Other traces are frontmatter tag `storybook` (L17),
description (L3), `ROLE` (L116), a `MUST commit once per sub-phase` (L143), an `EMIT` phase
list (L229), one checklist row (L245).

**But the correction goes one step further than ticket 07 stated.** The scaffolder already
exists and already does all three of foundation's bullets:
`mockup-component-storybook-setup` (171 lines) — *"scaffolds a standalone Storybook project,
installs dependencies, **and applies brand tokens as CSS custom properties**"* — writes
`.storybook/theme.*` from `tokens.json` (STEP 5: base/appBg/fontBase/fontCode/brandTitle),
`.storybook/preview.*` as a **CSS-custom-property decorator over all 11 colour tokens** (STEP
6), **viewport presets from `shell.md` breakpoints** (STEP 4 + 6), and `src/styles/brand.css`
(STEP 7). Ticket 14's `mockup-storybook` inherits that.

**And the gate is on the wrong artifact.** `foundation` gates on `_concept/prototype/storybook/`
— the **concept-side mockup project** — then themes the **app's** Storybook. It tests A to act
on B. The two are different projects in different trees, and the mockup one is already themed
by its own setup step.

**What `foundation` would have to keep, if anything.** The templates carry the app-side
recipe, not `foundation`: all 7 `TEMPLATE.md` have a `## Storybook Config` section with the
four machine keys `storybook_addon` / `story_format` / `component_import` / `setup_file` plus
a `.storybook/main.ts` and `.storybook/preview.tsx` sketch. So the app-side Storybook's
install recipe already lives in `templates/`, and the mockup-side scaffold + theme already
lives in the storybook cluster. What is left over for `foundation` is the question.

---

## Q5 — `templates-select`: skill, or last step of `techstack`?

### The diff

| | `techstack` (328) | `templates-select` (223) |
|---|---|---|
| discovers | `templates/*/TEMPLATE.md` at runtime (`MUST … never hardcode`) | `templates/template-*/TEMPLATE.md` at runtime (`MUST … never hardcode`) |
| reads of each | Identity table + "When to Use" | Identity table only (`Never load: template bodies beyond the Identity table`) |
| decides | abstract stack **and** `tech_stack_skill: <profile-id>` | `tech_stack_skill` |
| writes | `blueprint/techstack.md` (whole file) | `blueprint/techstack.md` — **`tech_stack_skill` only**, "Change nothing else" |
| approval | `CHECKPOINT stack_approved`, `UNTIL user explicitly approves` | `CHECKPOINT template_approved`, `UNTIL the user explicitly approves` |
| extra reads | brief, features, grounding | `?_meta/scope.yaml` (tier) |

**Both skills scan the same directory, read the same Identity tables, and set the same field,
each behind its own human approval checkpoint.** `techstack` STEP 4 already "select[s] the
best matching profile", and its CHECKLIST already requires *"tech_stack_skill field is set
(matches a `09_impl-architecture/templates/` directory or 'custom')"*.

What `templates-select` has that `techstack` does not:
1. an explicit weighted score — frontend ×3, ui_library ×2, backend ×1, database ×1;
2. a **tier tie-break** from `_meta/scope.yaml` (mvp/simple → `*-minimal`; standard/complex →
   the fuller UI-library template);
3. a filesystem existence check — `$ test -d 09_impl-architecture/templates/<id>`;
4. a no-match escape hatch (`custom`, "never map Svelte onto a Next template");
5. a "show a diff before overwriting an approved concrete id" rule.

Items 1–5 are roughly 60 body lines. The remaining ~120 are `Overview` / `When (Not) to Use` /
`Context Budget` / `Depth Behavior` / `Common Mistakes` / `Integration` — the boilerplate
ticket 03 measures at 16% collection-wide and deletes.

### How the flows wire them

- `architecture.flow.yaml`: `techstack` (`optional: false`) → `templates`
  (**`optional: true`**, `parameters.mode: '${templates}'`) → `arch-system` → `datamodel`.
  Global `templates: include | skip`.
- **The edge between them is `type: optional`** (`e-techstack-templates`) — per ticket 15,
  **it orders nothing**. Same for `e-templates-arch-system`. Sequence is a drawing, not a
  dependency.
- **Two of six consumers skip it:** `skaileup-implementation` passes `templates: skip`
  ("read-or-generate, no templates step"); `skaileup-concept-only` passes `templates: skip`.
  No consumer passes `templates:` explicitly to *include* it — `include` is only the default.
- `appbuilder-mvp` runs it as a bare node, again `optional: true`, again reached by
  `e-techstack-templates` `type: optional`; only `e-templates-scaffold` is `type: flow`.
- `skaileup-stepwise` runs `techstack` **without** `templates-select` at all.
- `09_impl-architecture/DOMAIN.md`'s own Sequence block omits it:
  `techstack → system ∥ datamodel → templates/<chosen-template>`.
- It was one of the 11 Phase-3 deferred skills (`flows/_meta/deferred_skills.yaml`, closed
  2026-05-30) — a later addition to a domain whose docs never absorbed it.

### What the templates actually are — and a broken contract

`profiles/` and `templates/` are **not the same thing**, and ticket 05 already settled the
words: **profile = project type**, **template = tech-stack reference**.

- Old repo `skaileup/contracts/profiles/` = 6 **project types** — `web-app.yaml`,
  `cli-tool.yaml`, `api-service.yaml`, `library.yaml`, `mobile-app.yaml`,
  `data-pipeline.yaml`. Ticket 09 hoisted this directory to the repo root.
- `-mp` `profiles/` = the same 6 files, unchanged: artifact-path maps
  (`techstack: path: "blueprint/techstack.md"`, `datamodel: path: "blueprint/datamodel/"`, …).
  **No stack content whatsoever.**
- The stack content is `09_impl-architecture/templates/` — 7 `TEMPLATE.md`, **3,799 lines**,
  each with the same 15 headings: `Identity`, `When to Use`, `Scaffold Recipe`,
  `Preview Compatibility`, `CSS Variables / Theming`, `Auth Setup`, `App Shell`,
  `Component Library`, `Mock Adaptation`, `Storybook Config`, `Migration / ORM`, `Codegen`,
  `Expert Skills`, `Key Implementation Patterns`, `Overview`.
- **`-mp` has no `templates/` directory at all.** The 3,799 lines have no home in the
  destination repo yet.

**The skill↔template contract is broken by name.** `scaffold` STEP 1 says *"Extract from
profile: `scaffold_command`, `project_structure`, `build_command`, `package_manager`,
`env_setup_command`"* and later reads `lint_command`, `type_check_command`, `seed_format`.
`foundation` tabulates `css_vars_mapping` / `auth_setup` / `app_shell` / `seed_format`.
**Not one of those keys occurs in any `TEMPLATE.md`.** The only machine keys the templates
define are `storybook_addon`, `story_format`, `component_import`, `setup_file` (7× each) and
`mock_template`. The content exists — as prose under `## Scaffold Recipe`, `## CSS Variables
/ Theming`, `## Auth Setup`, `## App Shell` — but every `MUST read <key> from the profile` is
literally unresolvable, and `foundation` even ships the fallback: *"If any section is missing
from the profile, ask the user for guidance."*

`templates/README.md` is also stale against its own templates: it calls `template-postxl`
"FastAPI + Vue + PostgreSQL" (the TEMPLATE and `templates-select`'s table both say React 19 +
Vite / NestJS + Prisma + PG) and says "Nuxt 3" where the templates say Nuxt 4.

---

## Q6 — how stack-specific are `seed` and `migrate`?

Measured, not estimated.

| | body lines | per-ORM branch block | branch % | what the rest is |
|---|---|---|---|---|
| `migrate` | 131 | **4** (STEP 5, one line each: Prisma / Drizzle / Directus / raw SQL) | **3%** | read + cross-check `model.dbml` vs `model.json`; load `semantic_types.md` translation table; stack-neutral conventions (UUID PKs, `created_at`/`updated_at`, `on_delete` from model.json defaulting SET NULL, junction table per m2m, snake_case columns); 6-point validation; summary |
| `seed` | 148 | **12** (STEP 6: `prisma/seed.ts` + `prisma/seeds/`, `src/db/seed.ts` + `src/db/seeds/`, `seeds/<scenario>.sql`) | **8%** | enumerate scenarios; build the insert-order dependency graph (parents before children, reverse for cleanup); one entry point taking a scenario argument; 6-point validation (IDs preserved, FKs resolve, enums match `model.json`, required fields, **empty actively clears**, edge_cases has specials); summary |

By token density across the whole body (any concrete stack/tool word): `migrate` 3%,
`seed` 2%. Both are **overwhelmingly stack-neutral**; the branch is a file-path table.

Three facts that decide where the residue goes:

1. **All 7 templates already have a `## Migration / ORM` section** — `template-postxl:505-566`
   carries the full `schema.prisma` sketch plus `prisma migrate dev` / `migrate deploy` /
   `migrate reset` / `prisma generate`. `migrate`'s four branch lines are a lossy summary of
   content that already exists per-template.
2. **No template has a seed section.** `grep -i seed` across all 7 `TEMPLATE.md` returns
   nothing, and the `seed_format` key `foundation` reads does not exist. `seed`'s 12 lines are
   the *only* place the per-ORM seed layout is written down.
3. **Neither skill reads its template.** Unlike `scaffold` and `foundation`, `migrate` and
   `seed` never resolve `templates/<tech_stack_skill>/TEMPLATE.md`. They both instead carry
   `MUST search for prog-expert-* skills` / `Search dev-implementation-experts-*` — and
   **no `prog-expert-*` skill exists** in `ai-assets-skaileup`, `ai-assets`,
   `ai-assets-skaile-powers`, `ai-assets-skill-development`, or `-mp`. The name appears only
   inside each template's `## Expert Skills` section as a wish-list. Two `MUST`s pointing at
   nothing installed.

### Seed is written three times

`impl-build-seed` is not the only seed writer:

- `scaffold` STEP 7: *"IF seed.json exists AND stack profile has seed setup instructions —
  Configure the `populated` scenario from seed.json — Write to the stack-appropriate seed file
  location."*
- `foundation` Phase 4: *"Extract the `populated` scenario — Transform to stack-specific seed
  format (per profile `seed_format` if defined) — Map concept field names to stack conventions
  — Assign explicit short IDs — Resolve cross-references — Write to the stack-appropriate seed
  file location — Run seed to verify."*
- `impl-build-seed`: all four scenarios, dependency-ordered, one file each.

And migration twice: `scaffold` STEP 6 *"Run initial migration from model.json/model.dbml"*
before `migrate` exists in the flow order at all.

---

## Q7 — `impl-build-docs` (254)

**Two different Starlight sites are in play, and the map's fog patch names the other one.**

- The map's open patch — *"`docs/` is a Starlight site that renders every SKILL.md"* — is
  **this collection's** site, generated by `docs/scripts/generate-skill-pages.mjs` (470 lines).
- `impl-build-docs` never touches it. It maintains the **target project's** Starlight docs.

**What `impl-build-docs` does.** `git diff --name-only` (or `main...HEAD` on a branch) →
filter out tests/configs/locks → for each changed file, grep every doc page's `_sources[].path`
to find the pages responsible → read the doc + the changed source and classify each mapped
section **CURRENT / STALE / MISSING / BROKEN** → rewrite only the stale sections, preserving
prose and heading positions → recompute `_source_hash` (SHA-256 of sorted path+content,
first 8 hex) and stamp `_last_synced` → scaffold pages for significant uncovered changes →
validate internal links → check sidebar `autogenerate` coverage in `astro.config.mjs`.

**Frontmatter dependency.** Three custom fields, all on **target-project doc pages**, none in
`_concept/`: `_sources[]` (`path` · `sections` · `description`), `_source_hash`,
`_last_synced`. Ticket 09 pruned `_concept/` artifact frontmatter — it does not reach these.
So: **no, it does not depend on frontmatter ticket 09 pruned.** What it does depend on:

- `contracts/doc_tracking.md` (225 lines) — the `_sources` schema, `@doc:` annotations,
  staleness protocol, coverage formula. **Ticket 09 already routed this into `build-docs`.**
  That contract names its consumers as `skaildev-doc` (a different collection) and
  **`update-starlight-docs`** — this skill's old name. Stale on both rows.
- Its own frontmatter carries top-level `requires: - implementation-contract`. **`-mp`'s
  `contracts/` has no `implementation-contract`** — a dangling `requires:` on port, and
  `requires` is one of the five fields ticket 01 found forge-concept actually reads.

**Two things that make it the odd one out.** Its frontmatter is 22 lines against the domain's
34-75, and it carries **no `artifacts:` block at all** — no `requires`/`produces` ids, so it
is invisible to the artifact graph. And it opens with a live TODO:

```
<!-- TODO: This skill currently assumes Starlight/Astro. Refactor to support
     framework-agnostic documentation systems (Docusaurus, VitePress, etc.) -->
```

**Whose repo is it documenting?** The `_sources` examples are
`agent-framework/cli/src/commands/run.ts`, `agent-framework/runner/src/runner.ts`; the path
convention is *"relative path from **monorepo root**"*; it excludes *"AI resource catalog
pages (auto-generated by the ai-resource-loader)"* and *"pages that cover skills/agents/flows"*.
Those are SKAILE's own monorepo, not a scaffolded app. The skill reads as written **for this
repo**, then filed under `impl-build` as if it were for the target project.

**On the collection docs site itself** (context for the fog patch, not this ticket's call):
`generate-skill-pages.mjs` reads only `name`, `description`, `metadata.stage|version|tags`
from each SKILL.md — a read-set ticket 09's prune leaves intact. What breaks it is elsewhere:
it renders a page per `DOMAIN.md` from `slug`/`name`/`description` (**ticket 05 deletes all
16**) and hard-links `skaileup/contracts/asset_frontmatter.md` (**ticket 09 deletes it**).

---

## Open tensions

Sharpest form of each live question. No answers here.

1. **`skaileup-concept-only` runs the whole architecture block and never reaches a build node,
   and every flow that declares a phase puts architecture in `conceptualization` and build in
   `implementation`.** If a nine-domain set is chosen on merit and one domain's boundary is
   already drawn unanimously by the machine contract — is folding `architecture` into `build`
   anything but a headcount saving that then has to be undone in `data.phase` on every node?

2. **Against that: `datamodel` writes `seed.json`, `migrate` reads `model.dbml`, `seed` reads
   `seed.json`, and `scaffold` runs the first migration itself — four skills, one data
   pipeline, cut in half by the domain line.** Is `architecture` a domain, or is `blueprint`
   simply the phase in which the `build` domain's first four skills happen to run?

3. **`PLANS.md`: after removing status (`progress.yaml`) and order (the flow graph), the
   residue is three sites and all three are *scope*** — `scaffold`'s Scope paragraph,
   `concept-brief`'s `## Raw Description`, `ops-add-feature`'s backlog note. Is that a file, or
   is it a section of something that already exists? And note the residue's own weakness: the
   `## Raw Description` section **is not in `contracts/plans.md`'s schema at all**, and ticket
   05 already reclassified user-supplied text as an **answer** bound for `onboarding.yaml`.

4. **Three of the nine PLANS.md "readers" read nothing** — two say *"PLANS.md carries no
   status"* and one says *"owned by a different skill"*. A fourth is the out-of-scope umbrella
   file, and a fifth only tests whether the file exists. Does the count that graduated this
   ticket survive contact with what the nine sites say — and if the surviving reader-count is
   two, does that change the answer or only the confidence?

5. **`impl-build-generate` has zero flow references, and 25% of its body names one vendor.**
   Its `## Codegen` content is already in `template-postxl/TEMPLATE.md:567-595`; what it adds
   is the four-level conflict cascade and the `<<<<<<< Custom` preservation rule. Is that
   cascade a skill, a `references/` file under the PostXL template, or nothing?

6. **`storybook-types` and `generate` share only the word PostXL** — different input
   (`model.json` vs `postxl-schema.json`), different tool (`pxl` vs `pnpm run generate`),
   different artifact (`_concept/prototype/storybook/` vs the app's `src/`). Ticket 06 killed
   one on the grounds of PostXL-only. Is "PostXL-only" the criterion, or is it "no flow ever
   runs it" — because those two rules disagree about which of the pair dies.

7. **`foundation`'s Storybook step gates on `_concept/prototype/storybook/` (the mockup
   project) to theme the app's Storybook (a different project), and every one of its three
   bullets is already performed by `mockup-component-storybook-setup` STEP 4-7 on the mockup
   project.** Ticket 07 moved *scaffolding* to `mockup-storybook`. Does *theming* move too —
   and if it does, is anything left of the step, or does the app-side Storybook turn out to be
   an artifact no skill currently owns?

8. **`templates-select` and `techstack` scan the same directory, read the same Identity
   tables, write the same field, and each hold their own human approval checkpoint.** What
   `templates-select` uniquely adds is ~60 lines: a weighted score, a tier tie-break, an
   existence check, a no-match escape. Is that a skill — when the edge that orders it is
   `type: optional` (so it orders nothing), the node is `optional: true` everywhere it appears,
   two of six consumers pass `templates: skip`, `skaileup-stepwise` omits it, and its own
   `DOMAIN.md` Sequence never mentions it?

9. **`seed` is 8% per-ORM and `migrate` is 3%** — and the ORM branch is a table of file paths,
   not logic. But the asymmetry cuts the other way from the ticket's framing: all 7 templates
   already carry `## Migration / ORM`, and **not one carries a seed section**. Does the residue
   go to `templates/` (where `Migration / ORM` already lives), or does moving 4 and 12 lines
   cost more coordination than it saves?

10. **The ticket says "belongs in `profiles/` at the repo root".** Ticket 05 settled that
    **profile = project type only** and **template = the tech-stack reference**, and `-mp`'s
    `profiles/` is six artifact-path maps with zero stack content. So the destination named in
    the question does not exist. **`-mp` has no `templates/` at all — 3,799 lines across 7
    `TEMPLATE.md` are homeless.** Does this ticket own creating that directory, or does the
    homelessness mean the templates are the *next* ticket and these eleven cannot be sized
    without it?

11. **Every template key `scaffold` and `foundation` MUST-read is absent from every template**
    — `scaffold_command`, `build_command`, `package_manager`, `env_setup_command`,
    `project_structure`, `lint_command`, `type_check_command`, `css_vars_mapping`,
    `auth_setup`, `app_shell`, `seed_format`: zero occurrences in 3,799 lines. The prose is
    there under `## Scaffold Recipe` / `## CSS Variables / Theming` / `## Auth Setup` /
    `## App Shell`; the names are not. Is the port a rewrite of eleven skill bodies, or a
    rewrite of the seven templates into the contract the bodies already assume — and which
    side of that seam does `-mp` want the keys on?

12. **Both `migrate` and `seed` carry `MUST search for prog-expert-*` skills that exist in no
    repo on disk**, and `infrastructure` cites two `references/` files that do not exist.
    Ticket 03's amendment says a hard guardrail survives as *a named failure with a check
    behind it*. What is the check behind a `MUST` whose target was never built?

13. **Seed is written by three skills and migration by two** (`scaffold` STEP 6/7,
    `foundation` Phase 4, plus `migrate`/`seed`) — and `scaffold` runs its migration before
    `migrate` appears in the flow. Is the survivor set decided by what each skill *is*, or by
    who owns the `populated` scenario?

14. **The `architecture` sub-flow's declared order is 3/4 decorative** — two of its three
    edges are `type: optional`, which ticket 15 proved order nothing; the same is true of
    `foundation → infrastructure` in `impl-build-setup`. If the flow graph is the thing that
    replaces `PLANS.md`'s Phases list, does it currently carry the order it is being asked to
    carry — and is fixing those edge types this ticket's job or ticket 10's?

15. **`impl-build-docs` reads as written for *this* monorepo, not for a scaffolded app**
    (`agent-framework/…` source paths, "relative path from monorepo root",
    an `ai-resource-loader` exclusion), it opens with a TODO admitting it hardcodes
    Starlight, it is the only one of the eleven with no `artifacts:` block, and its
    `requires: implementation-contract` points at a contract `-mp` does not have. Is it a
    build skill at all, or the collection's own doc tooling filed in the wrong domain — and
    does the map's open "docs site" patch turn out to be about this skill or only about
    `generate-skill-pages.mjs`?


---

## Post-08 delta — recon pass, 2026-09-05

Everything above predates ticket 08 (resolved 2026-09-05, ADR 0007). This section
was gathered after, against the renumbered tree and the ported skills. Where the two
halves disagree, this one is later. Still evidence only — nothing here is a ruling.

Evidence only. Paths relative to `ai-assets-skaileup/skaileup/` unless noted.

### Per-skill table
| skill | lines | flows (node id) | writes | reads (hard gate) | named by |
|---|---|---|---|---|---|
| `impl-architecture-techstack` | 328 | `architecture`:`techstack` · `appbuilder-mvp`:132 · `skaileup-stepwise`:84 | `_concept/blueprint/techstack.md` | `discovery/brief.md` | no SKILL.md — only `09_impl-architecture/DOMAIN.md`, `contracts/{flows,concept_structure}.md` |
| `impl-architecture-templates-select` | 223 | `architecture`:`templates` (optional, `skip` in 2 of 6 consumers) · `appbuilder-mvp`:144 | same file, `tech_stack_skill` field only | `blueprint/techstack.md` | `05_mockup-walkthrough/01_e_framework/SKILL.md:442`; `templates/README.md` |
| `impl-architecture-system` | 279 | `architecture`:`arch-system` (optional, `skip` in 2 of 6) · `skaileup-concept-reverse`:136 | `blueprint/architecture.md` | `brief.md`, `experience/features`, `techstack.md` | no SKILL.md |
| `impl-architecture-datamodel` | 373 | `architecture`:`datamodel` · `skaileup-concept-reverse`:147 · `skaileup-stepwise`:95 | `datamodel/{model.dbml,model.json,seed.json,feature_map.json}` + feature frontmatter feedback | `experience/features`, `techstack.md` | `04_product-spec/DOMAIN.md` |
| `impl-build-scaffold` | 234 | `impl-build-setup`:`scaffold` · `appbuilder-mvp`:156 · `skaileup-stepwise`:107 | `_implementation/{PLANS.md,progress.yaml,decisions.md}` + project dir + git branch | `techstack.md`, `brief.md`, `model.json` | `contracts/preview_compatibility.md` |
| `impl-build-foundation` | 279 | `impl-build-setup`:`foundation` · `skaileup-stepwise`:118 | `_implementation/progress.yaml`, `_implementation/verification/screenshots/foundation/` (`SKILL.md:224`), theme/auth/shell files | `package.json`, `discovery/brand/tokens.json`, `techstack.md` | `contracts/preview_compatibility.md` |
| `impl-build-infrastructure` | 238 | `impl-build-setup`:`infra-opt` (optional) | `backend/libs/`, `backend/apps/`, `docker-compose.yml`, `.env.example` | `blueprint/architecture.md`, `backend/` | no SKILL.md |
| `impl-build-migrate` | 169 | `impl-build-setup`:`migrate` · `skaileup-stepwise`:129 | `migrations/` (ORM-shaped) | `model.dbml`, `model.json`, `techstack.md` | no SKILL.md |
| `impl-build-seed` | 190 | `impl-build-setup`:`seed` | `scripts/seed` | `seed.json`, `model.json`, `techstack.md`, `migrations` | no SKILL.md |
| `impl-build-generate` | 139 | **zero** | `src/` (generated), `postxl-schema.json` | `postxl-schema.json` (hard) | no SKILL.md |
| `impl-build-docs` | 254 | `impl-build-setup`:`docs` | `docs/src/content/docs/**` | `docs/` | no SKILL.md |

**Zero cross-skill readers.** Grep of every `SKILL.md` in the collection for the eleven `name:` values
returns exactly one hit outside the two clusters: `impl-architecture-templates-select`, cited by
`05_mockup-walkthrough/01_e_framework/SKILL.md:442`. Everything else is `DOMAIN.md` / `contracts/flows.md`
(which ticket 09 deleted, 0 readers). What other domains actually reference is the **`templates/` path**,
never the skill: `06_mockup-component/.../06_orchestrator/SKILL.md:73,112,129,158`,
`05_mockup-walkthrough/01_a_text/SKILL.md:143,166,208`, `01_e_framework/SKILL.md:53,73,410`.

**Reachability.** Neither cluster is wired into a tier flow directly. Both are sub-flows:
`architecture.flow.yaml` (consumed by `appbuilder-{simple,standard,complex,cli}`,
`skaileup-implementation`, `skaileup-concept-only`) and `impl-build-setup.flow.yaml` (consumed by the
same minus `concept-only`). Consumer overrides:
`templates: skip` in `skaileup-implementation:91` and `skaileup-concept-only:259`;
`system: skip` in `appbuilder-simple:186` and `appbuilder-cli:127`.

**Sidecars** (1,292 lines / 48 KB): `validator.py` in 3 of 11 (`techstack` 91, `system` 78, `datamodel` 128 —
none in `10_impl-build/`, none with fixtures); `references/` in the same 3 (52 / 184 / 223 lines);
`CLI.md` ×4; two `DOMAIN.md`; `10_impl-build/contracts/` (`implementation-contract/CONTRACT.md` 104 —
`requires:` of `impl-build-docs`; `subagent_dispatch.md` 117 — absorbed by `agent_patterns.md` per ticket 09);
`10_impl-build/agents/skaileup-implement/` (99 lines, `-mp` has no `agents/`).

### templates/ inventory

**`templates/` is 3,799 lines / 134 KB of `TEMPLATE.md` + a 34-line README — larger than all eleven
skills combined (2,706 lines / 121 KB).** Seven directories, each containing exactly one file.

| template | lines | frontend / ui / data |
|---|---|---|
| `template-sveltekit-minimal` | 722 | SvelteKit 2 / none / Drizzle+SQLite |
| `template-postxl` | 665 | React 19+Vite / custom / NestJS+Prisma+PG |
| `template-nextjs-shadcn` | 556 | Next.js 15 / shadcn/ui / Supabase |
| `template-nuxt-minimal` | 507 | Nuxt 4 / none / Drizzle+SQLite |
| `template-nextjs-radix` | 486 | Next.js 15 / Radix / Directus |
| `template-nuxt-primevue` | 441 | Nuxt 4 / PrimeVue 4 / Directus |
| `template-nuxt-ui` | 422 | Nuxt 4 / @nuxt/ui v3 / Directus |

All seven are **real, not stubs**, and structurally identical: `Identity` · `When to Use` ·
`Scaffold Recipe` · `Preview Compatibility` · `CSS Variables / Theming` · `Auth Setup` · `App Shell` ·
`Component Library` · `Mock Adaptation` · `Storybook Config` · `Migration / ORM` · `Codegen` ·
`Expert Skills` · `Key Implementation Patterns`.

**No template carries a `validator.py` or a fixture** — each dir is one file (`find templates -type f`
= 8). The three `validator.py` files in this half sit on `techstack`/`system`/`datamodel`.

**The skill↔template key contract is broken in both directions.** Literal-key grep across all seven:

- `scaffold_command` **0/7** — read by `01_scaffold/SKILL.md:144,166`
- `css_vars_mapping` **0/7** — read by `02_foundation/SKILL.md:120,158,258,269,270`
- `seed_format` **0/7** — read by `02_foundation/SKILL.md:210,261`
- `story_extension` · `component_library` · `icon_library` **0/7** — read by the storybook orchestrator (ticket 14's find, confirmed)
- `storybook_addon` · `story_format` · `mock_template` **1/7 each** (mentions only, inside prose)

The information exists as prose sections (`## Scaffold Recipe`, `## CSS Variables / Theming`,
`## Component Library`), but no skill's extraction instruction names a section — they all name a key
that does not exist.

**`contracts/preview_compatibility.md` (292 lines) has exactly 7 readers, all here:**
`templates/template-*/TEMPLATE.md` `## Preview Compatibility` (radix:126, nuxt-min:122, primevue:128,
nuxt-ui:107, shadcn:136, sveltekit:225, postxl:175). Those sections are 22–74 lines each.

**`prog-expert-*` resolves outside this repo.** Every template's `## Expert Skills` section names
`prog-expert-{nextjs,nuxt,directus,prisma,nestjs,keycloak,supabase,primevue,sveltekit}`; so does
`04_migrate/SKILL.md:112-114`. They live in `ai-assets/ai-assets/dev-implementation-experts-*/skills/`,
a different collection — nothing in `skaile.yaml` here declares that dependency.

### templates-select vs techstack — the seam

`techstack` already picks a template. `SKILL.md:171` "Scan 09_impl-architecture/templates/\*/TEMPLATE.md";
`:205` "select the best matching profile"; `:249` writes `tech_stack_skill: <profile-id>`; and its own
checklist `:298` requires **"tech_stack_skill field is set (matches a 09_impl-architecture/templates/
directory or 'custom')"**.

`templates-select` then opens with the skip:

> `02_templates-select/SKILL.md:114-117` — "IF `tech_stack_skill` already names an existing
> `template-*` directory / > 'techstack.md already targets [id]. Re-pick the scaffold template?'
> / UNLESS the user wants to re-pick, skip to STEP 5 (no change)"

Its `## When NOT to Use` (`:63-66`) repeats this: "`tech_stack_skill` already names a real `template-*`
directory and is approved". Its only distinct content is the weighted score (frontend ×3, ui ×2,
backend/database ×1 each, `:143-146`) and a tier tie-break — a rubric `techstack` STEP 4 performs
by narrative instead. Both scan the same directory; `templates-select` additionally hardcodes the
seven ids in a table (`:129-137`) after a MUST forbidding exactly that (`:102`).

Two of six sub-flow consumers already pass `templates: skip`.

### Boilerplate vs instruction

Region measurement (frontmatter / preamble prose / DSL header block / STEP body / CHECKLIST / tail sections):

| skill | total | frontmatter | preamble | DSL hdr | STEP body | tail |
|---|---|---|---|---|---|---|
| techstack | 329 | 75 | 57 | 27 | 134 | 36 |
| templates-select | 224 | 41 | 44 | 25 | 78 | 36 |
| system | 280 | 66 | 61 | 29 | 84 | 40 |
| datamodel | 374 | 75 | 65 | 40 | 146 | 48 |
| scaffold | 235 | 55 | 48 | 34 | 68 | 30 |
| foundation | 280 | 59 | 56 | 38 | 84 | 43 |
| infrastructure | 239 | 49 | 42 | 35 | 100 | 13 |
| generate | 140 | 34 | 27 | 24 | 45 | 10 |

Genuine step instruction is **~40%** of each file; the rest is ticket 03's ten sections plus the
`ROLE/READS/WRITES/REFERENCES/MUST/NEVER/EMIT` block that ticket 03 already showed restates frontmatter.
`04_migrate` (169) and `05_seed` (190) use a different shape (no `STEP 1` marker, 129/146-line tails).

Fattest single blocks, all removable:

- `04_datamodel/SKILL.md:134-178` — `## Standalone Mode` **45 lines**, of which 40 are the DSL block.
  Same section is 34 lines in `03_system/SKILL.md:121-154`.
- `04_datamodel/SKILL.md:249-276` — `OUTPUT model.json` **28 lines** of JSON shape, duplicated by
  `04_datamodel/references/model_conventions.md` (223 lines, "DBML + model.json template" per `:167`).
- `03_system/references/output_template.md` — 184 lines that `03_system/SKILL.md:209-220` restates in 12.
- `04_migrate/SKILL.md:97-104` — STEP 5 fans out per ORM ("For Prisma… For Drizzle… For Directus…
  For raw SQL"). Every `TEMPLATE.md` already carries a `## Migration / ORM` section
  (postxl:505, shadcn:412, radix:373, nuxt-min:393, primevue:349, nuxt-ui:346, sveltekit:579).
- `02_foundation/SKILL.md:155-215` — five `Phase N` blocks each opening "Read <key> from tech stack
  profile", where the key does not exist in any profile.
- `06_generate` — its whole STEP 3/5 is the `## Codegen` section of `template-postxl/TEMPLATE.md:567-595`.
- `03_infrastructure/SKILL.md` writes `backend/libs/<module>/src/`, `backend/apps/<process>/src/` —
  the PostXL/NestJS monorepo layout, in a skill with no stack branch.

Two dead reads inside the bodies: `04_datamodel/SKILL.md:150` reads
`_concept/experience/behaviors/*.allium` (ticket 08 killed `.allium`), and
`02_foundation/SKILL.md:219` gates on `_concept/prototype/storybook/`, which ADR 0007 relocates to
`09_mockup/storybook/`.

### Homes in the ADR 0007 tree

Against `ai-assets-skaileup-mp/contracts/concept_structure.md` (commit `609ee67`).

| current output | ADR 0007 home |
|---|---|
| `blueprint/techstack.md` | `10_blueprint/techstack.md` |
| `blueprint/architecture.md` | `10_blueprint/architecture.md` |
| `blueprint/datamodel/*` | `10_blueprint/datamodel/` |
| `_implementation/decisions.md` | `11_build/decisions.md` |
| project code, `migrations/`, `scripts/seed`, `backend/libs`, `docker-compose.yml`, `.env.example`, `src/`, `docs/` | outside the artifact tree — unaffected |
| **`_implementation/PLANS.md`** | **none** |
| **`_implementation/progress.yaml`** (project-level) | **none** — `11_build/` holds only `slices/<slice_id>/` and `decisions.md`, and ticket 07 has `impl-slice-commit` delete the per-slice `progress.yaml` as transient |
| **`_implementation/verification/screenshots/foundation/`** (`02_foundation/SKILL.md:224`) | **none** |

Unclaimed in the other direction: `10_blueprint/glossary.md` and `10_blueprint/decisions.md` exist in
the tree and **none of the eleven writes either**; no ported `-mp` skill does either (`-mp/skills/` is
the four mockup skills).

#### `PLANS.md` — every writer and reader

Writers (2): `10_impl-build/01_scaffold/SKILL.md:49,198` (creates it) ·
`00_skaileup-orchestrator/skills/skaileup-build/SKILL.md:56,215` (writes `_implementation/PLANS.md`) —
plus `skills/skaileup/SKILL.md:29,141` writing `_concept/PLANS.md`.

Readers naming it at a step: `01_scaffold:116,122,234` · `02_foundation:228` · `03_infrastructure:238` ·
`11_impl-plan/03_plan-vertical:163,189` · `12_impl-slice/01_git-prepare:79,110` ·
`13_impl-quality/07_ready/references/report_templates.md:58` · `14_ops/08_review:100,118,200` +
`references/checks.md:116` + `references/gardening.md:18,26` · `14_ops/10_add-feature:273` ·
`14_ops/04_project-review:44,84,86` · `01_concept/01_brief:170` (reads a `## Raw Description` section
out of it) · both orchestrator skills · both `agents/*/SOUL.md`.

Contract + registry: `contracts/plans.md` (86 lines, deleted by ticket 09/07) ·
`contracts/artifacts.yaml:251` (unreachable) ·
`10_impl-build/contracts/implementation-contract/CONTRACT.md:35,80` ·
`01_concept/.../conceptualization-contract/CONTRACT.md:35,83-85` ·
`14_ops/contracts/CONTRACT.md:68,191,219,247,297-314` (out of scope per ticket 09).

Three of the four remaining in-cluster mentions say PLANS.md holds **no status**:
`01_scaffold:198` "NO checkboxes; status lives in progress.yaml", `02_foundation:228`, `03_infrastructure:238`.
Two orchestrator readers say the opposite — `skaileup/SKILL.md:113` "MUST update PLANS.md at every
checkpoint", `:232` "check the feature off in PLANS.md". Both orchestrators die with ticket 07.

### Open questions for the human

1. **The mass is in `templates/`, not the skills.** 3,799 lines vs 2,706. Ticket 09 hoisted `profiles/`
   to the repo root; `-mp` already has `profiles/`. Do the seven templates become `profiles/`, and if so
   is a 500-line stack profile acceptable when the *skill* ceiling is 140?
2. **The skill↔template contract is broken for every key any skill extracts.** Fix by giving templates
   frontmatter keys, or by rewriting the skills to read named sections? One is a 7-file edit, the other
   is 4+ skill edits — and ticket 14 already chose "derive instead of ask" for the storybook three.
3. **Does `templates-select` survive its own skip condition?** `techstack` writes a real `template-*` id
   and `templates-select` no-ops when it did. Is this a skill, or `techstack` STEP 4 with a score table?
4. **`preview_compatibility.md` (292 lines) is claimed by this ticket or lost.** Its seven readers are
   template sections. Does it fold into each template (7× duplication) or survive as a root contract?
5. **`PLANS.md`.** Every surviving in-cluster reader says it carries no status; every reader that treated
   it as status is an orchestrator ticket 07 deletes. Does the artifact survive at all, and if it does,
   where — `11_build/` has no slot, and `progress.yaml` and the flow graph cover status and order.
6. **`generate` (139, zero flows, PostXL-only).** Its steps are `template-postxl/TEMPLATE.md:567-595`
   plus a four-level conflict cascade. Ticket 06 killed `storybook-types` (also PostXL codegen) rather
   than sending it here. Does codegen become a template section + a `build-implement` step, or die?
7. **Does `architecture` stay a domain?** Four skills that write only `10_blueprint/` before any code —
   but `techstack`'s output is read by `scaffold`, `foundation`, and three mockup skills, so the seam is
   the artifact, not the domain.
8. **`docs` overlaps the fog patch.** `10_impl-build/07_docs` documents the *generated app* with
   Starlight, carries a `<!-- TODO -->` at `SKILL.md:26-28` admitting the Starlight lock-in, reads
   `docs/astro.config.mjs` and paths "relative from monorepo root" — i.e. it was written against **this
   repo's own** Starlight site (`docs/package.json`: `@astrojs/starlight ^0.37.7`,
   `scripts/generate-skill-pages.mjs`), which the map's "docs site" fog patch is separately deciding.
   Same skill, two sites. Not resolved here.
9. **`10_impl-build/agents/` + `contracts/`.** `-mp` has no `agents/`; `subagent_dispatch.md` was
   absorbed into `agent_patterns.md`; `implementation-contract` (104) is `requires:` of `impl-build-docs`
   and describes the `_implementation/` tree ADR 0007 replaces.
10. **`prog-expert-*` is a cross-collection dependency nothing declares.** Every template's
    `## Expert Skills` and `04_migrate` STEP 4 point at `ai-assets/dev-implementation-experts-*`.
    Does `-mp` declare it, drop the sections, or keep a dangling reference?
