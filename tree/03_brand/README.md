---
path: _concept/03_brand/
summary: the visual identity folder and the procedure that fills it
owner: []
may_propose: []
---

# _concept/03_brand/

What the product looks like and how it sounds. Every skill that renders anything reads `brand.tokens.json`, and both mockup renderers hard-gate on it, so this folder is what the visual half of the project stands on. Reads `brief.md`, `glossary.md` and `02_grounding/`; `design-brand` writes every file here, and `identity.md` is the one home of the tone of voice and copy guidelines.

## Contents

- `identity.md` — direction, colour rules, type, tone and copy, approval (`tree/03_brand/identity.md`)
- `brand.tokens.json` — W3C design tokens, plus `brand.dark.tokens.json` and `brand.resolver.json` when the brand has a dark mode (`tree/03_brand/brand.tokens.md`)
- `brandbook.html` — self-contained visual reference (`tree/03_brand/brandbook.md`)

## Writing it

The brand procedure, run by `design-brand`.

1. **Read the ground.** `brief.md` for the app, its audience and its comparables; `02_grounding/research/design-inspiration.md` and `colors-fonts.md` where research ran; `02_grounding/onboarding/answers.json` for an existing brand (`has_brand`) and where its files are (`brand_files`). A project that already has a brand gets that brand extracted and recorded, not replaced. When `02_grounding/findings/brand.md` exists (the reverse flow), seed the draft from it and show each graded value as a proposal: only `extracted` values are what the code says, and `inferred` or `needs_review` ones are the user's to settle before they reach `brand.tokens.json`.
2. **Discover the direction**, one decision batch per message (`tree/README.md § How a skill runs`), each built on the last answer: a site whose look they love; the feeling the product should give, offered as a spectrum rather than a dropdown; a calibration between two opposing examples that both fit this kind of app; light, dark or both; any font they are bound to.
3. **Extract from any reference URL they give.** Open it, screenshot it into `02_grounding/findings/` with an index row (source, date, `step: design-brand`) as `tree/02_grounding/findings/README.md` describes, and read off the dominant colours, the type pairing, the density, the elevation and the corner radius. Show what you found and ask whether to take it as-is, adapt it, or go the other way — a reference URL is the user's taste stated more precisely than they can say it.
4. **Propose a whole brand before writing anything:** the aesthetic and why it fits this product, each colour with the job it does rather than just its hex, the type choices justified against the direction, and the **memorable element** — the one thing that makes this app visually unmistakable (primary blue, grey secondary and Inter is the default any project gets and says nothing about this one). Iterate until the user approves in words.
5. **Write the files** from the approved proposal: `identity.md` (`tree/03_brand/identity.md`), `brand.tokens.json` and, for a brand with a dark mode, `brand.dark.tokens.json` and `brand.resolver.json` (`tree/03_brand/brand.tokens.md`), `brandbook.html` (`tree/03_brand/brandbook.md`). The approval from step 4 is recorded in `identity.md` and in the token file in the same write, as `tree/03_brand/brand.tokens.md § Writing it` says.
6. **Report the distinctive choices in a sentence or two** and name what reads the tokens next — the feature loop's screen specs, then the walkthrough and storybook.

## Checks

`identity.md`, `brand.tokens.json` and `brandbook.html` exist (plus the dark file and the resolver when the brand has a dark mode), the token file carries every required token and passes its schema, and the user has approved the direction, which `approved:` in `identity.md` and in the token file's `$extensions` records.
