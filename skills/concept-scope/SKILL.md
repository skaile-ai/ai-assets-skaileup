---
name: concept-scope
description: "Use when a project has no _concept/01_meta/scope.yaml yet, or the recorded sizing is wrong. Records the flow the project is sized by and resolves its project type. Triggers on 'new project', 'scope this', 'how big is this', 're-scope'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    produces:
      - { id: scope, path: "_concept/01_meta/scope.yaml" }
      - { id: concept-readme, path: "_concept/README.md" }
  prerequisites:
    inputs_optional:
      - { id: project_description, label: "What are you building?", type: textarea, hint: "One or two sentences — the signals below can be inferred from it" }
      - { id: project_type, label: "Project type", type: select, options: [web-app, cli-tool, api-service, library, mobile-app, data-pipeline] }
---

# concept-scope

Writes `_concept/01_meta/scope.yaml`, the first file a project grows: the **flow** the project is sized by and its **project type**, with the evidence behind both. It also leaves the pointer that sends later readers to the instruction tree. It sizes and stops — every artifact after this is some other skill's.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Record the sizing** — `tree/01_meta/scope.md`. Its `## Writing it` is the whole procedure; its `## Project types` table resolves `project_type`; the record is validated against `tree/01_meta/scope.schema.json` before it is written.
2. **Leave the pointer** — `tree/README.md § _concept/README.md`. Write that fixed text to `_concept/README.md` once the scope file is on disk.

**Done when** `_concept/01_meta/scope.yaml` exists, its `flow` is one of the four, its `project_type` is a row of the `## Project types` table, the user has seen the reasoning, and `_concept/README.md` holds the pointer.
