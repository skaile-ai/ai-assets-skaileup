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

## Ideas
| idea | featureset | source | raised_by |
|---|---|---|---|
| diet-filter | polls | `brief.md`: "a vegetarian never gets a steakhouse as the only choice" (2026-10-24) | concept-brief |
| chat-share | polls | `brief.md` Comparables: "borrow the vote inside the channel where the team already talks" (2026-10-24) | concept-brief |
| deadline-reminders | notifications (new) | `create-poll.md` DEFER: "reminders before the deadline, to a later notification feature" (2026-10-25) | spec-feature |
| vote-by-link | polls | `vote-on-place.md` DEFER: "voting by link without a login, to the next release" (2026-10-25) | spec-feature |

## Cut
- place-ratings - backlog story `rate_places` only; the first release picks a place and stops
- order-food - not a goal (`goals.md` non-goals)
