---
title: "skaileup-stepwise"
description: "Start-in-the-middle flow — build features now while the concept is grown gradually, feature by feature, with the slice asking the user open questions just-in-time."
order: 12
---

The **skaileup-stepwise** flow is the "start-in-the-middle" shape: you don't write
the whole concept up front, you **start in the middle and grow the concept as you
build**. A thin foundation is laid once, then a single per-feature loop runs the
unified [`skaileup-slice`](../skaileup-slice/) block at
`concept_depth: just-in-time`. The slice's concept half runs the **concept-needs
check** — it detects what *this* feature is missing, asks the user the open
questions, and seeds only the minimum into `_concept/` — then its impl half
builds the feature, and the loop repeats.

Concept is **never front-loaded**: it accretes as a by-product of building, only
what each feature needs. Nothing is produced beyond the minimum required to run
the feature's code.

## How it differs from the other impl flows

| Flow | Concept it builds | Concept timing |
|---|---|---|
| [`skaileup-implementation`](../skaileup-implementation/) | none (read-or-generate architecture only) | pre-existing, or generated once |
| [`appbuilder-standard`](../appbuilder-standard/) | full per-feature design (`skaileup-slice` at `concept_depth: full`) | per feature, designed before building |
| **`skaileup-stepwise`** | **only what each feature needs** (`skaileup-slice` at `concept_depth: just-in-time`) | **per feature, discovered + asked while building** |

## When to use

When you want to begin building immediately, don't have (and don't want to
write) a full concept up front, but still want a real concept to accumulate as
you go — with the slice asking you the open questions feature by feature.

## Pipeline

```
scope-project            (asks shape/size open questions → scope.yaml)
  → brief?               (one-paragraph seed, optional)
  → techstack → datamodel-skeleton → scaffold → foundation → migrate?
  → ┌─ per feature, repeat ───────────────────────────────────────────────┐
    │  skaileup-slice  (concept_depth: just-in-time)                       │
    │    concept half: concept-needs check → ask the user → seed minimum   │
    │    impl half:    plan → implement → test → commit                    │
    └──────────────────── loop back for the next feature ─────────────────┘
  → impl-quality-ready   (when the backlog is exhausted)
```

The loop is a `review-loop` self-edge on the slice node; it exits to `ready` when
no unbuilt features remain.

## Install manifest

Self-contained: `skaileup-stepwise.flow.yaml` carries a top-level
`requires:` block — `shared-contracts` + `conceptualization-contract` +
`implementation-contract`, the thin-foundation skills (scope, brief, techstack,
datamodel, scaffold, foundation, migrate), `impl-quality-ready`, and the unified
sub-flow `flow:skaileup-slice`. **No new skills** — the per-feature work is
delegated to `skaileup-slice`, whose manifest (and its two sub-flows') provides
the skills.

## Run it

```bash
skaile add flow:skaileup-stepwise
skaile run flow:skaileup-stepwise
```

## See also

- [`skaileup-slice`](../skaileup-slice/) — the unified per-feature block this flow delegates to
- [`skaileup-implementation`](../skaileup-implementation/) — code-build with no concept-design pass
- [Slice loops](../../../intro/slice-loops/) — the shared five-phase shape
