---
title: "experience"
description: "journeys · behaviors · screens · components"
sourcePath: "skaileup/experience/DOMAIN.md"
sidebar:
  label: "Overview"
  order: 0
---


# experience

Produces the full UX specification layer — personas, story maps, behavioral rules, screen layouts, and a shared component inventory — that sits between product features and implementation. Agents use this domain after features are approved and before mockup or implementation begins.

## Skills

- **experience-journeys** (`journeys/`) — Maps personas and story maps from the approved brief; writes `_concept/experience/journeys/stories.json` with EARS acceptance criteria staged hero/vital/hygiene/backlog.
- **experience-behaviors** (`behaviors/`) — Formalizes entity state machines and lifecycle rules per feature group; writes `_concept/experience/behaviors/<group>.allium` (one file per feature group).
- **experience-screens** (`screens/`) — Writes per-screen specs from approved features; outputs `_concept/experience/screens/00_layout/shell.md` and `_concept/experience/screens/<NN_group>/<screen>.md`; registers screens back into feature frontmatter.
- **experience-components** (`components/`) — Identifies shared UI patterns across all screens; writes `_concept/experience/screens/components/<name>.md` per reusable component, mapped to the tech stack's component library.
- **experience-screens-technical** (`screens-technical/`) — Component-level technical variant of `screens`. Experimental — not in the default pipeline.

## When to Use

- Features are approved (`_concept/experience/features/`) and you need UX artifacts before mockup or implementation.
- User says "map journeys", "write screen specs", "behavioral rules", or "component inventory".
- Concept pipeline is running at `simple-app` tier or higher (journeys + screens are standard; behaviors optional).
- Entering an impl-slice and the screen spec for that feature is missing.

## When NOT to Use

- Brief is not yet approved — run `concept-brief` and `product-spec-features` first.
- MVP tier: skip this domain; go directly to mockup-walkthrough.
- Screens already exist and only need patching — use `mockup-feedback` instead.

## Sequence

```
experience-journeys  →  experience-behaviors (optional)  →  experience-screens  →  experience-components
```

`journeys` is optional input for `screens` but recommended. `behaviors` can run in parallel with `screens`. `components` requires `screens` to be complete.

## Cross-references

- `../product-spec/` — `features` artifact is the hard gate for `behaviors`, `screens`, and `components`.
- `../design/` — `brand-identity` and `tokens.json` are consumed by `screens`.
- `../impl-architecture/` — `techstack.md` and `datamodel/model.json` are consumed by `screens-technical`.
- `skaileup/contracts/concept_structure.md` — canonical `_concept/` path rules.


## Skills in this domain

- [experience-behaviors](./experience-behaviors/) — Use when features are approved and user wants to formalize behavioral rules, state machines, or entity lifecycle. Also when user says 'behav
- [experience-components](./experience-components/) — Use when screen specs exist and you need to identify shared UI patterns (data tables, forms, cards, navigation) across screens. Maps compone
- [experience-journeys](./experience-journeys/) — Use after project brief is approved to map user journeys. Reads the approved brief, goals, and optional research to define personas and stor
- [experience-screens](./experience-screens/) — Use when features are approved and you need per-screen specifications. Produces grouped screen docs; registers back into feature frontmatter
- [experience-screens-technical](./experience-screens-technical/) — Technical variant of the screens skill with component inventories. Use when screen specs exist and require precise component-level breakdown
