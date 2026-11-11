---
name: architecture-datamodel
description: "Use when the project needs a schema before or while features are specified — derives entities, relationships and enums from whatever exists (glossary, journeys, features, findings, the brief), cites a glossary term for every entity, compares the consequences of the expensive modelling choices with the user, and writes the stack-neutral model with its seed scenarios. Triggers on 'data model', 'design the schema', 'what entities do we need', 'seed data'."
version: "0.6.0"
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
      - { id: proposals, path: "_concept/proposals/<date>-architecture-datamodel-<scope>.yaml" }
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

Derives the data model from what exists and writes it as two YAML files — `model.yaml` and `seed.yaml` — checked by `bunx @skaile/model@1 check` until it prints `ok`; nothing is generated beside them. Every entity cites a glossary term; a term the glossary lacks is written into the run's proposal file (`tree/proposals/README.md § Writing it`), not waited for. It stays stack-neutral — translating into a stack is `build-database`'s step. Every gate is soft: a missing glossary, journeys or features widen the questions, they do not stop the run.

## Route

Read `tree/protocol/running.md` and `tree/protocol/ownership.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Resolve the facts, settle the vocabulary, ask the gaps** — `tree/10_blueprint/datamodel/README.md § Writing it`, steps 1–3, applying `tree/10_blueprint/datamodel/README.md § Naming` to every entity, field, enum and relation. Derive-or-ask per `tree/protocol/running.md § How a skill runs`: what the code already holds comes from `concept-reverse` scoped `datamodel`; a concept with no glossary term is written into the run's proposal file (`tree/proposals/README.md § Writing it`) (`tree/glossary.md § Format`, *Proposal entry*) and modelling carries on.
2. **Compare consequences, design the expensive choices twice, approve** — `tree/10_blueprint/datamodel/README.md § Writing it`, steps 4–5. The choice and its rejected alternatives become one decision record in the run's proposal file (`tree/docs/adr/README.md § Writing it`: target `docs/adr/`, anchor `adr:<slug>`).
3. **Migrate an old model, write `model.yaml`, check it** — `tree/10_blueprint/datamodel/model.md § Writing it`: a project with `model.ts` or `model.json` and no `model.yaml` runs `bunx @skaile/model@1 migrate _concept/10_blueprint/datamodel` first; the format, the `$schema` line and the commands are in `tree/10_blueprint/datamodel/README.md § Format`; every entity models its glossary term, and `bunx @skaile/model@1 check _concept/10_blueprint/datamodel` (`npx` without Bun) runs after every write until it prints `ok`.
4. **Write `seed.yaml` with all four scenarios, check again** — `tree/10_blueprint/datamodel/seed.md § Writing it`: the same check validates every row against the model; then step 8 of the README's `## Writing it` (a stack export is `build-database`'s).

**Done when** `_concept/10_blueprint/datamodel/` holds exactly `model.yaml` and `seed.yaml`, `bunx @skaile/model@1 check` prints `ok` for them, the model is approved, every entity's `glossary` is a term in `glossary.md`, and `seed.yaml` carries all four standard scenarios.
