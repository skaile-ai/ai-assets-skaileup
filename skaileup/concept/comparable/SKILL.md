---
name: concept-comparable
description: "Use on standard-app / complex-app concepts after brief and goals exist, when reference apps deserve their own focused pass beyond the light version concept-brief writes. Studies 3-6 comparable products, captures what to borrow and what to avoid, and locates the positioning gap, then writes (or deepens) _concept/discovery/comparable.md."
metadata:
  version: '1.0.0'
  stage: alpha
  tags:
    - 'comparable'
    - 'competitors'
    - 'reference-apps'
    - 'positioning'
    - 'borrow-avoid'
    - 'differentiation'
  source: 'PHASE3'
  parameters:
    depth:
      type: enum
      values: [none, light, medium, max]
      default: medium
  artifacts:
    requires:
      - id: brief
        gate: hard
    produces:
      - id: comparable
        description: 'Reference apps with borrow/avoid lessons and the positioning gap'
    consumes:
      - id: goals
        gate: soft
      - id: research-competitors
        gate: soft
  prerequisites:
    files:
      - path: '_concept/discovery/brief.md'
        gate: hard
        description: 'Comparables are judged relative to the brief vision and audience'
    reads:
      - path: '_concept/discovery/goals.md'
        description: 'Differentiation is framed against the success criteria'
      - path: '_concept/discovery/comparable.md'
        description: 'Light comparable version concept-brief may have written — deepen rather than overwrite'
      - path: '_concept/_grounding/research/competitors.md'
        description: 'Deep competitor research (if grounding-research ran) — summarize into discovery-level lessons'
    produces:
      - path: '_concept/discovery/comparable.md'
        description: 'Reference apps, what to borrow/avoid, positioning gap'
---

# Comparable — Reference Apps & Positioning

## Overview

The **comparable** skill is the focused reference-apps pass for larger concepts.
`concept-brief` lists comparables lightly; on standard-app / complex-app this
skill turns them into actionable lessons — what to borrow, what to avoid — and
names the positioning gap this product fills. It writes only
`_concept/discovery/comparable.md`. It is the *discovery-level* summary, distinct
from the deep `_grounding/research/competitors.md` that `concept-grounding-research`
produces; if that research exists, this skill distills it rather than redoing it.

## When to Use

- Brief (and ideally goals) approved, tier is standard-app or complex-app
- The user wants to learn from existing apps before designing features
- The orchestrator dispatches this after `concept-goals` in the high-level pass

## When NOT to Use

- mvp / simple-app — the light `comparable.md` from `concept-brief` is enough
- No `_concept/discovery/brief.md` yet — run `concept-brief` first
- The user wants exhaustive market research — run `concept-grounding-research` (writes `_grounding/research/competitors.md`)

## Prerequisites

**REQUIRED BACKGROUND:** Read `contracts/concept_structure.md`,
`contracts/frontmatter.md`, and `contracts/agent_patterns.md` before proceeding.

**Hard gate:** `_concept/discovery/brief.md` must exist.

## Context Budget

| Action           | Path                                              | Required |
| ---------------- | ------------------------------------------------- | -------- |
| Must read        | `_concept/discovery/brief.md`                     | Yes      |
| Check if present | `_concept/discovery/goals.md`                     | No (framing)         |
| Check if present | `_concept/discovery/comparable.md`                | No (deepen existing) |
| Check if present | `_concept/_grounding/research/competitors.md`     | No (distill if present) |
| Never load       | `experience/`, `blueprint/`, downstream folders   | —        |

## Standalone Mode

**Gate check:** `_concept/discovery/brief.md` must exist.
**On completion:** Present the comparable summary, suggest `design-brand-visual` or `experience-journeys` next.

---

ROLE Comparable agent — distills reference apps into borrow/avoid lessons and a positioning gap in `_concept/discovery/comparable.md`.

READS
\_concept/discovery/brief.md — vision, audience, problem, hero flow
? \_concept/discovery/goals.md — success criteria (frames differentiation)
? \_concept/discovery/comparable.md — light comparable version to deepen
? \_concept/\_grounding/research/competitors.md — deep competitor research to distill (if it ran)

WRITES
\_concept/discovery/comparable.md — reference apps, borrow/avoid, positioning gap

REFERENCES
contracts/concept_structure.md — valid \_concept/ paths
contracts/frontmatter.md — required YAML fields
contracts/agent_patterns.md — communication style, standalone mode

MUST cover 3-6 comparables — direct, indirect, and at least one adjacent reference
MUST give each comparable a concrete borrow and a concrete avoid
MUST state the positioning gap — where this product differs and why that matters to the audience
MUST distill, not duplicate, \_grounding/research/competitors.md when it exists
MUST deepen an existing comparable.md rather than discarding it
MUST wait for explicit human approval before handing off
NEVER fabricate apps, features, or pricing the user/research did not provide — mark unknowns "unverified"

EMIT [comparable] started run_id=<uuid>

STEP 1: Gather context

- Read \_concept/discovery/brief.md for audience and problem
- IF \_concept/discovery/goals.md exists, read it — differentiation is framed against the goals
- IF \_concept/discovery/comparable.md exists, read it — deepen its content
- IF \_concept/\_grounding/research/competitors.md exists, read it — distill into discovery-level lessons (do not re-research)

STEP 2: Identify comparables (skip if research already lists them)

- Ask the user for apps they admire or compete with, if not already known
- Aim for 3-6: at least one direct competitor, one indirect, one adjacent (different domain, borrowable pattern)
- For each, establish: what it does well, where it falls short, who it serves

EMIT [comparable] checkpoint phase=comparables_gathered count=<N>

STEP 3: Write comparable.md

- $ mkdir -p \_concept/discovery

OUTPUT \_concept/discovery/comparable.md
---
comparables_count: <N>
positioning_gap: "<one-sentence differentiation>"
last_updated: <YYYY-MM-DD>
---
## Reference Apps
<For each app:>
### <name> — <direct | indirect | adjacent>
- **Does well:** <strength to borrow>
- **Borrow:** <the specific pattern/decision worth adopting>
- **Avoid:** <the specific mistake or friction to not repeat>
- **Serves:** <their audience vs ours>

## Positioning Gap
<Where this product sits that the comparables don't. Tie to the audience and goals.
Mark any unverified claims "unverified".>

STEP 4: Human approval
CHECKPOINT comparable_approved
Show comparable.md. > "Do these reference points and the positioning gap feel right? Approve to continue, or tell me what to change."

UNTIL user explicitly approves
- Apply changes, show updated comparable.md, ask again

STEP 5: Hand off

> "Comparables approved. Next steps:
>
> - Run `design-brand-visual` to define visual identity
> - Run `experience-journeys` to map the core flows
> - Or continue the orchestrator pipeline"

EMIT [comparable] completed run_id=<uuid> artifacts=discovery/comparable.md

CHECKLIST

- [ ] \_concept/discovery/comparable.md exists with all frontmatter fields
- [ ] 3-6 comparables, each with a borrow and an avoid
- [ ] positioning gap stated and tied to audience/goals
- [ ] \_grounding/research/competitors.md distilled (if it existed), not duplicated
- [ ] user has explicitly approved

---

## Depth Behavior

| Depth    | Behavior                                                                  |
| -------- | ------------------------------------------------------------------------- |
| `none`   | Skip — rely on the light comparable.md from concept-brief                 |
| `light`  | 3 comparables, borrow/avoid one-liners, positioning gap                   |
| `medium` | 3-6 comparables with full borrow/avoid + positioning gap (default)        |
| `max`    | Feature-by-feature matrix, pricing/positioning map, adjacent-domain scan  |

## Common Mistakes

| Mistake                                   | What to do instead                                              |
| ----------------------------------------- | -------------------------------------------------------------- |
| Re-running deep research                  | If `_grounding/research/competitors.md` exists, distill it.    |
| Only direct competitors                   | Include an adjacent reference — best patterns cross domains.   |
| Borrow/avoid too vague                    | Name the specific pattern or mistake, not "good UX".           |
| Fabricating pricing/features              | Mark unverified claims "unverified".                           |
| Overwriting concept-brief's comparable.md | Deepen the existing draft.                                     |

## Integration

- **Called by:** `concept-orchestrator` (high-level pass on standard/complex) or standalone
- **Requires:** `_concept/discovery/brief.md`
- **Feeds into:** `design-brand-visual`, `design-inspiration`, `experience-journeys`, `product-spec-features`
