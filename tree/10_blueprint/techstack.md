---
path: _concept/10_blueprint/techstack.md
summary: chosen technologies, resolved to one template id; no third-party services
owner: [architecture-techstack]
may_propose: []
---

# _concept/10_blueprint/techstack.md

The project's technology choice, resolved to exactly one template. `tech_stack_skill` is the single field every later skill resolves: `templates/<that string>/TEMPLATE.md` supplies the scaffold commands, theming, auth and ORM recipes to `build-scaffold` and `build-database`, so the abstract choice and the concrete template are one decision under one approval. The template set, its atoms and its section headings are described in `templates/README.md`.

## Format

```yaml
---
platform: web | mobile | desktop | api
framework: ""                   # e.g. PostXL, Laravel, Rails, custom
frontend: ""                    # e.g. Vite + React 19
ui_library: ""                  # e.g. @postxl/ui-components, shadcn/ui
backend: ""                     # e.g. NestJS + Fastify + tRPC
orm: ""                         # e.g. Prisma, TypeORM, Drizzle, Ecto
database: ""                    # e.g. PostgreSQL, SQLite
auth: ""                        # e.g. Keycloak, Auth.js, custom
package_manager: ""             # e.g. pnpm, bun, npm
tech_stack_skill: ""            # the winning template's directory name, or `custom`
last_updated: YYYY-MM-DD
---
```

`tech_stack_skill` is a directory name under `templates/`, or `custom` for no template, in which case `build-scaffold` takes every command from this file's prose. Body: a short section per axis saying why that choice fits this project, then `## Trade-offs Considered`, which is what a reader six months later opens this file for. Names and reasons only — a Prisma schema or a line of SQL here is `architecture-datamodel`'s output in the wrong file. Third-party services (payments, mail and SMS, file storage, analytics, error tracking, auth providers beyond the template's own) belong to `tree/10_blueprint/architecture.md`.

## Writing it

1. **Read the ground first.** `_concept/brief.md` for what is built and for whom; `_concept/01_meta/scope.yaml` for `flow` and `project_type`; every feature under `_concept/05_features/` that exists, for complexity signals; `_concept/02_grounding/onboarding/answers.json` for technology answers and their `confidence`. `project_type` sets which axes carry weight: `cli-tool`, `api-service`, `library` and `data-pipeline` grow no screens, so the UI-library axis is dead and the choice is a runtime and a data layer.
   - A `techstack.md` that already exists is a handed-off concept: read it back to the user and confirm it instead of re-running the selection, or everything downstream silently loses its basis.
   - When `_concept/02_grounding/findings/stack.md` exists (reverse flow), its graded values are proposals: show them, and step 3 asks about every one — an `extracted` value as a confirmation. The template still gets scored and approved here.
2. **Discover candidates at runtime.** Scan `templates/*/TEMPLATE.md`, reading only each `## Identity` table and `## When to Use`. The candidate set is whatever is on disk and the id is the directory name character for character; never write a list of ids into this file.
3. **Ask in plain language** (one decision batch per message — `tree/README.md § How a skill runs`): framework experience, web / mobile / desktop / API, how data-heavy the app is, CMS or admin panel, self-hosted or managed, budget. Skip every question an input already answered: a `locked` value in `answers.json` is honoured and not asked, a `preferred` one is offered as the default, an `open` one is recommended from and still asked. `appbuilder-mvp` settles this in a round or two; the other three flows work the whole list. Outside services are not asked here.
4. **Score every candidate on four weighted axes**: frontend framework ×3, UI library ×2, backend ×1, database ×1. Frontend dominates so a Nuxt project never lands on a Next template.
5. **Break ties on the flow** from `scope.yaml`. `appbuilder-mvp` takes the lighter `*-minimal` template; `appbuilder-standard`, `skaileup-concept-only` and `skaileup-concept-reverse` take the fuller UI-library one. Ties are the normal case because several templates share a frontend.
6. **A top frontend score of zero is an answer.** Report the gap, then offer the closest framework match or `tech_stack_skill: custom` (no template; `build-scaffold` works from this file alone with each command confirmed). A stack with no template is recorded as a gap in `templates/`.
7. **Approve stack and template together, once.** Show what the app will be built on in the user's language, with the technical line under it: frontend, UI library, backend, database, auth, the winning template id with its one-line identity, and the runner-up with the gap that lost. One id is on the table, not two.
8. **Check the id resolves, then write.** Run `test -d templates/<id>` before writing, since an id naming a missing directory fails at `build-scaffold` with nothing to fall back on. Then write the frontmatter, the per-axis sections and `## Trade-offs Considered`.

## Checks

- `tech_stack_skill` names a real `templates/` directory or `custom`.
- The user approved that one id.
- No third-party service and no schema appears in the file.
