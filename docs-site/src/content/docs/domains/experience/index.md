---
title: "experience"
description: "journeys · behaviors · screens · components"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`experience/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/experience/DOMAIN.md)
:::


# experience

Models the user experience layer: journeys, interaction behaviors, screens, and the components that compose them. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **experience-journeys** (`journeys/`) — Maps user journeys from the approved brief; defines personas and story maps organized by stage (hero, vital, hygiene, backlog) and writes `stories.json` with EARS acceptance criteria.
- **experience-behaviors** (`behaviors/`) — Formalizes behavioral rules, state machines, and entity lifecycle once features are approved.
- **experience-screens** (`screens/`) — Writes per-screen specifications organized in numbered groups; registers screens back into feature frontmatter via the feedback loop.
- **experience-screens-technical** (`screens-technical/`) — Technical variant of `screens` with precise component-level breakdowns. Experimental — not in the default pipeline.
- **experience-components** (`components/`) — Reusable component inventory; identifies shared UI patterns across screens and maps them to the tech stack's component library.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.


## Skills in this domain

- [experience-behaviors](./experience-behaviors/) — Use when features are approved and user wants to formalize behavioral rules, state machines, or entity lifecycle. Also when user says 'behav
- [experience-components](./experience-components/) — Reusable component inventory. Use when screen specs exist and you need to identify shared UI patterns (data tables, forms, cards, navigation
- [experience-journeys](./experience-journeys/) — Use after project brief is approved to map user journeys. Reads the approved brief, goals, and optional research to define personas and stor
- [experience-screens](./experience-screens/) — Use after features are approved to write screen specifications. Reads features, optional brand/techstack/datamodel/journeys artifacts, and p
- [experience-screens-technical](./experience-screens-technical/) — Technical variant of the screens skill with component inventories. Use when screen specs exist and require precise component-level breakdown
