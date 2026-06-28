---
title: "impl-slice"
description: "The per-feature implementation loop — a reusable building block the tier flows delegate to via a sub-flow node, once per feature."
order: 6
---

The **impl-slice** flow is not a tier — it is the **per-feature implementation
loop**, the canonical building block that `appbuilder-simple`, `appbuilder-standard`,
`appbuilder-complex`, and `appbuilder-cli` delegate to via a **sub-flow node**, once per
feature. It cuts a vertical slice (UI + logic + data) for one feature and is
standalone-runnable.

## When to use

- A tier flow runs it automatically, once per feature.
- Standalone: to implement one feature against an existing architecture —
  `skaile run flow:skaileup-impl-slice`.

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

The tier flows delegate to this full loop via a sub-flow node, so
`appbuilder-simple`, `appbuilder-standard`, `appbuilder-complex`, and `appbuilder-cli` all run every phase.
Only `appbuilder-mvp` keeps a trimmed inline pass (`plan-vertical → implement → commit`),
since its defining trait is a single linear build with no loop.

## Install manifest

`impl-slice.flow.yaml` carries a top-level `requires:` block listing
`shared-contracts` plus the `impl-plan-*` planning skills and the `impl-slice-*`
build skills — everything installed when you `skaile add flow:skaileup-impl-slice` to run
the slice standalone. Tier flows that inline these nodes list the same skills in
their own `requires:`.

## Scratch lifecycle

Scratch in `_implementation/slices/<id>/` is **deleted on commit** — truth lives in the
committed code.

## See also

- [Slice loops](../../../intro/slice-loops/) — the shared five-phase shape
- [`concept-slice`](../concept-slice/) — the concept-side counterpart
- [`appbuilder-simple`](../appbuilder-simple/) · [`appbuilder-standard`](../appbuilder-standard/) · [`appbuilder-complex`](../appbuilder-complex/)
