---
last_updated: 2026-10-25
approved: 2026-10-25
---

# Behaviors - polls

Who may trigger which transition is the role x action table of each feature spec (`05_features/polls/create-poll.md`, `vote-on-place.md`, `draw-pick.md`).

## Poll

States: `Open`, `Closed`.

| from | event | to | requires | ensures | criteria |
|---|---|---|---|---|---|
| - | an Organizer opens a Poll | Open | title, a deadline in the future and at least two Places | the Poll is listed for every Member | AC-run_a_lunch_poll-01 |
| Open | the deadline passes | Closed | the Poll has Votes | the Place with most Votes is the Pick | AC-run_a_lunch_poll-03 |
| Open | the deadline passes | Closed | two or more Places tie for most Votes | a Draw settles the Pick and is shown to every Member | AC-run_a_lunch_poll-04 |
| Open | the Organizer closes the Poll | Closed | the Poll is Open | the Pick rule of the deadline applies at once | AC-run_a_lunch_poll-05 |
| Closed | a Member tries to vote | Closed | the Poll is Closed | the Vote is refused and the Pick is kept | AC-vote_on_places-03 |

## Vote

States: `Cast`.

| from | event | to | requires | ensures | criteria |
|---|---|---|---|---|---|
| - | a Member selects a Place | Cast | the Poll is Open and the Member has no Vote in it | one Vote exists for the Member | AC-vote_on_places-01 |
| Cast | the Member selects another Place | Cast | the Poll is Open | the Vote points at the new Place; no second Vote exists | AC-vote_on_places-02 |

## Constants

| name | value | used by |
|---|---|---|
| `min_places_per_poll` | 2 | AC-run_a_lunch_poll-02 |
| `max_members_per_team` | 15 | `goals.md` constraints |
| `draw_animation_ms` | 2500 | `draw-pick` |

## Open questions

- May a Member remove their Vote without choosing another Place? Decide in `vote-on-place`; today a Vote can only move.
