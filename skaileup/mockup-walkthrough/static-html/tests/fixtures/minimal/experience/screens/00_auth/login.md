---
implements:
  - product-spec/features/00_auth/login.md
data_entities: [User]
layout: experience/screens/00_layout/shell.md
elements:
  - id: email-input
    kind: input
    label: "Email"
    states: [default, focus, error]
    data_entity: User
  - id: password-input
    kind: input
    label: "Password"
    states: [default, focus, error]
    data_entity: User
  - id: submit-button
    kind: button
    label: "Sign in"
    states: [default, loading, disabled, error]
    data_entity: User
    acceptance_refs:
      - product-spec/features/00_auth/login.md#AC-1
last_updated: 2026-05-08
---

# Login

The user signs in with email and password.

## Acceptance criteria

- AC-1: When the user submits valid credentials, they land on the dashboard.
