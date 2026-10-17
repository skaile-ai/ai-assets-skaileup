---
path: _concept/09_mockup/
summary: reviewable prototypes of the design and the feedback that edits the specs
writers: []
---

# _concept/09_mockup/

The prototype surfaces stakeholders review before the app exists. All three are derived from the specs and renderer-agnostic: the specs stay the source of truth, and nothing under `09_mockup/` is read as input by a spec skill except `feedback/devlog.md`, which tells a re-render which edits to keep.

## Contents

- `walkthrough/` — clickable static site, one page per screen and journey (`tree/09_mockup/walkthrough/README.md`).
- `storybook/` — component library, page compositions and journey click-dummies (`tree/09_mockup/storybook/README.md`).
- `feedback/` — the loop from a stakeholder's comment to an edited screen spec (`tree/09_mockup/feedback/README.md`).

Order of work: `mockup-walkthrough` builds the site, `mockup-annotate` instruments it and prepares `feedback/sessions/`, `mockup-feedback` turns returned notes into spec edits, and the next `mockup-walkthrough` run re-renders from the edited specs.
