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

## STEP 3: Render journeys

## STEP 4: Emit index.html and manifest.json

## STEP 5: Validate

## MUST / NEVER

## CHECKLIST
