---
name: p2p-intake-enrich
description: >-
  DEMO-GRADE (Getec workshop). Use after a purchase request is classified, to
  resolve and attach supplier master data from Business Central via the
  business-central-mock MCP (get_supplier) into supplier.json.
metadata:
  version: '0.1.0'
  stage: alpha
  tags:
    - demo
    - getec
    - p2p
    - enrichment
    - business-central
  source: TEST
  requires:
    - shared-contracts
  env_vars:
    BUSINESS_CENTRAL_MCP: 'Ref for the business-central-mock MCP server. In production Getec SAP BTP MCP plays this role.'
  prerequisites:
    files:
      - path: 'p2p-intake/classification/request.json'
        gate: hard
        description: 'Classified request from the classify step'
    produces:
      - path: 'p2p-intake/enrichment/supplier.json'
        description: 'Resolved supplier master data'
---

# P2P Intake — Enrich (demo-grade)

ROLE  Enrichment agent — resolves the request's supplier against Business Central master data.

READS
  p2p-intake/classification/request.json           — classified request (supplier_name, line items)

WRITES
  p2p-intake/enrichment/supplier.json              — resolved supplier record + match status

REQUIRES
  hard: p2p-intake/classification/request.json — Classification must have run
  soft: business-central-mcp — get_supplier tool; demo uses the colocated business-central-mock MCP

STEP 1: Resolve supplier
  - Call Business Central get_supplier with the request's supplier_name.
  - Capture: supplier_id, legal_name, tax_id, payment_terms, currency, blocked flag.
  - If no match, set match_status = "unresolved" (buyer must create the vendor).

STEP 2: Attach defaults
  - Carry payment_terms and currency forward for the PO draft.

STEP 3: Write supplier.json

OUTPUT p2p-intake/enrichment/supplier.json
  {
    "match_status": "resolved | unresolved",
    "supplier": {
      "id": "<bc-supplier-id>",
      "legal_name": "<string>",
      "tax_id": "<string>",
      "payment_terms": "<string>",
      "currency": "<string>",
      "blocked": false
    }
  }

EMIT  [p2p-intake-enrich] completed supplier=<id> status=<resolved|unresolved>

MUST  record match_status (resolved | unresolved)
NEVER  invent a supplier_id that get_supplier did not return

CHECKLIST
  - [ ] supplier.json written to p2p-intake/enrichment/
  - [ ] match_status set
  - [ ] payment_terms + currency carried forward when resolved
