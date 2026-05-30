---
title: "concept-goals"
description: "Use on standard-app / complex-app concepts after the brief is approved, when goals deserve their own focused pass beyond the light version concept-brief writes. Interviews the user on success criteria, measurable KPIs, constraints, deadlines, and exp"
sidebar:
  label: "concept-goals"
---

:::note[Skill manifest]
**Name:** `concept-goals`
**Stage:** alpha · **Version:** 1.0.0
**Tags:** goals, success-criteria, kpi, metrics, constraints, scope, non-goals
**Source:** [`skaileup/concept/goals/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/concept/goals/SKILL.md)
:::


# Goals — Success Criteria & Constraints

## Overview

The **goals** skill is the focused success-criteria pass for larger concepts.
`concept-brief` writes a light `goals.md` inline; on standard-app / complex-app
this skill deepens it into measurable success criteria, explicit non-goals, and
hard constraints that downstream features, scope, and acceptance criteria are
checked against. It writes only `_concept/discovery/goals.md`.

## When to Use

- The brief is approved and the tier is standard-app or complex-app
- The user wants to pin down "what does success look like" before designing features
- The orchestrator dispatches this in the high-level concept pass, after `concept-brief`

## When NOT to Use

- mvp / simple-app tiers — the light `goals.md` from `concept-brief` is enough
- No `_concept/discovery/brief.md` yet — run `concept-brief` first
- The user wants per-feature acceptance criteria — that's `product-spec-features`

## Prerequisites

**REQUIRED BACKGROUND:** Read `contracts/concept_structure.md`,
`contracts/frontmatter.md`, and `contracts/agent_patterns.md` before proceeding.

**Hard gate:** `_concept/discovery/brief.md` must exist.

## Context Budget

| Action           | Path                                            | Required |
| ---------------- | ----------------------------------------------- | -------- |
| Must read        | `_concept/discovery/brief.md`                   | Yes      |
| Check if present | `_concept/discovery/goals.md`                   | No (deepen existing) |
| Check if present | `_concept/_grounding/overview/user_input.json`  | No (pre-answers)     |
| Never load       | `experience/`, `blueprint/`, downstream folders | —        |

## Standalone Mode

**Gate check:** `_concept/discovery/brief.md` must exist.
**On completion:** Present the goals summary, suggest `concept-comparable` or `design-brand-visual` next.

---

ROLE Goals agent — turns the brief vision into measurable success criteria, constraints, and non-goals in `_concept/discovery/goals.md`.

READS
\_concept/discovery/brief.md — vision, audience, problem, hero flow
? \_concept/discovery/goals.md — light goals version to deepen (if concept-brief wrote one)
? \_concept/\_grounding/overview/user_input.json — pre-collected success_criteria answer

WRITES
\_concept/discovery/goals.md — success criteria, KPIs, constraints, deadlines, non-goals

REFERENCES
contracts/concept_structure.md — valid \_concept/ paths
contracts/frontmatter.md — required YAML fields
contracts/agent_patterns.md — communication style, standalone mode

MUST tie every success criterion back to the brief's problem or hero flow
MUST make criteria measurable where possible — a number, a threshold, or a yes/no condition
MUST record explicit non-goals — what this product deliberately will NOT do
MUST deepen an existing goals.md rather than discarding its content
MUST wait for explicit human approval before handing off
NEVER invent deadlines, budgets, or metrics the user has not implied — mark them "TBD" instead
NEVER write features, screens, or tech decisions — goals only

EMIT [goals] started run_id=<uuid>

STEP 1: Gather context

- Read \_concept/discovery/brief.md for the vision, audience, problem, and hero flow
- IF \_concept/discovery/goals.md already exists, read it — treat its content as a first draft to deepen
- Check \_grounding/overview/user_input.json for a pre-collected success_criteria answer; use it if present

STEP 2: Interview (skip questions already answered)

- Ask one at a time, adapting to each answer:
  1. How will you know this product succeeded? (the single most important outcome)
  2. What measurable signals back that up? (adoption, retention, task time, error rate, revenue …)
  3. Any hard constraints? (deadline, budget, team size, compliance, platform)
  4. What is explicitly OUT of scope for v1 — things people might expect but you will NOT build?
  5. What would make this a failure even if it ships?
- For complex tier, probe for tiered goals (launch / 3-month / 12-month) and leading vs lagging metrics

EMIT [goals] checkpoint phase=interviewed

STEP 3: Write goals.md

- $ mkdir -p \_concept/discovery

OUTPUT \_concept/discovery/goals.md
---
primary_outcome: "<the one success condition>"
kpis: [<measurable signal>, ...]
constraints: [<deadline|budget|compliance|platform>, ...]
non_goals: [<deliberately excluded>, ...]
last_updated: <YYYY-MM-DD>
---
## Success Criteria
<Each criterion tied to the brief's problem/hero flow; measurable where possible.>

## Metrics / KPIs
<Leading and lagging signals. Mark "TBD" where no target is known yet.>

## Constraints
<Deadlines, budget, team, compliance, platform limits. "TBD" if unstated.>

## Non-Goals
<What this product will deliberately NOT do in scope. Prevents creep downstream.>

STEP 4: Human approval
CHECKPOINT goals_approved
Show goals.md. > "Do these capture what success means for this product? Approve to continue, or tell me what to change."

UNTIL user explicitly approves
- Apply changes, show updated goals.md, ask again

STEP 5: Hand off

> "Goals approved. Next steps:
>
> - Run `concept-comparable` to study reference apps
> - Run `design-brand-visual` to define visual identity
> - Or continue the orchestrator pipeline"

EMIT [goals] completed run_id=<uuid> artifacts=discovery/goals.md

CHECKLIST

- [ ] \_concept/discovery/goals.md exists with all frontmatter fields
- [ ] every success criterion traces to the brief
- [ ] KPIs are measurable or explicitly "TBD"
- [ ] non-goals are recorded
- [ ] user has explicitly approved

---

## Depth Behavior

| Depth    | Behavior                                                                  |
| -------- | ------------------------------------------------------------------------- |
| `none`   | Skip — rely on the light goals.md from concept-brief                      |
| `light`  | Primary outcome + 2-3 KPIs only                                           |
| `medium` | Full success criteria, KPIs, constraints, non-goals (default)             |
| `max`    | Tiered goals (launch/3mo/12mo), leading vs lagging metrics, risk register |

## Common Mistakes

| Mistake                                  | What to do instead                                            |
| ---------------------------------------- | ------------------------------------------------------------ |
| Vague goals ("be successful")            | Force a measurable signal or a yes/no condition.             |
| Inventing deadlines/budgets              | Mark "TBD" — never fabricate numbers the user didn't imply.  |
| Overwriting concept-brief's goals.md     | Deepen the existing draft; keep what's still true.           |
| Listing features as goals                | Goals are outcomes; features are how. Keep them separate.    |

## Integration

- **Called by:** `concept-orchestrator` (high-level pass on standard/complex) or standalone
- **Requires:** `_concept/discovery/brief.md`
- **Feeds into:** `concept-comparable`, `product-spec-features` (acceptance criteria check against goals), scope-feature

