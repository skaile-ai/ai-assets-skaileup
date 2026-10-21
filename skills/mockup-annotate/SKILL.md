---
name: mockup-annotate
description: "Use when a built walkthrough is ready for stakeholders to comment on. Injects the annotation overlay so a reader can click any element and leave a note, and prepares the session directory their notes come back to. Turning the returned notes into edits is mockup-feedback's."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: walkthrough }
    produces:
      - { id: feedback-sessions, path: "_concept/09_mockup/feedback/sessions/" }
  prerequisites:
    files:
      # Hard: the overlay binds to the `data-spec-*` attributes and `manifest.json` that only
      # mockup-walkthrough's renderers emit, a machine-read format this skill can neither
      # derive nor ask a user for.
      - { path: "_concept/09_mockup/walkthrough", gate: hard, min_entries: 1 }
---

# mockup-annotate

Turns a rendered walkthrough into a surface people can comment on, and stops there. It edits only the built site, never a screen spec, and is idempotent. Reading what comes back and turning it into edits is `mockup-feedback`; a project with no built site needs `mockup-walkthrough` for it.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Locate the site, copy the overlay, inject the script tag into every page** — `tree/09_mockup/feedback/README.md § Annotating (mockup-annotate)` steps 1–3. The overlay is `skills/mockup-annotate/overlay/annotation-overlay.js`.
2. **Prepare the return path and validate** — `tree/09_mockup/feedback/README.md § Annotating (mockup-annotate)` steps 4–5: `python skills/mockup-annotate/validator.py _concept/09_mockup/walkthrough/<renderer>`.
3. **Report** — `tree/09_mockup/feedback/README.md § Annotating (mockup-annotate)` step 6 and *Getting the notes back*; the session format a reader's download follows is `tree/09_mockup/feedback/sessions/README.md`.

**Done when** the validator exits 0, `_concept/09_mockup/feedback/sessions/` exists, and the user has the site root and the reader instruction in front of them.
