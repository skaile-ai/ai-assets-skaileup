---
name: walkthrough-mockup-static-html
description: "Use when stakeholders need a clickable static HTML walkthrough of the application — zero build, no JS framework, openable directly in a browser. Generates one HTML file per screen and per journey, plus a manifest.json that the mockup-feedback cluster reads to resolve clicks back to source artefacts. Best for simple-app tier."
metadata:
  version: "0.1.0"
  tags:
    - walkthrough
    - mockup
    - static-html
    - zero-build
    - simple-app
    - frontend
    - prototype
    - data-spec
  stage: alpha
  prerequisites:
    files:
      - path: "experience/screens"
        gate: hard
        description: "Screen specs are the primary input — one file rendered per screen"
        min_entries: 1
      - path: "experience/journeys/stories.json"
        gate: hard
        description: "Journey definitions drive the journey/<id>.html sequencing"
      - path: "design/tokens.json"
        gate: hard
        description: "Brand tokens injected as CSS variables in the rendered shell"
      - path: "product-spec/features"
        gate: soft
        description: "Feature files are linked from manifest.json for traceability; absence is recorded as a warning, not a failure"
        min_entries: 1
    reads:
      - path: "experience/screens/00_layout/shell.md"
        description: "Optional shared layout reference; if present, used as the wrapping shell for every screen"
    produces:
      - path: "_concept/walkthrough-mockup/static-html"
        description: "Generated static site: index.html, screen/<group>/<name>.html, journey/<id>.html, manifest.json"
---

# Walkthrough Mockup — Static HTML

## Overview

The contract anchor among walkthrough renderers. Consumes screen specs
(plus their `elements:` frontmatter blocks per `contracts/elements_block.md`),
journey definitions, brand tokens, and feature files; produces a zero-build,
openable static HTML walkthrough at `_concept/walkthrough-mockup/static-html/`.

Every rendered DOM node carries `data-spec-screen` + `data-spec-element`
attributes (and `data-spec-provisional="true"` when the id was auto-slugged)
so the Phase 3 `mockup-feedback-*` cluster can resolve clicks back to source
artefacts. Output also includes a `manifest.json` index that
`mockup-feedback-annotate` reads.

**Rendering technology — decision recorded.** Stdlib-only Python string
templating using `html.escape`, `pathlib`, `json`, and `PyYAML` for
frontmatter. **No** Jinja, **no** Mako, **no** build tool, **no** JS
framework in the produced site. Rationale:

1. The produced site is zero-build by acceptance criterion. The renderer
   that *generates* the site runs at skill-execution time and never ships
   in the output, so its dependencies do not bleed through.
2. Every other validator/generator script in this repo uses stdlib + PyYAML
   (see `contracts/scripts/validator_lib.py`, `experience/screens/`).
   Consistency wins.
3. The templates are small (one shell, one screen, one journey, one index).
   `str.format`-style substitution is cheaper than a templating-engine
   dependency.

The next walkthrough variant author (Lit, Astro, framework-tier) should keep
this rationale in mind.

## Renderer Contract

This is the **public contract** of this skill. Every other walkthrough
variant in Phase 3 (Lit, Astro, framework-tier) MUST emit the same set of
`data-spec-*` attributes on the same DOM positions so the
`mockup-feedback-*` cluster can resolve clicks identically across renderers.

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
Phase 3's annotate skill ignores unknown ones, but a lean attribute set
keeps drift visible.

### `screen_id` vs `screen_path`

Both forms are kept in `manifest.json` so Phase 3 consumers can pick:

- `screen_path`: full repo-relative path with extension, e.g.
  `experience/screens/01_user_auth/login.md`. Used in journey
  `screen_sequence`, in `screens[].screen_path`, and in `source_anchor`s.
- `screen_id`: path stem under `experience/screens/` without `.md`, e.g.
  `01_user_auth/login`. Used in `data-spec-screen`, in the rendered HTML
  filename, and in `screens[].screen_id`.

### kind → DOM tag mapping

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
| `custom` | `<div>` | label as inner text; renderable but unstyled |

States beyond `default` are rendered as adjacent `<span class="state-<n>">`
children of the element so visual reviewers can see state coverage.

### Auto-slug fallback (this skill's portion of the hybrid ID strategy)

When a screen file has no `elements:` block, OR has a partial one, this
skill MUST:

  1. Walk the screen body and identify renderable widgets by source order.
     **Source set:** (a) markdown headings (`##`, `###`), (b) form-field
     lines matching `[label]: input|button|...` pattern, (c) acceptance-
     criteria mentions in body text. (Auto-slug net is intentionally wide;
     explicit ids always win on collision.)
  2. For each widget not present in `elements:` (matched by label-equality,
     case-insensitive), generate an id by:
     - Lowercase the label
     - Replace any non `[a-z0-9]` run with a single `-`
     - Trim leading/trailing `-`
     - If empty (label was e.g. `"…"`), fall back to `<kind>-<n>` where
       `n` is a 1-based counter scoped per-screen-per-kind
       (`button-1`, `button-2`, `input-1`, ...).
     - On collision with another auto-slugged id within the same screen,
       append `-2`, `-3`, ... until unique.
     - Collision with an explicit id: warning `kind: "auto_slug_collision"`
       and the auto-slugged element gets the suffixed id.
  3. Render the node with `data-spec-element="<auto-slugged-id>"` AND
     `data-spec-provisional="true"`.
  4. Append a `warnings[]` entry of `kind: "auto_slugged"` to
     `manifest.json` for each auto-slugged element.
  5. **Never** mutate the source `experience/screens/<group>/<name>.md`
     file. Promotion of provisional ids is `mockup-feedback-triage`'s job
     in Phase 3.

This procedure mirrors step 1 of the hybrid ID strategy from
`REFACTOR_MOCKUP.md` § 6 / `contracts/elements_block.md` § "Hybrid ID
strategy".

## Inputs

This skill consumes four input shapes, all under the project root:

| Path | Shape | Reference |
|---|---|---|
| `experience/screens/<group>/<screen>.md` | Markdown + YAML frontmatter (per `contracts/frontmatter.md` § "experience/screens/<group>/<screen>.md") with optional `elements:` block (per `contracts/elements_block.md`). | `contracts/elements_block.md` |
| `experience/journeys/stories.json` | JSON object containing a `journeys[]` array. Each journey has `id`, `title`, `description`, `screen_sequence: [<screen-path>, ...]`. | (pinned by this skill — see "Stories.json schema" below) |
| `design/tokens.json` | Token tree (e.g. `{"color": {"primary": "#0ea5e9"}, "spacing": {"sm": "8px"}}`). Flattened to CSS custom properties (`--token-<dotted-path-with-hyphens>`). | (pinned by this skill — same flattening rule as `component-mockup-isolated-html`) |
| `product-spec/features/<group>/<feature>.md` | Markdown + YAML frontmatter (per `contracts/frontmatter.md` § "experience/features/..."). Used **only** for `manifest.json#features`; not rendered as HTML. | `contracts/frontmatter.md` |

**Body markdown rule.** The screen markdown body is rendered as descriptive
text/headings inside the screen page, but DOES NOT receive `data-spec-element`
attributes. Only the explicit `elements:` block (or auto-slug fallback)
produces annotatable nodes.

**Stories.json schema (pinned by this skill).**

```json
{
  "version": "1.0",
  "last_updated": "YYYY-MM-DD",
  "journeys": [
    {
      "id": "user-signs-in",
      "title": "User signs in",
      "description": "First-time user authenticates and lands on the home screen.",
      "screen_sequence": [
        "experience/screens/01_user_auth/login.md",
        "experience/screens/02_dashboard/home.md"
      ]
    }
  ]
}
```

If `screen_sequence` is absent for a journey, this skill records a warning
of `kind: "missing_screen_sequence"` and skips that journey's render.

## Outputs

Generated under `_concept/walkthrough-mockup/static-html/`:

| Path | Description |
|---|---|
| `index.html` | Router/menu — `<body data-spec-index="true">`. Lists every screen (grouped) and every journey. |
| `screen/<group>/<name>.html` | One file per screen. `<body data-spec-screen="<screen_id>">`. |
| `journey/<id>.html` | One file per journey. `<body data-spec-journey="<id>">`. Walks through screens in order. |
| `manifest.json` | Machine-readable index keyed for `mockup-feedback-annotate`. See `## Manifest Schema` below. |

## ROLE / READS / WRITES / REFERENCES

ROLE  Walkthrough Static-HTML renderer — converts screen specs + journey
      definitions + tokens into a clickable zero-build static site whose
      DOM is annotatable end-to-end.

READS
  experience/screens/**/*.md            — screen specs (frontmatter + body)
  experience/journeys/stories.json      — journey definitions
  design/tokens.json                    — brand tokens
  ? product-spec/features/**/*.md       — feature traceability (soft)
  ? experience/screens/00_layout/shell.md — shared layout (soft)

WRITES
  _concept/walkthrough-mockup/static-html/index.html
  _concept/walkthrough-mockup/static-html/screen/<group>/<name>.html
  _concept/walkthrough-mockup/static-html/journey/<id>.html
  _concept/walkthrough-mockup/static-html/manifest.json

REFERENCES
  contracts/elements_block.md           — `elements:` schema + renderer contract
  contracts/frontmatter.md              — screen + feature + stories shapes
  contracts/asset_frontmatter.md        — this SKILL.md's own frontmatter shape
  contracts/skill_grammar.md            — DSL keywords used in this body
  contracts/iron_laws.md                — non-negotiable cross-skill constraints
  contracts/scripts/validator_lib.py    — used by walkthrough-mockup/static-html/validator.py
  REFACTOR_MOCKUP.md § 4, § 6           — shared input contract + hybrid ID strategy
  walkthrough-mockup/text/SKILL.md      — sibling skill (text variant) for tone reference

## STEP 1: Read inputs

  - Glob `experience/screens/**/*.md` (excluding `00_layout/`); sort lexicographically by path.
  - For each screen: parse YAML frontmatter (PyYAML); extract `implements[]`,
    `data_entities[]`, `layout`, `elements[]` (default to `[]`). Capture the
    screen body markdown for descriptive rendering.
  - Validate `elements[]` against `contracts/elements_block.md`. If
    `lab/validate-elements-block/` is available, delegate; otherwise emit
    `warnings[]` entries of `kind: "unknown_element_kind"` for any kind
    outside the v0.1 enum (`input, button, link, image, text, region, list,
    form, nav, media, custom`) but render the node anyway.
  - Read `experience/journeys/stories.json`. Validate each `journeys[]`
    entry has `id` AND `screen_sequence`. Missing `screen_sequence` →
    warning `kind: "missing_screen_sequence"`, skip that journey render.
  - Read `design/tokens.json`. Flatten the nested tree depth-first into a
    flat dict keyed `--token-<dotted-path-with-hyphens>`. Example:
    `{"color": {"primary": "#0ea5e9"}}` → `--token-color-primary: #0ea5e9`.
    (Same rule as `component-mockup-isolated-html/scripts/inline_tokens.py`.)
  - Glob `product-spec/features/**/*.md`; sort lexicographically. Build a
    `feature -> screens[]` map by inverting `screens[].implements[]`.
  - Build a normalised in-memory model:
    `{ screens: [...], journeys: [...], tokens: {...}, features: [...], warnings: [...] }`.

### Edge cases

  - **Malformed YAML in a screen file** → fail loudly, exit non-zero. No
    partial render. The error message names the offending file.
  - **Screen referenced from a journey but absent on disk** → record
    `manifest.warnings[]` with `kind: "missing_screen"` AND skip that
    journey step (the link in `journey/<id>.html` becomes a dead-end
    placeholder, NOT a 404).
  - **`elements:` entry with a `kind` outside the v0.1 enum** → render
    with `data-spec-element` set, kind treated as `custom`, record
    warning `kind: "unknown_element_kind"`.
  - **`layout:` reference pointing to a non-existent file** → warning
    `kind: "missing_layout"`, fall back to a built-in default shell.
  - **`product-spec/features/` empty or missing** → soft gate, warning
    `kind: "missing_feature"`, continue rendering. `manifest.features[]`
    is emitted as `[]`.

## STEP 2: Render screens

  For each parsed screen (in lexicographic order):

  - Determine output path:
    `_concept/walkthrough-mockup/static-html/screen/<group>/<name>.html`
  - Compute `screen_id` = path stem under `experience/screens/`
    (e.g. `01_user_auth/login`).
  - Open the wrapping shell (default or layout-driven). If the screen
    frontmatter declares `layout: experience/screens/00_layout/shell.md`
    AND that file exists, render the layout's body markdown as a wrapper
    around the screen content; if the layout file is missing, emit a
    warning `kind: "missing_layout"` and use the built-in default shell.
  - Inject the flattened `tokens.json` keys as CSS custom properties
    on `:root` inside the shell's `<style>` block.
  - Set `<body data-spec-screen="<screen_id>">`.
  - Render the explicit `elements[]` first (in declaration order):
    - Choose the HTML tag per the `kind → DOM tag mapping` table.
    - Emit `data-spec-element="<element.id>"`.
    - If the element entry has `provisional: true`, also emit
      `data-spec-provisional="true"`.
    - Render the label as visible text (escaped via
      `html.escape(..., quote=True)`).
    - For each state in `element.states` beyond `default`, render a small
      sibling `<span class="state-<state>">` so visual reviewers can see
      state coverage.
  - For widgets discoverable in the screen body but absent from
    `elements[]`, apply the auto-slug fallback and emit them at the
    bottom of `<main>` inside an HTML comment-delimited
    `<!-- auto-slugged --> ... <!-- /auto-slugged -->` group so the
    source ordering vs auto-slugged ordering is visually distinct.
  - Render the screen body markdown (descriptive text/headings only)
    inside a `<section class="screen-body-prose">`. Body content does
    NOT receive `data-spec-element` attributes — only the `elements:`
    block (or auto-slug fallback) does.
  - Add a footer linking back to `index.html` and, when the screen
    appears in any journey, list those journeys with links to
    `journey/<id>.html`. (See STEP 3 for the cross-journey rule.)
  - Write the file UTF-8, LF.

  MUST escape every label, id, screen_path, journey_id with
  `html.escape(..., quote=True)` before substitution into HTML.
  NEVER trust frontmatter strings; they may contain quotes, angle
  brackets, or unicode that breaks the document.

## STEP 3: Render journeys

## STEP 4: Emit index.html and manifest.json

## STEP 5: Validate

## MUST / NEVER

## CHECKLIST
