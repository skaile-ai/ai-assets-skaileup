# Elements Block — Frontmatter Schema

> **Status:** v0.3 — adds navigation targets + content-fidelity shapes
> (2026-07-05 merged mockup plan). Enums below are proposals; future
> renderer skills MAY propose additions via the normal contract-revision flow.
> See also: `contracts/frontmatter.md`, `lab/validate-elements-block/`,
> `contracts/walkthrough_renderer.md` (the renderer-side contract that
> consumes `target`/`items`/`columns`/`sample_rows`/`row_target`/`options`).

---

## Scope

This contract defines the optional `elements:` block on screen frontmatter
files at `experience/screens/<group>/<screen>.md`. It is consumed by:

- **Walkthrough renderers** (`mockup-walkthrough-*`) — emit stable HTML
  attributes per element so annotations can survive regenerations.
- **The mockup-feedback cluster** (`mockup-feedback-*`) — anchors annotations
  to specific elements and promotes auto-slugged IDs to explicit ones.

The `elements:` block is **optional** for hand-written screens. Absence (or
an empty list) triggers the auto-slug fallback (see *Hybrid ID strategy*
below). An empty list (`elements: []`) and an absent key are semantically
identical.

That fallback is a **safety net, not the primary path.** The
`experience-screens` skill (`skaileup/03_experience/03_screens/SKILL.md`)
treats an explicit `elements:` block as a hard MUST at depth `medium`/`max`
(exempt at `light`/`none`, matching the existing `### Wireframe` MUST
precedent), covering every interactive or structural thing named in
`### UI Elements`, `## Actions`, and `## Information Displayed` — including
`target:` for every action that names a destination screen. Renderers still
never hard-fail on a missing or partial block; the MUST lives at authoring
time, not render time.

---

## Schema

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
    # ── content fidelity — kind-gated, see § Content fidelity ──
    items:                           # OPTIONAL — nav | tabs | list only
      - <item>                       # entry shape depends on kind
    columns: [<string>, ...]         # REQUIRED iff kind: table
    sample_rows:                     # OPTIONAL — table only
      - [<string>, ...]              # len(row) == len(columns)
    row_target: <screen_id>[#<element-id>]  # OPTIONAL — table only
    options: [<string>, ...]         # OPTIONAL — input only, ⇒ renders <select>
```

---

## Field reference

| Field | Type | Required | Constraints |
|---|---|---|---|
| `id` | string | yes | kebab-case, matches `^[a-z][a-z0-9-]*[a-z0-9]$`, no `--`, unique within the screen |
| `kind` | enum string | yes | one of the values in the `kind` enum below |
| `label` | string | yes | human-readable; used as the on-screen label and as the auto-slug seed |
| `states` | list of enum strings | yes | non-empty; each value is in the `states` enum below; SHOULD include `default` |
| `provisional` | bool | no | `true` if the ID was auto-slugged and not yet promoted; `false` (or absent) once promoted |
| `describes` | string | no | one-line prose describing the element's role on the screen |
| `data_entity` | string | no | name of a `data_entities[]` entity this element renders or edits |
| `acceptance_refs` | list of strings | no | each entry is `<feature-path>#<criterion-id>`, mirroring the `story_refs:` convention |
| `target` | string | no | `screen_id` (path stem under `experience/screens/`) plus optional `#<element-id>` fragment; valid only when `kind` is `link`, `button`, `list`, `image`, or `custom`; MUST resolve against the rendered screen set, or the renderer records an `unresolved_target` warning — see § Navigation targets |
| `items` | list | no | valid only when `kind` is `nav`, `tabs`, or `list`; entry shape depends on `kind` — see § Content fidelity |
| `columns` | list of strings | yes, iff `kind: table` | column headers, in display order; valid only when `kind: table` |
| `sample_rows` | list of lists of strings | no | `table` only; each row's length MUST equal `len(columns)`; authored fixture data, never renderer-invented — see § Content fidelity |
| `row_target` | string | no | `table` only; same grammar and resolution rule as `target`; wraps every row |
| `options` | list of strings | no | `input` only; presence signals the renderer to emit a `<select>` with one `<option>` per value instead of a plain `<input>` |

---

## Navigation targets

The `target` field (and a table's `row_target`) points an interactive
element at another screen.

**Identity form.** A target is a `screen_id` — the path stem of a screen
file under `experience/screens/`, e.g. `11_intake/case_admission_form` for
`experience/screens/11_intake/case_admission_form.md`. This is the same
identity used by `data-spec-screen`, rendered filenames, and
`screens[].screen_id` in the walkthrough manifest. An optional
`#<element-id>` fragment addresses a specific element on the target screen.
A `target` is never a URL path (`/faelle`) or a bare filename — both are
malformed.

**Valid on.** `target` is meaningful only on `kind: link | button | list |
image | custom` (the "one element, one destination" kinds). `kind: table`
gets its own destination field, `row_target`, instead of a bare `target`
(see § Content fidelity). Declaring `target` on any other kind (`input`,
`text`, `region`, `form`, `nav`, `tabs`, `media`, `table`) is a validation
error — `nav` and `tabs` carry per-entry destinations through
`items[].target` instead of a single scalar `target`.

**Resolution rule.** From `screen/<gA>/<nA>.html`, a target `gB/nB` renders
`href="../<gB>/<nB>.html"` (plus `#<fragment>` when present); from
`index.html`, `href="screen/<gB>/<nB>.html"`. A target is resolvable iff
`experience/screens/<target-sans-fragment>.md` exists in the set of screens
actually rendered in this walkthrough.

**Soft-fail contract.** Renderers never hard-fail on an unresolved target.
When `target` doesn't resolve, the renderer emits `href="#"` and records a
`warnings[]` entry of `kind: "unresolved_target"` (see
`contracts/walkthrough_renderer.md`). Absence of `target` on an interactive
element is legal and renders inert — not everything navigates.

---

## Content fidelity

The `elements:` block is the **substance channel** for a screen's rendered
content, not just a registry of interaction ids. Where a field below is
declared, renderers MUST render it as real content, not a placeholder —
fabrication stays reserved for what's genuinely undeclared (see the
`table` skeleton-row rule below).

**Label vs. `describes`.** `label` is short, literal on-screen UI copy —
what a user reads on the button, tab, or nav item — and is **never** the
action sentence. The action sentence (e.g. `Click "Aufnehmen" on an
Anmeldung row → opens the admission form`) belongs in `describes:`. This
rule applies to every `label`, including entries inside `items[]`.

**`items[]` entry shape is kind-dependent** — one field, one resolution
rule, one auto-slug-id rule, no parallel field names per kind:

- `kind: nav` — `{id?, label, target, icon?}` — persistent/app-shell
  navigation; every entry needs a destination.
- `kind: tabs` — `{id?, label, target?}` — `target` is optional since tabs
  may be purely in-page (an entry without `target` renders as an inert
  `<span>`, not a link).
- `kind: list` — `{label, target?}`, or a bare string as shorthand for
  `{label: <string>}` with no target.

Every `items[]` entry's `label` follows the label-vs-`describes` rule above.

**`table` fields.** `columns` (required) is the header row, in display
order. `sample_rows`, when present, is content: each row renders verbatim
and its length MUST equal `len(columns)`. `columns` with no `sample_rows`
renders the header plus one skeleton row — there is no content to
fabricate, so the renderer doesn't invent any. `row_target`, when present,
wraps every row's first cell in a link to that destination.

**`input` + `options`.** Presence of `options` signals the renderer to emit
a `<select>` with one `<option>` per value instead of a plain `<input>`.

**Authored, never invented.** `sample_rows` and `items` content is authored
fixture data — sourced from `seed.json` scenarios or the screen's own
wireframe examples — never invented by a renderer. Renderers render exactly
what's declared; they do not backfill plausible-looking rows or items.

---

## Hybrid ID strategy

Reproduced from `docs/devlog/mockup-design.md` § 6 (auto-slug for fast iteration,
promote to explicit on first annotation):

1. **Initial render.** Walkthrough auto-slugs IDs from labels/text. Marks
   all IDs `provisional`.
2. **First annotation on a provisional element.** `mockup-feedback-triage`
   prompts to promote the ID to explicit. The promoted ID gets written
   into the screen's `elements:` frontmatter via patch.
3. **Subsequent renders.** Use the promoted ID, no longer provisional.
   Future regeneration of the screen preserves the ID.

This avoids upfront tedium AND ID instability across regenerations.

---

## Renderer contract

Walkthrough renderers MUST emit the following HTML data attributes:

- `data-spec-screen="<screen-path>"` on the screen root element.
- `data-spec-element="<element-id>"` on every annotatable node.
- `data-spec-provisional="true"` when the ID was auto-slugged (i.e. no
  explicit `elements:` entry exists, or the matching entry has
  `provisional: true`).

The screen path in `data-spec-screen` is the repo-relative path to the
screen markdown file (e.g. `experience/screens/01_user_auth/login.md`).

---

## ID rules

- **kebab-case.** Lowercase ASCII letters, digits, single hyphens.
  Regex: `^[a-z][a-z0-9-]*[a-z0-9]$`. No consecutive hyphens (`--`).
- **Unique within a screen.** Two elements on the same screen MUST NOT
  share an `id`.
- **Stable across regenerations.** Once an ID is promoted (i.e. written
  into `elements:` with `provisional: false` or omitted), regeneration
  MUST preserve it. Renaming a promoted ID is a breaking change for any
  annotations referencing it.

---

## `kind` enum

v0.3 — open for extension. The closed set:

```
input, button, link, image, text, region, list, form, nav, media, custom,
table, tabs
```

`table` and `tabs` (added in v0.3) are themselves the "propose an extension
over reaching for `custom`" case the original v0.1 note anticipated: a
table of real rows or a tab bar is a distinct enough shape to name, not a
`custom` div.

Use `custom` only when no other value fits; prefer proposing an extension
to this enum over reaching for `custom`.

---

## `states` enum

v0.1 — open for extension. The closed set:

```
default, focus, hover, active, disabled, loading, error, success, empty
```

Every element SHOULD include `default` in its `states:` list. Other
states are added as the screen needs them.

---

## Examples

### Explicit `elements:` entry (promoted)

```yaml
elements:
  - id: submit-button
    kind: button
    label: "Sign in"
    states: [default, loading, disabled, error]
    data_entity: User
    acceptance_refs:
      - experience/features/01_user_auth/login.md#AC-2
```

### Explicit `elements:` entry with `target:` (in-screen navigation)

`kind: link | button | list | image | custom` — one element, one
destination:

```yaml
elements:
  - id: open-admission-form
    kind: button
    label: "Aufnehmen"                          # on-screen UI copy — never the action sentence
    states: [default]
    target: 11_intake/case_admission_form        # screen_id, optional "#<element-id>" fragment
    describes: "Click \"Aufnehmen\" on an Anmeldung row → opens the admission form"
```

### `kind: nav` with `items` (app-shell / persistent nav)

```yaml
elements:
  - id: sidebar-nav
    kind: nav
    label: "Hauptnavigation"
    states: [default]
    items:
      - id: nav-tasks
        label: "Aufgaben"
        target: 20_tasks/task_list
        icon: "✓"
```

### `kind: tabs`

```yaml
elements:
  - id: case-tabs
    kind: tabs
    label: "Fälle & Aufnahmen Tabs"
    states: [default]
    items:
      - label: "Aufzunehmen"     # first item renders active; target optional (tabs may be in-page)
      - label: "Fälle"
```

### `kind: list` with `items`

`{label, target?}`, or a bare string shorthand for `{label: <string>}`
with no target:

```yaml
elements:
  - id: quick-links
    kind: list
    label: "Schnellzugriff"
    states: [default]
    items:
      - label: "Fälle"
        target: 11_intake/case_list
      - "Berichte"           # bare string shorthand — {label: "Berichte"}, no target
```

### `kind: table` with `sample_rows`

```yaml
elements:
  - id: faelle-table
    kind: table
    label: "Fälle"
    states: [default, loading, empty]
    data_entity: cases
    columns: ["Patient", "Falltyp", "Bereich", "Status", "Aufgenommen"]
    sample_rows:                        # authored fixtures — renderers never invent
      - ["Lena M.", "Teilstationär", "Kindergruppe", "Aktiv", "15.06.2026"]
      - ["Tom B.", "Ambulant", "Jugendgruppe", "Aktiv", "03.06.2026"]
    row_target: 11_intake/case_detail   # optional — every row links here
```

### `kind: input` with `options`

```yaml
elements:
  - id: filter-bereich
    kind: input
    label: "Bereich"
    states: [default]
    options: ["Alle", "Kindergruppe", "Jugendgruppe"]   # presence ⇒ render <select>
```

### Auto-slugged provisional rendering

When a screen file has no `elements:` block (or the block omits an
element actually present in the rendered walkthrough), the renderer
auto-slugs from the visible label and emits:

```html
<button
  data-spec-screen="experience/screens/01_user_auth/login.md"
  data-spec-element="sign-in"
  data-spec-provisional="true">
  Sign in
</button>
```

On the first annotation, `mockup-feedback-triage` prompts the user to
promote `sign-in` to an explicit entry; the patch writes it into
frontmatter and subsequent renders drop `data-spec-provisional`.

---

## Validation

The schema is enforced by `lab/validate-elements-block/` (a Python
validator that uses `contracts/scripts/validator_lib.py`, shipped in the
sister repo `ai-assets-skill-development`). Reference fixtures live at
`skaileup/contracts/tests/elements_block_examples.md` (9 valid, 11 invalid —
the original 3 valid/3 invalid set plus 6 new valid/8 new invalid v0.3
examples covering `target`/`items`/`table`/`tabs`/`options`).

Run:

```
python lab/validate-elements-block/validator.py skaileup/contracts/tests/elements_block_examples.md
```

Exit code is `0` when every example matches its declared `expect:`,
otherwise `1` with a `<path>:<line>: <message>` violation report.

**New invalid cases (v0.3).** In addition to the existing checks (missing
`id`, duplicate `id`s, `kind` outside the enum), the schema now also rejects:

- **`target` on a non-interactive kind** — `target` declared on anything
  other than `link`, `button`, `list`, `image`, or `custom`.
- **`items` on a non-`nav`/`tabs`/`list` kind** — `items` declared on any
  other `kind`.
- **Malformed `screen_id`** — a `target` (or `row_target`) that isn't a
  bare `screen_id` (+ optional `#fragment`), e.g. a URL-style path
  (`/faelle`) or a filename with an extension.
- **`columns` on a non-`table` kind.**
- **`sample_rows` length mismatch** — any row whose length differs from
  `len(columns)`.
- **`sample_rows`/`row_target` on a non-`table` kind** — either field
  declared on anything other than `kind: table`.
- **`options` on a non-`input` kind.**
- **`items` entry shape mismatch for its `kind`** — e.g. a `nav` entry
  missing `target`, or any `items` entry missing `label`.

**Cross-repo follow-up.** `lab/validate-elements-block` (in the sister repo
`ai-assets-skill-development`) implements the v0.1 checks only as of this
writing; it needs a matching v0.3 update to enforce the cases above. That
update is **not executed as part of this contract change** — it's tracked
as a follow-up in the sister repo. This repo's fixtures and CI are
unaffected in the meantime, since the validator itself ships elsewhere.
