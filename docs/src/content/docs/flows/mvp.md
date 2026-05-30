---
title: "mvp"
description: "Smallest tier — a single-feature, trivial-persistence app built in one linear pass with no slice loops."
sidebar:
  label: "mvp"
  order: 1
---

:::note[Flow manifest]
**Flow:** [`skaileup/flows/mvp/mvp.flow.yaml`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/flows/mvp/mvp.flow.yaml)
**Bundle:** [`skaileup/flows/mvp/mvp.bundle.yaml`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/flows/mvp/mvp.bundle.yaml)
:::


The **mvp** flow is the smallest tier. One feature, trivial persistence, one
implementation pass — no concept-slice loop, no impl-slice loop, no recap or
refactor. The whole concept→build pipeline runs linearly.

## When to use

Picked by `scope-project` when the idea is a single capability with throwaway
or trivial persistence — a demo, a spike, a one-screen tool.

| Signal | mvp |
|---|---|
| Feature count | 1 |
| Users | single |
| Persistence | trivial / none |
| Slice loops | none — one linear pass |

If the app has more than one real feature, `scope-project` picks
[`simple-app`](../simple-app/) instead.

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
`simple-app`.

## Paired bundle

`mvp.bundle.yaml` is the root of the inheritance chain (`mvp ⊂ simple-app ⊂
standard-app ⊂ complex-app`) and lists every skill the flow runs — 11 skills,
no inheritance.

## Run it

```bash
skaile add bundle:mvp     # install the 11 skills
skaile run flow:mvp       # execute the linear pipeline
```

## See also

- [Tiers](../../../intro/tiers/) — how `scope-project` chooses a tier
- [Flows + Bundles](../../../intro/flows-and-bundles/) — the flow↔bundle contract
- [`simple-app`](../simple-app/) — the next tier up

