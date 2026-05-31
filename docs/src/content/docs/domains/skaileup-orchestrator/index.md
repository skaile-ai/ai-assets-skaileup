---
title: "skaileup"
description: "Top-level conversational guide for the skaileup concept → implementation pipeline"
sourcePath: "skaileup/skaileup-orchestrator/DOMAIN.md"
sidebar:
  label: "Overview"
  order: 0
---


## Purpose

Entry point for users starting or resuming a skaileup pipeline session. Discovers installed
orchestrators and flows at runtime; guides users through each step with or without the flow
engine present. Does not contain pipeline logic — delegates to domain-specific orchestrators.

## Agents

| Agent    | Path             | What it does                    | When to use         |
| -------- | ---------------- | ------------------------------- | ------------------- |
| skaileup | agents/skaileup/ | Conversational guide and router | Always — start here |

## Notes

## Cross-references

- See `../../../../docs/devlog/SKILL_GRAPH.md` for the collection-level view.


## Skills in this domain

- [skaileup](./skaileup/) — Use when starting or resuming the full concept pipeline for a new product. Runs Discovery → Experience → Blueprint with checkpoint approvals
- [skaileup-build](./skaileup-build/) — Use when concept is complete and you want to build the entire application end-to-end. Drives the full pipeline from scaffold through feature
- [skaileup-scope-scope-project](./skaileup-scope-scope-project/) — Use when the user starts a new project and no _concept/_meta/scope.yaml exists yet, or when re-scoping (--tier= override). Picks one of mvp 
