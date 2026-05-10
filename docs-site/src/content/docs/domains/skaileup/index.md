---
title: "skaileup-scope"
description: "Project-size scoping — interviews user, picks tier, drives flow selection."
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`skaileup/scope/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/scope/DOMAIN.md)
:::


# skaileup/scope

Project-size scoping cluster: interviews the user, picks a tier (mvp / simple-app / standard-app / complex-app), and drives flow selection. First action in the skaileup pipeline.

## Skills

- **skaileup-scope-scope-project** (`scope-project/`) — Picks one of mvp / simple-app / standard-app / complex-app from a one-sentence project description and writes `_concept/_meta/scope.yaml`. Gates which flow runs next.

## Cross-references

- See `../../SKILL_GRAPH.md` for the catalog-level view.


## Skills in this domain

- [skaileup](./skaileup/) — Full concept pipeline orchestrator. Runs the complete conceptualization pipeline (Discovery -> Experience -> Blueprint) with checkpoint appr
- [skaileup-build](./skaileup-build/) — Full app implementation orchestrator. Reads the completed _concept/ and drives the entire pipeline from project scaffold through feature imp
- [skaileup-scope-scope-project](./skaileup-scope-scope-project/) — Use when the user starts a new project and no _concept/_meta/scope.yaml exists yet, or when re-scoping (--tier= override). Picks one of mvp 
