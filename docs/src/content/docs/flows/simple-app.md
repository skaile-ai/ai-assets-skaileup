---
title: "simple-app"
description: "Single-user app of up to ~5 features — linear concept pipeline plus a per-feature impl-slice loop."
sourcePath: "skaileup/flows/simple-app/simple-app.md"
sidebar:
  label: "simple-app"
  order: 2
---

:::note[Flow manifest]
**Flow:** [`skaileup/flows/simple-app/simple-app.flow.yaml`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/flows/simple-app/simple-app.flow.yaml)
**Bundle:** [`skaileup/flows/simple-app/simple-app.bundle.yaml`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/flows/simple-app/simple-app.bundle.yaml)
:::


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

## Paired bundle

`simple-app.bundle.yaml` **inherits `mvp`** and lists only its additions
(brand-visual, journeys, screens, static-html walkthrough, isolated-html
component mockup, datamodel, the `impl-build` setup skills, impl-slice
`test`/`recap`, and `test-e2e`).

> **Note — inherited variant.** The bundle carries `mockup-walkthrough-text`
> from mvp even though this tier renders with `mockup-walkthrough-static-html`.
> Installing the inherited variant is a no-op; the flow verifier reports it as a
> "tier-shape extra" warning by design.

## Run it

```bash
skaile add bundle:simple-app
skaile run flow:simple-app
```

## See also

- [`mvp`](../mvp/) — the tier below · [`standard-app`](../standard-app/) — the tier above
- [`impl-slice`](../impl-slice/) — the per-feature loop reused here
- [Tiers](../../../intro/tiers/) · [Flows + Bundles](../../../intro/flows-and-bundles/)

