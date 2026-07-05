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
Conceptualization: scope → onboard → seeds? ∥ research? → [concept-discovery goals=required] →
                   brand-visual → brand-voice? → inspiration? → journeys → features →
                   behaviors? → screens → screens-technical? → components? →
                   [architecture templates=skip] → text-walkthrough?
Review:            concept review
```

`[concept-discovery]` runs with `goals: required` (goals is optional in most
tiers, but concept-only always produces it) and delegates brief → goals →
comparable?; `[architecture]` runs with `templates: skip` and delegates
techstack → system → datamodel (no template resolution — there's no build to
scaffold against yet).

## Install manifest

Self-contained: `concept-only.flow.yaml` carries a top-level `requires:` block —
`shared-contracts` + `conceptualization-contract` + `meta-concept-contract`
plus its own direct concept skills (scope, grounding onboard/seeds/research,
design, experience, optional text walkthrough, ops-review) plus two `flow:`
refs for the sub-flows it delegates to (`concept-discovery`, `architecture`).
No inheritance, no extras.

## Run it

```bash
skaile add flow:skaileup-concept-only       # install the flow + its skills + contracts
skaile run flow:skaileup-concept-only       # execute the concept pipeline
```

When ready to build, hand the concept to a tier flow (e.g. `appbuilder-standard`) — the
concept artifacts it produced are the inputs those flows read.

## See also

- [`appbuilder-standard`](../appbuilder-standard/) — the tier to continue into for implementation
- [`reverse-engineer`](../reverse-engineer/) — the inverse: concept *from* code
- [Slice loops](../../../intro/slice-loops/) — how concept work scales per-feature
