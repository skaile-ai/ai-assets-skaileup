---
name: skaileup
description: "Use when the user names something they want — an artifact, a screen, a question, a request — and the skill that produces it or what it needs is unclear, or a project has no recorded scope. Triggers on 'which skill', 'where do I start', 'describe this screen', 'I have a bug report', 'a feature was requested'."
version: "0.2.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    produces:
      - { id: scope, path: "_concept/01_meta/scope.yaml" }
      - { id: concept-readme, path: "_concept/README.md" }
  prerequisites:
    inputs_optional:
      - { id: want, label: "What do you want?", type: textarea, hint: "An artifact, a screen, a question or a request — in your own words" }
---

# skaileup

The collection's front door, demand-driven: it takes what the user wants, names the skill that produces it and each input of that skill as present, derivable or to ask, and records `flow`, `project_type` and `depth` only when something needs one. It writes `_concept/01_meta/scope.yaml` and the `_concept/README.md` pointer and nothing else; the producer does the work, because a router that also did it would define a skill's job twice.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Take the want** — `tree/01_meta/scope.md § Routing a want`. Restate it as an artifact, a screen or feature, a question or outside work (request, bug report); the node says how each is routed, so a bug and a changed capability do not enter at the same skill.
2. **Find the producer** — `tree/README.md § The tree`. Resolve the wanted path to its node and read the node's `owner`; a skill the node does not name is never guessed.
3. **Mark each input** — `tree/01_meta/scope.md § Routing a want`. Read the producer's `metadata.prerequisites.files` and `metadata.artifacts.requires` — not its body — and mark each input `present`, `derivable` (name the `concept-reverse` scope and paths) or `ask`; the producer resolves them, so none is a stop.
4. **Ask only what the want needs** — `tree/01_meta/scope.md § Writing it`. Fold the absent `flow`, `project_type` or `depth` the want needs into the producer's first batch, and settle `proposed` entries; a key nobody needs stays unasked.
5. **Record the keys** — `tree/01_meta/scope.md § Format`. Validate against `tree/01_meta/scope.schema.json` and write only keys the user answered or the repository settled.
6. **Leave the pointer** — `tree/README.md § _concept/README.md`. Write it once, with the first file created under `_concept/`.
7. **Name the next step** — `tree/README.md § How a skill runs`. Rule 8: the producer first, then the skills that own what is still missing, each with the sentence that chose it.

**Done when** the user has the producing skill, every input with its status and the evidence for it, and `scope.yaml` holds exactly the keys that were asked or derived.
