---
title: "Flows"
description: "The tier flows and the two reusable slice-loop building blocks, each paired with a bundle."
sidebar:
  label: "Overview"
  order: 0
---


A **flow** is an executable pipeline; its paired **bundle** lists exactly the
skills the flow runs. Install the bundle, run the flow:

```bash
skaile add bundle:<name>     # install the skills
skaile run flow:<name>       # execute the pipeline
```

## Tier flows

Four sizes, chosen by `scope-project`. Bundles inherit
(`mvp ⊂ simple-app ⊂ standard-app ⊂ complex-app`); each bundle lists only its
additions.

| Flow | Scope | Shape |
|---|---|---|
| [`mvp`](./mvp/) | 1 feature, trivial persistence | one linear pass |
| [`simple-app`](./simple-app/) | single-user, ≤5 features | linear concept + impl-slice loop |
| [`standard-app`](./standard-app/) | multi-user, ≤20 features | high-level concept + concept-slice & impl-slice loops |
| [`complex-app`](./complex-app/) | multi-product / enterprise | standard-app superset + project-ops + audit |

## Slice-loop building blocks

Not tiers — reusable per-feature loops the tier flows inline once per feature.
Both are standalone-runnable.

| Flow | Loop |
|---|---|
| [`concept-slice`](./concept-slice/) | brainstorm → align → scope-feature → design-feature |
| [`impl-slice`](./impl-slice/) | plan → implement → test → recap → refactor → commit |

## See also

- [Tiers](../intro/tiers/) — the `scope-project` decision rule
- [Flows + Bundles](../intro/flows-and-bundles/) — the flow↔bundle contract and drift guard
- [Slice loops](../intro/slice-loops/) — the shared five-phase shape

