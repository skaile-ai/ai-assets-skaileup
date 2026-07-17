---
name: p2p-intake-po-draft
description: >-
  DEMO-GRADE (Getec workshop). Use after supplier enrichment, to create a
  purchase-order draft in Business Central via the business-central-mock MCP
  (create_po_draft) and record it as po-draft.json for the approval gate.
metadata:
  version: '0.1.0'
  stage: alpha
  tags:
    - demo
    - getec
    - p2p
    - purchase-order
    - business-central
  source: TEST
  requires:
    - shared-contracts
  env_vars:
    BUSINESS_CENTRAL_MCP: 'Ref for the business-central-mock MCP server. In production Getec SAP BTP MCP plays this role.'
  prerequisites:
    files:
      - path: 'p2p-intake/enrichment/supplier.json'
        gate: hard
        description: 'Resolved supplier from the enrich step'
    produces:
      - path: 'p2p-intake/po-draft/po-draft.json'
        description: 'Created PO draft (status pending approval)'
---

# P2P Intake — Create PO Draft (demo-grade)

ROLE  PO drafting agent — assembles line items + supplier into a Business Central PO draft.

READS
  p2p-intake/enrichment/supplier.json              — resolved supplier + terms
  p2p-intake/classification/request.json           — line items, cost_center, needed_by

WRITES
  p2p-intake/po-draft/po-draft.json                — created PO draft with BC draft id

REQUIRES
  hard: p2p-intake/enrichment/supplier.json — Enrichment must have run
  soft: business-central-mcp — create_po_draft tool; demo uses the colocated business-central-mock MCP

STEP 1: Build the PO body
  - Map request line items to PO lines (description, qty, unit, unit_price if known).
  - Attach supplier_id, payment_terms, currency, cost_center, needed_by.

STEP 2: Create the draft in Business Central
  - Call create_po_draft with the body; capture the returned po_number/draft id.
  - The draft's status is "pending_approval" — it is NOT posted here.

STEP 3: Write po-draft.json

OUTPUT p2p-intake/po-draft/po-draft.json
  {
    "po_number": "<bc-draft-id>",
    "supplier_id": "<bc-supplier-id>",
    "currency": "<string>",
    "lines": [ { "description": "<string>", "qty": 0, "unit_price": 0, "amount": 0 } ],
    "total": 0,
    "cost_center": "<string>",
    "status": "pending_approval"
  }

EMIT  [p2p-intake-po-draft] completed po=<id> total=<amount> status=pending_approval

MUST  leave status = "pending_approval" (the approval gate, not this skill, authorizes posting)
NEVER  call post_po from this skill

CHECKLIST
  - [ ] po-draft.json written to p2p-intake/po-draft/
  - [ ] po_number captured from create_po_draft
  - [ ] status is pending_approval (not posted)
