---
path: _concept/04_journeys/stories.yaml
summary: personas, story map by stage, EARS criteria with ids
owner: [experience-journeys]
may_propose: []
---

# _concept/04_journeys/stories.yaml

The personas and the staged journeys the product exists for, each with testable acceptance criteria. `spec-feature` seeds the roster from it, and feature specs, slice plans, the ledger and e2e verdicts all cite its criterion ids, so a wrong shape here is re-cut in every skill after it.

## Format

A data file, not a markdown artifact — no frontmatter.

The machine-readable form is `tree/04_journeys/journeys.schema.json`.

```yaml
version: "1.0"
last_updated: YYYY-MM-DD
project: Project Name           # name, problem and success metrics come from the brief
problem: "..."
success_metrics: ["..."]
stages:                         # the one place stages are defined; every other skill cites it
  hero: "The one journey that, if it fails, leaves the product with no reason to exist."
  vital: "Other journeys that make the product usable day to day."
  hygiene: "Operational flows the product cannot run without: onboarding, settings, roles, import/export."
  backlog: "Journeys deliberately out of this scope."
personas:
  - id: persona_id
    name: Persona Name
    role: role_name
    goals: ["..."]
journeys:
  - id: journey_id              # one journey is one story; this id is the <story-id> in criterion ids
    persona: persona_id
    title: Journey Title
    stage: hero                 # an id from stages: above
    steps:
      - action: What the user does
        system_response: What the system does
        acceptance:
          - { id: AC-journey_id-01, ears: "WHEN ..., THE SYSTEM SHALL ..." }
    candidate_features: [feature_slug]
    candidate_entities: [EntityName]
    candidate_screens: [screen_name]
```

Exactly one journey carries `stage: hero`; a second means the product's core has not been decided. A story `id` is a snake_case slug (lowercase letters, digits, `_`), unique in the file.

### EARS template

    WHEN <trigger>, THE SYSTEM SHALL <response>

Variants: `WHILE <state>, THE SYSTEM SHALL <response>` (state-driven); `IF <unwanted condition>, THEN THE SYSTEM SHALL <response>` (unwanted behaviour). One observable response per line; every criterion independently verifiable. Patterns in use: ubiquitous, event-driven, state-driven, optional-feature, complex.

### Criterion ids

    AC-<story-id>-<nn>

- `<story-id>` is the `id` of the journey the criterion belongs to; because a story id never contains `-`, the trailing `-<nn>` is unambiguous.
- `<nn>` is two digits, numbered per story in write order from `01`.
- A criterion `spec-feature` adds that no story holds takes the same shape with the feature slug as scope, `AC-<feature_slug>-<nn>`, using a slug that is not a story id. The slug keeps its hyphens (`AC-rechner-inputs-03`); the id still ends in `-<nn>`, so it parses from the right. Only `experience-journeys` and `spec-feature` coin ids.
- An id never changes and is never reused: a dropped criterion retires its id, an edited wording keeps it, a changed meaning is a new criterion with the next number.
- Every other artifact cites the id and never retypes the criterion text; the text lives here or in the feature spec that wrote it, and a second copy is the one that drifts.

### Deriving the criteria

`spec-feature` writes the feature-level criteria into the feature spec from these sources (each cited by its id):

| Source | What it yields |
|---|---|
| the grill and the scope line | every item ruled IN becomes a criterion; nothing else does |
| `_concept/04_journeys/stories.yaml` | story-level criteria, state transitions, guard conditions |
| `_concept/07_screens/<screen>.md` | one criterion per state — default, loading, error, empty, success — and per user action |
| `_concept/06_behaviors/<featureset>.md` | `requires` guards become the WHEN clause, postconditions the SHALL |
| `_concept/10_blueprint/datamodel/seed.json` | the concrete data a criterion is stated against |

Each criterion is one observable behaviour, specific ("the user sees 'Invalid email or password'", not "an error"), stated against concrete values (seed names, exact routes, status codes), independently verifiable, and every error state a screen lists is one.

### Registration

Journeys register nothing by frontmatter: `spec-feature` discovers them by reading this file. It seeds each roster row from the journey's `candidate_features`, sets `story_refs` in the feature's frontmatter to the journey ids that motivated it, and may add, merge or split features beyond the hints — `story_refs` traces the origin. A `story_refs` entry that names an id not in this file is flagged by `ops-review`.

## Writing it

1. **Resolve the facts, then ask** (`tree/README.md § How a skill runs`, rule 1). Read, in any order and none required: `brief.md` for the audience and the `hero_flow`; `goals.md` for what success means and therefore which journeys matter; `02_grounding/research/audiences.md` for personas grounded in real job titles; `02_grounding/findings/brief-seeds.md` and `routes.md` for what the code already lets users do (where a repository exists and they are absent or stale, run `concept-reverse` scoped to `brief` and `routes`). Mark what the code supplied `inferred`. What none of them settles — audience, hero flow, success — goes into one batch. Without research, derive the personas from the brief or findings and say so — an invented persona reads exactly like a researched one to every skill after this.
2. **Define two to five personas**, each with a slug id, a label and what they are trying to achieve. Put the list to the user before going further: personas are the axis everything below is organised on, and adding one later re-cuts every journey.
3. **Map exactly one hero journey.** It comes from the brief's `hero_flow` (or the answer to the batch) and is the journey whose failure leaves the product with no reason to exist: three to eight sequential stories, each with a snake_case slug `id`, its persona, its outcome and at least two acceptance criteria. Stop and get this one approved before mapping anything else.
4. **Map the rest, staged by what they are for, and write the `stages:` section.** `vital` — the other journeys that make the product usable day to day. `hygiene` — the operational flows nobody buys the product for and it cannot run without: onboarding, settings, roles, import and export. `backlog` — journeys deliberately out of this scope, sourced from the goals' non-goals and the gaps research found. The stage sets each story's priority, and `spec-feature` and `experience-shell` read it.
5. **Write acceptance criteria in EARS for every story** — at least two on a hero story, one everywhere else — in the pattern that fits, each with its `AC-<story-id>-<nn>` id given at write time. A vague criterion ("the system should work") is fixed here, once.
6. **Give every story its downstream hints** — `candidate_features`, `candidate_entities`, `candidate_screens` — as plain strings; they are hints, not specs. `candidate_entities` are read from `glossary.md`, never coined; a concept with no term is appended there as a `proposed` term and the hint carries on with it.
7. **Write the file** — validated against `tree/04_journeys/journeys.schema.json` before writing (convert YAML dates to ISO text first: an unquoted `2026-10-17` loads as a date, and `json.loads(json.dumps(doc, default=str))` turns it back) — with the project name, problem and success metrics from the brief or the answers, the personas, the `stages:` section with its four definitions, then the journeys. Show the map as a table by stage with counts, and iterate until the user approves.

## Checks

Exactly one hero journey; every story has an `id` and at least one EARS criterion carrying its `AC-<story-id>-<nn>` id plus its candidate hints; every `stage:` is a key of `stages:`; the user has approved the map.
