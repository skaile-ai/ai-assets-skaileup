---
name: design-brand
description: "Use when the brief is approved and the project has no visual identity yet, or the user wants to change it. Discovers a direction in plain language, extracts from reference sites, and writes the palette, tokens and brandbook. Triggers on 'brand', 'colors', 'fonts', 'design tokens', 'make it look good'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brief }
      - { id: research-design-inspiration }
      - { id: grounding-findings }
    produces:
      - { id: brand-identity, path: "_concept/03_brand/identity.md" }
      - { id: brand-tokens, path: "_concept/03_brand/tokens.json" }
      - { id: brand-book, path: "_concept/03_brand/brandbook.html" }
      - { id: grounding-findings, path: "_concept/02_grounding/findings/" }
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: hard }
      - { path: "_concept/02_grounding/research/design-inspiration.md", gate: soft }
      - { path: "_concept/02_grounding/findings", gate: soft }
    inputs_optional:
      - { id: reference_urls, label: "Reference websites", type: text, hint: "A site you love — the palette and style get extracted from it" }
      - { id: mood, label: "Desired feeling", type: text, hint: "calm, bold, editorial, technical, playful…" }
      - { id: light_dark, label: "Colour mode", type: select, options: [light, dark, both] }
---

# design-brand

Settles what the product looks like and how it sounds: writes `03_brand/` (`identity.md`, `tokens.json`, `brandbook.html`) and files the reference screenshots behind it in `02_grounding/findings/`. It stops at the brand — no screens, no copy beyond the voice.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Read the ground, discover the direction, extract from references, propose the whole brand** — steps 1–4 of `tree/03_brand/README.md § Writing it`. Reference screenshots go into `_concept/02_grounding/findings/` with an index row each, `step: design-brand` (format: `tree/02_grounding/findings/README.md`). Nothing is written to `_concept/03_brand/` before the user approves the proposal in words.
2. **Write the identity** — `_concept/03_brand/identity.md` per `tree/03_brand/identity.md`, with `approved: <date>` set in the same write as the user's yes.
3. **Write the tokens** — `_concept/03_brand/tokens.json` per `tree/03_brand/tokens.md`.
4. **Write the brandbook** — `_concept/03_brand/brandbook.html` per `tree/03_brand/brandbook.md`.
5. **Report the distinctive choices** — step 6 of `tree/03_brand/README.md § Writing it`.

**Done when** `identity.md`, `tokens.json` and `brandbook.html` exist, the token file carries every key its node lists, and `approved:` in `identity.md` records the user's approval.
