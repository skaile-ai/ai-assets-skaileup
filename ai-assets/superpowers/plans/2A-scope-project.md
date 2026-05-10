# Task 2A — `scope-project` Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author the `scope-project` skill that, given a one-sentence project description, picks a tier (`mvp` / `simple-app` / `standard-app` / `complex-app`) and writes a deterministic `_concept/_meta/scope.yaml` that all downstream Phase 2 skills (2B/2C/2D/2H) read as their tier-context contract.

**Architecture:**
- The skill is the orchestrator's first action. It collects (or accepts via `--tier=`) a one-sentence description, asks at most three short interview questions, applies a verbatim decision rule (copied from `SKILL_GRAPH.md` § 3), shows the decision to the user for approval, then writes a fixed-schema YAML to `_concept/_meta/scope.yaml`.
- A small Python validator (`validator.py`) checks the YAML's schema, allowed enum values, and presence of required fields, plus a snapshot harness exercises four canned descriptions (one per tier) to guard determinism.
- No skill dependencies — this skill is the root of the dependency graph.

**Tech Stack:**
- Skill DSL per `contracts/skill_grammar.md` and frontmatter per `contracts/asset_frontmatter.md`
- YAML output (UTF-8, LF line endings)
- Python 3.12+ for `validator.py` (PyYAML, stdlib only otherwise)

---

## Pre-flight

Before any step, confirm baseline state.

- [ ] **Pre-1: Confirm cwd**

Run: `pwd`
Expected: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`

- [ ] **Pre-2: Confirm branch / git state**

Run: `git status -sb`
Expected: clean tree (or only the in-progress migration branch's untracked plan docs). If dirty in unrelated files, stop and clarify with the user.

- [ ] **Pre-3: Confirm target dir exists and is empty**

Run: `ls -la skaileup/scope/scope-project/`
Expected: empty directory (Phase 1 scaffolded an empty dir, no `.placeholder` left). If files exist, read each before deciding whether to overwrite.

- [ ] **Pre-4: Confirm source documents are readable**

Run: `wc -l SKILL_GRAPH.md contracts/iron_laws.md contracts/skill_grammar.md contracts/asset_frontmatter.md CONTRIBUTING.md skaileup/skills/skaileup/SKILL.md`
Expected: line counts non-zero for all six files.

- [ ] **Pre-5: Confirm naming convention**

Per `CONTRIBUTING.md` and the parent plan (line 87), the skill `name:` MUST be `skaileup-scope-scope-project` (no shortening). The skill directory is `skaileup/scope/scope-project/`. Both must agree.

---

## Source-of-Truth Anchors (read before authoring)

The executing agent MUST read each of these once, in this order, before starting Task 1:

1. `SKILL_GRAPH.md` — full file, but especially:
   - § 3 "Tier behavior" — the verbatim decision rule (copied below into this plan)
   - § 6 "Flows × Bundles" — confirms each tier maps to a flow file `flows/<tier>.flow.yaml`
2. `contracts/iron_laws.md` — § "9. QUESTIONS ARE STANDALONE MESSAGES" applies (this skill asks questions)
3. `contracts/asset_frontmatter.md` — § "Skill — SKILL.md" frontmatter schema, especially `metadata.prerequisites`
4. `contracts/skill_grammar.md` — DSL keywords (`ROLE`, `READS`, `WRITES`, `INPUT`, `STEP`, `CHECKPOINT`, `OUTPUT`, `MUST`, `NEVER`, `CHECKLIST`)
5. `CONTRIBUTING.md` — naming, frontmatter integrity checklist
6. `skaileup/skills/skaileup/SKILL.md` — the base orchestrator that calls `scope-project` first

---

## Pinned Schema — `_concept/_meta/scope.yaml`

This schema is the contract for downstream tasks 2B / 2C / 2D / 2H. It MUST NOT change without coordinated updates to those mini-plans.

```yaml
# _concept/_meta/scope.yaml — written by skaileup-scope-scope-project
schema_version: "1.0"           # string; bump on breaking schema changes
tier: <enum>                    # one of: mvp | simple-app | standard-app | complex-app
flow_to_run: <string>           # canonical flow id; one of:
                                #   flow:mvp | flow:simple-app | flow:standard-app | flow:complex-app
reasoning: |                    # multi-line block; 2-6 sentences
  Plain-language explanation of why this tier was chosen.
  Should reference the decision-rule branch that fired.

description: <string>           # the one-sentence project description provided by the user
signals:                        # the inputs the rule consumed; recorded for re-scoping audit
  features_estimate: <integer>  # estimated count of distinct user-facing features
  multi_user: <boolean>         # true if app has more than one user role / multi-tenant / collaborative
  persistence: <enum>           # one of: trivial | structured | external
                                #   trivial    = local state / single JSON file / no DB
                                #   structured = single relational schema, single product
                                #   external   = multi-product, enterprise integration, queue/bus
  integrations: <list[string]>  # named external systems (e.g. ["stripe","sendgrid"]); [] if none

override:                       # populated when user passed --tier=
  applied: <boolean>
  requested_tier: <string|null> # null if no override
  rule_would_have_picked: <enum|null>   # what the decision rule would have returned

chosen_at: <iso-8601 timestamp>  # UTC, e.g. 2026-05-07T12:34:56Z
chosen_by: <string>              # "skaileup-scope-scope-project@<version>"
```

**Field rules (validator-enforced):**

- `tier` is REQUIRED and MUST be one of the four enum values.
- `flow_to_run` is REQUIRED and MUST be `flow:<tier>` (i.e. derived deterministically from `tier`).
- `reasoning` is REQUIRED, non-empty, length 30–800 chars after trimming.
- `description` is REQUIRED, non-empty, single line in the source (multi-line allowed but discouraged).
- `signals` is REQUIRED, all four sub-fields present.
- `override.applied` is REQUIRED. If `applied: true`, `requested_tier` MUST equal `tier`.
- `chosen_at` MUST parse as ISO-8601 UTC (suffix `Z`).

---

## Pinned Decision Rule (verbatim from SKILL_GRAPH.md § 3, lines 153–158)

```
if features ≤ 1 and persistence trivial:        → mvp
elif features ≤ 5 and single-user:              → simple-app
elif features ≤ 20 or multi-user:               → standard-app
elif multi-product or enterprise integration:   → complex-app
```

**Authoritative interpretation locked in for this skill:**

- `features` ↔ `signals.features_estimate`
- `persistence trivial` ↔ `signals.persistence == "trivial"`
- `single-user` ↔ `signals.multi_user == false`
- `multi-user` ↔ `signals.multi_user == true`
- `multi-product or enterprise integration` ↔ `signals.persistence == "external"` OR `len(signals.integrations) >= 2`

**Tie-break / fall-through:** if none of the four branches match (e.g. `features = 30, multi_user = false, persistence = structured, integrations = []`), the rule falls through to `complex-app`. Document this explicitly in the `reasoning` field.

User can override via `--tier=<name>` at any time (per § 3 line 160 of SKILL_GRAPH.md).

---

## File Targets

All paths absolute, inside the repo at `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`.

- **Create:** `skaileup/scope/scope-project/SKILL.md`
- **Create:** `skaileup/scope/scope-project/validator.py`
- **Create:** `skaileup/scope/scope-project/references/decision-rule.md`
  - Long-form expansion of the rule with examples; SKILL.md body links to it.
- **Create:** `skaileup/scope/scope-project/examples/mvp.scope.yaml`
- **Create:** `skaileup/scope/scope-project/examples/simple-app.scope.yaml`
- **Create:** `skaileup/scope/scope-project/examples/standard-app.scope.yaml`
- **Create:** `skaileup/scope/scope-project/examples/complex-app.scope.yaml`
- **Create:** `skaileup/scope/scope-project/examples/fixtures.json`
  - Four canned `{description, expected_tier, signals}` triples, one per tier.
- **Create:** `skaileup/scope/scope-project/tests/test_validator.py`
  - pytest cases that exercise the validator against the four example YAMLs and a few negatives.

No edits to any existing files in this task. (The base orchestrator `skaileup/skills/skaileup/SKILL.md` is updated in a later task — do not touch it here.)

---

## Task 1: Author `SKILL.md` frontmatter

**Files:**
- Create: `skaileup/scope/scope-project/SKILL.md`

- [ ] **Step 1: Write frontmatter (only — body comes in Task 2)**

Use this frontmatter exactly. Bump `metadata.version` only if a later iteration in the same task forces a breaking change (no precedent here — start at `1.0.0`).

```yaml
---
name: skaileup-scope-scope-project
description: "Use when the user starts a new project and no _concept/_meta/scope.yaml exists yet, or when re-scoping (--tier= override). Picks one of mvp / simple-app / standard-app / complex-app from a one-sentence project description and writes _concept/_meta/scope.yaml. First action in the skaileup pipeline; gates which flow runs next."
metadata:
  version: "1.0.0"
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
```

- [ ] **Step 2: Verify frontmatter parses as YAML**

Run: `python3 -c "import yaml,sys; yaml.safe_load(open('skaileup/scope/scope-project/SKILL.md').read().split('---')[1])"`
Expected: no output, exit 0.

- [ ] **Step 3: Verify name matches directory**

Run: `python3 -c "import yaml; print(yaml.safe_load(open('skaileup/scope/scope-project/SKILL.md').read().split('---')[1])['name'])"`
Expected: `skaileup-scope-scope-project`

- [ ] **Step 4: Commit (frontmatter only)**

```bash
git add skaileup/scope/scope-project/SKILL.md
git commit -m "feat(scope): add scope-project SKILL.md frontmatter (Task 2A step 1)"
```

---

## Task 2: Author `SKILL.md` body (DSL)

**Files:**
- Modify: `skaileup/scope/scope-project/SKILL.md` (append after frontmatter)

- [ ] **Step 1: Add ROLE / READS / WRITES / REFERENCES blocks**

Append below the frontmatter:

```
# Scope Project — pick the tier, write _concept/_meta/scope.yaml

ROLE  Project-size scoper — interviews the user briefly, applies the verbatim
      tier decision rule, and writes _concept/_meta/scope.yaml. The pipeline's
      first action; downstream flows (mvp/simple-app/standard-app/complex-app)
      depend on this output.

READS
  ? _concept/_meta/scope.yaml         — existing scope (re-scoping case only)

WRITES
  _concept/_meta/scope.yaml           — tier, reasoning, flow_to_run, signals,
                                        override, chosen_at, chosen_by

REFERENCES
  SKILL_GRAPH.md                              — § 3 tier behavior table
  contracts/iron_laws.md                      — § 9 questions are standalone
  skaileup/scope/scope-project/references/decision-rule.md
                                              — long-form rule examples
```

- [ ] **Step 2: Add MUST / NEVER constraints (place EARLY per skill_grammar.md authoring tip 4)**

```
MUST   ask each interview question as its own standalone message (iron_laws § 9)
MUST   apply the decision rule verbatim — do not invent new branches
MUST   show the chosen tier + reasoning to the user before writing the YAML
MUST   set flow_to_run to "flow:<tier>" deterministically from the chosen tier
MUST   record signals.* exactly as collected (no rounding, no normalization)
MUST   if --tier= or tier_override is provided, set override.applied=true and
       record what the rule would have picked in override.rule_would_have_picked
MUST   if _concept/_meta/scope.yaml already exists, load it, show diff to user,
       and require explicit approval before overwriting (iron_laws § 8)
NEVER  write _concept/_meta/scope.yaml before the user approves the decision
NEVER  silently change tier on re-scoping — always surface diff
NEVER  bury interview questions inside a longer explanation message
```

- [ ] **Step 3: Add INPUT block (per skill_grammar.md)**

```
INPUT
  Read from: _concept/_grounding/scope-project/input.json (if present)
  If missing, ask the user:
  - project_description: One-sentence project description (required)
  - tier_override: Force a specific tier (optional) [mvp | simple-app | standard-app | complex-app] default: <none>
  - features_estimate: Estimated number of distinct user-facing features (optional)
  - multi_user: Multiple user roles or shared state? (optional) [true | false]
  - persistence: Data persistence shape (optional) [trivial | structured | external]
  - integrations: External services, comma-separated (optional)
```

- [ ] **Step 4: Add STEPs**

```
STEP 1: Detect re-scoping mode
  - $ test -f _concept/_meta/scope.yaml && echo "RE-SCOPE" || echo "FRESH"
  - IF re-scope: load existing values as defaults for the interview
  - IF fresh: collect project_description (required) before continuing

STEP 2: Collect signals (skip individual questions if pre-supplied via INPUT)
  Ask each as a STANDALONE message:
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
  rule_tier = (
    "mvp"          if features_estimate <= 1 and persistence == "trivial"
    else "simple-app"   if features_estimate <= 5 and not multi_user
    else "standard-app" if features_estimate <= 20 or multi_user
    else "complex-app"  if persistence == "external" or len(integrations) >= 2
    else "complex-app"  # documented fall-through
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

STEP 6: Show decision to user (CHECKPOINT)
  CHECKPOINT scope_decision
    Show:
      • chosen_tier
      • flow_to_run = "flow:<chosen_tier>"
      • reasoning
      • signals (all four)
      • override block (if applied)
    > "Approve this tier, or reply with --tier=<name> to override."

STEP 7: Write _concept/_meta/scope.yaml
  - $ mkdir -p _concept/_meta
  - Write the YAML following the pinned schema
  - chosen_at = current UTC ISO-8601 with "Z" suffix
  - chosen_by = "skaileup-scope-scope-project@<metadata.version>"
  - IF re-scope: show unified diff vs prior file before write; require explicit "yes"

STEP 8: Validate the written file
  - $ python3 skaileup/scope/scope-project/validator.py _concept/_meta/scope.yaml
  - On failure: report errors and STOP. Do not commit.

EMIT  [scope-project] decided tier=<chosen_tier> rule_picked=<rule_tier> override=<bool>
```

- [ ] **Step 5: Add OUTPUT template**

```
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
  chosen_by: "skaileup-scope-scope-project@1.0.0"
```

- [ ] **Step 6: Add CHECKLIST**

```
CHECKLIST
  - [ ] Interview questions sent as standalone messages
  - [ ] Decision rule applied verbatim (no new branches invented)
  - [ ] Decision shown to user via CHECKPOINT before write
  - [ ] _concept/_meta/scope.yaml conforms to pinned schema (validator passes)
  - [ ] flow_to_run == "flow:" + tier
  - [ ] If override applied, override.requested_tier == tier and rule_would_have_picked recorded
  - [ ] If re-scoping, diff was shown and user approved overwrite
  - [ ] EMIT line printed
```

- [ ] **Step 7: Verify body parses cleanly and contains expected sections**

Run: `grep -c "^STEP " skaileup/scope/scope-project/SKILL.md`
Expected: `8`

Run: `grep -c "^MUST\|^NEVER" skaileup/scope/scope-project/SKILL.md`
Expected: at least `12` (8 MUST + 3 NEVER + ... allow some slack)

- [ ] **Step 8: Commit body**

```bash
git add skaileup/scope/scope-project/SKILL.md
git commit -m "feat(scope): add scope-project SKILL.md body (Task 2A step 2)"
```

---

## Task 3: Author the long-form decision-rule reference

**Files:**
- Create: `skaileup/scope/scope-project/references/decision-rule.md`

- [ ] **Step 1: Make references directory**

Run: `mkdir -p skaileup/scope/scope-project/references`

- [ ] **Step 2: Author `references/decision-rule.md`**

The file should:
- Quote SKILL_GRAPH.md § 3 lines 132–160 verbatim at the top (the table + the rule)
- Explain each branch in 2–3 sentences with one concrete example
- Show the "interpretation lock-in" table (the `↔` mappings from this plan's "Pinned Decision Rule" section)
- Document the fall-through behavior explicitly
- Show one worked example per tier, computing `chosen_tier` from `signals`

Length target: 80–150 lines. This is loaded only if the SKILL body's reference is followed (progressive disclosure per `asset_frontmatter.md`).

- [ ] **Step 3: Verify file exists and has content**

Run: `wc -l skaileup/scope/scope-project/references/decision-rule.md`
Expected: between 80 and 200 lines.

- [ ] **Step 4: Commit reference doc**

```bash
git add skaileup/scope/scope-project/references/decision-rule.md
git commit -m "docs(scope): add scope-project decision-rule reference"
```

---

## Task 4: Author the four example fixtures

**Files:**
- Create: `skaileup/scope/scope-project/examples/{mvp,simple-app,standard-app,complex-app}.scope.yaml`
- Create: `skaileup/scope/scope-project/examples/fixtures.json`

These are the four canonical inputs that downstream snapshot tests use. They are also the "golden output" the validator pins against.

- [ ] **Step 1: Make examples directory**

Run: `mkdir -p skaileup/scope/scope-project/examples`

- [ ] **Step 2: Author `fixtures.json`**

Schema:

```json
[
  {
    "id": "mvp-personal-budget",
    "description": "A single-user personal budget tracker that stores entries in one local JSON file.",
    "signals": {"features_estimate": 1, "multi_user": false, "persistence": "trivial", "integrations": []},
    "expected_tier": "mvp"
  },
  {
    "id": "simple-recipe-saver",
    "description": "A solo recipe collector with tagging, search, and a print-friendly view.",
    "signals": {"features_estimate": 4, "multi_user": false, "persistence": "structured", "integrations": []},
    "expected_tier": "simple-app"
  },
  {
    "id": "standard-team-todo",
    "description": "A team todo app with assignees, due-date reminders, comments, and per-project views.",
    "signals": {"features_estimate": 12, "multi_user": true, "persistence": "structured", "integrations": ["sendgrid"]},
    "expected_tier": "standard-app"
  },
  {
    "id": "complex-erp-portal",
    "description": "A multi-product B2B portal integrating Stripe billing, Salesforce CRM sync, and a queue-driven order pipeline.",
    "signals": {"features_estimate": 35, "multi_user": true, "persistence": "external", "integrations": ["stripe", "salesforce", "rabbitmq"]},
    "expected_tier": "complex-app"
  }
]
```

- [ ] **Step 3: Author the four example `*.scope.yaml` files**

Each file is the YAML the skill would produce for the matching fixture, with `chosen_at: "2026-05-07T00:00:00Z"` and `chosen_by: "skaileup-scope-scope-project@1.0.0"` for snapshot stability. `override.applied: false`.

Mvp example fields (others follow the same shape):

```yaml
schema_version: "1.0"
tier: mvp
flow_to_run: "flow:mvp"
reasoning: |
  features_estimate is 1 and persistence is trivial, so the first branch of the
  decision rule fires: this is an MVP. Single-user, no integrations, local JSON
  storage — the lightest tier is appropriate.
description: "A single-user personal budget tracker that stores entries in one local JSON file."
signals:
  features_estimate: 1
  multi_user: false
  persistence: trivial
  integrations: []
override:
  applied: false
  requested_tier: null
  rule_would_have_picked: null
chosen_at: "2026-05-07T00:00:00Z"
chosen_by: "skaileup-scope-scope-project@1.0.0"
```

- [ ] **Step 4: Verify each fixture's expected_tier matches the rule applied to its signals**

Run a quick local check (the validator does this too — Task 5):

```bash
python3 - <<'EOF'
import json
data = json.load(open('skaileup/scope/scope-project/examples/fixtures.json'))
def rule(s):
    if s['features_estimate'] <= 1 and s['persistence'] == 'trivial': return 'mvp'
    if s['features_estimate'] <= 5 and not s['multi_user']: return 'simple-app'
    if s['features_estimate'] <= 20 or s['multi_user']: return 'standard-app'
    if s['persistence'] == 'external' or len(s['integrations']) >= 2: return 'complex-app'
    return 'complex-app'
for f in data:
    assert rule(f['signals']) == f['expected_tier'], f
print("OK: all 4 fixtures match the rule")
EOF
```
Expected: `OK: all 4 fixtures match the rule`

- [ ] **Step 5: Commit fixtures**

```bash
git add skaileup/scope/scope-project/examples/
git commit -m "test(scope): add scope-project fixtures (one per tier)"
```

---

## Task 5: Author `validator.py`

**Files:**
- Create: `skaileup/scope/scope-project/validator.py`

The validator is invoked two ways:
1. By the skill itself in STEP 8 against the just-written `_concept/_meta/scope.yaml`.
2. By `tests/test_validator.py` against the four example fixtures and synthetic negatives.

- [ ] **Step 1: Write a failing test first (TDD)**

Create `skaileup/scope/scope-project/tests/test_validator.py` with cases that EXIST before `validator.py`:

```python
# tests/test_validator.py
import json, subprocess, sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_DIR / "validator.py"
EXAMPLES = SKILL_DIR / "examples"
FIXTURES = json.loads((EXAMPLES / "fixtures.json").read_text())

def run_validator(yaml_path):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(yaml_path)],
        capture_output=True, text=True
    )

def test_all_four_examples_pass():
    for f in FIXTURES:
        path = EXAMPLES / f"{f['expected_tier']}.scope.yaml"
        r = run_validator(path)
        assert r.returncode == 0, f"{path} failed: {r.stderr}"

def test_missing_tier_fails(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text('schema_version: "1.0"\nflow_to_run: "flow:mvp"\n')
    r = run_validator(p)
    assert r.returncode != 0
    assert "tier" in r.stderr.lower() or "tier" in r.stdout.lower()

def test_flow_must_match_tier(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text(
        'schema_version: "1.0"\ntier: mvp\nflow_to_run: "flow:standard-app"\n'
        'reasoning: "x"*40\ndescription: "x"\n'
        'signals: {features_estimate: 1, multi_user: false, persistence: trivial, integrations: []}\n'
        'override: {applied: false, requested_tier: null, rule_would_have_picked: null}\n'
        'chosen_at: "2026-05-07T00:00:00Z"\nchosen_by: "skaileup-scope-scope-project@1.0.0"\n'
    )
    r = run_validator(p)
    assert r.returncode != 0

def test_snapshot_rule_for_each_fixture():
    """Determinism guard: rule(signals) == expected_tier for all 4 fixtures."""
    def rule(s):
        if s['features_estimate'] <= 1 and s['persistence'] == 'trivial': return 'mvp'
        if s['features_estimate'] <= 5 and not s['multi_user']: return 'simple-app'
        if s['features_estimate'] <= 20 or s['multi_user']: return 'standard-app'
        if s['persistence'] == 'external' or len(s['integrations']) >= 2: return 'complex-app'
        return 'complex-app'
    for f in FIXTURES:
        assert rule(f['signals']) == f['expected_tier'], f
```

- [ ] **Step 2: Run tests to confirm they fail (validator.py doesn't exist yet)**

Run: `pytest skaileup/scope/scope-project/tests/test_validator.py -v`
Expected: tests fail (or error out) because `validator.py` is missing.

- [ ] **Step 3: Implement `validator.py`**

Skeleton (the implementer fills in details — keep stdlib + PyYAML only):

```python
#!/usr/bin/env python3
"""Validator for _concept/_meta/scope.yaml. Exit 0 if valid, 2 if not."""
import sys, re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

ALLOWED_TIERS = {"mvp", "simple-app", "standard-app", "complex-app"}
ALLOWED_PERSISTENCE = {"trivial", "structured", "external"}
ISO8601_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")

def err(msg):
    print(f"INVALID: {msg}", file=sys.stderr)

def validate(path: Path) -> int:
    try:
        data = yaml.safe_load(path.read_text())
    except Exception as e:
        err(f"YAML parse error: {e}"); return 2
    if not isinstance(data, dict):
        err("root must be a mapping"); return 2

    errors = []
    # Required keys
    for k in ("schema_version","tier","flow_to_run","reasoning","description",
              "signals","override","chosen_at","chosen_by"):
        if k not in data:
            errors.append(f"missing key: {k}")

    # tier enum
    if data.get("tier") not in ALLOWED_TIERS:
        errors.append(f"tier must be one of {sorted(ALLOWED_TIERS)}; got {data.get('tier')!r}")

    # flow_to_run derivation
    if data.get("tier") in ALLOWED_TIERS:
        expected_flow = f"flow:{data['tier']}"
        if data.get("flow_to_run") != expected_flow:
            errors.append(f"flow_to_run must be {expected_flow!r}; got {data.get('flow_to_run')!r}")

    # reasoning length
    r = (data.get("reasoning") or "").strip()
    if not (30 <= len(r) <= 800):
        errors.append(f"reasoning length {len(r)} not in [30, 800]")

    # signals
    s = data.get("signals") or {}
    for k in ("features_estimate","multi_user","persistence","integrations"):
        if k not in s: errors.append(f"signals.{k} missing")
    if not isinstance(s.get("features_estimate"), int):
        errors.append("signals.features_estimate must be int")
    if not isinstance(s.get("multi_user"), bool):
        errors.append("signals.multi_user must be bool")
    if s.get("persistence") not in ALLOWED_PERSISTENCE:
        errors.append(f"signals.persistence must be one of {sorted(ALLOWED_PERSISTENCE)}")
    if not isinstance(s.get("integrations"), list):
        errors.append("signals.integrations must be list")

    # override
    o = data.get("override") or {}
    if not isinstance(o.get("applied"), bool):
        errors.append("override.applied must be bool")
    if o.get("applied") is True:
        if o.get("requested_tier") != data.get("tier"):
            errors.append("override.requested_tier must equal tier when applied=true")

    # chosen_at format
    if not ISO8601_Z.match(str(data.get("chosen_at",""))):
        errors.append(f"chosen_at must match ISO-8601 UTC with Z suffix; got {data.get('chosen_at')!r}")

    if errors:
        for e in errors: err(e)
        return 2
    print(f"OK: {path}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: validator.py <path/to/scope.yaml>", file=sys.stderr); sys.exit(2)
    sys.exit(validate(Path(sys.argv[1])))
```

- [ ] **Step 4: Run tests, confirm they pass**

Run: `pytest skaileup/scope/scope-project/tests/test_validator.py -v`
Expected: all 4 tests pass.

- [ ] **Step 5: Run validator against each example as a smoke test**

Run:
```bash
for f in skaileup/scope/scope-project/examples/*.scope.yaml; do
  python3 skaileup/scope/scope-project/validator.py "$f" || exit 1
done
```
Expected: 4 lines of `OK: ...`, exit 0.

- [ ] **Step 6: Commit validator + tests**

```bash
git add skaileup/scope/scope-project/validator.py skaileup/scope/scope-project/tests/
git commit -m "test(scope): add scope.yaml validator + snapshot tests"
```

---

## Task 6: Determinism harness (snapshot test)

The acceptance criterion is "Outputs are deterministic for the same inputs (modulo LLM jitter)." We can't test the LLM directly here, but we can test the deterministic core: **rule(signals) → tier**. The snapshot test in Task 5 already does this for all four fixtures (`test_snapshot_rule_for_each_fixture`).

- [ ] **Step 1: Confirm the snapshot test fails if a fixture's signals are mutated**

Run a sanity check:
```bash
python3 - <<'EOF'
import json
p = 'skaileup/scope/scope-project/examples/fixtures.json'
data = json.load(open(p))
data[0]['signals']['features_estimate'] = 99   # would force out of mvp
import tempfile, os
tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w')
json.dump(data, tmp); tmp.close()
# run rule manually
def rule(s):
    if s['features_estimate']<=1 and s['persistence']=='trivial': return 'mvp'
    if s['features_estimate']<=5 and not s['multi_user']: return 'simple-app'
    if s['features_estimate']<=20 or s['multi_user']: return 'standard-app'
    return 'complex-app'
print(rule(data[0]['signals']))   # should NOT be 'mvp'
os.unlink(tmp.name)
EOF
```
Expected: prints something other than `mvp` (proves the rule is sensitive to input).

- [ ] **Step 2: No commit needed — sanity check only.**

---

## Task 7: Final verification

- [ ] **Step 1: Tree shape**

Run: `find skaileup/scope/scope-project -type f | sort`
Expected:
```
skaileup/scope/scope-project/SKILL.md
skaileup/scope/scope-project/examples/complex-app.scope.yaml
skaileup/scope/scope-project/examples/fixtures.json
skaileup/scope/scope-project/examples/mvp.scope.yaml
skaileup/scope/scope-project/examples/simple-app.scope.yaml
skaileup/scope/scope-project/examples/standard-app.scope.yaml
skaileup/scope/scope-project/references/decision-rule.md
skaileup/scope/scope-project/tests/test_validator.py
skaileup/scope/scope-project/validator.py
```

- [ ] **Step 2: Frontmatter integrity (per CONTRIBUTING.md § Integrity Checklist)**

Run:
```bash
python3 - <<'EOF'
import yaml
fm = yaml.safe_load(open('skaileup/scope/scope-project/SKILL.md').read().split('---')[1])
assert fm['name'] == 'skaileup-scope-scope-project', fm['name']
assert fm['description'].startswith('Use when'), 'description should start with "Use when"'
assert 'version' in fm['metadata']
assert isinstance(fm['metadata']['tags'], list) and len(fm['metadata']['tags']) >= 3
assert fm['metadata']['stage'] in ('alpha','beta','stable')
print("OK")
EOF
```
Expected: `OK`

- [ ] **Step 3: Validator + tests green**

Run: `pytest skaileup/scope/scope-project/tests/ -v`
Expected: all pass.

- [ ] **Step 4: Iron Laws spot-check**

Visually verify the SKILL.md body:
- § 8 NO OVERWRITING WITHOUT APPROVAL → STEP 7 enforces re-scope diff approval
- § 9 QUESTIONS ARE STANDALONE → MUST line + STEP 2 explicit instruction
- § 7 NO ARTIFACT WITHOUT PREREQUISITES → STEP 1 detects mode; project_description gate is hard via frontmatter `inputs_required`

- [ ] **Step 5: Schema-compatibility note for downstream tasks**

Add a brief paragraph at the bottom of `references/decision-rule.md`:

> **Schema stability:** the schema in this skill is the canonical contract for downstream tasks 2B / 2C / 2D / 2H. Bumping `schema_version` is a major version bump (per `contracts/asset_frontmatter.md` § Skills) and requires updates to every consumer.

- [ ] **Step 6: Final commit**

```bash
git add -A skaileup/scope/scope-project/
git commit -m "feat(scope): finalize scope-project skill (Task 2A complete)"
```

---

## Definition of Done

- [ ] `skaileup/scope/scope-project/SKILL.md` exists with valid frontmatter (`name: skaileup-scope-scope-project`) and full DSL body
- [ ] `validator.py` exists, runs against any candidate `scope.yaml`, exits 0 only for schema-compliant files
- [ ] Four example fixtures in `examples/` (one per tier) pass the validator
- [ ] `tests/test_validator.py` has at least 4 tests covering: all-examples-pass, missing-tier, flow/tier mismatch, fixture-rule-snapshot
- [ ] All tests green via `pytest skaileup/scope/scope-project/tests/ -v`
- [ ] `references/decision-rule.md` quotes SKILL_GRAPH.md § 3 verbatim and documents fall-through
- [ ] The `scope.yaml` schema in this plan matches the one produced by the skill (manually compare against any of the four example outputs)
- [ ] Iron Laws § 8 (overwrite approval) and § 9 (standalone questions) are enforced by `MUST` lines AND by step procedures
- [ ] No edits to `skaileup/skills/skaileup/SKILL.md` (base orchestrator) — that's a later task
- [ ] All commits land on the active migration branch with messages following the `feat(scope): / test(scope): / docs(scope):` prefix convention

---

## Open Questions / Ambiguities

1. **Path for `_concept/_grounding/scope-project/input.json` pre-collection** — `contracts/skill_grammar.md` § INPUT shows this pattern, but it's not clear whether the orchestrator pre-collects scope inputs into `_grounding/` for this skill specifically. The plan above treats this as optional (read if present, otherwise interview). If the orchestrator team confirms a different path, update STEP 1 + INPUT block.

2. **`flow_to_run` value form** — SKILL_GRAPH.md § 6 shows `bundle:simple-app` / `flow:simple-app` style identifiers in CLI examples. The plan pins `flow:<tier>`. Confirm with the flow-engine schema (`contracts/asset_frontmatter.md` § Flow shows `id: flow-id`); if flow ids drop the `flow:` prefix in practice, switch to bare `<tier>` (e.g. `flow_to_run: simple-app`). This is a small change to the validator's `expected_flow` and to all four examples.

3. **Determinism guarantee scope** — the acceptance criterion says "deterministic for the same inputs (modulo LLM jitter)." The plan's snapshot test only covers the deterministic *rule* — not the LLM-driven interview. If a stronger test is desired (e.g. running the skill twice via `claude -p` against the same description), the executing agent should add a Task 8 that wraps the skill in a transcript replay. Flagged as out-of-scope here.

4. **Re-scoping schema migrations** — the plan reserves `schema_version: "1.0"` but doesn't specify migration behavior for older `scope.yaml` files. Since this is the FIRST version, no migration logic is needed yet; future bumps must add a migrator. The validator currently rejects unknown `schema_version` only implicitly (by missing-fields errors). A stricter check could be added later.

5. **Naming-exception confirmation** — the parent plan (line 87) explicitly states `name: skaileup-scope-scope-project` (no shortening). CONTRIBUTING.md's "Naming pitfall" section warns about directory-vs-frontmatter mismatch but doesn't forbid the doubled prefix. The plan adopts the parent plan's directive verbatim. If a future cleanup wants to rename this to `scope-project` (short form), it's a major version bump.

6. **Fall-through wording** — the verbatim rule has four `if/elif` branches; the fourth (`multi-product or enterprise integration`) is technically reachable only when none of the prior three matched. The plan documents an explicit fall-through to `complex-app` for cases like "30 features, single-user, structured persistence, no integrations" which the literal rule would not classify. This interpretation should be sanity-checked with whoever wrote SKILL_GRAPH.md § 3 — flagged so it doesn't silently propagate.
