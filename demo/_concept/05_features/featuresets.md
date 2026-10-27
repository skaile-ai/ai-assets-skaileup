---
last_updated: 2026-10-25
approved: 2026-10-25
---

# Featuresets

## polls
An organizer opens a lunch poll, members vote for places and the app settles on a pick.

| feature | outcome | priority | story_refs |
|---|---|---|---|
| create-poll | an Organizer opens a Poll with a deadline and at least two Places | must-have | run_a_lunch_poll |
| vote-on-place | a Member casts one Vote and may move it until the Poll closes | must-have | vote_on_places, run_a_lunch_poll |
| draw-pick | a closed Poll names its Pick and a tie is settled by a visible Draw | must-have | run_a_lunch_poll |

## places
The team keeps one list of Places that every Poll offers.

| feature | outcome | priority | story_refs |
|---|---|---|---|
| manage-places | a Member adds, edits and archives the team's Places | must-have | manage_places |

## Roles
organizer, member

## Cut
- place-ratings - backlog story `rate_places` only; the first release picks a place and stops
- order-food - not a goal (`goals.md` non-goals)
