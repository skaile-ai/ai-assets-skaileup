---
path: [_concept/09_mockup/walkthrough/]
summary: clickable site per screen and journey, plus the manifest mockup-annotate reads
owner: [mockup-walkthrough]
may_propose: []
---

# _concept/09_mockup/walkthrough/

**schema_version: "1.2".** The built walkthrough: `<renderer>/index.html`, one page per screen, one per journey, and a `manifest.json`, where `<renderer>` is `static-html` or `astro`. This node owns everything both renderers share; each renderer's `skills/mockup-walkthrough/references/<renderer>/RENDERER.md` owns only its scaffold and the places it reads this node differently. `mockup-annotate` and `mockup-feedback` resolve a stakeholder's click to the producing artifact identically across renderers because every rendered node carries `data-spec-*` attributes from this node — a drifting attribute breaks that resolution.

**Change policy.** Pinned: a table, field name or warning kind changes only with a coordinated `mockup-annotate` update and a `schema_version` bump. `1.0` → `1.2` was additive-only (target resolution, app-shell nav, content synthesis, narrowed auto-slug, spec panel); `mockup-annotate` pins `^1.0` and is compatible.

## Contents

- `<renderer>/` — `static-html` or `astro`; the one directory `mockup-annotate` finds by its `manifest.json`.
- `<renderer>/screen/<group>/<name>.html`, `<renderer>/journey/<id>.html`, `<renderer>/index.html` — the pages.
- `<renderer>/manifest.json` — the machine index (§ Manifest schema).

## Format

### data-spec-* attribute table

| DOM location | Attribute | Value | Source |
|---|---|---|---|
| `<body>` of every `screen/<group>/<name>.html` | `data-spec-screen` | screen path stem (e.g. `01_user_auth/login`) | screen file path |
| every annotatable child node (form fields, buttons, links, images, regions, list items, nav items) | `data-spec-element` | element id (kebab-case) | `elements:` entry, or auto-slug |
| same node, when no explicit `elements:` entry exists for it | `data-spec-provisional` | literal string `"true"` | absent in YAML |
| `<body>` of every `journey/<id>.html` | `data-spec-journey` | journey id from stories.yaml | stories.yaml |
| each step link inside `journey/<id>.html` | `data-spec-screen` | the screen-stem of that step's screen | journey step entry |
| `<body>` of `index.html` | `data-spec-index` | literal string `"true"` | (none — site root marker) |

A renderer emits exactly the attributes in this table and no others; a lean attribute set keeps drift visible, and `mockup-annotate` ignores unknown ones. `data-spec-screen` carries the stem, never the repo-relative path with `.md`.

### screen_id vs screen_path

Both forms are kept in `manifest.json` so consumers can pick:

- `screen_path`: repo-relative path with extension, e.g. `07_screens/01_user_auth/login.md`. Used in journey `screen_sequence`, `screens[].screen_path` and `source_anchor`s.
- `screen_id`: path stem under `07_screens/` without `.md`, e.g. `01_user_auth/login`. Used in `data-spec-screen`, the rendered HTML filename and `screens[].screen_id`.

### kind → DOM tag mapping

| kind | rendered tag | notes |
|---|---|---|
| `input` | `<input>` or `<select>` | `options[]` present → `<select>` with one `<option>` per value; else unchanged (`name`, `aria-label`) |
| `button` | `<button>`, or `<a class="button">` when `target:` present | label as inner text; with `target:`, resolved relative href per § Target resolution |
| `link` | `<a>` | `href` = resolved `target:`; `href="#"` only as the unresolved/absent fallback (+ `unresolved_target` warning when declared-but-unresolved) |
| `image` | `<img>` | `src="#"` placeholder, `alt="<label>"`; `target:` present wraps the `<img>` in an `<a href="...">` (resolved per § Target resolution) |
| `text` | `<span>` | unchanged |
| `region` | `<section>` | label as inner `<h3>` |
| `list` | `<ul>` | one `<li>` per `items[]` entry (label verbatim; `items[].target` wraps that `<li>`'s content in `<a>`); absent/empty `items` → single placeholder `<li>`; the list element's own `target:` (distinct from `items[].target`) wraps the whole `<ul>` in an `<a href="...">`; both apply independently |
| `form` | `<form>` | unchanged |
| `nav` | `<nav>` | list of real links from `items[]` (or the generated app nav, § App-shell navigation); each item its own `data-spec-element` |
| `tabs` | `<nav class="tabs">` | one entry per `items[]`, first item active; entries with `target:` render as resolved `<a>`, without as inert `<span class="tab">`; each item its own `data-spec-element` (distinct from the container's); no JS switching (static fidelity boundary) |
| `table` | `<table>` | `<thead>` from `columns[]`; one `<tbody>` row per `sample_rows[]` (verbatim, escaped); no `sample_rows` → header + one skeleton row; `row_target:` wraps each row's first cell in `<a>` |
| `media` | `<figure>` | unchanged |
| `custom` | `<div>` | `target:` present wraps content in `<a>` |

States beyond `default` render as adjacent `<span class="state-<n>">` children of the element so reviewers see state coverage. Declared `columns` / `sample_rows` / `items` / `options` render as real DOM content, never a placeholder. `sample_rows` and `items` are authored fixture data (from `seed.json` scenarios or the screen's wireframe examples); a renderer renders exactly what is declared and backfills nothing.

### Target resolution

Resolves `target:` (`tree/07_screens/README.md § Navigation targets`) and a table's `row_target` on every rendered `link | button | list | image | custom` element, and on any `nav` / `tabs` / `list` `items[]` entry carrying its own `target`.

- **Rule.** From `screen/<gA>/<nA>.html`, a target `gB/nB` renders `href="../<gB>/<nB>.html"` (plus `#<fragment>` when present); from `index.html`, `href="screen/<gB>/<nB>.html"`. A target is resolvable iff `07_screens/<target-sans-fragment>.md` exists in the set of screens rendered in this walkthrough.
- **Soft-fail.** A target that does not resolve renders `href="#"` and records a `warnings[]` entry of `kind: "unresolved_target"`; renderers never hard-fail on it.
- **Absent target.** A `target:`-eligible element that declares none is intentionally inert (`<button>`, an untargeted `<span class="tab">`) and gets no warning.

### App-shell navigation

Generated, not authored as prose. One algorithm; each renderer implements it inside its own shell/layout template (the markup varies, never which nav wins):

1. **Shell-authoritative.** If `07_screens/shell.md` frontmatter has a `kind: nav` element (in its `elements:` block) with `items:`, render it in every screen page's shell wrapper, each item's `target` resolved per § Target resolution.
2. **Derived default.** Otherwise one link per rendered screen, grouped by the screen's directory segment under `07_screens/` (a feature slug). Group label = that directory name with any `NN_` numeric prefix stripped and `-`/`_` replaced by spaces. The generated nav element gets id `app-nav`, `data-spec-provisional="true"`, and exactly one `auto_slugged` warning (not one per link).

Either way, record the rendered nav in the manifest's top-level `app_nav[]` (§ Manifest schema) so annotate and later renders can diff what was shown.

### Auto-slug fallback

The renderer's half of the hybrid id strategy (provisional on render, promoted by feedback — `tree/09_mockup/feedback/README.md § Id promotion`). When a screen file has no `elements:` block, or a partial one:

1. Walk the screen body and identify renderable widgets by source order. Source set:
   - (a) markdown headings (`##`, `###`), **excluding** the canonical spec-template headings (case-insensitive): `Purpose`, `Route`, `What the User Sees`, `Wireframe`, `Information Displayed`, `Actions`, `Situations`, `UI Elements`, `Template Data`; the shell template's `Navigation`, `Layout Areas`, `Responsive Behaviour`; and any `# Screen: *` / `# Shell: *` H1. These are documentation structure: they feed § Spec reference panel's `<h2>` skeleton and are never rendered as `el-region` widgets. A screen's own non-canonical headings (a bespoke `## Notes`) stay in the net.
   - (b) form-field lines matching `[label]: input|button|...`,
   - (c) acceptance-criteria mentions in body text,
   - (d) `## Actions` bullets, label-extracted, reachable only when `elements:` is absent or partial for the widget a bullet describes. Label = the first quoted token (`"…"` or `„…“`) when the bullet has one; otherwise the clause before the first `→`, with a leading interaction verb (`Click`, `Change`, `Select`, `Switch`, `Drag`, `Pick`, `Open`, optionally after an article) stripped, truncated to ≤ 40 chars. The bullet's full text becomes the element's `describes:`. Kind: a quoted token or a `Click …` verb → `button`; `Change …` / `Select …` / `Pick …` → `input`; `Switch tab` → `tabs` (`items` from bold or quoted tab names in `## What the User Sees`, else two placeholder items).
   The net is deliberately wide; explicit ids win on collision.
2. For each widget not in `elements:` (matched by label-equality, case-insensitive), generate an id: lowercase the label; replace each non-`[a-z0-9]` run with a single `-`; trim leading/trailing `-`; if empty, `<kind>-<n>` with `n` a 1-based counter per screen per kind (`button-1`, `input-1`); on collision with another auto-slugged id in the same screen append `-2`, `-3`, … until unique. A collision with an explicit id records `kind: "auto_slug_collision"` and the auto-slugged element takes the suffixed id.
3. Render the node with `data-spec-element="<auto-slugged-id>"` and `data-spec-provisional="true"`.
4. Append a `warnings[]` entry of `kind: "auto_slugged"` to `manifest.json` per auto-slugged element.
5. The source `07_screens/<feature_slug>/<name>.md` is left untouched: promoting a provisional id is `mockup-feedback`'s job.

### items[] id derivation

Applies to the entries of a `nav`, `tabs` or `list` element and to the shell-authoritative app nav. `id` is optional on `nav` and `tabs` items and undefined on `list` items, so an id-less entry is the normal case, and feedback resolves a click on a list item by the id the renderer wrote — every renderer derives it the same way.

1. An entry that declares `id:` uses it verbatim: no `data-spec-provisional`, no warning.
2. An entry without `id:` gets one by the § Auto-slug fallback kebab-slug algorithm (lowercase label, non-alphanumeric runs → `-`, trim and collapse dashes, `<kind>-<n>` when the label slugs to empty), **scoped to that element's own `items[]`**: a collision suffix (`-2`, `-3`, …) disambiguates only within the same element's items.
3. Render the item's node — `<li>` for `list`, `<a>` or `<span class="tab">` for `tabs`, `<a>` for `nav` — with `data-spec-element="<derived-id>"` and `data-spec-provisional="true"` (an id-less entry establishes no identity of its own, like any auto-slugged widget).
4. Append one `auto_slugged` `warnings[]` entry per id-less item (`element_id` = the derived item id, `screen_path` = that screen's path).

### Spec reference panel

Every screen page renders the screen's full spec body — every canonical section (`Purpose`, `Route`, `What the User Sees`, `Wireframe`, `Information Displayed`, `Actions`, `Situations`, `UI Elements`, `Template Data`; for the shell `Navigation`, `Layout Areas`, `Responsive Behaviour`) plus the `### Wireframe` fence verbatim — only inside a collapsed `<details class="spec-panel"><summary>View spec</summary>…</details>`, placed after the synthesized UI and before the page footer; the spec body is never primary inline content.

- The panel carries no `data-spec-*` attribute: it is reference prose, not an annotatable surface.
- **Zero explicit elements.** When a screen has no `elements:` (or an empty one) and auto-slug recovers nothing either, the panel renders **open** (`<details open>`) because the spec is then the only content worth showing, and the renderer records `kind: "no_explicit_elements"`.

### Screen-in-multiple-journeys rule

A screen's "Next →" journey navigation exists only inside `journey/<id>.html`; screen pages embed no journey-step navigation (Next/Prev, journey ordering), or screen renders couple to journey state. A screen's footer may list the journeys it belongs to, linking to the journey pages. The screen's own `target:` links and the generated app-shell nav are not journey navigation and render on every screen regardless of membership.

### Error handling

| Condition | Behaviour |
|---|---|
| Malformed YAML in screen file | Fail loudly, exit non-zero, name the offending file |
| Screen in journey but absent on disk | `manifest.warnings[]` `kind: "missing_screen"` + dead-end `<li class="journey-step-missing">` |
| `screen_sequence` absent for a journey | `manifest.warnings[]` `kind: "missing_screen_sequence"`, skip that journey render |
| Zero journeys in `stories.yaml` | Render "No journeys defined", `kind: "no_journeys"` |
| Missing `05_features/` | Soft gate, `kind: "missing_feature"`, continue; `manifest.features[]` → `[]` |
| Unknown `elements:` kind | Render as `custom`, `kind: "unknown_element_kind"` |
| `layout:` reference to non-existent file | `kind: "missing_layout"`, fall back to the renderer's default shell |
| Auto-slug collision | `kind: "auto_slug_collision"`, suffix auto id with `-2`, `-3`, … |
| `target:` / `row_target:` doesn't resolve to a rendered screen | `href="#"`, `kind: "unresolved_target"` |
| Screen has zero explicit `elements:` (none discovered by auto-slug either) | Spec panel renders `open`, `kind: "no_explicit_elements"` |

## Manifest schema

The contract handed to `mockup-annotate`. Field names pinned exactly.
`<variant>` is the renderer's short name (`static-html` or `astro`);
`renderer_version` is `mockup-walkthrough`'s `version`.

```json
{
  "schema_version": "1.2",
  "renderer": "mockup-walkthrough-<variant>",
  "renderer_version": "0.1.0",
  "generated_at": "2026-05-07T12:34:56Z",
  "source_root": "07_screens",
  "app_nav": [
    {
      "label": "Aufgaben",
      "target": "../20_tasks/task_list.html",
      "source": "07_screens/shell.md"
    }
  ],
  "screens": [
    {
      "screen_path": "07_screens/01_user_auth/login.md",
      "screen_id": "01_user_auth/login",
      "rendered_html": "screen/01_user_auth/login.html",
      "implements": ["05_features/01_user_auth/login.md"],
      "data_entities": ["User"],
      "layout": "07_screens/shell.md",
      "elements": [
        {
          "element_id": "submit-button",
          "kind": "button",
          "label": "Sign in",
          "states": ["default", "loading", "disabled", "error"],
          "provisional": false,
          "source_anchor": "07_screens/01_user_auth/login.md#elements/submit-button"
        },
        {
          "element_id": "open-admission-form",
          "kind": "button",
          "label": "Aufnehmen",
          "states": ["default"],
          "provisional": false,
          "target": "11_intake/case_admission_form",
          "source_anchor": "07_screens/01_user_auth/login.md#elements/open-admission-form"
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
          "source_anchor": "07_screens/01_user_auth/login.md#elements/faelle-table"
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
          "source_anchor": "07_screens/01_user_auth/login.md#elements/pending-registrations"
        },
        {
          "element_id": "filter-bereich",
          "kind": "input",
          "label": "Bereich",
          "states": ["default"],
          "provisional": false,
          "options": ["Alle", "Kindergruppe", "Jugendgruppe"],
          "source_anchor": "07_screens/01_user_auth/login.md#elements/filter-bereich"
        }
      ]
    }
  ],
  "journeys": [
    {
      "journey_id": "user-signs-in",
      "rendered_html": "journey/user-signs-in.html",
      "source": "04_journeys/stories.yaml#user-signs-in",
      "screen_sequence": [
        "07_screens/01_user_auth/login.md",
        "07_screens/02_dashboard/home.md"
      ]
    }
  ],
  "features": [
    {
      "feature_path": "05_features/01_user_auth/login.md",
      "rendered_screens": ["07_screens/01_user_auth/login.md"]
    }
  ],
  "warnings": [
    {
      "kind": "auto_slugged",
      "screen_path": "07_screens/02_dashboard/home.md",
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
  `07_screens`).
- `app_nav[]`: the generated app-shell nav actually rendered into every
  screen's shell wrapper (§ App-shell navigation). One entry per rendered
  link.
  - `app_nav[].label` / `app_nav[].target`: as rendered — `target` is the
    renderer's own resolved/rendered href (per § Target resolution), not the
    raw `screen_id`. This is NOT the same form as `screens[].elements[].target`,
    which is the declared/verbatim value (see below) — the two fields look
    similar but carry opposite kinds of value. The resolved href is also
    renderer-scheme-specific: static-html emits a relative `.html`
    path (e.g. `"../20_tasks/task_list.html"`), astro emits a
    root-relative extension-less path (e.g. `"/screen/20_tasks/task_list"`);
    a consumer reading only the manifest should not assume one portable
    scheme across renderers.
  - `app_nav[].source`: `"derived"` when the renderer generated the
    default nav itself, or the shell source path (e.g.
    `"07_screens/shell.md"`) when a shell `kind: nav`
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
  the screen's `elements:` block (`screen_id[#fragment]` form) when declared, valid on
  the kinds listed in `tree/07_screens/README.md § Navigation targets` (`row_target`:
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
renderer's `RENDERER.md` (e.g. astro's `stale_tailwind_config`). Extend cautiously
— the feedback cluster switches on this field.


## Writing it

1. **Resolve the renderer, once, before anything else.** `_concept/02_grounding/onboarding/answers.json` key `renderer` wins when set (`static-html` | `astro`). Absent, the flow in `_concept/01_meta/scope.yaml` decides: `appbuilder-mvp` gets **static-html**; `appbuilder-standard` and `skaileup-concept-only` get **astro**. The answer names the output root `_concept/09_mockup/walkthrough/<renderer>/` and the one reference directory worked from, `skills/mockup-walkthrough/references/<renderer>/`. A flow this table does not list is a project that has not been scoped: say so and stop, because a guessed renderer's output may not be where the annotator looks.
2. **Read the inputs and build one in-memory model.**
   - Glob `07_screens/*/*.md` (one level, so the root `shell.md` is not a screen), sorted by path, and build the set of rendered screen ids **before** resolving any `target`, so resolution never depends on parse order.
   - Resolve every `target` / `row_target` / `items[].target` against that set; unresolved means `href: null` plus an `unresolved_target` warning.
   - Auto-slug what `elements:` leaves uncovered and derive ids for id-less `items[]`, per § Auto-slug fallback and § items[] id derivation.
   - Build the app nav per § App-shell navigation.
   - Flatten `03_brand/brand.tokens.json` into `--token-*` custom properties per `tree/03_brand/brand.tokens.md § Flattening to CSS`, plus a `.dark { … }` block when `brand.dark.tokens.json` exists (`tree/03_brand/brand.tokens.md § Light and dark`).
   - Read `04_journeys/stories.yaml`; a journey without a `screen_sequence` gets a `missing_screen_sequence` warning and is skipped.
   - Glob `05_features/*/*.md` (one level; `featuresets.md` is the roster, not a feature) for manifest traceability only: features are never rendered, and their absence costs the manifest its feature links rather than stopping the render.
   - Element-schema validation is authoring-time work (`tree/07_screens/README.md`); handle render-time semantics only, and let a screen file with malformed YAML stop the run naming the file rather than ship a half-rendered site.
3. **Render**, following `skills/mockup-walkthrough/references/<renderer>/RENDERER.md` and § Format. Escape every interpolated string (labels, ids, `screen_path`, `journey_id`, titles; quotes included) because frontmatter is authored prose and carries quotes and angle brackets. Renderers read their inputs and write only under the output root: promoting a provisional id is `mockup-feedback`'s job, and a renderer that edits its own inputs makes the next render unreproducible. Read `_concept/09_mockup/feedback/devlog.md` first when it exists (`tree/09_mockup/feedback/devlog.md`).
4. **Write `manifest.json`** from the model, conforming to § Manifest schema with `schema_version: "1.2"`. Element `target` / `row_target` / `items[].target` echo the **declared** `screen_id[#fragment]` verbatim; only `app_nav[].target` carries a resolved value, because the annotator resolves declared targets itself and a pre-resolved one hides which screen the author named. Sort `screens[]` by `screen_path`, `journeys[]` by `journey_id`, `features[]` by `feature_path`; leave `app_nav[]` in rendered order. Paths are repo-relative, never absolute filesystem paths. Write atomically (tmp → fsync → rename). Set `renderer` to `mockup-walkthrough-<renderer>` and `renderer_version` to the skill's `version`.
5. **Validate**: `python skills/mockup-walkthrough/references/<renderer>/validator.py _concept/09_mockup/walkthrough/<renderer>` from the repo root. Exit 0 is ready for `mockup-annotate`; exit 2 prints violations as `<file>:<line>: <message>`.

## Checks

- The validator exits 0.
- `manifest.json` names every screen under `07_screens/` and every journey in `stories.yaml`.
- Every `warnings[].kind` is in the enum or documented in the renderer's `RENDERER.md`.
