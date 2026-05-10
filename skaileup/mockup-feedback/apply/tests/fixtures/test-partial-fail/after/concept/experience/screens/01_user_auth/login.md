---
title: Login Screen
elements:
  - id: submit-button
    kind: button
    label: Sign In
    states: [default, loading]
    provisional: true
  - id: email-input
    kind: input
    label: Email
    states: [default, disabled]
    provisional: false
---

# Login Screen

## Layout

- email-input: full-width text field
- submit-button: right-aligned below form

## States

- default: form ready for input
- loading: spinner inside submit-button
