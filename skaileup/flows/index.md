---
title: "Flows"
description: "The tier flows and the two reusable slice-loop building blocks. Each flow is self-contained — it carries its own dependency manifest."
order: 0
---

A **flow** is an executable pipeline. Each flow is **self-contained**: its
top-level `requires:` block is the install manifest — the contracts its skills
read plus every skill its nodes run. Installing the flow provisions everything;
then run it:

```bash
skaile add flow:<name>      # install the flow + its skills + contracts
skaile run flow:<name>      # execute the pipeline
```

## Tier flows

Four sizes, chosen by `scope-project`. Each flow's `requires:` is the **exact**
set it runs — no inheritance, no extras. (Larger tiers are supersets of smaller
ones by construction, but each lists its own complete manifest.)

| Flow | Scope | Shape |
|---|---|---|
| [`appbuilder-mvp`](./appbuilder-mvp/) | 1 feature, trivial persistence | one linear pass |
| [`appbuilder-simple`](./appbuilder-simple/) | single-user, ≤5 features | linear concept + impl-slice loop |
| [`appbuilder-standard`](./appbuilder-standard/) | multi-user, ≤20 features | high-level concept + concept-slice & impl-slice loops |
| [`appbuilder-complex`](./appbuilder-complex/) | multi-product / enterprise | appbuilder-standard superset + project-ops + audit |

## Slice-loop building blocks

Not tiers — reusable per-feature loops the tier flows delegate to once per
feature. All standalone-runnable. `skaileup-slice` is the unified parent that
runs its two halves in sequence; consumers usually delegate to it.

| Flow | Loop |
|---|---|
| [`skaileup-slice`](./skaileup-slice/) | slice-concept → slice-impl (parent; `concept_depth`: full \| just-in-time \| skip) |
| [`skaileup-slice-concept`](./skaileup-slice-concept/) | brainstorm → align → scope-feature → design-feature (concept-needs check in just-in-time mode) |
| [`skaileup-slice-impl`](./skaileup-slice-impl/) | plan → implement → test → recap → refactor → commit |

## Variant flows

Alternate shapes the `scope-project` step routes to when a project doesn't fit
the four UI-oriented tiers. Each is self-contained with its own `requires:`.

| Flow | Shape |
|---|---|
| [`appbuilder-cli`](./appbuilder-cli/) | CLI tier — no UI/brand/screens/mockups; end-to-end concept + build + impl-slice loop + unit/integration tests |
| [`skaileup-concept-only`](./skaileup-concept-only/) | full concept package, no implementation — planning / team handoff |
| [`skaileup-concept-reverse`](./skaileup-concept-reverse/) | reverse a concept out of an existing codebase, then optionally enrich |

## Implementation-first flows

Implementation-led shapes that minimise or skip the upfront concept pass. Each
is self-contained with its own `requires:`.

| Flow | Shape |
|---|---|
| [`skaileup-impl`](./skaileup-impl/) | Code-build, no concept-design pass. Architecture is read-or-generate (reads an existing concept package if present, else generates the subset) → build + `skaileup-slice-impl` loop + quality. |
| [`skaileup-implementation`](./skaileup-implementation/) | Start-in-the-middle: thin foundation → per-feature loop of `skaileup-slice` at `concept_depth: just-in-time`. The slice's concept half builds only the concept each feature needs, on demand, as a by-product of building. |

## See also

- [Tiers](../intro/tiers/) — the `scope-project` decision rule
- [Flows](../intro/flows-and-bundles/) — how a flow declares its dependencies + the drift guard
- [Slice loops](../intro/slice-loops/) — the shared five-phase shape
