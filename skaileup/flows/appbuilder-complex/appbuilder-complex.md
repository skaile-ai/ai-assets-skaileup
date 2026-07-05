---
title: "appbuilder-complex"
description: "Multi-product / enterprise — a superset of appbuilder-standard adding brand voice, stack-native mockups, project-ops, supervised planning, and per-slice audit."
order: 4
---

The **appbuilder-complex** flow is the largest tier — multi-product or enterprise. It
is a **superset of [`appbuilder-standard`](../appbuilder-standard/)**: same two-pass concept +
per-feature loops, plus brand voice, the stack-native walkthrough renderer,
project-level ops, supervised implementation planning, and a quality `audit`
that runs every slice.

## When to use

Picked by `scope-project` for a platform: multiple products, many features,
enterprise concerns (infrastructure non-optional, project-wide subsystem maps).

| Signal | appbuilder-complex |
|---|---|
| Scope | multi-product / enterprise |
| Concept | high-level pass + concept-slice loop **with brainstorm** |
| Impl | impl-slice loop with **supervised** planning |
| Quality | eval-code + **audit every slice** |
| Project ops | overview · subsystem-map · integration · review |

## Pipeline

```
Conceptualization: scope → [concept-discovery] → brand-visual → brand-voice →
                   inspiration? → journeys → behaviors → features → screens →
                   components → (router: astro | framework | static-html) ∥
                   (router: storybook | skip) → [mockup-feedback] →
                   project-ops (overview → subsystem-map → integration → review) →
                   [architecture]
Implementation:    [impl-build-setup infrastructure=required] → [skaileup-slice] ↻
Review:            eval-code → audit (every slice) → [quality-gate]
```

Everything in `appbuilder-standard`, plus the deltas below:

- Concept adds `design-brand-voice` and a third router branch,
  `mockup-walkthrough-framework` (stack-native, highest fidelity) — the
  walkthrough router now tries astro, then framework, then falls back to
  static-html. `[concept-discovery]` and per-feature `[skaileup-slice]` run
  with the same `concept_depth: full` shape as `appbuilder-standard`, but the
  slice's concept half runs its full loop (**with** brainstorm), not the
  trimmed standard one.
- Project ops (once, between `[mockup-feedback]` and `[architecture]`):
  `ops-project-overview` → `-subsystem-map` → `-integration` → `-review`.
- `[impl-build-setup]` runs with `infrastructure: required` (non-optional,
  vs. `optional` in `appbuilder-standard`). Supervised implementation planning
  (`impl-plan-supervised`) runs inside every tier's `[skaileup-slice]` impl
  half now, so it is no longer a complex-only node.
- Quality adds `eval-code` → `audit` after every slice loop iteration, ahead of
  `[quality-gate]` (expressed via edge ordering, since the schema has no loop
  construct).

`mockup-walkthrough-framework` requires `templates-select` to have resolved a
concrete `template-*` first; it renders the walkthrough in the project's actual
framework (Next/Nuxt/SvelteKit). The router's static-html branch covers the
case where no template is resolved.

## Install manifest

The flow is self-contained: `appbuilder-complex.flow.yaml` carries a top-level
`requires:` block listing exactly what it installs — `shared-contracts` +
`meta-concept-contract` plus its own direct skills (the appbuilder-standard
set plus `brand-voice`, `mockup-walkthrough-framework`, the four `project-*`
ops skills, `eval-code`, `audit`) plus six `flow:` refs for the sub-flows it
delegates to (`concept-discovery`, `mockup-feedback`, `architecture`,
`impl-build-setup`, `skaileup-slice`, `quality-gate`). `skaileup-slice`'s own
manifest transitively provides the concept-slice brainstorm skill and
`impl-plan-supervised`; `impl-build-setup`'s manifest provides
`implementation-contract`. No inheritance, no extras.

## Run it

```bash
skaile add flow:appbuilder-complex    # install the flow + its skills + contracts
skaile run flow:appbuilder-complex
```

## See also

- [`appbuilder-standard`](../appbuilder-standard/) — the tier this extends
- [`skaileup-slice`](../skaileup-slice/) — the per-feature loop (concept half: [`skaileup-slice-concept`](../skaileup-slice-concept/), full loop with brainstorm; impl half: [`skaileup-slice-impl`](../skaileup-slice-impl/))
- [Slice loops](../../../intro/slice-loops/) · [Tiers](../../../intro/tiers/) · [Flows](../../../intro/flows-and-bundles/)
