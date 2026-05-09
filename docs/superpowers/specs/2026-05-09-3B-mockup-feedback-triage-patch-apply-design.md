---
title: 3B mockup-feedback-{triage, patch, apply} — design
date: 2026-05-09
status: draft
related:
  - docs/superpowers/plans/2026-05-07-skill-graph-migration.md (Task 3B)
  - docs/superpowers/plans/3A-mockup-feedback-annotate.md (sibling skill, Task 3A)
  - docs/superpowers/notes/forge-concept-walkthrough.md (Task 3.0 findings)
  - REFACTOR_MOCKUP.md §5, §11, §12
---

# 3B mockup-feedback-{triage, patch, apply} — design

## Context & scope

Phase 3 Task 3B of the skill-graph migration builds the patch loop that
processes the per-session annotation JSONs produced by Task 3A
(`mockup-feedback-annotate`). It splits across **three skills**:

- `mockup-feedback-triage` — routing
- `mockup-feedback-patch` — diff authoring
- `mockup-feedback-apply` — git + file writes + audit trail

This document is the agreed design. Implementation lives in a follow-up
mini-plan at `docs/superpowers/plans/3B-mockup-feedback-triage-patch-apply.md`
(written next, in the same pattern as `3A-mockup-feedback-annotate.md`).

**Supersedes the migration plan's Task 3B description on two points:**
the migration plan describes triage as classifying into
`bug|copy|layout|scope|out-of-scope` and prompting for provisional ID
promotion. This spec **rejects both**: triage is pure routing (decision
D1) and provisional promotion is emitted as an extra patch by the patch
skill (decision D5). Where the migration plan and this spec disagree on
3B internals, this spec wins.

**Already settled upstream — adopted verbatim, not re-discussed here:**

| Topic                                        | Source                                                      |
|----------------------------------------------|-------------------------------------------------------------|
| `data-spec-*` attribute names                | spec § Component 1 (forge-concept) + `contracts/elements_block.md` |
| Annotation `category` enum (`change|add|remove|question`) | spec § Component 5; set at annotate time by 3A overlay |
| Storage layout `_concept/_feedback/{sessions,patches,applied}/` + `devlog.md` | spec § Component 4; REFACTOR_MOCKUP.md §5 |
| Git policy: `sessions/` + `patches/` gitignored; `applied/` + `devlog.md` committed | REFACTOR_MOCKUP.md §11 row 8 |
| Patch granularity: section-level for `.md`, line-level for `.json` | REFACTOR_MOCKUP.md §11 row 4 |
| Last-write-wins JSON per session ID          | REFACTOR_MOCKUP.md §11 row 9                                |
| Devlog format                                 | REFACTOR_MOCKUP.md §5 (Devlog format subsection)            |
| Provisional ID promotion: hybrid auto-slug + promote-on-first-annotation | REFACTOR_MOCKUP.md §11 row 3 |

## Decisions made during brainstorming

Six design questions were resolved in this session. Each decision is
binding for the implementation plan; revisiting requires updating this
spec first.

### D1 — Triage classification axis

**Decision:** single axis. Triage is **pure routing** (resolve target
file path + group by file). The user's annotate-time `category`
(`change|add|remove|question`) is preserved unchanged through to patch.

**Rejected alternatives:**
- Two orthogonal axes (action + concern type). Adds a second classifier
  with no downstream consumer; routing already drives which file gets
  the patch.
- Re-classification at triage. Discards the user's intent and requires
  an LLM in triage; complicates the simplest skill.

**Implication:** triage is implementable as a deterministic Python
script. No LLM in this skill.

### D2 — Patch generation strategy

**Decision:** LLM-driven for all categories, with deterministic templates
described in the SKILL.md prompt for `add` / `remove` / `question`. Only
`change` requires the LLM to author free-form diffs. Validator checks
structural properties of the output (target section, frontmatter
preservation, parseable diff), not exact diff text.

**Rejected alternatives:**
- Pure deterministic Python. Cannot handle `change` annotations whose
  comments need rewording into the file's prose voice.
- Pure LLM (no templates). Mechanical mutations for `add`/`remove`/`question`
  become unreproducible and harder to test.

**Implication:** patch is the **only** LLM-touched skill in the cluster.
Apply remains deterministic.

### D3 — Apply atomicity

**Decision:** **per-session commit, best-effort.** Apply attempts every
approved patch; succeeded ones land in one git commit covering the
edited files + the devlog block + the `applied/<sid>.json` record.
Failed patches are recorded inside `applied/<sid>.json` with a reason
but produce no commit content for that file.

**Rejected alternatives:**
- Per-annotation commits. Pollutes git log; reviewer sees fragmented
  history. The session is the user's mental unit.
- All-or-nothing. One bad LLM diff blocks 9 good ones; user must fix
  and re-run the whole session.

**Implication:** apply must be tolerant of per-patch failure but record
it visibly. Pre-flight dry-run validates each diff before any write.

### D4 — Patch approval surface

**Decision:** patch emits **`_feedback/patches/<sid>.review.md`** — a
human-editable file with a checklist (`- [x]` / `- [ ]`) and one
fenced unified-diff block per patch. Apply parses the checklist and
applies only checked items. The user can also hand-edit a diff
in-place before running apply.

**Rejected alternatives:**
- Interactive CLI prompt. Doesn't persist; loses state on Ctrl-C; no
  natural hand-tweak.
- Defer to forge-concept's drawer UI. Skill becomes unusable
  standalone; binds the catalog to one consumer.

**Implication:** apply has two inputs (`patches/<sid>.json` for diff
bodies, `review.md` for the approval state). The two are kept in sync
by `patch_id` references; apply rejects the run if a checked item in
`review.md` has no matching `patches.json` entry.

### D5 — Provisional ID promotion placement

**Decision:** the **patch** skill emits a separate
`kind: "provisional-promotion"` diff alongside the content diff
whenever an annotation lands on an element with
`specRef.provisional=true`. Both diffs appear as independent
checklist items in `review.md`, so the user can opt out of promotion
while keeping the content edit (or vice versa).

**Rejected alternatives:**
- Apply auto-promotes implicitly. Hidden behavior; user can't opt out
  without editing the source file directly.
- Separate `mockup-feedback-promote` skill. Another skill, more
  orchestration; no payoff over an extra patch entry.

**Implication:** patch must read frontmatter (not just body) of every
target file with provisional annotations. The promotion diff edits
`elements: [{id, provisional: true}]` → `provisional: false`.

### D6 — `applied/<sid>.json` shape (committed audit trail)

**Decision:** **hybrid** — per-annotation entry containing
`{annotationId, patchId, target: {file, section, category}, body, status, error?}`.
Stores the original annotation body (which is otherwise unrecoverable
once `sessions/` rotates), but **not** the diff itself (recoverable via
git history). **No `commitSha` field** — see D7 below for the
cross-reference mechanism.

**Rejected alternatives:**
- Minimal status manifest. Loses the annotation body — agent
  regeneration memory has to dig through devlog prose to reconstruct intent.
- Rich record (echoes diff). Redundant with git history; bloats over time.

**Implication:** `applied/<sid>.json` is the canonical machine-readable
audit trail. `devlog.md` is the human-readable summary. Both are
committed.

### D7 — Commit ↔ session cross-reference

**Decision:** the commit subject line embeds the **full** session ID
(no truncation): `feedback: apply session <full-sid> (N applied, K failed)`.
The `applied/<sid>.json` filename also embeds the same full session ID.
To find the commit that landed a given session, use
`git log --grep="session <full-sid>"`. There is **no `commitSha`
field** in `applied/<sid>.json`.

Note: 3A's overlay-download filename truncates the session ID
(`annotations-${SESSION_ID.slice(0, 8)}.json`) for human readability,
but the **session ID inside the JSON** is full-length and is the
canonical identifier here.

**Rejected alternatives:**
- Store `commitSha` and write it via two-step commit-then-amend.
  Amending changes the SHA, so the value recorded inside the file
  references the orphaned pre-amend commit. Inconsistent with
  `git log` and broken after `git gc`.
- Two real commits (content + applied-with-SHA). Doubles the noise in
  git log per session and complicates the all-failed rollback path.
- `git commit-tree` plumbing to compute the SHA in advance. Works but
  adds substantial complexity for a value that's already recoverable
  via `git log --grep`.

**Implication:** apply emits exactly one commit per session. The
session ID is the join key between the audit JSON and git history.

---

## Architecture

Three skills, run in sequence by the user/agent. **No orchestrator**;
composition is documented in `mockup-feedback/DOMAIN.md`. Matches the
catalog convention.

```
sessions/<sid>.json          (produced by 3A annotate; gitignored)
        │
        ▼
┌──────────────────────┐
│  mockup-feedback-    │   1. read session JSON
│      triage          │   2. resolve target file path per annotation
│  (deterministic      │      (specRef.screen / .feature / .journey → _concept/ path)
│   Python)            │   3. group by file, emit triage JSON
└──────────────────────┘
        │
        ▼
triage/<sid>.json            { groups: [{file, annotations}], unresolved }
        │
        ▼
┌──────────────────────┐
│  mockup-feedback-    │   1. read triage JSON
│      patch           │   2. for each (file, annotations) group:
│  (LLM-driven         │      a. read target file (frontmatter + body)
│   skill prompt;      │      b. for each annotation: author section-level
│   add/remove/        │         diff (deterministic for add/remove/question,
│   question are       │         LLM for change)
│   templated;         │      c. if specRef.provisional, emit a second
│   change is LLM)     │         provisional-promotion diff
│                      │   3. emit patches JSON + review.md
└──────────────────────┘
        │
        ▼
patches/<sid>.json           { patches: [{annotationId, file, section, diff, kind}] }
patches/<sid>.review.md      checklist + unified-diff fences for review
        │  (user edits review.md, ticks/unticks boxes, optionally hand-edits diffs)
        ▼
┌──────────────────────┐
│  mockup-feedback-    │   1. read patches JSON + review.md (parse checked items)
│      apply           │   2. for each approved patch (best-effort):
│  (deterministic      │      a. apply diff to target file
│   Python +           │      b. on success: queue devlog entry
│   git CLI)           │      c. on failure: record reason
│                      │   3. one git commit per session: succeeded files +
│                      │      devlog.md append + applied/<sid>.json
└──────────────────────┘
        │
        ▼
applied/<sid>.json           committed audit trail (per D6)
_feedback/devlog.md          appended (per REFACTOR_MOCKUP.md §5)
_concept/**.md               edited
                  + git commit
```

**Invariants:**
- Each skill has a single concern; no shared state beyond JSON files.
- All three are independently invocable (a forge-concept consumer can
  skip `review.md` and call apply directly with its own approved patches).
- Re-running apply on an already-applied session aborts unless
  `--force` is passed (idempotency check via `applied/<sid>.json`).
- **Annotation partitioning invariant.** Every annotation in the input
  session JSON is routed by triage+patch into **exactly one** of:
  (a) `triage/<sid>.json#/unresolved` (no target file),
  (b) `patches/<sid>.json#/patches[]` (one or more proposed diffs),
  or (c) `patches/<sid>.json#/needs_manual[]` (cannot be automated).
  Every validator and consumer can rely on this partition.

---

## Data shapes

### Input — `_concept/_feedback/sessions/<sid>.json` (from 3A)

The shape produced by `mockup-feedback/annotate/overlay/annotation-overlay.js`
(see the Download payload in that file): `{sessionId, annotations}` —
no top-level `createdAt`. Schemas in `mockup-feedback/schemas/` must
treat any future top-level fields as optional.

```json
{
  "sessionId": "01J...",
  "annotations": [
    {
      "id": "01K...",
      "sessionId": "01J...",
      "createdAt": "2026-05-09T14:23:11Z",
      "specRef": {
        "element": "submit-button",
        "screen": "01_user_auth/login",
        "journey": "onboarding",
        "route": "/screen/01_user_auth/login",
        "provisional": true
      },
      "body": "this should be on the right",
      "category": "change",
      "status": "open"
    }
  ]
}
```

### `_concept/_feedback/triage/<sid>.json`

```json
{
  "sessionId": "01J...",
  "triagedAt": "2026-05-09T14:30:00Z",
  "groups": [
    {
      "file": "experience/screens/01_user_auth/login.md",
      "annotations": ["01K..."]
    }
  ],
  "unresolved": [
    {
      "annotationId": "01L...",
      "reason": "no _concept/ file matches specRef.screen='unknown/foo'"
    }
  ]
}
```

### `_concept/_feedback/patches/<sid>.json`

```json
{
  "sessionId": "01J...",
  "proposedAt": "2026-05-09T14:35:00Z",
  "patches": [
    {
      "id": "p-01K...-content",
      "annotationId": "01K...",
      "file": "experience/screens/01_user_auth/login.md",
      "section": "## Layout",
      "kind": "content",
      "category": "change",
      "diff": "@@ ## Layout @@\n-- submit-button: centered below form\n+- submit-button: right-aligned below form\n"
    },
    {
      "id": "p-01K...-promotion",
      "annotationId": "01K...",
      "file": "experience/screens/01_user_auth/login.md",
      "section": "frontmatter:elements",
      "kind": "provisional-promotion",
      "category": null,
      "diff": "@@ frontmatter:elements @@\n-  - id: submit-button\n-    provisional: true\n+  - id: submit-button\n+    provisional: false\n"
    }
  ],
  "needs_manual": []
}
```

**`kind` values:** `content` | `provisional-promotion` | `create-section`.

**`needs_manual` (top-level array on `patches/<sid>.json`).** Annotations
the patch skill cannot automate (empty body, contradictory intent,
unrecoverable target) are emitted into the top-level `needs_manual: []`
array as `{annotationId, reason}` — they are NOT entries in `patches[]`,
do NOT appear in `review.md` as checklist items, and do NOT participate
in apply. The user resolves them by hand-editing the target file (or
discards the annotation). This keeps `patches[]` exclusively for items
that can be applied programmatically.

**`category` semantics:** `category` always preserves the user's
annotate-time enum (`change|add|remove|question`) verbatim, OR is `null`
for derived patches that have no annotate-time origin (currently only
`provisional-promotion`). It is **never** overloaded with `kind` values.

### `_concept/_feedback/patches/<sid>.review.md`

```markdown
# Review patches for session 01J... (2 patches across 1 file)

## Needs manual review

(omit this section when `needs_manual` is empty)

- annotation `01M...` — empty body, cannot author a `change` diff
- annotation `01N...` — contradictory intent on submit-button

## experience/screens/01_user_auth/login.md

- [x] **p-01K...-content** · category=change · annotation: "this should be on the right"
  ```diff
  @@ ## Layout @@
  -- submit-button: centered below form
  +- submit-button: right-aligned below form
  ```

- [x] **p-01K...-promotion** · provisional ID promotion for `submit-button`
  ```diff
  @@ frontmatter:elements @@
  -  - id: submit-button
  -    provisional: true
  +  - id: submit-button
  +    provisional: false
  ```
```

**Rendering rules:**
- The `## Needs manual review` preamble appears **iff** `needs_manual`
  is non-empty. Each entry is `- annotation \`<annotationId>\` — <reason>`.
- These items have **no checkbox** — they are not approval-gated.
- Per-file checklist sections follow, one per group in `patches.json`.
- Every entry in `patches[]` produces exactly one `- [x]` checklist item;
  the user toggles `[x]` ↔ `[ ]` to approve or skip.

### `_concept/_feedback/applied/<sid>.json` (committed)

```json
{
  "sessionId": "01J...",
  "appliedAt": "2026-05-09T14:42:00Z",
  "items": [
    {
      "annotationId": "01K...",
      "patchId": "p-01K...-content",
      "target": {
        "file": "experience/screens/01_user_auth/login.md",
        "section": "## Layout",
        "category": "change"
      },
      "body": "this should be on the right",
      "status": "applied"
    },
    {
      "annotationId": "01K...",
      "patchId": "p-01K...-promotion",
      "target": {
        "file": "experience/screens/01_user_auth/login.md",
        "section": "frontmatter:elements",
        "category": null
      },
      "body": "this should be on the right",
      "status": "applied"
    }
  ]
}
```

`status` values: `applied` | `failed`. `failed` items add `error`
(string). `target.category` mirrors the patch's `category` field —
the user's annotate-time enum, or `null` for derived patches.

**No `commitSha` field.** Per D7, the commit ↔ session join is via
the commit subject (`git log --grep="session <sid>"`).

### `_concept/_feedback/devlog.md` (appended per session)

```markdown
## 2026-05-09 · session 01J... · static-html walkthrough
**Reviewer:** stakeholder · **Commit:** abc123

### experience/screens/01_user_auth/login.md
- submit-button moved to right side per layout convention
  (target: submit-button, comment: "this should be on the right")
- promoted submit-button from provisional to permanent
```

Format follows REFACTOR_MOCKUP.md §5 (Devlog format).

---

## Skill bodies

### `mockup-feedback-triage/SKILL.md`

**Tech:** Python 3 stdlib only. No LLM in this skill.

**Inputs:** `_concept/_feedback/sessions/<sid>.json` (or directory of unprocessed sessions).

**Outputs:** `_concept/_feedback/triage/<sid>.json`.

**Algorithm:**

1. Load session JSON; validate against `schemas/session.schema.json`.
2. For each annotation, resolve `specRef` → target file path. Lookup
   priority:
   - `specRef.screen` → `_concept/experience/screens/<screen>.md`
   - else `specRef.feature` → `_concept/experience/features/<feature>.md`
   - else `specRef.journey` → `_concept/experience/journeys/<journey>.md`
   - else → `unresolved` with `reason: "no specRef target"`.
3. Verify the resolved file exists; if not → `unresolved` with `reason: "file not found"`.
4. Group annotations by resolved file path; emit `triage/<sid>.json`.
5. Print summary: `N annotations triaged across M files; K unresolved`.

### `mockup-feedback-patch/SKILL.md`

**Tech:** SKILL.md is an agent prompt. Templates for
`add`/`remove`/`question` are described in the prompt as deterministic
text-construction rules. `change` requires the agent to author the diff
in the target file's prose voice.

**Inputs:** `_concept/_feedback/triage/<sid>.json`.

**Outputs:** `_concept/_feedback/patches/<sid>.json` + `patches/<sid>.review.md`.

**Algorithm (the SKILL.md prompt instructs):**

1. Read triage JSON; validate.
2. For each `(file, annotations)` group:
   1. Read the target file (full content).
   2. Parse frontmatter; identify the `elements:` block (if any) for
      provisional-promotion handling.
   3. For each annotation:
      - **`category=add`** → append `- {body}` under the section the
        spec § Component 5 mapping table dictates (e.g. `## Behavior`,
        `## States`). Diff is templated; no LLM call.
      - **`category=remove`** → strikethrough the matching line as
        `~~{line}~~`. Diff is templated.
      - **`category=question`** → append `- {body}` under
        `## Open Questions` (create section if absent). Templated.
      - **`category=change`** → LLM call: read the target section's
        current prose, rewrite to incorporate the annotation's intent
        in the file's voice. Output a unified diff scoped to that
        section.
      - **If `specRef.provisional=true`** → also emit a second patch
        with `kind: "provisional-promotion"` editing the `elements:`
        frontmatter block.
3. For any annotation the agent cannot patch (empty body, contradictory
   intent, unrecoverable target): emit a `{annotationId, reason}` entry
   into `needs_manual: [...]` (top-level on `patches/<sid>.json`).
   These entries do NOT appear as checklist items in `review.md` —
   they are surfaced in the review.md preamble as a bullet list under
   a `## Needs manual review` heading, for the user to act on directly.
4. Write `patches/<sid>.json` (machine-readable) and
   `patches/<sid>.review.md` (human-readable, all auto-generated items
   pre-checked, `needs_manual` items unchecked).
5. Print summary: `N patches authored across M files; review at <path>`.

### `mockup-feedback-apply/SKILL.md`

**Tech:** Python 3 stdlib + git CLI. No LLM in this skill.

**Inputs:** `_concept/_feedback/patches/<sid>.json` + `patches/<sid>.review.md` (checklist state).

**Outputs:** edits in `_concept/`, `_feedback/devlog.md` append,
`_feedback/applied/<sid>.json`, one git commit.

**Algorithm:**

1. **Pre-flight checks (abort on failure):**
   - `applied/<sid>.json` does NOT exist (idempotency); else abort
     unless `--force`.
   - Working tree clean (no unstaged or untracked-relevant changes);
     else abort with the user's `git status` echoed.
   - `patches.json` and `review.md` schemas valid.
2. Parse `review.md`: collect every checked patch ID. Cross-reference
   with `patches.json`; reject if any checked ID is missing in
   `patches.json`.
3. For each approved patch (best-effort):
   1. Apply the diff to the target file using a section-anchored
      Python rewriter (not `git apply` — diffs use header anchors,
      not line numbers, so they survive context drift better).
   2. On success: queue a devlog entry + an `applied` item.
   3. On failure (section header not found, frontmatter unparseable,
      file missing, etc.): record `{status: "failed", error: <msg>}`;
      revert the in-memory file content for that file (do not write to
      disk yet).
4. **All-failed short-circuit.** If zero patches succeeded: do **not**
   write `applied/<sid>.json`, do **not** append to `devlog.md`, do
   **not** create a git commit. Print failure summary and exit 2. The
   session can be retried after fixing the patches without `--force`,
   because no audit artifact was written.
5. Write all successful in-memory file contents to disk in one pass.
6. Append the session's devlog block to `_feedback/devlog.md` (only
   succeeded items contribute lines).
7. Write `applied/<sid>.json` with all items (succeeded + failed). No
   `commitSha` field — the commit subject embeds the session ID
   (per D7).
8. Stage edited files + `devlog.md` + `applied/<sid>.json`. Run
   `git commit -m "feedback: apply session <sid> (N applied, K failed)"`.
   Single commit, no amend.
9. On commit failure (hook rejection, etc.): roll back via
   `git restore --staged --worktree -- <files>` and **delete**
   `applied/<sid>.json` from the working tree (so the next attempt
   isn't locked out). Surface the hook output to the user verbatim.
10. Print summary: `N applied, K failed; session <sid> committed`.

---

## Failure modes & error handling

### Triage

- Session JSON missing/malformed → exit 1 with line-pointed error.
- Annotation has no `specRef` → impossible per 3A overlay invariants;
  defensive path → `unresolved` with reason.
- Resolved file path doesn't exist → `unresolved`; **does not abort**
  (other annotations still triaged).
- All annotations unresolved → still emits `triage/<sid>.json`
  (`groups: []`, populated `unresolved`); exits 0 with warning.

### Patch

Three failure classes:

- *Skill-prompt failures* (LLM cannot author a `change` diff): emit a
  `{annotationId, reason}` entry into the top-level `needs_manual: []`
  array on `patches/<sid>.json`. The annotation does NOT appear as a
  patch in `patches[]` and does NOT appear as a checklist item in
  `review.md` — it surfaces in the `review.md` preamble as a bullet
  under `## Needs manual review` for the user to handle directly.
- *Section not found* (e.g. `add` template targets `## States` but file
  has no such header): emit the patch with `kind: "create-section"` —
  the diff includes the section creation. No abort.
- *Frontmatter parse failure*: skip the provisional-promotion patch
  for that file; surface as a warning in summary. Content patches
  still proceed.

### Apply

- Working tree dirty → abort with `git status` echoed.
- `applied/<sid>.json` already exists (committed in HEAD) → abort
  unless `--force`. (Untracked / uncommitted `applied/<sid>.json` is
  not expected to appear under any code path; if one is found, the
  pre-flight working-tree-clean check catches it before idempotency.)
- Diff context drift: record the patch as `failed`; other patches
  continue.
- Git commit fails: roll back working tree AND delete the just-written
  `applied/<sid>.json`; surface hook output. Next run resumes cleanly,
  no `--force` needed.
- All patches fail → exit 2 without writing `applied/<sid>.json`,
  without devlog append, without commit. Session can be retried
  without `--force` after the underlying issue is fixed.

### Cross-cutting

- All three skills validate input JSON against schemas in
  `mockup-feedback/schemas/` before running. Mismatch → exit 1 with
  JSONPath to the bad field.
- All three accept `--dry-run` (don't write outputs; print intent).

---

## Test strategy

Pattern lifted from 3A: `validator.py` per skill +
`tests/run_validator.sh` runs PASS and FAIL fixtures. No browser tests
(those are deferred to Task 3F).

**Shared fixture:** `mockup-feedback/_test-fixtures/sessions/01J-minimal.json`
— hand-authored session JSON with one annotation per `category`,
including a `provisional: true` element. Built atop the same `_concept/`
minimal directory that 3A's static-html test consumes, so target files
actually exist.

### `mockup-feedback/triage/tests/`

- `fixtures/01J-minimal.json` (input session) → `expected/01J-minimal.triage.json` (golden output).
- `fixtures/01J-bad-ref.json` (annotation with `specRef.screen="nonexistent"`) → expected `triage.json` with that annotation in `unresolved`.
- `validator.py` checks: every annotation appears in either `groups` or
  `unresolved`; no duplicates; every group's `file` exists in
  `_concept/`.

### `mockup-feedback/patch/tests/`

LLM nondeterminism — golden-master not viable for diff text.

- `fixtures/01J-minimal.triage.json` → patch run produces
  `patches/01J-minimal.json` + `review.md`.
- `validator.py` checks **structural properties**:
  - Every input annotation appears in EXACTLY ONE of: `patches[]`
    (one or more entries) OR `needs_manual[]` (one entry). Asserts the
    partitioning invariant from §Architecture.
  - Every patch's `file` matches its annotation's resolved file.
  - Every patch's diff is parseable as a unified diff.
  - For each annotation with `provisional: true` that lands in
    `patches[]`, exactly one `kind: "provisional-promotion"` patch
    exists for it.
  - Every entry in `patches[]` has a corresponding `- [x]` checklist
    item in `review.md`.
  - Every entry in `needs_manual[]` appears as a bullet under the
    `## Needs manual review` preamble in `review.md` and has NO
    checklist item anywhere.
  - The `add`/`remove`/`question` patches match deterministic templates
    (regex assertions on the diff text).
- A second fixture (`01J-empty-body.triage.json`) exercises the
  `needs_manual` path — annotation has empty body. Validator confirms:
  the annotation appears in `needs_manual[]`, is absent from
  `patches[]`, has no checklist item, and is rendered as a bullet
  under `## Needs manual review` in `review.md`.

### `mockup-feedback/apply/tests/`

- `fixtures/before/` — pre-apply `_concept/` snapshot +
  `patches/01J-minimal.json` + `review.md` (all checked).
- `fixtures/after/` — expected `_concept/` snapshot + expected
  `applied/01J-minimal.json` + expected devlog block.
- `tests/run_apply.sh`: copy `before/` to a temp dir, init a throwaway
  git repo, run apply, diff against `after/`. Asserts working-tree
  state + commit message + `applied/<sid>.json` content.
  (Drops `appliedAt` and any other volatile fields before diff.)
- A second fixture has one patch with a deliberately-broken diff
  (section header missing) → expected outcome: 1 applied, 1 failed;
  `applied/<sid>.json` records failure; devlog only mentions the
  applied one.
- A third fixture has *every* patch's section header missing →
  expected outcome (all-failed short-circuit): exit 2, no commit,
  no `applied/<sid>.json` written, no devlog append, working tree
  unchanged. Asserts the no-lockout retry path: a re-run with the
  same inputs must again exit 2 cleanly without `--force`.

### Domain-level

- `mockup-feedback/DOMAIN.md` updated to list all four skills (annotate
  from 3A, plus triage/patch/apply) with one-line summaries each.

---

## Out of scope (deferred to other tasks)

- **End-to-end browser test** (open walkthrough, click, annotate,
  triage, patch, apply, verify regen) — Task 3F.
- **Pixel-anchor / unattributable annotations** — handled in 3A overlay
  (or a future revision); 3B operates only on annotations that already
  have a resolved `specRef` from the overlay.
- **forge-concept consumer surfaces** (`/api/feedback/*` routes,
  `FeedbackDrawer.vue`) — tracked in forge-concept's own spec.
- **Devlog rollup at 500 entries** — Task 3E (`lab/archive`).
- **Multi-user merge / conflict resolution** beyond last-write-wins —
  REFACTOR_MOCKUP.md §11 row 9 defers to a future revision.
- **Lit / Astro renderer support** — Task 3C; 3B depends only on the
  session JSON contract, not on which renderer produced it.
