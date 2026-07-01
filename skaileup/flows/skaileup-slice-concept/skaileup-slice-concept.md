---
title: "slice-concept"
description: "The concept half of the unified skaileup-slice block — the per-feature concept loop, with a just-in-time concept-needs mode."
order: 5
---

The **skaileup-slice-concept** flow is the **concept half** of the unified
[`skaileup-slice`](../skaileup-slice/) block: the per-feature concept loop. The
`skaileup-slice` parent runs it before `skaileup-slice-impl`; it is also
standalone-runnable for designing a single feature.

## Concept depth

A `concept_depth` global controls how much it produces per feature (the parent
forwards it via the sub-flow node's `parameters.concept_depth`):

| `concept_depth` | Behaviour | Used by |
|---|---|---|
| `full` | Run all four phases — complete per-feature concept design | `appbuilder-standard` / `appbuilder-complex` |
| `just-in-time` | Run the **concept-needs check**: detect which concept artifacts this feature is missing or under-specifies, ask the user the open questions, and write only the minimal versions needed to build it | `skaileup-stepwise` (start-in-the-middle) |
| `skip` | No-op — concept already exists up-front | linear tiers that run impl only |

## When to use

- The `skaileup-slice` parent runs it automatically, once per feature.
- Standalone: to design one feature in depth against an existing concept —
  `skaile run flow:skaileup-slice-concept`.

## Pipeline

```
brainstorm → align → scope-feature → design-feature
   /clear      /clear     /clear
```

Each phase writes a handoff file under `_concept/slices/<id>/` and `/clear`s
before the next, so no phase holds the whole slice in context. On
`design-feature` the result is appended to the permanent concept artifacts
(`product-spec/features/`, `experience/screens/`, mockups, this feature's
datamodel entities). In `just-in-time` mode only the artifacts the feature
actually needs are produced.

| Phase | What it does |
|---|---|
| `brainstorm` | Sparring on what the feature is. In just-in-time mode this runs the concept-needs check + open questions |
| `align` | AI interviews the user — surfaces edge cases, makes acceptance criteria explicit |
| `scope-feature` | Fixes what's IN and OUT — prevents mid-design scope creep |
| `design-feature` | Appends feature spec, screens, mockup, datamodel entities |

## Install manifest

`skaileup-slice-concept.flow.yaml` carries a top-level `requires:` block listing
`shared-contracts` plus the four `concept-slice-*` skills — everything installed
when you `skaile add flow:skaileup-slice-concept` to run the slice standalone.

## Slice dossier lifecycle

The phase handoffs in `_concept/slices/<id>/` are **frozen, not deleted**: the
terminator writes an `index.md` and keeps them as permanent per-feature
documentation. Truth still lives in the canonical `_concept/...` artifacts the
slice appends to.

## See also

- [Slice loops](../../../intro/slice-loops/) — the shared five-phase shape
- [`skaileup-slice`](../skaileup-slice/) — the unified parent block
- [`skaileup-slice-impl`](../skaileup-slice-impl/) — the implementation-side counterpart
- [`appbuilder-standard`](../appbuilder-standard/) · [`appbuilder-complex`](../appbuilder-complex/) — the tiers that delegate to this
