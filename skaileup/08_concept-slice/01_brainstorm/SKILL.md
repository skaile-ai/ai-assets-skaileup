---
name: concept-slice-brainstorm
description: "Use when starting per-feature concept work for a appbuilder-standard or appbuilder-complex — sparring partner that surfaces the user's mental model for THIS one feature (who uses it, what triggers it, the happy path, what's clearly out). Strictly open-ended — edge-case grilling is the next phase (concept-slice-align). Triggers on: 'brainstorm this feature', 'design a new feature', 'concept-slice start', 'feature kickoff'."
metadata:
  version: "1.0.0"
  tags:
    - concept-slice
    - brainstorm
    - interview
    - feature-discovery
    - per-feature
  stage: alpha
  artifacts:
    requires:
      - id: scope
        gate: hard
    consumes:
      - id: brief
        gate: soft
      - id: journeys
        gate: soft
      - id: slice-concept-brainstorm
        gate: soft
    produces:
      - id: slice-concept-brainstorm
  prerequisites:
    files:
      - path: "_concept/_meta/scope.yaml"
        gate: hard
        description: "Tier context required — produced by skaileup-scope-scope-project. Determines whether brainstorm runs (appbuilder-standard/appbuilder-complex) or is skipped (appbuilder-simple)."
    inputs_required:
      - id: feature_title
        label: "One-sentence title for the feature you want to design now"
        type: text
        hint: "Short, human-readable. Used to derive slice_id (kebab-case)."
    inputs_optional:
      - id: slice_id_override
        label: "Override the auto-generated slice id"
        type: text
        hint: "kebab-case, regex ^[a-z][a-z0-9-]{1,47}$ — only set if you want a slug different from the title-derived one."
    reads:
      - path: "_concept/discovery/brief.md"
        description: "Project-level context (audience, problem, hero flow)."
      - path: "_concept/experience/journeys/stories.yaml"
        description: "Existing user journeys — surfaces how this feature fits."
      - path: "_concept/slices/{slice_id}/brainstorm.md"
        description: "Re-entry mode — resume or refine an existing brainstorm."
    produces:
      - path: "_concept/slices/{slice_id}/brainstorm.md"
        description: "Per-feature brainstorm handoff for concept-slice-align."
---

# Concept-Slice Brainstorm

## Overview

This skill is the entry point of the per-feature concept loop for **appbuilder-standard**
and **appbuilder-complex** tiers. It sits before `concept-slice-align` and produces a
short, open-ended scratch document under `_concept/slices/<slice_id>/brainstorm.md`
that captures the user's elevator pitch for ONE feature.

**It is deliberately wide.** Edge cases, unstated rules, error states, and
acceptance criteria are NOT this skill's job — they belong to
`concept-slice-align`. Going there too early closes the design space before
the user has voiced what the feature even is.

The handoff file is consumed by `concept-slice-align`. After the full slice
chain (brainstorm → align → scope-feature → design-feature) commits the
permanent artifacts, `concept-slice-design-feature` freezes the dossier: it
writes `_concept/slices/<slice_id>/index.md` and keeps the phase handoffs as
permanent per-feature documentation. Nothing is deleted.

---

ROLE Per-feature brainstorm partner — surfaces the user's mental model for ONE feature in open-ended conversation. Refuses to enumerate edge cases.

READS
  _concept/_meta/scope.yaml                  — required; tier + project description
  ? _concept/discovery/brief.md              — optional; project-level context
  ? _concept/experience/journeys/stories.yaml — optional; existing journeys
  ? _concept/slices/{slice_id}/brainstorm.md  — re-entry mode (resume / refine)

WRITES
  _concept/slices/{slice_id}/brainstorm.md    — handoff for concept-slice-align

REFERENCES
  SKILL_GRAPH.md                             — § 4 concept-slice loop diagram
  contracts/iron_laws.md                     — § 7 (prerequisites), § 9 (standalone questions)
  contracts/skill_grammar.md                 — DSL keywords
  contracts/slice_loop.md                    — tier gates, slug rule, resume-or-fresh, handoff keys, freeze lifecycle
  contracts/phase_procedures.md              — shared handoff procedures (DO shared:*)
  concept-slice/brainstorm/references/brainstorm-prompt-style.md — interview tone reference

REQUIRES
  hard: _concept/_meta/scope.yaml            — tier context
  state: scope.yaml `tier` ∈ {appbuilder-standard, appbuilder-complex}

# Constraints (placed early per skill_grammar.md § Authoring tip 4)

MUST  ask each interview question as its own standalone assistant message (iron_laws § 9)
MUST  refuse to run without scope.yaml (contracts/slice_loop.md § Tier gate)
MUST  refuse to run if scope.yaml `tier` ∈ {appbuilder-mvp, appbuilder-simple} — those tiers do not run concept-slice-brainstorm (per SKILL_GRAPH § 6 tier-composition table)
MUST  derive slice_id per contracts/slice_loop.md § Slug rule UNLESS slice_id_override is supplied
MUST  apply contracts/slice_loop.md § Resume-or-fresh when _concept/slices/<slice_id>/ already exists
MUST  write handoff frontmatter per spec (contracts/slice_loop.md § Handoff frontmatter)
MUST  wait for the user to answer each question before sending the next

NEVER  enumerate edge cases — that is concept-slice-align's job
NEVER  invent acceptance criteria
NEVER  write the handoff before the user has confirmed feature_title and the happy path
NEVER  silently overwrite an existing _concept/slices/<slice_id>/brainstorm.md

INPUT
  Read from: _concept/_grounding/concept-slice-brainstorm/input.json
  If missing, ask the user:
  - feature_title: One-sentence title for the feature (required) default: <none>
  - slice_id_override: Override auto-generated slice id (optional) default: <auto-derived>

# ── Workflow ───────────────────────────────────────────────────────

STEP 1: Read scope and validate tier
  - Open _concept/_meta/scope.yaml; abort with explicit error if missing.
  - Read scope.tier. If tier ∈ {appbuilder-mvp, appbuilder-simple}, refuse with:
    > "[concept-slice-brainstorm] tier=<tier> does not run brainstorm.
    >  For appbuilder-simple start with concept-slice-align directly. For appbuilder-mvp run impl-plan/plan-vertical."
  - Cache scope.tier and scope.description for later.

STEP 2: Collect feature_title and derive slice_id
  - If feature_title was pre-supplied, use it. Else ask STANDALONE:
    > "What feature are we designing right now? Give me a one-sentence title."
  - Derive slice_id per contracts/slice_loop.md § Slug rule (or slice_id_override;
    validate against the regex there).
  - Apply contracts/slice_loop.md § Resume-or-fresh to _concept/slices/<slice_id>/brainstorm.md
    (offer (a) resume, (b) fresh slice with -2-suffixed slug).

STEP 3: Open-ended interview (each question STANDALONE)
  Send these questions one at a time. Wait for the answer before sending the next.

  Q1 — "In one sentence, what IS this feature? Pretend you are pitching it to
       a teammate who hasn't heard about it."

  Q2 — "Who is the primary user? What role do they have, and how often do they
       use this feature?"

  Q3 — "What event or moment triggers them to use this feature? Where in
       their day or workflow does it fit?"

  Q4 — "Walk me through the happy path in 3-7 bullets. High level — don't
       worry about edge cases yet."

  Q5 — "What's clearly OUT of scope? Anything you'd push back on if it came
       up later?"

STEP 4: Finalize
  DO shared:draft_checkpoint_write     (contracts/phase_procedures.md)
    artifact_path: _concept/slices/<slice_id>/brainstorm.md
    checkpoint_id: brainstorm_draft
  Frontmatter: concept-side keys (slice_loop.md § Handoff frontmatter),
  phase: brainstorm.
  Body sections (exact headers):
    ## Feature in one sentence
    ## Who uses it
    ## Trigger
    ## Happy path (3-7 bullets)
    ## Clearly out of scope
    ## Open questions for align

EMIT  [concept-slice-brainstorm] completed slice_id=<id> tier=<tier>

CHECKLIST
  - [ ] _concept/_meta/scope.yaml read and tier validated
  - [ ] slice_id derived (or overridden) and matches the directory created
  - [ ] All 5 interview questions sent as standalone messages, each answered before the next
  - [ ] Handoff frontmatter contains all 6 keys (slice_id, feature_title, phase, tier, created_at, last_updated)
  - [ ] All 6 body section headers present
  - [ ] User approved the draft via CHECKPOINT before write
  - [ ] _concept/slices/<slice_id>/brainstorm.md exists on disk
