---
path: [_concept/10_blueprint/datamodel/skaile-model.ts, _concept/10_blueprint/datamodel/gen.ts, _concept/10_blueprint/datamodel/datamodel-model.schema.json, _concept/10_blueprint/datamodel/datamodel-seed.schema.json]
summary: tool files copied into the project — the model DSL, its generator, two schemas
owner: [architecture-datamodel]
may_propose: []
---

# _concept/10_blueprint/datamodel/skaile-model.ts, gen.ts, datamodel-model.schema.json, datamodel-seed.schema.json

The four tool files that let `model.ts` and `seed.ts` be TypeScript and still produce `model.json`, `model.dbml` and `seed.json`: `skaile-model.ts` is the DSL (`entity`, `f.*`, `sharedEnum`, `defineModel`, `scenarios`, the types `Infer`, `Model`, `Seed`), `gen.ts` runs the two authored files and writes the generated ones, and the two schemas are copies of `tree/10_blueprint/datamodel/datamodel-model.schema.json` and `tree/10_blueprint/datamodel/datamodel-seed.schema.json` that `gen.ts` validates against. They live in the project so the mockup package imports the DSL relatively and so `gen.ts` runs there without the collection installed. They are tool files, not artifacts of the project's own: nobody edits them by hand, and `architecture-datamodel` replaces them with the skill's current copy.

## Format

- Source: `skills/architecture-datamodel/references/dsl/skaile-model.ts` and `skills/architecture-datamodel/references/dsl/gen.ts`, with `skills/architecture-datamodel/references/dsl/README.md` explaining what is authored and what is generated. Both start with the line `// skaile-model <version>`; equal versions mean equal behaviour.
- `skaile-model.ts` has no dependency and uses no Node API, so a browser bundle (the mockup package) can import it; `gen.ts` uses Node and the `tsx` runner, which `npx` fetches on first use.
- `gen.ts` ships its own minimal JSON Schema validator for the keywords the two schemas use and stops with a message when a schema uses another, so a schema change needs a matching `gen.ts` change.
- The schemas are byte copies; the collection's `tree/10_blueprint/datamodel/` copies stay the authoritative ones.

## Writing it

Copy per `tree/10_blueprint/datamodel/model.md § Writing it`, step 1: on the first write of the model, and again whenever the first-line version of the project's `skaile-model.ts` differs from the skill's. A change to the project's copy is overwritten by the next copy, so a wish for a different DSL goes to the collection's `skills/architecture-datamodel/references/dsl/`.

## Checks

- The project's `skaile-model.ts` and `gen.ts` carry the same version line as the skill's.
- The two schema copies equal the files in `tree/10_blueprint/datamodel/`.
