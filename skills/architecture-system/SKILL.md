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
    produces:
      - { id: architecture, path: "_concept/10_blueprint/architecture.md" }
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: hard }
      - { path: "_concept/05_features", gate: hard, min_entries: 1 }
      - { path: "_concept/10_blueprint/techstack.md", gate: hard }
      - { path: "_concept/06_behaviors", gate: soft, min_entries: 1 }
---

# architecture-system

Writes `10_blueprint/architecture.md`: what this project adds beyond its template, and nothing the stack already ships. A project whose features need nothing extra gets a short document saying so — that is the answer `build-plan` needs.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Read the stack and the features for the delta** — `tree/10_blueprint/architecture.md § Writing it`, steps 1–3.
2. **Screen and shape each addition** — `tree/10_blueprint/architecture.md § Design red flags`, then steps 4–5 of its `## Writing it` (seams for outside dependencies).
3. **Write and approve** — `tree/10_blueprint/architecture.md § Format`, then steps 6–7 of its `## Writing it`.

**Done when** `_concept/10_blueprint/architecture.md` exists, every entry in its frontmatter lists is described in the body with its dependencies and error behaviour, and the user approved it.
