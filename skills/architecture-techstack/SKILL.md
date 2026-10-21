---
name: architecture-techstack
description: "Use when a project has no technology decided — scans the stack templates on disk, asks what the project actually constrains, and records the winner as the one id every later skill resolves. Triggers on 'tech stack', 'what should we build this with', 'pick a framework', 'which template'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brief }
      - { id: scope }
      - { id: features }
      - { id: grounding-findings }
    produces:
      - { id: techstack, path: "_concept/10_blueprint/techstack.md" }
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: soft }
      - { path: "_concept/01_meta/scope.yaml", gate: soft }
      - { path: "_concept/05_features", gate: soft, min_entries: 1 }
      - { path: "_concept/02_grounding/findings", gate: soft }
    inputs_optional:
      - { id: framework_experience, label: "Framework experience", type: text, hint: "React, Vue, Svelte — or starting fresh?" }
      - { id: hosting, label: "Hosting", type: select, options: [self-hosted, managed] }
---

# architecture-techstack

Chooses the project's technology and resolves it to exactly one template in one pass, under one approval. It stops at `techstack.md`: third-party services are `architecture-system`'s, schemas are `architecture-datamodel`'s.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Resolve the facts, then choose the stack and its template** — `tree/10_blueprint/techstack.md § Writing it`, steps 1–7, derive-or-ask per `tree/README.md § How a skill runs`: the brief, the features and a repository's own stack (`concept-reverse` scoped `stack`) answer first; a `project_type` or `depth` that `scope.yaml` lacks is asked in the step 3 batch (`tree/01_meta/scope.md`). Read `templates/README.md` before scoring: it defines the template set, its atoms and its section headings.
2. **Check the id, then write the file** — `tree/10_blueprint/techstack.md § Format`, then step 8 of its `## Writing it`.

**Done when** `_concept/10_blueprint/techstack.md` exists, its `tech_stack_skill` names a real `templates/` directory or `custom`, and the user approved that one id.
