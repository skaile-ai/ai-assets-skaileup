---
name: impl-quality-test-plan
description: 'Use when you need a comprehensive test plan derived from concept specs. Generates test scenarios per feature covering happy paths, error states, edge cases, and permissions, mapped to seed data scenarios.'
metadata:
  version: '1.0.0'
  stage: alpha
  tags:
    - 'testing'
    - 'test-plan'
    - 'qa'
    - 'scenarios'
    - 'coverage'
    - 'acceptance'
  source: 'MIGRATED'
  artifacts:
    requires:
      - id: features
        gate: hard
      - id: journeys
        gate: hard
      - id: screens
        gate: hard
      - id: datamodel
        gate: hard
    consumes:
      - id: behaviors
        gate: soft
    produces:
      - id: test-plan
  prerequisites:
    files:
      - path: '_concept/experience/features'
        gate: hard
        description: 'Feature specs required to generate test scenarios'
        min_entries: 1
      - path: '_concept/experience/journeys/stories.json'
        gate: hard
        description: 'Stories with EARS acceptance criteria — every criterion must map to at least one test scenario'
      - path: '_concept/experience/screens'
        gate: hard
        description: 'Screen specs required for UI state test coverage'
        min_entries: 1
      - path: '_concept/blueprint/datamodel/model.json'
        gate: hard
        description: 'Data model required for data validation test scenarios'
    inputs_required:
      - id: test_scope
        label: 'Test Scope'
        type: select
        options:
          - must-have-only
          - all-features
        default: all-features
        hint: 'Whether to generate test scenarios for must-have features only or all features'
    reads:
      - path: '_concept/blueprint/datamodel/seed.json'
        description: 'Seed scenarios for test fixture mapping'
      - path: '_concept/experience/behaviors'
        description: 'Behavioral specs for state machine test coverage'
---

# Test Plan — Concept-Driven Test Generation

## Overview

Generates a structured test plan from the concept specifications. Reads features,
screens, data model, and seed data to produce test scenarios for every feature,
covering happy paths, error states, edge cases, and permission boundaries. Output
is a single plan file at `_concept/testing/test_plan.md`.

## When to Use

- After features, screens, and data model are approved — to define what needs testing
- Before implementation begins — to establish acceptance criteria upfront
- Before `e2e` — to have a structured test script to follow
- When the user says "test plan", "what should we test", or "generate test scenarios"

## When NOT to Use

- For running actual tests — use `e2e` (browser) or `verify` (spec fidelity)
- For generating test code — use `test-unit` or `test-integration`
- For auditing existing test coverage — use `audit`
- When features are still in draft — wait for approved specs first

## Prerequisites

**Hard gates:**

1. Feature specs must exist in `_concept/experience/features/`
2. Screen specs must exist in `_concept/experience/screens/`
3. Data model must exist at `_concept/blueprint/datamodel/model.json`

Recommended (not blocking): `seed.json`, `experience/behaviors/*.allium`

## Shared Contracts

Before starting, read:

- `contracts/concept_structure.md` — valid \_concept/ paths
- `contracts/frontmatter.md` — feature frontmatter fields
- `contracts/feedback_loop.md` — cross-reference protocol
- `contracts/seed_data.md` — scenario-based seed data convention
- `contracts/acceptance_criteria.md` — EARS patterns; every criterion must be traced to a test
- `contracts/iron_laws.md` — non-negotiable constraints

## Context Budget

| Source                                    | Priority |
| ----------------------------------------- | -------- |
| `_concept/discovery/brief.md`             | Required |
| `_concept/experience/features/**/*.md`    | Required |
| `_concept/experience/journeys/stories.json` | Required |
| `_concept/blueprint/datamodel/model.json` | Required |
| `_concept/blueprint/datamodel/seed.json`  | Required |
| `_concept/experience/screens/**/*.md`     | Required |
| `_concept/experience/behaviors/*.allium`  | Optional |

## Workflow

### Step 1: Read Context and Apply Scope Filter

1. Read `_concept/discovery/brief.md` — app overview
2. Read `_concept/experience/features/**/*.md` — all feature specs
3. Read `_concept/experience/journeys/stories.json` — stories + EARS `acceptance_criteria` (and `gherkin_scenarios` if present)
4. Read `_concept/experience/screens/**/*.md` — all screen specs
5. Read `_concept/blueprint/datamodel/model.json` — entities, relationships, field constraints
6. Read `_concept/blueprint/datamodel/seed.json` — named scenarios (if exists)
7. Read `_concept/experience/behaviors/*.allium` — behavioral rules (if exists)

Build an **acceptance-criteria index**: every story's EARS criteria, keyed by
`story-id`. Each feature lists its `story_refs:` — this is how feature scenarios
trace back to the originating stories. Each EARS criterion (and each
`gherkin_scenario`) is a test obligation that MUST be covered in Step 2.

Apply `test_scope` filter:

- `must-have-only`: include only features where `priority: must-have`
- `all-features`: include all features regardless of priority

### Step 2: Generate Scenarios Per Feature

For each in-scope feature, produce four scenario categories:

#### Happy Path

What happens when everything works correctly.

- One scenario per requirement checkbox in the feature spec
- **One scenario per EARS acceptance criterion** of every story in the feature's
  `story_refs:` — the criterion text is the expected outcome; tag the scenario
  with its `story-id`. Expand any `gherkin_scenarios` step-by-step.
- Map to `populated` seed data scenario
- Include expected UI state from screen spec

#### Error States

What happens when things go wrong.

- One scenario per error state documented in the feature spec
- Include form validation failures (derive from model.json field constraints)
- Include API error responses (network, auth, server)
- Map to `edge_cases` seed data scenario where applicable

#### Edge Cases

Boundary conditions and unusual inputs.

- Empty states (map to `empty` seed data scenario)
- Maximum length inputs (derive from model.json field types)
- Special characters in text fields
- Concurrent operations (if relevant)
- First-time user vs. returning user (map to `single_user` scenario)

#### Permissions (if roles exist)

Role-based access control scenarios.

- One scenario per role defined in feature's `roles:` field
- What each role CAN do (positive test)
- What each role CANNOT do (negative test)
- If `.allium` files exist, derive from `facing` clauses

### Step 3: Map Scenarios to Seed Data

For each scenario, specify which seed data scenario and entities to use:

```markdown
| Scenario                 | Seed Scenario | Entities                 | Setup Notes        |
| ------------------------ | ------------- | ------------------------ | ------------------ |
| Login with valid creds   | populated     | user (admin@example.com) | Pre-seeded user    |
| Login with invalid creds | populated     | —                        | Use wrong password |
| Dashboard empty state    | empty         | —                        | No data seeded     |
| Task list overflow       | edge_cases    | task (100 items)         | Pagination test    |
```

### Step 4: Calculate Coverage Summary

The `AC` columns track acceptance-criteria traceability: `AC` = EARS criteria
reachable via this feature's `story_refs`, `AC✓` = criteria with at least one
mapped scenario. **`AC✓` must equal `AC` for every feature** — any gap is listed
in the Uncovered Criteria section below and flagged to the user.

```
## Coverage Summary

| Feature | Happy | Error | Edge | Permissions | Total | AC | AC✓ |
|---------|-------|-------|------|-------------|-------|----|----|
| Login | 3 | 4 | 2 | 2 | 11 | 5 | 5 |
| Dashboard | 5 | 2 | 3 | 1 | 11 | 4 | 4 |
| Settings | 2 | 1 | 2 | 0 | 5 | 2 | 2 |
| **Total** | **10** | **7** | **7** | **3** | **27** | **11** | **11** |
```

If any `AC✓ < AC`, list the unmapped criteria:

```
## Uncovered Acceptance Criteria

| Story | Criterion (EARS) | Feature | Reason |
|-------|------------------|---------|--------|
| story-04 | WHEN session expires THE SYSTEM SHALL re-prompt login | Login | No screen spec for expiry state |
```

Resolve each gap by adding a scenario, or record why it cannot be tested here
(e.g. requires load testing). **Do not silently drop a criterion.**

### Step 5: Write Test Plan

Write `_concept/testing/test_plan.md`:

```yaml
---
last_updated: YYYY-MM-DD
scope: all-features # or must-have-only
feature_count: N
scenario_count: N
seed_data_mapped: true
ac_total: N # EARS criteria in scope
ac_covered: N # criteria with >=1 mapped scenario (must equal ac_total)
---
```

Structure the file:

```markdown
# Test Plan

## Scope

[must-have-only | all-features] — N features, N scenarios

## Coverage Summary

[table from Step 4]

## Uncovered Acceptance Criteria

[table from Step 4 — empty if every criterion is covered]

## Feature: <Name>

### Happy Path

- [ ] **Scenario name** — Description. Route: /path. Seed: populated.
      AC: story-02. Expected: [outcome]. Evidence: [what to check].

### Error States

- [ ] **Scenario name** — Description. Trigger: [how to cause error].
      Expected: [error message/behavior].

### Edge Cases

- [ ] **Scenario name** — Description. Seed: edge_cases.
      Expected: [outcome].

### Permissions

- [ ] **Scenario name** — Role: admin. Expected: [access granted/denied].

## Seed Data Requirements

[table from Step 3]
```

### Step 6: Present Summary

Show the coverage summary table and ask:

> "Test plan generated with N scenarios across N features. Review the plan at
> `_concept/testing/test_plan.md`. Would you like to adjust scope, add
> custom scenarios, or proceed?"

## Outputs

- `_concept/testing/test_plan.md` — the complete test plan

## Common Mistakes

| Mistake                                           | What to do instead                                                |
| ------------------------------------------------- | ----------------------------------------------------------------- |
| Writing test code instead of a plan               | This skill produces a markdown plan, not executable tests         |
| Ignoring seed.json scenarios                      | Map every scenario to a named seed data scenario                  |
| Only testing happy paths                          | Require at least 1 error + 1 edge case per feature                |
| Inventing requirements not in specs               | Every scenario must trace to a feature requirement or screen spec |
| Ignoring stories.json EARS criteria               | Every acceptance criterion must map to ≥1 scenario; gaps go in Uncovered Acceptance Criteria |
| Skipping permissions when roles exist             | If `roles:` has multiple entries, generate permission scenarios   |
| Testing nice-to-have when scope is must-have-only | Respect the `test_scope` user input                               |

EMIT [test-plan] started run_id=<uuid> scope=<scope>
EMIT [test-plan] checkpoint phase=scenarios_generated features=<N> scenarios=<N> ac_total=<N> ac_covered=<N>
EMIT [test-plan] completed run_id=<uuid> output=\_concept/testing/test_plan.md features=<N> scenarios=<N> ac_total=<N> ac_covered=<N>
