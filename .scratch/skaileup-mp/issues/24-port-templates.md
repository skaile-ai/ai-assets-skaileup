# 24: Port the templates — 7 × TEMPLATE.md into `templates/`

**Type:** task
**Blocked by:** None (18 resolved)
**Status:** ready

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
