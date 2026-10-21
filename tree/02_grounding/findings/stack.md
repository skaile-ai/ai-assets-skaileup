---
path: _concept/02_grounding/findings/stack.md
summary: the platform, frameworks, database and tooling the manifests declare
owner: [concept-reverse]
may_propose: []
---

# _concept/02_grounding/findings/stack.md

The stack the repository actually uses. `architecture-techstack` seeds its choice from it and
asks about every value; the chosen template still has to be scored and approved there.

## Format

Frontmatter per `tree/02_grounding/findings/README.md`, with one graded field per dimension:
`platform`, `frontend`, `ui_library`, `backend`, `database`, `orm`, `auth`, `hosting`,
`package_manager`. The body carries what no field holds: version constraints that will bite (a
major pinned below current, a peer-dependency conflict), unusual combinations that look
deliberate (two ORMs, a second frontend framework in one package), and anything CI does that
the manifests do not explain.

## Writing it

Read the root manifest (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`,
`composer.json`, `Gemfile`) and its lock file, then the framework config files, the Dockerfile
and `docker-compose.yml`, the CI workflow files and `.env.example`, stopping on a dimension once
a manifest declares it. A dependency in `dependencies` is a stronger signal than the same name in
`devDependencies`, which is stronger than a mention in a config comment.

| dimension | where it is declared |
|---|---|
| `platform` | Dockerfile base image, CI runner image, deployment config |
| `frontend` | `nuxt`, `next`, `remix`, `astro`, `@sveltejs/kit`, or `vite` plus `react` / `vue` |
| `ui_library` | `@nuxt/ui`, `shadcn-ui`, `@radix-ui/*`, `primevue`, `vuetify`, `@mantine/core`, `@chakra-ui/react`, `tailwindcss` |
| `backend` | `express`, `fastify`, `hono`, `koa`, `@nestjs/core`, `django`, `fastapi`, `flask`, `rails`, `laravel` |
| `database` | `pg`, `mysql2`, `sqlite3`, `mongodb` — and the ORM below usually names it too |
| `orm` | `@prisma/client`, `drizzle-orm`, `typeorm`, `mongoose`, `sequelize`, `sqlalchemy` |
| `auth` | `next-auth`, `lucia`, `passport`, `@auth0/nextjs-auth0`, `better-auth`, `@supabase/supabase-js`, a Keycloak client |
| `hosting` | `vercel.json`, `netlify.toml`, `railway.json`, `fly.toml`, or the deploy step in CI |
| `package_manager` | `bun.lockb` → bun · `pnpm-lock.yaml` → pnpm · `yarn.lock` → yarn · `package-lock.json` → npm |

Grading: `extracted` when a manifest or config names it; `inferred` when only an import or
directory convention implies it — a `server/api/` tree with no server framework in the manifest
is a framework-provided server, which is worth saying rather than guessing at; `needs_review`
when the dimension has no signal, because an empty graded field beats a plausible default that
gets built on.

## Checks

All nine dimensions are present and graded.
