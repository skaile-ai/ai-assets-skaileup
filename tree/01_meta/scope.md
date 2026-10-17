---
path: _concept/01_meta/scope.yaml
summary: flow and project type — the sizing every skill reads its depth from
writers: [concept-scope]
---

# _concept/01_meta/scope.yaml

The first file a project grows and the one eleven skills read to decide how deep to go; it is the entry of every flow (`skaileup-concept-reverse` included, where `concept-reverse` runs right after it). It records two values and the evidence behind them: the **flow** the project is sized by and its **project type**. A wrong value here mis-sizes every artifact after it.

## Format

```yaml
flow: appbuilder-standard
project_type: web-app
reasoning: |
  Nine user-facing capabilities with two roles sharing state, one relational
  schema, and no external store — standard rather than mvp on both counts.
signals:
  features_estimate: 9
  multi_user: true
  persistence: structured
  integrations: [stripe]
  existing_repo: false
chosen_at: "2026-09-05T14:22:00Z"
```

`chosen_at` is ISO-8601 UTC. `tree/01_meta/scope.schema.json` is the machine-readable form: the top level is closed to `flow`, `project_type`, `reasoning`, `signals` and `chosen_at` (`flow`, `project_type` and `chosen_at` required). Nothing else belongs in the file: it records what was decided, and a file that also named the flow that wrote it would be naming its own caller.

A flow *is* the sizing, so the project is sized by the flow it runs under. The four names are the whole vocabulary — a fifth value is a flow that will not load:

| flow | fits |
|---|---|
| `appbuilder-mvp` | one capability, single user, no data layer to design |
| `appbuilder-standard` | anything else that gets built |
| `skaileup-concept-only` | the design is the deliverable; no code follows |
| `skaileup-concept-reverse` | a repository already exists and the concept is extracted from it; `concept-reverse` runs right after `concept-scope` |

## Project types

`project_type` is one of `web-app`, `cli-tool`, `api-service`, `library`, `mobile-app`, `data-pipeline`; unset reads as `web-app`, and `architecture-techstack` and `build-scaffold` both branch on it. The right-hand column lists what a project of that type never grows — artifact ids, skill names or domains. A skill that finds one of those missing has found a project shaped this way, not a gap to report.

| project_type | never grows |
|---|---|
| web-app | — |
| mobile-app | mockup-storybook |
| library | journeys, screens, brand-identity, brand-tokens, behaviors, datamodel, mockup, mockup-storybook, app-design, interaction-review |
| cli-tool | journeys, screens, brand-identity, brand-tokens, behaviors, mockup, mockup-storybook, app-design, interaction-review |
| data-pipeline | journeys, screens, brand-identity, brand-tokens, behaviors, mockup, mockup-storybook, app-design, interaction-review |
| api-service | journeys, screens, brand-identity, brand-tokens, behaviors, mockup, mockup-storybook, app-design, interaction-review |

A `hard` prerequisite on anything listed here would block a project that was never going to have it, so such a gate is `soft` and the step that reads it says what the skill does without the file.

## Writing it

1. **Check for an existing scope.** `scope.yaml` present means a re-scope: load it and use its values as the defaults for every question below, so the user corrects a sizing rather than restating one. Its `chosen_at` is the honest answer to "has anything changed since".
2. **Collect the signals**, each question as its own message. Ask for: how many distinct things a user can do; whether more than one role shares state; how data is persisted (none, one relational schema, or an external store the project does not own); which external services are named; whether a repository already exists. Take what the description or the input dialog already answered and ask only for the rest. Record each answer as the user gave it — the reasoning quotes these numbers, and a normalised signal makes a re-scope argue with a sizing nobody can reconstruct.
3. **Resolve the project type** against the table above. When the description settles it, confirm rather than ask.
4. **Record the flow, deriving it only when nothing else has.** On a host that started the run from an onboarding profile the flow is already chosen and this step writes down which one. Where nothing has chosen, put the four flows to the user with your recommendation from the signals.
5. **Show the decision, then validate and write.** Present flow, project type, the signals literally, and two to six sentences of reasoning naming which signals decided it. On a re-scope show the diff against the loaded file and get a yes to overwriting: a silent re-size changes the depth of every skill still to run and leaves the artifacts already written at the old one. Validate the record against `tree/01_meta/scope.schema.json`, then write the file.

## Checks

- The record validates against `tree/01_meta/scope.schema.json`: `flow` is one of the four names, `project_type` is a row of the table above, and `chosen_at` is ISO-8601 UTC.
- The user has seen the reasoning.
