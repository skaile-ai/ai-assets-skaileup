---
title: "concept"
description: "brief · goals · comparable"
sourcePath: "skaileup/concept/DOMAIN.md"
sidebar:
  label: "Overview"
  order: 0
---


# concept

Produces the discovery artifacts that ground all downstream concept and implementation work: a brief, articulated goals, comparables, and a grounding profile. Agents use this domain at the start of every pipeline run, before design or implementation begins.

## Skills

- **concept-brief** (`brief/`) — Dialog-driven capture of project idea, goals, and comparables; writes `_concept/discovery/brief.md`, `goals.md`, `comparable.md`.
- **concept-goals** (`goals/`) — Focused success-criteria pass for standard/complex tiers; deepens `_concept/discovery/goals.md` with measurable KPIs, constraints, and non-goals.
- **concept-comparable** (`comparable/`) — Focused reference-apps pass for standard/complex tiers; deepens `_concept/discovery/comparable.md` with borrow/avoid lessons and the positioning gap (distills `_grounding/research/competitors.md` if present).
- **concept-grounding-onboard** (`grounding/onboard/`) — Collects project identity, tier preference, and tech decisions; writes `_concept/_grounding/onboarding/profile.yaml` and `decisions.yaml`.
- **concept-grounding-research** (`grounding/research/`) — Research mode (runs in parallel): competitors, audiences, design inspiration, domain analysis; writes into `_grounding/research/` and `_grounding/findings/index.md`.
- **concept-grounding-seeds** (`grounding/seeds/`) — Scans `_seeds/`, classifies files, maps them to artifact slots, updates `_concept/concept.yaml` seeds section.

## When to Use

- No `_concept/discovery/` exists and the user describes a new idea or project.
- User says "start from scratch", "new project", "I have an app idea", or wants to redefine an existing brief.
- A concept pipeline is starting and no grounding profile (`profile.yaml`) is present yet.
- Existing `_seeds/` material needs to be classified and wired into the concept.

## When NOT to Use

- `_concept/discovery/brief.md` already exists and the user wants to move forward — go to `design/` or `product-spec/`.
- The user is adding a feature to an existing concept — use `concept-slice/` or `ops/add-feature`.
- Grounding data is already complete — skip `grounding/` skills and use existing artifacts directly.

## Sequence

```
concept-grounding-onboard
  └── concept-grounding-seeds     (if _seeds/ present)
  └── concept-grounding-research  (parallel, any time)
concept-brief
  └── concept-goals        (standard/complex high-level pass — deepen goals.md)
  └── concept-comparable   (standard/complex high-level pass — deepen comparable.md)
```

## Cross-references

- `grounding/DOMAIN.md` — sub-domain detail for the three grounding skills.
- `../design/DOMAIN.md` — next domain after concept is complete.
- `../contracts/` — iron laws and artifact schemas every skill reads.


## Skills in this domain

- [concept-brief](./concept-brief/) — Use when starting a new concept and no _concept/discovery/ exists, or when the user says 'I have an app idea', 'new project', 'start from sc
- [concept-comparable](./concept-comparable/) — Use on standard-app / complex-app concepts after brief and goals exist, when reference apps deserve their own focused pass beyond the light 
- [concept-goals](./concept-goals/) — Use on standard-app / complex-app concepts after the brief is approved, when goals deserve their own focused pass beyond the light version c
- [concept-grounding-onboard](./concept-grounding-onboard/) — Use when starting a new concept pipeline and project identity, tier, and technology decisions have not been captured yet. Collects these thr
- [concept-grounding-research](./concept-grounding-research/) — Use when grounding decisions in real-world data — competitor analysis, audience research, design inspiration, behavioral patterns, color/fon
- [concept-grounding-seeds](./concept-grounding-seeds/) — Use after concept-grounding-onboard when the user has provided existing material in _seeds/. Scans and auto-classifies each file by content 
