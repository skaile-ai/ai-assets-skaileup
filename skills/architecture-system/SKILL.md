---
name: architecture-system
description: "Use when the stack is chosen and the features need more than the stack ships with — records the custom modules, protocols and external integrations this project adds, and stops there. Triggers on 'architecture', 'system design', 'do we need a websocket', 'which modules', 'how does this talk to Stripe'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brief }
      - { id: features }
      - { id: techstack }
      - { id: behaviors }
      - { id: datamodel }
      - { id: grounding-findings }
    produces:
      - { id: architecture, path: "_concept/10_blueprint/architecture.md" }
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: soft }
      - { path: "_concept/05_features", gate: soft, min_entries: 1 }
      - { path: "_concept/10_blueprint/techstack.md", gate: soft }
      - { path: "_concept/06_behaviors", gate: soft, min_entries: 1 }
      - { path: "_concept/10_blueprint/datamodel", gate: soft }
      - { path: "_concept/02_grounding/findings", gate: soft }
---

# architecture-system

Writes `10_blueprint/architecture.md` as C4 levels — what this project adds beyond its template, and nothing the stack already ships — plus the API and event contracts where the project has them. A project whose features need nothing extra gets a short document saying so — that is the answer `build-plan` needs.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Resolve the stack and the features for the delta** — `tree/10_blueprint/architecture.md § Writing it`, steps 1–3. Derive-or-ask per `tree/README.md § How a skill runs`: a stack or a feature the files lack comes from `concept-reverse` scoped `stack`, `routes` or `datamodel`, and the rest goes into the step 3 batch.
2. **Screen and shape each addition** — `tree/10_blueprint/architecture.md § Design red flags`, then steps 4–5 of its `## Writing it` (seams for outside dependencies).
3. **Write `architecture.md` by C4 level** — `tree/10_blueprint/architecture.md § Format` (system context with every external integration, containers, components, deployment, risks and technical debt), then step 6 of its `## Writing it`.
4. **Write the API and event contracts where the project has them** — `tree/10_blueprint/openapi.md` for an HTTP API served to clients other than the own UI (always for `api-service`), `tree/10_blueprint/asyncapi.md` for published or consumed messages, per step 7 of `tree/10_blueprint/architecture.md § Writing it`. A project with neither writes neither file and says so in `architecture.md`.
5. **Approve all of it together** — step 8 of `tree/10_blueprint/architecture.md § Writing it`. A change to an endpoint, channel or payload that a reader names re-runs steps 3–5 for the affected parts per `tree/10_blueprint/architecture.md § Changing a contract`.

**Done when** `_concept/10_blueprint/architecture.md` exists, every entry in its frontmatter lists is described in the body with its dependencies and error behaviour, `openapi.yaml` and `asyncapi.yaml` exist exactly where step 4 says they are due, and the user approved them all together.
