---
name: skaileup-datamodel
description: "Data model definition: DBML, model.json, seed schema, feature map."
type: domain
stage: alpha
version: 0.1.0
building_blocks:
  skills: "skailup-datamodel"
  contracts: "n/a"
  docs: "n/a"
  tools: "n/a"
---

## Purpose

Define the data model — entities, relationships, seed schema, and feature-to-entity mapping. Separated from architecture because it has different inputs (reads features + techstack + architecture) and different consumers (migrate reads datamodel; scaffold reads architecture).

Extracted from the former `skaileup-blueprint` domain.

## Skills

| Skill | What It Does | When to Use |
|---|---|---|
| `skailup-datamodel` | Data model (DBML, model.json, seed schema, feature map) | After features + techstack are defined |

## Artifacts

**Reads from:**
- `_concept/experience/features/`
- `_concept/architecture/techstack.md` (soft)

**Writes to:**
- `_concept/datamodel/model.json`
- `_concept/datamodel/model.dbml`
- `_concept/datamodel/seed.json`
- `_concept/datamodel/feature_map.json`
