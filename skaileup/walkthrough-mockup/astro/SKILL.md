---
name: mockup-walkthrough-astro
description: "Use when stakeholders need a clickable Astro walkthrough of the application — built static site, Tailwind-styled, openable directly in a browser. Generates one HTML file per screen and per journey, plus a manifest.json that the mockup-feedback cluster reads. Best for standard-app tier."
metadata:
  version: "0.1.0"
  tags:
    - walkthrough
    - mockup
    - astro
    - tailwind
    - standard-app
    - frontend
    - prototype
    - data-spec
  stage: alpha
  prerequisites:
    files:
      - path: "experience/screens"
        gate: hard
        description: "Screen specs are the primary input — one HTML file rendered per screen"
        min_entries: 1
      - path: "experience/journeys/stories.json"
        gate: hard
        description: "Journey definitions drive the journey/<id>.html sequencing"
      - path: "design/tokens.json"
        gate: hard
        description: "Brand tokens injected as Tailwind CSS vars in the built shell"
      - path: "product-spec/features"
        gate: soft
        description: "Feature files linked from manifest.json for traceability; absence is a warning"
        min_entries: 1
    reads:
      - path: "experience/screens/00_layout/shell.md"
        description: "Optional shared layout reference; if present, used as reference for the Shell.astro wrapper"
  produces:
    - path: "_concept/mockup-walkthrough/astro"
      description: "Astro project source + built site: index.html, screen/<group>/<name>.html, journey/<id>.html, manifest.json"
---

# Walkthrough Mockup — Astro

## Overview

Astro-rendered variant of the walkthrough mockup cluster. Consumes the same
four inputs as `mockup-walkthrough-static-html` (screen specs, journey
definitions, brand tokens, feature files); produces a Tailwind-styled built
Astro static site at `_concept/mockup-walkthrough/astro/`.

Every rendered DOM node carries the same `data-spec-*` attributes as the
static-html variant so the `mockup-feedback-*` cluster can resolve clicks
identically across renderers. The `manifest.json` schema is identical —
only `renderer: "mockup-walkthrough-astro"` differs.

**Two-mode behaviour — decision recorded.** The agent detects whether an
Astro project already exists by checking for
`_concept/mockup-walkthrough/astro/astro.config.mjs`:

- **Init** (absent): scaffold project skeleton → generate `specs.json` +
  `global.css` → `bun install` → `bun run build` → write `manifest.json`
- **Update** (present): regenerate `specs.json` + `global.css` only →
  `bun run build` → rewrite `manifest.json`

On update runs the agent NEVER touches `astro.config.mjs`,
`tailwind.config.mjs`, or `.astro` template files — those belong to the
user.

**Generation approach — decision recorded.** Agent-direct: the agent reads
screen specs and derives `src/data/specs.json` inline (no persistent
generator script). Same pattern as static-html's Python renderer.

## Renderer Contract

**Public contract.** Every `data-spec-*` attribute MUST be emitted on the
same DOM position as `mockup-walkthrough-static-html` so the
`mockup-feedback-*` cluster resolves clicks identically across renderers.

### `data-spec-*` attribute table

| DOM location | Attribute | Value | Source |
|---|---|---|---|
| `<body>` of every `screen/<group>/<name>.html` | `data-spec-screen` | screen path stem (e.g. `01_user_auth/login`) | screen file path |
| every annotatable child node (form fields, buttons, links, images, regions, list items, nav items) | `data-spec-element` | element id (kebab-case) | `elements:` entry, or auto-slug |
| same node, when no explicit `elements:` entry exists for it | `data-spec-provisional` | literal string `"true"` | absent in YAML |
| `<body>` of every `journey/<id>.html` | `data-spec-journey` | journey id from stories.json | stories.json |
| each step link inside `journey/<id>.html` | `data-spec-screen` | the screen-stem of that step's screen | journey step entry |
| `<body>` of `index.html` | `data-spec-index` | literal string `"true"` | (none — site root marker) |

**The renderer MUST NOT add `data-spec-*` attributes outside this table.**

### `screen_id` vs `screen_path`

Identical semantics to `mockup-walkthrough-static-html`. See that skill's
"screen_id vs screen_path" section for the full definition. In brief:
`screen_id` is the path stem used in `data-spec-screen` and HTML filenames;
`screen_path` is the full repo-relative path with `.md` extension used in
`manifest.json` and `stories.json` `screen_sequence` entries.

### `kind → DOM tag mapping`

| kind | rendered tag | notes |
|---|---|---|
| `input` | `<input>` | with `name="<id>"` and `aria-label="<label>"` |
| `button` | `<button>` | label as inner text |
| `link` | `<a>` | `href="#"` placeholder |
| `image` | `<img>` | `src="#"` placeholder, `alt="<label>"` |
| `text` | `<span>` | label as inner text |
| `region` | `<section>` | label as inner `<h3>` |
| `list` | `<ul>` | empty list with placeholder `<li>` |
| `form` | `<form>` | placeholder; nested inputs not auto-derived |
| `nav` | `<nav>` | placeholder list of links |
| `media` | `<figure>` | `<figcaption>` carries label |
| `custom` | `<div>` | label as inner text; rendered but unstyled |

States beyond `default` are rendered as adjacent `<span class="state-<n>">`
children of the element.

### Auto-slug fallback

Identical to `mockup-walkthrough-static-html`. See that skill's "Auto-slug
fallback" section. The Astro template emits `data-spec-provisional="true"`
on any element where `element.provisional === true`. There is NO separate
top-level `auto_slugged[]` array — `provisional: true` lives on the element
object itself. The `kind: "auto_slugged"` warning entry in
`manifest.warnings[]` is still required per the auto-slug step.

## Inputs

Same four input shapes as `mockup-walkthrough-static-html`:

| Path | Shape |
|---|---|
| `experience/screens/<group>/<screen>.md` | Markdown + YAML frontmatter with optional `elements:` block per `contracts/elements_block.md` |
| `experience/journeys/stories.json` | JSON `{ "journeys": [{ "id", "title", "description", "screen_sequence" }] }` |
| `design/tokens.json` | Token tree. Flattened to CSS custom properties (`--token-<dotted-path-with-hyphens>`). |
| `product-spec/features/<group>/<feature>.md` | Used only for `manifest.json#features`; not rendered as HTML. |

## Outputs

Generated under `_concept/mockup-walkthrough/astro/`:

| Path | Description |
|---|---|
| `index.html` | Router/menu — `<body data-spec-index="true">`. Lists every screen and journey. |
| `screen/<group>/<name>.html` | One file per screen. `<body data-spec-screen="<screen_id>">`. |
| `journey/<id>.html` | One file per journey. `<body data-spec-journey="<id>">`. Walks through screens in order. |
| `manifest.json` | Machine-readable index for `mockup-feedback-annotate`. |

## Astro project layout

```
_concept/mockup-walkthrough/astro/          ← project root (committed)
├── src/
│   ├── data/
│   │   └── specs.json                      ← regenerated each run
│   ├── layouts/
│   │   └── Shell.astro                     ← token-driven wrapper (scaffolded once)
│   ├── pages/
│   │   ├── index.astro                     ← site root, data-spec-index="true"
│   │   ├── screen/
│   │   │   └── [...slug].astro             ← one route → all screens
│   │   └── journey/
│   │       └── [id].astro                  ← one route → all journeys
│   └── styles/
│       └── global.css                      ← Tailwind base + :root token vars (regenerated each run)
├── astro.config.mjs                        ← outDir='.', emptyOutDir=false (scaffolded once)
├── tailwind.config.mjs                     ← generated from tokens.json on init only
├── package.json                            ← (scaffolded once)
├── _astro/                                 ← hashed CSS/JS chunks from build (committed)
├── index.html                              ← built output
├── screen/<group>/<name>.html              ← built output
├── journey/<id>.html                       ← built output
└── manifest.json                           ← written after build, not by Astro
```

## `specs.json` shape

`specs.json` bridges source artefacts to Astro templates at build time.

```json
{
  "screens": [
    {
      "screen_id": "01_user_auth/login",
      "screen_path": "experience/screens/01_user_auth/login.md",
      "rendered_html": "screen/01_user_auth/login.html",
      "group": "01_user_auth",
      "title": "Login",
      "implements": ["product-spec/features/01_user_auth/login.md"],
      "data_entities": ["User"],
      "layout": "experience/screens/00_layout/shell.md",
      "elements": [
        {
          "element_id": "submit-button",
          "kind": "button",
          "label": "Sign in",
          "states": ["default", "loading"],
          "provisional": false,
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/submit-button"
        }
      ],
      "journeys": ["user-signs-in"]
    }
  ],
  "journeys": [
    {
      "journey_id": "user-signs-in",
      "title": "User signs in",
      "description": "First-time user authenticates.",
      "rendered_html": "journey/user-signs-in.html",
      "source": "experience/journeys/stories.json#user-signs-in",
      "screen_sequence": ["01_user_auth/login", "02_dashboard/home"]
    }
  ],
  "token_vars": {
    "--token-color-primary": "#0ea5e9",
    "--token-spacing-sm": "8px"
  },
  "features": [
    {
      "feature_path": "product-spec/features/01_user_auth/login.md",
      "rendered_screens": ["experience/screens/01_user_auth/login.md"]
    }
  ]
}
```

**specs.json → manifest.json projection.** `specs.json` carries
template-convenience fields that MUST NOT be copied to `manifest.json`:
- `screens[].title`, `screens[].group`, `screens[].journeys[]`
- `journeys[].title`, `journeys[].description`

Build `manifest.json` from the in-memory model using the pinned shape
directly (not by serialising `specs.json`).

## ROLE / READS / WRITES / REFERENCES

ROLE  Walkthrough Astro renderer — converts screen specs + journey definitions
      + tokens into a Tailwind-styled clickable Astro static site whose DOM is
      annotatable end-to-end via the same data-spec-* contract as static-html.

READS
  experience/screens/**/*.md            — screen specs (frontmatter + body)
  experience/journeys/stories.json      — journey definitions
  design/tokens.json                    — brand tokens
  ? product-spec/features/**/*.md       — feature traceability (soft)
  ? experience/screens/00_layout/shell.md — shared layout reference (soft)
  ? _concept/mockup-walkthrough/astro/astro.config.mjs — mode detection

WRITES
  _concept/mockup-walkthrough/astro/src/data/specs.json        (every run)
  _concept/mockup-walkthrough/astro/src/styles/global.css      (every run)
  _concept/mockup-walkthrough/astro/astro.config.mjs           (init only)
  _concept/mockup-walkthrough/astro/tailwind.config.mjs        (init only)
  _concept/mockup-walkthrough/astro/package.json               (init only)
  _concept/mockup-walkthrough/astro/src/layouts/Shell.astro    (init only)
  _concept/mockup-walkthrough/astro/src/pages/index.astro      (init only)
  _concept/mockup-walkthrough/astro/src/pages/screen/[...slug].astro (init only)
  _concept/mockup-walkthrough/astro/src/pages/journey/[id].astro    (init only)
  _concept/mockup-walkthrough/astro/index.html                 (built — every run)
  _concept/mockup-walkthrough/astro/screen/<group>/<name>.html (built — every run)
  _concept/mockup-walkthrough/astro/journey/<id>.html          (built — every run)
  _concept/mockup-walkthrough/astro/manifest.json              (every run)

REFERENCES
  contracts/elements_block.md           — elements: schema + renderer contract
  contracts/frontmatter.md              — screen + feature + stories shapes
  contracts/asset_frontmatter.md        — this SKILL.md's own frontmatter shape
  contracts/skill_grammar.md            — DSL keywords used in this body
  contracts/iron_laws.md                — non-negotiable cross-skill constraints
  contracts/scripts/validator_lib.py    — used by mockup-walkthrough/astro/validator.py
  REFACTOR_MOCKUP.md § 4, § 6           — shared input contract + hybrid ID strategy
  mockup-walkthrough/static-html/SKILL.md — sibling skill (contract anchor)

## STEP 1: Read inputs

- Glob `experience/screens/**/*.md` (excluding `00_layout/`); sort
  lexicographically. Parse YAML frontmatter (PyYAML). Extract `implements[]`,
  `data_entities[]`, `layout`, `elements[]` (default `[]`). Capture body
  markdown.
- Validate `elements[]` against `contracts/elements_block.md`. Emit
  `warnings[]` entries of `kind: "unknown_element_kind"` for any kind outside
  the v0.1 enum but render anyway.
- Read `experience/journeys/stories.json`. Validate each journey has `id` AND
  `screen_sequence`. Missing `screen_sequence` → warning
  `kind: "missing_screen_sequence"`, skip that journey.
- Read `design/tokens.json`. Flatten depth-first:
  `{"color": {"primary": "#0ea5e9"}}` → `--token-color-primary: #0ea5e9`.
- Glob `product-spec/features/**/*.md`. Build feature→screens map by inverting
  `screens[].implements[]`.
- Apply auto-slug fallback: for each widget in screen body absent from
  `elements[]`, generate kebab-case id, set `provisional: true`, set
  `source_anchor: "#auto/<id>"`. Append `kind: "auto_slugged"` to
  `warnings[]`. On id collision with another auto-slugged element within the
  same screen, suffix with `-2`, `-3`, … until unique and emit
  `kind: "auto_slug_collision"` to `warnings[]`.
- Build normalised in-memory model:
  `{ screens, journeys, token_vars, features, warnings }`.

### Edge cases

- **Malformed YAML** → fail loudly, exit non-zero, name the offending file.
- **Screen in journey but absent on disk** → `kind: "missing_screen"`,
  dead-end placeholder step (link present, class `journey-step-missing`).
- **`elements:` kind outside v0.1 enum** → render as `custom`,
  `kind: "unknown_element_kind"`.
- **`layout:` reference to non-existent file** → `kind: "missing_layout"`,
  fall back to `Shell.astro` default.
- **`product-spec/features/` empty or missing** → soft gate,
  `kind: "missing_feature"`, continue. `manifest.features[]` → `[]`.
- **Zero journeys** → render "No journeys defined",
  `kind: "no_journeys"`.

## STEP 2: Detect mode

Check `_concept/mockup-walkthrough/astro/astro.config.mjs`.
- Absent → **Init** (proceed to STEP 3 then STEP 4).
- Present → **Update** (skip STEP 3, proceed directly to STEP 4).

## STEP 3: Scaffold project (Init only)

Write the following files. Do NOT write these on update runs.

### `_concept/mockup-walkthrough/astro/package.json`

```json
{
  "name": "mockup-walkthrough-astro",
  "type": "module",
  "scripts": {
    "build": "astro build",
    "dev": "astro dev"
  },
  "dependencies": {
    "astro": "^4.0.0",
    "@astrojs/tailwind": "^5.0.0",
    "tailwindcss": "^3.4.0"
  }
}
```

### `_concept/mockup-walkthrough/astro/astro.config.mjs`

```js
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [tailwind({ configFile: './tailwind.config.mjs' })],
  outDir: '.',
  build: {
    format: 'file',
  },
  emptyOutDir: false,
});
```

### `_concept/mockup-walkthrough/astro/tailwind.config.mjs`

Generate from `token_vars`. Example for tokens
`{"color": {"primary": "#0ea5e9"}, "spacing": {"sm": "8px"}}`:

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: 'var(--token-color-primary)',
      },
      spacing: {
        sm: 'var(--token-spacing-sm)',
      },
    },
  },
  plugins: [],
};
```

The mapping rule: for each `--token-<a>-<b>` var, expose it as
`theme.extend.<a>.<b>: 'var(--token-<a>-<b>)'`. Only one level of nesting
is required for the standard token shape.

### `_concept/mockup-walkthrough/astro/src/layouts/Shell.astro`

The Shell layout accepts a `bodyAttrs` prop so child pages can set
`data-spec-*` attributes on the document `<body>`:

```astro
---
import '../styles/global.css';
const { title = 'Walkthrough', bodyAttrs = {} } = Astro.props;
---
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
  </head>
  <body {...bodyAttrs} class="bg-white text-gray-900 font-sans p-4">
    <slot />
    <footer class="mt-8 text-sm text-gray-500">
      <a href="/">← Back to index</a>
    </footer>
  </body>
</html>
```

### `_concept/mockup-walkthrough/astro/src/pages/index.astro`

```astro
---
import Shell from '../layouts/Shell.astro';
import specs from '../data/specs.json';
---
<Shell title="Walkthrough Index" bodyAttrs={{ 'data-spec-index': 'true' }}>
  <h1 class="text-2xl font-bold mb-4">Walkthrough</h1>
  <section id="screens" class="mb-8">
    <h2 class="text-xl font-semibold mb-2">Screens</h2>
    <ul class="list-disc pl-6">
      {specs.screens.map((s: any) => (
        <li><a href={`/screen/${s.screen_id}`} class="text-blue-600 hover:underline">{s.title || s.screen_id}</a></li>
      ))}
    </ul>
  </section>
  <section id="journeys">
    <h2 class="text-xl font-semibold mb-2">Journeys</h2>
    {specs.journeys.length === 0
      ? <p>No journeys defined</p>
      : <ul class="list-disc pl-6">
          {specs.journeys.map((j: any) => (
            <li><a href={`/journey/${j.journey_id}`} class="text-blue-600 hover:underline">{j.title || j.journey_id}</a></li>
          ))}
        </ul>
    }
  </section>
</Shell>
```

### `_concept/mockup-walkthrough/astro/src/pages/screen/[...slug].astro`

```astro
---
import Shell from '../../layouts/Shell.astro';
import specs from '../../data/specs.json';

export function getStaticPaths() {
  return (specs as any).screens.map((screen: any) => ({
    params: { slug: screen.screen_id },
    props: { screen },
  }));
}

const { screen } = Astro.props as any;

function renderElement(el: any): string {
  const prov = el.provisional ? ' data-spec-provisional="true"' : '';
  const tagMap: Record<string, string> = {
    input: `<input name="${el.element_id}" aria-label="${el.label}" data-spec-element="${el.element_id}"${prov} class="border rounded px-2 py-1" />`,
    button: `<button data-spec-element="${el.element_id}"${prov} class="px-4 py-2 bg-primary text-white rounded">${el.label}</button>`,
    link: `<a href="#" data-spec-element="${el.element_id}"${prov} class="text-blue-600 underline">${el.label}</a>`,
    image: `<img src="#" alt="${el.label}" data-spec-element="${el.element_id}"${prov} class="w-full" />`,
    text: `<span data-spec-element="${el.element_id}"${prov}>${el.label}</span>`,
    region: `<section data-spec-element="${el.element_id}"${prov}><h3>${el.label}</h3></section>`,
    list: `<ul data-spec-element="${el.element_id}"${prov}><li>…</li></ul>`,
    form: `<form data-spec-element="${el.element_id}"${prov}></form>`,
    nav: `<nav data-spec-element="${el.element_id}"${prov}><ul><li>…</li></ul></nav>`,
    media: `<figure data-spec-element="${el.element_id}"${prov}><figcaption>${el.label}</figcaption></figure>`,
    custom: `<div data-spec-element="${el.element_id}"${prov}>${el.label}</div>`,
  };
  const base = tagMap[el.kind] ?? tagMap.custom;
  const states = (el.states || [])
    .filter((s: string) => s !== 'default')
    .map((s: string) => `<span class="state-${s}">${el.label} [${s}]</span>`)
    .join('');
  return base + states;
}
---
<Shell title={screen.title || screen.screen_id} bodyAttrs={{ 'data-spec-screen': screen.screen_id }}>
  <h1 class="text-2xl font-bold mb-4">{screen.title || screen.screen_id}</h1>
  <main class="space-y-4">
    {screen.elements.map((el: any) => (
      <div set:html={renderElement(el)} />
    ))}
  </main>
  <section class="mt-8 text-sm text-gray-500">
    <p>Journeys: {screen.journeys.length === 0 ? 'none' :
      screen.journeys.map((jid: string) => (
        <a href={`/journey/${jid}`} class="underline mr-2">{jid}</a>
      ))
    }</p>
  </section>
</Shell>
```

### `_concept/mockup-walkthrough/astro/src/pages/journey/[id].astro`

```astro
---
import Shell from '../../layouts/Shell.astro';
import specs from '../../data/specs.json';

export function getStaticPaths() {
  return (specs as any).journeys.map((journey: any) => ({
    params: { id: journey.journey_id },
    props: { journey },
  }));
}

const { journey } = Astro.props as any;
const screens = (specs as any).screens;

function findScreen(screen_id: string) {
  return screens.find((s: any) => s.screen_id === screen_id);
}
---
<Shell title={journey.title || journey.journey_id} bodyAttrs={{ 'data-spec-journey': journey.journey_id }}>
  <h1 class="text-2xl font-bold mb-2">{journey.title}</h1>
  {journey.description && <p class="text-gray-600 mb-6">{journey.description}</p>}
  <ol class="space-y-4 list-decimal pl-6">
    {journey.screen_sequence.map((screen_id: string, i: number) => {
      const screen = findScreen(screen_id);
      const isLast = i === journey.screen_sequence.length - 1;
      if (!screen) {
        return (
          <li class="journey-step-missing text-red-500">
            <span data-spec-screen={screen_id}>Missing screen: {screen_id}</span>
          </li>
        );
      }
      return (
        <li>
          <h2 class="font-semibold">Step {i + 1}: {screen.title || screen_id}</h2>
          <a href={`/screen/${screen_id}`} data-spec-screen={screen_id} class="text-blue-600 underline">
            Open screen
          </a>
          {!isLast && (
            <span class="ml-4">
              <a href={`/screen/${journey.screen_sequence[i + 1]}`} class="text-blue-600 underline">Next →</a>
            </span>
          )}
          {isLast && (
            <span class="ml-4"><a href="/" class="text-blue-600 underline">→ Index</a></span>
          )}
        </li>
      );
    })}
  </ol>
</Shell>
```

## STEP 4: Generate `specs.json` and `global.css` (both modes)

Write `src/data/specs.json` derived from the in-memory model. Schema as shown
in the `specs.json` shape section above. Overwrite unconditionally.

Write `src/styles/global.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  /* one line per flattened token_var */
  --token-<name>: <value>;
}
```

Overwrite unconditionally. This file is agent-managed every run.

On update runs only: compare the count of `--token-*` keys in the freshly
derived in-memory model vs. the CSS var declarations in the existing
`global.css` before overwriting. If counts differ, append
`kind: "stale_tailwind_config"` to `warnings[]`.

## STEP 5: Build

Run from `_concept/mockup-walkthrough/astro/`:

```bash
bun run build
```

On non-zero exit: print full stderr and exit non-zero. Do not write
`manifest.json`.

After build: verify `dist/` does NOT exist under the project root. If it
does: fail with "astro.config.mjs outDir misconfigured — dist/ must not
exist".

## STEP 6: Write `manifest.json`

Emit the pinned schema. Build it from the in-memory model — NOT by
serialising `specs.json`. Template-only fields from `specs.json`
(`screens[].title`, `screens[].group`, `screens[].journeys[]`,
`journeys[].title`, `journeys[].description`) MUST NOT appear in
`manifest.json`.

```json
{
  "schema_version": "1.0",
  "renderer": "mockup-walkthrough-astro",
  "renderer_version": "0.1.0",
  "generated_at": "<ISO-8601 UTC>",
  "source_root": "experience/screens",
  "screens": [
    {
      "screen_path": "experience/screens/01_user_auth/login.md",
      "screen_id": "01_user_auth/login",
      "rendered_html": "screen/01_user_auth/login.html",
      "implements": ["product-spec/features/01_user_auth/login.md"],
      "data_entities": ["User"],
      "layout": "experience/screens/00_layout/shell.md",
      "elements": [
        {
          "element_id": "submit-button",
          "kind": "button",
          "label": "Sign in",
          "states": ["default", "loading"],
          "provisional": false,
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/submit-button"
        }
      ]
    }
  ],
  "journeys": [
    {
      "journey_id": "user-signs-in",
      "rendered_html": "journey/user-signs-in.html",
      "source": "experience/journeys/stories.json#user-signs-in",
      "screen_sequence": [
        "experience/screens/01_user_auth/login.md",
        "experience/screens/02_dashboard/home.md"
      ]
    }
  ],
  "features": [
    {
      "feature_path": "product-spec/features/01_user_auth/login.md",
      "rendered_screens": ["experience/screens/01_user_auth/login.md"]
    }
  ],
  "warnings": []
}
```

Sort: `screens[]` by `screen_path`, `journeys[]` by `journey_id`,
`features[]` by `feature_path`. Write atomically (tmp → rename).

`renderer_version` matches the `metadata.version` in this SKILL.md's
frontmatter (`"0.1.0"`).

## STEP 7: Validate

Run from the repo root:

```bash
python mockup-walkthrough/astro/validator.py _concept/mockup-walkthrough/astro
```

Exit 0 = ready. Exit 2 = violation report.

## Error handling

### Inherited from static-html (identical behaviour)

| Condition | Behaviour |
|---|---|
| Malformed YAML in screen file | Fail loudly, exit non-zero, name the offending file |
| Screen in journey but absent on disk | `manifest.warnings[]` `kind: "missing_screen"` + dead-end `<li class="journey-step-missing">` |
| `screen_sequence` absent for a journey | `manifest.warnings[]` `kind: "missing_screen_sequence"`, skip that journey render |
| Zero journeys in `stories.json` | Render "No journeys defined", `kind: "no_journeys"` |
| Missing `product-spec/features/` | Soft gate, `kind: "missing_feature"`, continue; `manifest.features[]` → `[]` |
| Unknown `elements:` kind | Render as `custom`, `kind: "unknown_element_kind"` |
| `layout:` reference to non-existent file | `kind: "missing_layout"`, fall back to `Shell.astro` default |
| Auto-slug collision | `kind: "auto_slug_collision"`, suffix auto id with `-2`, `-3`, … |

### Astro-specific

| Condition | Behaviour |
|---|---|
| `bun install` exits non-zero | Fail loudly with stderr; do not build |
| `bun run build` exits non-zero | Fail loudly with stderr; do not write `manifest.json` |
| `dist/` exists after build | Fail: "astro.config.mjs outDir misconfigured — dist/ must not exist" |
| Token count differs from CSS var count (update runs only) | `kind: "stale_tailwind_config"`; user must extend `tailwind.config.mjs` manually |

### `warnings[].kind` enum

`auto_slugged`, `auto_slug_collision`, `missing_layout`, `missing_feature`,
`unknown_element_kind`, `missing_screen`, `missing_screen_sequence`,
`no_journeys`, `stale_tailwind_config`

`stale_tailwind_config` is the only Astro-specific addition.

## MUST / NEVER

MUST  emit data-spec-screen on every screen `<body>`
MUST  emit data-spec-element on every annotatable child node
MUST  emit data-spec-provisional="true" on auto-slugged element nodes
MUST  emit data-spec-journey="<id>" on every journey `<body>`
MUST  emit data-spec-index="true" on index.html `<body>`
MUST  write manifest.json conforming to pinned schema (schema_version: "1.0")
MUST  sort manifest arrays lexicographically
MUST  set emptyOutDir: false in astro.config.mjs
MUST  set build.format: 'file' in astro.config.mjs
MUST  set outDir: '.' in astro.config.mjs
MUST  write specs.json and global.css before running bun run build
MUST  regenerate global.css on every run (agent-managed)
MUST  return getStaticPaths() slugs without trailing slashes

NEVER regenerate astro.config.mjs, tailwind.config.mjs, or .astro templates on update runs
NEVER create a dist/ subdirectory — outDir must be '.'
NEVER emit data-spec-* attributes outside the pinned table
NEVER mutate source files (experience/screens/**, stories.json, tokens.json, features/**)
NEVER inject journey-step navigation into screen/**/*.html
NEVER inline absolute filesystem paths in manifest.json
NEVER use a separate auto_slugged[] array — set provisional: true on the element object (the kind: "auto_slugged" warning entry in manifest.warnings[] is still required per the auto-slug step)

## CHECKLIST

- [ ] `_concept/mockup-walkthrough/astro/index.html` exists
- [ ] `_concept/mockup-walkthrough/astro/manifest.json` exists and parses as JSON
- [ ] `manifest.schema_version == "1.0"` and `manifest.renderer == "mockup-walkthrough-astro"`
- [ ] One `screen/<group>/<name>.html` per screen file under `experience/screens/`
- [ ] One `journey/<id>.html` per journey in `stories.json`
- [ ] Every `<body>` in `screen/**/*.html` has `data-spec-screen`
- [ ] Every annotatable node in `screen/**/*.html` has `data-spec-element`
- [ ] Every auto-slugged element node also has `data-spec-provisional="true"`
- [ ] Every `<body>` in `journey/**/*.html` has `data-spec-journey`
- [ ] `index.html` `<body>` has `data-spec-index="true"`
- [ ] No `dist/` subdirectory under `_concept/mockup-walkthrough/astro/`
- [ ] At least one `<link rel="stylesheet">` in `index.html` and referenced CSS file is non-empty
- [ ] Validator (`mockup-walkthrough/astro/validator.py`) exits 0

EMIT  [mockup-walkthrough-astro] started run_id=<uuid>
EMIT  [mockup-walkthrough-astro] checkpoint screens=<N> journeys=<M>
EMIT  [mockup-walkthrough-astro] completed run_id=<uuid> screens=<N> journeys=<M> warnings=<W>
