---
title: "mockup-walkthrough"
description: "Clickable application walkthrough: text · static-html · lit · astro · framework"
sourcePath: "skaileup/mockup-walkthrough/DOMAIN.md"
sidebar:
  label: "Overview"
  order: 0
---


# mockup-walkthrough

Renders approved screen specs and journey definitions into a navigable, clickable prototype. Agents use this domain when stakeholders need to walk through the application before any implementation begins.

## Skills

- **mockup-walkthrough-text** (`text/`) — Linked multi-page HTML prototype (Alpine+Shoelace, Vue 3+PrimeVue, or Preact+HTM); writes to `_concept/mockups/`. Stack auto-selected from `stack.md` if present.
- **mockup-walkthrough-static-html** (`static-html/`) — Zero-build static HTML walkthrough; writes `screen/<group>/<name>.html`, `journey/<id>.html`, and `manifest.json` to `_concept/mockups/`. Best for simple-app tier.
- **mockup-walkthrough-astro** (`astro/`) — Tailwind-styled Astro site; same output contract as static-html but built via `bun run build`. Astro source committed alongside built output. Best for standard-app tier.
- **mockup-walkthrough-lit** (`lit/`) — Lit web-components site (Vite); light-DOM components so `data-spec-*` stays queryable. Embeddable into a host page. Alt for embedded contexts.
- **mockup-walkthrough-framework** (`framework/`) — Stack-native renderer; resolves `tech_stack_skill` from `_concept/blueprint/techstack.md` to a `template-*` and renders in that framework (Next/Nuxt/SvelteKit). Highest fidelity — complex-app tier. Requires `impl-architecture-templates-select` to have run.

## When to Use

- `experience/screens/` has at least one screen spec and the user asks for a prototype, mockup, or "show me what it looks like"
- The orchestrator has completed the experience phase and is advancing to the mockup cluster
- Stakeholders need a browser-openable artifact before any code is written

## When NOT to Use

- Screen specs don't exist yet — run `experience-screens` first
- User wants isolated component previews — use `mockup-component` instead
- A real implementation already exists and the ask is to review it — use `ops-review`

## Sequence

Pick one skill per run based on tier:

```
mvp / quick scan   → mockup-walkthrough-text
simple-app tier    → mockup-walkthrough-static-html
standard-app tier  → mockup-walkthrough-astro  (or -lit for embedded contexts)
complex-app tier   → mockup-walkthrough-framework  (stack-native; static-html fallback)
```

All renderers share the same output contract; `manifest.json` is consumed by `mockup-feedback-annotate` in the next cluster phase.

## Cross-references

- `../mockup-feedback/DOMAIN.md` — reads `manifest.json` produced here
- `../experience/DOMAIN.md` — screen specs and `stories.json` are the primary inputs
- `../contracts/elements_block.md` — `data-spec-*` attribute contract shared across all three skills


## Skills in this domain

- [mockup-walkthrough-astro](./mockup-walkthrough-astro/) — Use when stakeholders need a clickable Astro walkthrough of the application — built static site, Tailwind-styled, openable directly in a bro
- [mockup-walkthrough-framework](./mockup-walkthrough-framework/) — Use when stakeholders need the highest-fidelity clickable walkthrough rendered in the project's CHOSEN stack framework (Next.js / Nuxt / Sve
- [mockup-walkthrough-lit](./mockup-walkthrough-lit/) — Use when stakeholders need a clickable Lit web-components walkthrough of the application — built with Vite, rendered as custom elements whos
- [mockup-walkthrough-static-html](./mockup-walkthrough-static-html/) — Use when stakeholders need a clickable static HTML walkthrough of the application — zero build, no JS framework, openable directly in a brow
- [mockup-walkthrough-text](./mockup-walkthrough-text/) — Use when screen specs are approved and user wants interactive HTML mockups. Also when user says 'mockup', 'prototype', 'show me what it look
