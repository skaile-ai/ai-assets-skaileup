---
title: "mockup-component"
description: "Components in isolation: storybook + isolated-html (see docs/devlog/mockup-design.md)"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`skaileup/mockup-walkthrough/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/mockup-walkthrough/DOMAIN.md)
:::


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
- See `../../docs/devlog/mockup-design.md` if this domain is a mockup cluster.


## Skills in this domain

- [mockup-component-isolated-html](./mockup-component-isolated-html/) — Use when components are specced and an mvp/simple-app team needs a quick visual reference without a Storybook build. Renders one standalone 
- [mockup-component-storybook](./mockup-component-storybook/) — Use after screens are approved to generate a 3-layer Storybook project: custom building-block components, full-page screen compositions, and
- [mockup-component-storybook-components](./mockup-component-storybook-components/) — Sub-skill 2/4: Identify custom building-block components from screen specs, build them using the project's component library, and create the
- [mockup-component-storybook-journeys](./mockup-component-storybook-journeys/) — Sub-skill 4/4: Build clickable multi-screen user journey stories (click-dummies). Each journey flows through real page components inside App
- [mockup-component-storybook-pages](./mockup-component-storybook-pages/) — Sub-skill 3/4: Build AppShell and full-page screen compositions from screen specs. Each page includes all state variants and responsive view
- [mockup-component-storybook-setup](./mockup-component-storybook-setup/) — Sub-skill 1/4: Scaffold a standalone Storybook project, install dependencies, and apply brand tokens as CSS custom properties. Called by the
- [mockup-component-storybook-types](./mockup-component-storybook-types/) — PostXL-specific: replaces mocked Storybook types with schema-generated types from model.json. Runs pxl types to generate TypeScript interfac
