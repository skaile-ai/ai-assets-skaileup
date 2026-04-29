---
name: skaileup-grounding
description: 'All context-gathering before concept work: project identity dialog, web research, and seed file ingestion.'
type: domain
stage: alpha
version: 0.1.0
building_blocks:
  skills: 'skaileup-onboard, skaileup-research, skaileup-ingest-seeds'
  contracts: 'conceptualization-contract'
  docs: 'README.md'
  tools: 'n/a'
---

## Purpose

Gather all external context needed before concept definition begins. Three skills that answer: "What is this project, what does the market look like, and what material does the user already have?"

Merges the former `skaileup-onboard` (project identity dialog) and `skaileup-research` (web research) domains into a single bootstrap domain.

## Skills

| Skill                   | What It Does                                                            | When to Use                     |
| ----------------------- | ----------------------------------------------------------------------- | ------------------------------- |
| `skaileup-onboard`      | Project identity + tier dialog — collects name, problem, audience, type | First step of any new project   |
| `skaileup-research`     | Agentic web research — competitors, audiences, design patterns          | After onboard, before discovery |
| `skaileup-ingest-seeds` | Classify user-provided files into artifact slots                        | When user provides seed files   |

## Artifacts

**Reads from:** (nothing — this is the entry point)

**Writes to:**

- `_grounding/onboarding/profile.yaml`
- `_grounding/onboarding/decisions.yaml`
- `_grounding/research/*.md`
- `_grounding/seeds/`

## Notes

- Onboard must run before research (research uses profile.yaml for context)
- Seeds ingestion is optional — only runs if `_seeds/` directory exists
- The conceptualization contract in `contracts/` predates this reorganization and covers the full concept pipeline
