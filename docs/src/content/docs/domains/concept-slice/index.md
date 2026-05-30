---
title: "concept-slice"
description: "Per-feature concept loop (big apps only): brainstorm · align · scope-feature · design-feature"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`skaileup/concept-slice/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/concept-slice/DOMAIN.md)
:::


# concept-slice

Runs the concept loop at per-feature granularity for large applications. Each pass through the four-skill sequence produces one feature's permanent `_concept/` artifacts (feature spec, screen specs, mockup stub) and then deletes its scratch. Use when `_concept/_meta/scope.yaml` declares tier `standard-app` or `complex-app`.

## Skills

- **concept-slice-brainstorm** (`brainstorm/`) — Open-ended interview: surfaces who uses the feature, what triggers it, and the happy path. Writes `_slice/concept/{slice_id}/brainstorm.md`.
- **concept-slice-align** (`align/`) — Adversarial grilling: edge cases, error states, role/permission gaps. Produces EARS-format acceptance criteria in `_slice/concept/{slice_id}/align.md`. Entry point for `simple-app` tier (skips brainstorm).
- **concept-slice-scope-feature** (`scope-feature/`) — Forces an IN/OUT/DEFER decision on every edge-case item from align. Writes `_slice/concept/{slice_id}/scope-feature.md`.
- **concept-slice-design-feature** (`design-feature/`) — Commits permanent artifacts: `_concept/experience/features/{slice_id}.md`, screen specs under `_concept/experience/screens/`, and a mockup-walkthrough stub. Deletes `_slice/concept/{slice_id}/` on success.

## When to Use

- `_concept/_meta/scope.yaml` exists and tier is `standard-app` or `complex-app`
- The product has more features than can be designed in a single context window
- Starting a new feature after the top-level concept phase is complete
- Re-entering design for a feature that was deferred in an earlier pass

## When NOT to Use

- Tier is `mvp` — use the linear concept pipeline instead
- No `_concept/_meta/scope.yaml` — run `skaileup-orchestrator/scope/` first
- Feature is already fully specced in `_concept/experience/features/` — go straight to `impl-plan` or `impl-slice`

## Sequence

```
brainstorm → align → scope-feature → design-feature
```

Each skill reads the previous phase's scratch file. `/clear` between phases. `design-feature` is the only step that writes to `_concept/`; the rest write only to `_slice/concept/{slice_id}/`.

## Cross-references

- `skaileup/contracts/` — iron laws and EARS acceptance-criteria schema read by `align`
- `skaileup/concept/` — linear concept pipeline for `mvp`/`simple-app` tiers
- `skaileup/impl-slice/` — mirrors this loop on the implementation side
- `skaileup/mockup-walkthrough/` — `design-feature` emits a stub consumed here


## Skills in this domain

- [concept-slice-align](./concept-slice-align/) — Use when concept-slice-brainstorm has completed (or as the entry point for simple-app) and you need to grill the user about THIS feature — s
- [concept-slice-brainstorm](./concept-slice-brainstorm/) — Use when starting per-feature concept work for a standard-app or complex-app — sparring partner that surfaces the user's mental model for TH
- [concept-slice-design-feature](./concept-slice-design-feature/) — Use when concept-slice-scope-feature has completed and you need to commit THIS feature's permanent _concept/ artifacts — the feature spec, a
- [concept-slice-scope-feature](./concept-slice-scope-feature/) — Use when concept-slice-align has completed and you need to draw the IN/OUT line for THIS feature — reads align's edge-case list, forces an I
