---
path: _concept/09_mockup/
summary: the reviewable prototype of the design and the feedback that edits the specs
owner: []
may_propose: []
---

# _concept/09_mockup/

The prototype stakeholders review before the app exists, and the loop that carries what they say back into the specs. The prototype is derived from the specs and the data model; the specs stay the source of truth, and nothing under `09_mockup/` is read as input by a spec skill except `feedback/devlog.md`, which tells a re-render which edits to keep.

## Contents

- `storybook/` — one Vue Storybook package of floorplans, screens, entities, the whole app and journeys (`tree/09_mockup/storybook/README.md`).
- `feedback/` — the loop from a stakeholder's note to an edited screen spec or a proposed model entry (`tree/09_mockup/feedback/README.md`).
