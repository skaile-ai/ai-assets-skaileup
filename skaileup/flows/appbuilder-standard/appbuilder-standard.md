---
title: "appbuilder-standard"
description: "Multi-user app of up to ~20 features — high-level concept pass plus per-feature concept-slice and impl-slice loops, with a feedback loop on mockups."
order: 3
---

The **appbuilder-standard** flow is the first tier where the product is too big to
design in one pass. Concept runs in **two passes**: a project-wide high-level
pass, then a per-feature `concept-slice` loop. Implementation runs a full
`impl-slice` loop per feature. Mockups gain a `mockup-feedback` annotation loop.

## When to use

Picked by `scope-project` for a multi-user app with a real feature backlog.

| Signal | appbuilder-standard |
|---|---|
| Feature count | ≤ 20 |
| Users | multi-user |
| Concept | high-level pass + per-feature concept-slice loop |
| Impl | per-feature impl-slice loop (with refactor) |
| Mockup feedback | annotate → triage → patch → apply |

## Pipeline

```
Conceptualization: scope → [concept-discovery] → brand-visual → inspiration? →
                   journeys → behaviors? → features → screens → components →
                   (router: astro | static-html) ∥ (router: storybook | skip) →
                   [mockup-feedback] → [architecture]
Implementation:    [impl-build-setup] → [skaileup-slice] ↻ per feature
Review:            [quality-gate]
```

`[...]` = delegated to a shared sub-flow; each carries its own install
manifest, so this flow's `requires:` lists the sub-flows as `flow:` refs
instead of re-listing their skills.

`[concept-discovery]` delegates brief → goals → comparable; `[architecture]`
delegates techstack → templates → system → datamodel; `[impl-build-setup]`
delegates scaffold → foundation → infrastructure → migrate → seed → docs;
`[quality-gate]` delegates unit → integration → e2e → ready → review → sync.
The mockup renderers are picked by **router** nodes, not a parallel-fallback
pair: the walkthrough router tries astro first, falling back to static-html;
the component router tries storybook, or skips if unavailable.

Per feature, `[skaileup-slice]` runs its concept half (`align → scope-feature →
design-feature`, no brainstorm — `concept_depth: full`) then its impl half
(`brainstorm → align → plan-vertical → implement → test → recap → refactor →
commit`).

The high-level pass designs the "grand scheme"; the per-feature loop designs and
builds one feature at a time, learning from delivery before the next. See
[Slice loops](../../../intro/slice-loops/) for why.

## Install manifest

The flow is self-contained: `appbuilder-standard.flow.yaml` carries a top-level
`requires:` block listing exactly what it installs — `shared-contracts` plus
its own direct skills (scope, brand-visual, inspiration, journeys, behaviors,
features, screens, components, the astro/static-html/storybook mockup renderer
skills) plus six `flow:` refs for the sub-flows it delegates to
(`concept-discovery`, `mockup-feedback`, `architecture`, `impl-build-setup`,
`skaileup-slice`, `quality-gate`). Each sub-flow's own manifest transitively
provides its skills and any contracts it reads (e.g. `implementation-contract`
comes in via `architecture` / `impl-build-setup`, not listed here directly). No
inheritance, no extras.

## Run it

```bash
skaile add flow:appbuilder-standard    # install the flow + its skills + contracts
skaile run flow:appbuilder-standard
```

## See also

- [`appbuilder-simple`](../appbuilder-simple/) — the tier below · [`appbuilder-complex`](../appbuilder-complex/) — the tier above
- [`skaileup-slice`](../skaileup-slice/) — the per-feature loop reused here (concept half: [`skaileup-slice-concept`](../skaileup-slice-concept/); impl half: [`skaileup-slice-impl`](../skaileup-slice-impl/))
- [Slice loops](../../../intro/slice-loops/) · [Tiers](../../../intro/tiers/) · [Flows](../../../intro/flows-and-bundles/)
