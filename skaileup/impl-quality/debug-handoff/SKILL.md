---
name: impl-quality-debug-handoff
description: "Use when the user is stuck on a bug and wants to hand off to a fresh agent (or themselves after /clear). Produces a self-contained markdown summary — bug description, attempts so far, current hypothesis, suggested next steps — pasteable into a new chat with no prior context."
metadata:
  version: "0.1.0"
  tags:
    - debug
    - handoff
    - fresh-chat
    - escalation
    - context-transfer
  stage: alpha
  artifacts:
    consumes:
      - id: slice-impl-plan
        gate: soft
    produces:
      - id: debug-context
      - id: debug-handoff-brief
  prerequisites:
    inputs_required:
      - id: bug_description
        label: "Bug description — what is broken?"
        type: textarea
        hint: "2-5 sentences. Symptom + impact + repro reliability."
      - id: attempts_so_far
        label: "What have you tried so far?"
        type: textarea
        hint: "One bullet per attempt: what you tried, what happened, why you ruled it out."
    inputs_optional:
      - id: hypothesis
        label: "Current hypothesis (with confidence)"
        type: textarea
        hint: "1-3 sentences. Confidence MUST be one of: low / medium / high."
      - id: out_of_scope
        label: "Approaches you have ruled out (do NOT do these)"
        type: textarea
        hint: "Helps the next agent avoid rabbit holes you have already explored."
      - id: bug_id
        label: "Short bug slug (kebab-case) for the _debug/<id>/ directory"
        type: text
        hint: "e.g. login-redirect-loop. Auto-derived from the symptom if omitted."
    reads:
      - path: "_debug/<id>/context.md"
        description: "Shared interview state from a prior debug skill invocation (optional)"
      - path: "_debug/<id>/protocol.md"
        description: "If debug-self-verify ran first, executed steps and outcomes feed the handoff"
      - path: "_slice/impl/<id>/plan.md"
        description: "If invoked from inside a slice, the slice plan's testing strategy"
    produces:
      - path: "_debug/<id>/handoff.md"
        description: "Self-contained handoff brief — pasteable into a fresh chat with no prior context"
      - path: "_debug/<id>/context.md"
        description: "Shared interview state — written only if it does not already exist"
---

# Debug Handoff — Fresh-Chat Brief Author

## Overview

Converts an in-progress debug session into a **self-contained markdown brief** the next agent
(or the user themselves after `/clear`) can pick up cold. The brief is pasteable: no prior context
required, no chat-relative references like "as discussed above", no relative paths that will not
resolve in a different working directory.

This is the antidote to "I will explain it again from scratch": instead of re-typing the bug
history into a new chat, the user pastes one file and the next agent has everything it needs.

## When to Use

- **Ad-hoc by the user** when they say "I am giving up, hand this off", "summarize for /clear", or
  "I need a fresh agent to look at this".
- **Called by another skill on bug-out** — e.g. when `impl-quality/debug-self-verify` has run its
  protocol three times and still cannot reach a verdict, escalation goes here.

> **Call sites:** these two paths are the only intended entry points in v0.1.0. This skill is **not**
> wired into any `flows/*.flow.yaml` yet. Flow wiring is deferred to a future task.

## When NOT to Use

- The user wants the AI to autonomously verify a fix → use `impl-quality/debug-self-verify`.
- The bug is closed and the user wants a post-mortem doc → write a regular markdown report; this
  skill is for live, unresolved bugs.
- No bug exists yet — use `impl-quality/audit` to find issues, then come back.

## Workspace Zone — `_debug/<id>/`

This skill writes to a workspace zone `_debug/<id>/` mirroring `_slice/` and `_feedback/`. The zone is:

- **Per-bug**, not per-slice — debug sessions are not always tied to a slice.
- **Not committed by default** — handoff briefs are scratch artifacts, regenerated when the bug
  evolves.
- **Shared with `debug-self-verify`** — both skills read/write `_debug/<id>/context.md` so the user
  does not get re-interviewed when the two skills run in sequence.

`<id>` is a kebab-case slug derived from the symptom (e.g. `login-redirect-loop`), or a timestamp
(`2026-05-07-1430`) if the agent cannot infer one.

---

ROLE  Debug Handoff Author — converts an in-progress debug session into a self-contained markdown brief the next agent can pick up cold.

READS
  ? _debug/<id>/context.md          — shared interview state (if a prior debug skill ran)
  ? _debug/<id>/protocol.md         — if debug-self-verify ran first, attempts and outcomes feed the handoff
  ? _slice/impl/<id>/plan.md        — if invoked inside a slice, the plan's testing strategy
  git log -10 --oneline             — recent commit history for the "Last working commit" field

WRITES
  _debug/<id>/handoff.md            — the handoff document (canonical schema below)
  _debug/<id>/context.md            — only if it does not yet exist (interview output)

REFERENCES
  contracts/iron_laws.md                                          — § 9 standalone-question rule (non-negotiable)
  contracts/skill_grammar.md                                      — DSL keywords used in this body
  impl-quality/debug-handoff/examples/handoff-auth-redirect.md    — tone target: low-confidence hypothesis
  impl-quality/debug-handoff/examples/handoff-database-deadlock.md — tone target: medium-confidence hypothesis

MUST  ask each interview question as a STANDALONE message (Iron Laws § 9)
MUST  produce a handoff that conforms to the pinned schema (every required heading present)
MUST  ensure the output is self-contained — no relative paths, no in-chat references like "as discussed above"
MUST  redact obvious secrets (api keys, passwords, tokens) using <env:VAR_NAME> placeholders
MUST  state hypothesis confidence as exactly one of: low / medium / high
MUST  run validator.py on the produced handoff before returning; do not return until it passes
NEVER  link to chat history or local-only resources the next agent cannot access
NEVER  fabricate attempts or hypotheses — if the user did not state them, write "(none yet)"
NEVER  bundle the interview question into the same message as a status update — Iron Laws § 9 forbids it
NEVER  overwrite an existing _debug/<id>/handoff.md without showing the diff first

EMIT  [debug-handoff] started run_id=<uuid> bug_id=<id>

# ── STEP 1: Read or gather context ──────────────────────────

STEP 1: Resolve bug context
  IF _debug/<id>/context.md exists
    - Read it as authoritative.
    - Confirm the symptom and repro with the user as ONE standalone message:
      > "I found existing context at _debug/<id>/context.md. Symptom: <summary>. Still accurate, or has it changed?"
    - Wait for the answer before proceeding.
  ELSE
    - Send Q1 as a STANDALONE message (Iron Laws § 9):
      > "What's the bug? Two to five sentences — symptom + impact + how reliably you can reproduce it."
    - Wait for the answer.
    - Send Q2 as a STANDALONE message:
      > "How do I reproduce it? Numbered steps, or 'intermittent' with a frequency estimate."
    - Wait for the answer.
    - Derive <id>: kebab-case slug from the symptom (3-5 words max), or YYYY-MM-DD-HHMM if no clear noun.
    - Write _debug/<id>/context.md per the shared schema (see Pinned Schema below).

# ── STEP 2: Read prior protocol (if any) ────────────────────

STEP 2: Mine the protocol for attempts
  IF _debug/<id>/protocol.md exists
    - Parse its "Verification Steps" section. Each step that was executed becomes a row in the
      handoff's "Attempts So Far" table:
        Step name                 → "What was tried"
        Run output                → "Outcome"
        Why the step did not pass → "Why ruled out"
    - If no step produced a definitive outcome (all timed out / all stale), record that as a meta-row:
      "Ran self-verify protocol — no step produced a definitive verdict (output mismatch on N of M steps)".

# ── STEP 3: Identify "last working commit" candidates ───────

STEP 3: Read recent git history
  RUN  git log -10 --oneline
  - Send a STANDALONE message (Iron Laws § 9):
    > "Here are the 10 most recent commits. Which one was the last known good — i.e. the bug was not present at this SHA? Reply with the SHA, or 'unknown'."
  - Wait for the answer. Record the SHA (or "unknown") in the handoff's Environment section.

# ── STEP 4: Interview for missing fields ────────────────────

STEP 4: Walk the schema and ask one standalone question per still-empty section
  - For every required section in the pinned schema (below) that is still empty, send ONE standalone
    message asking for it. Iron Laws § 9 — never bundle questions.
  - Required sections that always need user input (cannot be inferred from prior artifacts):
    - "Current Hypothesis" (with confidence: low / medium / high)
    - "Suggested Next Steps"
    - "Open Questions for the Next Agent"
  - For "Out-of-Scope": send this question as a STANDALONE message verbatim:
    > "Are there any approaches you've ruled out that the next agent should NOT try? List them. If none, say 'none'."

# ── STEP 5: Draft handoff.md ────────────────────────────────

STEP 5: Write _debug/<id>/handoff.md per the pinned schema (below).
  - Resolve every <id> placeholder in the body to the actual slug.
  - Use absolute or repo-rooted paths only (e.g. `src/auth/login.ts`, never `../../auth/login.ts`).

# ── STEP 6: Self-redact pass ────────────────────────────────

STEP 6: Scan and redact secrets
  - Scan the draft for: hardcoded `Bearer ` strings, AWS-key-shaped tokens (`AKIA[0-9A-Z]{16}`),
    `process.env.SECRET_*` literal values, GitHub PATs (`ghp_[A-Za-z0-9]{36}`), email passwords,
    OAuth client secrets.
  - Replace each with `<env:VAR_NAME>` and add a one-line note in the "Environment" section:
    > "Redacted: <env:STRIPE_SECRET_KEY>, <env:AWS_ACCESS_KEY_ID>"
  - If any redaction happens, the user must be informed in the CHECKPOINT message before they paste.

# ── STEP 7: Self-validate ───────────────────────────────────

STEP 7: Run the validator
  RUN  python impl-quality/debug-handoff/validator.py _debug/<id>/handoff.md
  IF exit code != 0
    - Read the diagnostic, fix the handoff, re-run.
  UNTIL validator passes (exit 0).

# ── CHECKPOINT ──────────────────────────────────────────────

CHECKPOINT handoff_review
  Send a STANDALONE message (Iron Laws § 9):
  > "Handoff ready at _debug/<id>/handoff.md. Anything to add before you paste it into a fresh chat?"
  - If redactions happened in STEP 6, list them in this same message.
  - Wait for confirmation. If the user wants edits, apply them and re-validate.

EMIT  [debug-handoff] completed run_id=<uuid> bug_id=<id> attempts=<N> confidence=<low|medium|high>

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

## Pinned Schema — `_debug/<id>/handoff.md` (output)

The validator enforces this shape. Authoring is done when a produced handoff matches it AND
`validator.py` exits 0.

```markdown
# Debug Handoff — <id>

> Paste this entire file into a fresh chat. It is self-contained: no prior context required.

## Bug Description
<2-5 sentences. Symptom + impact + repro reliability.>

## Repro Steps
1. ...
2. ...

(If non-deterministic: state frequency, e.g. "fails ~30% of the time on Mondays".)

## Environment
- OS / runtime: <values>
- Branch / commit: <SHA>
- Relevant env vars: <redacted list>
- Last working commit (if known): <SHA>

## Attempts So Far

| # | What was tried | Outcome | Why ruled out |
|---|----------------|---------|---------------|
| 1 | <action>       | <result>| <reasoning>   |
| 2 | ...            | ...     | ...           |

## Current Hypothesis
<1-3 sentences. State confidence: low / medium / high.>

## Suggested Next Steps
1. <next experiment, with rationale>
2. <fallback experiment if 1 fails>
3. <escalation path if both fail — e.g. "ask the user for more logs">

## Files & Paths Involved
- `<path>` — <one-line role in the bug>
- ...

## Open Questions for the Next Agent
- <question 1>
- <question 2>

## Out-of-Scope (do NOT do these)
- <action that was explicitly ruled out by the user>
- ...
```

---

CHECKLIST
  - [ ] _debug/<id>/handoff.md exists and validator.py exits 0
  - [ ] All schema sections present and non-empty (or marked "(none yet)")
  - [ ] No relative chat references ("see above", "you mentioned earlier")
  - [ ] No `<id>` placeholder remains unresolved in the body
  - [ ] Secrets redacted to `<env:VAR>` placeholders, with redactions disclosed in the CHECKPOINT message
  - [ ] Confidence level on hypothesis is exactly one of: low / medium / high
  - [ ] User shown the handoff via a STANDALONE message (Iron Laws § 9)
