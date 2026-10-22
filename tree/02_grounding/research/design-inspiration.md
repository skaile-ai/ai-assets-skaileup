---
path: _concept/02_grounding/research/design-inspiration.md
summary: layout, colour, typography and component references with sources
owner: [concept-research]
may_propose: []
---

# _concept/02_grounding/research/design-inspiration.md

The visual references the screens will be designed against. `design-brand`, `experience-shell`
and `mockup-storybook` read it; it is the file that most often goes unwritten because the
competitor work ran long, and without it brand and shell are designed from nothing.

## Format

```yaml
---
references_collected: 8
last_updated: YYYY-MM-DD
---
```

Sections for layout patterns, colour directions, typography pairings and component patterns.
Each reference carries its source and where in this product it would apply;
`references_collected` equals the reference count. Once `_concept/03_brand/brand.tokens.json` exists,
references stay inside it — an off-palette reference collected after the brand is chosen is one
nothing can be built from.

## Writing it

1. Always write this file, whatever the scope.
2. Dispatch and write per `tree/02_grounding/research/README.md`; file screenshots under
   `tree/02_grounding/findings/README.md`.

## Checks

The file exists, `references_collected` matches, and every reference names its source and its
place in this product.
