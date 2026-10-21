---
name: concept-onboard
description: "Use at the start of a project to capture what the pipeline needs and the user already knows — technology preferences, an existing brand, the material they are bringing with them. Also when they say 'I have existing docs', 'use these files', or an answer needs someone who is not in the room. Triggers on 'onboard', 'set up the project', 'ingest my seeds'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: scope }
      - { id: grounding-findings }
    produces:
      - { id: onboarding-answers, path: "_concept/02_grounding/onboarding/answers.json" }
      - { id: onboarding-questions, path: "_concept/02_grounding/onboarding/questions.md" }
  prerequisites:
    files:
      - { path: "_concept/01_meta/scope.yaml", gate: soft }
      - { path: "_concept/02_grounding/findings", gate: soft }
    inputs_optional:
      - { id: framework, label: "Preferred framework or language", type: text, hint: "Skip if undecided" }
      - { id: database, label: "Database preference", type: text }
      - { id: ui_library, label: "UI component library", type: text }
      - { id: auth, label: "Authentication approach", type: text }
      - { id: has_brand, label: "Is there an existing brand?", type: boolean }
---

# concept-onboard

Captures what a project arrives with — technology preferences, an existing brand, the seeds
the user dropped in — before any artifact is designed against it. It collects and records and
designs nothing: the vision is `concept-brief`'s, the sizing `skaileup`'s.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Record the answers** — `tree/02_grounding/onboarding/answers.md`. Merge the host's saved step input, read `project_type` from `scope.yaml` (asked in the first batch when absent, per `tree/01_meta/scope.md`), collect technology preferences with their confidence, the brand and the renderer, inventory the seeds, validate against `tree/02_grounding/onboarding/onboarding-answers.schema.json`, stamp `approved:`.
2. **Route questions nobody in the room can answer** — `tree/02_grounding/onboarding/questions.md`.

**Done when** `answers.json` exists and carries `approved:`, every seed under `02_grounding/seeds/` appears in its `seeds` list, and any question for someone outside the room is in `questions.md`.
