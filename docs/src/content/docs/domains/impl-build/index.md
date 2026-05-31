---
title: "impl-build"
description: "One-time / project-level: scaffold · foundation · infrastructure · migrate · seed · generate · docs"
sourcePath: "skaileup/impl-build/DOMAIN.md"
sidebar:
  label: "Overview"
  order: 0
---


# impl-build

One-time, project-level setup tasks that run before feature slices begin. Agents use this domain to take a completed concept to a working, runnable codebase.

## Skills

- **impl-build-scaffold** (`scaffold/`) — Creates the project directory, runs stack scaffold commands, initializes git, writes `_implementation/` tracking.
- **impl-build-foundation** (`foundation/`) — Applies brand tokens → CSS variables, auth setup, and app shell layout; configures Storybook. Writes to `src/`.
- **impl-build-infrastructure** (`infrastructure/`) — Implements custom backend modules, provider abstractions, and communication infra (WebSocket, SSE) from `_concept/blueprint/architecture.md`.
- **impl-build-migrate** (`migrate/`) — Generates ORM migration files (Prisma, Drizzle, Directus, raw SQL) from `model.dbml` + `model.json`.
- **impl-build-seed** (`seed/`) — Generates independently runnable seed scripts for each scenario in `seed.json` (empty, single_user, populated, edge_cases).
- **impl-build-generate** (`generate/`) — PostXL-only: runs generators from `postxl-schema.json`, resolves merge conflicts via four-level cascade, verifies build.
- **impl-build-docs** (`docs/`) — After any coding step: detects git-changed files, checks Starlight doc accuracy via `_sources` frontmatter, rewrites stale sections.

## When to Use

- Starting a greenfield project from a finished concept (`stack.md` exists, no `src/` yet).
- Tech stack is decided and `impl-architecture` artifacts are present in `_concept/blueprint/`.
- Running `standard-app` or `complex-app` flow (scaffold → foundation → infrastructure → migrate → seed precede the first impl-slice).
- After any coding step that may have drifted docs (triggers `impl-build-docs`).

## When NOT to Use

- Feature implementation — use `impl-slice` instead.
- Concept is incomplete or `stack.md` is missing — run `impl-architecture` first.
- `impl-build-generate` when the stack is not PostXL.

## Sequence

```
scaffold → foundation → [infrastructure] → migrate → seed → [generate]
                                                            ↓
                                              (impl-slice begins here)
```

`impl-build-docs` re-runs after each coding step, not once at the end.

## Cross-references

- `../impl-architecture/` — produces `stack.md`, `architecture.md`, `model.dbml` that this domain reads.
- `../impl-slice/` — consumes the runnable project this domain produces.
- `../contracts/semantic_types.md` — used by `impl-build-migrate` for type translation.


## Skills in this domain

- [impl-build-docs](./impl-build-docs/) — Use after completing an implementation step to verify and update Starlight documentation. Detects git-changed files, resolves which doc page
- [impl-build-foundation](./impl-build-foundation/) — Use after scaffold and before feature implementation to apply the three foundational layers every app needs: brand tokens → CSS variables, a
- [impl-build-generate](./impl-build-generate/) — Use when the project uses the PostXL tech stack and you need to regenerate code or resolve merge conflicts after a schema change or custom a
- [impl-build-infrastructure](./impl-build-infrastructure/) — Use when architecture.md defines custom_modules or processes beyond the standard stack. Sets up custom NestJS/backend modules, provider abst
- [impl-build-migrate](./impl-build-migrate/) — Use after the data model is finalized and before feature implementation to generate database migration files. Reads model.dbml + model.json 
- [impl-build-scaffold](./impl-build-scaffold/) — Use when a concept is complete and no project directory exists yet. Reads stack.md, uses the stack profile for scaffold commands and convent
- [impl-build-seed](./impl-build-seed/) — Use after migrate to generate executable seed scripts from seed.json. Covers all seed scenarios (empty, single_user, populated, edge_cases);
