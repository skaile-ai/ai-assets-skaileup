---
path: _concept/05_features/featuresets.md
summary: the roster of featuresets and the features in each, with priorities
owner: [spec-feature]
may_propose: []
---

# _concept/05_features/featuresets.md

The roster: every featureset this product has and every feature in it, named and prioritised. It grows one row at a time: each `spec-feature` run adds the row of the feature it specifies, so a roster row and a feature spec appear in the same write set and no row outlives its spec. It holds no requirements, and every role name in a feature's `permissions:` comes from this file.

## Format

Frontmatter is the universal pair from `tree/README.md § Frontmatter every markdown artifact carries`. The body, in this order:

1. One section per featureset: its slug (lowercase, hyphenated; it becomes the directory each feature spec is written into), one sentence on what a user does in it, and a table of its features, one row per specified feature.
2. `## Roles` — the role vocabulary across every featureset: names only, no grants.
3. `## Cut` — every candidate that was cut, with the reason.

```markdown
## onboarding
A new user creates an account and gets to a working first state.

| feature | outcome | priority | story_refs |
|---|---|---|---|
| registration | a visitor becomes a User with a verified email | must-have | onboarding_flow, invite_flow |
| profile-setup | a User fills in the profile the app needs | nice-to-have | onboarding_flow |

## Roles
admin, member, guest

## Cut
- bulk-import — backlog story only, `feature_scope` = must-have only
```

The roster holds no requirements, no acceptance criteria and no screens. Entity names in outcome lines are read, never coined: from `_concept/10_blueprint/datamodel/model.json` when it exists, else from `_concept/glossary.md` (format: `tree/glossary.md`).

## Writing it

Each step runs inside a `spec-feature` run (`tree/05_features/[featureset]/[feature].md § Writing it`) and binds the row that run adds.

1. **Read the roster and find the candidates.** Open `_concept/05_features/featuresets.md` if it exists. A run that names a feature starts there; a run that names none offers the `candidate_features` hints of `_concept/04_journeys/stories.yaml` (format: `tree/04_journeys/stories.md`) that no row or `## Cut` line covers, hero and vital stories first. A feature that traces to no story and no line of `_concept/brief.md` or `_concept/goals.md` is one you thought of rather than one the product needs — find the journey it serves, or leave it out and let the user add it back deliberately. A project whose `project_type` never grows journeys (`tree/01_meta/scope.md § Project types`) has no `stories.yaml`: trace the feature to the brief's hero flow or a goal, and write that line where the table says story ids. With no stories, brief or goals at all, the feature's purpose and the user it serves are the first question of the run's batch, and `story_refs` stays empty until a journey exists.
2. **Let the competitor findings sharpen the candidates**, where research ran: a gap users complain about in `_concept/02_grounding/research/competitors.md` is a candidate with evidence behind it, and a feature every competitor has that no journey mentions is a question to ask rather than a feature to add.
3. **Place the feature by what a user is doing**, not by which entity is touched: in an existing featureset when its one-sentence purpose fits, else in a new one with its slug and purpose line. A featureset so large it has no single purpose gets re-cut the first time somebody looks for something in it, and one holding a single feature is a folder pretending to be a grouping, so say which of the two a placement leads to. Renaming a slug later rewrites every cross-reference to it, so confirm a new slug before the file is written.
4. **Ask the priority in the run's first decision batch** (`tree/README.md § How a skill runs`), recommendation first. Hero, vital and hygiene stories (`stories.yaml § stages`) recommend must-have; backlog stories recommend nice-to-have. The optional `feature_scope` answer calibrates the recommendation: must-have only recommends cutting everything backlog-derived, comprehensive keeps it all. A candidate the user declines goes under `## Cut` with the reason rather than being dropped, so the next reader can tell a decision from an oversight.
5. **Settle roles once per role.** A role the grill names that `## Roles` lacks is added after the user confirms the name, names only; a feature's `permissions:` (`tree/05_features/README.md § Permissions`) only lines up with its siblings if the words were agreed here first.
6. **Add the row** with the feature's outcome line, priority and `story_refs` when the feature spec is written, in the same write set the user sees (`tree/05_features/[featureset]/[feature].md § Writing it`, step 8). A concept with no glossary term is appended there as a `proposed` term and the row carries on with it; an entity the model lacks is a proposed entity in `model.json`.

## Checks

- Every row names a feature whose spec exists at `05_features/<featureset>/<feature>.md`, and every spec has a row.
- Every row carries a priority and `story_refs`, and traces to a story, to an explicit line of the brief or goals, or to the purpose the user stated in the run's first batch.
- Every role used in a feature's `permissions:` is in `## Roles`.
