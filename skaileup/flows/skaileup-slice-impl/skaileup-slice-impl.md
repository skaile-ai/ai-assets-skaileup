---
title: "slice-impl"
description: "The implementation half of the unified skaileup-slice block — the per-feature implementation loop."
order: 6
---

The **skaileup-slice-impl** flow is the **implementation half** of the unified
[`skaileup-slice`](../skaileup-slice/) block: the per-feature implementation
loop. The `skaileup-slice` parent runs it after `skaileup-slice-concept`; the
linear/impl-only tier flows (`appbuilder-simple`, `appbuilder-cli`,
`skaileup-implementation`) delegate to it directly via a **sub-flow node**, once per
feature. It cuts a vertical slice (UI + logic + data) for one feature and is
standalone-runnable.

## When to use

- The `skaileup-slice` parent or a linear tier runs it automatically, once per feature.
- Standalone: to implement one feature against an existing architecture —
  `skaile run flow:skaileup-slice-impl`.

## Pipeline

```
Plan:   impl-plan-brainstorm → impl-plan-align → impl-plan-plan-vertical
Build:  git-prepare → supervised → implement → implement-page? → test → recap → refactor → commit → git-finish
          /clear between phases, scratch in _implementation/slices/<id>/
```

The full loop runs the same way standalone and when delegated to from a tier:

| Phase | What it does |
|---|---|
| `brainstorm` → `align` → `plan-vertical` | Shape the slice; vertical plan = UI + logic + data for one feature |
| `git-prepare` | Cut the slice branch / prepare the working tree |
| `supervised` | Supervised dispatch with two-stage review — runs on every slice |
| `implement` | Write the slice |
| `implement-page` | Build the page(s) for the slice — optional, skipped for non-UI slices |
| `test` | Cover it |
| `recap` | Capture what changed / learned |
| `refactor` | Forced simplification pass — subtractions only |
| `commit` | Land it; scratch deleted |
| `git-finish` | Close out the slice / branch, persist git preferences, and gate the loop's completion |

Consumers delegate to this full loop via a sub-flow node — directly
(`appbuilder-simple`, `appbuilder-cli`, `skaileup-implementation`) or through the
`skaileup-slice` parent (`appbuilder-standard`, `appbuilder-complex`,
`skaileup-stepwise`) — so every phase runs the same way.
Only `appbuilder-mvp` keeps a trimmed inline pass (`plan-vertical → implement → commit`),
since its defining trait is a single linear build with no loop.

## Install manifest

`skaileup-slice-impl.flow.yaml` carries a top-level `requires:` block listing
`shared-contracts` plus the `impl-plan-*` planning skills and the `impl-slice-*`
build skills — everything installed when you `skaile add flow:skaileup-slice-impl`
to run the slice standalone.

## Scratch lifecycle

Scratch in `_implementation/slices/<id>/` is **deleted on commit** — truth lives in the
committed code.

## See also

- [Slice loops](../../../intro/slice-loops/) — the shared five-phase shape
- [`skaileup-slice`](../skaileup-slice/) — the unified parent block
- [`skaileup-slice-concept`](../skaileup-slice-concept/) — the concept-side counterpart
- [`appbuilder-simple`](../appbuilder-simple/) · [`appbuilder-standard`](../appbuilder-standard/) · [`appbuilder-complex`](../appbuilder-complex/)
