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
permanent artifacts, `concept-slice-design-feature` deletes the entire
`_concept/slices/<slice_id>/` directory.

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
  concept-slice/brainstorm/references/brainstorm-prompt-style.md — interview tone reference

REQUIRES
  hard: _concept/_meta/scope.yaml            — tier context
  state: scope.yaml `tier` ∈ {appbuilder-standard, appbuilder-complex}

# Constraints (placed early per skill_grammar.md § Authoring tip 4)

MUST  ask each interview question as its own standalone assistant message (iron_laws § 9)
MUST  refuse to run if _concept/_meta/scope.yaml is missing (iron_laws § 7)
MUST  refuse to run if scope.yaml `tier` ∈ {appbuilder-mvp, appbuilder-simple} — those tiers do not run concept-slice-brainstorm (per SKILL_GRAPH § 6 tier-composition table)
MUST  derive slice_id from feature_title via the kebab-case rule (lower → non-alnum→hyphen → strip-trim → max 48 chars) UNLESS slice_id_override is supplied
MUST  refuse to overwrite an existing _concept/slices/<slice_id>/ — ask the user to (a) resume the existing slice, or (b) suffix -2 to the slug
MUST  write the handoff frontmatter exactly as specified (slice_id, feature_title, phase, tier, created_at, last_updated)
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
  - Derive slice_id from feature_title using the kebab-case rule, OR use
    slice_id_override if provided. Validate against ^[a-z][a-z0-9-]{1,47}$.
  - Check whether _concept/slices/<slice_id>/ already exists.
    IF it exists
      - Ask STANDALONE:
        > "A slice with id `<slice_id>` already exists. Do you want to
        >  (a) resume that slice (read its existing brainstorm.md), or
        >  (b) start a fresh slice with the suffix `-2`?"
      - Wait for answer. Branch accordingly.
    ELSE
      - $ mkdir -p _concept/slices/<slice_id>/

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

STEP 4: Draft handoff in memory
  Compose the brainstorm.md content. Frontmatter:
    ```
    ---
    slice_id: <slug>
    feature_title: <user's title, verbatim>
    phase: brainstorm
    tier: <scope.tier>
    created_at: <ISO-8601 UTC, e.g. 2026-05-08T12:34:56Z>
    last_updated: <same as created_at on first write>
    ---
    ```

  Body sections (use these exact headers):
    ## Feature in one sentence
    ## Who uses it
    ## Trigger
    ## Happy path (3-7 bullets)
    ## Clearly out of scope
    ## Open questions for align

  Show the full draft to the user.

STEP 5: Approval
  CHECKPOINT brainstorm_draft
    > "Here's the brainstorm draft. Approve to write to
    >  _concept/slices/<slice_id>/brainstorm.md, or tell me what to change."

STEP 6: Write the handoff
  - Write _concept/slices/<slice_id>/brainstorm.md
  - Verify file exists and frontmatter parses

EMIT  [concept-slice-brainstorm] completed slice_id=<id> tier=<tier>

CHECKLIST
  - [ ] _concept/_meta/scope.yaml read and tier validated
  - [ ] slice_id derived (or overridden) and matches the directory created
  - [ ] All 5 interview questions sent as standalone messages, each answered before the next
  - [ ] Handoff frontmatter contains all 6 keys (slice_id, feature_title, phase, tier, created_at, last_updated)
  - [ ] All 6 body section headers present
  - [ ] User approved the draft via CHECKPOINT before write
  - [ ] _concept/slices/<slice_id>/brainstorm.md exists on disk
