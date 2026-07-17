---
title: "contract-migration"
description: "Getec demo flow: extract → price/validate (pricing-engine MCP) → confidence gate → emit engine-input. Low confidence pauses for human approval; otherwise autonomous."
order: 20
---

The **contract-migration** flow is a Getec workshop demo (not a product tier). It
migrates a legacy energy-supply contract into a pricing-engine input artifact and
demonstrates a **confidence gate**: when the priced result's confidence is below
`confidence_threshold` the gate pauses for human approval; otherwise the flow runs
autonomously to completion. Standalone-runnable: `skaile run flow:contract-migration`.

## Pipeline

```
extract → price (pricing-engine MCP) → [confidence gate] → emit engine-input
```

- **extract** (`contract-migration-extract`) — structured terms + per-field confidence → `contract-migration/extraction/terms.json`
- **price** (`contract-migration-price`) — prices/validates against the pricing-engine MCP (demo falls back to an in-skill deterministic calc), sets an overall `confidence` → `contract-migration/pricing/pricing-result.json`
- **confidence gate** — `artifact.pricing-result.confidence >= confidence_threshold`; `on_fail: pause-for-human`. Low confidence → approval; else autonomous. Both paths continue to emit.
- **emit** (`contract-migration-emit`) — assembles the engine-input artifact, stamping `approval_mode` (autonomous | human-approved) → `contract-migration/engine-input/engine-input.json`

## Gate demonstration

To make the gate pause, feed a contract whose extraction raises a validation flag
(e.g. missing tariff or unpriceable tariff) — the priced `confidence` drops below
`confidence_threshold` (0.8) and the gate escalates to human approval before emit.

## Scope note

The **pricing-engine MCP** is Getec's real system and is out of scope for this
repo; the `price` skill computes in-line (labelled `demo-fallback`) when no
pricing-engine MCP is wired, so the flow runs standalone. Only the mock **Business
Central** MCP (used by `p2p-intake`) is built here.

## Install manifest

`contract-migration.flow.yaml` carries a top-level `requires:` listing
`shared-contracts` and the three `contract-migration-*` skills.
