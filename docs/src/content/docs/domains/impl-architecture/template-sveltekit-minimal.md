---
title: "template-sveltekit-minimal"
description: "Reference document and invocable skill for the SvelteKit 2 + Svelte 5 + Tailwind + Drizzle + SQLite stack. Read by scaffold, foundation, design, mock, and storybook skills when 05_techstack/stack.md selects this stack."
sidebar:
  label: "template-sveltekit-minimal"
---

:::note[Skill manifest]
**Name:** `template-sveltekit-minimal`
**Stage:** alpha · **Version:** —
**Tags:** sveltekit, svelte5, tailwind, drizzle, sqlite, adapter-node, oslojs, bun, minimal, personal, blog, tool, prototype, learning
**Source:** [`skaileup/impl-architecture/templates/template-sveltekit-minimal/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/impl-architecture/templates/template-sveltekit-minimal/SKILL.md)
:::


# Tech Stack: SvelteKit 2 Minimal (Svelte 5 + Tailwind + Drizzle + SQLite)

## Overview

Lightweight full-stack application built entirely with SvelteKit 2 and Svelte 5
runes — no external backend, no managed service. The frontend is Svelte 5 with
Tailwind CSS 4 (no component library). The backend is SvelteKit's built-in
server (`+page.server.ts` load functions and `+server.ts` API routes) running
on `@sveltejs/adapter-node`, with Drizzle ORM writing to a local SQLite
database. Authentication is hand-rolled session cookies using `@oslojs/crypto`
for token hashing — the canonical post-Lucia pattern. Zero external
dependencies at runtime beyond the Node/Bun process — ideal for personal
projects, internal tools, blogs, simple utilities, and rapid learning
prototypes that don't need enterprise-scale infrastructure.

## Identity

| Field           | Value                                                                          |
| --------------- | ------------------------------------------------------------------------------ |
| Frontend        | SvelteKit 2 (Svelte 5 runes), SSR                                              |
| UI Library      | Tailwind CSS 4 (no component library — custom components only)                 |
| Backend         | SvelteKit server (`+page.server.ts` actions, `+server.ts` API routes)          |
| Database        | SQLite (via Drizzle ORM + `better-sqlite3`)                                    |
| Auth            | Hand-rolled session cookies (`@oslojs/crypto` hashing, sessions in Drizzle)    |
| ORM / DB Access | Drizzle ORM + Drizzle Kit                                                      |
| Adapter         | `@sveltejs/adapter-node`                                                       |
| Package Manager | bun                                                                            |
| CSS Methodology | Tailwind CSS 4 with `@theme` CSS custom properties                             |

## When to Use

- Best for: personal projects, blogs, portfolios, internal tools, simple CRUD apps
- Best for: developers who prefer Svelte's reactive primitives over Vue/React
- Best for: rapid prototypes where a deployed SQLite file is sufficient
- Best for: single-developer projects with light load
- Best for: apps that need to run as a single process (Docker-friendly, fly.io, Coolify)
- Avoid when: you expect concurrent writes at scale — SQLite is single-writer; switch to PostgreSQL
- Avoid when: multiple service instances need to share data — SQLite is file-local; use Turso (libSQL) or migrate to PostgreSQL
- Avoid when: you need a rich component library out of the box — there is none here; build everything from scratch or pick a stack with one
- Avoid when: the team has zero Svelte experience and tight deadlines — Svelte 5 runes have a learning curve

## Scaffold Recipe

```bash
# 1. Initialize SvelteKit 2 project (skeleton template, TypeScript, ESLint, Prettier)
bunx sv@latest create . --template minimal --types ts --no-add-ons

# 2. Install runtime dependencies
bun add drizzle-orm better-sqlite3 @oslojs/crypto @oslojs/encoding

# 3. Install dev dependencies
bun add -d drizzle-kit @types/better-sqlite3 tailwindcss @tailwindcss/vite

# 4. Install the Node adapter (default skeleton ships adapter-auto)
bun add -d @sveltejs/adapter-node

# 5. Configure svelte.config.js (see snippet below)

# 6. Configure vite.config.ts to load Tailwind plugin

# 7. Create database schema at src/lib/server/db/schema.ts

# 8. Generate and apply first migration
bun drizzle-kit generate
bun drizzle-kit migrate

# 9. Run dev server
bun run dev
```

`svelte.config.js`:

```javascript
import adapter from '@sveltejs/adapter-node'
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte'

// Skaile workspace preview injects SKAILE_PREVIEW_BASE = '/preview/<sid>/'.
// SvelteKit wants paths.base WITHOUT a trailing slash, with a leading slash,
// or "" — strip the trailing slash so '/preview/<sid>/' becomes
// '/preview/<sid>'. Falls back to '' for normal local dev / production.
const previewBase = (process.env.SKAILE_PREVIEW_BASE ?? '').replace(/\/+$/, '')

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter(),
    paths: { base: previewBase },
  },
}

export default config
```

`vite.config.ts`:

```typescript
import { sveltekit } from '@sveltejs/kit/vite'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
})
```

`.env`:

```bash
SESSION_SECRET=replace-with-32-char-random-secret-string
DB_PATH=./data/app.db
```

`drizzle.config.ts`:

```typescript
import { defineConfig } from 'drizzle-kit'

export default defineConfig({
  schema: './src/lib/server/db/schema.ts',
  out: './src/lib/server/db/migrations',
  dialect: 'sqlite',
  dbCredentials: {
    url: process.env.DB_PATH ?? './data/app.db',
  },
})
```

## Preview Compatibility

Apps generated by this profile run in the Skaile workspace's preview iframe at
`/preview/<session-id>/`. SvelteKit needs **two** things to be preview-ready —
the `paths.base` config above (already wired), **and** a navigation wrapper.
Unlike Next/Nuxt, SvelteKit's `goto('/foo')` does **not** auto-prepend
`paths.base`; the app code has to do it itself, otherwise bare paths look
external to SvelteKit's router and trigger a hard `location.href = ...`
that escapes the iframe.

Ship these two files alongside the scaffold:

**`src/lib/nav.ts`:**

```typescript
import { goto as svelteGoto } from '$app/navigation'
import { base } from '$app/paths'

/**
 * Wraps SvelteKit's `goto` to auto-prepend the configured base path so
 * internal navigation works behind the Skaile preview proxy or any subpath
 * deploy.
 *
 * Pass-through for absolute URLs (`https://...`, `mailto:...`, `//cdn/...`)
 * and paths that already include the base (idempotent — safe to double-call).
 */
export function goto(
  path: string,
  opts?: Parameters<typeof svelteGoto>[1],
): ReturnType<typeof svelteGoto> {
  if (/^[a-z][a-z0-9+.-]*:|^\/\//i.test(path)) return svelteGoto(path, opts)
  if (base && (path === base || path.startsWith(`${base}/`))) {
    return svelteGoto(path, opts)
  }
  const normalized = path.startsWith('/') ? path : `/${path}`
  return svelteGoto(`${base}${normalized}`, opts)
}
```

**`src/lib/Link.svelte`** (SvelteKit doesn't ship a `<Link>` component; bare
`<a href>` is what you get otherwise):

```svelte
<script lang="ts">
  import { base } from '$app/paths'

  let { href, children, ...rest } = $props<{ href: string; children: unknown }>()

  const resolved = $derived(
    /^[a-z][a-z0-9+.-]*:|^\/\//i.test(href)
      ? href
      : base && (href === base || href.startsWith(`${base}/`))
        ? href
        : `${base}${href.startsWith('/') ? href : `/${href}`}`,
  )
</script>

<a href={resolved} {...rest}>{@render children()}</a>
```

**Conventions in app code (non-negotiable):**

- Always import `goto` from `$lib/nav`, never from `$app/navigation` directly.
- Use `<Link href="/dashboard">` from `$lib/Link.svelte` instead of raw
  `<a href>` for in-app navigation.
- Never use `window.location.href = '/foo'` or `window.location.assign(...)` —
  `Location` is `[LegacyUnforgeable]` and the proxy cannot intercept it.
- Reach API routes via path-relative `fetch('/api/users')` — the proxy fans
  `/preview/<sid>/api/...` out to the same SvelteKit server.

See `contracts/preview_compatibility.md` for the full
contract, anti-patterns, and the underlying browser limit that forces this
discipline.

## CSS Variables / Theming

Pure Tailwind CSS 4 with no component library. Brand tokens from
`04_brand/tokens.json` map directly to CSS custom properties in the `@theme`
block.

**`src/app.css`:**

```css
@import 'tailwindcss';

@theme {
  /* Colors from tokens.json */
  --color-primary-50: {tokens.color.primary.50};
  --color-primary-100: {tokens.color.primary.100};
  --color-primary-500: {tokens.color.primary.500};
  --color-primary-600: {tokens.color.primary.600};
  --color-primary-700: {tokens.color.primary.700};
  --color-primary-900: {tokens.color.primary.900};

  --color-neutral-50: {tokens.color.neutral.50};
  --color-neutral-100: {tokens.color.neutral.100};
  --color-neutral-500: {tokens.color.neutral.500};
  --color-neutral-900: {tokens.color.neutral.900};

  --color-success: {tokens.color.success};
  --color-warning: {tokens.color.warning};
  --color-error: {tokens.color.error};

  /* Typography from tokens.json */
  --font-sans: {tokens.typography.fontFamily.sans};
  --font-mono: {tokens.typography.fontFamily.mono};
  --text-base: {tokens.typography.fontSize.base};

  /* Border radius from tokens.json */
  --radius-sm: {tokens.borderRadius.sm};
  --radius-md: {tokens.borderRadius.md};
  --radius-lg: {tokens.borderRadius.lg};

  /* Shadows from tokens.json */
  --shadow-sm: {tokens.shadow.sm};
  --shadow-md: {tokens.shadow.md};
}

/* Light/dark semantic aliases */
:root {
  --bg: var(--color-white);
  --bg-raised: var(--color-neutral-50);
  --fg: var(--color-neutral-900);
  --fg-muted: var(--color-neutral-500);
  --border: var(--color-neutral-200);
}

.dark {
  --bg: var(--color-neutral-950);
  --bg-raised: var(--color-neutral-900);
  --fg: var(--color-neutral-50);
  --fg-muted: var(--color-neutral-400);
  --border: var(--color-neutral-800);
}

@layer components {
  .btn-primary {
    @apply inline-flex items-center px-4 py-2 bg-primary-500 text-white rounded-md
           hover:bg-primary-600 focus-visible:outline-none focus-visible:ring-2
           focus-visible:ring-primary-500 focus-visible:ring-offset-2 transition-colors;
  }
  .card {
    @apply bg-bg-raised border border-border rounded-lg shadow-sm p-6;
  }
  .input {
    @apply w-full rounded-md border border-border bg-bg px-3 py-2 text-sm
           focus:outline-none focus:ring-2 focus:ring-primary-500;
  }
}
```

Import once from the root layout:

```svelte
<!-- src/routes/+layout.svelte -->
<script lang="ts">
  import '../app.css'
  let { children } = $props()
</script>

{@render children()}
```

Token mapping table:
| `tokens.json` key | CSS custom property | Tailwind class |
|-------------------|---------------------|-|
| `color.primary.*` | `--color-primary-*` | `bg-primary-500` |
| `typography.fontFamily.sans` | `--font-sans` | `font-sans` |
| `borderRadius.md` | `--radius-md` | `rounded-md` |
| `color.error` | `--color-error` | `text-error` |

## Auth Setup

Hand-rolled session cookies using `@oslojs/crypto` for token hashing
(the canonical post-Lucia pattern). Sessions are stored in a Drizzle table
keyed by a hashed token; the cookie carries the unhashed token.

**`src/lib/server/auth.ts`:**

```typescript
import { sha256 } from '@oslojs/crypto/sha2'
import { encodeBase32LowerCaseNoPadding, encodeHexLowerCase } from '@oslojs/encoding'
import { db } from '$lib/server/db'
import { sessions, users } from '$lib/server/db/schema'
import { eq } from 'drizzle-orm'

const DAY_IN_MS = 1000 * 60 * 60 * 24
const SESSION_TTL_DAYS = 30

export const sessionCookieName = 'session'

export function generateSessionToken(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(20))
  return encodeBase32LowerCaseNoPadding(bytes)
}

export async function createSession(token: string, userId: string) {
  const sessionId = encodeHexLowerCase(sha256(new TextEncoder().encode(token)))
  const session = {
    id: sessionId,
    userId,
    expiresAt: new Date(Date.now() + DAY_IN_MS * SESSION_TTL_DAYS),
  }
  await db.insert(sessions).values(session)
  return session
}

export async function validateSessionToken(token: string) {
  const sessionId = encodeHexLowerCase(sha256(new TextEncoder().encode(token)))
  const result = await db
    .select({ user: users, session: sessions })
    .from(sessions)
    .innerJoin(users, eq(sessions.userId, users.id))
    .where(eq(sessions.id, sessionId))
    .limit(1)
  if (result.length === 0) return { session: null, user: null }
  const { session, user } = result[0]
  if (Date.now() >= session.expiresAt.getTime()) {
    await db.delete(sessions).where(eq(sessions.id, session.id))
    return { session: null, user: null }
  }
  // Sliding expiration: extend if more than half-life remains
  if (Date.now() >= session.expiresAt.getTime() - (DAY_IN_MS * SESSION_TTL_DAYS) / 2) {
    session.expiresAt = new Date(Date.now() + DAY_IN_MS * SESSION_TTL_DAYS)
    await db
      .update(sessions)
      .set({ expiresAt: session.expiresAt })
      .where(eq(sessions.id, session.id))
  }
  return { session, user }
}

export async function invalidateSession(sessionId: string) {
  await db.delete(sessions).where(eq(sessions.id, sessionId))
}
```

**`src/hooks.server.ts`:**

```typescript
import type { Handle } from '@sveltejs/kit'
import { sessionCookieName, validateSessionToken } from '$lib/server/auth'

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get(sessionCookieName)
  if (!token) {
    event.locals.user = null
    event.locals.session = null
    return resolve(event)
  }
  const { session, user } = await validateSessionToken(token)
  event.locals.user = user
  event.locals.session = session
  return resolve(event)
}
```

**`src/app.d.ts`** (augment locals):

```typescript
declare global {
  namespace App {
    interface Locals {
      user: { id: string; email: string; name: string } | null
      session: { id: string; expiresAt: Date } | null
    }
  }
}

export {}
```

**`src/routes/login/+page.server.ts`** (form action):

```typescript
import { fail, redirect } from '@sveltejs/kit'
import { eq } from 'drizzle-orm'
import { db } from '$lib/server/db'
import { users } from '$lib/server/db/schema'
import {
  createSession,
  generateSessionToken,
  sessionCookieName,
} from '$lib/server/auth'
import { verifyPasswordHash } from '$lib/server/password'
import type { Actions } from './$types'

export const actions: Actions = {
  default: async ({ request, cookies }) => {
    const data = await request.formData()
    const email = String(data.get('email') ?? '')
    const password = String(data.get('password') ?? '')
    const [user] = await db.select().from(users).where(eq(users.email, email))
    if (!user || !(await verifyPasswordHash(password, user.passwordHash))) {
      return fail(401, { message: 'Invalid credentials' })
    }
    const token = generateSessionToken()
    const session = await createSession(token, user.id)
    cookies.set(sessionCookieName, token, {
      path: '/',
      httpOnly: true,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
      expires: session.expiresAt,
    })
    redirect(303, '/dashboard')
  },
}
```

Use `event.locals.user` in `+page.server.ts` and `+layout.server.ts` load
functions to gate access:

```typescript
import { redirect } from '@sveltejs/kit'
import type { LayoutServerLoad } from './$types'

export const load: LayoutServerLoad = async ({ locals }) => {
  if (!locals.user) redirect(303, '/login')
  return { user: locals.user }
}
```

> **Important:** the `redirect(303, '/dashboard')` calls above use a bare path
> on purpose — SvelteKit's server-side `redirect()` emits a relative
> `Location` header that the Skaile preview proxy rewrites on the way back
> through. Client-side `goto` calls must use the `$lib/nav` wrapper instead.

## App Shell

SvelteKit layouts are thin for this stack — typically a single
`src/routes/+layout.svelte` with header, content, and footer.

**`src/routes/+layout.svelte`:**

```svelte
<script lang="ts">
  import '../app.css'
  import AppHeader from '$lib/components/AppHeader.svelte'
  let { children } = $props()
</script>

<div class="min-h-screen flex flex-col bg-bg text-fg">
  <AppHeader />
  <main class="flex-1 container mx-auto px-4 py-8 max-w-5xl">
    {@render children()}
  </main>
  <footer class="border-t border-border py-6 text-center text-sm text-fg-muted">
    &copy; {new Date().getFullYear()}
  </footer>
</div>
```

For dashboard-style apps with a sidebar, use a nested layout at
`src/routes/(app)/+layout.svelte`.

## Component Library

There is no external component library. Build a small set of reusable
Svelte components in `src/lib/components/`:

| Generic UI concept | Custom component                         | Notes                                      |
| ------------------ | ---------------------------------------- | ------------------------------------------ |
| Button             | `src/lib/components/Button.svelte`       | Accepts `variant`, `size`, `loading` props |
| DataTable          | `src/lib/components/Table.svelte`        | Simple `<table>` wrapper with snippet rows |
| Modal/Dialog       | `src/lib/components/Dialog.svelte`       | HTML `<dialog>` element + Tailwind         |
| Form Input         | `src/lib/components/Input.svelte`        | Input + label + error message              |
| Select/Dropdown    | `src/lib/components/Select.svelte`       | Native `<select>` styled with Tailwind     |
| Navigation         | `src/lib/components/AppNav.svelte`       | `<Link>` list with `aria-current` styling  |
| Card               | `src/lib/components/Card.svelte`         | `<div class="card">` wrapper with snippets |
| Toast/Notification | `src/lib/stores/toast.svelte.ts`         | Svelte 5 rune-based store + portal         |
| Anchor link        | `src/lib/Link.svelte`                    | **Required** — base-aware `<a>` (above)    |

> Keep this component set small. If component complexity grows significantly,
> consider switching to a stack with a component library (e.g.
> nuxt-ui, nextjs-shadcn) or pulling in `bits-ui`/`shadcn-svelte`.

## Mock Adaptation

The mock skill uses CDN-based HTML templates. This stack's Tailwind-only
styling is closest to **`alpine_shoelace`** — both are minimal and rely on
utility classes rather than a heavy component library.

```yaml
mock_template: alpine_shoelace
```

Note: The mock uses Shoelace components as placeholders. The actual
implementation replaces Shoelace with custom Svelte components styled with
Tailwind. Structural layout intent is preserved.

## Storybook Config

```yaml
storybook_addon: '@storybook/svelte'
story_format: Svelte component (.stories.svelte)
component_import: '$lib/components'
setup_file: .storybook/preview.ts
```

**`.storybook/main.ts`:**

```typescript
export default {
  framework: '@storybook/sveltekit',
  stories: ['../src/lib/components/**/*.stories.svelte'],
  addons: ['@storybook/addon-essentials'],
}
```

**`.storybook/preview.ts`:**

```typescript
import '../src/app.css' // brand tokens via @theme
import type { Preview } from '@storybook/svelte'

export default {
  parameters: { backgrounds: { default: 'light' } },
} satisfies Preview
```

Write stories for `src/lib/components/` only. Server-side load functions
and `+server.ts` API routes are not testable in Storybook.

## Migration / ORM

Drizzle ORM with Drizzle Kit manages SQLite migrations.

**`src/lib/server/db/schema.ts`:**

```typescript
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core'

export const users = sqliteTable('users', {
  id: text('id')
    .primaryKey()
    .$defaultFn(() => crypto.randomUUID()),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  passwordHash: text('password_hash').notNull(),
  createdAt: integer('created_at', { mode: 'timestamp' })
    .$defaultFn(() => new Date())
    .notNull(),
  updatedAt: integer('updated_at', { mode: 'timestamp' })
    .$defaultFn(() => new Date())
    .notNull(),
})

export const sessions = sqliteTable('sessions', {
  id: text('id').primaryKey(), // hashed token (sha256 hex)
  userId: text('user_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  expiresAt: integer('expires_at', { mode: 'timestamp' }).notNull(),
})
```

**`src/lib/server/db/index.ts`:**

```typescript
import { drizzle } from 'drizzle-orm/better-sqlite3'
import Database from 'better-sqlite3'
import * as schema from './schema'

const sqlite = new Database(process.env.DB_PATH ?? './data/app.db')
sqlite.pragma('journal_mode = WAL')
sqlite.pragma('foreign_keys = ON')
export const db = drizzle(sqlite, { schema })
```

**Migration commands:**

```bash
# Generate migration SQL from schema changes
bun drizzle-kit generate

# Apply pending migrations
bun drizzle-kit migrate

# Inspect current schema
bun drizzle-kit introspect

# Open Drizzle Studio (browser DB viewer)
bun drizzle-kit studio
```

Migration files are stored in `src/lib/server/db/migrations/` and committed
to version control. Never edit migration files after they have been applied.

## Codegen

None. Drizzle ORM generates TypeScript types directly from the schema file —
no codegen step required:

```typescript
import type { InferSelectModel, InferInsertModel } from 'drizzle-orm'
import { users } from '$lib/server/db/schema'

type User = InferSelectModel<typeof users>
type NewUser = InferInsertModel<typeof users>
```

## Expert Skills

Which `prog-expert-*` skills to look for:

- `prog-expert-sveltekit` — SvelteKit 2 routing, load functions, form actions, SSR, hooks, Svelte 5 runes (when this expert exists; fall back to general Svelte/Vite knowledge until then)

## Key Implementation Patterns

**1. `+page.server.ts` for all server-side data:**
All backend logic lives in `+page.server.ts` (page-scoped) or `+server.ts`
(API endpoints). Use load functions for reads and form actions for
writes — they integrate with SvelteKit's progressive enhancement out of
the box.

```typescript
// src/routes/posts/+page.server.ts
import { db } from '$lib/server/db'
import { posts } from '$lib/server/db/schema'
import { desc } from 'drizzle-orm'
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async () => {
  return { posts: await db.select().from(posts).orderBy(desc(posts.createdAt)) }
}
```

**2. Auth check in `+layout.server.ts` for protected route groups:**
Group protected routes under `src/routes/(app)/` and gate them in
`(app)/+layout.server.ts`. The `(app)` is a layout group — it does not
appear in the URL.

```typescript
// src/routes/(app)/+layout.server.ts
import { redirect } from '@sveltejs/kit'
import type { LayoutServerLoad } from './$types'

export const load: LayoutServerLoad = async ({ locals }) => {
  if (!locals.user) redirect(303, '/login')
  return { user: locals.user }
}
```

**3. SQLite WAL mode for better concurrency:**
Enable Write-Ahead Logging immediately after opening the database
connection (already in the `index.ts` snippet above). Critical for any app
with concurrent reads and writes.

**4. Keep data directory outside the project for Docker deployments:**
Mount `DB_PATH` as a Docker volume. Use an absolute path or a path outside
the app directory to avoid losing data on container rebuild:

```dockerfile
VOLUME ["/data"]
ENV DB_PATH=/data/app.db
```

**5. Use form actions over JSON API endpoints when possible:**
SvelteKit's `<form method="POST">` + `+page.server.ts` actions give
progressive enhancement, automatic CSRF protection, and built-in error
handling. Only reach for `+server.ts` JSON endpoints when the client is
not a SvelteKit page (mobile app, third-party integration, etc.).

**6. Use `$lib/nav` everywhere — never `$app/navigation` directly:**
Add an ESLint rule (or a code review checklist item) to forbid imports
from `$app/navigation`. This is the only way to guarantee preview
compatibility doesn't regress when a contributor reaches for `goto`.

