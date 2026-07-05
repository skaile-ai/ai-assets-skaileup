---
name: impl-plan-align
description: "Use when an implementation slice has its concept artifacts (feature.md + screens) frozen and needs a grill-me interview to surface unstated assumptions, technical constraints, and edge cases before plan-vertical writes the slice plan. Reads _concept/experience/features/<group>/<feature_slug>.md + _implementation/slices/<id>/brainstorm.md (if standard/complex tier). Writes _implementation/slices/<id>/align.md. Triggers on: 'align this slice', 'grill me on the implementation', 'lock down impl assumptions', 'pre-plan grill'."
metadata:
  version: "1.0.0"
  tags:
    - impl-plan
    - align
    - interview
    - grill-me
    - acceptance-criteria
    - edge-cases
    - per-slice
  stage: alpha
  artifacts:
    requires:
      - id: scope
        gate: hard
      - id: features
        gate: hard
      - id: screens
        gate: hard
    consumes:
      - id: slice-impl-brainstorm
        gate: soft
      - id: datamodel
        gate: soft
      - id: techstack
        gate: soft
    produces:
      - id: slice-impl-align
      - id: glossary
      - id: impl-decisions
  prerequisites:
    files:
      - path: "_concept/_meta/scope.yaml"
        gate: hard
        description: "Tier context required — produced by skaileup-scope-scope-project."
      - path: "_concept/experience/features/{feature_slug}.md"
        gate: hard
        description: "Permanent feature artifact written by concept-slice-design-feature."
      - path: "_concept/experience/screens/{feature_slug}/"
        gate: hard
        description: "Permanent screen specs for this feature (≥ 1 file expected)."
        min_entries: 1
      - path: "_implementation/slices/{slice_id}/brainstorm.md"
        gate: soft
        description: "Required when tier is appbuilder-standard or appbuilder-complex (the strict gate is enforced in STEP 1 because for appbuilder-simple this skill is the cluster entry point and brainstorm.md does not exist)."
    inputs_required:
      - id: feature_slug
        label: "Kebab-case feature slug; resolves to _concept/experience/features/<group>/<feature_slug>.md"
        type: text
        hint: "Must match the slug used by concept-slice. Regex ^[a-z][a-z0-9-]{1,47}$."
    inputs_optional:
      - id: slice_id_override
        label: "Override the auto-derived slice_id (rarely needed; default = feature_slug)"
        type: text
    reads:
      - path: "_concept/blueprint/datamodel/model.json"
        description: "Data model — surfaces entity-related grill questions."
      - path: "_concept/blueprint/techstack.md"
        description: "Stack constraints — informs the technical-constraints sub-section."
      - path: "_implementation/slices/{slice_id}/align.md"
        description: "Re-entry mode — refine an existing align."
    produces:
      - path: "_implementation/slices/{slice_id}/align.md"
        description: "Per-slice impl align handoff for impl-plan-plan-vertical."
      - path: "_concept/blueprint/glossary.md"
        description: "Ubiquitous-language glossary — terms pinned during the grill (inline capture; see contracts/domain_model.md)."
      - path: "_implementation/decisions.md"
        description: "Build-time ADRs — appended when a grill decision passes the 3-test gate (see contracts/domain_model.md)."
---

# Implementation Align — per-slice grill

## Overview

`impl-plan-align` is the implementation-readiness grill of the per-slice impl-loop.
It runs after `impl-plan-brainstorm` (when tier ∈ {appbuilder-standard, appbuilder-complex}) or as
the cluster entry point (when tier == appbuilder-simple). It does NOT run for tier == appbuilder-mvp.

The skill inverts brainstorm: now the AI asks pointed questions, the user defends.
Pillars covered: state transitions, boundary inputs, concurrency, permissions,
persistence/offline, error states, cross-feature data, performance, test seam.

The output is `_implementation/slices/<slice_id>/align.md` — a structured handoff file consumed
by `impl-plan-plan-vertical`. The `_implementation/slices/<slice_id>/` dossier is durable:
`impl-slice-commit` freezes it after the slice's atomic commit lands — writes `index.md`, keeps
the phase handoffs as permanent documentation, removes only the transient `progress.yaml`.
No impl-plan skill deletes or freezes the dir itself.

**Per-slice scope** is enforced. Edge cases discovered in this grill belong to THIS
feature; cross-feature touch points are documented but not grilled in depth (their
features have their own slice align runs).

## When to Use

- An implementation slice's concept artifacts (feature.md + screens) are frozen and
  the user is ready to commit to acceptance criteria for the implementation.
- Tier is `appbuilder-simple`, `appbuilder-standard`, or `appbuilder-complex`.
- For standard/complex: `_implementation/slices/<id>/brainstorm.md` exists.

## When NOT to Use

- Tier is `appbuilder-mvp` — appbuilder-mvp skips align per SKILL_GRAPH § 6. Use `impl-plan-plan-vertical`.
- Concept artifacts are missing — refer the caller to `concept-slice/design-feature`.
- For standard/complex without brainstorm — refer the caller to `impl-plan-brainstorm`.

---

ROLE Per-slice implementation-readiness grill — adversarial interviewer that surfaces edge cases, technical constraints, and acceptance handoff for ONE feature's implementation.

READS
  _concept/_meta/scope.yaml                                       — required; tier
  _concept/experience/features/{group}/{feature_slug}.md        — required; permanent feature artifact
  _concept/experience/screens/{feature_slug}/*.md                 — required; permanent screen specs (≥ 1 file)
  _implementation/slices/{slice_id}/brainstorm.md                            — required IF tier ∈ {appbuilder-standard, appbuilder-complex};
                                                                    ENTRY POINT IF tier == appbuilder-simple
  ? _concept/blueprint/datamodel/model.json                       — optional; data model for entity grilling
  ? _concept/blueprint/techstack.md                               — optional; stack constraints
  ? _implementation/slices/{slice_id}/align.md                               — re-entry mode

WRITES
  _implementation/slices/{slice_id}/align.md                                 — handoff for impl-plan-plan-vertical
  _concept/blueprint/glossary.md                                  — inline: terms pinned during the grill (per domain_model.md)
  _implementation/decisions.md                                    — inline: ADRs when a grill decision passes the 3-test gate (per domain_model.md)

REFERENCES
  SKILL_GRAPH.md                                                  — § 5.2 per-slice impl loop, § 6 tier composition
  contracts/iron_laws.md                                          — § 7 (no artifact without prerequisites), § 9 (standalone questions)
  contracts/skill_grammar.md                                      — DSL keywords
  contracts/asset_frontmatter.md                                  — § Skill SKILL.md frontmatter schema
  contracts/domain_model.md                                       — glossary format, ADR format, the 3-test gate
  contracts/grill_bank.md                                         — grill question bank: tone + 9 pillars + EARS provenance
  contracts/slice_loop.md                                         — tier gates, slug rule, resume-or-fresh, handoff keys, freeze lifecycle
  contracts/phase_procedures.md                                   — shared handoff procedures (DO shared:*)
  docs/devlog/2A-scope-project.md                      — § Pinned scope.yaml schema
  docs/devlog/2B-concept-slice-cluster.md              — § Pinned permanent artifact paths

REQUIRES
  hard: _concept/_meta/scope.yaml                                 — tier context
  state: scope.yaml `tier` ∈ {appbuilder-simple, appbuilder-standard, appbuilder-complex}

# Constraints (placed early per skill_grammar.md § Authoring tip 4)

MUST  ask each grill question as its own standalone assistant message (iron_laws § 9)
MUST  refuse to run if _concept/_meta/scope.yaml is missing or tier == appbuilder-mvp (appbuilder-mvp skips align per SKILL_GRAPH § 6)
MUST  refuse to run if the feature.md at _concept/experience/features/<group>/<feature_slug>.md is missing (iron_laws § 7)
MUST  refuse to run if tier ∈ {appbuilder-standard, appbuilder-complex} and _implementation/slices/<slice_id>/brainstorm.md is missing
MUST  copy slice_id, feature_title, feature_path from brainstorm.md frontmatter when present; never re-derive
MUST  surface every P1 question to the user as a standalone message before writing align.md
MUST  copy EARS acceptance criteria from feature.md verbatim into "## Acceptance handoff"
MUST  set phase: align in the handoff frontmatter
MUST  produce at least one P1 or P2 question OR resolve every prior P1 with a "## Decisions made" entry — empty grills are not acceptable
MUST  capture domain vocabulary inline (STEP 5a): when the grill pins or sharpens a term, write it to _concept/blueprint/glossary.md per contracts/domain_model.md — term → definition + `_Avoid_` list, zero implementation detail
MUST  append an ADR to _implementation/decisions.md when a grill decision passes the 3-test gate (hard-to-reverse AND surprising AND a real trade-off); skip otherwise

NEVER  invent edge cases the user did not confirm — every "## Edge cases to handle" bullet must trace to a Q/A in "## Decisions made" or to a feature.md/screen line
NEVER  add implementation detail or general programming concepts to glossary.md (domain_model.md § Glossary format)
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
  IF tier == appbuilder-mvp
    - refuse: "[impl-plan-align] tier=appbuilder-mvp does not run align. Use impl-plan-plan-vertical."
  - Resolve feature_slug → feature_path:
    $ ls _concept/experience/features/*/<feature_slug>.md
    Refuse if zero or >1 matches.
  - slice_id := feature_slug (or slice_id_override if set).
  IF tier ∈ {appbuilder-standard, appbuilder-complex}
    - require _implementation/slices/<slice_id>/brainstorm.md to exist
    - if missing, refuse with:
      > "[impl-plan-align] tier=<tier> requires
      >  _implementation/slices/<slice_id>/brainstorm.md. Run impl-plan-brainstorm first."
    - copy slice_id, feature_title, feature_path from brainstorm.md frontmatter (verify match).
  ELSE  # tier == appbuilder-simple
    - brainstorm.md not required; this skill is the cluster entry.
    - $ mkdir -p _implementation/slices/<slice_id>/
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

STEP 4: Run the grill (one pillar per STANDALONE message)
  All 9 pillars (contracts/grill_bank.md § The 9 Pillars — use the "Good
  question" phrasing, adapt nouns to this feature):
    1. State transitions          6. Errors
    2. Boundary inputs            7. Cross-feature data
    3. Concurrency                8. Performance
    4. Permissions (role × action matrix, every cell)
    5. Persistence and offline    9. Test seam
  Send ONE question per message; wait for each answer (iron_laws § 9). Skip a
  pillar only when brainstorm.md already answered it — cite that answer in
  "## Decisions made" (grill_bank.md § Anti-patterns).

STEP 5: Surface P1 open questions
  - For each unanswered grill point that BLOCKS plan-vertical, send STANDALONE:
    > "P1 blocker: <question>. I need an answer before I can write align.md."
  - Wait for answer. Repeat until no P1 questions remain.

STEP 5a: Capture the domain model (inline, per contracts/domain_model.md)
  Apply contracts/domain_model.md the moment vocabulary/decisions crystallise:
  - TERM pinned → write/update _concept/blueprint/glossary.md (term, 1-2
    sentence definition, `_Avoid_:` list; lazy-create; zero implementation detail).
  - DECISION passing the 3-test gate → append ADR to _implementation/decisions.md
    (date + title + 1-3 sentences); failing the gate it stays in
    align.md's "## Decisions made".
  - Never invent a definition or decision the user did not confirm.

STEP 6: Finalize
  DO shared:draft_checkpoint_write     (contracts/phase_procedures.md)
    artifact_path: _implementation/slices/<slice_id>/align.md
    checkpoint_id: align_draft
  Frontmatter: impl-side keys (slice_loop.md § Handoff frontmatter — slice_id,
  feature_title, feature_path, phase, tier, created_at, last_updated),
  phase: align.
  Body sections (exact headers, in order):
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
    Criteria" copied VERBATIM (contracts/acceptance_criteria.md § EARS template;
    grill_bank.md § EARS provenance). ≥ 1 EARS line required.

EMIT  [impl-plan-align] completed slice_id=<id> tier=<tier> p1_count=<n> p2_count=<n>

CHECKLIST
  - [ ] _concept/_meta/scope.yaml read and tier validated (∈ {appbuilder-simple, appbuilder-standard, appbuilder-complex})
  - [ ] feature_slug resolved to a single _concept/experience/features/<group>/<feature_slug>.md
  - [ ] tier-dependent prerequisite check passed (brainstorm.md required for standard/complex)
  - [ ] _implementation/slices/<slice_id>/ directory exists
  - [ ] All 9 pillars grilled STANDALONE; each answered before next
  - [ ] All P1 blockers surfaced and answered before draft
  - [ ] All 7 body sections present; `## Constraints` has all 3 sub-sections
  - [ ] At least one P1/P2 question in `## Open questions` OR every prior P1 resolved in `## Decisions made`
  - [ ] EARS acceptance criteria copied verbatim into `## Acceptance handoff` (≥ 1 EARS line)
  - [ ] User approved the draft via CHECKPOINT before write
  - [ ] _implementation/slices/<slice_id>/align.md exists on disk and validator.py exits 0
