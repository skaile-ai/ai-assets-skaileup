---
name: concept-reverse
description: "Use when the code already holds a fact the concept needs, or a repository exists and the concept has to be extracted from it rather than designed. Reads the routes, screens, schema, stack, brand, interaction surfaces and docs of the requested scope, and writes what the code actually says as graded, freshness-stamped findings the owning skills seed from. Triggers on 'reverse engineer this project', 'extract the concept from this codebase', 'document this existing app', 're-read the screens from the code'."
version: "0.2.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
    - contract:@skaile-ai/app-design-rulebook
  artifacts:
    requires: []
    produces:
      - { id: grounding-findings, path: "_concept/02_grounding/findings/" }
  prerequisites:
    files: []
    inputs_optional:
      - { id: scope, label: "Scope", type: text, hint: "One or more of routes, screens, datamodel, interaction, brand, stack, brief; empty means all seven" }
      - { id: paths, label: "Path filter", type: text, hint: "Source globs to re-read, e.g. app/pages/inbox*; empty means the whole app" }
      - { id: repo_path, label: "Repository path", type: text, hint: "Defaults to the project root" }
      - { id: app_hint, label: "What does this app do?", type: text, hint: "Only needed when the README is thin" }
---

# concept-reverse

Reads an existing repository for the requested scope and paths and writes down what it actually is,
as graded findings and nothing else. It runs whole, one scope, or one path filter, and any skill's
derive step may call it (`tree/02_grounding/findings/README.md § Scopes and freshness`); the
artifacts that seed from the findings are written by their owners, never here.

## Route

Read `tree/README.md` once per session, then the nodes of the requested scopes — each holds the format and procedure for its part; this file holds only the order. A scope absent from the request is skipped and listed as `skip: not requested`.

1. **Resolve the request and extract** — `tree/02_grounding/findings/README.md § Extracting (concept-reverse)`: scope and paths, the app, the freshness of each existing file, then one file per requested scope, the citation check and the report.
2. **`brief`** — `tree/02_grounding/findings/brief-seeds.md`.
3. **`stack`** — `tree/02_grounding/findings/stack.md`.
4. **`brand`** — `tree/02_grounding/findings/brand.md`.
5. **`routes`** — `tree/02_grounding/findings/routes.md`.
6. **`screens`** — `tree/02_grounding/findings/screens.md`.
7. **`datamodel`** — `tree/02_grounding/findings/datamodel.md`.
8. **`interaction`** — `tree/02_grounding/findings/interaction.md`; its `§ Where UI sits per stack` holds the recipes shared with `quality-interaction`, and the P14–P17 rows cite `rulebook/rules.md`.
9. **Catalogue them** — `tree/02_grounding/findings/index.md`, one row per written file with `step: concept-reverse`.

**Done when** each requested scope's findings file exists in `02_grounding/findings/`, is listed in `findings/index.md`, carries `scope`, `paths`, `source_sha` (the current `git rev-parse HEAD`) and `last_updated`, every value in it carries a confidence grade, and every cited path resolves on disk; files of other scopes are untouched.
