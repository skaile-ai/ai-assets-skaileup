# 25: Port architecture + build — write the 5 skills

**Type:** task
**Blocked by:** 24 (18 resolved)
**Status:** blocked

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
