# Renderer: static-html

A zero-build site at `_concept/09_mockup/walkthrough/static-html/`, openable from the filesystem
with no toolchain. This is the shared contract's reference implementation: where the contract
is ambiguous, this renderer's output under `tests/expected/` is the tie-breaker.

Route item 3 of `../../SKILL.md` expands into the render rules below. Before rendering, read
`_concept/09_mockup/feedback/devlog.md` when it exists and treat each applied line for a
screen or feature file you are about to render as a constraint — a regeneration that reverts a
change a stakeholder already asked for reads as the tool ignoring the feedback round.

## What this renderer does differently

- **Hrefs are relative, with the extension** — `<screen>.html` from a screen page, `../journey/<id>.html`
  and `../floorplan/<screen>.html` likewise, and `screen/<screen>.html` from `index.html`. An unresolved target
  renders `href="#"`. Relative hrefs are what make the site work from a `file://` path and from
  any directory it is later copied to.
- **Everything runs at render time.** There is no build step and no pre-resolved data file, so
  targets, auto-slugs and `items[]` ids are resolved as each page is written.
- **Styling is one inline `<style>` block** in the shell, carrying the `--token-*` custom
  properties flattened from `03_brand/brand.tokens.json` per
  `tree/03_brand/brand.tokens.md § Flattening to CSS` (`:root`), plus a `.dark { … }`
  block from `brand.dark.tokens.json` when that file exists. No stylesheet file, no bundle.
- **Generate with the Python standard library plus PyYAML** — `html.escape`, `pathlib`, `json`,
  string substitution. No templating engine, no bundler. The generator runs at skill time and
  never ships, so its dependencies do not reach the output; keeping it stdlib-only is what makes
  the produced site trivially inspectable and keeps this renderer runnable anywhere Python is.

## Page layout

`index.html` sets `<body data-spec-index="true">` and lists screens flat, in `screen_id` order, and
journeys flat. Zero journeys renders the literal `No journeys defined` plus a `no_journeys`
warning. A `<footer>` carries the generation timestamp.

Each `screen/<screen>.html` sets `<body data-spec-screen="<screen_id>">` and stacks:
the app nav as a `<nav class="app-nav">` between `<header>` and `<main>` (shell chrome, so it
renders identically on every page); the floorplan section (two `<iframe>`s onto
`../floorplan/<screen>.html`) or the `.floorplan-notice`, per
`tree/09_mockup/walkthrough/README.md § Floorplan frame`; the explicit `elements[]` in declaration order inside
`<section class="elements">`; then the auto-slugged widgets, fenced in
`<!-- auto-slugged --> … <!-- /auto-slugged -->` so derived content stays visibly distinct from
authored content; then the spec reference panel; then a footer linking back to `index.html` and
to every journey this screen appears in.

Each `journey/<id>.html` sets `<body data-spec-journey="<journey_id>">` and renders an `<ol>` of
steps, each with an `Open screen` link and a `Next →` link (the last step points at
`index.html`). A screen missing from disk gets an `<li class="journey-step-missing">` that keeps
its `data-spec-screen` attribute — the annotator can still capture a comment on a screen that
was specified but not written — plus a `missing_screen` warning. Journey sequencing lives
entirely in the journey page: no journey-specific "Next" is injected into a screen page, which
is what lets one screen appear in several journeys cleanly.

## Per-kind rendering

Tags come from the contract's `kind` → DOM tag mapping. What this renderer settles on top of it:

- **`link` / `button` / `image` / `custom` with a `target:`** → a resolved `<a>` (button as
  `<a class="button">`). Without one, the base tag renders inert. An absent `target:` is legal
  and gets no warning.
- **`list`** → `<ul>`, one `<li>` per `items[]` entry carrying its own `data-spec-element`. An
  item's `target:` wraps its label; the list's own `target:` additionally wraps the whole `<ul>`
  — the two wrap independently. Empty or absent `items` renders one placeholder `<li>`. `list`
  items have no `id` field in the schema at all, so the derived-and-provisional path is the
  normal case here, not an edge case.
- **`table`** → `<table>` with `<thead>` from `columns[]` and one `<tr>` per `sample_rows[]`
  entry, cells verbatim in column order. `row_target:` wraps each row's **first cell only**.
  With no `sample_rows`, render the header plus exactly one skeleton row of empty `<td>`s —
  a reviewer reading fabricated sample data cannot tell it from specified data.
- **`tabs`** → `<nav class="tabs">`, first entry `active`, an entry with `target:` as
  `<a class="tab">` and one without as an inert `<span class="tab">`. No JS switching.
- **`input` with `options:`** → `<select>` with one `<option>` per value; without, a plain
  `<input>`.
- Each state in `element.states` beyond `default` renders a small sibling
  `<span class="state-<state>">`, so state coverage is visible on the page.

## Styles the shell block carries

Beyond the token custom properties: `[data-spec-provisional="true"]` as a dashed outline (one
attribute selector covers auto-slugged elements and the generated app nav alike, both being
provisional by definition); `.app-nav` as a flex list; bordered
`.element table`; padded `.element select`; `nav.tabs` with a bottom-border active state; and
`details.spec-panel` bordered and padded, with the native `<details>` collapse doing the work;
`.floorplan-frames` as a wrapping flex row, `.floorplan iframe` bordered, and `.floorplan-notice`
as a dashed amber box.

## The frame files

`floorplan/<screen>.html` files are standalone documents (the rulebook preview with its markup and
`<style>` kept, scripts removed, regions filled) and carry no shell chrome of their own: the
`shell` region lists the app nav links with `target="_top"`, so a click leaves the frame. The
rulebook is read from the installed contract `<contracts>/app-design-rulebook/`; `validator.py --rulebook <dir>` takes the same path and defaults to that contract under the working directory, then to the `rulebook/` of the collection checkout.

## Zero-build is the invariant the validator checks

No JS framework, no bundler artefact, no `<script src="…">` pointing anywhere non-relative.
The whole promise of this renderer is that a stakeholder can open `index.html` from a shared
folder; a single absolute script URL breaks that for everyone offline or behind a proxy, and
`validator.py` fails the run on it.
