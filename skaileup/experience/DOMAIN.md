---
name: experience
description: "journeys · behaviors · screens · components"
metadata:
  stage: alpha
  type: domain
---

# experience

Models the user experience layer: journeys, interaction behaviors, screens, and the components that compose them.

## Skills

- **experience-journeys** (`journeys/`) — Maps user journeys from the approved brief; defines personas and story maps organized by stage (hero, vital, hygiene, backlog) and writes `stories.json` with EARS acceptance criteria.
- **experience-behaviors** (`behaviors/`) — Formalizes behavioral rules, state machines, and entity lifecycle once features are approved.
- **experience-screens** (`screens/`) — Writes per-screen specifications organized in numbered groups; registers screens back into feature frontmatter via the feedback loop.
- **experience-screens-technical** (`screens-technical/`) — Technical variant of `screens` with precise component-level breakdowns. Experimental — not in the default pipeline.
- **experience-components** (`components/`) — Reusable component inventory; identifies shared UI patterns across screens and maps them to the tech stack's component library.

## Cross-references

- See `../../../docs/devlog/SKILL_GRAPH.md` for the catalog-level view.
