---
path: _concept/02_grounding/findings/brand.md
summary: colours, type, radius, spacing and mode the repository's theme carries
writers: [concept-reverse]
---

# _concept/02_grounding/findings/brand.md

The brand the code already carries. `design-brand` seeds its draft from it and shows each graded
value as a proposal: only `extracted` values are what the code says, and `inferred` or
`needs_review` ones are the user's to settle before they reach `_concept/03_brand/brand.tokens.json`.

## Format

Frontmatter per `tree/02_grounding/findings/README.md`, with graded fields for:

- **Colours** — primary, secondary, accent, background, surface, text, muted text, border, and
  the semantic set (success, warning, error). A palette expressed as a scale (`50`…`900`) gives
  its `500` or most-used step as the value, with the scale noted in the body.
- **Typography** — heading, body and mono families, and the type scale where one is defined.
  Fonts loaded in the layout count even when the config does not name them.
- **Radius, spacing and elevation** — the default corner radius and the spacing unit show the
  design language (sharp, moderate, rounded, pill) more reliably than any prose in the repo.
- **Mode** — `light`, `dark` or `both`, from the `darkMode` strategy and whether a `.dark` block
  defines values.

## Writing it

1. Read in this order; a later source refines what an earlier one established rather than
   replacing it: `tailwind.config.{ts,js,mjs}` (`theme.extend.colors`, `fontFamily`,
   `borderRadius`, `darkMode`); CSS custom-property files (`tokens.css`, `variables.css`,
   `globals.css`, `app.css` — the `:root` and `.dark` blocks); design-token files
   (`tokens.json`, `design-tokens.json`, `*.tokens.json`, `*.tokens`, `*.resolver.json` — W3C DTCG; a
   resolver names the light and dark files — a `style-dictionary/` tree); theme providers
   (`ThemeProvider.tsx`, `theme.ts`, a Chakra or Mantine theme object); framework theme config
   (`nuxt.config.ts` `ui.colors`, a Vuetify theme block); the root layout or `app.vue` for
   global styles, loaded fonts and body classes.
2. Grade: a hex read from a config is `extracted`; a colour derived from usage frequency across
   components is `inferred` and says so.
3. A repository with no theme layer gets this file written with every field listed and
   `needs_review` throughout — a skeleton `design-brand` can report against beats an absence it
   has to rediscover, and `design-brand` still writes `brand.tokens.json` itself, since both mockup
   renderers hard-gate on that file. A palette assembled from taste when the repository
   declares none is indistinguishable from a real one and gets built against.

## Checks

Every field is listed and graded; colours come from a cited theme source or are `needs_review`.
