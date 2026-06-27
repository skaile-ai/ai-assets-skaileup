---
title: "concept-only"
description: "Variant flow that produces a complete concept package with no implementation — for planning, documentation, or team handoff."
order: 8
---

The **concept-only** flow runs the full concept pipeline and stops — no build,
no impl-slice loop. The output is a complete concept document package suitable
for planning, documentation, or handing off to a development team. It replaces
the legacy `concept-only` + `prototype` flows and is the canonical home for the
`concept-grounding-*` skills.

## When to use

Picked when the deliverable is the concept itself — a spec, a pitch, a handoff —
not running code.

| Signal | concept-only |
|---|---|
| Implementation | none |
| Grounding | onboard → seeds → research |
| Output | full concept package + optional text walkthrough |

## Pipeline

```
scope-project
  → grounding:   concept-grounding-onboard → seeds? → research?
  → discovery:   concept-brief → concept-goals → concept-comparable?
  → design:      design-brand-visual → brand-voice? → inspiration?
  → experience:  experience-journeys → product-spec-features → behaviors?
                   → experience-screens → screens-technical? → components?
  → architecture: techstack → system → datamodel
  → mockup-walkthrough-text?   → ops-review?
```

## Install manifest

Self-contained: `concept-only.flow.yaml` carries a top-level `requires:` block —
`shared-contracts` + `conceptualization-contract` + `meta-concept-contract` plus
exactly the concept skills its nodes run. No inheritance, no extras.

## Run it

```bash
skaile add flow:concept-only       # install the flow + its skills + contracts
skaile run flow:concept-only       # execute the concept pipeline
```

When ready to build, hand the concept to a tier flow (e.g. `appbuilder-standard`) — the
concept artifacts it produced are the inputs those flows read.

## See also

- [`appbuilder-standard`](../appbuilder-standard/) — the tier to continue into for implementation
- [`reverse-engineer`](../reverse-engineer/) — the inverse: concept *from* code
- [Slice loops](../../../intro/slice-loops/) — how concept work scales per-feature
