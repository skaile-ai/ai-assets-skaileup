---
title: "concept-brief"
description: "Use when starting a new concept and no _concept/discovery/ exists, or when the user says 'I have an app idea', 'new project', 'start from scratch', or wants to redefine an existing brief."
sidebar:
  label: "concept-brief"
---

:::note[Skill manifest]
**Name:** `concept-brief`
**Stage:** alpha · **Version:** 1.0.0
**Tags:** brief, idea, project, vision, start, new, pitch, audience, problem
**Source:** [`skaileup/concept/brief/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/concept/brief/SKILL.md)
:::


# Overview — Project Brief

## Overview

The **overview** skill is the Product Definition agent. It produces the project
brief artifacts in `_concept/discovery/`. It does NOT write features,
data models, screens, brand, or tech stack.

## When to Use

- The user has a new app idea and `_concept/discovery/` does not yet exist
- The user says "I have an app idea", "new project", "start from scratch"
- The user wants to redefine or rewrite an existing project brief
- The orchestrator dispatches this as the first conceptualization step

## When NOT to Use

- `_concept/discovery/brief.md` already exists and is approved — run downstream skills instead
- The user wants to add features to an existing concept — use the **features** skill
- The user wants to research the domain first — use the **research** skill, then come back

## Prerequisites

**REQUIRED BACKGROUND:** Read `contracts/concept_structure.md`,
`contracts/frontmatter.md`, `contracts/iron_laws.md`, and
`contracts/agent_patterns.md` before proceeding.

No hard gates — this is the first step in the pipeline.

## Context Budget

| Action           | Path                                                  | Required |
| ---------------- | ----------------------------------------------------- | -------- |
| Must read        | `contracts/concept_structure.md`      | Yes      |
| Must read        | `contracts/frontmatter.md`            | Yes      |
| Check if present | `_concept/_grounding/overview/user_input.json`        | No       |
| Check if present | `_concept/_grounding/research/domain.md`               | No       |
| Check if present | `_concept/_grounding/research/competitors.md`          | No       |
| Never load       | `experience/`, `blueprint/`, or any downstream folder | —        |

Keep context minimal. This skill writes the foundation — it must not be
influenced by downstream artifacts.

## Standalone Mode

**Gate check:** None — first step.
**On completion:** Present summary, then suggest next steps (research, brand-visual, features).

---

ROLE Product Definition agent — produces `_concept/discovery/` artifacts only.

READS
? \_concept/\_grounding/overview/user_input.json — pre-collected dialog answers
? \_concept/\_grounding/research/domain.md — domain research (if research ran first)
? \_concept/\_grounding/research/competitors.md — competitor research (if research ran first)

WRITES
\_concept/discovery/brief.md — elevator pitch, audience, problem, hero flow
\_concept/discovery/goals.md — success criteria, constraints, deadlines
\_concept/discovery/comparable.md — similar apps with lessons learned

REFERENCES
contracts/concept_structure.md — valid \_concept/ paths and naming rules
contracts/frontmatter.md — required YAML fields
contracts/iron_laws.md — non-negotiable constraints
contracts/agent_patterns.md — communication style, standalone mode

MUST include all required frontmatter fields in brief.md
MUST wait for explicit human approval before handing off
MUST save complexity assessment to \_grounding/overview/user_input.json, not to brief.md frontmatter
NEVER write features, data models, screens, brand, or tech stack
NEVER proceed past the checkpoint without user approval
NEVER block on missing input fields — generate the best brief from whatever is given
NEVER invent comparable products if the user has not mentioned any

EMIT [overview] started run_id=<uuid>

STEP 1: Gather context

- Check \_grounding/overview/user_input.json for pre-collected answers; use them if present
- If raw_description is provided (free-form text field or PLANS.md ## Raw Description section):
  - Extract as many fields as possible from it (app name, pitch, audience, problem, hero flow, comparables, success criteria)
  - Note any fields that could not be inferred — proceed anyway; user will review in Step 3
- If raw_description is NOT provided, ask these questions one by one:
  1. What does the app do? (one sentence)
  2. Who is the primary user? (role, context, skill level)
  3. What is the single most important problem it solves?
  4. What's the most important action a user should be able to do? (the hero flow)
  5. Are there apps that do something similar?
  6. What does success look like? Any constraints or deadlines?
  7. How big is this — a focused tool, a moderate feature set, or a large complex system?
- Wait for answers before proceeding

STEP 2: Write project artifacts

- $ mkdir -p \_concept/discovery

OUTPUT \_concept/discovery/brief.md
---
elevator_pitch: "<one-sentence pitch>"
audience: "<primary user description>"
problem: "<core problem statement>"
hero_flow: "<primary user journey>"
comparable_products: [<list or []>]
last_updated: <YYYY-MM-DD>
---
<Full description in natural language: app vision, who it serves, what
problem it solves, and the primary user journey.>

OUTPUT \_concept/discovery/goals.md
Success criteria, constraints, deadlines, known limitations.

OUTPUT \_concept/discovery/comparable.md
For each comparable app: - What it does well - What to borrow - What to avoid
(If no comparables were mentioned, state that explicitly — do not fabricate.)

STEP 2b: Assess complexity

- Analyse the description for scope signals:
  - small: ≤5 implied features, no custom backend, "simple"/"internal"/"quick"
  - standard: 6–15 implied features, moderate complexity
  - complex: 16+ features OR SaaS/multi-tenant OR significant custom backend, "platform"/"enterprise"
- Save assessment to \_grounding/overview/user_input.json:
  { "complexity": "<small|standard|complex>", "complexity_rationale": "<brief reason>" }
- Tell the user:
  IF small
  > "This looks like a focused app. I'll keep things streamlined — fewer questions, faster progress."
  > IF standard
  > "This is a moderate-sized app. I'll guide you through each step and handle technical details automatically."
  > IF complex
  > "This is a substantial app. I'll be thorough at each step and involve you in key technical decisions."
- User can disagree — update user_input.json if they do

EMIT [overview] checkpoint phase=brief_written files=discovery/brief.md,discovery/goals.md,discovery/comparable.md

STEP 3: Human approval
CHECKPOINT brief_approval
Show the user the content of brief.md. > "Does this capture your vision? Approve to continue, or tell me what to change."

UNTIL user explicitly approves - Apply requested changes to the artifacts - Show updated content and ask for approval again

STEP 4: Hand off

> "Project brief approved. Next steps:
>
> - Run `research` to explore the domain (optional but recommended)
> - Run `brand-visual` to define visual identity
> - Run `features` to spec out what the app does
> - Or run the orchestrator to walk through the full pipeline"

EMIT [overview] completed run_id=<uuid> artifacts=discovery/brief.md,discovery/goals.md,discovery/comparable.md

CHECKLIST

- [ ] \_concept/discovery/brief.md exists with all frontmatter fields
- [ ] \_concept/discovery/goals.md exists
- [ ] \_concept/discovery/comparable.md exists
- [ ] Complexity assessment saved to \_grounding/overview/user_input.json
- [ ] User has explicitly approved the brief

---

## Depth Behavior

| Depth    | Behavior                                                                  |
| -------- | ------------------------------------------------------------------------- |
| `none`   | Skip this skill entirely                                                  |
| `light`  | Produce minimal output — key points only, no elaboration                  |
| `medium` | Standard output — balanced detail and coverage (default)                  |
| `max`    | Comprehensive output — exhaustive analysis, extended examples, edge cases |

## Common Mistakes

| Mistake                                   | Why it happens                                              | What to do instead                                                 |
| ----------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------ |
| Writing features inside brief.md          | Agent tries to be helpful and plan ahead                    | Stop at the brief. Features are a separate skill.                  |
| Skipping user review                      | Agent assumes the brief is good enough                      | Always present the brief and wait for explicit approval.           |
| Loading downstream artifacts              | Agent reads features/ or screens/ "for context"             | This is the first step. Nothing downstream exists yet.             |
| Inventing comparable products             | User didn't mention any, agent fills the gap                | If no comparables: say so in comparable.md. Do not fabricate.      |
| Blocking on missing input                 | Agent refuses to proceed without all fields                 | Generate the best brief from whatever was given; note assumptions. |
| Saving complexity to brief.md frontmatter | Old behavior — complexity_tier was removed from frontmatter | Save to \_grounding/overview/user_input.json only.                 |

## Research Mode

When research is active (`research_depth` ≠ `skip` and `overview` is in `modes.research.triggers`),
domain and competitor research run in parallel. Before writing the brief, check:

- `_concept/_grounding/research/domain.md` — domain findings for the problem statement
- `_concept/_grounding/research/competitors.md` — competitor findings for comparable.md

If research data exists, incorporate it. If it does not, proceed without it — research is optional.

**What this skill benefits from researching:** Market landscape, existing solutions,
target audience demographics and pain points, domain terminology.

## Integration

- **Called by:** `concept-orchestrator` or standalone (first step in the concept pipeline)
- **Feeds into:** all downstream skills via `_concept/discovery/`
- **Feedback loops:** None inbound (root node). Every downstream skill reads from `discovery/`.

