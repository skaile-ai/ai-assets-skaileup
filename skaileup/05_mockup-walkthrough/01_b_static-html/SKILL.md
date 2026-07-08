---
name: mockup-walkthrough-static-html
description: "Use when stakeholders need a clickable static HTML walkthrough of the application — zero build, no JS framework, openable directly in a browser. Generates one HTML file per screen and per journey, plus a manifest.json that the mockup-feedback cluster reads to resolve clicks back to source artefacts. Best for appbuilder-simple tier."
metadata:
  version: "0.2.0"
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
(schema_version "1.2"): data-spec-* attribute table, screen_id vs screen_path,
kind → DOM tag mapping (incl. `target` resolution, `table`, `tabs`, populated
`list`/`select`), § Target resolution, § App-shell navigation, § Auto-slug
fallback (narrowed source set), § Spec reference panel, manifest schema +
field semantics, warnings[].kind enum, shared error handling,
screen-in-multiple-journeys rule, shared MUST/NEVER. Read before rendering;
pinned, MUST NOT be restated here.

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

**Body markdown rule.** Screen markdown body renders as reference prose
inside the collapsed § Spec reference panel (STEP 3), and DOES NOT receive
`data-spec-element` attributes there. Only explicit `elements:` block (or
auto-slug fallback) produces annotatable nodes, and those render in the
page's synthesized main content flow, not inside the spec panel.

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
  - **Build the rendered-screen-id set first** (all `screen_id` values —
    `<group>/<name>` path stems — from this glob) before parsing any
    element's `target:`. Every `target`/`row_target`/`items[].target` value
    is validated against this set (§ Navigation targets resolution below);
    building it up front means resolution never depends on parse order.
  - For each screen: parse YAML frontmatter (PyYAML); extract `implements[]`,
    `data_entities[]`, `layout`, `elements[]` (default `[]`). Capture screen
    body markdown for descriptive rendering.
  - Validate `elements[]` against `contracts/elements_block.md` (v0.3). If
    `lab/validate-elements-block/` available, delegate; otherwise apply these
    checks per element and emit `warnings[]` accordingly (render the node
    regardless — soft-fail always):
    - `kind` outside the v0.3 enum (`input, button, link, image, text,
      region, list, form, nav, media, custom, table, tabs`) → warning
      `kind: "unknown_element_kind"`, treat as `custom`.
    - `target` / `row_target` present → resolve against the rendered-screen-id
      set (§ Navigation targets below); unresolved → `href="#"` +
      `kind: "unresolved_target"` warning; this is the only target-related
      check this renderer performs at render time (shape/grammar validation —
      malformed `screen_id`, `target` on a non-interactive kind, etc. — is
      `lab/validate-elements-block`'s job per the contract, not re-litigated
      here).
    - `columns` / `sample_rows` / `items` / `options` — parsed and rendered
      verbatim as declared (§ Content fidelity); this renderer does not
      re-validate `sample_rows` row length against `columns` length —
      authoring-time validation owns that.

  > **Design note:** this renderer does NOT re-validate `elements:` block
  > schema shape — `sample_rows` row-length vs. `columns`, per-kind `items`
  > shape, or `target`/`screen_id` grammar. That's `lab/validate-elements-block`'s
  > job at authoring time (`contracts/elements_block.md` § Validation is
  > explicit that the schema validator, not the renderer, owns those
  > checks). This renderer assumes schema-valid input and handles only
  > render-time semantics — target resolution success/failure, reflected
  > via `unresolved_target` warnings (see § Navigation targets below).
  > Consistent with `contracts/walkthrough_renderer.md`'s `warnings[].kind`
  > enum, which has no length-mismatch or shape-mismatch kind at all.

  - **Navigation targets — resolution rule** (`contracts/elements_block.md`
    § Navigation targets, `contracts/walkthrough_renderer.md` § Target
    resolution): a `target`/`row_target` value is `screen_id[#fragment]`.
    Strip the fragment; the target resolves iff the remaining `screen_id` is
    in the rendered-screen-id set built above. From `screen/<gA>/<nA>.html`,
    a resolved target `gB/nB` renders `href="../<gB>/<nB>.html"` (+
    `#<fragment>` when present). Unresolved → `href="#"` + `unresolved_target`
    warning (declared-but-unresolved only; an absent `target:` is not an
    error and gets no warning).
  - Parse `experience/screens/00_layout/shell.md` frontmatter, when the file
    exists, for an `elements:` entry with `kind: nav` and non-empty `items:`
    — this is the **shell-authoritative app nav** (§ App-shell navigation,
    used in STEP 3). Absent file, absent `elements:`, absent `kind: nav`
    entry, or an entry with empty/absent `items:` — all fall through to the
    **derived-default** case (STEP 3).
  - Read `experience/journeys/stories.yaml`. Validate each `journeys[]` entry
    has `id` AND `screen_sequence`. Missing `screen_sequence` → warning
    `kind: "missing_screen_sequence"`, skip that journey render.
  - Read `design/tokens.json`. Flatten nested tree depth-first into flat dict
    keyed `--token-<dotted-path-with-hyphens>`. Example:
    `{"color": {"primary": "#0ea5e9"}}` → `--token-color-primary: #0ea5e9`
    (same rule as `mockup-component-isolated-html/scripts/inline_tokens.py`).
  - Glob `experience/features/**/*.md`; sort lexicographically. Build
    `feature -> screens[]` map by inverting `screens[].implements[]`.
  - **Auto-slug source set** (rewritten, `contracts/walkthrough_renderer.md`
    § Auto-slug fallback) — walked only when a screen's `elements:` is
    absent OR partial (i.e. for any widget not already covered by an
    explicit entry, matched by label-equality, case-insensitive):
    - (a) markdown `##`/`###` headings, **excluding** — case-insensitive —
      the canonical spec-template headings `Purpose`, `Route`, `What the
      User Sees`, `Wireframe`, `Information Displayed`, `Actions`,
      `Situations`, `UI Elements`, `Template Data`; the shell template's own
      `Navigation`, `Layout Areas`, `Responsive Behaviour`; and any
      `# Screen: *` / `# Shell: *` H1 (H1s are never scanned regardless — only
      `##`/`###` are widget sources). These excluded headings become the
      § Spec reference panel's skeleton instead (see STEP 3) and are
      **never** rendered as `el-region` widgets. A screen's own
      non-canonical heading (e.g. a bespoke `## Notes`) stays in the
      discovery net and renders as an inert `<span>` (`kind: text`), same as
      before this revision.
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
    ID generation, collision handling, `data-spec-provisional="true"`, and
    the `auto_slugged` warning-per-element rule are unchanged from before
    this revision (kebab-case slug of the label; `<kind>-<n>` fallback when
    the label slugs to empty; `-2`/`-3`… suffix on collision;
    `auto_slug_collision` warning when colliding with an explicit id).
  - Build normalised in-memory model:
    `{ screens: [...], journeys: [...], tokens: {...}, features: [...],
    shell_nav: {...} | null, warnings: [...] }`.

### Edge cases

  - **Malformed YAML in a screen file** → fail loudly, exit non-zero. No
    partial render; error message names offending file.
  - **Screen referenced from a journey but absent on disk** → record
    `manifest.warnings[]` with `kind: "missing_screen"` AND skip that journey
    step (link in `journey/<id>.html` becomes dead-end placeholder, NOT a 404).
  - **`elements:` entry with a `kind` outside v0.3 enum** → render with
    `data-spec-element` set, kind treated as `custom`, record warning
    `kind: "unknown_element_kind"`.
  - **`target`/`row_target` declared but unresolved** → `href="#"` +
    warning `kind: "unresolved_target"`; never hard-fail.
  - **`layout:` reference pointing to non-existent file** → warning
    `kind: "missing_layout"`, fall back to built-in default shell.
  - **`experience/features/` empty or missing** → soft gate, warning
    `kind: "missing_feature"`, continue rendering; `manifest.features[]`
    emitted as `[]`.

## STEP 3: Render screens

  > **`items[]` id derivation (`nav` / `tabs` / `list`, referenced below and
  > by the shell-authoritative app nav above).** `elements_block.md` leaves
  > `id` optional on `nav`/`tabs` items and doesn't define an `id` field on
  > `list` items at all — an id-less `items[]` entry is the normal case,
  > not an edge case. When an entry declares `id:`, use it verbatim (no
  > `data-spec-provisional`, no warning). When it does **not**:
  > 1. Derive an id via the same kebab-slug algorithm as top-level
  >    auto-slug (STEP 2 § Auto-slug source set: lowercase, non-alphanumeric
  >    runs → `-`, trim/collapse dashes; `<kind>-<n>` fallback when the
  >    label slugs to empty), **scoped to that element's own `items[]`** —
  >    a collision suffix (`-2`/`-3`…) disambiguates only within the same
  >    element's items, never across the whole screen.
  > 2. Render the item's node (the `<li>` for `list`, the `<a>`/`<span
  >    class="tab">` for `tabs`, the `<a>` for `nav`) with
  >    `data-spec-element="<derived-id>"` **and** `data-spec-provisional="true"`.
  > 3. Append a `warnings[]` entry of `kind: "auto_slugged"` to
  >    `manifest.json` (`element_id` = the derived item id, `screen_path` =
  >    this screen's path) — one entry per id-less item, same shape as any
  >    other `auto_slugged` warning.
  >
  > This follows directly from `contracts/walkthrough_renderer.md`'s
  > `data-spec-*` attribute table, which names "list items, nav items"
  > explicitly as `data-spec-provisional`-eligible whenever "no explicit
  > `elements:` entry exists for it" — an id-less `items[]` entry has no
  > explicit entry establishing its own identity (it's derived from
  > `label`), exactly like a top-level auto-slugged widget.

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
  - **Render the app-shell nav** (`contracts/walkthrough_renderer.md`
    § App-shell navigation) as a `<nav class="app-nav">` sibling placed
    after the `<header>` and before `<main>` — i.e. shell chrome, not
    screen-specific main content — identically on every screen page:
    - **Shell-authoritative case** (STEP 2 found a `kind: nav` element
      with `items:` on `00_layout/shell.md`): `data-spec-element="<the
      shell element's id>"` on the `<nav>` container, no
      `data-spec-provisional` on the container itself (it's
      shell-authoritative, not derived). One `<li>` per `items[]` entry,
      each `<a data-spec-element="<item-id>" href="<resolved>">` (resolved
      per § Target resolution) — `<item-id>` per the **`items[]` id
      derivation** rule above: verbatim when the item declares `id:`;
      otherwise a derived kebab-slug id, plus `data-spec-provisional="true"`
      on that `<a>` and an `auto_slugged` warning, scoped to this nav's own
      items. No group subdivision — the authored order is used verbatim.
    - **Derived-default case** (no authoritative shell nav): one link per
      *rendered* screen (this walkthrough's screens, in the same
      lexicographic-by-`screen_path` order as `manifest.screens[]` —
      deterministic, no separate sort invented), grouped under a
      `<span class="nav-group-label">` per `<group>` (the screen's
      directory segment; label = dir name with its `NN_` prefix stripped
      and underscores replaced by spaces — e.g. `00_auth` → `auth`; this
      label is generated-nav-only, distinct from the raw `<group>` heading
      `index.html`'s screen list already uses and continues to use
      unchanged). Container gets `data-spec-element="app-nav"
      data-spec-provisional="true"`; each per-screen link gets its own
      `data-spec-element="app-nav-<n>"` (1-based, position in the flat
      link list) `data-spec-provisional="true"` — link text = screen
      filename stem, underscores → spaces (e.g. `verify_email` →
      `verify email`); href resolved exactly like any other target. Emit
      **exactly one** `auto_slugged` `warnings[]` entry for the whole
      generated nav (`element_id: "app-nav"`, no `screen_path` — it isn't
      owned by one screen), never one per link.
    - Either way, record the rendered nav in `manifest.app_nav[]` (one
      entry per link, in the same order rendered): `label` = the link text
      as rendered, `target` = the resolved href **as it renders from any
      `screen/<group>/<name>.html` page** (all screen pages sit at the same
      depth, so this href string is identical regardless of source
      screen — no need to special-case it per screen), `source` =
      `"derived"` or the shell source path.
  - Render the explicit `elements[]` first (in declaration order), as the
    page's primary content flow inside `<section class="elements">` (no
    separate "grid" treatment — this is the same content-flow container as
    before, just no longer paired with a prose dump above/below it):
    - Choose the HTML tag per `contracts/walkthrough_renderer.md` § kind →
      DOM tag mapping. Per-kind specifics this renderer implements:
      - `link`/`button`/`image`/`custom` with a `target:` → resolved
        `<a href="...">` (button: `<a class="button">`); without `target:`
        → unchanged inert tag (button stays `<button>`; a `link`/`image`/
        `custom` with no `target:` renders its unchanged base tag with
        `href="#"`/no-wrap respectively — absence of `target:` is legal
        and inert, not a warning).
      - `list` → `<ul>`, one `<li>` per `items[]` entry (label verbatim
        text; an entry with `target:` wraps its label in `<a>`); the
        list's own `target:` (if declared) additionally wraps the whole
        `<ul>` in an outer `<a>` — the two wrap independently, both can be
        present at once. Empty/absent `items` → single placeholder `<li>`.
        Each `<li>` gets `data-spec-element="<item-id>"` per the **`items[]`
        id derivation** rule above — `list` items have no `id` field in the
        schema at all, so the derived (provisional + `auto_slugged`) path
        is the normal one, not an edge case.
      - `table` → `<table data-spec-element="<id>">` with `<thead>` built
        from `columns[]` and one `<tbody><tr>` per `sample_rows[]` entry,
        cells verbatim/escaped in column order; `row_target:` (when
        present) wraps each row's **first cell only** in a resolved `<a>`.
        No `sample_rows` → header row plus exactly one skeleton `<tr>`
        (empty `<td>`s, one per column) — never fabricated content.
      - `tabs` → `<nav class="tabs" data-spec-element="<id>">`, one entry
        per `items[]`: first entry gets class `active`; an entry with
        `target:` renders `<a class="tab" data-spec-element="<item-id>"
        href="...">`, without renders `<span class="tab"
        data-spec-element="<item-id>">` (inert); no JS tab-switching.
        `<item-id>` per the **`items[]` id derivation** rule above —
        `elements_block.md`'s own pinned `tabs` example never gives an item
        an `id` either, so expect the derived (provisional + `auto_slugged`)
        path on nearly every `tabs` element in practice.
      - `input` with `options:` → `<select data-spec-element="<id>"
        name="<id>" aria-label="<label>">`, one `<option value="<v>">`
        per value; without `options:` → unchanged `<input>`.
    - Emit `data-spec-element="<element.id>"` on the tag identified above
      (or on the outer wrapping `<a>` when target-wrapping applies to a
      kind whose base tag isn't itself the `<a>`, e.g. `custom`/`image`;
      for `link`/`button` the `<a>` IS the tagged node).
    - If the element entry has `provisional: true`, also emit
      `data-spec-provisional="true"`.
    - Render the label as visible text (escaped via
      `html.escape(..., quote=True)`), except where a kind's mapping above
      renders structured content instead (table rows, list/tabs items,
      select options) — those render their own declared content, not the
      element's own top-level `label`.
    - For each state in `element.states` beyond `default`, render a small
      sibling `<span class="state-<state>">` so visual reviewers can see
      state coverage.
  - For widgets discoverable in the screen body but absent from
    `elements[]`, apply the auto-slug fallback (STEP 2 source set) and
    emit them at the bottom of `<main>`'s synthesized-content flow (after
    the explicit elements, still before the spec panel) inside an HTML
    comment-delimited `<!-- auto-slugged --> ... <!-- /auto-slugged -->`
    group so the source ordering vs auto-slugged ordering is visually
    distinct.
  - **Spec reference panel** (`contracts/walkthrough_renderer.md` §
    Spec reference panel) — replaces the old `screen-body-prose` section.
    Placed after the synthesized UI (explicit + auto-slugged elements) and
    before the footer:
    `<details class="spec-panel"><summary>View spec</summary>…</details>`.
    Content = the screen body's top-level intro prose (any paragraph
    before the first `##`/`###` heading) **plus** every canonical section
    present (heading + its content, per the STEP 2 exclusion list) **plus**
    the `### Wireframe` fence verbatim. A screen's own non-canonical
    heading is **not** additionally duplicated here — it is already
    surfaced via auto-slug discovery (as an inert widget) or covered by an
    explicit element; duplicating it into the panel too would show the
    same content twice for no reason. No `data-spec-*` attribute of any
    kind inside the panel — it is reference prose, not an annotatable
    surface.
    - **Zero explicit elements.** When the screen has no `elements:` at all
      (or an empty one) AND the auto-slug walk (STEP 2) discovers nothing
      either, render `<details open class="spec-panel">` instead of
      collapsed, and emit a `warnings[]` entry of `kind:
      "no_explicit_elements"`. This is independent of whether the screen
      HAS explicit elements that are merely few — a screen with even one
      declared element (however partial) keeps the panel collapsed.
  - Add a footer linking back to `index.html` and, when the screen
    appears in any journey, list those journeys with links to
    `journey/<id>.html`. (See STEP 3 for the cross-journey rule.)
  - Write the file UTF-8, LF.

  MUST escape every label, id, screen_path, journey_id with
  `html.escape(..., quote=True)` before substitution into HTML.
  NEVER trust frontmatter strings; they may contain quotes, angle
  brackets, or unicode that breaks the document.

### Inline CSS additions

  Extend the shell's `<style>` block (same block that already carries the
  flattened token custom properties + `body`/`.state` rules) with:

  - `[data-spec-provisional="true"] { outline: 1px dashed #999;
    outline-offset: 2px; }` — the auto-slug visual-distinction treatment,
    generalized via the attribute selector so it applies uniformly to
    auto-slugged elements AND the generated app-nav (both are provisional
    by definition) without a separate `.auto-slugged` rule.
  - `.app-nav` — group label, and a horizontal `<ul>` (flex, gap, no
    bullets) for the nav links.
  - `.element table` / `.element table th, td` / `.element table thead` —
    real bordered table styles, distinct from (and replacing, for
    rendered content) the old prose-table styling that only ever applied
    inside `screen-body-prose`.
  - `.element select` — minimal padding so it doesn't look like plain text.
  - `nav.tabs`, `nav.tabs .tab`, `nav.tabs .tab.active` — flex tab bar,
    bottom-border active-state treatment (no JS switching, static fidelity
    only).
  - `details.spec-panel` / `details.spec-panel summary` — bordered,
    padded, collapsed-by-default (native `<details>` semantics handle the
    collapse; no extra CSS needed for that part), pointer cursor on the
    summary.

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
  - `schema_version = "1.2"`.
  - `renderer = "mockup-walkthrough-static-html"`,
    `renderer_version = "0.2.0"` (this skill's `metadata.version`).
  - `generated_at = ` current UTC ISO-8601 (e.g.
    `2026-05-08T12:34:56Z`). For deterministic snapshot tests, the
    validator replaces this value with `"<pinned>"` before comparison
    (see STEP 5).
  - `screens[].elements[]` — echo `target` / `columns` / `sample_rows` /
    `items` / `options` / `row_target` verbatim from frontmatter when the
    element declares them (per `contracts/walkthrough_renderer.md` § Field
    semantics — these are the *declared* value, not the resolved href; the
    rendered HTML carries the resolved href).
  - Top-level `app_nav[]` — one entry per rendered nav link, in rendered
    order (positional, not alphabetic): `{label, target, source}` per
    STEP 3's app-shell nav rendering.
  - Sort `screens[]` by `screen_path`, `journeys[]` by `journey_id`,
    and `features[]` by `feature_path` for deterministic diffs. `app_nav[]`
    is NOT sorted — it keeps rendered order.
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
  - [ ] `manifest.schema_version == "1.2"`
  - [ ] One `screen/<group>/<name>.html` per screen file under `experience/screens/`
  - [ ] One `journey/<id>.html` per journey in `stories.yaml`
  - [ ] Every `<body>` in `screen/**/*.html` has `data-spec-screen`
  - [ ] Every annotatable node in `screen/**/*.html` has `data-spec-element`
  - [ ] Every auto-slugged element node also has `data-spec-provisional="true"`
  - [ ] No `<script src="http...">` or non-relative resource URL appears in any output file
  - [ ] Validator (`mockup-walkthrough/static-html/validator.py`) exits 0 on the produced site
  - [ ] Every `elements[]` entry with a resolvable target renders an `<a>` whose href resolves to an existing rendered file
  - [ ] No rendered screen contains `href="#"` on a node whose manifest element declares a resolved target
  - [ ] Every screen page contains the app nav (`<nav>`) with one resolvable href per entry
  - [ ] No canonical spec heading appears as an `el-region` widget
  - [ ] Every declared table renders `sample_rows` verbatim as `<tbody>` rows
  - [ ] Spec body appears only inside `<details class="spec-panel">`
  - [ ] No auto-slugged label exceeds 40 chars or contains an action sentence

EMIT  [mockup-walkthrough-static-html] started run_id=<uuid>
EMIT  [mockup-walkthrough-static-html] checkpoint screens=<N> journeys=<M>
EMIT  [mockup-walkthrough-static-html] completed run_id=<uuid> screens=<N> journeys=<M> warnings=<W>
