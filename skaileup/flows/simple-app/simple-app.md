---
title: "simple-app"
description: "Single-user app of up to ~5 features — linear concept pipeline plus a per-feature impl-slice loop."
order: 2
---

The **simple-app** flow handles a single-user app of up to ~5 features. Concept
still runs linearly (no concept-slice loop), but implementation now repeats a
full **impl-slice loop** once per feature.

## When to use

Picked by `scope-project` for a focused single-user app — real persistence, a
handful of features, no multi-user concerns.

| Signal | simple-app |
|---|---|
| Feature count | ≤ 5 |
| Users | single |
| Concept | linear (brand + journeys + screens) |
| Impl | per-feature impl-slice loop |

## Pipeline

Inherits the mvp shape and adds design, experience, component mockups, the full
`impl-build` setup, and the impl-slice loop:

```
Concept (linear):
  scope-project → concept-brief → design-brand-visual
    → experience-journeys → product-spec-features → experience-screens
    → mockup-walkthrough-static-html → mockup-component-isolated-html

Setup (once):
  techstack → templates-select → datamodel
    → scaffold → foundation → migrate → seed → docs

Per-feature loop (impl-slice):
  impl-plan-align → impl-plan-plan-vertical
    → implement → test → recap → commit

Quality:
  test-unit + test-e2e
```

## Install manifest

The flow is self-contained: `simple-app.flow.yaml` carries a top-level
`requires:` block listing exactly what it installs — `shared-contracts` +
`implementation-contract` plus the 24 skills its nodes run, no more. No
inheritance and no extras: unlike the old inherited bundle it carries only the
skills this tier actually renders with (e.g. `mockup-walkthrough-static-html`,
never mvp's `mockup-walkthrough-text`).

## Run it

```bash
skaile add flow:simple-app    # install the flow + its skills + contracts
skaile run flow:simple-app
```

## See also

- [`mvp`](../mvp/) — the tier below · [`standard-app`](../standard-app/) — the tier above
- [`impl-slice`](../impl-slice/) — the per-feature loop reused here
- [Tiers](../../../intro/tiers/) · [Flows](../../../intro/flows-and-bundles/)
