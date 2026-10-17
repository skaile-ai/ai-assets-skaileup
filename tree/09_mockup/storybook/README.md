---
path: _concept/09_mockup/storybook/
summary: standalone Storybook of components, page compositions and journey click-dummies
writers: [mockup-storybook]
---

# _concept/09_mockup/storybook/

A standalone Storybook in three layers: custom components, full-page screen compositions, and one clickable click-dummy per user journey. It is a concept artifact, a surface for reviewing the design before the app exists. An app that wants its own Storybook gets it as ordinary build work behind the template's `## Storybook Config`; the two never share a directory. Nothing here is framework-specific except the six stack atoms step 1 resolves; layout, story titles, variant names and the page manifest are identical on every stack, and only the file extension moves (`story_extension`).

## Format

### Directory layout

```
_concept/09_mockup/storybook/
├── package.json
├── .storybook/{main,theme,preview}.<ts|js>
└── src/
    ├── styles/brand.css
    ├── @types/{README.md, <entity>.<ts|js>, index.<ts|js>}
    ├── components/{AppShell.<ext>, <ComponentName>.<ext>, index.<ts|js>}
    ├── pages/{<Group>/<PageName>.<ext>, manifest.json}
    └── stories/
        ├── Components/<ComponentName>.stories.<ext>
        ├── Pages/00 Layout/AppShell.stories.<ext>
        ├── Pages/<NN Group>/<PageName>.stories.<ext>
        └── Journeys/{Hero,Vital,Hygiene}/<FlowName>.stories.<ext>
```

`AppShell` lives in `components/`, not `pages/`: pages render inside it, so it is a building block that happens to be page-shaped.

### Group naming

A screen spec's directory segment carries a sort key and a label: `01_user_auth` → prefix `01`, label `User Auth`. Page components go to `src/pages/01_user_auth/`; their stories go to `src/stories/Pages/01 User Auth/` (space, not underscore: Storybook renders the folder name in the sidebar).

### Story titles

| Layer | Title |
|---|---|
| Components | `Components/<ComponentName>` |
| App shell | `Pages/00 Layout/AppShell` |
| Pages | `Pages/<NN> <GroupName>/<PageName>` |
| Journeys | `Journeys/<Stage>/<JourneyLabel>` |

Component stories carry the `autodocs` tag. Page and journey stories set `layout: 'fullscreen'`.

### Named variants

| Layer | Exports |
|---|---|
| Component | `Default`, `AllVariants`, plus `WithData` / `Empty` / `Loading` where the component supports them |
| AppShell | `DesktopExpanded`, `DesktopCollapsed`, `Mobile` |
| Page | one per state the screen spec lists (`Default`, `Populated`, `Empty`, `Loading`, `Error`, …), plus `Mobile` and `Tablet` |
| Journey | a single `Interactive` story |

A component that appears in several screens with different configurations gets one variant per configuration. Story data is realistic and domain-appropriate, drawn from `10_blueprint/datamodel/seed.json` scenarios where a data model exists and from the screen spec's own examples otherwise; lorem ipsum reads as an unfinished screen and hides the layout questions the review exists to answer.

### `src/pages/manifest.json`

One entry per screen spec, keyed by the spec's path relative to `_concept/`:

```json
{
  "07_screens/01_user_auth/login.md": {
    "component": "01_user_auth/Login",
    "import": "./src/pages/01_user_auth/Login",
    "route": "/login"
  }
}
```

The journeys layer resolves each journey's walkthrough-manifest `screen_sequence` through this file (the story map's `candidate_screens` when no manifest exists); a screen missing from it falls back to matching on route or purpose against the screen specs.

### The click-dummy pattern

One `Interactive` story per journey, built only from existing page components and `AppShell`:

- Track the current step in framework-local reactive state; render the matching page component as AppShell's content.
- Wire the advance on **real** UI: a nav item, an action button, a link the screen spec already declares. The journey tests whether the design's own affordances carry a person through the flow, so an added Prev/Next control would answer the wrong question.
- Highlight the active nav item for the current step and show a banner with the persona name, `Step N of M` and the step description.
- When the reader clicks something that does not advance, add a `click-hint` class to the elements that do and drop it after about three seconds: a dead click with no feedback reads as a broken prototype.
- Let the data reflect progression: after a "create project" step, the next screen shows that project.
- Reuse the interfaces in `src/@types/`; keep per-step data inline in the story file.

## Writing it

Where the screens come from: `mockup-walkthrough` already resolved the screen set and every journey's screen sequence into `_concept/09_mockup/walkthrough/<renderer>/manifest.json` (`<renderer>` is the subdirectory holding it; shape in `tree/09_mockup/walkthrough/README.md § Manifest schema`). Read it first and take `screens[]` (`screen_path`, `screen_id`, `elements[]`) and `journeys[]` (`journey_id`, `screen_sequence`) from it, so this skill and the walkthrough cannot disagree about what a screen or journey is. The manifest carries no state lists, persona or stage; those still come from the screen spec and from `stories.yaml`, found by `journeys[].source`. No manifest yet: read `07_screens/*/*.md` (one level; `shell.md` is not a screen) and `stories.yaml` directly, and say in the report that the walkthrough was not built first.

1. **Resolve the stack and read its atoms by name.** `10_blueprint/techstack.md` names `tech_stack_skill`; `templates/<that id>/TEMPLATE.md` carries `storybook_addon`, `story_format`, `story_extension`, `component_import`, `component_library`, `icon_library` and `package_manager` under `metadata.atoms`. Every template declares every atom with a value or an explicit `null`, and `null` is the answer, not a missing one: `component_library: null` means the stack ships none, so step 3's split puts every element on the custom side, and `icon_library: null` means inline the SVGs. Confirm the set with the user before scaffolding, because a wrong addon surfaces at the end of step 6 after every story is written against it. Carry the atoms as the only stack-shaped values in the run; every later step names an atom, not a framework.
2. **Scaffold, when `_concept/09_mockup/storybook/package.json` is absent.** Write the project files listed in `skills/mockup-storybook/references/scaffold.md`: `package.json` on the resolved addon, `.storybook/main`, `theme` and `preview`, and `src/styles/brand.css`; then install with the resolved package manager and confirm `run build` passes before writing a single story. Every colour, font, radius and spacing value comes from `03_brand/brand.tokens.json` (flattened per `tree/03_brand/brand.tokens.md § Flattening to CSS`) and viewport presets come from `07_screens/shell.md`, so the prototype agrees with the brand it exists to show. Already present: leave it alone and go to step 3, because the scaffold is the user's by then.
3. **Build the components layer.** Take the deduplicated union of `elements[]` across the manifest's screens (the screen specs' `UI Elements` sections when there is no manifest). Split it against what the component library actually exports, read from the installed package's type declarations, into *library* elements (pages import them directly; no story) and *custom* elements (you build them). Show both lists and confirm the split before building. For each custom element write the component under `src/components/`, a minimal interface under `src/@types/` covering only the properties it renders, and a story under `src/stories/Components/`. Where `10_blueprint/datamodel/seed.json` exists, source the `WithData` and `Empty` variants from its `populated` and `empty` scenarios, so stories and later tests share one fixture. Finish with the `src/components/index` barrel, which step 4 imports from; an empty barrel with a comment is the right output when the library covered everything.
4. **Build the pages layer.** `AppShell` first, from `07_screens/shell.md`, with nav items derived from the shell spec: it is the frame every page renders inside, so a page built before it gets composed twice. Then one page component and one story per manifest screen, with a named variant for every state the spec lists and `Mobile` / `Tablet` variants alongside. Close with `src/pages/manifest.json` mapping each screen spec path to its component and route; step 5 reads it to turn a `screen_sequence` into imports.
5. **Build the journeys layer**, when the manifest lists journeys or `04_journeys/stories.yaml` exists. Journeys come from `journeys[]`: `screen_sequence` gives the steps and the story map at `source` gives stage, persona and step descriptions. One story per `hero`, `vital` and `hygiene` story map; `backlog` maps are out of scope by stage, and there is exactly one hero. Each is a single interactive story per § The click-dummy pattern: navigation happens through the real nav items and action buttons, because a walkthrough with its own navigation is no evidence the design's navigation works. Mark the hero flow as the default story. No `stories.yaml`: note the skipped layer in the project README, naming what to run.
6. **Verify.** `run build` from the storybook directory, then count the story files per layer and report the three counts with the command that opens the result. A build that fails here is fixed here, since a Storybook nobody can start is not reviewable.

## Checks

`run build` passes; every screen spec has a page story, every custom component has a component story, and every non-backlog story map has a journey story.
