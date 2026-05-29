---
name: design
description: "brand-identity · tokens · voice · inspiration"
metadata:
  stage: alpha
  type: domain
---

# design

Produces the visual and verbal identity of a product: design tokens consumed by all downstream skills, and copy guidelines consumed by implementation. Agents use this domain after the concept brief is approved and before screens or implementation begin.

## Skills

- **design-brand-visual** (`brand-visual/`) — Discovers aesthetic direction, extracts palettes from reference URLs, and writes `_concept/discovery/brand/identity.md` + `tokens.json` + `brandbook.html`.
- **design-brand-voice** (`brand-voice/`) — Defines tone of voice, error messages, empty states, and micro-copy patterns; writes `_concept/discovery/brand/behavioral.md` + `copy_guidelines.md`.

## When to Use

- `_concept/discovery/brief.md` exists and is approved, but `_concept/discovery/brand/` is empty or incomplete.
- User mentions "brand", "colors", "fonts", "tokens", "visual identity", or "tone of voice".
- Concept tier is `mvp` or higher and at least one downstream skill (screens, mockup, scaffold) needs `tokens.json`.

## When NOT to Use

- Brief does not exist yet — run `concept-brief` first.
- Project is an API-only service with no UI — skip design entirely.
- Tokens already exist and user only wants to tweak values — edit files directly.

## Sequence

`design-brand-visual` must run before `design-brand-voice`: voice requires `identity.md` and `tokens.json` as hard gates.

```
design-brand-visual  →  design-brand-voice
```

Both skills can be skipped via `depth: none`.

## Cross-references

- `../contracts/concept_structure.md` — canonical `_concept/` path rules every skill reads.
- `../contracts/frontmatter.md` — required frontmatter fields for brand artifacts.
- `../experience/` — `screens` and `components` read `tokens.json` produced here.
- `../impl-architecture/` — scaffold and theming setup consume `tokens.json`.
