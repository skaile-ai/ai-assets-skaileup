---
name: experience-screen
description: "Use when one screen needs specifying on its own — a screen already built in the code, a screen a feature needs, or a layout to try before anything is specified. Derives it from the findings or asks, picks the floorplan, posture and density, binds regions, records tier overrides and can prototype it early with sample data. Triggers on 'describe this screen', 'spec the inbox screen', 'which layout fits this', 'prototype this screen', 'try two layouts'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
    - contract:@skaile-ai/app-design-rulebook
  artifacts:
    requires:
      - { id: grounding-findings }
      - { id: glossary }
      - { id: datamodel }
      - { id: app-design }
    produces:
      - { id: screens, path: "_concept/07_screens/<screen>.md" }
      - { id: screen-prototypes, path: "_concept/09_mockup/prototypes/<screen>/a.html" }
  prerequisites:
    files:
      - { path: "_concept/02_grounding/findings/screens.md", gate: soft }
      - { path: "_concept/glossary.md", gate: soft }
      - { path: "_concept/10_blueprint/datamodel/", gate: soft }
      - { path: "_concept/05_features", gate: soft }
      - { path: "_concept/07_screens/shell.md", gate: soft }
      - { path: "APP-DESIGN.md", gate: soft }
    inputs_optional:
      - { id: screen, label: "Which screen (name, route or file)?", type: text }
---

# experience-screen

Writes one screen at `07_screens/<screen>.md`, on its own: no feature, brief or shell is needed first, and every missing input is derived from the code or asked. It writes no feature, no shell and no `APP-DESIGN.md`; what belongs to them goes to their owners as `proposed` entries.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Resolve, sort and ask** — `tree/07_screens/[screen].md § Writing it`, steps 1–3. One screen per run; a missing name is the first question. Missing glossary, model, features, shell or `APP-DESIGN.md` never stop the run: the facts come from `findings/screens.md` or a scoped `concept-reverse`, and the rest is batched.
2. **Offer the early prototype** — `tree/09_mockup/prototypes/[screen]/a.md`. Offered before the spec is written, since the layout is a spatial choice (`tree/README.md § How a skill runs`, rule 6): a floorplan preview with the screen's sample data, a second variant on request. When the user declines, skip it; when they pick a variant, its floorplan and bindings carry into item 3.
3. **Choose the floorplan, bind regions, settle tiers** — `tree/07_screens/[screen].md § Writing it`, steps 4–6, with the floorplan READMEs of `rulebook/floorplans/` and `rulebook/rules.md § P18` and `§ P21`. Reads `APP-DESIGN.md` per `tree/APP-DESIGN.md § Reading it`; a missing term, attribute or screen default becomes a `proposed` entry at its owner (`tree/glossary.md § Format`, `tree/10_blueprint/datamodel/model.md`).
4. **Write the screen and link it** — `tree/07_screens/[screen].md § Writing it`, steps 7–8, with the `elements:` block per `tree/07_screens/README.md` and the cross-link per `tree/05_features/README.md § Links in both directions`.
5. **Show the screen in the user's terms** — what is where, what changes on a phone, which attribute sits behind which disclosure — and iterate to approval; then write `approved:` per `tree/README.md § Frontmatter every markdown artifact carries`.

**Done when** `tree/07_screens/[screen].md § Checks` holds: `screen_id` equals the filename, the floorplan exists with `kind: screen`, every region key is in its `§ Regions`, every `implements:` entry resolves, every tier override has its reason, and the completion summary names the proposed entries left at their owners and the features whose `screens:` now carries a proposed entry.
