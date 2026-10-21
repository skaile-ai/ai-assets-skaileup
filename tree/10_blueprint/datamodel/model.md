---
path: [_concept/10_blueprint/datamodel/model.dbml, _concept/10_blueprint/datamodel/model.json]
summary: model.json is authored, model.dbml generated — semantic types, relations
owner: [architecture-datamodel]
may_propose: [spec-feature]
---

# _concept/10_blueprint/datamodel/model.dbml, model.json

The canonical, stack-neutral data model, in two forms: `model.json`, the one authored model (and the editor canvas's file), and `model.dbml`, generated from it to read. The skill renders `model.dbml` from `model.json` on every write and nobody edits it by hand. Both carry semantic types — intent, not output format — and `build-database` maps them to a concrete stack. Cross-references from other artifacts (`data_entities[]`, `story_refs`) always target the entity `id` in `model.json`; stack-specific files are derived and never referenced. Names follow `tree/10_blueprint/datamodel/README.md § Naming`.

## Format

`model.json` validates against `tree/10_blueprint/datamodel/datamodel-model.schema.json` (JSON Schema 2020-12, lenient: the required keys are those the host's editor needs, plus `glossary_id`). Validate before writing. Top-level keys: `version` (`"1.0"`), `entities[]`, `relationships[]` and optional `enums[]`; `editor` (canvas viewport) is written by the editor, never by a skill. An entity carries `id` (PascalCase singular — the model name every other artifact cites), `glossary_id` (the kebab-case id of the glossary term it models — `Order line` → `order-line`; the name, definition and object axes live on that term, so the entity holds no copy of them), `display_name`, `fields[]` and the metadata below; a field carries a stable `id`, a snake_case `name` and a semantic `type` (the scalar types, `enum`, or `relation`).

**Proposed entity.** A skill in `may_propose` (`spec-feature`) that needs an entity the model lacks appends it with `status: "proposed"`, `proposed_by`, `proposed_on` and `source` (`tree/README.md § Ownership`); `architecture-datamodel` promotes it by dropping the markers or rejects it with a record in `_concept/10_blueprint/decisions.md`. A proposed entity is never confirmed in `model.dbml` and carries no seed data until promoted.

**Scalar types**

| Type | Meaning | Example fields |
|---|---|---|
| `string` | Short text (≤ 255 chars) | name, title, slug, email, url |
| `text` | Long plain text | description, bio, notes |
| `richtext` | Formatted content (HTML/markdown) | article body, changelog |
| `integer` | Whole number | count, sort_order, age |
| `float` | Decimal number | rating, latitude |
| `decimal` | Precise decimal (financial, scientific) | amount, balance, tax_rate |
| `boolean` | True/false | is_active, is_published |
| `date` | Date only (no time) | birth_date, due_date |
| `datetime` | Date + time with timezone | created_at, published_at |
| `json` | Arbitrary structured data | settings, metadata, preferences |
| `uuid` | Unique identifier | id, external_id |
| `password` | Secret (hashed at app layer) | password_hash |
| `image` | Image file reference | avatar, cover_image |
| `file` | Any file reference | attachment, document |

**Optionality.** Every field is required by default; mark an optional one `required: false`. The `?` suffix belongs to Prisma output and is never written in the model.

**Enum type.** Defined inline as an object mapping PascalCase values to descriptions. Inline enums stay as written below; a shared enum reused across models lives in the top-level `enums[]`, each `{ id, values: [{ value, label }] }`, and a field references it by `enum_id`. The translator generates the concrete enum (Prisma `enum`, SQL `CHECK`).

```json
{
  "id": "task_status",
  "name": "status",
  "type": "enum",
  "values": {
    "Draft": "Initial state, not yet submitted",
    "InReview": "Awaiting approval",
    "Published": "Live and visible"
  }
}
```

**Relation types**

| Type | Meaning | Example |
|---|---|---|
| `m2o` | Many-to-one | task.assigned_to → User |
| `o2m` | One-to-many (inverse of m2o) | user.tasks → Task[] |
| `m2m` | Many-to-many | Task ↔ Tag (via junction model) |

Declare `m2o` with the `_id` suffix on the owning side, once in the entity's fields (`type: "relation"`, `relation_target` = the target entity `id`) and once in `relationships[]` (`from`, `from_field`, `to`, `type`, optional `on_delete`: `cascade | set_null | restrict`); never declare `o2m`, the translator generates it; give every `m2m` an explicit junction model (`TaskTag` with an `m2o` to both sides).

**Model metadata**

| Property | Purpose |
|---|---|
| `label_field` | Field used as display name in UI lists and dropdowns — set on every model |
| `key_field` | URL-friendly unique identifier (slug / readable URL) — set when the model has a human-readable unique slug |
| `standard_fields` | Auto-generated fields to include; defaults to `["id", "created_at", "updated_at"]` for every model |
| `faker` | Per-field hint for seed generation (e.g. `"faker.internet.email"`) |

`standard_fields` entries are injected by the translator, so they are not repeated in the model's fields list.

**Field properties**, all optional:

| Property | Type | Purpose |
|---|---|---|
| `required` | boolean | Whether the field must have a value (default: `true`) |
| `unique` | boolean | Enforce uniqueness |
| `readonly` | boolean | Prevent editing after creation |
| `indexed` | boolean | Create a database index |
| `max_length` | number | Maximum character length (string fields) |
| `placeholder` | string | UI hint text |
| `faker` | string | Seed data generator hint |

Stack-specific concerns (Prisma decorators, Directus system collections, PostXL `standardFields` casing) belong to the stack translator, not to the model; see `tree/10_blueprint/datamodel/README.md § Materialising the database`.

**Example.** A minimal whole `model.json` that validates against the schema: entities identified by PascalCase `id`, an `m2o` field of `type: "relation"` whose `relation_target` is the referenced entity id and which is also listed once in `relationships[]` (owning side only), and the status enum inline.

```json
{
  "version": "1.0",
  "entities": [
    {
      "id": "User",
      "glossary_id": "user",
      "display_name": "User",
      "label_field": "display_name",
      "key_field": "email",
      "standard_fields": ["id", "created_at", "updated_at"],
      "fields": [
        { "id": "user_display_name", "name": "display_name", "type": "string", "max_length": 80, "faker": "faker.person.fullName" },
        { "id": "user_email", "name": "email", "type": "string", "unique": true, "faker": "faker.internet.email" },
        { "id": "user_avatar", "name": "avatar", "type": "image", "required": false }
      ]
    },
    {
      "id": "Task",
      "glossary_id": "task",
      "display_name": "Task",
      "label_field": "title",
      "standard_fields": ["id", "created_at", "updated_at"],
      "fields": [
        { "id": "task_title", "name": "title", "type": "string", "max_length": 120 },
        {
          "id": "task_status",
          "name": "status",
          "type": "enum",
          "values": {
            "Draft": "Initial state, not yet submitted",
            "InReview": "Awaiting approval",
            "Published": "Live and visible"
          }
        },
        { "id": "task_due_date", "name": "due_date", "type": "date", "required": false },
        { "id": "task_owner_id", "name": "owner_id", "type": "relation", "relation_target": "User", "indexed": true }
      ]
    }
  ],
  "relationships": [
    { "id": "task_owner", "from": "Task", "from_field": "owner_id", "to": "User", "type": "m2o", "on_delete": "cascade" }
  ]
}
```

## Checks

- `model.json` validates against `tree/10_blueprint/datamodel/datamodel-model.schema.json` before it is written.
- Every entity has a `glossary_id` that exists in `_concept/glossary.md`, and its `id` is that term in PascalCase.
- Every field type is a semantic type from the table above; no raw SQL or Prisma type appears.
- Every entity sets `label_field` and declares `standard_fields`.
- Every `m2m` has a junction model and no `o2m` is declared.
- `model.dbml` is the render of the current `model.json`; where they diverge, a hand edit is the likely cause and `build-database` reports every disagreement rather than preferring one.
