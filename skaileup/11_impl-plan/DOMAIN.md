---
name: impl-plan
description: "brainstorm · align · plan-vertical · supervised (testing-strategy is part of plan output)"
metadata:
  stage: alpha
  type: domain
---

# impl-plan

Turns a frozen feature spec into a vertical-slice implementation plan, then optionally executes it via supervised subagents. Used at the start of every impl-slice cycle before any code is written.

## Skills

- **impl-plan-brainstorm** (`brainstorm/`) — Sparring partner on risks, unknowns, and dependencies for a single feature. Writes `_implementation/slices/<id>/brainstorm.md`. Standard-app / complex-app tiers only.
- **impl-plan-align** (`align/`) — Grill-me interview surfacing unstated assumptions, technical constraints, and edge cases. Reads brainstorm.md (if present) and feature/screen specs; writes `_implementation/slices/<id>/align.md`.
- **impl-plan-plan-vertical** (`plan-vertical/`) — Decomposes the feature into vertical slices (UI + Logic + Data rows), adds testing strategy and an anti-horizontal-layering block. Writes `_implementation/slices/<id>/plan.md`.
- **impl-plan-supervised** (`supervised/`) — Dispatches one subagent per task from `_implementation/superpowers-plan.md`, enforces spec-compliance review before code-quality review, handles 4-status reports (DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED).

## When to Use

- Feature spec (`_concept/product-spec/features/<group>/<feature_slug>.md`) and screen specs are frozen and implementation is about to start.
- Any tier: mvp enters at plan-vertical; simple-app skips brainstorm; standard-app/complex-app run the full chain.
- Agent needs a decomposition that resists horizontal layering (all-API-first or all-DB-first patterns).
- Supervised subagent dispatch is wanted for parallelism or spec-compliance enforcement.

## When NOT to Use

- Concept work is still in progress — wait until `concept-slice` artifacts are frozen.
- A plan already exists in `_implementation/slices/<id>/plan.md` and the slice is underway — use `impl-slice` directly.
- Single-file fixes or hotfixes with no feature decomposition needed — skip to `impl-slice-implement`.

## Sequence

```
[standard-app / complex-app]  brainstorm → align → plan-vertical → (optional) supervised
[simple-app]                  align → plan-vertical → (optional) supervised
[mvp]                         plan-vertical → (optional) supervised
```

Each step reads the previous step's output. `/clear` between steps is recommended to avoid context bloat.

## Cross-references

- `../impl-slice/` — consumes `_implementation/slices/<id>/plan.md` produced here.
- `../concept-slice/` — produces the feature + screen artifacts this domain reads.
- `../skaileup/contracts/skill_grammar.md` — DSL reference.
- `../../../docs/devlog/SKILL_GRAPH.md` — collection-level view.
