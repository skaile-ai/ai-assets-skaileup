---
name: skaileup-architecture
description: "Techstack selection and concept-level system architecture."
type: domain
stage: alpha
version: 0.1.0
building_blocks:
  skills: "skailup-techstack, skailup-architecture"
  contracts: "n/a"
  docs: "n/a"
  tools: "n/a"
---

## Purpose

Make the technical decisions that shape how the system will be built: which frameworks, which database, which auth strategy (techstack), and how modules/services/boundaries are organized (system architecture).

This is **concept architecture** — "what the system should look like." Implementation architecture ("how the code is organized") lives in `skaileup-build/` via scaffold and infrastructure skills.

Extracted from the former `skaileup-blueprint` domain.

## Skills

| Skill | What It Does | When to Use |
|---|---|---|
| `skailup-techstack` | Technology stack selection with reasoning | After brief + features are defined |
| `skailup-architecture` | System architecture: modules, services, boundaries | After techstack + features |

## Artifacts

**Reads from:**
- `_concept/discovery/brief.md`
- `_concept/experience/features/`
- `_grounding/research/*.md` (soft)

**Writes to:**
- `_concept/architecture/techstack.md`
- `_concept/architecture/system.md`
