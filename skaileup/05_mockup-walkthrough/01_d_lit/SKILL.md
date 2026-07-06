---
name: mockup-walkthrough-lit
description: "Use when stakeholders need a clickable Lit web-components walkthrough of the application — built with Vite, rendered as custom elements whose built HTML is openable directly in a browser AND embeddable into a host page. Generates one HTML file per screen and per journey, plus a manifest.json that the mockup-feedback cluster reads. Best for appbuilder-standard tier when the mockup must drop into an existing host shell."
metadata:
  version: "0.2.0"
  tags:
    - walkthrough
    - mockup
    - lit
    - web-components
    - embeddable
    - appbuilder-standard
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
      - path: "experience/journeys/stories.yaml"
        gate: hard
        description: "Journey definitions drive the journey/<id>.html sequencing"
      - path: "design/tokens.json"
        gate: hard
        description: "Brand tokens injected as CSS custom properties in the built shell"
      - path: "experience/features"
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

Lit web-components variant of walkthrough mockup cluster. Consumes same four
inputs as `mockup-walkthrough-static-html` (screen specs, journey
definitions, brand tokens, feature files); produces Vite-built site of Lit
custom elements at `_concept/mockup-walkthrough/lit/`.

Every rendered DOM node carries same `data-spec-*` attributes as static-html
variant so `mockup-feedback-*` cluster resolves clicks identically across
renderers. `manifest.json` schema is identical — only
`renderer: "mockup-walkthrough-lit"` differs.

**Embeddable angle — decision recorded.** `docs/devlog/mockup-design.md` § 1
classes this renderer as "Lit web components, embeddable". Built custom
elements (`<screen-view>`, `<journey-view>`, `<index-view>`) are self-contained,
droppable into host page (e.g. forge-concept walkthrough shell) without
iframe: host imports bundled component JS, mounts tag. This is differentiator
over astro (which emits standalone static site only). For embed path to work,
components MUST render into **light DOM** (see Renderer Contract) so host's
`mockup-feedback-*` overlay can query `data-spec-*` nodes.

**Two-mode behaviour — decision recorded.** Agent detects whether Vite + Lit
project already exists by checking for
`_concept/mockup-walkthrough/lit/vite.config.js`:

- **Init** (absent): scaffold project skeleton (vite.config.js, package.json,
  Lit component templates, per-page HTML entries) → generate `specs.json` +
  `global.css` → `bun install` → `bun run build` → write `manifest.json`
- **Update** (present): regenerate `specs.json` + `global.css` only →
  check the scaffold isn't stale (§ `stale_scaffold` check, STEP 3) →
  `bun run build` → rewrite `manifest.json`

On update runs, agent NEVER touches `vite.config.js`, `package.json`, Lit
component source under `src/components/`, or per-page HTML entry files —
those belong to user.

**Generation approach — decision recorded.** Agent-direct: agent reads screen
specs, derives `src/data/specs.json` plus each per-page HTML entry inline (no
persistent generator script). Each page HTML generated directly from
`specs.json` by agent with custom-element markup inlined, so build step isn't
strictly required to produce queryable light-DOM HTML — Vite build only
bundles/optimises. Same agent-direct pattern as static-html's Python renderer
and astro's inline derivation.

## Renderer Contract

**Public contract.** Every `data-spec-*` attribute MUST be emitted on same
DOM position as `mockup-walkthrough-static-html` so `mockup-feedback-*`
cluster resolves clicks identically across renderers.

### Light DOM — the key Lit-specific risk

LitElement defaults to **Shadow DOM**. Shadow DOM would encapsulate every
rendered node so `mockup-feedback-*` cluster's `document.querySelectorAll('[data-spec-element]')`
returns nothing — `data-spec-*` attributes hidden behind shadow boundary.
Therefore every Lit component in this renderer MUST override
`createRenderRoot()` to render into **light DOM**:

```js
createRenderRoot() { return this; }
```

With light-DOM rendering, every `data-spec-screen`, `data-spec-element`,
`data-spec-provisional`, `data-spec-journey`, and `data-spec-index` attribute
lands on queryable light-DOM node exactly as in static-html / astro. This is
single most important Lit-specific invariant; validator and CHECKLIST both
assert it.

Implements shared walkthrough renderer contract — `contracts/walkthrough_renderer.md`
(schema_version "1.2"): data-spec-* attribute table, screen_id vs screen_path,
kind → DOM tag mapping (incl. `target` resolution, `table`, `tabs`, populated
`list`/`select`), § Target resolution, § App-shell navigation, § Auto-slug
fallback (narrowed source set), § Spec reference panel, manifest schema +
field semantics, warnings[].kind enum, shared error handling,
screen-in-multiple-journeys rule, shared MUST/NEVER. Read before rendering;
pinned, MUST NOT be restated here.

Renderer-specific manifest values: `renderer: "mockup-walkthrough-lit"`,
`renderer_version:` this SKILL.md's `metadata.version`.

Lit-specific: `<screen-view>` component emits `data-spec-provisional="true"`
where `element.provisional === true`; NO separate top-level `auto_slugged[]`
array — `provisional: true` lives on element object.

**Lit-specific corollary of the contract (not a deviation from it): all
target/content resolution happens in STEP 2, not in the component.** Same
architectural constraint astro's renderer documented, for the same reason:
`src/components/screen-view.js` is scaffolded once at project-init time (§
Two-mode behaviour above) and is NEVER rewritten on update runs — so, exactly
like astro's `.astro` templates, every value the component's `render()` would
otherwise need to *resolve* (a `target:` → href, an auto-slugged item's id,
the spec panel's rendered body, the app-nav's grouped shape) MUST already be
sitting fully-resolved in `specs.json` before the component ever runs. The
`TAG` map only interpolates (`el.href ?? '#'`); it never derives a target or
an id itself. See § `specs.json` shape and STEP 2 below. The one place lit's
runtime differs from astro's is *when* the resolved data gets interpolated —
astro's build produces static HTML at build time, while lit's `render()`
executes client-side, in the browser, when the custom element upgrades (Vite
inlines the current `specs.json` into the bundled JS at `bun run build` time,
so a fresh build is still required to pick up a regenerated `specs.json` —
this is why STEP 6 always re-runs the build after STEP 5 rewrites
`specs.json`). This distinction doesn't change the STEP-2-only-resolution
rule itself, only its execution context.

**Lit's hrefs are relative, `.html`-suffixed** (`../<group>/<name>.html` from
a screen page, `screen/<group>/<name>.html` from `index.html`), matching
static-html's file-relative scheme and this renderer's own pre-existing
`journey-view.js`/`index-view.js` precedent (`../screen/${sid}.html`,
`screen/${s.screen_id}.html`) — NOT astro's root-relative, extension-less
clean-URL scheme. Astro's scheme fits its `build.format: 'file'` +
`getStaticPaths()` slug routing; lit's Vite multi-page build emits one real
`.html` file per page with no router, so relative file-to-file links are the
native fit here, same as static-html.

## Inputs

Same four input shapes as `mockup-walkthrough-static-html`:

| Path | Shape |
|---|---|
| `experience/screens/<group>/<screen>.md` | Markdown + YAML frontmatter with optional `elements:` block per `contracts/elements_block.md` |
| `experience/journeys/stories.yaml` | JSON `{ "journeys": [{ "id", "title", "description", "screen_sequence" }] }` |
| `design/tokens.json` | Token tree. Flattened to CSS custom properties (`--token-<dotted-path-with-hyphens>`). |
| `experience/features/<group>/<feature>.md` | Used only for `manifest.json#features`; not rendered as HTML. |

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

Per-page HTML entry files mount matching custom element, set body
`data-spec-*` marker. Because components render into light DOM, built HTML
carries every `data-spec-*` attribute on queryable nodes regardless of
whether page opened standalone or embedded into host shell.

## `specs.json` shape

`specs.json` bridges source artefacts to the Lit components at mount time.
Every value the component's `render()` would otherwise need to *resolve* — a
target's href, an item's derived id, a screen's rendered spec body — is
pre-resolved here (§ Renderer Contract above); `screen-view.js` only
interpolates.

```json
{
  "app_nav": {
    "element_id": "app-nav",
    "provisional": true,
    "groups": [
      {
        "label": "auth",
        "items": [
          {
            "label": "login",
            "href": "screen/01_user_auth/login.html",
            "element_id": "app-nav-1",
            "provisional": true
          }
        ]
      }
    ]
  },
  "screens": [
    {
      "screen_id": "01_user_auth/login",
      "screen_path": "experience/screens/01_user_auth/login.md",
      "rendered_html": "screen/01_user_auth/login.html",
      "group": "01_user_auth",
      "title": "Login",
      "implements": ["experience/features/01_user_auth/login.md"],
      "data_entities": ["User"],
      "layout": "experience/screens/00_layout/shell.md",
      "body_html": "<p>Intro prose…</p><h3>Purpose</h3><p>…</p>",
      "app_nav": {
        "element_id": "app-nav",
        "provisional": true,
        "groups": [
          {
            "label": "auth",
            "items": [
              {
                "label": "login",
                "href": "screen/01_user_auth/login.html",
                "element_id": "app-nav-1",
                "provisional": true
              }
            ]
          }
        ]
      },
      "elements": [
        {
          "element_id": "submit-button",
          "kind": "button",
          "label": "Sign in",
          "states": ["default", "loading"],
          "provisional": false,
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/submit-button"
        },
        {
          "element_id": "go-register",
          "kind": "link",
          "label": "Create an account",
          "states": ["default"],
          "provisional": false,
          "target": "01_user_auth/register",
          "href": "../01_user_auth/register.html",
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/go-register"
        },
        {
          "element_id": "recent-signins",
          "kind": "table",
          "label": "Recent sign-ins",
          "states": ["default"],
          "provisional": false,
          "columns": ["Name", "Email"],
          "sample_rows": [["Lena M.", "lena@example.com"]],
          "row_target": "01_user_auth/verify_email",
          "row_href": "../01_user_auth/verify_email.html",
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/recent-signins"
        },
        {
          "element_id": "signup-benefits",
          "kind": "list",
          "label": "Why join",
          "states": ["default"],
          "provisional": false,
          "items": [
            {
              "label": "See your login screen",
              "target": "01_user_auth/login",
              "href": "../01_user_auth/login.html",
              "element_id": "see-your-login-screen",
              "provisional": true
            },
            {
              "label": "Get onboarding tips",
              "element_id": "get-onboarding-tips",
              "provisional": true
            }
          ],
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/signup-benefits"
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
      "source": "experience/journeys/stories.yaml#user-signs-in",
      "screen_sequence": ["01_user_auth/login", "02_dashboard/home"]
    }
  ],
  "token_vars": {
    "--token-color-primary": "#0ea5e9",
    "--token-spacing-sm": "8px"
  },
  "features": [
    {
      "feature_path": "experience/features/01_user_auth/login.md",
      "rendered_screens": ["experience/screens/01_user_auth/login.md"]
    }
  ]
}
```

Every `items[]` entry (whether the schema's bare-string shorthand or the
`{label, target?}` dict form) is normalised in `specs.json` to always carry
its own resolved `element_id` and `provisional` — this is the § Auto-slug
fallback "items[] id derivation" rule (see STEP 2 below) executed once at
generation time so `screen-view.js` never has to re-derive it. `href` is
present on an item only when the item declares a `target`.

`app_nav` is a single object shaped `{element_id, provisional, groups:
[{label, items: [{label, href, element_id, provisional}]}]}` — the
shell-authoritative case emits exactly one unlabeled group (no subdivision,
authored order verbatim); the derived-default case emits one group per
screen `<group>` directory (§ App-shell navigation, STEP 2). Every screen
carries its own `app_nav` field set to that same shared object, since every
screen renders the identical generated nav (same design astro's `specs.json`
uses for the same reason).

**specs.json → manifest.json projection.** `specs.json` carries
template-convenience fields that MUST NOT be copied to `manifest.json`:
- `screens[].title`, `screens[].group`, `screens[].journeys[]`, `screens[].body_html`, `screens[].app_nav`
- `screens[].elements[].href`, `screens[].elements[].row_href`
- `screens[].elements[].items[].element_id`, `screens[].elements[].items[].provisional`, `screens[].elements[].items[].href`
- `journeys[].title`, `journeys[].description`
- top-level `app_nav` (manifest's `app_nav[]` is the flat, pinned-shape projection of it — see § Manifest schema)

Build `manifest.json` from the in-memory model using the pinned shape directly
(not by serialising `specs.json`) — this also means every
`manifest.json#screens[].elements[].target` / `.row_target` /
`.items[].target` stays the **declared** `screen_id[#fragment]` value (per
`contracts/walkthrough_renderer.md` § Field semantics), never the resolved
`href` — only `specs.json` and the rendered HTML carry the resolved form.

## ROLE / READS / WRITES / REFERENCES

ROLE  Walkthrough Lit renderer — converts screen specs + journey definitions
      + tokens into a Vite-built site of light-DOM Lit web components whose DOM
      is annotatable end-to-end via the same data-spec-* contract as static-html,
      and which is embeddable into a host page.

READS
  experience/screens/**/*.md            — screen specs (frontmatter + body)
  experience/journeys/stories.yaml      — journey definitions
  design/tokens.json                    — brand tokens
  ? experience/features/**/*.md       — feature traceability (soft)
  ? experience/screens/00_layout/shell.md — shared layout reference (soft)
  ? _concept/mockup-walkthrough/lit/vite.config.js — mode detection
  ? _concept/mockup-walkthrough/lit/src/components/screen-view.js — stale_scaffold check (update mode only)

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
  contracts/walkthrough_renderer.md     — shared renderer contract (pinned)
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

Mirrors `mockup-walkthrough-static-html`'s STEP 2 (and `mockup-walkthrough-astro`'s
STEP 2, which mirrors it exactly) for parsing, validation, target resolution,
and auto-slug derivation — only the output shape differs (an in-memory model
that STEP 5 serialises to `specs.json`, rather than strings substituted
directly into HTML).

- Glob `experience/screens/**/*.md` (excluding `00_layout/`); sort
  lexicographically by path. **Build the rendered-screen-id set first** (all
  `screen_id` values from this glob) before resolving any element's
  `target:` — every `target`/`row_target`/`items[].target` is validated
  against this set (§ Target resolution below); building it up front means
  resolution never depends on parse order.
- For each screen: parse YAML frontmatter (PyYAML); extract `implements[]`,
  `data_entities[]`, `layout`, `elements[]` (default `[]`). Capture the
  screen body markdown (needed for `body_html` below and for auto-slug
  discovery).
- Validate `elements[]` against `contracts/elements_block.md` (v0.3). If
  `lab/validate-elements-block/` available, delegate; otherwise apply these
  checks per element and emit `warnings[]` accordingly (render the node
  regardless — soft-fail always):
  - `kind` outside the v0.3 enum (`input, button, link, image, text,
    region, list, form, nav, media, custom, table, tabs`) → warning
    `kind: "unknown_element_kind"`, treat as `custom`.
  - `target` / `row_target` present → resolve against the rendered-screen-id
    set (§ Target resolution below); unresolved → `href: null` on the
    in-memory element (`screen-view.js` falls back to `'#'`) +
    `kind: "unresolved_target"` warning. Resolved → set `href` / `row_href`
    to the lit-scheme resolved path (see § Target resolution). This is the
    only target-related check this renderer performs at render time — shape/
    grammar validation (malformed `screen_id`, `target` on a non-interactive
    kind, etc.) is `lab/validate-elements-block`'s job per the contract, not
    re-litigated here.
  - `columns` / `sample_rows` / `items` / `options` — parsed and carried
    verbatim into the in-memory model (§ Content fidelity); this renderer
    does not re-validate `sample_rows` row length against `columns` length
    — authoring-time validation owns that.

  > **Design note:** this renderer does NOT re-validate `elements:` block
  > schema shape — `sample_rows` row-length vs. `columns`, per-kind `items`
  > shape, or `target`/`screen_id` grammar. That's `lab/validate-elements-block`'s
  > job at authoring time. This renderer assumes schema-valid input and
  > handles only render-time semantics — target resolution success/failure,
  > reflected via `unresolved_target` warnings (see § Target resolution
  > below). Consistent with `contracts/walkthrough_renderer.md`'s
  > `warnings[].kind` enum, which has no length-mismatch or shape-mismatch
  > kind at all.

- **§ Target resolution** (`contracts/elements_block.md` § Navigation
  targets, `contracts/walkthrough_renderer.md` § Target resolution): a
  `target`/`row_target` value is `screen_id[#fragment]`. Strip the fragment;
  the target resolves iff the remaining `screen_id` is in the
  rendered-screen-id set built above. From `screen/<gA>/<nA>.html`, a
  resolved target `gB/nB` gets `href: "../<gB>/<nB>.html"` (+
  `#<fragment>` when present) — lit's relative, `.html`-suffixed scheme
  (§ Renderer Contract above), matching static-html's, NOT astro's
  root-relative clean-URL scheme. Unresolved → `href: null` (`screen-view.js`
  renders `'#'`) + `unresolved_target` warning (declared-but-unresolved
  only; an absent `target:` is not an error, gets no warning, and the
  element simply has no `href` key).
- Parse `experience/screens/00_layout/shell.md` frontmatter, when the file
  exists, for an `elements:` entry with `kind: nav` and non-empty `items:`
  — this is the **shell-authoritative app nav** (§ App-shell navigation,
  used below). Absent file, absent `elements:`, absent `kind: nav` entry,
  or an entry with empty/absent `items:` — all fall through to the
  **derived-default** case.
- Read `experience/journeys/stories.yaml`. Validate each `journeys[]` entry
  has `id` AND `screen_sequence`. Missing `screen_sequence` → warning
  `kind: "missing_screen_sequence"`, skip that journey render.
- Read `design/tokens.json`. Flatten nested tree depth-first into flat dict
  keyed `--token-<dotted-path-with-hyphens>`.
- Glob `experience/features/**/*.md`; sort lexicographically. Build
  `feature -> screens[]` map by inverting `screens[].implements[]`.
- **Auto-slug source set** (`contracts/walkthrough_renderer.md` § Auto-slug
  fallback) — walked only when a screen's `elements:` is absent OR partial
  (i.e. for any widget not already covered by an explicit entry, matched by
  label-equality, case-insensitive):
  - (a) markdown `##`/`###` headings, **excluding** — case-insensitive —
    the canonical spec-template headings `Purpose`, `Route`, `What the
    User Sees`, `Wireframe`, `Information Displayed`, `Actions`,
    `Situations`, `UI Elements`, `Template Data`; the shell template's own
    `Navigation`, `Layout Areas`, `Responsive Behaviour`; and any
    `# Screen: *` / `# Shell: *` H1 (H1s are never scanned regardless —
    only `##`/`###` are widget sources). These excluded headings become
    the § Spec reference panel's `body_html` skeleton instead (see below)
    and are **never** rendered as `el-region` widgets. A screen's own
    non-canonical heading (e.g. a bespoke `## Notes`) stays in the
    discovery net and produces an inert `kind: text` element.
  - (b) form-field lines matching `[label]: input|button|...` pattern,
  - (c) acceptance-criteria mentions in body text,
  - (d) **`## Actions` bullets, label-extracted.** For each bullet: label
    = the first quoted token (`"…"` or `„…“`) when present; otherwise the
    clause preceding the first `→`, with a leading interaction verb
    (`Click`, `Change`, `Select`, `Switch`, `Drag`, `Pick`, `Open`,
    optionally preceded by an article) stripped, truncated to ≤ 40 chars.
    The bullet's full text becomes the synthesized element's `describes:`.
    Kind inference: a quoted token, or a `Click …` verb → `button`;
    `Change …` / `Select …` / `Pick …` → `input`; `Switch tab` → `tabs`
    (items sourced from bold/quoted tab names in `## What the User Sees`,
    or two placeholder items if none found).
  ID generation: kebab-case slug of the label; `<kind>-<n>` fallback when
  the label slugs to empty; `-2`/`-3`… suffix on collision;
  `auto_slug_collision` warning when colliding with an explicit id. Each
  auto-slugged element gets `provisional: true` and a `warnings[]` entry of
  `kind: "auto_slugged"`.

  > **`items[]` id derivation (`nav` / `tabs` / `list`, used by the
  > shell-authoritative app nav too).** `elements_block.md` leaves `id`
  > optional on `nav`/`tabs` items and doesn't define an `id` field on
  > `list` items at all — an id-less `items[]` entry is the normal case,
  > not an edge case. When an entry declares `id:`, use it verbatim
  > (`provisional: false`, no warning) on the normalised in-memory item.
  > When it does **not**:
  > 1. Derive an id via the same kebab-slug algorithm as top-level
  >    auto-slug, **scoped to that element's own `items[]`** — a collision
  >    suffix (`-2`/`-3`…) disambiguates only within the same element's
  >    items, never across the whole screen.
  > 2. Set the normalised item's `element_id` to the derived id and
  >    `provisional: true` — this is what `screen-view.js` reads to emit
  >    `data-spec-element="<derived-id>"` and
  >    `data-spec-provisional="true"`, never re-deriving it itself.
  > 3. Append a `warnings[]` entry of `kind: "auto_slugged"` to the
  >    in-memory model (`element_id` = the derived item id, `screen_path` =
  >    this screen's path) — one entry per id-less item.
  >
  > This follows directly from `contracts/walkthrough_renderer.md`'s
  > `data-spec-*` attribute table, which names "list items, nav items"
  > explicitly as `data-spec-provisional`-eligible whenever "no explicit
  > `elements:` entry exists for it" — an id-less `items[]` entry has no
  > explicit entry establishing its own identity (it's derived from
  > `label`), exactly like a top-level auto-slugged widget. Every `items[]`
  > entry — whether it declared an explicit `id` or not — gets normalised
  > to carry `element_id`/`provisional` in the in-memory model /
  > `specs.json`, so `screen-view.js` never branches on "did this come
  > with an id"; it just reads `item.element_id`.
  >
  > Every `items[].target` (dict-shaped entries only) is resolved exactly
  > like a top-level `target` (§ Target resolution above), yielding the
  > item's own `href`. A bare-string item, or a dict item with no
  > `target`, gets no `href` key (legal + inert, same as an untargeted
  > button).

- **Spec panel body** (`body_html`, consumed by STEP 4's scaffolded
  `<details class="spec-panel">` block, per `contracts/walkthrough_renderer.md`
  § Spec reference panel) — computed once per screen, here, not at render
  time (§ Renderer Contract above explains why): render to an HTML fragment
  string = the screen body's top-level intro prose (any paragraph before the
  first `##`/`###` heading) **plus** every canonical section present
  (heading as `<h3>`, its content below) **plus** the `### Wireframe` fence
  verbatim as `<pre><code>…</code></pre>`. A screen's own non-canonical
  heading is **not** additionally duplicated here — it's already surfaced
  via auto-slug discovery (or an explicit element). HTML-escape every
  interpolated string per the shared MUST. No `data-spec-*` attribute of any
  kind belongs inside `body_html` — it's reference prose, not an annotatable
  surface.
  - **Zero explicit elements.** When the screen has no `elements:` at all
    (or an empty one) AND the auto-slug walk above discovers nothing
    either, record on the in-memory screen model that its spec panel MUST
    render `open` (STEP 4's component reads this off
    `screen.elements.filter(e => !e.provisional).length === 0`, so no
    separate boolean field is needed in `specs.json`) and emit a
    `warnings[]` entry of `kind: "no_explicit_elements"`.
- **§ App-shell navigation** (`contracts/walkthrough_renderer.md` § App-shell
  navigation) — build the `app_nav` in-memory model, one entry per
  generated/authoritative link, each already carrying its resolved `href`:
  - **Shell-authoritative case** (shell nav found above): one entry per
    `items[]` entry on the shell's `kind: nav` element, `label`/`href`
    resolved per § Target resolution, `element_id` per the **`items[]` id
    derivation** rule above, `source` = `"experience/screens/00_layout/shell.md"`,
    grouped into a single unlabeled group (no subdivision — "the authored
    order is used verbatim").
  - **Derived-default case**: one entry per *rendered* screen (this
    walkthrough's screens, in the same lexicographic-by-`screen_path` order
    as the screens array — deterministic, no separate sort invented),
    grouped by `<group>` (the screen's directory segment; group label =
    dir name with its `NN_` prefix stripped and underscores replaced by
    spaces — e.g. `00_auth` → `auth`). `element_id: "app-nav"` on the whole
    generated nav, `provisional: true`; each per-screen entry gets
    `element_id: "app-nav-<n>"` (1-based, flat position across all groups),
    `provisional: true`, `label` = screen filename stem with underscores →
    spaces (e.g. `verify_email` → `verify email`), `href` resolved exactly
    like any other target. Emit **exactly one** `auto_slugged` `warnings[]`
    entry for the whole generated nav (`element_id: "app-nav"`, no
    `screen_path` key — it isn't owned by one screen), never one per link.
  - Either way, record the result as the single `app_nav` object shaped
    `{element_id, provisional, groups: [{label, items: [...]}]}` (§
    `specs.json` shape above); every screen references this same object.
- Build normalised in-memory model:
  `{ screens: [{..., body_html, elements: [{..., href?, row_href?, items?:
  [{..., element_id, provisional, href?}]}]}], journeys, token_vars,
  features, app_nav, shell_nav: {...} | null, warnings }`.

### Edge cases

- **Malformed YAML** → fail loudly, exit non-zero, name the offending file.
- **Screen in journey but absent on disk** → `kind: "missing_screen"`,
  dead-end placeholder step (link present, class `journey-step-missing`).
- **`elements:` kind outside v0.3 enum** → render as `custom`,
  `kind: "unknown_element_kind"`.
- **`layout:` reference to non-existent file** → `kind: "missing_layout"`,
  fall back to the `<screen-view>` default shell.
- **`experience/features/` empty or missing** → soft gate,
  `kind: "missing_feature"`, continue. `manifest.features[]` → `[]`.
- **Zero journeys** → render "No journeys defined",
  `kind: "no_journeys"`.
- **`target`/`row_target`/`items[].target` declared but unresolved** →
  `href: null` on the in-memory model (`screen-view.js` renders `'#'`) +
  `kind: "unresolved_target"`; never hard-fail.

## STEP 3: Detect mode

Check `_concept/mockup-walkthrough/lit/vite.config.js`.
- Absent → **Init** (proceed to STEP 4).
- Present → **Update** (skip STEP 4, run the § `stale_scaffold` check below,
  then proceed directly to STEP 5).

### `stale_scaffold` check (update mode only)

Scaffolded files (`src/components/screen-view.js`, `journey-view.js`,
`index-view.js`) are never rewritten on update runs (§ Two-mode behaviour
above) — so a project scaffolded before this SKILL.md revision (or
hand-edited since) may be missing the `el.href` interpolation, the
`table`/`tabs` `TAG` entries, or the spec-panel/app-nav blocks this revision
adds. Detect this **before** regenerating `specs.json` so the warning
reflects the scaffold as it stood at the start of the run:

- Read `src/components/screen-view.js` as text.
- If it does **not** contain the literal substring `el.href`, OR does
  **not** contain the literal substring `spec-panel` → append a
  `warnings[]` entry of `kind: "stale_scaffold"`
  (`message: "src/components/screen-view.js predates this renderer's
  target/content-fidelity revision (missing el.href and/or spec-panel) —
  delete the scaffold to let it regenerate, or port the template changes
  from this SKILL.md by hand."`).
- This is a warning, not a failure — the build still proceeds against the
  stale scaffold (whatever it renders is what ships); the warning exists so
  `mockup-feedback-annotate`/the user knows target/content fidelity may be
  incomplete on this project.

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
import { unsafeHTML } from 'lit/directives/unsafe-html.js';
import specs from '../data/specs.json';

function renderItems(items, kind) {
  if (!items || items.length === 0) {
    return kind === 'list' ? html`<li>…</li>` : nothing;
  }
  return items.map((item, i) => {
    const prov = !!item.provisional;
    const label = item.label ?? String(item);
    if (kind === 'list') {
      const inner = item.href ? html`<a href=${item.href}>${label}</a>` : label;
      return html`<li data-spec-element=${item.element_id} ?data-spec-provisional=${prov}>${inner}</li>`;
    }
    if (kind === 'tabs') {
      const cls = i === 0 ? 'tab active' : 'tab';
      return item.href
        ? html`<a href=${item.href} class=${cls} data-spec-element=${item.element_id} ?data-spec-provisional=${prov}>${label}</a>`
        : html`<span class=${cls} data-spec-element=${item.element_id} ?data-spec-provisional=${prov}>${label}</span>`;
    }
    // nav
    return html`<li><a href=${item.href ?? '#'} data-spec-element=${item.element_id} ?data-spec-provisional=${prov}>${label}</a></li>`;
  });
}

function renderTable(el, prov) {
  const thead = html`<tr>${el.columns.map((c) => html`<th>${c}</th>`)}</tr>`;
  const tbody =
    el.sample_rows && el.sample_rows.length > 0
      ? el.sample_rows.map(
          (row) => html`<tr>${row.map(
            (cell, i) => html`<td>${i === 0 && el.row_href ? html`<a href=${el.row_href}>${cell}</a>` : cell}</td>`,
          )}</tr>`,
        )
      // No sample_rows declared — header + one skeleton row, never fabricated content.
      : html`<tr>${el.columns.map(() => html`<td></td>`)}</tr>`;
  return html`<table data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
    ><thead>${thead}</thead><tbody>${tbody}</tbody></table>`;
}

const TAG = {
  input: (el, prov) =>
    el.options
      ? html`<select name=${el.element_id} aria-label=${el.label}
          data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
          class="border rounded px-2 py-1">${el.options.map(
            (o) => html`<option value=${o}>${o}</option>`,
          )}</select>`
      : html`<input name=${el.element_id} aria-label=${el.label}
      data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      class="border rounded px-2 py-1" />`,
  button: (el, prov) =>
    el.href
      ? html`<a href=${el.href} data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
          class="button btn-primary">${el.label}</a>`
      : html`<button data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      class="btn-primary">${el.label}</button>`,
  link: (el, prov) =>
    html`<a href=${el.href ?? '#'} data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      class="link">${el.label}</a>`,
  image: (el, prov) => {
    const img = html`<img src="#" alt=${el.label} data-spec-element=${el.element_id}
      ?data-spec-provisional=${prov} />`;
    return el.href ? html`<a href=${el.href}>${img}</a>` : img;
  },
  text: (el, prov) =>
    html`<span data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      >${el.label}</span>`,
  region: (el, prov) =>
    html`<section data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      ><h3>${el.label}</h3></section>`,
  list: (el, prov) => {
    const ul = html`<ul data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      >${renderItems(el.items, 'list')}</ul>`;
    return el.href ? html`<a href=${el.href}>${ul}</a>` : ul;
  },
  form: (el, prov) =>
    html`<form data-spec-element=${el.element_id} ?data-spec-provisional=${prov}></form>`,
  nav: (el, prov) =>
    html`<nav data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      ><ul>${renderItems(el.items, 'nav')}</ul></nav>`,
  tabs: (el, prov) =>
    html`<nav class="tabs" data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      >${renderItems(el.items, 'tabs')}</nav>`,
  table: (el, prov) => renderTable(el, prov),
  media: (el, prov) =>
    html`<figure data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
      ><figcaption>${el.label}</figcaption></figure>`,
  custom: (el, prov) =>
    el.href
      ? html`<a href=${el.href} data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
          >${el.label}</a>`
      : html`<div data-spec-element=${el.element_id} ?data-spec-provisional=${prov}
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

  // Generated app-shell nav (§ App-shell navigation) — same `specs.app_nav`
  // shared object on every screen; grouped either by the shell-authoritative
  // author order (single unlabeled group) or by derived-default `<group>`.
  renderAppNav(appNav) {
    if (!appNav) return nothing;
    return html`
      <nav class="app-nav" data-spec-element=${appNav.element_id} ?data-spec-provisional=${!!appNav.provisional}>
        ${appNav.groups.map(
          (group) => html`
            <div class="nav-group">
              ${group.label ? html`<span class="nav-group-label">${group.label}</span>` : nothing}
              <ul>
                ${group.items.map(
                  (item) => html`
                    <li><a href=${item.href ?? '#'} data-spec-element=${item.element_id}
                      ?data-spec-provisional=${!!item.provisional}>${item.label}</a></li>
                  `,
                )}
              </ul>
            </div>
          `,
        )}
      </nav>
    `;
  }

  render() {
    const screen = this.screen;
    if (!screen) return html`<p>Unknown screen: ${this.screenId}</p>`;
    // § Spec reference panel — open when zero non-provisional (explicit) elements exist.
    const nonProvisional = screen.elements.filter((el) => !el.provisional);
    const openPanel = nonProvisional.length === 0;
    return html`
      ${this.renderAppNav(screen.app_nav)}
      <h1>${screen.title || screen.screen_id}</h1>
      <main class="space-y-4">
        ${screen.elements.map((el) => this.renderElement(el))}
      </main>
      <details class="spec-panel" ?open=${openPanel}>
        <summary>View spec</summary>
        ${unsafeHTML(screen.body_html)}
      </details>
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

Per-kind mapping mirrors `contracts/walkthrough_renderer.md` § kind → DOM tag
mapping exactly (this renderer implements every row, same as static-html and
astro): `link`/`button`/`custom` wrap in `<a>` iff `el.href` is set (`custom`
replaces the `<div>` entirely with the `<a>`, carrying `data-spec-element`
itself — matching astro's precedent for this kind); `image` keeps
`data-spec-element` on the `<img>` and wraps it in a plain outer `<a>` when
`el.href` is set; `list` renders one `<li>` per item (each with its own
resolved `href` when declared) plus an independent outer-`<a>` wrap when the
list element's own `href` is set (`data-spec-element` stays on the `<ul>`);
`table` builds `<thead>` from `columns` and either real `<tbody>` rows from
`sample_rows` (first cell wrapped in `<a>` when `row_href` is set) or one
skeleton row when `sample_rows` is absent — never fabricated; `tabs` marks
the first entry `active`, entries with an `href` render as `<a class="tab">`,
others as inert `<span class="tab">`; `nav` renders real links from `items[]`
via the `renderItems` helper (`kind: 'nav'` branch) — the generated app-nav
(`renderAppNav`) is a separate rendering path since it carries the grouped
`{groups: [{label, items}]}` shape (§ App-shell navigation), not a bare
`items[]`; `input` becomes a real `<select>` with one `<option>` per value
when `options` is present. States
beyond `default` render as adjacent `<span class="state-<n>">` siblings,
same convention already established by this component before this revision.

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

Agent generates one HTML entry per page directly from `specs.json` (STEP 5).
Each sets body `data-spec-*` marker, mounts matching custom element. Because
components render light DOM, mounted markup carries `data-spec-*` attributes
on queryable nodes. `src/pages/index.html` scaffolded once on init; per-screen
and per-journey entries regenerated every run (agent-direct — they enumerate
current screen/journey set).

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

Write `src/data/specs.json` derived from the in-memory model built in STEP 2
(screens with `body_html`, pre-resolved `href`/`row_href`, normalised
`items[]`, and each screen's own `app_nav` field set to the shared top-level
`app_nav` object — every screen renders the identical generated nav, see §
App-shell navigation). Schema as shown in § `specs.json` shape above.
Overwrite unconditionally.

Regenerate every per-page HTML entry under `src/pages/screen/**` and
`src/pages/journey/**` from current screen/journey set (agent-direct). Each
sets correct body `data-spec-*` marker, mounts matching custom element. This
is what makes built HTML carry queryable `data-spec-*` nodes without
depending on client-side hydration.

Write `src/styles/global.css`:

```css
:root {
  /* one line per flattened token_var */
  --token-<name>: <value>;
}

/* minimal element styling keyed to token vars */
.btn-primary { background: var(--token-color-primary); color: #fff; }

[data-spec-provisional="true"] { outline: 1px dashed #999; outline-offset: 2px; }
.app-nav { display: flex; gap: 1rem; }
.app-nav .nav-group { display: flex; align-items: center; gap: 0.5rem; }
.app-nav .nav-group-label { font-weight: 600; text-transform: uppercase; font-size: 0.75rem; }
table { border-collapse: collapse; width: 100%; }
table th, table td { border: 1px solid #ccc; padding: 0.25rem 0.5rem; text-align: left; }
select { padding: 0.25rem 0.5rem; }
nav.tabs { display: flex; gap: 0.5rem; border-bottom: 1px solid #ccc; }
nav.tabs .tab.active { border-bottom: 2px solid var(--token-color-primary, #0ea5e9); }
details.spec-panel { border: 1px solid #ccc; border-radius: 4px; padding: 0.5rem; margin-top: 1rem; }
details.spec-panel summary { cursor: pointer; font-weight: 600; }
```

The `[data-spec-provisional="true"]` rule generalizes the auto-slug visual
treatment via the attribute selector, same as static-html/astro — it applies
uniformly to auto-slugged elements AND the generated app-nav (both are
provisional by definition) without a separate `.auto-slugged` rule.

Overwrite unconditionally. File is agent-managed every run.

On update runs only: compare count of `--token-*` keys in freshly derived
in-memory model vs. CSS var declarations in existing `global.css` before
overwriting. If counts differ, append `kind: "stale_token_css"` to
`warnings[]`.

## STEP 6: Build

Run from `_concept/mockup-walkthrough/lit/`:

```bash
bun run build
```

On non-zero exit: print full stderr, exit non-zero. Do not write
`manifest.json`.

After build: verify `dist/` does NOT exist under project root. If it does:
fail with "vite.config.js outDir misconfigured — dist/ must not exist".

Agent-direct per-page HTML already carries `data-spec-*` attributes in light
DOM, so built output is queryable whether or not Vite-bundled component JS
hydrates.

## STEP 7: Write `manifest.json`

Emit pinned schema (`contracts/walkthrough_renderer.md` § Manifest schema,
`schema_version: "1.2"`). Build from the STEP 2 in-memory model — NOT by
serialising `specs.json`. Template-only fields from `specs.json`
(`screens[].title`, `screens[].group`, `screens[].journeys[]`,
`screens[].body_html`, `screens[].app_nav`, `screens[].elements[].href`,
`.row_href`, `items[].element_id`/`.provisional`/`.href`, `journeys[].title`,
`journeys[].description`, top-level `app_nav` object) MUST NOT appear in
`manifest.json` — see § `specs.json` → `manifest.json` projection above.

New fields this revision adds to `manifest.json#screens[].elements[]`:
`target` / `row_target` / `columns` / `sample_rows` / `items` / `options`,
echoed **verbatim** from the declared frontmatter (the *declared* value,
never the resolved `href` — matches static-html/astro and the pinned
contract exactly). Top-level `app_nav[]` — one **flat** entry per rendered
nav link, in rendered order (positional, not alphabetic): `{label, target,
source}`, projected out of the grouped `specs.json#app_nav.groups[].items[]`
shape by flattening every group's items in order; `target` IS the resolved
href (per contract § Field semantics, `app_nav`'s `target` is the rendered
value, unlike element `target`).

Sort `screens[]` by `screen_path`, `journeys[]` by `journey_id`, `features[]`
by `feature_path`. `app_nav[]` is NOT sorted — it keeps rendered order.
Write atomically (tmp → fsync → rename).

`renderer: "mockup-walkthrough-lit"`, `renderer_version:` this SKILL.md's
`metadata.version`.

## STEP 8: Validate

Run from repo root:

```bash
python mockup-walkthrough/lit/validator.py _concept/mockup-walkthrough/lit
```

Exit 0 = ready. Exit 2 = violation report.

> **NOTE — validator gap (pre-existing, not fixed by this revision).**
> `mockup-walkthrough/lit/validator.py` does not exist on disk yet, unlike
> static-html's and astro's siblings. When it is eventually authored it
> MUST include the same checks static-html's/astro's validators implement
> — in particular: `target`/`row_target`/`items[].target` resolution
> (every resolvable target renders a real `<a href>`, never a stray
> `href="#"`), table-row-count/items-count/options-count fidelity against
> the declared `elements:` block, canonical-heading-slug-leak detection (no
> `data-spec-element` value is a canonical-heading slug), `<details
> class="spec-panel">` presence on every screen page, and the
> `no_explicit_elements` open-panel case. This SKILL.md's STEP 8 already
> assumes that validator exists; do not author it as part of any task whose
> scope is this SKILL.md alone — this note only records what it must cover
> once it is written.

## Error handling

### Shared conditions

See `contracts/walkthrough_renderer.md` § Shared error handling.

### Lit-specific

| Condition | Behaviour |
|---|---|
| `bun install` exits non-zero | Fail loudly with stderr; do not build |
| `bun run build` exits non-zero | Fail loudly with stderr; do not write `manifest.json` |
| `dist/` exists after build | Fail: "vite.config.js outDir misconfigured — dist/ must not exist" |
| A component omits `createRenderRoot() { return this; }` (Shadow DOM leak) | Fail: data-spec-* would be unqueryable; the validator asserts light DOM |
| Token count differs from CSS var count (update runs only) | `kind: "stale_token_css"`; user must extend `global.css` token block manually |
| Scaffold missing `el.href` and/or `spec-panel` (update runs only) | `kind: "stale_scaffold"`; user must delete the scaffold or port the template changes (§ `stale_scaffold` check, STEP 3) |

### `warnings[].kind` enum

Shared enum per `contracts/walkthrough_renderer.md` § warnings[].kind enum
(`auto_slugged`, `auto_slug_collision`, `missing_layout`, `missing_feature`,
`unknown_element_kind`, `missing_screen`, `missing_screen_sequence`,
`no_journeys`, `unresolved_target`, `no_explicit_elements`);
`stale_token_css` and `stale_scaffold` are this renderer's two Lit-specific
additions.

## MUST / NEVER

Shared MUST/NEVER: `contracts/walkthrough_renderer.md` § Shared MUST / NEVER.

MUST  render every Lit component into light DOM via `createRenderRoot() { return this; }`
MUST  set emptyOutDir: false in vite.config.js
MUST  set build.outDir to the project root (built files next to source)
MUST  write specs.json, global.css, and per-page HTML before running bun run build
MUST  regenerate global.css and per-page screen/journey HTML on every run (agent-managed)
MUST  reference components/styles with relative URLs so built pages are openable and embeddable
MUST  pre-resolve every `target`/`row_target`/`items[].target` into an `href` (or `null`) in `specs.json` at STEP 2/5 — `screen-view.js` only interpolates `el.href ?? '#'`, it never resolves a target itself
MUST  render declared `columns`/`sample_rows`/`items`/`options` as real DOM content in `screen-view.js` — no placeholder when content is declared
MUST  render the spec body only inside the collapsed (or, when zero explicit elements, open) `<details class="spec-panel">`, sourced from `body_html`
MUST  run the `stale_scaffold` check on every update run and record a `warnings[]` entry when the scaffold predates this revision

NEVER use Shadow DOM in any walkthrough component — it hides data-spec-* from the feedback overlay
NEVER regenerate vite.config.js, package.json, or src/components/*.js on update runs
NEVER create a dist/ subdirectory — outDir must be the project root
NEVER use a separate auto_slugged[] array — set provisional: true on the element object (the kind: "auto_slugged" warning entry in manifest.warnings[] is still required per the auto-slug step)
NEVER let a scaffolded component re-derive target resolution or auto-slug ids at render time — that logic lives in STEP 2 only

## CHECKLIST

- [ ] `_concept/mockup-walkthrough/lit/index.html` exists
- [ ] `_concept/mockup-walkthrough/lit/manifest.json` exists and parses as JSON
- [ ] `manifest.schema_version == "1.2"` and `manifest.renderer == "mockup-walkthrough-lit"`
- [ ] One `screen/<group>/<name>.html` per screen file under `experience/screens/`
- [ ] One `journey/<id>.html` per journey in `stories.yaml`
- [ ] Every Lit component overrides `createRenderRoot()` to return `this` (light DOM)
- [ ] Every `<body>` in `screen/**/*.html` has `data-spec-screen`
- [ ] Every annotatable node in `screen/**/*.html` has `data-spec-element` on a light-DOM node
- [ ] Every auto-slugged element node also has `data-spec-provisional="true"`
- [ ] Every `<body>` in `journey/**/*.html` has `data-spec-journey`
- [ ] `index.html` `<body>` has `data-spec-index="true"`
- [ ] No `dist/` subdirectory under `_concept/mockup-walkthrough/lit/`
- [ ] At least one `<link rel="stylesheet">` in `index.html` and referenced CSS file is non-empty
- [ ] No canonical spec heading appears as an `el-region` widget
- [ ] Every declared table renders `sample_rows` verbatim as `<tbody>` rows
- [ ] Spec body appears only inside `<details class="spec-panel">`
- [ ] No auto-slugged label exceeds 40 chars or contains an action sentence
- [ ] Validator (`mockup-walkthrough/lit/validator.py`) exits 0

EMIT  [mockup-walkthrough-lit] started run_id=<uuid>
EMIT  [mockup-walkthrough-lit] checkpoint screens=<N> journeys=<M>
EMIT  [mockup-walkthrough-lit] completed run_id=<uuid> screens=<N> journeys=<M> warnings=<W>
