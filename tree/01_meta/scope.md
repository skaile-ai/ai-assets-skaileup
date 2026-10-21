---
path: _concept/01_meta/scope.yaml
summary: flow, project type and depth — written when the first skill needs one
owner: [skaileup]
may_propose: [architecture-techstack, concept-brief, concept-glossary, concept-onboard, concept-research, experience-interaction, quality-test, spec-feature]
---

# _concept/01_meta/scope.yaml

The project's recorded sizing, grown one key at a time: a key is written when the first skill that needs it finds it absent and asks. It holds the **flow** (the advisory recipe the project started from), its **project type**, its **depth** and, where it differs from the default, where the project's **glossary** words live, with the evidence behind them. A wrong value mis-sizes every artifact that reads it; an absent one blocks nothing.

## Format

```yaml
flow: skaileup-greenfield
project_type: web-app
depth: standard
glossary: CONTEXT.md        # only to override the default; absent reads as in the table
reasoning: |
  Nine user-facing capabilities with two roles sharing state and one relational
  schema — standard depth rather than sketch on both counts.
signals:
  features_estimate: 9
  multi_user: true
  persistence: structured
  integrations: [stripe]
  existing_repo: false
proposed:
  - { key: depth, value: sketch, proposed_by: concept-research, proposed_on: "2026-10-21", source: "user: 'a quick pass is enough'" }
chosen_at: "2026-09-05T14:22:00Z"
```

`tree/01_meta/scope.schema.json` is the machine-readable form: the top level is closed to the keys above, none is required, and an absent key reads as its default in the table. Nothing else belongs in the file: it records what was decided, and a file that also named the skill that wrote it would be naming its own caller. `chosen_at` is ISO-8601 UTC, written with every change.

| key | values | absent reads as |
|---|---|---|
| `flow` | `skaileup-greenfield` · `skaileup-reverse` | no recipe chosen; nothing waits on it |
| `project_type` | the rows of `## Project types` | `web-app` |
| `depth` | `sketch` · `standard` · `exhaustive` | `standard` |
| `glossary` | a project-relative path (no leading `/`, no `..`) · `concept` | `CONTEXT.md` when the project root has one, else `concept` |

`flow` names the recipe in `flows/`, which orders skills and sizes nothing. `depth` is the project-wide default for how far each artifact goes — `sketch` the thinnest version that still lets the next artifact be written, `standard` the version a team can build from, `exhaustive` every case and consequence stated; a skill states in its node what each level changes, and may ask a deeper or shallower one for a single artifact (`tree/README.md § How a skill runs`, rule 3). `glossary` names the project glossary — the file outside `_concept/` that holds the definitions — or `concept` for every word in `_concept/glossary.md`; every skill resolves it the same way (`tree/glossary.md § Where the words live`).

## Project types

`project_type` is one of `web-app`, `cli-tool`, `api-service`, `library`, `mobile-app`, `data-pipeline`; unset reads as `web-app`, and `architecture-techstack` and `build-scaffold` both branch on it. The right-hand column lists what a project of that type never grows — artifact ids, skill names or domains. A skill that finds one of those missing has found a project shaped this way, not a gap to report.

| project_type | never grows |
|---|---|
| web-app | — |
| mobile-app | mockup-storybook |
| library | journeys, screens, brand-identity, brand-tokens, behaviors, datamodel, build-database, mockup, mockup-storybook, app-design, interaction-review |
| cli-tool | journeys, screens, brand-identity, brand-tokens, behaviors, mockup, mockup-storybook, app-design, interaction-review |
| data-pipeline | journeys, screens, brand-identity, brand-tokens, behaviors, mockup, mockup-storybook, app-design, interaction-review |
| api-service | journeys, screens, brand-identity, brand-tokens, behaviors, mockup, mockup-storybook, app-design, interaction-review |

A `hard` prerequisite on anything listed here would block a project that was never going to have it, so such a gate is `soft` and the step that reads it says what the skill does without the file.

## Asking a missing key

A skill that needs `project_type` or `depth`, finds the key absent and asks it in its own batch, appends one `proposed` entry — `key`, `value`, `proposed_by`, `proposed_on`, `source` — and works with that value at once. While the key is absent, the latest proposed entry for it (greatest `proposed_on`, the later list position breaking a tie) is its value. `skaileup` confirms an entry by writing the key and dropping the entry, or rejects it and records the rejection in `_concept/10_blueprint/decisions.md`. `glossary` is asked by `concept-glossary` alone, and only when the key is absent, the project root has no `CONTEXT.md` and holds a `CONTEXT-MAP.md` — a map names several contexts and does not say which one this `_concept/` describes; every other absence reads as the default and asks nothing.

## Routing a want

The router's answer is a table: the want, the skill that produces it, and each input of that skill with its status.

| status | holds when | what the producer does |
|---|---|---|
| `present` | the file exists in `_concept/` or at the project root | reads it; where the code has moved on, the file wins and the difference is a question for the user |
| `derivable` | a findings file in `_concept/02_grounding/findings/` covers it, or the code holds it | reads the findings; where none covers the paths, runs `concept-reverse` for one scope and the paths of the want; a findings file whose `source_sha` differs from git HEAD is stale for those paths |
| `ask` | neither settles it | batch-asks it, per `tree/README.md § How a skill runs` |

A want is an artifact (a path or its name), a screen or feature by name, or a question about the project. Find its path in `tree/README.md § The tree`; the `owner` of that node is the producer, except a screen, whose producer is `experience-screen`, and a feature, whose producer is `spec-feature`. A question about an existing artifact is answered from that artifact, and the router names a producer only when the artifact is absent. Work arriving from outside the collection — a request, a bug report, a feature ask — is triaged first (the user runs `/triage`; without it, say the item was not triaged and go on) and then enters at one skill: `spec-feature` when the product's capability is new or changes, `build-plan` when the spec was right and the code is not.

The inputs of a producer are its `metadata.prerequisites.files` and `metadata.artifacts.requires`; the router reads both and never a skill body. The router names the inputs and stops: the producer resolves them.

**Worked example.** "Describe the inbox already built in this repo" — no `_concept/`, no brief, no scope.

| | |
|---|---|
| want | the screen `inbox` → producer `experience-screen` |
| `findings/screens.md` | `derivable` — `concept-reverse` scope `screens`, paths `app/pages/inbox*` |
| glossary terms of the inbox | `ask` — answered in the batch and filed as `proposed` glossary entries |
| `APP-DESIGN.md` | absent — the floorplan is chosen from the rulebook defaults and appended as a proposed `§ Screen defaults` row in a stub `APP-DESIGN.md` holding only proposed entries (`tree/APP-DESIGN.md § Format`) |
| `scope.yaml` | `depth` is the only key the screen needs and it is absent → one question in the same batch; `flow` and `project_type` stay unasked |

Next step: `experience-screen`, one batch (floorplan confirmation, posture, tier-3 exceptions), `07_screens/inbox.md` written. No brief, feature or flow was needed.

## Writing it

1. **Read what exists.** `scope.yaml` if present — its keys are the defaults for every question below, so the user corrects a sizing rather than restating one; its `proposed` entries; and `_concept/02_grounding/onboarding/answers.json` plus the host's onboarding profile, which may already have chosen the `flow`.
2. **Derive what the repository settles.** A repository with code and no `_concept/` is `existing_repo: true` and a `skaileup-reverse` project; `project_type` follows from the manifests (`_concept/02_grounding/findings/stack.md`, or `concept-reverse` for scope `stack`). Mark each derived value as inferred.
3. **Ask only the keys the want needs.** Batch-ask them with the other questions of the producer's first batch (`tree/README.md § How a skill runs`, rule 2), each with a recommendation and the consequence of each answer; a user who named neither depth nor a size gets `depth` with what each level produces. The signals behind a recommendation — how many distinct things a user can do, whether more than one role shares state, how data is persisted, which external services are named, whether a repository exists — are asked only when the recommendation needs them, and recorded as the user gave them.
4. **Settle the `proposed` entries.** Confirm, reject or amend each with the user; a confirmed entry becomes the key.
5. **Show the decision, then validate and write.** Present the keys written, the signals literally and two to six sentences of reasoning. Show the diff against the loaded file before overwriting a confirmed key: a silent re-size changes the depth of every skill still to run and leaves the artifacts already written at the old one. Validate against `tree/01_meta/scope.schema.json`, then write.

## Checks

- The record validates against `tree/01_meta/scope.schema.json`: `flow` and `depth` are values of the table above, `project_type` is a row of `## Project types`, and `chosen_at` is ISO-8601 UTC.
- Every `proposed` entry names a key the file does not already hold confirmed.
- No key was asked that the want did not need.
