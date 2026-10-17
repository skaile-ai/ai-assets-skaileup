---
path: _concept/10_blueprint/datamodel/seed.json
summary: realistic seed scenarios for mockups, screen specs and E2E tests
writers: [architecture-datamodel]
---

# _concept/10_blueprint/datamodel/seed.json

Realistic sample data organised as named scenarios, so each consumer picks the state it needs. Mockups render it, screen specs quote it and the E2E tests run against it, so a thin `populated` scenario shows up as a design nobody could review. `seed.json` is the source of truth: `build-database` wires it into the project's seed script in the layout the template's `## Seed` section gives, and nothing writes back into it.

## Format

Entity keys are the snake_case form of the entity `id` in `model.json`, singular (`Task` → `task`, `ProjectMember` → `project_member`); relation fields end in `_id`; enum values are PascalCase. The file validates against `tree/10_blueprint/datamodel/datamodel-seed.schema.json` (JSON Schema 2020-12: `version`, and `scenarios` with the four standard ones required, each `{ description, data }`); it cannot check that keys exist in the model, that relations resolve inside their scenario, or that `populated` covers every enum value, so the data quality rules below are checked by hand.

```json
{
  "version": "1.0",
  "scenarios": {
    "empty": {
      "description": "App with no user data yet — tests empty states",
      "data": { "user": [], "task": [] }
    },
    "single_user": {
      "description": "One user, minimal data — tests first-use experience",
      "data": {
        "user": [
          { "id": "u1", "email": "maria.schmidt@example.com", "display_name": "Maria Schmidt", "role": "Admin", "created_at": "2026-03-01T10:00:00Z", "updated_at": "2026-03-01T10:00:00Z" }
        ],
        "task": []
      }
    },
    "populated": {
      "description": "Realistic usage — multiple users, varied data, mixed statuses",
      "data": {
        "user": [
          { "id": "u1", "email": "maria.schmidt@example.com", "display_name": "Maria Schmidt", "role": "Admin", "created_at": "2026-03-01T10:00:00Z", "updated_at": "2026-03-10T08:00:00Z" },
          { "id": "u2", "email": "jean-pierre.dubois@example.com", "display_name": "Jean-Pierre Dubois", "role": "Member", "created_at": "2026-03-02T14:00:00Z", "updated_at": "2026-03-09T16:00:00Z" }
        ],
        "task": [
          { "id": "t1", "title": "Design landing page", "status": "Done", "assigned_to_id": "u1", "created_at": "2026-03-01T10:30:00Z", "updated_at": "2026-03-07T15:00:00Z" },
          { "id": "t2", "title": "Write user documentation", "status": "Todo", "assigned_to_id": null, "created_at": "2026-03-05T14:00:00Z", "updated_at": "2026-03-05T14:00:00Z" }
        ]
      }
    },
    "edge_cases": {
      "description": "Stress-tests for layout, validation, and i18n",
      "data": {
        "user": [
          { "id": "u10", "email": "maría-josé.fernández-garcía-de-la-cruz@subdomain.example.co.uk", "display_name": "María José Fernández-García de la Cruz", "role": "Member" },
          { "id": "u11", "email": "a@b.co", "display_name": "X", "role": "Admin" }
        ],
        "task": [
          { "id": "t10", "title": "A", "status": "Todo", "assigned_to_id": "u11" }
        ]
      }
    },
    "permissions": {
      "description": "Tests role-based visibility — admin sees everything, member sees own",
      "data": {
        "user": [
          { "id": "u20", "email": "admin@example.com", "display_name": "Admin User", "role": "Admin" },
          { "id": "u21", "email": "member@example.com", "display_name": "Regular Member", "role": "Member" }
        ],
        "task": [
          { "id": "t20", "title": "Admin-only task", "status": "Todo", "assigned_to_id": "u20", "visibility": "Admin" }
        ]
      }
    }
  }
}
```

**Standard scenarios** — all four are always present:

| Scenario | Purpose | Used by |
|---|---|---|
| `empty` | No data — empty states, onboarding flows | Mockups (empty state), E2E (first-use) |
| `single_user` | Minimal — first-use experience | Mockups (getting started), E2E (setup flow) |
| `populated` | Realistic — the happy-path view | Mockups (default view), E2E (core journeys) |
| `edge_cases` | Stress — long names, special chars, missing optionals | Mockups (layout robustness), E2E (validation) |

Further scenarios (`permissions` and others) are optional and follow feature needs.

**Data quality rules**
- Every relation field references a valid id from the related entity in the same scenario, so relations resolve inside their own scenario.
- Every record in `populated` and `single_user` carries `created_at` and `updated_at`.
- `populated` has at least 2 entries per entity (3+ preferred) and its statuses cover every enum value across the records.
- `edge_cases` includes long names (100+ characters), special characters (umlauts, accents, hyphens, plus signs) in text fields, and null values for optional fields.
- Data looks real: names from different locales (German, French, Japanese, Spanish), varied string lengths from `"X"` to very long, realistic email formats including subdomains and international TLDs.
- A stack that needs a fixed dev identity for auth-scoped queries (a user matching the mock JWT subject) gets that record in every scenario except `empty`; the template's `## Seed` section says whether it does.

## Writing it

Write the file after the model is approved, with all four standard scenarios plus `permissions` when the journeys name distinct roles. Generate values that are realistic and varied, with entity keys and field names following `tree/10_blueprint/datamodel/README.md § Naming`. Validate the file against `tree/10_blueprint/datamodel/datamodel-seed.schema.json` before writing it.

Readers by scenario:

- `mockup-walkthrough` and `mockup-storybook` render each screen in `populated` as the hero view, `empty` for empty-state design and `edge_cases` to verify layout.
- `spec-feature` references `populated` in a screen's `## Template Data` section and mentions `empty` and `edge_cases` in `## States`.
- `quality-e2e` uses `empty` for onboarding and first-use flows, `populated` for core journeys, `edge_cases` for validation and layout stress, `permissions` for role-based access.
- `build-database` generates one runnable script per scenario from this file.

## Checks

- All four standard scenarios exist.
- Every relation resolves inside its own scenario.
- `seed.json` validates against `tree/10_blueprint/datamodel/datamodel-seed.schema.json`, and each entity key is the snake_case form of an entity `id` in `model.json`.
