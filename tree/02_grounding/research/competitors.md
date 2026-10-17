---
path: _concept/02_grounding/research/competitors.md
summary: per-product analysis of comparable products
writers: [concept-research]
---

# _concept/02_grounding/research/competitors.md

One analysis per comparable product. `concept-brief` cites it for the analysis behind a product
named in `## Comparables`, and `spec-featuresets` treats a gap users complain about here as a
candidate feature with evidence behind it.

## Format

```yaml
---
products_analyzed: 5
last_updated: YYYY-MM-DD
---
```

Per product: features, strengths, the gaps users complain about, pricing, audience, and what it
means for this product. A feature that could not be verified is written as "not publicly
available" rather than filled in; `products_analyzed` equals the number of product sections.

## Writing it

1. Put the user's own comparables (from `brief.md § Comparables` or the onboarding answers)
   first, then the products research found.
2. Dispatch and write per `tree/02_grounding/research/README.md`, with a source against every
   claim.

## Checks

`products_analyzed` matches the product sections and every claim names its source.
