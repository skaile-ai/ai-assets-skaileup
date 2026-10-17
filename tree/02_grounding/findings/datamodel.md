---
path: _concept/02_grounding/findings/datamodel.md
summary: entities, fields, relations and enums the schema declares
writers: [concept-reverse]
---

# _concept/02_grounding/findings/datamodel.md

The entities, fields, relations and enums the repository's schema declares, mapped to semantic
types. `architecture-datamodel` reads it as evidence. An entity name here is not final until the
model is built, so a name guessed into a spec now diverges from the model silently and nothing
catches it.

## Format

Frontmatter per `tree/02_grounding/findings/README.md`. Per entity: field names and types,
relations (foreign keys, `@relation`, `hasMany` / `belongsTo`), unique constraints, nullability,
defaults and enum values, with the file and line the entity came from. Framework types are
translated to the types in `tree/10_blueprint/datamodel/model.md`, never carried over raw; a
stack-specific type in the semantic layer cannot be retargeted.

| framework | semantic |
|---|---|
| `String`, `varchar`, `text` | `string` — `text` / `@db.Text` on a long field is `richtext` |
| `Int`, `Float`, `Decimal`, `numeric` | `number` |
| `Boolean`, `bool` | `boolean` |
| `DateTime`, `timestamp`, `date` | `datetime` |
| `Json`, `jsonb` | `json` |
| an `@id` / primary key column | `uuid` |
| a relation field or foreign key | `relation` |
| a column holding a path or URL to an upload | `image` or `file` |
| an enum type or a checked string column | `enum`, with its values |

## Writing it

1. Read the schema sources in priority order; the first present is authoritative and the rest
   fill the gaps it leaves. A disagreement between two of them is a finding to report, not to
   resolve silently.
   1. **Prisma** — `prisma/schema.prisma`
   2. **Drizzle** — `db/schema.ts`, `src/db/*.ts`
   3. **TypeORM** — decorated classes under `src/entities/`, `src/models/`
   4. **Mongoose** — `models/*.ts`, `src/models/*.ts` with `new Schema({…})`
   5. **SQL migrations** — `migrations/`, `db/migrations/`; take the most recent migration per
      table, since earlier ones describe columns that no longer exist
   6. **SQLAlchemy** — `models.py`, `app/models/*.py`
   7. **TypeScript interfaces** — `src/types/`, `shared/types/`, only when no ORM is present
   8. **GraphQL schema** — `schema.graphql`, `src/schema.ts`
2. Record where fixture, factory and seed files live and what they cover: they are real example
   data for this schema, the `populated` scenario that `tree/10_blueprint/datamodel/seed.md`
   builds on, and they beat invented rows because they already satisfy the constraints.

## Checks

Every entity cites its file and line, and every type is a semantic type.
