---
name: experience-journeys
description: "Use when the brief is approved and nothing has mapped what users actually do yet. Defines the personas and the staged story map that features are derived from. Triggers on 'map the journeys', 'user stories', 'what do users do', 'story map'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brief }
      - { id: goals }
      - { id: research-audiences }
      - { id: glossary }
    produces:
      - { id: journeys, path: "_concept/04_journeys/stories.yaml" }
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: hard }
      - { path: "_concept/goals.md", gate: soft }
      - { path: "_concept/02_grounding/research/audiences.md", gate: soft }
      - { path: "_concept/glossary.md", gate: soft }
---

# experience-journeys

Writes `04_journeys/stories.yaml`: who the users are and the staged map of what they are trying to do. It maps journeys and stops — no feature specs, no screens.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Map the journeys and write the story map** — `tree/04_journeys/stories.md` (`## Writing it` for the steps, `### EARS template` and `### Criterion ids` for the criteria, `### Registration` for the `candidate_*` hints `spec-featuresets` consumes). Get the persona list and the hero journey approved before mapping the rest. Validate the file against `tree/04_journeys/journeys.schema.json` before writing.

**Done when** `stories.yaml` exists with exactly one hero journey, every story has an `id` and at least one EARS criterion carrying its `AC-<story-id>-<nn>` id plus its candidate hints, and the user has approved the map.
