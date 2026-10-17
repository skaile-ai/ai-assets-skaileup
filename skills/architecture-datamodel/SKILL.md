---
name: architecture-datamodel
description: "Use when the glossary exists and the project needs a schema before any feature is specified — derives entities, relationships and enums from the journeys (or the brief where there are none), settles every name against the glossary, and writes the stack-neutral model with its seed scenarios. Triggers on 'data model', 'design the schema', 'what entities do we need', 'seed data'."
version: "0.2.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brief }
      - { id: journeys }
      - { id: glossary }
      - { id: techstack }
    produces:
      - { id: datamodel, path: "_concept/10_blueprint/datamodel/" }
  prerequisites:
    files:
      - { path: "_concept/04_journeys/stories.yaml", gate: soft }
      - { path: "_concept/glossary.md", gate: hard }
      - { path: "_concept/10_blueprint/techstack.md", gate: soft }
      - { path: "_concept/10_blueprint/architecture.md", gate: soft }
---

# architecture-datamodel

Derives the data model from the journeys and the glossary and writes `model.dbml`, `model.json` and `seed.json`. It runs before any feature exists and stays stack-neutral; translating into a stack is `build-database`'s step.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Derive, name and approve the model** — `tree/10_blueprint/datamodel/README.md § Writing it`, steps 1–4, applying `tree/10_blueprint/datamodel/README.md § Naming` to every entity, field, enum and relation.
2. **Write `model.dbml` and `model.json`** — `tree/10_blueprint/datamodel/model.md`, validating `model.json` against `tree/10_blueprint/datamodel/datamodel-model.schema.json` first; entity `id`s are the PascalCase model names.
3. **Write `seed.json` with all four scenarios** — `tree/10_blueprint/datamodel/seed.md`, validated against `tree/10_blueprint/datamodel/datamodel-seed.schema.json`; then step 7 of the README's `## Writing it` (a stack export is `build-database`'s).

**Done when** `model.dbml`, `model.json` and `seed.json` exist under `_concept/10_blueprint/datamodel/`, the model is approved, every model name and enum vocabulary is a term in `glossary.md`, and `seed.json` carries all four standard scenarios.
