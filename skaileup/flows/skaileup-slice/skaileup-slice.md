---
title: "skaileup-slice"
description: "The unified per-feature building block — runs a feature's concept half then its impl half, with a concept_depth dial for how much concept to produce."
order: 4
---

The **skaileup-slice** flow is the unified per-feature building block: it runs a
feature's **concept half** then its **implementation half** by delegating to two
sub-flows — [`skaileup-slice-concept`](../skaileup-slice-concept/) then
[`skaileup-slice-impl`](../skaileup-slice-impl/). It is the single thing
consumers delegate to when they want both halves per feature.

## The `concept_depth` dial

One global controls how much concept the slice produces per feature. Consumers
set it on the sub-flow node's `parameters.concept_depth`; it is forwarded to the
concept half.

| `concept_depth` | Concept half | Used by |
|---|---|---|
| `full` | Complete per-feature concept design (all four phases) | `appbuilder-standard`, `appbuilder-complex` |
| `just-in-time` | Concept-needs check — detect what the feature is missing, ask the user, seed only the minimum | `skaileup-stepwise` (start-in-the-middle) |
| `skip` | No-op — concept already exists; run impl only | linear tiers (which usually delegate to `skaileup-slice-impl` directly instead) |

## When to use

- A tier or the start-in-the-middle flow delegates to it, once per feature.
- Standalone: to take one feature from concept through build —
  `skaile run flow:skaileup-slice`.

## Pipeline

```
slice-concept  (concept_depth: full | just-in-time | skip)
  → slice-impl  (plan → implement → test → recap → refactor → commit)
```

## Install manifest

Self-contained: `skaileup-slice.flow.yaml` carries a top-level `requires:` block —
`shared-contracts` plus the two sub-flows `flow:skaileup-slice-concept` +
`flow:skaileup-slice-impl`. The sub-flows' own manifests transitively provide
their node skills; the parent re-lists none of them.

## Run it

```bash
skaile add flow:skaileup-slice
skaile run flow:skaileup-slice
```

## See also

- [`skaileup-slice-concept`](../skaileup-slice-concept/) · [`skaileup-slice-impl`](../skaileup-slice-impl/) — the two halves
- [`appbuilder-standard`](../appbuilder-standard/) · [`skaileup-stepwise`](../skaileup-stepwise/) — the consumers that set `concept_depth`
- [Slice loops](../../../intro/slice-loops/) — the shared five-phase shape
