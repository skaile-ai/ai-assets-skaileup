---
name: impl-plan
description: "brainstorm · align · plan-vertical · supervised (testing-strategy is part of plan output)"
metadata:
  stage: alpha
  type: domain
---

# impl-plan

Produces the implementation plan through brainstorm, alignment, vertical slice planning, and supervised refinement; the testing strategy is included as part of the plan output. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **impl-plan-brainstorm** (`brainstorm/`) — Per-slice sparring partner on risks, unknowns, and dependencies for a single feature; writes `_slice/impl/<id>/brainstorm.md` for align to consume.
- **impl-plan-align** (`align/`) — Grill-me interview that surfaces unstated assumptions, technical constraints, and edge cases before plan-vertical writes the slice plan.
- **impl-plan-plan-vertical** (`plan-vertical/`) — Writes the per-slice vertical-decomposition plan (one row per user-facing slice — UI + Logic + Data) plus testing strategy and an anti-horizontal-nudge block.
- **impl-plan-supervised** (`supervised/`) — Supervised subagent-driven implementation orchestrator: dispatches one subagent per task, enforces spec-compliance review, handles 4-status reports and escalation.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.
