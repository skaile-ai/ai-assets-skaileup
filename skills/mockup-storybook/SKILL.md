---
name: mockup-storybook
description: "Use when screen specs are approved and stakeholders want a living component library — Storybook stories for custom components, full-page screen compositions, and clickable journey walkthroughs. Framework-agnostic: the addon, story format and component library come from the project's template."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: walkthrough }
      - { id: screens }
      - { id: brand-tokens }
      - { id: techstack }
      - { id: journeys }
      - { id: datamodel }
    produces:
      - { id: storybook, path: "_concept/09_mockup/storybook/" }
  prerequisites:
    files:
      - { path: "_concept/07_screens", gate: hard, min_entries: 1 }
      - { path: "_concept/03_brand/tokens.json", gate: hard }
      - { path: "_concept/10_blueprint/techstack.md", gate: hard }
      - { path: "_concept/04_journeys/stories.yaml", gate: soft, min_entries: 1 }
      # Soft: the manifest is the shortcut to screens and journeys already resolved once;
      # without it the spec files are read directly (see "Where the screens come from").
      - { path: "_concept/09_mockup/walkthrough", gate: soft, min_entries: 1 }
---

# mockup-storybook

Builds a standalone Storybook at `_concept/09_mockup/storybook/` in three layers: custom components, full-page screen compositions, and one click-dummy per user journey. It is a concept artifact; an app's own Storybook is ordinary build work behind the template's `## Storybook Config`.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Resolve the stack and read its atoms by name; confirm them with the user** — `tree/09_mockup/storybook/README.md § Writing it` step 1. Screens and journeys come from the walkthrough manifest when it exists (`tree/09_mockup/walkthrough/README.md § Manifest schema`), from the spec files otherwise.
2. **Scaffold, when `package.json` is absent** — `skills/mockup-storybook/references/scaffold.md` lists the files; `tree/09_mockup/storybook/README.md § Writing it` step 2 says when and how.
3. **Build components, pages, then journeys** — `tree/09_mockup/storybook/README.md § Writing it` steps 3–5, with layout, titles and variants from `§ Format`.
4. **Verify** — `tree/09_mockup/storybook/README.md § Writing it` step 6: `run build`, then report the three story counts.

**Done when** `run build` passes and every screen spec has a page story, every custom component has a component story, and every non-backlog story map has a journey story.
