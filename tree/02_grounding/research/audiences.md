---
path: _concept/02_grounding/research/audiences.md
summary: personas with real job titles, tools, pain points and design implications
owner: [concept-research]
may_propose: []
---

# _concept/02_grounding/research/audiences.md

Personas grounded in the people who will use the product. `experience-journeys` reads it to
decide which journeys matter; a persona like "busy professional" describes nobody and produces
screens for nobody.

## Format

```yaml
---
personas_defined: 3
last_updated: YYYY-MM-DD
---
```

Per persona: a real job title, the tools they use today, their pain points, and the design
implications for this product. `personas_defined` equals the number of persona sections.

## Writing it

1. Start from the audience segments named in the answers or the brief.
2. Dispatch and write per `tree/02_grounding/research/README.md`, with a source against every
   claim.

## Checks

`personas_defined` matches the persona sections, and every persona names a real job title.
