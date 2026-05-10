---
title: "concept-grounding"
description: "All context-gathering before concept work: project identity dialog, web research, and seed file ingestion."
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`concept/grounding/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/concept/grounding/DOMAIN.md)
:::


## Purpose

Gather all external context needed before concept definition begins. Three skills that answer: "What is this project, what does the market look like, and what material does the user already have?"

Merges the former `concept-grounding-onboard` (project identity dialog) and `concept-grounding-research` (web research) domains into a single bootstrap domain.

## Skills

| Skill                   | What It Does                                                            | When to Use                     |
| ----------------------- | ----------------------------------------------------------------------- | ------------------------------- |
| `concept-grounding-onboard`      | Project identity + tier dialog — collects name, problem, audience, type | First step of any new project   |
| `concept-grounding-research`     | Agentic web research — competitors, audiences, design patterns          | After onboard, before discovery |
| `concept-grounding-seeds` | Classify user-provided files into artifact slots                        | When user provides seed files   |

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


## Skills in this domain

- [concept-brief](./concept-brief/) — Use when starting a new concept and no _concept/discovery/ exists, or when the user says 'I have an app idea', 'new project', 'start from sc
- [concept-grounding-onboard](./concept-grounding-onboard/) — Collects project identity, complexity tier preferences, and technology decisions through a structured dialog. Produces profile.yaml and deci
- [concept-grounding-research](./concept-grounding-research/) — Use when grounding decisions in real-world data — competitor analysis, audience research, design inspiration, behavioral patterns, color/fon
- [concept-grounding-seeds](./concept-grounding-seeds/) — Scans the _seeds/ directory, auto-classifies each file by content analysis, maps files to artifact slots, validates against schemas, and upd
