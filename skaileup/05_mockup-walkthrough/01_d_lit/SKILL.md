---
name: mockup-walkthrough-lit
description: "Use when stakeholders need a clickable Lit web-components walkthrough of the application — built with Vite, rendered as custom elements whose built HTML is openable directly in a browser AND embeddable into a host page. Generates one HTML file per screen and per journey, plus a manifest.json that the mockup-feedback cluster reads. Best for standard-app tier when the mockup must drop into an existing host shell."
metadata:
  version: "0.1.0"
  tags:
    - walkthrough
    - mockup
    - lit
    - web-components
    - embeddable
    - standard-app
    - frontend
    - prototype
    - data-spec
  stage: alpha
  artifacts:
    requires:
      - id: screens
        gate: hard
      - id: journeys
        gate: hard
      - id: brand-tokens
        gate: hard
    consumes:
      - id: features
        gate: soft
    produces:
      - id: walkthrough
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
        description: "Brand tokens injected as CSS custom properties in the built shell"
      - path: "product-spec/features"
        gate: soft
        description: "Feature files linked from manifest.json for traceability; absence is a warning"
        min_entries: 1
    reads:
      - path: "experience/screens/00_layout/shell.md"
        description: "Optional shared layout reference; if present, used as a reference for the <screen-view> shell wrapper"
  produces:
    - path: "_concept/mockup-walkthrough/lit"
      description: "Vite + Lit project source + built site: index.html, screen/<group>/<name>.html, journey/<id>.html, manifest.json"
---

# Walkthrough Mockup — Lit

## Overview

Lit web-components variant of the walkthrough mockup cluster. Consumes the same
four inputs as `mockup-walkthrough-static-html` (screen specs, journey
definitions, brand tokens, feature files); produces a Vite-built site of Lit
custom elements at `_concept/mockup-walkthrough/lit/`.

Every rendered DOM node carries the same `data-spec-*` attributes as the
static-html variant so the `mockup-feedback-*` cluster can resolve clicks
identically across renderers. The `manifest.json` schema is identical — only
`renderer: "mockup-walkthrough-lit"` differs.

**Embeddable angle — decision recorded.** `docs/devlog/mockup-design.md` § 1
classes this renderer as "Lit web components, embeddable". The built custom
elements (`<screen-view>`, `<journey-view>`, `<index-view>`) are self-contained
and can be dropped into a host page (e.g. a forge-concept walkthrough shell)
without an iframe: the host imports the bundled component JS and mounts the tag.
This is the differentiator over astro (which emits a standalone static site
only). For the embed path to work the components MUST render into **light DOM**
(see Renderer Contract) so the host's `mockup-feedback-*` overlay can query the
`data-spec-*` nodes.

**Two-mode behaviour — decision recorded.** The agent detects whether a Vite +
Lit project already exists by checking for
`_concept/mockup-walkthrough/lit/vite.config.js`:

- **Init** (absent): scaffold project skeleton (vite.config.js, package.json,
  Lit component templates, per-page HTML entries) → generate `specs.json` +
  `global.css` → `bun install` → `bun run build` → write `manifest.json`
- **Update** (present): regenerate `specs.json` + `global.css` only →
  `bun run build` → rewrite `manifest.json`

On update runs the agent NEVER touches `vite.config.js`, `package.json`, the
Lit component source under `src/components/`, or the per-page HTML entry files —
those belong to the user.

**Generation approach — decision recorded.** Agent-direct: the agent reads
screen specs and derives `src/data/specs.json` plus each per-page HTML entry
inline (no persistent generator script). Each page HTML is generated directly
from `specs.json` by the agent with the custom-element markup inlined, so a
build step is not strictly required to produce queryable light-DOM HTML — the
Vite build only bundles/optimises. Same agent-direct pattern as static-html's
Python renderer and astro's inline derivation.

## Renderer Contract

**Public contract.** Every `data-spec-*` attribute MUST be emitted on the same
DOM position as `mockup-walkthrough-static-html` so the `mockup-feedback-*`
cluster resolves clicks identically across renderers.

### Light DOM — the key Lit-specific risk

LitElement defaults to **Shadow DOM**. Shadow DOM would encapsulate every
rendered node so the `mockup-feedback-*` cluster's `document.querySelectorAll('[data-spec-element]')`
returns nothing — the `data-spec-*` attributes would be hidden behind the shadow
boundary. Therefore every Lit component in this renderer MUST override
`createRenderRoot()` to render into **light DOM**:

```js
createRenderRoot() { return this; }
```

With light-DOM rendering, every `data-spec-screen`, `data-spec-element`,
`data-spec-provisional`, `data-spec-journey`, and `data-spec-index` attribute
lands on a queryable light-DOM node exactly as in static-html / astro. This is
the single most important Lit-specific invariant; the validator and CHECKLIST
both assert it.

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
fallback" section. The Lit `<screen-view>` component emits
`data-spec-provisional="true"` on any element where `element.provisional === true`.
There is NO separate top-level `auto_slugged[]` array — `provisional: true` lives
on the element object itself. The `kind: "auto_slugged"` warning entry in
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

Generated under `_concept/mockup-walkthrough/lit/`:

| Path | Description |
|---|---|
| `index.html` | Router/menu — `<body data-spec-index="true">`. Lists every screen and journey. |
| `screen/<group>/<name>.html` | One file per screen. `<body data-spec-screen="<screen_id>">`. |
| `journey/<id>.html` | One file per journey. `<body data-spec-journey="<id>">`. Walks through screens in order. |
| `manifest.json` | Machine-readable index for `mockup-feedback-annotate`. |

## Vite + Lit project layout

```
_concept/mockup-walkthrough/lit/             ← project root (committed)
├── src/
│   ├── data/
│   │   └── specs.json                       ← regenerated each run
│   ├── components/
│   │   ├── screen-view.js                   ← <screen-view> LitElement, light DOM (scaffolded once)
│   │   ├── journey-view.js                  ← <journey-view> LitElement, light DOM (scaffolded once)
│   │   └── index-view.js                    ← <index-view> LitElement, light DOM (scaffolded once)
│   ├── pages/
│   │   ├── index.html                       ← site root entry, body data-spec-index="true"
│   │   ├── screen/<group>/<name>.html       ← per-screen entry, body data-spec-screen="<id>"
│   │   └── journey/<id>.html                ← per-journey entry, body data-spec-journey="<id>"
│   └── styles/
│       └── global.css                       ← :root token vars (regenerated each run)
├── vite.config.js                           ← multi-page input, outDir='.', emptyOutDir=false (scaffolded once)
├── package.json                             ← lit + vite deps (scaffolded once)
├── assets/                                  ← hashed CSS/JS chunks from build (committed)
├── index.html                              ← built output
├── screen/<group>/<name>.html              ← built output
├── journey/<id>.html                       ← built output
└── manifest.json                           ← written after build, not by Vite
```

Per-page HTML entry files mount the matching custom element and set the body
`data-spec-*` marker. Because the components render into light DOM, the built
HTML carries every `data-spec-*` attribute on queryable nodes regardless of
whether the page is opened standalone or embedded into a host shell.

## `specs.json` shape

`specs.json` bridges source artefacts to the Lit components at mount time.

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

Build `manifest.json` from the in-memory model using the pinned shape directly
(not by serialising `specs.json`).

## ROLE / READS / WRITES / REFERENCES

ROLE  Walkthrough Lit renderer — converts screen specs + journey definitions
      + tokens into a Vite-built site of light-DOM Lit web components whose DOM
      is annotatable end-to-end via the same data-spec-* contract as static-html,
      and which is embeddable into a host page.

READS
  experience/screens/**/*.md            — screen specs (frontmatter + body)
  experience/journeys/stories.json      — journey definitions
  design/tokens.json                    — brand tokens
  ? product-spec/features/**/*.md       — feature traceability (soft)
  ? experience/screens/00_layout/shell.md — shared layout reference (soft)
  ? _concept/mockup-walkthrough/lit/vite.config.js — mode detection

WRITES
  _concept/mockup-walkthrough/lit/src/data/specs.json          (every run)
  _concept/mockup-walkthrough/lit/src/styles/global.css        (every run)
  _concept/mockup-walkthrough/lit/vite.config.js               (init only)
  _concept/mockup-walkthrough/lit/package.json                 (init only)
  _concept/mockup-walkthrough/lit/src/components/screen-view.js (init only)
  _concept/mockup-walkthrough/lit/src/components/journey-view.js (init only)
  _concept/mockup-walkthrough/lit/src/components/index-view.js  (init only)
  _concept/mockup-walkthrough/lit/src/pages/index.html         (init only)
  _concept/mockup-walkthrough/lit/src/pages/screen/<group>/<name>.html (every run — agent-direct)
  _concept/mockup-walkthrough/lit/src/pages/journey/<id>.html  (every run — agent-direct)
  _concept/mockup-walkthrough/lit/index.html                   (built — every run)
  _concept/mockup-walkthrough/lit/screen/<group>/<name>.html   (built — every run)
  _concept/mockup-walkthrough/lit/journey/<id>.html            (built — every run)
  _concept/mockup-walkthrough/lit/manifest.json                (every run)

REFERENCES
  contracts/elements_block.md           — elements: schema + renderer contract
  contracts/frontmatter.md              — screen + feature + stories shapes
  contracts/asset_frontmatter.md        — this SKILL.md's own frontmatter shape
  contracts/skill_grammar.md            — DSL keywords used in this body
  contracts/iron_laws.md                — non-negotiable cross-skill constraints
  contracts/scripts/validator_lib.py    — used by mockup-walkthrough/lit/validator.py
  docs/devlog/mockup-design.md § 4, § 6           — shared input contract + hybrid ID strategy
  mockup-walkthrough/static-html/SKILL.md — sibling skill (contract anchor)
  mockup-walkthrough/astro/SKILL.md     — sibling skill (structural mirror)

## STEP 1: Read feedback devlog (preserved intent)

- If `_concept/_feedback/devlog.md` exists, read it.
- Filter entries where `target_paths` overlaps files under
  `_concept/mockup-walkthrough/lit/`.
- For each matching entry: extract `patch_summary` as a preserved-intent constraint.
  Do not undo these during regeneration.
- If no devlog or no matching entries: proceed with no constraints.

## STEP 2: Read inputs

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
  fall back to the `<screen-view>` default shell.
- **`product-spec/features/` empty or missing** → soft gate,
  `kind: "missing_feature"`, continue. `manifest.features[]` → `[]`.
- **Zero journeys** → render "No journeys defined",
  `kind: "no_journeys"`.

## STEP 3: Detect mode

Check `_concept/mockup-walkthrough/lit/vite.config.js`.
- Absent → **Init** (proceed to STEP 4).
- Present → **Update** (skip STEP 4, proceed directly to STEP 5).

## STEP 4: Scaffold project (Init only)

Write the following files. Do NOT write these on update runs.

### `_concept/mockup-walkthrough/lit/package.json`

```json
{
  "name": "mockup-walkthrough-lit",
  "type": "module",
  "scripts": {
    "build": "vite build",
    "dev": "vite",
    "preview": "vite preview"
  },
  "dependencies": {
    "lit": "^3.0.0"
  },
  "devDependencies": {
    "vite": "^5.0.0"
  }
}
```

### `_concept/mockup-walkthrough/lit/vite.config.js`

Multi-page build: one Rollup input per built HTML page. `outDir: '.'` with
`emptyOutDir: false` so the build emits `index.html`, `screen/...`, and
`journey/...` next to the source without wiping the committed project.

```js
import { defineConfig } from 'vite';
import { globSync } from 'glob';

// One input per per-page HTML entry under src/pages/.
const inputs = Object.fromEntries(
  globSync('src/pages/**/*.html').map((f) => [
    f.replace(/^src\/pages\//, '').replace(/\.html$/, ''),
    f,
  ]),
);

export default defineConfig({
  root: 'src/pages',
  build: {
    outDir: '../../',
    emptyOutDir: false,
    rollupOptions: { input: inputs },
  },
});
```

### `_concept/mockup-walkthrough/lit/src/components/screen-view.js`

The `<screen-view>` element renders the screen's elements into **light DOM**.
`createRenderRoot() { return this; }` is mandatory — without it the
`data-spec-*` nodes hide behind the shadow boundary.

```js
import { LitElement, html, nothing } from 'lit';
import specs from '../data/specs.json';

const TAG = {
  input: (el, prov) =>
    html`<input name=${el.element_id} aria-label=${el.label}
      data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      class="border rounded px-2 py-1" />`,
  button: (el, prov) =>
    html`<button data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      class="btn-primary">${el.label}</button>`,
  link: (el, prov) =>
    html`<a href="#" data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      class="link">${el.label}</a>`,
  image: (el, prov) =>
    html`<img src="#" alt=${el.label} data-spec-element=${el.element_id}
      ?data-spec-provisional=${prov} />`,
  text: (el, prov) =>
    html`<span data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      >${el.label}</span>`,
  region: (el, prov) =>
    html`<section data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      ><h3>${el.label}</h3></section>`,
  list: (el, prov) =>
    html`<ul data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      ><li>…</li></ul>`,
  form: (el, prov) =>
    html`<form data-spec-element=${el.element_id} ?data-spec-provisional=${prov}></form>`,
  nav: (el, prov) =>
    html`<nav data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      ><ul><li>…</li></ul></nav>`,
  media: (el, prov) =>
    html`<figure data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      ><figcaption>${el.label}</figcaption></figure>`,
  custom: (el, prov) =>
    html`<div data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      >${el.label}</div>`,
};

export class ScreenView extends LitElement {
  static properties = { screenId: { type: String, attribute: 'screen-id' } };
  // Light DOM — data-spec-* MUST be queryable by mockup-feedback-*.
  createRenderRoot() { return this; }

  get screen() {
    return specs.screens.find((s) => s.screen_id === this.screenId);
  }

  renderElement(el) {
    const prov = !!el.provisional;
    const base = (TAG[el.kind] ?? TAG.custom)(el, prov);
    const states = (el.states || [])
      .filter((s) => s !== 'default')
      .map((s) => html`<span class="state-${s}">${el.label} [${s}]</span>`);
    return html`${base}${states}`;
  }

  render() {
    const screen = this.screen;
    if (!screen) return html`<p>Unknown screen: ${this.screenId}</p>`;
    return html`
      <h1>${screen.title || screen.screen_id}</h1>
      <main class="space-y-4">
        ${screen.elements.map((el) => this.renderElement(el))}
      </main>
      <section class="meta">
        <p>Journeys:
          ${screen.journeys.length === 0
            ? 'none'
            : screen.journeys.map(
                (jid) => html`<a href=${`../../journey/${jid}.html`}>${jid}</a> `,
              )}
        </p>
      </section>
    `;
  }
}
customElements.define('screen-view', ScreenView);
```

### `_concept/mockup-walkthrough/lit/src/components/journey-view.js`

```js
import { LitElement, html, nothing } from 'lit';
import specs from '../data/specs.json';

export class JourneyView extends LitElement {
  static properties = { journeyId: { type: String, attribute: 'journey-id' } };
  createRenderRoot() { return this; } // light DOM

  get journey() {
    return specs.journeys.find((j) => j.journey_id === this.journeyId);
  }
  findScreen(id) {
    return specs.screens.find((s) => s.screen_id === id);
  }

  render() {
    const journey = this.journey;
    if (!journey) return html`<p>Unknown journey: ${this.journeyId}</p>`;
    const seq = journey.screen_sequence;
    return html`
      <h1>${journey.title || journey.journey_id}</h1>
      ${journey.description ? html`<p class="muted">${journey.description}</p>` : nothing}
      <ol class="steps">
        ${seq.map((sid, i) => {
          const screen = this.findScreen(sid);
          const isLast = i === seq.length - 1;
          if (!screen) {
            return html`<li class="journey-step-missing">
              <span data-spec-screen=${sid}>Missing screen: ${sid}</span>
            </li>`;
          }
          return html`<li>
            <h2>Step ${i + 1}: ${screen.title || sid}</h2>
            <a href=${`../screen/${sid}.html`} data-spec-screen=${sid}>Open screen</a>
            ${isLast
              ? html`<a class="next" href="../index.html">→ Index</a>`
              : html`<a class="next" href=${`../screen/${seq[i + 1]}.html`}>Next →</a>`}
          </li>`;
        })}
      </ol>
    `;
  }
}
customElements.define('journey-view', JourneyView);
```

### `_concept/mockup-walkthrough/lit/src/components/index-view.js`

```js
import { LitElement, html } from 'lit';
import specs from '../data/specs.json';

export class IndexView extends LitElement {
  createRenderRoot() { return this; } // light DOM

  render() {
    return html`
      <h1>Walkthrough</h1>
      <section id="screens">
        <h2>Screens</h2>
        <ul>
          ${specs.screens.map(
            (s) => html`<li><a href=${`screen/${s.screen_id}.html`}
              >${s.title || s.screen_id}</a></li>`,
          )}
        </ul>
      </section>
      <section id="journeys">
        <h2>Journeys</h2>
        ${specs.journeys.length === 0
          ? html`<p>No journeys defined</p>`
          : html`<ul>
              ${specs.journeys.map(
                (j) => html`<li><a href=${`journey/${j.journey_id}.html`}
                  >${j.title || j.journey_id}</a></li>`,
              )}
            </ul>`}
      </section>
    `;
  }
}
customElements.define('index-view', IndexView);
```

### Per-page HTML entries

The agent generates one HTML entry per page directly from `specs.json` (STEP 5).
Each sets the body `data-spec-*` marker and mounts the matching custom element.
Because the components render light DOM, the mounted markup carries the
`data-spec-*` attributes on queryable nodes. `src/pages/index.html` is scaffolded
once on init; the per-screen and per-journey entries are regenerated every run
(agent-direct — they enumerate the current screen/journey set).

Example `src/pages/screen/01_user_auth/login.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Login</title>
    <link rel="stylesheet" href="/styles/global.css" />
    <script type="module" src="/components/screen-view.js"></script>
  </head>
  <body data-spec-screen="01_user_auth/login">
    <screen-view screen-id="01_user_auth/login"></screen-view>
    <footer><a href="/index.html">← Back to index</a></footer>
  </body>
</html>
```

`src/pages/index.html` mounts `<index-view>` with `<body data-spec-index="true">`;
`src/pages/journey/<id>.html` mounts `<journey-view journey-id="<id>">` with
`<body data-spec-journey="<id>">`.

## STEP 5: Generate `specs.json`, `global.css`, and per-page HTML (both modes)

Write `src/data/specs.json` derived from the in-memory model. Schema as shown in
the `specs.json` shape section above. Overwrite unconditionally.

Regenerate every per-page HTML entry under `src/pages/screen/**` and
`src/pages/journey/**` from the current screen/journey set (agent-direct). Each
sets the correct body `data-spec-*` marker and mounts the matching custom
element. This is what makes the built HTML carry queryable `data-spec-*` nodes
without depending on client-side hydration.

Write `src/styles/global.css`:

```css
:root {
  /* one line per flattened token_var */
  --token-<name>: <value>;
}

/* minimal element styling keyed to token vars */
.btn-primary { background: var(--token-color-primary); color: #fff; }
```

Overwrite unconditionally. This file is agent-managed every run.

On update runs only: compare the count of `--token-*` keys in the freshly
derived in-memory model vs. the CSS var declarations in the existing
`global.css` before overwriting. If counts differ, append
`kind: "stale_token_css"` to `warnings[]`.

## STEP 6: Build

Run from `_concept/mockup-walkthrough/lit/`:

```bash
bun run build
```

On non-zero exit: print full stderr and exit non-zero. Do not write
`manifest.json`.

After build: verify `dist/` does NOT exist under the project root. If it does:
fail with "vite.config.js outDir misconfigured — dist/ must not exist".

The agent-direct per-page HTML already carries the `data-spec-*` attributes in
light DOM, so the built output is queryable whether or not the Vite-bundled
component JS hydrates.

## STEP 7: Write `manifest.json`

Emit the pinned schema. Build it from the in-memory model — NOT by serialising
`specs.json`. Template-only fields from `specs.json` (`screens[].title`,
`screens[].group`, `screens[].journeys[]`, `journeys[].title`,
`journeys[].description`) MUST NOT appear in `manifest.json`.

```json
{
  "schema_version": "1.0",
  "renderer": "mockup-walkthrough-lit",
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

`renderer_version` matches the `metadata.version` in this SKILL.md's frontmatter
(`"0.1.0"`).

## STEP 8: Validate

Run from the repo root:

```bash
python mockup-walkthrough/lit/validator.py _concept/mockup-walkthrough/lit
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
| `layout:` reference to non-existent file | `kind: "missing_layout"`, fall back to `<screen-view>` default |
| Auto-slug collision | `kind: "auto_slug_collision"`, suffix auto id with `-2`, `-3`, … |

### Lit-specific

| Condition | Behaviour |
|---|---|
| `bun install` exits non-zero | Fail loudly with stderr; do not build |
| `bun run build` exits non-zero | Fail loudly with stderr; do not write `manifest.json` |
| `dist/` exists after build | Fail: "vite.config.js outDir misconfigured — dist/ must not exist" |
| A component omits `createRenderRoot() { return this; }` (Shadow DOM leak) | Fail: data-spec-* would be unqueryable; the validator asserts light DOM |
| Token count differs from CSS var count (update runs only) | `kind: "stale_token_css"`; user must extend `global.css` token block manually |

### `warnings[].kind` enum

`auto_slugged`, `auto_slug_collision`, `missing_layout`, `missing_feature`,
`unknown_element_kind`, `missing_screen`, `missing_screen_sequence`,
`no_journeys`, `stale_token_css`

`stale_token_css` is the only Lit-specific addition.

## MUST / NEVER

MUST  emit data-spec-screen on every screen `<body>`
MUST  emit data-spec-element on every annotatable child node
MUST  emit data-spec-provisional="true" on auto-slugged element nodes
MUST  emit data-spec-journey="<id>" on every journey `<body>`
MUST  emit data-spec-index="true" on index.html `<body>`
MUST  render every Lit component into light DOM via `createRenderRoot() { return this; }`
MUST  write manifest.json conforming to pinned schema (schema_version: "1.0")
MUST  sort manifest arrays lexicographically
MUST  set emptyOutDir: false in vite.config.js
MUST  set build.outDir to the project root (built files next to source)
MUST  write specs.json, global.css, and per-page HTML before running bun run build
MUST  regenerate global.css and per-page screen/journey HTML on every run (agent-managed)
MUST  reference components/styles with relative URLs so built pages are openable and embeddable

NEVER use Shadow DOM in any walkthrough component — it hides data-spec-* from the feedback overlay
NEVER regenerate vite.config.js, package.json, or src/components/*.js on update runs
NEVER create a dist/ subdirectory — outDir must be the project root
NEVER emit data-spec-* attributes outside the pinned table
NEVER mutate source files (experience/screens/**, stories.json, tokens.json, features/**)
NEVER inject journey-step navigation into screen/**/*.html
NEVER inline absolute filesystem paths in manifest.json
NEVER use a separate auto_slugged[] array — set provisional: true on the element object (the kind: "auto_slugged" warning entry in manifest.warnings[] is still required per the auto-slug step)

## CHECKLIST

- [ ] `_concept/mockup-walkthrough/lit/index.html` exists
- [ ] `_concept/mockup-walkthrough/lit/manifest.json` exists and parses as JSON
- [ ] `manifest.schema_version == "1.0"` and `manifest.renderer == "mockup-walkthrough-lit"`
- [ ] One `screen/<group>/<name>.html` per screen file under `experience/screens/`
- [ ] One `journey/<id>.html` per journey in `stories.json`
- [ ] Every Lit component overrides `createRenderRoot()` to return `this` (light DOM)
- [ ] Every `<body>` in `screen/**/*.html` has `data-spec-screen`
- [ ] Every annotatable node in `screen/**/*.html` has `data-spec-element` on a light-DOM node
- [ ] Every auto-slugged element node also has `data-spec-provisional="true"`
- [ ] Every `<body>` in `journey/**/*.html` has `data-spec-journey`
- [ ] `index.html` `<body>` has `data-spec-index="true"`
- [ ] No `dist/` subdirectory under `_concept/mockup-walkthrough/lit/`
- [ ] At least one `<link rel="stylesheet">` in `index.html` and referenced CSS file is non-empty
- [ ] Validator (`mockup-walkthrough/lit/validator.py`) exits 0

EMIT  [mockup-walkthrough-lit] started run_id=<uuid>
EMIT  [mockup-walkthrough-lit] checkpoint screens=<N> journeys=<M>
EMIT  [mockup-walkthrough-lit] completed run_id=<uuid> screens=<N> journeys=<M> warnings=<W>
