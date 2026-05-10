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

Runs the concept loop at a per-feature granularity for large applications: brainstorm, align, scope, and design each feature slice individually. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **concept-slice-brainstorm** (`brainstorm/`) — Per-feature sparring partner that surfaces the user's mental model for one feature (who uses it, what triggers it, the happy path, what's clearly out).
- **concept-slice-align** (`align/`) — Grills the user about a single feature: edge cases, unstated rules, error states, role/permission gaps; produces EARS-format acceptance criteria.
- **concept-slice-scope-feature** (`scope-feature/`) — Forces an IN/OUT/DEFER decision on each edge-case item from align and produces the final scope decision the design step honors.
- **concept-slice-design-feature** (`design-feature/`) — Commits the feature's permanent `_concept/` artifacts (feature spec, screen specs, mockup-walkthrough stub) and clears the slice scratch on success.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.


## Skills in this domain

- [concept-slice-align](./concept-slice-align/) — Use when concept-slice-brainstorm has completed (or as the entry point for simple-app) and you need to grill the user about THIS feature — s
- [concept-slice-brainstorm](./concept-slice-brainstorm/) — Use when starting per-feature concept work for a standard-app or complex-app — sparring partner that surfaces the user's mental model for TH
- [concept-slice-design-feature](./concept-slice-design-feature/) — Use when concept-slice-scope-feature has completed and you need to commit THIS feature's permanent _concept/ artifacts — the feature spec, a
- [concept-slice-scope-feature](./concept-slice-scope-feature/) — Use when concept-slice-align has completed and you need to draw the IN/OUT line for THIS feature — reads align's edge-case list, forces an I
