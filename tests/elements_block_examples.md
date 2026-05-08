# `elements:` Block — Validation Examples

> Consumed by `lab/validate-elements-block` (validator.py).
> Each example is a fenced YAML block preceded by a sentinel comment of the form
> `<!-- example: <name> · expect: valid|invalid -->`.
>
> Schema: see `contracts/elements_block.md`.

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
