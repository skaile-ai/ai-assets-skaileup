---
name: mockup-storybook
description: "Use when a screen, an entity editor or a journey should be seen and critiqued as a running prototype, or when the user says 'prototype this screen', 'build the storybook', 'click-dummy', 'try the editor for this entity'. Grows one Vue Storybook package layer by layer: floorplans, screens, entity editors, the whole app, journeys."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brand-tokens }
      - { id: screens }
      - { id: app-shell }
      - { id: journeys }
      - { id: datamodel }
    produces:
      - { id: storybook, path: "_concept/09_mockup/storybook/" }
  prerequisites:
    files:
      - { path: "_concept/07_screens", gate: soft, min_entries: 1 }
      - { path: "_concept/03_brand/brand.tokens.json", gate: soft }
      - { path: "_concept/04_journeys/stories.yaml", gate: soft, min_entries: 1 }
      - { path: "_concept/10_blueprint/datamodel", gate: soft }
---

# mockup-storybook

Grows the Storybook package at `_concept/09_mockup/storybook/` one layer at a time: the scaffold with its 16 floorplans, a layout story per screen, editor and display components per entity, the whole app, and one story per journey. A run builds every layer whose inputs exist now and names each skipped layer with its missing input; the specs and the data model are never edited here except by `proposed` entries in `model.ts`.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Resolve which screens, entities and journeys exist** — `tree/09_mockup/storybook/README.md § Writing it` step 1, derive-or-ask per `tree/README.md § How a skill runs`.
2. **Scaffold, when `package.json` is absent** — `tree/09_mockup/storybook/README.md § Writing it` step 2; the package layout is in `tree/09_mockup/storybook/README.md § Package layout`.
3. **Bring the brand tokens and the data model in** — `tree/09_mockup/storybook/README.md § Writing it` step 3; the model is `tree/10_blueprint/datamodel/model.md § Format` and `tree/10_blueprint/datamodel/model.md § Writing it`.
4. **Write a screen's layout story** — `tree/09_mockup/storybook/README.md § Writing it` step 4, from the screen spec `tree/07_screens/[screen].md § Format`. `experience-screen` calls this step to show a layout before the screen is specified.
5. **Write the entity stories, proposing the fields an editor needs** — `tree/09_mockup/storybook/README.md § Writing it` step 5, with the states from `tree/09_mockup/storybook/README.md § Globals and state stories` and the proposal move from `tree/09_mockup/storybook/README.md § The data model`.
6. **Write the App and the journeys** — `tree/09_mockup/storybook/README.md § Writing it` step 6, from the shell `tree/07_screens/shell.md § Format` and the story map `tree/04_journeys/stories.md § Format`.
7. **Verify** — `tree/09_mockup/storybook/README.md § Writing it` step 7, and report the story count per layer.

Worked examples for steps 4–6: `skills/mockup-storybook/references/screen-story.md`, `skills/mockup-storybook/references/entity-stories.md`, `skills/mockup-storybook/references/journey-story.md`. Notes a stakeholder leaves on the running Storybook are read and applied by `mockup-feedback`.

**Done when** `npm run check` exits 0 in `_concept/09_mockup/storybook/` and `tree/09_mockup/storybook/README.md § Checks` holds for every layer whose inputs exist.
