---
name: "shared-contracts"
description: "Shared reference layer read by every skill — iron laws, golden principles, skill grammar, canonical frontmatter, _concept/ structure, semantic types, and acceptance-criteria conventions. Not invocable; skills read these files via REFERENCES/requires to enforce shared constraints."
metadata:
  stage: alpha
  do_not_invoke: true
---

# Shared Contracts — Reference Layer

**Do not invoke directly.** This is a dependency contract — every skill in the
collection reads these files (via `REFERENCES` / `requires`) to enforce shared
constraints, schemas, and conventions. No flow runs it; installing any flow
pulls it in because the flow's skills depend on it.

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
