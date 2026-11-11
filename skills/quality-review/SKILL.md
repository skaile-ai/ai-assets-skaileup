---
name: quality-review
description: "Use when a feature's spec is built and its code needs an adversarial review before it ships — resolves the spec and its parent issue, takes the fixed point from the integration branch `spec/<featureset>-<feature>`, runs `code-review`, adds the security, accessibility and acceptance-criteria axes, and flips the ledger rows whose ticket is closed. Triggers on 'review this feature', 'code review the login feature', 'is this ready to ship'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
    - skill:@mattpocock/code-review#0.1.0
    - skill:@mattpocock/diagnosing-bugs#0.1.0
  artifacts:
    requires:
      - { id: features }
      - { id: acceptance-criteria }
    produces:
      - { id: review, path: "_concept/11_build/reviews/<feature_slug>.yaml" }
      - { id: acceptance-criteria, path: "_concept/11_build/acceptance-criteria/<featureset>/<feature_slug>.ac.md" }
  prerequisites:
    files:
      - { path: "_concept/05_features", gate: soft, min_entries: 1 }
      - { path: "_concept/11_build/acceptance-criteria", gate: soft }
---

# quality-review

Reviews one feature's shipped code. It is the one place in the collection that judges the
built feature against its spec; `build-implement`, `ops-review` and `quality-release` do not
repeat that verdict. The global `code-review` skill reads the diff; this skill supplies what
it otherwise asks a human for, plus the security, accessibility and criteria axes.

## Route

Read `tree/protocol/running.md` (the todo list, rules 1, 2 and 8) once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Take the evaluator's stance** — `tree/11_build/README.md § Verdicts`. The verdict file and the flipped ledger rows are the only things this skill writes.
2. **Resolve the spec, its parent issue and the fixed point** (`git merge-base origin/main spec/<featureset>-<feature>`, else the parent issue's PR base, else ask) — `tree/11_build/reviews/README.md § Writing it` (step 1).
3. **Build, call the Skill tool with "code-review", add the security and accessibility axes** — `tree/11_build/reviews/README.md § Writing it` (steps 2–4). Hand `code-review` the fixed point and the spec (feature file path plus the parent issue and its sub-issues), from a context that did not write the code; call the Skill tool with "diagnosing-bugs" on a red build. Where either is not installed the node names the fallback.
4. **Add the acceptance-criteria axis: flip every ledger row whose ticket is closed against the running app** — `tree/11_build/acceptance-criteria/README.md § Flipping rows (quality-review)`.
5. **Write the verdict, report by axis** — `tree/11_build/reviews/README.md § Writing it` (steps 6–7). On `changes-requested`, call the Skill tool with "diagnosing-bugs" against the findings.

**Done when** `11_build/reviews/<feature_slug>.yaml` is on disk with its `fixed_point`, `branch` and `parent_issue`, every finding in it carries a file, a line and a resolution, every ledger row whose ticket is closed carries this run's verdict or is named as not exercised, and the verdict is `approved` only where no finding is `critical` or `high`.
