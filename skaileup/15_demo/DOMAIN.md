---
slug: demo
description: "Demo-grade process skills for the Getec August workshop: contract-migration + p2p-intake"
metadata:
  stage: alpha
  type: domain
---

# demo

Demo-grade skills backing the two Getec workshop demo flows
(`flows/contract-migration/`, `flows/p2p-intake/`). All are DEMO-GRADE stubs:
enough grammar and structure to validate and run standalone, not production
skills. The p2p skills call the colocated **business-central-mock** MCP server
(`flows/p2p-intake/business-central-mock/`).

## Skills

- **contract-migration-extract** (`01_contract-migration-extract/`) — Extract structured terms + per-field confidence from a legacy energy-supply contract → `contract-migration/extraction/terms.json`.
- **contract-migration-price** (`02_contract-migration-price/`) — Price/validate terms against the pricing-engine MCP (demo fallback: in-skill deterministic calc); sets the confidence the gate reads → `contract-migration/pricing/pricing-result.json`.
- **contract-migration-emit** (`03_contract-migration-emit/`) — Assemble the engine-input artifact, stamping approval_mode (autonomous | human-approved) → `contract-migration/engine-input/engine-input.json`.
- **p2p-intake-classify** (`04_p2p-intake-classify/`) — Normalize + classify an inbound purchase request → `p2p-intake/classification/request.json`.
- **p2p-intake-enrich** (`05_p2p-intake-enrich/`) — Resolve supplier master data via Business Central `get_supplier` → `p2p-intake/enrichment/supplier.json`.
- **p2p-intake-po-draft** (`06_p2p-intake-po-draft/`) — Create a PO draft via `create_po_draft` (status `pending_approval`) → `p2p-intake/po-draft/po-draft.json`.
- **p2p-intake-post** (`07_p2p-intake-post/`) — Post the approved PO via `post_po` → `p2p-intake/posted/po-posted.json`.

## When to Use

- Only via the demo flows (`skaile run flow:contract-migration`, `skaile run flow:p2p-intake`) or when rehearsing the Getec workshop.
- Not part of the appbuilder/skaileup tier pipelines.
