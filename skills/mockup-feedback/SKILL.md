---
name: mockup-feedback
description: "Use when stakeholder annotations have come back from an annotated walkthrough and need to land in the concept. Routes each annotation to the file it belongs in, authors a reviewable diff for it, and — after you approve the review file — applies the approved diffs in one commit."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      # Soft, not hard: step 1 adopts a session that has not landed yet, so a hard
      # gate would refuse the skill in exactly the case it exists to handle.
      - { id: feedback-sessions }
    produces:
      - { id: feedback-applied, path: "_concept/09_mockup/feedback/" }
  prerequisites:
    files:
      - { path: "_concept/09_mockup/feedback/sessions", gate: soft, min_entries: 1 }
---

# mockup-feedback

One pass over one session file: adopt, triage, patch, apply. It ends with edited screen specs, an audit trail and exactly one commit, and never edits the walkthrough; `mockup-walkthrough` re-renders it. The pass stops at the review file: nothing is written into the specs until the user approves it, and a screen takes human-approved patches only (`tree/07_screens/[screen].md § Patching (mockup-feedback)`).

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Adopt the session file, taking its name from its own `sessionId`** — `tree/09_mockup/feedback/README.md § Filing feedback (mockup-feedback)` step 1; format in `tree/09_mockup/feedback/sessions/README.md`.
2. **Pick the session, then triage it** — `tree/09_mockup/feedback/README.md § Filing feedback (mockup-feedback)` steps 2–3; `python skills/mockup-feedback/scripts/triage.py` and its format in `tree/09_mockup/feedback/triage/README.md`.
3. **Author one patch per annotation, plus the review file** — `tree/09_mockup/feedback/patches/README.md`, scope and id rules in `tree/09_mockup/feedback/README.md § Patch scope`. `stories.yaml` and feature specs take no patch; those annotations become `needs_manual`.
4. **Present the review file and stop** — `tree/09_mockup/feedback/README.md § Filing feedback (mockup-feedback)` step 5.
5. **Pre-flight, apply, report** — `tree/09_mockup/feedback/README.md § Filing feedback (mockup-feedback)` steps 6–7: `python skills/mockup-feedback/scripts/apply.py` writes `_concept/09_mockup/feedback/applied/<sid>.json` (format: `tree/09_mockup/feedback/applied/README.md`) and appends to `_concept/09_mockup/feedback/devlog.md` (format: `tree/09_mockup/feedback/devlog.md`).

**Done when** one commit exists carrying the edited specs, `applied/<sid>.json` and the devlog append, and every annotation in the session appears in `applied/<sid>.json`, in `needs_manual`, or in the triage file's unresolved list.
