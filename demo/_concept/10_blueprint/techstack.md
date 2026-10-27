---
platform: web
framework: Nuxt 4
frontend: Nuxt 4 (Vue 3)
ui_library: Nuxt UI
backend: Nitro server routes
orm: Drizzle
database: PostgreSQL
auth: email magic link
package_manager: bun
tech_stack_skill: template-nuxt-ui
last_updated: 2026-10-24
---

# Tech stack

## Frontend
Nuxt 4 with Nuxt UI: the team uses it already, and the phone-first screens are standard components (list, button group, modal) that Nuxt UI ships.

## Backend
Nitro routes in the same repository. One deployable unit is enough for four entities and a handful of endpoints.

## Database
PostgreSQL: Votes, Polls and Places are relational, and the "one vote per member per poll" rule is a unique constraint.

## Auth
Email magic link. A team of ten does not want a password for a lunch app, and the link doubles as the invitation.

## Trade-offs Considered
- **template-nuxt-primevue**: loses on the UI-library axis; the team knows Nuxt UI.
- **SQLite**: simpler to run, but two members voting in the same second needs real row locking.
- **Password login**: more code (reset flow, hashing) for a worse experience.
