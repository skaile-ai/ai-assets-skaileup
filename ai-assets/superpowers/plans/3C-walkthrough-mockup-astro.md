# walkthrough-mockup-astro Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author `walkthrough-mockup/astro/SKILL.md` (agent prompt) and `walkthrough-mockup/astro/validator.py` (output validator), updating `walkthrough-mockup/DOMAIN.md` to register the new skill.

**Architecture:** The SKILL.md is a Markdown agent prompt that instructs Claude how to produce a built Astro static site from screen specs, journeys, tokens, and features. The validator.py extends static-html's validator with three Astro-specific checks (no dist/, correct renderer name, non-empty stylesheet). No runtime code is compiled; the entire implementation is document + Python script authoring.

**Tech Stack:** Markdown + YAML (SKILL.md format), Python 3 stdlib + PyYAML (validator.py), same test harness as static-html (fixtures/ + expected/ + run_validator.sh).

**Spec:** `docs/superpowers/specs/2026-05-09-walkthrough-mockup-astro-design.md`
**Reference:** `walkthrough-mockup/static-html/SKILL.md` and `walkthrough-mockup/static-html/validator.py`

**Working directory:** `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`

---

## File map

| File | Action | Responsibility |
|---|---|---|
| `walkthrough-mockup/astro/SKILL.md` | Create | Full agent prompt for generating an Astro walkthrough |
| `walkthrough-mockup/astro/validator.py` | Create | Validates built Astro site against contract |
| `walkthrough-mockup/astro/tests/fixtures/minimal/` | Create | Shared input fixture (reused from static-html) |
| `walkthrough-mockup/astro/tests/expected/minimal/` | Create | Pre-fabricated minimal Astro site output for snapshot validation |
| `walkthrough-mockup/astro/tests/run_validator.sh` | Create | One-shot test runner |
| `walkthrough-mockup/astro/tests/.gitignore` | Create | Ignore rendered/ scratch dir |
| `walkthrough-mockup/DOMAIN.md` | Modify | Add `walkthrough-mockup-astro` to skills list |

---

## Task 1: Write SKILL.md

**Files:**
- Create: `walkthrough-mockup/astro/SKILL.md`

- [ ] **Step 1.1: Create directory**

```bash
mkdir -p walkthrough-mockup/astro
```

- [ ] **Step 1.2: Write SKILL.md**

Write the file `walkthrough-mockup/astro/SKILL.md` with the following exact content:

```markdown
---
name: walkthrough-mockup-astro
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
    produces:
      - path: "_concept/walkthrough-mockup/astro"
        description: "Astro project source + built site: index.html, screen/<group>/<name>.html, journey/<id>.html, manifest.json"
---

# Walkthrough Mockup — Astro

## Overview

Astro-rendered variant of the walkthrough mockup cluster. Consumes the same
four inputs as `walkthrough-mockup-static-html` (screen specs, journey
definitions, brand tokens, feature files); produces a Tailwind-styled built
Astro static site at `_concept/walkthrough-mockup/astro/`.

Every rendered DOM node carries the same `data-spec-*` attributes as the
static-html variant so the `mockup-feedback-*` cluster can resolve clicks
identically across renderers. The `manifest.json` schema is identical —
only `renderer: "walkthrough-mockup-astro"` differs.

**Two-mode behaviour — decision recorded.** The agent detects whether an
Astro project already exists by checking for
`_concept/walkthrough-mockup/astro/astro.config.mjs`:

- **Init** (absent): scaffold project skeleton → generate `specs.json` +
  `global.css` → `bun install` → `astro build` → write `manifest.json`
- **Update** (present): regenerate `specs.json` + `global.css` only →
  `astro build` → rewrite `manifest.json`

On update runs the agent NEVER touches `astro.config.mjs`,
`tailwind.config.mjs`, or `.astro` template files — those belong to the
user.

**Generation approach — decision recorded.** Agent-direct: the agent reads
screen specs and derives `src/data/specs.json` inline (no persistent
generator script). Same pattern as static-html's Python renderer.

## Renderer Contract

**Public contract.** Every `data-spec-*` attribute MUST be emitted on the
same DOM position as `walkthrough-mockup-static-html` so the
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

Identical semantics to `walkthrough-mockup-static-html`. See that skill's
"screen_id vs screen_path" section.

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

Identical to `walkthrough-mockup-static-html`. See that skill's "Auto-slug
fallback" section. The Astro template emits `data-spec-provisional="true"`
on any element where `element.provisional === true`. There is NO separate
top-level `auto_slugged[]` array — `provisional: true` lives on the element
object itself. The `kind: "auto_slugged"` warning entry in
`manifest.warnings[]` is still required per the auto-slug step.

## Inputs

Same four input shapes as `walkthrough-mockup-static-html`:

| Path | Shape |
|---|---|
| `experience/screens/<group>/<screen>.md` | Markdown + YAML frontmatter with optional `elements:` block per `contracts/elements_block.md` |
| `experience/journeys/stories.json` | JSON `{ "journeys": [{ "id", "title", "description", "screen_sequence" }] }` |
| `design/tokens.json` | Token tree. Flattened to CSS custom properties (`--token-<dotted-path-with-hyphens>`). |
| `product-spec/features/<group>/<feature>.md` | Used only for `manifest.json#features`; not rendered as HTML. |

## Astro project layout

```
_concept/walkthrough-mockup/astro/          ← project root (committed)
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
  ? _concept/walkthrough-mockup/astro/astro.config.mjs — mode detection

WRITES
  _concept/walkthrough-mockup/astro/src/data/specs.json        (every run)
  _concept/walkthrough-mockup/astro/src/styles/global.css      (every run)
  _concept/walkthrough-mockup/astro/astro.config.mjs           (init only)
  _concept/walkthrough-mockup/astro/tailwind.config.mjs        (init only)
  _concept/walkthrough-mockup/astro/package.json               (init only)
  _concept/walkthrough-mockup/astro/src/layouts/Shell.astro    (init only)
  _concept/walkthrough-mockup/astro/src/pages/index.astro      (init only)
  _concept/walkthrough-mockup/astro/src/pages/screen/[...slug].astro (init only)
  _concept/walkthrough-mockup/astro/src/pages/journey/[id].astro    (init only)
  _concept/walkthrough-mockup/astro/index.html                 (built — every run)
  _concept/walkthrough-mockup/astro/screen/<group>/<name>.html (built — every run)
  _concept/walkthrough-mockup/astro/journey/<id>.html          (built — every run)
  _concept/walkthrough-mockup/astro/manifest.json              (every run)

REFERENCES
  contracts/elements_block.md           — elements: schema + renderer contract
  contracts/frontmatter.md              — screen + feature + stories shapes
  contracts/asset_frontmatter.md        — this SKILL.md's own frontmatter shape
  contracts/skill_grammar.md            — DSL keywords used in this body
  contracts/iron_laws.md                — non-negotiable cross-skill constraints
  contracts/scripts/validator_lib.py    — used by walkthrough-mockup/astro/validator.py
  REFACTOR_MOCKUP.md § 4, § 6           — shared input contract + hybrid ID strategy
  walkthrough-mockup/static-html/SKILL.md — sibling skill (contract anchor)

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
  `warnings[]`.
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

Check `_concept/walkthrough-mockup/astro/astro.config.mjs`.
- Absent → **Init** (proceed to STEP 3 then STEP 4).
- Present → **Update** (skip STEP 3, proceed directly to STEP 4).

## STEP 3: Scaffold project (Init only)

Write the following files. Do NOT write these on update runs.

### `_concept/walkthrough-mockup/astro/package.json`

```json
{
  "name": "walkthrough-mockup-astro",
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

### `_concept/walkthrough-mockup/astro/astro.config.mjs`

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

### `_concept/walkthrough-mockup/astro/tailwind.config.mjs`

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

### `_concept/walkthrough-mockup/astro/src/layouts/Shell.astro`

```astro
---
import '../styles/global.css';
const { title = 'Walkthrough' } = Astro.props;
---
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
  </head>
  <body class="bg-white text-gray-900 font-sans p-4">
    <slot />
    <footer class="mt-8 text-sm text-gray-500">
      <a href="/">← Back to index</a>
    </footer>
  </body>
</html>
```

### `_concept/walkthrough-mockup/astro/src/pages/index.astro`

```astro
---
import Shell from '../layouts/Shell.astro';
import specs from '../data/specs.json';
---
<Shell title="Walkthrough Index">
  <body data-spec-index="true">
    <h1 class="text-2xl font-bold mb-4">Walkthrough</h1>
    <section id="screens" class="mb-8">
      <h2 class="text-xl font-semibold mb-2">Screens</h2>
      <ul class="list-disc pl-6">
        {specs.screens.map(s => (
          <li><a href={`/screen/${s.screen_id}`} class="text-blue-600 hover:underline">{s.title || s.screen_id}</a></li>
        ))}
      </ul>
    </section>
    <section id="journeys">
      <h2 class="text-xl font-semibold mb-2">Journeys</h2>
      {specs.journeys.length === 0
        ? <p>No journeys defined</p>
        : <ul class="list-disc pl-6">
            {specs.journeys.map(j => (
              <li><a href={`/journey/${j.journey_id}`} class="text-blue-600 hover:underline">{j.title || j.journey_id}</a></li>
            ))}
          </ul>
      }
    </section>
  </body>
</Shell>
```

Note: the `<body>` tag with `data-spec-index="true"` must be the rendered
`<body>` of the HTML document. Because `Shell.astro` already writes the
`<body>`, adjust the template so `data-spec-index="true"` is on the actual
document body. Approach: pass the attribute as a prop to Shell:

```astro
---
// Shell.astro — update to accept bodyAttrs prop
const { title = 'Walkthrough', bodyAttrs = {} } = Astro.props;
---
<body {...bodyAttrs} class="bg-white text-gray-900 font-sans p-4">
```

Then in `index.astro`:

```astro
<Shell title="Walkthrough Index" bodyAttrs={{ 'data-spec-index': 'true' }}>
  ...content without <body> wrapper...
</Shell>
```

Apply the same pattern for `screen/[...slug].astro` (`data-spec-screen`) and
`journey/[id].astro` (`data-spec-journey`).

### `_concept/walkthrough-mockup/astro/src/pages/screen/[...slug].astro`

```astro
---
import Shell from '../../layouts/Shell.astro';
import specs from '../../data/specs.json';

export function getStaticPaths() {
  return specs.screens.map(screen => ({
    params: { slug: screen.screen_id },
    props: { screen },
  }));
}

const { screen } = Astro.props;

function renderElement(el) {
  // Returns an HTML string for one element.
  // Tag mapping:
  const tagMap = {
    input: `<input name="${el.element_id}" aria-label="${el.label}" data-spec-element="${el.element_id}"${el.provisional ? ' data-spec-provisional="true"' : ''} class="border rounded px-2 py-1" />`,
    button: `<button data-spec-element="${el.element_id}"${el.provisional ? ' data-spec-provisional="true"' : ''} class="px-4 py-2 bg-primary text-white rounded">${el.label}</button>`,
    link: `<a href="#" data-spec-element="${el.element_id}"${el.provisional ? ' data-spec-provisional="true"' : ''} class="text-blue-600 underline">${el.label}</a>`,
    image: `<img src="#" alt="${el.label}" data-spec-element="${el.element_id}"${el.provisional ? ' data-spec-provisional="true"' : ''} class="w-full" />`,
    text: `<span data-spec-element="${el.element_id}"${el.provisional ? ' data-spec-provisional="true"' : ''}>${el.label}</span>`,
    region: `<section data-spec-element="${el.element_id}"${el.provisional ? ' data-spec-provisional="true"' : ''}><h3>${el.label}</h3></section>`,
    list: `<ul data-spec-element="${el.element_id}"${el.provisional ? ' data-spec-provisional="true"' : ''}><li>…</li></ul>`,
    form: `<form data-spec-element="${el.element_id}"${el.provisional ? ' data-spec-provisional="true"' : ''}></form>`,
    nav: `<nav data-spec-element="${el.element_id}"${el.provisional ? ' data-spec-provisional="true"' : ''}><ul><li>…</li></ul></nav>`,
    media: `<figure data-spec-element="${el.element_id}"${el.provisional ? ' data-spec-provisional="true"' : ''}><figcaption>${el.label}</figcaption></figure>`,
    custom: `<div data-spec-element="${el.element_id}"${el.provisional ? ' data-spec-provisional="true"' : ''}>${el.label}</div>`,
  };
  const base = tagMap[el.kind] ?? tagMap.custom;
  const states = (el.states || []).filter(s => s !== 'default')
    .map(s => `<span class="state-${s}">${el.label} [${s}]</span>`).join('');
  return base + states;
}
---
<Shell title={screen.title || screen.screen_id} bodyAttrs={{ 'data-spec-screen': screen.screen_id }}>
  <h1 class="text-2xl font-bold mb-4">{screen.title || screen.screen_id}</h1>
  <main class="space-y-4">
    {screen.elements.map(el => (
      <div set:html={renderElement(el)} />
    ))}
  </main>
  <section class="mt-8 text-sm text-gray-500">
    <p>Journeys: {screen.journeys.length === 0 ? 'none' : screen.journeys.map(jid => (
      <a href={`/journey/${jid}`} class="underline mr-2">{jid}</a>
    ))}</p>
  </section>
</Shell>
```

### `_concept/walkthrough-mockup/astro/src/pages/journey/[id].astro`

```astro
---
import Shell from '../../layouts/Shell.astro';
import specs from '../../data/specs.json';

export function getStaticPaths() {
  return specs.journeys.map(journey => ({
    params: { id: journey.journey_id },
    props: { journey },
  }));
}

const { journey } = Astro.props;
const screens = specs.screens;
function findScreen(screen_id) {
  return screens.find(s => s.screen_id === screen_id);
}
---
<Shell title={journey.title || journey.journey_id} bodyAttrs={{ 'data-spec-journey': journey.journey_id }}>
  <h1 class="text-2xl font-bold mb-2">{journey.title}</h1>
  {journey.description && <p class="text-gray-600 mb-6">{journey.description}</p>}
  <ol class="space-y-4 list-decimal pl-6">
    {journey.screen_sequence.map((screen_id, i) => {
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

After writing all files, run:

```bash
cd _concept/walkthrough-mockup/astro && bun install
```

Expected: no errors.

- [ ] **Step 1.3: Generate `specs.json` and `global.css` (STEP 4 of skill)**

For the init run, write:

`_concept/walkthrough-mockup/astro/src/data/specs.json` — derived from the
project's screen specs at `experience/screens/**/*.md`, journeys, tokens,
features per the spec's `specs.json` shape.

`_concept/walkthrough-mockup/astro/src/styles/global.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --token-color-primary: #0ea5e9;
  --token-spacing-sm: 8px;
  /* ... one var per flattened token */
}
```

- [ ] **Step 1.4: Run the build**

```bash
cd _concept/walkthrough-mockup/astro && bun run build
```

Expected: exits 0, produces `index.html`, `screen/`, `journey/`, `_astro/`.
Verify no `dist/` directory was created.

- [ ] **Step 1.5: Verify no dist/**

```bash
test ! -d _concept/walkthrough-mockup/astro/dist && echo "OK — no dist/" || echo "FAIL — dist/ exists"
```

- [ ] **Step 1.6: Commit**

```bash
git add walkthrough-mockup/astro/SKILL.md
git commit -m "feat: add walkthrough-mockup-astro SKILL.md (Task 3C)"
```

---

## Task 2: Write validator.py

**Files:**
- Create: `walkthrough-mockup/astro/validator.py`

The Astro validator extends static-html's validator. The differences:
1. `RENDERER = "walkthrough-mockup-astro"`
2. Added `check_no_dist(site, report)` — fails if `dist/` exists under site root
3. Added `check_stylesheet(site, report)` — verifies `index.html` has a `<link rel="stylesheet">` whose href resolves to a non-empty file
4. The `check_zero_build` function is retained unchanged (Astro's relative chunk URLs pass the existing patterns)

- [ ] **Step 2.1: Write validator.py**

Write `walkthrough-mockup/astro/validator.py`:

```python
#!/usr/bin/env python3
"""validator.py — walkthrough-mockup-astro validator.

Two modes:

1. **Site-root mode** (default): structural checks only.
   $ python validator.py <site-root> [--source-root <path>]

2. **Fixture mode**: structural checks + byte-compare against expected snapshot.
   $ python validator.py <site-root> --fixture <name>

Exit codes:
  0  PASS
  2  FAIL — at least one violation
  1  internal error

Site-root layout expected:

  <site-root>/
    index.html
    manifest.json
    screen/<group>/<name>.html
    journey/<id>.html
    _astro/<hashed-css-chunks>

Stdlib + PyYAML only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# ── Pinned constants ─────────────────────────────────────────────────

SCHEMA_VERSION = "1.0"
RENDERER = "walkthrough-mockup-astro"
TOP_LEVEL_KEYS = {
    "schema_version",
    "renderer",
    "renderer_version",
    "generated_at",
    "source_root",
    "screens",
    "journeys",
    "features",
    "warnings",
}
ALLOWED_DATA_SPEC_ATTRS = {
    "data-spec-screen",
    "data-spec-element",
    "data-spec-provisional",
    "data-spec-journey",
    "data-spec-index",
}

JS_FRAMEWORK_PATTERNS = [
    re.compile(r'<script\s+[^>]*src\s*=\s*"https?://', re.IGNORECASE),
    re.compile(r'<script\s+[^>]*src\s*=\s*"//', re.IGNORECASE),
    re.compile(
        r'<link\s+[^>]*rel\s*=\s*"stylesheet"[^>]*href\s*=\s*"https?://',
        re.IGNORECASE,
    ),
]


# ── Violation accumulator ────────────────────────────────────────────


class Report:
    def __init__(self) -> None:
        self.violations: list[str] = []

    def add(self, where: str, message: str) -> None:
        self.violations.append(f"{where}: {message}")

    def ok(self) -> bool:
        return not self.violations

    def print_and_exit(self) -> None:
        if self.ok():
            print("PASS — walkthrough-mockup-astro validator")
            sys.exit(0)
        print(
            f"FAIL — walkthrough-mockup-astro: "
            f"{len(self.violations)} violation(s)"
        )
        for v in self.violations:
            print(f"  {v}")
        sys.exit(2)


# ── Tiny attribute extractor ─────────────────────────────────────────


class AttrCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        self.tags.append((tag, dict(attrs)))

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        self.tags.append((tag, dict(attrs)))


def parse_html(path: Path) -> list[tuple[str, dict[str, str]]]:
    parser = AttrCollector()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.tags


def find_body_attrs(tags: list[tuple[str, dict[str, str]]]) -> dict[str, str]:
    for tag, attrs in tags:
        if tag == "body":
            return attrs
    return {}


def collect_attr_values(
    tags: list[tuple[str, dict[str, str]]], attr: str
) -> list[str]:
    return [a[attr] for _, a in tags if attr in a]


# ── Structural checks ────────────────────────────────────────────────


def check_manifest_shape(site: Path, report: Report) -> dict | None:
    manifest_path = site / "manifest.json"
    if not manifest_path.exists():
        report.add(str(manifest_path), "manifest.json missing")
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.add(str(manifest_path), f"manifest.json invalid JSON: {exc}")
        return None
    if not isinstance(manifest, dict):
        report.add(str(manifest_path), "manifest.json root must be an object")
        return None
    missing = TOP_LEVEL_KEYS - manifest.keys()
    if missing:
        report.add(
            str(manifest_path),
            f"manifest.json missing top-level keys: {sorted(missing)}",
        )
    if manifest.get("schema_version") != SCHEMA_VERSION:
        report.add(
            str(manifest_path),
            f"schema_version != {SCHEMA_VERSION!r} "
            f"(got {manifest.get('schema_version')!r})",
        )
    if manifest.get("renderer") != RENDERER:
        report.add(
            str(manifest_path),
            f"renderer != {RENDERER!r} (got {manifest.get('renderer')!r})",
        )
    return manifest


def check_no_dist(site: Path, report: Report) -> None:
    dist = site / "dist"
    if dist.exists():
        report.add(
            str(dist),
            "dist/ subdirectory found — astro.config.mjs outDir misconfigured "
            "(must be '.' with emptyOutDir: false)",
        )


def check_stylesheet(site: Path, report: Report) -> None:
    index_path = site / "index.html"
    if not index_path.exists():
        return  # check_index will already report this
    tags = parse_html(index_path)
    stylesheet_href = None
    for tag, attrs in tags:
        if tag == "link" and attrs.get("rel") == "stylesheet":
            stylesheet_href = attrs.get("href", "")
            break
    if stylesheet_href is None:
        report.add(
            str(index_path),
            'index.html missing <link rel="stylesheet"> — Tailwind not applied',
        )
        return
    # Resolve href relative to site root (strip leading slash if present)
    href_clean = stylesheet_href.lstrip("/")
    css_path = site / href_clean
    if not css_path.exists():
        report.add(
            str(css_path),
            f"stylesheet href={stylesheet_href!r} resolves to missing file",
        )
        return
    if css_path.stat().st_size == 0:
        report.add(
            str(css_path),
            f"stylesheet {stylesheet_href!r} is empty — Tailwind build produced no CSS",
        )


def check_index(site: Path, report: Report) -> None:
    index_path = site / "index.html"
    if not index_path.exists():
        report.add(str(index_path), "index.html missing")
        return
    tags = parse_html(index_path)
    body_attrs = find_body_attrs(tags)
    if body_attrs.get("data-spec-index") != "true":
        report.add(
            str(index_path),
            'index.html <body> missing data-spec-index="true"',
        )


def check_screens(
    site: Path,
    manifest: dict,
    project_root: Path,
    source_root: Path,
    report: Report,
) -> None:
    for screen in manifest.get("screens", []):
        rendered = site / screen.get("rendered_html", "")
        screen_id = screen.get("screen_id", "")
        screen_path = screen.get("screen_path", "")
        elements = screen.get("elements", [])

        if not rendered.exists():
            report.add(
                str(rendered),
                f"rendered_html does not exist (screen_id={screen_id!r})",
            )
            continue

        if screen_path:
            src = (project_root / screen_path).resolve()
            if not src.exists():
                report.add(
                    str(src),
                    f"data-spec-screen source missing for screen_id={screen_id!r}",
                )
            else:
                try:
                    src.relative_to(source_root)
                except ValueError:
                    report.add(
                        str(src),
                        f"source not under --source-root={source_root}",
                    )

        tags = parse_html(rendered)
        body_attrs = find_body_attrs(tags)
        if body_attrs.get("data-spec-screen") != screen_id:
            report.add(
                str(rendered),
                f"<body> data-spec-screen={body_attrs.get('data-spec-screen')!r} "
                f"!= manifest screen_id={screen_id!r}",
            )

        rendered_element_ids = set(collect_attr_values(tags, "data-spec-element"))
        for elem in elements:
            elem_id = elem.get("element_id", "")
            if elem_id not in rendered_element_ids:
                report.add(
                    str(rendered),
                    f'data-spec-element="{elem_id}" missing from rendered HTML',
                )

        for _, attrs in tags:
            for k in attrs:
                if k.startswith("data-spec-") and k not in ALLOWED_DATA_SPEC_ATTRS:
                    report.add(
                        str(rendered),
                        f"unknown attribute {k!r} (not in renderer contract)",
                    )

        check_zero_build(rendered, report)


def check_journeys(
    site: Path, manifest: dict, screen_id_set: set[str], report: Report
) -> None:
    for journey in manifest.get("journeys", []):
        rendered = site / journey.get("rendered_html", "")
        journey_id = journey.get("journey_id", "")

        if not rendered.exists():
            report.add(
                str(rendered),
                f"rendered_html missing (journey_id={journey_id!r})",
            )
            continue

        tags = parse_html(rendered)
        body_attrs = find_body_attrs(tags)
        if body_attrs.get("data-spec-journey") != journey_id:
            report.add(
                str(rendered),
                f"<body> data-spec-journey={body_attrs.get('data-spec-journey')!r} "
                f"!= manifest journey_id={journey_id!r}",
            )

        for tag, attrs in tags:
            if tag == "a" and "data-spec-screen" in attrs:
                step_id = attrs["data-spec-screen"]
                if step_id not in screen_id_set:
                    report.add(
                        str(rendered),
                        f'data-spec-screen="{step_id}" not in rendered screens set',
                    )

        check_zero_build(rendered, report)


def check_zero_build(html_path: Path, report: Report) -> None:
    text = html_path.read_text(encoding="utf-8")
    for pat in JS_FRAMEWORK_PATTERNS:
        if pat.search(text):
            report.add(
                str(html_path),
                f"non-relative script/stylesheet URL found ({pat.pattern!r})",
            )
            return


# ── Fixture mode ─────────────────────────────────────────────────────


def normalise_manifest_for_compare(text: str) -> str:
    return re.sub(
        r'"generated_at"\s*:\s*"[^"]*"',
        '"generated_at": "<pinned>"',
        text,
    )


def fixture_diff(site: Path, expected: Path, report: Report) -> None:
    if not expected.is_dir():
        report.add(str(expected), "expected snapshot directory missing")
        return
    expected_files = sorted(
        p.relative_to(expected) for p in expected.rglob("*") if p.is_file()
    )
    for rel in expected_files:
        exp_path = expected / rel
        got_path = site / rel
        if not got_path.exists():
            report.add(str(got_path), f"expected fixture file missing: {rel}")
            continue
        exp_text = exp_path.read_text(encoding="utf-8")
        got_text = got_path.read_text(encoding="utf-8")
        if rel.name == "manifest.json":
            got_text = normalise_manifest_for_compare(got_text)
            exp_text = normalise_manifest_for_compare(exp_text)
        if got_text != exp_text:
            for i, (a, b) in enumerate(
                zip(exp_text.splitlines(), got_text.splitlines()), 1
            ):
                if a != b:
                    report.add(
                        f"{got_path}:{i}",
                        f"snapshot mismatch — expected {a[:80]!r}, got {b[:80]!r}",
                    )
                    break
            else:
                report.add(str(got_path), "snapshot mismatch (length differs)")


# ── Entry ────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="validator.py",
        description="walkthrough-mockup-astro validator",
    )
    parser.add_argument("site_root", help="site root directory")
    parser.add_argument("--fixture", default=None, help="fixture name under tests/expected/")
    parser.add_argument(
        "--source-root",
        default="experience/screens",
        help="path the manifest source_root resolves to",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="root that screen_path values are anchored to",
    )
    parser.add_argument("--cwd", default=None, help="optional working dir for test runs")
    args = parser.parse_args()

    cwd = Path(args.cwd) if args.cwd else Path.cwd()
    site = (cwd / args.site_root).resolve()
    source_root = (cwd / args.source_root).resolve()
    if args.project_root is not None:
        project_root = (cwd / args.project_root).resolve()
    else:
        project_root = source_root.parent.parent

    if not site.is_dir():
        print(f"FAIL — site root does not exist: {site}", file=sys.stderr)
        sys.exit(1)

    report = Report()
    check_no_dist(site, report)
    check_stylesheet(site, report)
    manifest = check_manifest_shape(site, report)
    check_index(site, report)
    if manifest is not None:
        check_screens(site, manifest, project_root, source_root, report)
        screen_id_set = {s.get("screen_id", "") for s in manifest.get("screens", [])}
        check_journeys(site, manifest, screen_id_set, report)

    if args.fixture:
        skill_root = Path(__file__).resolve().parent
        expected = skill_root / "tests" / "expected" / args.fixture
        fixture_diff(site, expected, report)

    report.print_and_exit()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2.2: Verify it loads**

```bash
python walkthrough-mockup/astro/validator.py --help
```

Expected: prints usage, exits 0.

- [ ] **Step 2.3: Commit**

```bash
git add walkthrough-mockup/astro/validator.py
git commit -m "feat: add walkthrough-mockup-astro validator.py"
```

---

## Task 3: Create test fixtures and validate

**Files:**
- Create: `walkthrough-mockup/astro/tests/fixtures/minimal/` (copy from static-html)
- Create: `walkthrough-mockup/astro/tests/expected/minimal/` (pre-fabricated minimal site output)
- Create: `walkthrough-mockup/astro/tests/run_validator.sh`
- Create: `walkthrough-mockup/astro/tests/.gitignore`

The test strategy: build a minimal pre-fabricated HTML site that mimics what
an Astro build would produce from the `minimal` fixture, then run the
validator in structural mode against it.

- [ ] **Step 3.1: Copy input fixture**

```bash
cp -r walkthrough-mockup/static-html/tests/fixtures/minimal \
      walkthrough-mockup/astro/tests/fixtures/minimal
mkdir -p walkthrough-mockup/astro/tests/expected/minimal
```

- [ ] **Step 3.2: Write expected minimal site output**

Create the pre-fabricated expected output files. These mimic what
`astro build` would produce from the `minimal` fixture.

**`walkthrough-mockup/astro/tests/expected/minimal/_astro/style.css`**
```css
:root{--token-color-primary:#0ea5e9;--token-spacing-sm:8px}
```
(non-empty — satisfies the stylesheet check)

**`walkthrough-mockup/astro/tests/expected/minimal/index.html`**
```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Walkthrough</title>
<link rel="stylesheet" href="_astro/style.css">
</head>
<body data-spec-index="true" class="bg-white text-gray-900 font-sans p-4">
<h1>Walkthrough</h1>
<section id="screens"><h2>Screens</h2><ul>
<li><a href="/screen/00_auth/login">Login</a></li>
<li><a href="/screen/00_auth/register">Register</a></li>
</ul></section>
<section id="journeys"><h2>Journeys</h2><ul>
<li><a href="/journey/sign-in">User signs in</a></li>
</ul></section>
<footer><a href="/">← Back to index</a></footer>
</body>
</html>
```

**`walkthrough-mockup/astro/tests/expected/minimal/screen/00_auth/login.html`**
```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Login</title>
<link rel="stylesheet" href="../../_astro/style.css">
</head>
<body data-spec-screen="00_auth/login" class="bg-white text-gray-900 font-sans p-4">
<h1>Login</h1>
<main>
<input name="email-input" aria-label="Email" data-spec-element="email-input" class="border rounded px-2 py-1">
<input name="password-input" aria-label="Password" data-spec-element="password-input" class="border rounded px-2 py-1">
<button data-spec-element="submit-button" class="px-4 py-2 bg-primary text-white rounded">Sign in</button>
</main>
<footer><a href="/">← Back to index</a></footer>
</body>
</html>
```

**`walkthrough-mockup/astro/tests/expected/minimal/screen/00_auth/register.html`**
```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Register</title>
<link rel="stylesheet" href="../../_astro/style.css">
</head>
<body data-spec-screen="00_auth/register" class="bg-white text-gray-900 font-sans p-4">
<h1>Register</h1>
<main></main>
<footer><a href="/">← Back to index</a></footer>
</body>
</html>
```

**`walkthrough-mockup/astro/tests/expected/minimal/journey/sign-in.html`**
```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>User signs in</title>
<link rel="stylesheet" href="../_astro/style.css">
</head>
<body data-spec-journey="sign-in" class="bg-white text-gray-900 font-sans p-4">
<h1>User signs in</h1>
<ol>
<li>
<h2>Step 1: Login</h2>
<a href="/screen/00_auth/login" data-spec-screen="00_auth/login">Open screen</a>
<a href="/">→ Index</a>
</li>
</ol>
<footer><a href="/">← Back to index</a></footer>
</body>
</html>
```

**`walkthrough-mockup/astro/tests/expected/minimal/manifest.json`**
```json
{
  "schema_version": "1.0",
  "renderer": "walkthrough-mockup-astro",
  "renderer_version": "0.1.0",
  "generated_at": "<pinned>",
  "source_root": "experience/screens",
  "screens": [
    {
      "screen_path": "experience/screens/00_auth/login.md",
      "screen_id": "00_auth/login",
      "rendered_html": "screen/00_auth/login.html",
      "implements": ["product-spec/features/00_auth/login.md"],
      "data_entities": ["User"],
      "layout": "experience/screens/00_layout/shell.md",
      "elements": [
        {
          "element_id": "email-input",
          "kind": "input",
          "label": "Email",
          "states": ["default", "focus", "error"],
          "provisional": false,
          "source_anchor": "experience/screens/00_auth/login.md#elements/email-input"
        },
        {
          "element_id": "password-input",
          "kind": "input",
          "label": "Password",
          "states": ["default", "focus", "error"],
          "provisional": false,
          "source_anchor": "experience/screens/00_auth/login.md#elements/password-input"
        },
        {
          "element_id": "submit-button",
          "kind": "button",
          "label": "Sign in",
          "states": ["default", "loading", "disabled", "error"],
          "provisional": false,
          "source_anchor": "experience/screens/00_auth/login.md#elements/submit-button"
        }
      ]
    },
    {
      "screen_path": "experience/screens/00_auth/register.md",
      "screen_id": "00_auth/register",
      "rendered_html": "screen/00_auth/register.html",
      "implements": [],
      "data_entities": [],
      "layout": null,
      "elements": []
    }
  ],
  "journeys": [
    {
      "journey_id": "sign-in",
      "rendered_html": "journey/sign-in.html",
      "source": "experience/journeys/stories.json#sign-in",
      "screen_sequence": [
        "experience/screens/00_auth/login.md"
      ]
    }
  ],
  "features": [
    {
      "feature_path": "product-spec/features/00_auth/login.md",
      "rendered_screens": ["experience/screens/00_auth/login.md"]
    }
  ],
  "warnings": []
}
```

- [ ] **Step 3.3: Write test runner**

**`walkthrough-mockup/astro/tests/run_validator.sh`**
```bash
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SKILL_DIR="$REPO_ROOT/walkthrough-mockup/astro"
SITE_DIR="$SKILL_DIR/tests/expected/minimal"
FIXTURE_SRC="$SKILL_DIR/tests/fixtures/minimal"

echo "=== walkthrough-mockup-astro validator tests ==="

echo ""
echo "1. Structural pass (expected/minimal site-root mode)..."
python "$SKILL_DIR/validator.py" "$SITE_DIR" \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC"
echo "   PASS"

echo ""
echo "2. dist/ check — FAIL expected..."
TMPDIR=$(mktemp -d)
cp -r "$SITE_DIR/." "$TMPDIR/"
mkdir "$TMPDIR/dist"
python "$SKILL_DIR/validator.py" "$TMPDIR" \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC" && echo "   UNEXPECTED PASS" && exit 1 || echo "   FAIL as expected (exit $?)"
rm -rf "$TMPDIR"

echo ""
echo "3. Wrong renderer name — FAIL expected..."
TMPDIR=$(mktemp -d)
cp -r "$SITE_DIR/." "$TMPDIR/"
python -c "
import json, pathlib
p = pathlib.Path('$TMPDIR/manifest.json')
m = json.loads(p.read_text())
m['renderer'] = 'wrong-renderer'
p.write_text(json.dumps(m, indent=2))
"
python "$SKILL_DIR/validator.py" "$TMPDIR" \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC" && echo "   UNEXPECTED PASS" && exit 1 || echo "   FAIL as expected (exit $?)"
rm -rf "$TMPDIR"

echo ""
echo "4. Missing stylesheet — FAIL expected..."
TMPDIR=$(mktemp -d)
cp -r "$SITE_DIR/." "$TMPDIR/"
python -c "
import pathlib
p = pathlib.Path('$TMPDIR/index.html')
text = p.read_text().replace('<link rel=\"stylesheet\" href=\"_astro/style.css\">', '')
p.write_text(text)
"
python "$SKILL_DIR/validator.py" "$TMPDIR" \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC" && echo "   UNEXPECTED PASS" && exit 1 || echo "   FAIL as expected (exit $?)"
rm -rf "$TMPDIR"

echo ""
echo "5. Empty stylesheet — FAIL expected..."
TMPDIR=$(mktemp -d)
cp -r "$SITE_DIR/." "$TMPDIR/"
> "$TMPDIR/_astro/style.css"
python "$SKILL_DIR/validator.py" "$TMPDIR" \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC" && echo "   UNEXPECTED PASS" && exit 1 || echo "   FAIL as expected (exit $?)"
rm -rf "$TMPDIR"

echo ""
echo "=== All tests passed ==="
```

```bash
chmod +x walkthrough-mockup/astro/tests/run_validator.sh
```

**`walkthrough-mockup/astro/tests/.gitignore`**
```
rendered/
```

- [ ] **Step 3.4: Run the test suite**

```bash
cd /mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup
bash walkthrough-mockup/astro/tests/run_validator.sh
```

Expected output:
```
=== walkthrough-mockup-astro validator tests ===

1. Structural pass (expected/minimal site-root mode)...
   PASS

2. dist/ check — FAIL expected...
   FAIL as expected (exit 2)

3. Wrong renderer name — FAIL expected...
   FAIL as expected (exit 2)

4. Missing stylesheet — FAIL expected...
   FAIL as expected (exit 2)

5. Empty stylesheet — FAIL expected...
   FAIL as expected (exit 2)

=== All tests passed ===
```

- [ ] **Step 3.5: Commit**

```bash
git add walkthrough-mockup/astro/tests/
git commit -m "test: add walkthrough-mockup-astro validator tests and fixtures"
```

---

## Task 4: Update DOMAIN.md and register skill

**Files:**
- Modify: `walkthrough-mockup/DOMAIN.md`

- [ ] **Step 4.1: Add astro skill to DOMAIN.md**

Edit `walkthrough-mockup/DOMAIN.md`. Add after the `static-html` entry:

```markdown
- **walkthrough-mockup-astro** (`astro/`) — Tailwind-styled Astro static site walkthrough — one HTML file per screen and per journey, built via `bun astro build`, plus `manifest.json`. Astro source committed alongside built output. Best for standard-app tier.
```

Also update the `description:` in the YAML frontmatter to include `astro`:

```yaml
description: "Clickable application walkthrough: text · static-html · astro · lit · framework"
```

- [ ] **Step 4.2: Commit**

```bash
git add walkthrough-mockup/DOMAIN.md
git commit -m "docs: register walkthrough-mockup-astro in DOMAIN.md"
```

---

## Acceptance criteria

- [ ] `walkthrough-mockup/astro/SKILL.md` exists with `name: walkthrough-mockup-astro` frontmatter
- [ ] `walkthrough-mockup/astro/validator.py --help` exits 0
- [ ] `bash walkthrough-mockup/astro/tests/run_validator.sh` exits 0 with all 5 tests passing
- [ ] `walkthrough-mockup/DOMAIN.md` lists `walkthrough-mockup-astro`
- [ ] `git log --oneline -4` shows 4 clean commits
