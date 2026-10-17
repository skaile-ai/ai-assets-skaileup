---
path: _concept/02_grounding/findings/index.md
summary: catalogue of findings files and raw material, with the skill that took each
writers: [concept-reverse, concept-research, design-brand]
---

# _concept/02_grounding/findings/index.md

The catalogue of everything in `findings/`. The `step` column tells a later reader which skill
took each item, and a screenshot without a row is raw material nobody can attribute.

## Format

A markdown table, one row per file, with the universal frontmatter
(`tree/README.md § Frontmatter every markdown artifact carries`):

```markdown
| file | source | date | step |
|---|---|---|---|
| brand.md | tailwind.config.ts, app.css | 2026-01-15 | concept-reverse |
| linear-home.png | https://linear.app | 2026-01-15 | design-brand |
```

`step` is the `name:` of the skill that took the item, character for character.

## Writing it

Each writer appends a row per file it adds, in the same write: `concept-reverse` for the six
evidence files, `concept-research` for its raw material, `design-brand` for each reference it
screenshots.

## Checks

Every file in `findings/` other than this one has a row, and every row's `step` names an
installed skill.
