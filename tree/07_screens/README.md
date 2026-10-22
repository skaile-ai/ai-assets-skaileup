---
path: [_concept/07_screens/]
summary: the app shell and one flat spec per screen, with the elements block
owner: []
may_propose: []
---

# _concept/07_screens/

The app frame and every screen, one spec per screen. `shell.md` is the frame (`tree/07_screens/shell.md`, owned by `experience-shell`); every other screen is one flat file `<screen>.md` (`tree/07_screens/[screen].md`), owned by `experience-screen` together with its `elements:` block. `mockup-feedback` is the one other skill that writes a screen, and only as human-approved patches (`tree/07_screens/[screen].md § Patching (mockup-feedback)`). No screen sits in a feature or other directory level. A screen's name is its `screen_id`: the filename stem, lowercase and hyphenated, `^[a-z][a-z0-9-]{1,47}$`, no numeric prefix. `shell` is a reserved name: no screen may take it. Features reference screens, never contain them.

## Contents

- `shell.md` — the frame; format in `tree/07_screens/shell.md`.
- `<screen>.md` — one file per screen; format in `tree/07_screens/[screen].md`.

## The `elements:` block

The optional `elements:` key in a screen's frontmatter is the substance channel for what the screen renders: `mockup-storybook` builds the screen's story from it, and a note left on that story is routed back to the screen spec. `experience-screen` writes the block in every screen spec, covering every interactive or structural thing under `### UI Elements`, `### Actions` and `### Information Displayed`; `experience-shell` writes the `kind: nav` elements in `shell.md`. Nothing else writes it except the id confirmation described in `tree/09_mockup/feedback/README.md`.

An absent block and `elements: []` mean the same thing. A screen without a block gets a story built from its section prose alone, and the story shows only what the prose names, so the obligation to declare every element is the author's, at authoring time.

### Schema

```yaml
elements:                            # OPTIONAL — top-level frontmatter key
  - id: <kebab-case-string>          # REQUIRED — unique within this screen
    kind: <enum>                     # REQUIRED — see kind enum
    label: <string>                  # REQUIRED — human-readable label
    states: [<state>, ...]           # REQUIRED — at least [default]
    # ── optional fields ──
    provisional: <bool>              # OPTIONAL — true if auto-slugged
    describes: <string>              # OPTIONAL — short prose role description
    data_entity: <EntityName>        # OPTIONAL — entity this element renders/edits
    acceptance_refs:                 # OPTIONAL — back-link to feature acceptance
      - <feature-path>#<criterion-id>
    # ── placement ──
    region: <region-id>              # OPTIONAL — a region id of the screen's floorplan
    # ── navigation — link | button | list | image | custom only ──
    target: <screen_id>[#<element-id>]   # OPTIONAL — navigation destination
    # ── content fidelity — kind-gated ──
    items:                           # OPTIONAL — nav | tabs | list only
      - <item>                       # entry shape depends on kind
    columns: [<string>, ...]         # REQUIRED iff kind: table
    sample_rows:                     # OPTIONAL — table only
      - [<string>, ...]              # len(row) == len(columns)
    row_target: <screen_id>[#<element-id>]  # OPTIONAL — table only
    options: [<string>, ...]         # OPTIONAL — input only, ⇒ renders <select>
```

### Field reference

| Field | Type | Required | Constraints |
|---|---|---|---|
| `id` | string | yes | kebab-case, matches `^[a-z][a-z0-9-]*[a-z0-9]$`, no `--`, unique within the screen |
| `kind` | enum string | yes | one of the `kind` enum below |
| `label` | string | yes | human-readable; the on-screen label |
| `states` | list of enum strings | yes | non-empty; each value is in the `states` enum below; should include `default` |
| `provisional` | bool | no | `true` while the id is a first guess nobody has confirmed; `false` or absent once confirmed |
| `describes` | string | no | one-line prose describing the element's role on the screen |
| `data_entity` | string | no | the id of a `model.ts` entity this element renders or edits |
| `region` | string | no | a region id from the `§ Regions` of the screen's `floorplan:`; the screen story places the element inside that region of the floorplan, and an element without it goes to the floorplan's main region. In `shell.md` it is a region id of the shell frame |
| `acceptance_refs` | list of strings | no | each entry `<feature-path>#<criterion-id>`, mirroring `story_refs:` |
| `target` | string | no | `screen_id` plus optional `#<element-id>`; valid only on `link`, `button`, `list`, `image`, `custom`; resolves against the screens that exist under `07_screens/`, else the story renders the element inert |
| `items` | list | no | valid only on `nav`, `tabs`, `list`; entry shape per kind, see Content fidelity |
| `columns` | list of strings | yes, iff `kind: table` | column headers in display order; valid only on `table` |
| `sample_rows` | list of lists of strings | no | `table` only; each row's length equals `len(columns)`; authored fixture data |
| `row_target` | string | no | `table` only; same grammar and resolution as `target`; wraps every row |
| `options` | list of strings | no | `input` only; presence makes the story render a select with one option per value |

### Navigation targets

`target` (and a table's `row_target`) points an interactive element at another screen.

- **Identity form.** A target is a `screen_id`: the filename stem of a screen under `07_screens/`, e.g. `case-admission-form` for `07_screens/case-admission-form.md` — the same identity as the route of its component under `src/screens/` and the `data-screen` attribute in the Storybook package. An optional `#<element-id>` fragment addresses an element on the target screen. A URL path (`/faelle`), a bare filename or a path with a directory is malformed.
- **Valid on** `kind: link | button | list | image | custom` — one element, one destination. A `table` carries `row_target` instead; `nav` and `tabs` carry per-entry destinations through `items[].target`. `target` on any other kind is a validation error.
- **Resolution.** A target is resolvable iff `07_screens/<target-sans-fragment>.md` exists.
- **Soft-fail.** An unresolved target renders as an inert element in the story and is listed in the screen step's report. A `target` is optional — an interactive element without one stays inert, because not everything navigates.

### Content fidelity

Where a field below is declared, the story renders it as real content; fabrication stays reserved for what is genuinely undeclared.

- **`label` vs `describes`.** `label` is short, literal on-screen UI copy — what a user reads on the button, tab or nav item — and is never the action sentence. The action sentence (`Click "Aufnehmen" on an Anmeldung row → opens the admission form`) goes in `describes:`. This holds for every `label`, including entries inside `items[]`.
- **`items[]` entry shape by kind** — `nav`: `{id?, label, target, icon?}`, every entry needs a destination; `tabs`: `{id?, label, target?}`, an entry without `target` is an inert in-page tab; `list`: `{label, target?}` or a bare string as shorthand for `{label: <string>}` with no target.
- **`table`.** `columns` is the header row. `sample_rows`, when present, renders verbatim. `columns` alone renders the header plus one skeleton row; there is no content to fabricate, so none is invented. `row_target` makes every row's first cell navigate.
- **`input` + `options`** renders a select.
- **Authored, never invented.** `sample_rows` and `items` content is fixture data sourced from `seed.ts` scenarios or the screen's own `### Template Data`; the story renders exactly what is declared.

### ID rules

- kebab-case: lowercase ASCII letters, digits, single hyphens; regex `^[a-z][a-z0-9-]*[a-z0-9]$`, no `--`.
- Unique within a screen.
- Stable across edits: once an id is confirmed (written into `elements:` with `provisional: false` or omitted), later edits preserve it, and renaming a confirmed id breaks every story, play function and note that references it.

### `kind` enum

```
input, button, link, image, text, region, list, form, nav, media, custom, table, tabs
```

Use `custom` only when no other value fits; propose an extension to this enum over reaching for it — `table` and `tabs` are exactly that case, a shape distinct enough to name.

### `states` enum

```
default, focus, hover, active, disabled, loading, error, success, empty
```

Every element should include `default`; other states are added as the screen needs them.

### Example

```yaml
elements:
  - id: open-admission-form
    kind: button
    label: "Aufnehmen"                          # on-screen copy, never the action sentence
    states: [default, loading, disabled, error]
    data_entity: Case
    acceptance_refs: [05_features/intake/admission.md#AC-admission-02]
    target: case-admission-form                 # screen_id, optional "#<element-id>" fragment
    describes: "Click \"Aufnehmen\" on an Anmeldung row → opens the admission form"
  - id: cases-table
    kind: table
    label: "Fälle"
    states: [default, loading, empty]
    columns: ["Patient", "Falltyp", "Status"]
    sample_rows:                                # authored fixtures
      - ["Lena M.", "Teilstationär", "Aktiv"]
      - ["Tom B.", "Ambulant", "Aktiv"]
    row_target: case-detail
  - id: filter-area
    kind: input
    label: "Bereich"
    states: [default]
    options: ["Alle", "Kindergruppe", "Jugendgruppe"]   # presence ⇒ <select>
  - id: main-nav
    kind: nav
    label: "Hauptnavigation"
    states: [default]
    items:
      - { id: nav-tasks, label: "Aufgaben", target: task-list, icon: "✓" }
```

## Checks

A block holds when no element misses its `id`, no id repeats, every `kind` is in the enum, `target`, `items`, `columns`, `sample_rows`, `row_target` and `options` appear only on the kinds that take them, every `screen_id` is well formed, every `sample_rows` row has `len(columns)` cells, and every `items` entry carries its kind's required fields. No separate checker covers the block, so the author reads it back once before saving.
