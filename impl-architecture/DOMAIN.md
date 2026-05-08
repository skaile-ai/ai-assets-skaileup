---
name: impl-architecture
description: "techstack · system · datamodel · templates/"
metadata:
  stage: alpha
  type: domain
---

# impl-architecture

Defines the technical foundation: tech stack decisions, system architecture, data model, and reusable code templates. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **impl-architecture-techstack** (`techstack/`) — Discovers available stacks from `templates/`, asks plain-language questions, recommends the best match, and writes `stack.md`.
- **impl-architecture-system** (`system/`) — Documents system architecture: overview, backend structure, data flow, communication protocols, external integrations, infrastructure.
- **impl-architecture-datamodel** (`datamodel/`) — Produces `model.dbml` (DBML), `model.json` (editor canvas), `seed.json` (test scenarios), and `feature_map.json` (model-to-feature cross-reference).
- **templates/** — Cluster of 7 stack-specific scaffold templates (PostXL, Next.js + Radix/shadcn, Nuxt minimal/UI/PrimeVue, SvelteKit minimal). Selector `impl-architecture-templates-select` (Phase 3 deferred) picks one at runtime. See `templates/DOMAIN.md`.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.
