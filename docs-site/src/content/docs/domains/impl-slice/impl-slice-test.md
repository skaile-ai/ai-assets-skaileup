---
title: "impl-slice-test"
description: "Use when a slice's implement step has finished and you need a per-slice usability gate before proceeding to recap. Runs manual checks + automated tests from plan.md ## Testing strategy, captures user usability observations, emits a Done/NeedsMoreWork"
sidebar:
  label: "test"
---

:::note[Skill manifest]
**Name:** `impl-slice-test`
**Stage:** alpha · **Version:** 1.0.0
**Tags:** impl-slice, test, usability, per-slice, gate, feedback-loop
**Source:** [`impl-slice/test/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/impl-slice/test/SKILL.md)
:::


# impl-slice-test — per-slice usability gate

## Overview

Runs the slice's manual checks and automated tests defined by `plan.md ## Testing
strategy`, captures usability observations from the user (does it FEEL right?),
and emits exactly one of three decisions: `Done`, `Needs more work`, or
`Blocked`. The slice does not advance to `impl-slice-recap` unless the user
confirms `Decision: Done`.

This is a **slice-scoped gate**, not a codebase-wide regression suite. The
distinction matters: `impl-quality/test-{unit,integration,e2e}` run all tests
across the project after each slice; this skill runs only what `plan.md`
declared for THIS slice and adds an explicit usability check that the regression
suites cannot capture.

| Skill | Scope | When |
|---|---|---|
| `impl-slice-test` (this) | One slice | Inside the per-slice loop, before recap/refactor/commit |
| `impl-quality/test-unit` | Whole repo | Between slices or at release |
| `impl-quality/test-integration` | Whole repo | Between slices or at release |
| `impl-quality/test-e2e` | Whole repo | Between slices or at release |

## When to Use

- `impl-slice-implement` has just landed code for one slice and the slice needs
  to be gated before `recap`/`refactor`/`commit`.
- The slice's `plan.md` exists at `_slice/impl/<slice_id>/plan.md`.
- The user is available to answer 4 short usability questions.

## When NOT to Use

- Running the whole project's test suite — use `impl-quality/test-unit`,
  `impl-quality/test-integration`, or `impl-quality/test-e2e` instead.
- The slice's `plan.md` does not exist — run `impl-plan-plan-vertical` first.
- No code has been implemented yet — run `impl-slice-implement` first.

---

ROLE Per-slice usability gate — runs slice tests + asks usability questions; produces a Done/NeedsMoreWork/Blocked verdict in `_slice/impl/<slice_id>/test.md`.

READS
  _slice/impl/{slice_id}/plan.md                              — required (predecessor handoff per Task 2C)
  ? _slice/impl/{slice_id}/test.md                            — re-entry mode
  ? package.json                                              — optional; test runner detection
  ? pyproject.toml                                            — optional; test runner detection

WRITES
  _slice/impl/{slice_id}/test.md                              — handoff for impl-slice-recap

REFERENCES
  SKILL_GRAPH.md                                              — § 5.2 per-slice impl loop
  contracts/iron_laws.md                                      — § 7 (no artifact without prerequisites), § 9 (standalone questions)
  contracts/skill_grammar.md                                  — DSL keywords
  contracts/asset_frontmatter.md                              — Skill SKILL.md schema
  impl-slice/test/references/usability-question-pillars.md    — sample usability prompts and tone guidance
  docs/superpowers/plans/2C-impl-plan-align-vertical.md       — § Pinned plan.md Schema
  docs/superpowers/plans/2D-impl-slice-cluster.md             — § Pinned test.md Schema

REQUIRES
  hard: _slice/impl/{slice_id}/plan.md                        — predecessor handoff

# Constraints (placed early per skill_grammar.md § Authoring tip 4)

MUST  ask each usability question as its own standalone message (iron_laws § 9)
MUST  refuse to run if _slice/impl/<slice_id>/plan.md is missing (iron_laws § 7)
MUST  copy slice_id, feature_title, feature_path, tier from plan.md frontmatter unchanged
MUST  tag every "## Manual checks done" bullet with [PASS|FAIL|SKIPPED]
MUST  tag every "## Automated tests run" bullet with [PASS|FAIL|SKIPPED]
MUST  emit exactly one "Decision: Done|Needs more work|Blocked" line
MUST  refuse to emit "Decision: Done" if "## Outstanding issues" contains any [BLOCKER]
MUST  set phase: test in the handoff frontmatter
MUST  source every Manual-checks-done bullet from plan.md "### Manual checks"
MUST  source every Automated-tests-run bullet from plan.md "### Automated tests"

NEVER  run the project's full regression suite — that is impl-quality/test-{unit,integration,e2e}
NEVER  invent manual checks or automated tests not in plan.md "## Testing strategy"
NEVER  proceed past a usability question until the user has answered it
NEVER  bundle multiple interview questions in a single message

INPUT
  Read from: _concept/_grounding/impl-slice-test/input.json
  If missing, ask the user:
  - slice_id: Slice id (== feature_slug) (required) default: <none>

# ── Workflow ───────────────────────────────────────────────────────

STEP 0: Verify predecessor handoff
  - Resolve plan.md path: _slice/impl/<slice_id>/plan.md
  - If missing: refuse with explicit message:
    > "[impl-slice-test] _slice/impl/<slice_id>/plan.md is missing.
    >  Run impl-plan-plan-vertical first (Iron Law § 7)."
  - Parse plan.md frontmatter; cache slice_id, feature_title, feature_path, tier.
  - Verify slice_id matches input slice_id; refuse on mismatch.
  - Extract `## Testing strategy ### Manual checks` bullets.
  - Extract `## Testing strategy ### Automated tests` bullets.
  - Extract `## Slice scope` line (1-2 lines copied verbatim into test.md).

STEP 1: Run manual checks (one question per bullet, each STANDALONE)
  For each bullet under plan.md "### Manual checks":
    - Send a STANDALONE message to the user (iron_laws § 9):
      > "Manual check: <bullet text>
      >  Did this pass? Reply PASS, FAIL, or SKIPPED, plus a 1-line note."
    - Wait for response.
    - Record `[PASS|FAIL|SKIPPED]` + 1-line note for the bullet.
  NEVER bundle multiple manual-check questions into one message.

STEP 2: Run automated tests
  For each bullet under plan.md "### Automated tests":
    - Determine the command (the bullet text either includes the command
      or names the test; if ambiguous, ask the user as a STANDALONE message).
    - $ <test command>
    - Capture exit code.
    - Record `[PASS|FAIL|SKIPPED]` + actual command + exit code for the bullet.
  Detect runner from package.json or pyproject.toml when convenient.
  NEVER run tests outside this slice's plan.md list.

STEP 3: Usability interview (4 STANDALONE questions)
  Use the four sample prompts from references/usability-question-pillars.md.
  Each is its own assistant message; wait for the answer before sending the next.
  Default 4 prompts (substitute alternates from the reference file when fitting):
    1) "Did the flow feel awkward — too many clicks, too much text, hidden state?"
    2) "Was anything surprising — buttons in wrong places, naming inconsistent with the rest of the app?"
    3) "Would a new user get stuck anywhere?"
    4) "Does any screen have too much going on?"
  Record each answer as a free-form bullet in the draft `## Usability observations`.

STEP 4: Compose Outstanding issues
  - From STEP 1 FAILed manual checks → numbered items, tagged [BLOCKER|SHOULD-FIX|NICE-TO-HAVE].
  - From STEP 2 FAILed automated tests → numbered items, tagged [BLOCKER|SHOULD-FIX|NICE-TO-HAVE].
  - From STEP 3 user-flagged usability concerns → numbered items, tagged.
  - If a manual check or test was SKIPPED with a critical reason, surface it as [SHOULD-FIX].
  - Default tag for FAIL: [BLOCKER]. Promote to [SHOULD-FIX] only on user override.

STEP 5: Propose Decision
  - If `## Outstanding issues` contains zero [BLOCKER] items → propose `Decision: Done`.
  - Else if any [BLOCKER] is rooted in this slice → propose `Decision: Needs more work`.
  - Else if a [BLOCKER] is rooted OUTSIDE the slice (concept gap, infra missing,
    upstream dependency not delivered) → propose `Decision: Blocked`.
  CHECKPOINT decision_proposal
    > "Proposed `Decision: <value>` based on <n> blockers. Approve to write
    >  test.md, or tell me which issue you want re-tagged or removed."

STEP 6: Write the handoff
  Frontmatter (cross-phase contract — copy slice_id, feature_title, feature_path, tier
  from plan.md verbatim):
    ```
    ---
    slice_id: <feature_slug>
    feature_title: <copied verbatim>
    feature_path: <copied verbatim>
    phase: test
    tier: <copied verbatim>
    created_at: <ISO-8601 UTC; copy from plan.md if available, else now()>
    last_updated: <ISO-8601 UTC; now()>
    ---
    ```

  Body sections (use these exact headers, in order):
    ## Slice goal recap (1-2 lines)
    ## Manual checks done
    ## Automated tests run
    ## Usability observations
    ## Outstanding issues
    ## Decision

  - `## Slice goal recap (1-2 lines)`: copy verbatim from plan.md `## Slice scope`.
  - `## Manual checks done`: every plan.md `### Manual checks` bullet appears here, tagged.
  - `## Automated tests run`: every plan.md `### Automated tests` bullet appears here, tagged.
  - `## Usability observations`: free-form bullets from STEP 3.
  - `## Outstanding issues`: numbered list from STEP 4. `_(none)_` allowed.
  - `## Decision`: exactly one line: `Decision: Done` | `Decision: Needs more work` | `Decision: Blocked`.

  Write to _slice/impl/<slice_id>/test.md.

STEP 7: Validate
  - $ python3 impl-slice/test/validator.py _slice/impl/<slice_id>/test.md \
        --plan _slice/impl/<slice_id>/plan.md
  - On failure: report errors and STOP. Do not advance.

EMIT  [impl-slice-test] completed slice_id=<id> decision=<value> blockers=<n>

CHECKLIST
  - [ ] _slice/impl/<slice_id>/plan.md read; frontmatter cached
  - [ ] All plan.md "### Manual checks" bullets answered and tagged [PASS|FAIL|SKIPPED]
  - [ ] All plan.md "### Automated tests" bullets executed and tagged [PASS|FAIL|SKIPPED]
  - [ ] 4 usability questions asked as standalone messages and answered
  - [ ] "## Decision" line emitted; if Done, zero [BLOCKER] in Outstanding issues
  - [ ] _slice/impl/<slice_id>/test.md exists on disk and validator.py exits 0

---

## Common Mistakes

| Mistake | What to do instead |
|---|---|
| Running the full project regression suite | Run only the bullets in plan.md "## Testing strategy" |
| Bundling all 4 usability questions in one prompt | Send each as its own assistant message (Iron Law § 9) |
| Marking `Decision: Done` with a [BLOCKER] in Outstanding issues | Resolve the blocker (back to implement) or re-tag with user approval |
| Inventing a new test command not in plan.md | Refuse — surface the gap to the user; update plan.md upstream if needed |
| Skipping the usability questions because tests passed | Usability is the gate's distinguishing feature — every slice gets all 4 |

