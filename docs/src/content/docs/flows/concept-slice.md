---
title: "concept-slice"
description: "The per-feature concept loop — a reusable building block that standard-app and complex-app inline once per feature."
sourcePath: "skaileup/flows/concept-slice/concept-slice.md"
sidebar:
  label: "concept-slice"
  order: 5
---

:::note[Flow manifest]
**Flow:** [`skaileup/flows/concept-slice/concept-slice.flow.yaml`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/flows/concept-slice/concept-slice.flow.yaml)
**Bundle:** [`skaileup/flows/concept-slice/concept-slice.bundle.yaml`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/flows/concept-slice/concept-slice.bundle.yaml)
:::


The **concept-slice** flow is not a tier — it is the **per-feature concept
loop**, a canonical building block that the `standard-app` and `complex-app`
tier flows inline as nodes, once per feature in their backlog. It is also
standalone-runnable for designing a single feature.

## When to use

- A tier flow runs it automatically, once per feature.
- Standalone: when you want to design one feature in depth against an existing
  concept — `skaile run flow:concept-slice`.

## Pipeline

```
brainstorm → align → scope-feature → design-feature
   /clear      /clear     /clear
```

Each phase writes a scratch file under `_slice/concept/<id>/` and `/clear`s
before the next, so no phase holds the whole slice in context. On
`design-feature` the result is appended to the permanent concept artifacts
(`product-spec/features/`, `experience/screens/`, mockups, this feature's
datamodel entities).

| Phase | What it does |
|---|---|
| `brainstorm` | Sparring on what the feature is (complex-app only; standard-app skips it) |
| `align` | AI interviews the user — surfaces edge cases, makes acceptance criteria explicit |
| `scope-feature` | Fixes what's IN and OUT — prevents mid-design scope creep |
| `design-feature` | Appends feature spec, screens, mockup, datamodel entities |

## Paired bundle

`concept-slice.bundle.yaml` is a **leaf bundle** (no inheritance) listing the
four `concept-slice-*` skills. Tier bundles install these via their own
inheritance; this bundle is for running the slice standalone.

## Scratch lifecycle

Scratch in `_slice/concept/<id>/` is **deleted on completion** — truth lives in
the permanent `_concept/` artifacts the slice appends to.

## See also

- [Slice loops](../../../intro/slice-loops/) — the shared five-phase shape
- [`impl-slice`](../impl-slice/) — the implementation-side counterpart
- [`standard-app`](../standard-app/) · [`complex-app`](../complex-app/) — the tiers that inline this

