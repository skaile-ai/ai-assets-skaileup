---
name: concept-reverse
description: "Use when a repository already exists and the concept has to be extracted from it rather than designed. Reads the routes, screens, schema, stack, brand and docs, and writes what the code actually says as graded findings the owning skills seed from. Triggers on 'reverse engineer this project', 'extract the concept from this codebase', 'document this existing app'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: scope }
    produces:
      - { id: grounding-findings, path: "_concept/02_grounding/findings/" }
  prerequisites:
    files:
      - { path: "_concept/01_meta/scope.yaml", gate: soft }
    inputs_optional:
      - { id: repo_path, label: "Repository path", type: text, hint: "Defaults to the project root" }
      - { id: app_hint, label: "What does this app do?", type: text, hint: "Only needed when the README is thin" }
---

# concept-reverse

Reads an existing repository and writes down what it actually is, as graded findings and nothing
else. It is one node in a flow: `concept-brief`, `design-brand` and `architecture-techstack` seed
their drafts from the findings, and none of their artifacts is written here.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Extract and grade** — `tree/02_grounding/findings/README.md § Extracting (concept-reverse)`: confirm the repository, map it, write the six findings, verify citations, hand off.
2. **Write the six findings** — `tree/02_grounding/findings/brief-seeds.md`, `tree/02_grounding/findings/stack.md`, `tree/02_grounding/findings/brand.md`, `tree/02_grounding/findings/routes.md`, `tree/02_grounding/findings/screens.md`, `tree/02_grounding/findings/datamodel.md`. Each node holds its detection recipe.
3. **Catalogue them** — `tree/02_grounding/findings/index.md`, one row per file with `step: concept-reverse`.

**Done when** `brief-seeds.md`, `stack.md`, `brand.md`, `routes.md`, `screens.md` and `datamodel.md` exist in `02_grounding/findings/` and are listed in `findings/index.md`, every value in them carries a confidence grade, and every cited path resolves on disk.
