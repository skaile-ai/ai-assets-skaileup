---
status: accepted
date: 2026-10-24
by: architecture-techstack
level: product
kind: decision
refs: [_concept/10_blueprint/techstack.md, _concept/10_blueprint/architecture.md]
---

# One Nuxt container, no separate API

The app is one Nuxt 4 project with Nitro routes and PostgreSQL. A team lunch planner has four entities and no second client, so a split API would add a deployment and nothing else.

## Considered Options

- A separate NestJS API: a second container for four entities.
- SQLite: no safe concurrent votes.

## Consequences

One deployable unit; a later mobile client would reuse the Nitro routes as they are.
