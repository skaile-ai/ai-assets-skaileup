---
name: build-plan
description: "Use when a frozen feature spec needs breaking into buildable work — cuts the feature into vertical slices, gives each its blocking edges, and writes one slice dossier per slice. Triggers on 'plan this feature', 'break it into slices', 'what do we build first'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: features }
      - { id: screens }
      - { id: techstack }
      - { id: datamodel }
      - { id: standards }
      - { id: interaction-review }
      - { id: grounding-findings }
    produces:
      - { id: slice-plan, path: "_concept/11_build/slices/<slice_id>/plan.md" }
      - { id: acceptance-criteria, path: "_concept/11_build/acceptance-criteria/<featureset>/<feature_slug>.ac.md" }
  prerequisites:
    files:
      # Hard: the spec's criterion ids and `screens:` list are machine-joined into the ledger and the plan;
      # an id cannot be derived from the code, and `spec-feature` writes it.
      - { path: "_concept/05_features", gate: hard, min_entries: 1 }
      - { path: "_concept/07_screens", gate: soft, min_entries: 1 }
      - { path: "_concept/10_blueprint/techstack.md", gate: soft }
      - { path: "_concept/10_blueprint/datamodel", gate: soft }
      - { path: "_concept/02_grounding/standards/index.yml", gate: soft }
      - { path: "_concept/11_build/interaction.sarif", gate: soft }
      - { path: "_concept/02_grounding/findings", gate: soft }
---

# build-plan

Turns one frozen feature spec into the vertical slices that build it, each with the slices
that block it and its own dossier under `11_build/slices/<slice_id>/`. It plans and writes no
code: a dossier is built by `build-implement`.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Read the feature, cut the slices, give them blocking edges, quiz the user** — `tree/11_build/slices/README.md § Writing it` (steps 1–5; step 2 joins the open `interaction.sarif` changes). Only the feature spec is required to plan; a missing screen, stack or model is derived from the findings or asked in the quiz. Write nothing until the user approves the breakdown.
2. **Write one dossier per approved slice** — `tree/11_build/slices/[slice_id]/plan.md`.
3. **Create the criteria ledger** — `tree/11_build/acceptance-criteria/README.md § Creating the ledger`. Every row untested, one per criterion id the spec carries.
4. **Report the frontier** — `tree/11_build/slices/README.md § Writing it` (step 7): the slices whose blockers are all satisfied, in the order they can start.

**Done when** every acceptance criterion in the spec is claimed by a slice, every `blocked_by` names a slice that exists, each slice's `plan.md` is on disk, and the ledger holds one untested row per criterion.
