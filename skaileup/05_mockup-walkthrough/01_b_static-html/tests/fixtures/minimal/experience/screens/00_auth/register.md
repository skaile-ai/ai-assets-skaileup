---
implements:
  - experience/features/00_auth/login.md
data_entities: [User]
layout: experience/screens/00_layout/shell.md
elements:
  - id: go-login
    kind: link
    label: "Sign in instead"
    states: [default]
    target: 00_auth/login
    describes: "Click \"Sign in instead\" → returns to the login screen"
  - id: account-type-tabs
    kind: tabs
    label: "Account type"
    states: [default]
    items:
      - label: "Personal"
      - label: "Business"
  - id: signup-benefits
    kind: list
    label: "Why join"
    states: [default]
    items:
      - label: "See your login screen"
        target: 00_auth/login
      - "Get onboarding tips"
  - id: learn-more
    kind: link
    label: "Learn more about business accounts"
    states: [default]
    target: 00_auth/business_account_info
    describes: "Click \"Learn more about business accounts\" → intended for a screen not yet authored"
last_updated: 2026-07-06
---

# Register

A new user creates an account.

## Email

## Password

## Create account
