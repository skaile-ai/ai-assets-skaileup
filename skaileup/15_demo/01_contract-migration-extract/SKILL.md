---
name: contract-migration-extract
description: >-
  DEMO-GRADE (Getec workshop). Use when a legacy energy-supply contract must be
  turned into structured terms for pricing. Extracts customer, meter, tariff,
  consumption and validity fields from a contract document into terms.json.
metadata:
  version: '0.1.0'
  stage: alpha
  tags:
    - demo
    - getec
    - contract-migration
    - extraction
  source: TEST
  requires:
    - shared-contracts
  prerequisites:
    inputs_optional:
      - id: contract_path
        label: 'Path to the source contract document'
        type: text
        default: null
        hint: 'A PDF/DOCX/MD contract (anonymized PoC contract for the demo). If absent, a bundled sample is used.'
    produces:
      - path: 'contract-migration/extraction/terms.json'
        description: 'Structured contract terms extracted from the source document'
---

# Contract Migration — Extract (demo-grade)

ROLE  Contract extraction agent — reads a legacy energy-supply contract and emits structured terms for the pricing step.

READS
  ? {contract_path}                                — source contract document (demo: anonymized PoC contract)
  contracts/golden_principles.md                   — mechanical rules for artifact output

WRITES
  contract-migration/extraction/terms.json         — structured contract terms + per-field extraction confidence

REQUIRES
  soft: {contract_path} — Source contract; a bundled sample is used when absent (demo mode)

STEP 1: Locate the source
  - If {contract_path} is set and exists, read it.
  - ELSE fall back to a representative sample so the demo runs standalone.

STEP 2: Extract terms
  - Pull: customer_id, customer_name, delivery_point (meter/MaLo id), tariff_type,
    annual_consumption_kwh, base_price_eur_per_year, energy_price_ct_per_kwh,
    contract_start, contract_end, index_clause (if any).
  - For each field, record a 0..1 extraction_confidence.
  - Compute overall_confidence = min of field confidences (weakest link).

STEP 3: Write terms.json

OUTPUT contract-migration/extraction/terms.json
  {
    "customer": { "id": "<string>", "name": "<string>" },
    "delivery_point": "<malo-id>",
    "tariff": { "type": "<string>", "base_price_eur_per_year": 0, "energy_price_ct_per_kwh": 0 },
    "consumption": { "annual_kwh": 0 },
    "validity": { "start": "<iso-date>", "end": "<iso-date>" },
    "index_clause": "<string|null>",
    "extraction_confidence": 0.0,
    "field_confidence": { "<field>": 0.0 }
  }

EMIT  [contract-migration-extract] completed fields=<n> confidence=<0..1>

MUST  write extraction_confidence for every extracted field
NEVER  invent contract values that are not present in the source (mark missing fields null with confidence 0)

CHECKLIST
  - [ ] terms.json written to contract-migration/extraction/
  - [ ] extraction_confidence present and in [0,1]
  - [ ] missing fields are null, not fabricated
