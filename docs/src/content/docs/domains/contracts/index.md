---
title: "contracts"
description: "Shared reference layer (every skill reads)"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`skaileup/contracts/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/contracts/DOMAIN.md)
:::


# contracts

Reference material consumed by every skill in the catalog. Not invocable — no flow runs it. Skills read these files via `REFERENCES` declarations to enforce shared constraints, schemas, and conventions.

## Contents

- **`iron_laws.md`** — Non-negotiable gates (e.g. no data model without features). Skills enforce via `requires`.
- **`golden_principles.md`** — Mechanical rules enforced by lint (entities, enums, naming).
- **`skill_grammar.md`** — DSL keyword reference (`STEP`, `MUST`, `NEVER`, `CHECKLIST`, etc.).
- **`asset_frontmatter.md`** — Canonical YAML frontmatter for skill/prompt/agent/flow assets.
- **`frontmatter.md`** — YAML fields for `_concept/` output artifacts.
- **`semantic_types.md`** — Stack-independent types and translation table.
- **`concept_structure.md`** — Canonical `_concept/` paths, naming rules, read direction.
- **`acceptance_criteria.md`** — EARS format (When/Then/So that).
- **`agent_patterns.md`** — Standalone mode, subagent dispatch, communication style rules.
- **`skill_template.md`** — Template for new SKILL.md files.
- **`skill_testing.md`** — Fixture format and `_validation.json` schema for skill self-tests.
- **`flows.md`** — Multi-step flow definition format.
- **`plans.md`** — PLANS.md format (concept plan + implementation plan + decisions log).
- **`feedback_loop.md`** — Cross-reference protocol (features ↔ screens, model → features).
- **`seed_data.md`** — Scenario-based seed data conventions.
- **`elements_block.md`** — `elements:` block schema for screen/component artifacts.

### Subdirectories

- **`schemas/`** — YAML schemas for structured concept artifacts (audiences, competitors, onboarding profile, etc.).
- **`profiles/`** — Stack profiles per app type (`web-app`, `api-service`, `cli-tool`, `mobile-app`, etc.). Read by `impl-architecture-techstack`.
- **`scripts/`** — Shared Python linting tools (`lint_concept.py`, `validate_skill_rules.py`, `validator_lib.py`). Run by `impl-quality` skills.

## When to Use

- Any skill enforcing iron laws or golden principles should declare `REFERENCES contracts/iron_laws.md`.
- Any skill producing `_concept/` artifacts must reference `concept_structure.md` for canonical paths.
- New skill authors read `skill_grammar.md` and `skill_template.md` before writing a SKILL.md.
- `lab/validate` runs `scripts/validate_skill_rules.py` against skills under review.

## When NOT to Use

- Do not add invocable skills here — this domain is reference-only.
- Do not store project-specific artifacts here; `_concept/` is the output layer.

## Cross-references

- `skaileup/flows/_meta/` — `verify_flows.py` validates bundles match flow node graphs.
- `ai-assets/lab/compile-bundle/` — reads `profiles/` to emit bundle YAMLs.
- `SKILL_GRAPH.md` — catalog-level view of domain relationships.


## Skills in this domain

_No skills found._
