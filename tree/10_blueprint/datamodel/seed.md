---
path: [_concept/10_blueprint/datamodel/seed.ts, _concept/10_blueprint/datamodel/seed.json]
summary: seed.ts is authored and typed against the model; seed.json is generated
owner: [architecture-datamodel]
may_propose: []
---

# _concept/10_blueprint/datamodel/seed.ts, seed.json

Realistic sample data organised as named scenarios, so each consumer picks the state it needs. Mockups render it, screen specs quote it and the E2E tests run against it, so a thin `populated` scenario shows up as a design nobody could review. `seed.ts` is the authored source: it is typed against `model.ts`, so a row with a field the model does not have fails `tsc` while the mockup is being built, which is how a model error surfaces early. `gen.ts` writes `seed.json`, the file `build-database` wires into the project's seed script in the layout the template's `## Seed` section gives; nothing edits it by hand and nothing writes back into it.

## Format

`seed.ts` imports the model and calls `scenarios`:

```ts
import { scenarios } from './skaile-model'
import { model } from './model'

export const seed = scenarios(model, {
  empty: { description: 'App with no user data yet — tests empty states', data: { user: [], task: [] } },
  single_user: {
    description: 'One user, minimal data — tests first-use experience',
    data: {
      user: [{ id: 'u1', display_name: 'Maria Schmidt', email: 'maria.schmidt@example.com', created_at: '2026-03-01T10:00:00Z', updated_at: '2026-03-01T10:00:00Z' }],
      task: [],
    },
  },
  populated: { description: 'Realistic usage — multiple users, varied data, mixed statuses', data: { /* … */ } },
  edge_cases: { description: 'Stress-tests for layout, validation, and i18n', data: { /* … */ } },
})
```

The `data` keys are the snake_case form of the entity `id` in `model.ts`, singular (`Task` → `task`, `ProjectMember` → `project_member`); a row has `id`, the declared fields by their `name`, and the optional `created_at` and `updated_at`; relation fields end in `_id`; enum values are PascalCase. The generated `seed.json` is `{ "version": "1.0", "scenarios": { <name>: { "description", "data": { <entity_key>: [row] } } } }` and validates against `tree/10_blueprint/datamodel/datamodel-seed.schema.json` (JSON Schema 2020-12: `version`, and `scenarios` with the four standard ones required). `gen.ts` also checks what the schema cannot: that each key names an entity, that a row has no undeclared field and every required one, that an enum value is declared, and that relations resolve inside their own scenario. That `populated` covers every enum value stays a review check.

**Standard scenarios** — all four are always present:

| Scenario | Purpose | Used by |
|---|---|---|
| `empty` | No data — empty states, onboarding flows | Mockups (empty state), E2E (first-use) |
| `single_user` | Minimal — first-use experience | Mockups (getting started), E2E (setup flow) |
| `populated` | Realistic — the happy-path view | Mockups (default view), E2E (core journeys) |
| `edge_cases` | Stress — long names, special chars, missing optionals | Mockups (layout robustness), E2E (validation) |

Further scenarios (`permissions` and others) are optional, follow feature needs, and appear as keys of the same object.

**Data quality rules**
- Every relation field references a valid id from the related entity in the same scenario, so relations resolve inside their own scenario.
- Every record in `populated` and `single_user` carries `created_at` and `updated_at`.
- `populated` has at least 2 entries per entity (3+ preferred) and its statuses cover every enum value across the records.
- `edge_cases` includes long names (100+ characters), special characters (umlauts, accents, hyphens, plus signs) in text fields, and null values for optional fields.
- Data looks real: names from different locales (German, French, Japanese, Spanish), varied string lengths from `"X"` to very long, realistic email formats including subdomains and international TLDs.
- A stack that needs a fixed dev identity for auth-scoped queries (a user matching the mock JWT subject) gets that record in every scenario except `empty`; the template's `## Seed` section says whether it does.
- A proposed entity (`tree/10_blueprint/datamodel/model.md § Format`) may carry rows that the mockup needs; they are scratch data until the entity is promoted.

## Writing it

Write `seed.ts` after the model is approved and `model.ts` exists, with all four standard scenarios plus `permissions` when the journeys name distinct roles. Generate values that are realistic and varied, with entity keys and field names following `tree/10_blueprint/datamodel/README.md § Naming`. Run `npx tsx gen.ts` in `_concept/10_blueprint/datamodel/` (`tree/10_blueprint/datamodel/model.md § Writing it`); it validates the seed against `tree/10_blueprint/datamodel/datamodel-seed.schema.json` and writes `seed.json`. Then type-check with `npx -y -p typescript@5 tsc --noEmit --strict --target es2022 --module esnext --moduleResolution bundler model.ts seed.ts` in the same directory. A `tsc` or `gen.ts` error on a row names the field to fix in `seed.ts` or to add to `model.ts`.

Readers by scenario:

- `mockup-storybook` renders each screen in `populated` as the hero view, `empty` for empty-state design and `edge_cases` to verify layout; the scenario keys are its toolbar.
- `spec-feature` references `populated` in a screen's `## Template Data` section and mentions `empty` and `edge_cases` in `## States`.
- `quality-e2e` uses `empty` for onboarding and first-use flows, `populated` for core journeys, `edge_cases` for validation and layout stress, `permissions` for role-based access.
- `build-database` generates one runnable script per scenario from `seed.json`.

## Checks

- All four standard scenarios exist.
- Every relation resolves inside its own scenario.
- `gen.ts` exits 0: `seed.json` validates against `tree/10_blueprint/datamodel/datamodel-seed.schema.json`, and each entity key is the snake_case form of an entity `id` in `model.ts`.
- `tsc --noEmit` over `model.ts` and `seed.ts` is clean.
