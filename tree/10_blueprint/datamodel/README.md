---
path: _concept/10_blueprint/datamodel/
summary: stack-neutral data model, naming rules and how it becomes a database
owner: [architecture-datamodel]
may_propose: [spec-feature, experience-screen, mockup-storybook, mockup-feedback]
---

# _concept/10_blueprint/datamodel/

The project's data model, derived from the glossary, the journeys and whatever else exists, and kept as two authored YAML files: `model.yaml` (entities, fields, enums, relations and proposed entries) and `seed.yaml` (realistic data as named scenarios, every row checked against the model). Nothing generated lives beside them. It is the vocabulary that feature specs, behaviors and screens are written against: downstream skills read entity names from `model.yaml` (through `@skaile/model`, `## Format`) and never coin their own, and each feature spec lists the models it uses in its own `data_entities[]` (the model holds no list of features). Every entity cites the glossary term it models, so the glossary stays the one place a concept is defined and its object axes (navigation, lifecycle, origin, operations) live there, not here. The model is stack-neutral — types are semantic, never SQL or Prisma — because translating it here would freeze a schema before the stack's migration tool has seen it. Node files: `tree/10_blueprint/datamodel/model.md` and `tree/10_blueprint/datamodel/seed.md`.

## Format

`architecture-datamodel` owns both files; the directory holds exactly `model.yaml` and `seed.yaml`. A stack-specific schema file is `build-database`'s alone: a translation of the model for one migration tool, written where the chosen template's `## Migration / ORM` section says, and the canonical files are never edited to match it. A feature spec or a mockup that needs an entity or field the model lacks adds it to `model.yaml` with a `proposed` key (`tree/README.md § Ownership`, `tree/10_blueprint/datamodel/model.md § Format`) and the owner promotes or rejects it.

The npm package `@skaile/model` owns the format of both files (ADR 0030) and is the one tool that reads them:

- **Schemas.** `model.schema.json` and `seed.schema.json` ship in the package; neither this collection nor the project holds a copy. The first line of each file binds the published copy, so an editor with YAML-schema support (VS Code with Red Hat YAML, JetBrains) completes keys, shows their descriptions and flags mistakes while the file is typed:
  ```yaml
  # yaml-language-server: $schema=https://cdn.jsdelivr.net/npm/@skaile/model@1/schema/model.schema.json
  ```
  `seed.yaml` starts with the same line ending in `seed.schema.json`.
- **Check.** `bunx @skaile/model check _concept/10_blueprint/datamodel` (`npx @skaile/model check …` without Bun; Node 20 or later) validates both files: the schema, then everything a schema cannot say (`tree/10_blueprint/datamodel/model.md § Checks`, `tree/10_blueprint/datamodel/seed.md § Checks`). It prints `ok` with counts, or one `file:path: message (line n)` per issue and exits 1. Every write to either file ends with it.
- **Read.** `bunx @skaile/model json _concept/10_blueprint/datamodel` prints the normalized `{ "model": …, "seed": … }` — entities with their fields, the derived `relationships[]`, the shared `enums[]`, the scenarios — and exits 1 with the issues when the files do not check. Readers that need data (`build-database`, the tests, Python scripts) take it from there; TypeScript code imports `loadModel` and `loadSeed` from `@skaile/model`. `bunx @skaile/model types --out <file>` writes the row types (`TaskRow`, one union type per shared enum); the mockup package gets them from the package's Vite plugin (`tree/09_mockup/storybook/README.md`).
- **Migrate.** A project from before ADR 0030 holds `model.ts` and `seed.ts`, the JSON and DBML generated from them and four tool files. `bunx @skaile/model migrate _concept/10_blueprint/datamodel` converts the generated JSON into the two YAML files, checks them and deletes the nine legacy files; it changes nothing when `model.yaml` already exists or the JSON is older than its TypeScript source. Canvas layout (the `editor` block, entity positions) is not carried over: it is the host's state, not the model's.

## Naming

Entity names come from the glossary (`tree/glossary.md § Where the words live`): where the glossary has a term the model uses it, and a word on a term's `_Avoid_` list is renamed to the term. Output conventions (camelCase fields in Prisma or PostXL) are applied by the stack translator, never in the semantic layer.

**Entities**
- The entity id, its key under `entities:` in `model.yaml`, is the model name: PascalCase singular (`User`, `Task`, `ProjectMember`); no two entities share an id.
- Every entity models a glossary term, named by `glossary`: the kebab-case slug of the term (`Order line` → `order-line`), while the entity id is its PascalCase form (`OrderLine`). `glossary` defaults to the kebab-case of the id, so it is written only where the term's slug differs from that. An entity with no term in the glossary gets a `proposed` term first (`## Writing it`, step 2), and its `glossary` is that term's id.
- Every entity has the standard fields `id`, `created_at` and `updated_at` (`standard_fields`, the default); `id` is a `uuid` primary key, the timestamps are `datetime`. They are never declared under `fields:`.

**Fields**
- Names are `lowercase_snake_case` (`display_name`, `assigned_to_id`).
- The type is a semantic type (`tree/10_blueprint/datamodel/model.md`), never a backend type.
- An optional field uses `required: false`, never a `?` suffix.

**Enums**
- Values are PascalCase (`Draft`, `InProgress`, `Done`).
- An inline enum is `{ type: enum, values: { Draft: description, InProgress: description } }` on the field and auto-names as `{entity_name}_{field_name}` with the entity's snake_case form (`task_status`, `user_role`); an enum reused across models is declared once under the top-level `enums:` and referenced by `{ type: enum, enum: <id> }` (`tree/10_blueprint/datamodel/model.md`).
- Every shared enum is referenced by at least one field; shared enum ids are `lowercase_snake_case` and match their purpose.

**Relations**
- A many-to-one field name ends in `_id` (`owner_id`, `project_id`) and is `{ type: m2o, to: User }`, whose target is the referenced entity `User`.
- Inverse relations are derived by the loader and generated by the translator, never declared.
- A many-to-many relation has an explicit junction entity.

**Seed data**
- Entity keys are the snake_case form of the model's entity id, singular (`Task` → `task`, `ProjectMember` → `project_member`); field names match the model, enum values are PascalCase, relation fields end in `_id`.

## Writing it

1. **Read what exists, in any order.** The glossary (`tree/glossary.md § Where the words live`: the words already pinned) with `_concept/glossary.md` (each term's kind, and each object's axes), `_concept/04_journeys/stories.yaml` (actors, stages and EARS criteria — event criteria become transitions, state criteria become guards, and what a journey creates, changes or looks up is an entity or a field), the feature specs and their `data_entities[]`, `_concept/02_grounding/findings/datamodel.md`, `_concept/brief.md`, and `techstack.md` and `architecture.md` when they exist (translation hints; an integration's entities). Each is read when it exists and its absence only widens step 3: project types that grow no journeys (`api-service`, `cli-tool`, `data-pipeline`, `library`) take the brief's hero flow and problem instead. Derive what the sources settle, run `concept-reverse` scoped where the code holds the schema, and ask only what neither settles (`tree/README.md § How a skill runs`).
2. **Settle the vocabulary.** List every candidate entity and enum vocabulary the sources imply — each journey's `candidate_entities` is the starting list — plus entities with no journey behind them (sessions, audit logs, job records), and check each against the glossary per `## Naming`. A concept with no term gets a `proposed` term, filed per `tree/glossary.md § Where the words live` with its `kind` (`tree/README.md § Ownership`), and modelling carries on against it; `concept-glossary` confirms or renames it later, and a rename is one `glossary` edit in `model.yaml`.
3. **Ask what the sources left ambiguous** (`tree/README.md § How a skill runs`, one decision batch per message): what each journey stores, how things connect ("a user has many tasks"), which roles may see or change what. The roles answer feeds the seed's `permissions` scenario and the fields those rules evaluate on. The grants themselves are the feature specs' `## Permissions` tables; this step records no grants, and on a re-run reads those tables where they exist and seeds the roles and grants as written there.
4. **Compare consequences before committing a modelling choice** (`tree/README.md § How a skill runs`, rule 5): a table per choice, one row per option, with these columns, in the user's words:

   | option | user-visible | data / permission | affected artifacts | reversibility |
   |---|---|---|---|---|

   For an expensive choice — inheritance versus composition, the tenant model, soft versus hard delete across the whole model — **design it twice**: sketch three genuinely different models (in parallel, one subagent per sketch where the harness has subagents), compare them on the five columns, and let the user pick. The losers go to `_concept/10_blueprint/decisions.md` as the *options rejected* of one record (`tree/10_blueprint/decisions.md`).
5. **Approve in plain language** — what the app keeps track of and how those things relate, in the user's words, counts underneath. Write nothing before the user says yes; a model features, screens and seeds are about to name is cheapest to change while it is still a paragraph.
6. **Write `model.yaml`, then run the check** per `tree/10_blueprint/datamodel/model.md § Writing it` (`bunx @skaile/model check`, `## Format`); apply `## Naming`. An `m2m` gets an explicit junction model; a raw SQL type here survives into a migration that will not apply.
7. **Write `seed.yaml`, then run the check again** per `tree/10_blueprint/datamodel/seed.md § Writing it`, with all four standard scenarios plus `permissions` when the journeys name distinct roles.
8. **A stack export is `build-database`'s.** When the user asks for a stack-specific schema, `build-database` writes it against these files rather than replacing them.

## Materialising the database

`build-database` turns the canonical model into the stack's schema, then the seeds into runnable scripts. Which stack-specific file results depends on the stack in `techstack.md`:

| stack signal | stack-specific file |
|---|---|
| generic / unknown | none — `model.yaml` is the schema |
| Prisma | `schema.prisma` |
| PostXL / NestJS | `postxl-schema.json` |

The file lives where the chosen template's `## Migration / ORM` section says; its `## Seed` section gives the seed layout and run command, selected by the `seed_format` atom (`prisma`, `drizzle` or `sql`).

**Semantic type translation**

| Semantic | Prisma / PostXL | Supabase | Raw SQL | Directus |
|---|---|---|---|---|
| `string` | `String` | `text` | `VARCHAR(255)` | `string` |
| `text` | `String` | `text` | `TEXT` | `text` |
| `richtext` | `String` | `text` | `TEXT` | `text` (WYSIWYG) |
| `integer` | `Int` | `int4` | `INTEGER` | `integer` |
| `float` | `Float` | `float8` | `DOUBLE PRECISION` | `float` |
| `decimal` | `Decimal` | `numeric` | `NUMERIC` | `float` |
| `boolean` | `Boolean` | `bool` | `BOOLEAN` | `boolean` |
| `date` | `DateTime` | `date` | `DATE` | `date` |
| `datetime` | `DateTime` | `timestamptz` | `TIMESTAMPTZ` | `timestamp` |
| `enum` | `enum` | `text` + CHECK | `VARCHAR` + CHECK | `string` (dropdown) |
| `json` | `Json` | `jsonb` | `JSONB` | `json` |
| `uuid` | `String @id @default(uuid())` | `uuid` | `UUID` | `uuid` |
| `password` | `String` | `text` | `TEXT` | `hash` |
| `slug` / `string` unique | `String` + `@unique` | `text` | `VARCHAR(255)` | `string` |
| `email` / `string` | `String` | `text` | `VARCHAR(255)` | `string` |
| `url` / `string` | `String` | `text` | `TEXT` | `string` |
| `image` | `String` (URL) or `imageId → File` | storage ref | `TEXT` | M2O → directus_files |
| `file` | `String` (URL) or `fileId → File` | storage ref | `TEXT` | M2O → directus_files |
| optional (`required: false`) | `Type?` suffix | `NULL` | nullable column | — |
| `m2o` | field ending `Id`, type = model name | FK | FOREIGN KEY | M2O |
| `o2m` | auto-generated inverse | — | — | O2M |
| `m2m` | explicit junction model | junction table | junction table | M2M |

**Conventions the model deliberately leaves out**
- `standard_fields` expands to an auto-generating UUID primary key plus `created_at`, and `updated_at` wherever the model declares it.
- Columns are snake_case.
- `on_delete` comes from the relationship in the model and defaults to SET NULL where unset, which orphans a row rather than deleting one nobody asked to delete.
- Every `m2m` gets a junction table with the two foreign keys; `o2m` is generated from its `m2o`, never written by hand.

**Schema validation** — six checks before migrating: every entity in the model has a table; every relationship is a foreign key or a junction table; every enum is defined; no semantic type survives in the output; primary keys auto-generate; on-delete behaviour matches the model.

## Checks

- `model.yaml` and `seed.yaml` are the only files in `_concept/10_blueprint/datamodel/`, `bunx @skaile/model check` prints `ok` for them, and the model is approved.
- Every entity's `glossary` (stated or defaulted) is a term in `_concept/glossary.md` (a `proposed` term counts), and every enum vocabulary is a term there.
- `seed.yaml` carries all four standard scenarios.
- The mechanical rules in `## Naming` hold; a violation is a finding in the audit report.
