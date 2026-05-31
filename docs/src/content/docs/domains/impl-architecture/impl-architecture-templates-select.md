---
title: "impl-architecture-templates-select"
description: "Use after techstack.md exists to resolve the abstract stack decision to exactly one concrete scaffold template (template-postxl, template-nextjs-shadcn, template-nextjs-radix, template-nuxt-ui, template-nuxt-primevue, template-nuxt-minimal, template-"
sourcePath: "skaileup/impl-architecture/templates-select/SKILL.md"
sidebar:
  label: "impl-architecture-templates-select"
---

:::note[Skill manifest]
**Name:** `impl-architecture-templates-select`
**Stage:** alpha · **Version:** 1.0.0
**Tags:** templates, scaffold, stack-selection, selector, techstack, architecture
:::


# Templates Select — resolve the concrete scaffold template

## Overview

The **techstack** skill decides the *abstract* stack (frontend framework, UI
library, backend, database). **templates-select** is the runtime chooser that
maps that decision onto exactly one of the concrete scaffold templates under
`impl-architecture/templates/template-*/`. Downstream skills (`scaffold`,
`foundation`, `design`, the mockup and storybook skills) read
`impl-architecture/templates/<tech_stack_skill>/TEMPLATE.md` — so this skill's
only job is to set `tech_stack_skill` to a real `template-*` directory id.

## When to Use

- `_concept/blueprint/techstack.md` exists and `tech_stack_skill` is unset, or
  set to an abstract value (e.g. `nextjs`) that is not a `template-*` id
- The orchestrator dispatches this immediately after `techstack` is approved
- The user wants to re-pick the scaffold template without redoing the stack

## When NOT to Use

- No `techstack.md` yet — run **techstack** first
- `tech_stack_skill` already names a real `template-*` directory and is approved
- The user has an existing codebase — use **reverse-engineer** instead

## Prerequisites

**REQUIRED BACKGROUND:** Read `contracts/concept_structure.md` and
`contracts/frontmatter.md` before proceeding.

**Hard gate:** `_concept/blueprint/techstack.md` must exist.

## Context Budget

| Action           | Path                                                   | Required                 |
| ---------------- | ------------------------------------------------------ | ------------------------ |
| Must read        | `_concept/blueprint/techstack.md`                      | Yes                      |
| Must read        | `impl-architecture/templates/template-*/TEMPLATE.md`   | Yes (candidate discovery)|
| Check if present | `_concept/_meta/scope.yaml`                            | No (tier weighting)      |
| Never load       | template bodies beyond the Identity table              | —                        |

---

ROLE Template selector — scores the concrete scaffold templates against the
approved stack and writes the single best match back as `tech_stack_skill`.

READS
\_concept/blueprint/techstack.md — frontend, ui_library, backend, database, tech_stack_skill
impl-architecture/templates/template-\*/TEMPLATE.md — candidate templates (discovered at runtime)
? \_concept/\_meta/scope.yaml — tier (mvp|simple-app|standard-app|complex-app) for weighting

WRITES
\_concept/blueprint/techstack.md — tech_stack_skill set to the chosen template-\* id

REFERENCES
contracts/concept_structure.md — valid \_concept/ paths
contracts/frontmatter.md — techstack.md frontmatter fields
impl-architecture/templates/DOMAIN.md — the template cluster and its naming exception

MUST discover candidate templates from impl-architecture/templates/template-\*/TEMPLATE.md at runtime — never hardcode the list
MUST score on frontend first, then ui_library, then backend + database
MUST write tech_stack_skill as a real template-\* directory id that exists on disk
MUST get user confirmation before writing — the template fixes scaffold commands for the whole build
NEVER invent a template-\* id that has no directory
NEVER overwrite an already-approved concrete tech_stack_skill without showing a diff

EMIT [templates-select] started run_id=<uuid>

STEP 1: Read the stack decision

- Read `_concept/blueprint/techstack.md` frontmatter: `frontend`, `ui_library`,
  `backend`, `database`, and any existing `tech_stack_skill`
- IF `tech_stack_skill` already names an existing `template-*` directory
  - > "techstack.md already targets [id]. Re-pick the scaffold template?"
  - UNLESS the user wants to re-pick, skip to STEP 5 (no change)
- Check `_concept/_meta/scope.yaml` for `tier` (default: standard-app)

EMIT [templates-select] checkpoint phase=stack_read frontend=<value> ui=<value>

STEP 2: Discover candidate templates

- Scan `impl-architecture/templates/template-*/TEMPLATE.md`
- For each, read only the Identity table / description: framework, UI library,
  backend, database
- Build a candidate table. The collection currently ships:

  | template-\* id              | frontend       | ui library   | backend / data        |
  | --------------------------- | -------------- | ------------ | --------------------- |
  | `template-postxl`           | React 19 +Vite | (custom)     | NestJS + Prisma + PG  |
  | `template-nextjs-shadcn`    | Next.js 15     | shadcn/ui    | Supabase              |
  | `template-nextjs-radix`     | Next.js 15     | Radix UI     | Directus              |
  | `template-nuxt-ui`          | Nuxt 4         | @nuxt/ui v3  | Directus              |
  | `template-nuxt-primevue`    | Nuxt 4         | PrimeVue 4   | Directus              |
  | `template-nuxt-minimal`     | Nuxt 4         | (none)       | Drizzle + SQLite      |
  | `template-sveltekit-minimal`| SvelteKit 2    | (none)       | Drizzle + SQLite      |

  Treat the on-disk scan as authoritative — new templates may have been added.

STEP 3: Score and rank

- For each candidate, score:
  - frontend framework match — **weight 3** (a Nuxt stack never maps to a Next template)
  - ui_library match — **weight 2**
  - backend + database match — **weight 1 each**
- Tier tie-break from scope.yaml:
  - `mvp` / `simple-app` → prefer the lighter `*-minimal` template when frontend ties
  - `standard-app` / `complex-app` → prefer the fuller UI-library template
- IF the top frontend score is 0 (no framework matches the chosen frontend)
  - Do NOT force a pick. Report the gap and offer the closest framework match,
    or `tech_stack_skill: custom` (no template — scaffold runs from techstack.md alone)

EMIT [templates-select] checkpoint phase=ranked top=<template-id> score=<n>

STEP 4: Confirm with the user

CHECKPOINT template_approved
> "Your stack ([frontend] + [ui_library] + [backend]) maps best to:
>
> **[template-id]** — [one-line identity].
>
> Why: [framework match], [ui-library match], [tier fit].
> Runner-up: [second-id] ([gap]).
>
> Approve to lock the scaffold template, or pick another from the list."

UNTIL the user explicitly approves a template-\* id (or chooses `custom`)

STEP 5: Write the choice

- Update `tech_stack_skill` in `_concept/blueprint/techstack.md` frontmatter to
  the approved `template-*` id (or `custom`). Change nothing else.
- $ test -d impl-architecture/templates/<id> || echo "ERROR: no such template dir"

OUTPUT \_concept/blueprint/techstack.md (frontmatter field only)
tech_stack_skill: <template-\* id | custom>

STEP 6: Hand off

> "Scaffold template locked: [id].
>
> - `scaffold` will run its `scaffold_command` and lay out the project
> - `foundation` will apply the css/auth/app-shell recipes from its TEMPLATE.md
> - All downstream skills now resolve `templates/[id]/TEMPLATE.md`"

EMIT [templates-select] completed run_id=<uuid> tech_stack_skill=<template-id>

CHECKLIST

- [ ] impl-architecture/templates/template-\*/TEMPLATE.md was scanned at runtime
- [ ] frontend was the primary scoring axis
- [ ] chosen tech_stack_skill is an existing template-\* directory (or "custom")
- [ ] user explicitly approved the template
- [ ] only the tech_stack_skill field of techstack.md changed

---

## Depth Behavior

| Depth    | Behavior                                                                       |
| -------- | ------------------------------------------------------------------------------ |
| `none`   | Skip — leave tech_stack_skill as techstack wrote it                            |
| `light`  | Auto-pick the top frontend match, no runner-up explanation                     |
| `medium` | Score, show top + runner-up, confirm (default)                                 |
| `max`    | Full scoring table for all candidates with per-axis breakdown before confirm   |

## Common Mistakes

| Mistake                                        | What to do instead                                                       |
| ---------------------------------------------- | ------------------------------------------------------------------------ |
| Hardcoding the seven template ids              | Scan `templates/template-*/TEMPLATE.md` — the list can grow.             |
| Matching on UI library before framework        | Framework is weight 3; a Vue UI lib never lands you on a React template. |
| Writing an abstract value (`nextjs`)           | `tech_stack_skill` must be a real `template-*` directory id.             |
| Forcing a pick when no framework matches       | Offer closest match or `custom`; never map Svelte onto a Next template.  |
| Rewriting other techstack.md fields            | Touch only `tech_stack_skill`.                                           |

## Integration

- **Called by:** `concept-orchestrator` / `skaileup-build`, right after `techstack`
- **Requires:** `_concept/blueprint/techstack.md`
- **Feeds into:** `scaffold`, `foundation`, `design`, mockup + storybook skills —
  all resolve `impl-architecture/templates/<tech_stack_skill>/TEMPLATE.md`

