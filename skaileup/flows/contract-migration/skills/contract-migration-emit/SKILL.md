---
name: contract-migration-emit
description: >-
  DEMO-GRADE (Getec workshop). Use after a priced result has passed (or been
  approved through) the confidence gate, to emit the final engine-input artifact
  the downstream pricing engine consumes.
metadata:
  version: '0.1.0'
  stage: alpha
  tags:
    - demo
    - getec
    - contract-migration
    - artifact
  source: TEST
  requires:
    - shared-contracts
  prerequisites:
    files:
      - path: 'contract-migration/pricing/pricing-result.json'
        gate: hard
        description: 'Priced result from the price step'
    produces:
      - path: 'contract-migration/engine-input/engine-input.json'
        description: 'Final engine-input artifact for the downstream pricing engine'
---

# Contract Migration — Emit Engine-Input (demo-grade)

ROLE  Artifact emitter — assembles the validated pricing result into the engine-input artifact the pricing engine ingests.

READS
  contract-migration/pricing/pricing-result.json   — priced result (post confidence gate)
  ? contract-migration/extraction/terms.json        — for identifiers carried into the artifact

WRITES
  contract-migration/engine-input/engine-input.json — final engine-input artifact
  contract-migration/engine-input/emit.md           — one-page human-readable summary

REQUIRES
  hard: contract-migration/pricing/pricing-result.json — Pricing must have run and passed/approved the gate

STEP 1: Read the priced result
  - Load pricing-result.json; carry customer + delivery_point identifiers from terms.json.

STEP 2: Assemble engine-input
  - Map priced line items to the engine input schema; stamp approval_mode
    (autonomous | human-approved) and confidence from the gate decision.

STEP 3: Write engine-input.json and emit.md

OUTPUT contract-migration/engine-input/engine-input.json
  {
    "customer_id": "<string>",
    "delivery_point": "<malo-id>",
    "priced": { "total_eur_per_year": 0, "line_items": [ { "label": "<string>", "amount_eur": 0 } ] },
    "provenance": { "confidence": 0.0, "approval_mode": "autonomous | human-approved", "engine": "<string>" }
  }

EMIT  [contract-migration-emit] completed customer=<id> approval_mode=<mode> total=<eur>

MUST  stamp approval_mode reflecting whether the confidence gate ran autonomously or via human approval
NEVER  emit an engine-input artifact when validation flags remain unresolved and unapproved

CHECKLIST
  - [ ] engine-input.json written to contract-migration/engine-input/
  - [ ] provenance.approval_mode and provenance.confidence set
  - [ ] emit.md summary written
