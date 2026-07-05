---
title: "architecture"
description: "Shared architecture block: techstack → templates-select(opt) → system(opt) → datamodel; writes _concept/blueprint/."
order: 14
---

The **architecture** flow is the shared blueprint block. Six flows delegate to
it via a **sub-flow node** (`appbuilder-simple`, `appbuilder-standard`,
`appbuilder-complex`, `appbuilder-cli`, `skaileup-implementation`,
`skaileup-concept-only`); it is standalone-runnable
(`skaile run flow:architecture`). It writes `_concept/blueprint/` — it belongs
to the **conceptualization** phase even in implementation-led flows.

## Pipeline

```
techstack → templates-select? → system? → datamodel
```

## Variance knobs

| Global | Values | Default | Who overrides |
|---|---|---|---|
| `templates` | `include` \| `skip` | `include` | skaileup-implementation, skaileup-concept-only: `skip` |
| `system` | `include` \| `skip` | `include` | appbuilder-simple, appbuilder-cli: `skip` |

## Install manifest

`architecture.flow.yaml` carries a top-level `requires:` listing
`shared-contracts` and the four `impl-architecture-*` skills.
