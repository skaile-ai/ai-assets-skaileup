---
name: impl-plan-plan-vertical
description: "Use when an implementation slice has its align.md (or, for appbuilder-mvp, its feature.md) ready and needs a vertical-decomposition plan. Reads _implementation/slices/<id>/align.md + concept artifacts. Writes _implementation/slices/<id>/plan.md containing one row per user-facing slice (UI + Logic + Data), testing strategy, and an anti-horizontal-nudge block. Resists the LLM default of horizontal layering. Triggers on: 'plan the slice', 'decompose into rows', 'write the per-slice implementation plan', 'plan-vertical for <feature>'."
metadata:
  version: "2.0.0"
  tags:
    - impl-plan
    - plan
    - vertical-slice
    - decomposition
    - testing-strategy
    - anti-horizontal
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
      - id: slice-impl-align
        gate: soft
      - id: slice-impl-brainstorm
        gate: soft
      - id: datamodel
        gate: soft
      - id: techstack
        gate: soft
    produces:
      - id: slice-impl-plan
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
        description: "Permanent screen specs (≥ 1 file)."
        min_entries: 1
      - path: "_implementation/slices/{slice_id}/align.md"
        gate: soft
        description: "Required when tier ∈ {appbuilder-simple, appbuilder-standard, appbuilder-complex}; STEP 1 enforces hard. For appbuilder-mvp this skill is the cluster entry point and align.md is not expected."
    inputs_required:
      - id: feature_slug
        label: "Kebab-case feature slug; resolves to _concept/experience/features/<group>/<feature_slug>.md"
        type: text
        hint: "Same slug used by concept-slice and impl-plan-align. Regex ^[a-z][a-z0-9-]{1,47}$."
    inputs_optional:
      - id: slice_id_override
        label: "Override the auto-derived slice_id (rarely needed; default = feature_slug)"
        type: text
      - id: task_granularity
        label: "Decomposition granularity: feature (one row per user-facing slice) or screen (one row per screen)"
        type: select
        options:
          - feature
          - screen
        default: feature
    reads:
      - path: "_implementation/slices/{slice_id}/brainstorm.md"
        description: "Optional context — referenced for 'why this row' notes."
      - path: "_concept/blueprint/datamodel/model.json"
        description: "Optional — entity dependency hints inform row order, NOT row shape."
      - path: "_concept/blueprint/techstack.md"
        description: "Optional — stack constraints for the Logic column."
      - path: "_implementation/slices/{slice_id}/plan.md"
        description: "Re-entry mode — refine an existing plan."
    produces:
      - path: "_implementation/slices/{slice_id}/plan.md"
        description: "Per-slice impl plan handoff for impl-slice/implement (Task 2D)."
---

# Plan-Vertical — per-slice vertical decomposition

## Overview

`impl-plan-plan-vertical` is final phase of per-slice impl-loop before
`impl-slice/implement` takes over. Decomposes ONE feature into small set of
**vertical rows** — each row crosses UI + Logic + Data, an end-to-end
user-facing slice buildable, testable, shippable before next row begins.

> **DO NOT build all UI first, then all logic, then all data.** This skill
> actively resists that pattern. The default LLM failure mode is horizontal
> layering ("scaffold every screen, wire every handler, run every migration"),
> which produces N half-finished slices and zero working ones.

Output is `_implementation/slices/<slice_id>/plan.md` — structured handoff
consumed by `impl-slice/implement`, `impl-slice/test`, `impl-slice/recap`. The
`_implementation/slices/<slice_id>/` dossier is durable: `impl-slice-commit`
freezes it after slice's atomic commit lands — writes `index.md`, keeps phase
handoffs, removes only transient `progress.yaml`.

## When to Use

- Implementation slice's `align.md` approved (tier ∈ {simple, standard, complex}).
- OR tier == appbuilder-mvp and feature.md ready (appbuilder-mvp's plan-vertical is cluster entry).
- User wants slice converted into actionable, vertically-decomposed plan.

## When NOT to Use

- Concept artifacts (feature.md + screens) missing — refer to `concept-slice/design-feature`.
- Tier ∈ {simple, standard, complex} without align.md — refer to `impl-plan-align`.
- Tier == standard/complex without brainstorm.md — refer to `impl-plan-brainstorm`.
- Project-wide implementation plans — out of scope. Skill is per-slice.

---

## Anti-horizontal nudge (placed early per skill_grammar.md § Authoring tip 4)

The following block is a CONSTRAINT, not commentary. It is also embedded
VERBATIM in the output `plan.md` under `## Anti-horizontal nudge`. The
validator pins the exact-string match.

```markdown
## Anti-horizontal nudge

> **DO NOT build all UI first, then all logic, then all data.**
>
> The default LLM failure mode for implementation planning is horizontal layering: "first scaffold every screen, then wire every handler, then run every migration." This produces N half-finished slices and zero working ones.
>
> Instead: pick ONE row from `## Vertical decomposition` and complete it end-to-end (UI renders → handler responds → data round-trips → test green) BEFORE starting the next row.
>
> If you find yourself thinking any of the following, **stop**:
> - "I'll come back and wire the data after I've built all the screens."
> - "Let me get the UI looking right across the whole feature first."
> - "I'll batch the migrations and run them at the end."
> - "I'll add tests once everything is hooked up."
>
> A row is **not done** until: UI renders real data, the handler is callable from the UI, the data layer persists round-trips, and the test for that row is green. Then — and only then — start the next row.
```

---

ROLE Per-slice plan writer that resists horizontal decomposition — produces a vertical-row table (UI + Logic + Data) with embedded testing strategy and anti-horizontal nudge.

READS
  _concept/_meta/scope.yaml                                       — required; tier
  _concept/experience/features/{group}/{feature_slug}.md        — required; permanent feature artifact
  _concept/experience/screens/{feature_slug}/*.md                 — required; permanent screen specs (≥ 1)
  _implementation/slices/{slice_id}/align.md                                 — required IF tier ∈ {appbuilder-simple, appbuilder-standard, appbuilder-complex};
                                                                    ENTRY POINT IF tier == appbuilder-mvp
  ? _implementation/slices/{slice_id}/brainstorm.md                          — optional; "why this row" context
  ? _concept/blueprint/datamodel/model.json                       — optional; entity dependency hints (row ORDER only)
  ? _concept/blueprint/techstack.md                               — optional; stack constraints for Logic column
  ? _implementation/slices/{slice_id}/plan.md                                — re-entry mode

WRITES
  _implementation/slices/{slice_id}/plan.md                                  — handoff for impl-slice/implement (Task 2D)

REFERENCES
  SKILL_GRAPH.md                                                  — § 5.2 per-slice impl loop, § 6 tier composition
  contracts/iron_laws.md                                          — § 7 (no artifact without prerequisites), § 9 (standalone questions)
  contracts/plans.md                                              — note: this is a per-slice plan, sibling of project-level PLANS.md
  contracts/skill_grammar.md                                      — DSL keywords
  contracts/asset_frontmatter.md                                  — § Skill SKILL.md frontmatter schema
  contracts/slice_loop.md                                         — tier gates, slug rule, resume-or-fresh, handoff keys, freeze lifecycle
  contracts/phase_procedures.md                                   — shared handoff procedures (DO shared:*)
  impl-plan/plan-vertical/references/anti-horizontal-rules.md     — long-form expansion of the nudge with worked counter-examples
  docs/devlog/2A-scope-project.md                      — § Pinned scope.yaml schema
  docs/devlog/2B-concept-slice-cluster.md              — § Pinned permanent artifact paths
  docs/devlog/2C-impl-plan-align-vertical.md           — § Pinned plan.md schema (this skill's output contract)

REQUIRES
  hard: _concept/_meta/scope.yaml                                 — tier context

# Constraints (placed early per skill_grammar.md § Authoring tip 4)

MUST  produce one row per user-facing slice; each row crosses UI + Logic + Data
MUST  refuse to write a plan whose rows have empty UI, Logic, or Data cells without an explicit user-confirmed reason logged in the row's notes
MUST  embed the verbatim anti-horizontal-nudge template in the output plan.md `## Anti-horizontal nudge` section (validator pins exact-string match)
MUST  ask any clarification question as its own standalone assistant message (iron_laws § 9)
MUST  refuse to run if _concept/_meta/scope.yaml is missing
MUST  refuse to run if tier ∈ {appbuilder-simple, appbuilder-standard, appbuilder-complex} and _implementation/slices/<slice_id>/align.md is missing (iron_laws § 7)
MUST  refuse to write the plan if feature.md is missing
MUST  copy EARS acceptance criteria from feature.md (or align.md "## Acceptance handoff") verbatim into "## Testing strategy ### Automated tests" — every EARS line maps to ≥ 1 test row
MUST  include the 5 required Definition of Done items verbatim (see schema below)
MUST  set phase: plan in the handoff frontmatter
MUST  write to _implementation/slices/<slice_id>/plan.md (per-slice scratch); never write to a project-wide path — the project-level PLANS.md is owned by a different skill

NEVER  produce a plan that batches all UI as one row, then all logic as another row, then all data as a third
NEVER  decompose by technical layer (frontend / backend / db) instead of by user-facing vertical
NEVER  defer testing strategy to a later phase — it goes in plan.md, this skill
NEVER  write more than one plan.md per slice (re-entry: load existing, show diff, ask before any change)
NEVER  invent rows the user did not confirm — every row should trace to an align.md edge case, an EARS line, or a screen file

INPUT
  Read from: _concept/_grounding/impl-plan-plan-vertical/input.json
  If missing, ask the user:
  - feature_slug: Kebab-case feature slug (required) default: <none>
  - slice_id_override: Override auto-derived slice id (optional) default: <feature_slug>
  - task_granularity: Decomposition granularity (optional) [feature | screen] default: feature

# ── Workflow ───────────────────────────────────────────────────────

STEP 1: Read scope and resolve tier-dependent gate
  - Open _concept/_meta/scope.yaml; abort with explicit error if missing.
  - Read scope.tier.
  - Resolve feature_slug → feature_path, set slice_id := feature_slug
    (or slice_id_override) per contracts/slice_loop.md § Slug rule.
  IF tier ∈ {appbuilder-simple, appbuilder-standard, appbuilder-complex}
    - require _implementation/slices/<slice_id>/align.md to exist
    - if missing, refuse with:
      > "[impl-plan-plan-vertical] tier=<tier> requires
      >  _implementation/slices/<slice_id>/align.md. Run impl-plan-align first."
    - copy slice_id, feature_title, feature_path from align.md frontmatter (verify match).
  ELSE  # tier == appbuilder-mvp
    - align.md not required; this skill is cluster entry.
    - $ mkdir -p _implementation/slices/<slice_id>/
    - read feature_title from feature.md frontmatter.

STEP 2: Read context
  - Read align.md (when present); cache "## Acceptance handoff" EARS lines, "## Edge cases to handle", "## Constraints".
  - Read feature.md (always); cache "## Acceptance Criteria" EARS lines (fallback if align.md absent).
  - $ ls _concept/experience/screens/<feature_slug>/*.md  → read each.
  - Read brainstorm.md, model.json, techstack.md if present ("why this row" context, Logic-column stack notes).

STEP 3: Identify user-facing slices (the rows)
  Inline MUST (anti-horizontal): each row crosses UI + Logic + Data. If you can't
  fill all three for a row, row isn't vertical — merge or split it.

  Heuristics by `task_granularity`:
    - feature (default): walk align.md "## Acceptance handoff" EARS lines AND
      screen files; group user-facing interactions sharing a single
      end-to-end seam into ONE row.
    - screen: one row per screen file.

  Resist making rows = layers. If a candidate row is "all UI for the
  feature" or "all migrations", it isn't decomposed — STOP, re-decompose
  by user-facing seam.

STEP 4: Fill UI / Logic / Data per row
  Inline MUST (anti-horizontal): each row crosses UI + Logic + Data; rows
  with empty cells require explicit user-confirmed reason in row's notes
  column (validator emits a warning).

  For each row:
    - UI: which screen(s)/component(s) render slice. Cite by file path
      (`screens/<feature_slug>/<file>.md` or component path).
    - Logic: which handler/middleware/service backs slice. Cite by
      symbol (`auth.signIn(email, pw)`, `comments.create()`, etc.).
    - Data: which entity/table/field row reads or writes. Cite by name.
    - Notes (optional column): justification for cells intentionally
      `-` (e.g. pure-UI polish row).

  Reference model.json for entity dependency hints — parents before children
  for ROW ORDER, never to override ROW SHAPE.

STEP 5: Derive testing strategy
  For each EARS line in align.md "## Acceptance handoff" (or feature.md
  "## Acceptance Criteria" for appbuilder-mvp) (format: contracts/acceptance_criteria.md
  § EARS template), assign at least one row to cover it AND
  at least one test in `### Automated tests`.

  Test tags: each automated-test bullet starts with `[unit]`, `[integration]`,
  or `[e2e]`. Tag by smallest reliable seam.

  Manual checks: bullet list of click-paths user runs before approving
  slice (smoke-test focus, not thorough QA).

  Exit criteria: bullets that, when ALL true, mean slice is "done" and
  ready for `impl-slice/recap`. MUST include literal line:
    "all rows in `## Vertical decomposition` complete end-to-end"

STEP 6: Finalize
  DO shared:draft_checkpoint_write     (contracts/phase_procedures.md)
    artifact_path: _implementation/slices/<slice_id>/plan.md
    checkpoint_id: plan_draft
  Frontmatter: impl-side keys (slice_loop.md § Handoff frontmatter — slice_id,
  feature_title, feature_path, phase, tier, created_at, last_updated), phase: plan.
  Body sections (exact headers, in order):
    ## Slice scope
    ## Vertical decomposition
    ## Testing strategy
    ### Manual checks
    ### Automated tests
    ### Exit criteria
    ## Anti-horizontal nudge
    ## Definition of done
    ## Open carry-overs

  - `## Slice scope`: exactly one line, ≤ 200 chars.
  - `## Vertical decomposition`: markdown table, header `| # | UI | Logic | Data |`, ≥ 1 data row.
  - `## Anti-horizontal nudge`: VERBATIM template (see "Anti-horizontal nudge"
    block at top of this SKILL.md). Validator pins exact-string match.
  - `## Definition of done`: 5 verbatim checkbox items:
    - [ ] All vertical rows complete end-to-end (UI + Logic + Data wired)
    - [ ] All tests in § "Automated tests" pass
    - [ ] All manual checks in § "Manual checks" verified by user
    - [ ] No row left half-implemented (no "UI built but data not wired", etc.)
    - [ ] `_concept/experience/features/<group>/<feature_slug>.md` § Acceptance Criteria all green
  - `## Open carry-overs`: P3/DEFERRED items pulled from align.md "## Open
    questions surfaced by the grill". `_(none)_` allowed.
  - Validator note: empty UI/Logic/Data cells produce WARNING (stderr), not
    failure; surface to user.

EMIT  [impl-plan-plan-vertical] completed slice_id=<id> tier=<tier> rows=<n> tests=<n>

CHECKLIST
  - [ ] _concept/_meta/scope.yaml read and tier validated
  - [ ] feature_slug resolved to a single _concept/experience/features/<group>/<feature_slug>.md
  - [ ] tier-dependent prerequisite check passed (align.md required for non-appbuilder-mvp tiers)
  - [ ] _implementation/slices/<slice_id>/ directory exists
  - [ ] All 6 top-level body sections present (Slice scope, Vertical decomposition, Testing strategy, Anti-horizontal nudge, Definition of done, Open carry-overs)
  - [ ] `## Vertical decomposition` table has header `| # | UI | Logic | Data |` and ≥ 1 data row
  - [ ] Every EARS line maps to ≥ 1 test in `### Automated tests`
  - [ ] Anti-horizontal nudge embedded VERBATIM (validator pins exact match)
  - [ ] 5 Definition of Done items present verbatim
  - [ ] User approved the draft via CHECKPOINT before write
  - [ ] _implementation/slices/<slice_id>/plan.md exists on disk and validator.py exits 0
