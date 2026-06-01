# Preview Compatibility Contract

> **Audience:** authors of stack profiles in `09_impl-architecture/templates/` and
> AI agents running the `impl-build-scaffold` / `impl-build-foundation`
> skills.
> **Used by:** every `template-*` profile that targets a web
> framework (Next.js, Nuxt, SvelteKit, Vite + router).

This is the canonical recipe set for making generated apps run inside the
Skaile workspace's preview iframe. The platform side of the contract (the
proxy that mounts each session at `/preview/<session-id>/...` and the env vars
it injects) is defined in the `platform` repo; this document captures
everything an app needs to do to satisfy that contract.

A copy of this guide is also published as user-facing docs at
`platform/docs/preview-app-compatibility.md`. The two are kept in sync
deliberately so app authors and skill authors read from the same source.

## TL;DR — what every preview-ready app needs

To run cleanly in the workspace preview, an app must:

1. **Read its base path from `SKAILE_PREVIEW_BASE`** in its framework config —
   Vite `base`, SvelteKit `paths.base`, Next `basePath`, Nuxt `app.baseURL`.
2. **Use base-aware navigation primitives** — the framework's `<Link>` /
   `router.push()` / `goto()` / `navigateTo()`. Never bare `<a href="/foo">`
   or `window.location.href = '/foo'`.
3. **Use path-relative API calls** — `fetch('/api/users')`, never hardcoded
   `fetch('http://localhost:8000/users')`.

Profiles that scaffold preview-ready apps must inject (1) into the relevant
config file at scaffold time, document (2) and (3) in their convention rules,
and ship a `nav.ts`-style helper for any framework that doesn't auto-prepend
the base path (currently SvelteKit only).

## Why this isn't automatic

Browsers enforce `Location` and all its members as `[LegacyUnforgeable]` per
the WebIDL spec — `location.pathname`, `location.href`, `location.assign(...)`,
`location.replace(...)` cannot be redefined from JavaScript. The Skaile
preview proxy injects a small client-side patch that wraps `history.pushState`
/ `history.replaceState` / `fetch` / `WebSocket` / `XMLHttpRequest.open`, but
it *cannot* intercept `Location` reads or writes.

Consequence: if an app reads `location.pathname` directly to make routing
decisions, or writes `window.location.href = '/foo'` to navigate, the proxy
can't help. The framework has to be told about its base path, and the
framework's own router has to handle it.

## Environment variables the preview manager injects

Every preview container runs with these set:

| Env var | Example value | What it's for |
|---|---|---|
| `SKAILE_PREVIEW_BASE` | `/preview/8a3f.../` (FE) or `/preview/8a3f.../api/` (BE) | The proxy path this role is mounted under, **with trailing slash** |
| `SKAILE_PREVIEW_ROLE` | `frontend` \| `backend` | Which role this container is serving |
| `SKAILE_PREVIEW_SESSION_ID` | `8a3f...` | Raw session UUID, in case the app needs it |

Outside preview (production deploys, plain `bun run dev` locally), the env
vars are unset. Configs **must** fall back to `'/'` (or empty string when the
framework expects no base path) — never crash if the var is missing.

## Per-framework recipes

### SvelteKit

SvelteKit needs **two** things: the config, and a navigation wrapper. Unlike
Next/Nuxt, SvelteKit's `goto('/foo')` does **not** auto-prepend `paths.base` —
the app code has to do it itself.

**`svelte.config.js`:**

```js
import adapter from "@sveltejs/adapter-node";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

// SvelteKit wants paths.base WITHOUT trailing slash, with leading slash, or "".
const previewBase = (process.env.SKAILE_PREVIEW_BASE ?? "").replace(/\/+$/, "");

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter(),
    paths: { base: previewBase },
  },
};

export default config;
```

**`src/lib/nav.ts`** (or wherever app utilities live):

```ts
import { goto as svelteGoto } from "$app/navigation";
import { base } from "$app/paths";

/**
 * Wraps SvelteKit's `goto` to auto-prepend the configured base path so
 * internal navigation works behind a preview proxy or any subpath deploy.
 *
 * Pass-through for absolute URLs (`https://...`, `mailto:...`, `//cdn/...`)
 * and paths that already include the base (idempotent — safe to double-call).
 */
export function goto(
  path: string,
  opts?: Parameters<typeof svelteGoto>[1],
): ReturnType<typeof svelteGoto> {
  if (/^[a-z][a-z0-9+.-]*:|^\/\//i.test(path)) return svelteGoto(path, opts);
  if (base && (path === base || path.startsWith(`${base}/`))) {
    return svelteGoto(path, opts);
  }
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return svelteGoto(`${base}${normalized}`, opts);
}
```

**`src/lib/Link.svelte`** for in-app anchors (SvelteKit doesn't ship a
`<Link>` component; bare `<a href>` is what you get):

```svelte
<script lang="ts">
  import { base } from "$app/paths";

  let { href, children, ...rest } = $props<{ href: string; children: unknown }>();

  const resolved = $derived(
    /^[a-z][a-z0-9+.-]*:|^\/\//i.test(href)
      ? href
      : base && (href === base || href.startsWith(`${base}/`))
        ? href
        : `${base}${href.startsWith("/") ? href : `/${href}`}`,
  );
</script>

<a href={resolved} {...rest}>{@render children()}</a>
```

**Convention** in the app code:

- Always import `goto` from `$lib/nav`, never from `$app/navigation` directly.
- Use `<Link>` from `$lib/Link.svelte` instead of raw `<a href>`.
- Done. `goto('/dashboard')` and `<Link href="/dashboard">` both resolve
  correctly in preview *and* in production.

### Next.js

Next's `<Link>` and `useRouter().push()` are already base-aware once
`basePath` is set — no helpers needed.

**`next.config.js`:**

```js
const previewBase = (process.env.SKAILE_PREVIEW_BASE ?? "").replace(/\/+$/, "");

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Empty string disables Next's basePath; falsy values must be `undefined`
  // (not `''`) — passing an empty string trips Next's config validator.
  basePath: previewBase || undefined,
};

export default nextConfig;
```

In app code: keep using `<Link href="/dashboard">` and
`router.push('/dashboard')` as normal. Next prepends `basePath` automatically.

### Nuxt

Nuxt's `<NuxtLink>` and `navigateTo()` are already base-aware once
`app.baseURL` is set — no helpers needed.

**`nuxt.config.ts`:**

```ts
export default defineNuxtConfig({
  app: {
    // Nuxt expects a value WITH trailing slash, defaulting to "/".
    baseURL: process.env.SKAILE_PREVIEW_BASE ?? "/",
  },
});
```

In app code: keep using `<NuxtLink to="/dashboard">` and
`await navigateTo('/dashboard')` as normal. Nuxt prepends `baseURL`
automatically.

### Vite + React Router

For an SPA bundled by Vite, the asset base path is set on Vite, and the
router gets its own base via `basename`.

**`vite.config.ts`:**

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: process.env.SKAILE_PREVIEW_BASE ?? "/",
});
```

**`src/main.tsx`:**

```tsx
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  // import.meta.env.BASE_URL is what Vite injects for `base` above —
  // strip the trailing slash for React Router's `basename`.
  <BrowserRouter basename={import.meta.env.BASE_URL.replace(/\/+$/, "")}>
    <App />
  </BrowserRouter>,
);
```

In app code: `<Link to="/dashboard">` and `navigate('/dashboard')` work
normally; React Router prepends `basename` automatically.

### Vite (no router)

For a plain Vite SPA without a client-side router, only the asset base needs
configuring:

```ts
// vite.config.ts
export default defineConfig({
  base: process.env.SKAILE_PREVIEW_BASE ?? "/",
});
```

Vite rewrites `<script src="/x.js">`, `<link href="/y.css">`, and `import` /
`new URL()` literals at build time. Asset URLs come out correct in both
preview and production. There's nothing to do for navigation because there
is none.

## Anti-patterns — what doesn't work

| Don't | Do | Why |
|---|---|---|
| `goto('/foo')` (SvelteKit, bare) | `goto(\`${base}/foo\`)` or `$lib/nav` wrapper | SvelteKit's `goto` doesn't auto-prepend `paths.base`; bare `/foo` looks external to SvelteKit's router and triggers a hard `location.href = ...` that escapes the iframe |
| `<a href="/foo">` in any framework | Framework `<Link>` / `<NuxtLink>` / `<a href="{base}/foo">` | Browser navigation through a bare `<a>` doesn't go through SPA routers — it does a full page load that, on `/foo`, escapes the iframe |
| `window.location.href = '/foo'` | Framework `goto` / `router.push` / `navigateTo` | `Location.href` is `[LegacyUnforgeable]` — the proxy's client patch cannot intercept this |
| `window.location.assign('/foo')` | Same | Same reason |
| `fetch('http://localhost:8000/users')` | `fetch('/api/users')` | Hardcoded host bypasses the preview proxy entirely; backend-only previews depend on the `/api` prefix routing |
| Hardcoded API base in env | `import.meta.env.VITE_API_BASE` defaulting to `'/api'` | Path-relative survives both preview and production behind a reverse proxy |

## What the proxy *can* patch

For completeness — these don't need help from the app, the proxy's injected
client patch handles them:

- `history.pushState` / `history.replaceState` — SPA-internal navigations
  stay inside the preview base
- `fetch` — relative URLs are rewritten to the preview base
- `new WebSocket()` — same
- `XMLHttpRequest.prototype.open` — same
- ES module `import()` specifier resolution — via injected
  `<script type="importmap">`
- HTTP redirect `Location` headers from the server — rewritten on the way
  back through the proxy

## Limits accepted

Apps that absolutely require unmodifiable hard navigation through `location`
cannot be made preview-compatible without code changes. The "deploy mode"
roadmap mentions a subdomain-per-session preview as a future option that
would sidestep this entirely (each session gets its own origin, no path
prefix needed) — but that's not the path-prefix preview's mandate.

## Profile authors — checklist

When writing or updating a `template-*` profile that targets a
web framework, ensure:

- [ ] The Scaffold Recipe injects the relevant `SKAILE_PREVIEW_BASE` read
  into the generated framework config file
- [ ] The fall-back value is correct for the framework (`'/'` for Nuxt,
  `undefined` for Next, `""` after trim for SvelteKit, `'/'` for Vite)
- [ ] A "Preview Compatibility" section in the profile names this contract
  and shows the exact config snippet
- [ ] Anti-patterns relevant to the framework are listed (bare `goto`,
  bare `<a href>`, hardcoded `localhost` fetch URLs)
- [ ] For SvelteKit specifically: the profile ships `src/lib/nav.ts` and
  `src/lib/Link.svelte` and codifies "always import `goto` from `$lib/nav`"
  as a convention rule
