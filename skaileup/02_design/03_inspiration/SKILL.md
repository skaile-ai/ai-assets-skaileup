---
name: design-inspiration
description: "Use on appbuilder-standard / appbuilder-complex concepts after brand-visual, to collect concrete visual references — layout patterns, color/typography directions, component patterns — that ground downstream screens and mockups. Reads the chosen brand tokens and comparables, then writes _concept/_grounding/research/design-inspiration.md per the design-inspiration-v1 schema."
metadata:
  version: '1.0.0'
  stage: alpha
  tags:
    - 'design'
    - 'inspiration'
    - 'references'
    - 'layout'
    - 'color'
    - 'typography'
    - 'component-patterns'
  source: 'PHASE3'
  parameters:
    depth:
      type: enum
      values: [none, light, medium, max]
      default: medium
  artifacts:
    requires:
      - id: brand-tokens
        gate: hard
    produces:
      - id: research-design-inspiration
        description: 'Layout, color, typography, and component reference collection'
    consumes:
      - id: comparable
        gate: soft
  prerequisites:
    files:
      - path: '_concept/discovery/brand/tokens.json'
        gate: hard
        description: 'Inspiration is collected in service of the already-chosen brand direction'
    reads:
      - path: '_concept/discovery/brand/identity.md'
        description: 'Aesthetic direction the references must stay consistent with'
      - path: '_concept/discovery/comparable.md'
        description: 'Reference apps whose patterns are worth borrowing'
      - path: '_concept/_grounding/research/design-inspiration.md'
        description: 'Deep design research (if grounding-research ran) — deepen rather than overwrite'
    produces:
      - path: '_concept/_grounding/research/design-inspiration.md'
        description: 'Layout patterns, color references, typography references, component patterns'
---

# Design Inspiration — Visual Reference Collection

## Overview

The **inspiration** skill collects concrete visual references — layout patterns,
color and typography directions, and component patterns — that give downstream
`experience-screens` and the mockup skills something specific to design against.
It runs *after* `design-brand-visual` so the references stay consistent with the
already-chosen tokens, and writes `_concept/_grounding/research/design-inspiration.md`
following the `design-inspiration-v1` schema. It is the interview-driven path to
the same artifact `concept-grounding-research` produces autonomously.

## When to Use

- `_concept/discovery/brand/tokens.json` exists, tier is appbuilder-standard or appbuilder-complex
- The user wants reference patterns captured before screens are designed
- The orchestrator dispatches this after `design-brand-visual` in the high-level pass

## When NOT to Use

- appbuilder-mvp / appbuilder-simple — inspiration is optional; brand tokens are enough to start
- No brand tokens yet — run `design-brand-visual` first
- API-only service with no UI — skip design entirely

## Prerequisites

**REQUIRED BACKGROUND:** Read `contracts/concept_structure.md`,
`contracts/frontmatter.md`, and the `contracts/schemas/design-inspiration-v1.yaml`
schema before proceeding.

**Hard gate:** `_concept/discovery/brand/tokens.json` must exist.

## Context Budget

| Action           | Path                                              | Required |
| ---------------- | ------------------------------------------------- | -------- |
| Must read        | `_concept/discovery/brand/tokens.json`            | Yes      |
| Must read        | `contracts/schemas/design-inspiration-v1.yaml`    | Yes (output shape) |
| Check if present | `_concept/discovery/brand/identity.md`            | No (aesthetic direction) |
| Check if present | `_concept/discovery/comparable.md`                | No (borrowable patterns) |
| Check if present | `_concept/_grounding/research/design-inspiration.md` | No (deepen existing)  |
| Never load       | `experience/screens/`, `blueprint/`               | —        |

## Standalone Mode

**Gate check:** `_concept/discovery/brand/tokens.json` must exist.
**On completion:** Present the reference summary, suggest `experience-journeys` or `experience-screens` next.

---

ROLE Design inspiration agent — collects layout, color, typography, and component references consistent with the chosen brand, into `_concept/_grounding/research/design-inspiration.md`.

READS
\_concept/discovery/brand/tokens.json — chosen palette, type scale, spacing (references must stay consistent)
? \_concept/discovery/brand/identity.md — aesthetic direction and mood
? \_concept/discovery/comparable.md — reference apps with borrowable patterns
? \_concept/\_grounding/research/design-inspiration.md — deep research to deepen (if it ran)

WRITES
\_concept/\_grounding/research/design-inspiration.md — layout/color/typography/component references (design-inspiration-v1)

REFERENCES
contracts/concept_structure.md — valid \_concept/ paths
contracts/schemas/design-inspiration-v1.yaml — required output shape
contracts/frontmatter.md — required YAML fields

MUST conform to the design-inspiration-v1 schema (references_collected, last_updated, and the four reference arrays)
MUST keep every reference consistent with the chosen brand tokens — no off-palette or off-type suggestions
MUST cite a source for each reference (app name, URL, or comparable entry)
MUST record applicability — where in this product each pattern would be used
MUST deepen an existing design-inspiration.md rather than discarding it
NEVER invent reference URLs — use named sources or the user's comparables; mark inferred patterns "general pattern"
NEVER restyle the brand — this collects references, it does not change tokens.json

EMIT [inspiration] started run_id=<uuid>

STEP 1: Gather context

- Read \_concept/discovery/brand/tokens.json — the palette, type scale, spacing the references must respect
- Read the design-inspiration-v1 schema for the exact output shape
- IF \_concept/discovery/brand/identity.md exists, read it for aesthetic direction
- IF \_concept/discovery/comparable.md exists, mine it for borrowable layout/component patterns
- IF \_concept/\_grounding/research/design-inspiration.md exists, read it — deepen it

STEP 2: Collect references (interview where needed)

- Ask the user for apps/sites whose look they admire, if not already known from comparables
- For each kind, gather references that fit the chosen brand:
  - **Layout patterns** — page structures, navigation models, density
  - **Color references** — palettes/moods consistent with tokens.json
  - **Typography references** — pairings and usage consistent with the type scale
  - **Component patterns** — cards, tables, forms, empty states worth modeling
- For each reference capture: source, the pattern, and where it applies in this product

EMIT [inspiration] checkpoint phase=references_collected count=<N>

STEP 3: Write design-inspiration.md

- $ mkdir -p \_concept/\_grounding/research

OUTPUT \_concept/\_grounding/research/design-inspiration.md
---
references_collected: <N>
last_updated: <YYYY-MM-DD>
layout_patterns:
  - source: "<app|url|comparable>"
    pattern: "<the layout/navigation pattern>"
    applicability: "<where in this product>"
color_references:
  - source: "<source>"
    palette: "<palette consistent with tokens.json>"
    mood: "<mood/tone>"
typography_references:
  - source: "<source>"
    fonts: "<pairing consistent with the type scale>"
    usage: "<headings|body|data>"
component_patterns:
  - source: "<source>"
    component: "<card|table|form|empty-state|…>"
    notes: "<what to model, what to adapt>"
---
## Notes
<Narrative tying the references back to the brand direction and the product's screens.>

STEP 4: Human approval
CHECKPOINT inspiration_approved
Show the reference summary grouped by kind. > "Do these references match the direction you want? Approve to continue, or tell me what to add or drop."

UNTIL user explicitly approves
- Apply changes, show updated references, ask again

STEP 5: Hand off

> "Design inspiration captured. Next steps:
>
> - Run `experience-journeys` to map the core flows
> - Run `experience-screens` — it will design against these references
> - Or continue the orchestrator pipeline"

EMIT [inspiration] completed run_id=<uuid> artifacts=_grounding/research/design-inspiration.md references=<N>

CHECKLIST

- [ ] \_concept/\_grounding/research/design-inspiration.md exists and conforms to design-inspiration-v1
- [ ] references_collected count matches the entries
- [ ] every reference cites a source and an applicability
- [ ] all references are consistent with tokens.json
- [ ] an existing design-inspiration.md was deepened, not discarded

---

## Depth Behavior

| Depth    | Behavior                                                                       |
| -------- | ------------------------------------------------------------------------------ |
| `none`   | Skip — brand tokens alone are enough for downstream screens                    |
| `light`  | Layout + color references only, 2-3 each                                       |
| `medium` | All four reference kinds, a few entries each (default)                         |
| `max`    | Exhaustive per-screen reference set + annotated moodboard notes                |

## Common Mistakes

| Mistake                                  | What to do instead                                             |
| ---------------------------------------- | ------------------------------------------------------------- |
| Suggesting off-palette colors            | Every color reference must be consistent with tokens.json.    |
| Inventing reference URLs                 | Use named sources/comparables; mark inferred ones "general pattern". |
| Re-running deep design research          | If `_grounding/research/design-inspiration.md` exists, deepen it. |
| Changing the brand                       | This collects references; tokens.json is owned by brand-visual. |
| No applicability                         | Every pattern names where in the product it would be used.    |

## Integration

- **Called by:** `concept-orchestrator` (high-level pass on standard/complex) or standalone
- **Requires:** `_concept/discovery/brand/tokens.json` (from `design-brand-visual`)
- **Feeds into:** `experience-screens` and the mockup skills, which design against these references
