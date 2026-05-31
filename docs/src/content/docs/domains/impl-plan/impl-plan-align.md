---
title: "impl-plan-align"
description: "Use when an implementation slice has its concept artifacts (feature.md + screens) frozen and needs a grill-me interview to surface unstated assumptions, technical constraints, and edge cases before plan-vertical writes the slice plan. Reads _concept/"
sourcePath: "skaileup/impl-plan/align/SKILL.md"
sidebar:
  label: "impl-plan-align"
---

:::note[Skill manifest]
**Name:** `impl-plan-align`
**Stage:** alpha · **Version:** 1.0.0
**Tags:** impl-plan, align, interview, grill-me, acceptance-criteria, edge-cases, per-slice
:::


# Implementation Align — per-slice grill

## Overview

`impl-plan-align` is the implementation-readiness grill of the per-slice impl-loop.
It runs after `impl-plan-brainstorm` (when tier ∈ {standard-app, complex-app}) or as
the cluster entry point (when tier == simple-app). It does NOT run for tier == mvp.

The skill inverts brainstorm: now the AI asks pointed questions, the user defends.
Pillars covered: state transitions, boundary inputs, concurrency, permissions,
persistence/offline, error states, cross-feature data, performance, test seam.

The output is `_slice/impl/<slice_id>/align.md` — a structured handoff file consumed
by `impl-plan-plan-vertical`. The `_slice/impl/<slice_id>/` directory is scratch and
is deleted by `impl-slice/commit` after the slice's atomic commit lands. None of the
impl-plan skills delete the dir themselves.

**Per-slice scope** is enforced. Edge cases discovered in this grill belong to THIS
feature; cross-feature touch points are documented but not grilled in depth (their
features have their own slice align runs).

## When to Use

- An implementation slice's concept artifacts (feature.md + screens) are frozen and
  the user is ready to commit to acceptance criteria for the implementation.
- Tier is `simple-app`, `standard-app`, or `complex-app`.
- For standard/complex: `_slice/impl/<id>/brainstorm.md` exists.

## When NOT to Use

- Tier is `mvp` — mvp skips align per SKILL_GRAPH § 6. Use `impl-plan-plan-vertical`.
- Concept artifacts are missing — refer the caller to `concept-slice/design-feature`.
- For standard/complex without brainstorm — refer the caller to `impl-plan-brainstorm`.

---

ROLE Per-slice implementation-readiness grill — adversarial interviewer that surfaces edge cases, technical constraints, and acceptance handoff for ONE feature's implementation.

READS
  _concept/_meta/scope.yaml                                       — required; tier
  _concept/product-spec/features/{group}/{feature_slug}.md        — required; permanent feature artifact
  _concept/experience/screens/{feature_slug}/*.md                 — required; permanent screen specs (≥ 1 file)
  _slice/impl/{slice_id}/brainstorm.md                            — required IF tier ∈ {standard-app, complex-app};
                                                                    ENTRY POINT IF tier == simple-app
  ? _concept/blueprint/datamodel/model.json                       — optional; data model for entity grilling
  ? _concept/blueprint/techstack.md                               — optional; stack constraints
  ? _slice/impl/{slice_id}/align.md                               — re-entry mode

WRITES
  _slice/impl/{slice_id}/align.md                                 — handoff for impl-plan-plan-vertical

REFERENCES
  SKILL_GRAPH.md                                                  — § 5.2 per-slice impl loop, § 6 tier composition
  contracts/iron_laws.md                                          — § 7 (no artifact without prerequisites), § 9 (standalone questions)
  contracts/skill_grammar.md                                      — DSL keywords
  contracts/asset_frontmatter.md                                  — § Skill SKILL.md frontmatter schema
  impl-plan/align/references/grill-style.md                       — interview tone reference + 9 grill pillars
  docs/superpowers/plans/2A-scope-project.md                      — § Pinned scope.yaml schema
  docs/superpowers/plans/2B-concept-slice-cluster.md              — § Pinned permanent artifact paths

REQUIRES
  hard: _concept/_meta/scope.yaml                                 — tier context
  state: scope.yaml `tier` ∈ {simple-app, standard-app, complex-app}

# Constraints (placed early per skill_grammar.md § Authoring tip 4)

MUST  ask each grill question as its own standalone assistant message (iron_laws § 9)
MUST  refuse to run if _concept/_meta/scope.yaml is missing or tier == mvp (mvp skips align per SKILL_GRAPH § 6)
MUST  refuse to run if the feature.md at _concept/product-spec/features/<group>/<feature_slug>.md is missing (iron_laws § 7)
MUST  refuse to run if tier ∈ {standard-app, complex-app} and _slice/impl/<slice_id>/brainstorm.md is missing
MUST  copy slice_id, feature_title, feature_path from brainstorm.md frontmatter when present; never re-derive
MUST  surface every P1 question to the user as a standalone message before writing align.md
MUST  copy EARS acceptance criteria from feature.md verbatim into "## Acceptance handoff"
MUST  set phase: align in the handoff frontmatter
MUST  produce at least one P1 or P2 question OR resolve every prior P1 with a "## Decisions made" entry — empty grills are not acceptable

NEVER  invent edge cases the user did not confirm — every "## Edge cases to handle" bullet must trace to a Q/A in "## Decisions made" or to a feature.md/screen line
NEVER  proceed past question N until the user has answered question N
NEVER  silently overwrite an existing align.md (re-entry mode requires explicit user confirmation)
NEVER  re-author EARS acceptance criteria — they live in feature.md and are copied verbatim

INPUT
  Read from: _concept/_grounding/impl-plan-align/input.json
  If missing, ask the user:
  - feature_slug: Kebab-case feature slug (required) default: <none>
  - slice_id_override: Override auto-derived slice id (optional) default: <feature_slug>

# ── Workflow ───────────────────────────────────────────────────────

STEP 1: Read scope and resolve tier-dependent gate
  - Open _concept/_meta/scope.yaml; abort with explicit error if missing.
  - Read scope.tier.
  IF tier == mvp
    - refuse: "[impl-plan-align] tier=mvp does not run align. Use impl-plan-plan-vertical."
  - Resolve feature_slug → feature_path:
    $ ls _concept/product-spec/features/*/<feature_slug>.md
    Refuse if zero or >1 matches.
  - slice_id := feature_slug (or slice_id_override if set).
  IF tier ∈ {standard-app, complex-app}
    - require _slice/impl/<slice_id>/brainstorm.md to exist
    - if missing, refuse with:
      > "[impl-plan-align] tier=<tier> requires
      >  _slice/impl/<slice_id>/brainstorm.md. Run impl-plan-brainstorm first."
    - copy slice_id, feature_title, feature_path from brainstorm.md frontmatter (verify match).
  ELSE  # tier == simple-app
    - brainstorm.md not required; this skill is the cluster entry.
    - $ mkdir -p _slice/impl/<slice_id>/
    - read feature_title from feature.md frontmatter (do not ask the user a redundant question).

STEP 2: Read context
  - Read brainstorm.md (when present); cache risks + open questions.
  - Read feature.md (always); cache title, body, "## Acceptance Criteria" section verbatim.
  - $ ls _concept/experience/screens/<feature_slug>/*.md  → read each.
  - Read model.json + techstack.md if present.

STEP 3: Recap and confirm scope (STANDALONE)
  > "I'm grilling on `<feature_title>`, tier `<tier>`. Concept summary: <1 paragraph
  >  derived from feature.md body + screen names>. Anything wrong before I start
  >  the grill?"
  CHECKPOINT recap_confirmed
  Wait for confirmation/refinement.

STEP 4: Grill — state transitions (STANDALONE)
  > "What happens if the user starts the flow but doesn't complete it? Is the partial
  >  state persisted, discarded, or shown as 'in progress'?"

STEP 5: Grill — boundary inputs (STANDALONE)
  > "What's the max/min/zero case for each user-supplied input? What does the system
  >  do at each boundary — reject, truncate, allow?"

STEP 6: Grill — concurrency (STANDALONE)
  > "Two users hit this at the same time on the same row. What's the rule —
  >  last-write-wins, optimistic locking, conflict UI?"

STEP 7: Grill — permissions (STANDALONE)
  > "Walk me through who can do what here. Guest? Member? Admin? Owner?
  >  I need a complete role × action matrix."

STEP 8: Grill — persistence and offline (STANDALONE)
  > "If the user closes the tab mid-action, what's saved? What happens on reload —
  >  resume, restart, or discard?"

STEP 9: Grill — errors (STANDALONE)
  > "What does the user see when this fails — toast, inline error, modal, retry button?
  >  What recovery actions are available?"

STEP 10: Grill — cross-feature data (STANDALONE)
  > "Does this feature touch any other feature's entities? Any FKs that span features?
  >  Who owns the contract?"

STEP 11: Grill — performance (STANDALONE)
  > "What's the worst-case data size — 10 rows, 1000 rows, 100k rows? What's the
  >  pagination/virtualization strategy?"

STEP 12: Grill — test seam (STANDALONE)
  > "How will we know this is working without manually clicking through? What's the
  >  smallest automated test we can write — unit, integration, or e2e?"

STEP 13: Surface P1 open questions
  - For each unanswered grill point that BLOCKS plan-vertical, send STANDALONE:
    > "P1 blocker: <question>. I need an answer before I can write align.md."
  - Wait for answer. Repeat until no P1 questions remain.

STEP 14: Draft align.md in memory
  Frontmatter (cross-phase contract):
    ```
    ---
    slice_id: <feature_slug>
    feature_title: <copied from brainstorm.md or feature.md, verbatim>
    feature_path: _concept/product-spec/features/<group>/<feature_slug>.md
    phase: align
    tier: <scope.tier>
    created_at: <ISO-8601 UTC; copy from brainstorm.md if present, else now()>
    last_updated: <ISO-8601 UTC; now()>
    ---
    ```

  Body sections (use these exact headers, in order):
    ## Feature recap (1-2 lines)
    ## Concept summary
    ## Open questions surfaced by the grill
    ## Edge cases to handle
    ## Constraints
    ### Technical
    ### Scope
    ### Deadline / supervision
    ## Decisions made
    ## Acceptance handoff

  - `## Feature recap` is 1-2 lines condensed from feature.md.
  - `## Concept summary` is 1 paragraph that NAMES every screen file by relative path
    under `_concept/experience/screens/<feature_slug>/`.
  - `## Open questions surfaced by the grill` is a numbered list. Each item starts
    with `^\d+\.\s+\[P1|P2|P3\]`. At least ONE [P1] or [P2] item is required UNLESS
    `## Decisions made` resolves every prior P1.
  - `## Edge cases to handle` is bullets with 1-sentence rationales. Every bullet
    traces to either a `## Decisions made` entry or a feature.md/screen line.
  - `## Constraints ### Technical` lists stack/library limitations, perf bounds.
  - `## Constraints ### Scope` lists what's IN this slice vs DEFERRED.
  - `## Constraints ### Deadline / supervision` lists supervision tier (autonomous /
    mostly autonomous / HITL per SKILL_GRAPH § 3) inferred from scope.yaml.
  - `## Decisions made` is Q/A pairs. Empty list ONLY if `## Open questions` has zero
    P1 items.
  - `## Acceptance handoff` is the EARS criteria from feature.md "## Acceptance
    Criteria" copied VERBATIM. At least one line in "WHEN ..., THE SYSTEM SHALL ..."
    form.

  Show the full draft to the user.

STEP 15: Approval
  CHECKPOINT align_draft
    > "Here's the impl-plan align draft for slice `<slice_id>`.
    >  Approve to write to _slice/impl/<slice_id>/align.md, or tell me what to change."

STEP 16: Write the handoff
  - Write _slice/impl/<slice_id>/align.md
  - Verify file exists and frontmatter parses
  - $ python3 impl-plan/align/validator.py _slice/impl/<slice_id>/align.md

EMIT  [impl-plan-align] completed slice_id=<id> tier=<tier> p1_count=<n> p2_count=<n>

CHECKLIST
  - [ ] _concept/_meta/scope.yaml read and tier validated (∈ {simple-app, standard-app, complex-app})
  - [ ] feature_slug resolved to a single _concept/product-spec/features/<group>/<feature_slug>.md
  - [ ] tier-dependent prerequisite check passed (brainstorm.md required for standard/complex)
  - [ ] _slice/impl/<slice_id>/ directory exists
  - [ ] All grill questions sent as STANDALONE messages; each answered before next
  - [ ] All P1 blockers surfaced and answered before draft
  - [ ] All 7 body sections present; `## Constraints` has all 3 sub-sections
  - [ ] At least one P1/P2 question in `## Open questions` OR every prior P1 resolved in `## Decisions made`
  - [ ] EARS acceptance criteria copied verbatim into `## Acceptance handoff` (≥ 1 EARS line)
  - [ ] User approved the draft via CHECKPOINT before write
  - [ ] _slice/impl/<slice_id>/align.md exists on disk and validator.py exits 0

