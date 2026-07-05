# Walkthrough Renderer Contract

**schema_version: "1.0"** · Owner of everything shared by the four
`mockup-walkthrough-*` renderers: `static-html` (reference implementation),
`astro`, `lit`, `framework`. Each renderer's SKILL.md owns ONLY its
technology-specific scaffold (build setup, templates, config) and cites this
file for the behaviour below. The `mockup-feedback-*` cluster resolves clicks
identically across renderers because of this contract.

**Change policy.** Pinned. Do not change any table, field name, or warning
kind without a coordinated update to `mockup-feedback-annotate` and a
`schema_version` bump.

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

## Auto-slug fallback

The renderer's portion of the hybrid ID strategy (`elements_block.md`
§ "Hybrid ID strategy"). When a screen file has no `elements:` block, OR has
a partial one, the renderer MUST:

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
     file. Promotion of provisional ids is `mockup-feedback-triage`'s job.

## Manifest schema

The contract handed to `mockup-feedback-annotate`. Field names pinned exactly.
`<variant>` is the renderer's short name (`static-html`, `astro`, `lit`,
`framework`); `renderer_version` is the renderer SKILL.md's
`metadata.version`.

```json
{
  "schema_version": "1.0",
  "renderer": "mockup-walkthrough-<variant>",
  "renderer_version": "0.1.0",
  "generated_at": "2026-05-07T12:34:56Z",
  "source_root": "experience/screens",
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

- `schema_version`: bump on breaking change. Feedback cluster pins `^1.0`.
- `renderer` / `renderer_version`: identifies which walkthrough variant
  produced the site.
- `generated_at`: ISO-8601 UTC; lets feedback-annotate detect stale renders.
- `source_root`: relative path the screen paths are anchored to (always
  `experience/screens`).
- `screens[].screen_path`: full path with `.md`. Used by feedback-annotate
  when it needs to read the source file.
- `screens[].screen_id`: the path stem `<group>/<name>` (no `.md`); the
  value emitted in `data-spec-screen`.
- `screens[].rendered_html`: site-relative path to the rendered HTML.
- `screens[].elements[].element_id`: the value emitted in
  `data-spec-element`.
- `screens[].elements[].provisional`: `true` when auto-slugged
  (mirrors `data-spec-provisional`).
- `screens[].elements[].source_anchor`: fragment-style pointer back to the
  source file. Explicit ids: `#elements/<element_id>`. Provisional:
  `#auto/<element_id>` (no entry yet in the YAML).
- `journeys[].screen_sequence`: ordered list of screen source paths. Same
  order drives the rendered "Next →" links inside `journey/<id>.html`.
- Sorting: `screens[]` by `screen_path`, `journeys[]` by `journey_id`,
  `features[]` by `feature_path` — deterministic diffs. Write atomically
  (tmp → fsync → rename).

## warnings[].kind enum

`auto_slugged`, `auto_slug_collision`, `missing_layout`, `missing_feature`,
`unknown_element_kind`, `missing_screen`, `missing_screen_sequence`,
`no_journeys`. Renderer-specific additions are allowed and documented in that
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

## Screen-in-multiple-journeys rule

When a screen appears in two or more journeys, each `journey/<id>.html`
retains its own "Next →" link only inside the journey HTML. The screen HTML
itself does NOT embed journey-specific navigation (else screen renders couple
to journey state). Cross-journey continuation is solely owned by
`journey/<id>.html`; the screen's footer may list the journeys it
participates in, linking to the journey pages.

## Shared MUST / NEVER

MUST  emit `data-spec-screen` on every screen `<body>`
MUST  emit `data-spec-element` on every annotatable child node
MUST  emit `data-spec-provisional="true"` on auto-slugged element nodes
MUST  emit `data-spec-journey="<id>"` on every journey `<body>`
MUST  emit `data-spec-index="true"` on `index.html` `<body>`
MUST  write `manifest.json` conforming to `§ Manifest schema` (`schema_version: "1.0"`)
MUST  sort manifest arrays lexicographically (`screens` by `screen_path`, `journeys` by `journey_id`, `features` by `feature_path`)
MUST  HTML-escape every interpolated string (labels, ids, paths, titles) including quotes

NEVER  emit `data-spec-*` attributes outside the pinned table
NEVER  mutate source files (`experience/screens/**`, `experience/journeys/stories.yaml`, `design/tokens.json`, `experience/features/**`) — renderers are read-only on inputs
NEVER  inject journey-step navigation into `screen/**/*.html` — cross-journey continuation lives only in `journey/<id>.html`
NEVER  inline absolute filesystem paths into `manifest.json` — repo-relative paths only
