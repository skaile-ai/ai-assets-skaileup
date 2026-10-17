# templates/

Seven tech-stack references, one directory each. A template is **reference data an agent loads
one section of** — not instruction it follows top to bottom — so the skill line ceilings do
not apply here and the seven run 420–740 lines because the stacks are genuinely that large.

`templates/` is a root asset kind, sibling to `skills/` · `flows/` · `tree/`
(ADR 0009). It is not `tree/`, because no skill reads a template at a step the way it reads
a tree node — a skill resolves *one* template by name and then reads from it. Project types are
not templates either: they live in `tree/01_meta/scope.md § Project types`, and **a project type
says what a project never grows, a template is a tech-stack reference** (ADR 0002's vocabulary).

## The one rule about names

**The directory name is the template id, character for character.** `_concept/10_blueprint/techstack.md`
records the winner as `tech_stack_skill: template-postxl`, and every skill that needs stack
knowledge resolves `templates/<that string>/TEMPLATE.md`. There is no registry, no index to keep
in sync, and no numbering — the same rule ADR 0002 applies to `skills/`, applied to a second kind
of asset. Frontmatter `name:` repeats the directory name and must agree with it.

## Atoms and recipes

Two shapes were being confused under one word, "key", and that confusion is what broke the
skill↔template contract for every name any skill extracted — 0/7 across the whole set, so
`impl-build-foundation`'s *"if any section is missing from the profile, ask the user"* branch
fired on every run. ADR 0009 types the seam:

- **An atom is one value, extracted by name.** Atoms live in frontmatter under
  `metadata.atoms`. **Every template declares every atom** — with a value, or with an explicit
  `null`. There is no third state; a key that is simply absent is the defect, because a reader
  cannot tell "this stack has none" from "nobody wrote it down".
- **A recipe is paragraphs, not a value.** Recipes stay named `##` sections and a skill cites the
  heading. `## Scaffold Recipe`, `## CSS Variables / Theming`, `## Auth Setup`, `## App Shell`,
  `## Migration / ORM`, `## Seed`, `## Storybook Config`, `## Codegen` are recipes. Pretending one
  of those was a key is what broke the contract in the first place.

**No skill names an atom that is not in this list, and no skill invents a section heading.**
Adding either is an edit to all seven templates plus this file, not a line in one skill.

### The atom set — sixteen keys, 7/7 each

Build and scaffold atoms:

| atom | postxl | shadcn | radix | nuxt-ui | primevue | nuxt-min | sk-min |
|---|---|---|---|---|---|---|---|
| `scaffold_command` | `postxl scaffold new <app-name>` | `npx create-next-app@latest . --typescript --tailwind --app --src-dir --import-alias "@/*"` | `npx create-next-app@latest . --typescript --tailwind --app --src-dir --import-alias "@/*"` | `bunx nuxi@latest init . --packageManager bun` | `bunx nuxi@latest init . --packageManager bun` | `bunx nuxi@latest init . --packageManager bun` | `bunx sv@latest create . --template minimal --types ts --no-add-ons` |
| `package_manager` | `pnpm` | `pnpm` | `pnpm` | `bun` | `bun` | `bun` | `bun` |
| `build_command` | `pnpm run build` | `pnpm build` | `pnpm build` | `bun run build` | `bun run build` | `bun run build` | `bun run build` |
| `env_setup_command` | `null` | `null` | `null` | `null` | `null` | `null` | `null` |
| `project_structure` | `apps/frontend/ · apps/backend/ — pnpm workspace monorepo` | `src/app/ · src/components/ui/ · src/components/shell/ · src/lib/ · supabase/` | `src/app/ · src/components/ui/ · src/components/shell/ · src/lib/` | `app.vue · layouts/ · pages/ · components/app/ · composables/ · server/api/` | `app.vue · layouts/ · pages/ · components/app/ · composables/ · server/api/` | `layouts/ · pages/ · components/ui/ · composables/ · server/api/ · server/db/` | `src/routes/ · src/lib/ · src/lib/components/ · src/lib/server/db/` |
| `lint_command` | `pnpm run lint` | `pnpm lint` | `pnpm lint` | `null` | `null` | `null` | `null` |
| `type_check_command` | `pnpm run test:types` | `pnpm exec tsc --noEmit` | `pnpm exec tsc --noEmit` | `bunx nuxi typecheck` | `bunx nuxi typecheck` | `bunx nuxi typecheck` | `bun run check` |
| `seed_format` | `prisma` | `sql` | `sql` | `sql` | `sql` | `drizzle` | `drizzle` |

Mockup and Storybook atoms:

| atom | postxl | shadcn | radix | nuxt-ui | primevue | nuxt-min | sk-min |
|---|---|---|---|---|---|---|---|
| `storybook_addon` | `@storybook/react` | `@storybook/nextjs` | `@storybook/nextjs` | `@storybook/nuxt` | `@storybook/vue3` | `@storybook/vue3` | `@storybook/svelte` |
| `story_format` | `CSF3` | `CSF3` | `CSF3` | `Vue SFC` | `Vue SFC` | `Vue SFC` | `Svelte CSF` |
| `story_extension` | `.tsx` | `.tsx` | `.tsx` | `.vue` | `.vue` | `.vue` | `.svelte` |
| `component_import` | `@postxl/ui-components` | `@/components/ui` | `@radix-ui/react-*` | `@nuxt/ui` | `primevue/*` | `@/components/ui` | `$lib/components` |
| `setup_file` | `apps/frontend/.storybook/setup.ts` | `.storybook/preview.tsx` | `.storybook/setup.ts` | `.storybook/setup.ts` | `.storybook/setup.ts` | `.storybook/setup.ts` | `.storybook/preview.ts` |
| `component_library` | `@postxl/ui-components` | `shadcn/ui` | `@radix-ui/react-*` | `@nuxt/ui` | `primevue` | `null` | `null` |
| `icon_library` | `null` | `lucide-react` | `lucide-react` | `@iconify-json/lucide` | `primeicons` | `null` | `null` |
| `mock_template` | `preact_htm` | `preact_htm` | `preact_htm` | `vue_primevue` | `vue_primevue` | `alpine_shoelace` | `alpine_shoelace` |

What each one means, and what `null` means for it:

| atom | value | `null` means |
|---|---|---|
| `scaffold_command` | The command that creates the project in an empty directory | — (never null) |
| `package_manager` | `pnpm` \| `bun` \| `npm` — the one the recipe's commands assume | — (never null) |
| `build_command` | Production build, used as the scaffold's smoke test | — (never null) |
| `env_setup_command` | The command that produces the app's local env file(s) | The scaffolder emits no `.env.example`, so there is nothing to run. The `.env` *contents* are recipe material under `## Scaffold Recipe`. **Currently `null` in all seven** — the first stack whose scaffolder ships an example file fills it |
| `project_structure` | The source directories the scaffold is expected to produce, as one line | — (never null) |
| `lint_command` | Lint the whole project | The scaffold recipe installs no linter. Adding one is the project's decision, not the template's |
| `type_check_command` | Type-check without emitting | — (never null) |
| `seed_format` | `prisma` \| `drizzle` \| `sql` — selects the seed layout in `## Seed` | — (never null) |
| `storybook_addon` | The Storybook framework package | — (never null) |
| `story_format` | `CSF3` \| `Vue SFC` \| `Svelte CSF` | — (never null) |
| `story_extension` | Component file extension inside the Storybook project | — (never null) |
| `component_import` | The module specifier stories import library components from | — (never null) |
| `setup_file` | The Storybook file that registers the theme/plugins | — (never null) |
| `component_library` | The library a screen spec's UI elements are checked against | The stack has none. Every element in a screen spec is a custom component — that is the answer, not a gap |
| `icon_library` | The icon package the app uses | Either the stack pins none deliberately (the two minimal stacks — inline the SVGs) or the template genuinely does not know (`template-postxl`: `@postxl/ui-components` re-exports no icon set). Each template's `## Component Library` says which |
| `mock_template` | Which CDN mock template best approximates this stack | — (never null) |

`story_extension`, `component_library` and `icon_library` were the three values
`mockup-storybook` had to *derive* because no template carried them. They are carried now; a
skill reads them.

## The section set — sixteen headings, identical in all seven

`## Overview` · `## Identity` · `## When to Use` · `## Scaffold Recipe` ·
`## Preview Compatibility` · `## CSS Variables / Theming` · `## Auth Setup` · `## App Shell` ·
`## Component Library` · `## Mock Adaptation` · `## Storybook Config` · `## Migration / ORM` ·
`## Seed` · `## Codegen` · `## Expert Skills` · `## Key Implementation Patterns`

Two of those carry weight worth naming:

- **`## Seed`** is the only written record of the per-ORM seed layout. It came from the deleted
  `impl-build-seed`, whose per-ORM lines existed nowhere else. The stack-neutral half — the four
  scenarios and the rules they obey — stays in `tree/10_blueprint/datamodel/seed.md`; the template carries the
  paths and the run command.
- **`## Codegen`** in `template-postxl` absorbed the whole of the deleted `impl-build-generate`,
  including the four-level conflict cascade and the `<<<<<<< Custom` preservation rule. That skill
  was PostXL-specific in a stack-neutral costume; ADR 0009 sent it here. In the other six the
  section is short, because those stacks have no generator.

`## Expert Skills` is **optional in all seven**. The `prog-expert-*` skills live in a different
collection (`ai-assets/dev-implementation-experts-*`) and `skaile.yaml` has no dependency
mechanism — glob discovery only, no `assets:` block — so the dependency cannot be declared even
if it were wanted. The sections read *"if it is installed, consult it"*. Nothing is gated on one.

## The seven

| id | frontend | UI library | backend / database |
|---|---|---|---|
| `template-postxl` | React 19 + Vite (SPA) | `@postxl/ui-components` | NestJS + Prisma + PostgreSQL, Keycloak auth |
| `template-nextjs-shadcn` | Next.js 15 App Router | shadcn/ui | Supabase (managed Postgres) |
| `template-nextjs-radix` | Next.js 15 App Router | Radix UI primitives | Directus + PostgreSQL |
| `template-nuxt-ui` | Nuxt 4 | `@nuxt/ui` v3 (Reka UI) | Directus + PostgreSQL |
| `template-nuxt-primevue` | Nuxt 4 | PrimeVue 4 | Directus + PostgreSQL |
| `template-nuxt-minimal` | Nuxt 4 | none — Tailwind only | Nitro + Drizzle + SQLite |
| `template-sveltekit-minimal` | SvelteKit 2 / Svelte 5 | none — Tailwind only | SvelteKit server + Drizzle + SQLite |

## `preview_compatibility.md`

Beside the templates, not in `tree/`. Its seven readers are the templates' own
`## Preview Compatibility` sections, and templates are not skills, so no `_concept/` part has a
node for it while it is genuinely needed — duplicating 292 lines seven times was the alternative. Each
template keeps a short framework-specific section (the config snippet, the navigation rules that
bite on *that* framework) and points here for the proxy contract, the anti-pattern table, and the
`[LegacyUnforgeable]` rationale behind all of it.

## Adding a stack

A stack this collection has no template for is a gap **here**, not in `skills/`. That is the
trade ADR 0009 made: adding one is sixteen sections of reference work rather than a special case
wedged into a skill, and no skill grows a branch for it.

Write `templates/<id>/TEMPLATE.md` with all sixteen atoms — value or explicit `null` — and all
sixteen sections in the order above, add a row to the two matrices and the identity table here,
and give it a `## Preview Compatibility` section that points at `preview_compatibility.md`.
