---
title: "skaileup-scope"
description: "Project-size scoping — interviews user, picks tier, drives flow selection."
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`skaileup/skaileup-orchestrator/scope/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/skaileup-orchestrator/scope/DOMAIN.md)
:::


# skaileup/scope

Project-size scoping cluster: interviews the user, picks a tier (mvp / simple-app / standard-app / complex-app), and drives flow selection. First action in the skaileup pipeline.

## Skills

- **skaileup-scope-scope-project** (`scope-project/`) — Picks one of mvp / simple-app / standard-app / complex-app from a one-sentence project description and writes `_concept/_meta/scope.yaml`. Gates which flow runs next.

## Cross-references

- See `../../../../docs/devlog/SKILL_GRAPH.md` for the catalog-level view.


## Skills in this domain

- [skaileup](./skaileup/) — Use when starting or resuming the full concept pipeline for a new product. Runs Discovery → Experience → Blueprint with checkpoint approvals
- [skaileup-build](./skaileup-build/) — Use when concept is complete and you want to build the entire application end-to-end. Drives the full pipeline from scaffold through feature
- [skaileup-scope-scope-project](./skaileup-scope-scope-project/) — Use when the user starts a new project and no _concept/_meta/scope.yaml exists yet, or when re-scoping (--tier= override). Picks one of mvp 
