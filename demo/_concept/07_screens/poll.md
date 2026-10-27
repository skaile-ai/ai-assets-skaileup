---
screen_id: poll
title: Poll
implements:
  - 05_features/polls/vote-on-place.md
  - 05_features/polls/draw-pick.md
  - { path: 05_features/polls/create-poll.md, status: proposed, proposed_by: spec-feature, proposed_on: 2026-10-25 }
floorplan: object-page
posture: sovereign
density: default
regions:
  header: { shows: poll, representation: page }
  child-collections: { shows: vote, representation: row }
tier_overrides:
  - { object: place, attribute: walking-minutes, tier: 2, region: child-collections, reason: "members compare by name first" }
elements:
  - id: place-choices
    kind: list
    label: "Places to vote for"
    states: [default, disabled, loading]
    region: child-collections
    data_entity: Vote
    acceptance_refs: [05_features/polls/vote-on-place.md#AC-vote_on_places-01]
    items:
      - { label: "Trattoria da Enzo" }
      - { label: "Green Fork" }
      - { label: "Mezze Garden" }
  - id: draw-pick
    kind: button
    label: "Draw the pick"
    states: [default, loading, disabled]
    region: header
    data_entity: Poll
    acceptance_refs: [05_features/polls/draw-pick.md#AC-run_a_lunch_poll-04]
    describes: "Shown to the Organizer when a closed poll tied; replays the draw for everyone (CON-1)"
last_updated: 2026-10-25
---

# Screen: Poll

### Purpose
Vote for a place, watch the counts and see the pick. The task is working on one Poll, so the floorplan is the object page of OBJ-1 (SCR-2).

### Route
`/polls/<id>`

### Information Displayed
- `header`: title, status, the one primary action (Close poll for the Organizer while open).
- `facts`: closes at, organizer, votes, pick, four facts (H12).
- `child-collections`: one row per Place with its vote count and the voters' first names; walking minutes at tier 2 (TIER-1, OBJ-3).
- `history`: collapsed behind "Votes over time (n)".

### Actions
- Click a Place: casts or moves the Vote and shows an undo toast (EDIT-2).
- Close poll (Organizer): closes at once, then shows the pick (AC-run_a_lunch_poll-05).
- Draw the pick: replays the draw animation for a tied closed poll (CON-1, FBK-1).
- Back to `polls`.

### Situations
- Default: places ranked by votes.
- Loading: a skeleton per region (FBK-1).
- Error: a refused vote shows "Voting closed at 12:30" inline (MSG-1).
- Success: the pick row carries the Saffron chip.
- Empty: seed scenario `empty` has no poll; the screen is unreachable. In `single_user` a poll without votes shows "Be the first to vote".
- Edge cases: seed scenario `edge_cases`, a place name of 100 characters wraps to two lines.

### UI Elements
`place-choices` and `draw-pick`, each declared in `elements:`.

### Template Data
Seed scenario `populated`: poll `q1` with three votes, Trattoria da Enzo leading with two.
