---
title: "cli-app"
description: "Variant tier for command-line tools — end-to-end, no UI/brand/screens/mockups, unit + integration tests (no E2E)."
order: 7
---

The **cli-app** flow is the tier for command-line tools. It runs the full
concept→build→slice pipeline like the UI tiers, but drops everything UI: no
brand, no journeys, no screens, no mockups, no E2E. Features are described as
commands. It replaces the legacy split `cli-concept` + `cli` flows with one
conformant, self-contained flow.

## When to use

Picked by `scope-project` when the deliverable is a headless tool — a CLI,
script, or daemon — rather than an app with a UI.

| Signal | cli-app |
|---|---|
| UI | none (headless) |
| Design / mockups | skipped |
| Tests | unit + integration (no E2E) |
| Slice loops | impl-slice, once per feature |

## Pipeline

```
scope-project → concept-brief → product-spec-features   (features as commands)
  → techstack → templates-select → datamodel
  → scaffold → foundation (headless) → migrate?/seed? → docs
  → [per feature]  impl-plan-align → impl-plan-plan-vertical
       → impl-slice-implement → impl-slice-test → impl-slice-recap → impl-slice-commit
  → impl-quality-test-unit + impl-quality-test-integration
```

## Install manifest

Self-contained: `cli-app.flow.yaml` carries a top-level `requires:` block —
`shared-contracts` + `implementation-contract` plus exactly the 19 skills its
nodes run. No inheritance, no extras.

## Run it

```bash
skaile add flow:cli-app       # install the flow + its skills + contracts
skaile run flow:cli-app       # execute the pipeline
```

## See also

- [Tiers](../../../intro/tiers/) — how `scope-project` chooses a flow
- [`mvp`](../mvp/) — the smallest UI-oriented tier
- [`impl-slice`](../impl-slice/) — the per-feature loop this flow inlines
