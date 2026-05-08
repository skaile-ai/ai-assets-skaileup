# Elements Block — Frontmatter Schema

> **Status:** v0.1 — open for extension. Enums below are proposals; future
> renderer skills MAY propose additions via the normal contract-revision flow.
> See also: `contracts/frontmatter.md`, `lab/validate-elements-block/`.

---

## Scope

This contract defines the optional `elements:` block on screen frontmatter
files at `experience/screens/<group>/<screen>.md`. It is consumed by:

- **Walkthrough renderers** (`walkthrough-mockup-*`) — emit stable HTML
  attributes per element so annotations can survive regenerations.
- **The mockup-feedback cluster** (`mockup-feedback-*`) — anchors annotations
  to specific elements and promotes auto-slugged IDs to explicit ones.

The `elements:` block is **optional**. Absence (or an empty list) triggers
the auto-slug fallback (see *Hybrid ID strategy* below). An empty list
(`elements: []`) and an absent key are semantically identical.

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

---

## Hybrid ID strategy

Reproduced from `REFACTOR_MOCKUP.md` § 6 (auto-slug for fast iteration,
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

v0.1 — open for extension. The closed set:

```
input, button, link, image, text, region, list, form, nav, media, custom
```

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
validator that uses `contracts/scripts/validator_lib.py`). Reference
fixtures live at `tests/elements_block_examples.md` (3 valid, 3 invalid).

Run:

```
python lab/validate-elements-block/validator.py tests/elements_block_examples.md
```

Exit code is `0` when every example matches its declared `expect:`,
otherwise `1` with a `<path>:<line>: <message>` violation report.
