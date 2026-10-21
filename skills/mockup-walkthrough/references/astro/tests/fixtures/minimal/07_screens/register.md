---
screen_id: register
title: Register
implements:
  - 05_features/auth/login.md
floorplan: wizard
posture: transient
density: comfortable
regions:
  step-list: { shows: user, representation: chip }
  step-body: { shows: user, representation: page }
elements:
  - id: go-login
    kind: link
    region: footer
    label: "Sign in instead"
    states: [default]
    target: login
    describes: "Click \"Sign in instead\" → returns to the login screen"
  - id: account-type-tabs
    kind: tabs
    region: step-body
    label: "Account type"
    states: [default]
    items:
      - label: "Personal"
      - label: "Business"
  - id: signup-benefits
    kind: list
    region: step-help
    label: "Why join"
    states: [default]
    items:
      - label: "See your login screen"
        target: login
      - "Get onboarding tips"
  - id: learn-more
    kind: link
    region: step-help
    label: "Learn more about business accounts"
    states: [default]
    target: business-account-info
    describes: "Click \"Learn more about business accounts\" → intended for a screen not yet authored"
last_updated: 2026-07-06
---

# Register

A new user creates an account.

## Email

## Password

## Create account
