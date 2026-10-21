---
path: _concept/02_grounding/findings/routes.md
summary: every route or endpoint, the file defining it, what a user does there
owner: [concept-reverse]
may_propose: []
---

# _concept/02_grounding/findings/routes.md

Every route or endpoint the app exposes, as evidence for the journeys and featuresets. Routes
are evidence, not features: a feature file listing API paths describes the server rather than
the user.

## Format

Frontmatter per `tree/02_grounding/findings/README.md`. One entry per route: the route, the file
that defines it, and what a user does there, kept in user terms — the route is the citation, what
the user can do is the finding. Routes recovered from component names because there is no router
are `inferred`, and the report says so.

## Writing it

Discover routes in priority order:

1. **Router definitions** — `src/router/`, `app/router.ts`, Next.js `app/**/page.tsx` or
   `pages/**/*.tsx`, Nuxt `pages/**/*.vue`, SvelteKit `src/routes/**/+page.svelte`, Rails
   `config/routes.rb`, Django `urls.py`, FastAPI router registrations.
2. **API route handlers** — `server/api/`, `api/`, `routes/`, `controllers/`, and
   `app.get(…)` / `router.post(…)` call sites.
3. **Navigation components** — sidebar, navbar and breadcrumb components, which name the
   destinations a user is actually offered and so tell a real screen from a route nothing links to.

File-system routers give the route from the path; explicit routers give it from the registration.

## Checks

Every entry cites its defining file, which exists on disk.
