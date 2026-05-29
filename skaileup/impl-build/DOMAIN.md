---
name: impl-build
description: "One-time / project-level: scaffold · foundation · infrastructure · migrate · seed · generate · docs"
metadata:
  stage: alpha
  type: domain
---

# impl-build

Handles one-time and project-level build tasks: scaffolding, foundation setup, infrastructure, migration, seeding, code generation, and documentation.

## Skills

- **impl-build-scaffold** (`scaffold/`) — Scaffolds a new project from a completed concept; reads `stack.md`, runs the stack's scaffold commands, initializes git, and sets up `_implementation/` tracking.
- **impl-build-foundation** (`foundation/`) — Applies the three foundational layers every app needs before feature work: brand tokens → CSS variables, authentication, and app shell layout. Also seeds initial data and configures Storybook.
- **impl-build-infrastructure** (`infrastructure/`) — Sets up custom backend infrastructure from `architecture.md`: NestJS/backend modules, provider abstractions, additional processes, and communication infrastructure (WebSocket, SSE).
- **impl-build-migrate** (`migrate/`) — Generates database migrations from the data model for the target ORM (Prisma, Drizzle, Directus, raw SQL); translates semantic types via contracts.
- **impl-build-seed** (`seed/`) — Generates executable seed scripts from `seed.json` scenarios (empty, single_user, populated, edge_cases) for the chosen stack.
- **impl-build-generate** (`generate/`) — PostXL code generation and conflict resolution: runs PostXL generators from `postxl-schema.json`, auto-resolves merge conflicts via a four-level cascade, and verifies the build.
- **impl-build-docs** (`docs/`) — Verifies and updates Starlight documentation after an implementation step: detects git-changed files, resolves which doc pages cover them, checks accuracy, rewrites stale sections.

## Cross-references

- See `../../../docs/devlog/SKILL_GRAPH.md` for the catalog-level view.
