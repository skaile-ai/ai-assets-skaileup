---
priority: must-have
roles: [organizer, member]
permissions:
  organizer: [create, read, update, delete]
  member: [create, read, update]
story_refs: [manage_places]
screens:
  - path: 07_screens/places.md
data_entities: [Place]
last_updated: 2026-10-25
---

# manage-places

## Scope
- IN: any Member adds a Place with name, cuisine and walking minutes; the website is optional.
- IN: archiving hides a Place from new Polls and keeps it in the closed Polls that used it. Only the Organizer deletes a Place nobody ever voted for.
- OUT: opening hours. The list stays a list of names, not a directory.
- DEFER: a price hint on each Place, held as a proposed field `price_level` in the data model.

## Acceptance criteria
- AC-manage_places-01 - add a place
- AC-manage_places-02 - archive a place
