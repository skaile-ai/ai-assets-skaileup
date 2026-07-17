---
title: "p2p-intake"
description: "Getec demo flow: classify → enrich → create PO draft → approval gate → post. Business Central is mocked by the colocated business-central-mock MCP server."
order: 21
---

The **p2p-intake** flow is a Getec workshop demo (not a product tier). It runs a
procure-to-pay intake end to end and demonstrates an **approval gate**: a PO draft
is created but the flow pauses for a human before posting it to Business Central.
Standalone-runnable: `skaile run flow:p2p-intake`.

## Pipeline

```
classify → enrich (get_supplier) → create PO draft (create_po_draft) → [approval gate] → post (post_po)
```

- **classify** (`p2p-intake-classify`) — normalizes the inbound request, assigns category/urgency/route → `p2p-intake/classification/request.json`
- **enrich** (`p2p-intake-enrich`) — resolves supplier master data via Business Central `get_supplier` → `p2p-intake/enrichment/supplier.json`
- **po-draft** (`p2p-intake-po-draft`) — creates a PO draft via `create_po_draft` (status `pending_approval`) → `p2p-intake/po-draft/po-draft.json`
- **approval gate** — `artifact.po-draft.status == 'approved'`; `on_fail: pause-for-human`. Always pauses until a human approves the draft.
- **post** (`p2p-intake-post`) — posts the approved PO via `post_po` → `p2p-intake/posted/po-posted.json`

## Business Central mock

Business Central is mocked by the colocated **business-central-mock** MCP server
(`skaileup/flows/p2p-intake/business-central-mock/`), which exposes
`get_supplier` / `create_po_draft` / `post_po` over an in-memory store seeded with
three suppliers (one blocked, to exercise the failure path). In production, Getec's
**SAP BTP MCP layer** plays this role — the skills call the same tool surface
unchanged.

## Gate demonstration

The approval gate always pauses (it requires `po-draft.status == 'approved'`, which
only a human sets). Approve to post; send back for revision otherwise.

## Install manifest

`p2p-intake.flow.yaml` carries a top-level `requires:` listing `shared-contracts`
and the four `p2p-intake-*` skills. The MCP server is provisioned separately (it is
a runtime connector, not a skill/contract asset).
