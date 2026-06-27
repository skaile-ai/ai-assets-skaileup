---
title: "skaileup-impl"
description: "Implementation-only flow (handoff) — no concept pass; reads an existing concept package, then build + impl-slice loop + quality."
order: 10
---

The **skaileup-impl** flow builds an app from a concept package that already
exists — produced by [`concept-only`](../concept-only/) or handed off from
another team. It carries **zero concept skills**: a precondition gate verifies
the inputs, then it runs build setup, the per-feature impl-slice loop, and
quality. This is the smallest *full-build* install in the collection — because a
flow is its own install bundle, `skaile add flow:skaileup-impl` provisions only
the build + quality skills plus the impl-slice loop, nothing from the concept
half.

## When to use

When the concept is done (or owned elsewhere) and you only want to implement.

| Signal | skaileup-impl |
|---|---|
| Concept pass | none — required as input |
| Reads | `_concept/blueprint/`, `_concept/experience/features/` |
| Build | scaffold → foundation → infrastructure? → migrate → seed → docs |
| Slice loops | impl-slice, once per feature |
| Tests | unit + integration + e2e + ready |

If you have **no** concept package, use
[`skaileup-impl-standalone`](../skaileup-impl-standalone/), which generates the
architecture subset itself.

## Pipeline

```
[gate: require _concept/blueprint + features]
  → scaffold → foundation → infrastructure? → migrate → seed → docs
  → [per feature]  impl-slice loop  (brainstorm → align → plan-vertical
       → implement → test → recap → refactor → commit)
  → impl-quality-test-unit → -test-integration → -test-e2e → -ready
```

## Install manifest

Self-contained: `skaileup-impl.flow.yaml` carries a top-level `requires:` block —
`shared-contracts` + `implementation-contract`, the 6 build skills, the 4 quality
skills, and `flow:impl-slice`. No concept skills, no inheritance, no extras.

## Run it

```bash
skaile add flow:skaileup-impl       # install the flow + its skills + contracts
skaile run flow:skaileup-impl       # execute the pipeline
```

## See also

- [`concept-only`](../concept-only/) — produces the concept package this flow consumes
- [`skaileup-impl-standalone`](../skaileup-impl-standalone/) — same, but self-sufficient (no handoff)
- [`impl-slice`](../impl-slice/) — the per-feature loop this flow delegates to
