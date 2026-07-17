---
name: p2p-intake-post
description: >-
  DEMO-GRADE (Getec workshop). Use after the approval gate authorizes a PO
  draft, to post it to Business Central via the business-central-mock MCP
  (post_po) and record the posted confirmation.
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
      - path: 'p2p-intake/po-draft/po-draft.json'
        gate: hard
        description: 'Approved PO draft from the po-draft step (past the approval gate)'
    produces:
      - path: 'p2p-intake/posted/po-posted.json'
        description: 'Posted PO confirmation from Business Central'
---

# P2P Intake — Post PO (demo-grade)

ROLE  Posting agent — commits an approved PO draft to Business Central and records the confirmation.

READS
  p2p-intake/po-draft/po-draft.json                — approved PO draft (past the approval gate)

WRITES
  p2p-intake/posted/po-posted.json                 — posted PO confirmation (number + status)

REQUIRES
  hard: p2p-intake/po-draft/po-draft.json — A PO draft must exist and have cleared the approval gate
  soft: business-central-mcp — post_po tool; demo uses the colocated business-central-mock MCP

STEP 1: Post the PO
  - Call Business Central post_po with the draft's po_number.
  - Capture the returned posted number and status ("posted").

STEP 2: Write po-posted.json

OUTPUT p2p-intake/posted/po-posted.json
  {
    "po_number": "<bc-po-number>",
    "supplier_id": "<bc-supplier-id>",
    "total": 0,
    "status": "posted",
    "posted_at": "<iso-datetime>"
  }

EMIT  [p2p-intake-post] completed po=<id> status=posted total=<amount>

MUST  only run after the approval gate has authorized the draft
NEVER  post a draft whose status is not approved

CHECKLIST
  - [ ] po-posted.json written to p2p-intake/posted/
  - [ ] status is posted
  - [ ] posted po_number recorded
