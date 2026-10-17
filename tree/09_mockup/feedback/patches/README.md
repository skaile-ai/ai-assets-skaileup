---
path: _concept/09_mockup/feedback/patches/
summary: proposed section-anchored patches and the review file a human approves
writers: [mockup-feedback]
---

# _concept/09_mockup/feedback/patches/

Per session, `patches/<sid>.json` (the machine patch set) and `patches/<sid>.review.md` (the approval gate), written together by `mockup-feedback` and gitignored. `apply.py` applies only the patches the human left checked in the review file, so every format below is read by a script: a drifting anchor or a de-bolded patch id makes a patch fail or vanish.

## Format

### Section-anchored diffs

Every diff anchors to a heading, never to a line number: concept files are edited by hand between feedback rounds, so an offset computed at proposal time is wrong by apply time.

```
@@ ## Section Name @@
- line to remove (full content, including the markdown bullet)
+ line to add
```

Frontmatter edits use the `frontmatter:elements` anchor instead:

```
@@ frontmatter:elements @@
-  - id: <element-id>
-    provisional: true
+  - id: <element-id>
+    provisional: false
```

What `apply.py` does with these:

- The anchor matches a heading line **exactly**: `@@ ## Layout @@` needs a literal `## Layout` line in the file.
- Removed lines exist in that section as a **consecutive block**, matched exactly; the first mismatch fails that patch and only that patch.
- There are no context lines; a line starting with neither `-` nor `+` is ignored.
- A diff with no removes inserts at the end of the section; if the section does not exist, the adds are appended to the file and the patch is `kind: create-section`.

### Categories

One diff shape per `category` of `tree/09_mockup/feedback/sessions/README.md`. `change` is authored; the rest are templates, matched exactly.

| Category | Diff |
|---|---|
| `change` | Rewrite the section the annotated element sits in, scoped to the lines that move. |
| `add` | `@@ ## States @@` then `+ - <annotation body>`, under the section the addition belongs to: `## States` for a state, `## Behavior` for a behaviour. |
| `remove` | `@@ ## <section> @@`, then the original line as a remove and the same line struck through as an add: `+ - ~~<original line>~~`. Strikethrough, not deletion, so the review file shows what a reader asked to drop. |
| `question` | `@@ ## Open Questions @@` then `+ - <annotation body>`, creating the section if absent. |

### Derived patches

Two patches are emitted alongside a content patch rather than in response to a comment (rules: `tree/09_mockup/feedback/README.md § Id promotion`).

**`provisional-promotion`**: the annotated element's id was auto-slugged. Flip `provisional: true` to `false` in the element's frontmatter entry. Read the file's `elements:` block first for its exact indentation; if the frontmatter is missing or unparseable, skip the promotion, warn, and keep the content patch.

```json
{
  "id": "p-<annotationId>-promotion",
  "annotationId": "<annotationId>",
  "file": "<same file>",
  "section": "frontmatter:elements",
  "kind": "provisional-promotion",
  "category": null,
  "diff": "@@ frontmatter:elements @@\n-  - id: <element-id>\n-    provisional: true\n+  - id: <element-id>\n+    provisional: false\n"
}
```

**`target-promotion`**: the annotation asks for navigation ("this should link to…", "clicking this should open…") and the element has no `target:` yet. Resolve the destination to a `screen_id` through the walkthrough manifest's screen list, with confidence or not at all: an unresolvable destination becomes a `needs_manual` entry reading `navigation intent unresolved — no matching screen`, because a wrong `target:` silently rewires the walkthrough.

```json
{
  "id": "p-<annotationId>-target",
  "kind": "target-promotion",
  "section": "frontmatter:elements",
  "diff": "@@ frontmatter:elements @@\n-  - id: <element-id>\n+  - id: <element-id>\n+    target: <resolved-screen-id>\n"
}
```

### `patches/<sid>.json`

`file` is relative to the concept root, with no `_concept/` prefix. Ids follow `p-<annotationId>-content` / `-promotion` / `-target`.

```json
{
  "sessionId": "<sid>",
  "proposedAt": "<ISO-8601 UTC>",
  "patches": [
    {
      "id": "p-ann-c1-content",
      "annotationId": "ann-c1",
      "file": "07_screens/01_user_auth/login.md",
      "section": "## Layout",
      "kind": "content",
      "category": "change",
      "body": "this should be on the right",
      "diff": "@@ ## Layout @@\n-- submit-button: centered below form\n+- submit-button: right-aligned below form\n"
    }
  ],
  "needs_manual": [
    { "annotationId": "<id>", "reason": "<why no patch could be authored>" }
  ]
}
```

Every triaged annotation ends in `patches[]` (once or more) or `needs_manual[]` (exactly once), never both and never neither. JSON Schema (draft-07):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Patches",
  "type": "object",
  "required": ["sessionId", "proposedAt", "patches", "needs_manual"],
  "properties": {
    "sessionId":   { "type": "string" },
    "proposedAt":  { "type": "string" },
    "patches": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "annotationId", "file", "section", "kind", "body", "diff"],
        "properties": {
          "id":           { "type": "string" },
          "annotationId": { "type": "string" },
          "file":         { "type": "string" },
          "section":      { "type": "string" },
          "kind":         { "type": "string", "enum": ["content", "provisional-promotion", "target-promotion", "create-section"] },
          "category":     { "type": ["string", "null"] },
          "body":         { "type": "string", "description": "Original annotation body (copied from session JSON by patch skill; preserved in applied/ audit trail)" },
          "diff":         { "type": "string" }
        }
      }
    },
    "needs_manual": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["annotationId", "reason"],
        "properties": {
          "annotationId": { "type": "string" },
          "reason":       { "type": "string" }
        }
      }
    }
  }
}
```

### `patches/<sid>.review.md`

The approval gate. `apply.py` reads exactly one thing from it, `- [x] **<patch-id>**`, so the patch id is bold and immediately follows the checkbox.

```markdown
# Review patches for session <sid> (N patches across M files)

## Needs manual review

- annotation `<id>` — <reason>

## <file path>

- [x] **<patch-id>** · category=<category> · annotation: "<body preview>"
  ```diff
  <diff text>
  ```

## Test impact

Re-run the quality-test skill after applying — these spec changes affect coverage:

- `<file>` — <Happy|Error|Edge|Permissions>: <suggested scenario> (AC: <story-id>)
```

Every auto-generated patch starts checked; the user unchecks to skip. Omit `## Needs manual review` and `## Test impact` when they would be empty. A patch changes testable behaviour when it touches `## Behavior`, `## States`, `## Requirements`, `## Error States`, `## Success Criteria` or `## Permissions` in a screen file, or when an `add` introduces a new state, behaviour or error case; each gets one suggested scenario under `## Test impact`. The scenarios are notes, not patches: no checkbox, and `apply.py` ignores them. Copy, token and layout changes have no test impact; leave them out rather than listing them as unaffected.

## Writing it

Author one patch per annotation per `tree/09_mockup/feedback/README.md § Filing feedback (mockup-feedback)` step 4, then write `.json` and `.review.md` together.

## Checks

`python skills/mockup-feedback/scripts/validate_patches.py <triage-json> <patches-json> <review-md> [<session-json>]` exits 0: the partition invariant above holds; each patch's `file` matches its annotation's triaged file; each diff starts with a valid `@@` anchor; a provisional annotation with patches has exactly one `provisional-promotion` patch; every patch has a `- [x]` item in the review file; every `needs_manual` entry has a bullet under `## Needs manual review` and no checklist item; `add` / `remove` / `question` diffs match their templates.
