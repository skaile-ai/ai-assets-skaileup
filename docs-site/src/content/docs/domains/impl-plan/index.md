---
title: "impl-plan"
description: "brainstorm · align · plan-vertical · supervised (testing-strategy is part of plan output)"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`impl-plan/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/impl-plan/DOMAIN.md)
:::


# impl-plan

Produces the implementation plan through brainstorm, alignment, vertical slice planning, and supervised refinement; the testing strategy is included as part of the plan output. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **impl-plan-brainstorm** (`brainstorm/`) — Per-slice sparring partner on risks, unknowns, and dependencies for a single feature; writes `_slice/impl/<id>/brainstorm.md` for align to consume.
- **impl-plan-align** (`align/`) — Grill-me interview that surfaces unstated assumptions, technical constraints, and edge cases before plan-vertical writes the slice plan.
- **impl-plan-plan-vertical** (`plan-vertical/`) — Writes the per-slice vertical-decomposition plan (one row per user-facing slice — UI + Logic + Data) plus testing strategy and an anti-horizontal-nudge block.
- **impl-plan-supervised** (`supervised/`) — Supervised subagent-driven implementation orchestrator: dispatches one subagent per task, enforces spec-compliance review, handles 4-status reports and escalation.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.


## Skills in this domain

- [impl-plan-align](./impl-plan-align/) — Use when an implementation slice has its concept artifacts (feature.md + screens) frozen and needs a grill-me interview to surface unstated 
- [impl-plan-brainstorm](./impl-plan-brainstorm/) — Use when starting per-slice implementation work for a feature in a standard-app or complex-app tier project. Sparring partner on risks, unkn
- [impl-plan-plan-vertical](./impl-plan-plan-vertical/) — Use when an implementation slice has its align.md (or, for mvp, its feature.md) ready and needs a vertical-decomposition plan. Reads _slice/
- [impl-plan-supervised](./impl-plan-supervised/) — Supervised subagent-driven implementation. Dispatches one subagent per task from the superpowers plan, enforces spec-compliance review befor
