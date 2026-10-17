---
name: concept-brief
description: "Use when a concept has no _concept/brief.md yet, or the user wants to redefine one. Writes the pitch (with its comparables) and the goals — the two root files everything downstream reads. Triggers on 'I have an app idea', 'new project', 'start from scratch', 'redo the brief'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: scope }
      - { id: grounding-findings }
    produces:
      - { id: brief, path: "_concept/brief.md" }
      - { id: goals, path: "_concept/goals.md" }
  prerequisites:
    files:
      - { path: "_concept/01_meta/scope.yaml", gate: soft }
      - { path: "_concept/02_grounding/findings", gate: soft }
    inputs_optional:
      - { id: raw_description, label: "Describe your idea", type: textarea, hint: "Free-form — name, audience, problem and hero flow can all be mined from this" }
      - { id: elevator_pitch, label: "What does the app do?", type: text, hint: "One sentence: who it is for, what it does" }
      - { id: target_audience, label: "Who is the primary user?", type: text, hint: "Role, context, skill level" }
      - { id: problem_statement, label: "What problem does it solve?", type: text, hint: "The single most important one" }
      - { id: hero_flow, label: "Most important user action", type: text, hint: "The one thing every user must be able to do" }
      - { id: comparable_products, label: "Similar apps", type: text }
      - { id: success_criteria, label: "What does success look like?", type: text, hint: "Goals, constraints, deadlines" }
---

# concept-brief

The two root files of a concept — `brief.md` (comparables included as a section) and `goals.md` — and nothing else. It writes what the user actually said and hands off to `concept-glossary`.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Draft the brief and its comparables** — `tree/brief.md § Drafting the brief`. Covers reading `02_grounding/`, seeding from `brief-seeds.md`, the pitch and `## Comparables`; nothing is approved yet.
2. **Draft the goals** — `tree/goals.md`. Run it after the pitch exists and before any approval, so the user sees the goals.
3. **Approve both and hand off** — `tree/brief.md § Approving both files`. One yes covers `brief.md` and `goals.md`.

**Done when** `brief.md` (with its `## Comparables` section) and `goals.md` are on disk and the user has said yes to both, which `approved:` in their frontmatter records.
