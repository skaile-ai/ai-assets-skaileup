---
title: "mockup-feedback-apply"
description: "Reads patches/<sid>.json + patches/<sid>.review.md (checklist), applies approved section-anchored diffs to _concept/ files (best-effort), appends devlog, writes applied/<sid>.json, creates one git commit. Fourth and final skill in the mockup-feedback"
sidebar:
  label: "mockup-feedback-apply"
---

:::note[Skill manifest]
**Name:** `mockup-feedback-apply`
**Stage:** alpha · **Version:** 0.1.0
**Tags:** mockup-feedback, apply, git, audit
**Source:** [`skaileup/mockup-feedback/apply/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/mockup-feedback/apply/SKILL.md)
:::


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

If `apply.py` exits 2, stop here and print the all-failed message from the
failure recovery table below. Do not proceed to Step 4.

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

