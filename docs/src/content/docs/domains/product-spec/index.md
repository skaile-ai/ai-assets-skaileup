---
title: "product-spec"
description: "features · acceptance criteria"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`skaileup/product-spec/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/product-spec/DOMAIN.md)
:::


# product-spec

Translates approved user journeys into a structured feature set with acceptance criteria, roles, and permissions. Agents use this domain after journeys are approved and before screens or datamodel work begins.

## Skills

- **product-spec-features** (`features/`) — Derives features from `_concept/experience/journeys/stories.json` and the project brief; writes one `.md` per feature under `_concept/experience/features/<NN_group>/`.

## When to Use

- `_concept/experience/journeys/stories.json` exists and is approved
- User says "define features", "what should the app do", or "plan functionality"
- Orchestrator dispatches this step after the journeys phase
- Expanding or reprioritizing an existing feature set

## When NOT to Use

- No approved brief or journeys yet — run `concept-brief` and `experience-journeys` first
- User wants to design screens — run `experience-screens` (requires features to exist)
- User wants to define the data model — run `impl-architecture-datamodel` (requires features to exist)
- Adding a single new feature to an approved concept — use `ops-add-feature` instead

## Sequence

```
experience-journeys (stories.json approved)
        ↓
product-spec-features   →  _concept/experience/features/<NN_group>/<feature>.md
        ↓                        ↓
experience-screens       impl-architecture-datamodel
  (back-fills screens[])   (back-fills data_entities[])
```

## Cross-references

- `../contracts/concept_structure.md` — valid `_concept/` paths and naming rules
- `../contracts/frontmatter.md` — required frontmatter fields for feature files
- `../contracts/feedback_loop.md` — how downstream skills back-fill `screens[]` and `data_entities[]`
- `../experience/` — journeys domain (prerequisite)
- `../SKILL_GRAPH.md` — collection-level dependency map


## Skills in this domain

- [product-spec-features](./product-spec-features/) — Use after user journeys are approved to plan features. Derives features from stories.json candidate hints and the project brief. Writes feat
