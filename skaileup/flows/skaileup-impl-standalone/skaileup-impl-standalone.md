---
title: "skaileup-impl-standalone"
description: "Self-sufficient implementation flow — no concept package needed; generates its own architecture subset, then build + impl-slice loop + quality."
order: 11
---

The **skaileup-impl-standalone** flow lets you start building immediately
without a full concept pass *and* without a handoff package. It produces just
the technical concept it needs — techstack → system architecture → datamodel,
elicited from a one-line product description — then runs build setup, the
per-feature impl-slice loop, and quality. No UX/brand/journeys/screens/mockups;
only the architecture subset required to write and run code.

Each feature's spec is built **just-in-time** inside the slice loop: the
impl-plan brainstorm/align phase elicits the feature before implementing it, so
the concept accretes feature-by-feature instead of being front-loaded.

## When to use

When you want to go straight to code, own no prior concept, and don't need the
UX-oriented concept pass.

| Signal | skaileup-impl-standalone |
|---|---|
| Concept pass | architecture subset only (generated here) |
| Reads | nothing — self-sufficient |
| Build | scaffold → foundation → infrastructure? → migrate → seed → docs |
| Slice loops | impl-slice, once per feature (spec elicited per slice) |
| Tests | unit + integration + e2e? + ready |

If a concept package already exists, prefer
[`skaileup-impl`](../skaileup-impl/) (handoff) and skip regenerating the
architecture.

## Pipeline

```
techstack → system → datamodel
  → scaffold → foundation → infrastructure? → migrate → seed → docs
  → [per feature]  impl-slice loop  (brainstorm elicits the feature spec →
       align → plan-vertical → implement → test → recap → refactor → commit)
  → impl-quality-test-unit → -test-integration → -test-e2e? → -ready
```

## Install manifest

Self-contained: `skaileup-impl-standalone.flow.yaml` carries a top-level
`requires:` block — `shared-contracts` + `implementation-contract`, the 3
architecture skills, the 6 build skills, the 4 quality skills, and
`flow:impl-slice`. No UX/experience concept skills, no inheritance, no extras.

## Run it

```bash
skaile add flow:skaileup-impl-standalone
skaile run flow:skaileup-impl-standalone
```

## See also

- [`skaileup-impl`](../skaileup-impl/) — implementation-only from an existing concept package
- [`impl-slice`](../impl-slice/) — the per-feature loop this flow delegates to
- [Slice loops](../../../intro/slice-loops/) — the shared five-phase shape
