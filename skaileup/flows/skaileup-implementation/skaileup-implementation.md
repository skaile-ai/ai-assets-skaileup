---
title: "skaileup-implementation"
description: "The code-build flow — no concept-design pass. Architecture is read-or-generate: reads an existing concept package if present, else generates the subset; then build + slice-impl loop + quality."
order: 11
---

The **skaileup-implementation** flow builds code with **no concept-design pass**. Its
architecture step is **read-or-generate**: if a concept package already exists —
handed off, or produced by [`skaileup-concept-only`](../skaileup-concept-only/)
or [`skaileup-concept-reverse`](../skaileup-concept-reverse/) — it reads
`_concept/blueprint/` (techstack → system → datamodel); otherwise it generates
that architecture subset from a one-line product description. Then it runs build
setup, the per-feature `skaileup-slice-impl` loop, and quality. No
UX/brand/journeys/screens/mockups — only the architecture required to write and
run code.

Each feature's spec is built **just-in-time** inside the slice loop: the
impl-plan brainstorm/align phase elicits the feature before implementing it, so
the concept accretes feature-by-feature instead of being front-loaded.

> Collapses the two former impl-only flows — a handoff gate and a standalone
> variant — which differed only by whether the concept pre-existed.
> Read-or-generate unifies them into one.

## When to use

When you want to go straight to code: building from an existing concept package,
or starting with none and not needing the UX-oriented concept pass.

| Signal | skaileup-implementation |
|---|---|
| Concept pass | none (architecture is read-or-generate) |
| Reads | `_concept/blueprint/` if present, else nothing |
| Build | scaffold → foundation → infrastructure? → migrate → seed → docs |
| Slice loop | `skaileup-slice-impl`, once per feature (spec elicited per slice) |
| Tests | unit + integration + e2e? + ready |

## Pipeline

```
Conceptualization: [architecture templates=skip]  (read-or-generate blueprint)
Implementation:    [impl-build-setup] → [skaileup-slice-impl] ↻ per feature
Review:            [quality-gate e2e=optional ops_tail=skip]
```

This flow is now pure composition: every node is a sub-flow node and its
`requires:` is `shared-contracts` plus four `flow:` refs.

`[architecture]` runs with `templates: skip` and delegates techstack → system →
datamodel, reading `_concept/blueprint/` if present, else generating that
subset; `[impl-build-setup]` delegates scaffold → foundation → infrastructure? →
migrate → seed → docs; `[skaileup-slice-impl]` runs once per feature
(brainstorm elicits the feature spec just-in-time → align → plan-vertical →
git-prepare → implement → implement-page → test → recap → refactor → commit →
git-finish); `[quality-gate]` runs with `e2e: optional` and `ops_tail: skip`,
delegating unit → integration → e2e? → ready (no ops review/sync tail).

## Install manifest

Self-contained: `skaileup-implementation.flow.yaml` carries a top-level
`requires:` block — `shared-contracts` plus four `flow:` refs
(`architecture`, `impl-build-setup`, `skaileup-slice-impl`, `quality-gate`).
No direct skills of its own, no UX/experience concept skills, no inheritance,
no extras — each sub-flow's own manifest transitively provides its skills and
contracts (e.g. `implementation-contract` comes in via `impl-build-setup`).

## Run it

```bash
skaile add flow:skaileup-implementation
skaile run flow:skaileup-implementation
```

## See also

- [`skaileup-concept-only`](../skaileup-concept-only/) · [`skaileup-concept-reverse`](../skaileup-concept-reverse/) — produce a concept package to build from
- [`skaileup-slice-impl`](../skaileup-slice-impl/) — the per-feature loop this flow delegates to
- [`skaileup-stepwise`](../skaileup-stepwise/) — start-in-the-middle: grows a real concept as it builds
- [Slice loops](../../../intro/slice-loops/) — the shared five-phase shape
