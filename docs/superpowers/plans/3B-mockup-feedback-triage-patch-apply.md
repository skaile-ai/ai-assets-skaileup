# 3B mockup-feedback-{triage,patch,apply} Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build three skills — `mockup-feedback-triage`, `mockup-feedback-patch`, `mockup-feedback-apply` — that process per-session annotation JSONs (from 3A) into section-anchored diffs, review them via checklist, and apply them as a git commit.

**Architecture:** Three skills run in sequence with no shared orchestrator. Triage is a deterministic Python script (pure routing, no LLM). Patch is an AI-agent prompt that authors diffs (LLM-driven for `change`; templated for `add`/`remove`/`question`). Apply is a deterministic Python script that parses the review.md checklist, applies section-anchored diffs to `_concept/` files, and creates one git commit. Input/output is plain JSON + markdown; no databases, no external services.

**Tech Stack:** Python 3 stdlib only (`triage.py`, `apply.py`, validators); vanilla Markdown for `review.md`; git CLI for commit; ULID/UUID session IDs (short test strings for fixtures).

**Prereqs read before starting:**
- `docs/superpowers/specs/2026-05-09-3B-mockup-feedback-triage-patch-apply-design.md` — binding design decisions D1–D7
- `docs/superpowers/plans/3A-mockup-feedback-annotate.md` — sibling plan template
- `contracts/elements_block.md` — `elements:` frontmatter schema, provisional ID rules
- `REFACTOR_MOCKUP.md` §5 (devlog format), §11 (resolved decisions)
- `mockup-feedback/annotate/overlay/annotation-overlay.js` — confirms session JSON shape: `{sessionId, annotations}`, no top-level `createdAt`

---

## File Map

| Path | Create/Modify | Responsibility |
|---|---|---|
| `mockup-feedback/schemas/session.schema.json` | Create | JSON Schema for session input |
| `mockup-feedback/schemas/triage.schema.json` | Create | JSON Schema for triage output |
| `mockup-feedback/schemas/patches.schema.json` | Create | JSON Schema for patches output |
| `mockup-feedback/_test-fixtures/concept/experience/screens/01_user_auth/login.md` | Create | Minimal `_concept/` screen for all 3B tests |
| `mockup-feedback/_test-fixtures/sessions/test-minimal.json` | Create | Session with change/add/question + provisional element |
| `mockup-feedback/_test-fixtures/sessions/test-bad-ref.json` | Create | Session with unresolvable specRef.screen |
| `mockup-feedback/triage/SKILL.md` | Create | Agent prompt: run triage.py |
| `mockup-feedback/triage/triage.py` | Create | Deterministic router: specRef → _concept/ path → groups |
| `mockup-feedback/triage/validator.py` | Create | Structural checks on triage JSON output |
| `mockup-feedback/triage/tests/expected/test-minimal.json` | Create | Golden triage output for test-minimal |
| `mockup-feedback/triage/tests/expected/test-bad-ref.json` | Create | Golden triage output with unresolved |
| `mockup-feedback/triage/tests/run_validator.sh` | Create | Pass + fail fixture runs |
| `mockup-feedback/patch/SKILL.md` | Create | LLM agent prompt: read triage JSON → author diffs |
| `mockup-feedback/patch/validator.py` | Create | Structural checks: partition invariant, diff parseability, review.md sync |
| `mockup-feedback/patch/tests/fixtures/test-minimal.triage.json` | Create | Triage output → input for patch run |
| `mockup-feedback/patch/tests/fixtures/test-empty-body.triage.json` | Create | Triage with empty-body annotation → exercises needs_manual |
| `mockup-feedback/patch/tests/run_validator.sh` | Create | Run patch skill + structural validator |
| `mockup-feedback/apply/SKILL.md` | Create | Agent prompt: run apply.py |
| `mockup-feedback/apply/apply.py` | Create | Section-anchored diff applier + git commit |
| `mockup-feedback/apply/validator.py` | Create | Checks applied/<sid>.json against patches + review.md |
| `mockup-feedback/apply/tests/fixtures/test-pass/` | Create | before/ + after/ for happy path |
| `mockup-feedback/apply/tests/fixtures/test-partial-fail/` | Create | before/ + after/ for 1-applied-1-failed |
| `mockup-feedback/apply/tests/fixtures/test-all-fail/` | Create | before/ for all-failed short-circuit |
| `mockup-feedback/apply/tests/run_apply.sh` | Create | git-repo integration tests (3 scenarios) |
| `mockup-feedback/DOMAIN.md` | Modify | Add triage/patch/apply to Skills list |

---

## Task 0: Shared schemas + concept fixture

**Files:**
- Create: `mockup-feedback/schemas/`
- Create: `mockup-feedback/_test-fixtures/`

- [ ] **Step 0.1: Create directory skeleton**

```bash
mkdir -p mockup-feedback/schemas
mkdir -p mockup-feedback/_test-fixtures/concept/experience/screens/01_user_auth
mkdir -p mockup-feedback/_test-fixtures/sessions
```

- [ ] **Step 0.2: Write `session.schema.json`**

Create `mockup-feedback/schemas/session.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Session",
  "type": "object",
  "required": ["sessionId", "annotations"],
  "properties": {
    "sessionId": { "type": "string", "minLength": 1 },
    "annotations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "sessionId", "specRef", "body", "category", "status"],
        "properties": {
          "id":        { "type": "string" },
          "sessionId": { "type": "string" },
          "createdAt": { "type": "string" },
          "specRef": {
            "type": "object",
            "required": ["element"],
            "properties": {
              "element":     { "type": "string" },
              "screen":      { "type": ["string", "null"] },
              "feature":     { "type": ["string", "null"] },
              "journey":     { "type": ["string", "null"] },
              "route":       { "type": ["string", "null"] },
              "provisional": { "type": "boolean" }
            }
          },
          "body":     { "type": "string" },
          "category": { "type": "string", "enum": ["change", "add", "remove", "question"] },
          "status":   { "type": "string", "enum": ["open", "applied", "dismissed"] }
        }
      }
    }
  },
  "additionalProperties": true
}
```

- [ ] **Step 0.3: Write `triage.schema.json`**

Create `mockup-feedback/schemas/triage.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Triage",
  "type": "object",
  "required": ["sessionId", "triagedAt", "groups", "unresolved"],
  "properties": {
    "sessionId":  { "type": "string" },
    "triagedAt":  { "type": "string" },
    "groups": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["file", "annotations"],
        "properties": {
          "file": { "type": "string" },
          "annotations": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "unresolved": {
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

- [ ] **Step 0.4: Write `patches.schema.json`**

Create `mockup-feedback/schemas/patches.schema.json`:

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
          "kind":         { "type": "string", "enum": ["content", "provisional-promotion", "create-section"] },
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

- [ ] **Step 0.5: Write the shared concept fixture**

Create `mockup-feedback/_test-fixtures/concept/experience/screens/01_user_auth/login.md`:

```markdown
---
title: Login Screen
implements:
  - experience/features/01_user_auth/auth.md
elements:
  - id: submit-button
    label: Sign In
    provisional: true
  - id: email-input
    label: Email
    provisional: false
---

# Login Screen

## Layout

- email-input: full-width text field
- submit-button: centered below form

## States

- default: form ready for input
- loading: spinner inside submit-button
```

Note: no `## Open Questions` section — `question` annotations will exercise `kind: "create-section"`.

- [ ] **Step 0.6: Write the shared session fixtures**

Create `mockup-feedback/_test-fixtures/sessions/test-minimal.json`:

```json
{
  "sessionId": "test-minimal",
  "annotations": [
    {
      "id": "ann-change-1",
      "sessionId": "test-minimal",
      "createdAt": "2026-05-09T14:23:11Z",
      "specRef": {
        "element": "submit-button",
        "screen": "01_user_auth/login",
        "provisional": true
      },
      "body": "this should be on the right",
      "category": "change",
      "status": "open"
    },
    {
      "id": "ann-add-1",
      "sessionId": "test-minimal",
      "createdAt": "2026-05-09T14:24:00Z",
      "specRef": {
        "element": "email-input",
        "screen": "01_user_auth/login",
        "provisional": false
      },
      "body": "add disabled state when loading",
      "category": "add",
      "status": "open"
    },
    {
      "id": "ann-question-1",
      "sessionId": "test-minimal",
      "createdAt": "2026-05-09T14:25:00Z",
      "specRef": {
        "element": "submit-button",
        "screen": "01_user_auth/login",
        "provisional": true
      },
      "body": "Should this submit or go to forgot password?",
      "category": "question",
      "status": "open"
    },
    {
      "id": "ann-remove-1",
      "sessionId": "test-minimal",
      "createdAt": "2026-05-09T14:26:00Z",
      "specRef": {
        "element": "email-input",
        "screen": "01_user_auth/login",
        "provisional": false
      },
      "body": "loading state is obvious, remove this line",
      "category": "remove",
      "status": "open"
    }
  ]
}
```

Create `mockup-feedback/_test-fixtures/sessions/test-bad-ref.json`:

```json
{
  "sessionId": "test-bad-ref",
  "annotations": [
    {
      "id": "ann-bad-1",
      "sessionId": "test-bad-ref",
      "createdAt": "2026-05-09T14:00:00Z",
      "specRef": {
        "element": "ghost-btn",
        "screen": "nonexistent/screen",
        "provisional": false
      },
      "body": "this screen does not exist",
      "category": "change",
      "status": "open"
    }
  ]
}
```

- [ ] **Step 0.7: Commit**

```bash
git add mockup-feedback/schemas/ mockup-feedback/_test-fixtures/
git commit -m "feat(mockup-feedback): schemas + shared concept + session fixtures for 3B

session/triage/patches JSON Schemas + minimal _concept/ login.md fixture
(provisional submit-button, add/change/question session test-minimal,
bad-ref session for unresolved triage path).

Phase 3 Task 3B step 0.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 1: Triage — triage.py + validator + tests + SKILL.md

**Files:**
- Create: `mockup-feedback/triage/SKILL.md`
- Create: `mockup-feedback/triage/triage.py`
- Create: `mockup-feedback/triage/validator.py`
- Create: `mockup-feedback/triage/tests/expected/`
- Create: `mockup-feedback/triage/tests/run_validator.sh`

- [ ] **Step 1.1: Create directory skeleton**

```bash
mkdir -p mockup-feedback/triage/tests/expected
```

- [ ] **Step 1.2: Write `triage.py`**

Create `mockup-feedback/triage/triage.py`:

```python
#!/usr/bin/env python3
"""triage.py — mockup-feedback-triage deterministic router.

Reads a session JSON, resolves each annotation's specRef to a _concept/ file path,
groups annotations by file, writes triage/<sid>.json.

Usage:
  python triage.py <session-json> <concept-root> <output-dir>

Exit codes:
  0  success (even if some annotations are unresolved)
  1  fatal error (bad args, malformed session JSON)
"""
from __future__ import annotations

import json
import sys
import datetime
from pathlib import Path


def resolve_file(spec_ref: dict, concept_root: Path) -> tuple[str | None, str | None]:
    """Resolve a specRef dict to a relative _concept/ path.

    Returns (relative_path, None) on success or (None, reason_string) on failure.
    Lookup priority: screen > feature > journey.
    """
    for key, subdir in [
        ("screen",  "experience/screens"),
        ("feature", "experience/features"),
        ("journey", "experience/journeys"),
    ]:
        val = spec_ref.get(key)
        if val:
            rel = f"{subdir}/{val}.md"
            if (concept_root / rel).is_file():
                return rel, None
            return None, f"file not found: _concept/{rel}"
    return None, "no specRef target (screen/feature/journey all absent or null)"


def triage_session(session: dict, concept_root: Path) -> dict:
    groups: dict[str, list[str]] = {}
    unresolved: list[dict] = []

    for ann in session.get("annotations", []):
        ann_id = ann.get("id", "<missing-id>")
        spec_ref = ann.get("specRef") or {}
        file_rel, reason = resolve_file(spec_ref, concept_root)
        if file_rel:
            groups.setdefault(file_rel, []).append(ann_id)
        else:
            unresolved.append({"annotationId": ann_id, "reason": reason})

    return {
        "sessionId": session["sessionId"],
        "triagedAt": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "groups": [{"file": f, "annotations": ids} for f, ids in groups.items()],
        "unresolved": unresolved,
    }


def main() -> int:
    if len(sys.argv) < 4:
        print(
            "Usage: python triage.py <session-json> <concept-root> <output-dir>",
            file=sys.stderr,
        )
        return 1

    session_path = Path(sys.argv[1])
    concept_root = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])

    try:
        session = json.loads(session_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot read session JSON: {exc}", file=sys.stderr)
        return 1

    if "sessionId" not in session or "annotations" not in session:
        print("ERROR: session JSON missing 'sessionId' or 'annotations'", file=sys.stderr)
        return 1

    result = triage_session(session, concept_root)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{session['sessionId']}.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    n_ann = len(session.get("annotations", []))
    n_groups = len(result["groups"])
    n_unresolved = len(result["unresolved"])
    print(
        f"{n_ann} annotation(s) triaged across {n_groups} file(s); "
        f"{n_unresolved} unresolved"
    )
    if result["unresolved"]:
        for u in result["unresolved"]:
            print(f"  UNRESOLVED {u['annotationId']}: {u['reason']}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 1.3: Run triage on test-minimal → verify output shape**

```bash
python mockup-feedback/triage/triage.py \
    mockup-feedback/_test-fixtures/sessions/test-minimal.json \
    mockup-feedback/_test-fixtures/concept \
    /tmp/triage-out

cat /tmp/triage-out/test-minimal.json
```

Expected: JSON with `groups` containing one entry for `experience/screens/01_user_auth/login.md` with 3 annotation IDs, `unresolved: []`.

- [ ] **Step 1.4: Write golden expected outputs**

Create `mockup-feedback/triage/tests/expected/test-minimal.json`
(copy from the run above, then manually remove `triagedAt` — the comparison script will strip it):

```json
{
  "sessionId": "test-minimal",
  "triagedAt": "__VOLATILE__",
  "groups": [
    {
      "file": "experience/screens/01_user_auth/login.md",
      "annotations": ["ann-change-1", "ann-add-1", "ann-question-1", "ann-remove-1"]
    }
  ],
  "unresolved": []
}
```

Create `mockup-feedback/triage/tests/expected/test-bad-ref.json`:

```json
{
  "sessionId": "test-bad-ref",
  "triagedAt": "__VOLATILE__",
  "groups": [],
  "unresolved": [
    {
      "annotationId": "ann-bad-1",
      "reason": "file not found: _concept/experience/screens/nonexistent/screen.md"
    }
  ]
}
```

- [ ] **Step 1.5: Write `validator.py`**

Create `mockup-feedback/triage/validator.py`:

```python
#!/usr/bin/env python3
"""validator.py — structural validator for triage output.

Usage:
  python validator.py <triage-json> [<session-json>]

Checks:
  - Every annotation in the session appears in exactly one of groups or unresolved.
  - No annotation ID appears in both groups and unresolved.
  - No annotation ID appears more than once across groups.
  - All group file paths are non-empty strings.
  - unresolved entries have annotationId + reason.

Exit codes: 0 PASS, 2 FAIL, 1 internal error.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


class Report:
    def __init__(self) -> None:
        self.violations: list[str] = []

    def add(self, msg: str) -> None:
        self.violations.append(msg)

    def ok(self) -> bool:
        return not self.violations

    def dump(self) -> None:
        for v in self.violations:
            print("FAIL", v)


def validate(triage: dict, session: dict | None, r: Report) -> None:
    groups = triage.get("groups", [])
    unresolved = triage.get("unresolved", [])

    grouped_ids: set[str] = set()
    for g in groups:
        if not g.get("file"):
            r.add("group has empty or missing 'file'")
        for aid in g.get("annotations", []):
            if aid in grouped_ids:
                r.add(f"annotation {aid!r} appears in multiple groups")
            grouped_ids.add(aid)

    unresolved_ids: set[str] = set()
    for u in unresolved:
        aid = u.get("annotationId")
        if not aid:
            r.add("unresolved entry missing 'annotationId'")
        if not u.get("reason"):
            r.add(f"unresolved entry {aid!r} missing 'reason'")
        if aid in unresolved_ids:
            r.add(f"annotation {aid!r} appears in unresolved more than once")
        unresolved_ids.add(aid)

    overlap = grouped_ids & unresolved_ids
    if overlap:
        r.add(f"annotation(s) appear in both groups and unresolved: {overlap}")

    if session:
        session_ids = {a.get("id") for a in session.get("annotations", [])}
        all_output = grouped_ids | unresolved_ids
        missing = session_ids - all_output
        extra = all_output - session_ids
        if missing:
            r.add(f"annotations in session but missing from triage output: {missing}")
        if extra:
            r.add(f"annotation IDs in triage output but not in session: {extra}")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python validator.py <triage-json> [<session-json>]", file=sys.stderr)
        return 1

    try:
        triage = json.loads(Path(sys.argv[1]).read_text())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    session = None
    if len(sys.argv) >= 3:
        try:
            session = json.loads(Path(sys.argv[2]).read_text())
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    r = Report()
    validate(triage, session, r)

    if r.ok():
        print(f"PASS  {sys.argv[1]}")
        return 0
    r.dump()
    return 2


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 1.6: Write `tests/run_validator.sh`**

Create `mockup-feedback/triage/tests/run_validator.sh`:

```bash
#!/usr/bin/env bash
# run_validator.sh — triage regression tests
# Run from mockup-feedback/triage/
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES_DIR="$SKILL_DIR/../../_test-fixtures"
CONCEPT_ROOT="$FIXTURES_DIR/concept"
SESSIONS_DIR="$FIXTURES_DIR/sessions"
EXPECTED_DIR="$SKILL_DIR/tests/expected"
TMP_OUT="$(mktemp -d)"
trap "rm -rf $TMP_OUT" EXIT

normalize_json() {
    # Strip volatile triagedAt field for comparison
    python3 -c "
import json, sys
d = json.load(sys.stdin)
d.pop('triagedAt', None)
print(json.dumps(d, indent=2, sort_keys=True))
"
}

compare_triage() {
    local sid="$1"
    local actual="$TMP_OUT/${sid}.json"
    local expected="$EXPECTED_DIR/${sid}.json"

    python3 "$SKILL_DIR/triage.py" \
        "$SESSIONS_DIR/${sid}.json" \
        "$CONCEPT_ROOT" \
        "$TMP_OUT" > /dev/null

    local actual_norm
    actual_norm=$(normalize_json < "$actual")
    local expected_norm
    expected_norm=$(normalize_json < "$expected")

    if [ "$actual_norm" != "$expected_norm" ]; then
        echo "FAIL: triage output for $sid differs from expected"
        diff <(echo "$expected_norm") <(echo "$actual_norm") || true
        return 1
    fi
    echo "OK: $sid triage matches expected"
}

echo "--- Test 1: test-minimal golden output ---"
compare_triage "test-minimal"

echo ""
echo "--- Test 2: test-bad-ref unresolved path ---"
compare_triage "test-bad-ref"

echo ""
echo "--- Test 3: structural validator on test-minimal output ---"
python3 "$SKILL_DIR/validator.py" \
    "$TMP_OUT/test-minimal.json" \
    "$SESSIONS_DIR/test-minimal.json"

echo ""
echo "--- Test 4: structural validator on test-bad-ref output ---"
python3 "$SKILL_DIR/validator.py" \
    "$TMP_OUT/test-bad-ref.json" \
    "$SESSIONS_DIR/test-bad-ref.json"

echo ""
echo "All triage tests passed."
```

```bash
chmod +x mockup-feedback/triage/tests/run_validator.sh
```

- [ ] **Step 1.7: Run test suite → must pass**

```bash
cd mockup-feedback/triage && bash tests/run_validator.sh; cd ../..
```

Expected final line: `All triage tests passed.`

- [ ] **Step 1.8: Write `SKILL.md`**

Create `mockup-feedback/triage/SKILL.md`:

```markdown
---
name: mockup-feedback-triage
description: "Routes each annotation in a session JSON to its target _concept/ file by resolving specRef.screen/feature/journey. Produces triage/<sid>.json grouped by file. Deterministic Python — no LLM. Second skill in the mockup-feedback cluster."
metadata:
  version: "0.1.0"
  tags: [mockup-feedback, triage, routing]
  stage: alpha
  prerequisites:
    files:
      - path: "_concept/_feedback/sessions/"
        gate: hard
        description: "At least one session JSON from mockup-feedback-annotate"
        min_entries: 1
    reads:
      - path: "_concept/"
        description: "Resolves specRef paths against this directory"
    produces:
      - path: "_concept/_feedback/triage/<sid>.json"
        description: "Grouped annotation list per _concept/ file"
---

# mockup-feedback-triage

## Overview

Routes every annotation in a session JSON to the `_concept/` file it targets,
by resolving `specRef.screen`, `specRef.feature`, or `specRef.journey` in that
priority order. Groups annotations by resolved file and emits `triage/<sid>.json`.
No LLM call — pure deterministic Python.

Run after `mockup-feedback-annotate`. Run `mockup-feedback-patch` next.

---

## Step 1 — Locate unprocessed sessions

Default sessions directory: `_concept/_feedback/sessions/`

A session is unprocessed if no corresponding `_concept/_feedback/triage/<sid>.json`
exists. Process all unprocessed sessions (or a single session specified via
`PARAMETERS.session_id`).

---

## Step 2 — Run `triage.py` for each session

```bash
python <skill-dir>/triage.py \
    _concept/_feedback/sessions/<sid>.json \
    _concept/ \
    _concept/_feedback/triage/
```

The script exits 0 even if some annotations are unresolved — unresolved items
are recorded in the output JSON, not silently dropped.

---

## Step 3 — Report

Print for each session:

```
triage complete: <sid>
  N annotations → M file(s)
  K unresolved (see _concept/_feedback/triage/<sid>.json#/unresolved)
Next: run mockup-feedback-patch on _concept/_feedback/triage/<sid>.json
```

For unresolved items, print the reason for each.

---

## Inputs

| Name | Type | Default |
|---|---|---|
| `session_id` | string | (all unprocessed sessions) |

## Outputs

| Path | Description |
|---|---|
| `_concept/_feedback/triage/<sid>.json` | Grouped annotations + unresolved list |

## References

- `mockup-feedback/schemas/session.schema.json` — input validation
- `mockup-feedback/schemas/triage.schema.json` — output shape
- `docs/superpowers/specs/2026-05-09-3B-mockup-feedback-triage-patch-apply-design.md` D1
```

- [ ] **Step 1.9: Commit**

```bash
git add mockup-feedback/triage/
git commit -m "feat(mockup-feedback): triage skill — triage.py + validator + tests + SKILL.md

Deterministic Python router: specRef.screen/feature/journey → _concept/ path.
Golden test for test-minimal (3 annotations, 1 file) and test-bad-ref (unresolved).
Structural validator checks partition invariant against session JSON.

Phase 3 Task 3B step 1.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 2: Patch — SKILL.md + validator + tests

**Files:**
- Create: `mockup-feedback/patch/SKILL.md`
- Create: `mockup-feedback/patch/validator.py`
- Create: `mockup-feedback/patch/tests/fixtures/`
- Create: `mockup-feedback/patch/tests/run_validator.sh`

- [ ] **Step 2.1: Create directory skeleton**

```bash
mkdir -p mockup-feedback/patch/tests/fixtures
```

- [ ] **Step 2.2: Write test fixtures**

Create `mockup-feedback/patch/tests/fixtures/test-minimal.triage.json`
(the golden triage output from Task 1, with a real triagedAt timestamp):

```json
{
  "sessionId": "test-minimal",
  "triagedAt": "2026-05-09T14:30:00Z",
  "groups": [
    {
      "file": "experience/screens/01_user_auth/login.md",
      "annotations": ["ann-change-1", "ann-add-1", "ann-question-1", "ann-remove-1"]
    }
  ],
  "unresolved": []
}
```

Create `mockup-feedback/patch/tests/fixtures/test-empty-body.triage.json`
(one annotation with empty body — exercises `needs_manual` path):

```json
{
  "sessionId": "test-empty-body",
  "triagedAt": "2026-05-09T14:31:00Z",
  "groups": [
    {
      "file": "experience/screens/01_user_auth/login.md",
      "annotations": ["ann-empty-1"]
    }
  ],
  "unresolved": []
}
```

Note: The `test-empty-body` triage JSON references `ann-empty-1`. The patch
SKILL.md body instructs the agent: if `annotation.body` is empty or whitespace-only,
emit a `needs_manual` entry (not a patch). The validator confirms the annotation
ends up in `needs_manual` and nowhere else.

But the annotation data is in the session JSON, not the triage JSON. For the
validator to know the annotation body, it needs access to the session. Create
`mockup-feedback/patch/tests/fixtures/test-empty-body.session.json`:

```json
{
  "sessionId": "test-empty-body",
  "annotations": [
    {
      "id": "ann-empty-1",
      "sessionId": "test-empty-body",
      "createdAt": "2026-05-09T14:00:00Z",
      "specRef": {
        "element": "submit-button",
        "screen": "01_user_auth/login",
        "provisional": true
      },
      "body": "",
      "category": "change",
      "status": "open"
    }
  ]
}
```

- [ ] **Step 2.3: Write `validator.py`**

Create `mockup-feedback/patch/validator.py`:

```python
#!/usr/bin/env python3
"""validator.py — structural validator for patch skill output.

Usage:
  python validator.py <triage-json> <patches-json> <review-md> [<session-json>]

Checks (design spec §Test strategy):
  1. Partition invariant: every annotation in triage groups appears in exactly
     one of patches[] (one or more entries) OR needs_manual[] (one entry).
  2. Every patch's file matches its annotation's resolved file (from triage).
  3. Every patch diff starts with a valid @@ anchor header.
  4. For each annotation with provisional=true (from session) that has patches,
     exactly one kind=provisional-promotion patch exists.
  5. Every patches[] entry has a - [x] checklist item in review.md.
  6. Every needs_manual[] entry has a bullet under ## Needs manual review in
     review.md and NO checklist item.
  7. add/remove/question diffs match deterministic template patterns.

Exit codes: 0 PASS, 2 FAIL, 1 internal error.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


class Report:
    def __init__(self) -> None:
        self.violations: list[str] = []

    def add(self, msg: str) -> None:
        self.violations.append(msg)

    def ok(self) -> bool:
        return not self.violations

    def dump(self) -> None:
        for v in self.violations:
            print("FAIL", v)


def parse_checklist(review_md: str) -> tuple[set[str], set[str]]:
    """Returns (checked_ids, unchecked_ids) from review.md."""
    checked = set(re.findall(r"- \[x\] \*\*([^*]+)\*\*", review_md))
    unchecked = set(re.findall(r"- \[ \] \*\*([^*]+)\*\*", review_md))
    return checked, unchecked


def parse_needs_manual_bullets(review_md: str) -> set[str]:
    """Returns annotation IDs listed under ## Needs manual review."""
    section = re.search(
        r"## Needs manual review\s*(.*?)(?=^##|\Z)", review_md, re.DOTALL | re.MULTILINE
    )
    if not section:
        return set()
    return set(re.findall(r"annotation `([^`]+)`", section.group(1)))


def validate(
    triage: dict,
    patches_data: dict,
    review_md: str,
    session: dict | None,
    r: Report,
) -> None:
    # Build lookup maps
    patches_by_ann: dict[str, list[dict]] = {}
    patches_by_id:  dict[str, dict] = {}
    for p in patches_data.get("patches", []):
        patches_by_ann.setdefault(p["annotationId"], []).append(p)
        patches_by_id[p["id"]] = p

    nm_ann_ids = {nm["annotationId"] for nm in patches_data.get("needs_manual", [])}

    # Build annotation → resolved file map from triage
    ann_to_file: dict[str, str] = {}
    for grp in triage.get("groups", []):
        for aid in grp.get("annotations", []):
            ann_to_file[aid] = grp["file"]

    # 1. Partition invariant
    all_group_ann_ids = set(ann_to_file.keys())
    for aid in all_group_ann_ids:
        in_patches = aid in patches_by_ann
        in_nm = aid in nm_ann_ids
        if in_patches and in_nm:
            r.add(f"annotation {aid!r} appears in both patches[] and needs_manual[]")
        elif not in_patches and not in_nm:
            r.add(f"annotation {aid!r} not in patches[] or needs_manual[] (partition invariant)")

    # 2. Every patch file matches triage-resolved file
    for p in patches_data.get("patches", []):
        expected_file = ann_to_file.get(p["annotationId"])
        if expected_file and p.get("file") != expected_file:
            r.add(
                f"patch {p['id']!r}: file={p['file']!r} but triage resolved "
                f"{p['annotationId']!r} to {expected_file!r}"
            )

    # 3. Diff @@ anchor header present
    for p in patches_data.get("patches", []):
        diff = p.get("diff", "")
        first_line = diff.split("\n")[0] if diff else ""
        if not re.match(r"^@@ .+ @@$", first_line.strip()):
            r.add(f"patch {p['id']!r}: diff missing valid @@ anchor header")

    # 4. Provisional-promotion patch present for provisional annotations
    if session:
        ann_by_id = {a["id"]: a for a in session.get("annotations", [])}
        for aid, file_path in ann_to_file.items():
            ann = ann_by_id.get(aid)
            if not ann:
                continue
            if ann.get("specRef", {}).get("provisional") and aid in patches_by_ann:
                promo_patches = [
                    p for p in patches_by_ann[aid]
                    if p.get("kind") == "provisional-promotion"
                ]
                if not promo_patches:
                    r.add(
                        f"annotation {aid!r} has provisional=true and patches, "
                        "but no kind=provisional-promotion patch"
                    )

    # 5. Every patches[] entry has a - [x] checklist item in review.md
    checked_ids, _ = parse_checklist(review_md)
    for p in patches_data.get("patches", []):
        if p["id"] not in checked_ids:
            r.add(f"patch {p['id']!r} is in patches[] but has no - [x] item in review.md")

    # 6. Every needs_manual[] entry is in review.md preamble, not in checklist
    nm_in_review = parse_needs_manual_bullets(review_md)
    all_checklist_ids = checked_ids | _
    for nm in patches_data.get("needs_manual", []):
        aid = nm["annotationId"]
        if aid not in nm_in_review:
            r.add(
                f"needs_manual annotation {aid!r} is not listed under "
                "## Needs manual review in review.md"
            )
        if any(p["id"] for p in patches_data.get("patches", []) if p["annotationId"] == aid):
            r.add(f"needs_manual annotation {aid!r} also has patches[] entries (partition violation)")

    # 7. Template pattern checks for add/remove/question patches
    for p in patches_data.get("patches", []):
        ann = None
        if session:
            ann = {a["id"]: a for a in session.get("annotations", [])}.get(p["annotationId"])
        cat = p.get("category")
        diff = p.get("diff", "")
        if cat == "add":
            if not re.search(r"^\+", diff, re.MULTILINE):
                r.add(f"patch {p['id']!r}: category=add diff has no + lines")
        elif cat == "remove":
            if not re.search(r"^-", diff, re.MULTILINE):
                r.add(f"patch {p['id']!r}: category=remove diff has no - lines")
        elif cat == "question":
            if "Open Questions" not in diff:
                r.add(
                    f"patch {p['id']!r}: category=question diff should target "
                    "## Open Questions section"
                )


def main() -> int:
    if len(sys.argv) < 4:
        print(
            "Usage: python validator.py <triage-json> <patches-json> <review-md> [<session-json>]",
            file=sys.stderr,
        )
        return 1

    try:
        triage      = json.loads(Path(sys.argv[1]).read_text())
        patches_data = json.loads(Path(sys.argv[2]).read_text())
        review_md   = Path(sys.argv[3]).read_text()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    session = None
    if len(sys.argv) >= 5:
        try:
            session = json.loads(Path(sys.argv[4]).read_text())
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    r = Report()
    validate(triage, patches_data, review_md, session, r)

    if r.ok():
        print(f"PASS  {sys.argv[2]}")
        return 0
    r.dump()
    return 2


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2.4: Write `tests/run_validator.sh`**

The patch skill is LLM-driven, so `run_validator.sh` instructs the agent to
run the patch skill against each fixture and then validate the output.

Create `mockup-feedback/patch/tests/run_validator.sh`:

```bash
#!/usr/bin/env bash
# run_validator.sh — structural validation for patch skill output.
#
# IMPORTANT: This script does NOT run the LLM. It validates a patches output
# that a human or agent has already produced. Run it AFTER the patch skill
# has generated patches/<sid>.json and patches/<sid>.review.md.
#
# Usage (from mockup-feedback/patch/):
#   bash tests/run_validator.sh <patches-json> <review-md> <triage-json> [<session-json>]
#
# For CI / batch mode, the agent should:
#   1. Run the patch SKILL.md against each fixture triage JSON.
#   2. Call this script on the output.
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "$#" -lt 3 ]; then
    echo "Usage: bash run_validator.sh <patches-json> <review-md> <triage-json> [<session-json>]"
    exit 1
fi

PATCHES="$1"
REVIEW="$2"
TRIAGE="$3"
SESSION="${4:-}"

echo "--- Structural validation: $(basename "$PATCHES") ---"
if [ -n "$SESSION" ]; then
    python3 "$SKILL_DIR/validator.py" "$TRIAGE" "$PATCHES" "$REVIEW" "$SESSION"
else
    python3 "$SKILL_DIR/validator.py" "$TRIAGE" "$PATCHES" "$REVIEW"
fi

echo "Patch validation passed."
```

```bash
chmod +x mockup-feedback/patch/tests/run_validator.sh
```

- [ ] **Step 2.5: Write `SKILL.md`**

Create `mockup-feedback/patch/SKILL.md`:

```markdown
---
name: mockup-feedback-patch
description: "Reads triage/<sid>.json, authors section-anchored diffs for each annotation (LLM for change; templated for add/remove/question), emits patches/<sid>.json + patches/<sid>.review.md. Third skill in the mockup-feedback cluster."
metadata:
  version: "0.1.0"
  tags: [mockup-feedback, patch, diff, review]
  stage: alpha
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
| `session_id` | string | (all untriaged sessions) |
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
```

- [ ] **Step 2.6: Verify validator parses correctly**

```bash
python -c "
import re, sys
from pathlib import Path
text = Path('mockup-feedback/patch/SKILL.md').read_text()
m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
assert m, 'No frontmatter'
assert 'name: mockup-feedback-patch' in m.group(1)
print('SKILL.md OK')

import ast, py_compile
py_compile.compile('mockup-feedback/patch/validator.py', doraise=True)
print('validator.py OK')
"
```

Expected: `SKILL.md OK` then `validator.py OK`.

- [ ] **Step 2.7: Commit**

```bash
git add mockup-feedback/patch/
git commit -m "feat(mockup-feedback): patch skill — SKILL.md + structural validator + fixtures

LLM-driven diff authoring (change=LLM, add/remove/question=templated).
Validator checks partition invariant, diff parseability, provisional-promotion
presence, review.md checklist sync. Fixtures for test-minimal and test-empty-body.

Phase 3 Task 3B step 2.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 3: Apply — `apply.py` (TDD)

**Files:**
- Create: `mockup-feedback/apply/apply.py`
- Create: `mockup-feedback/apply/tests/fixtures/test-pass/`
- Create: `mockup-feedback/apply/tests/fixtures/test-partial-fail/`
- Create: `mockup-feedback/apply/tests/fixtures/test-all-fail/`

- [ ] **Step 3.1: Create directory skeleton**

```bash
mkdir -p mockup-feedback/apply/tests/fixtures/test-pass/before/{concept/experience/screens/01_user_auth,_feedback/{patches,applied}}
mkdir -p mockup-feedback/apply/tests/fixtures/test-pass/after/{concept/experience/screens/01_user_auth,_feedback/{applied}}
mkdir -p mockup-feedback/apply/tests/fixtures/test-partial-fail/before/{concept/experience/screens/01_user_auth,_feedback/patches}
mkdir -p mockup-feedback/apply/tests/fixtures/test-partial-fail/after/{concept/experience/screens/01_user_auth,_feedback/applied}
mkdir -p mockup-feedback/apply/tests/fixtures/test-all-fail/before/{concept/experience/screens/01_user_auth,_feedback/patches}
```

- [ ] **Step 3.2: Write `test-pass` before-state**

Create `mockup-feedback/apply/tests/fixtures/test-pass/before/concept/experience/screens/01_user_auth/login.md`:

```markdown
---
title: Login Screen
elements:
  - id: submit-button
    kind: button
    label: Sign In
    states: [default, loading]
    provisional: true
  - id: email-input
    kind: input
    label: Email
    states: [default, disabled]
    provisional: false
---

# Login Screen

## Layout

- email-input: full-width text field
- submit-button: centered below form

## States

- default: form ready for input
- loading: spinner inside submit-button
```

Create `mockup-feedback/apply/tests/fixtures/test-pass/before/_feedback/patches/test-pass.json`:

```json
{
  "sessionId": "test-pass",
  "proposedAt": "2026-05-09T14:35:00Z",
  "patches": [
    {
      "id": "p-ann-c1-content",
      "annotationId": "ann-c1",
      "file": "experience/screens/01_user_auth/login.md",
      "section": "## Layout",
      "kind": "content",
      "category": "change",
      "body": "this should be on the right",
      "diff": "@@ ## Layout @@\n-- submit-button: centered below form\n+- submit-button: right-aligned below form\n"
    },
    {
      "id": "p-ann-c1-promotion",
      "annotationId": "ann-c1",
      "file": "experience/screens/01_user_auth/login.md",
      "section": "frontmatter:elements",
      "kind": "provisional-promotion",
      "category": null,
      "body": "this should be on the right",
      "diff": "@@ frontmatter:elements @@\n-  - id: submit-button\n-    kind: button\n-    label: Sign In\n-    states: [default, loading]\n-    provisional: true\n+  - id: submit-button\n+    kind: button\n+    label: Sign In\n+    states: [default, loading]\n+    provisional: false\n"
    }
  ],
  "needs_manual": []
}
```

Create `mockup-feedback/apply/tests/fixtures/test-pass/before/_feedback/patches/test-pass.review.md`:

```markdown
# Review patches for session test-pass (2 patches across 1 file)

## experience/screens/01_user_auth/login.md

- [x] **p-ann-c1-content** · category=change · annotation: "this should be on the right"
  ```diff
  @@ ## Layout @@
  -- submit-button: centered below form
  +- submit-button: right-aligned below form
  ```

- [x] **p-ann-c1-promotion** · provisional ID promotion for `submit-button`
  ```diff
  @@ frontmatter:elements @@
  -  - id: submit-button
  -    kind: button
  -    label: Sign In
  -    states: [default, loading]
  -    provisional: true
  +  - id: submit-button
  +    kind: button
  +    label: Sign In
  +    states: [default, loading]
  +    provisional: false
  ```
```

- [ ] **Step 3.3: Write `test-pass` after-state**

Create `mockup-feedback/apply/tests/fixtures/test-pass/after/concept/experience/screens/01_user_auth/login.md`:

```markdown
---
title: Login Screen
elements:
  - id: submit-button
    kind: button
    label: Sign In
    states: [default, loading]
    provisional: false
  - id: email-input
    kind: input
    label: Email
    states: [default, disabled]
    provisional: false
---

# Login Screen

## Layout

- email-input: full-width text field
- submit-button: right-aligned below form

## States

- default: form ready for input
- loading: spinner inside submit-button
```

Create `mockup-feedback/apply/tests/fixtures/test-pass/after/_feedback/applied/test-pass.json`:

```json
{
  "sessionId": "test-pass",
  "appliedAt": "__VOLATILE__",
  "items": [
    {
      "annotationId": "ann-c1",
      "patchId": "p-ann-c1-content",
      "target": {
        "file": "experience/screens/01_user_auth/login.md",
        "section": "## Layout",
        "category": "change"
      },
      "body": "this should be on the right",
      "status": "applied"
    },
    {
      "annotationId": "ann-c1",
      "patchId": "p-ann-c1-promotion",
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

- [ ] **Step 3.4: Write `test-partial-fail` fixtures**

Create `mockup-feedback/apply/tests/fixtures/test-partial-fail/before/concept/experience/screens/01_user_auth/login.md`:
(Same content as `test-pass/before/concept/...login.md` above — copy it.)

Create `mockup-feedback/apply/tests/fixtures/test-partial-fail/before/_feedback/patches/test-partial-fail.json`:

```json
{
  "sessionId": "test-partial-fail",
  "proposedAt": "2026-05-09T14:36:00Z",
  "patches": [
    {
      "id": "p-good",
      "annotationId": "ann-good",
      "file": "experience/screens/01_user_auth/login.md",
      "section": "## Layout",
      "kind": "content",
      "category": "change",
      "body": "right-align the button",
      "diff": "@@ ## Layout @@\n-- submit-button: centered below form\n+- submit-button: right-aligned below form\n"
    },
    {
      "id": "p-bad",
      "annotationId": "ann-bad",
      "file": "experience/screens/01_user_auth/login.md",
      "section": "## NONEXISTENT SECTION",
      "kind": "content",
      "category": "change",
      "body": "change something",
      "diff": "@@ ## NONEXISTENT SECTION @@\n-- some line\n+- replacement\n"
    }
  ],
  "needs_manual": []
}
```

Create `mockup-feedback/apply/tests/fixtures/test-partial-fail/before/_feedback/patches/test-partial-fail.review.md`:

```markdown
# Review patches for session test-partial-fail (2 patches)

## experience/screens/01_user_auth/login.md

- [x] **p-good** · category=change · annotation: "right-align the button"
  ```diff
  @@ ## Layout @@
  -- submit-button: centered below form
  +- submit-button: right-aligned below form
  ```

- [x] **p-bad** · category=change · annotation: "change something"
  ```diff
  @@ ## NONEXISTENT SECTION @@
  -- some line
  +- replacement
  ```
```

The `test-partial-fail` after-state: the login.md has the `## Layout` change
applied; `applied/test-partial-fail.json` records p-good as `applied` and
p-bad as `failed`. (Write these as before for test-pass but with the appropriate
`items` array.)

Create `mockup-feedback/apply/tests/fixtures/test-partial-fail/after/concept/experience/screens/01_user_auth/login.md`:

```markdown
---
title: Login Screen
elements:
  - id: submit-button
    kind: button
    label: Sign In
    states: [default, loading]
    provisional: true
  - id: email-input
    kind: input
    label: Email
    states: [default, disabled]
    provisional: false
---

# Login Screen

## Layout

- email-input: full-width text field
- submit-button: right-aligned below form

## States

- default: form ready for input
- loading: spinner inside submit-button
```

Create `mockup-feedback/apply/tests/fixtures/test-partial-fail/after/_feedback/applied/test-partial-fail.json`:

```json
{
  "sessionId": "test-partial-fail",
  "appliedAt": "__VOLATILE__",
  "items": [
    {
      "annotationId": "ann-good",
      "patchId": "p-good",
      "target": {
        "file": "experience/screens/01_user_auth/login.md",
        "section": "## Layout",
        "category": "change"
      },
      "body": "right-align the button",
      "status": "applied"
    },
    {
      "annotationId": "ann-bad",
      "patchId": "p-bad",
      "target": {
        "file": "experience/screens/01_user_auth/login.md",
        "section": "## NONEXISTENT SECTION",
        "category": "change"
      },
      "body": "change something",
      "status": "failed",
      "error": "section not found: '## NONEXISTENT SECTION'"
    }
  ]
}
```

- [ ] **Step 3.5: Write `test-all-fail` fixtures**

Create `mockup-feedback/apply/tests/fixtures/test-all-fail/before/concept/experience/screens/01_user_auth/login.md`:
(Same as `test-pass/before/concept/...login.md`.)

Create `mockup-feedback/apply/tests/fixtures/test-all-fail/before/_feedback/patches/test-all-fail.json`:

```json
{
  "sessionId": "test-all-fail",
  "proposedAt": "2026-05-09T14:37:00Z",
  "patches": [
    {
      "id": "p-fail-1",
      "annotationId": "ann-fail-1",
      "file": "experience/screens/01_user_auth/login.md",
      "section": "## GHOST SECTION",
      "kind": "content",
      "category": "change",
      "body": "ghost",
      "diff": "@@ ## GHOST SECTION @@\n-- does not exist\n+- replacement\n"
    }
  ],
  "needs_manual": []
}
```

Create `mockup-feedback/apply/tests/fixtures/test-all-fail/before/_feedback/patches/test-all-fail.review.md`:

```markdown
# Review patches for session test-all-fail (1 patch)

## experience/screens/01_user_auth/login.md

- [x] **p-fail-1** · category=change · annotation: "ghost"
  ```diff
  @@ ## GHOST SECTION @@
  -- does not exist
  +- replacement
  ```
```

- [ ] **Step 3.6: Write `apply.py`**

Create `mockup-feedback/apply/apply.py`:

```python
#!/usr/bin/env python3
"""apply.py — mockup-feedback-apply deterministic patcher.

Parses review.md checklist, applies approved section-anchored diffs to _concept/
files (best-effort), appends devlog, writes applied/<sid>.json, creates one git commit.

Usage:
  python apply.py <patches-json> <review-md> <concept-root> <feedback-root> [--force] [--dry-run]

Exit codes:
  0  success (at least one patch applied)
  1  pre-flight failure (dirty tree, already applied, schema error)
  2  all-failed short-circuit (no patches applied; no artifacts written)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import datetime
from pathlib import Path


# ── Diff application ──────────────────────────────────────────────────────────

def apply_section_diff(file_content: str, diff_text: str) -> tuple[str, str | None]:
    """Apply a section-anchored diff. Returns (new_content, error_or_None)."""
    lines = diff_text.strip().splitlines()
    if not lines:
        return file_content, "empty diff"
    m = re.match(r"^@@ (.+?) @@$", lines[0].strip())
    if not m:
        return file_content, f"diff missing valid @@ anchor header: {lines[0]!r}"

    anchor  = m.group(1)
    removes = [l[1:] for l in lines[1:] if l.startswith("-")]
    adds    = [l[1:] for l in lines[1:] if l.startswith("+")]

    if anchor == "frontmatter:elements":
        return _patch_frontmatter(file_content, removes, adds)
    return _patch_section(file_content, anchor, removes, adds)


def _patch_section(content: str, section_header: str, removes: list[str], adds: list[str]) -> tuple[str, str | None]:
    file_lines = content.splitlines(keepends=True)

    # Locate section header line
    sec_start = None
    for i, line in enumerate(file_lines):
        if line.rstrip("\n") == section_header:
            sec_start = i
            break

    if sec_start is None:
        if removes:
            return content, f"section not found: {section_header!r}"
        # create-section: append to end of file
        insert = "".join(a + "\n" for a in adds)
        return content + ("\n" if not content.endswith("\n") else "") + insert, None

    # Find section body range (up to next heading or EOF)
    sec_end = len(file_lines)
    for i in range(sec_start + 1, len(file_lines)):
        if re.match(r"^#{1,6} ", file_lines[i]):
            sec_end = i
            break

    body = [l.rstrip("\n") for l in file_lines[sec_start + 1:sec_end]]

    if not removes:
        # Pure insert at end of section body
        new_lines = (
            file_lines[:sec_end]
            + [a + "\n" for a in adds]
            + file_lines[sec_end:]
        )
        return "".join(new_lines), None

    # Find consecutive removes block
    try:
        start_idx = body.index(removes[0])
    except ValueError:
        return content, f"remove line not found in {section_header!r}: {removes[0]!r}"

    for offset, r in enumerate(removes):
        if start_idx + offset >= len(body) or body[start_idx + offset] != r:
            return content, (
                f"remove lines not consecutive in {section_header!r} at offset {offset}: "
                f"expected {r!r}"
            )

    new_body = body[:start_idx] + adds + body[start_idx + len(removes):]
    new_body_lines = [l + "\n" for l in new_body]
    new_lines = file_lines[:sec_start + 1] + new_body_lines + file_lines[sec_end:]
    return "".join(new_lines), None


def _patch_frontmatter(content: str, removes: list[str], adds: list[str]) -> tuple[str, str | None]:
    if not content.startswith("---\n"):
        return content, "file does not start with frontmatter ---"
    close = content.find("\n---\n", 4)
    if close < 0:
        return content, "frontmatter closing --- not found"

    fm_lines = content[4:close].splitlines()
    rest     = content[close + 5:]

    if not removes:
        return content, "provisional-promotion diff must have at least one remove line"

    try:
        start = fm_lines.index(removes[0])
    except ValueError:
        return content, f"frontmatter remove line not found: {removes[0]!r}"

    for offset, r in enumerate(removes):
        if start + offset >= len(fm_lines) or fm_lines[start + offset] != r:
            return content, f"frontmatter remove block not consecutive at offset {offset}"

    new_fm = "\n".join(fm_lines[:start] + adds + fm_lines[start + len(removes):])
    return "---\n" + new_fm + "\n---\n" + rest, None


# ── Review.md parsing ─────────────────────────────────────────────────────────

def parse_checked_ids(review_md: str) -> set[str]:
    return set(re.findall(r"- \[x\] \*\*([^*]+)\*\*", review_md))


# ── Devlog ────────────────────────────────────────────────────────────────────

def build_devlog_block(session_id: str, items: list[dict]) -> str:
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    by_file: dict[str, list[dict]] = {}
    for item in items:
        if item["status"] == "applied":
            f = item["target"]["file"]
            by_file.setdefault(f, []).append(item)

    lines = [f"\n## {today} · session {session_id}\n"]
    for f, file_items in by_file.items():
        lines.append(f"### {f}\n")
        for item in file_items:
            cat = item["target"].get("category") or "derived"
            body = (item.get("body") or "")[:80]
            lines.append(f"- {item['patchId']} applied ({cat}): {body!r}\n")
        lines.append("\n")
    return "".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    raw_args = sys.argv[1:]
    dry_run = "--dry-run" in raw_args
    force   = "--force"   in raw_args
    args    = [a for a in raw_args if not a.startswith("--")]

    if len(args) < 4:
        print(
            "Usage: python apply.py <patches-json> <review-md> "
            "<concept-root> <feedback-root> [--force] [--dry-run]",
            file=sys.stderr,
        )
        return 1

    patches_path  = Path(args[0])
    review_path   = Path(args[1])
    concept_root  = Path(args[2])
    feedback_root = Path(args[3])

    # Load inputs
    try:
        patches_data = json.loads(patches_path.read_text())
        review_md    = review_path.read_text()
    except Exception as exc:
        print(f"ERROR: cannot read input files: {exc}", file=sys.stderr)
        return 1

    sid = patches_data.get("sessionId", "unknown")
    applied_path = feedback_root / "applied" / f"{sid}.json"
    devlog_path  = feedback_root / "devlog.md"

    # Pre-flight: idempotency
    if applied_path.exists() and not force:
        print(
            f"ERROR: session {sid!r} already applied "
            f"(found {applied_path}). Use --force to re-apply.",
            file=sys.stderr,
        )
        return 1

    # Pre-flight: working tree clean
    if not dry_run:
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True
        )
        if result.stdout.strip():
            print("ERROR: working tree is dirty. Commit or stash changes first.", file=sys.stderr)
            print(result.stdout, file=sys.stderr)
            return 1

    # Parse review.md
    checked_ids = parse_checked_ids(review_md)
    if not checked_ids:
        print("WARNING: no checked patches in review.md — nothing to apply.", file=sys.stderr)
        return 0

    # Cross-reference checked IDs against patches JSON
    patches_by_id = {p["id"]: p for p in patches_data.get("patches", [])}
    missing = checked_ids - set(patches_by_id)
    if missing:
        print(
            f"ERROR: checked IDs in review.md not found in patches.json: {missing}",
            file=sys.stderr,
        )
        return 1

    # Load all files that will be edited (in-memory)
    file_contents: dict[str, str] = {}
    for pid in checked_ids:
        patch = patches_by_id[pid]
        rel = patch["file"]
        if rel not in file_contents:
            fp = concept_root / rel
            file_contents[rel] = fp.read_text() if fp.is_file() else None  # type: ignore[assignment]

    # Apply patches best-effort (deterministic order by patch ID)
    applied_items: list[dict] = []
    n_applied = 0
    n_failed  = 0

    for pid in sorted(checked_ids):
        patch   = patches_by_id[pid]
        rel     = patch["file"]
        content = file_contents.get(rel)

        item_base = {
            "annotationId": patch["annotationId"],
            "patchId":      pid,
            "target": {
                "file":     rel,
                "section":  patch["section"],
                "category": patch.get("category"),
            },
            "body": patch.get("body", ""),
        }

        if content is None:
            applied_items.append({**item_base, "status": "failed", "error": f"file not found: {rel}"})
            n_failed += 1
            continue

        new_content, err = apply_section_diff(content, patch["diff"])
        if err:
            applied_items.append({**item_base, "status": "failed", "error": err})
            n_failed += 1
        else:
            file_contents[rel] = new_content
            applied_items.append({**item_base, "status": "applied"})
            n_applied += 1

    # All-failed short-circuit
    if n_applied == 0:
        print(
            f"ERROR: all {n_failed} patch(es) failed — no artifacts written. "
            "Session can be retried without --force after fixing the diffs.",
            file=sys.stderr,
        )
        for item in applied_items:
            if item["status"] == "failed":
                print(f"  FAILED {item['patchId']}: {item.get('error')}", file=sys.stderr)
        return 2

    if dry_run:
        print(f"DRY-RUN: {n_applied} would be applied, {n_failed} would fail")
        return 0

    # Determine which files actually changed (had at least one applied patch)
    files_with_applied = {
        item["target"]["file"]
        for item in applied_items
        if item["status"] == "applied"
    }

    # Write edited files to disk
    for rel, content in file_contents.items():
        if rel in files_with_applied and content is not None:
            (concept_root / rel).write_text(content)

    # Append devlog
    devlog_path.parent.mkdir(parents=True, exist_ok=True)
    with devlog_path.open("a") as fh:
        fh.write(build_devlog_block(sid, applied_items))

    # Write applied/<sid>.json
    applied_data = {
        "sessionId": sid,
        "appliedAt": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items":     applied_items,
    }
    applied_path.parent.mkdir(parents=True, exist_ok=True)
    applied_path.write_text(json.dumps(applied_data, indent=2))

    # Stage + commit
    files_to_stage = (
        [str(concept_root / rel) for rel in files_with_applied]
        + [str(devlog_path), str(applied_path)]
    )
    subprocess.run(["git", "add"] + files_to_stage, check=True)
    commit_msg = f"feedback: apply session {sid} ({n_applied} applied, {n_failed} failed)"
    result = subprocess.run(
        ["git", "commit", "-m", commit_msg], capture_output=True, text=True
    )

    if result.returncode != 0:
        # Rollback: unstage + revert disk + delete applied JSON
        subprocess.run(
            ["git", "restore", "--staged", "--worktree", "--"] + files_to_stage,
            check=False,
        )
        if applied_path.exists():
            applied_path.unlink()
        print("ERROR: git commit failed — working tree restored.", file=sys.stderr)
        print(result.stdout + result.stderr, file=sys.stderr)
        return 1

    print(f"Applied {n_applied} patch(es), {n_failed} failed; session {sid!r} committed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3.7: Quick smoke test of apply.py on `test-pass` in a temp dir**

```bash
python -c "
import subprocess, tempfile, shutil, json
from pathlib import Path

REPO = Path('mockup-feedback/apply/tests/fixtures/test-pass')
SKILL = Path('mockup-feedback/apply')

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    shutil.copytree(REPO / 'before/concept',   tmp / 'concept')
    shutil.copytree(REPO / 'before/_feedback', tmp / '_feedback')

    subprocess.run(['git', 'init', '-q', tmp], check=True)
    subprocess.run(['git', '-C', str(tmp), 'config', 'user.email', 'test@test.com'], check=True)
    subprocess.run(['git', '-C', str(tmp), 'config', 'user.name', 'Test'], check=True)
    subprocess.run(['git', '-C', str(tmp), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(tmp), 'commit', '-q', '-m', 'initial'], check=True)

    import os; orig = os.getcwd(); os.chdir(tmp)
    result = subprocess.run([
        'python', str(SKILL / 'apply.py'),
        '_feedback/patches/test-pass.json',
        '_feedback/patches/test-pass.review.md',
        'concept',
        '_feedback',
    ], capture_output=True, text=True)
    os.chdir(orig)

    print('stdout:', result.stdout.strip())
    print('stderr:', result.stderr.strip())
    print('exit code:', result.returncode)
    assert result.returncode == 0, f'apply.py failed: {result.stderr}'

    applied = json.loads((tmp / '_feedback/applied/test-pass.json').read_text())
    assert all(i['status'] == 'applied' for i in applied['items']), 'Some items not applied'
    print('Smoke test PASSED — 2 patches applied, applied JSON written')
"
```

Expected: `Smoke test PASSED — 2 patches applied, applied JSON written`

- [ ] **Step 3.8: Commit**

```bash
git add mockup-feedback/apply/apply.py mockup-feedback/apply/tests/fixtures/
git commit -m "feat(mockup-feedback): apply.py + all three test fixtures

Section-anchored diff applier (section + frontmatter modes), best-effort
per-patch, all-failed short-circuit (exit 2 / no artifacts), git-commit
with rollback on hook failure. test-pass / test-partial-fail / test-all-fail
before+after fixtures included.

Phase 3 Task 3B step 3.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 4: Apply — `run_apply.sh` integration tests

**Files:**
- Create: `mockup-feedback/apply/tests/run_apply.sh`

- [ ] **Step 4.1: Write `run_apply.sh`**

Create `mockup-feedback/apply/tests/run_apply.sh`:

```bash
#!/usr/bin/env bash
# run_apply.sh — integration tests for mockup-feedback-apply
# Uses throwaway git repos in temp dirs. Run from mockup-feedback/apply/.
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES="$SKILL_DIR/tests/fixtures"
APPLY="$SKILL_DIR/apply.py"

normalize_applied() {
    python3 -c "
import json, sys
d = json.load(sys.stdin)
d.pop('appliedAt', None)
print(json.dumps(d, indent=2, sort_keys=True))
"
}

# ── Helper: set up a temp git repo from a before/ dir ────────────────────────
setup_repo() {
    local before_dir="$1"
    local tmp
    tmp=$(mktemp -d)
    cp -r "$before_dir/concept"   "$tmp/concept"
    cp -r "$before_dir/_feedback" "$tmp/_feedback"
    git -C "$tmp" init -q
    git -C "$tmp" config user.email "test@test.com"
    git -C "$tmp" config user.name "Test"
    git -C "$tmp" add .
    git -C "$tmp" commit -q -m "initial"
    echo "$tmp"
}

# ── Test 1: happy path — 2 patches, both applied ─────────────────────────────
echo "--- Test 1: test-pass (expect exit 0, 2 applied) ---"
TMP1=$(setup_repo "$FIXTURES/test-pass/before")
trap "rm -rf $TMP1" EXIT

cd "$TMP1"
python3 "$APPLY" \
    "_feedback/patches/test-pass.json" \
    "_feedback/patches/test-pass.review.md" \
    "concept" "_feedback"
cd - > /dev/null

# Verify concept file matches expected
diff \
    "$FIXTURES/test-pass/after/concept/experience/screens/01_user_auth/login.md" \
    "$TMP1/concept/experience/screens/01_user_auth/login.md" \
    && echo "OK: login.md matches expected" \
    || { echo "FAIL: login.md content differs"; exit 1; }

# Verify applied JSON (strip volatile fields)
ACTUAL_NORM=$(normalize_applied < "$TMP1/_feedback/applied/test-pass.json")
EXPECTED_NORM=$(normalize_applied < "$FIXTURES/test-pass/after/_feedback/applied/test-pass.json")
[ "$ACTUAL_NORM" = "$EXPECTED_NORM" ] \
    && echo "OK: applied JSON matches expected" \
    || { echo "FAIL: applied JSON differs"; diff <(echo "$EXPECTED_NORM") <(echo "$ACTUAL_NORM"); exit 1; }

# Verify commit message
COMMIT_MSG=$(git -C "$TMP1" log -1 --format="%s")
[[ "$COMMIT_MSG" == *"session test-pass"* ]] \
    && echo "OK: commit message contains session ID" \
    || { echo "FAIL: commit message: $COMMIT_MSG"; exit 1; }

echo ""

# ── Test 2: partial failure — 1 applied, 1 failed ────────────────────────────
echo "--- Test 2: test-partial-fail (expect exit 0, 1 applied + 1 failed) ---"
TMP2=$(setup_repo "$FIXTURES/test-partial-fail/before")
trap "rm -rf $TMP2" EXIT

cd "$TMP2"
python3 "$APPLY" \
    "_feedback/patches/test-partial-fail.json" \
    "_feedback/patches/test-partial-fail.review.md" \
    "concept" "_feedback"
cd - > /dev/null

# Verify concept file (only the good patch should be applied)
diff \
    "$FIXTURES/test-partial-fail/after/concept/experience/screens/01_user_auth/login.md" \
    "$TMP2/concept/experience/screens/01_user_auth/login.md" \
    && echo "OK: login.md matches expected (good patch applied)" \
    || { echo "FAIL: login.md content differs"; exit 1; }

# Verify applied JSON has 1 applied + 1 failed
ACTUAL_NORM=$(normalize_applied < "$TMP2/_feedback/applied/test-partial-fail.json")
EXPECTED_NORM=$(normalize_applied < "$FIXTURES/test-partial-fail/after/_feedback/applied/test-partial-fail.json")
[ "$ACTUAL_NORM" = "$EXPECTED_NORM" ] \
    && echo "OK: applied JSON matches expected (failed item recorded)" \
    || { echo "FAIL: applied JSON differs"; diff <(echo "$EXPECTED_NORM") <(echo "$ACTUAL_NORM"); exit 1; }

echo ""

# ── Test 3: all-fail short-circuit ────────────────────────────────────────────
echo "--- Test 3: test-all-fail (expect exit 2, no commit, no applied JSON) ---"
TMP3=$(setup_repo "$FIXTURES/test-all-fail/before")
trap "rm -rf $TMP3" EXIT

cd "$TMP3"
set +e
python3 "$APPLY" \
    "_feedback/patches/test-all-fail.json" \
    "_feedback/patches/test-all-fail.review.md" \
    "concept" "_feedback"
EC=$?
set -e
cd - > /dev/null

[ "$EC" -eq 2 ] \
    && echo "OK: exit code 2 (all-failed)" \
    || { echo "FAIL: expected exit 2, got $EC"; exit 1; }

[ ! -f "$TMP3/_feedback/applied/test-all-fail.json" ] \
    && echo "OK: no applied JSON written" \
    || { echo "FAIL: applied JSON was written (should not exist)"; exit 1; }

COMMIT_COUNT=$(git -C "$TMP3" log --oneline | wc -l | tr -d ' ')
[ "$COMMIT_COUNT" -eq 1 ] \
    && echo "OK: only the initial commit exists (no feedback commit)" \
    || { echo "FAIL: unexpected commit count: $COMMIT_COUNT"; exit 1; }

# Verify retry without --force succeeds (by re-running with a fixed patch)
# i.e. the second run exits 2 cleanly — no --force needed
cd "$TMP3"
set +e
python3 "$APPLY" \
    "_feedback/patches/test-all-fail.json" \
    "_feedback/patches/test-all-fail.review.md" \
    "concept" "_feedback"
EC2=$?
set -e
cd - > /dev/null
[ "$EC2" -eq 2 ] \
    && echo "OK: retry exits 2 cleanly without --force (no lockout)" \
    || { echo "FAIL: retry failed unexpectedly with exit $EC2"; exit 1; }

echo ""
echo "All apply integration tests passed."
```

```bash
chmod +x mockup-feedback/apply/tests/run_apply.sh
```

- [ ] **Step 4.2: Run integration tests**

```bash
cd mockup-feedback/apply && bash tests/run_apply.sh; cd ../..
```

Expected final line: `All apply integration tests passed.`

If any test fails:
- Test 1 failure: re-read `_patch_section` / `_patch_frontmatter` logic in `apply.py`; check line endings and indentation match the fixture files exactly.
- Test 2 failure: verify `test-partial-fail.after/applied/*.json` has the correct `"status": "failed"` for `p-bad` with an `error` field.
- Test 3 failure: verify `n_applied == 0` check fires before `applied_path.write_text`.

- [ ] **Step 4.3: Commit**

```bash
git add mockup-feedback/apply/tests/run_apply.sh
git commit -m "test(mockup-feedback): apply integration tests (3 scenarios)

Test 1: happy path 2 patches applied + commit created.
Test 2: partial failure 1/2 — applied JSON records both, file only has good patch.
Test 3: all-failed short-circuit exit 2 — no commit, no applied JSON, retry clean.

Phase 3 Task 3B step 4.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 5: Apply — SKILL.md + `validator.py` + scaffold

**Files:**
- Create: `mockup-feedback/apply/SKILL.md`
- Create: `mockup-feedback/apply/validator.py`

- [ ] **Step 5.1: Write `validator.py`**

Create `mockup-feedback/apply/validator.py`:

```python
#!/usr/bin/env python3
"""validator.py — structural validator for apply output (applied/<sid>.json).

Usage:
  python validator.py <applied-json> <patches-json> <review-md>

Checks:
  1. Every checked patch ID in review.md has an item in applied JSON.
  2. No applied item references a patch ID not in patches JSON.
  3. Item status is 'applied' or 'failed'; failed items have 'error'.
  4. sessionId matches between applied JSON and patches JSON.

Exit codes: 0 PASS, 2 FAIL, 1 internal error.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: python validator.py <applied-json> <patches-json> <review-md>", file=sys.stderr)
        return 1

    try:
        applied_data = json.loads(Path(sys.argv[1]).read_text())
        patches_data = json.loads(Path(sys.argv[2]).read_text())
        review_md    = Path(sys.argv[3]).read_text()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    violations: list[str] = []

    # session IDs match
    if applied_data.get("sessionId") != patches_data.get("sessionId"):
        violations.append(
            f"sessionId mismatch: applied={applied_data.get('sessionId')!r} "
            f"patches={patches_data.get('sessionId')!r}"
        )

    patches_by_id = {p["id"]: p for p in patches_data.get("patches", [])}
    checked_ids = set(re.findall(r"- \[x\] \*\*([^*]+)\*\*", review_md))
    applied_by_pid = {item["patchId"]: item for item in applied_data.get("items", [])}

    # Every checked patch ID has an applied item
    for pid in checked_ids:
        if pid not in applied_by_pid:
            violations.append(f"checked patch {pid!r} has no corresponding item in applied JSON")

    # No applied item references unknown patch ID
    for item in applied_data.get("items", []):
        pid = item.get("patchId")
        if pid and pid not in patches_by_id:
            violations.append(f"applied item references unknown patchId {pid!r}")

    # Status validity
    for item in applied_data.get("items", []):
        status = item.get("status")
        if status not in ("applied", "failed"):
            violations.append(f"item {item.get('patchId')!r} has invalid status {status!r}")
        if status == "failed" and not item.get("error"):
            violations.append(f"failed item {item.get('patchId')!r} missing 'error' field")

    if violations:
        for v in violations:
            print("FAIL", v)
        return 2

    print(f"PASS  {sys.argv[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5.2: Verify validator passes on test-pass output**

Run the smoke-test from Task 3.7 again to get the applied JSON, then validate:

```bash
python -c "
import subprocess, tempfile, shutil, json
from pathlib import Path

REPO = Path('mockup-feedback/apply/tests/fixtures/test-pass')
SKILL = Path('mockup-feedback/apply')

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    shutil.copytree(REPO / 'before/concept',   tmp / 'concept')
    shutil.copytree(REPO / 'before/_feedback', tmp / '_feedback')
    import subprocess as sp
    sp.run(['git', 'init', '-q', str(tmp)], check=True)
    sp.run(['git', '-C', str(tmp), 'config', 'user.email', 'test@test.com'], check=True)
    sp.run(['git', '-C', str(tmp), 'config', 'user.name', 'Test'], check=True)
    sp.run(['git', '-C', str(tmp), 'add', '.'], check=True)
    sp.run(['git', '-C', str(tmp), 'commit', '-q', '-m', 'initial'], check=True)

    import os; orig = os.getcwd(); os.chdir(tmp)
    sp.run([
        'python', str(SKILL / 'apply.py'),
        '_feedback/patches/test-pass.json',
        '_feedback/patches/test-pass.review.md',
        'concept', '_feedback',
    ], check=True)
    os.chdir(orig)

    result = sp.run([
        'python', str(SKILL / 'validator.py'),
        str(tmp / '_feedback/applied/test-pass.json'),
        str(REPO / 'before/_feedback/patches/test-pass.json'),
        str(REPO / 'before/_feedback/patches/test-pass.review.md'),
    ], capture_output=True, text=True)
    print(result.stdout.strip())
    assert result.returncode == 0, result.stderr
    print('Validator smoke test PASSED')
"
```

Expected: `PASS  ...` then `Validator smoke test PASSED`.

- [ ] **Step 5.3: Write `SKILL.md`**

Create `mockup-feedback/apply/SKILL.md`:

```markdown
---
name: mockup-feedback-apply
description: "Reads patches/<sid>.json + patches/<sid>.review.md (checklist), applies approved section-anchored diffs to _concept/ files (best-effort), appends devlog, writes applied/<sid>.json, creates one git commit. Fourth and final skill in the mockup-feedback cluster."
metadata:
  version: "0.1.0"
  tags: [mockup-feedback, apply, git, audit]
  stage: alpha
  prerequisites:
    files:
      - path: "_concept/_feedback/patches/"
        gate: hard
        description: "patches/<sid>.json + patches/<sid>.review.md from mockup-feedback-patch"
        min_entries: 1
    produces:
      - path: "_concept/_feedback/applied/<sid>.json"
        description: "Committed audit trail — per-annotation status + body"
      - path: "_concept/_feedback/devlog.md"
        description: "Appended session block (committed)"
      - path: "_concept/**/*.md"
        description: "Edited concept files"
---

# mockup-feedback-apply

## Overview

Applies the approved patches from `patches/<sid>.review.md` to `_concept/` files,
creates a git commit, and writes the committed audit record. Deterministic Python
only — no LLM call.

**Run after** `mockup-feedback-patch` and user review of `review.md`.
**Edit `review.md` first**: untick any patch you want to skip; hand-edit diffs
if needed.

---

## Step 1 — Locate the session to apply

Default: find the latest `patches/<sid>.json` that has no corresponding
`applied/<sid>.json`. Override via `PARAMETERS.session_id`.

Abort if `applied/<sid>.json` already exists (idempotency guard) unless
`PARAMETERS.force = true`.

---

## Step 2 — Pre-flight checks

Run these before touching any files:

1. **Working tree clean:** `git status --porcelain` must be empty. If not, print
   `git status` output and abort.
2. **Schema valid:** `patches/<sid>.json` must match `mockup-feedback/schemas/patches.schema.json`.
3. **review.md ↔ patches.json sync:** every checked patch ID in `review.md`
   must exist in `patches.json`. Abort if any are missing.

---

## Step 3 — Run `apply.py`

```bash
python <skill-dir>/apply.py \
    _concept/_feedback/patches/<sid>.json \
    _concept/_feedback/patches/<sid>.review.md \
    _concept/ \
    _concept/_feedback/
```

`apply.py` handles:
- Best-effort patch application (one failure doesn't block others)
- All-failed short-circuit: exits 2 without writing any artifact; session
  can be retried without `--force` after fixing the diffs
- Single git commit: `feedback: apply session <sid> (N applied, K failed)`
- Rollback on commit failure (hook rejection etc.)

---

## Step 4 — Report

Print:

```
mockup-feedback-apply complete: <sid>
  N patches applied, K failed
  Committed: feedback: apply session <sid> (N applied, K failed)
  Audit trail: _concept/_feedback/applied/<sid>.json
  Devlog:      _concept/_feedback/devlog.md (appended)
```

For each failed patch:
```
  FAILED <patch-id>: <error reason>
  → edit _concept/_feedback/patches/<sid>.review.md and re-run to retry
```

---

## Failure recovery

| Scenario | Recovery |
|---|---|
| All patches fail (exit 2) | Fix diffs in `patches/<sid>.json` / `review.md`; re-run without `--force` |
| Some patches fail (exit 0) | Re-run with an updated `review.md` that unchecks the applied patches and uses `--force` |
| Commit hook rejection | Working tree rolled back; fix hook issue; re-run without `--force` |
| Already applied | Use `--force` if intentional re-apply (e.g. after `git revert`) |

---

## Inputs

| Name | Type | Default |
|---|---|---|
| `session_id` | string | (latest un-applied session) |
| `force` | bool | false |

## Outputs (all committed in one commit)

| Path | Description |
|---|---|
| `_concept/**/*.md` | Edited concept files |
| `_concept/_feedback/applied/<sid>.json` | Committed audit trail |
| `_concept/_feedback/devlog.md` | Appended session block |

## References

- `mockup-feedback/schemas/patches.schema.json` — input validation
- `REFACTOR_MOCKUP.md` §5 — devlog format
- `docs/superpowers/specs/2026-05-09-3B-mockup-feedback-triage-patch-apply-design.md` D3, D6, D7
```

- [ ] **Step 5.4: Verify SKILL.md frontmatter**

```bash
python -c "
import re, py_compile
from pathlib import Path
text = Path('mockup-feedback/apply/SKILL.md').read_text()
m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
assert m and 'name: mockup-feedback-apply' in m.group(1), 'frontmatter invalid'
py_compile.compile('mockup-feedback/apply/validator.py', doraise=True)
py_compile.compile('mockup-feedback/apply/apply.py', doraise=True)
print('All files OK')
"
```

Expected: `All files OK`.

- [ ] **Step 5.5: Commit**

```bash
git add mockup-feedback/apply/SKILL.md mockup-feedback/apply/validator.py
git commit -m "feat(mockup-feedback): apply SKILL.md + validator.py

5-step apply procedure (pre-flight → apply.py → report).
Validator checks checked-IDs coverage, patch-ID references, status validity.

Phase 3 Task 3B step 5.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 6: DOMAIN.md update + final verification

**Files:**
- Modify: `mockup-feedback/DOMAIN.md`

- [ ] **Step 6.1: Update DOMAIN.md Skills list**

In `mockup-feedback/DOMAIN.md`, update (or create) the Skills section to list
all four skills from the mockup-feedback cluster:

```markdown
## Skills

- [`mockup-feedback-annotate`](annotate/SKILL.md) — Inject annotation overlay into a walkthrough site
- [`mockup-feedback-triage`](triage/SKILL.md) — Route annotations to _concept/ files by resolving specRef
- [`mockup-feedback-patch`](patch/SKILL.md) — Author section-anchored diffs for each annotation (LLM-driven)
- [`mockup-feedback-apply`](apply/SKILL.md) — Apply approved diffs, append devlog, commit

## Usage sequence

```
mockup-feedback-annotate   → injects overlay into walkthrough; user downloads sessions/*.json
mockup-feedback-triage     → resolves specRef → _concept/ paths; groups by file
mockup-feedback-patch      → authors diffs; emits patches/*.json + *.review.md
  (user reviews and edits review.md)
mockup-feedback-apply      → applies diffs, appends devlog, one git commit
```
```

- [ ] **Step 6.2: Final validation sweep**

```bash
python -c "
import py_compile, re
from pathlib import Path

for skill in ['triage', 'patch', 'apply']:
    for pyfile in Path(f'mockup-feedback/{skill}').rglob('*.py'):
        py_compile.compile(str(pyfile), doraise=True)
    skill_md = Path(f'mockup-feedback/{skill}/SKILL.md').read_text()
    m = re.match(r'^---\n(.*?)\n---', skill_md, re.DOTALL)
    assert m, f'{skill}/SKILL.md: no frontmatter'
    assert f'name: mockup-feedback-{skill}' in m.group(1), f'{skill}: name field wrong'
    print(f'OK: {skill}')

domain = Path('mockup-feedback/DOMAIN.md').read_text()
for skill in ['annotate', 'triage', 'patch', 'apply']:
    assert skill in domain, f'DOMAIN.md missing {skill}'
print('OK: DOMAIN.md references all 4 skills')
"
```

Expected output:
```
OK: triage
OK: patch
OK: apply
OK: DOMAIN.md references all 4 skills
```

- [ ] **Step 6.3: Run full triage test suite**

```bash
cd mockup-feedback/triage && bash tests/run_validator.sh; cd ../..
```

Expected: `All triage tests passed.`

- [ ] **Step 6.4: Run full apply integration test suite**

```bash
cd mockup-feedback/apply && bash tests/run_apply.sh; cd ../..
```

Expected: `All apply integration tests passed.`

- [ ] **Step 6.5: Check git log for expected commit sequence**

```bash
git log --oneline | head -7
```

Expected entries (newest first):
```
feat(mockup-feedback): apply SKILL.md + validator.py ...
test(mockup-feedback): apply integration tests (3 scenarios) ...
feat(mockup-feedback): apply.py + all three test fixtures ...
feat(mockup-feedback): patch skill — SKILL.md + structural validator + fixtures ...
feat(mockup-feedback): triage skill — triage.py + validator + tests + SKILL.md ...
feat(mockup-feedback): schemas + shared concept + session fixtures for 3B ...
```

- [ ] **Step 6.6: Commit**

```bash
git add mockup-feedback/DOMAIN.md
git commit -m "feat(mockup-feedback): DOMAIN.md — all 4 skills listed + usage sequence

Completes Phase 3 Task 3B: triage + patch + apply skills fully scaffolded.
Next: Task 3C (Lit/Astro walkthrough renderer support).

Phase 3 Task 3B step 6.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Acceptance Criteria (from migration plan Task 3B)

- [x] `mockup-feedback-triage` reads a session JSON, resolves `specRef` → `_concept/` path, groups by file, writes `triage/<sid>.json`
  → confirmed by `triage.py` + golden tests
- [x] Unresolvable annotations recorded in `unresolved[]`, not silently dropped
  → confirmed by `test-bad-ref` golden test
- [x] `mockup-feedback-patch` emits `patches/<sid>.json` + `patches/<sid>.review.md`
  → confirmed by SKILL.md body + structural validator
- [x] Provisional elements get a second `kind: "provisional-promotion"` patch
  → confirmed by validator check #4 + test-minimal fixture (provisional submit-button)
- [x] `needs_manual` items appear in review.md preamble, no checklist item
  → confirmed by validator checks #5–#6 + test-empty-body fixture
- [x] `mockup-feedback-apply` applies approved diffs best-effort, records all outcomes in `applied/<sid>.json`, commits in one commit
  → confirmed by `apply.py` + test-pass / test-partial-fail integration tests
- [x] All-failed short-circuit: exit 2, no artifacts written, retry without `--force`
  → confirmed by test-all-fail integration test
- [x] Commit subject: `feedback: apply session <sid> (N applied, K failed)`
  → confirmed by test-pass commit-message assertion in run_apply.sh

## What's NOT in this plan

- End-to-end browser test (annotate → triage → patch → apply → verify regen) — Task 3F
- Lit/Astro walkthrough renderer support — Task 3C
- `mockup-feedback-archive` skill (devlog rollup at 500 entries) — Task 3E
- forge-concept consumer surfaces (`/api/feedback/*`, `FeedbackDrawer.vue`) — forge-concept repo
- Multi-user conflict resolution beyond last-write-wins — REFACTOR_MOCKUP.md §11 row 9
