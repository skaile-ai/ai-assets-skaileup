---
name: experience-shell
description: "Use when the app needs its frame — the shell frame, the navigation model it realises, the one list of destinations, and the layout patterns every screen reuses. Works with or without features and screens, from the code's own routes when they exist. Triggers on 'app shell', 'navigation structure', 'sidebar or top bar', 'what does the layout look like', 'design the frame'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
    - contract:@skaile-ai/app-design-rulebook
  artifacts:
    requires:
      - { id: glossary }
      - { id: featuresets }
      - { id: journeys }
      - { id: brand-tokens }
      - { id: screens }
      - { id: grounding-findings }
      - { id: app-design }
    produces:
      - { id: app-shell, path: "_concept/07_screens/shell.md" }
  prerequisites:
    files:
      - { path: "APP-DESIGN.md", gate: soft }
      - { path: "_concept/glossary.md", gate: soft }
      - { path: "_concept/07_screens", gate: soft, min_entries: 1 }
      - { path: "_concept/02_grounding/findings", gate: soft }
      - { path: "_concept/05_features/featuresets.md", gate: soft }
      - { path: "_concept/04_journeys/stories.yaml", gate: soft }
      - { path: "_concept/03_brand/brand.tokens.json", gate: soft }
---

# experience-shell

Writes exactly one file: `07_screens/shell.md`, the frame every screen appears inside — the shell frame, the navigation model it realises and the one destination list. It writes no screen spec (`experience-screen` does) and needs no feature or screen first: the destinations come from the objects, the findings or the screens that exist, and a model nobody decided is written as provisional.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Know the `elements:` block** — `tree/07_screens/README.md`; the shell's nav element is written to its schema and `§ Content fidelity` shapes.
2. **Resolve the facts and derive the destination list** — `tree/07_screens/shell.md § Writing it`, steps 1–2: `APP-DESIGN.md § Navigation model` and the objects with `navigation: primary` when they exist, else the findings and the screens, else one batch of questions.
3. **Decide what is open, choose the frame, write the sections** — `tree/07_screens/shell.md § Writing it`, steps 3–5, with the shell floorplans of `rulebook/floorplans/` (`rulebook/rules.md § P18`, `§ P22`). Without a decided model the file says `navigation: provisional` and names `experience-interaction` as the owner of the decision.
4. **Mirror the list and show the frame** — `tree/07_screens/shell.md § Writing it`, steps 6–7.
5. **Cite interaction decisions, never make them** — `tree/APP-DESIGN.md § Reading it`: empty, error, confirmation, message and editing patterns are referenced by MSG, EDIT and MOD id; without the file they go under `## Proposed interaction patterns` for `experience-interaction`.

**Done when** `tree/07_screens/shell.md § Checks` holds: `shell.md` names a `kind: shell` frame matching the primary surface, carries `navigation: decided` or the visible provisional line, and its `elements:` nav block lists the same destinations as `## Navigation`, in the same order.
