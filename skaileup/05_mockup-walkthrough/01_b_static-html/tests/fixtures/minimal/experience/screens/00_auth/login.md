---
implements:
  - experience/features/00_auth/login.md
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
      - experience/features/00_auth/login.md#AC-1
  - id: go-register
    kind: link
    label: "Create an account"
    states: [default]
    target: 00_auth/register
    describes: "Click \"Create an account\" → opens the registration screen"
  - id: recent-signins
    kind: table
    label: "Recent sign-ins"
    states: [default, loading, empty]
    data_entity: User
    columns: ["Name", "Email", "Last sign-in"]
    sample_rows:
      - ["Lena M.", "lena@example.com", "2026-07-05"]
      - ["Tom B.", "tom@example.com", "2026-07-04"]
    row_target: 00_auth/verify_email
  - id: filter-role
    kind: input
    label: "Role"
    states: [default]
    options: ["All", "Admin", "User"]
last_updated: 2026-07-06
---

# Login

The user signs in with email and password. When they submit valid credentials, they land on the dashboard (see AC-1 in the login feature spec).
