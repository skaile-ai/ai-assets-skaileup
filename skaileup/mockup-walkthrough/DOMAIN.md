---
name: mockup-walkthrough
description: "Clickable application walkthrough: text · static-html · lit · astro · framework"
metadata:
  stage: alpha
  type: domain
---

# mockup-walkthrough

Renders approved screen specs and journey definitions into a navigable, clickable prototype. Agents use this domain when stakeholders need to walk through the application before any implementation begins.

## Skills

- **mockup-walkthrough-text** (`text/`) — Linked multi-page HTML prototype (Alpine+Shoelace, Vue 3+PrimeVue, or Preact+HTM); writes to `_concept/mockups/`. Stack auto-selected from `stack.md` if present.
- **mockup-walkthrough-static-html** (`static-html/`) — Zero-build static HTML walkthrough; writes `screen/<group>/<name>.html`, `journey/<id>.html`, and `manifest.json` to `_concept/mockups/`. Best for simple-app tier.
- **mockup-walkthrough-astro** (`astro/`) — Tailwind-styled Astro site; same output contract as static-html but built via `bun run build`. Astro source committed alongside built output. Best for standard-app tier.

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
standard-app tier  → mockup-walkthrough-astro
```

All three share the same output contract; `manifest.json` is consumed by `mockup-feedback-annotate` in the next cluster phase.

## Cross-references

- `../mockup-feedback/DOMAIN.md` — reads `manifest.json` produced here
- `../experience/DOMAIN.md` — screen specs and `stories.json` are the primary inputs
- `../contracts/elements_block.md` — `data-spec-*` attribute contract shared across all three skills
