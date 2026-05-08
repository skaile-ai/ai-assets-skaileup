---
name: walkthrough-mockup
description: "Clickable application walkthrough: text · static-html · lit · astro · framework"
metadata:
  stage: alpha
  type: domain
---

# walkthrough-mockup

Produces clickable application walkthroughs at increasing fidelity levels, from plain text through static HTML, Lit, Astro, and full framework targets. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **walkthrough-mockup-text** (`text/`) — Generates a linked multi-page interactive HTML prototype across 3 stacks (Alpine+Shoelace, Vue 3+PrimeVue, Preact+HTM); auto-selects template from the tech-stack profile.
- **walkthrough-mockup-static-html** (`static-html/`) — Zero-build clickable static HTML walkthrough — one HTML file per screen and per journey, plus `manifest.json` for the mockup-feedback cluster. Best for simple-app tier.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.
- See `../REFACTOR_MOCKUP.md` if this domain is a mockup cluster.
