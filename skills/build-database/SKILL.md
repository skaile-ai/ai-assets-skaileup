---
name: build-database
description: "Use when the data model is settled and the app needs a real database — translates the model into the stack's schema, migrates it, and generates one runnable seed script per scenario. Triggers on 'migrate', 'generate the schema', 'seed the database', 'set up the data layer'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: datamodel }
      - { id: techstack }
    produces: []
  prerequisites:
    files:
      # Hard: `model.json` is the machine-read model this skill translates; it cannot be derived from
      # `model.dbml` (a generated render) or asked for field by field, and `architecture-datamodel` writes it.
      - { path: "_concept/10_blueprint/datamodel/model.json", gate: hard }
      - { path: "_concept/10_blueprint/techstack.md", gate: soft }
---

# build-database

One pass over `_concept/10_blueprint/datamodel/`: the schema first, then the seed scripts that fill it — one pass because both share the same read of the model and the same dependency order. Read `tree/README.md` once per session.

Almost all of it is stack-neutral. The rest lives in two sections of the chosen template — `## Migration / ORM` for the schema file and the migrate commands, `## Seed` for the seed layout and run command — which this skill cites rather than restates. Types, conventions and validation are `tree/10_blueprint/datamodel/README.md § Materialising the database`; the scenarios and their rules are `tree/10_blueprint/datamodel/seed.md`; the model's own format is `tree/10_blueprint/datamodel/model.md`.

Without `techstack.md` the target is derived or asked (step 2), so the only hard input is the model.

## Steps

1. **Cross-check the model's two halves.** `model.json` is present (the gate); `model.dbml`, when present, is authoritative for structure and `model.json` for relationship and enum metadata. Name every disagreement to the user rather than preferring one — a divergence is somebody's hand edit, and the wrong pick propagates into schema and seeds at once.
2. **Resolve the target from the template, deriving or asking when the stack is unrecorded** (`tree/README.md § How a skill runs`, rule 1). `_concept/10_blueprint/techstack.md` names `tech_stack_skill`; without it read `_concept/02_grounding/findings/stack.md` (`concept-reverse` scoped `stack` fills it from the code), then ask for the template in one batch with whatever else is open. That template's `## Migration / ORM` gives the schema file, its location and the migrate commands, and its `seed_format` atom (`prisma`, `drizzle` or `sql`) selects the layout described in its `## Seed`. Where a `prog-expert-<orm>` skill is installed, consult it for idiomatic patterns; nothing here waits on one.
3. **Translate every semantic type** through the translation table in `tree/10_blueprint/datamodel/README.md § Materialising the database`; a semantic type left in the output fails at the migration tool.
4. **Apply the conventions the model leaves out**, from the same section: expand `standard_fields`, snake_case the columns, take `on_delete` from `model.json` (SET NULL where unset), give every `m2m` its junction table with the two foreign keys, and generate `o2m` from its `m2o`.
5. **Validate the schema six ways, then migrate** — the six checks in the same section. Run the migrate command, confirming first when the target is anything but a local development database.
6. **Build the insert order before writing a seed.** Walk the relationships into a dependency graph: entities with no foreign keys first, then each entity after everything it points at. The reverse is the cleanup order; deleting parents first leaves dangling references that make a re-seed fail on its second run.
7. **Generate the seeds at the paths `## Seed` names.** One file per scenario in `_concept/10_blueprint/datamodel/seed.json` (`tree/10_blueprint/datamodel/seed.md`) — `empty`, `single_user`, `populated`, `edge_cases`, and any the model added — plus one entry point that takes the scenario name and defaults to `populated`. The entry point clears in reverse dependency order, then inserts. A file per scenario keeps scenarios switchable mid-session.
8. **Validate the seeds six ways.**
   - Every id from `seed.json` is preserved, since the relations resolve through it.
   - Every foreign key value exists as a primary key.
   - Every enum value matches `model.json`.
   - Required fields are populated in every scenario.
   - `empty` actively clears all data rather than inserting nothing.
   - `edge_cases` reaches the database intact — special characters, hundred-character strings and null optionals are its point, and a column that silently truncates them is the finding.
9. **Run each scenario end to end, then report**: the target, the counts of tables, relationships and enums, the scenarios and the files behind them, and the command that switches between them.

**Done when** the migration has applied, every scenario runs clean from the entry point, and switching scenarios leaves behind no rows from the one before it.
