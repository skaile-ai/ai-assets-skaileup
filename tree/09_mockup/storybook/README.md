---
path: _concept/09_mockup/storybook/
summary: one Vue Storybook package — floorplans, screens, entities, the app, journeys
owner: [mockup-storybook]
may_propose: []
---

# _concept/09_mockup/storybook/

The one surface stakeholders review before the app exists: a Vue 3, Vite and Storybook 10 package on Nuxt UI 4, copied from `skills/mockup-storybook/references/scaffold/` and grown in five story layers — floorplans, screens, entities, the whole app, journeys. It is a concept artifact: the specs and the data model stay the source of truth, and nothing here is read as input by a spec skill. The package grows incrementally and is critiqued component by component, so a field the editor needs but the model lacks surfaces as a proposal in `model.ts` while the editor is drawn, and a stakeholder's note lands on the Vue file it was made on. An app that wants its own Storybook gets it as ordinary build work; the two never share a directory.

## Format

### Package layout

```
_concept/09_mockup/storybook/
├── package.json  tsconfig.json  vite.config.ts  vitest.config.ts  .gitignore  README.md
├── .storybook/{main.ts, preview.ts}
├── scripts/{inbox.ts, resolve.ts, gen-tokens.ts}
└── src/
    ├── styles/{main.css, tokens.css}              tokens.css is generated from 03_brand
    ├── floorplans/{<id>.vue, <id>.stories.ts, index.ts, floorplan.css, NavLink.vue}   the 16 rulebook floorplans
    ├── model/{store.ts, scenario.ts}              the in-memory store and the scenario list
    ├── components/{Field.vue, Screen.vue, StoryFrame.vue, field-types.ts, nav-types.ts, shell-context.ts}
    ├── app/{App.vue, Shell.vue, routes.ts, nav.ts, router.ts, App.stories.ts}
    ├── env.d.ts
    ├── screens/<screen_id>.vue + <screen_id>.stories.ts      one per 07_screens/<screen_id>.md
    ├── entities/<Entity>/{<Entity>Editor.vue, <Entity>Row.vue, *.stories.ts}
    └── journeys/<journey_id>.stories.ts
```

Everything outside `src/screens/`, `src/entities/`, `src/journeys/` and `src/app/nav.ts` ships with the scaffold, the 16 floorplans included, and is never hand-edited in a project; those four are the project's own and are written by `mockup-storybook`. `tokens.css`, `storybook-static/`, `node_modules/` and the type files Nuxt UI generates are gitignored.

### Story layers

| Layer | Title | One story per | Shows |
|---|---|---|---|
| Floorplans | `Floorplans/<id>` | rulebook floorplan | the regions and the `§ Responsive` behaviour of `rulebook/floorplans/<id>/README.md`, with neutral placeholders |
| Screens | `Screens/<screen_id>` | `07_screens/<screen_id>.md` | the screen's floorplan with its `regions:` filled from the seed |
| Entities | `Entities/<Entity>/<Component>` | state of an editor or display component | one `model.ts` entity |
| App | `App` | — | the whole app: shell, navigation and every screen over an in-memory router |
| Journeys | `Journeys/<journey_id>` | journey of `04_journeys/stories.yaml` | the App story started at the journey's first screen, a `play` function walking its steps |

Each layer is built from the one below it: a screen composes a floorplan, entity components fill its regions, the App routes the screens, a journey drives the App. A layer whose inputs do not exist yet is absent, never faked.

### Globals and state stories

| Global | Values | Effect |
|---|---|---|
| `scenario` | the keys of `seed.scenarios`, starting on `populated` when the seed has it, else its first key; `empty` alone when no seed exists | the store serves that scenario's rows |
| `fail` | `off`, `on` | the store rejects writes after a latency |
| `theme` | `light`, `dark` | toggles the `dark` class, so the `.dark` block of `tokens.css` applies |
| viewport | `narrow` (390 px), `wide` (1280 px) | the two breakpoints of the floorplans' `§ Responsive` |

An entity component gets one story per state: `Default`, `Empty` (`globals: { scenario: 'empty' }`), `Saving` (a `play` function submits and asserts the busy state), `Error` (`globals: { fail: 'on' }`) and `EdgeCases` (`globals: { scenario: 'edge_cases' }`). A screen story needs a state only for a situation its spec lists that these do not cover. The store is a `reactive()` object behind `provide` and `inject`: no network, no Pinia, and `save` is the only write.

### The data model

The package reads `_concept/10_blueprint/datamodel/model.ts` and `seed.ts` through the alias `@model` and has no generator of its own; the typed vocabulary and the generated files are in `tree/10_blueprint/datamodel/model.md § Format`. An entity component types its rows with `Infer<typeof Task>`, so a seed row or a field name that no longer fits the model fails `vue-tsc` and `tsc`. An empty project, with no model yet, still builds: the store falls back to the `empty` scenario.

When a component needs a field the model lacks, append it to its entity in `model.ts` with `proposed: { by: 'mockup-storybook', on: '<date>', source: '<why the editor needs it>' }`, run `gen.ts`, and use the field. The marker stays until `architecture-datamodel` promotes or rejects it (`tree/README.md § Ownership`). `model.ts` is never absent for an editor: when it does not exist, `mockup-storybook` creates it by the copy step of `tree/10_blueprint/datamodel/model.md § Writing it`, with the entities the first editor needs, all marked proposed.

### The one attribute

`Screen.vue` renders a screen's root with `data-screen="<screen_id>"`. It is the only `data-` attribute the package emits: journey `play` functions assert `[data-screen="<next screen>"]` after each step. What a note points at comes from the component chain, not from attributes.

## Annotation

Notes come from `@ecsplico/annotation-inbox`, wired the way the host wires it: `VueTracer()` and an inbox middleware in `.storybook/main.ts`, `mountAnnotationToolbar()` in `.storybook/preview.ts`. A stakeholder clicks an element in a running `storybook dev`, writes the note, and it lands in `<project>/.data/annotations/items/<sessionId>-<n>.json`, where `<project>` is the directory holding `_concept/`. The static `storybook build` has no toolbar: the mount asks the dev server first and stays silent without one.

An item carries what `mockup-feedback` reads (`tree/09_mockup/feedback/triage/README.md`):

| Field | Holds |
|---|---|
| `inboxId` | `<sessionId>-<n>`, the id a resolution names |
| `comment` | the stakeholder's text |
| `target.kind`, `target.ref` | `element` with `<path>:<line>:<col>` of the Vue file under `src/`, for an element written in our own template; `route` for a click on what a Nuxt UI component renders (a `UButton`, a `UInput`) |
| `vueComponents` | the component chain of the click; it names our component (`TaskEditor (src/entities/Task/TaskEditor.vue)`) even when `target.kind` is `route` |
| `url` | the Storybook iframe URL; its `id=` is the story id (`entities-task-taskeditor--default`) |
| `status` | `open`, `implemented` or `rejected` |

`src/entities/<Entity>/` maps a note to an entity, `src/screens/<screen_id>.vue` to a screen spec, a story id starting `journeys-` to a journey, and `src/floorplans/` to the rulebook; an entity directory that is not a `model.ts` entity id breaks that mapping. `npm run resolve -- --ids <id,id> --status implemented|rejected --resolution "<why>"`, run in the package directory, closes notes through the same inbox; `rejected` needs a resolution. `.data/` is local state, gitignored in the project and never an artifact; any agent reads it with the `annotation-inbox` skill.

## What the host serves

`storybook-static/`, the output of `npm run build-storybook`, uses relative asset paths and opens from a file or any static host. A host that shows mockups serves that directory, and one that runs `npm run storybook` shows the live stories with the annotation toolbar.

## Writing it

`mockup-storybook` runs the steps in order and skips a layer whose inputs do not exist, naming the missing input in its completion summary. Later runs add the layers whose inputs have appeared since. Nothing gates a step: a missing input is derived or asked for per `tree/README.md § How a skill runs`.

1. **Resolve the facts.** Read what exists: `03_brand/brand.tokens.json`, `07_screens/*.md` and `shell.md`, `10_blueprint/datamodel/model.ts` and `seed.ts`, `04_journeys/stories.yaml`, and the package itself when it exists. Take the screen list from the files under `07_screens/` (`shell.md` is not a screen), the journey list from the non-`backlog` stories, and the entity list from the exports of `model.ts`. Resolve the rest per `tree/README.md § How a skill runs`.
2. **Scaffold, when `_concept/09_mockup/storybook/package.json` is absent.** Copy `skills/mockup-storybook/references/scaffold/` into the directory unchanged, run `npm install` there and `npx playwright install chromium` once (the play functions run in it), then `npm run check`; confirm it passes before writing a story. A package that exists is left as it is: a stale copy is a question for the user, never an overwrite.
3. **Bring tokens and the model in.** The package writes `src/styles/tokens.css` from `03_brand/brand.tokens.json` (and `brand.dark.tokens.json`) on every dev, build and test start, as the `--ui-*` variables of Nuxt UI (`tree/03_brand/brand.tokens.md § Flattening to CSS` fixes the flattening); `npm run tokens` is the manual form. Without brand tokens Nuxt UI's defaults stay and the summary says so. When `model.ts` is absent and step 5 will need entities, create it per § The data model.
4. **Write a screen's layout story.** For each screen spec without a story, or the one named by the caller: `src/screens/<screen_id>.vue` places the screen's floorplan component (`floorplan:` in the spec) with `:chrome="!useInShell()"` so the shell is drawn once, fills each slot its `regions:` binds from the seed, leaves an unbound region as a neutral placeholder, and wraps the root in `Screen.vue`; `src/screens/<screen_id>.stories.ts` titles it `Screens/<screen_id>`. A caller that has no spec yet (`experience-screen` showing a layout before specifying) passes the screen id and the floorplan id instead, and every region is a placeholder until the spec binds it; when the package does not exist yet, step 2 runs first. Open the story at `narrow` and `wide` before reporting it. Worked example: `skills/mockup-storybook/references/screen-story.md`.
5. **Write the entity stories.** For each entity a screen binds in a region, or whose editor a screen's `### Actions` names: `src/entities/<Entity>/<Entity>Editor.vue` (a `UForm` of `Field` wrappers typed by `Infer`), `<Entity>Row.vue`, and one story per state. Every field the editor needs that the model lacks goes through § The data model as a proposal, and the completion summary lists each one. Worked example: `skills/mockup-storybook/references/entity-stories.md`.
6. **Write the App and the journeys.** The routes need no edit: `routes.ts` globs `src/screens/*.vue`, one route `/<screen_id>` each. Write `src/app/nav.ts` — the shell floorplan id named by `shell_frame:` in `07_screens/shell.md` and the `kind: nav` items of that file, in order (empty entries list every screen). Then one `src/journeys/<journey_id>.stories.ts` per non-`backlog` journey: the App story with `args.start` at the route of its first screen and a `play` function that follows `steps[]` through the real navigation, asserting `[data-screen="<screen_id>"]` after each. Worked example: `skills/mockup-storybook/references/journey-story.md`.
7. **Verify.** `npm run check` from the package directory builds, type-checks and runs the play functions; fix a failure here, since a Storybook nobody can start is not reviewable. Report the story count per layer and the command that opens the result.

## Checks

- `npm run check` exits 0 from `_concept/09_mockup/storybook/`.
- Every `07_screens/<screen_id>.md` has a `Screens/<screen_id>` story, and every entity a screen binds has a directory under `src/entities/`.
- Every non-`backlog` journey has a `Journeys/<journey_id>` story whose `play` function passes.
- A field an editor uses is in `model.ts`, `proposed` when `architecture-datamodel` has not confirmed it.
- No file under `floorplans/`, `components/`, `app/` (except `nav.ts`), `model/`, `scripts/` or `.storybook/` differs from the scaffold.
