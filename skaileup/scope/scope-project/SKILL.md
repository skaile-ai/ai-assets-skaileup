---
name: skaileup-scope-scope-project
description: "Use when the user starts a new project and no _concept/_meta/scope.yaml exists yet, or when re-scoping (--tier= override). Picks one of mvp / simple-app / standard-app / complex-app from a one-sentence project description and writes _concept/_meta/scope.yaml. First action in the skaileup pipeline; gates which flow runs next."
metadata:
  version: "1.1.0"
  tags:
    - scope
    - tier
    - orchestrator-entry
    - flow-selection
    - skaileup
  stage: alpha
  prerequisites:
    inputs_required:
      - id: project_description
        label: "One-sentence project description"
        type: text
        hint: "Plain English. Example: 'A team todo app with assignees and due-date reminders.'"
    inputs_optional:
      - id: tier_override
        label: "Force a specific tier (skips interview)"
        type: select
        options: [mvp, simple-app, standard-app, complex-app]
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

ROLE  Project-size scoper — interviews the user briefly, applies the verbatim
      tier decision rule, and writes _concept/_meta/scope.yaml. The pipeline's
      first action; downstream flows (mvp/simple-app/standard-app/complex-app)
      depend on this output.

READS
  ? _concept/_meta/scope.yaml         — existing scope (re-scoping case only)
  ? _concept/_grounding/scope-project/input.json
                                      — pre-collected interview answers (optional)

WRITES
  _concept/_meta/scope.yaml           — tier, reasoning, flow_to_run, signals,
                                        override, chosen_at, chosen_by

REFERENCES
  SKILL_GRAPH.md                              — § 3 tier behavior table
  contracts/iron_laws.md                      — § 9 questions are standalone
  skaileup/scope/scope-project/references/decision-rule.md
                                              — long-form rule examples

MUST   ask each interview question as its own standalone message (iron_laws § 9)
MUST   apply the decision rule verbatim — do not invent new branches
MUST   show the chosen tier + reasoning to the user before writing the YAML
MUST   set flow_to_run to "flow:<tier>" deterministically from the chosen tier
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
  - tier_override: Force a specific tier (optional) [mvp | simple-app | standard-app | complex-app] default: <none>
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
  - "How many distinct user-facing features will this app have? Best estimate is fine."
    → features_estimate (integer)
  - "Will more than one user role share state, or is it single-user?"
    → multi_user (boolean)
  - "How is data persisted? trivial (no DB / local state), structured (one relational schema),
    or external (multi-product, enterprise integration, queue/bus)?"
    → persistence (enum)
  - "Any named external integrations? (comma-separated, or 'none')"
    → integrations (list[string])

STEP 3: Apply the decision rule (verbatim from SKILL_GRAPH.md § 3)
  Order matters — enterprise check sits ABOVE the multi-user/feature-count branch
  so that a multi-user enterprise app does not short-circuit to `standard-app`.

  rule_tier = (
    "mvp"          if features_estimate <= 1 and persistence == "trivial"
    else "simple-app"   if features_estimate <= 5 and not multi_user
    else "complex-app"  if persistence == "external" or len(integrations) >= 2
    else "standard-app" if features_estimate <= 20 or multi_user
    else "complex-app"  # explicit fall-through (large but unclassified)
  )

STEP 4: Resolve override
  - IF tier_override is set:
      chosen_tier = tier_override
      override.applied = true
      override.requested_tier = tier_override
      override.rule_would_have_picked = rule_tier
  - ELSE:
      chosen_tier = rule_tier
      override.applied = false
      override.requested_tier = null
      override.rule_would_have_picked = null

STEP 5: Compose reasoning (2-6 sentences)
  - State which decision-rule branch fired (or that override was applied)
  - Reference the relevant signals literally (numbers + booleans), don't paraphrase
  - If fall-through fired, say so explicitly
  - Length must be 30-800 characters after trimming (validator-enforced)

STEP 6: Show decision to user (CHECKPOINT)
  CHECKPOINT scope_decision
    Show:
      - chosen_tier
      - flow_to_run = "flow:<chosen_tier>"
      - reasoning
      - signals (all four)
      - override block (if applied)
    > "Approve this tier, or reply with --tier=<name> to override."

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

EMIT  [scope-project] decided tier=<chosen_tier> rule_picked=<rule_tier> override=<bool>

OUTPUT _concept/_meta/scope.yaml
  schema_version: "1.0"
  tier: <enum>
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
  chosen_by: "skaileup-scope-scope-project@1.1.0"

CHECKLIST
  - [ ] Interview questions sent as standalone messages
  - [ ] Decision rule applied verbatim (no new branches invented)
  - [ ] Decision shown to user via CHECKPOINT before write
  - [ ] _concept/_meta/scope.yaml conforms to pinned schema (validator passes)
  - [ ] flow_to_run == "flow:" + tier
  - [ ] If override applied, override.requested_tier == tier and rule_would_have_picked recorded
  - [ ] If re-scoping, diff was shown and user approved overwrite
  - [ ] EMIT line printed
