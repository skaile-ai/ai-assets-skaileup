---
title: "impl-architecture-templates"
description: "stack-specific scaffold templates · selector entry point: impl-architecture-templates-select"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`skaileup/impl-architecture/templates/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/impl-architecture/templates/DOMAIN.md)
:::


# impl-architecture/templates/

Stack-specific scaffold templates. Each subdirectory is a concrete `SKILL.md` describing one stack's scaffold conventions (file layout, package manifest, dev-stack commands, foundation steps, recommended UI library).

The catalog references this cluster via the **selector** skill `impl-architecture-templates-select` (Phase 3 deferred — see `flows/_meta/deferred_skills.yaml`). At runtime the selector reads `_concept/_meta/scope.yaml` + `_concept/blueprint/techstack.md` and resolves to exactly one of the concrete templates below.

## Concrete templates

- **template-postxl** (`template-postxl/`) — PostXL full-stack template (FastAPI + Vue + PostgreSQL).
- **template-nextjs-radix** (`template-nextjs-radix/`) — Next.js App Router + Radix UI primitives.
- **template-nextjs-shadcn** (`template-nextjs-shadcn/`) — Next.js App Router + shadcn/ui components.
- **template-nuxt-minimal** (`template-nuxt-minimal/`) — Nuxt 3 minimal scaffold (no UI library).
- **template-nuxt-primevue** (`template-nuxt-primevue/`) — Nuxt 3 + PrimeVue.
- **template-nuxt-ui** (`template-nuxt-ui/`) — Nuxt 3 + Nuxt UI.
- **template-sveltekit-minimal** (`template-sveltekit-minimal/`) — SvelteKit minimal scaffold (no UI library).

## Naming exception

Per `CONTRIBUTING.md`, these skills use the shortened form (`name: template-postxl`, etc.) instead of the path-based `impl-architecture-templates-template-postxl`. The cluster's selector skill — `impl-architecture-templates-select` — uses path-based naming because it is a regular Phase 3 skill, not a template profile.

## Cross-references

- `../../../SKILL_GRAPH.md` § 6 — tier-composition table (`impl-arch/templates-select`)
- `../../contracts/skill_grammar.md` — SKILL.md DSL
- `../techstack/SKILL.md` — discovers the available stacks from this directory and recommends one
- `../../flows/_meta/deferred_skills.yaml` — selector is currently deferred to Phase 3


## Skills in this domain

- [impl-architecture-datamodel](./impl-architecture-datamodel/) — Use when features are approved but _concept/blueprint/datamodel/ is empty. Produces model.dbml (DBML), model.json (editor canvas), seed.json
- [impl-architecture-system](./impl-architecture-system/) — Use after features and techstack are approved to document system architecture. Produces architecture.md with system overview, backend struct
- [impl-architecture-techstack](./impl-architecture-techstack/) — Use when the project brief exists and tech stack hasn't been chosen. Discovers available stacks from impl-architecture/profiles/, asks plain
- [template-nextjs-radix](./template-nextjs-radix/) — Reference document and invocable skill for the Next.js 15 + Radix UI + Directus stack. Read by scaffold, foundation, design, mock, and story
- [template-nextjs-shadcn](./template-nextjs-shadcn/) — Reference document and invocable skill for the Next.js 15 + shadcn/ui + Supabase stack. Read by scaffold, foundation, design, mock, and stor
- [template-nuxt-minimal](./template-nuxt-minimal/) — Reference document and invocable skill for the Nuxt 4 + Tailwind + Drizzle + SQLite stack. Read by scaffold, foundation, design, mock, and s
- [template-nuxt-primevue](./template-nuxt-primevue/) — Reference document and invocable skill for the Nuxt 4 + PrimeVue 4 + Directus stack. Read by scaffold, foundation, design, mock, and storybo
- [template-nuxt-ui](./template-nuxt-ui/) — Reference document and invocable skill for the Nuxt 4 + @nuxt/ui v3 + Directus stack. Read by scaffold, foundation, design, mock, and storyb
- [template-postxl](./template-postxl/) — Reference document and invocable skill for the PostXL platform stack (React 19 + Vite + NestJS + Prisma + Keycloak). Read by scaffold, found
- [template-sveltekit-minimal](./template-sveltekit-minimal/) — Reference document and invocable skill for the SvelteKit 2 + Svelte 5 + Tailwind + Drizzle + SQLite stack. Read by scaffold, foundation, des
