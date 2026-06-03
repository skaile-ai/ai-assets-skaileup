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
| [`mvp`](./mvp/) | 1 feature, trivial persistence | one linear pass |
| [`simple-app`](./simple-app/) | single-user, ≤5 features | linear concept + impl-slice loop |
| [`standard-app`](./standard-app/) | multi-user, ≤20 features | high-level concept + concept-slice & impl-slice loops |
| [`complex-app`](./complex-app/) | multi-product / enterprise | standard-app superset + project-ops + audit |

## Slice-loop building blocks

Not tiers — reusable per-feature loops the tier flows inline once per feature.
Both are standalone-runnable.

| Flow | Loop |
|---|---|
| [`concept-slice`](./concept-slice/) | brainstorm → align → scope-feature → design-feature |
| [`impl-slice`](./impl-slice/) | plan → implement → test → recap → refactor → commit |

## See also

- [Tiers](../intro/tiers/) — the `scope-project` decision rule
- [Flows](../intro/flows-and-bundles/) — how a flow declares its dependencies + the drift guard
- [Slice loops](../intro/slice-loops/) — the shared five-phase shape
