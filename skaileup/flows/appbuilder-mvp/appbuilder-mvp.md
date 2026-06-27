---
title: "appbuilder-mvp"
description: "Smallest tier — a single-feature, trivial-persistence app built in one linear pass with no slice loops."
order: 1
---

The **appbuilder-mvp** flow is the smallest tier. One feature, trivial persistence, one
implementation pass — no concept-slice loop, no impl-slice loop, no recap or
refactor. The whole concept→build pipeline runs linearly.

## When to use

Picked by `scope-project` when the idea is a single capability with throwaway
or trivial persistence — a demo, a spike, a one-screen tool.

| Signal | appbuilder-mvp |
|---|---|
| Feature count | 1 |
| Users | single |
| Persistence | trivial / none |
| Slice loops | none — one linear pass |

If the app has more than one real feature, `scope-project` picks
[`appbuilder-simple`](../appbuilder-simple/) instead.

## Pipeline

```
scope-project → concept-brief → product-spec-features
  → mockup-walkthrough-text          (ASCII/linked text walkthrough)
  → techstack → templates-select     (pick the scaffold template)
  → scaffold
  → impl-plan-plan-vertical
  → impl-slice-implement → impl-slice-commit
  → impl-quality-test-unit
```

One impl pass, then commit. No `test`/`recap`/`refactor` phase — those start at
`appbuilder-simple`.

## Install manifest

The flow is self-contained: `appbuilder-mvp.flow.yaml` carries a top-level `requires:`
block listing exactly what it installs — `shared-contracts` plus the 11 skills
its nodes run. No separate bundle, no inheritance, no extras.

## Run it

```bash
skaile add flow:appbuilder-mvp       # install the flow + its 11 skills + contract
skaile run flow:appbuilder-mvp       # execute the linear pipeline
```

## See also

- [Tiers](../../../intro/tiers/) — how `scope-project` chooses a tier
- [Flows](../../../intro/flows-and-bundles/) — how a flow declares its dependencies
- [`appbuilder-simple`](../appbuilder-simple/) — the next tier up
