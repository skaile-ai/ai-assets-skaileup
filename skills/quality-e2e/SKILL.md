---
name: quality-e2e
description: "Use when the app runs and its journeys need proving end to end in a real browser — drives every story from stories.yaml with agent-browser, screenshots each step, checks the database behind it, and writes each journey's verdict into the acceptance-criteria ledger. Triggers on 'test the app', 'e2e tests', 'browser testing', 'walk the journeys'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: journeys }
      - { id: features }
      - { id: screens }
      - { id: datamodel }
    produces:
      - { id: acceptance-criteria, path: "_concept/11_build/acceptance-criteria/<featureset>/<feature_slug>.ac.md" }
  prerequisites:
    files:
      - { path: "_concept/04_journeys/stories.yaml", gate: soft }
      - { path: "_concept/05_features", gate: hard, min_entries: 1 }
      - { path: "_concept/07_screens", gate: soft, min_entries: 1 }
      - { path: "_concept/10_blueprint/datamodel", gate: soft }
      - { path: "_concept/10_blueprint/openapi.yaml", gate: soft }
---

# quality-e2e

Drives the running application through every story in `04_journeys/stories.yaml`, one
journey per story, and reports what a user can and cannot actually do. Where `quality-test`
asserts against units, this asserts against the product: a journey's pass condition is its own
criterion ids, observed in the browser with `agent-browser`.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Walk every journey and write its verdict into the ledger** — `tree/11_build/acceptance-criteria/README.md § Flipping rows`, the `quality-e2e` procedure (steps 1–8; step 2 covers an `api-service` with no UI journeys). A feature with no ledger stops the run and names `build-plan`.

**Done when** every story in `stories.yaml` (or, without journeys, every derived path or documented operation) has been run with a pass or a fail and a criterion id behind it, the ledger rows this run evaluated carry that verdict and its evidence, and no dev server or browser session is left alive.
