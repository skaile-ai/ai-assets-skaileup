---
priority: must-have
roles: [organizer, member]
permissions:
  organizer: [create, read, update]
  member: [read]
story_refs: [run_a_lunch_poll]
screens:
  - path: 07_screens/polls.md
  - path: 07_screens/poll.md
data_entities: [Poll, Place]
last_updated: 2026-10-25
---

# create-poll

## Scope
- IN: an Organizer sets a title, a deadline and picks two or more Places from the team list. A poll without a deadline invites a poll that never closes.
- IN: the Poll opens at once and every Member sees it in the list.
- IN: the Organizer may close a Poll early (`update`). Only the Organizer: recorded in `02_grounding/onboarding/questions.md`.
- OUT: editing the Places of an open Poll. Votes would point at a Place that vanished.
- OUT: recurring polls. One decision per day keeps the model small.
- DEFER: reminders before the deadline, to a later notification feature.

## Acceptance criteria
- AC-run_a_lunch_poll-01 - open a poll with title, deadline and places
- AC-run_a_lunch_poll-02 - refuse fewer than two places
- AC-run_a_lunch_poll-05 - close a poll early
