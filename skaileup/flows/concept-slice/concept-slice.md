---
title: "concept-slice"
description: "The per-feature concept loop — a reusable building block that appbuilder-standard and appbuilder-complex inline once per feature."
order: 5
---

The **concept-slice** flow is not a tier — it is the **per-feature concept
loop**, a canonical building block that the `appbuilder-standard` and `appbuilder-complex`
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

Each phase writes a scratch file under `_concept/slices/<id>/` and `/clear`s
before the next, so no phase holds the whole slice in context. On
`design-feature` the result is appended to the permanent concept artifacts
(`product-spec/features/`, `experience/screens/`, mockups, this feature's
datamodel entities).

| Phase | What it does |
|---|---|
| `brainstorm` | Sparring on what the feature is (appbuilder-complex only; appbuilder-standard skips it) |
| `align` | AI interviews the user — surfaces edge cases, makes acceptance criteria explicit |
| `scope-feature` | Fixes what's IN and OUT — prevents mid-design scope creep |
| `design-feature` | Appends feature spec, screens, mockup, datamodel entities |

## Install manifest

`concept-slice.flow.yaml` carries a top-level `requires:` block listing
`shared-contracts` plus the four `concept-slice-*` skills — everything installed
when you `skaile add flow:concept-slice` to run the slice standalone. Tier flows
that inline these nodes list the same skills in their own `requires:`.

## Scratch lifecycle

Scratch in `_concept/slices/<id>/` is **deleted on completion** — truth lives in
the permanent `_concept/` artifacts the slice appends to.

## See also

- [Slice loops](../../../intro/slice-loops/) — the shared five-phase shape
- [`impl-slice`](../impl-slice/) — the implementation-side counterpart
- [`appbuilder-standard`](../appbuilder-standard/) · [`appbuilder-complex`](../appbuilder-complex/) — the tiers that inline this
