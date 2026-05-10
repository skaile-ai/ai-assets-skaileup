---
title: "component-mockup"
description: "Components in isolation: storybook + isolated-html (see REFACTOR_MOCKUP.md)"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`component-mockup/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/component-mockup/DOMAIN.md)
:::


# component-mockup

Develops and previews UI components in isolation using Storybook and isolated HTML outputs. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **component-mockup-storybook** (`storybook/orchestrator/`) — Generates a 3-layer Storybook project (custom building-block components, full-page screen compositions, clickable user journey flows); framework-agnostic, delegates to 4 sub-skills.
- **component-mockup-storybook-setup** (`storybook/setup/`) — Sub-skill 1/4: scaffolds the Storybook project, installs dependencies, applies brand tokens as CSS custom properties.
- **component-mockup-storybook-components** (`storybook/components/`) — Sub-skill 2/4: identifies custom building-block components from screen specs, builds them, creates Storybook stories.
- **component-mockup-storybook-pages** (`storybook/pages/`) — Sub-skill 3/4: builds AppShell and full-page screen compositions including state variants and responsive viewports; writes `manifest.json` for journeys.
- **component-mockup-storybook-journeys** (`storybook/journeys/`) — Sub-skill 4/4: builds clickable multi-screen user journey stories (click-dummies) for hero, vital, and hygiene flows.
- **component-mockup-storybook-types** (`storybook/types/`) — PostXL-specific: replaces mocked Storybook types with schema-generated types from `model.json`; preserves UI-only types.
- **component-mockup-isolated-html** (`isolated-html/`) — Renders one standalone HTML file per component showing all variants × states in a token-driven grid; no JS, no framework, openable via `file://`.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.
- See `../REFACTOR_MOCKUP.md` if this domain is a mockup cluster.


## Skills in this domain

- [component-mockup-isolated-html](./component-mockup-isolated-html/) — Use when components are specced and an mvp/simple-app team needs a quick visual reference without a Storybook build. Renders one standalone 
- [component-mockup-storybook](./component-mockup-storybook/) — Use after screens are approved to generate a 3-layer Storybook project: custom building-block components, full-page screen compositions, and
- [component-mockup-storybook-components](./component-mockup-storybook-components/) — Sub-skill 2/4: Identify custom building-block components from screen specs, build them using the project's component library, and create the
- [component-mockup-storybook-journeys](./component-mockup-storybook-journeys/) — Sub-skill 4/4: Build clickable multi-screen user journey stories (click-dummies). Each journey flows through real page components inside App
- [component-mockup-storybook-pages](./component-mockup-storybook-pages/) — Sub-skill 3/4: Build AppShell and full-page screen compositions from screen specs. Each page includes all state variants and responsive view
- [component-mockup-storybook-setup](./component-mockup-storybook-setup/) — Sub-skill 1/4: Scaffold a standalone Storybook project, install dependencies, and apply brand tokens as CSS custom properties. Called by the
- [component-mockup-storybook-types](./component-mockup-storybook-types/) — PostXL-specific: replaces mocked Storybook types with schema-generated types from model.json. Runs pxl types to generate TypeScript interfac
