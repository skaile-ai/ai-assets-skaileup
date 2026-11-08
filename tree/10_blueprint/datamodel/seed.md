---
path: _concept/10_blueprint/datamodel/seed.yaml
summary: named scenarios of sample data, every row checked against model.yaml
owner: [architecture-datamodel]
may_propose: []
---

# _concept/10_blueprint/datamodel/seed.yaml

Realistic sample data organised as named scenarios, so each consumer picks the state it needs. Mockups render it, screen specs quote it and the E2E tests run against it, so a thin `populated` scenario shows up as a design nobody could review. `seed.yaml` is authored and checked against `model.yaml` by `bunx @skaile/model check` (`tree/10_blueprint/datamodel/README.md § Format`): a row with a field the model does not have, a missing required field or an undeclared enum value is an error naming the row, which is how a model error surfaces early. It is a file of its own beside the model because its rows outnumber the model's lines many times over. `build-database` wires it into the project's seed script in the layout the template's `## Seed` section gives, reading it through `bunx @skaile/model json`; nothing writes back into it.

## Format

```yaml
# yaml-language-server: $schema=https://cdn.jsdelivr.net/npm/@skaile/model@1/schema/seed.schema.json
version: 1

scenarios:
  empty:
    description: App with no user data yet - tests empty states
    data: { user: [], task: [] }

  single_user:
    description: One user, minimal data - tests first-use experience
    data:
      user:
        - { id: u1, display_name: Maria Schmidt, email: maria.schmidt@example.com, created_at: 2026-03-01T10:00:00Z, updated_at: 2026-03-01T10:00:00Z }
      task: []

  populated:
    description: Realistic usage - multiple users, varied data, mixed statuses
    data:
      user:
        - { id: u1, display_name: Maria Schmidt, email: maria.schmidt@example.com, created_at: 2026-03-01T10:00:00Z, updated_at: 2026-03-01T10:00:00Z }
      task:
        - { id: t1, title: Draft the release notes, status: Draft, priority: High, owner_id: u1, created_at: 2026-03-02T09:00:00Z, updated_at: 2026-03-02T09:00:00Z }

  edge_cases:
    description: Stress-tests for layout, validation, and i18n
    data: { user: [], task: [] }
```

- The first line binds the package's schema for editors (`tree/10_blueprint/datamodel/README.md § Format`); keep it as written.
- Top level: `version` (always `1`) and `scenarios`, a scenario name (`lowercase_snake_case`) to `{ description, data }`.
- The `data` keys are the snake_case form of the entity id in `model.yaml`, singular (`Task` → `task`, `ProjectMember` → `project_member`); a row has a string `id` unique in its entity, the declared fields by their `name`, and the optional `created_at` and `updated_at`; relation fields end in `_id` and hold the target row's `id`; enum values are PascalCase. A row per line (`- { … }`) keeps a scenario scannable; a row with long text may be a block.
- An optional field (`required: false`) may be `null` or left out; a required one is always present and never `null`.

**Standard scenarios** — all four are always present:

| Scenario | Purpose | Used by |
|---|---|---|
| `empty` | No data — empty states, onboarding flows | Mockups (empty state), E2E (first-use) |
| `single_user` | Minimal — first-use experience | Mockups (getting started), E2E (setup flow) |
| `populated` | Realistic — the happy-path view | Mockups (default view), E2E (core journeys) |
| `edge_cases` | Stress — long names, special chars, missing optionals | Mockups (layout robustness), E2E (validation) |

Further scenarios (`permissions` and others) are optional, follow feature needs, and appear as keys of the same mapping.

**Data quality rules**
- Every relation field references a valid id from the related entity in the same scenario, so relations resolve inside their own scenario.
- Every record in `populated` and `single_user` carries `created_at` and `updated_at`.
- `populated` has at least 2 entries per entity (3+ preferred) and its statuses cover every enum value across the records.
- `edge_cases` includes long names (100+ characters), special characters (umlauts, accents, hyphens, plus signs) in text fields, and null values for optional fields.
- Data looks real: names from different locales (German, French, Japanese, Spanish), varied string lengths from `"X"` to very long, realistic email formats including subdomains and international TLDs.
- A stack that needs a fixed dev identity for auth-scoped queries (a user matching the mock JWT subject) gets that record in every scenario except `empty`; the template's `## Seed` section says whether it does.
- A proposed entity (`tree/10_blueprint/datamodel/model.md § Format`) may carry rows that the mockup needs; they are scratch data until the entity is promoted.
- A value YAML would read as another type is quoted: a text field holding `true`, `false`, `null` or a number is written `"…"`, and the check reports the type where it is not.

## Writing it

Write `seed.yaml` after the model is approved and `model.yaml` checks, with all four standard scenarios plus `permissions` when the journeys name distinct roles. Generate values that are realistic and varied, with entity keys and field names following `tree/10_blueprint/datamodel/README.md § Naming`. Run `bunx @skaile/model check _concept/10_blueprint/datamodel` (`npx @skaile/model check …` without Bun); an issue on a row names the scenario, the entity, the row and the field to fix in `seed.yaml` or to add to `model.yaml` (as a proposal when this skill does not own the model). Run it again until it prints `ok`.

Readers by scenario:

- `mockup-storybook` renders each screen in `populated` as the hero view, `empty` for empty-state design and `edge_cases` to verify layout; the scenario keys are its toolbar.
- `spec-feature` references `populated` in a screen's `## Template Data` section and mentions `empty` and `edge_cases` in `## States`.
- `quality-e2e` uses `empty` for onboarding and first-use flows, `populated` for core journeys, `edge_cases` for validation and layout stress, `permissions` for role-based access.
- `build-database` generates one runnable script per scenario from the seed `bunx @skaile/model json` prints.

## Checks

`bunx @skaile/model check` prints `ok`, which covers:

- The file validates against the package's `seed.schema.json`, and all four standard scenarios exist.
- Each entity key names an entity of `model.yaml`; every row has a unique `id`, no undeclared field and every required one (not null).
- Scalar values have their field's type, and enum values are declared.
- Every relation resolves inside its own scenario.

Reviewed, not checked by the tool: `populated` covers every enum value and has at least two rows per entity, and `edge_cases` carries the stress values above.
