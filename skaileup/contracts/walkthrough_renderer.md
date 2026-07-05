# Walkthrough Renderer Contract

**schema_version: "1.2"** · Owner of everything shared by the four
`mockup-walkthrough-*` renderers: `static-html` (reference implementation),
`astro`, `lit`, `framework`. Each renderer's SKILL.md owns ONLY its
technology-specific scaffold (build setup, templates, config) and cites this
file for the behaviour below. The `mockup-feedback-*` cluster resolves clicks
identically across renderers because of this contract.

**Change policy.** Pinned. Do not change any table, field name, or warning
kind without a coordinated update to `mockup-feedback-annotate` and a
`schema_version` bump. `"1.0"` → `"1.2"` (this revision) is a direct,
additive-only bump — no table, field, or warning kind was renamed or
removed, only added (target resolution, app-shell nav, content synthesis,
narrowed auto-slug, spec panel); the intermediate `"1.1"` was intentionally
never cut. `mockup-feedback-annotate` pins `^1.0` and was verified
compatible with this revision (see Task 9,
`docs/devlog/2026-07-05-mockup-merged-execution-plan.md`).

## data-spec-* attribute table

| DOM location | Attribute | Value | Source |
|---|---|---|---|
| `<body>` of every `screen/<group>/<name>.html` | `data-spec-screen` | screen path stem (e.g. `01_user_auth/login`) | screen file path |
| every annotatable child node (form fields, buttons, links, images, regions, list items, nav items) | `data-spec-element` | element id (kebab-case) | `elements:` entry, or auto-slug |
| same node, when no explicit `elements:` entry exists for it | `data-spec-provisional` | literal string `"true"` | absent in YAML |
| `<body>` of every `journey/<id>.html` | `data-spec-journey` | journey id from stories.yaml | stories.yaml |
| each step link inside `journey/<id>.html` | `data-spec-screen` | the screen-stem of that step's screen | journey step entry |
| `<body>` of `index.html` | `data-spec-index` | literal string `"true"` | (none — site root marker) |

**The renderer MUST NOT add `data-spec-*` attributes outside this table.**
Feedback-annotate ignores unknown ones, but a lean attribute set keeps drift
visible.

## screen_id vs screen_path

Both forms are kept in `manifest.json` so feedback consumers can pick:

- `screen_path`: full repo-relative path with extension, e.g.
  `experience/screens/01_user_auth/login.md`. Used in journey
  `screen_sequence`, in `screens[].screen_path`, and in `source_anchor`s.
- `screen_id`: path stem under `experience/screens/` without `.md`, e.g.
  `01_user_auth/login`. Used in `data-spec-screen`, in the rendered HTML
  filename, and in `screens[].screen_id`.

## kind → DOM tag mapping

| kind | rendered tag | notes |
|---|---|---|
| `input` | `<input>` or `<select>` | `options[]` present → `<select>` with one `<option>` per value; else unchanged (`name`, `aria-label`) |
| `button` | `<button>`, or `<a class="button">` when `target:` present | label as inner text; with `target:`, resolved relative href per § Target resolution |
| `link` | `<a>` | `href` = resolved `target:`; `href="#"` only as the unresolved/absent fallback (+ `unresolved_target` warning when declared-but-unresolved) |
| `image` | `<img>` | unchanged (`src="#"` placeholder, `alt="<label>"`) |
| `text` | `<span>` | unchanged |
| `region` | `<section>` | unchanged (label as inner `<h3>`) |
| `list` | `<ul>` | one `<li>` per `items[]` entry (label verbatim, `target:` wraps in `<a>`); absent/empty `items` → single placeholder `<li>` (degenerate case) |
| `form` | `<form>` | unchanged |
| `nav` | `<nav>` | list of real links from `items[]` (or the generated app nav, § App-shell navigation); each item its own `data-spec-element` |
| `tabs` | `<nav class="tabs">` | one entry per `items[]`, first item active; entries with `target:` render as resolved `<a>`, without as inert `<span class="tab">`; no JS switching (static fidelity boundary) |
| `table` | `<table>` | `<thead>` from `columns[]`; one `<tbody>` row per `sample_rows[]` (verbatim, escaped); no `sample_rows` → header + one skeleton row; `row_target:` wraps each row's first cell in `<a>` |
| `media` | `<figure>` | unchanged |
| `custom` | `<div>` | unchanged, gains: `target:` present wraps content in `<a>` |

States beyond `default` are rendered as adjacent `<span class="state-<n>">`
children of the element so visual reviewers can see state coverage.

## Target resolution

Resolves `target:` (`elements_block.md` § Navigation targets) and a table's
`row_target` on every rendered `link | button | list | image | custom`
element, and on any `nav` / `tabs` / `list` `items[]` entry carrying its own
`target`.

**Resolution rule.** From `screen/<gA>/<nA>.html`, a target `gB/nB` renders
`href="../<gB>/<nB>.html"` (plus `#<fragment>` when present); from
`index.html`, `href="screen/<gB>/<nB>.html"`. A target is resolvable iff
`experience/screens/<target-sans-fragment>.md` exists in the set of screens
actually rendered in this walkthrough.

**Soft-fail contract.** Renderers never hard-fail on an unresolved target.
When `target` doesn't resolve, the renderer emits `href="#"` and records a
`warnings[]` entry of `kind: "unresolved_target"`.

**Absent target.** A `target:`-eligible element that declares no `target:`
at all is not an error and gets no warning — an absent target on a
button/form-like action is intentionally inert (`<button>`, an untargeted
`<span class="tab">`, ...); not everything navigates.

## App-shell navigation

Generated, not authored as prose. The contract defines one nav-generation
algorithm; each renderer implements it inside its own shell/layout template
(no per-renderer variance in *which* nav wins, only in the markup used to
render it).

  1. **Shell-authoritative case.** If
     `experience/screens/00_layout/shell.md` frontmatter has a `kind: nav`
     element (in its `elements:` block) with `items:`, that element is
     authoritative: render it in every screen page's shell wrapper, with
     each item's `target` resolved per § Target resolution above.
  2. **Derived-default case.** Otherwise, derive a default nav: one link per
     rendered screen, grouped by `<group>` (the screen's directory segment
     under `experience/screens/`). Group label = that directory name with
     its `NN_` numeric prefix stripped and underscores replaced by spaces.
     The generated nav element gets id `app-nav`,
     `data-spec-provisional="true"`, and the renderer records exactly one
     `auto_slugged` warning for it (not one per link).

Either way, record the rendered nav in the manifest's top-level `app_nav[]`
(§ Manifest schema) so feedback-annotate and future renders can diff what
was actually shown.

## Auto-slug fallback

The renderer's portion of the hybrid ID strategy (`elements_block.md`
§ "Hybrid ID strategy"). When a screen file has no `elements:` block, OR has
a partial one, the renderer MUST:

  1. Walk the screen body and identify renderable widgets by source order.
     **Source set:**
     - (a) markdown headings (`##`, `###`) — **excluding** the canonical
       spec-template headings (case-insensitive): `Purpose`, `Route`,
       `What the User Sees`, `Wireframe`, `Information Displayed`,
       `Actions`, `Situations`, `UI Elements`, `Template Data`; plus the
       shell template's own `Navigation`, `Layout Areas`,
       `Responsive Behaviour`; plus any `# Screen: *` / `# Shell: *` H1.
       These are documentation structure, not widgets — they become the
       § Spec reference panel's `<h2>` skeleton instead and are **never**
       rendered as `el-region` widgets. A screen's own non-canonical
       headings (e.g. a bespoke `## Notes`) stay in the discovery net.
     - (b) form-field lines matching `[label]: input|button|...` pattern,
     - (c) acceptance-criteria mentions in body text,
     - (d) **`## Actions` bullets, label-extracted.** Reachable only when
       `elements:` is absent or partial for the widget a bullet describes.
       For each such bullet: label = the first quoted token (`"…"` or
       `„…“`) when the bullet contains one; otherwise the clause preceding
       the first `→`, with a leading interaction verb (`Click`, `Change`,
       `Select`, `Switch`, `Drag`, `Pick`, `Open`, optionally preceded by an
       article) stripped, truncated to ≤ 40 chars. The bullet's full text
       becomes the synthesized element's `describes:`. Kind inference from
       the bullet: a quoted token, or a `Click …` verb, → `button`;
       `Change …` / `Select …` / `Pick …` → `input`; `Switch tab` →
       `tabs` (with `items` sourced from bold or quoted tab names found in
       `## What the User Sees`, or two placeholder items if none are
       found).
     (Auto-slug net is intentionally wide; explicit ids always win on
     collision.)
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
     file. Promotion of provisional ids is `mockup-feedback-triage`'s job.

## Spec reference panel

Every screen page renders the screen's full spec body — every canonical
section (`Purpose`, `Route`, `What the User Sees`, `Wireframe`,
`Information Displayed`, `Actions`, `Situations`, `UI Elements`,
`Template Data`; for the shell, `Navigation`, `Layout Areas`,
`Responsive Behaviour`) plus the `### Wireframe` fence verbatim — inside a
collapsed

```html
<details class="spec-panel"><summary>View spec</summary>…</details>
```

element, placed after the synthesized UI and before the page footer.

- **No `data-spec-*` attribute of any kind** is emitted inside the panel —
  it is reference prose, not an annotatable surface.
- **Zero explicit elements.** When a screen has no `elements:` at all (or
  an empty one) and auto-slug recovers nothing either, the panel renders
  **open** (`<details open>`) instead of collapsed — the synthesized UI
  above it is empty, so the spec is the only content worth showing — and
  the renderer emits a `warnings[]` entry of `kind: "no_explicit_elements"`.

## Manifest schema

The contract handed to `mockup-feedback-annotate`. Field names pinned exactly.
`<variant>` is the renderer's short name (`static-html`, `astro`, `lit`,
`framework`); `renderer_version` is the renderer SKILL.md's
`metadata.version`.

```json
{
  "schema_version": "1.2",
  "renderer": "mockup-walkthrough-<variant>",
  "renderer_version": "0.1.0",
  "generated_at": "2026-05-07T12:34:56Z",
  "source_root": "experience/screens",
  "app_nav": [
    {
      "label": "Aufgaben",
      "target": "20_tasks/task_list",
      "source": "experience/screens/00_layout/shell.md"
    }
  ],
  "screens": [
    {
      "screen_path": "experience/screens/01_user_auth/login.md",
      "screen_id": "01_user_auth/login",
      "rendered_html": "screen/01_user_auth/login.html",
      "implements": ["experience/features/01_user_auth/login.md"],
      "data_entities": ["User"],
      "layout": "experience/screens/00_layout/shell.md",
      "elements": [
        {
          "element_id": "submit-button",
          "kind": "button",
          "label": "Sign in",
          "states": ["default", "loading", "disabled", "error"],
          "provisional": false,
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/submit-button"
        },
        {
          "element_id": "open-admission-form",
          "kind": "button",
          "label": "Aufnehmen",
          "states": ["default"],
          "provisional": false,
          "target": "11_intake/case_admission_form",
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/open-admission-form"
        },
        {
          "element_id": "faelle-table",
          "kind": "table",
          "label": "Fälle",
          "states": ["default", "loading", "empty"],
          "provisional": false,
          "columns": ["Patient", "Falltyp", "Bereich", "Status", "Aufgenommen"],
          "sample_rows": [
            ["Lena M.", "Teilstationär", "Kindergruppe", "Aktiv", "15.06.2026"]
          ],
          "row_target": "11_intake/case_detail",
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/faelle-table"
        },
        {
          "element_id": "pending-registrations",
          "kind": "list",
          "label": "Aufzunehmende Anmeldungen",
          "states": ["default", "empty"],
          "provisional": false,
          "items": [
            {"label": "Lena M. · geb. 14.03.2014 · Kindergruppe", "target": "11_intake/case_admission_form"}
          ],
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/pending-registrations"
        },
        {
          "element_id": "filter-bereich",
          "kind": "input",
          "label": "Bereich",
          "states": ["default"],
          "provisional": false,
          "options": ["Alle", "Kindergruppe", "Jugendgruppe"],
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/filter-bereich"
        }
      ]
    }
  ],
  "journeys": [
    {
      "journey_id": "user-signs-in",
      "rendered_html": "journey/user-signs-in.html",
      "source": "experience/journeys/stories.yaml#user-signs-in",
      "screen_sequence": [
        "experience/screens/01_user_auth/login.md",
        "experience/screens/02_dashboard/home.md"
      ]
    }
  ],
  "features": [
    {
      "feature_path": "experience/features/01_user_auth/login.md",
      "rendered_screens": ["experience/screens/01_user_auth/login.md"]
    }
  ],
  "warnings": [
    {
      "kind": "auto_slugged",
      "screen_path": "experience/screens/02_dashboard/home.md",
      "element_id": "kpi-card-1",
      "message": "No elements: block in screen frontmatter; auto-slugged 1 element."
    }
  ]
}
```

### Field semantics

- `schema_version`: bump on breaking change. Feedback cluster pins `^1.0`;
  `1.0` → `1.2` is additive-only and verified compatible with that pin
  (see the Change policy note above).
- `renderer` / `renderer_version`: identifies which walkthrough variant
  produced the site.
- `generated_at`: ISO-8601 UTC; lets feedback-annotate detect stale renders.
- `source_root`: relative path the screen paths are anchored to (always
  `experience/screens`).
- `app_nav[]`: the generated app-shell nav actually rendered into every
  screen's shell wrapper (§ App-shell navigation). One entry per rendered
  link.
  - `app_nav[].label` / `app_nav[].target`: as rendered (resolved target,
    not the raw `screen_id` — same resolution as `screens[].elements[].target`).
  - `app_nav[].source`: `"derived"` when the renderer generated the
    default nav itself, or the shell source path (e.g.
    `"experience/screens/00_layout/shell.md"`) when a shell `kind: nav`
    element was authoritative.
- `screens[].screen_path`: full path with `.md`. Used by feedback-annotate
  when it needs to read the source file.
- `screens[].screen_id`: the path stem `<group>/<name>` (no `.md`); the
  value emitted in `data-spec-screen`.
- `screens[].rendered_html`: site-relative path to the rendered HTML.
- `screens[].elements[].element_id`: the value emitted in
  `data-spec-element`.
- `screens[].elements[].provisional`: `true` when auto-slugged
  (mirrors `data-spec-provisional`).
- `screens[].elements[].target` / `.row_target`: echoed verbatim from
  `elements_block.md` (`screen_id[#fragment]` form) when declared, valid on
  the kinds listed in that contract's § Navigation targets (`row_target`:
  `table` only). Absent when the element declares no target. These are the
  *declared* value, not the resolved href — the rendered HTML carries the
  resolved href, this field is for feedback-annotate to re-derive it.
- `screens[].elements[].columns` / `.sample_rows`: echoed verbatim from a
  `kind: table` element's frontmatter when present.
- `screens[].elements[].items` / `.options`: echoed verbatim from a
  `nav` / `tabs` / `list` element's `items[]`, or an `input` element's
  `options[]`, when present.
- `screens[].elements[].source_anchor`: fragment-style pointer back to the
  source file. Explicit ids: `#elements/<element_id>`. Provisional:
  `#auto/<element_id>` (no entry yet in the YAML).
- `journeys[].screen_sequence`: ordered list of screen source paths. Same
  order drives the rendered "Next →" links inside `journey/<id>.html`.
- Sorting: `screens[]` by `screen_path`, `journeys[]` by `journey_id`,
  `features[]` by `feature_path` — deterministic diffs. `app_nav[]` keeps
  authored/derived order (nav is positional, not alphabetic). Write
  atomically (tmp → fsync → rename).

## warnings[].kind enum

`auto_slugged`, `auto_slug_collision`, `missing_layout`, `missing_feature`,
`unknown_element_kind`, `missing_screen`, `missing_screen_sequence`,
`no_journeys`, `unresolved_target`, `no_explicit_elements`.
Renderer-specific additions are allowed and documented in that
renderer's SKILL.md (e.g. astro's `stale_tailwind_config`). Extend cautiously
— the feedback cluster switches on this field.

## Shared error handling

| Condition | Behaviour |
|---|---|
| Malformed YAML in screen file | Fail loudly, exit non-zero, name the offending file |
| Screen in journey but absent on disk | `manifest.warnings[]` `kind: "missing_screen"` + dead-end `<li class="journey-step-missing">` |
| `screen_sequence` absent for a journey | `manifest.warnings[]` `kind: "missing_screen_sequence"`, skip that journey render |
| Zero journeys in `stories.yaml` | Render "No journeys defined", `kind: "no_journeys"` |
| Missing `experience/features/` | Soft gate, `kind: "missing_feature"`, continue; `manifest.features[]` → `[]` |
| Unknown `elements:` kind | Render as `custom`, `kind: "unknown_element_kind"` |
| `layout:` reference to non-existent file | `kind: "missing_layout"`, fall back to the renderer's default shell |
| Auto-slug collision | `kind: "auto_slug_collision"`, suffix auto id with `-2`, `-3`, … |
| `target:` / `row_target:` doesn't resolve to a rendered screen | `href="#"`, `kind: "unresolved_target"` |
| Screen has zero explicit `elements:` (none discovered by auto-slug either) | Spec panel renders `open`, `kind: "no_explicit_elements"` |

## Screen-in-multiple-journeys rule

When a screen appears in two or more journeys, each `journey/<id>.html`
retains its own "Next →" link only inside the journey HTML. The screen HTML
itself does NOT embed journey-specific navigation (else screen renders couple
to journey state). Cross-journey continuation is solely owned by
`journey/<id>.html`; the screen's footer may list the journeys it
participates in, linking to the journey pages. This is the *journey*-nav
restriction specifically — the screen's own `target:` links and the
generated app-shell nav (§ App-shell navigation) are unaffected by it and
render on every screen regardless of journey membership; see the narrowed
NEVER below.

## Shared MUST / NEVER

MUST  emit `data-spec-screen` on every screen `<body>`
MUST  emit `data-spec-element` on every annotatable child node
MUST  emit `data-spec-provisional="true"` on auto-slugged element nodes
MUST  emit `data-spec-journey="<id>"` on every journey `<body>`
MUST  emit `data-spec-index="true"` on `index.html` `<body>`
MUST  write `manifest.json` conforming to `§ Manifest schema` (`schema_version: "1.2"`)
MUST  sort manifest arrays lexicographically (`screens` by `screen_path`, `journeys` by `journey_id`, `features` by `feature_path`)
MUST  HTML-escape every interpolated string (labels, ids, paths, titles) including quotes
MUST  resolve every declared `target:` into a relative href, or emit `unresolved_target` and fall back to `href="#"`
MUST  render declared `columns` / `sample_rows` / `items` / `options` as real DOM content — no placeholder when content is declared
MUST  render the spec body only inside the collapsed spec panel (§ Spec reference panel), never inline as primary content

NEVER  emit `data-spec-*` attributes outside the pinned table
NEVER  mutate source files (`experience/screens/**`, `experience/journeys/stories.yaml`, `design/tokens.json`, `experience/features/**`) — renderers are read-only on inputs
NEVER  inject journey-*step* navigation (Next/Prev, journey-ordering) into `screen/**/*.html` — that lives only in `journey/<id>.html`; screen-intrinsic `target:` links and the generated app-shell nav are REQUIRED and are NOT journey-nav
NEVER  inline absolute filesystem paths into `manifest.json` — repo-relative paths only
NEVER  render a canonical spec-template heading (§ Auto-slug fallback exclusion list) as a widget
NEVER  fabricate sample data (`sample_rows`, `items`) not present in the screen source
