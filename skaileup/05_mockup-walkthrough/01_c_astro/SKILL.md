---
name: mockup-walkthrough-astro
description: "Use when stakeholders need a clickable Astro walkthrough of the application — built static site, Tailwind-styled, openable directly in a browser. Generates one HTML file per screen and per journey, plus a manifest.json that the mockup-feedback cluster reads. Best for appbuilder-standard tier."
metadata:
  version: "0.2.0"
  tags:
    - walkthrough
    - mockup
    - astro
    - tailwind
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
        description: "Brand tokens injected as Tailwind CSS vars in the built shell"
      - path: "experience/features"
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

Astro-rendered variant of walkthrough mockup cluster. Consumes same four
inputs as `mockup-walkthrough-static-html` (screen specs, journey
definitions, brand tokens, feature files); produces Tailwind-styled built
Astro static site at `_concept/mockup-walkthrough/astro/`.

Every rendered DOM node carries same `data-spec-*` attributes as static-html
variant so `mockup-feedback-*` cluster resolves clicks identically across
renderers. `manifest.json` schema is identical — only
`renderer: "mockup-walkthrough-astro"` differs.

**Two-mode behaviour — decision recorded.** Agent detects whether Astro
project already exists by checking for
`_concept/mockup-walkthrough/astro/astro.config.mjs`:

- **Init** (absent): scaffold project skeleton → generate `specs.json` +
  `global.css` → `bun install` → `bun run build` → write `manifest.json`
- **Update** (present): regenerate `specs.json` + `global.css` only →
  check the scaffold isn't stale (§ `stale_scaffold` check) → `bun run
  build` → rewrite `manifest.json`

On update runs, agent NEVER touches `astro.config.mjs`,
`tailwind.config.mjs`, or `.astro` template files — those belong to user.
**This is the key architectural constraint this renderer works under, vs.
static-html:** static-html's templates are Python string-formatting calls
that run fresh on every render, so target/content fidelity is "just" a
matter of the renderer computing the right string each time. Astro's
`.astro` route templates are scaffolded once at project-init time and MUST
NOT be touched on update runs — so every value a template would otherwise
need to *resolve* (a `target:` → href, an unresolved target's fallback, the
spec panel's rendered body) MUST already be sitting fully-resolved in
`specs.json` before the template ever runs. The template only interpolates;
it never derives. See § `specs.json` shape and § Renderer Contract below.

**Generation approach — decision recorded.** Agent-direct: agent reads
screen specs, derives `src/data/specs.json` inline (no persistent generator
script). Same pattern as static-html's Python renderer.

## Renderer Contract

Implements shared walkthrough renderer contract — `contracts/walkthrough_renderer.md`
(schema_version "1.2"): data-spec-* attribute table, screen_id vs screen_path,
kind → DOM tag mapping (incl. `target` resolution, `table`, `tabs`,
populated `list`/`select`), § Target resolution, § App-shell navigation,
§ Auto-slug fallback (narrowed source set), § Spec reference panel, manifest
schema + field semantics, warnings[].kind enum, shared error handling,
screen-in-multiple-journeys rule, shared MUST/NEVER. Read before rendering;
pinned, MUST NOT be restated here.

Renderer-specific manifest values: `renderer: "mockup-walkthrough-astro"`,
`renderer_version:` this SKILL.md's `metadata.version`.

Astro-specific: template emits `data-spec-provisional="true"` where
`element.provisional === true`; NO separate top-level `auto_slugged[]`
array — `provisional: true` lives on element object.

**Astro-specific corollary of the contract (not a deviation from it): all
target/content resolution happens in STEP 2, not in the template.** Every
other renderer MAY resolve a `target:` at render time because its templates
run at render time too. Astro's scaffolded `.astro` templates run at build
time, long after the agent that could re-derive an auto-slug id or resolve
a target has finished — so this renderer's `specs.json` carries the
*already-resolved* `href` (and `row_href`, and per-`items[]`-entry `href`)
alongside the *declared* `target`/`row_target`/`items[].target` fields the
manifest still echoes verbatim. The template does `el.href ?? '#'`, never
its own resolution logic. This is the one place astro's shape genuinely
differs from static-html's — flagged explicitly per this skill's authoring
brief.

Astro's hrefs are **root-relative, extension-less** (`/screen/<screen_id>`,
`/journey/<journey_id>`, `/`), matching the clean-URL convention this
renderer's `index.astro` and journey template already used before this
revision (`href={\`/screen/${s.screen_id}\`}`) — NOT static-html's
`../<group>/<name>.html` relative-file scheme, which only makes sense for a
walkthrough opened directly via `file://`. Astro's build always emits real
`.html` files on disk (`build.format: 'file'`), but the *served* URL is the
extension-less form; this renderer's own precedent (established before this
revision, unchanged by it) is followed here rather than static-html's,
since it's what the existing Astro templates already do.

## Inputs

Same four input shapes as `mockup-walkthrough-static-html`:

| Path | Shape |
|---|---|
| `experience/screens/<group>/<screen>.md` | Markdown + YAML frontmatter with optional `elements:` block per `contracts/elements_block.md` (v0.3) |
| `experience/journeys/stories.yaml` | JSON `{ "journeys": [{ "id", "title", "description", "screen_sequence" }] }` |
| `design/tokens.json` | Token tree. Flattened to CSS custom properties (`--token-<dotted-path-with-hyphens>`). |
| `experience/features/<group>/<feature>.md` | Used only for `manifest.json#features`; not rendered as HTML. |

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
Every value a template would otherwise need to resolve — a target's href,
an item's derived id, a screen's rendered spec body — is pre-resolved here
(§ Renderer Contract above); the template only interpolates.

```json
{
  "app_nav": [
    {
      "label": "login",
      "href": "/screen/00_auth/login",
      "source": "derived"
    }
  ],
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
          "href": "/screen/01_user_auth/register",
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
          "row_href": "/screen/01_user_auth/verify_email",
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
              "href": "/screen/01_user_auth/login",
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
generation time so the template never has to re-derive it. `href` is
present on an item only when the item declares a `target`.

**specs.json → manifest.json projection.** `specs.json` carries
template-convenience fields that MUST NOT be copied to `manifest.json`:
- `screens[].title`, `screens[].group`, `screens[].journeys[]`, `screens[].body_html`
- `screens[].elements[].href`, `screens[].elements[].row_href`
- `screens[].elements[].items[].element_id`, `screens[].elements[].items[].provisional`, `screens[].elements[].items[].href`
- `journeys[].title`, `journeys[].description`
- `app_nav[].href` (manifest's `app_nav[].target` carries the same resolved value, under the pinned field name — see § Manifest schema)

Build `manifest.json` from the in-memory model using the pinned shape
directly (not by serialising `specs.json`) — this also means every
`manifest.json#screens[].elements[].target` / `.row_target` /
`.items[].target` stays the **declared** `screen_id[#fragment]` value (per
`contracts/walkthrough_renderer.md` § Field semantics), never the resolved
`href` — only `specs.json` and the rendered HTML carry the resolved form.

## ROLE / READS / WRITES / REFERENCES

ROLE  Walkthrough Astro renderer — converts screen specs + journey definitions
      + tokens into a Tailwind-styled clickable Astro static site whose DOM is
      annotatable end-to-end via the same data-spec-* contract as static-html.

READS
  experience/screens/**/*.md            — screen specs (frontmatter + body)
  experience/journeys/stories.yaml      — journey definitions
  design/tokens.json                    — brand tokens
  ? experience/features/**/*.md       — feature traceability (soft)
  ? experience/screens/00_layout/shell.md — shared layout + shell-authoritative nav (soft)
  ? _concept/mockup-walkthrough/astro/astro.config.mjs — mode detection
  ? _concept/mockup-walkthrough/astro/src/pages/screen/[...slug].astro — stale_scaffold check (update mode only)

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
  contracts/walkthrough_renderer.md     — shared renderer contract (pinned)
  contracts/elements_block.md           — elements: schema + renderer contract (v0.3)
  contracts/frontmatter.md              — screen + feature + stories shapes
  contracts/asset_frontmatter.md        — this SKILL.md's own frontmatter shape
  contracts/skill_grammar.md            — DSL keywords used in this body
  contracts/iron_laws.md                — non-negotiable cross-skill constraints
  contracts/scripts/validator_lib.py    — used by mockup-walkthrough/astro/validator.py
  docs/devlog/mockup-design.md § 4, § 6           — shared input contract + hybrid ID strategy
  mockup-walkthrough/static-html/SKILL.md — sibling skill (contract anchor; STEP 2 below mirrors its STEP 2)

## STEP 1: Read feedback devlog (preserved intent)

- If `_concept/_feedback/devlog.md` exists, read it.
- Filter entries where `target_paths` overlaps files under
  `_concept/mockup-walkthrough/astro/`.
- For each matching entry: extract `patch_summary` as a preserved-intent constraint.
  Do not undo these during regeneration.
- If no devlog or no matching entries: proceed with no constraints.

## STEP 2: Read inputs

Mirrors `mockup-walkthrough-static-html`'s STEP 2 exactly for parsing,
validation, target resolution, and auto-slug derivation — only the output
shape differs (an in-memory model that STEP 5 serialises to `specs.json`,
rather than strings substituted directly into HTML).

- Glob `experience/screens/**/*.md` (excluding `00_layout/`); sort
  lexicographically by path. **Build the rendered-screen-id set first**
  (all `screen_id` values from this glob) before resolving any element's
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
    in-memory element (template falls back to `'#'`) +
    `kind: "unresolved_target"` warning. Resolved → set `href` /
    `row_href` to the astro-scheme resolved path (see § Target resolution).
    This is the only target-related check this renderer performs at render
    time — shape/grammar validation (malformed `screen_id`, `target` on a
    non-interactive kind, etc.) is `lab/validate-elements-block`'s job per
    the contract, not re-litigated here.
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
  `target`/`row_target` value is `screen_id[#fragment]`. Strip the
  fragment; the target resolves iff the remaining `screen_id` is in the
  rendered-screen-id set built above. A resolved target `gB/nB` gets
  `href: "/screen/gB/nB"` (+ `#<fragment>` when present) — astro's
  root-relative, extension-less scheme (§ Renderer Contract above), NOT
  static-html's `../<group>/<name>.html`. Unresolved → `href: null` (the
  template renders `'#'`) + `unresolved_target` warning (declared-but-
  unresolved only; an absent `target:` is not an error, gets no warning,
  and the element simply has no `href` key).
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
    the § Spec reference panel's `body_html` skeleton instead (see STEP 5)
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
  >    `provisional: true` — this is what the template reads to emit
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
  > `specs.json`, so the template never branches on "did this come with an
  > id"; it just reads `item.element_id`.
  >
  > Every `items[].target` (dict-shaped entries only) is resolved exactly
  > like a top-level `target` (§ Target resolution above), yielding the
  > item's own `href`. A bare-string item, or a dict item with no
  > `target`, gets no `href` key (legal + inert, same as an untargeted
  > button).

- **Spec panel body** (`body_html`, consumed by STEP 4's scaffolded
  `<details class="spec-panel">` block, per `contracts/walkthrough_renderer.md`
  § Spec reference panel) — computed once per screen, here, not at build
  time (§ Renderer Contract above explains why): render to an HTML
  fragment string = the screen body's top-level intro prose (any paragraph
  before the first `##`/`###` heading) **plus** every canonical section
  present (heading as `<h3>`, its content below) **plus** the
  `### Wireframe` fence verbatim as `<pre><code>…</code></pre>`. A screen's
  own non-canonical heading is **not** additionally duplicated here — it's
  already surfaced via auto-slug discovery (or an explicit element).
  HTML-escape every interpolated string per the shared MUST. No
  `data-spec-*` attribute of any kind belongs inside `body_html` — it's
  reference prose, not an annotatable surface.
  - **Zero explicit elements.** When the screen has no `elements:` at all
    (or an empty one) AND the auto-slug walk above discovers nothing
    either, record on the in-memory screen model that its spec panel MUST
    render `open` (STEP 4's template reads this off
    `screen.elements.filter(e => !e.provisional).length === 0`, so no
    separate boolean field is needed in `specs.json`) and emit a
    `warnings[]` entry of `kind: "no_explicit_elements"`.
- **§ App-shell navigation** (`contracts/walkthrough_renderer.md` § App-shell
  navigation) — build the `app_nav` in-memory model, one entry per
  generated/authoritative link, each already carrying its resolved `href`:
  - **Shell-authoritative case** (shell nav found above): one entry per
    `items[]` entry on the shell's `kind: nav` element, `label`/`href`
    resolved per § Target resolution, `element_id` per the **`items[]` id
    derivation** rule above, `source` = `"experience/screens/00_layout/shell.md"`.
  - **Derived-default case**: one entry per *rendered* screen (this
    walkthrough's screens, in the same lexicographic-by-`screen_path` order
    as the screens array — deterministic, no separate sort invented),
    grouped by `<group>` (the screen's directory segment; group label =
    dir name with its `NN_` prefix stripped and underscores replaced by
    spaces — e.g. `00_auth` → `auth`). `element_id: "app-nav"` on the
    whole generated nav, `provisional: true`; each per-screen entry gets
    `element_id: "app-nav-<n>"` (1-based, flat position across all
    groups), `provisional: true`, `label` = screen filename stem with
    underscores → spaces (e.g. `verify_email` → `verify email`), `href`
    resolved exactly like any other target. Emit **exactly one**
    `auto_slugged` `warnings[]` entry for the whole generated nav
    (`element_id: "app-nav"`, no `screen_path` key — it isn't owned by one
    screen), never one per link.
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
  fall back to `Shell.astro` default.
- **`experience/features/` empty or missing** → soft gate,
  `kind: "missing_feature"`, continue. `manifest.features[]` → `[]`.
- **Zero journeys** → render "No journeys defined",
  `kind: "no_journeys"`.
- **`target`/`row_target`/`items[].target` declared but unresolved** →
  `href: null` on the in-memory model (template renders `'#'`) +
  `kind: "unresolved_target"`; never hard-fail.

## STEP 3: Detect mode

Check `_concept/mockup-walkthrough/astro/astro.config.mjs`.
- Absent → **Init** (proceed to STEP 4 then STEP 5).
- Present → **Update** (skip STEP 4's file-writes, run the § `stale_scaffold`
  check below, then proceed to STEP 5).

### `stale_scaffold` check (update mode only)

Scaffolded files (`src/pages/screen/[...slug].astro`, `src/layouts/Shell.astro`,
etc.) are never rewritten on update runs (§ Two-mode behaviour above) — so a
project scaffolded before this SKILL.md revision (or hand-edited since) may
be missing the `el.href` interpolation, the `table`/`tabs` tag-map rows, or
the spec-panel block this revision adds. Detect this **before** regenerating
`specs.json` so the warning reflects the scaffold as it stood at the start
of the run:

- Read `src/pages/screen/[...slug].astro` as text.
- If it does **not** contain the literal substring `el.href`, OR does
  **not** contain the literal substring `spec-panel` → append a
  `warnings[]` entry of `kind: "stale_scaffold"`
  (`message: "src/pages/screen/[...slug].astro predates this renderer's
  target/content-fidelity revision (missing el.href and/or spec-panel) —
  delete the scaffold to let it regenerate, or port the template changes
  from this SKILL.md by hand."`).
- This is a warning, not a failure — the build still proceeds against the
  stale scaffold (whatever it renders is what ships); the warning exists so
  `mockup-feedback-annotate`/the user knows target/content fidelity may be
  incomplete on this project.

## STEP 4: Scaffold project (Init only)

Write following files. Do NOT write on update runs.

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
`data-spec-*` attributes on the document `<body>`, and an optional
`appNav` prop (`specs.app_nav`, only passed by the screen template — see
§ App-shell navigation; `index.astro` and the journey template do NOT pass
it, matching static-html's precedent that the generated nav renders only
inside a screen's shell wrapper):

```astro
---
import '../styles/global.css';
const { title = 'Walkthrough', bodyAttrs = {}, appNav = null } = Astro.props;
---
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
  </head>
  <body {...bodyAttrs} class="bg-white text-gray-900 font-sans p-4">
    {appNav && (
      <nav class="app-nav" data-spec-element={appNav.element_id} data-spec-provisional="true">
        {appNav.groups.map((group: any) => (
          <div class="nav-group">
            <span class="nav-group-label">{group.label}</span>
            <ul class="flex gap-4 list-none p-0">
              {group.items.map((item: any) => (
                <li><a href={item.href ?? '#'} data-spec-element={item.element_id} data-spec-provisional="true">{item.label}</a></li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
    )}
    <slot />
    <footer class="mt-8 text-sm text-gray-500">
      <a href="/">← Back to index</a>
    </footer>
  </body>
</html>
```

`appNav` is shaped `{ element_id: "app-nav", groups: [{ label, items:
[{label, href, element_id}] }] }` — grouped exactly like the derived-default
case's directory grouping (§ App-shell navigation), or a single unlabeled
group when the shell-authoritative case applies (no group subdivision for
an authored nav — "the authored order is used verbatim").

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

Unchanged by this revision — `index.astro` doesn't render per-element
content or the app-nav (§ App-shell navigation only requires the generated
nav inside screen pages), so it's out of this revision's scope.

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

function provAttr(el: any): string {
  return el.provisional ? ' data-spec-provisional="true"' : '';
}

function renderItems(items: any[], kind: string): string {
  if (!items || items.length === 0) {
    return kind === 'list' ? '<li>…</li>' : '';
  }
  return items
    .map((item: any, i: number) => {
      const prov = provAttr(item);
      const label = item.label ?? String(item);
      if (kind === 'list') {
        const inner = item.href ? `<a href="${item.href}">${label}</a>` : label;
        return `<li data-spec-element="${item.element_id}"${prov}>${inner}</li>`;
      }
      if (kind === 'tabs') {
        const active = i === 0 ? ' active' : '';
        return item.href
          ? `<a href="${item.href}" class="tab${active}" data-spec-element="${item.element_id}"${prov}>${label}</a>`
          : `<span class="tab${active}" data-spec-element="${item.element_id}"${prov}>${label}</span>`;
      }
      // nav
      return `<li><a href="${item.href ?? '#'}" data-spec-element="${item.element_id}"${prov}>${label}</a></li>`;
    })
    .join('\n');
}

function renderTable(el: any): string {
  const thead = `<tr>${el.columns.map((c: string) => `<th class="border px-2 py-1 text-left">${c}</th>`).join('')}</tr>`;
  let tbody: string;
  if (el.sample_rows && el.sample_rows.length > 0) {
    tbody = el.sample_rows
      .map((row: string[]) => {
        const cells = row.map((cell: string, i: number) => {
          const content = i === 0 && el.row_href ? `<a href="${el.row_href}">${cell}</a>` : cell;
          return `<td class="border px-2 py-1">${content}</td>`;
        });
        return `<tr>${cells.join('')}</tr>`;
      })
      .join('\n');
  } else {
    // No sample_rows declared — header + one skeleton row, never fabricated content.
    tbody = `<tr>${el.columns.map(() => '<td class="border px-2 py-1"></td>').join('')}</tr>`;
  }
  return `<table data-spec-element="${el.element_id}"${provAttr(el)} class="border-collapse w-full"><thead>${thead}</thead><tbody>${tbody}</tbody></table>`;
}

function renderElement(el: any): string {
  const prov = provAttr(el);
  const href = el.href ?? '#';
  let base: string;
  switch (el.kind) {
    case 'input':
      base = el.options
        ? `<select name="${el.element_id}" aria-label="${el.label}" data-spec-element="${el.element_id}"${prov} class="border rounded px-2 py-1">${el.options.map((o: string) => `<option value="${o}">${o}</option>`).join('')}</select>`
        : `<input name="${el.element_id}" aria-label="${el.label}" data-spec-element="${el.element_id}"${prov} class="border rounded px-2 py-1" />`;
      break;
    case 'button':
      base = el.href
        ? `<a href="${href}" data-spec-element="${el.element_id}"${prov} class="button px-4 py-2 bg-primary text-white rounded inline-block">${el.label}</a>`
        : `<button data-spec-element="${el.element_id}"${prov} class="px-4 py-2 bg-primary text-white rounded">${el.label}</button>`;
      break;
    case 'link':
      base = `<a href="${href}" data-spec-element="${el.element_id}"${prov} class="text-blue-600 underline">${el.label}</a>`;
      break;
    case 'image':
      base = `<img src="#" alt="${el.label}" data-spec-element="${el.element_id}"${prov} class="w-full" />`;
      if (el.href) base = `<a href="${href}">${base}</a>`;
      break;
    case 'text':
      base = `<span data-spec-element="${el.element_id}"${prov}>${el.label}</span>`;
      break;
    case 'region':
      base = `<section data-spec-element="${el.element_id}"${prov}><h3>${el.label}</h3></section>`;
      break;
    case 'list': {
      const inner = renderItems(el.items, 'list');
      base = `<ul data-spec-element="${el.element_id}"${prov} class="list-disc pl-6">${inner}</ul>`;
      if (el.href) base = `<a href="${href}">${base}</a>`;
      break;
    }
    case 'form':
      base = `<form data-spec-element="${el.element_id}"${prov}></form>`;
      break;
    case 'nav': {
      const inner = renderItems(el.items, 'nav');
      base = `<nav data-spec-element="${el.element_id}"${prov} class="flex gap-4">${inner}</nav>`;
      break;
    }
    case 'tabs': {
      const inner = renderItems(el.items, 'tabs');
      base = `<nav class="tabs flex gap-2 border-b" data-spec-element="${el.element_id}"${prov}>${inner}</nav>`;
      break;
    }
    case 'table':
      base = renderTable(el);
      break;
    case 'media':
      base = `<figure data-spec-element="${el.element_id}"${prov}><figcaption>${el.label}</figcaption></figure>`;
      break;
    default: // custom, and unknown_element_kind fallback
      base = `<div data-spec-element="${el.element_id}"${prov}>${el.label}</div>`;
      if (el.href) base = `<a href="${href}" data-spec-element="${el.element_id}"${prov}>${el.label}</a>`;
  }
  const states = (el.states || [])
    .filter((s: string) => s !== 'default')
    .map((s: string) => `<span class="state-${s}">${el.label} [${s}]</span>`)
    .join('');
  return `<div>${base}${states}</div>`;
}

const nonProvisional = screen.elements.filter((el: any) => !el.provisional);
const openPanel = nonProvisional.length === 0;
---
<Shell title={screen.title || screen.screen_id} bodyAttrs={{ 'data-spec-screen': screen.screen_id }} appNav={screen.app_nav}>
  <h1 class="text-2xl font-bold mb-4">{screen.title || screen.screen_id}</h1>
  <main class="space-y-4">
    {screen.elements.map((el: any) => (
      <Fragment set:html={renderElement(el)} />
    ))}
  </main>
  <details class="spec-panel mt-4 border rounded p-2" open={openPanel}>
    <summary class="cursor-pointer font-semibold">View spec</summary>
    <Fragment set:html={screen.body_html} />
  </details>
  <section class="mt-8 text-sm text-gray-500">
    <p>Journeys: {screen.journeys.length === 0 ? 'none' :
      screen.journeys.map((jid: string) => (
        <a href={`/journey/${jid}`} class="underline mr-2">{jid}</a>
      ))
    }</p>
  </section>
</Shell>
```

Per-kind mapping mirrors `contracts/walkthrough_renderer.md` § kind → DOM
tag mapping exactly (this renderer implements every row, same as
static-html): `link`/`button`/`image`/`custom` wrap in `<a>` iff `el.href`
is set; `list` renders one `<li>` per item (each with its own resolved
`href` when declared) plus an independent outer-`<a>` wrap when the list
element's own `href` is set; `table` builds `<thead>` from `columns` and
either real `<tbody>` rows from `sample_rows` (first cell wrapped in `<a>`
when `row_href` is set) or one skeleton row when `sample_rows` is absent
— never fabricated; `tabs` marks the first entry `active`, entries with an
`href` render as `<a class="tab">`, others as inert `<span class="tab">`;
`input` becomes a real `<select>` with one `<option>` per value when
`options` is present. States beyond `default` render as adjacent
`<span class="state-<n>">` siblings, same convention already established
by this template before this revision.

`screen.app_nav` is set by STEP 5 to the same `{element_id, groups}` shape
`Shell.astro` expects, or `null`/absent when this screen has no nav to
render (never the case in practice — every screen gets the generated nav
per § App-shell navigation — but the prop stays optional so `Shell.astro`
also works for `index.astro`/the journey template, which never pass it).

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

Unchanged by this revision — journey pages never render per-element
content or the app-nav (§ Screen-in-multiple-journeys rule: journey-nav
and screen content are deliberately kept separate), so this template is
out of this revision's scope.

## STEP 5: Generate `specs.json` and `global.css` (both modes)

Write `src/data/specs.json` derived from the in-memory model built in
STEP 2 (screens with `body_html`, pre-resolved `href`/`row_href`, and
normalised `items[]`; top-level `app_nav`, reshaped into the
`{element_id, groups}` form `Shell.astro` expects; each screen also gets
its own `app_nav` field set to that same shared object, since every screen
renders the identical generated nav — see § App-shell navigation). Schema
as shown in § `specs.json` shape above. Overwrite unconditionally.

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

Overwrite unconditionally. File is agent-managed every run.

On update runs only: compare count of `--token-*` keys in freshly derived
in-memory model vs. CSS var declarations in existing `global.css` before
overwriting. If counts differ, append `kind: "stale_tailwind_config"` to
`warnings[]`.

## STEP 6: Build

Run from `_concept/mockup-walkthrough/astro/`:

```bash
bun run build
```

On non-zero exit: print full stderr, exit non-zero. Do not write
`manifest.json`.

After build: verify `dist/` does NOT exist under project root. If it does:
fail with "astro.config.mjs outDir misconfigured — dist/ must not exist".

## STEP 7: Write `manifest.json`

Emit pinned schema (`contracts/walkthrough_renderer.md` § Manifest schema,
`schema_version: "1.2"`). Build from the STEP 2 in-memory model — NOT by
serialising `specs.json`. Template-only fields from `specs.json`
(`screens[].title`, `screens[].group`, `screens[].journeys[]`,
`screens[].body_html`, `screens[].elements[].href`, `.row_href`,
`items[].element_id`/`.provisional`/`.href`, `journeys[].title`,
`journeys[].description`, `app_nav[].href`) MUST NOT appear in
`manifest.json` — see § `specs.json` → `manifest.json` projection above.

New fields this revision adds to `manifest.json#screens[].elements[]`:
`target` / `row_target` / `columns` / `sample_rows` / `items` / `options`,
echoed **verbatim** from the declared frontmatter (the *declared* value,
never the resolved `href` — matches static-html and the pinned contract
exactly). Top-level `app_nav[]` — one entry per rendered nav link, in
rendered order (positional, not alphabetic): `{label, target, source}`
where `target` IS the resolved href (per contract § Field semantics,
app_nav's `target` is the rendered value, unlike element `target`).

Sort `screens[]` by `screen_path`, `journeys[]` by `journey_id`,
`features[]` by `feature_path`. `app_nav[]` is NOT sorted — it keeps
rendered order. Write atomically (tmp → fsync → rename).

`renderer: "mockup-walkthrough-astro"`, `renderer_version:` this SKILL.md's
`metadata.version`.

## STEP 8: Validate

Run from repo root:

```bash
python mockup-walkthrough/astro/validator.py _concept/mockup-walkthrough/astro
```

Exit 0 = ready. Exit 2 = violation report.

## Error handling

### Shared conditions

See `contracts/walkthrough_renderer.md` § Shared error handling — including
`unresolved_target` (soft-fail, `href` falls back to `'#'`, never
hard-fail) and `no_explicit_elements` (spec panel renders `open`).

### Astro-specific

| Condition | Behaviour |
|---|---|
| `bun install` exits non-zero | Fail loudly with stderr; do not build |
| `bun run build` exits non-zero | Fail loudly with stderr; do not write `manifest.json` |
| `dist/` exists after build | Fail: "astro.config.mjs outDir misconfigured — dist/ must not exist" |
| Token count differs from CSS var count (update runs only) | `kind: "stale_tailwind_config"`; user must extend `tailwind.config.mjs` manually |
| Scaffold missing `el.href` and/or `spec-panel` (update runs only) | `kind: "stale_scaffold"`; user must delete the scaffold or port the template changes (§ `stale_scaffold` check, STEP 3) |

### `warnings[].kind` enum

Shared enum per `contracts/walkthrough_renderer.md` § warnings[].kind enum
(`auto_slugged`, `auto_slug_collision`, `missing_layout`, `missing_feature`,
`unknown_element_kind`, `missing_screen`, `missing_screen_sequence`,
`no_journeys`, `unresolved_target`, `no_explicit_elements`);
`stale_tailwind_config` and `stale_scaffold` are this renderer's two
Astro-specific additions.

## MUST / NEVER

Shared MUST/NEVER: `contracts/walkthrough_renderer.md` § Shared MUST / NEVER.

MUST  set emptyOutDir: false in astro.config.mjs
MUST  set build.format: 'file' in astro.config.mjs
MUST  set outDir: '.' in astro.config.mjs
MUST  write specs.json and global.css before running bun run build
MUST  regenerate global.css on every run (agent-managed)
MUST  return getStaticPaths() slugs without trailing slashes
MUST  pre-resolve every `target`/`row_target`/`items[].target` into an `href` (or `null`) in `specs.json` at STEP 2/5 — the `.astro` templates only interpolate `el.href ?? '#'`, they never resolve a target themselves
MUST  keep the shared content-fidelity and spec-panel MUSTs (`walkthrough_renderer.md` § Shared MUST/NEVER) true specifically in the scaffolded `.astro` templates, sourced from `specs.json`'s `body_html`
MUST  run the `stale_scaffold` check on every update run and record a `warnings[]` entry when the scaffold predates this revision

NEVER regenerate astro.config.mjs, tailwind.config.mjs, or .astro templates on update runs
NEVER create a dist/ subdirectory — outDir must be '.'
NEVER use a separate auto_slugged[] array — set provisional: true on the element object (the kind: "auto_slugged" warning entry in manifest.warnings[] is still required per the auto-slug step)
NEVER let a scaffolded `.astro` template re-derive target resolution or auto-slug ids at build time — that logic lives in STEP 2 only

## CHECKLIST

- [ ] `_concept/mockup-walkthrough/astro/index.html` exists
- [ ] `_concept/mockup-walkthrough/astro/manifest.json` exists and parses as JSON
- [ ] `manifest.schema_version == "1.2"` and `manifest.renderer == "mockup-walkthrough-astro"`
- [ ] One `screen/<group>/<name>.html` per screen file under `experience/screens/`
- [ ] One `journey/<id>.html` per journey in `stories.yaml`
- [ ] Every `<body>` in `screen/**/*.html` has `data-spec-screen`
- [ ] Every annotatable node in `screen/**/*.html` has `data-spec-element`
- [ ] Every auto-slugged element node also has `data-spec-provisional="true"`
- [ ] Every `<body>` in `journey/**/*.html` has `data-spec-journey`
- [ ] `index.html` `<body>` has `data-spec-index="true"`
- [ ] No `dist/` subdirectory under `_concept/mockup-walkthrough/astro/`
- [ ] At least one `<link rel="stylesheet">` in `index.html` and referenced CSS file is non-empty
- [ ] Every screen page contains the app nav (`<nav class="app-nav">`) with one resolvable href per entry
- [ ] Every element with a resolvable target renders an `<a>` (or wraps one) whose `href` resolves to an existing rendered file — no `href="#"` on a node whose manifest element declares a resolved target
- [ ] No canonical spec heading appears as an `el-region` widget (no `data-spec-element` value is a canonical-heading slug)
- [ ] Every declared table renders `sample_rows` verbatim as `<tbody>` rows
- [ ] Spec body appears only inside `<details class="spec-panel">`
- [ ] `manifest.app_nav[]` is present and every entry resolves to an existing rendered file
- [ ] Validator (`mockup-walkthrough/astro/validator.py`) exits 0

EMIT  [mockup-walkthrough-astro] started run_id=<uuid>
EMIT  [mockup-walkthrough-astro] checkpoint screens=<N> journeys=<M>
EMIT  [mockup-walkthrough-astro] completed run_id=<uuid> screens=<N> journeys=<M> warnings=<W>
