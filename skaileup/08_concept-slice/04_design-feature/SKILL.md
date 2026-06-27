---
name: concept-slice-design-feature
description: "Use when concept-slice-scope-feature has completed and you need to commit THIS feature's permanent _concept/ artifacts — the feature spec, all required screen specs, and the per-feature mockup-walkthrough stub. The only writer of permanent _concept/ artifacts in the concept-slice cluster. Freezes _concept/slices/<id>/ on success by writing index.md and keeping the dossier as documentation. Triggers on: 'design this feature', 'commit slice artifacts', 'design-feature'."
metadata:
  version: "1.0.0"
  tags:
    - concept-slice
    - design-feature
    - commit
    - permanent-artifact
    - feature-portion
    - walkthrough
  stage: alpha
  artifacts:
    requires:
      - id: scope
        gate: hard
      - id: slice-concept-scope
        gate: hard
      - id: slice-concept-align
        gate: hard
    consumes:
      - id: slice-concept-brainstorm
        gate: soft
      - id: brand-tokens
        gate: soft
      - id: datamodel
        gate: soft
      - id: features
        gate: soft
      - id: screens
        gate: soft
    produces:
      - id: features
      - id: screens
      - id: walkthrough
      - id: slice-concept-index
  prerequisites:
    files:
      - path: "_concept/_meta/scope.yaml"
        gate: hard
        description: "Tier context required."
      - path: "_concept/slices/{slice_id}/scope-feature.md"
        gate: hard
        description: "Predecessor handoff — produced by concept-slice-scope-feature."
      - path: "_concept/slices/{slice_id}/align.md"
        gate: hard
        description: "Acceptance criteria source — produced by concept-slice-align."
    inputs_required:
      - id: slice_id
        label: "Slice id (kebab-case)"
        type: text
    inputs_optional:
      - id: feature_group
        label: "Feature group (sub-dir under experience/features/)"
        type: text
        hint: "Defaults to the feature_slug if not provided."
    reads:
      - path: "_concept/slices/{slice_id}/brainstorm.md"
        description: "Optional — used for agent_notes summary."
      - path: "_concept/discovery/brand/tokens.json"
        description: "Optional — referenced in screens."
      - path: "_concept/blueprint/datamodel/model.json"
        description: "Optional — used to fill data_entities."
      - path: "_concept/experience/features"
        description: "Sibling features — required for cross-feature collision check."
      - path: "_concept/experience/screens"
        description: "Sibling screens — required for cross-feature collision check."
    produces:
      - path: "_concept/experience/features/{feature_group}/{feature_slug}.md"
        description: "Per-feature spec, conformant to contracts/frontmatter.md § experience/features."
      - path: "_concept/experience/screens/{feature_slug}/{screen_slug}.md"
        description: "One screen file per entry in scope-feature.md `## Required screens`."
      - path: "_concept/mockup-walkthrough/{tier}/{feature_slug}.{ext}"
        description: "Walkthrough source stub (ext per tier: appbuilder-simple=.html, appbuilder-standard=.astro, appbuilder-complex=.html with framework-pending flag)."
      - path: "_concept/slices/{slice_id}/index.md"
        description: "Frozen slice dossier — links to the feature/screens/walkthrough artifacts; keeps the slice folder as documentation."
---

# Concept-Slice Design-Feature

## Overview

`concept-slice-design-feature` is the COMMIT phase of the concept-slice cluster.
It is the only skill in the cluster that writes permanent `_concept/`
artifacts and the only one that freezes the slice dossier.

**Three permanent writes:**

1. `_concept/experience/features/<group>/<feature_slug>.md` — the feature spec,
   conformant to `contracts/frontmatter.md` § "experience/features/...".
2. `_concept/experience/screens/<feature_slug>/<screen_slug>.md` — one file per
   entry in scope-feature.md's `## Required screens`. The first segment of
   each path is `<feature_slug>` (this is the path-segment rule).
3. `_concept/mockup-walkthrough/<tier>/<feature_slug>.<ext>` — one walkthrough
   source stub. Extension depends on tier:
   - `appbuilder-simple` → `.html`
   - `appbuilder-standard` → `.astro`
   - `appbuilder-complex` → `.html` (framework variant pending; flagged via EMIT)

**One freeze:** after every write succeeds AND the user has approved, this skill
writes `_concept/slices/<slice_id>/index.md` and **keeps** the slice folder. The
phase handoffs (`brainstorm.md`, `align.md`, `scope-feature.md`) stay as the
feature's permanent decision record; `index.md` links forward to the canonical
artifacts above. Nothing is deleted. (This is the Suggestion-B convention: slices
are durable per-feature documentation, not throwaway scratch.)

**The path-segment rule** is the cluster's hardest invariant. See
`concept-slice/design-feature/references/feature-portion-rule.md`.

---

ROLE Per-feature commit — turns scope-feature.md + align.md into permanent _concept/ artifacts (feature spec + screens + walkthrough stub) and freezes the slice dossier with an index.md.

READS
  _concept/_meta/scope.yaml                          — required; tier (drives walkthrough sub-dir)
  _concept/slices/{slice_id}/scope-feature.md         — required; predecessor handoff
  _concept/slices/{slice_id}/align.md                 — required; acceptance criteria source
  ? _concept/slices/{slice_id}/brainstorm.md          — optional; for agent_notes
  ? _concept/discovery/brand/tokens.json             — optional; referenced in screens
  ? _concept/blueprint/datamodel/model.json          — optional; data_entities
  ? _concept/experience/features/**/*.md             — REQUIRED for cross-feature collision check
  ? _concept/experience/screens/**/*.md              — REQUIRED for cross-feature collision check

WRITES
  _concept/experience/features/{feature_group}/{feature_slug}.md
  _concept/experience/screens/{feature_slug}/{screen_slug}.md   (1..N — one per required screen)
  _concept/mockup-walkthrough/{tier}/{feature_slug}.{ext}
  _concept/slices/{slice_id}/index.md                 — frozen dossier; written only on success

FREEZES
  _concept/slices/{slice_id}/                         — kept as documentation; index.md added, handoffs retained, nothing deleted

REFERENCES
  SKILL_GRAPH.md                                     — § 4 concept-slice loop
  docs/devlog/mockup-design.md                                 — § 4 walkthrough tiers, § 9 tier composition
  contracts/iron_laws.md                             — § 7, § 8, § 9
  contracts/frontmatter.md                           — experience/features, experience/screens schemas
  concept-slice/design-feature/references/feature-portion-rule.md — path-segment rule with examples

REQUIRES
  hard: _concept/_meta/scope.yaml
  hard: _concept/slices/{slice_id}/scope-feature.md
  hard: _concept/slices/{slice_id}/align.md
  state: scope.yaml `tier` ∈ {appbuilder-simple, appbuilder-standard, appbuilder-complex}

# Constraints (placed early per skill_grammar.md § Authoring tip 4)

MUST  read scope.yaml AND scope-feature.md AND align.md before any write (iron_laws § 7)
MUST  apply the path-segment rule (see references/feature-portion-rule.md) to every proposed write
MUST  show a unified diff and require explicit yes/no/edit on every existing-file overwrite (iron_laws § 8)
MUST  copy acceptance criteria from align.md verbatim into feature.md (no paraphrasing)
MUST  pick mockup-walkthrough extension from tier per the table in this file (appbuilder-simple=html, appbuilder-standard=astro, appbuilder-complex=html+flag)
MUST  write _concept/slices/<slice_id>/index.md ONLY after every permanent write succeeds AND user has approved
MUST  keep the slice folder and its phase handoffs (brainstorm/align/scope-feature) — they are permanent documentation
MUST  send each overwrite-approval question as its own STANDALONE message (iron_laws § 9)
MUST  refuse to run if scope.yaml `tier` == appbuilder-mvp

NEVER  modify any path whose segment does not match <feature_slug>
NEVER  delete _concept/slices/<slice_id>/ or any of its phase handoffs (freeze, never delete)
NEVER  write index.md if any write was skipped, refused, or failed
NEVER  invent screens not listed in scope-feature.md `## Required screens`
NEVER  invent acceptance criteria not present in align.md
NEVER  modify another feature's files even if they appear stale or wrong

INPUT
  Read from: _concept/_grounding/concept-slice-design-feature/input.json
  If missing, ask the user:
  - slice_id: Slice id (required) default: <none>
  - feature_group: Feature group (optional) default: <feature_slug>

# ── Workflow ───────────────────────────────────────────────────────

STEP 0: Read all three handoffs + scope.yaml
  - Open _concept/_meta/scope.yaml; abort with explicit error if missing.
    Refuse if tier == appbuilder-mvp.
  - Open _concept/slices/<slice_id>/scope-feature.md; abort if missing.
  - Open _concept/slices/<slice_id>/align.md; abort if missing.
  - Open _concept/slices/<slice_id>/brainstorm.md if present; cache for
    agent_notes summary.
  - Cache: tier, feature_slug (= slice_id), feature_title, required_screens,
    required_entities, in_scope_acceptance_criteria.

STEP 1: Cross-feature collision check
  - Scan _concept/experience/features/**/*.md
    for any path containing /<feature_slug>.md or /<feature_slug>/ that
    belongs to a *different* slice.
  - Scan _concept/experience/screens/**/*.md for the same.
  - IF a collision is detected (another feature owns the same slug):
    - EMIT [concept-slice-design-feature] warning collision feature_slug=<slug> existing=<path>
    - Send STANDALONE:
      > "Feature slug `<slug>` already exists at `<path>` from a different
      >  slice. Disambiguate before continuing — rename this slice's
      >  feature_title or confirm intentional refinement of the existing
      >  one."
    - Wait for user direction; do NOT proceed silently.

STEP 2: Compose feature.md content (in memory)
  Path: _concept/experience/features/<feature_group>/<feature_slug>.md
  Frontmatter (per contracts/frontmatter.md § experience/features):
    ```
    ---
    priority: must-have
    roles: [...]                      # from scope-feature.md inferred or asked
    permissions:                      # copy table from align.md
      <role>: [<actions>]
    story_refs: []
    agent_notes: |
      <one-paragraph summary; reuse brainstorm.md if present>
    screens: []                       # filled at end of STEP 4
    data_entities: []                 # = scope-feature.md `## Required entities`
    last_updated: YYYY-MM-DD
    ---
    ```
  Body:
    ```
    # <feature_title>

    ## Acceptance Criteria
    <verbatim copy of scope-feature.md `## Acceptance criteria (final)` bullets>

    ## Notes
    <any agent notes from brainstorm or align worth preserving>
    ```

STEP 3: Pre-write check for feature.md
  - Apply path-segment rule: filename stem MUST equal <feature_slug>.
  - Stat the target path:
    IF it does NOT exist
      - Mark as "create".
    ELSE
      - Read existing content; compute unified diff against proposed.
      - CHECKPOINT overwrite_feature_md (STANDALONE)
        > "_concept/experience/features/<group>/<feature_slug>.md
        >  already exists. Diff:
        >  <diff>
        >  Approve overwrite? (yes / no / edit)"
      - On `no`: STOP entire skill, do NOT delete scratch.
      - On `edit`: prompt for changes, regenerate, repeat from start of STEP 3.
      - On `yes`: mark as "overwrite".

STEP 4: Compose each screen file (in memory)
  For each `<group>/<screen>` in scope-feature.md `## Required screens`:
    - Target path: _concept/experience/screens/<feature_slug>/<screen>.md
      (the FIRST segment under screens/ MUST be <feature_slug>; if
      `<group>` differs from <feature_slug> in scope-feature.md, use
      <feature_slug> for the screen dir per path-segment rule.)
    - Frontmatter (per contracts/frontmatter.md § experience/screens):
      ```
      ---
      implements:
        - _concept/experience/features/<feature_group>/<feature_slug>.md
      data_entities: [<from scope-feature.md required entities>]
      # Omit `layout` when _concept/experience/screens/00_layout/shell.md
      # does not yet exist (per plan Open Question § 4 resolution).
      last_updated: YYYY-MM-DD
      ---
      ```
    - Body: a short stub naming the screen and its purpose. Detailed
      composition is the job of `experience-screens` later — this skill
      writes only the slot.
  - After all screen paths are known, set `screens:` in feature.md frontmatter
    to the list of relative paths.

STEP 5: Pre-write check for each screen file
  - Apply path-segment rule: first dir under screens/ MUST equal <feature_slug>.
  - Stat each target; for any that exists, run a STANDALONE overwrite
    CHECKPOINT (one per file) with the diff.
  - On `no` for any screen: STOP, do NOT delete scratch.

STEP 6: Compose mockup-walkthrough stub
  - Determine extension from tier:
    | tier         | extension | note                                       |
    |--------------|-----------|--------------------------------------------|
    | appbuilder-simple   | html      | static placeholder                         |
    | appbuilder-standard | astro     | Astro page placeholder                     |
    | appbuilder-complex  | html      | with HTML comment "framework variant pending" |
  - Path: _concept/mockup-walkthrough/<tier>/<feature_slug>.<ext>
  - Body: a placeholder noting the feature_title, the list of required
    screens, and (for appbuilder-complex) a flag comment.
  - For tier == appbuilder-complex, additionally:
    EMIT [concept-slice-design-feature] warning appbuilder-complex-stub feature_slug=<slug>

STEP 7: Pre-write check for walkthrough stub
  - Apply path-segment rule: filename stem MUST equal <feature_slug>.
  - Stat; on existence, STANDALONE overwrite CHECKPOINT with diff.

STEP 8: Final approval — show full plan
  CHECKPOINT design_feature_plan
    > "Plan summary:
    >    create / overwrite: <feature.md path>
    >    create / overwrite: <screen.md paths (1..N)>
    >    create / overwrite: <walkthrough stub path>
    >    freeze (write index.md, keep folder): _concept/slices/<slice_id>/
    >  Approve to execute, or tell me what to change."

STEP 9: Execute writes in order
  - Write feature.md
  - Write each screen file
  - Write walkthrough stub
  - On any write failure: STOP, do NOT write index.md, surface error.

STEP 10: Verify all writes
  - Re-read each file; assert frontmatter parses.
  - If any verification fails: STOP, do NOT write index.md.

STEP 11: Freeze the slice — write _concept/slices/<slice_id>/index.md
  Do NOT delete anything. Keep brainstorm.md, align.md, scope-feature.md in place.
  Write index.md with this shape:
    ```
    ---
    slice_id: <slice_id>
    feature_title: <feature_title>
    phase: frozen
    tier: <tier>
    status: complete
    last_updated: YYYY-MM-DD
    ---

    # Slice: <feature_title>

    Frozen concept dossier. The phase handoffs below are the decision record;
    the canonical artifacts are the truth.

    ## Canonical artifacts
    - Feature spec: _concept/experience/features/<feature_group>/<feature_slug>.md
    - Screens:
      - _concept/experience/screens/<feature_slug>/<screen_slug>.md   (1..N)
    - Walkthrough: _concept/mockup-walkthrough/<tier>/<feature_slug>.<ext>

    ## Process history (kept)
    - brainstorm.md — feature framing + open questions
    - align.md — acceptance criteria, edge cases, permissions
    - scope-feature.md — in/out scope before design
    ```
  - Verify index.md exists and its frontmatter parses.

STEP 12: EMIT
  EMIT [concept-slice-design-feature] completed slice_id=<id> feature=<slug> tier=<tier> screens=<n> frozen=_concept/slices/<id>/

CHECKLIST
  - [ ] scope.yaml read; tier ∈ {appbuilder-simple, appbuilder-standard, appbuilder-complex}
  - [ ] All three handoffs (scope-feature.md, align.md, scope.yaml) read; brainstorm.md cached if present
  - [ ] Cross-feature collision check passed (or user disambiguated)
  - [ ] Path-segment rule applied to every proposed write
  - [ ] Acceptance criteria copied verbatim from scope-feature.md (which echoes align.md IN-scope subset)
  - [ ] Required-screen count matches actual screen files written
  - [ ] Walkthrough extension matches tier
  - [ ] All overwrites approved via STANDALONE CHECKPOINT
  - [ ] All writes succeeded and verified
  - [ ] _concept/slices/<slice_id>/index.md written; phase handoffs kept (nothing deleted)
