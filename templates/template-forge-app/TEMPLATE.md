---
name: template-forge-app
description: 'Tech-stack reference for the SKAILE App Template: Nuxt 4 + @nuxt/ui v4 + one server-action catalogue (UI, HTTP, MCP, CLI, chat) + Drizzle on PGlite or Postgres. Resolved by directory name from _concept/10_blueprint/techstack.md.'
metadata:
  type: template
  version: '0.1.0'
  atoms:
    scaffold_command: 'GIGET_AUTH=$(gh auth token) bunx giget@latest gh:skaile-ai/skaile-app-template . --install'
    package_manager: 'bun'
    build_command: 'bun run build'
    env_setup_command: 'cp .env.example .env'
    project_structure: 'app/ · server/db/ (schema + model.ts) · server/utils/ (data.ts, actions/) · server/plugins/ · shared/ · bin/ · layers/ · test/'
    lint_command: 'bun run lint'
    type_check_command: 'bun run typecheck'
    seed_format: 'drizzle'
    storybook_addon: '@storybook/nuxt'
    story_format: 'Vue SFC'
    story_extension: '.vue'
    component_import: '@nuxt/ui'
    setup_file: '.storybook/setup.ts'
    component_library: '@nuxt/ui'
    icon_library: '@iconify-json/lucide'
    mock_template: 'vue_primevue'
  tags:
    - 'nuxt'
    - 'nuxt-ui'
    - 'reka-ui'
    - 'drizzle'
    - 'pglite'
    - 'postgresql'
    - 'nitro'
    - 'nuxt-auth-utils'
    - 'mcp'
    - 'server-actions'
    - 'agents'
    - 'ssr'
    - 'vue3'
    - 'tailwind'
    - 'bun'
    - 'skaile'
    - 'data-driven'
---

# Tech Stack: SKAILE App Template (Nuxt 4 + @nuxt/ui + server actions + Drizzle)

## Overview

A runnable Nuxt 4 starter for data-driven apps in which **every capability is a server action**.
One catalogue (`server/utils/actions/*.ts`, built on `@skaile/forge-app-actions`) is written once —
a Zod input, an LLM-readable description, an audience and an authorization check — and every
surface runs that same code path: the web UI (typed actions client), the HTTP API
(`/api/actions/<id>`), MCP for agents (`/mcp`), the app's own CLI (`bin/app.ts`), and through
optional layers the in-app chat's tools, a SKAILE workspace agent and pg-boss workers. The UI is
@nuxt/ui v4 with the `@skaile/brand` Nuxt UI bridge in a `UDashboardGroup` sidebar shell.

Data is Drizzle ORM on the Postgres dialect only: **PGlite in-process** (`.data/pg`, zero setup)
when `DATABASE_URL` is unset, **postgres-js against Postgres 17** when it is set. Migrations
apply on boot, an empty database is seeded with an owner and demo data, so `bun install && bun run dev`
works with no services and no `.env`. Optional capabilities live in `layers/<name>/` (Nuxt
auto-registers each one) and are subtractive: delete the folder and the app still runs.

Best suited for SKAILE-built internal tools, back-office and data apps where agents (Claude Code,
omp, the workspace agent) must be able to do everything a person can, with the same rights.

## Identity

| Field           | Value                                                                                        |
| --------------- | -------------------------------------------------------------------------------------------- |
| Frontend        | Nuxt 4.6 (Vue 3, Composition API), SSR                                                       |
| UI Library      | @nuxt/ui v4 (4.12, Reka UI + Tailwind CSS 4) + `@skaile/brand` Nuxt UI bridge                |
| Backend         | Nitro (Nuxt server) + `@skaile/forge-app-actions` catalogue → HTTP `/api/actions`, MCP `/mcp` |
| Database        | PGlite 0.5 in-process (local, default) or PostgreSQL 17 (`DATABASE_URL`)                     |
| Auth            | `nuxt-auth-utils` sealed-cookie sessions (`APP_AUTH_MODE=local` or `password`) + API tokens  |
| ORM / DB Access | Drizzle ORM 0.45 (Postgres dialect), drizzle-kit migrations                                  |
| Package Manager | bun                                                                                          |
| CSS Methodology | Tailwind CSS 4 + @nuxt/ui tokens from `@skaile/brand/nuxt-ui.css`                            |

## When to Use

- Best for: data-driven apps (lists, forms, dashboards) where agents and scripts must reach every feature, not just people
- Best for: SKAILE projects that want an MCP server, an HTTP API and a CLI without writing them three times
- Best for: apps that must run locally with zero services (PGlite) and deploy to Postgres unchanged (Docker, Coolify)
- Best for: products that will grow an in-app assistant, a workspace agent or background jobs (layers)
- Avoid when: the backend is a headless CMS the client edits directly — use template-nuxt-ui or template-nuxt-primevue with Directus
- Avoid when: the stack is React — use template-nextjs-shadcn, template-nextjs-radix or template-postxl
- Avoid when: a static or content site with no data model — template-nuxt-minimal is lighter

## Scaffold Recipe

```bash
# 1. Copy the template into the empty project directory and install
#    (the template is a runnable app, not a generator: no prompts).
#    The repository is private: giget reads a GitHub token from GIGET_AUTH,
#    e.g. GIGET_AUTH=$(gh auth token).
GIGET_AUTH=$(gh auth token) bunx giget@latest gh:skaile-ai/skaile-app-template . --install

# 2. Optional: an env file (nothing is required locally; see .env.example)
cp .env.example .env

# 3. Run: http://localhost:7400, signed in as the owner, demo data seeded
bun run dev

# 4. The gate: lint + typecheck + tests
bun run check
```

What the scaffold already contains, so the foundation step does **not** re-create it:

- `nuxt.config.ts` with `@nuxt/ui`, `@vueuse/nuxt`, `nuxt-auth-utils`, `@skaile/forge-app-actions`
  (HTTP `/api/actions`, MCP `/mcp`), `app.baseURL` from `SKAILE_PREVIEW_BASE`, dev port 7400
- `server/db/schema/*` (users, api_tokens, settings, user_preferences, projects, tasks, chat
  threads/messages, notifications), `server/db/migrations/`, `server/db/seed.ts`
- the dashboard shell, Settings (General, AI, API tokens, Profile), command palette, `<SchemaForm>`
- `bin/app.ts` CLI (citty), `Dockerfile`, `compose.yaml` (Postgres 17 + app), `/api/health`
- `skaile.yaml` declaring the skaileup flow for coding agents

Then **rename the example domain**: `projects`/`tasks` (schema, actions, pages, seed) are there
so every surface has real data on first start; replace them with the blueprint's entities.

Environment (`.env.example` documents all; only production needs values):

| Variable | Default | Meaning |
|---|---|---|
| `DATABASE_URL` | unset → PGlite in `.data/pg` | Postgres connection string |
| `PGLITE_DIR` | `.data/pg` | PGlite data directory |
| `APP_AUTH_MODE` | `local` without `DATABASE_URL`, else `password` | `local`: auto-signed-in owner |
| `NUXT_APP_SECRET` | generated in dev | Seals the session cookie, ≥ 32 chars — **required in production** |
| `APP_OWNER_EMAIL` / `APP_OWNER_NAME` / `APP_OWNER_PASSWORD` | `owner@localhost` / `Owner` / none | First owner, created on an empty database |

Commands from `package.json`:

| Command | What |
|---|---|
| `bun run dev` | dev server on :7400 |
| `bun run build` / `bun run preview` | production build in `.output` (`node .output/server/index.mjs`) |
| `bun run lint` / `bun run typecheck` / `bun run test` | eslint (`@nuxt/eslint`) / `nuxt typecheck` / vitest |
| `bun run check` | all three — the gate |
| `bun run db:generate` | new migration from `server/db/schema` changes |
| `bun run db:migrate` / `bun run db:seed` | apply migrations / seed demo data (CLI, no server) |
| `bun run cli --help` | `actions`, `token create\|list\|revoke`, `db migrate\|seed` |

## Preview Compatibility

Apps generated from this template run in the Skaile workspace's preview iframe at
`/preview/<session-id>/`. The scaffold's `nuxt.config.ts` already wires it:

```typescript
const baseURL = process.env.SKAILE_PREVIEW_BASE || '/'

export default defineNuxtConfig({
  app: {
    baseURL,
    head: { link: [{ rel: 'icon', type: 'image/svg+xml', href: `${baseURL.replace(/\/$/, '')}/favicon.svg` }] },
  },
})
```

Conventions in app code:

- Use `<NuxtLink to="/tasks">`, `navigateTo('/tasks')` and the shell's `appShell.nav` entries —
  Nuxt prepends `app.baseURL` automatically.
- Call the server through `useActions()` (the typed actions client) or path-relative
  `$fetch('/api/...')`; never hardcode `http://localhost:7400`. The proxy fans
  `/preview/<sid>/api/...` and `/preview/<sid>/mcp` out to the same Nitro server.
- Never use raw `<a href="/foo">` or `window.location.href = '/foo'` for in-app navigation.
- Static asset URLs built by hand (the favicon above) must carry the base themselves.

See `templates/preview_compatibility.md` for the full contract, anti-patterns, and per-framework
rationale.

## CSS Variables / Theming

`app/assets/css/main.css` imports Tailwind, @nuxt/ui, then the SKAILE brand bridge, which sets
the @nuxt/ui palette, radius and light/dark tokens:

```css
@import "tailwindcss";
@import "@nuxt/ui";
/* SKAILE brand → Nuxt UI tokens (palette, radius, light/dark); must come after @nuxt/ui. */
@import "@skaile/brand/nuxt-ui.css";
```

For a **SKAILE-branded** app that is the whole theme. For a **client brand**, values come from
`_concept/03_brand/brand.tokens.json` (DTCG), flattened to `--token-*` custom properties
(`tree/03_brand/brand.tokens.md § Flattening to CSS`), and replace the brand import with the same
two-level mapping template-nuxt-ui uses — a `brand` ramp derived from `color.primary` with
`color-mix()` in `@theme`, and `--ui-*` surface aliases:

```css
@import "tailwindcss";
@import "@nuxt/ui";

@theme {
  --color-brand-50: color-mix(in oklch, var(--token-color-primary) 8%, white);
  --color-brand-500: var(--token-color-primary);
  --color-brand-900: color-mix(in oklch, var(--token-color-primary) 40%, black);
  /* ...100-400, 600-800, 950 on the same pattern */
  --font-sans: var(--token-font-body);
  --radius-md: var(--token-radius-base);
}

:root {
  --ui-bg: var(--token-color-background);
  --ui-bg-muted: var(--token-color-surface);
  --ui-text: var(--token-color-text);
  --ui-text-muted: var(--token-color-text-muted);
  --ui-border: var(--token-color-border);
  --ui-radius: var(--token-radius-base);
}
```

```typescript
// app/app.config.ts — merged with the existing appShell block
export default defineAppConfig({
  ui: { colors: { primary: 'brand', neutral: 'zinc' } },
})
```

| DTCG path (`brand.tokens.json`) | @nuxt/ui target | CSS variable |
|---|---|---|
| `color.primary` | `ui.colors.primary: 'brand'` | `--color-brand-*` (derived ramp) |
| `color.background`, `color.surface` | `--ui-bg`, `--ui-bg-muted` | `--token-color-background`, `--token-color-surface` |
| `color.text`, `color.text-muted` | `--ui-text`, `--ui-text-muted` | `--token-color-text`, `--token-color-text-muted` |
| `color.border` | `--ui-border` | `--token-color-border` |
| `font.body` | `@theme --font-sans` | `--token-font-body` |
| `radius.base` | `--ui-radius`, `@theme --radius-md` | `--token-radius-base` |

Dark mode is `@nuxtjs/color-mode` through @nuxt/ui; the person's stored preference
(`user_preferences.colorMode`) wins over the browser on every device.

## Auth Setup

Already wired by the scaffold; the blueprint decides the mode, not the code.

- **Sessions:** `nuxt-auth-utils` sealed cookie (`skaile-app-session`, 7 days), sealed with
  `NUXT_APP_SECRET`. `APP_AUTH_MODE=local` signs every request in as the owner
  (`server/middleware/10.local-session.ts`; desktop and local use). `password` uses the `users`
  table with hashed passwords and the `/login` page; the first owner comes from `APP_OWNER_*`.
- **Machine access:** API tokens (`api_tokens`, SHA-256-hashed, prefix `sk_app_`, shown once,
  kind `cli|mcp|agent`, scopes). Created in **Settings → API tokens** or
  `bun run cli token create --name laptop --kind cli --scopes '*'` (server stopped — PGlite
  allows one process per data directory).
- **One principal everywhere:** `server/plugins/actions.ts` resolves a `Principal`
  `{ kind: 'user'|'token'|'agent'|'system', id, name, roles, scopes }` in the
  `forge-app-actions:http:authorize` and `:mcp:authorize` hooks. `/api/actions` accepts a bearer
  token or the session cookie (effect actions only from the app's own origin — CSRF); `/mcp`
  accepts bearer tokens only.
- **Per-action rules** live in each action's `authorize(ctx)`: `requireRole(ctx, 'owner')`,
  `requireScope(ctx, 'tasks:write')` from `server/utils/principal.ts`. Custom Nitro routes use
  `requirePrincipal(event)` from `server/utils/auth.ts`.
- Client: `useMe()` gives the signed-in person and preferences; `app/middleware/auth.global.ts`
  sends anonymous visitors to `/login` in password mode.

The chat and agent layers act with the signed-in person's principal: an assistant never does
more than its user.

## App Shell

`app/layouts/default.vue` is a @nuxt/ui dashboard shell: `UDashboardGroup unit="rem"
storage="local" storage-key="skaile-app"` holding a collapsible, resizable left
`UDashboardSidebar` with only the logo, the `UNavigationMenu` and the `UserMenu` in its footer
(Settings, Profile, API tokens, Appearance, sign out; avatar only when collapsed), the page, the right-hand drawers
layers add, and `UDashboardSearch` as the ⌘K command palette (navigation and quick-create
actions). Panel sizes and open state persist in localStorage under `skaile-app-sidebar-<id>`
(`skaile-app-sidebar-default`, `skaile-app-sidebar-assistant`). `app/app.vue` wraps everything
in `<UApp>` and mounts the one `ConfirmDialog`.

**One header, rendered per page.** Every page puts `<AppHeader title :badge :back>` (wraps
`UDashboardNavbar`) in its `UDashboardPanel #header`. `back` is a route and shows the back arrow;
the `#actions` slot holds the page's create button for its data type ("New task", "New
project"). The global cluster on the right is the same everywhere: search (⌘K), the
notifications bell (`NotificationsMenu`: unread chip, latest 10, mark one / mark all read), then
the header widgets layers push; the chat layer's assistant toggle is the rightmost button.

**Assistant drawer (chat layer).** `ChatDrawer` is a right `UDashboardSidebar id="assistant"
side="right"`, resizable 20–48rem (default 28rem), with a thread picker (switch, rename, delete),
"New conversation" and the assistant toggle as close button in its header: closed, the toggle is
the header's rightmost button; open, the drawer shows it in the same top-right spot. ⌘J, the
palette or the toggle open it, and on phones it is a slideover. There is no `/chat` page: `/chat/<id>` redirects to
`/?assistant=<id>` and opens the drawer on that thread. Without the chat layer there is no toggle
and no drawer.

**Navigation is data, not markup.** Sidebar and Settings sub-nav entries come from
`app.config.ts` (Settings itself is not a nav entry; it lives in the user menu):

```typescript
export default defineAppConfig({
  appShell: {
    nav: [
      { label: 'Dashboard', icon: 'i-lucide-layout-dashboard', to: '/', order: 10 },
      { label: 'Projects', icon: 'i-lucide-folder-kanban', to: '/projects', order: 20 },
    ],
    settingsNav: [
      { label: 'General', icon: 'i-lucide-sliders-horizontal', to: '/settings', order: 10 },
    ],
  },
})
```

A layer adds entries in its own `app.config.ts` (arrays concatenate, the shell sorts by
`order`; core uses 10–90). A new screen is a page under `app/pages/` with an `<AppHeader>` plus
one `nav` entry — never an edit to the layout.

Everything else a layer adds to the shell goes through the runtime hook `app-shell:extend` with
`{ commands, header, drawers, overlays, settingsSections }` (`app/types/app-shell.d.ts`): palette
groups, header widgets, right-hand panels rendered after the page, once-mounted overlays, and
settings scopes shown as cards on a core settings page. The chat layer's plugin:

```typescript
export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.hook('app-shell:extend', (shell) => {
    shell.commands.push({ id: 'assistant', label: 'Assistant', items: [/* Ask the assistant, ⌘J */] })
    shell.header.push(AssistantToggle)  // in every AppHeader's global cluster
    shell.drawers.push(ChatDrawer)      // UDashboardSidebar side="right" after the page
    shell.settingsSections.push({ route: '/settings/ai', scope: 'assistant', title: 'Assistant' })
  })
})
```

**Key files:**

- `app/layouts/default.vue` — the shell; `app/composables/useAppShell.ts` — sorted nav;
  `app/utils/appShell.ts` — injection key for the collected extension
- `app/components/AppHeader.vue` — the per-page header; `NotificationsMenu.vue`; `UserMenu.vue` (sidebar footer)
- `app/composables/useQuickCreate.ts` — the create modals the palette and page headers open
- `app/components/form/FormModal.vue`, `form/SaveHint.vue`, `form/DiscardPrompt.vue`;
  `app/composables/useFormDirty.ts`, `useDiscardGuard.ts`, `useLeaveGuard.ts`;
  `app/utils/formMissing.ts`, `app/utils/formErrors.ts` — the forms kit
- `app/composables/useConfirm.ts` + `app/components/ConfirmDialog.vue` — the one confirm dialog
- `app/components/SchemaForm.vue` — renders any settings scope's JSON schema as a `UForm`
- `app/pages/settings.vue` + `app/pages/settings/*` — the Settings sub-shell
- `layers/chat/app/components/ChatDrawer.vue`, `AssistantToggle.vue`,
  `composables/useAssistant.ts` — the assistant drawer

### UI rules (APP-DESIGN.md)

The template ships `APP-DESIGN.md` with the full rules; agents follow it. In short:

- **Row actions:** a row's primary state change is a visible button (tasks: Complete / Reopen,
  icon-only with `aria-label` and tooltip on narrow screens). The ⋮ menu holds only Edit, a
  separator, then Delete last in the error color. Delete confirms.
- **Forms:** `FormModal` wraps `UModal`. A mask click never closes it; the footer is
  `[Delete] ··· [Cancel] [Save]`, Save is the only solid button and Enter submits. Closing with
  unsaved input asks "Discard changes?" in place, in the footer. Save is disabled only while the
  client schema fails, with `SaveHint` naming what is missing ("Missing: Title"); a server
  refusal never disables it. A 400 naming a field lands on that field (`form.setErrors`),
  anything else is a toast. Full-screen on phones. Settings pages ask before leaving unsaved
  changes.
- **Confirm:** `useConfirm().confirm({ title, description, confirmLabel, color })` resolves to a
  boolean through the one `ConfirmDialog`; the accept label is the verb ("Delete task") in the
  error color.

## Component Library

| Generic UI concept | @nuxt/ui Component                         | Import        |
| ------------------ | ------------------------------------------ | ------------- |
| App shell          | `UDashboardGroup` / `UDashboardSidebar`    | auto-imported |
| Page / Header      | `UDashboardPanel` / `AppHeader` (wraps `UDashboardNavbar`) | auto-imported |
| Command Palette    | `UDashboardSearch` / `UCommandPalette`     | auto-imported |
| Button             | `UButton`                                  | auto-imported |
| DataTable          | `UTable`                                   | auto-imported |
| Modal/Dialog       | `FormModal` (wraps `UModal`) for forms     | auto-imported |
| Confirm            | `useConfirm()` + `ConfirmDialog`           | auto-imported |
| Right drawer       | `UDashboardSidebar side="right"`           | auto-imported |
| Slideover          | `USlideover`                               | auto-imported |
| Form (wrapper)     | `UForm`                                    | auto-imported |
| Form Field         | `UFormField`                               | auto-imported |
| Form Input         | `UInput` / `UTextarea`                     | auto-imported |
| Select/Dropdown    | `USelect` / `USelectMenu`                  | auto-imported |
| Date Picker        | `UInputDate` + `UCalendar`                 | auto-imported |
| Navigation         | `UNavigationMenu`                          | auto-imported |
| Card               | `UCard`                                    | auto-imported |
| Toast/Notification | `useToast()`                               | auto-imported |
| Badge              | `UBadge`                                   | auto-imported |
| Avatar / User menu | `UAvatar` / `UDropdownMenu`                | auto-imported |
| Tabs               | `UTabs`                                    | auto-imported |
| Empty state        | `UEmpty`                                   | auto-imported |

All components are auto-imported by the `@nuxt/ui` module.

**Icons — `@iconify-json/lucide`.** Installed as a dependency; icons are referenced by name
(`i-lucide-list-checks`) and bundled locally by Nuxt Icon, so nothing hits the Iconify API.

## Mock Adaptation

@nuxt/ui is not available via CDN (it needs the Tailwind v4 build pipeline), so the mock skill
uses the **`vue_primevue`** template as the closest Vue-based approximation.

```yaml
mock_template: vue_primevue
```

The CDN mock is a structural approximation only. Fidelity to @nuxt/ui and the SKAILE brand comes
from the mockup Storybook and, ultimately, the running app (`bun run dev` needs no services).

## Storybook Config

```yaml
storybook_addon: '@storybook/nuxt'
story_format: Vue SFC
component_import: '@nuxt/ui'
setup_file: .storybook/setup.ts
```

**The scaffold ships no Storybook.** Per ADR 0009 the built app gets none from this collection;
the values above are what an app that wants one uses, as ordinary `build-implement` work, and
what the mockup Storybook assumes for this stack. `@storybook/nuxt` is required rather than
`@storybook/vue3`, because @nuxt/ui's auto-imports and the `appShell` app config must be active.

**`.storybook/main.ts`:**

```typescript
export default {
  framework: '@storybook/nuxt',
  stories: ['../app/components/**/*.stories.ts'],
  addons: ['@storybook/addon-essentials'],
}
```

**`.storybook/setup.ts`:** import `../app/assets/css/main.css` so the brand bridge applies.

Stories cover `app/components/` only. Pages call server actions and need the Nitro server; test
those with vitest against the actions instead.

## Migration / ORM

One Drizzle schema (`server/db/schema/*.ts`, Postgres dialect), one migration folder
(`server/db/migrations/`), applied **on boot** by the database plugin on both engines (PGlite
and postgres-js share the journal). Never hand-edit applied migrations.

```bash
# after changing server/db/schema/*.ts
bun run db:generate        # drizzle-kit generate → server/db/migrations/NNNN_*.sql

# apply without starting the server (server must be stopped on PGlite)
bun run db:migrate
```

Server code uses `useDb()` (full schema) and `withTx(fn)` from `server/utils/db.ts`. **On PGlite
every query inside a transaction must use `tx`**, not `useDb()` — the single connection
deadlocks otherwise. `useDbTarget()` returns `{ kind: 'pglite', client }` or
`{ kind: 'postgres', url }` for libraries that need the raw connection (pg-boss). Code outside a
request awaits `dbReady()` first. Only the core owns the schema; layers add no tables.

## Seed

`seed_format: drizzle`. Seed code is generated from `_concept/10_blueprint/datamodel/seed.json` —
one module per scenario plus one entry point that takes the scenario name. The scenario set and
the rules every scenario obeys are stack-neutral and live in `tree/10_blueprint/datamodel/seed.md`;
what is stack-specific is the layout and the run command below.

| Path | What it is |
|---|---|
| `server/db/seed.ts` | Entry point used by boot and the CLI: `ensureOwner(db)` then the scenario; the generated version takes a scenario name, defaulting to `populated` |
| `server/db/seeds/<scenario>.ts` | One module per scenario, typed Drizzle inserts against `server/db/schema`, deleting in reverse dependency order first |
| `bin/app.ts` (`db seed`) | The CLI command; give it a positional `scenario` argument passed through to the entry point |

```bash
bun run db:seed                     # bun bin/app.ts db seed — server stopped on PGlite
bun bin/app.ts db seed <scenario>   # once the scenario argument is added
```

As scaffolded, `server/db/seed.ts` exports `ensureOwner` and `seedDemoData` (demo projects, tasks,
a welcome notification) and `db seed` takes no argument: `seedDemoData` is the example the
generated scenarios replace. Boot seeds only an empty database (it skips when projects exist),
so re-seeding a dev database goes through the CLI. `ensureOwner` stays: it creates the first
owner from `APP_OWNER_*` and is not scenario data.

## Codegen

None. The server-action catalogue is plain TypeScript: `useActions()` infers input and output
types from the action definitions, the MCP tool list and the `/api/actions` manifest are derived
at runtime, and Drizzle types come from the schema (`typeof table.$inferSelect`). The only
generated artefacts are migrations (`bun run db:generate`) and Nuxt's own `.nuxt/` types
(`postinstall: nuxt prepare`).

### Data: a new table is schema + `defineEntity`

CRUD is generic. `@skaile/forge-data` derives a model from the Drizzle schema and exposes every
annotated table through seven fixed actions (`server/utils/data.ts` wires model, backend and
service and registers them in the core list). A new table is a Drizzle table in
`server/db/schema/` plus one `defineEntity` in `server/db/model.ts`, added to `dataEntities`;
no per-table action, no hand-written form fields. Domain rules (defaults, derived values,
checks) go into hooks; derived counts and sort keys into `computed` (Drizzle `sql`).

```typescript
// server/db/model.ts
export const taskEntity = defineEntity(tasks, {
  name: 'tasks', label: 'Task', labelField: 'title',
  description: 'Work item inside a project. Complete it by setting status to done.', // read by agents
  scope: 'tasks',                                   // → tasks:read / tasks:write
  fields: {
    id: { readOnly: true }, description: { long: true },
    createdBy: { readOnly: true }, completedAt: { readOnly: true },
  },
  search: ['title', 'description'],
  defaultSort: [{ field: 'createdAt', order: 'desc' }],
  computed: {
    priorityRank: { type: 'integer', hidden: true, sortable: true,
      sql: t => sql`case ${t.priority} when 'high' then 3 when 'medium' then 2 else 1 end` },
  },
  ops: { delete: true },
  hooks: {
    async beforeCreate(values, ctx) {
      values.priority ??= (await getSettings(appSettings, dbOf(ctx))).defaultTaskPriority
      values.createdBy = actorUserId(ctx.principal as Principal)
      values.completedAt = values.status === 'done' ? ctx.now.toISOString() : null
    },
    beforeUpdate(changes, current, ctx) {
      if (changes.status === 'done') changes.completedAt ??= current.completedAt ?? ctx.now.toISOString()
      else if (changes.status !== undefined) changes.completedAt = null
    },
  },
})
```

Hidden fields stay unreachable through filter, sort, search and expand; `rowPolicy` restricts
rows per principal; hooks throw `DataError('invalid' | 'not_found' | ...)`, mapped to 400/404/….

| Action           | Kind   | Audience    | MCP tool              |
| ---------------- | ------ | ----------- | --------------------- |
| `data.describe`  | query  | user, llm   | `app_data_describe`   |
| `data.list`      | query  | user, llm   | `app_data_list`       |
| `data.get`       | query  | user, llm   | `app_data_get`        |
| `data.aggregate` | query  | user, llm   | `app_data_aggregate`  |
| `data.create`    | effect | user, llm   | `app_data_create`     |
| `data.update`    | effect | user, llm   | `app_data_update`     |
| `data.delete`    | effect | user only   | none: agents ask through `inbox.ask` |

Every call names the `entity`; `values` are validated per entity. Lists return
`{ items, total, limit, offset }` (`limit` ≤ 100), `expand: ['project']` adds `project: { id, label }`.
The filter is flat: `where` is AND, `anyOf` an OR of AND groups, fields may be one to-one path deep.

```bash
bun run cli actions data.list --json '{"entity":"tasks","where":[{"field":"status","op":"ne","value":"done"},{"field":"dueAt","op":"lt","value":"2026-11-06T00:00:00Z"}],"sort":[{"field":"priorityRank","order":"desc"}],"expand":["project"]}'
```

Operators: `eq ne gt gte lt lte in nin contains startsWith isNull notNull`. The UI goes through
`useData('tasks').list(q)`; the dashboard counts with `data.aggregate` (`groupBy: 'status'`).

### Bespoke actions: only for non-CRUD verbs

Tokens (hashing), settings, AI (`ai.*`), me, notifications, chat, inbox, jobs and the workspace
agent keep dedicated actions, and their tables are not exposed as entities. A new verb that is not
create/read/update/delete is one action:

```typescript
// server/utils/actions/<area>.ts
export const reportsExport = defineAppAction({
  id: 'reports.export',            // <area>.<verb>; MCP tool name app_reports_export
  kind: 'effect',                  // query | effect
  destructive: false,              // effects must state it: MCP destructiveHint
  idempotent: true,                // optional: repeating changes nothing (MCP idempotentHint)
  audience: ['user', 'llm'],       // 'llm' exposes it on MCP and as a chat tool; deletes → ['user']
  description: 'Export the project report as CSV. Use when the user asks for a report file.',
  input: z.object({ projectId: z.string().uuid() }).strict(),
  authorize: ctx => requireScope(ctx, 'projects:read'),
  run: async ({ projectId }, ctx) => { /* … */ },
})
```

Add it to the core list in `server/utils/actions/core.ts` (a layer calls `registerActions([...])`
in its own Nitro plugin) and it appears in the UI client, HTTP, MCP, CLI and chat at once.

### Other workspaces: the `app-data` connector

The in-app workspace agent reaches data through `/mcp`. Other SKAILE workspaces point at a
running app with the `app-data` connector shipped in `@skaile/forge-data`; it calls
`/api/actions/data.*` with an API token, so scopes, hooks and row policy stay in the app.

```yaml
# skaile.yaml
plugins: ['@skaile/forge-data@^0.2.0']
connectors:
  - id: app
    driver: app-data
    access: read-write             # or read-only
    options: { url: 'https://my-app.example.com' }
    auth: pat:env:APP_TOKEN        # an API token created in the app (tokens.*)
```

## Expert Skills

Optional, and nothing here depends on them. The `prog-expert-*` skills live in a different
collection (`ai-assets/dev-implementation-experts-*`) and `skaile.yaml` has no dependency
mechanism — glob discovery only, no `assets:` block — so this collection cannot install them
and cannot check for them. If one is installed, consult it; if it is not, carry on. No step in
any skill is gated on one being present.

- `prog-expert-nuxt` — Nuxt 4 routing, SSR hydration, composables, server routes, Nitro config, layers

## Key Implementation Patterns

**1. Every feature is a server action — never a bare API route.**
UI pages call `useActions().call('<id>', input)`; do not add `server/api/*.ts` handlers for
domain logic, or the feature silently disappears from MCP, CLI and chat. Custom routes are for
transport-level needs only (health, auth callbacks, file streams) and use `requirePrincipal(event)`.

**2. Descriptions are written for an LLM.**
`description` and Zod `.describe()` texts are what agents read on MCP and in chat. Say when to use
the action, not what the code does. Inputs are `.strict()`.

**3. Audience is the security boundary for agents.**
`audience: ['user']` keeps destructive actions (deletes, token revocation) off MCP and chat tools.
`authorize` still runs for every surface; the chat acts with the signed-in person's principal.
An effect must declare `destructive` (`true` when it deletes, revokes, stops or overwrites
values, `false` when it only adds or flips a flag) and may add `idempotent: true`. MCP clients
get them as tool annotations (queries: `readOnlyHint` alone), the HTTP manifest lists them;
they authorize nothing.

**4. Settings are scopes, not env vars.**
Product settings use `defineSettingsScope(name, z.object({...}).strict(), defaults)` in
`server/utils/settings.ts`; `settings.get` / `settings.update` and `<SchemaForm>` render and save
them, so they are reachable over every surface. A scope only an action may change declares
`managedBy` (`settings.update` refuses it). Env (`runtimeConfig`) is for secrets and infra only.

**5. Optional capabilities are layers.**
`layers/<name>/` with its own `nuxt.config.ts`, `app/`, `server/`, `app.config.ts` nav entries and
`registerActions(...)` plugin. Core never imports from a layer; deleting the folder must leave a
working app. PGlite allows one process per data directory: run admin commands through
`bun run cli actions ...` while the dev server holds it.

**6. Models are roles, chosen in Settings › AI.**
Which model answers is not a setting of the consumer. A layer declares a *model role*
(`registerModelRole({ id, kind, label, description, enabled }, { status? })` in its server plugin:
chat layer `assistant`, workspace-agent layer `agent`) and resolves it per use with
`resolveRoleModel(id)`; owners assign `<provider>/<model>` per role in the core page
`/settings/ai`, next to the provider registry and its keys (`.data/ai`, `AI_PROVIDER_<NAME>`), all
through `ai.*` actions (audience `user`, never MCP or chat tools). An unassigned chat role falls
back to `NUXT_AI_BASE_URL` / `NUXT_AI_API_KEY` / `NUXT_AI_MODEL`. The `decision`, `image`, `tts`
and `stt` roles of `@skaile/forge-settings` exist and are switched off. Consumer knobs (the
assistant's prompt addendum) are their own settings scope, shown on the AI page through
`shell.settingsSections`.
