---
priority: must-have
roles: [organizer, member]
permissions:
  organizer: [create, read, update]
  member: [create, read, update]
story_refs: [vote_on_places, run_a_lunch_poll]
screens:
  - path: 07_screens/poll.md
data_entities: [Vote, Poll, Member]
last_updated: 2026-10-25
---

# vote-on-place

## Scope
- IN: every Member casts exactly one Vote per open Poll and may move it until the Poll closes.
- IN: the counts are visible to all while the Poll is open, because a hidden count made people vote twice in the pilot.
- OUT: a Veto that strikes a Place for everyone. Filed as a proposed glossary term `veto`; the team has not decided whether one Member may override the vote.
- OUT: weighted votes. Every Member counts once.
- DEFER: voting by link without a login, to the next release.

## Acceptance criteria
- AC-vote_on_places-01 - one vote per member recorded
- AC-vote_on_places-02 - moving a vote keeps one per member
- AC-vote_on_places-03 - closed polls refuse votes
