---
title: "complex-app"
description: "Multi-product / enterprise — a superset of standard-app adding brand voice, stack-native mockups, project-ops, supervised planning, and per-slice audit."
order: 4
---

The **complex-app** flow is the largest tier — multi-product or enterprise. It
is a **superset of [`standard-app`](../standard-app/)**: same two-pass concept +
per-feature loops, plus brand voice, the stack-native walkthrough renderer,
project-level ops, supervised implementation planning, and a quality `audit`
that runs every slice.

## When to use

Picked by `scope-project` for a platform: multiple products, many features,
enterprise concerns (infrastructure non-optional, project-wide subsystem maps).

| Signal | complex-app |
|---|---|
| Scope | multi-product / enterprise |
| Concept | high-level pass + concept-slice loop **with brainstorm** |
| Impl | impl-slice loop with **supervised** planning |
| Quality | eval-code + **audit every slice** |
| Project ops | overview · subsystem-map · integration · review |

## Pipeline

Everything in `standard-app`, plus the deltas below:

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

The flow is self-contained: `complex-app.flow.yaml` carries a top-level
`requires:` block listing exactly what it installs — `shared-contracts` +
`implementation-contract` + `meta-concept-contract` plus every skill its nodes
run (the full standard-app set plus `brand-voice`,
`mockup-walkthrough-framework`, `concept-slice-brainstorm`,
`impl-plan-supervised`, `eval-code`, `audit`, and the four `project-*` ops
skills). No inheritance, no extras.

## Run it

```bash
skaile add flow:complex-app    # install the flow + its skills + contracts
skaile run flow:complex-app
```

## See also

- [`standard-app`](../standard-app/) — the tier this extends
- [`concept-slice`](../concept-slice/) (with brainstorm) and [`impl-slice`](../impl-slice/) — the per-feature loops
- [Slice loops](../../../intro/slice-loops/) · [Tiers](../../../intro/tiers/) · [Flows](../../../intro/flows-and-bundles/)
