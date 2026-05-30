---
title: "standard-app"
description: "Multi-user app of up to ~20 features — high-level concept pass plus per-feature concept-slice and impl-slice loops, with a feedback loop on mockups."
order: 3
---

The **standard-app** flow is the first tier where the product is too big to
design in one pass. Concept runs in **two passes**: a project-wide high-level
pass, then a per-feature `concept-slice` loop. Implementation runs a full
`impl-slice` loop per feature. Mockups gain a `mockup-feedback` annotation loop.

## When to use

Picked by `scope-project` for a multi-user app with a real feature backlog.

| Signal | standard-app |
|---|---|
| Feature count | ≤ 20 |
| Users | multi-user |
| Concept | high-level pass + per-feature concept-slice loop |
| Impl | per-feature impl-slice loop (with refactor) |
| Mockup feedback | annotate → triage → patch → apply |

## Pipeline

```
High-level concept (project-wide, one pass):
  scope-project → concept-brief → concept-goals → concept-comparable
    → design-brand-visual → design-inspiration
    → experience-journeys → experience-behaviors → product-spec-features
    → experience-screens → experience-components
    → mockup-walkthrough-astro → mockup-component-storybook
    → mockup-feedback: annotate → triage → patch → apply

Setup (once):
  techstack → templates-select → system → datamodel
    → scaffold → foundation → infrastructure → migrate → seed → docs

Per-feature loop:
  concept-slice:  align → scope-feature → design-feature   (no brainstorm)
  impl-slice:     brainstorm → align → plan-vertical
                    → implement → test → recap → refactor → commit

Quality:  test-unit + test-integration + test-e2e + ready
Ops:      review + sync
```

The high-level pass designs the "grand scheme"; the per-feature loop designs and
builds one feature at a time, learning from delivery before the next. See
[Slice loops](../../../intro/slice-loops/) for why.

## Paired bundle

`standard-app.bundle.yaml` **inherits `simple-app`** and adds the high-level
concept skills (`goals`, `comparable`, `inspiration`), the Astro walkthrough +
Storybook component mockups, the full `mockup-feedback` cluster, the
`concept-slice` skills, `impl-slice-refactor`, integration tests, `ready`, and
`ops` review/sync.

## Run it

```bash
skaile add bundle:standard-app
skaile run flow:standard-app
```

## See also

- [`simple-app`](../simple-app/) — the tier below · [`complex-app`](../complex-app/) — the tier above
- [`concept-slice`](../concept-slice/) and [`impl-slice`](../impl-slice/) — the per-feature loops reused here
- [Slice loops](../../../intro/slice-loops/) · [Tiers](../../../intro/tiers/)
