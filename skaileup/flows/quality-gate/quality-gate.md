---
title: "quality-gate"
description: "Shared post-loop quality gate: unit → integration → e2e → ready, plus the optional ops review → sync tail."
order: 16
---

The **quality-gate** flow is the shared post-loop quality gate.
`appbuilder-standard`, `appbuilder-complex` and `skaileup-implementation`
delegate to it via a **sub-flow node** after their slice loop; it is
standalone-runnable (`skaile run flow:quality-gate`). `appbuilder-simple`
(unit + e2e) and `appbuilder-cli` (unit + integration) run subsets and keep
their inline quality nodes.

## Pipeline

```
test-unit → test-integration → test-e2e → ready → ops-review? → ops-sync?
```

## Variance knobs

| Global | Values | Default | Who overrides |
|---|---|---|---|
| `e2e` | `required` \| `optional` | `required` | skaileup-implementation: `optional` |
| `ops_tail` | `include` \| `skip` | `include` | skaileup-implementation: `skip` |

## Install manifest

`quality-gate.flow.yaml` carries a top-level `requires:` listing
`shared-contracts`, the four `impl-quality-*` gate skills and the
`ops-review` / `ops-sync` tail.
