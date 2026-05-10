---
title: "impl-quality-debug-self-verify"
description: "Use when the user is stuck on a bug and wants the AI to autonomously verify whether a fix worked. Produces a self-runnable verification protocol (test commands + expected outputs + success criteria) the AI executes without user-as-test-loop."
sidebar:
  label: "impl-quality-debug-self-verify"
---

:::note[Skill manifest]
**Name:** `impl-quality-debug-self-verify`
**Stage:** alpha · **Version:** 0.1.0
**Tags:** debug, verify, autonomous, protocol, test-loop, fix-verification
**Source:** [`skaileup/impl-quality/debug-self-verify/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/impl-quality/debug-self-verify/SKILL.md)
:::


# Debug Self-Verify — Verification Protocol Author

## Overview

Turns a bug + (optional) hypothesis into a **self-runnable verification protocol** the AI executes
autonomously. The protocol is a list of test commands, each with an exact expected output and a
one-line pass criterion. The AI iterates the steps and produces a verdict — pass, fail, or escalate
to `debug-handoff`.

This is the antidote to "user-as-test-loop": instead of asking the user to manually re-run the bug
after each attempted fix, the AI captures the verification recipe up front and runs it itself.

## When to Use

- **Ad-hoc by the user** when they say "is it fixed?", "verify this works", or "set up a way for
  me to know when this bug is gone".
- **Called by another skill on bug-out** — e.g. an `impl-slice/implement` that has been looping on
  a failing test can escalate to this skill to formalize the verification recipe.

> **Call sites:** these two paths are the only intended entry points in v0.1.0. This skill is **not**
> wired into any `flows/*.flow.yaml` yet. Flow wiring is deferred to a future task.

## When NOT to Use

- The bug is already fixed and the user just wants a regression test → use `impl-quality/test-unit`
  or `impl-quality/test-integration` for permanent test coverage.
- The user wants to **escalate** (hand the bug to a fresh agent) → use `impl-quality/debug-handoff`.
- No bug exists yet — use `impl-quality/audit` to find issues, then come back.

## Workspace Zone — `_debug/<id>/`

This skill writes to a workspace zone `_debug/<id>/` mirroring `_slice/` and `_feedback/`. The zone is:

- **Per-bug**, not per-slice — debug sessions are not always tied to a slice.
- **Not committed by default** — protocols are scratch artifacts, intended to be regenerated when
  re-debugging the same area.
- **Shared with `debug-handoff`** — both skills read/write `_debug/<id>/context.md` so the user does
  not get re-interviewed when the two skills run in sequence.

`<id>` is a kebab-case slug derived from the symptom (e.g. `login-redirect-loop`), or a timestamp
(`2026-05-07-1430`) if the agent cannot infer one.

---

ROLE  Verification Protocol Author — turns a bug + hypothesis into a self-runnable test plan the AI executes autonomously to verdict.

READS
  ? _debug/<id>/context.md          — shared interview state (if a prior debug skill ran)
  package.json                      — detect runnable test/build/lint/typecheck scripts
  ? pyproject.toml                  — Python project marker (pytest / ruff config)
  ? _slice/impl/<id>/plan.md        — if invoked inside a slice, the plan's testing strategy

WRITES
  _debug/<id>/protocol.md           — the verification protocol (canonical schema below)
  _debug/<id>/context.md            — only if it does not yet exist (interview output)

REFERENCES
  contracts/iron_laws.md                                      — § 9 standalone-question rule (non-negotiable)
  contracts/skill_grammar.md                                  — DSL keywords used in this body
  impl-quality/debug-self-verify/examples/protocol-flaky-test.md   — tone target: hypothesis-agnostic
  impl-quality/debug-self-verify/examples/protocol-build-error.md  — tone target: hypothesis-specific

MUST  ask the user for bug description and repro as STANDALONE messages (Iron Laws § 9)
MUST  produce a protocol that conforms to the pinned schema (every required heading present)
MUST  order verification steps cheap-to-expensive (lint/typecheck → unit → integration → e2e)
MUST  include explicit failure exit conditions (setup failure, output mismatch, retry exhaustion)
MUST  state whether the protocol is hypothesis-agnostic or hypothesis-specific
MUST  run validator.py on the produced protocol before returning; do not return until it passes
NEVER  block waiting for human-in-the-loop verification — the protocol must be machine-runnable end to end
NEVER  invent test commands not supported by the project's package.json / pyproject.toml
NEVER  bundle the interview question into the same message as a status update — Iron Laws § 9 forbids it
NEVER  overwrite an existing _debug/<id>/context.md without showing the diff first

EMIT  [debug-self-verify] started run_id=<uuid> bug_id=<id>

# ── STEP 1: Read or gather context ──────────────────────────

STEP 1: Resolve bug context
  IF _debug/<id>/context.md exists
    - Read it as authoritative.
    - Confirm the symptom and repro with the user as ONE standalone message:
      > "I found existing context at _debug/<id>/context.md. Symptom: <summary>. Still accurate, or has it changed?"
    - Wait for the answer before proceeding.
  ELSE
    - Send Q1 as a STANDALONE message (Iron Laws § 9):
      > "What's the bug? One to three sentences — what you observe vs. what you expected."
    - Wait for the answer.
    - Send Q2 as a STANDALONE message:
      > "How do I reproduce it? Numbered steps, or say 'intermittent' and tell me the frequency."
    - Wait for the answer.
    - Send Q3 as a STANDALONE message (optional):
      > "Do you have a current hypothesis about the cause? If yes, state it with confidence (low/medium/high). If no, just say 'no hypothesis'."
    - Wait for the answer.
    - Derive <id>: kebab-case slug from the symptom (3-5 words max), or YYYY-MM-DD-HHMM if no clear noun.
    - Write _debug/<id>/context.md per the shared schema (see Pinned Schema below).

# ── STEP 2: Detect runnable commands ────────────────────────

STEP 2: Inventory the project's test/build commands
  - Read package.json scripts. Note: test, lint, typecheck, build, and any custom scripts referenced in the bug description.
  - IF pyproject.toml exists, read [tool.pytest.ini_options], [tool.ruff], [tool.mypy], [project.scripts].
  - Build the candidate-command list. The protocol may ONLY use commands from this list (or commands the user has explicitly authorized in the interview).

# ── STEP 3: Choose protocol mode ────────────────────────────

STEP 3: Choose hypothesis-agnostic OR hypothesis-specific
  IF user provided a hypothesis with confidence ≥ medium
    - Mode: HYPOTHESIS-SPECIFIC. The protocol verifies the cause is fixed
      (e.g. "the race condition no longer occurs under N concurrent requests").
  ELSE
    - Mode: HYPOTHESIS-AGNOSTIC. The protocol verifies only the symptom is gone.
  - State the choice in the protocol's "Hypothesis Under Test" section explicitly.

# ── STEP 4: Draft verification steps ────────────────────────

STEP 4: Draft the verification steps, ordered cheap-to-expensive
  - Order: lint / format → typecheck → unit test → integration test → e2e / manual repro automation.
  - Each step gets:
    - Exact shell command (no placeholders, no `<...>`)
    - Expected-success output (literal string OR regex, fenced)
    - Expected-still-broken output (literal string OR regex, fenced) — optional but preferred when known
    - One-line pass criterion (e.g. "exit code 0 AND stdout matches expected")
  - Cap at 5 steps for v0.1.0. If more are needed, the bug is too big for one protocol — split it.

# ── STEP 5: Draft failure exit conditions ───────────────────

STEP 5: Specify when to STOP the protocol and escalate
  - Setup failure: command-not-found, missing dependency, env var unset.
  - Output mismatch: a step's output matches NEITHER expected-success nor expected-broken — protocol is stale.
  - Retry exhaustion on flaky steps: cap N=3 retries.
  - Escalation target: the user, or `impl-quality/debug-handoff` if the user wants to hand off.

# ── STEP 6: Write protocol.md ───────────────────────────────

STEP 6: Write _debug/<id>/protocol.md per the pinned schema (below).

# ── STEP 7: Self-validate ───────────────────────────────────

STEP 7: Run the validator
  RUN  python impl-quality/debug-self-verify/validator.py _debug/<id>/protocol.md
  IF exit code != 0
    - Read the diagnostic, fix the protocol, re-run.
  UNTIL validator passes (exit 0).

# ── CHECKPOINT ──────────────────────────────────────────────

CHECKPOINT protocol_review
  Send a STANDALONE message (Iron Laws § 9):
  > "Verification protocol ready at _debug/<id>/protocol.md. Run it now, or save for later?"
  IF user says "run now"
    - Iterate the protocol's steps in order.
    - For each step, run the command, compare output to expected fences, record the verdict.
    - On first FAIL → stop, report which step failed and the actual output.
    - On all PASS → report the verdict and offer to delete _debug/<id>/.

EMIT  [debug-self-verify] completed run_id=<uuid> bug_id=<id> mode=<hypothesis-agnostic|hypothesis-specific> steps=<N>

---

## Pinned Schema — `_debug/<id>/context.md` (shared input scratch)

Both `debug-self-verify` and `debug-handoff` read this file if it exists; whichever skill runs first
writes it. This avoids re-interviewing the user when both skills run in sequence.

```markdown
# Debug Context — <id>

## Symptom
<1-3 sentences: what the user observes vs. what they expected>

## Repro
<numbered steps, or "intermittent — see notes" if not reliable>
1. ...
2. ...

## Environment
<bullet list>
- OS / runtime versions
- Branch / commit SHA
- Relevant env vars (redacted as `<env:VAR_NAME>` if sensitive)

## Attempts So Far
| # | What was tried | Outcome | Why ruled out (or partial) |
|---|----------------|---------|----------------------------|
| 1 | ...            | ...     | ...                        |

## Current Hypothesis
<1-3 sentences. May be empty on first call.>

## Files Touched
<bullet list of paths the user thinks are involved>
```

## Pinned Schema — `_debug/<id>/protocol.md` (output)

The validator enforces this shape. Authoring is done when a produced protocol matches it AND
`validator.py` exits 0.

```markdown
# Verification Protocol — <id>

## Bug Summary
<1-2 sentences referencing _debug/<id>/context.md § Symptom>

## Hypothesis Under Test
<1-3 sentences: which hypothesis from context.md does this protocol verify?
If hypothesis-agnostic ("just check the symptom is gone"), state that explicitly.>

## Verification Steps

Each step is independently executable. Steps are ordered cheap-to-expensive
(so the AI bails early on the first signal of failure).

### Step 1: <short name>
- **Command:** `<exact shell command>`
- **Expected output (success):** `<literal string or regex, fenced>`
- **Expected output (still-broken):** `<literal string or regex, fenced>` *(optional)*
- **Pass criterion:** `<one-line predicate, e.g. "exit code 0 AND stdout matches expected">`

### Step 2: ...
(repeat)

## Success Criteria

The bug is verified fixed when ALL of the following hold:
- [ ] Step 1 pass criterion met
- [ ] Step 2 pass criterion met
- [ ] ... (one checkbox per step above)

## Failure Exit Conditions

If any of these occur, STOP the protocol and escalate (typically to `impl-quality/debug-handoff`):
- A step's command errors with a setup failure (not a test failure) — `command not found`, missing dep
- A step's output matches neither expected-success nor expected-broken — protocol no longer covers reality
- Maximum N=3 retry attempts on a flaky step exhausted

## Notes for Future Re-runs
<free-form bullet list. The agent fills in things observed during protocol design that the next
runner should know — e.g. "step 3 is flaky on Mondays", "skip step 4 if running offline".>
```

---

CHECKLIST
  - [ ] _debug/<id>/protocol.md exists and validator.py exits 0
  - [ ] All verification steps have exact commands (no `<placeholder>` syntax remaining)
  - [ ] "Hypothesis Under Test" section is non-empty
  - [ ] "Failure Exit Conditions" section is present and lists at least the three default conditions
  - [ ] User shown the protocol via a STANDALONE message (Iron Laws § 9)
  - [ ] _debug/<id>/context.md exists (either pre-existing or freshly written)

