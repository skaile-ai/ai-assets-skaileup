---
name: contract-migration-price
description: >-
  DEMO-GRADE (Getec workshop). Use after contract terms are extracted, to price
  and validate them against the pricing-engine MCP and produce a priced result
  with an overall confidence score that drives the downstream confidence gate.
metadata:
  version: '0.1.0'
  stage: alpha
  tags:
    - demo
    - getec
    - contract-migration
    - pricing
  source: TEST
  requires:
    - shared-contracts
  env_vars:
    PRICING_ENGINE_MCP: 'Optional. Endpoint/ref for Getec pricing-engine MCP. Demo falls back to an in-skill deterministic calc.'
  prerequisites:
    files:
      - path: 'contract-migration/extraction/terms.json'
        gate: hard
        description: 'Structured terms from the extract step'
    produces:
      - path: 'contract-migration/pricing/pricing-result.json'
        description: 'Priced line items + validation flags + overall confidence'
---

# Contract Migration — Price & Validate (demo-grade)

ROLE  Pricing agent — prices extracted contract terms against the pricing-engine MCP and scores the result's confidence.

READS
  contract-migration/extraction/terms.json         — structured contract terms (with per-field confidence)

WRITES
  contract-migration/pricing/pricing-result.json   — priced line items, validation flags, overall confidence

REQUIRES
  hard: contract-migration/extraction/terms.json — Extraction must have run
  soft: pricing-engine-mcp — Getec pricing-engine MCP tool; demo falls back to an in-skill deterministic calc

STEP 1: Read terms
  - Load terms.json; note extraction_confidence and field_confidence.

STEP 2: Price against the pricing engine
  IF the pricing-engine MCP tool is available
    - Call it with the normalized terms; capture priced line items and engine validation flags.
  ELSE
    - Demo fallback: compute total_eur_per_year = base_price_eur_per_year
      + annual_kwh * energy_price_ct_per_kwh / 100. Flag any missing/implausible inputs.

STEP 3: Validate + score confidence
  - Validation flags: missing_fields, implausible_consumption, unpriceable_tariff, index_clause_unresolved.
  - overall_confidence = extraction_confidence, reduced by 0.3 per raised validation flag (floored at 0).
  - A single hard flag (unpriceable_tariff) forces confidence below the gate threshold so the human is consulted.

STEP 4: Write pricing-result.json

OUTPUT contract-migration/pricing/pricing-result.json
  {
    "engine": "pricing-engine-mcp | demo-fallback",
    "line_items": [ { "label": "<string>", "amount_eur": 0 } ],
    "total_eur_per_year": 0,
    "validation_flags": [ "<flag>" ],
    "confidence": 0.0,
    "source_extraction_confidence": 0.0
  }

EMIT  [contract-migration-price] completed total=<eur> flags=<n> confidence=<0..1>

MUST  set a numeric confidence in [0,1] on every run (the confidence gate reads it)
MUST  record which engine produced the price (mcp vs demo-fallback)
NEVER  claim a price the pricing engine did not return (in fallback mode, label it demo-fallback)

CHECKLIST
  - [ ] pricing-result.json written to contract-migration/pricing/
  - [ ] confidence present and in [0,1]
  - [ ] engine field records mcp or demo-fallback
