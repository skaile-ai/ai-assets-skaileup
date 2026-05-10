---
name: mockup-component
description: "Components in isolation: storybook + isolated-html (see REFACTOR_MOCKUP.md)"
metadata:
  stage: alpha
  type: domain
---

# mockup-component

Develops and previews UI components in isolation using Storybook and isolated HTML outputs. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **mockup-component-storybook** (`storybook/orchestrator/`) — Generates a 3-layer Storybook project (custom building-block components, full-page screen compositions, clickable user journey flows); framework-agnostic, delegates to 4 sub-skills.
- **mockup-component-storybook-setup** (`storybook/setup/`) — Sub-skill 1/4: scaffolds the Storybook project, installs dependencies, applies brand tokens as CSS custom properties.
- **mockup-component-storybook-components** (`storybook/components/`) — Sub-skill 2/4: identifies custom building-block components from screen specs, builds them, creates Storybook stories.
- **mockup-component-storybook-pages** (`storybook/pages/`) — Sub-skill 3/4: builds AppShell and full-page screen compositions including state variants and responsive viewports; writes `manifest.json` for journeys.
- **mockup-component-storybook-journeys** (`storybook/journeys/`) — Sub-skill 4/4: builds clickable multi-screen user journey stories (click-dummies) for hero, vital, and hygiene flows.
- **mockup-component-storybook-types** (`storybook/types/`) — PostXL-specific: replaces mocked Storybook types with schema-generated types from `model.json`; preserves UI-only types.
- **mockup-component-isolated-html** (`isolated-html/`) — Renders one standalone HTML file per component showing all variants × states in a token-driven grid; no JS, no framework, openable via `file://`.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.
- See `../REFACTOR_MOCKUP.md` if this domain is a mockup cluster.
