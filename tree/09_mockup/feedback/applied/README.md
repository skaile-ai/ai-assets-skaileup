---
path: _concept/09_mockup/feedback/applied/
summary: committed per-session record of which patches landed and which failed
owner: [mockup-feedback]
may_propose: []
---

# _concept/09_mockup/feedback/applied/

`applied/<sid>.json`, written by `skills/mockup-feedback/scripts/apply.py` in the same commit as the spec edits and the devlog append. It is the durable record once `sessions/` rotates, and its presence marks the session as applied: `apply.py` refuses a second run for the same `<sid>` without `--force`.

## Format

```json
{
  "sessionId": "<sid>",
  "appliedAt": "<ISO-8601 UTC>",
  "items": [
    {
      "annotationId": "ann-good",
      "patchId": "p-good",
      "target": { "file": "07_screens/01_user_auth/login.md", "section": "## Layout", "category": "change" },
      "body": "right-align the button",
      "status": "applied"
    },
    {
      "annotationId": "ann-bad",
      "patchId": "p-bad",
      "target": { "file": "07_screens/01_user_auth/login.md", "section": "## NONEXISTENT SECTION", "category": "change" },
      "body": "change something",
      "status": "failed",
      "error": "section not found: '## NONEXISTENT SECTION'"
    }
  ]
}
```

One item per checked patch, applied and failed alike: annotation id, patch id, target `file` / `section` / `category`, the verbatim annotation `body`, `status` (`applied` | `failed`) and an `error` on failure. A derived patch has `category: null`.

## Writing it

Only `apply.py` writes this file (`tree/09_mockup/feedback/README.md § Filing feedback (mockup-feedback)`, step 6). It applies each checked patch best-effort, writes this file, appends the devlog block and makes one commit `feedback: apply session <sid> (<n> applied, <m> failed)`. If the commit fails it restores the working tree and deletes this file. All-failed (exit 2) writes nothing.

## Checks

`python skills/mockup-feedback/scripts/validate_applied.py <applied-json> <patches-json> <review-md>` exits 0: every checked patch id in the review file has an item here, no item references a patch id absent from the patches JSON, every item's `status` is `applied` or `failed` (failed items carry an `error`), and `sessionId` matches the patches JSON. Every annotation of the session appears here, in `needs_manual`, or in the triage file's unresolved list.
