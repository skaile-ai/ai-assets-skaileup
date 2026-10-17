---
name: quality-review
description: "Use when a feature's slices are frozen and its code needs an adversarial review before it ships — resolves the fixed point from the trace and the spec from the feature file, runs `code-review`, and adds the security, accessibility and acceptance-criteria axes. Triggers on 'review this feature', 'code review the login feature', 'is this ready to ship'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: features }
      - { id: slice-plan }
      - { id: acceptance-criteria }
    produces:
      - { id: review, path: "_concept/11_build/reviews/<feature_slug>.yaml" }
      - { id: acceptance-criteria, path: "_concept/11_build/acceptance-criteria/<featureset>/<feature_slug>.ac.md" }
  prerequisites:
    files:
      - { path: "_concept/05_features", gate: hard, min_entries: 1 }
      - { path: "_concept/11_build/slices", gate: hard, min_entries: 1 }
      - { path: "_concept/11_build/trace.yaml", gate: hard }
      - { path: "_concept/11_build/acceptance-criteria", gate: soft }
---

# quality-review

Reviews one feature's shipped code. It is the one place in the collection that judges the
built feature against its spec; `build-implement`, `ops-review` and `quality-release` do not
repeat that verdict. The global `code-review` skill reads the diff; this skill supplies what
it otherwise asks a human for, plus the security, accessibility and criteria axes.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Take the evaluator's stance** — `tree/11_build/README.md § Verdicts`. The verdict file and the re-checked ledger rows are the only things this skill writes.
2. **Resolve the trace row, build, run `code-review`, add the security and accessibility axes** — `tree/11_build/reviews/README.md § Writing it` (steps 1–4). Call the Skill tool with "code-review" from a context that did not write the code, and call the Skill tool with "diagnosing-bugs" on a red build; where either is not installed the node names the fallback.
3. **Re-check the ledger rows marked `PASS` against the running app** — `tree/11_build/acceptance-criteria/README.md § Reading`.
4. **Read the accepted debt, write the verdict, report by axis** — `tree/11_build/reviews/README.md § Writing it` (steps 6–8). On `changes-requested`, call the Skill tool with "diagnosing-bugs" against the findings.

**Done when** `11_build/reviews/<feature_slug>.yaml` is on disk, every finding in it carries a file, a line and a resolution, and the verdict is `approved` only where no finding is `critical` or `high`.
