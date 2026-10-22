# 0026 — The mockup stage is one Vue Storybook package

**Status:** accepted

Replaces the four mockup surfaces of `_concept/09_mockup/` — early prototypes, the walkthrough
site, the template-resolved Storybook and the annotation overlay — with one package.
Amends [ADR 0020](0020-screens-are-independent-artifacts.md): the early prototype it offers
from a floorplan preview becomes the screen's layout story. Amends
[ADR 0022](0022-shared-artifact-contracts-and-proposed-entries.md): the data model a skill
proposes into is `model.ts`, and `model.json` is generated.

## Context

A prototype is useful when it grows by component, is critiqued component by component, and is
built in tandem with the data model, so that a missing field or a wrong entity surfaces while
the editor for that data is drawn rather than in the build. The four surfaces did not allow
that. `prototypes/` was static HTML with sample data, `walkthrough/` a second renderer with its
own manifest, `storybook/` a stack resolved per project from a template and gated on
`techstack.md`, and `mockup-annotate` an overlay coupled to the walkthrough through
`data-spec-*` attributes. A review note named a spec element and nothing about a component or a
model field, and no surface read the data model as typed code.

The host this collection is used from, `skaile-forge`, fixed several facts that the decision
rests on (read 2026-10, from the repositories):

- Forge is Nuxt 4, Vue 3 and Nuxt UI 4.11 with Storybook 10.6. Its `.storybook/main.ts` already
  wires `VueTracer()` and `annotationInbox({ endpoint: true })`.
- `@ecsplico/annotation-inbox` captures a component chain with `file:line:col` targets for Vue
  only: `runtime/inbox.ts` reads `__vueParentComponent` through `vite-plugin-vue-tracer`. A
  React app yields `target.kind: 'route'`, a note with no component.
- Forge lists and resolves notes from `<workspace>/.data/annotations`, shows them in its
  annotation list, hands them to agents over MCP, and the `annotation-inbox` and
  `annotation-watch` skills read the same store.
- Forge has no data-model editor, only a spec. It reads `model.json` over
  `GET /api/workspaces/:id/concepts/10_blueprint/datamodel/model.json` and reads no `seed.json`.
  Its TypeBox mirror `shared/schemas/datamodel.ts` is behind the tree's
  `datamodel-model.schema.json`: no `glossary_id`, no proposal markers.
- Forge shows prototypes by iframing `_concept/09_mockup/walkthrough/**/*.html`; its raw-file
  content types lack `.json` and `.woff2`. A `storybook build` output uses relative asset
  paths, so it is servable there after a small forge change.
- Forge derives a flow node's "done" from the node's `produces` paths existing on disk.
- Nuxt UI runs in a plain Vue and Vite app (`@nuxt/ui/vite`, `@nuxt/ui/vue-plugin`,
  tailwindcss, vue-router).

## Decision

**D1 — One Vue package, five story layers, Storybook as the only review surface.**
`_concept/09_mockup/storybook/` is a Vue 3.5, Vite, TypeScript, Storybook 10
(`@storybook/vue3-vite`) and Nuxt UI 4 package, copied verbatim from
`skills/mockup-storybook/references/scaffold/`. No template resolves it and no `techstack.md`
gates it. The stories are `Floorplans/<id>` (the 16 rulebook floorplans, shipped),
`Screens/<screen>`, `Entities/<Entity>/*`, `App` (the whole click-dummy in one story over an
in-memory router) and `Journeys/<id>` (the App story started at the journey's first screen,
with a `play` function walking its steps). Vue, because the host is Vue: the prototype uses the
component kit forge uses and reads like the product it previews, and the annotation package
locates a note to a source position only through Vue single-file components. `storybook build`
output is the shareable artifact.

**D2 — The data model is authored in TypeScript; `model.json`, `model.dbml` and `seed.json` are
generated.** `10_blueprint/datamodel/model.ts` is written with a typed DSL whose runtime,
`skaile-model.ts`, ships beside it, and `seed.ts` is typed against it, so a seed row that no
longer fits the model fails `tsc` — the early detector the prototype exists for. `gen.ts` writes
the three generated files. `model.json` stays the interchange contract with everything outside
the package: `build-database`, the end-to-end tests and forge. A skill in a node's `may_propose`
appends a field or entity with a `proposed: { by, on, source }` option directly in `model.ts`,
and the owner promotes it by removing the option. The package imports `model.ts` and `seed.ts`
relatively and carries no generator of its own.

**D3 — Behaviour prototyping is reduced to what earns its place.** Kept: seed scenarios as a
Storybook global, a `fail` global that makes the in-memory store reject writes after a latency,
one story per component state, play functions for journeys and editor flows run headless by
`@storybook/addon-vitest`. Dropped: MSW from `openapi.yaml` (the prototype never fetches), XState
from `06_behaviors/` (a state is a story), the Astro and static-HTML renderers, and the
walkthrough manifest (Storybook's `index.json` is the story list).

**D4 — Annotation is `@ecsplico/annotation-inbox`, wired as forge wires it, with no addon of
our own.** The package's Vite config adds `VueTracer()` and a small middleware that mounts the
inbox's HTTP handler over `openFileInbox(<project root>)`, so every note lands in
`<project>/.data/annotations/items/` as an `InboxItem` whose `target.ref` is
`<file>:<line>:<col>` of the Vue file the note points at. That is the store forge lists, agents
read over MCP, and `annotation-inbox` and `annotation-watch` already process. No overlay, no
`data-spec-*` attributes, no categories, no session files. The one attribute the package still
emits is `data-screen="<id>"` on a screen's root, for journey play functions.

**D5 — `mockup-walkthrough`, `mockup-annotate` and the `prototypes/` surface are deleted.**
`mockup-storybook` owns the package and runs incrementally: scaffold when absent, then every
layer whose inputs now exist. `experience-screen`'s early-prototype step calls
`mockup-storybook` to write the screen's layout story. `mockup-feedback` stays: it reads open
inbox items, routes them by target path, writes reviewable patches, and resolves each note
through the inbox. The greenfield flow's walkthrough and annotate nodes become one `storybook`
node.

## Options rejected

- **React, with the same Storybook.** Every note from a React prototype is a route-level note,
  so forge could show none of the component targeting the annotation package exists for.
- **`@storybook-vue/nuxt`, the host's own framework.** It needs a Nuxt app; the prototype is a
  component package, not an app, and forge-common's components are a Nuxt module.
- **A routed Vite app as the click-dummy, Storybook beside it.** Two dev servers and two review
  surfaces for one prototype. The full app runs inside the `App` story over a memory router, and
  nothing is lost.
- **`seed.json` imported by the TypeScript side.** An imported JSON file is not a fresh object
  literal, so a misspelled field would never raise an excess-property error; the seed stays
  authored in TypeScript for that reason.
- **The package's own `annotationInbox({ endpoint: true })` plugin.** It stores under
  `searchForWorkspaceRoot(process.cwd())/.data/annotations`, which for a nested package is the
  package itself. A project-rooted inbox needs the small middleware.
- **MSW and XState in the prototype.** They answer questions the prototype does not ask: it
  never fetches, and a state is a story.

## Consequences

- A project's prototype needs Node 20.19 or later, `npm install` in
  `_concept/09_mockup/storybook/` and, for headless play functions, a Playwright Chromium
  (about 150 MB). `npm run check` builds, type-checks and runs the play functions.
- `model.ts` is the one authored model; a hand edit of `model.json`, `model.dbml` or
  `seed.json` is overwritten by the next `gen.ts` run. The `editor` key of `model.json` is the
  one part `gen.ts` keeps from the existing file.
- Stakeholders annotate on a running `storybook dev`; the static build has no toolbar. Notes are
  local state under `.data/`, gitignored in the project and never an artifact.
- The directory `src/entities/<Entity>/` is load-bearing: triage maps a note's target file to an
  entity through it, and `src/screens/<screen_id>.vue` to a screen spec.
- Existing prototypes, walkthroughs and feedback session files are not migrated.
- The `mobile-app` project type keeps the stage: the viewport presets cover it.

## Host follow-ups (forge repository; the collection does not depend on them)

- Serve the built prototype: `WALKTHROUGH_DIR` in `server/utils/concept-tree.ts` points at
  `09_mockup/storybook/storybook-static`, and `RAW_CONTENT_TYPES` in
  `server/utils/concept-workspace.ts` gains `.json`, `.woff2` and `.map`. Live mode needs
  nothing: an agent's `npm run storybook` URL already opens in the chat.
- Progress of the stage: `mockup-storybook` lists `_concept/09_mockup/storybook/` in `produces`,
  so forge marks the node done once a file exists; finer progress (story counts per layer) can
  come from `storybook-static/index.json`.
- Sync `shared/schemas/datamodel.ts` with `datamodel-model.schema.json`: `glossary_id`,
  `status`, `proposed_by`, `proposed_on` and `source` on entity and field. A future canvas is a
  viewer of entities and the owner of `editor` only; its entity edits would be overwritten by
  the next generation.
- Optional upstream in `@ecsplico/annotation-inbox`: an `annotationInbox({ dir })` option, so a
  nested package can point the endpoint at the project root without the middleware.
