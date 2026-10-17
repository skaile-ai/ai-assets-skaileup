---
name: build-implement
description: "Use when a planned vertical slice is ready to build — implements it test-first, reviews it against its spec, then commits it and freezes its dossier. Triggers on 'build this slice', 'implement the next slice', 'land it'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: slice-plan }
      - { id: acceptance-criteria }
      - { id: features }
      - { id: screens }
      - { id: datamodel }
      - { id: standards }
    produces:
      - { id: slice-index, path: "_concept/11_build/slices/<slice_id>/index.md" }
      - { id: acceptance-criteria, path: "_concept/11_build/acceptance-criteria/<featureset>/<feature_slug>.ac.md" }
      - { id: trace, path: "_concept/11_build/trace.yaml" }
  prerequisites:
    files:
      - { path: "_concept/11_build/slices", gate: hard, min_entries: 1 }
      - { path: "_concept/05_features", gate: hard, min_entries: 1 }
      - { path: "_concept/07_screens", gate: soft, min_entries: 1 }
      - { path: "_concept/02_grounding/standards/index.yml", gate: soft }
      - { path: "_concept/10_blueprint/openapi.yaml", gate: soft }
      - { path: "_concept/10_blueprint/asyncapi.yaml", gate: soft }
---

# build-implement

Builds one vertical slice and lands it. What it knows about the work is `plan.md` and the
artifacts that plan names; what it knows about how to build is `tdd` and `code-review`, which
it calls and does not restate. Both have to be installed: this skill stops and names the
missing one rather than improvising a test loop or a review.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Load the slice, build and review it, run the gate, recap, propose the simplification** — `tree/11_build/slices/[slice_id]/index.md § Writing it` (steps 1–6). Call the Skill tool with "tdd" for each row. Call the Skill tool with "code-review" once the rows are done. Confirm the seams with the user before the first test. A row implementing an operation in `openapi.yaml` or `asyncapi.yaml` matches it, and a contract that is wrong goes back to `architecture-system` (step 2 of that section).
2. **Commit atomically** — `tree/11_build/slices/[slice_id]/index.md § Writing it` (step 7): a user-approved decomposition and an explicit file list per commit.
3. **Record the slice in the trace** — `tree/11_build/trace.md`, validated against `tree/11_build/trace.schema.json` before writing. Written once the last commit has landed.
4. **Flip the ledger rows the gate exercised** — `tree/11_build/acceptance-criteria/README.md § Flipping rows`, stamped with the last commit's short sha.
5. **Freeze the dossier** — `tree/11_build/slices/[slice_id]/index.md § Writing it` (step 8).

**Done when** the slice's commits are on the branch, `index.md` exists beside `plan.md`, and `trace.yaml` carries the slice's entry.
