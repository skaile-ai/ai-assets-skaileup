---
name: impl-slice-refactor
description: "Use when a slice has been recapped and you need a forced-simplification pass. Proposes 1-3 SMALLEST-IMPROVEMENT candidates that preserve behavior — only subtractions, simplifications, clarifications, never additions. Asks user to approve before any code edit. May exit with no edits if user declines or no candidate qualifies."
metadata:
  version: "1.0.0"
  tags:
    - impl-slice
    - refactor
    - simplify
    - subtract
    - force-simpler
    - per-slice
    - anti-addition
  stage: alpha
  artifacts:
    requires:
      - id: slice-impl-recap
        gate: hard
      - id: slice-impl-plan
        gate: hard
      - id: slice-impl-test
        gate: hard
    produces:
      - id: slice-impl-refactor
  prerequisites:
    files:
      - path: "_slice/impl/{slice_id}/recap.md"
        gate: hard
        description: "Predecessor handoff — recap.md drives Files-touched and slice context."
      - path: "_slice/impl/{slice_id}/plan.md"
        gate: hard
        description: "Plan provides slice scope and Definition-of-done context."
      - path: "_slice/impl/{slice_id}/test.md"
        gate: hard
        description: "Verify slice passes test gate (Decision: Done) before refactor."
    inputs_required:
      - id: slice_id
        label: "Slice id (== feature_slug); resolves to _slice/impl/<slice_id>/*.md"
        type: text
        hint: "Inherited verbatim from upstream phases."
    inputs_optional:
      - id: max_candidates
        label: "Maximum candidate count (1-3, default 3)"
        type: number
        default: 3
    reads:
      - path: "_slice/impl/{slice_id}/refactor.md"
        description: "Re-entry mode — refine an existing refactor proposal."
    produces:
      - path: "_slice/impl/{slice_id}/refactor.md"
        description: "Per-slice refactor handoff for impl-slice-commit."
---

# impl-slice-refactor — force-simplify

## Overview

Your default is to ADD complexity — a new helper, a new abstraction, a new
file. This skill exists to RESIST that. The only refactor types this skill
produces are SUBTRACT, SIMPLIFY, CLARIFY. There is no field for additions.

After a slice has been recapped, this skill inspects the slice's files and
proposes 1-3 SMALLEST-IMPROVEMENT candidates whose Type is one of
`subtraction`, `simplification`, `clarification`. Each candidate must
preserve behavior and declare HOW behavior preservation is verified. The
skill writes `_slice/impl/<slice_id>/refactor.md` with `Approval status:
pending`, asks the user to approve / reject / modify, and only then applies
edits to in-tree code (Iron Law § 8). The skill exits successfully whether
or not any edits were applied — `refactor.md` is the durable record either
way.

## The "smallest improvement" question

> "Could a new dev follow this without mental jumps?" (SKILL_GRAPH § 5.2)

Sample questions to ask yourself before proposing a candidate:

- What is the SHORTEST piece of code that, if removed, would make a future reader's life easier?
- Which name lies — promising more than the function does, or hiding what it does?
- Where does a flow split into two paths that could be one?
- Which abstraction is paying for itself with exactly one caller?
- What state is being tracked twice in different shapes?

## When to Use

- `_slice/impl/<slice_id>/recap.md` exists and the slice's `test.md` shows `Decision: Done`.
- The user wants a forced-simplification pass before commit.

## When NOT to Use

- The slice has not been recapped — run `impl-slice-recap` first.
- You are tempted to extract a new utility, helper, or abstraction — that is OUT OF SCOPE for this skill. The schema has no "addition" Type.
- For codebase-wide refactor reviews — out of scope for this per-slice skill.

---

ROLE Per-slice force-simplify — resists additions; proposes 1-3 subtract/simplify/clarify candidates with user approval before any in-tree edit.

READS
  _slice/impl/{slice_id}/recap.md                             — required (predecessor)
  _slice/impl/{slice_id}/plan.md                              — required (slice goal context)
  _slice/impl/{slice_id}/test.md                              — required (verify Decision: Done before refactor)
  ? <implementation files identified by recap.md "## Files touched">  — read-only inspection until approval
  ? _slice/impl/{slice_id}/refactor.md                        — re-entry mode

WRITES
  _slice/impl/{slice_id}/refactor.md                          — handoff for impl-slice-commit
  <in-tree code files>                                        — ONLY after user approval (Iron Law § 8)

REFERENCES
  SKILL_GRAPH.md                                              — § 5.2 per-slice impl loop
  contracts/iron_laws.md                                      — § 7, § 8, § 9
  contracts/skill_grammar.md                                  — DSL keywords
  contracts/asset_frontmatter.md                              — Skill SKILL.md schema
  impl-slice/refactor/references/anti-addition-rules.md       — long-form expansion + counter-examples
  docs/superpowers/plans/2C-impl-plan-align-vertical.md       — § Pinned plan.md Schema
  docs/superpowers/plans/2D-impl-slice-cluster.md             — § Pinned refactor.md Schema

REQUIRES
  hard: _slice/impl/{slice_id}/recap.md                       — predecessor handoff
  hard: _slice/impl/{slice_id}/plan.md
  hard: _slice/impl/{slice_id}/test.md

# Constraints (placed early per skill_grammar.md § Authoring tip 4 — these are LOAD-BEARING)

MUST  propose ONLY subtractions, simplifications, or clarifications (Type field restricted to {subtraction, simplification, clarification})
MUST  produce 1-3 candidates exactly. Not 0, not 4. If you cannot find 1, the slice is already minimal AND you must explain why in "## What I considered but rejected"
MUST  produce ≥ 1 item in "## What I considered but rejected" — naming an addition you considered and explaining why you did NOT propose it (this surfaces the bias and forces you to dismiss it explicitly)
MUST  ask the user for approval as a standalone message before any code edit (iron_laws § 8 + § 9)
MUST  set "Approval status: pending" in the initial write; update only after user response
MUST  refuse to run if recap.md, plan.md, or test.md is missing (iron_laws § 7)
MUST  refuse to run if test.md's Decision is not "Done"
MUST  copy slice_id, feature_title, feature_path, tier from recap.md frontmatter unchanged
MUST  preserve behavior — every candidate must declare HOW behavior preservation is verified (test, manual check, "no behavior to preserve")
MUST  set phase: refactor in the handoff frontmatter

NEVER  propose a new file, a new abstraction, a new helper, a new module — additions are out of scope (the schema has no "addition" Type)
NEVER  edit any in-tree file before "Approval status" is "approved" or "modified"
NEVER  exceed 3 candidates
NEVER  produce 0 candidates without an explicit explanation in "## What I considered but rejected"
NEVER  rationalize: "this is technically a simplification because it makes the future cleaner" — that is the bias talking

INPUT
  Read from: _concept/_grounding/impl-slice-refactor/input.json
  If missing, ask the user:
  - slice_id: Slice id (required) default: <none>
  - max_candidates: Maximum candidate count (optional, 1-3) default: 3

# ── Workflow ───────────────────────────────────────────────────────

STEP 0: Verify predecessors
  - Resolve recap.md, plan.md, test.md paths under _slice/impl/<slice_id>/.
  - If any is missing: refuse with explicit message:
    > "[impl-slice-refactor] _slice/impl/<slice_id>/<file> missing.
    >  Run upstream skill first (Iron Law § 7)."
  - Verify test.md contains the literal line `Decision: Done`. If not, refuse:
    > "[impl-slice-refactor] test.md decision is not Done. Resolve [BLOCKER]
    >  items before refactor."
  - Parse recap.md frontmatter; cache slice_id, feature_title, feature_path, tier.

STEP 1: Read implementation (read-only)
  - Read recap.md "## Files touched"; load each path as read-only context.
  - Cache the slice's symbols, function names, file boundaries.
  Inline MUST: NO file write of any kind in this step (Iron Law § 8).

STEP 2: Generate candidate ideas (deliberate over-generation)
  - Enumerate 4-6 candidate refactor ideas covering the design space:
    deletions, simplifications, clarifications — AND a couple of additions
    (the latter are deliberate so the next step has something to reject).
  - Brief each idea: one-line title, Type, one-line rationale.

STEP 3: Filter
  - Drop every idea whose Type is "addition" — new file, new helper, new abstraction.
  - Drop every idea that does not preserve behavior (lacks a test or check).
  - Drop every idea whose Risk is "high" without a clear preservation check.
  Inline MUST: at least 1 dropped addition is recorded for the rejected list.

STEP 4: Pick 1-3 candidates
  - From the surviving filtered set, pick the candidates with LOWEST risk
    and SMALLEST diff. Prefer subtraction > simplification > clarification.
  - Cap at min(max_candidates, 3).
  - Reject the rest; record at least 1 rejection (typically the deliberate
    "addition" from STEP 2) in `## What I considered but rejected`.

STEP 5: Write refactor.md (Approval status: pending)
  Frontmatter (cross-phase contract — copy from recap.md):
    ```
    ---
    slice_id: <feature_slug>
    feature_title: <copied verbatim>
    feature_path: <copied verbatim>
    phase: refactor
    tier: <copied verbatim>
    created_at: <ISO-8601 UTC; copy from recap.md if available, else now()>
    last_updated: <ISO-8601 UTC; now()>
    ---
    ```

  Body sections (use these exact headers, in order):
    ## Slice goal recap (1-2 lines)
    ## Smallest improvement candidates
    ## What I considered but rejected (1-3 items)
    ## User approval gate
    ## Applied changes

  - `## Slice goal recap (1-2 lines)`: copy from plan.md `## Slice scope`.
  - `## Smallest improvement candidates`: 1-3 numbered items. Each item:
    ```
    ### N. <one-line title>
    **Type:** subtraction | simplification | clarification
    **Files:** <relative paths, comma-separated>
    **Diff sketch:** (optional) a 5-15 line unified-diff-style sketch
    **Rationale:** 1-2 sentences. Why does removing/simplifying make the next reader's life easier?
    **Risk:** low | medium | high — <1 sentence on what could break>
    **Behavior preservation:** how is preservation verified? (test, manual check, or "no behavior to preserve — it's dead code")
    ```
  - `## What I considered but rejected (1-3 items)`: ≥ 1 numbered item; each names an idea (often an addition) and a 1-sentence "why not."
  - `## User approval gate`: exactly one line: `Approval status: pending`.
  - `## Applied changes`: exactly `_(none — approval pending)_`.

  Write to _slice/impl/<slice_id>/refactor.md.

STEP 6: Approval gate (STANDALONE message per iron_laws § 9)
  CHECKPOINT refactor_approval
    > "Refactor proposal for `<slice_id>` is ready at
    >  _slice/impl/<slice_id>/refactor.md. Which candidate(s) should I apply,
    >  if any? You can also reject all and we move on to commit."
  Wait for response. NO in-tree edits before this CHECKPOINT resolves
  (iron_laws § 8).

STEP 7: Apply (or record rejection)
  Inline MUST: NO in-tree edit before the user's response (Iron Law § 8).

  IF user approves candidate(s) N:
    - Apply the diff to in-tree files exactly as proposed.
    - Run the validator and the candidate's `Behavior preservation` test.
    - Set `Approval status: approved`.
    - Replace `## Applied changes` body with the actual edits made
      (file, hunk count, summary line).
  ELSE IF user requests modifications:
    - Apply the modified version after the user confirms the new diff.
    - Set `Approval status: modified`.
    - Populate `## Applied changes` with the modified edits.
  ELSE  # user rejects all
    - Set `Approval status: rejected`.
    - Replace `## Applied changes` body with `_(none — user declined refactor)_`.
  - Re-write _slice/impl/<slice_id>/refactor.md.

STEP 8: Validate
  - $ python3 impl-slice/refactor/validator.py _slice/impl/<slice_id>/refactor.md
  - On failure: report errors and STOP. Do not advance.

EMIT  [impl-slice-refactor] completed slice_id=<id> approval=<status> applied=<n>

CHECKLIST
  - [ ] 1-3 candidates produced; none has Type=addition
  - [ ] ≥ 1 item in "## What I considered but rejected"
  - [ ] Approval gate started as `pending`; resolved to approved|rejected|modified
  - [ ] No in-tree edits before user approval
  - [ ] Validator green for the chosen approval state
  - [ ] _slice/impl/<slice_id>/refactor.md exists with phase: refactor

---

## Common Mistakes

| Mistake | What to do instead |
|---|---|
| Proposing a "new helper" disguised as a simplification | Apply the addition heuristic from references/anti-addition-rules.md — extract that, instead, into the rejected list |
| Editing files before user approval | NEVER. The schema starts at `Approval status: pending` and only transitions after the user replies |
| Producing 0 candidates because "nothing to refactor" | Surface the dismissed candidates in "## What I considered but rejected" (≥ 1 required) |
| Producing 4+ candidates | Cap at 3. Pick the lowest-risk, smallest-diff trio |
| Listing candidate Type as "refactor" | Use the strict enum: subtraction \| simplification \| clarification |
