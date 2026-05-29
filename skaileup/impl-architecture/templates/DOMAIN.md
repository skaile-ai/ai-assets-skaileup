---
name: impl-architecture-templates
description: "stack-specific scaffold templates · selector entry point: impl-architecture-templates-select"
metadata:
  stage: alpha
  type: cluster
---

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

- `../../../../../docs/devlog/SKILL_GRAPH.md` § 6 — tier-composition table (`impl-arch/templates-select`)
- `../../contracts/skill_grammar.md` — SKILL.md DSL
- `../techstack/SKILL.md` — discovers the available stacks from this directory and recommends one
- `../../flows/_meta/deferred_skills.yaml` — selector is currently deferred to Phase 3
