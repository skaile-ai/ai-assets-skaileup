---
priority: must-have
roles: [organizer, member]
permissions:
  organizer: [create, read, update, delete]
  member: [create, read, update]
story_refs: [manage_places]
follows: []
screens:
  - path: 07_screens/places.md
data_entities: [Place]
tracker: { issue: 104 }
last_updated: 2026-10-25
---

# manage-places

## Scope
- IN: any Member adds a Place with name, cuisine and walking minutes; the website is optional.
- IN: archiving hides a Place from new Polls and keeps it in the closed Polls that used it. Only the Organizer deletes a Place nobody ever voted for.
- OUT: opening hours. The list stays a list of names, not a directory.
- DEFER: showing a price hint on each Place. The data model already carries `price_level`, promoted from a mockup-storybook proposal (`_concept/proposals/2026-10-22-mockup-storybook-place-card.yaml`).

## Acceptance criteria
- AC-manage_places-01 - add a place
- AC-manage_places-02 - archive a place
