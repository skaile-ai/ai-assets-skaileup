---
path: _concept/03_brand/identity.md
summary: colours, fonts, tone of voice and copy guidelines
owner: [design-brand]
may_propose: []
---

# _concept/03_brand/identity.md

The written brand: the direction, how colour and type are used, and how the product speaks. Screen specs and copy in every later skill read it, and it is the only home of the tone of voice, so a voice left out here is invented again in every screen.

## Format

Frontmatter: `mood` (calm, bold, professional, playful …), `mode` (`light`, `dark` or `both`), then the universal fields from `tree/README.md § Frontmatter every markdown artifact carries` — `last_updated`, and `approved: <date>` once the user has said yes.

```markdown
---
mood: calm
mode: light
last_updated: 2026-10-16
approved: 2026-10-16
---

# Identity
## Direction
## Colour
## Type
## Spacing and elevation
## Atmosphere
## Memorable element
## Tone and copy
```

Body sections: the direction and why it fits this product; colour usage rules, each colour with the job it does; the type hierarchy; spacing; elevation; atmosphere; and the **memorable element**, the one thing that makes the app visually unmistakable.

**Tone and copy** holds how the product speaks (three or four adjectives, each with what it rules out), how it addresses the user, how errors, empty states and buttons read, and the words it avoids.

## Writing it

Follow the procedure in `tree/03_brand/README.md § Writing it`; this node is step 5's first file. `approved: <date>` is also recorded in the token file (`tree/03_brand/brand.tokens.md § Writing it`). Take Tone and copy from the brief and the direction the user approved, and ask only when those leave the voice open, built on the feeling chosen in step 2. `approved: <date>` is written with the user's yes, per `tree/README.md § Frontmatter every markdown artifact carries`.

## Checks

Every body section above is present, `mood` and `mode` match the token files (`tree/03_brand/brand.tokens.md § Light and dark`), and `approved:` is set.
