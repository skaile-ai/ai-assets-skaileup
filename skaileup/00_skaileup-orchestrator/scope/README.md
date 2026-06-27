---
name: skaileup-scope
description: "Project-size scoping — interviews user, picks tier, drives flow selection."
metadata:
  stage: alpha
  type: domain
---

# skaileup/scope

Project-size scoping cluster: interviews the user, picks a tier (appbuilder-mvp / appbuilder-simple / appbuilder-standard / appbuilder-complex), and drives flow selection. First action in the skaileup pipeline.

## Skills

- **skaileup-scope-scope-project** (`scope-project/`) — Picks one of appbuilder-mvp / appbuilder-simple / appbuilder-standard / appbuilder-complex from a one-sentence project description and writes `_concept/_meta/scope.yaml`. Gates which flow runs next.

## Cross-references

- See `../../../../docs/devlog/SKILL_GRAPH.md` for the collection-level view.
