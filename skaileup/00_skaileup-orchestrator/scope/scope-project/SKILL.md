---
name: skaileup-scope-scope-project
description: "Use when the user starts a new project and no _concept/_meta/scope.yaml exists yet, or when re-scoping (--tier= override). First checks the project shape (CLI tool, concept-only package, or reverse-engineering an existing repo) then, for a normal app, sizes it to one of appbuilder-mvp / appbuilder-simple / appbuilder-standard / appbuilder-complex — routing to one of seven flows. Writes _concept/_meta/scope.yaml. First action in the skaileup pipeline; gates which flow runs next."
metadata:
  version: "1.2.0"
  tags:
    - scope
    - tier
    - orchestrator-entry
    - flow-selection
    - skaileup
  stage: alpha
  artifacts:
    consumes:
      - id: onboarding-profile
        gate: soft
      - id: onboarding-decisions
        gate: soft
    produces:
      - id: scope
  prerequisites:
    inputs_required:
      - id: project_description
        label: "One-sentence project description"
        type: text
        hint: "Plain English. Example: 'A team todo app with assignees and due-date reminders.'"
    inputs_optional:
      - id: shape
        label: "Project shape (skip to infer from the description)"
        type: select
        options: [app, cli, concept-only, reverse-engineer]
        default: app
        hint: "Stage-0 route. 'app' falls through to tier sizing; the others route to appbuilder-cli / skaileup-concept-only / skaileup-concept-reverse."
      - id: tier_override
        label: "Force a specific flow (skips interview)"
        type: select
        options: [appbuilder-mvp, appbuilder-simple, appbuilder-standard, appbuilder-complex, appbuilder-cli, skaileup-concept-only, skaileup-concept-reverse]
        default: null
        hint: "Equivalent to --tier=<name>. Bypasses the decision rule but records what the rule would have picked."
      - id: features_estimate
        label: "Estimated number of distinct user-facing features"
        type: number
        hint: "Skip if you'd rather be asked during the interview."
      - id: multi_user
        label: "Multiple user roles or shared/collaborative state?"
        type: boolean
      - id: persistence
        label: "Data persistence shape"
        type: select
        options: [trivial, structured, external]
      - id: integrations
        label: "External services (comma-separated)"
        type: text
    reads:
      - path: "_concept/_meta/scope.yaml"
        description: "Existing scope (re-scoping case). When present, current values are loaded as defaults."
    produces:
      - path: "_concept/_meta/scope.yaml"
        description: "Authoritative tier + reasoning + signals for this project. Read by every downstream tier flow."
---

# Scope Project — pick the tier, write _concept/_meta/scope.yaml

ROLE  Project scoper — interviews the user briefly, first classifies the
      project shape (Stage 0), then for a normal app applies the verbatim tier
      sizing rule (Stage 1), and writes _concept/_meta/scope.yaml. The
      pipeline's first action; downstream flows (the four sizing tiers plus the
      appbuilder-cli / skaileup-concept-only / skaileup-concept-reverse variants) depend on this output.

READS
  ? _concept/_meta/scope.yaml         — existing scope (re-scoping case only)
  ? _concept/_grounding/scope-project/input.json
                                      — pre-collected interview answers (optional)

WRITES
  _concept/_meta/scope.yaml           — shape, tier, reasoning, flow_to_run,
                                        signals, override, chosen_at, chosen_by

REFERENCES
  SKILL_GRAPH.md                              — § 3 tier behavior table
  contracts/iron_laws.md                      — § 9 questions are standalone
  skaileup/scope/scope-project/references/decision-rule.md
                                              — long-form rule examples

MUST   ask each interview question as its own standalone message (iron_laws § 9)
MUST   resolve shape (Stage 0) BEFORE sizing (Stage 1) — a non-app shape
       short-circuits the sizing rule to its variant flow
MUST   apply the decision rule verbatim — do not invent new branches
MUST   show the chosen flow + reasoning to the user before writing the YAML
MUST   set flow_to_run to "flow:<tier>" deterministically from the chosen route
MUST   record signals.* exactly as collected (no rounding, no normalization)
MUST   if --tier= or tier_override is provided, set override.applied=true and
       record what the rule would have picked in override.rule_would_have_picked
MUST   if _concept/_meta/scope.yaml already exists, load it, show diff to user,
       and require explicit approval before overwriting (iron_laws § 8)
MUST   write chosen_at as ISO-8601 UTC with a "Z" suffix
MUST   set chosen_by to "skaileup-scope-scope-project@<metadata.version>"
NEVER  write _concept/_meta/scope.yaml before the user approves the decision
NEVER  silently change tier on re-scoping — always surface diff
NEVER  bury interview questions inside a longer explanation message
NEVER  invent values for signals — if a signal is missing, ask for it

INPUT
  Read from: _concept/_grounding/scope-project/input.json (if present)
  If missing, ask the user:
  - project_description: One-sentence project description (required)
  - shape: Project shape (optional) [app | cli | concept-only | reverse-engineer] default: app
  - tier_override: Force a specific flow (optional) [appbuilder-mvp | appbuilder-simple | appbuilder-standard | appbuilder-complex | appbuilder-cli | skaileup-concept-only | skaileup-concept-reverse] default: <none>
  - features_estimate: Estimated number of distinct user-facing features (optional)
  - multi_user: Multiple user roles or shared state? (optional) [true | false]
  - persistence: Data persistence shape (optional) [trivial | structured | external]
  - integrations: External services, comma-separated (optional)

STEP 1: Detect re-scoping mode
  - $ test -f _concept/_meta/scope.yaml && echo "RE-SCOPE" || echo "FRESH"
  - IF re-scope: load existing values as defaults for the interview
  - IF fresh: collect project_description (required) before continuing
  - IF _concept/_grounding/scope-project/input.json exists: load it as
    pre-supplied answers and skip the matching interview questions in STEP 2

STEP 2: Collect signals (skip individual questions if pre-supplied via INPUT)
  Ask each as a STANDALONE message (iron_laws § 9 — never bundle questions):
  - SHAPE FIRST: "What kind of deliverable is this? (1) a normal application,
    (2) a command-line tool with no UI, (3) a concept/spec package only — no
    implementation, or (4) extracting a concept from an existing codebase?"
    → shape (app | cli | concept-only | reverse-engineer)
    If the answer is clearly inferable from project_description, you may infer
    it and confirm rather than ask. The sizing questions below are still asked
    (they inform reasoning and are recorded) regardless of shape.
  - "How many distinct user-facing features will this app have? Best estimate is fine."
    → features_estimate (integer)
  - "Will more than one user role share state, or is it single-user?"
    → multi_user (boolean)
  - "How is data persisted? trivial (no DB / local state), structured (one relational schema),
    or external (multi-product, enterprise integration, queue/bus)?"
    → persistence (enum)
  - "Any named external integrations? (comma-separated, or 'none')"
    → integrations (list[string])

STEP 3: Apply the decision rule (verbatim from references/decision-rule.md)

  STAGE 0 — shape check (runs first; a non-app shape short-circuits sizing):
    rule_route = (
      "skaileup-concept-reverse" if shape == "reverse-engineer"
      else "skaileup-concept-only"     if shape == "concept-only"
      else "appbuilder-cli"          if shape == "cli"
      else <STAGE 1 sizing>   # shape == "app"
    )

  STAGE 1 — tier sizing (only when shape == "app").
  Order matters — enterprise check sits ABOVE the multi-user/feature-count branch
  so that a multi-user enterprise app does not short-circuit to `appbuilder-standard`.

  rule_tier = (
    "appbuilder-mvp"          if features_estimate <= 1 and persistence == "trivial"
    else "appbuilder-simple"   if features_estimate <= 5 and not multi_user
    else "appbuilder-complex"  if persistence == "external" or len(integrations) >= 2
    else "appbuilder-standard" if features_estimate <= 20 or multi_user
    else "appbuilder-complex"  # explicit fall-through (large but unclassified)
  )

  rule_route is the variant flow (Stage 0) or rule_tier (Stage 1). Throughout
  the rest of this skill, "tier" denotes the resolved rule_route.

STEP 4: Resolve override
  - IF tier_override is set:
      chosen_tier = tier_override   # may be a sizing tier OR a variant flow
      override.applied = true
      override.requested_tier = tier_override
      override.rule_would_have_picked = rule_route
  - ELSE:
      chosen_tier = rule_route
      override.applied = false
      override.requested_tier = null
      override.rule_would_have_picked = null

  Set chosen_shape: "app" for a sizing tier, else the variant's shape
  (appbuilder-cli → "cli"; skaileup-concept-only → "concept-only"; skaileup-concept-reverse →
  "reverse-engineer"). Write it to the top-level `shape` field.

STEP 5: Compose reasoning (2-6 sentences)
  - State the shape (Stage 0) and, for an app, which sizing branch fired
    (or that override was applied)
  - Reference the relevant signals literally (numbers + booleans), don't paraphrase
  - If fall-through fired, say so explicitly
  - Length must be 30-800 characters after trimming (validator-enforced)

STEP 6: Show decision to user (CHECKPOINT)
  CHECKPOINT scope_decision
    Show:
      - shape + chosen_tier
      - flow_to_run = "flow:<chosen_tier>"
      - reasoning
      - signals (all four)
      - override block (if applied)
    > "Approve this flow, or reply with --tier=<name> to override."

STEP 7: Write _concept/_meta/scope.yaml
  - $ mkdir -p _concept/_meta
  - Write the YAML following the pinned schema (see OUTPUT below)
  - chosen_at = current UTC ISO-8601 with "Z" suffix
  - chosen_by = "skaileup-scope-scope-project@<metadata.version>"
  - IF re-scope: show unified diff vs prior file before write; require explicit "yes"
    (iron_laws § 8 — NO OVERWRITING WITHOUT APPROVAL)

STEP 8: Validate the written file
  - $ python3 skaileup/scope/scope-project/validator.py _concept/_meta/scope.yaml
  - On failure: report errors and STOP. Do not commit.

EMIT  [scope-project] decided shape=<chosen_shape> tier=<chosen_tier> rule_picked=<rule_route> override=<bool>

OUTPUT _concept/_meta/scope.yaml
  schema_version: "1.0"
  shape: <app|cli|concept-only|reverse-engineer>   # optional; defaults to app
  tier: <enum>                                     # sizing tier OR variant flow id
  flow_to_run: "flow:<tier>"
  reasoning: |
    <2-6 sentences>
  description: "<one-sentence project description>"
  signals:
    features_estimate: <int>
    multi_user: <bool>
    persistence: <trivial|structured|external>
    integrations: [<string>, ...]
  override:
    applied: <bool>
    requested_tier: <string|null>
    rule_would_have_picked: <enum|null>
  chosen_at: "<iso-8601 UTC Z>"
  chosen_by: "skaileup-scope-scope-project@1.2.0"

CHECKLIST
  - [ ] Interview questions sent as standalone messages
  - [ ] Shape resolved (Stage 0) before sizing (Stage 1)
  - [ ] Decision rule applied verbatim (no new branches invented)
  - [ ] Decision shown to user via CHECKPOINT before write
  - [ ] _concept/_meta/scope.yaml conforms to pinned schema (validator passes)
  - [ ] flow_to_run == "flow:" + tier
  - [ ] shape agrees with tier (app → sizing tier; variant → its routed flow)
  - [ ] If override applied, override.requested_tier == tier and rule_would_have_picked recorded
  - [ ] If re-scoping, diff was shown and user approved overwrite
  - [ ] EMIT line printed
