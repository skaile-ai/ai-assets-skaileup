---
name: skaileup
description: "Use when the user names something they want — an artifact, a screen, a question, a request — and the skill that produces it or what it needs is unclear, when a project has no recorded scope or expectations, or to walk the concept top-down (frame → look → data → features) before anything is built. Triggers on 'which skill', 'where do I start', 'how do we work together', 'walk me through the app', 'what is decided', 'continue the concept', 'describe this screen', 'I have a bug report', 'a feature was requested'."
version: "0.5.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
    - skill:@mattpocock/setup-matt-pocock-skills#0.1.0
  artifacts:
    produces:
      - { id: expectations, path: "_concept/01_meta/expectations.md" }
      - { id: scope, path: "_concept/01_meta/scope.yaml" }
      - { id: walkthrough, path: "_concept/01_meta/walkthrough.yaml" }
      - { id: concept-readme, path: "_concept/README.md" }
      - { id: adr, path: "docs/adr/<NNNN>-<slug>.md" }
      - { id: agent-guidance, path: "docs/agents/domain.md" }
  prerequisites:
    inputs_optional:
      - { id: want, label: "What do you want?", type: textarea, hint: "An artifact, a screen, a question or a request — in your own words" }
---

# skaileup

The collection's front door and guide: it walks the user top-down through the concept — frame, look, data, features — and holds the user's yes on each stage, takes what the user wants, names the skill that produces it and each input of that skill as present, derivable or to ask, and records `flow`, `project_type` and `depth` only when something needs one. It writes `_concept/01_meta/expectations.md`, `_concept/01_meta/scope.yaml`, `_concept/01_meta/walkthrough.yaml` (through its script), the marked walkthrough section of the project's agent file, the `_concept/README.md` pointer, the `## skaileup artifacts` section of `docs/agents/domain.md` with its `### Concept (skaileup)` sub-block, and the decision records in `docs/adr/` — the one of a waived stage, and every one another skill proposed, which it numbers and writes (`tree/docs/adr/README.md`) — and nothing else; the producer does the work, because a guide that also did it would define a skill's job twice.

## Route

Read `tree/protocol/running.md`, `tree/protocol/ownership.md` and `tree/protocol/delegation.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order. `<skill-dir>` is this skill's directory.

1. **Settle the expectations** — `tree/01_meta/expectations.md § Writing it`. When the file is missing, its two batches come before the first producer runs; when it exists, apply `## Working together` per `tree/01_meta/expectations.md § Reading it`.
2. **Open the walk** — `tree/01_meta/walkthrough.md § Writing it`. Run `python3 <skill-dir>/scripts/walkthrough.py init`, then `guard --write`, then `status`, and show the status table to the user.
3. **Take the want** — `tree/01_meta/scope.md § Routing a want`. Restate it as an artifact, a screen or feature, a question or outside work (request, bug report); the node says how each is routed. A want that changes an approved stage runs `walkthrough.py reopen <stage> --reason "<the user's words>"` first; a build want while `walkthrough.py gate build` fails continues the walk instead, and the reply names the stage that blocks.
4. **Walk the open stage** — `tree/01_meta/walkthrough.md § Format` and `tree/01_meta/scope.md § Routing a want`. `walkthrough.py next` names the producer; mark each input from its `metadata.prerequisites.files` and `metadata.artifacts.requires` as `present`, `derivable` (name the `concept-reverse` scope and paths) or `ask`, fold the absent `flow`, `project_type` or `depth` the want needs into its first batch, and run it as lead or through a delegate (`tree/protocol/delegation.md § Delegation`), relaying every decision batch to the user unchanged.
5. **Show the checkpoint** — the stage's row in `tree/01_meta/walkthrough.md § Format`, and `tree/09_mockup/storybook/README.md § Writing it` for look, data and features. For `frame` show the completion summary; for the other three run `mockup-storybook` for the stage's layer and give the user the Storybook URL. Add a one-screen summary of what the stage decided, and ask "approve <stage> / change … / waive (needs a decision record)" as one decision batch.
6. **Record the yes** — `tree/01_meta/walkthrough.md § Writing it`. Only on the user's own yes run `walkthrough.py approve <stage> --source "user, <date>"`. On a waive, first write the decision record to `docs/adr/<NNNN>-<slug>.md` (`tree/docs/adr/README.md § Format`, level `product`, the user's reason verbatim), then run `walkthrough.py waive <stage> --adr adr:<slug> --source "user, <date>"`.
7. **Promote the proposed decision records** — `tree/docs/adr/README.md § Writing it`, *Promoting*: every pending entry targeting `docs/adr/` gets the next number and its file; only one that contradicts a higher-level record goes to the user, in one batch.
8. **Record the keys, settle proposals, leave the pointer, name the next step** — `tree/01_meta/scope.md § Format` and `§ Writing it` step 4 with `tree/proposals/README.md § Writing it` for the pending `key:` entries targeting `scope.yaml`, `tree/README.md § _concept/README.md`, `tree/protocol/running.md § How a skill runs`. Validate against `tree/01_meta/scope.schema.json` and write only keys the user answered or the repository settled; write the pointer once, with the first file created under `_concept/`; the next step is what `walkthrough.py next` prints, with the sentence that chose it.
9. **Point the upstream skills at the concept** — `tree/docs/agents/domain.md § Writing it`. When the next step is a `build-*`, `quality-review` or `quality-test` skill and `docs/agents/domain.md` has no `## skaileup artifacts` section, Read the installed `setup-matt-pocock-skills` skill and follow it, with its recommended answers (the user is asked only where `expectations.md` says so), then write the section and the sub-block; a run that changed which artifacts exist rewrites the section.

**Done when** the user has seen the walk's status, the current stage's checkpoint was shown, `walkthrough.yaml` holds only yeses and waives the user gave, no pending proposal entry targets `docs/adr/` except one waiting on the user, `expectations.md` holds the user's answers or the defaults they accepted, `scope.yaml` holds exactly the keys that were asked or derived, and before a build-side step `docs/agents/domain.md § skaileup artifacts` names exactly the artifacts on disk.
