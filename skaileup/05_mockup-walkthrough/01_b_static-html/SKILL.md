---
name: mockup-walkthrough-static-html
description: "Use when stakeholders need a clickable static HTML walkthrough of the application — zero build, no JS framework, openable directly in a browser. Generates one HTML file per screen and per journey, plus a manifest.json that the mockup-feedback cluster reads to resolve clicks back to source artefacts. Best for appbuilder-simple tier."
metadata:
  version: "0.1.0"
  tags:
    - walkthrough
    - mockup
    - static-html
    - zero-build
    - appbuilder-simple
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
        description: "Screen specs are the primary input — one file rendered per screen"
        min_entries: 1
      - path: "experience/journeys/stories.yaml"
        gate: hard
        description: "Journey definitions drive the journey/<id>.html sequencing"
      - path: "design/tokens.json"
        gate: hard
        description: "Brand tokens injected as CSS variables in the rendered shell"
      - path: "experience/features"
        gate: soft
        description: "Feature files are linked from manifest.json for traceability; absence is recorded as a warning, not a failure"
        min_entries: 1
    reads:
      - path: "experience/screens/00_layout/shell.md"
        description: "Optional shared layout reference; if present, used as the wrapping shell for every screen"
    produces:
      - path: "_concept/mockup-walkthrough/static-html"
        description: "Generated static site: index.html, screen/<group>/<name>.html, journey/<id>.html, manifest.json"
---

# Walkthrough Mockup — Static HTML

## Overview

Contract anchor among walkthrough renderers. Consumes screen specs (plus
`elements:` frontmatter blocks per `contracts/elements_block.md`), journey
definitions, brand tokens, feature files — produces zero-build, openable
static HTML walkthrough at `_concept/mockup-walkthrough/static-html/`.

Every rendered DOM node carries `data-spec-screen` + `data-spec-element`
attributes (and `data-spec-provisional="true"` when id was auto-slugged) so
Phase 3 `mockup-feedback-*` cluster resolves clicks back to source artefacts.
Output also includes `manifest.json` index that `mockup-feedback-annotate` reads.

**Rendering technology — decision recorded.** Stdlib-only Python string
templating using `html.escape`, `pathlib`, `json`, `PyYAML` for frontmatter.
**No** Jinja, **no** Mako, **no** build tool, **no** JS framework in produced
site. Rationale:

1. Produced site is zero-build by acceptance criterion — the renderer that
   *generates* it runs at skill-execution time, never ships in output, so
   its dependencies don't bleed through.
2. Every other validator/generator script in this repo uses stdlib + PyYAML
   (see `contracts/scripts/validator_lib.py`, `experience/screens/`) — consistency wins.
3. Templates are small (one shell, one screen, one journey, one index).
   `str.format`-style substitution cheaper than templating-engine dependency.

Next walkthrough variant author (Lit, Astro, framework-tier) should keep this
rationale in mind.

## Renderer Contract

Implements shared walkthrough renderer contract — `contracts/walkthrough_renderer.md`
(schema_version "1.0"): data-spec-* attribute table, screen_id vs screen_path,
kind → DOM tag mapping, auto-slug fallback, manifest schema + field semantics,
warnings[].kind enum, shared error handling, screen-in-multiple-journeys rule,
shared MUST/NEVER. Read before rendering; pinned, MUST NOT be restated here.

Renderer-specific manifest values: `renderer: "mockup-walkthrough-static-html"`,
`renderer_version:` this SKILL.md's `metadata.version`.

static-html is contract's reference implementation: when behaviour is
ambiguous, this renderer's output is tie-breaker.

## Inputs

Skill consumes four input shapes, all under project root:

| Path | Shape | Reference |
|---|---|---|
| `experience/screens/<group>/<screen>.md` | Markdown + YAML frontmatter (per `contracts/frontmatter.md` § "experience/screens/<group>/<screen>.md") with optional `elements:` block (per `contracts/elements_block.md`). | `contracts/elements_block.md` |
| `experience/journeys/stories.yaml` | JSON object containing a `journeys[]` array. Each journey has `id`, `title`, `description`, `screen_sequence: [<screen-path>, ...]`. | (pinned by this skill — see "Stories.json schema" below) |
| `design/tokens.json` | Token tree (e.g. `{"color": {"primary": "#0ea5e9"}, "spacing": {"sm": "8px"}}`). Flattened to CSS custom properties (`--token-<dotted-path-with-hyphens>`). | (pinned by this skill — same flattening rule as `mockup-component-isolated-html`) |
| `experience/features/<group>/<feature>.md` | Markdown + YAML frontmatter (per `contracts/frontmatter.md` § "experience/features/..."). Used **only** for `manifest.json#features`; not rendered as HTML. | `contracts/frontmatter.md` |

**Body markdown rule.** Screen markdown body renders as descriptive
text/headings inside screen page, but DOES NOT receive `data-spec-element`
attributes. Only explicit `elements:` block (or auto-slug fallback) produces
annotatable nodes.

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

Generated under `_concept/mockup-walkthrough/static-html/`:

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
  experience/journeys/stories.yaml      — journey definitions
  design/tokens.json                    — brand tokens
  ? experience/features/**/*.md       — feature traceability (soft)
  ? experience/screens/00_layout/shell.md — shared layout (soft)

WRITES
  _concept/mockup-walkthrough/static-html/index.html
  _concept/mockup-walkthrough/static-html/screen/<group>/<name>.html
  _concept/mockup-walkthrough/static-html/journey/<id>.html
  _concept/mockup-walkthrough/static-html/manifest.json

REFERENCES
  contracts/walkthrough_renderer.md     — shared renderer contract (pinned)
  contracts/elements_block.md           — `elements:` schema + renderer contract
  contracts/frontmatter.md              — screen + feature + stories shapes
  contracts/asset_frontmatter.md        — this SKILL.md's own frontmatter shape
  contracts/skill_grammar.md            — DSL keywords used in this body
  contracts/iron_laws.md                — non-negotiable cross-skill constraints
  contracts/scripts/validator_lib.py    — used by mockup-walkthrough/static-html/validator.py
  docs/devlog/mockup-design.md § 4, § 6           — shared input contract + hybrid ID strategy
  mockup-walkthrough/text/SKILL.md      — sibling skill (text variant) for tone reference

## STEP 1: Read feedback devlog (preserved intent)

  - If `_concept/_feedback/devlog.md` exists, read it.
  - Filter entries where `target_paths` overlaps files under
    `_concept/mockup-walkthrough/static-html/`.
  - For each matching entry: extract `patch_summary` as a preserved-intent constraint.
    Do not undo these during regeneration.
  - If no devlog or no matching entries: proceed with no constraints.

## STEP 2: Read inputs

  - Glob `experience/screens/**/*.md` (excluding `00_layout/`); sort lexicographically by path.
  - For each screen: parse YAML frontmatter (PyYAML); extract `implements[]`,
    `data_entities[]`, `layout`, `elements[]` (default `[]`). Capture screen
    body markdown for descriptive rendering.
  - Validate `elements[]` against `contracts/elements_block.md`. If
    `lab/validate-elements-block/` available, delegate; otherwise emit
    `warnings[]` entries of `kind: "unknown_element_kind"` for any kind
    outside v0.1 enum (`input, button, link, image, text, region, list,
    form, nav, media, custom`) but render node anyway.
  - Read `experience/journeys/stories.yaml`. Validate each `journeys[]` entry
    has `id` AND `screen_sequence`. Missing `screen_sequence` → warning
    `kind: "missing_screen_sequence"`, skip that journey render.
  - Read `design/tokens.json`. Flatten nested tree depth-first into flat dict
    keyed `--token-<dotted-path-with-hyphens>`. Example:
    `{"color": {"primary": "#0ea5e9"}}` → `--token-color-primary: #0ea5e9`
    (same rule as `mockup-component-isolated-html/scripts/inline_tokens.py`).
  - Glob `experience/features/**/*.md`; sort lexicographically. Build
    `feature -> screens[]` map by inverting `screens[].implements[]`.
  - Build normalised in-memory model:
    `{ screens: [...], journeys: [...], tokens: {...}, features: [...], warnings: [...] }`.

### Edge cases

  - **Malformed YAML in a screen file** → fail loudly, exit non-zero. No
    partial render; error message names offending file.
  - **Screen referenced from a journey but absent on disk** → record
    `manifest.warnings[]` with `kind: "missing_screen"` AND skip that journey
    step (link in `journey/<id>.html` becomes dead-end placeholder, NOT a 404).
  - **`elements:` entry with a `kind` outside v0.1 enum** → render with
    `data-spec-element` set, kind treated as `custom`, record warning
    `kind: "unknown_element_kind"`.
  - **`layout:` reference pointing to non-existent file** → warning
    `kind: "missing_layout"`, fall back to built-in default shell.
  - **`experience/features/` empty or missing** → soft gate, warning
    `kind: "missing_feature"`, continue rendering; `manifest.features[]`
    emitted as `[]`.

## STEP 3: Render screens

  For each parsed screen (in lexicographic order):

  - Determine output path:
    `_concept/mockup-walkthrough/static-html/screen/<group>/<name>.html`
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
    - Choose the HTML tag per `contracts/walkthrough_renderer.md` § kind → DOM tag mapping.
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

## STEP 4: Render journeys

  For each journey in `stories.yaml`'s `journeys[]` array:

  - Determine output path:
    `_concept/mockup-walkthrough/static-html/journey/<journey_id>.html`
  - Set `<body data-spec-journey="<journey_id>">`.
  - Render `<h1>` with the escaped `journey.title` and a `<p>` with the
    escaped `journey.description` (when present).
  - Render an `<ol>` of steps. For each entry in `screen_sequence`:
    - Resolve the screen file. If absent on disk, emit a `<li>` with
      class `journey-step-missing` and a `data-spec-screen` attribute
      still present (so feedback-annotate can capture intent), AND
      append a `manifest.warnings[]` entry of `kind: "missing_screen"`.
    - Otherwise render `<li>` containing:
      - A heading `Step <n>: <screen_label>` (label = screen filename
        stem with underscores → spaces, escaped).
      - An `<a href="../screen/<group>/<name>.html"
        data-spec-screen="<screen_id>">Open screen</a>` link.
      - A `Next →` link to the next step's screen (or to `index.html`
        on the last step).
  - The acceptance criterion "clicking a journey link walks through
    screens in order" is honoured by the journey HTML alone — STEP 2
    only lists journeys this screen participates in (no
    journey-specific "Next" injection inside the screen HTML, so the
    same screen can appear in multiple journeys cleanly).
  - Write the file UTF-8, LF.

  Screen-in-multiple-journeys rule: see `contracts/walkthrough_renderer.md` § Screen-in-multiple-journeys rule.

## STEP 5: Emit index.html and manifest.json

### STEP 4a: Emit `index.html`

  - Set `<body data-spec-index="true">`.
  - Render two top-level sections:
    - `<section id="screens">` — flat list grouped by `<group>`, each
      entry an `<a href="screen/<group>/<name>.html">` linking to the
      screen page.
    - `<section id="journeys">` — flat list, each entry an
      `<a href="journey/<id>.html">` linking to the journey page.
      If `stories.yaml` has zero journeys, render the literal text
      `"No journeys defined"` and add a `warnings[]` entry of
      `kind: "missing_screen_sequence"` (when caused by absent
      `screen_sequence`) or `kind: "no_journeys"` (when absent file).
  - Embed a `<footer>Generated <generated_at></footer>` line.
  - Write the file UTF-8, LF.

### STEP 4b: Emit `manifest.json`

  - Build the object using the pinned schema (see `## Manifest Schema`
    below — pasted inline so future readers don't have to chase the
    plan document).
  - `schema_version = "1.0"`.
  - `renderer = "mockup-walkthrough-static-html"`,
    `renderer_version = "0.1.0"` (this skill's `metadata.version`).
  - `generated_at = ` current UTC ISO-8601 (e.g.
    `2026-05-08T12:34:56Z`). For deterministic snapshot tests, the
    validator replaces this value with `"<pinned>"` before comparison
    (see STEP 5).
  - Sort `screens[]` by `screen_path`, `journeys[]` by `journey_id`,
    and `features[]` by `feature_path` for deterministic diffs.
  - Write atomically: write to `manifest.json.tmp`, fsync, rename to
    `manifest.json`.

## Manifest Schema

Pinned in `contracts/walkthrough_renderer.md` § Manifest schema (+ § Field
semantics, § warnings[].kind enum). This renderer emits
`renderer: "mockup-walkthrough-static-html"`.

## STEP 6: Validate

  - Run `mockup-walkthrough/static-html/validator.py
    _concept/mockup-walkthrough/static-html` from the repo root.
  - The validator confirms (a) every `data-spec-*` attribute resolves
    to an existing source file or rendered HTML target; (b)
    `manifest.json` matches the pinned schema; (c) every screen-link
    inside `journey/<id>.html` resolves; (d) no JS framework was
    emitted (zero-build invariant).
  - Exit 0 = ready for Phase 3 to consume. Exit 2 = violation report
    with `<file>:<line>: <message>` lines.

## MUST / NEVER

Shared MUST/NEVER: `contracts/walkthrough_renderer.md` § Shared MUST / NEVER
(data-spec emission, manifest schema + sorting, escaping, no source mutation,
no journey-nav injection, no absolute paths).

MUST  escape via `html.escape(..., quote=True)` specifically (the contract's escape rule, pinned to the stdlib call)
MUST  use only stdlib + PyYAML in the renderer (no Jinja, no Mako, no build tool)

NEVER  include a JS framework, a bundler artefact, or any `<script src="...">` pointing at a non-relative URL — the site is openable as a static set of files

## CHECKLIST

  - [ ] `_concept/mockup-walkthrough/static-html/index.html` exists
  - [ ] `_concept/mockup-walkthrough/static-html/manifest.json` exists and parses as JSON
  - [ ] `manifest.schema_version == "1.0"`
  - [ ] One `screen/<group>/<name>.html` per screen file under `experience/screens/`
  - [ ] One `journey/<id>.html` per journey in `stories.yaml`
  - [ ] Every `<body>` in `screen/**/*.html` has `data-spec-screen`
  - [ ] Every annotatable node in `screen/**/*.html` has `data-spec-element`
  - [ ] Every auto-slugged element node also has `data-spec-provisional="true"`
  - [ ] No `<script src="http...">` or non-relative resource URL appears in any output file
  - [ ] Validator (`mockup-walkthrough/static-html/validator.py`) exits 0 on the produced site

EMIT  [mockup-walkthrough-static-html] started run_id=<uuid>
EMIT  [mockup-walkthrough-static-html] checkpoint screens=<N> journeys=<M>
EMIT  [mockup-walkthrough-static-html] completed run_id=<uuid> screens=<N> journeys=<M> warnings=<W>
