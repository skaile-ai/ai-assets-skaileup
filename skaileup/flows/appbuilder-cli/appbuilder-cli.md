---
title: "appbuilder-cli"
description: "Variant tier for command-line tools — end-to-end, no UI/brand/screens/mockups, unit + integration tests (no E2E)."
order: 7
---

The **appbuilder-cli** flow is the tier for command-line tools. It runs the full
concept→build→slice pipeline like the UI tiers, but drops everything UI: no
brand, no journeys, no screens, no mockups, no E2E. Features are described as
commands. It replaces the legacy split `cli-concept` + `cli` flows with one
conformant, self-contained flow.

## When to use

Picked by `scope-project` when the deliverable is a headless tool — a CLI,
script, or daemon — rather than an app with a UI.

| Signal | appbuilder-cli |
|---|---|
| UI | none (headless) |
| Design / mockups | skipped |
| Tests | unit + integration (no E2E) |
| Slice loops | impl-slice, once per feature |

## Pipeline

```
Conceptualization: scope → brief → features(commands) → [architecture system=skip]
Implementation:    [impl-build-setup infrastructure=skip data_setup=optional] →
                   [skaileup-slice-impl] ↻
Review:            unit → integration (inline — cli runs a quality subset, not the gate)
```

`[architecture]` delegates techstack → templates → datamodel (`system: skip` —
no system-architecture step); `[impl-build-setup]` delegates scaffold →
foundation (headless) → migrate → seed → docs (`infrastructure: skip`,
`data_setup: optional`); `[skaileup-slice-impl]` runs the full impl-only loop
once per feature: brainstorm → align → plan-vertical → git-prepare → implement
→ implement-page → test → recap → refactor → commit → git-finish. Like
appbuilder-simple, appbuilder-cli doesn't delegate to `[quality-gate]` — review
is two inline skill nodes (`test-unit`, `test-integration`), no E2E.

## Install manifest

Self-contained: `appbuilder-cli.flow.yaml` carries a top-level `requires:` block —
`shared-contracts` plus its own 5 direct skills (scope, brief,
features-as-commands, unit tests, integration tests) plus three `flow:` refs
for the sub-flows it delegates to (`architecture`, `impl-build-setup`,
`skaileup-slice-impl`). `implementation-contract` is no longer listed
directly — `impl-build-setup`'s own manifest provides it. No inheritance, no
extras.

## Run it

```bash
skaile add flow:appbuilder-cli       # install the flow + its skills + contracts
skaile run flow:appbuilder-cli       # execute the pipeline
```

## See also

- [Tiers](../../../intro/tiers/) — how `scope-project` chooses a flow
- [`appbuilder-mvp`](../appbuilder-mvp/) — the smallest UI-oriented tier
- [`skaileup-slice-impl`](../skaileup-slice-impl/) — the per-feature loop this flow delegates to
