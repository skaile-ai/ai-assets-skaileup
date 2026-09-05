# 25: Port architecture + build — write the 5 skills

**Type:** task
**Blocked by:** None — 24 resolved 2026-09-05 (18 resolved)
**Status:** resolved

## Question

Nothing to decide — ticket 18 settled the survivor set, ADR 0009 and ADR 0010 record the two
rules behind it. This writes the skills. Same relation 14 has to 06 and 19 has to 07.

**Eleven skills / 2,706 lines → five**, each `SKILL.md` under the 140-line ceiling (ticket 03),
dir name == `name:` exactly (ticket 04), no `MUST`/`NEVER` block, `data.phase` declared by the
flows and not by the name.

### `architecture/` — 3 skills

- **`architecture-techstack`** — reads `_concept/brief.md` + `05_features/`, scans
  `templates/*/TEMPLATE.md` Identity tables at runtime (never hardcode the ids), writes
  `10_blueprint/techstack.md` including `tech_stack_skill`. **Absorbs `templates-select`'s ~60
  lines of real content**: the weighted score (frontend ×3, ui ×2, backend ×1, database ×1), the
  tier tie-break from `01_meta/scope.yaml` (mvp/simple → `*-minimal`, standard/complex → the
  fuller UI-library template), the `test -d templates/<id>` existence check, and the `custom`
  no-match escape ("never map Svelte onto a Next template"). One skill, one field, **one**
  human approval checkpoint — today there are two over the same field.
- **`architecture-system`** — writes `10_blueprint/architecture.md`, **shrunk to what the
  project adds beyond the template's defaults**: custom modules, protocols, external
  integrations, which is exactly the frontmatter it already emits. Do **not** port "baseline
  every section with what the chosen stack provides out of the box" — that is the template's job
  under ADR 0009. Drop `references/output_template.md` (184 lines the body restates in 12) and
  the 34-line Standalone Mode block.
- **`architecture-datamodel`** — writes `10_blueprint/datamodel/{model.dbml,model.json,seed.json,feature_map.json}`
  plus the feedback loop into feature `data_entities[]`. **New: it also writes
  `10_blueprint/glossary.md`** — entity and field names with their one-line meanings, derived
  from `model.json`. ADR 0007 puts that file in the tree and nothing wrote it; `datamodel` is the
  only skill holding the whole vocabulary at once. Drop the 45-line Standalone Mode block and the
  28-line `OUTPUT model.json` shape (duplicated by `references/model_conventions.md`).
  Its read of `06_behaviors/*.allium` is dead — ticket 08 killed `.allium`.

### `build/` — 2 one-time skills, beside ticket 19's four

- **`build-scaffold`** (`scaffold` + `foundation`) — nothing to a themed, authed, shelled app:
  scaffold command, git branch, then walk the template's named sections in order
  (`## Scaffold Recipe` → `## CSS Variables / Theming` → `## Auth Setup` → `## App Shell`).
  ticket 02's mechanism: the recipe lives in the template, the skill is order plus checkpoints.
  **Writes no `PLANS.md`, no `progress.yaml`, no `decisions.md`** (ADR 0010 — the first two die;
  `11_build/decisions.md` already has its writer from ticket 13). **Runs no migration and no
  seed** — that triple-write is what `build-database` exists to end. **No Storybook step at all**
  (ADR 0009: the built app gets no Storybook from this collection).
- **`build-database`** (`migrate` + `seed`) — one pass over `10_blueprint/datamodel/`: schema
  then seed. Keep the stack-neutral substance, which is 97% of `migrate` and 92% of `seed` —
  `model.dbml` ↔ `model.json` cross-check, the `semantic_types.md` translation table, UUID PKs,
  `created_at`/`updated_at`, `on_delete` defaulting to SET NULL, a junction table per m2m,
  snake_case columns, the insert-order dependency graph (parents before children, reversed for
  cleanup), one entry point taking a scenario argument, and both 6-point validations (IDs
  preserved, FKs resolve, enums match `model.json`, required fields present, **empty actively
  clears**, edge_cases carries specials). **Drop both per-ORM branch tables** — migration's four
  lines are already `## Migration / ORM`, seed's twelve are ticket 24's new `## Seed` section.
  Drop the `MUST search for prog-expert-*` (ticket 24 softens it in the templates).

### Dying — confirm nothing of substance is left behind

`impl-architecture-templates-select` (folded) · `impl-build-foundation` (folded) ·
`impl-build-migrate` + `impl-build-seed` (folded) · **`impl-build-infrastructure`** ·
**`impl-build-generate`** · **`impl-build-docs`**, and with the last of those
`contracts/doc_tracking.md` (225 lines, which ticket 09 had routed *into* `build-docs`).

Also not porting: the three `validator.py` (91/78/128) and three `references/` (52/184/223)
unless a step genuinely needs them; four `CLI.md`; both `DOMAIN.md` (ticket 05 kills all 16);
`10_impl-build/agents/skaileup-implement/` (no `agents/` in `-mp`);
`10_impl-build/contracts/implementation-contract/CONTRACT.md` (104 — it describes the
`_implementation/` tree ADR 0007 replaced, and it is the dangling `requires:` of the dying
`build-docs`); `contracts/subagent_dispatch.md` (ticket 09 absorbed it into `agent_patterns.md`).

### Also in scope

- **Write against ADR 0007's tree, not the old paths.** Ticket 19 hit this: `10_blueprint/`, not
  `blueprint/`; `11_build/`, not `_implementation/`. Cite `contracts/concept_structure.md` for
  paths and the other contracts for shape.
- **Extract atoms by name from template frontmatter; cite recipe sections by heading.** Never
  invent either (ADR 0009). If a needed atom is missing, that is a defect in ticket 24's list,
  not a prompt to ask the user.
- Record final line counts per skill and anything that had to differ from ticket 18's shape.

### Notes

Blocked by ticket 24 strictly: these five extract atoms that do not exist until the templates
carry them. Porting in the other order reproduces the defect ticket 18 found — `foundation`'s
*"if any section is missing from the profile, ask the user for guidance"* branch firing on every
run because all eleven keys were 0/7.

`infrastructure` cites `references/layer_patterns.md` and `references/dependency_mapping.md`,
**neither of which exists on disk** — nothing to carry across even if it had survived.

## Note from ticket 10

Three constraints from the flow graphs, one of them a defect this ticket must fix rather than
port.

- **`build-scaffold`'s brand gate becomes conditional.** `impl-build-foundation:95-98` lists
  `03_brand/tokens.json` under *"Hard gates (all must exist)"*, and this ticket merges
  `foundation` into `build-scaffold`. **`appbuilder-mvp` has no `design-brand` node**, so the
  merged skill would hard-refuse in that flow on every run. Apply tokens if
  `03_brand/tokens.json` exists, else stack defaults — ticket 03's rule (constraint stated at
  the step, check behind it) rather than frontmatter that blocks a whole flow. This is the same
  class of defect as the template branch this ticket already found firing on every run.
- **`appbuilder-mvp` has no data layer** — no `architecture-datamodel`, no `build-database`.
  Deliberate: `build-scaffold`'s template supplies the ORM default and the schema grows inside
  `build-implement`. So **`build-database` must not be a precondition of anything in `mvp`**,
  and `build-implement` cannot hard-gate on a migration having run.
- **`architecture-techstack` reads `project_type` from `onboarding.yaml`**, and
  `concept-scope` resolves it against root-level `profiles/<project_type>.yaml` — which is how
  ticket 18's relocated `profiles/` finally gets a reader, and where `cli` landed after ticket
  10 deleted the `appbuilder-cli` flow. `templates-select` stays folded in, as this ticket ruled.
- **Node placement**: `architecture-{techstack,system,datamodel}` are phase
  `conceptualization`; `build-{scaffold,database,plan,implement,branch}` are `implementation`.
  `mvp` runs `architecture-techstack` and `build-{scaffold,plan,implement}` only.

## Answer

**11 skills / 2,706 lines → 5 skills / 422 lines of `SKILL.md`**, all in `-mp` `skills/`, all
under the 140-line ceiling, dir name == `name:`, no `MUST`/`NEVER` block, no `parameters:`,
no `data.phase`, no `references/`. `scripts/check.py`: 29 skills, 0 errors.

| skill | lines | absorbed |
|---|---|---|
| `architecture-techstack` | 87 | `01_techstack` (328) + `02_templates-select` (223) |
| `architecture-system` | 74 | `03_system` (279) |
| `architecture-datamodel` | 90 | `04_datamodel` (373) |
| `build-scaffold` | 90 | `01_scaffold` (234) + `02_foundation` (279) |
| `build-database` | 81 | `04_migrate` (169) + `05_seed` (190) |

**Atoms named, all sixteen respected**: `scaffold_command`, `package_manager`,
`project_structure`, `build_command`, `lint_command`, `type_check_command`,
`env_setup_command` (`build-scaffold`) and `seed_format` (`build-database`). Nothing outside
ticket 24's list was needed. Every `null` is taken as a branch and stated as one:
`env_setup_command: null` → the env contents are `## Scaffold Recipe` material;
`lint_command: null` → one fewer verification command. **Sections cited by heading only**:
`## Identity`, `## When to Use`, `## Scaffold Recipe`, `## CSS Variables / Theming`,
`## Auth Setup`, `## App Shell`, `## Migration / ORM`, `## Seed`, `## Storybook Config`.
No template id appears in any of the five — `architecture-techstack` scans
`templates/*/TEMPLATE.md` at runtime.

### Deviations from ticket 18's shape

1. **`tier` is dead, so the tie-break is stated in flow names.** `templates-select`'s tier
   tie-break becomes: `appbuilder-mvp` → the lighter `*-minimal`; `appbuilder-standard`,
   `skaileup-concept-only`, `skaileup-concept-reverse` → the fuller UI-library template
   (ticket 10 retired `tier`; `scope.yaml` carries `flow`).
2. **`project_type` is read from `01_meta/scope.yaml`, not `onboarding.yaml`.** The note from
   ticket 10 predates the landed `concept-scope`, which writes `project_type` into
   `scope.yaml` and itself says *"`architecture-techstack` and `build-scaffold` both branch on
   this value."* `onboarding.yaml` stays as the fallback when scope has not been written.
3. **The glossary is reconciled, not authored.** `contracts/domain_model.md` says the glossary
   is built lazily and inline, *"no skill produces these in a dedicated write-the-glossary
   pass"*, carries **zero implementation detail**, and is updated in place — and
   `spec-feature` already appends to it. So `architecture-datamodel` writes an entry per
   **model name and enum vocabulary** (not per field, which would be the implementation detail
   the contract excludes), leaves existing entries alone, and **renames the model to match the
   glossary** where the two disagree, since the specs and screens are already on the
   glossary's word. This still gives `10_blueprint/glossary.md` the writer ADR 0007 left it
   without, in the form the contract allows.
4. **`feature-map.json`, hyphenated.** `contracts/concept_structure.md` names it that way and
   its naming rule requires it; `contracts/artifact_frontmatter.md` still says
   `feature_map.json` (see defects below).
5. **`build-scaffold` cuts the branch only when nothing else did.** Ticket 25 says "scaffold
   command, git branch", but ticket 19's `build-branch` owns `build/<app-slug>` and
   `appbuilder-mvp` has no `build-branch` node. So: find the branch and commit onto it; create
   it (and `git init`) only when absent. Same class of fix as the brand gate — the fallback is
   named at the step rather than left to a second writer.
6. **One commit per section.** `foundation` committed per sub-phase; `build-scaffold` keeps
   that (scaffold, then theme / auth / shell) so a bisect can separate them.

### The defect ticket 10 named — fixed, not ported

`build-scaffold` step 5: `03_brand/tokens.json` present → every value traces to a token, light
and dark where both exist, atmosphere from `identity.md`. Absent → the stack's own defaults
from `## CSS Variables / Theming`, **named to the user** with how to replace them. The step
states why both halves exist: refusing would make every `appbuilder-mvp` run fail, inventing
hex values would make the app disagree with a brand it is meant to wear. `tokens.json` is a
`soft` gate in frontmatter and the step carries the branch, per ADR 0008.

### Dying — swept, nothing of substance stranded

- **`templates-select`** — score, tie-break, `test -d`, `custom` escape and *"never map Svelte
  onto a Next template"* all in `architecture-techstack`. Deliberately dropped: its hardcoded
  seven-row candidate table (the thing ADR 0009 forbids) and the second checkpoint.
- **`foundation`** — brand / auth / shell / verify in `build-scaffold`. Dropped by ruling:
  Storybook phase (ADR 0009), seed phase (→ `build-database`), `progress.yaml` update
  (ADR 0010), `_implementation/verification/screenshots/` (no ADR 0007 home), and the
  *"ask the user if the profile is missing a section"* branch (the defect ticket 24 removed).
- **`migrate` + `seed`** — dbml↔json cross-check, semantic translation, `standard_fields`
  expansion (UUID PK + `created_at`/`updated_at`), snake_case columns, `on_delete` default
  SET NULL, junction per m2m, the insert-order graph and its reverse, one entry point taking a
  scenario argument, and both 6-point validations, all in `build-database`. Per-ORM tables
  gone (now `## Migration / ORM` and `## Seed`); `prog-expert-*` softened to *if installed,
  consult it — nothing waits on one*.
- **`infrastructure`** — dies. Its one stack-neutral idea, the **provider seam** (interface +
  real + in-memory stand-in, chosen by config, so a slice builds before credentials exist),
  lands as `architecture-system` step 5. Its bottom-up five-layer order is **deliberately not
  carried**: `build-plan` already rules layer-first decomposition out, so porting it would
  contradict a landed sibling. Its two `references/` never existed on disk.
- **`generate`** — verified absorbed into `template-postxl` `## Codegen` (TEMPLATE.md:613).
- **`docs`** + `contracts/doc_tracking.md` — verified repo tooling: `agent-framework/…` source
  paths, `docs/src/content/docs/**`, an `ai-resource-loader` exclusion, `_sources` frontmatter
  for a Starlight site, and a consuming-skills table naming `skaildev-doc`. Nothing
  project-facing to strand.
- **The three `references/` were not needed.** `model_conventions.md` is covered by
  `contracts/semantic_types.md` (§ Model Metadata, § Field Properties, § Relation Types,
  § Rules for Skills); `output_template.md`'s six sections collapse to
  `architecture-system` step 6; `integration_categories.md` is one clause of
  `architecture-techstack` step 8. No `references/` directory was created for any of the five.

### For ticket 28 (the flow YAMLs)

- All five node skills exist at `skills/<name>/`. Phases: `architecture-*` →
  `conceptualization`, `build-*` → `implementation`.
- **`appbuilder-mvp` runs `architecture-techstack` and `build-{scaffold,plan,implement}` only.**
  `build-database` is a precondition of nothing there, and `build-scaffold` runs with no brand
  node and no `build-branch` node — both branches are in the skill.
- `architecture-system` and `architecture-datamodel` both hard-gate `05_features/`, so they sit
  after the `spec-feature` loop. `architecture-techstack` gates only `brief.md`, so it can run
  earlier; its `05_features/` read is soft.
- `build-scaffold` hard-gates `10_blueprint/techstack.md` — `architecture-techstack` precedes it
  in every flow that reaches build.
- Edge order inside `architecture`: techstack → system → datamodel (system reads the template
  for the delta; datamodel reads `architecture.md` when it exists, softly).

### Defects found, not patched (read-only on `templates/`, and out of ticket scope)

1. `contracts/artifact_frontmatter.md § blueprint/techstack.md` **does not list
   `tech_stack_skill`** — the one field the whole template mechanism turns on. It is documented
   only in `templates/README.md`. → ticket 16.
2. Same file: heading is `feature_map.json`, `concept_structure.md` says `feature-map.json`,
   and its own naming rule requires the hyphen. Its blueprint headings are also pre-0007
   (`blueprint/…` not `10_blueprint/…`). → ticket 16.
3. `contracts/seed_data.md` line 3 still cites `_concept/blueprint/datamodel/seed.json`. → 16.
4. `skills/mockup-storybook` (ticket 14, written before the templates landed) still **derives**
   `story_extension`, `component_library` and `icon_library` — all three now exist as atoms,
   7/7 — and it points at **`build-foundation`**, a skill this ticket's merge means will never
   exist. Two-line fix, but it belongs to whoever owns 14/16, not here.

