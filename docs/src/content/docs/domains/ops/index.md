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

Provides cross-cutting operational skills: code review, syncing, evaluation, feature addition, reverse engineering, and project-level orchestration. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **ops-review** (`review/`) — Structure audit + entropy check + doc gardening for `_concept/`; produces `quality.json` with score (audit mode) or auto-fixes safe issues (gardening mode).
- **ops-sync** (`sync/`) — Scans `_concept/` for broken cross-references, missing bidirectional links, and orphaned entities; shows a diff before applying fixes.
- **ops-add-feature** (`add-feature/`) — Surgically adds or modifies a feature in a live concept; cascades changes through journeys, tech stack, architecture, data model, and screens.
- **ops-reverse-engineer** (`reverse-engineer/`) — Generates or bootstraps a `_concept/` folder from an existing project repository.
- **ops-eval-concept** (`eval-concept/`) — Concept completeness gate; an independent adversarial evaluator verifies traceable acceptance criteria, screen specs, data model coverage, and unambiguous brief.
- **ops-eval-feature** (`eval-feature/`) — Feature implementation evaluator; an independent sub-agent verifies the running app matches the feature spec via browser-based user-perspective journeys.
- **ops-eval-product** (`eval-product/`) — Whole-product evaluator; runs after all feature groups are approved and grades the application against original goals on quality, originality, craft, functionality plus performance, accessibility, and mobile.
- **ops-project-overview** (`project-overview/`) — Generates the `discovery/` section of a meta-concept: ecosystem brief, unified goals, and competitive positioning for a multi-product project.
- **ops-project-subsystem-map** (`project-subsystem-map/`) — Generates the `2_subsystems/` section of a meta-concept: index of all subsystems with maturity, audience, tech stack, and references.
- **ops-project-integration** (`project-integration/`) — Generates the `3_integration/` section of a meta-concept: inter-repo architecture, deployment topology, and shared contracts.
- **ops-project-review** (`project-review/`) — Audits a meta-concept for completeness, consistency, and accuracy across subsystems, references, and maturity claims.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.


## Skills in this domain

- [ops-add-feature](./ops-add-feature/) — Use when adding a new feature or modifying an existing feature in a live concept. Surgically adds the feature spec, cascades changes through
- [ops-eval-concept](./ops-eval-concept/) — Concept completeness and clarity gate. An independent evaluator reviews _concept/ artifacts adversarially — assumes gaps exist and proves co
- [ops-eval-feature](./ops-eval-feature/) — Feature implementation evaluator. An independent sub-agent verifies the running app matches the feature spec and acceptance criteria after a
- [ops-eval-product](./ops-eval-product/) — Whole-product evaluator. Runs after all feature groups are approved by eval-feature. Evaluates the complete application against the original
- [ops-project-integration](./ops-project-integration/) — Generate the 3_integration/ section of a meta-concept: inter-repo architecture, deployment topology, and shared contracts for a multi-produc
- [ops-project-overview](./ops-project-overview/) — Generate the discovery/ section of a meta-concept: ecosystem brief, unified goals, and competitive positioning for a multi-product project.
- [ops-project-review](./ops-project-review/) — Audit a meta-concept for completeness, consistency, and accuracy. Checks that all subsystems are documented, references are valid, maturity 
- [ops-project-subsystem-map](./ops-project-subsystem-map/) — Generate the 2_subsystems/ section of a meta-concept: index of all subsystems with maturity, audience, tech stack, and references to per-sub
- [ops-reverse-engineer](./ops-reverse-engineer/) — Use when the user has an existing project repository and wants to generate or bootstrap a _concept/ folder from it. Triggered by: 'reverse e
- [ops-review](./ops-review/) — Structure audit + entropy check + doc gardening for _concept/. In audit mode: scan completeness, cross-reference integrity, golden principle
- [ops-sync](./ops-sync/) — Use when cross-references in _concept/ are broken or out of sync. Scans the entire concept folder, finds broken links, missing bidirectional
