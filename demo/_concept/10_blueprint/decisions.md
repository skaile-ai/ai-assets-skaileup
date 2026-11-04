---
last_updated: 2026-10-26
---

# Decisions

## DR-1 — One Nuxt container, no separate API

- **Date**: 2026-10-24
- **By**: architecture-techstack
- **Level**: product
- **Kind**: decision
- **Decision**: The app is one Nuxt 4 project with Nitro routes and PostgreSQL. A team lunch planner has four entities and no second client, so a split API would add a deployment and nothing else.
- **Options rejected**: separate NestJS API (a second container for four entities); SQLite (no safe concurrent votes).
- **Consequence**: one deployable unit; a later mobile client would reuse the Nitro routes as they are.
- **Refs**: `_concept/10_blueprint/techstack.md`, `_concept/10_blueprint/architecture.md`

## DR-2 — A tie is settled by one visible random draw

- **Date**: 2026-10-25
- **By**: spec-feature
- **Level**: feature polls/draw-pick
- **Kind**: decision
- **Decision**: When places tie for the most votes at closing, the app draws one of them at random and shows the draw to every member. No second voting round.
- **Options rejected**: a runoff vote (drags the decision out, the thing the product removes); the organizer decides (brings the loudest-voice problem back).
- **Consequence**: the pick is always final at the deadline; `draw-pick` needs a stored draw so a reload shows the same result.
- **Refs**: `_concept/05_features/polls/draw-pick.md`, journey `run_a_lunch_poll`, `AC-run_a_lunch_poll-04`

## DR-3 — Every member sees a poll's state live, through one channel

- **Date**: 2026-10-25
- **By**: spec-feature
- **Level**: featureset polls
- **Kind**: pattern
- **Applies when**: a polls feature changes something every Member of the Poll sees — a Vote count, the Draw, the Pick.
- **Decision**: The similarity check for `draw-pick` matched `vote-on-place`: both change the open `poll` screen for every Member, the counts as Votes arrive and the Draw at closing. The user chose to generalise: a change to a Poll reaches every Member who has it open as it happens, and everyone else on the next load, through one live channel per Poll. A result only some Members saw happen reads as rigged, the problem the product removes (`brief.md`).
- **Options rejected**: reuse `vote-on-place` for the Draw (the Draw is no Member's action and has its own permissions); keep them separate (two update paths on one screen, which drift apart the first time one changes).
- **Consequence**: counts, the Draw and the Pick arrive the same way; a later polls feature that changes what Members see follows this record instead of adding an update path. The level is the featureset because `places` has no state Members watch together.
- **Refs**: `_concept/05_features/polls/vote-on-place.md`, `_concept/05_features/polls/draw-pick.md`, `_concept/08_dossiers/draw-pick/index.md`, `_concept/07_screens/poll.md`

## DR-4 — Weighted votes are not part of the product

- **Date**: 2026-10-26
- **By**: spec-feature
- **Level**: product
- **Kind**: decision
- **Decision**: The proposal to let an organizer's vote count double was refused: it recreates the loudest voice the product replaces.
- **Options rejected**: none
- **Consequence**: one vote per member, everywhere; the data model has no weight field.
- **Refs**: `_concept/05_features/polls/vote-on-place.md`, `_concept/goals.md`
- **Status**: rejected
