---
title: "mockup-component"
description: "Components in isolation: storybook + isolated-html (see docs/devlog/mockup-design.md)"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`skaileup/mockup-component/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/mockup-component/DOMAIN.md)
:::


# mockup-component

Renders UI components in isolation — either as a live Storybook project (`_concept/experience/4_storybook/`) or as zero-dependency HTML files (`_concept/mockup-component/isolated-html/`). Used after screens are approved, before implementation begins.

## Skills

- **mockup-component-storybook** (`storybook/orchestrator/`) — Orchestrates the full 3-layer Storybook build; delegates to 4 sub-skills in sequence; writes `_concept/experience/4_storybook/`.
- **mockup-component-storybook-setup** (`storybook/setup/`) — Sub-skill 1/4: scaffolds the Storybook project, installs deps, injects brand tokens as CSS custom properties.
- **mockup-component-storybook-components** (`storybook/components/`) — Sub-skill 2/4: builds custom building-block components from screen specs and creates their stories.
- **mockup-component-storybook-pages** (`storybook/pages/`) — Sub-skill 3/4: builds AppShell + full-page screen compositions with all state variants; writes `manifest.json` for journeys.
- **mockup-component-storybook-journeys** (`storybook/journeys/`) — Sub-skill 4/4: builds clickable multi-screen journey stories (click-dummies) for hero, vital, and hygiene flows.
- **mockup-component-storybook-types** (`storybook/types/`) — PostXL-specific: replaces mocked types with schema-generated TypeScript from `model.json` after datamodel is finalized.
- **mockup-component-isolated-html** (`isolated-html/`) — Renders one standalone `<component>.html` per component (all variants x states, token-driven grid, no JS, openable via `file://`).

## When to Use

- Screens are approved (`_concept/experience/`) and the team needs a visual reference before writing implementation code.
- Standard-app or complex-app tier: use `mockup-component-storybook` for a live, interactive component library.
- MVP or simple-app tier: use `mockup-component-isolated-html` for a quick, zero-build visual reference.
- PostXL projects: run `mockup-component-storybook-types` after `impl-architecture/datamodel` is finalized.

## When NOT to Use

- Screens not yet approved — run `experience/screens` first.
- The goal is a full clickable app walkthrough — use `mockup-walkthrough/` instead.
- Implementation is already underway and components exist in code — inspect the running app directly.

## Sequence

`mockup-component-storybook` calls its sub-skills in order: setup → components → pages → journeys. The `types` sub-skill is optional and runs last, only for PostXL.

## Cross-references

- `../mockup-walkthrough/` — for full app walkthroughs rather than isolated components.
- `../mockup-feedback/` — annotation and patch loop that reads the storybook or isolated-html output.
- `../contracts/concept_structure.md` — valid `_concept/` paths.
- `../../docs/devlog/mockup-design.md` — mockup cluster design and how the three mockup domains relate.


## Skills in this domain

- [mockup-component-isolated-html](./mockup-component-isolated-html/) — Use when components are specced and an mvp/simple-app team needs a quick visual reference without a Storybook build. Renders one standalone 
- [mockup-component-storybook](./mockup-component-storybook/) — Use after screens are approved to generate a 3-layer Storybook project: custom building-block components, full-page screen compositions, and
- [mockup-component-storybook-components](./mockup-component-storybook-components/) — Use when screen specs are approved and building-block component stories are needed. Sub-skill 2/4: identifies custom components from specs, 
- [mockup-component-storybook-journeys](./mockup-component-storybook-journeys/) — Use when Storybook pages are built and clickable multi-screen journey stories are needed. Sub-skill 4/4: builds click-dummy journeys (hero, 
- [mockup-component-storybook-pages](./mockup-component-storybook-pages/) — Use when building-block components are ready and full-page screen compositions are needed. Sub-skill 3/4: builds AppShell and page stories f
- [mockup-component-storybook-setup](./mockup-component-storybook-setup/) — Use when no Storybook project exists yet and one needs to be scaffolded for mockup work. Sub-skill 1/4: scaffolds a standalone Storybook pro
- [mockup-component-storybook-types](./mockup-component-storybook-types/) — Use after the datamodel is finalized and Storybook stories still use placeholder types (PostXL projects only). Replaces mocked types with sc
