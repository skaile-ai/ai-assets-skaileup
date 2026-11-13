---
path: [_concept/02_grounding/findings/app-model/]
summary: one ontology of the app from code, docs and the running app, compared
owner: [app-model]
may_propose: []
---

# _concept/02_grounding/findings/app-model/

What `app-model` found when it read the app three ways: from its code, from its docs (this
`_concept/` tree among them) and from the running app (an `app-explore` crawl). Each source
becomes one model in the same format, the three are merged, and every place they disagree is a
row in a mismatch register. It is evidence like the rest of `findings/`: no skill designs from it
without citing it, and nothing in it is a decision.

`app-model` is published outside this collection (`@skaile-ai/app-model`, library
`ai-assets-app-explore`), so `scripts/check.py` admits it as an owner and proposer through
`EXTERNAL_WRITERS`. Its format, `app-model/1`, uses this tree's vocabulary: term ids follow the
*Ids* rule of `tree/glossary.md § Where the words live`, `kind` and the four object axes are the glossary's, screen
representations are `row · card · chip · peek · page`, and featureset and feature ids are the
slugs of `tree/05_features/featuresets.md`.

## Contents

| file | what it holds |
|---|---|
| `app-model.code.yaml`, `app-model.docs.yaml`, `app-model.app.yaml` | one model per source: terms, relations, screens, navigation, tasks, featuresets, features |
| `align.yaml` | the user's or agent's calls on candidate term pairs: `same` or `different` |
| `app-model.merged.yaml` | the merged model; every entry names the sources it was seen in (`seen_in`) |
| `compare.yaml`, `compare.md` | the mismatch register: rule, severity, the value per source, a suggestion (`fix-ui`, `fix-docs`, `decide`) |
| `feature-map.md` | features with their status (`built`, `hidden`, `unbuilt`, `undocumented`, `ui-only`) and what no feature covers |
| `proposals.md` | proposed glossary terms, only when `_concept/01_meta/scope.yaml` names no glossary target |

## Format

The YAML files follow `app-model/1` (the `app-model` skill's `references/format.md` and
`schema/app-model.schema.json`). Every entry carries `evidence` (cited `path:line`, `docs` heading,
crawl state or walk) and a `grade` with the three values of `tree/02_grounding/findings/README.md
§ Format`: in this folder the field is `grade`, not `extraction_confidence`. The markdown files
carry `last_updated` and `source_sha` (`git rev-parse HEAD` of the code the models were read at),
so a reader can tell whether the code has moved since.

## Who reads it

- `concept-glossary` and `concept-brief` settle what `app-model` proposed from it: glossary terms
  with `status: proposed` and `## Ideas` rows in `tree/05_features/featuresets.md`, each with
  `proposed_by: app-model` and a `source` into this folder.
- `experience-app-objects` starts its object list from `app-model.merged.yaml` when its
  `source_sha` is HEAD, and `experience-app-interview` puts the `decide` rows of `compare.yaml` on
  its agenda (both published beside `app-model`).
- `spec-feature` and `experience-screen` may cite `feature-map.md` and `compare.md` as evidence of
  what the running app does today.

## Writing it

`app-model` writes every file here. Outside this folder it writes only its rows in
`tree/02_grounding/findings/index.md` (one per file, `step: app-model`) and its proposals
(`may_propose:` of `tree/glossary.md` and `tree/05_features/featuresets.md`). A re-run rewrites
the files of the sources it read again.

## Checks

- Every YAML file validates against `app-model/1` (`model.py validate`).
- Every file here has a row in `findings/index.md` whose `step` is `app-model`.
- `compare.md` and `feature-map.md` carry `last_updated` and `source_sha`.
