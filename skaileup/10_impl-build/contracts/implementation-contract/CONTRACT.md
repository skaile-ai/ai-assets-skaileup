---
name: 'implementation-contract'
description: 'Shared contract for all impl-build-implementation skills. Describes _implementation/ folder layout, scaffold-to-verify pipeline, progress.yaml format, git workflow, and how implementation reads from _concept/. REQUIRED reading for any implementation skill.'
metadata:
  stage: 'alpha'
  do_not_invoke: true
---

# Implementation Domain — Shared Contract

**Do not invoke directly.** This is a dependency contract — all `impl-build-implementation` skills read this before operating.

## Scope

This contract covers artifacts and conventions that are **implementation-specific**.
Conventions shared with `conceptualization` (semantic types, pipeline graph, plans format) live in `contracts/`.

## Prerequisites from \_concept/

Implementation reads the following before starting:

```
_concept/discovery/brief.md         ← app name, slug, complexity_tier
_concept/experience/features/**/*.md          ← feature list and priorities
_concept/blueprint/datamodel/model.json       ← data model
_concept/blueprint/techstack.md         ← tech stack (drives expert skill selection)
_concept/experience/screens/**/*.md           ← screen specs (for verification)
? _concept/blueprint/architecture.md
```

## \_implementation/ Folder Layout

```
_implementation/
├── PLANS.md              ← durable implementation plan — lean scope + ordered phases (no status)
├── progress.yaml         ← machine-readable feature status (completion source of truth)
├── decisions.md          ← build-time decision records (ADRs) — append-only, 3-test gate
└── <framework-specific>/ ← scaffold output (managed by foundation/scaffold skills)
```

## progress.yaml Format

```yaml
schema_version: "1.0"
app: <slug>
updated_at: YYYY-MM-DDTHH:MM:SSZ
features:
  - id: <group>/<feature-slug>
    label: <Human Label>
    status: not_started | in_progress | implemented | verified
    impl_status: pending | scaffolded | coded | tested
    last_updated: YYYY-MM-DD
```

## Pipeline Phase Structure

| Phase       | Group             | Skills involved                         |
| ----------- | ----------------- | --------------------------------------- |
| Orchestrate | `00_orchestrator` | orchestrator (drives all phases)        |
| Setup       | `10_setup`        | foundation, scaffold, infrastructure    |
| Features    | `20_features`     | feature (per-feature TDD loop), page    |
| Verify      | `30_verify`       | verify (spec compliance + quality gate) |
| Utilities   | `utilities`       | migrate, seed, scaffold, generate       |

## Expert Skill Discovery

During implementation, skills search for matching `skaileup-prog-expert-*` skills:

1. Read `_concept/blueprint/techstack.md`
2. Search paths: `.claude/skills/`, `.agents/skills/`, paths in `pipeline.json` `config.expert_search_paths`
3. If found: include expert SKILL.md in subagent context
4. Expert recipes guide implementation patterns

## Git Workflow (Saxe lineage)

- Feature branches: `feat/<feature-slug>`
- Commit format: `feat(<group>): <description>`
- Merge only after `verify` step passes

## PLANS.md (Implementation Phase)

Lean scope + ordered phases only. **No status checkboxes** (live status is
`progress.yaml`) and **no decisions section** (decisions are ADRs in `decisions.md`,
per `contracts/domain_model.md`). See `contracts/plans.md` for the canonical shape.

```markdown
## Implementation Plan: <App Name>

### Scope
<What's built this phase, what's out.>

### Stack
- Framework: <framework>
- Profile: <profile>

### Phases
1. scaffold
2. foundation
3. feature/user_auth
4. feature/dashboard
   ...

> Live status: progress.yaml. Decisions: decisions.md.
```
