---
title: "impl-plan-brainstorm"
description: "Use when starting per-slice implementation work for a feature in a standard-app or complex-app tier project. Sparring partner on risks, unknowns, dependencies for THIS feature only. Reads _concept/_meta/scope.yaml + _concept/product-spec/features/<gr"
sidebar:
  label: "impl-plan-brainstorm"
---

:::note[Skill manifest]
**Name:** `impl-plan-brainstorm`
**Stage:** alpha · **Version:** 2.0.0
**Tags:** impl-plan, brainstorm, planning, risks, decomposition, pre-implementation, unknowns, per-slice, feature-scoped
**Source:** [`skaileup/impl-plan/brainstorm/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/impl-plan/brainstorm/SKILL.md)
:::


# Implementation Brainstorm — per-slice

## Overview

`impl-plan-brainstorm` is the entry point of the per-slice impl-loop for **standard-app**
and **complex-app** tiers. It is scoped to ONE feature (the slice), not the whole project.
Its job is to surface implementation risks, unknowns, and dependencies — and to flush out
P1 questions that would otherwise block `impl-plan-align` from running a useful grill.

The output is `_slice/impl/<slice_id>/brainstorm.md` — a structured handoff file consumed
by `impl-plan-align`. The `_slice/impl/<slice_id>/` directory is scratch and is deleted by
`impl-slice/commit` after the slice's atomic commit lands. None of the impl-plan skills
delete the dir themselves.

**Per-slice scope** is the key behaviour change from the legacy project-wide brainstorm:
risks are listed for THIS feature only. Project-wide audits live in `ops/audit` or
`impl-quality/audit`. If the user asks for a project-wide brainstorm, refuse and refer
them to those skills.

## When to Use

- Starting per-slice implementation for a standard-app or complex-app feature whose
  concept artifacts (`feature.md` + screens) are already frozen.
- Re-entering an existing slice (`_slice/impl/<id>/brainstorm.md` exists) to refine risks
  or answer a previously-flagged P1 question.

## When NOT to Use

- Tier is `mvp` or `simple-app` — those tiers skip brainstorm per SKILL_GRAPH § 6 tier
  composition. Their entry point is `impl-plan-plan-vertical` (mvp) or `impl-plan-align`
  (simple-app). Refuse and point the caller at the right skill.
- Project-wide brainstorming — out of scope. Use `ops/audit` or `impl-quality/audit`.
- Concept artifacts are missing (`_concept/product-spec/features/<group>/<feature_slug>.md`
  not present). Refuse and refer the caller to `concept-slice/design-feature`.

---

ROLE Per-slice implementation brainstorm partner — surfaces risks, unknowns, and dependencies for ONE feature only. Refuses project-wide scope.

READS
  _concept/_meta/scope.yaml                                       — required; tier + project description
  _concept/product-spec/features/{group}/{feature_slug}.md        — required; the feature being planned
  ? _concept/experience/screens/{feature_slug}/*.md               — optional; screen specs for this feature
  ? _concept/blueprint/datamodel/model.json                       — optional; data model (entity-touching risks)
  ? _concept/blueprint/techstack.md                               — optional; stack-specific risks
  ? _slice/impl/{slice_id}/brainstorm.md                          — re-entry mode (resume/refine existing)

WRITES
  _slice/impl/{slice_id}/brainstorm.md                            — handoff for impl-plan-align

REFERENCES
  SKILL_GRAPH.md                                                  — § 5.2 per-slice impl loop, § 6 tier composition, § 7 workspace zones
  contracts/iron_laws.md                                          — § 7 (no artifact without prerequisites), § 9 (standalone questions)
  contracts/skill_grammar.md                                      — DSL keywords
  contracts/asset_frontmatter.md                                  — § Skill SKILL.md frontmatter schema
  docs/superpowers/plans/2A-scope-project.md                      — § Pinned scope.yaml schema
  docs/superpowers/plans/2B-concept-slice-cluster.md              — § Pinned permanent artifact paths

REQUIRES
  hard: _concept/_meta/scope.yaml                                 — tier context
  state: scope.yaml `tier` ∈ {standard-app, complex-app}

# Constraints (placed early per skill_grammar.md § Authoring tip 4)

MUST  ask each interview question as its own standalone assistant message (iron_laws § 9)
MUST  refuse to run if _concept/_meta/scope.yaml is missing (iron_laws § 7)
MUST  refuse to run if scope.yaml `tier` ∈ {mvp, simple-app} — those tiers do not run impl-plan-brainstorm (per SKILL_GRAPH § 6 tier-composition table); the base orchestrator is responsible for not invoking this skill at those tiers
MUST  resolve feature_slug to _concept/product-spec/features/<group>/<feature_slug>.md before any other step; refuse if file missing (iron_laws § 7)
MUST  scope brainstorm to THIS ONE feature; do NOT enumerate risks for other features
MUST  surface every P1 question to the user as a standalone message before writing brainstorm.md
MUST  write the handoff frontmatter exactly per the cross-phase contract (slice_id, feature_title, feature_path, phase, tier, created_at, last_updated)
MUST  set phase: brainstorm in the handoff frontmatter
MUST  set slice_id := feature_slug (raw kebab-case slug, regex ^[a-z][a-z0-9-]{1,47}$) — same rule as concept-slice
MUST  derive the {group} segment of feature_path by globbing _concept/product-spec/features/*/<feature_slug>.md and refusing if zero or >1 matches

NEVER  expand the scope to project-wide risks (that's a different skill — ops/audit or impl-quality/audit)
NEVER  write brainstorm.md before unresolved P1 blockers are surfaced and answered
NEVER  enumerate edge cases — that is impl-plan-align's grill (separation of concerns)
NEVER  invent acceptance criteria — they live in feature.md and are copied verbatim by impl-plan-align
NEVER  silently overwrite an existing _slice/impl/<slice_id>/brainstorm.md (re-entry: load it, show diff, ask)

INPUT
  Read from: _concept/_grounding/impl-plan-brainstorm/input.json
  If missing, ask the user:
  - feature_slug: Kebab-case feature slug (required) default: <none>
  - focus_area: Focus a single risk dimension (optional) [data | auth | integrations | stack | performance | ux] default: <none>

# ── Workflow ───────────────────────────────────────────────────────

STEP 1: Read scope and validate tier
  - Open _concept/_meta/scope.yaml; abort with explicit error if missing:
    > "[impl-plan-brainstorm] required file _concept/_meta/scope.yaml not found.
    >  Run skaileup-scope-scope-project first."
  - Read scope.tier. If tier ∈ {mvp, simple-app}, refuse with:
    > "[impl-plan-brainstorm] tier=<tier> does not run brainstorm.
    >  For simple-app start with impl-plan-align directly. For mvp run impl-plan-plan-vertical."
  - Cache scope.tier and scope.description for later.
  - Reminder placed inline (per skill_grammar.md § Authoring tip 1):
    MUST scope brainstorm to THIS ONE feature; do NOT enumerate risks for other features.

STEP 2: Resolve feature_slug → feature_path
  - If feature_slug was pre-supplied, use it. Else ask STANDALONE:
    > "Which feature are we brainstorming? Give me the kebab-case slug
    >  (the filename of _concept/product-spec/features/<group>/<feature_slug>.md)."
  - Validate slug against ^[a-z][a-z0-9-]{1,47}$.
  - $ ls _concept/product-spec/features/*/<feature_slug>.md
    IF zero matches
      - refuse: "[impl-plan-brainstorm] feature.md not found for slug <slug>. Run concept-slice/design-feature first."
    ELIF >1 match (slug collision across groups)
      - refuse with the matching paths and ask the user which group is intended.
    ELSE
      - feature_path := the single match; group := dirname.basename
  - slice_id := feature_slug.
  - Check whether _slice/impl/<slice_id>/ already exists.
    IF _slice/impl/<slice_id>/brainstorm.md exists
      - Ask STANDALONE:
        > "A brainstorm at _slice/impl/<slice_id>/brainstorm.md already exists.
        >  Do you want to (a) resume — refine the existing brainstorm,
        >  or (b) abandon and start fresh (overwrites)?"
      - Wait for answer. On (b), require explicit confirmation before any write.
    ELSE
      - $ mkdir -p _slice/impl/<slice_id>/

STEP 3: Read concept artifacts
  - Read feature.md (required). Note: title (frontmatter), first paragraph of body, data_entities[] if present, journey_stage if present.
  - $ ls _concept/experience/screens/<feature_slug>/*.md  → if any, read each.
  - Read _concept/blueprint/datamodel/model.json if present.
  - Read _concept/blueprint/techstack.md if present.
  - Reminder (inline MUST): scope to THIS feature only; mention other features only as cross-feature touch points, not as risk owners.

STEP 4: Assess risks across six dimensions
  For EACH dimension below, note known facts vs unknowns, scoped to THIS feature:
    - data            — entities touched, soft-deletes, multi-tenancy, FK ownership
    - auth            — role matrix completeness, session edge cases, gating
    - integrations    — external APIs, queues, webhooks (touched by THIS feature)
    - stack           — unfamiliar libraries, version constraints, perf hotspots
    - performance     — worst-case data sizes, expensive queries, real-time needs
    - ux              — multi-step flows, optimistic UI, offline behavior
  - If focus_area was supplied, deepen that dimension and list the others as one-line summaries.

STEP 5: Surface P1 questions (each STANDALONE)
  - For each unknown that BLOCKS impl-plan-align's grill, send STANDALONE:
    > "P1 blocker: <question>. I need an answer before I can write brainstorm.md."
  - Wait for answer. Repeat until no P1 questions remain unanswered.
  - P2 questions go in the handoff but do not block.
  - P3 questions are nice-to-know — also in the handoff.

STEP 6: Draft handoff in memory
  Frontmatter (cross-phase contract):
    ```
    ---
    slice_id: <feature_slug>
    feature_title: <title from feature.md frontmatter, verbatim>
    feature_path: _concept/product-spec/features/<group>/<feature_slug>.md
    phase: brainstorm
    tier: <scope.tier>
    created_at: <ISO-8601 UTC, e.g. 2026-05-08T12:34:56Z>
    last_updated: <same as created_at on first write>
    ---
    ```

  Body sections (use these exact headers, in order):
    ## App-level summary (1 paragraph)
    ## Feature summary (1 paragraph)
    ## Risks and unknowns
    ### Data
    ### Auth
    ### Integrations
    ### Stack
    ### Performance
    ### UX
    ## Open questions
    ## Recommended mitigations

  - `## App-level summary` is 1 paragraph derived from scope.description + 1 line "tier: <tier>".
  - `## Feature summary` is 1 paragraph derived from feature.md (title + first body paragraph).
  - `## Risks and unknowns` MUST contain all six sub-headings; an empty sub-heading must contain the literal `_(no risks identified for this feature)_`.
  - `## Open questions` MUST contain a markdown table with the header `| Priority | Question | Blocks |` and at least the table delimiter row.
  - `## Recommended mitigations` is a bullet list, one per significant risk (≥ one per non-empty risk sub-heading).

  Show the full draft to the user.

STEP 7: Approval
  CHECKPOINT brainstorm_draft
    > "Here's the impl-plan brainstorm draft for slice `<slice_id>`.
    >  Approve to write to _slice/impl/<slice_id>/brainstorm.md, or tell me what to change."

STEP 8: Write the handoff
  - Write _slice/impl/<slice_id>/brainstorm.md
  - Verify file exists and frontmatter parses
  - $ python3 impl-plan/brainstorm/validator.py _slice/impl/<slice_id>/brainstorm.md

EMIT  [impl-plan-brainstorm] completed slice_id=<id> tier=<tier> p1_count=<n> p2_count=<n>

CHECKLIST
  - [ ] _concept/_meta/scope.yaml read and tier validated (∈ {standard-app, complex-app})
  - [ ] feature_slug resolved to a single _concept/product-spec/features/<group>/<feature_slug>.md
  - [ ] _slice/impl/<slice_id>/ directory exists (created or pre-existing)
  - [ ] All concept artifacts (feature.md required; screens/model/techstack optional) read
  - [ ] Risk areas assessed across all six dimensions, scoped to THIS feature
  - [ ] All P1 questions surfaced as STANDALONE messages and answered before draft
  - [ ] Handoff frontmatter contains all 7 keys (slice_id, feature_title, feature_path, phase, tier, created_at, last_updated)
  - [ ] All 5 top-level body sections present; `## Risks and unknowns` has all 6 sub-headings
  - [ ] `## Open questions` has the priority table header line
  - [ ] User approved the draft via CHECKPOINT before write
  - [ ] _slice/impl/<slice_id>/brainstorm.md exists on disk and validator.py exits 0

