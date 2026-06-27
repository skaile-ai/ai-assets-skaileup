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

Everything in `appbuilder-standard`, plus the deltas below:

```
Concept adds:
  design-brand-voice
  mockup-walkthrough-framework        (stack-native, highest fidelity)
  concept-slice gains brainstorm      (full loop, not the trimmed standard one)

Project ops (once, after high-level concept):
  project-overview → subsystem-map → integration → review

Planning adds:
  impl-plan-supervised                (human-in-the-loop plan gate)

Quality adds (every slice):
  eval-code → audit                   (expressed via edge ordering)
```

`mockup-walkthrough-framework` requires `templates-select` to have resolved a
concrete `template-*` first; it renders the walkthrough in the project's actual
framework (Next/Nuxt/SvelteKit). A static-html fallback node covers the case
where no template is resolved.

## Install manifest

The flow is self-contained: `appbuilder-complex.flow.yaml` carries a top-level
`requires:` block listing exactly what it installs — `shared-contracts` +
`implementation-contract` + `meta-concept-contract` plus every skill its nodes
run (the full appbuilder-standard set plus `brand-voice`,
`mockup-walkthrough-framework`, `concept-slice-brainstorm`,
`impl-plan-supervised`, `eval-code`, `audit`, and the four `project-*` ops
skills). No inheritance, no extras.

## Run it

```bash
skaile add flow:appbuilder-complex    # install the flow + its skills + contracts
skaile run flow:appbuilder-complex
```

## See also

- [`appbuilder-standard`](../appbuilder-standard/) — the tier this extends
- [`concept-slice`](../concept-slice/) (with brainstorm) and [`impl-slice`](../impl-slice/) — the per-feature loops
- [Slice loops](../../../intro/slice-loops/) · [Tiers](../../../intro/tiers/) · [Flows](../../../intro/flows-and-bundles/)
