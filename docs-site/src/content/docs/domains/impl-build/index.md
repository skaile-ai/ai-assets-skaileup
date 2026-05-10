---
title: "impl-build"
description: "One-time / project-level: scaffold · foundation · infrastructure · migrate · seed · generate · docs"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`impl-build/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/impl-build/DOMAIN.md)
:::


# impl-build

Handles one-time and project-level build tasks: scaffolding, foundation setup, infrastructure, migration, seeding, code generation, and documentation. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **impl-build-scaffold** (`scaffold/`) — Scaffolds a new project from a completed concept; reads `stack.md`, runs the stack's scaffold commands, initializes git, and sets up `_implementation/` tracking.
- **impl-build-foundation** (`foundation/`) — Applies the three foundational layers every app needs before feature work: brand tokens → CSS variables, authentication, and app shell layout. Also seeds initial data and configures Storybook.
- **impl-build-infrastructure** (`infrastructure/`) — Sets up custom backend infrastructure from `architecture.md`: NestJS/backend modules, provider abstractions, additional processes, and communication infrastructure (WebSocket, SSE).
- **impl-build-migrate** (`migrate/`) — Generates database migrations from the data model for the target ORM (Prisma, Drizzle, Directus, raw SQL); translates semantic types via contracts.
- **impl-build-seed** (`seed/`) — Generates executable seed scripts from `seed.json` scenarios (empty, single_user, populated, edge_cases) for the chosen stack.
- **impl-build-generate** (`generate/`) — PostXL code generation and conflict resolution: runs PostXL generators from `postxl-schema.json`, auto-resolves merge conflicts via a four-level cascade, and verifies the build.
- **impl-build-docs** (`docs/`) — Verifies and updates Starlight documentation after an implementation step: detects git-changed files, resolves which doc pages cover them, checks accuracy, rewrites stale sections.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.


## Skills in this domain

- [impl-build-docs](./impl-build-docs/) — Use after completing an implementation step to verify and update Starlight documentation. Detects git-changed files, resolves which doc page
- [impl-build-foundation](./impl-build-foundation/) — Applies the three foundational layers every app needs before feature work: brand tokens → CSS variables, authentication setup, and app shell
- [impl-build-generate](./impl-build-generate/) — PostXL code generation and conflict resolution. Runs PostXL generators from postxl-schema.json, auto-resolves merge conflicts using a four-l
- [impl-build-infrastructure](./impl-build-infrastructure/) — Sets up custom backend infrastructure from the architecture doc. Implements custom NestJS/backend modules, provider abstractions (real + in-
- [impl-build-migrate](./impl-build-migrate/) — Generates database migrations from the data model. Reads model.dbml + model.json and stack.md, then generates migration files for the target
- [impl-build-scaffold](./impl-build-scaffold/) — Scaffolds a new project from a completed concept. Reads stack.md to determine the tech stack, uses the stack's profile for scaffold commands
- [impl-build-seed](./impl-build-seed/) — Generates seed scripts from seed.json. Reads seed.json scenarios (empty, single_user, populated, edge_cases) and generates executable seed s
