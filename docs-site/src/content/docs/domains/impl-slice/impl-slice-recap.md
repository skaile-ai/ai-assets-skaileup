---
title: "impl-slice-recap"
description: "Use when a slice has passed the per-slice test gate and needs the mandatory recap step. Produces a 1-3 sentence 'what was built' summary, an ASCII diagram of the feature flow (mandatory), a Files-touched list, and an Outcome-vs-plan comparison. Skipp"
sidebar:
  label: "recap"
---

:::note[Skill manifest]
**Name:** `impl-slice-recap`
**Stage:** alpha · **Version:** 1.0.0
**Tags:** impl-slice, recap, diagram, ascii, mandatory, per-slice, documentation
**Source:** [`impl-slice/recap/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/impl-slice/recap/SKILL.md)
:::


# impl-slice-recap — mandatory recap + diagram

## Overview

The diagram is mandatory. Skipping it produces a slice that no future agent
can reason about without re-reading every file. After the slice has passed
`impl-slice-test`, this skill captures (1) what was built in user-visible
terms, (2) an ASCII diagram of the feature flow, (3) a Files-touched list,
and (4) an Outcome-vs-plan comparison. The output is `_slice/impl/<slice_id>/
recap.md` — the predecessor handoff for `impl-slice-refactor`.

## When to Use

- `_slice/impl/<slice_id>/test.md` exists with `Decision: Done`.
- The user wants to lock in the slice's mental model before refactoring or committing.

## When NOT to Use

- Slice has not passed the per-slice test gate — run `impl-slice-test` first.
- For codebase-wide architecture diagrams — out of scope for this per-slice skill.
- For commit-message authoring — that lives in `impl-slice-commit`.

---

ROLE Per-slice recap — produces a flow diagram + comparison to plan in `_slice/impl/<slice_id>/recap.md`.

READS
  _slice/impl/{slice_id}/test.md                              — required (predecessor)
  _slice/impl/{slice_id}/plan.md                              — required (read for goal recap + DoD)
  ? _slice/impl/{slice_id}/recap.md                           — re-entry mode
  ? <implementation files identified by git diff>             — optional; informs Files touched

WRITES
  _slice/impl/{slice_id}/recap.md                             — handoff for impl-slice-refactor

REFERENCES
  SKILL_GRAPH.md                                              — § 5.2 per-slice impl loop
  contracts/iron_laws.md                                      — § 7 (no artifact without prerequisites), § 9 (standalone questions)
  contracts/skill_grammar.md                                  — DSL keywords
  contracts/asset_frontmatter.md                              — Skill SKILL.md schema
  impl-slice/recap/references/diagram-shapes.md               — 5 starter ASCII shapes
  docs/superpowers/plans/2C-impl-plan-align-vertical.md       — § Pinned plan.md Schema
  docs/superpowers/plans/2D-impl-slice-cluster.md             — § Pinned recap.md Schema

REQUIRES
  hard: _slice/impl/{slice_id}/test.md                        — predecessor handoff
  hard: _slice/impl/{slice_id}/plan.md                        — plan context

# Constraints (placed early per skill_grammar.md § Authoring tip 4)

MUST  produce an ASCII diagram in a fenced code block — diagram is MANDATORY (SKILL_GRAPH § 5.2)
MUST  describe what was built in user-visible terms (what the user sees / does), NOT in implementation terms (which file changed)
MUST  cover all 5 body sections; the diagram section is non-negotiable
MUST  refuse to run if _slice/impl/<slice_id>/test.md is missing (iron_laws § 7)
MUST  refuse to run if test.md `Decision:` is not "Done"
MUST  copy slice_id, feature_title, feature_path, tier from test.md frontmatter unchanged
MUST  ask any clarification question as its own standalone message (iron_laws § 9)
MUST  set phase: recap in the handoff frontmatter

NEVER  produce a recap without an ASCII diagram (paragraph-only is not acceptable)
NEVER  describe the slice in pure-implementation terms ("modified file X to call Y")
NEVER  exceed 3 sentences in "## What was built (1-3 sentences)" without a follow-up trim

INPUT
  Read from: _concept/_grounding/impl-slice-recap/input.json
  If missing, ask the user:
  - slice_id: Slice id (required) default: <none>
  - diagram_type: Diagram flavour (optional) [data-flow | control-flow | component-tree | state-machine | request-lifecycle] default: data-flow

# ── Workflow ───────────────────────────────────────────────────────

STEP 0: Verify predecessors
  - Resolve plan.md and test.md paths under _slice/impl/<slice_id>/.
  - If either is missing: refuse with explicit message:
    > "[impl-slice-recap] _slice/impl/<slice_id>/<file> missing. Run upstream
    >  skill (impl-plan-plan-vertical or impl-slice-test) first (Iron Law § 7)."
  - Parse test.md frontmatter; cache slice_id, feature_title, feature_path, tier.
  - Verify test.md contains the literal line `Decision: Done`. If not, refuse:
    > "[impl-slice-recap] test.md decision is not Done. Resolve [BLOCKER]
    >  items in test.md '## Outstanding issues' before recap."
  - Read plan.md `## Slice scope` (1-2 lines copied verbatim into recap.md).
  - Read plan.md `## Definition of done` items.

STEP 1: Derive Files touched
  - Determine the slice base commit (use `_implementation/git-state.json` if present;
    else use `git log --oneline -20` heuristic — the commit just before the slice
    started). If ambiguous, ask the user as a STANDALONE message.
  - $ git diff --name-status <base>..HEAD
  - Build a list of bullets: `<path> (new|modified|deleted)`.
  - Drop irrelevant paths if the slice is narrower than the working tree.

STEP 2: Draft "What was built (1-3 sentences)"
  - Plain English, user-visible terms ("Members can post comments and see them
    update live across browsers", NOT "Added comments.tsx and a tRPC mutation").
  - Aim for 1-2 sentences; allow 3 only if the slice covers genuinely two
    user-visible behaviours.

STEP 3: Compose the ASCII diagram
  - Default `diagram_type: data-flow`. Consult references/diagram-shapes.md
    for the matching starter shape.
  - Customize the starter:
    - Rename nodes to this slice's actors (UI screen, handler/route, store/table).
    - Add error paths if the slice has explicit failure modes.
    - Add branches if the flow has decision points.
  - The diagram MUST live in a fenced code block (```), with NO language
    identifier, contain ≥ 5 non-empty lines, and use at least one of the
    diagram characters: → > | ─ +.
  - Soft note: some viewers strip `→`. Prefer `>` if portability matters; the
    validator accepts both.

STEP 4: Compose Outcome vs. plan
  Three sub-headings:
    ### Met expectations
    ### Deviated
    ### Carried over
  - `### Met expectations`: bullets from plan.md `## Definition of done` that
    are now true. Reference the matching test.md PASS lines.
  - `### Deviated`: bullets where the implementation differs from the plan,
    with a 1-line "why".
  - `### Carried over`: bullets pulled from plan.md `## Open carry-overs` that
    are still open.

STEP 5: Assemble draft recap.md in memory; show to user; CHECKPOINT
  CHECKPOINT recap_draft
    > "Here's the recap for `<slice_id>` — 1-3 sentence summary, ASCII
    >  diagram, files touched, outcome vs plan. Approve to write to
    >  _slice/impl/<slice_id>/recap.md, or tell me what to change."

STEP 6: Write the handoff
  Frontmatter (cross-phase contract — copy from test.md):
    ```
    ---
    slice_id: <feature_slug>
    feature_title: <copied verbatim>
    feature_path: <copied verbatim>
    phase: recap
    tier: <copied verbatim>
    created_at: <ISO-8601 UTC; copy from test.md if available, else now()>
    last_updated: <ISO-8601 UTC; now()>
    ---
    ```

  Body sections (use these exact headers, in order):
    ## Slice goal recap (1-2 lines)
    ## What was built (1-3 sentences)
    ## ASCII diagram
    ## Files touched
    ## Outcome vs. plan
    ### Met expectations
    ### Deviated
    ### Carried over

  Write to _slice/impl/<slice_id>/recap.md.

STEP 7: Validate
  - $ python3 impl-slice/recap/validator.py _slice/impl/<slice_id>/recap.md
  - On failure: report errors and STOP. Do not advance.

EMIT  [impl-slice-recap] completed slice_id=<id> diagram_type=<type> files_touched=<n>

CHECKLIST
  - [ ] _slice/impl/<slice_id>/test.md verified Decision: Done
  - [ ] _slice/impl/<slice_id>/plan.md read; "## Slice scope" + DoD cached
  - [ ] All 5 body sections present
  - [ ] ASCII diagram present in fenced block, ≥ 5 lines, contains → > | ─ or +
  - [ ] _slice/impl/<slice_id>/recap.md written; validator.py exits 0

---

## Common Mistakes

| Mistake | What to do instead |
|---|---|
| Paragraph-only "what was built" with no diagram | Diagram is MANDATORY — pick a shape from references/diagram-shapes.md |
| Implementation-language description ("modified X to call Y") | Re-write in user-visible terms ("Members can edit their own comments") |
| Diagram with only labels, no arrows or boxes | The validator pins ≥ 5 lines and at least one of → > \| ─ + |
| Skipping "Outcome vs. plan" because all DoD items are green | Always emit all three sub-headings; "Deviated" can be `_(none)_` |

