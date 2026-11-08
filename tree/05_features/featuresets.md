---
path: _concept/05_features/featuresets.md
summary: the roster of featuresets, their features and priorities, and the open ideas
owner: [concept-brief, spec-feature]
may_propose: [concept-research, experience-journeys]
---

# _concept/05_features/featuresets.md

The roster: every featureset this product has and every feature in it, named and prioritised, and the ideas nobody has specified yet. Feature rows grow one at a time: each `spec-feature` run adds the row of the feature it specifies, so a feature row and its spec appear in the same write set and no feature row outlives its spec. `## Ideas` holds the candidates before that: `concept-brief` writes the first ones from the brief, and a run that specifies one moves its row. The roster holds no requirements, and every role name in a feature's `permissions:` comes from this file.

## Format

Frontmatter is the universal pair from `tree/README.md § Frontmatter every markdown artifact carries`. The body, in this order:

1. One section per featureset: its slug (lowercase, hyphenated; it becomes the directory each feature spec is written into), one sentence on what a user does in it, and a table of its features, one row per specified feature.
2. `## Roles` — the role vocabulary across every featureset: names only, no grants.
3. `## Ideas` — candidate features not specified yet, one row each, per `## Ideas` below.
4. `## Cut` — every candidate that was cut, with the reason.

```markdown
## onboarding
A new user creates an account and gets to a working first state.

| feature | outcome | priority | story_refs |
|---|---|---|---|
| registration | a visitor becomes a User with a verified email | must-have | onboarding_flow, invite_flow |
| profile-setup | a User fills in the profile the app needs | nice-to-have | onboarding_flow |

## Roles
admin, member, guest

## Ideas
| idea | featureset | source | proposed_by |
|---|---|---|---|
| team-invites | onboarding | `brief.md` hero flow: "invite the team" (2026-10-20) | concept-brief |
| csv-export | reports (new) | `competitors.md`: Acme gap "no export" (2026-10-21) | concept-research |

## Cut
- bulk-import — backlog story only, `feature_scope` = must-have only
```

A row whose `proposed_by` names a skill in `may_propose:` is that skill's proposed entry (`tree/README.md § Ownership`): the column names the proposer, and `source` carries the evidence and the date.

The roster holds no requirements, no acceptance criteria and no screens. Entity names in outcome lines are read, never coined: from `_concept/10_blueprint/datamodel/model.yaml` when it exists, else from the glossary (`tree/glossary.md § Where the words live`).

## Ideas

An idea is a candidate feature nobody has specified: an app idea from the brief or the user, a feature a DEFER names, a gap research found. A row names it by the slug the feature would take (`tree/05_features/[featureset]/[feature].md § Slug`), the featureset it would join (an existing slug, or a new one marked `(new)`), its source with the date (a file and the line, or the user's words), and the skill that wrote it. It carries no outcome, priority or criteria, because an idea is not a decision: those are settled when it is specified. A row is added only for an idea that no feature row, idea or `## Cut` line covers.

- `concept-brief` writes the first rows (`### First ideas (concept-brief)`).
- `spec-feature` adds a row for a feature its grill names that the run does not specify, a DEFER included. It moves a row when it acts on it: into the featureset's table when it specifies the idea, or under `## Cut` with the reason when the user declines it.
- `experience-journeys` proposes a feature the user named that no journey's `candidate_features` carries; `concept-research` proposes a gap users complain about in `_concept/02_grounding/research/competitors.md`. Specifying the idea promotes it; declining it moves it under `## Cut`.

A declined idea that clears the decisions gate is also appended to `_concept/10_blueprint/decisions.md` with `Status: rejected` (`tree/10_blueprint/decisions.md`), by the owner that declined it.

## Writing it

### Feature rows (spec-feature)

Each step runs inside a `spec-feature` run (`tree/05_features/[featureset]/[feature].md § Writing it`) and binds the row that run adds.

1. **Read the roster and find the candidates.** Open `_concept/05_features/featuresets.md` if it exists. A run that names a feature starts there; a run that names none offers the `## Ideas` rows first, then the `candidate_features` hints of `_concept/04_journeys/stories.yaml` (format: `tree/04_journeys/stories.md`) that no row, idea or `## Cut` line covers, hero and vital stories first. A feature that traces to no story and no line of `_concept/brief.md` or `_concept/goals.md` is one you thought of rather than one the product needs — find the journey it serves, or leave it out and let the user add it back deliberately. A project whose `project_type` never grows journeys (`tree/01_meta/scope.md § Project types`) has no `stories.yaml`: trace the feature to the brief's hero flow or a goal, and write that line where the table says story ids. With no stories, brief or goals at all, the feature's purpose and the user it serves are the first question of the run's batch, and `story_refs` stays empty until a journey exists.
2. **Let the competitor findings sharpen the candidates**, where research ran: a gap users complain about in `_concept/02_grounding/research/competitors.md` is a candidate with evidence behind it, and a feature every competitor has that no journey mentions is a question to ask rather than a feature to add.
3. **Place the feature by what a user is doing**, not by which entity is touched: in an existing featureset when its one-sentence purpose fits, else in a new one with its slug and purpose line. A featureset so large it has no single purpose gets re-cut the first time somebody looks for something in it, and one holding a single feature is a folder pretending to be a grouping, so say which of the two a placement leads to. Renaming a slug later rewrites every cross-reference to it, so confirm a new slug before the file is written.
4. **Ask the priority in the grill's first decision batch** (`tree/README.md § How a skill runs`), recommendation first. Hero, vital and hygiene stories (`stories.yaml § stages`) recommend must-have; backlog stories recommend nice-to-have. The optional `feature_scope` answer calibrates the recommendation: must-have only recommends cutting everything backlog-derived, comprehensive keeps it all. A candidate the user declines goes under `## Cut` with the reason rather than being dropped, so the next reader can tell a decision from an oversight.
5. **Settle roles once per role.** A role the grill names that `## Roles` lacks is added after the user confirms the name, names only; a feature's `permissions:` (`tree/05_features/README.md § Permissions`) only lines up with its siblings if the words were agreed here first.
6. **Add the row** with the feature's outcome line, priority and `story_refs` when the feature spec is written, in the same write set the user sees (`tree/05_features/[featureset]/[feature].md § Writing it`, step 9). An idea row the feature came from leaves `## Ideas` in the same write. A concept with no glossary term is filed as a `proposed` term per `tree/glossary.md § Where the words live` and the row carries on with it; an entity the model lacks is a proposed entity in `model.yaml`.

### First ideas (concept-brief)

Each step runs inside a `concept-brief` run (`tree/brief.md § Drafting the brief`).

1. **Collect the candidates from the brief.** Every feature the user named in the description or the onboarding answers, and each one the hero flow cannot work without, that no feature row, idea or `## Cut` line covers already. Name each by its would-be slug and place it by what a user does in it, as step 3 of `### Feature rows (spec-feature)` does, marking a new featureset `(new)`.
2. **Show them with the brief and goals, and write them after the same yes** (`tree/brief.md § Approving both files`), with `proposed_by: concept-brief` and the brief line or the user's words as source. When the roster does not exist, create it holding the frontmatter and `## Ideas` only. A re-run adds rows and never edits a feature row, `## Roles` or a `## Cut` line.

## Checks

- Every feature row names a feature whose spec exists at `05_features/<featureset>/<feature>.md`, and every spec has a row.
- Every feature row carries a priority and `story_refs`, and traces to a story, to an explicit line of the brief or goals, or to the purpose the user stated in the run's first batch.
- Every role used in a feature's `permissions:` is in `## Roles`.
- Every `## Ideas` row has an idea, a featureset, a dated source and a `proposed_by` that is an owner or a `may_propose` skill of this node; no idea has a spec, a feature row or a `## Cut` line.
