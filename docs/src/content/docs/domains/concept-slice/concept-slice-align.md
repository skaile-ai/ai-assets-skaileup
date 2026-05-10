---
title: "concept-slice-align"
description: "Use when concept-slice-brainstorm has completed (or as the entry point for simple-app) and you need to grill the user about THIS feature — surfaces edge cases, unstated rules, error states, role/permission gaps, and produces EARS-format acceptance cr"
sidebar:
  label: "concept-slice-align"
---

:::note[Skill manifest]
**Name:** `concept-slice-align`
**Stage:** alpha · **Version:** 1.0.0
**Tags:** concept-slice, align, interview, edge-cases, acceptance-criteria, grill-me
**Source:** [`skaileup/concept-slice/align/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/concept-slice/align/SKILL.md)
:::


# Concept-Slice Align

## Overview

`concept-slice-align` is the grill phase of the per-feature concept loop. It
reads the brainstorm handoff (or, for simple-app, kicks off the slice
directly) and runs an adversarial interview that surfaces:

- Edge cases the user hasn't voiced
- Error states ("what does the user see when X fails?")
- Role/permission matrices
- State transitions and concurrency rules
- Unstated assumptions

The output is `_slice/concept/<slice_id>/align.md`, which contains EARS-format
acceptance criteria, a permissions table, and a list of resolved/open
questions. `concept-slice-scope-feature` consumes this next.

**This is where rigor enters the loop.** Brainstorm captured the dream;
align makes it implementable.

---

ROLE Per-feature alignment grill — adversarial interviewer that surfaces edge cases, permissions, and acceptance criteria for ONE feature.

READS
  _concept/_meta/scope.yaml                  — required; tier
  _slice/concept/{slice_id}/brainstorm.md    — required IF tier ∈ {standard-app, complex-app}
                                               (simple-app skips brainstorm; align is the entry)
  ? _concept/discovery/brief.md              — optional; project-level context
  ? _concept/experience/features/**/*.md     — optional; sibling features
  ? _slice/concept/{slice_id}/align.md       — re-entry mode

WRITES
  _slice/concept/{slice_id}/align.md         — handoff for concept-slice-scope-feature

REFERENCES
  SKILL_GRAPH.md                             — § 4 concept-slice loop diagram
  contracts/iron_laws.md                     — § 7, § 9
  contracts/skill_grammar.md                 — DSL keywords
  concept-slice/align/references/align-prompt-style.md — interview tone reference

REQUIRES
  hard: _concept/_meta/scope.yaml            — tier context
  state: scope.yaml `tier` ∈ {simple-app, standard-app, complex-app}

# Constraints

MUST  ask each grill question as its own standalone assistant message (iron_laws § 9)
MUST  produce acceptance criteria in EARS format ("WHEN <trigger>, THE <system> SHALL <response>")
MUST  refuse to run if _concept/_meta/scope.yaml is missing (iron_laws § 7)
MUST  refuse to run if scope.yaml `tier` ∈ {standard-app, complex-app} AND _slice/concept/<slice_id>/brainstorm.md is missing
MUST  copy slice_id and feature_title from brainstorm.md when present; never re-derive
MUST  surface every P1 (blocking) open question to the user as a standalone message before writing align.md
MUST  emit an EARS-formatted acceptance criterion for every IN-scope happy-path bullet in brainstorm.md

NEVER  invent acceptance criteria the user did not confirm
NEVER  proceed past question N until the user has answered question N
NEVER  silently overwrite an existing align.md (re-entry mode requires explicit user confirmation)

INPUT
  Read from: _concept/_grounding/concept-slice-align/input.json
  If missing, ask the user:
  - slice_id: Slice id (required) default: <none>
  - feature_title: Feature title (optional, required for simple-app entry) default: <none>

# ── Workflow ───────────────────────────────────────────────────────

STEP 1: Read scope and resolve tier-dependent gate
  - Open _concept/_meta/scope.yaml; abort with explicit error if missing.
  - Read scope.tier.
  IF tier ∈ {standard-app, complex-app}
    - require _slice/concept/<slice_id>/brainstorm.md to exist
    - if missing, refuse with:
      > "[concept-slice-align] tier=<tier> requires
      >  _slice/concept/<slice_id>/brainstorm.md. Run concept-slice-brainstorm first."
  ELSE IF tier == simple-app
    - brainstorm.md not required; this skill is the cluster entry.
    - $ mkdir -p _slice/concept/<slice_id>/
    - if feature_title was not supplied, ask STANDALONE:
      > "What feature are we aligning on? One-sentence title."
  ELSE
    - refuse: tier=mvp does not run concept-slice-align (use impl-plan/plan-vertical).

STEP 2: Read brainstorm context (when present)
  - Load brainstorm.md frontmatter; copy slice_id, feature_title verbatim.
  - Send a STANDALONE 1-paragraph summary back as a sanity check:
    > "Quick recap of the brainstorm: <2-3 sentences echoing feature_title,
    >  who uses it, trigger, happy path>. Does this still match how you
    >  see it, or has anything shifted?"
  - Wait for confirmation/refinement.

STEP 3: Grill — state transitions (STANDALONE)
  > "What happens if the user starts the flow but doesn't complete it?
  >  Where does state go — saved? discarded? half-saved?"

STEP 4: Grill — boundary inputs (STANDALONE)
  > "What are the limits? Maximum length, minimum, zero, empty, very large?
  >  What's the system's behavior at each edge?"

STEP 5: Grill — concurrency (STANDALONE)
  > "Two users hit this at the same time. What's the rule — first-write-wins,
  >  last-write-wins, conflict shown to both, lock?"

STEP 6: Grill — permissions matrix (STANDALONE)
  > "Walk me through who can do what here. Guest? Member? Admin? Owner?
  >  I'll build a table — fill in the rows you have, I'll mark the rest TBD."

STEP 7: Grill — persistence + recovery (STANDALONE)
  > "If the user closes the tab mid-action, what's saved? When they
  >  re-open, what state do they land in?"

STEP 8: Grill — errors (STANDALONE)
  > "When this fails — network drop, validation error, server 500 —
  >  what does the user see? What can they do next?"

STEP 9: Grill — cross-feature touch points (STANDALONE)
  > "Does this feature read or write data owned by another feature?
  >  Which one? What's the contract?"

STEP 10: Surface P1 open questions
  - For each open question that BLOCKS scope-feature (e.g. "what's the
    persistence rule"), send STANDALONE before drafting align.md:
    > "Blocker: <question>. I need an answer before I can write align.md."
  - Wait for answer. Repeat until no P1 questions remain.

STEP 11: Draft align.md in memory
  Frontmatter (copy slice_id and feature_title from brainstorm.md, or fresh
  for simple-app):
    ```
    ---
    slice_id: <slug>
    feature_title: <verbatim>
    phase: align
    tier: <scope.tier>
    created_at: <ISO-8601 UTC; copy from brainstorm.md if present, else now()>
    last_updated: <ISO-8601 UTC; now()>
    ---
    ```

  Body sections (use these exact headers, in order):
    ## Feature recap (one sentence)
    ## Acceptance criteria (EARS)
    ## Edge cases
    ## Error states
    ## Permissions / roles
    ## Unstated assumptions exposed
    ## Resolved questions
    ## Open questions blocking scope-feature

  - `## Acceptance criteria (EARS)` MUST contain at least one line in
    "WHEN ..., THE SYSTEM SHALL ..." form.
  - `## Permissions / roles` MUST contain a markdown table with at least
    one role row + an actions header row.

STEP 12: Approval
  CHECKPOINT align_draft
    > "Here's the align draft with EARS criteria and permissions table.
    >  Approve to write to _slice/concept/<slice_id>/align.md, or tell me
    >  what to change."

STEP 13: Write the handoff
  - Write _slice/concept/<slice_id>/align.md
  - Verify file exists and frontmatter parses

EMIT  [concept-slice-align] completed slice_id=<id> tier=<tier> ears_count=<n> roles=<n>

CHECKLIST
  - [ ] scope.yaml read and tier validated
  - [ ] tier-dependent prerequisite check passed (brainstorm.md required for standard/complex)
  - [ ] All grill questions sent STANDALONE; each answered before next
  - [ ] P1 blockers surfaced and answered before draft
  - [ ] All 8 body sections present in draft
  - [ ] At least one EARS criterion present
  - [ ] Permissions table present (≥ 2 lines with `|`)
  - [ ] User approved draft via CHECKPOINT before write
  - [ ] _slice/concept/<slice_id>/align.md exists on disk

