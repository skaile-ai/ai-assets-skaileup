---
title: "walkthrough-mockup"
description: "Clickable application walkthrough: text · static-html · lit · astro · framework"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`walkthrough-mockup/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/walkthrough-mockup/DOMAIN.md)
:::


# walkthrough-mockup

Produces clickable application walkthroughs at increasing fidelity levels, from plain text through static HTML, Lit, Astro, and full framework targets. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **walkthrough-mockup-text** (`text/`) — Generates a linked multi-page interactive HTML prototype across 3 stacks (Alpine+Shoelace, Vue 3+PrimeVue, Preact+HTM); auto-selects template from the tech-stack profile.
- **walkthrough-mockup-static-html** (`static-html/`) — Zero-build clickable static HTML walkthrough — one HTML file per screen and per journey, plus `manifest.json` for the mockup-feedback cluster. Best for simple-app tier.
- **walkthrough-mockup-astro** (`astro/`) — Tailwind-styled Astro static site walkthrough — one HTML file per screen and per journey, built via `bun run build`, plus `manifest.json`. Astro source committed alongside built output. Best for standard-app tier.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.
- See `../REFACTOR_MOCKUP.md` if this domain is a mockup cluster.


## Skills in this domain

- [walkthrough-mockup-astro](./walkthrough-mockup-astro/) — Use when stakeholders need a clickable Astro walkthrough of the application — built static site, Tailwind-styled, openable directly in a bro
- [walkthrough-mockup-static-html](./walkthrough-mockup-static-html/) — Use when stakeholders need a clickable static HTML walkthrough of the application — zero build, no JS framework, openable directly in a brow
- [walkthrough-mockup-text](./walkthrough-mockup-text/) — Use when screen specs are approved and user wants interactive HTML mockups. Also when user says 'mockup', 'prototype', 'show me what it look
