---
name: mockup-feedback-patch
description: "Use when a triage file exists for a feedback session and you need to author diffs for each annotation. Produces patches/<sid>.json + patches/<sid>.review.md (LLM for change; templated for add/remove/question). Third skill in the mockup-feedback cluster."
metadata:
  version: "0.1.0"
  tags: [mockup-feedback, patch, diff, review]
  stage: alpha
  artifacts:
    requires:
      - id: feedback-triage
        gate: hard
    produces:
      - id: feedback-patches
      - id: feedback-patches-review
  prerequisites:
    files:
      - path: "_concept/_feedback/triage/"
        gate: hard
        description: "triage/<sid>.json from mockup-feedback-triage"
        min_entries: 1
    produces:
      - path: "_concept/_feedback/patches/<sid>.json"
        description: "Machine-readable patch list"
      - path: "_concept/_feedback/patches/<sid>.review.md"
        description: "Human-editable checklist; tick boxes before running apply"
---

# mockup-feedback-patch

## Overview

For each `(file, annotations)` group in `triage/<sid>.json`:
1. Read the target `_concept/` file (frontmatter + body).
2. For each annotation, author a **section-anchored unified diff** in the
   target file's prose voice.
3. For annotations on provisional elements, also emit a
   `kind: "provisional-promotion"` diff.
4. For annotations that change **testable behavior** (see *Test impact* below),
   author a one-line suggested test scenario.
5. Write `patches/<sid>.json` (machine-readable) and
   `patches/<sid>.review.md` (human checklist, all auto-items pre-checked).

Each patch entry in `patches/<sid>.json` must include a `body` field copied
verbatim from `annotation.body`. This preserves the annotation's original text
in the committed `applied/<sid>.json` audit trail (D6), since `sessions/` is
gitignored and rotates.

Run after `mockup-feedback-triage`. Run `mockup-feedback-apply` after the
user reviews and edits `review.md`.

---

## Diff format

All diffs use section-anchored headers, NOT line-number offsets:

```
@@ ## Section Name @@
- line to remove (full content including any markdown bullet)
+ line to add
```

For frontmatter edits:

```
@@ frontmatter:elements @@
-  - id: <element-id>
-    provisional: true
+  - id: <element-id>
+    provisional: false
```

The `apply.py` script parses these headers. Do not use standard `git diff`
format (no `@@` with line numbers).

---

## Category templates

### `category=change`

LLM call: read the section the annotation's element appears in, rewrite to
incorporate the annotation's intent. Output a unified diff of that section.
Scope the diff to the relevant lines only.

### `category=add`

Append `- <annotation.body>` under the most appropriate section (typically
`## States` for state additions, `## Behavior` for behavior additions).
If the section is absent, use `kind: "create-section"` and include
`+## <SectionName>` as the first add line.

Template:
```
@@ ## States @@
+ - <annotation.body>
```

### `category=remove`

Strikethrough the matching line:

Template:
```
@@ ## <section> @@
- - <original line>
+ - ~~<original line>~~
```

### `category=question`

Append to `## Open Questions` (create section if absent):

Template:
```
@@ ## Open Questions @@
+ - <annotation.body>
```

---

## Provisional promotion

When `specRef.provisional=true` for an annotation that produces a content diff,
also emit a second patch with `kind: "provisional-promotion"`:

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

Read the file's `elements:` frontmatter block to get the exact indentation.
If frontmatter is missing or unparseable, skip the promotion patch and print
a warning — do not abort.

---

## Test impact

A patch changes **testable behavior** when:

- the target is a **feature** file and the diff touches `## Requirements`,
  `## Error States`, `## Success Criteria`, or `## Permissions`, or
- the target is a **screen** file and the diff touches `## Behavior` or
  `## States`, or
- `category=add` introduces a new state, behavior, or error case.

For each such patch, author a single suggested test scenario tagged with its
category (Happy / Error / Edge / Permissions) and, where the target feature has
`story_refs:`, the relevant `story-id`. These are **suggestions for `test-plan`**,
not diffs — they are not applied to concept files and never carry a checkbox.

Collect them under `## Test impact` in `review.md` (see format below). They close
the feedback→test loop: after `mockup-feedback-apply` lands the spec edits,
re-running `impl-quality-test-plan` regenerates scenarios from the updated
features/screens, and these suggestions flag what to confirm got covered.

Purely cosmetic patches (copy, tokens, layout, provisional-promotion) have no
test impact — omit them.

---

## Handling unautomatable annotations

If an annotation cannot be patched (empty body, contradictory intent,
unrecoverable target), emit a `needs_manual` entry instead of a patch:

```json
{ "annotationId": "<id>", "reason": "<explanation>" }
```

Do NOT add a checklist item in `review.md` for this annotation.
DO add a bullet under `## Needs manual review` in `review.md`:

```markdown
## Needs manual review

- annotation `<id>` — <reason>
```

---

## review.md format

```markdown
# Review patches for session <sid> (N patches across M files)

## Needs manual review

(omit this section when needs_manual is empty)

- annotation `<id>` — <reason>

## <file path>

- [x] **<patch-id>** · category=<category> · annotation: "<body preview>"
  ```diff
  <diff text>
  ```

- [x] **<patch-id-promotion>** · provisional ID promotion for `<element-id>`
  ```diff
  <diff text>
  ```

## Test impact

(omit this section when no patch changes testable behavior)

Re-run `impl-quality-test-plan` after applying — these spec changes affect coverage:

- `<feature-or-screen path>` — <category>: <suggested scenario> (AC: <story-id>)
```

All auto-generated patches start as `- [x]` (checked). Users toggle
`[x]` → `[ ]` to skip a patch, or hand-edit the diff in-place. The
`## Test impact` bullets are advisory notes, **not** patches — they carry no
checkbox and `apply.py` ignores them.

---

## Output

After writing both files, print:

```
mockup-feedback-patch complete: <sid>
  N patches authored across M files
  K needs_manual (see review.md preamble)
  T test-impact scenarios suggested (see review.md ## Test impact)
  review at: _concept/_feedback/patches/<sid>.review.md
Next: edit review.md as needed, then run mockup-feedback-apply
  (if T > 0, re-run impl-quality-test-plan after apply)
```

---

## Inputs

| Name | Type | Default |
|---|---|---|
| `session_id` | string | (all unpatched sessions) |
| `concept_root` | path | `_concept/` |

## Outputs

| Path | Description |
|---|---|
| `_concept/_feedback/patches/<sid>.json` | Patch list (machine-readable) |
| `_concept/_feedback/patches/<sid>.review.md` | Checklist for human review |

## References

- `contracts/elements_block.md` — `elements:` frontmatter schema, provisional ID rules (4-space indent)
- `mockup-feedback/schemas/patches.schema.json` — output shape
- `docs/superpowers/specs/2026-05-09-3B-mockup-feedback-triage-patch-apply-design.md` D2, D4, D5
