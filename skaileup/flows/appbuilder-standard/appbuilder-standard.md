---
title: "appbuilder-standard"
description: "Multi-user app of up to ~20 features — high-level concept pass plus per-feature concept-slice and impl-slice loops, with a feedback loop on mockups."
order: 3
---

The **appbuilder-standard** flow is the first tier where the product is too big to
design in one pass. Concept runs in **two passes**: a project-wide high-level
pass, then a per-feature `concept-slice` loop. Implementation runs a full
`impl-slice` loop per feature. Mockups gain a `mockup-feedback` annotation loop.

## When to use

Picked by `scope-project` for a multi-user app with a real feature backlog.

| Signal | appbuilder-standard |
|---|---|
| Feature count | ≤ 20 |
| Users | multi-user |
| Concept | high-level pass + per-feature concept-slice loop |
| Impl | per-feature impl-slice loop (with refactor) |
| Mockup feedback | annotate → triage → patch → apply |

## Pipeline

```
High-level concept (project-wide, one pass):
  scope-project → concept-brief → concept-goals → concept-comparable
    → design-brand-visual → design-inspiration
    → experience-journeys → experience-behaviors → product-spec-features
    → experience-screens → experience-components
    → mockup-walkthrough-astro → mockup-component-storybook
    → mockup-feedback: annotate → triage → patch → apply

Setup (once):
  techstack → templates-select → system → datamodel
    → scaffold → foundation → infrastructure → migrate → seed → docs

Per-feature loop:
  concept-slice:  align → scope-feature → design-feature   (no brainstorm)
  impl-slice:     brainstorm → align → plan-vertical
                    → implement → test → recap → refactor → commit

Quality:  test-unit + test-integration + test-e2e + ready
Ops:      review + sync
```

The high-level pass designs the "grand scheme"; the per-feature loop designs and
builds one feature at a time, learning from delivery before the next. See
[Slice loops](../../../intro/slice-loops/) for why.

## Install manifest

The flow is self-contained: `appbuilder-standard.flow.yaml` carries a top-level
`requires:` block listing exactly what it installs — `shared-contracts` +
`implementation-contract` plus every skill its nodes run (the full high-level
concept pass, Astro walkthrough + Storybook mockups, the `mockup-feedback`
cluster, the `concept-slice` skills, `impl-slice-refactor`, integration tests,
`ready`, and `ops` review/sync). No inheritance, no extras.

## Run it

```bash
skaile add flow:appbuilder-standard    # install the flow + its skills + contracts
skaile run flow:appbuilder-standard
```

## See also

- [`appbuilder-simple`](../appbuilder-simple/) — the tier below · [`appbuilder-complex`](../appbuilder-complex/) — the tier above
- [`concept-slice`](../concept-slice/) and [`impl-slice`](../impl-slice/) — the per-feature loops reused here
- [Slice loops](../../../intro/slice-loops/) · [Tiers](../../../intro/tiers/) · [Flows](../../../intro/flows-and-bundles/)
