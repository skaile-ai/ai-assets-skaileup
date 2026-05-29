---
name: concept
description: "brief · goals · comparable"
metadata:
  stage: alpha
  type: domain
---

# concept

Produces the discovery artifacts that ground all downstream concept and implementation work: a brief, articulated goals, comparables, and a grounding profile. Agents use this domain at the start of every pipeline run, before design or implementation begins.

## Skills

- **concept-brief** (`brief/`) — Dialog-driven capture of project idea, goals, and comparables; writes `_concept/discovery/brief.md`, `goals.md`, `comparable.md`.
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
```

## Cross-references

- `grounding/DOMAIN.md` — sub-domain detail for the three grounding skills.
- `../design/DOMAIN.md` — next domain after concept is complete.
- `../contracts/` — iron laws and artifact schemas every skill reads.
