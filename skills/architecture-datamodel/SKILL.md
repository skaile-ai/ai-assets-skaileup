---
name: architecture-datamodel
description: "Use when the project needs a schema before or while features are specified — derives entities, relationships and enums from whatever exists (glossary, journeys, features, findings, the brief), cites a glossary term for every entity, compares the consequences of the expensive modelling choices with the user, and writes the stack-neutral model with its seed scenarios. Triggers on 'data model', 'design the schema', 'what entities do we need', 'seed data'."
version: "0.3.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brief }
      - { id: journeys }
      - { id: glossary }
      - { id: features }
      - { id: grounding-findings }
      - { id: techstack }
    produces:
      - { id: datamodel, path: "_concept/10_blueprint/datamodel/" }
      - { id: decisions, path: "_concept/10_blueprint/decisions.md" }
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: soft }
      - { path: "_concept/04_journeys/stories.yaml", gate: soft }
      - { path: "_concept/glossary.md", gate: soft }
      - { path: "_concept/05_features", gate: soft, min_entries: 1 }
      - { path: "_concept/02_grounding/findings", gate: soft }
      - { path: "_concept/10_blueprint/techstack.md", gate: soft }
      - { path: "_concept/10_blueprint/architecture.md", gate: soft }
---

# architecture-datamodel

Derives the data model from what exists and writes `model.json`, generated `model.dbml` and `seed.json`. Every entity cites a glossary term; a term the glossary lacks is filed as a proposed term per `tree/glossary.md § Where the words live`, not waited for. It stays stack-neutral — translating into a stack is `build-database`'s step. Every gate is soft: a missing glossary, journeys or features widen the questions, they do not stop the run.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Resolve the facts, settle the vocabulary, ask the gaps** — `tree/10_blueprint/datamodel/README.md § Writing it`, steps 1–3, applying `tree/10_blueprint/datamodel/README.md § Naming` to every entity, field, enum and relation. Derive-or-ask per `tree/README.md § How a skill runs`: what the code already holds comes from `concept-reverse` scoped `datamodel`; a concept with no glossary term is filed as a proposed term per `tree/glossary.md § Where the words live` (a missing glossary starts with these entries) and modelling carries on.
2. **Compare consequences, design the expensive choices twice, approve** — `tree/10_blueprint/datamodel/README.md § Writing it`, steps 4–5. Rejected alternatives and the reason go to `_concept/10_blueprint/decisions.md` as the *options rejected* of one record (`tree/10_blueprint/decisions.md`).
3. **Write `model.json`, render `model.dbml`** — `tree/10_blueprint/datamodel/model.md`, validating `model.json` against `tree/10_blueprint/datamodel/datamodel-model.schema.json` first; every entity carries its `glossary_id`, and `model.dbml` is regenerated from `model.json` on every write.
4. **Write `seed.json` with all four scenarios** — `tree/10_blueprint/datamodel/seed.md`, validated against `tree/10_blueprint/datamodel/datamodel-seed.schema.json`; then steps 7–8 of the README's `## Writing it` (a stack export is `build-database`'s).

**Done when** `model.json`, `model.dbml` (rendered from it) and `seed.json` exist under `_concept/10_blueprint/datamodel/`, the model is approved, every entity's `glossary_id` is a term in `glossary.md`, and `seed.json` carries all four standard scenarios.
