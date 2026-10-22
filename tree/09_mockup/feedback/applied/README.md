---
path: _concept/09_mockup/feedback/applied/
summary: committed per-round record of patches landed, failed and notes closed
owner: [mockup-feedback]
may_propose: []
---

# _concept/09_mockup/feedback/applied/

`applied/<round>.json`, written by `skills/mockup-feedback/scripts/apply.py` in the same commit as the file edits and the devlog append. It is the durable record once the notes leave the open list, and its presence marks the round as applied: `apply.py` refuses a second run for the same `<round>` without `--force`.

## Format

```json
{
  "roundId": "<round>",
  "appliedAt": "<ISO-8601 UTC>",
  "items": [
    {
      "inboxId": "k3m9x2-1",
      "patchId": "p-k3m9x2-1-model",
      "target": { "file": "10_blueprint/datamodel/model.ts", "section": "ts:entity/Task/fields", "category": null },
      "body": "The editor needs an estimate field.",
      "status": "applied"
    },
    {
      "inboxId": "k3m9x2-2",
      "patchId": "p-k3m9x2-2-content",
      "target": { "file": "07_screens/inbox.md", "section": "## NONEXISTENT SECTION", "category": "change" },
      "body": "Put the filter bar above the list.",
      "status": "failed",
      "error": "section not found: '## NONEXISTENT SECTION'"
    }
  ],
  "resolutions": [
    {
      "id": "k3m9x2-1",
      "status": "implemented",
      "resolution": "Task.estimate proposed in model.ts.",
      "state": "pending",
      "command": "cd <package dir> && npm install && npx tsx scripts/resolve.ts --ids k3m9x2-1 --status implemented --resolution 'Task.estimate proposed in model.ts.'"
    },
    { "id": "k3m9x2-2", "state": "open", "reason": "patch not applied: p-k3m9x2-2-content" }
  ]
}
```

One item per checked patch, applied and failed alike: note id, patch id, target `file` / `section` / `category`, the verbatim note `body`, `status` (`applied` | `failed`) and an `error` on failure. A patch without a category has `category: null`.

One resolution per note a checked patch answers, with a `state`:

| `state` | Meaning | Extra keys |
|---|---|---|
| `resolved` | the note is closed in the inbox with `status` and `resolution` | none |
| `pending` | every patch landed, but the mockup package is not installed or its `resolve.ts` failed | `command`, the exact command that closes the note; `error` when `resolve.ts` ran and failed |
| `open` | a patch listing the note was unchecked or failed, so the note stays open | `reason` |

## Writing it

Only `apply.py` writes this file (`tree/09_mockup/feedback/README.md § Filing feedback (mockup-feedback)`, step 5). It applies each checked patch best-effort, runs `gen.ts` when `model.ts` changed, writes this file with every answerable note `pending`, appends the devlog block and makes one commit `feedback: apply round <round> (<n> applied, <m> failed)`. Only after that commit does it close the notes through `_concept/09_mockup/storybook/scripts/resolve.ts`, run with the package's own `tsx`, and amend the commit with the `resolved` states, so a note is never closed for a change that is not in the history. If the commit fails it restores the working tree, deletes this file and closes no note. All-failed (exit 2) writes nothing. A `pending` resolution is closed later by running its `command` once; that edits the inbox, which is local state, not a file of this commit.

## Checks

`python skills/mockup-feedback/scripts/validate_applied.py <applied-json> <patches-json> <review-md>` exits 0: every checked patch id in the review file has an item here, no item references a patch id absent from the patches JSON, every item's `status` is `applied` or `failed` (failed items carry an `error`), `roundId` matches the patches JSON, and every note a checked patch lists in `resolves[]` has one `resolutions[]` entry with a valid `state` (`pending` carries `command`, `open` carries `reason`). Every note of the round appears here, in `needs_manual`, or in the triage file's unresolved list.
