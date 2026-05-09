# Design: walkthrough-mockup-astro (Task 3C)

**Date:** 2026-05-09
**Status:** approved
**Author:** matthias (brainstormed with Claude)

## Scope

Author the `walkthrough-mockup-astro` SKILL.md only — Lit and framework variants are deferred. Astro is priority as it is the standard-app default stack.

## What it produces

A built Astro static site at `_concept/walkthrough-mockup/astro/` with:
- The same four inputs as `walkthrough-mockup-static-html` (screens, journeys, tokens, features)
- The same `data-spec-*` DOM attribute contract on identical positions
- The same `manifest.json` schema (`schema_version: "1.0"`, `renderer: "walkthrough-mockup-astro"`)
- Tailwind CSS styling driven by `design/tokens.json`
- The Astro source committed alongside the built HTML (no `dist/` subdirectory)

## SKILL.md frontmatter

The produced SKILL.md must have the following YAML frontmatter:

```yaml
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
        description: "Screen specs are the primary input"
        min_entries: 1
      - path: "experience/journeys/stories.json"
        gate: hard
        description: "Journey definitions"
      - path: "design/tokens.json"
        gate: hard
        description: "Brand tokens → Tailwind config + CSS vars"
      - path: "product-spec/features"
        gate: soft
        description: "Feature files for traceability; absence is a warning"
        min_entries: 1
    produces:
      - path: "_concept/walkthrough-mockup/astro"
        description: "Astro project source + built site: index.html, screen/<group>/<name>.html, journey/<id>.html, manifest.json"
---
```

## Architecture

### Two-mode behavior

The agent detects mode by checking for `_concept/walkthrough-mockup/astro/astro.config.mjs`:

- **Init** (file absent): scaffold full project skeleton → generate `src/data/specs.json` → `bun install` → `astro build` → write `manifest.json`
- **Update** (file present): regenerate `src/data/specs.json` and `src/styles/global.css` only → `astro build` → rewrite `manifest.json`

On update runs the agent NEVER touches `astro.config.mjs`, `tailwind.config.mjs`, or `.astro` template files — those belong to the user.

### Generation approach

Approach A (agent-direct): the agent reads screen specs, derives `src/data/specs.json` inline (no persistent generator script), runs `astro build`, and writes `manifest.json` from the same in-memory model. Chosen for simplicity and alignment with the static-html pattern.

## File layout

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
├── package.json
├── _astro/                                 ← hashed CSS/JS chunks emitted by Astro build (committed)
├── index.html                              ← built output
├── screen/<group>/<name>.html              ← built output
├── journey/<id>.html                       ← built output
└── manifest.json                           ← written after build, not by Astro
```

Key Astro config decisions:
- `outDir: '.'` and `emptyOutDir: false` — built HTML lands at project root without clobbering `src/`
- `build.format: 'file'` — produces `screen/01_user_auth/login.html` not `screen/01_user_auth/login/index.html`
- Three dynamic route templates serve all screens and journeys (no per-screen file authoring)
- `_astro/` directory: Astro emits hashed CSS/JS bundle chunks here; commit alongside built HTML; the validator does NOT flag its presence

**`global.css` ownership:** `global.css` is **agent-managed** (regenerated each run alongside `specs.json`). This ensures new tokens from `tokens.json` appear in `:root` on every update run. `tailwind.config.mjs` is **user-owned** (scaffolded once, never regenerated). If the user adds tokens that require new Tailwind utilities, they must extend `tailwind.config.mjs` manually; on update runs only, the skill emits a `manifest.warnings[]` entry of `kind: "stale_tailwind_config"` when `tokens.json` has changed since init (detected by comparing token key count in the freshly derived `specs.json` vs. CSS var declarations in the existing `global.css` before it is overwritten). On init runs this check is skipped — there is no prior `global.css` to compare against.

## Data flow

`specs.json` is the single bridge between source artefacts and Astro templates.

### specs.json shape

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
      "description": "First-time user authenticates and lands on the home screen.",
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

**Auto-slug handling:** auto-slugged elements have `"provisional": true` on the element object itself — there is NO separate top-level `auto_slugged[]` array. This matches the static-html contract exactly. The Astro template emits `data-spec-provisional="true"` on any element where `element.provisional === true`. `source_anchor` for provisional elements uses the `#auto/<element_id>` fragment form.

### Template consumption

`.astro` templates read `specs.json` at build time via `import specs from '../data/specs.json'`. Dynamic routes use `getStaticPaths()` to expand screens and journeys. The `[...slug].astro` page returns `params` where `slug` is the `screen_id` string (e.g. `"01_user_auth/login"`). `getStaticPaths()` MUST NOT append a trailing slash to slug values — Astro + `build.format: 'file'` will produce the correct `.html` filename from a slash-delimited slug. All `data-spec-*` attributes are emitted from template expressions using `specs.json` fields — identical DOM positions to static-html.

### specs.json → manifest.json projection

`specs.json` carries additional navigation-convenience fields that the Astro templates need but that the pinned manifest schema does not include. The agent MUST NOT copy these template-only fields into `manifest.json`:

- `screens[].title`, `screens[].group`, `screens[].journeys[]` — template-only; absent from manifest `screens[]`
- `journeys[].title`, `journeys[].description` — template-only; absent from manifest `journeys[]`

The agent builds `manifest.json` from the same in-memory model, but uses the pinned manifest shape directly — not by serialising `specs.json`. The pinned `manifest.json#screens[]` shape is: `screen_path`, `screen_id`, `rendered_html`, `implements`, `data_entities`, `layout`, `elements[]`. The pinned `manifest.json#journeys[]` shape is: `journey_id`, `rendered_html`, `source`, `screen_sequence`.

### manifest.json

Written after `astro build` completes, from the same in-memory model. Matches the pinned schema exactly — only `renderer` and `renderer_version` differ from the static-html variant. Sort order: screens by `screen_path`, journeys by `journey_id`, features by `feature_path`. Written atomically (tmp → rename).

### Token → Tailwind mapping

`tokens.json` is flattened depth-first to CSS custom properties using the same rule as `component-mockup-isolated-html` and `walkthrough-mockup-static-html`:
- `{"color": {"primary": "#0ea5e9"}}` → `--token-color-primary: #0ea5e9`

On init, `tailwind.config.mjs` is scaffolded to expose these vars as Tailwind utilities. `global.css` declares them on `:root` and is regenerated every run (agent-managed). The user can extend `tailwind.config.mjs` freely — it is not regenerated on update runs.

## SKILL.md step structure

**STEP 1 — Read inputs** (identical to static-html)
Parse all screen files, `stories.json`, `tokens.json`, features. Apply auto-slug fallback (provisional elements get `provisional: true` on the element object, `source_anchor: "#auto/<id>"`). Build in-memory model with `{ screens, journeys, token_vars, features, warnings }`.

**STEP 2 — Detect mode**
Check `_concept/walkthrough-mockup/astro/astro.config.mjs`. Absent → Init. Present → Update.

**STEP 3 — Init only: scaffold project**
Write `astro.config.mjs`, `tailwind.config.mjs`, `package.json` (with `astro`, `@astrojs/tailwind`, `tailwindcss`), `src/layouts/Shell.astro`, `src/pages/index.astro`, `src/pages/screen/[...slug].astro`, `src/pages/journey/[id].astro`. Run `bun install`.

**STEP 4 — Generate `specs.json` and `global.css`** (both modes)
Derive `src/data/specs.json` from in-memory model. Write `src/styles/global.css` with `:root { <token vars> }` + Tailwind base directives. Overwrite both unconditionally.

**STEP 5 — Build**
Run `bun astro build` from the project root. On non-zero exit: fail loudly with full stderr, do not proceed.

**STEP 6 — Write `manifest.json`**
Emit pinned schema with `renderer: "walkthrough-mockup-astro"`, `renderer_version` from SKILL.md frontmatter. Same sort order as static-html. Write atomically (tmp → rename).

**STEP 7 — Validate**
Run `walkthrough-mockup/astro/validator.py _concept/walkthrough-mockup/astro`.

## ROLE / READS / WRITES / REFERENCES

```
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
```

## Error handling

### Inherited from static-html (identical behavior)

| Condition | Behavior |
|---|---|
| Malformed YAML in screen file | Fail loudly, exit non-zero, name the file |
| Screen in journey but missing on disk | `manifest.warnings[]` `kind: "missing_screen"` + dead-end placeholder link |
| `screen_sequence` absent for a journey | `manifest.warnings[]` `kind: "missing_screen_sequence"`, skip that journey render |
| Zero journeys in `stories.json` | Render `"No journeys defined"`, `kind: "no_journeys"` |
| Missing `product-spec/features/` | Soft gate, `kind: "missing_feature"`, continue |
| Unknown `elements:` kind | Render as `custom`, `kind: "unknown_element_kind"`, warn |
| `layout:` reference pointing to non-existent file | `kind: "missing_layout"`, fall back to `Shell.astro` default |
| Auto-slug collision | `kind: "auto_slug_collision"`, suffix auto id with `-2`, `-3`, ... |

### Astro-specific

| Condition | Behavior |
|---|---|
| `bun install` exits non-zero | Fail loudly with stderr; do not build |
| `astro build` exits non-zero | Fail loudly with stderr; do not write `manifest.json` |
| `dist/` subdirectory exists after build | Fail: "astro.config.mjs outDir misconfigured — dist/ must not exist" |
| `tokens.json` key count differs from CSS var count in existing `global.css` (update runs only) | `kind: "stale_tailwind_config"` warning; user must extend `tailwind.config.mjs` manually |
| Update run would touch `.astro` files or `astro.config.mjs` | NEVER rule |

### `warnings[].kind` enum

The full set of warning kinds (inherited from static-html, no new kinds added):
`auto_slugged`, `auto_slug_collision`, `missing_layout`, `missing_feature`, `unknown_element_kind`, `missing_screen`, `missing_screen_sequence`, `no_journeys`, `stale_tailwind_config`

`stale_tailwind_config` is the only Astro-specific addition to the enum.

## Validator

`walkthrough-mockup/astro/validator.py` extends the static-html validator.

**Inherited checks:**
- Every `data-spec-*` attribute resolves to an existing source file or rendered HTML
- `manifest.json` matches pinned schema
- Every screen link inside `journey/<id>.html` resolves
- No external (non-relative) `<script src="...">` in any output file

**Astro-specific checks:**
- No `dist/` subdirectory under the output root
- `manifest.renderer == "walkthrough-mockup-astro"`
- At least one `<link rel="stylesheet">` in `index.html` AND the referenced CSS file is non-empty (size > 0 bytes)

## MUST / NEVER

```
MUST  emit data-spec-screen on every screen <body>
MUST  emit data-spec-element on every annotatable child node
MUST  emit data-spec-provisional="true" on auto-slugged element nodes
MUST  emit data-spec-journey="<id>" on every journey <body>
MUST  emit data-spec-index="true" on index.html <body>
MUST  write manifest.json conforming to pinned schema (schema_version: "1.0")
MUST  sort manifest arrays lexicographically
MUST  set emptyOutDir: false in astro.config.mjs
MUST  set build.format: 'file' in astro.config.mjs
MUST  set outDir: '.' in astro.config.mjs
MUST  write specs.json and global.css before running astro build
MUST  regenerate global.css on every run (agent-managed)
MUST  return getStaticPaths() slugs without trailing slashes

NEVER regenerate astro.config.mjs, tailwind.config.mjs, or .astro templates on update runs
NEVER create a dist/ subdirectory — outDir must be '.'
NEVER emit data-spec-* attributes outside the pinned table
NEVER mutate source files (experience/screens/**, stories.json, tokens.json, features/**)
NEVER inject journey-step navigation into screen/**/*.html
NEVER inline absolute filesystem paths in manifest.json
NEVER use a separate auto_slugged[] array — set provisional: true on the element object (the kind: "auto_slugged" warning entry in manifest.warnings[] is still required per auto-slug step)
```

## CHECKLIST

- [ ] `_concept/walkthrough-mockup/astro/index.html` exists
- [ ] `_concept/walkthrough-mockup/astro/manifest.json` exists and parses as JSON
- [ ] `manifest.schema_version == "1.0"` and `manifest.renderer == "walkthrough-mockup-astro"`
- [ ] One `screen/<group>/<name>.html` per screen file under `experience/screens/`
- [ ] One `journey/<id>.html` per journey in `stories.json`
- [ ] Every `<body>` in `screen/**/*.html` has `data-spec-screen`
- [ ] Every annotatable node in `screen/**/*.html` has `data-spec-element`
- [ ] Every auto-slugged element node also has `data-spec-provisional="true"`
- [ ] Every `<body>` in `journey/**/*.html` has `data-spec-journey`
- [ ] `index.html` `<body>` has `data-spec-index="true"`
- [ ] No `dist/` subdirectory under `_concept/walkthrough-mockup/astro/`
- [ ] At least one `<link rel="stylesheet">` in `index.html` and referenced CSS file is non-empty
- [ ] Validator (`walkthrough-mockup/astro/validator.py`) exits 0

## EMIT

```
EMIT  [walkthrough-mockup-astro] started run_id=<uuid>
EMIT  [walkthrough-mockup-astro] checkpoint screens=<N> journeys=<M>
EMIT  [walkthrough-mockup-astro] completed run_id=<uuid> screens=<N> journeys=<M> warnings=<W>
```

## Outputs

| Path | Description |
|---|---|
| `walkthrough-mockup/astro/SKILL.md` | The agent prompt (primary deliverable) |
| `walkthrough-mockup/astro/validator.py` | Validation script (extends static-html's) |
| `_concept/walkthrough-mockup/astro/` | Generated Astro project + built site |

## Relation to existing skills

- Consumes the same input contract as `walkthrough-mockup-static-html` (Task 2F) — no input changes
- Emits the same `manifest.json` schema — `mockup-feedback-annotate` (Task 3A) reads either renderer's output unchanged
- `data-spec-*` attribute positions are identical — `mockup-feedback-triage/patch/apply` (Task 3B) works on either renderer's output
