---
title: "mockup-feedback-patch"
description: "Use when a triage file exists for a feedback session and you need to author diffs for each annotation. Produces patches/<sid>.json + patches/<sid>.review.md (LLM for change; templated for add/remove/question). Third skill in the mockup-feedback clust"
sidebar:
  label: "mockup-feedback-patch"
---

:::note[Skill manifest]
**Name:** `mockup-feedback-patch`
**Stage:** alpha · **Version:** 0.1.0
**Tags:** mockup-feedback, patch, diff, review
**Source:** [`skaileup/mockup-feedback/patch/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/mockup-feedback/patch/SKILL.md)
:::


# mockup-feedback-patch

## Overview

For each `(file, annotations)` group in `triage/<sid>.json`:
1. Read the target `_concept/` file (frontmatter + body).
2. For each annotation, author a **section-anchored unified diff** in the
   target file's prose voice.
3. For annotations on provisional elements, also emit a
   `kind: "provisional-promotion"` diff.
4. Write `patches/<sid>.json` (machine-readable) and
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
```

All auto-generated patches start as `- [x]` (checked). Users toggle
`[x]` → `[ ]` to skip a patch, or hand-edit the diff in-place.

---

## Output

After writing both files, print:

```
mockup-feedback-patch complete: <sid>
  N patches authored across M files
  K needs_manual (see review.md preamble)
  review at: _concept/_feedback/patches/<sid>.review.md
Next: edit review.md as needed, then run mockup-feedback-apply
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

