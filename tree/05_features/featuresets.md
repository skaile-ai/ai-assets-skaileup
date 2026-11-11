---
path: _concept/05_features/featuresets.md
summary: the roster of featuresets, their features and priorities, and the open ideas
owner: [concept-brief]
may_propose: [concept-research, experience-journeys, spec-feature]
---

# _concept/05_features/featuresets.md

The roster: every featureset this product has and every feature in it, named and prioritised, and the ideas nobody has specified yet. `concept-brief` owns the file and is the only skill that writes it. Feature rows grow one at a time: each `spec-feature` run proposes the row of the feature it specifies, and `concept-brief` promotes it, so no feature row outlives its spec. `## Ideas` holds the candidates before that: `concept-brief` writes the first ones from the brief, and other skills propose more. The roster holds no requirements, and every role name in a feature's `permissions:` comes from this file.

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
| idea | featureset | source | raised_by |
|---|---|---|---|
| team-invites | onboarding | `brief.md` hero flow: "invite the team" (2026-10-20) | concept-brief |
| csv-export | reports (new) | `competitors.md`: Acme gap "no export" (2026-10-21) | concept-research |

## Cut
- bulk-import — backlog story only, `feature_scope` = must-have only
```

`raised_by` names the skill the idea came from — `concept-brief` for its own rows, the proposer for a promoted proposal entry — and `source` carries the evidence and the date.

The roster holds no requirements, no acceptance criteria and no screens. Entity names in outcome lines are read, never coined: from `_concept/10_blueprint/datamodel/model.yaml` when it exists, else from the glossary (`tree/glossary.md § Where the words live`).

**Proposal entry** (`tree/proposals/README.md`). A skill under `may_propose` writes a roster change into its run's proposal file, never into this one. The `anchor` is `idea:<slug>`, the feature's would-be slug, for every move of that feature, or `role:<name>` for a role the roster lacks (`payload`: the role name). The `payload` of an `idea:` entry is a mapping `{ move, featureset, row }`:

| `move` | what it does | `row` |
|---|---|---|
| `idea` | adds a row to `## Ideas` | the `## Ideas` table row, `raised_by` the proposer |
| `table` | adds the feature row to the featureset's table and removes the idea row of that slug, if any | the feature table row |
| `cut` | adds the line under `## Cut` and removes the idea row of that slug, if any | the `## Cut` line with its reason |

`featureset` is the slug the row joins; a featureset the roster lacks adds `purpose`, its one-sentence line, to the mapping.

```yaml
- id: p2
  target: _concept/05_features/featuresets.md
  anchor: idea:team-invites
  payload: { move: table, featureset: onboarding, row: "| team-invites | a member invites a teammate by email | must-have | invite_flow |" }
  source: "_concept/05_features/onboarding/team-invites.md, approved 2026-11-11"
  status: proposed
```

Until `concept-brief` promotes it, a pending entry targeting this file counts as part of the roster for every reader: a feature is specified once its `table` entry exists, and an idea is covered once its `idea` or `cut` entry exists.

## Ideas

An idea is a candidate feature nobody has specified: an app idea from the brief or the user, a feature a DEFER names, a gap research found. A row names it by the slug the feature would take (`tree/05_features/[featureset]/[feature].md § Slug`), the featureset it would join (an existing slug, or a new one marked `(new)`), its source with the date (a file and the line, or the user's words), and the skill that raised it. It carries no outcome, priority or criteria, because an idea is not a decision: those are settled when it is specified. A row is added only for an idea that no feature row, idea, `## Cut` line or pending proposal entry covers.

- `concept-brief` writes the first rows (`### First ideas (concept-brief)`).
- `spec-feature` proposes a `move: idea` entry for a feature its grill names that the run does not specify, a DEFER included, and a `move: table` or `move: cut` entry for the feature it acts on: `table` when it specifies the idea, `cut` with the reason when the user declines it.
- `experience-journeys` proposes a feature the user named that no journey's `candidate_features` carries; `concept-research` proposes a gap users complain about in `_concept/02_grounding/research/competitors.md`. Both are `move: idea` entries.

A declined idea that clears the three-test gate is also proposed as a decision record with `status: rejected` (`tree/docs/adr/README.md § Writing it`), by the run in which the user declined it. A rejected proposal entry is not such a decision and gets no record: its `reason` is the record.

## Writing it

### Feature rows (spec-feature)

Each step runs inside a `spec-feature` run (`tree/05_features/[featureset]/[feature].md § Writing it`) and binds the entries that run proposes. Every write goes into the run's proposal file (`tree/proposals/README.md § Writing it`).

1. **Read the roster and find the candidates.** Open `_concept/05_features/featuresets.md` if it exists, with the pending proposal entries that target it. A run that names a feature starts there; a run that names none offers the `## Ideas` rows and pending `move: idea` entries first, then the `candidate_features` hints of `_concept/04_journeys/stories.yaml` (format: `tree/04_journeys/stories.md`) that no row, idea, `## Cut` line or entry covers, hero and vital stories first. A feature that traces to no story and no line of `_concept/brief.md` or `_concept/goals.md` is one you thought of rather than one the product needs — find the journey it serves, or leave it out and let the user add it back deliberately. A project whose `project_type` never grows journeys (`tree/01_meta/scope.md § Project types`) has no `stories.yaml`: trace the feature to the brief's hero flow or a goal, and write that line where the table says story ids. With no stories, brief or goals at all, the feature's purpose and the user it serves are the first question of the run's batch, and `story_refs` stays empty until a journey exists.
2. **Let the competitor findings sharpen the candidates**, where research ran: a gap users complain about in `_concept/02_grounding/research/competitors.md` is a candidate with evidence behind it, and a feature every competitor has that no journey mentions is a question to ask rather than a feature to add.
3. **Place the feature by what a user is doing**, not by which entity is touched: in an existing featureset when its one-sentence purpose fits, else in a new one with its slug and purpose line. A featureset so large it has no single purpose gets re-cut the first time somebody looks for something in it, and one holding a single feature is a folder pretending to be a grouping, so say which of the two a placement leads to. Renaming a slug later rewrites every cross-reference to it, so confirm a new slug before the entry is written.
4. **Ask the priority in the grill's first decision batch** (`tree/protocol/running.md § How a skill runs`), recommendation first. Hero, vital and hygiene stories (`stories.yaml § stages`) recommend must-have; backlog stories recommend nice-to-have. The optional `feature_scope` answer calibrates the recommendation: must-have only recommends cutting everything backlog-derived, comprehensive keeps it all. A candidate the user declines becomes a `move: cut` entry with the reason rather than being dropped, so the next reader can tell a decision from an oversight.
5. **Settle roles once per role.** A role the grill names that `## Roles` lacks becomes a `role:<name>` entry after the user confirms the name; a feature's `permissions:` (`tree/05_features/README.md § Permissions`) only lines up with its siblings if the words were agreed here first.
6. **Propose the row** — a `move: table` entry with the feature's outcome line, priority and `story_refs` — when the feature spec is written, in the same write set the user sees (`tree/05_features/[featureset]/[feature].md § Writing it`, step 9). A concept with no glossary term is written into the same proposal file per `tree/glossary.md § Format`, *Proposal entry*, and the row carries on with it; an entity the model lacks is an entry per `tree/10_blueprint/datamodel/model.md § Format`.

### First ideas (concept-brief)

Each step runs inside a `concept-brief` run (`tree/brief.md § Drafting the brief`).

1. **Collect the candidates from the brief.** Every feature the user named in the description or the onboarding answers, and each one the hero flow cannot work without, that no feature row, idea, `## Cut` line or pending entry covers already. Name each by its would-be slug and place it by what a user does in it, as step 3 of `### Feature rows (spec-feature)` does, marking a new featureset `(new)`.
2. **Show them with the brief and goals, and write them after the same yes** (`tree/brief.md § Approving both files`), with `raised_by: concept-brief` and the brief line or the user's words as source. When the roster does not exist, create it holding the frontmatter and `## Ideas` only. A re-run adds rows and never edits a feature row, `## Roles` or a `## Cut` line except by promoting an entry.

### Settling roster moves (concept-brief)

At the start of every `concept-brief` run, and in a run the lead starts for this alone, settle the pending entries targeting this file per `tree/proposals/README.md § Writing it`, oldest file first.

1. **Promote `spec-feature`'s entries without a user batch.** The user approved the spec, its scope line and its priority in the `spec-feature` run (`tree/05_features/[featureset]/[feature].md § Writing it`, step 9), and that approval covers the move. Apply each entry as its `move` says — creating the featureset section from `purpose` when it is new, or adding the role to `## Roles` — and create the file holding the frontmatter and what the entries add when it does not exist.
2. **Promote `move: idea` entries from `experience-journeys` and `concept-research` without a user batch too**: an idea is not a decision, and the proposer already had the user's words or the evidence behind it.
3. **Reject only what the roster already settles**: an entry whose slug a feature row, idea or `## Cut` line covers in a way the entry does not change, with that line as the reason. Two entries that disagree on one slug (a `table` and a `cut`) go to the user as one question with a recommendation.
4. **Close each entry**: `status: promoted` or `rejected`, `settled_by: concept-brief`, `settled_on`, and the `reason` of a rejection.

## Checks

- Every feature row names a feature whose spec exists at `05_features/<featureset>/<feature>.md`, and every spec has a row or a pending `move: table` entry.
- Every feature row carries a priority and `story_refs`, and traces to a story, to an explicit line of the brief or goals, or to the purpose the user stated in the run's first batch.
- Every role used in a feature's `permissions:` is in `## Roles` or in a pending `role:` entry.
- Every `## Ideas` row has an idea, a featureset, a dated source and a `raised_by` that is the owner or a `may_propose` skill of this node; no idea has a spec, a feature row or a `## Cut` line.
- No pending proposal entry targets this file at the end of a `concept-brief` run, except one the user deferred.
