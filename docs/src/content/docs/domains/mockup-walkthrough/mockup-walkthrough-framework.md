---
title: "mockup-walkthrough-framework"
description: "Use when stakeholders need the highest-fidelity clickable walkthrough rendered in the project's CHOSEN stack framework (Next.js / Nuxt / SvelteKit), resolved from the selected scaffold template. Generates a stack-native built site — one route/page pe"
sourcePath: "skaileup/mockup-walkthrough/framework/SKILL.md"
sidebar:
  label: "mockup-walkthrough-framework"
---

:::note[Skill manifest]
**Name:** `mockup-walkthrough-framework`
**Stage:** alpha · **Version:** 0.1.0
**Tags:** walkthrough, mockup, framework, stack-native, complex-app, frontend, prototype, data-spec
:::


# Walkthrough Mockup — Framework (stack-native)

## Overview

Highest-fidelity variant of the walkthrough mockup cluster, used by the
**complex-app** tier. Consumes the same four inputs as
`mockup-walkthrough-static-html` (screen specs, journey definitions, brand
tokens, feature files) PLUS one more — `_concept/blueprint/techstack.md` —
and produces a built site rendered in the **project's chosen framework**
(Next.js / Nuxt / SvelteKit) at `_concept/mockup-walkthrough/framework/`.

The framework is not fixed: it is resolved from the `tech_stack_skill`
field in `techstack.md`, which names exactly one concrete scaffold template
under `impl-architecture/templates/template-*/`. That template's
`TEMPLATE.md` is the authority for which framework to scaffold, its
scaffold/dev/build commands, and its routing conventions. This makes the
framework walkthrough a true preview of the production stack — it doubles
as the seed of the real application shell.

Every rendered DOM node carries the same `data-spec-*` attributes as the
static-html and astro variants so the `mockup-feedback-*` cluster can
resolve clicks identically across renderers. The `manifest.json` schema is
identical — only `renderer: "mockup-walkthrough-framework"` and the added
`target_framework` field differ.

**Two-mode behaviour — decision recorded.** The agent detects whether a
framework project already exists by checking for
`_concept/mockup-walkthrough/framework/package.json`:

- **Init** (absent): resolve framework → scaffold a minimal app in the
  resolved framework using the template's conventions → generate
  `specs.json` + token styles → install → build → write `manifest.json`
- **Update** (present): regenerate `specs.json` + token styles only →
  rebuild → rewrite `manifest.json`

On update runs the agent NEVER touches the framework's config files
(`next.config.*`, `nuxt.config.*`, `svelte.config.*`, `package.json`) or
the user-owned page/route templates — those belong to the user.

**Generation approach — decision recorded.** Agent-direct: the agent reads
screen specs and derives `specs.json` inline (no persistent generator
script). Same pattern as static-html's Python renderer and astro's inline
derivation.

## Renderer Contract

**Public contract.** Every `data-spec-*` attribute MUST be emitted on the
same DOM position as `mockup-walkthrough-static-html` so the
`mockup-feedback-*` cluster resolves clicks identically across renderers —
**regardless of the underlying framework.** If the resolved framework uses
client components / islands / hydration, the built (SSR/SSG) HTML MUST
still carry the `data-spec-*` attributes server-side, so a static fetch of
the built page resolves every attribute without running JavaScript.

### `data-spec-*` attribute table

| DOM location | Attribute | Value | Source |
|---|---|---|---|
| `<body>` of every `screen/<group>/<name>` built page | `data-spec-screen` | screen path stem (e.g. `01_user_auth/login`) | screen file path |
| every annotatable child node (form fields, buttons, links, images, regions, list items, nav items) | `data-spec-element` | element id (kebab-case) | `elements:` entry, or auto-slug |
| same node, when no explicit `elements:` entry exists for it | `data-spec-provisional` | literal string `"true"` | absent in YAML |
| `<body>` of every `journey/<id>` built page | `data-spec-journey` | journey id from stories.json | stories.json |
| each step link inside `journey/<id>` | `data-spec-screen` | the screen-stem of that step's screen | journey step entry |
| `<body>` of the index page | `data-spec-index` | literal string `"true"` | (none — site root marker) |

**The renderer MUST NOT add `data-spec-*` attributes outside this table.**

### `screen_id` vs `screen_path`

Identical semantics to `mockup-walkthrough-static-html`. See that skill's
"screen_id vs screen_path" section for the full definition. In brief:
`screen_id` is the path stem used in `data-spec-screen` and the route slug;
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
fallback" section. The framework templates emit
`data-spec-provisional="true"` on any element where
`element.provisional === true`. There is NO separate top-level
`auto_slugged[]` array — `provisional: true` lives on the element object
itself. The `kind: "auto_slugged"` warning entry in `manifest.warnings[]`
is still required per the auto-slug step.

## Inputs

Same four input shapes as `mockup-walkthrough-static-html`, plus the
techstack gate:

| Path | Shape |
|---|---|
| `experience/screens/<group>/<screen>.md` | Markdown + YAML frontmatter with optional `elements:` block per `contracts/elements_block.md` |
| `experience/journeys/stories.json` | JSON `{ "journeys": [{ "id", "title", "description", "screen_sequence" }] }` |
| `design/tokens.json` | Token tree. Flattened to CSS custom properties (`--token-<dotted-path-with-hyphens>`). |
| `product-spec/features/<group>/<feature>.md` | Used only for `manifest.json#features`; not rendered as HTML. |
| `_concept/blueprint/techstack.md` | Frontmatter `tech_stack_skill` resolves the framework; the template's `TEMPLATE.md` supplies scaffold/build conventions. |

## Outputs

Generated under `_concept/mockup-walkthrough/framework/`:

| Path | Description |
|---|---|
| `<built index page>` | Router/menu — `<body data-spec-index="true">`. Lists every screen and journey. |
| `screen/<group>/<name>` (built) | One built page per screen. `<body data-spec-screen="<screen_id>">`. |
| `journey/<id>` (built) | One built page per journey. `<body data-spec-journey="<id>">`. Walks through screens in order. |
| `manifest.json` | Machine-readable index for `mockup-feedback-annotate`. |
| `package.json` + `dev`/`build`/`preview` scripts | So any developer can run the walkthrough — the skill itself does not auto-serve. |

> The exact built-output layout (e.g. `out/`, `.output/public/`, `build/`)
> depends on the resolved framework's static build target. The validator is
> pointed at the project root and discovers the built HTML; the
> `rendered_html` paths in `manifest.json` are recorded relative to that
> project root.

## Framework project layout (framework-agnostic)

The project lays out one root layout/shell, one index page, one
screen-collection route, and one journey-collection route, plus an
agent-managed data file and stylesheet. Concrete file names follow the
resolved template's routing convention.

```
_concept/mockup-walkthrough/framework/      ← project root (committed)
├── <data>/specs.json                       ← regenerated each run (agent-managed)
├── <styles>/global.css                     ← token vars (regenerated each run, agent-managed)
├── <root layout / shell>                   ← token-driven wrapper (scaffolded once)
├── <index page>                            ← site root, data-spec-index="true"
├── <screen collection route>               ← one route → all screens (catch-all slug)
├── <journey collection route>              ← one route → all journeys (id param)
├── <framework config>                      ← next.config.* | nuxt.config.* | svelte.config.* (scaffolded once)
├── package.json                            ← dev/build/preview scripts (scaffolded once)
└── manifest.json                           ← written after build, not by the framework
```

### Next.js (App Router) example

```
_concept/mockup-walkthrough/framework/
├── src/app/layout.tsx                       ← root layout (token CSS import, body data-spec passthrough)
├── src/app/page.tsx                         ← index, <body data-spec-index="true">
├── src/app/screen/[...slug]/page.tsx        ← generateStaticParams → all screens
├── src/app/journey/[id]/page.tsx            ← generateStaticParams → all journeys
├── src/data/specs.json                      ← regenerated each run
├── src/app/globals.css                      ← :root token vars (regenerated each run)
├── next.config.ts                           ← output: 'export' (static), scaffolded once
└── package.json
```

`src/app/page.tsx` sets `data-spec-index="true"` on the document body; the
screen route's `generateStaticParams()` returns one entry per
`specs.screens[]` with `slug = screen_id.split('/')`; the journey route's
`generateStaticParams()` returns one entry per `specs.journeys[]` keyed by
`journey_id`. Each page's root element (or the layout's `<body>`) carries
the `data-spec-*` marker, and `next.config.ts` sets `output: 'export'` so
the build emits static HTML carrying the attributes server-side.

### Nuxt / SvelteKit equivalents

Follow the resolved template's routing convention:

- **Nuxt** — `pages/index.vue`, `pages/screen/[...slug].vue`,
  `pages/journey/[id].vue`; `nuxt.config.ts` with `nitro.prerender` /
  `ssr: true` so routes are prerendered to static HTML. `definePageMeta`
  or a wrapping `<body>` attribute carries the `data-spec-*` markers.
- **SvelteKit** — `src/routes/+page.svelte`,
  `src/routes/screen/[...slug]/+page.svelte`,
  `src/routes/journey/[id]/+page.svelte` with `+page.server.ts`
  `entries()` for prerender; `@sveltejs/adapter-static` so the build emits
  static HTML. `<svelte:body>` / element attributes carry the markers.

In every case the **built HTML must carry `data-spec-*` server-side** — see
the Renderer Contract.

## `specs.json` shape

`specs.json` bridges source artefacts to the framework templates at build
time. Identical shape to astro's `specs.json`.

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

ROLE  Walkthrough stack-native renderer — resolves the project's chosen
      framework from techstack.md and converts screen specs + journey
      definitions + tokens into a built site in that framework whose DOM is
      annotatable end-to-end via the same data-spec-* contract as static-html.

READS
  _concept/blueprint/techstack.md       — frontmatter tech_stack_skill → framework
  impl-architecture/templates/<tech_stack_skill>/TEMPLATE.md — scaffold/build/routing
  experience/screens/**/*.md            — screen specs (frontmatter + body)
  experience/journeys/stories.json      — journey definitions
  design/tokens.json                    — brand tokens
  ? product-spec/features/**/*.md       — feature traceability (soft)
  ? experience/screens/00_layout/shell.md — shared layout reference (soft)
  ? _concept/mockup-walkthrough/framework/package.json — mode detection

WRITES
  _concept/mockup-walkthrough/framework/<data>/specs.json        (every run)
  _concept/mockup-walkthrough/framework/<styles>/global.css      (every run)
  _concept/mockup-walkthrough/framework/<framework config>       (init only)
  _concept/mockup-walkthrough/framework/package.json             (init only)
  _concept/mockup-walkthrough/framework/<root layout>            (init only)
  _concept/mockup-walkthrough/framework/<index page>             (init only)
  _concept/mockup-walkthrough/framework/<screen route>           (init only)
  _concept/mockup-walkthrough/framework/<journey route>          (init only)
  _concept/mockup-walkthrough/framework/<built index page>       (built — every run)
  _concept/mockup-walkthrough/framework/screen/<group>/<name>    (built — every run)
  _concept/mockup-walkthrough/framework/journey/<id>             (built — every run)
  _concept/mockup-walkthrough/framework/manifest.json            (every run)

REFERENCES
  contracts/elements_block.md           — elements: schema + renderer contract
  contracts/frontmatter.md              — screen + feature + stories shapes
  contracts/asset_frontmatter.md        — this SKILL.md's own frontmatter shape
  contracts/skill_grammar.md            — DSL keywords used in this body
  contracts/iron_laws.md                — non-negotiable cross-skill constraints
  contracts/scripts/validator_lib.py    — used by mockup-walkthrough/framework/validator.py
  impl-architecture/templates/DOMAIN.md — the template cluster + naming exception
  impl-architecture/templates-select/SKILL.md — resolves tech_stack_skill to a template-* id
  docs/devlog/mockup-design.md § 4, § 6, § 10     — shared input contract + hybrid ID strategy + deployability
  mockup-walkthrough/static-html/SKILL.md — sibling skill (contract anchor)
  mockup-walkthrough/astro/SKILL.md     — sibling skill (structural anchor)

## STEP 1: Read feedback devlog (preserved intent)

- If `_concept/_feedback/devlog.md` exists, read it.
- Filter entries where `target_paths` overlaps files under
  `_concept/mockup-walkthrough/framework/`.
- For each matching entry: extract `patch_summary` as a preserved-intent constraint.
  Do not undo these during regeneration.
- If no devlog or no matching entries: proceed with no constraints.

## STEP 2: Resolve framework

This is the key differentiator from the astro/static-html renderers. The
framework is not fixed — it is read from the project's stack decision.

- Read `_concept/blueprint/techstack.md` frontmatter. Extract
  `tech_stack_skill`.
- Resolve it against `impl-architecture/templates/<tech_stack_skill>/`:
  - **If `tech_stack_skill` is unset, abstract (e.g. `nextjs`, `nuxt`),
    or `custom`** — it is NOT a real `template-*` directory. HARD-FAIL with:
    > "tech_stack_skill is not resolved to a concrete scaffold template. Run
    > `impl-architecture-templates-select` first to pick a template-* id,
    > then re-run this skill." Append `kind: "unresolved_template"` to
    > `warnings[]` (in the diagnostic, not a manifest — no manifest is
    > written on hard-fail). You MAY note that a static-html fallback exists
    > (the complex-app flow's `mock-static-fallback`) if the user wants a
    > walkthrough without resolving the template.
  - **If the directory does not exist on disk** — same hard-fail; the id is
    stale.
- Read `impl-architecture/templates/<tech_stack_skill>/TEMPLATE.md`. From
  its **Identity** table and **Scaffold Recipe** learn:
  - the framework (Next.js / Nuxt / SvelteKit) → derive `target_framework`
    (`nextjs` | `nuxt` | `sveltekit`)
  - the scaffold command, the package manager, and the dev/build commands
  - the routing convention (App Router catch-all, Nuxt `pages/`, SvelteKit
    `src/routes/`)
- Derive `target_framework` from the Identity table's Frontend value
  (Next.js → `nextjs`, Nuxt → `nuxt`, SvelteKit → `sveltekit`). This value
  is recorded in `manifest.json#target_framework`.

EMIT  [mockup-walkthrough-framework] checkpoint phase=framework_resolved tech_stack_skill=<id> target_framework=<value>

## STEP 3: Read inputs

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
  fall back to the scaffolded root layout default.
- **`product-spec/features/` empty or missing** → soft gate,
  `kind: "missing_feature"`, continue. `manifest.features[]` → `[]`.
- **Zero journeys** → render "No journeys defined",
  `kind: "no_journeys"`.

## STEP 4: Detect mode

Check `_concept/mockup-walkthrough/framework/package.json`.
- Absent → **Init** (proceed to STEP 5 then STEP 6).
- Present → **Update** (skip STEP 5, proceed directly to STEP 6).

## STEP 5: Scaffold project (Init only)

Scaffold a minimal app in the resolved framework using the template's
conventions. Do NOT do this on update runs.

- Run the template's **scaffold command** (from its Scaffold Recipe) into
  the project root `_concept/mockup-walkthrough/framework/`, then prune the
  scaffold down to the four routes this walkthrough needs. Configure the
  framework for a **static export** target so the build emits plain HTML:
  - **Next.js** — `next.config.ts` with `output: 'export'`
  - **Nuxt** — `nuxt.config.ts` with `nitro.prerender` (or
    `nuxi generate`)
  - **SvelteKit** — `@sveltejs/adapter-static` + per-route `prerender = true`
- Author the four route/page files (root layout, index, screen collection,
  journey collection) per the framework's routing convention — see the
  layout examples above. Each must wire `data-spec-*` onto the built body
  and read from `specs.json`.
- Emit `package.json` with `dev`, `build`, and `preview` scripts so any
  developer can run the walkthrough locally (mockup-design.md § 10
  "Walkthrough deployability"). The skill itself never auto-serves; it only
  builds. Example scripts (Next.js):

  ```json
  {
    "name": "mockup-walkthrough-framework",
    "private": true,
    "scripts": {
      "dev": "next dev",
      "build": "next build",
      "preview": "npx serve out"
    }
  }
  ```

  Nuxt: `dev: nuxi dev`, `build: nuxi generate`,
  `preview: npx serve .output/public`. SvelteKit: `dev: vite dev`,
  `build: vite build`, `preview: vite preview`.
- Install dependencies using the template's package manager.

On update runs the agent NEVER regenerates the framework config or the
route/page templates — only `specs.json` and the token stylesheet.

## STEP 6: Generate `specs.json` and token styles (both modes)

Write `specs.json` (under the framework's data dir, e.g.
`src/data/specs.json`) derived from the in-memory model. Schema as shown in
the `specs.json` shape section above. Overwrite unconditionally.

Write the token stylesheet (e.g. `src/app/globals.css` or
`assets/css/global.css` per the template) with one `:root` custom property
per flattened `token_var`:

```css
:root {
  /* one line per flattened token_var */
  --token-<name>: <value>;
}
```

Overwrite unconditionally. This file is agent-managed every run.

On update runs only: compare the count of `--token-*` keys in the freshly
derived in-memory model vs. the CSS var declarations in the existing
stylesheet before overwriting. If counts differ, append
`kind: "stale_token_styles"` to `warnings[]`.

## STEP 7: Build

Run the template's **build command** from
`_concept/mockup-walkthrough/framework/`. Fall back to `bun run build` if
the template does not name a build command:

```bash
bun run build
```

On non-zero exit: print full stderr and exit non-zero. Do not write
`manifest.json`.

After build, the agent MUST verify the built HTML carries `data-spec-*`
server-side: fetch one built `screen/<group>/<name>` page from disk and
confirm `data-spec-screen` is present in the static HTML (not only injected
at runtime). If absent → fail: "built HTML missing data-spec-* server-side —
move the attributes out of client-only code into the SSR/SSG output".

## STEP 8: Write `manifest.json`

Emit the pinned schema. Build it from the in-memory model — NOT by
serialising `specs.json`. Template-only fields from `specs.json`
(`screens[].title`, `screens[].group`, `screens[].journeys[]`,
`journeys[].title`, `journeys[].description`) MUST NOT appear in
`manifest.json`.

```json
{
  "schema_version": "1.0",
  "renderer": "mockup-walkthrough-framework",
  "renderer_version": "0.1.0",
  "target_framework": "nextjs",
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

`target_framework` is the one field added beyond the pinned static-html /
astro schema. It records the framework resolved in STEP 2 (`nextjs` |
`nuxt` | `sveltekit`) so `mockup-feedback-annotate` knows how the built
HTML was produced. `rendered_html` paths are recorded relative to the
project root (the framework's static-export output location).

Sort: `screens[]` by `screen_path`, `journeys[]` by `journey_id`,
`features[]` by `feature_path`. Write atomically (tmp → rename).

`renderer_version` matches the `metadata.version` in this SKILL.md's
frontmatter (`"0.1.0"`).

## STEP 9: Validate

Run from the repo root:

```bash
python mockup-walkthrough/framework/validator.py _concept/mockup-walkthrough/framework
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
| `layout:` reference to non-existent file | `kind: "missing_layout"`, fall back to scaffolded root layout default |
| Auto-slug collision | `kind: "auto_slug_collision"`, suffix auto id with `-2`, `-3`, … |

### Framework-specific

| Condition | Behaviour |
|---|---|
| `tech_stack_skill` abstract / `custom` / unset | HARD-FAIL — tell user to run `impl-architecture-templates-select`; `kind: "unresolved_template"`; note `mock-static-fallback` exists |
| `tech_stack_skill` names a non-existent `template-*` dir | HARD-FAIL — stale id; `kind: "unresolved_template"` |
| Dependency install exits non-zero | Fail loudly with stderr; do not build |
| Build command exits non-zero | Fail loudly with stderr; do not write `manifest.json` |
| Built HTML missing `data-spec-*` server-side | Fail: attributes must be emitted in SSR/SSG output, not client-only |
| Token count differs from CSS var count (update runs only) | `kind: "stale_token_styles"`; user must extend the token stylesheet manually |

### `warnings[].kind` enum

`auto_slugged`, `auto_slug_collision`, `missing_layout`, `missing_feature`,
`unknown_element_kind`, `missing_screen`, `missing_screen_sequence`,
`no_journeys`, `stale_token_styles`, `unresolved_template`

`unresolved_template` and `stale_token_styles` are the framework-specific
additions. `unresolved_template` is emitted in the hard-fail diagnostic
(STEP 2) — no `manifest.json` is written when the framework cannot be
resolved.

## MUST / NEVER

MUST  resolve target_framework from techstack.md `tech_stack_skill` before scaffolding
MUST  hard-fail when `tech_stack_skill` is abstract/custom/unset or has no template-* dir
MUST  emit data-spec-screen on every screen `<body>`
MUST  emit data-spec-element on every annotatable child node
MUST  emit data-spec-provisional="true" on auto-slugged element nodes
MUST  emit data-spec-journey="<id>" on every journey `<body>`
MUST  emit data-spec-index="true" on the index page `<body>`
MUST  emit every data-spec-* attribute in the built (SSR/SSG) HTML server-side, not client-only
MUST  configure the framework for a static-export build target
MUST  emit package.json with dev/build/preview scripts (deployability)
MUST  write manifest.json conforming to pinned schema (schema_version: "1.0") with target_framework
MUST  sort manifest arrays lexicographically
MUST  write specs.json and token styles before running the build
MUST  regenerate the token stylesheet on every run (agent-managed)

NEVER regenerate the framework config or route/page templates on update runs
NEVER emit data-spec-* attributes outside the pinned table
NEVER invent a target_framework not derived from a real template-* TEMPLATE.md
NEVER mutate source files (experience/screens/**, stories.json, tokens.json, features/**, techstack.md)
NEVER inject journey-step navigation into screen routes
NEVER inline absolute filesystem paths in manifest.json
NEVER use a separate auto_slugged[] array — set provisional: true on the element object (the kind: "auto_slugged" warning entry in manifest.warnings[] is still required per the auto-slug step)

## CHECKLIST

- [ ] `tech_stack_skill` resolved to an existing `template-*` directory before scaffolding
- [ ] `manifest.target_framework` matches the resolved template's framework
- [ ] Built index page exists under `_concept/mockup-walkthrough/framework/`
- [ ] `_concept/mockup-walkthrough/framework/manifest.json` exists and parses as JSON
- [ ] `manifest.schema_version == "1.0"` and `manifest.renderer == "mockup-walkthrough-framework"`
- [ ] One built `screen/<group>/<name>` page per screen file under `experience/screens/`
- [ ] One built `journey/<id>` page per journey in `stories.json`
- [ ] Every screen page `<body>` has `data-spec-screen` in the built HTML (server-side)
- [ ] Every annotatable node in screen pages has `data-spec-element`
- [ ] Every auto-slugged element node also has `data-spec-provisional="true"`
- [ ] Every journey page `<body>` has `data-spec-journey`
- [ ] Index page `<body>` has `data-spec-index="true"`
- [ ] `package.json` declares `dev`, `build`, and `preview` scripts
- [ ] Validator (`mockup-walkthrough/framework/validator.py`) exits 0

EMIT  [mockup-walkthrough-framework] started run_id=<uuid>
EMIT  [mockup-walkthrough-framework] checkpoint phase=framework_resolved tech_stack_skill=<id> target_framework=<value>
EMIT  [mockup-walkthrough-framework] checkpoint screens=<N> journeys=<M>
EMIT  [mockup-walkthrough-framework] completed run_id=<uuid> target_framework=<value> screens=<N> journeys=<M> warnings=<W>

