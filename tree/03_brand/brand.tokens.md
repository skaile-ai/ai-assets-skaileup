---
path: [_concept/03_brand/brand.tokens.json, _concept/03_brand/brand.dark.tokens.json, _concept/03_brand/brand.resolver.json]
summary: brand as W3C design tokens, with optional dark overlay and resolver
writers: [design-brand]
---

# _concept/03_brand/brand.tokens.json

The brand in machine-readable form, written as W3C Design Tokens Community Group tokens so any token tool (Style Dictionary, Terrazzo, Figma plugins, Storybook addons) reads it without a converter. The walkthrough, `build-scaffold` and Storybook flatten it into `--token-*` CSS custom properties, and both mockup renderers hard-gate on it, so a missing token becomes a bland default in every rendered screen. Specs: [Format Module 2025.10](https://www.designtokens.org/tr/2025.10/format/), [Resolver Module 2025.10](https://www.designtokens.org/tr/2025.10/resolver/).

## Format

| File | Written when |
|---|---|
| `_concept/03_brand/brand.tokens.json` | always; the light base, or the dark-only palette |
| `_concept/03_brand/brand.dark.tokens.json` | the brand has both modes; overrides of the colour tokens only |
| `_concept/03_brand/brand.resolver.json` | the dark file exists |

Only the base file is a declared product of `design-brand`: a node counts as done when every declared path exists, and a one-mode brand never writes the other two.

Plain JSON (RFC 8259), `.tokens.json` so editors open it as JSON. The base file is validated against `tree/03_brand/brand-tokens.schema.json`; the dark file is a partial overlay and is not.

Every token carries its own `$type` and `$value` (a group's inherited `$type` is not used, so the schema check and hand-edits stay simple). Colour is the spec's object, never a bare string:

```json
{ "color": { "primary": { "$type": "color",
  "$value": { "colorSpace": "srgb", "components": [0.2, 0.4, 0.9], "hex": "#3366e6" } } } }
```

`components` are 0–1 and `hex` is always present as six digits (`#rrggbb`) because the CSS rule below reads `hex`. A colour with transparency adds `alpha` (0–1); `hex` then stays the opaque colour. A dimension is `{ "value": 8, "unit": "px" }` (`px` or `rem`; the unit is required even for `0`). A shadow is the composite object `{ color, offsetX, offsetY, blur, spread }`, with `inset` optional, or an array of them.

### Required tokens

More tokens and groups are allowed; these paths must exist, each with the `$type` shown.

| Path | `$type` | Job |
|---|---|---|
| `color.primary` `color.secondary` `color.accent` | `color` | brand colours; the memorable element usually lives in `accent` |
| `color.background` `color.surface` `color.text` `color.text-muted` `color.border` | `color` | page, raised surface, body and secondary text, dividers |
| `color.error` `color.success` `color.warning` | `color` | the semantic set |
| `font.heading` `font.body` `font.mono` | `fontFamily` | a string, or an array ordered from most to least preferred |
| `radius.base` `spacing.base` | `dimension` | the corner radius and the spacing unit |
| `shadow.sm` `shadow.md` `shadow.lg` | `shadow` | the three elevations |

Root `$extensions["ai.skaile"]` is required and is `{ "mode": "light" | "dark", "approved": "YYYY-MM-DD" }`; `mode` is the mode the file describes and `approved` appears with the approval. The key follows the spec's reverse-domain-name advice, and tools preserve extension data they do not read. The atmosphere (grain, gradients, texture) lives in `identity.md` only.

## Light and dark

The base file is always the light palette. A brand with both modes adds `brand.dark.tokens.json`, which repeats only the colour tokens that change (its own `mode` is `dark`), and `brand.resolver.json`, one modifier whose contexts apply in array order, the later source winning:

```json
{ "version": "2025.10", "name": "brand",
  "modifiers": { "mode": { "default": "light", "contexts": {
    "light": [{ "$ref": "brand.tokens.json" }],
    "dark":  [{ "$ref": "brand.tokens.json" }, { "$ref": "brand.dark.tokens.json" }] } } },
  "resolutionOrder": [{ "$ref": "#/modifiers/mode" }] }
```

A dark-only brand writes its dark palette into `brand.tokens.json` with `mode: dark` and no overlay; it flattens into `:root` like any base. A one-mode brand writes neither extra file.

## Flattening to CSS

Renderers, scaffold and Storybook turn tokens into CSS: path segments joined with `-`, prefixed `--token-`; `$`-keys are never path segments. Colour → its `hex`, or `rgb(R G B / a)` when `alpha` is below 1 (R, G, B are `components` × 255, rounded; `a` is `alpha`); dimension → `<value><unit>`; fontFamily → the string, or the array joined with `, `; shadow → a CSS `box-shadow` string whose colours flatten by the same colour rule; an alias `{a.b}` → `var(--token-a-b)`. The base file goes in `:root`, the dark file's tokens in a `.dark { … }` block.

```css
:root  { --token-color-primary: #3366e6; --token-radius-base: 8px;
         --token-font-body: "Inter", system-ui, sans-serif; }
.dark  { --token-color-primary: #7aa2ff; }
```

## Writing it

Run after the approved proposal in `tree/03_brand/README.md § Writing it` (step 5), so every value matches what `identity.md` describes.

1. Write every token in the required-tokens table, with the shapes above, to `_concept/03_brand/brand.tokens.json`.
2. Validate it against `tree/03_brand/brand-tokens.schema.json` before writing.
3. When the brand has a dark mode, write `_concept/03_brand/brand.dark.tokens.json` (the colour overrides) and `_concept/03_brand/brand.resolver.json` as shown above; a one-mode brand writes neither.
4. Record the approval twice, in the same write as the user's yes: `approved: <date>` in `identity.md` frontmatter (`tree/03_brand/identity.md`) and the same date in `$extensions["ai.skaile"].approved` of the base file, because tools read the token file without opening `identity.md`. Both stay absent until the user approves, and a later edit that changes the substance clears both.

## Checks

Every required token is present with its `$type`, the base file passes `tree/03_brand/brand-tokens.schema.json`, the base file's `$extensions["ai.skaile"].mode` is `light` or `dark` and agrees with `mode` in `identity.md` (`both` in `identity.md` means the base is `light` and the dark file and resolver exist), and both approval stamps agree.
