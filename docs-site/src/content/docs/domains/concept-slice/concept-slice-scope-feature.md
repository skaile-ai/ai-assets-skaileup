---
title: "concept-slice-scope-feature"
description: "Use when concept-slice-align has completed and you need to draw the IN/OUT line for THIS feature — reads align's edge-case list, forces an IN/OUT/DEFER decision on each item, and produces the final scope decision that concept-slice-design-feature hon"
sidebar:
  label: "scope-feature"
---

:::note[Skill manifest]
**Name:** `concept-slice-scope-feature`
**Stage:** alpha · **Version:** 1.0.0
**Tags:** concept-slice, scope-feature, in-out, boundary, interview
**Source:** [`concept-slice/scope-feature/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/concept-slice/scope-feature/SKILL.md)
:::


# Concept-Slice Scope-Feature

## Overview

`concept-slice-scope-feature` reads the align handoff and, for each edge case
the user surfaced, forces an IN-scope / OUT-of-scope / DEFER decision. It
also lists required entities and required screens — the deterministic
inputs that `concept-slice-design-feature` will turn into permanent
artifacts.

**This is the firewall against scope creep.** Once this file is committed,
`concept-slice-design-feature` honors it strictly: no screens not listed,
no acceptance criteria not pre-cleared.

---

ROLE Per-feature scope adjudicator — turns align's edge cases into IN/OUT/DEFER buckets and pins required entities + screens.

READS
  _concept/_meta/scope.yaml                  — required; tier
  _slice/concept/{slice_id}/align.md         — required (predecessor handoff)
  ? _concept/experience/features/**/*.md     — optional; sibling features
  ? _slice/concept/{slice_id}/scope-feature.md — re-entry mode

WRITES
  _slice/concept/{slice_id}/scope-feature.md — handoff for concept-slice-design-feature

REFERENCES
  SKILL_GRAPH.md                             — § 4 concept-slice loop
  contracts/iron_laws.md                     — § 7, § 9
  concept-slice/scope-feature/references/scope-prompt-style.md — interview tone

REQUIRES
  hard: _concept/_meta/scope.yaml
  hard: _slice/concept/{slice_id}/align.md

# Constraints

MUST  read align.md and surface each edge case to the user as a STANDALONE IN/OUT/DEFER question (iron_laws § 9)
MUST  refuse to run if align.md is missing (iron_laws § 7)
MUST  copy slice_id and feature_title from align.md unchanged
MUST  filter acceptance criteria to IN-scope only (drop criteria whose edge case was marked OUT or DEFER)
MUST  list required screens in "<group>/<screen>" form (matches experience/screens/ directory layout)
MUST  refuse to run if scope.yaml `tier` ∈ {mvp} (mvp does not run concept-slice)

NEVER  silently move an item between IN/OUT/DEFER without user confirmation
NEVER  add edge cases align.md did not surface (cite-only — scope is a filter, not a generator)
NEVER  invent screen slugs that don't trace back to a feature happy-path bullet

INPUT
  Read from: _concept/_grounding/concept-slice-scope-feature/input.json
  If missing, ask the user:
  - slice_id: Slice id (required) default: <none>

# ── Workflow ───────────────────────────────────────────────────────

STEP 1: Read predecessor handoffs
  - Open _concept/_meta/scope.yaml; abort if missing.
  - Refuse if scope.tier == mvp.
  - Open _slice/concept/<slice_id>/align.md; abort with explicit error if missing:
    > "[concept-slice-scope-feature] _slice/concept/<slice_id>/align.md
    >  is missing. Run concept-slice-align first."
  - Parse align.md frontmatter; cache slice_id, feature_title, tier.
  - Parse the "## Edge cases" and "## Open questions blocking scope-feature"
    sections.

STEP 2: Walk each edge case (each STANDALONE)
  For each numbered edge case in align.md:
    Send STANDALONE:
    > "Edge case: <case verbatim>.
    >  Is this IN scope for this slice, OUT of scope (we ignore it),
    >  or DEFER (we'll do it later in another slice)?
    >  IN / OUT / DEFER + one-sentence rationale, please."
  Wait for answer; record decision + rationale.

STEP 3: Walk each open blocker (each STANDALONE)
  For each open question still unresolved in align.md:
    Send STANDALONE:
    > "Open question: <question>. Is this IN, OUT, or DEFER for THIS slice?"

STEP 4: Required entities
  Send STANDALONE:
  > "What entities does this feature read or write? (e.g. User, Todo,
  >  Comment) — these drive datamodel decisions later."

STEP 5: Required screens
  Send STANDALONE:
  > "What screens does this feature need? Use the form `<group>/<screen>`
  >  (e.g. `team-todo-comments/list`, `team-todo-comments/detail`).
  >  Group = feature_slug for slice-owned screens."

STEP 6: Draft scope-feature.md in memory
  Frontmatter (copy slice_id, feature_title, tier from align.md):
    ```
    ---
    slice_id: <slug>
    feature_title: <verbatim>
    phase: scope-feature
    tier: <tier>
    created_at: <copy from align.md if present, else now()>
    last_updated: <now()>
    ---
    ```

  Body sections (use these exact headers, in order):
    ## In scope
    ## Out of scope
    ## Deferred
    ## Owned by another feature
    ## Acceptance criteria (final)
    ## Required entities
    ## Required screens

  - `## In scope` MUST have at least one bullet.
  - `## Acceptance criteria (final)` MUST be the IN-scope subset of
    align.md's `## Acceptance criteria (EARS)` — copied verbatim.
  - `## Required screens` bullets MUST match `^- [a-z0-9-]+/[a-z0-9-]+$`
    (one screen per line).

STEP 7: Approval
  CHECKPOINT scope_decision
    > "Here's the scope decision: <n> IN, <n> OUT, <n> DEFER.
    >  Required entities: <list>. Required screens: <list>.
    >  Approve to write to _slice/concept/<slice_id>/scope-feature.md."

STEP 8: Write the handoff
  - Write _slice/concept/<slice_id>/scope-feature.md
  - Verify file exists and frontmatter parses

EMIT  [concept-slice-scope-feature] completed slice_id=<id> in_scope=<n> out=<n> deferred=<n> screens=<n> entities=<n>

CHECKLIST
  - [ ] scope.yaml read; tier validated
  - [ ] align.md present; frontmatter parsed
  - [ ] Each edge case in align.md got a STANDALONE IN/OUT/DEFER question
  - [ ] All 7 body sections present
  - [ ] `## In scope` has ≥ 1 bullet
  - [ ] Every screen line matches `^- <group>/<screen>$`
  - [ ] User approved via CHECKPOINT before write
  - [ ] _slice/concept/<slice_id>/scope-feature.md exists on disk

