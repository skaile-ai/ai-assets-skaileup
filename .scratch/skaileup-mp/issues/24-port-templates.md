# 24: Port the templates — 7 × TEMPLATE.md into `templates/`

**Type:** task
**Blocked by:** None (18 resolved)
**Status:** resolved

## Question

Nothing to decide — ticket 18 settled the shape and ADR 0009 records it. This writes it. Same
relation 14 has to 06 and 19 has to 07.

**`-mp` has no `templates/` directory at all**, and the seven `TEMPLATE.md` are **3,799 lines /
134 KB — larger than all eleven architecture+build skills combined** (2,706). They are the
single largest homeless asset left in the migration.

Create `templates/` at the repo root — sibling to `skills/` · `flows/` · `contracts/` ·
`profiles/` — one directory per template, **directory name == template id** (ticket 04's rule
applied to a second asset kind), one `TEMPLATE.md` each. **No line ceiling**: ticket 03's 140
governs instruction an agent follows top to bottom; a template is reference data an agent loads
one section of.

| template | lines | frontend / ui / data |
|---|---|---|
| `template-sveltekit-minimal` | 722 | SvelteKit 2 / none / Drizzle+SQLite |
| `template-postxl` | 665 | React 19+Vite / custom / NestJS+Prisma+PG |
| `template-nextjs-shadcn` | 556 | Next.js 15 / shadcn/ui / Supabase |
| `template-nuxt-minimal` | 507 | Nuxt 4 / none / Drizzle+SQLite |
| `template-nextjs-radix` | 486 | Next.js 15 / Radix / Directus |
| `template-nuxt-primevue` | 441 | Nuxt 4 / PrimeVue 4 / Directus |
| `template-nuxt-ui` | 422 | Nuxt 4 / @nuxt/ui v3 / Directus |

All seven are real, not stubs, and structurally identical — 15 shared headings.

### In scope

1. **Add the frontmatter atom block to all seven.** ADR 0009's typed seam: **atoms** are one
   value each, extracted by name; **recipes** stay named sections cited by heading. Every atom a
   skill extracts is currently **0/7** across 3,799 lines — `scaffold_command`, `build_command`,
   `package_manager`, `env_setup_command`, `project_structure`, `lint_command`,
   `type_check_command`, `seed_format`, plus ticket 14's `story_extension`, `component_library`,
   `icon_library`. The values exist as prose under `## Scaffold Recipe` etc.; lift them.
   `storybook_addon` / `story_format` / `component_import` / `setup_file` / `mock_template`
   exist today only as prose mentions (1/7 each) — regularise them into the same block.
2. **Add a `## Seed` section to all seven.** `grep -i seed` across the templates returns
   nothing today. `impl-build-seed`'s twelve per-ORM lines (`prisma/seed.ts` + `prisma/seeds/`,
   `src/db/seed.ts` + `src/db/seeds/`, `seeds/<scenario>.sql`) are the **only** place that
   layout is written down — losing them loses it. `## Migration / ORM` already exists in all
   seven and needs no equivalent work.
3. **Absorb `impl-build-generate` into `template-postxl`'s `## Codegen`.** That section
   (`:567-595`) already carries when to run `pnpm run generate`, why `postxl-schema.json` is the
   source of truth, the five generated output locations and the `pnpm prisma generate` pairing.
   What the dead skill adds and must not be lost: the **four-level conflict cascade**
   (auto-overwrite generated-only / preserve `<<<<<<< Custom` blocks /
   `pnpm run generate --diff` on ejected files / escalate) and the custom-block preservation
   rule.
4. **Soften `## Expert Skills` in all seven.** The nine `prog-expert-*` skills live in
   `ai-assets/dev-implementation-experts-*`, a different collection, and **`skaile.yaml` has no
   dependency mechanism** — no `assets:` block by design, glob discovery only. Rewrite as *"if
   `prog-expert-<x>` is installed, consult it"*: optional, no gate, nothing declared.
5. **Port `contracts/preview_compatibility.md` (292 lines) as `templates/preview_compatibility.md`.**
   Its seven readers are the templates' own `## Preview Compatibility` sections (22–74 lines
   each) — reference data, not skills, so it fails ticket 09's contracts bar while being
   genuinely needed. Each template keeps its short framework-specific section and points at the
   shared file for the proxy rules. **Also fix `-mp`'s `contracts/README.md`**, which still
   carries a row for ticket 09's `preview_compatibility → walkthrough_renderer` fold-in — a fold
   ticket 14 proved wrong and that never happened.
6. **Rewrite `templates/README.md` (34 lines), which is stale against its own templates** — it
   calls `template-postxl` "FastAPI + Vue + PostgreSQL" (the TEMPLATE and `templates-select`'s
   own table both say React 19 + Vite / NestJS + Prisma + PG) and says "Nuxt 3" where three
   templates say Nuxt 4. State the atoms/recipes contract and the dir-name-is-the-id rule here.
7. **Record the atom set** so ticket 25 can write against it and ticket 16 can check it: one
   list, every template declares all of it, a value or an explicit `null`.

### Out of scope

- Writing the five skills — ticket 25, which is blocked by this one.
- Adding an eighth template or dropping any of the seven. ADR 0009 makes an unsupported stack a
  gap in `templates/`, but which stacks are supported is not this ticket's call.
- Ticket 16's validator itself; this ticket only fixes the data it will check.

### Notes

**The order matters and is the reason this is a separate ticket.** Ticket 25's skills extract
atoms by name. Porting the skills first would have them read keys that do not exist — the exact
defect ticket 18 found, where `foundation`'s *"if any section is missing from the profile, ask
the user"* branch fired on every run.

`profiles/` (six project types at the repo root) is a **different thing** and is untouched here
— ticket 05: profile = project type, template = tech-stack reference. Its pre-0007 stale paths
belong to ticket 16.

## Answer

**Written in `ai-assets-skaileup-mp`, working tree left dirty for the orchestrator.**
`templates/` now exists at the repo root beside `skills/` · `flows/` · `contracts/` ·
`profiles/`: seven `template-<id>/TEMPLATE.md`, `preview_compatibility.md`, and `README.md`.
Directory name == template id == frontmatter `name:`, 7/7. `scripts/check.py` green
(22 skills, 0 errors); `scripts/test_check.py` 31 passed.

### The atom set — sixteen keys, contract for ticket 25

Atoms live in **`metadata.atoms`** in each `TEMPLATE.md` frontmatter. **Every template declares
every key** — a value, or an explicit `null`. There is no third state; an absent key is the
defect this ticket exists to remove, because a reader cannot distinguish "this stack has none"
from "nobody wrote it down". Verified 7/7 by literal grep and by a YAML parse of all seven.

| atom | postxl | shadcn | radix | nuxt-ui | primevue | nuxt-min | sk-min |
|---|---|---|---|---|---|---|---|
| `scaffold_command` | `postxl scaffold new <app-name>` | `create-next-app` | `create-next-app` | `nuxi init` | `nuxi init` | `nuxi init` | `sv create` |
| `package_manager` | pnpm | pnpm | pnpm | bun | bun | bun | bun |
| `build_command` | `pnpm run build` | `pnpm build` | `pnpm build` | `bun run build` | `bun run build` | `bun run build` | `bun run build` |
| `env_setup_command` | null | null | null | null | null | null | null |
| `project_structure` | value | value | value | value | value | value | value |
| `lint_command` | `pnpm run lint` | `pnpm lint` | `pnpm lint` | null | null | null | null |
| `type_check_command` | `pnpm run test:types` | `tsc --noEmit` | `tsc --noEmit` | `nuxi typecheck` | `nuxi typecheck` | `nuxi typecheck` | `bun run check` |
| `seed_format` | prisma | sql | sql | sql | sql | drizzle | drizzle |
| `storybook_addon` | `@storybook/react` | `@storybook/nextjs` | `@storybook/nextjs` | `@storybook/nuxt` | `@storybook/vue3` | `@storybook/vue3` | `@storybook/svelte` |
| `story_format` | CSF3 | CSF3 | CSF3 | Vue SFC | Vue SFC | Vue SFC | Svelte CSF |
| `story_extension` | `.tsx` | `.tsx` | `.tsx` | `.vue` | `.vue` | `.vue` | `.svelte` |
| `component_import` | `@postxl/ui-components` | `@/components/ui` | `@radix-ui/react-*` | `@nuxt/ui` | `primevue/*` | `@/components/ui` | `$lib/components` |
| `setup_file` | value | value | value | value | value | value | value |
| `component_library` | `@postxl/ui-components` | `shadcn/ui` | `@radix-ui/react-*` | `@nuxt/ui` | `primevue` | **null** | **null** |
| `icon_library` | **null** | `lucide-react` | `lucide-react` | `@iconify-json/lucide` | `primeicons` | **null** | **null** |
| `mock_template` | `preact_htm` | `preact_htm` | `preact_htm` | `vue_primevue` | `vue_primevue` | `alpine_shoelace` | `alpine_shoelace` |

Exact values are in `templates/README.md`, which carries the full matrix and is the single place
both **25** and **16** read. The README also defines what each key means and what `null` means
for it specifically — `null` is not one thing.

**The set is sixteen, not ADR 0009's nine.** The ADR's parenthetical list is illustrative: it
omits `storybook_addon` / `story_format` / `component_import` / `setup_file` / `mock_template`,
which this ticket was told to regularise into the same block, and `env_setup_command` /
`project_structure`, which `impl-build-scaffold` extracted by name. Sixteen is the closed set.

**Three atoms `mockup-storybook` currently *derives* are now declared.** `-mp`
`skills/mockup-storybook/SKILL.md` step 1 says to derive `story_extension` from `story_format`,
`component_library` from the `## Component Library` section and `icon_library` from the
dependency list. All three are frontmatter values now, under exactly those names. That skill was
not edited — a sibling session owns `skills/` — so **ticket 25 (or whoever next touches
`mockup-storybook`) should replace the derive branch with a read**, and drop "confirm all six
with the user" down to a report, since six of six are now stated.

### Where the recipes stayed — cited by heading, never by key

Sixteen `##` headings, identical and in the same order in all seven (verified programmatically):
`Overview` · `Identity` · `When to Use` · `Scaffold Recipe` · `Preview Compatibility` ·
`CSS Variables / Theming` · `Auth Setup` · `App Shell` · `Component Library` ·
`Mock Adaptation` · `Storybook Config` · `Migration / ORM` · **`Seed`** · `Codegen` ·
`Expert Skills` · `Key Implementation Patterns`.

**No skill may name an atom outside the sixteen or a heading outside the sixteen.** Adding either
is an edit to all seven templates plus `templates/README.md`, not a line in one skill.

### What ticket 25 must know before it writes a skill

1. **`## Seed` is new and is the only record of the per-ORM layout.** `impl-build-seed`'s twelve
   lines are now stack-accurate paths per template (`apps/backend/prisma/seed.ts` +
   `prisma/seeds/`, `server/db/seed.ts` + `seeds/`, `src/lib/server/db/seed.ts` + `seeds/`,
   `supabase/seed.sql` + `supabase/seeds/`, `seeds/run.ts` + `seeds/<scenario>.{ts,sql}` for the
   three Directus stacks). The **stack-neutral half stays in the skill**: the four scenarios,
   insert order, "empty actively clears", FK and enum validation — `contracts/seed_data.md`
   already holds the scenario set and every template cites it. `build-database` reads
   `seed_format` to pick the layout and reads the section for the paths.
2. **`impl-build-seed`'s `MUST search for prog-expert-*` does not port.** Nothing installs those
   skills and nothing can check for them; the templates now say "if installed, consult it".
3. **`env_setup_command` is `null` in all seven** and that is a real finding, not an omission: no
   template's scaffolder emits a `.env.example`, and the `.env` *contents* are recipe material
   under `## Scaffold Recipe`. The key exists so `build-scaffold` reads it without growing a
   missing-key branch — the exact defect ADR 0009 records. If a skill wants to *do* something
   here it reads the recipe section, not the atom.
4. **`lint_command` is `null` on the four bun stacks** — `nuxi init` and `sv create --no-add-ons`
   install no linter. `build-scaffold`'s verify step runs build + type-check unconditionally and
   lint only when the atom has a value.
5. **`architecture-techstack` (which absorbs `templates-select`) scores against
   `metadata.tags`** — kept on all seven for exactly that, plus the `## Identity` table.

### `impl-build-generate` — where the cascade went

Absorbed whole into `template-postxl`'s `## Codegen`, which grew three subsections under the
content already there (`### Before generating`, `### Resolving conflicts — a four-level cascade`,
`### After generating`). Nothing of the skill survives outside it. Carried across: the pre-flight
(schema is valid JSON · lock file present or first run · clean tree · concept-vs-project schema
disagreement is a question, not an overwrite); the **four-level cascade as a table** — overwrite
generated-only, verify `<<<<<<< Custom` blocks survived, `pnpm run generate --diff` on ejected
files taking structure and keeping business logic, escalate a genuine design decision; the
**custom-block preservation rule stated as its own paragraph** with the reason it matters (a
dropped block is silent — the build still passes and the behaviour is gone) and the check that
makes level 2 real (count markers before and after); the Prisma migration pairing and its
data-loss branch; the build + lint + types verify; and the standalone-commit rule. The three
`MUST`/`NEVER` lines are gone as uppercase and present as prose at the step they bind — ADR 0003.

### Three deliberate `null`s worth naming

- **`icon_library: null` on `template-postxl`.** `@postxl/ui-components` re-exports no icon set
  and the template pins none, so there is no value to read. Guessing one would put a wrong
  package into a scaffold command. The `## Component Library` section says so and tells the
  reader to pick one and record it in the project's own standards.
- **`icon_library: null` and `component_library: null` on the two minimal stacks.** Here `null`
  is the *answer*, not a hole: no component library means nothing to check screen-spec elements
  against, so every element is custom — which is the branch `mockup-storybook` should take. Both
  sections say to inline the SVGs rather than take a runtime dependency the stack exists to avoid.
- Where a value was asserted that the source prose did not carry — `@iconify-json/lucide`
  (nuxt-ui), `primeicons` (primevue) — a grounding line was added to that template's
  `## Component Library`, so the atom is traceable to prose rather than to an author's memory.

### Also done

- **`preview_compatibility.md` ported to `templates/`** (292 lines), header rewritten for its new
  home and its stale `09_impl-architecture/templates/` + `impl-build-scaffold`/`-foundation`
  audience note replaced; "profile" → "template" throughout its checklist. All seven
  `## Preview Compatibility` sections repointed from `contracts/` to `templates/`, 7/7.
- **`contracts/README.md`**: the `preview_compatibility → walkthrough_renderer` row this ticket
  expected to delete **was never in `-mp`** — ticket 16 rewrote that file wholesale and the row
  did not survive into it (`git log -S` finds no occurrence). What was missing was the pointer, so
  a "What is not here" entry now records that the fold never happened, why it was wrong, and where
  the file actually lives. The `seed_data.md` row gained the templates as a second reader.
- **`templates/README.md` rewritten** — the stale version called `template-postxl`
  "FastAPI + Vue + PostgreSQL" and said "Nuxt 3" three times. It now states the atoms/recipes
  contract, the dir-name-is-the-id rule, both atom matrices, the per-atom meaning and `null`
  semantics, the sixteen headings, a corrected identity table, why `preview_compatibility.md`
  sits there, and how to add a stack.
- **Pre-0007 paths swept in all seven**: `_concept/discovery/brand/tokens.json` →
  `_concept/03_brand/tokens.json`, `_concept/blueprint/datamodel/` →
  `_concept/10_blueprint/datamodel/`. Frontmatter dropped the dead `requires: standards-contract`
  (no such contract in `-mp`) and the "invocable skill" self-description.
- **One source contradiction fixed**: `template-sveltekit-minimal`'s scaffold comment claimed
  "ESLint, Prettier" beside a `--no-add-ons` flag that installs neither. Corrected, with the
  `lint_command: null` / `type_check_command: bun run check` consequence stated inline.

### Left undone, deliberately

- **`skills/` untouched**, including `mockup-storybook`'s derive branch (item above) — sibling
  sessions own that tree.
- **No eighth template and none dropped** — out of scope by the ticket.
- **No validator for the atom block.** Ticket **16** owns the check; this ticket only fixed the
  data. The rule it should enforce is stated in `templates/README.md`: sixteen atom keys present
  in every `metadata.atoms` (value or explicit `null`), sixteen `##` headings in order, and
  directory name == `name:`.

### For the forge-concept register

Nothing new. Templates are not discovered by `parseSkillRequirements` — they are resolved by name
and read by an agent — so ADR 0011's `metadata:` nesting is followed here for repo consistency
rather than because a host reader requires it. If templates are ever made host-visible, that is
the same `fm.metadata ?? {}` site already recorded under **27**.
