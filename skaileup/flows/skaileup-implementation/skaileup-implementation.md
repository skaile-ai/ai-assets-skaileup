---
title: "skaileup-implementation"
description: "Start-in-the-middle flow — build features now while the full concept is discovered gradually, feature by feature, asking the user open questions just-in-time."
order: 12
---

The **skaileup-implementation** flow is the "superpowers" shape: you don't write
the whole concept up front, you **start in the middle and build the concept
gradually**. A thin foundation is laid once, then a single per-feature loop
interleaves the two slice loops — `concept-slice` discovers *this* feature's
concept (and surfaces the open questions it needs answered), then `impl-slice`
builds it, and the loop repeats for the next feature.

The **"spec" here is the full concept** — journeys, screens, behaviors, design —
not a one-off technical plan. It's just grown **just-in-time**: each iteration
the concept-slice phase transparently discovers what's missing for the feature
at hand, asks the user the open questions, and accretes the answers into the
canonical `_concept/` tree. Nothing is front-loaded beyond the minimum needed to
run code.

## How it differs from the other impl flows

| Flow | "Spec" it builds | Concept timing |
|---|---|---|
| [`skaileup-impl`](../skaileup-impl/) | none — consumes a handed-off concept | fully upfront (elsewhere) |
| [`skaileup-impl-standalone`](../skaileup-impl-standalone/) | impl plan only (technical) | per slice, technical only |
| **`skaileup-implementation`** | **full concept (all parts)** | **per feature, discovered + asked** |

## When to use

When you want to begin building immediately, don't have (and don't want to
write) a full concept up front, but still want a real concept to accumulate as
you go — with the flow asking you the open questions feature by feature.

## Pipeline

```
scope-project            (asks shape/size open questions → scope.yaml)
  → brief?               (one-paragraph seed, optional)
  → techstack → datamodel-skeleton → scaffold → foundation → migrate?
  → ┌─ per feature, repeat ──────────────────────────────────────────┐
    │  concept-slice   (discover the feature's concept; ask the user) │
    │    → impl-slice  (build it: plan → implement → test → commit)   │
    └──────────────── loop back for the next feature ────────────────┘
  → impl-quality-ready   (when the backlog is exhausted)
```

The loop is a `review-loop` edge from `impl-slice` back to `concept-slice`; it
exits to `ready` when no unbuilt features remain.

## Install manifest

Self-contained: `skaileup-implementation.flow.yaml` carries a top-level
`requires:` block — `shared-contracts` + `conceptualization-contract` +
`implementation-contract`, the thin-foundation skills (scope, brief, techstack,
datamodel, scaffold, foundation, migrate), `impl-quality-ready`, and the two
sub-flows `flow:concept-slice` + `flow:impl-slice`. **No new skills** — the loops
are delegated to the slice flows, whose own manifests provide their skills.

## Run it

```bash
skaile add flow:skaileup-implementation
skaile run flow:skaileup-implementation
```

## See also

- [`concept-slice`](../concept-slice/) — the per-feature concept loop this flow delegates to
- [`impl-slice`](../impl-slice/) — the per-feature build loop this flow delegates to
- [Slice loops](../../../intro/slice-loops/) — the shared five-phase shape
