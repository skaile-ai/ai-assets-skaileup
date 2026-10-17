---
path: _concept/05_features/featuresets.md
summary: the roster of featuresets and the features in each, with priorities
writers: [spec-featuresets]
---

# _concept/05_features/featuresets.md

The roster: every featureset this product has and every feature in it, named and prioritised. It draws the boundaries and writes no feature spec — `spec-feature` takes one entry at a time and turns it into the spec and its screens. The loop runs `spec-feature` once per must-have entry, and every role name used in a later `## Permissions` table comes from this file.

## Format

Frontmatter is the universal pair from `tree/README.md § Frontmatter every markdown artifact carries`. The body, in this order:

1. One section per featureset: its slug (lowercase, hyphenated; it becomes the directory each feature spec is written into), one sentence on what a user does in it, and a table of its features.
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

The roster holds no requirements, no acceptance criteria and no screens. Entity names in outcome lines are read, never coined: from `10_blueprint/datamodel/model.json` when it exists, else from `tree/glossary.md`.

## Writing it

1. **Start from the stories, not from the domain.** Read `_concept/04_journeys/stories.yaml` and collect every `candidate_features` hint across every journey (`tree/04_journeys/stories.md`); read `brief.md` and `goals.md` for what is in scope at all. A feature that traces to no story and no line of the brief is one you thought of rather than one the product needs — find the journey it serves, or leave it out and let the user add it back deliberately. A project whose `project_type` never grows journeys (`tree/01_meta/scope.md § Project types`) has no `stories.yaml`: derive the roster from the brief's hero flow and goals, trace each feature to a line of the brief, and write that line where the table says story ids.
2. **Let the competitor findings sharpen the list**, where research ran: a gap users complain about in `02_grounding/research/competitors.md` is a candidate with evidence behind it, and a feature every competitor has that no journey mentions is a question to ask rather than a feature to add.
3. **Cluster into featuresets by what a user is doing**, not by which entity is touched. Aim for a handful: a featureset so large it has no single purpose gets re-cut the first time somebody looks for something in it, and one holding a single feature is a folder pretending to be a grouping.
4. **Prioritise from the story stage** (`stories.yaml § stages`). Hero, vital and hygiene stories give must-have features; backlog stories give nice-to-have. The `feature_scope` answer calibrates what survives — must-have only cuts everything backlog-derived, comprehensive keeps it all — and whatever is cut is written under `## Cut` rather than dropped, so the next reader can tell a decision from an oversight. Without stories there is no stage: the brief's hero flow gives must-have, everything else nice-to-have, and the user confirms the split in step 7.
5. **Settle the role vocabulary once**, here: the roles across every featureset, names only. Each feature spec's `## Permissions` is the one record of who may do what (`tree/05_features/README.md § Permissions`), and its tables only line up if the words were agreed in one place first.
6. **Write the file** in the format above. A concept with no glossary term or no model entity is handed back: the flow re-enters `concept-glossary` for a missing term and `architecture-datamodel` for a missing model.
7. **Put the whole roster to the user as a table** with counts per featureset and per priority, and iterate until they approve; this is the cheapest point at which a mis-grouped feature costs a line instead of a directory rename. Then hand off: the loop runs `spec-feature` once per must-have entry.

## Checks

- Every featureset lists its features with priority and `story_refs`.
- Every feature traces to a story or to an explicit line of the brief.
- The user has approved the roster (`approved:` set).
