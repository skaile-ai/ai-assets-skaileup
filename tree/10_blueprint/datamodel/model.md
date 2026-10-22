---
path: [_concept/10_blueprint/datamodel/model.ts, _concept/10_blueprint/datamodel/model.json, _concept/10_blueprint/datamodel/model.dbml]
summary: model.ts is authored; model.json and model.dbml are generated from it
owner: [architecture-datamodel]
may_propose: [spec-feature, experience-screen, mockup-storybook, mockup-feedback]
---

# _concept/10_blueprint/datamodel/model.ts, model.json, model.dbml

The canonical, stack-neutral data model. `model.ts` is the one authored file: TypeScript written with the DSL of `tree/10_blueprint/datamodel/skaile-model.md`, so the mockup package and the seed import its types and a row that no longer fits the model fails `tsc`. `gen.ts` runs it and writes `model.json`, the interchange file every other reader takes (`build-database`, the E2E tests, the host's canvas, which owns only its `editor` key), and `model.dbml`, rendered to read. Nobody edits the two generated files, because the next run overwrites them. All three carry semantic types — intent, not output format — and `build-database` maps them to a concrete stack. Cross-references from other artifacts (`data_entities[]`, `story_refs`) target the entity `id`, which is its export name in `model.ts`; stack-specific files are derived and never referenced. Names follow `tree/10_blueprint/datamodel/README.md § Naming`.

## Format

`model.ts` has exactly this layout, because `mockup-feedback` appends to it as plain text:

```ts
import { defineModel, entity, f, sharedEnum } from './skaile-model'

export const Priority = sharedEnum({ Low: 'Can wait', High: 'Needs attention today' })

export const User = entity({
  glossary: 'user',
  display: 'User',
  label_field: 'display_name',
  fields: {
    display_name: f.string({ max_length: 80 }),
    email: f.email({ unique: true }),
  },
})

export const Task = entity({
  glossary: 'task',
  display: 'Task',
  label_field: 'title',
  fields: {
    title: f.string({ max_length: 120 }),
    status: f.enum({ Draft: 'Initial state', Published: 'Live and visible' }),
    priority: f.enumRef(Priority),
    due_date: f.date({ required: false }),
    owner_id: f.m2o(() => User, { on_delete: 'cascade' }),
    estimate: f.decimal({ required: false, proposed: { by: 'mockup-storybook', on: '2026-07-01', source: 'TaskEditor needs an effort estimate' } }),
  },
})

export const model = defineModel({
  entities: {
    User,
    Task,
  },
  enums: {
    priority: Priority,
  },
})
```

- One `export const <EntityId> = entity({` per entity, at column 0. The id is PascalCase singular, the export name, the key in `entities` and the string every other artifact cites; `glossary` is the kebab-case id of the glossary term it models (`Order line` → `order-line`, so the id is `OrderLine`), and the name, definition and object axes live on that term, so the entity holds no copy of them.
- Inside an entity: `  fields: {` (two spaces), exactly one field per line as `    <name>: f.<type>(...),` (four spaces, trailing comma), closed by `  },`. A field `name` is `lowercase_snake_case`; its `id` in `model.json` is derived as `<entity_snake>_<name>`.
- `export const model = defineModel({` at column 0 with `  entities: {`, one `    <EntityId>,` per line, closed by `  },`; a shared enum adds `  enums: {` with `    <enum_id>: <ConstName>,` lines after it.
- `model.json` validates against `tree/10_blueprint/datamodel/datamodel-model.schema.json` (JSON Schema 2020-12, lenient: the required keys are those the host's editor needs, plus `glossary_id`); `gen.ts` validates before it writes. Top-level keys: `version` (`"1.0"`), `entities[]`, `relationships[]` (derived from `m2o` and `m2m`), `enums[]` (the shared enums) and `editor` (the canvas viewport, carried over from the existing file).
- Inside `skaile-model.ts` the types `Infer<typeof Task>` (a row), `Model` and `Seed` give the mockup and `seed.ts` their typing.

**Scalar types**, one `f.<type>(options)` each; the row type is what `Infer` gives the field:

| Type | Meaning | Row type | Example fields |
|---|---|---|---|
| `string` | Short text (≤ 255 chars) | `string` | name, title |
| `text` | Long plain text | `string` | description, bio, notes |
| `richtext` | Formatted content (HTML/markdown) | `string` | article body, changelog |
| `integer` | Whole number | `number` | count, sort_order, age |
| `float` | Decimal number | `number` | rating, latitude |
| `decimal` | Precise decimal (financial, scientific) | `number` | amount, balance, tax_rate |
| `boolean` | True/false | `boolean` | is_active, is_published |
| `date` | Date only (no time), ISO `YYYY-MM-DD` | `string` | birth_date, due_date |
| `datetime` | Date + time with timezone, ISO 8601 | `string` | published_at |
| `json` | Arbitrary structured data | `unknown` | settings, metadata, preferences |
| `uuid` | Unique identifier | `string` | external_id |
| `slug` | URL-friendly unique string | `string` | slug |
| `email` | Email address | `string` | email |
| `url` | Web address | `string` | website |
| `password` | Secret (hashed at app layer) | `string` | password_hash |
| `image` | Image file reference | `string` | avatar, cover_image |
| `file` | Any file reference | `string` | attachment, document |

**Optionality.** Every field is required by default; mark an optional one `required: false`. Its row key is then `T | null` and may be omitted. The `?` suffix belongs to Prisma output and is never written in the model.

**Enum type.** `f.enum({ Draft: 'Initial state' })` defines an inline enum, an object mapping PascalCase values to descriptions (the field's row type is the union of the values). An enum reused across entities is declared once with `sharedEnum({ ... })`, listed in `defineModel({ enums })` under its `snake_case` id, and referenced by `f.enumRef(<Const>)`. The translator generates the concrete enum (Prisma `enum`, SQL `CHECK`).

**Relation types**

| Type | DSL | Meaning | Example |
|---|---|---|---|
| `m2o` | `f.m2o(() => User, { on_delete? })` | Many-to-one, owning side | task.owner_id → User |
| `o2m` | never declared | One-to-many, the inverse of an m2o; the translator generates it | user.tasks → Task[] |
| `m2m` | `f.m2m(() => Tag, { through: 'TaskTag' })` | Many-to-many via an explicit junction entity | Task ↔ Tag |

Declare `m2o` with the `_id` suffix on the owning side; its row value is the target's `id` and `model.json` gets one relation field plus one `relationships[]` entry (`on_delete`: `cascade | set_null | restrict`, `label`, `inverse` as `inverse_label`). `m2m` holds no column: the junction entity (`TaskTag`) has an `m2o` to both sides, and `through` names it by its id, which is how two entities refer to each other without a type cycle. A self-reference is `f.m2o('Task')` for the same reason.

**Entity options**

| Option | `model.json` key | Purpose |
|---|---|---|
| `glossary` | `glossary_id` | The glossary term the entity models |
| `display` | `display_name` | Human name of the entity |
| `label_field` | `label_field` | Field used as display name in UI lists and dropdowns — set on every entity |
| `key_field` | `key_field` | URL-friendly unique identifier — set when the entity has a human-readable unique slug |
| `standard_fields` | `standard_fields` | Auto-generated fields; defaults to `["id", "created_at", "updated_at"]` for every entity |
| `icon`, `color`, `position`, `from_features` | same | Canvas and traceability hints, all optional |
| `proposed` | `status`, `proposed_by`, `proposed_on`, `source` | Marks the entity as proposed |

`standard_fields` entries are injected by the translator, so they are not repeated in `fields`.

**Field options**, all optional:

| Option | Purpose |
|---|---|
| `required` | Whether the field must have a value (default: `true`) |
| `unique`, `readonly`, `indexed`, `primary` | Enforce uniqueness, prevent editing after creation, create a database index, mark as primary key |
| `max_length` | Maximum character length (string fields) |
| `default` | Value a new row starts with |
| `placeholder` | UI hint text |
| `faker` | Seed data generator hint (e.g. `'faker.internet.email'`) |
| `description` | What the field holds, in the term's words |
| `proposed` | Marks the field as proposed |

An `m2o` field also takes `on_delete`, `label` and `inverse`.

**Proposed entity or field.** A skill in `may_propose` (`spec-feature`, `experience-screen`, `mockup-storybook`, `mockup-feedback`) that needs an entity or field the model lacks appends it to `model.ts` with `proposed: { by: '<skill>', on: '<YYYY-MM-DD>', source: '<evidence or the user's words>' }` (`tree/README.md § Ownership`), as an option of the field or the entity, then runs `gen.ts`; the generated entry carries `status: "proposed"`, `proposed_by`, `proposed_on` and `source`. `architecture-datamodel` promotes it by deleting the `proposed` option or rejects it with a record in `_concept/10_blueprint/decisions.md`. A proposed entity or field is never confirmed in `model.dbml`: it is left out there and named in the file's header comment; its seed rows are scratch data for the mockup until promotion.

**`model.dbml`** is rendered by `gen.ts`: one `Enum` per inline and shared enum, one `Table` per confirmed entity (`id uuid [pk]`, the fields with semantic type names, `created_at` and `updated_at` as `datetime`), one `Ref: <Entity>.<field> > <Target>.id [delete: …]` per `m2o`, and `[not null]`, `[null]`, `[unique]`, `[default: …]` and `[note: …]` settings from the field options.

Stack-specific concerns (Prisma decorators, Directus system collections, PostXL `standardFields` casing) belong to the stack translator, not to the model; see `tree/10_blueprint/datamodel/README.md § Materialising the database`.

## Writing it

1. **Copy the tool files.** When `_concept/10_blueprint/datamodel/skaile-model.ts` is absent, or its first-line `// skaile-model <version>` differs from the skill's copy, copy `skaile-model.ts` and `gen.ts` from `skills/architecture-datamodel/references/dsl/` and the two schemas `tree/10_blueprint/datamodel/datamodel-model.schema.json` and `tree/10_blueprint/datamodel/datamodel-seed.schema.json` beside `model.ts`; `gen.ts` finds the schemas next to itself. Never edit the copies (`tree/10_blueprint/datamodel/skaile-model.md`).
2. **Write `model.ts`** in the layout of `## Format`, from the approved model (`tree/10_blueprint/datamodel/README.md § Writing it`), applying `tree/10_blueprint/datamodel/README.md § Naming`. Every entity carries its `glossary`, `display` and `label_field`; an `m2m` gets a junction entity. A raw SQL type here survives into a migration that will not apply.
3. **Run `npx tsx gen.ts`** in `_concept/10_blueprint/datamodel/`. It checks the mechanical rules of `## Checks`, validates `model.json` against the schema and writes `model.json` and `model.dbml` (and `seed.json` once `seed.ts` exists, `tree/10_blueprint/datamodel/seed.md`); on a violation it exits non-zero naming the file, the JSON path and the schema pointer and writes nothing. Fix `model.ts` and run it again.
4. **A proposal by another skill** appends its field or entity per `## Format`, runs `gen.ts` and restores the file when `gen.ts` fails.

## Checks

- `gen.ts` exits 0, so `model.json` validates against `tree/10_blueprint/datamodel/datamodel-model.schema.json` and the seed validates against `tree/10_blueprint/datamodel/datamodel-seed.schema.json`.
- Every entity has a `glossary` that exists in `_concept/glossary.md`, and its id is that term in PascalCase (`gen.ts` checks the second half).
- Every field is an `f.*` of the tables above; no raw SQL or Prisma type appears.
- Every entity sets `label_field` (naming one of its fields) and declares `standard_fields`.
- Every `m2o` name ends in `_id` and targets an entity listed in `defineModel`; every `m2m` has a junction entity with an `m2o` to both sides and no `o2m` is declared.
- Every shared enum is referenced by at least one field.
- `model.json` and `model.dbml` are the render of the current `model.ts`; where they diverge, a hand edit is the likely cause and `build-database` reports every disagreement rather than preferring one.
