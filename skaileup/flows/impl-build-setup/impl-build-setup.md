---
title: "impl-build-setup"
description: "Shared one-time build-setup block: scaffold → foundation → infrastructure(opt) → migrate → seed → docs."
order: 13
---

The **impl-build-setup** flow is the shared one-time build-setup block. The
build-bearing tiers (`appbuilder-simple`, `appbuilder-standard`,
`appbuilder-complex`, `appbuilder-cli`) and `skaileup-implementation` delegate
to it via a **sub-flow node** right after architecture; it is
standalone-runnable (`skaile run flow:impl-build-setup`).

## Pipeline

```
scaffold → foundation → infrastructure? → migrate → seed → docs
```

## Variance knobs

Consumers set these on the sub-flow node's `parameters:` (threaded to nodes
via `${...}`, the `concept_depth` pattern):

| Global | Values | Default | Who overrides |
|---|---|---|---|
| `infrastructure` | `skip` \| `optional` \| `required` | `optional` | simple + cli: `skip`; complex: `required` |
| `data_setup` | `required` \| `optional` | `required` | cli: `optional` (migrate/seed are optional data steps) |

## Install manifest

`impl-build-setup.flow.yaml` carries a top-level `requires:` listing
`shared-contracts`, `implementation-contract` (cited by `impl-build-docs`) and
the six `impl-build-*` skills — everything installed by
`skaile add flow:impl-build-setup`.
