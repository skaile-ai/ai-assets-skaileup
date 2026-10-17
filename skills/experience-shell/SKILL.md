---
name: experience-shell
description: "Use when the screens are specified (or, on an existing codebase, recorded in the findings) and the app needs its frame — navigation, layout areas, breakpoints, and the patterns every screen reuses. Triggers on 'app shell', 'navigation structure', 'what does the layout look like', 'design the frame'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brief }
      - { id: featuresets }
      - { id: journeys }
      - { id: brand-tokens }
      - { id: screens }
      - { id: grounding-findings }
    produces:
      - { id: app-shell, path: "_concept/07_screens/shell.md" }
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: hard }
      - { path: "_concept/05_features", gate: hard, min_entries: 1 }
      - { path: "_concept/07_screens", gate: soft, min_entries: 1 }
      - { path: "_concept/02_grounding/findings", gate: soft }
      - { path: "_concept/04_journeys/stories.yaml", gate: soft }
      - { path: "_concept/03_brand/tokens.json", gate: soft }
---

# experience-shell

Writes exactly one file: `07_screens/shell.md`, the frame every screen appears inside. `spec-feature` is the sole writer of screen specs and of the rest of `07_screens/`; this skill never writes one, and `shell` is a reserved slug there. It runs after the feature loop, or before it in the reverse flow, where the frame is drawn around the screens the codebase already has.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Know the `elements:` block** — `tree/07_screens/README.md`; the shell's nav element is written to its schema and `§ Content fidelity` shapes.
2. **Draw and write the frame** — `tree/07_screens/shell.md`: read the screens, derive the navigation, layout areas, breakpoints, shared patterns, mirror the nav into `elements:`, then show the user and iterate to approval.

**Done when** `07_screens/shell.md` exists with its navigation, layout areas, breakpoints and shared patterns, and its `elements:` nav block lists the same destinations as its `## Navigation` section, in the same order.
