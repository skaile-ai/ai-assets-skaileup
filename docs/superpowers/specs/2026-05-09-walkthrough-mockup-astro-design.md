# Design: walkthrough-mockup-astro (Task 3C)

**Date:** 2026-05-09
**Status:** approved
**Author:** matthias (brainstormed with Claude)

## Scope

Author the `walkthrough-mockup-astro` SKILL.md — one of the three Phase 3C renderers. Lit and framework variants are deferred; Astro is priority as it is the standard-app default stack.

## What it produces

A built Astro static site at `_concept/walkthrough-mockup/astro/` with:
- The same four inputs as `walkthrough-mockup-static-html` (screens, journeys, tokens, features)
- The same `data-spec-*` DOM attribute contract on identical positions
- The same `manifest.json` schema (`schema_version: "1.0"`, `renderer: "walkthrough-mockup-astro"`)
- Tailwind CSS styling driven by `design/tokens.json`
- The Astro source committed alongside the built HTML (no `dist/` subdirectory)

## Architecture

### Two-mode behavior

The agent detects mode by checking for `_concept/walkthrough-mockup/astro/astro.config.mjs`:

- **Init** (file absent): scaffold full project skeleton → generate `specs.json` → `bun install` → `astro build` → write `manifest.json`
- **Update** (file present): regenerate `specs.json` only → `astro build` → rewrite `manifest.json`

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
│       └── global.css                      ← Tailwind base + :root token vars
├── astro.config.mjs                        ← outDir='.', emptyOutDir=false
├── tailwind.config.mjs                     ← generated from tokens.json on init
├── package.json
├── index.html                              ← built output
├── screen/<group>/<name>.html              ← built output
├── journey/<id>.html                       ← built output
└── manifest.json                           ← written after build, not by Astro
```

Key Astro config decisions:
- `outDir: '.'` and `emptyOutDir: false` — built HTML lands at project root without clobbering `src/`
- `build.format: 'file'` — produces `screen/01_user_auth/login.html` not `screen/01_user_auth/login/index.html`
- Three dynamic route templates serve all screens and journeys (no per-screen file authoring)

## Data flow

`specs.json` is the single bridge between source artefacts and Astro templates.

### specs.json shape

```json
{
  "screens": [
    {
      "screen_id": "01_user_auth/login",
      "screen_path": "experience/screens/01_user_auth/login.md",
      "group": "01_user_auth",
      "title": "Login",
      "elements": [
        {
          "element_id": "submit-button",
          "kind": "button",
          "label": "Sign in",
          "states": ["default", "loading"],
          "provisional": false
        }
      ],
      "journeys": ["user-signs-in"],
      "auto_slugged": ["kpi-card-1"]
    }
  ],
  "journeys": [
    {
      "journey_id": "user-signs-in",
      "title": "User signs in",
      "description": "First-time user authenticates and lands on the home screen.",
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

### Template consumption

`.astro` templates read `specs.json` at build time via `import specs from '../data/specs.json'`. Dynamic routes use `getStaticPaths()` to expand screens and journeys. All `data-spec-*` attributes are emitted from template expressions using `specs.json` fields — identical DOM positions to static-html.

### manifest.json

Written after `astro build` completes, from the same in-memory model. Matches the pinned schema exactly — only `renderer` and `renderer_version` differ from the static-html variant.

### Token → Tailwind mapping

`tokens.json` is flattened depth-first to CSS custom properties using the same rule as `component-mockup-isolated-html` and `walkthrough-mockup-static-html`:
- `{"color": {"primary": "#0ea5e9"}}` → `--token-color-primary: #0ea5e9`

On init, `tailwind.config.mjs` is scaffolded to expose these vars as Tailwind utilities. `global.css` declares them on `:root`. The user can extend `tailwind.config.mjs` freely — it is not regenerated on update runs.

## SKILL.md step structure

**STEP 1 — Read inputs** (identical to static-html)
Parse all screen files, `stories.json`, `tokens.json`, features. Apply auto-slug fallback. Build in-memory model with `{ screens, journeys, token_vars, features, warnings }`.

**STEP 2 — Detect mode**
Check `_concept/walkthrough-mockup/astro/astro.config.mjs`. Absent → Init. Present → Update.

**STEP 3 — Init only: scaffold project**
Write `astro.config.mjs`, `tailwind.config.mjs`, `package.json` (with `astro`, `@astrojs/tailwind`, `tailwindcss`), `src/layouts/Shell.astro`, `src/pages/index.astro`, `src/pages/screen/[...slug].astro`, `src/pages/journey/[id].astro`, `src/styles/global.css`. Run `bun install`.

**STEP 4 — Generate specs.json** (both modes)
Derive `src/data/specs.json` from in-memory model. Overwrite unconditionally.

**STEP 5 — Build**
Run `bun astro build` from the project root. On non-zero exit: fail loudly with full stderr, do not proceed.

**STEP 6 — Write manifest.json**
Emit pinned schema with `renderer: "walkthrough-mockup-astro"`, `renderer_version` from SKILL.md frontmatter. Same sort order as static-html (screens by `screen_path`, journeys by `journey_id`, features by `feature_path`). Write atomically (tmp → rename).

**STEP 7 — Validate**
Run `walkthrough-mockup/astro/validator.py _concept/walkthrough-mockup/astro`.

## Error handling

### Inherited from static-html (identical behavior)

| Condition | Behavior |
|---|---|
| Malformed YAML in screen file | Fail loudly, exit non-zero, name the file |
| Screen in journey but missing on disk | `manifest.warnings[]` + dead-end placeholder link |
| Missing `product-spec/features/` | Soft gate, warn, continue |
| Unknown `elements:` kind | Render as `custom`, warn |

### Astro-specific

| Condition | Behavior |
|---|---|
| `bun install` exits non-zero | Fail loudly with stderr; do not build |
| `astro build` exits non-zero | Fail loudly with stderr; do not write `manifest.json` |
| `dist/` subdirectory exists after build | Fail: "astro.config.mjs outDir misconfigured — dist/ must not exist" |
| Update run would touch `.astro` files or `astro.config.mjs` | NEVER rule (not a runtime check) |

## Validator

`walkthrough-mockup/astro/validator.py` extends the static-html validator:

**Inherited checks:**
- Every `data-spec-*` attribute resolves to an existing source file or rendered HTML
- `manifest.json` matches pinned schema
- Every screen link inside `journey/<id>.html` resolves
- No external (non-relative) `<script src="...">` in any output file

**Astro-specific checks:**
- No `dist/` subdirectory under the output root
- `manifest.renderer == "walkthrough-mockup-astro"`
- At least one `<link rel="stylesheet">` present in `index.html` (Tailwind was applied)

## MUST / NEVER

```
MUST  emit data-spec-screen on every screen <body>
MUST  emit data-spec-element on every annotatable child node
MUST  emit data-spec-provisional="true" on auto-slugged element nodes
MUST  write manifest.json conforming to pinned schema (schema_version: "1.0")
MUST  sort manifest arrays lexicographically
MUST  set emptyOutDir: false in astro.config.mjs
MUST  use build.format: 'file' in astro.config.mjs
MUST  write specs.json before running astro build

NEVER regenerate astro.config.mjs, tailwind.config.mjs, or .astro templates on update runs
NEVER create a dist/ subdirectory — outDir must be '.'
NEVER emit data-spec-* attributes outside the pinned table
NEVER mutate source files (experience/screens/**, stories.json, tokens.json, features/**)
NEVER inject journey-step navigation into screen/**/*.html
NEVER inline absolute filesystem paths in manifest.json
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
- [ ] No `dist/` subdirectory under `_concept/walkthrough-mockup/astro/`
- [ ] At least one stylesheet link in `index.html`
- [ ] Validator (`walkthrough-mockup/astro/validator.py`) exits 0

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
