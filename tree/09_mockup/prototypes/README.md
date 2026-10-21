---
path: _concept/09_mockup/prototypes/
summary: early single-screen prototypes built from a floorplan preview and sample data
owner: []
may_propose: []
---

# _concept/09_mockup/prototypes/

Cheap prototypes made before a screen is specified, so the user judges the layout on a page instead of in prose. One directory per prototyped screen, `<screen>/`, named for the screen's `screen_id` (`tree/07_screens/[screen].md`); a prototype carries no screen spec and no feature, and nothing in `07_screens/` or `05_features/` is read from it. `experience-screen` writes it as the optional step before the spec; `mockup-walkthrough` builds the full clickable site separately (`tree/09_mockup/walkthrough/README.md`) and never reads this directory.

## Contents

- `<screen>/` — the prototype variants of one screen; see `tree/09_mockup/prototypes/[screen]/README.md`.
