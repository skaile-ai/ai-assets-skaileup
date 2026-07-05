# `elements:` Block — Validation Examples

> Consumed by `lab/validate-elements-block` (validator.py).
> Each example is a fenced YAML block preceded by a sentinel comment of the form
> `<!-- example: <name> · expect: valid|invalid -->`.
>
> Schema: see `contracts/elements_block.md`.
>
> **Counts:** 9 valid, 11 invalid — the original set (3 valid, 3 invalid) plus
> 6 new valid / 8 new invalid v0.3 examples covering
> `target`/`items`/`table`/`tabs`/`options` (2 more than the initial 5/7 plan:
> a `list` + `items` valid case and a `sample_rows`/`row_target`-on-non-`table`
> invalid case were folded in during review — see `elements_block.md` § Content
> fidelity and § Validation).
>
> **Cross-repo follow-up:** `lab/validate-elements-block` (in the sister repo
> `ai-assets-skill-development`) implements the v0.1 checks only as of this
> writing; it needs a matching v0.3 update before the new examples below pass
> there. That update is out of scope for this repo — this repo's fixtures and
> CI are unaffected in the meantime, since the validator itself ships
> elsewhere.

## Valid examples

<!-- example: full-login · expect: valid -->
```yaml
implements:
  - experience/features/01_user_auth/login.md
data_entities: [User]
layout: experience/screens/00_layout/shell.md
elements:
  - id: email-input
    kind: input
    label: "Email"
    states: [default, focus, error]
  - id: password-input
    kind: input
    label: "Password"
    states: [default, focus, error]
  - id: submit-button
    kind: button
    label: "Sign in"
    states: [default, loading, disabled, error]
last_updated: 2026-05-06
```

<!-- example: minimal-single-element · expect: valid -->
```yaml
implements:
  - experience/features/02_dashboard/overview.md
data_entities: [User]
layout: experience/screens/00_layout/shell.md
elements:
  - id: header
    kind: text
    label: "Welcome"
    states: [default]
last_updated: 2026-05-07
```

<!-- example: with-optional-fields · expect: valid -->
```yaml
implements:
  - experience/features/01_user_auth/login.md
data_entities: [User]
layout: experience/screens/00_layout/shell.md
elements:
  - id: email-input
    kind: input
    label: "Email"
    states: [default, focus, error]
    provisional: true
    describes: "Primary identifier the user types to authenticate"
    data_entity: User
    acceptance_refs:
      - experience/features/01_user_auth/login.md#AC-1
  - id: submit-button
    kind: button
    label: "Sign in"
    states: [default, loading, disabled]
    describes: "Submits the credential pair to the auth endpoint"
    acceptance_refs:
      - experience/features/01_user_auth/login.md#AC-2
      - experience/features/01_user_auth/login.md#AC-3
last_updated: 2026-05-07
```

<!-- example: with-target · expect: valid -->
```yaml
implements:
  - experience/features/11_intake/anmeldungen.md
data_entities: [Case]
layout: experience/screens/00_layout/shell.md
elements:
  - id: open-admission-form
    kind: button
    label: "Aufnehmen"
    states: [default]
    target: 11_intake/case_admission_form
    describes: "Click \"Aufnehmen\" on an Anmeldung row → opens the admission form"
  - id: view-case-detail
    kind: link
    label: "Details ansehen"
    states: [default]
    target: 11_intake/case_detail#patient-summary
    describes: "Click \"Details ansehen\" → opens the case detail screen, scrolled to the patient summary"
last_updated: 2026-07-05
```

<!-- example: nav-with-items · expect: valid -->
```yaml
implements:
  - experience/features/00_layout/navigation.md
data_entities: [User]
layout: experience/screens/00_layout/shell.md
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
      - id: nav-cases
        label: "Fälle"
        target: 11_intake/case_list
last_updated: 2026-07-05
```

<!-- example: tabs-two-items · expect: valid -->
```yaml
implements:
  - experience/features/11_intake/anmeldungen.md
data_entities: [Case]
layout: experience/screens/00_layout/shell.md
elements:
  - id: case-tabs
    kind: tabs
    label: "Fälle & Aufnahmen Tabs"
    states: [default]
    items:
      - label: "Aufzunehmen"
      - label: "Fälle"
        target: 11_intake/case_list
last_updated: 2026-07-05
```

<!-- example: table-with-sample-rows · expect: valid -->
```yaml
implements:
  - experience/features/11_intake/anmeldungen.md
data_entities: [Case]
layout: experience/screens/00_layout/shell.md
elements:
  - id: faelle-table
    kind: table
    label: "Fälle"
    states: [default, loading, empty]
    data_entity: cases
    columns: ["Patient", "Falltyp", "Bereich", "Status", "Aufgenommen"]
    sample_rows:
      - ["Lena M.", "Teilstationär", "Kindergruppe", "Aktiv", "15.06.2026"]
      - ["Tom B.", "Ambulant", "Jugendgruppe", "Aktiv", "03.06.2026"]
    row_target: 11_intake/case_detail
last_updated: 2026-07-05
```

<!-- example: input-with-options · expect: valid -->
```yaml
implements:
  - experience/features/11_intake/anmeldungen.md
data_entities: [Case]
layout: experience/screens/00_layout/shell.md
elements:
  - id: filter-bereich
    kind: input
    label: "Bereich"
    states: [default]
    options: ["Alle", "Kindergruppe", "Jugendgruppe"]
last_updated: 2026-07-05
```

<!-- example: list-with-items · expect: valid -->
```yaml
implements:
  - experience/features/00_layout/navigation.md
data_entities: [Case]
layout: experience/screens/00_layout/shell.md
elements:
  - id: quick-links
    kind: list
    label: "Schnellzugriff"
    states: [default]
    items:
      - label: "Fälle"
        target: 11_intake/case_list
      - "Berichte"
last_updated: 2026-07-05
```

## Invalid examples

<!-- example: missing-id · expect: invalid · reason: id field required -->
```yaml
implements:
  - experience/features/01_user_auth/login.md
data_entities: [User]
layout: experience/screens/00_layout/shell.md
elements:
  - id: email-input
    kind: input
    label: "Email"
    states: [default, focus, error]
  - kind: input
    label: "Password"
    states: [default, focus, error]
last_updated: 2026-05-06
```

<!-- example: duplicate-ids · expect: invalid · reason: ids must be unique within a screen -->
```yaml
implements:
  - experience/features/01_user_auth/login.md
data_entities: [User]
layout: experience/screens/00_layout/shell.md
elements:
  - id: email-input
    kind: input
    label: "Email"
    states: [default, focus, error]
  - id: email-input
    kind: input
    label: "Confirm email"
    states: [default, focus, error]
last_updated: 2026-05-06
```

<!-- example: bad-kind-enum · expect: invalid · reason: kind must be from the kind enum -->
```yaml
implements:
  - experience/features/01_user_auth/login.md
data_entities: [User]
layout: experience/screens/00_layout/shell.md
elements:
  - id: mystery-thing
    kind: widget
    label: "Mystery"
    states: [default]
last_updated: 2026-05-06
```

<!-- example: target-on-input · expect: invalid · reason: target valid only on kind: link | button | list | image | custom -->
```yaml
implements:
  - experience/features/11_intake/anmeldungen.md
data_entities: [Case]
layout: experience/screens/00_layout/shell.md
elements:
  - id: filter-bereich
    kind: input
    label: "Bereich"
    states: [default]
    target: 11_intake/case_list
last_updated: 2026-07-05
```

<!-- example: items-on-button · expect: invalid · reason: items valid only on kind: nav | tabs | list -->
```yaml
implements:
  - experience/features/11_intake/anmeldungen.md
data_entities: [Case]
layout: experience/screens/00_layout/shell.md
elements:
  - id: open-admission-form
    kind: button
    label: "Aufnehmen"
    states: [default]
    items:
      - label: "Aufzunehmen"
last_updated: 2026-07-05
```

<!-- example: malformed-target · expect: invalid · reason: target must be a bare screen_id (+ optional #fragment), never a URL-style path -->
```yaml
implements:
  - experience/features/11_intake/anmeldungen.md
data_entities: [Case]
layout: experience/screens/00_layout/shell.md
elements:
  - id: open-admission-form
    kind: button
    label: "Aufnehmen"
    states: [default]
    target: /faelle
last_updated: 2026-07-05
```

<!-- example: columns-on-list · expect: invalid · reason: columns valid only on kind: table -->
```yaml
implements:
  - experience/features/00_layout/navigation.md
data_entities: [Case]
layout: experience/screens/00_layout/shell.md
elements:
  - id: quick-links
    kind: list
    label: "Schnellzugriff"
    states: [default]
    columns: ["Name", "Status"]
last_updated: 2026-07-05
```

<!-- example: sample-row-length-mismatch · expect: invalid · reason: every sample_rows row length must equal len(columns) -->
```yaml
implements:
  - experience/features/11_intake/anmeldungen.md
data_entities: [Case]
layout: experience/screens/00_layout/shell.md
elements:
  - id: faelle-table
    kind: table
    label: "Fälle"
    states: [default]
    columns: ["Patient", "Falltyp", "Bereich", "Status", "Aufgenommen"]
    sample_rows:
      - ["Lena M.", "Teilstationär", "Kindergruppe", "Aktiv", "15.06.2026"]
      - ["Tom B.", "Ambulant", "Jugendgruppe"]
last_updated: 2026-07-05
```

<!-- example: options-on-button · expect: invalid · reason: options valid only on kind: input -->
```yaml
implements:
  - experience/features/11_intake/anmeldungen.md
data_entities: [Case]
layout: experience/screens/00_layout/shell.md
elements:
  - id: open-admission-form
    kind: button
    label: "Aufnehmen"
    states: [default]
    options: ["Alle", "Kindergruppe"]
last_updated: 2026-07-05
```

<!-- example: items-bad-shape-on-tabs · expect: invalid · reason: every items entry requires a label, which is missing here -->
```yaml
implements:
  - experience/features/11_intake/anmeldungen.md
data_entities: [Case]
layout: experience/screens/00_layout/shell.md
elements:
  - id: case-tabs
    kind: tabs
    label: "Fälle & Aufnahmen Tabs"
    states: [default]
    items:
      - target: 11_intake/case_list
last_updated: 2026-07-05
```

<!-- example: sample-rows-on-non-table · expect: invalid · reason: sample_rows/row_target valid only on kind: table -->
```yaml
implements:
  - experience/features/00_layout/navigation.md
data_entities: [Case]
layout: experience/screens/00_layout/shell.md
elements:
  - id: quick-links
    kind: list
    label: "Schnellzugriff"
    states: [default]
    sample_rows:
      - ["Fälle", "11_intake/case_list"]
last_updated: 2026-07-05
```
