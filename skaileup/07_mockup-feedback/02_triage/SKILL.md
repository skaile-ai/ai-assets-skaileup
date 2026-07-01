---
name: mockup-feedback-triage
description: "Use when a feedback session JSON exists and annotations need to be routed to their target concept files. Resolves specRef.screen/feature/journey and produces triage/<sid>.json grouped by file. Deterministic — no LLM. Second skill in the mockup-feedback cluster."
metadata:
  version: "0.1.0"
  tags: [mockup-feedback, triage, routing]
  stage: alpha
  artifacts:
    requires:
      - id: feedback-sessions
        gate: hard
    produces:
      - id: feedback-triage
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
| `_concept/_feedback/triage/<sid>.json` | Grouped annotation list per _concept/ file |

---

## References

- `mockup-feedback/schemas/session.schema.json` — input validation
- `mockup-feedback/schemas/triage.schema.json` — output shape
- `docs/devlog/2026-05-09-3B-mockup-feedback-triage-patch-apply-design.md` D1
