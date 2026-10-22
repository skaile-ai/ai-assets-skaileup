---
name: mockup-feedback
description: "Use when stakeholder notes left on the Storybook prototype need to land in the concept, or when the user says 'work through the feedback', 'apply the annotations', 'what did the reviewers say'. Routes each open note to the spec, data-model entity or glossary term it belongs in, authors a reviewable diff for it, and — after you approve the review file — applies the approved diffs in one commit and closes the notes."
version: "0.2.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      # The notes sit in the annotation inbox, not in an artifact; the storybook id
      # only says a prototype exists for people to annotate.
      - { id: storybook }
      - { id: screens }
      - { id: datamodel }
    produces:
      - { id: feedback-applied, path: "_concept/09_mockup/feedback/" }
  prerequisites:
    files:
      - { path: "_concept/09_mockup/storybook", gate: soft }
---

# mockup-feedback

One pass over the open notes of the project's annotation inbox: read, triage, patch, apply, resolve. It ends with edited screen specs, proposals in `model.ts` and the glossary, an audit trail, exactly one commit and the answered notes closed. The pass stops at the review file: nothing is written into the specs or the model until the user approves it, and a screen takes human-approved patches only (`tree/07_screens/[screen].md § Patching (mockup-feedback)`). It never edits the prototype; `mockup-storybook` builds a proposed field into the editor.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Read the open notes** — `tree/09_mockup/feedback/README.md § Filing feedback (mockup-feedback)` step 1; list them with the `annotation-inbox` skill (store and item shape: `tree/09_mockup/storybook/README.md § Annotation`).
2. **Triage them** — `tree/09_mockup/feedback/README.md § Filing feedback (mockup-feedback)` step 2; `python skills/mockup-feedback/scripts/triage.py` and its format in `tree/09_mockup/feedback/triage/README.md`.
3. **Author one patch per note, plus the review file** — `tree/09_mockup/feedback/patches/README.md`, scope rules in `tree/09_mockup/feedback/README.md § Patch scope`; a model proposal follows `tree/10_blueprint/datamodel/model.md § Format`, and its glossary term goes into the file `tree/glossary.md § Where the words live` resolves. `stories.yaml` and feature specs take no patch; those notes become `needs_manual`. Validate with `python skills/mockup-feedback/scripts/validate_patches.py`.
4. **Present the review file and stop** — `tree/09_mockup/feedback/README.md § Filing feedback (mockup-feedback)` step 4.
5. **Pre-flight, apply, resolve, report** — `tree/09_mockup/feedback/README.md § Filing feedback (mockup-feedback)` steps 5–6: `python skills/mockup-feedback/scripts/apply.py` runs `gen.ts` after a `model.ts` change, closes the notes in the inbox, writes `_concept/09_mockup/feedback/applied/<round>.json` (format: `tree/09_mockup/feedback/applied/README.md`) and appends to `_concept/09_mockup/feedback/devlog.md` (format: `tree/09_mockup/feedback/devlog.md`).

**Done when** one commit exists carrying the edited files, `applied/<round>.json` and the devlog append, and every note of the round appears in `applied/<round>.json` as a resolution, in `needs_manual`, or in the triage file's unresolved list.
