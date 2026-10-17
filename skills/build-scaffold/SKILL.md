---
name: build-scaffold
description: "Use when the stack is chosen and no project exists yet — runs the template's scaffold recipe, then themes it, wires auth and builds the app shell, leaving a running app to build features into. Triggers on 'scaffold', 'bootstrap the project', 'set up the repo', 'create the app'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brief }
      - { id: techstack }
      - { id: brand-tokens }
      - { id: screens }
    produces: []
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: hard }
      - { path: "_concept/10_blueprint/techstack.md", gate: hard }
      - { path: "_concept/03_brand/brand.tokens.json", gate: soft }
      - { path: "_concept/07_screens", gate: soft, min_entries: 1 }
      - { path: "_concept/10_blueprint/openapi.yaml", gate: soft }
      - { path: "_concept/10_blueprint/asyncapi.yaml", gate: soft }
      - { path: "APP-DESIGN.md", gate: soft }
---

# build-scaffold

Takes an empty directory to a running, themed, authenticated, navigable app by walking the chosen template's recipe sections in order: `## Scaffold Recipe`, `## CSS Variables / Theming`, `## Auth Setup`, `## App Shell`. The recipe belongs to the template; the order, the checkpoints and the verification are this skill's. Read `tree/README.md` once per session.

It stops at the shell: no schema or seed data (`build-database`), no feature code (`build-plan` cuts it, `build-implement` builds it), no plan or status file (order is the flow graph, completion is git, so the scaffold's record is its commit), and no Storybook — the one in `_concept/09_mockup/storybook/` belongs to the mockup domain (`tree/09_mockup/storybook/README.md`), and an app that wants its own gets it as ordinary build work behind the template's `## Storybook Config`.

## Steps

1. **Resolve the stack and read its atoms by name.** `_concept/10_blueprint/techstack.md` (`tree/10_blueprint/techstack.md`) names `tech_stack_skill`; `templates/<that id>/TEMPLATE.md` carries `scaffold_command`, `package_manager`, `project_structure`, `build_command`, `lint_command`, `type_check_command` and `env_setup_command` under `metadata.atoms`. Every template declares every atom with a value or an explicit `null`, and a `null` is the answer: `env_setup_command: null` means the scaffolder ships no `.env.example` and the env file's contents are recipe material under `## Scaffold Recipe`; `lint_command: null` means step 8 has one less check. `tech_stack_skill: custom` means no template — take each command from `techstack.md` and confirm it with the user before running it.
2. **Confirm before creating anything.** App name and slug from `_concept/brief.md`, the resolved scaffold command verbatim, the directory it runs in, and what this run will not do (no database, no seed data, no features). After the scaffolder runs, changing the stack means deleting the tree.
3. **Run `## Scaffold Recipe` end to end.** The `scaffold_command` in the empty directory, dependencies with `package_manager`, then the recipe's remaining steps in order — config files, environment files, the directories it names. Check the result against `project_structure`; a layout that came out different means a flag was dropped, and the next three sections are written against the intended layout.
   - Where `_concept/10_blueprint/openapi.yaml` exists (`tree/10_blueprint/openapi.md`), write one route or handler stub per operation, at the path and method it documents, answering `501` until a slice builds it, and derive request validation from the operation's parameter and body schemas. Where `_concept/10_blueprint/asyncapi.yaml` exists (`tree/10_blueprint/asyncapi.md`), do the same for each channel's handler. Without them the stack's own example routes stay. The contract is `architecture-system`'s: a path or schema that needs to change goes back to it and is not edited here.
   - When this run created the project, write one line in the root `AGENTS.md` (create it if absent) telling coding agents to read `APP-DESIGN.md` for the interaction rules, if that file exists (`tree/APP-DESIGN.md`). A directory that already held a project keeps its `AGENTS.md` and `CLAUDE.md` untouched; say that the link is missing instead.
4. **Commit the scaffold on the build branch.** `build-branch` opens `build/<app-slug>` when the flow runs it; find that branch and commit onto it. When there is none (`appbuilder-mvp` has no branch step), initialize the repo if needed and cut `build/<app-slug>` here, so a generated project never lands unreviewed on the default branch.
5. **Theme it — `## CSS Variables / Theming`.**
   - With `_concept/03_brand/brand.tokens.json` present, flatten it to CSS custom properties per `tree/03_brand/brand.tokens.md § Flattening to CSS` and wire the section's theme variables to those, so every colour, font, radius, spacing value and shadow traces to a token. Where `_concept/03_brand/brand.dark.tokens.json` exists its tokens become the dark block (`tree/03_brand/brand.tokens.md § Light and dark`); without it the app has one mode. Import fonts from the provider the font tokens name, and read `_concept/03_brand/identity.md` (`tree/03_brand/identity.md`) for atmosphere.
   - Without tokens (`appbuilder-mvp` runs no brand step), take the stack's own defaults from that section and tell the user which defaults you took and how to replace them later. Do not refuse to run, and do not invent hex values.
6. **Wire auth — `## Auth Setup`.** Config files, plugins and middleware, packages and the role mapping, at the locations the section gives. Roles come from the `permissions:` blocks under `_concept/05_features/` (`tree/05_features/README.md`); where the auth feature has no spec yet, leave placeholder logic with a TODO naming the feature that will replace it. Credentials come from the environment, never a literal in a config file.
7. **Build the app shell — `## App Shell`.** Layout at the location the section names; navigation carrying every screen under `_concept/07_screens/`, plus active state, the icons the screen specs name and mobile collapse. `_concept/07_screens/shell.md` (`tree/07_screens/shell.md`) is the spec when it exists; without it, derive the nav from the screen directories rather than typing items by hand.
8. **Verify, then show it.** Run `build_command`, plus `lint_command` and `type_check_command` wherever they are not `null`, until all pass. Start the app and walk it with the user: the shell renders, the theme is applied, the nav reaches every screen, the login page loads. Approve, or name what to change and fix it here. Then land steps 5 to 7 as one commit each, so a bisect can separate a broken theme from a broken shell.

**Done when** the app builds and runs, its theme traces to tokens or to a named stack default, its nav covers every screen spec, and the scaffold plus one commit per section are on `build/<app-slug>`.
