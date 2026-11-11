---
path: _concept/10_blueprint/datamodel/model.yaml
summary: the authored data model; checked and read through @skaile/model
owner: [architecture-datamodel]
may_propose: [spec-feature, experience-screen, mockup-storybook, mockup-feedback]
---

# _concept/10_blueprint/datamodel/model.yaml

The canonical, stack-neutral data model, and the one file that holds it: entities, fields, enums, relations and proposed entries. Nothing is generated from it into `_concept/`; every reader takes it through `@skaile/model` (`tree/10_blueprint/datamodel/README.md § Format`): `build-database` and the tests through `bunx @skaile/model@1 json`, the host's canvas through `loadModel`, the mockup package through the package's Vite plugin, whose row types make a component that uses a field the model no longer has fail `vue-tsc`. The file carries semantic types — intent, not output format — and `build-database` maps them to a concrete stack. Cross-references from other artifacts (`data_entities[]`, `story_refs`) target the entity id, its key under `entities:`; stack-specific files are derived and never referenced. Names follow `tree/10_blueprint/datamodel/README.md § Naming`.

## Format

```yaml
# yaml-language-server: $schema=https://cdn.jsdelivr.net/npm/@skaile/model@1/schema/model.schema.json
version: 1

enums:
  priority: { Low: Can wait, High: Needs attention today }

entities:
  User:
    label_field: display_name
    fields:
      display_name: { type: string, max_length: 80 }
      email: { type: email, unique: true }

  Task:
    label_field: title
    fields:
      title: { type: string, max_length: 120 }
      status:
        type: enum
        values: { Draft: Initial state, Published: Live and visible }
      priority: { type: enum, enum: priority }
      due_date: { type: date, required: false }
      owner_id: { type: m2o, to: User, on_delete: cascade, label: Owner, inverse: Tasks }
      estimate:
        type: decimal
        required: false
        proposed: { by: mockup-storybook, on: 2026-07-01, source: TaskEditor needs an effort estimate }
```

- The first line binds the package's schema for editors (`tree/10_blueprint/datamodel/README.md § Format`); keep it as written.
- Top level: `version` (always `1`), `enums` (the shared enums: a `lowercase_snake_case` id to `{ Value: description }`) and `entities` (the entity id, PascalCase singular, to its definition). An entity id is the string every other artifact cites.
- A field is `<name>: <type>` — a bare type name is a required field with no other options, for scalar types only — or `<name>: { type: <type>, <option>: … }`; a long options object may be written as a block, as `status` and `estimate` are above. A field `name` is `lowercase_snake_case`; its id in the normalized model is `<entity_snake>_<name>`.
- `id`, `created_at` and `updated_at` are standard fields: never declared under `fields:`.
- Keys are snake_case and the schema rejects an unknown one, naming the allowed keys, so a misspelt option is an error rather than a silent no-op.
- `bunx @skaile/model@1 json` prints the normalized model: `entities[]` (with `glossary_id`, `display_name`, `standard_fields` and `fields[]` filled in), `relationships[]` derived from every `m2o` and `m2m`, and `enums[]`, the shared enums with `{ value, label }` entries. Readers rely on that shape, never on the file's own layout.

**Scalar types**, one `type` each; the row type is what the package's row types give the field:

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

**Enum type.** `{ type: enum, values: { Draft: Initial state } }` defines an inline enum, a mapping of PascalCase values to descriptions (the field's row type is the union of the values). An enum reused across entities is declared once under the top-level `enums:` by its `snake_case` id and referenced by `{ type: enum, enum: <id> }`; a field has `values` or `enum`, never both. The translator generates the concrete enum (Prisma `enum`, SQL `CHECK`).

**Relation types**

| Type | Written as | Meaning | Example |
|---|---|---|---|
| `m2o` | `{ type: m2o, to: User, on_delete: cascade }` | Many-to-one, owning side | task.owner_id → User |
| `o2m` | never declared | One-to-many, the inverse of an m2o; the translator generates it | user.tasks → Task[] |
| `m2m` | `{ type: m2m, to: Tag, through: TaskTag }` | Many-to-many via an explicit junction entity | Task ↔ Tag |

Declare `m2o` with the `_id` suffix on the owning side; its row value is the target's `id`, and the normalized model gets one relation field plus one `relationships[]` entry (`on_delete`: `cascade | set_null | restrict`, `label`, `inverse` as `inverse_label`). `m2m` holds no column: the junction entity (`TaskTag`) has an `m2o` to both sides, and `through` names it by its id. An entity may target itself (`parent_id: { type: m2o, to: Task, required: false }`).

**Entity options**

| Option | Default | Normalized key | Purpose |
|---|---|---|---|
| `fields` | required | `fields[]` | The entity's own fields, by name |
| `glossary` | kebab-case of the id | `glossary_id` | The glossary term the entity models; its PascalCase form must be the id |
| `display` | the id in words, sentence case | `display_name` | Human name of the entity |
| `label_field` | none | `label_field` | Field used as display name in UI lists and dropdowns — set on every entity |
| `key_field` | none | `key_field` | URL-friendly unique identifier — set when the entity has a human-readable unique slug |
| `standard_fields` | `[id, created_at, updated_at]` | `standard_fields` | Fields the stack injects; not repeated in `fields` |
| `icon`, `color`, `from_features` | none | same | Canvas and traceability hints, all optional |
| `proposed` | none | `status`, `proposed_by`, `proposed_on`, `source` | Marks the entity as proposed |

Where the cards of an entity sit on a canvas is the host's state, not a key of the model.

**Field options**, all optional and for scalar, enum and `m2o` fields:

| Option | Purpose |
|---|---|
| `required` | Whether the field must have a value (default: `true`) |
| `unique`, `readonly`, `indexed`, `primary` | Enforce uniqueness, prevent editing after creation, create a database index (default `true` for `m2o`), mark as primary key |
| `max_length` | Maximum character length (string fields) |
| `default` | Value a new row starts with |
| `placeholder` | UI hint text |
| `faker` | Seed data generator hint (e.g. `faker.internet.email`) |
| `description` | What the field holds, in the term's words |
| `proposed` | Marks the field as proposed |

An `m2o` field also takes `to`, `on_delete`, `label` and `inverse`; an `m2m` takes `to`, `through`, `label` and `inverse`. An option that does not apply to the field's type is an error.

**Proposed entity or field.** A skill in `may_propose` (`spec-feature`, `experience-screen`, `mockup-storybook`, `mockup-feedback`) that needs an entity or field the model lacks adds it to `model.yaml` with `proposed: { by: <skill>, on: <YYYY-MM-DD>, source: <evidence or the user's words> }` (`tree/protocol/ownership.md § Ownership`), as a key of the field or the entity, then runs the check; the normalized entry carries `status: "proposed"`, `proposed_by`, `proposed_on` and `source`. `architecture-datamodel` promotes it by deleting the `proposed` key or rejects it by deleting the entry, with a record in `_concept/10_blueprint/decisions.md`. Until then the host's canvas shows it as proposed, and its seed rows are scratch data for the mockup.

Stack-specific concerns (Prisma decorators, Directus system collections, PostXL `standardFields` casing) belong to the stack translator, not to the model; see `tree/10_blueprint/datamodel/README.md § Materialising the database`.

## Writing it

1. **Migrate a pre-YAML model first.** When `_concept/10_blueprint/datamodel/` holds `model.ts` or `model.json` and no `model.yaml`, run `bunx @skaile/model@1 migrate _concept/10_blueprint/datamodel` (`tree/10_blueprint/datamodel/README.md § Format`) and continue on the files it writes. When it refuses because the TypeScript has no JSON or is newer than it, run the project's own generator in that directory (`npx tsx gen.ts`, still there until the migration deletes it), then `migrate` again. Any other refusal names what it cannot carry over; report it and stop.
2. **Write `model.yaml`** in the layout of `## Format`, from the approved model (`tree/10_blueprint/datamodel/README.md § Writing it`), applying `tree/10_blueprint/datamodel/README.md § Naming`. Every entity carries its `label_field`, and `glossary` where the term's slug is not the kebab-case of the id; an `m2m` gets a junction entity. A raw SQL type here survives into a migration that will not apply.
3. **Run `bunx @skaile/model@1 check _concept/10_blueprint/datamodel`** (`npx @skaile/model@1 check …` without Bun). Each issue names the file, the JSON path and the line; fix `model.yaml` and run it again until it prints `ok`.
4. **A proposal by another skill** adds its field or entity per `## Format`, runs the check and restores the file when the check fails.

## Checks

`bunx @skaile/model@1 check` prints `ok`, which covers:

- The file validates against the package's `model.schema.json`: known keys only, a known `type` per field, options that apply to that type.
- Every entity's id is the PascalCase form of its `glossary`; `label_field` and `key_field` name a field of the entity.
- An enum field has `values` or `enum`, a referenced shared enum is declared, and every shared enum is referenced by at least one field.
- Every `m2o` name ends in `_id` and targets an entity of the model; every `m2m` names a `through` entity with an `m2o` to both sides; no `o2m` is declared.

Reviewed, not checked by the tool:

- Every entity's `glossary` is a term in `_concept/glossary.md` (a `proposed` term counts).
- Every entity sets `label_field`.
- No raw SQL or Prisma type appears, in a type or a `default`.
