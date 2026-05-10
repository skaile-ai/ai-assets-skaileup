---
name: concept-slice
description: "Per-feature concept loop (big apps only): brainstorm · align · scope-feature · design-feature"
metadata:
  stage: alpha
  type: domain
---

# concept-slice

Runs the concept loop at a per-feature granularity for large applications: brainstorm, align, scope, and design each feature slice individually. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **concept-slice-brainstorm** (`brainstorm/`) — Per-feature sparring partner that surfaces the user's mental model for one feature (who uses it, what triggers it, the happy path, what's clearly out).
- **concept-slice-align** (`align/`) — Grills the user about a single feature: edge cases, unstated rules, error states, role/permission gaps; produces EARS-format acceptance criteria.
- **concept-slice-scope-feature** (`scope-feature/`) — Forces an IN/OUT/DEFER decision on each edge-case item from align and produces the final scope decision the design step honors.
- **concept-slice-design-feature** (`design-feature/`) — Commits the feature's permanent `_concept/` artifacts (feature spec, screen specs, mockup-walkthrough stub) and clears the slice scratch on success.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.
