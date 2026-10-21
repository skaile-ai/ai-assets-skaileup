---
path: [_concept/05_features/]
summary: the feature roster and one spec per feature, grouped into featuresets
owner: []
may_propose: []
---

# _concept/05_features/

The product's features. `featuresets.md` is the roster, written once by `spec-featuresets`; each `<featureset>/<feature>.md` is one feature's permanent spec, written by `spec-feature`, one run per feature. A featureset is the only grouping level: a feature belongs to exactly one and nothing sits between them. Implementation scaffolding, `experience-behaviors`, the seed and the ledger all read these files, so a rule stated here once is a rule nobody restates.

## Contents

- `featuresets.md` — the roster; format in `tree/05_features/featuresets.md`.
- `<featureset>/` — one directory per featureset, named by a lowercase hyphenated slug; see `tree/05_features/[featureset]/README.md`.
- `<featureset>/<feature>.md` — one feature spec; format and procedure in `tree/05_features/[featureset]/[feature].md`.

## Permissions

Each feature file carries its permissions in frontmatter and restates them as a table for the reader. Implementation scaffolding reads them for the authorization policy; the data model does not, because it is built before any feature exists and takes its roles from the journeys.

```markdown
---
permissions:
  admin: [create, read, update, delete]
  member: [read, update]
  guest: [read]
---

## Permissions

| Role   | Actions                      |
| ------ | ---------------------------- |
| admin  | create, read, update, delete |
| member | read, update                 |
| guest  | read                         |
```

Role names come from the vocabulary `featuresets.md` settles once; the same person never appears as `admin` in one spec and `owner` in the next.

## Links in both directions

Every link between artifacts exists in both files: if screen X implements feature Y, feature Y lists screen X and screen X lists feature Y. A run that writes one side writes the other in the same step and updates `last_updated` on both.

| when | write | and |
|---|---|---|
| `spec-featuresets` writes the roster | `story_refs` on each feature = the journey ids that motivated it | features may be added, merged or split beyond what journeys suggest; `story_refs` traces the origin |
| `spec-feature` writes a screen | the screen's `implements:` lists the feature path(s) | append the screen path to each feature's `screens:` array |
| `spec-feature` writes a feature spec | `data_entities:` = model names from `10_blueprint/datamodel/model.json` | the feature's `data_entities` is the only feature↔entity join; the model holds no list of features |
| a screen is deleted or renamed | find every feature whose `screens:` names it; remove or update the entry | |
| a feature is deleted | find every screen whose `implements:` names it; remove the entry or flag it for human review | the model needs no update |

`06_behaviors/<featureset>.md` is optional: when it exists, `spec-feature` turns each transition into screen requirements — what a transition exposes is a data requirement, what triggers it is a user action, its `requires` guard is a state-dependent element. No frontmatter link is registered for it; readers check the folder.

## Checks

- Every feature's `screens:` entries and every screen's `implements:` entries resolve to each other.
- A feature's `story_refs` name journey ids that exist in `_concept/04_journeys/stories.yaml`.
- A feature's `data_entities` names models that exist in `model.json`, and a model no feature lists is an entity nobody asked for or a feature nobody wrote down.
