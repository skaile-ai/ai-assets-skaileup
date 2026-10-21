---
path: [_concept/07_screens/]
summary: the app shell and one spec per screen, with the elements block
owner: []
may_propose: []
---

# _concept/07_screens/

The app frame and every screen, one spec per screen. `shell.md` is the frame (`tree/07_screens/shell.md`, written by `experience-shell`); every other screen lives at `<feature_slug>/<screen>.md` (`tree/07_screens/[feature_slug]/[screen].md`, written by `spec-feature`, which is the only writer of screen specs and of their `elements:` blocks). `shell` is a reserved slug: no feature may take it. Directory names under here are slugs — lowercase, hyphenated, no spaces, no numeric prefix.

## Contents

- `shell.md` — the frame; format in `tree/07_screens/shell.md`.
- `<feature_slug>/` — one directory per feature; see `tree/07_screens/[feature_slug]/README.md`.

## The `elements:` block

The optional `elements:` key in a screen's frontmatter is the substance channel for what the screen renders: the walkthrough renderers emit stable HTML attributes per element so annotations survive regeneration, and the feedback skills anchor annotations to elements. `spec-feature` writes the block in every screen spec, covering every interactive or structural thing under `### UI Elements`, `### Actions` and `### Information Displayed`; `experience-shell` writes the `kind: nav` elements in `shell.md`. Nothing else writes it except the id promotion described in `tree/09_mockup/feedback/README.md`.

An absent block and `elements: []` mean the same thing. The renderer's auto-slug fallback is a safety net, not the primary path: renderers never hard-fail on a missing or partial block, so the obligation is the author's, at authoring time — a screen without a block renders as an auto-slugged guess.

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
| `label` | string | yes | human-readable; the on-screen label and the auto-slug seed |
| `states` | list of enum strings | yes | non-empty; each value is in the `states` enum below; should include `default` |
| `provisional` | bool | no | `true` if the id was auto-slugged and not yet promoted; `false` or absent once promoted |
| `describes` | string | no | one-line prose describing the element's role on the screen |
| `data_entity` | string | no | name of a `data_entities[]` entity this element renders or edits |
| `acceptance_refs` | list of strings | no | each entry `<feature-path>#<criterion-id>`, mirroring `story_refs:` |
| `target` | string | no | `screen_id` plus optional `#<element-id>`; valid only on `link`, `button`, `list`, `image`, `custom`; resolves against the rendered screen set, else the renderer records an `unresolved_target` warning |
| `items` | list | no | valid only on `nav`, `tabs`, `list`; entry shape per kind, see Content fidelity |
| `columns` | list of strings | yes, iff `kind: table` | column headers in display order; valid only on `table` |
| `sample_rows` | list of lists of strings | no | `table` only; each row's length equals `len(columns)`; authored fixture data |
| `row_target` | string | no | `table` only; same grammar and resolution as `target`; wraps every row |
| `options` | list of strings | no | `input` only; presence makes the renderer emit a `<select>` with one `<option>` per value |

### Navigation targets

`target` (and a table's `row_target`) points an interactive element at another screen.

- **Identity form.** A target is a `screen_id`: the path stem of a screen file under `07_screens/`, e.g. `11_intake/case_admission_form` for `07_screens/11_intake/case_admission_form.md` — the same identity as `data-spec-screen`, rendered filenames and `screens[].screen_id` in the walkthrough manifest. An optional `#<element-id>` fragment addresses an element on the target screen. A URL path (`/faelle`) or a bare filename is malformed.
- **Valid on** `kind: link | button | list | image | custom` — one element, one destination. A `table` carries `row_target` instead; `nav` and `tabs` carry per-entry destinations through `items[].target`. `target` on any other kind is a validation error.
- **Resolution.** A target is resolvable iff `07_screens/<target-sans-fragment>.md` exists in the set of screens rendered in this walkthrough.
- **Soft-fail.** Renderers never hard-fail on an unresolved target: they emit `href="#"` and record a `warnings[]` entry (`tree/09_mockup/walkthrough/README.md`). A `target` is optional — an interactive element without one renders inert, because not everything navigates.

### Content fidelity

Where a field below is declared, renderers render it as real content; fabrication stays reserved for what is genuinely undeclared.

- **`label` vs `describes`.** `label` is short, literal on-screen UI copy — what a user reads on the button, tab or nav item — and is never the action sentence. The action sentence (`Click "Aufnehmen" on an Anmeldung row → opens the admission form`) goes in `describes:`. This holds for every `label`, including entries inside `items[]`.
- **`items[]` entry shape by kind** — `nav`: `{id?, label, target, icon?}`, every entry needs a destination; `tabs`: `{id?, label, target?}`, an entry without `target` is an inert in-page tab; `list`: `{label, target?}` or a bare string as shorthand for `{label: <string>}` with no target.
- **`table`.** `columns` is the header row. `sample_rows`, when present, renders verbatim. `columns` alone renders the header plus one skeleton row; there is no content to fabricate, so none is invented. `row_target` wraps every row's first cell in a link.
- **`input` + `options`** renders a `<select>`.
- **Authored, never invented.** `sample_rows` and `items` content is fixture data sourced from `seed.json` scenarios or the screen's own wireframe examples; renderers render exactly what is declared.

### ID rules

- kebab-case: lowercase ASCII letters, digits, single hyphens; regex `^[a-z][a-z0-9-]*[a-z0-9]$`, no `--`.
- Unique within a screen.
- Stable across regenerations: once an id is promoted (written into `elements:` with `provisional: false` or omitted), regeneration preserves it, and renaming a promoted id breaks every annotation that references it.

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
    target: 11_intake/case_admission_form       # screen_id, optional "#<element-id>" fragment
    describes: "Click \"Aufnehmen\" on an Anmeldung row → opens the admission form"
  - id: cases-table
    kind: table
    label: "Fälle"
    states: [default, loading, empty]
    columns: ["Patient", "Falltyp", "Status"]
    sample_rows:                                # authored fixtures
      - ["Lena M.", "Teilstationär", "Aktiv"]
      - ["Tom B.", "Ambulant", "Aktiv"]
    row_target: 11_intake/case_detail
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
      - { id: nav-tasks, label: "Aufgaben", target: 20_tasks/task_list, icon: "✓" }
```

## Checks

The renderers reject what they cannot render: a missing `id`, duplicate ids, a `kind` outside the enum, `target` or `items` or `columns` or `sample_rows` or `row_target` or `options` on a kind that does not take it, a malformed `screen_id`, a `sample_rows` row whose length differs from `len(columns)`, and an `items` entry that misses its kind's required fields. The validator is `skills/mockup-walkthrough/references/<renderer>/validator.py`, run as a step of `mockup-walkthrough`; no separate checker covers the block.
