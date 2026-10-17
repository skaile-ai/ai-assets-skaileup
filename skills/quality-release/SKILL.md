---
name: quality-release
description: "Use as the last gate before a release — walks the whole running application against the brief and goals it started from and grades it on seven axes, then writes the release verdict. Triggers on 'is this ready to release', 'grade the app', 'final gate', 'release review'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brief }
      - { id: goals }
      - { id: journeys }
      - { id: brand-tokens }
      - { id: acceptance-criteria }
      - { id: trace }
    produces:
      - { id: release-verdict, path: "_concept/11_build/release.yaml" }
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: hard }
      - { path: "_concept/11_build/trace.yaml", gate: hard }
      - { path: "_concept/goals.md", gate: soft }
      - { path: "_concept/03_brand/tokens.json", gate: soft }
---

# quality-release

The last gate: whether the thing that exists is the thing the project set out to build. It is
the only skill that reads `brief.md` and `goals.md` against the running application, grades it
on seven axes and refuses; it never edits code.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Take the evaluator's stance** — `tree/11_build/README.md § Verdicts`. Walk the app as a user and do not read what it was supposed to do.
2. **Refuse on an incomplete trace or ledger, extract the intent, walk the product, score, write the verdict** — `tree/11_build/release.md`. The thresholds, rubrics and verdict table are in the same node.

**Done when** `11_build/release.yaml` is on disk, every goal in it carries evidence from the running app, every design score cites the elements behind it, and the verdict follows the release thresholds rather than an impression of the app.
