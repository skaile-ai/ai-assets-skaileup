---
implements:
  - experience/features/00_auth/login.md
data_entities: [User]
layout: experience/screens/00_layout/shell.md
last_updated: 2026-07-06
---

# Screen: Verify Email

### Purpose

The user understands their account is not yet active until they confirm the email address it was created with.

### Route

`/verify-email`

### What the User Sees

A short confirmation message stating that a verification email was sent, plus the address it was sent to. There is no form to fill in on this screen.

### Wireframe

```text
┌─────────────────────────────────────────────┐
│ [=] App Name              [search] [avatar] │
├────────────┬────────────────────────────────┤
│ Nav Item 1 │  Verify your email             │
│ Nav Item 2 │ ┌────────────────────────────┐ │
│ Nav Item 3 │ │  Confirmation message      │ │
│            │ │                            │ │
│            │ └────────────────────────────┘ │
└────────────┴────────────────────────────────┘
```

### Information Displayed

The address the verification email was sent to, and the time it was sent.

### Actions

This screen is not yet interactive. No elements: block has been authored for it, so it has no declared actions.

### Situations

- **Default** — the confirmation message is shown
- **Loading** — while the resend request is in flight

### UI Elements

This screen has not yet had its functional elements catalogued.

### Template Data

Not applicable — no seed.json scenario exists for this screen yet.
