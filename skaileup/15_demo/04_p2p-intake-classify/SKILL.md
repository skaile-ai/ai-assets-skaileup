---
name: p2p-intake-classify
description: >-
  DEMO-GRADE (Getec workshop). Use when an inbound purchase request (email,
  form, webhook payload) enters procure-to-pay intake. Classifies category,
  urgency and routing, and normalizes the request into request.json.
metadata:
  version: '0.1.0'
  stage: alpha
  tags:
    - demo
    - getec
    - p2p
    - classification
  source: TEST
  requires:
    - shared-contracts
  prerequisites:
    inputs_optional:
      - id: request_payload
        label: 'Raw inbound purchase request payload'
        type: textarea
        default: null
        hint: 'Email/form/webhook text. If absent, a bundled sample request is used so the demo runs standalone.'
    produces:
      - path: 'p2p-intake/classification/request.json'
        description: 'Normalized, classified purchase request'
---

# P2P Intake — Classify (demo-grade)

ROLE  Intake classifier — normalizes an inbound purchase request and assigns category, urgency and routing.

READS
  ? {request_payload}                              — raw inbound request (demo: bundled sample when absent)
  contracts/golden_principles.md                   — mechanical rules for artifact output

WRITES
  p2p-intake/classification/request.json           — normalized + classified request

REQUIRES
  soft: {request_payload} — Raw request; a bundled sample is used when absent (demo mode)

STEP 1: Read the payload
  - Use {request_payload} if present, else the bundled sample.

STEP 2: Classify + normalize
  - Extract: requestor, supplier_name (as stated), line items (description, qty, unit),
    cost_center, needed_by.
  - Assign: category (goods | services | energy | it), urgency (low | normal | high),
    route (auto | buyer-review).

STEP 3: Write request.json

OUTPUT p2p-intake/classification/request.json
  {
    "requestor": "<string>",
    "supplier_name": "<string>",
    "line_items": [ { "description": "<string>", "qty": 0, "unit": "<string>" } ],
    "cost_center": "<string>",
    "needed_by": "<iso-date>",
    "classification": { "category": "<string>", "urgency": "<string>", "route": "<string>" }
  }

EMIT  [p2p-intake-classify] completed category=<cat> items=<n> route=<route>

MUST  populate classification.category, urgency and route on every run
NEVER  drop line items present in the payload

CHECKLIST
  - [ ] request.json written to p2p-intake/classification/
  - [ ] classification block complete
  - [ ] line items preserved from payload
