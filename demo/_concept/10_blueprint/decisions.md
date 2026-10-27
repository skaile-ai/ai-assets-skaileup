---
last_updated: 2026-10-26
---

# Decisions

## DR-1 — One Nuxt container, no separate API

- **Date**: 2026-10-24
- **By**: architecture-techstack
- **Decision**: The app is one Nuxt 4 project with Nitro routes and PostgreSQL. A team lunch planner has four entities and no second client, so a split API would add a deployment and nothing else.
- **Options rejected**: separate NestJS API (a second container for four entities); SQLite (no safe concurrent votes).
- **Consequence**: one deployable unit; a later mobile client would reuse the Nitro routes as they are.
- **Refs**: `_concept/10_blueprint/techstack.md`, `_concept/10_blueprint/architecture.md`

## DR-2 — A tie is settled by one visible random draw

- **Date**: 2026-10-25
- **By**: spec-feature
- **Decision**: When places tie for the most votes at closing, the app draws one of them at random and shows the draw to every member. No second voting round.
- **Options rejected**: a runoff vote (drags the decision out, the thing the product removes); the organizer decides (brings the loudest-voice problem back).
- **Consequence**: the pick is always final at the deadline; `draw-pick` needs a stored draw so a reload shows the same result.
- **Refs**: `_concept/05_features/polls/draw-pick.md`, journey `run_a_lunch_poll`, `AC-run_a_lunch_poll-04`

## DR-3 — Weighted votes are not part of the product

- **Date**: 2026-10-26
- **By**: spec-feature
- **Decision**: The proposal to let an organizer's vote count double was refused: it recreates the loudest voice the product replaces.
- **Options rejected**: none
- **Consequence**: one vote per member, everywhere; the data model has no weight field.
- **Refs**: `_concept/05_features/polls/vote-on-place.md`, `_concept/goals.md`
- **Status**: rejected
