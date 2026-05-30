---
title: "impl-slice"
description: "The per-feature implementation loop — a reusable building block that simple-app, standard-app, and complex-app inline once per feature."
order: 6
---

The **impl-slice** flow is not a tier — it is the **per-feature implementation
loop**, the canonical building block that `simple-app`, `standard-app`, and
`complex-app` inline as nodes, once per feature. It cuts a vertical slice
(UI + logic + data) for one feature and is standalone-runnable.

## When to use

- A tier flow runs it automatically, once per feature.
- Standalone: to implement one feature against an existing architecture —
  `skaile run flow:impl-slice`.

## Pipeline

```
Plan:   impl-plan-brainstorm → impl-plan-align → impl-plan-plan-vertical
Build:  implement → test → recap → refactor → commit
          /clear between phases, scratch in _slice/impl/<id>/
```

| Phase | What it does |
|---|---|
| `brainstorm` → `align` → `plan-vertical` | Shape the slice; vertical plan = UI + logic + data for one feature |
| `implement` | Write the slice |
| `test` | Cover it |
| `recap` | Capture what changed / learned |
| `refactor` | Forced simplification pass — subtractions only (standard/complex tiers) |
| `commit` | Land it; scratch deleted |

Lower tiers run a trimmed loop: `mvp` is `plan-vertical → implement → commit`;
`simple-app` adds `align`, `test`, `recap`; `refactor` starts at `standard-app`.

## Paired bundle

`impl-slice.bundle.yaml` is a **leaf bundle** (no inheritance) listing the
`impl-plan-*` planning skills and the `impl-slice-*` build skills. Tier bundles
install these via their own inheritance; this bundle is for running the slice
standalone.

## Scratch lifecycle

Scratch in `_slice/impl/<id>/` is **deleted on commit** — truth lives in the
committed code.

## See also

- [Slice loops](../../../intro/slice-loops/) — the shared five-phase shape
- [`concept-slice`](../concept-slice/) — the concept-side counterpart
- [`simple-app`](../simple-app/) · [`standard-app`](../standard-app/) · [`complex-app`](../complex-app/)
