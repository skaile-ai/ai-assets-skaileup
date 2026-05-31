---
title: "ops"
description: "Cross-cutting: review · sync · eval · add-feature · reverse-engineer · project-*"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`skaileup/ops/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/ops/DOMAIN.md)
:::


# ops

Cross-cutting skills that operate on an existing concept or implementation: health checks, concept mutation, evaluation gates, and multi-product project orchestration. Used after initial generation is complete or when the pipeline needs a quality gate.

## Skills

- **ops-review** (`review/`) — Audit or auto-fix `_concept/`; produces `_concept/quality.json` with a completeness + entropy score.
- **ops-sync** (`sync/`) — Repair broken cross-references and orphaned entities in `_concept/`; shows diff before applying.
- **ops-add-feature** (`add-feature/`) — Add or modify a feature in a live concept; cascades through journeys, tech stack, architecture, data model, and screens.
- **ops-reverse-engineer** (`reverse-engineer/`) — Bootstrap a `_concept/` folder from an existing repository.
- **ops-eval-concept** (`eval-concept/`) — Adversarial completeness gate; produces `_concept/eval-concept.json`. Run before implementation begins.
- **ops-eval-feature** (`eval-feature/`) — Browser-based feature verifier after each feature group; produces `_implementation/eval-feature/{group}.json`.
- **ops-eval-product** (`eval-product/`) — Whole-product final gate; grades quality, craft, accessibility, and mobile; produces `_implementation/eval-product.json`.
- **ops-project-overview** (`project-overview/`) — Generates `discovery/` in a meta-concept: ecosystem brief, goals, competitive positioning.
- **ops-project-subsystem-map** (`project-subsystem-map/`) — Generates `2_subsystems/` in a meta-concept: subsystem index with maturity, audience, and tech stack.
- **ops-project-integration** (`project-integration/`) — Generates `3_integration/` in a meta-concept: inter-repo architecture, deployment topology, shared contracts.
- **ops-project-review** (`project-review/`) — Audits a meta-concept for completeness, consistency, and accurate maturity claims.

## When to Use

- Concept is complete and needs a quality gate before implementation (`ops-eval-concept`, `ops-review`).
- User asks to add/change a feature in an already-built concept (`ops-add-feature`).
- `_concept/` has stale cross-references after a bulk edit (`ops-sync`).
- Working with an existing codebase that has no `_concept/` yet (`ops-reverse-engineer`).
- Multi-product project requires a meta-concept (`ops-project-*`).

## When NOT to Use

- Concept does not exist yet — use the `concept/` domain first.
- Implementation has not started — `ops-eval-feature` / `ops-eval-product` require a running app.
- Single-product apps — `ops-project-*` skills are for multi-repo ecosystems only.

## Sequence

Eval skills have a hard order:

```
ops-eval-concept  →  (implementation runs)  →  ops-eval-feature (per group)  →  ops-eval-product
```

`ops-review` and `ops-sync` are independent and can run at any time.

## Cross-references

- `../contracts/` — iron laws and golden principles every ops skill reads.
- `../impl-quality/` — implementation-side quality skills (test, audit, debug).
- `../SKILL_GRAPH.md` — collection-level view and domain relationships.


## Skills in this domain

- [ops-add-feature](./ops-add-feature/) — Use when adding a new feature or modifying an existing feature in a live concept. Surgically adds the feature spec, cascades changes through
- [ops-eval-concept](./ops-eval-concept/) — Use before implementation begins to verify concept completeness and clarity. Independent adversarial review of _concept/ artifacts: checks e
- [ops-eval-feature](./ops-eval-feature/) — Use after each feature group is implemented to verify the running app matches specs. Independent browser-based adversarial review: simulates
- [ops-eval-product](./ops-eval-product/) — Use after all feature groups pass eval-feature as the final gate before release. Grades the complete application against original brief goal
- [ops-project-integration](./ops-project-integration/) — Use when building a multi-product meta-concept and the integration section is missing. Generates 3_integration/ covering inter-repo architec
- [ops-project-overview](./ops-project-overview/) — Use when starting a multi-product meta-concept and the discovery section does not exist yet. Generates discovery/ covering ecosystem brief, 
- [ops-project-review](./ops-project-review/) — Use when a multi-product meta-concept needs a quality check. Audits for completeness, consistency, and accuracy — verifies all subsystems ar
- [ops-project-subsystem-map](./ops-project-subsystem-map/) — Use when building a multi-product meta-concept and the subsystem index is missing. Generates 2_subsystems/ with maturity, audience, tech sta
- [ops-reverse-engineer](./ops-reverse-engineer/) — Use when the user has an existing project repository and wants to generate or bootstrap a _concept/ folder from it. Triggered by: 'reverse e
- [ops-review](./ops-review/) — Use when _concept/ needs a quality check or housekeeping pass. In audit mode: scans completeness, cross-reference integrity, golden principl
- [ops-sync](./ops-sync/) — Use when cross-references in _concept/ are broken or out of sync. Scans the entire concept folder, finds broken links, missing bidirectional
