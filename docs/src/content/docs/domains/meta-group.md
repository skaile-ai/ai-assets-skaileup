---
title: "Meta group"
description: "The cross-cutting layer — orchestrators, ops, the skill-on-skill lab, and the shared contracts every skill reads."
sidebar:
  label: "Overview"
  order: 0
---

The **Meta group** is the cross-cutting layer that routes the pipeline, runs
cross-cutting operations, builds skills out of skills, and holds the shared
contracts every skill reads.

## Domains

- [**skaileup-orchestrator**](./skaileup-orchestrator/) — base orchestrators + scope/ — pipeline entry
- [**ops**](./ops/) — review · sync · add-feature · reverse-engineer · eval-* · project-*
- [**lab**](./lab/) — skill-on-skill: validate · judge · improve · learn · compile-bundle
- [**contracts**](./contracts/) — the shared reference layer (iron laws, golden principles, schemas)

## See also

- [How It's Consumed](../../intro/consumption/) — `skaile add` / `skaile run`
- [Flows](../../flows/) — what the orchestrators execute
- [Contributing](../../reference/contributing/) — authoring skills with the `skaile` CLI
