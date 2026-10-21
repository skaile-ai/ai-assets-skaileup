---
path: _concept/06_behaviors/<featureset>.md
summary: states, transitions and named constants for one featureset's entities
owner: [experience-behaviors]
may_propose: []
---

# _concept/06_behaviors/<featureset>.md

The states an entity can be in, what moves it between them, and what has to hold on either side. The feature specs and the screens are built against it: what a transition exposes becomes a screen's data requirement, what triggers it a user action, its `requires` guard a state-dependent element, and its `requires`/`ensures` the WHEN/SHALL of a criterion. The file is named for its featureset and exists only for featuresets with a real lifecycle — an entity with exactly one state is not a state machine and does not belong here.

## Format

Frontmatter is the universal pair from `tree/README.md § Frontmatter every markdown artifact carries`. States, transitions and constants are plain markdown tables in the body, not frontmatter: every reader is an agent or a person, and a grammar with no parser drifts from what it claims to describe without anything noticing. Entity and enum names are those the data model uses (`tree/10_blueprint/datamodel/README.md § Naming`).

Per entity: its states listed, then a transition table. A transition that realises a criterion names it by id in `criteria`, never by its text (ids per `tree/04_journeys/stories.md`).

| from | event | to | requires | ensures | criteria |
|---|---|---|---|---|---|
| active | failed login, count reaches the limit | locked | account is active | further attempts are refused | AC-login-03 |

Then `## Constants` — the values the rules quote (retry limits, lockout durations, session timeouts, page sizes), named once so the same number is not re-guessed in a feature spec, a screen and the code — and `## Open questions`.

## Writing it

1. **Read the featuresets and what has been specified so far.** `05_features/featuresets.md` for the grouping, every feature spec already written under it, `brief.md` for the domain, and `04_journeys/stories.yaml` for the criteria (by id) the lifecycles have to satisfy. With no roster yet, propose the featureset slug from the glossary cluster or the code area the entity lives in and confirm it with the user in the first batch, so the file name matches the roster `spec-feature` grows later. `02_grounding/research/behavioral-patterns.md`, where it exists, carries how this domain already models these lifecycles — worth borrowing before inventing.
2. **Find the entities with a life.** Entity names are read, never coined: from `10_blueprint/datamodel/model.json` when it exists, else from the glossary (`tree/glossary.md § Where the words live`), else from `02_grounding/findings/datamodel.md` (a scoped `concept-reverse` for `datamodel` when the code holds the schema). An entity none of them names goes into the first batch (`tree/README.md § How a skill runs`) and is filed as a `proposed` term per `tree/glossary.md § Where the words live`, and the table carries on with it. For each featureset ask what things the features act on, which of them can be in more than one state, what moves them between states — a user action, a clock, another entity — and what must be true before and after each move.
3. **Write one markdown file per featureset** at `06_behaviors/<featureset>.md`: each entity's states and its transition table, in the format above.
4. **Name the constants, and point at the permissions.** Who can trigger which transition is the feature spec's role × action table (`tree/05_features/README.md § Permissions`, in `05_features/<featureset>/<feature>.md`), so cite it per entity and never restate it; where that spec is not written yet, the roles for a transition go under `## Open questions`, and `spec-feature` settles them in its table.
5. **Record what formalising exposed.** Every ambiguity the feature specs left open goes under `## Open questions`, phrased as the decision it needs rather than as an observation — these are the rules that would otherwise be settled silently by whoever implements them first.
6. **Report the tables** — per featureset: entities, states, transitions, open questions — and put the open questions to the user; their answers go back into the tables before the file is treated as settled. When an answer, or any later edit, changes a rule a written feature spec rests on, name that spec's file (`05_features/<featureset>/<feature>.md`) in the completion summary: `spec-feature` updates the spec's criteria by id.

## Checks

- Every featureset with a real lifecycle has a file; each entity in it has its states and a transition table.
- The open questions have been put to the user.
