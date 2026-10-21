---
screen_id: login
title: Login
implements:
  - 05_features/auth/login.md
floorplan: wizard
posture: transient
density: comfortable
regions:
  step-body: { shows: user, representation: page }
  step-help: { shows: user, representation: peek }
tier_overrides:
  - { object: user, attribute: email, tier: 1, region: step-body, reason: "identifies the account being signed in" }
elements:
  - id: email-input
    kind: input
    region: step-body
    label: "Email"
    states: [default, focus, error]
    data_entity: User
  - id: password-input
    kind: input
    region: step-body
    label: "Password"
    states: [default, focus, error]
    data_entity: User
  - id: submit-button
    kind: button
    region: footer
    label: "Sign in"
    states: [default, loading, disabled, error]
    data_entity: User
    acceptance_refs:
      - 05_features/auth/login.md#AC-1
  - id: go-register
    kind: link
    region: step-help
    label: "Create an account"
    states: [default]
    target: register
    describes: "Click \"Create an account\" → opens the registration screen"
  - id: recent-signins
    kind: table
    region: step-body
    label: "Recent sign-ins"
    states: [default, loading, empty]
    data_entity: User
    columns: ["Name", "Email", "Last sign-in"]
    sample_rows:
      - ["Lena M.", "lena@example.com", "2026-07-05"]
      - ["Tom B.", "tom@example.com", "2026-07-04"]
    row_target: verify-email
  - id: filter-role
    kind: input
    region: step-body
    label: "Role"
    states: [default]
    options: ["All", "Admin", "User"]
last_updated: 2026-07-06
---

# Login

The user signs in with email and password. When they submit valid credentials, they land on the dashboard (see AC-1 in the login feature spec).

## Purpose

Authenticate a returning user and route them into the app.

## Actions

- Click "Forgot password?" → opens the password reset screen
- Change theme → toggles dark mode
