---
title: "appbuilder-simple"
description: "Single-user app of up to ~5 features — linear concept pipeline plus a per-feature impl-slice loop."
order: 2
---

The **appbuilder-simple** flow handles a single-user app of up to ~5 features. Concept
still runs linearly (no concept-slice loop), but implementation now repeats a
full **impl-slice loop** once per feature.

## When to use

Picked by `scope-project` for a focused single-user app — real persistence, a
handful of features, no multi-user concerns.

| Signal | appbuilder-simple |
|---|---|
| Feature count | ≤ 5 |
| Users | single |
| Concept | linear (brand + journeys + screens) |
| Impl | per-feature impl-slice loop |

## Pipeline

Inherits the appbuilder-mvp shape and adds design, experience, component mockups, the full
`impl-build` setup, and the impl-slice loop:

```
Conceptualization: scope → brief → brand-visual → journeys → features → screens →
                   static-html ∥ isolated-html → [architecture system=skip]
Implementation:    [impl-build-setup infrastructure=skip] → [skaileup-slice-impl] ↻
Review:            unit → e2e (inline — simple runs a quality subset, not the gate)
```

`[architecture]` delegates techstack → templates → datamodel (no system-architecture
step — `system: skip`); `[impl-build-setup]` delegates scaffold → foundation →
migrate → seed → docs (no infrastructure step — `infrastructure: skip`);
`[skaileup-slice-impl]` runs the impl-only loop once per feature: brainstorm →
align → plan-vertical → git-prepare → implement → implement-page → test → recap
→ refactor → commit → git-finish. Unlike the tier flows above it, appbuilder-simple
doesn't delegate to `[quality-gate]` — review is two inline skill nodes
(`test-unit`, `test-e2e`), not the shared gate's unit/integration/e2e/ready/ops chain.

## Install manifest

The flow is self-contained: `appbuilder-simple.flow.yaml` carries a top-level
`requires:` block listing exactly what it installs — `shared-contracts` plus
its own 10 direct skills (scope, brief, brand-visual, journeys, features,
screens, static-html walkthrough, isolated-html components, unit tests, e2e
tests) plus three `flow:` refs for the sub-flows it delegates to (`architecture`,
`impl-build-setup`, `skaileup-slice-impl`). No inheritance and no extras:
unlike the old inherited bundle it carries only the skills this tier actually
renders with (e.g. `mockup-walkthrough-static-html`, never appbuilder-mvp's
`mockup-walkthrough-text`), and `implementation-contract` is no longer listed
directly — it comes in transitively via `impl-build-setup`'s own manifest.

## Run it

```bash
skaile add flow:appbuilder-simple    # install the flow + its skills + contracts
skaile run flow:appbuilder-simple
```

## See also

- [`appbuilder-mvp`](../appbuilder-mvp/) — the tier below · [`appbuilder-standard`](../appbuilder-standard/) — the tier above
- [`skaileup-slice-impl`](../skaileup-slice-impl/) — the per-feature loop reused here
- [Tiers](../../../intro/tiers/) · [Flows](../../../intro/flows-and-bundles/)
