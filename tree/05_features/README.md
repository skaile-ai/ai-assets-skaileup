---
path: [_concept/05_features/]
summary: the feature roster and one spec per feature, grouped into featuresets
owner: []
may_propose: []
---

# _concept/05_features/

The product's features. `featuresets.md` is the roster and each `<featureset>/<feature>.md` is one feature's permanent spec; `spec-feature` writes both, one run per feature, and the run adds the feature's roster row. A featureset is the only grouping level: a feature belongs to exactly one and nothing sits between them. Implementation scaffolding, `experience-behaviors`, the seed and the ledger all read these files, so a rule stated here once is a rule nobody restates.

## Contents

- `featuresets.md` — the roster; format in `tree/05_features/featuresets.md`.
- `<featureset>/` — one directory per featureset, named by a lowercase hyphenated slug; see `tree/05_features/[featureset]/README.md`.
- `<featureset>/<feature>.md` — one feature spec; format and procedure in `tree/05_features/[featureset]/[feature].md`.

## Permissions

Each feature file records who may do what once, in its frontmatter `permissions:` map. Implementation scaffolding and the review read that map for the authorization policy, and no body table restates it — a second copy is the one that drifts. The data model does not read it, because it is built before any feature exists and takes its roles from the journeys.

```yaml
permissions:
  admin: [create, read, update, delete]
  member: [read, update]
  guest: [read]
```

A grant that holds only under a condition (`member: update — own items only`) is a line under `## Scope`, citing the role and action it narrows.

Role names come from the vocabulary `featuresets.md` settles once; the same person never appears as `admin` in one spec and `owner` in the next.

## Links in both directions

Every link between a feature and a screen exists in both files: if screen X implements feature Y, feature Y lists screen X in `screens:` (entries `- path: 07_screens/<screen>.md`) and screen X lists feature Y in `implements:`. The two files have different owners, so a run writes its own side and proposes the other, as a mapping `{ path: <file>, status: proposed, proposed_by: <skill>, proposed_on: YYYY-MM-DD }`: `spec-feature` lists the screen in `screens:` and appends a proposed entry to the screen's `implements:`, and `experience-screen` writes its own `implements:` and appends a proposed entry to the feature's `screens:`. The owner turns a proposed entry into a plain `- path:` one on its next run; until then it counts for the cross-link.

| when | write | and |
|---|---|---|
| `spec-feature` adds a roster row | `story_refs` on the feature = the journey ids that motivated it | features may be added, merged or split beyond what journeys suggest; `story_refs` traces the origin |
| `spec-feature` lists a screen | the feature's `screens:` names the existing screen file | append a proposed entry to that screen's `implements:`; a screen that does not exist yet is named for `experience-screen` to write |
| `experience-screen` writes a screen | the screen's `implements:` lists the feature path(s) | append a proposed entry to each feature's `screens:` |
| `spec-feature` writes a feature spec | `data_entities:` = model names from `10_blueprint/datamodel/model.json` | the feature's `data_entities` is the only feature↔entity join; the model holds no list of features |
| a screen is deleted or renamed | find every feature whose `screens:` names it; remove or update the entry | |
| a feature is deleted | find every screen whose `implements:` names it; remove the entry or flag it for human review | the model needs no update |

`06_behaviors/<featureset>.md` is optional: when it exists, `spec-feature` turns each transition into screen requirements — what a transition exposes is a data requirement, what triggers it is a user action, its `requires` guard is a state-dependent element. No frontmatter link is registered for it; readers check the folder.

## Checks

- Every feature's `screens:` entries and every screen's `implements:` entries resolve to each other.
- A feature's `story_refs` name journey ids that exist in `_concept/04_journeys/stories.yaml`.
- A feature's `data_entities` names models that exist in `model.json`, and a model no feature lists is an entity nobody asked for or a feature nobody wrote down.
