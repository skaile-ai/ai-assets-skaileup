---
slug: concept-slice
description: "Per-feature concept loop (big apps only): brainstorm · align · scope-feature · design-feature"
metadata:
  stage: alpha
  type: domain
---

# concept-slice

Runs the concept loop at per-feature granularity for large applications. Each pass through the four-skill sequence produces one feature's permanent `_concept/` artifacts (feature spec, screen specs, mockup stub) and then freezes its slice dossier (writes `index.md`, keeps the phase handoffs as documentation). Use when `_concept/_meta/scope.yaml` declares tier `appbuilder-standard` or `appbuilder-complex`.

## Skills

- **concept-slice-brainstorm** (`brainstorm/`) — Open-ended interview: surfaces who uses the feature, what triggers it, and the happy path. Writes `_concept/slices/{slice_id}/brainstorm.md`.
- **concept-slice-align** (`align/`) — Adversarial grilling: edge cases, error states, role/permission gaps. Produces EARS-format acceptance criteria in `_concept/slices/{slice_id}/align.md`. Entry point for `appbuilder-simple` tier (skips brainstorm).
- **concept-slice-scope-feature** (`scope-feature/`) — Forces an IN/OUT/DEFER decision on every edge-case item from align. Writes `_concept/slices/{slice_id}/scope-feature.md`.
- **concept-slice-design-feature** (`design-feature/`) — Commits permanent artifacts: `_concept/experience/features/{slice_id}.md`, screen specs under `_concept/experience/screens/`, and a mockup-walkthrough stub. Freezes `_concept/slices/{slice_id}/` on success (writes index.md, keeps the dossier as documentation).

## When to Use

- `_concept/_meta/scope.yaml` exists and tier is `appbuilder-standard` or `appbuilder-complex`
- The product has more features than can be designed in a single context window
- Starting a new feature after the top-level concept phase is complete
- Re-entering design for a feature that was deferred in an earlier pass

## When NOT to Use

- Tier is `appbuilder-mvp` — use the linear concept pipeline instead
- No `_concept/_meta/scope.yaml` — run `skaileup-orchestrator/scope/` first
- Feature is already fully specced in `_concept/experience/features/` — go straight to `impl-plan` or `impl-slice`

## Sequence

```
brainstorm → align → scope-feature → design-feature
```

Each skill reads the previous phase's handoff. `/clear` between phases. `design-feature` is the only step that writes the canonical `_concept/experience/...` artifacts; all four write into the slice dossier `_concept/slices/{slice_id}/`, which is frozen (kept) on commit as permanent per-feature documentation.

## Cross-references

- `skaileup/contracts/` — iron laws and EARS acceptance-criteria schema read by `align`
- `skaileup/concept/` — linear concept pipeline for `appbuilder-mvp`/`appbuilder-simple` tiers
- `skaileup/impl-slice/` — mirrors this loop on the implementation side
- `skaileup/mockup-walkthrough/` — `design-feature` emits a stub consumed here
