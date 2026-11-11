---
name: concept-brief
description: "Use when a concept has no _concept/brief.md yet, or the user wants to redefine one. Writes the pitch (with its comparables), the goals — the two root files everything downstream reads — and the first feature ideas in the roster. Triggers on 'I have an app idea', 'new project', 'start from scratch', 'redo the brief'."
version: "0.2.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: scope }
      - { id: expectations }
      - { id: grounding-findings }
    produces:
      - { id: brief, path: "_concept/brief.md" }
      - { id: goals, path: "_concept/goals.md" }
      - { id: featuresets, path: "_concept/05_features/featuresets.md" }
      - { id: decisions, path: "_concept/10_blueprint/decisions.md" }
      - { id: proposals, path: "_concept/proposals/<date>-concept-brief-<scope>.yaml" }
  prerequisites:
    files:
      - { path: "_concept/01_meta/scope.yaml", gate: soft }
      - { path: "_concept/01_meta/expectations.md", gate: soft }
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

The two root files of a concept — `brief.md` (comparables included as a section) and `goals.md` — and the first feature ideas in the roster's `## Ideas`. It writes what the user actually said; pinning the words they settled is `concept-glossary`'s.

## Route

Read `tree/protocol/running.md` and `tree/protocol/ownership.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Resolve the facts and draft the brief** — `tree/brief.md § Drafting the brief`, steps 1–4. Read `02_grounding/`; a missing `brief-seeds.md` for a built project is derived by a scoped `concept-reverse` (`brief`); the user's description, `depth` from `scope.yaml` (asked in the same batch when absent, per `tree/01_meta/scope.md`) and the gaps go in one batch (`tree/protocol/running.md § How a skill runs`). Nothing is approved yet.
2. **Draft the goals** — `tree/goals.md`. Draft them after the pitch exists and before any approval, so the user sees the goals; read `## The result` of `_concept/01_meta/expectations.md` where it exists (`tree/01_meta/expectations.md § Format`), cited, never copied.
3. **List the first ideas** — `tree/05_features/featuresets.md § First ideas`. Candidates from the brief, shown with it, written only after the yes.
4. **Approve them together** — `tree/brief.md § Approving both files`. One yes covers `brief.md`, `goals.md` and the ideas; a declined idea goes under `## Cut` (`tree/05_features/featuresets.md § Ideas`).
5. **Settle the roster proposals** — `tree/05_features/featuresets.md § Writing it` and `tree/proposals/README.md § Writing it`: pending entries targeting `featuresets.md`. A `spec-feature` move is promoted without a batch, since the spec's approval covers it; an idea from another skill goes into one batch with a recommendation each.

**Done when** `brief.md` (with its `## Comparables` section) and `goals.md` are on disk, the first ideas are rows of `## Ideas` in `featuresets.md`, no pending proposal entry targets it, and the user has said yes to all of them, which `approved:` in the brief and goals frontmatter records.
