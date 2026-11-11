---
name: quality-release
description: "Use as the last gate before a release — walks the whole running application against the brief and goals it started from and grades it on seven axes, then writes the release verdict. Triggers on 'is this ready to release', 'grade the app', 'final gate', 'release review'."
version: "0.2.0"
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
      - { id: review }
      - { id: grounding-findings }
      - { id: features }
    produces:
      - { id: release-verdict, path: "_concept/11_build/release.yaml" }
  prerequisites:
    files:
      # Hard: each feature spec's `tracker.issue` names the parent issue whose tickets and pull requests the
      # refusal in step 1 checks completeness against with `gh`; without a spec there is nothing to release.
      - { path: "_concept/05_features", gate: hard, min_entries: 1 }
      - { path: "_concept/brief.md", gate: soft }
      - { path: "_concept/goals.md", gate: soft }
      - { path: "_concept/03_brand/brand.tokens.json", gate: soft }
      - { path: "_concept/04_journeys/stories.yaml", gate: soft }
      - { path: "_concept/11_build/acceptance-criteria", gate: soft }
      - { path: "_concept/11_build/reviews", gate: soft }
      - { path: "_concept/02_grounding/findings", gate: soft }
---

# quality-release

The last gate: whether the thing that exists is the thing the project set out to build. It is
the only skill that reads `brief.md` and `goals.md` against the running application, grades it
on seven axes and refuses; it never edits code.

## Route

Read `tree/protocol/running.md` (the todo list, rules 1, 2 and 8) once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Take the evaluator's stance** — `tree/11_build/README.md § Verdicts`. Walk the app as a user and do not read what it was supposed to do.
2. **Refuse on an unbuilt spec or an incomplete ledger, extract the intent, walk the product, score, write the verdict** — `tree/11_build/release.md`. The thresholds, rubrics and verdict table are in the same node.

**Done when** `11_build/release.yaml` is on disk, every goal in it carries evidence from the running app, every design score cites the elements behind it, and the verdict follows the release thresholds rather than an impression of the app.
