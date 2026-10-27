---
priority: must-have
roles: [organizer, member]
permissions:
  organizer: [read, update]
  member: [read]
story_refs: [run_a_lunch_poll]
screens:
  - path: 07_screens/poll.md
data_entities: [Poll, Vote, Place]
last_updated: 2026-10-25
---

# draw-pick

## Scope
- IN: at the deadline the Poll closes and the Place with the most Votes becomes the Pick.
- IN: a tie for most Votes is settled by a Draw among the tied Places, shown to every Member as it happens.
- IN: a Poll with no Votes closes without a Pick and says so.
- OUT: a second round of voting after a tie. The Draw is the point of the product.
- DEFER: weighting the Draw by walking time, which needs a decision on what "fair" means.

## Acceptance criteria
- AC-run_a_lunch_poll-03 - the most voted place becomes the pick
- AC-run_a_lunch_poll-04 - a tie is drawn and shown
