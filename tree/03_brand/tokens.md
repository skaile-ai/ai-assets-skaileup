---
path: _concept/03_brand/tokens.json
summary: machine-readable design tokens
writers: [design-brand]
---

# _concept/03_brand/tokens.json

The brand in machine-readable form. The walkthrough flattens it into `--token-*` CSS custom properties and storybook themes from it, so a missing key becomes a bland default in every rendered screen; both mockup renderers hard-gate on this file. A data file — no frontmatter.

## Format

Keys, all required:

| key | content |
|---|---|
| `colors` | `primary`, `secondary`, `accent`, `background`, `surface`, `text`, `text_muted`, `border`, `error`, `success`, `warning` |
| `fonts` | the type families by role |
| `radius` | corner radius |
| `mode` | `light`, `dark` or `both` |
| `spacing_base` | the base spacing unit |
| `shadows` | the elevation scale |
| `atmosphere` | the background treatment the identity describes |
| `tailwind` | a block of CSS custom properties derived from the keys above |

```json
{
  "colors": { "primary": "#1F4E5F", "secondary": "#E8DCC8", "accent": "#D9622B",
              "background": "#FAF7F2", "surface": "#FFFFFF", "text": "#1B1B1B",
              "text_muted": "#6B6B6B", "border": "#E2DCD0", "error": "#B3261E",
              "success": "#2E7D32", "warning": "#B26A00" },
  "fonts": { "heading": "Fraunces", "body": "Inter" },
  "radius": "6px",
  "mode": "light",
  "spacing_base": "8px",
  "shadows": { "sm": "0 1px 2px rgba(0,0,0,.08)" },
  "atmosphere": "warm paper grain",
  "tailwind": { "--color-primary": "#1F4E5F" }
}
```

## Writing it

Fill it from the approved proposal in `tree/03_brand/README.md § Writing it` (step 5), so every value matches what `identity.md` describes.

## Checks

Every key above is present and `mode` equals `mode` in `identity.md`.
