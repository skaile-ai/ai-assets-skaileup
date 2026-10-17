---
path: [_concept/10_blueprint/datamodel/model.dbml, _concept/10_blueprint/datamodel/model.json]
summary: the canonical stack-neutral model — semantic types, relations, metadata
writers: [architecture-datamodel]
---

# _concept/10_blueprint/datamodel/model.dbml, model.json

The canonical, stack-neutral data model, in two forms: `model.dbml` to read and `model.json` for the editor canvas. Both carry semantic types — intent, not output format — and `build-database` maps them to a concrete stack. Cross-references from other artifacts (`data_entities[]`, `story_refs`) always target `model.json`; stack-specific files are derived and never referenced. A container of models under `models`, `entities` or `tables` is accepted, each model identified by `name`; names follow `tree/10_blueprint/datamodel/README.md § Naming`.

## Format

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

**Enum type.** Defined inline as an object mapping PascalCase values to descriptions; a shared enum is defined at the top level of the schema and referenced by name. The translator generates the concrete enum (Prisma `enum`, SQL `CHECK`).

```json
{
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

Declare `m2o` with the `_id` suffix on the owning side; never declare `o2m`, the translator generates it; give every `m2m` an explicit junction model (`TaskTag` with an `m2o` to both sides).

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

**Example.** A minimal whole `model.json` in the canonical shape: the `models` container, each model identified by `name`, the `m2o` field typed with the referenced model's snake_case name, and the status enum inline.

```json
{
  "models": [
    {
      "name": "user",
      "label_field": "display_name",
      "key_field": "email",
      "standard_fields": ["id", "created_at", "updated_at"],
      "fields": [
        { "name": "display_name", "type": "string", "max_length": 80, "faker": "faker.person.fullName" },
        { "name": "email", "type": "string", "unique": true, "faker": "faker.internet.email" },
        { "name": "avatar", "type": "image", "required": false }
      ]
    },
    {
      "name": "task",
      "label_field": "title",
      "standard_fields": ["id", "created_at", "updated_at"],
      "fields": [
        { "name": "title", "type": "string", "max_length": 120 },
        {
          "name": "status",
          "type": "enum",
          "values": {
            "Draft": "Initial state, not yet submitted",
            "InReview": "Awaiting approval",
            "Published": "Live and visible"
          }
        },
        { "name": "due_date", "type": "date", "required": false },
        { "name": "owner_id", "type": "user", "indexed": true }
      ]
    }
  ]
}
```

## Checks

- Every field type is a semantic type from the table above; no raw SQL or Prisma type appears.
- Every model sets `label_field` and declares `standard_fields`.
- Every `m2m` has a junction model and no `o2m` is declared.
- `model.dbml` and `model.json` agree; where they diverge, a hand edit is the likely cause and `build-database` reports every disagreement rather than preferring one.
