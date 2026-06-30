---
title: "skaileup-impl"
description: "The code-build flow — no concept-design pass. Architecture is read-or-generate: reads an existing concept package if present, else generates the subset; then build + slice-impl loop + quality."
order: 11
---

The **skaileup-impl** flow builds code with **no concept-design pass**. Its
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

> Replaces the two former impl-only flows — the `skaileup-impl` handoff gate and
> `skaileup-impl-standalone` — which differed only by whether the concept
> pre-existed. Read-or-generate collapses them into one.

## When to use

When you want to go straight to code: building from an existing concept package,
or starting with none and not needing the UX-oriented concept pass.

| Signal | skaileup-impl |
|---|---|
| Concept pass | none (architecture is read-or-generate) |
| Reads | `_concept/blueprint/` if present, else nothing |
| Build | scaffold → foundation → infrastructure? → migrate → seed → docs |
| Slice loop | `skaileup-slice-impl`, once per feature (spec elicited per slice) |
| Tests | unit + integration + e2e? + ready |

## Pipeline

```
techstack → system → datamodel        (read _concept/blueprint/ if present, else generate)
  → scaffold → foundation → infrastructure? → migrate → seed → docs
  → [per feature]  skaileup-slice-impl loop  (brainstorm elicits the feature spec →
       align → plan-vertical → implement → test → recap → refactor → commit)
  → impl-quality-test-unit → -test-integration → -test-e2e? → -ready
```

## Install manifest

Self-contained: `skaileup-impl.flow.yaml` carries a top-level `requires:` block —
`shared-contracts` + `implementation-contract`, the 3 architecture skills, the 6
build skills, the 4 quality skills, and `flow:skaileup-slice-impl`. No
UX/experience concept skills, no inheritance, no extras.

## Run it

```bash
skaile add flow:skaileup-impl
skaile run flow:skaileup-impl
```

## See also

- [`skaileup-concept-only`](../skaileup-concept-only/) · [`skaileup-concept-reverse`](../skaileup-concept-reverse/) — produce a concept package to build from
- [`skaileup-slice-impl`](../skaileup-slice-impl/) — the per-feature loop this flow delegates to
- [`skaileup-implementation`](../skaileup-implementation/) — start-in-the-middle: grows a real concept as it builds
- [Slice loops](../../../intro/slice-loops/) — the shared five-phase shape
