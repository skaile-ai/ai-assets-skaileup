---
title: "concept-discovery"
description: "Shared discovery block: brief → goals(opt) → comparable(opt)."
order: 17
---

The **concept-discovery** flow is the shared opening discovery pass.
`appbuilder-standard`, `appbuilder-complex` and `skaileup-concept-only`
delegate to it via a **sub-flow node**; it is standalone-runnable
(`skaile run flow:concept-discovery`). Tiers that run `concept-brief` alone
(`appbuilder-mvp`, `appbuilder-simple`, `appbuilder-cli`,
`skaileup-stepwise`) keep it inline.

## Pipeline

```
brief → goals? → comparable?
```

## Variance knobs

| Global | Values | Default | Who overrides |
|---|---|---|---|
| `goals` | `optional` \| `required` | `optional` | skaileup-concept-only: `required` |

## Install manifest

`concept-discovery.flow.yaml` carries a top-level `requires:` listing
`shared-contracts` plus `concept-brief`, `concept-goals`, `concept-comparable`.
