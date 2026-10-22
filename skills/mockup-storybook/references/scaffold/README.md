# Component mockup (Storybook)

The clickable mockup of this project: Vue 3 + Nuxt UI 4 components in Storybook 10, over the data model in `_concept/10_blueprint/datamodel/`. Stakeholders and agents review it in the running Storybook and leave notes on it.

## Run

```sh
npm install
npx playwright install chromium   # once; the headless check below needs it
npm run storybook                 # http://localhost:6006
npm run check                     # storybook build, vue-tsc, then every story's play function in headless Chromium
npm run build-storybook           # static build in storybook-static/
```

Node 20.19 or newer. `npm run tokens` writes `src/styles/tokens.css` by hand; Storybook, the build and the check do it on every start anyway, and again when a brand token file changes.

## Layers

| Story title | Source | What it shows |
|---|---|---|
| `Floorplans/<id>` | `src/floorplans/<id>.vue` | the 16 rulebook floorplans with placeholder content |
| `Screens/<screen_id>` | `src/screens/<screen_id>.vue` | one screen of `_concept/07_screens/<screen_id>.md` |
| `Entities/<Entity>/<Component>` | `src/entities/<Entity>/` | an editor and a row component per data-model entity, one story per state: `Default`, `Empty`, `Saving`, `Error`, `EdgeCases` |
| `App` | `src/app/` | every screen inside the project's shell, switched by an in-memory router |
| `Journeys/<journey_id>` | `src/journeys/<journey_id>.stories.ts` | the `App` story opened at the journey's first screen, with a play function that walks the steps |

The folder `src/entities/<Entity>/` is named after the entity's id in `model.ts`; feedback triage maps a note to an entity through it. A screen's file name is its screen id; the screen's root is `<Screen id="<screen_id>">`, which emits `data-screen`, the one attribute the package adds, so play functions can assert navigation on it. A screen places its screen floorplan inside `Screen` and passes `:chrome="!inShell"` with `const inShell = useInShell()` (from `src/components/shell-context.ts`): alone in `Screens/<screen_id>` the floorplan draws its `shell` placeholder, inside `App` and `Journeys/*` the real shell frames it.

## Data

`@model/model` and `@model/seed` resolve to `_concept/10_blueprint/datamodel/model.ts` and `seed.ts`. Components import row types from there (`Infer<typeof Task>` from `@model/skaile-model`), so a field the model lacks fails `vue-tsc`, and a seed row that no longer fits the model fails it too. Without a data model the package still builds, with one empty scenario.

Toolbar globals: **Scenario** (the keys of `seed.scenarios`), **Writes** (`fail` makes every save of the fake store reject after a short delay), **Theme**, and the viewport presets `narrow` (390 px) and `wide` (1280 px). `useStore()` from `src/model/store.ts` gives components the active scenario's rows (`rows('task')`) and `save('task', row)`; call it at the top of `<script setup>`, not inside a `computed`.

## Notes on the mockup

Run `npm run storybook`, open the toolbar's pointer icon at the bottom right, click an element and write the note. Every note is written to `<project>/.data/annotations/items/<sessionId>-<n>.json` (the project is the directory holding `_concept/`), the same store forge lists and the `annotation-inbox` skill reads.

- A note on an element written in one of our own templates names it as `src/entities/Task/TaskEditor.vue:52:6`. A click on an element that a Nuxt UI component renders (a button, an input) names only the story's route, but the note's `vueComponents` still lists our components around it, which is what triage reads.
- `GET http://localhost:6006/__annotations?format=markdown` lists the open notes while Storybook runs.
- Close notes with `npx tsx scripts/resolve.ts --ids <inboxId>,<inboxId> --status implemented|rejected --resolution "<why>"` (`rejected` needs a reason). `mockup-feedback`'s `apply.py` runs this after its commit, for the notes the applied patches answered.
- The static build has no toolbar and no endpoint; annotate on `storybook dev`.
- `.data/` is local state: keep it out of git.

## Never hand-edit

- `src/styles/tokens.css`: generated from `_concept/03_brand/brand.tokens.json` (and `brand.dark.tokens.json`).
- `auto-imports.d.ts`, `components.d.ts`: written by Nuxt UI when Vite runs; type-checking therefore runs after the build in `npm run check`.
- `storybook-static/`, `node_modules/`.
- `_concept/10_blueprint/datamodel/skaile-model.ts` and `gen.ts`: tool files of the data model; the model is authored in `model.ts`, and `model.json`, `model.dbml`, `seed.json` are generated from it.

Written per project from the specs, not generated: `src/app/nav.ts` (the shell floorplan and its destinations, from `07_screens/shell.md`; empty means every screen is listed), `src/screens/`, `src/entities/`, `src/journeys/`.
