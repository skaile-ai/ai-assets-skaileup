---
name: skaileup-domain-model
description: "Use to build and sharpen the project's domain model — the ubiquitous-language glossary and its decision records (ADRs). A standalone grill (the skaileup analog of grill-with-docs): challenges fuzzy terms and stress-tests them against concrete scenarios and the code, updating the glossary inline; decisions are captured as ADRs only optionally, offered to the user at the end of the session. Run any time vocabulary has drifted or the model needs hardening — during planning, during implementation, or as a cleanup pass. Triggers on: 'sharpen the domain model', 'pin down the glossary', 'define this term', 'record this decision', 'grill the domain'."
metadata:
  version: "1.0.0"
  tags:
    - ops
    - domain-model
    - glossary
    - ubiquitous-language
    - adr
    - decisions
    - interview
    - grill-me
  stage: alpha
  artifacts:
    consumes:
      - id: features
        gate: soft
      - id: datamodel
        gate: soft
      - id: architecture
        gate: soft
      - id: glossary
        gate: soft
    produces:
      - id: glossary
      - id: concept-decisions
  prerequisites:
    inputs_optional:
      - id: topic
        label: "A concept, term, or area to sharpen (leave blank to sweep the whole model)"
        type: text
    reads:
      - path: "_concept/blueprint/glossary.md"
        description: "Existing glossary — the model being sharpened (created lazily if absent)."
      - path: "_concept/experience/features/**/*.md"
        description: "Feature specs — the vocabulary in active use."
      - path: "_concept/blueprint/datamodel/"
        description: "Entities — cross-check that terms and entities agree."
      - path: "_concept/decisions.md"
        description: "Existing design ADRs — respect and supersede, never silently edit."
    produces:
      - path: "_concept/blueprint/glossary.md"
        description: "Glossary — terms added/sharpened inline."
      - path: "_concept/decisions.md"
        description: "Design ADRs — appended when a decision passes the 3-test gate."
---

# Domain Model — sharpen the glossary + capture decisions

## Overview

`skaileup-domain-model` is the **active** domain-modeling discipline: challenging terms,
inventing edge-case scenarios, and writing the glossary and decisions the moment they
crystallise. Merely *reading* `glossary.md` for vocabulary is not this skill — that's
a one-line habit any skill does. This skill is for when you are **changing** the
model, not just consuming it.

It is the skaileup analog of `grill-with-docs`: a grill whose *byproduct* is durable
docs. The align skills (`concept-slice-align`, `impl-plan-align`) capture terms and
decisions inline as they run; this skill is the standalone **sharpen-later** tool —
run it any time the model has drifted, a term is contested, or a decision needs
recording outside a slice grill.

Both outputs and their formats are defined in
`contracts/domain_model.md` — the glossary format,
the ADR format, and the 3-test gate. This skill does not redefine them.

## When to Use

- A term is fuzzy or overloaded and needs a canonical definition.
- Vocabulary has drifted — the same concept is named differently across features,
  screens, datamodel, or code.
- A hard-to-reverse decision was just made and needs recording as an ADR.
- A periodic pass to harden the model before a big build phase.

## When NOT to Use

- Just to *read* the glossary for vocabulary — do that inline, no skill needed.
- To record a transient, easily-reversed choice — that fails the ADR gate; leave it
  in the slice `align.md`.

---

ROLE Active domain modeler — an adversarial interviewer that sharpens the ubiquitous language and records decisions as a byproduct. Challenges fuzzy terms, invents edge-case scenarios, cross-checks against code, and writes glossary + ADRs inline.

READS
  _concept/blueprint/glossary.md                 — the model being sharpened (may not exist yet)
  _concept/experience/features/**/*.md           — vocabulary in active use
  _concept/blueprint/datamodel/                   — entities to reconcile with terms
  _concept/decisions.md                           — existing ADRs to respect/supersede

WRITES
  _concept/blueprint/glossary.md                 — terms added/sharpened inline (per domain_model.md § Glossary format)
  _concept/decisions.md                           — ADRs appended when the 3-test gate passes (per domain_model.md § ADR format)

REFERENCES
  contracts/domain_model.md                       — glossary format, ADR format, the 3-test gate, the discipline
  contracts/concept_structure.md                  — canonical paths
  contracts/iron_laws.md                          — § 9 standalone questions
  contracts/skill_grammar.md                      — DSL keywords

# Constraints (placed early per skill_grammar.md)

MUST  ask each challenge as its own standalone assistant message (iron_laws § 9)
MUST  keep glossary.md free of ALL implementation detail — term → definition only (domain_model.md § Glossary format)
MUST  list rejected synonyms under `_Avoid_` for every term that has competing words — this is the anti-drift mechanism
MUST  treat ADRs as OPTIONAL and END-OF-SESSION: during the grill, only NOTE decision candidates in memory — write no ADR mid-session
MUST  after the grill, ask the user once whether to record the noted decisions as ADRs; write ONLY the ones the user opts into
MUST  apply the 3-test gate before OFFERING any decision as an ADR candidate: hard-to-reverse AND surprising AND a real trade-off (domain_model.md § ADR gate)
MUST  create glossary.md / decisions.md lazily — only when the first term/decision is actually resolved, never as empty scaffolding
MUST  update a term in place; append (never edit) an ADR — to change a decision, add a new one that supersedes and mark the old Status
MUST  get user confirmation on a definition before writing it

NEVER  add a general programming concept (timeout, retry, cache, DTO) to the glossary — only domain-specific terms
NEVER  write an ADR for an easily-reversed or obvious choice — it fails the gate
NEVER  silently overwrite or delete an existing glossary term or ADR
NEVER  invent a definition the user did not confirm

# ── Workflow ───────────────────────────────────────────────────────

STEP 1: Load the model
  - Read glossary.md if it exists (else note: first-term-creates-it).
  - Read decisions.md if it exists (cache existing ADRs to respect).
  - If `topic` given, scope to it; else scan features/ + datamodel/ for terms in use.

STEP 2: Find the friction (STANDALONE, one per message)
  For each fuzzy, overloaded, or drifting term, challenge it:
  - Against the glossary: "Your glossary defines 'cancellation' as X, but here you
    mean Y — which is it?"
  - Sharpen vagueness: "You said 'account' — do you mean the Customer or the login
    User? Those are different things. Pick the canonical term."
  - Concrete scenario: invent an edge case that forces a precise boundary between two
    concepts. "An Order with zero Items — is that still an Order, or a Draft?"
  - Cross-reference the code/datamodel: "Your model has one `Order` entity, but you
    just described partial cancellation — does an Order own Items, or is a Line the
    cancellable unit?"

STEP 3: Resolve → write the glossary entry (inline)
  When the user confirms a definition:
  - Write/update the term in glossary.md immediately (don't batch).
  - Format per domain_model.md § Glossary format: name, 1–2 sentence definition,
    `_Avoid_:` list of rejected synonyms. Group under a subheading if a cluster forms.
  - Confirm back: "Pinned. 'Customer' = <def>. Avoid: client, buyer, account, user."
  - If a decision surfaces and passes the 3-test gate, do NOT write it now — NOTE it in
    memory as an ADR candidate for the end-of-session offer.

STEP 4: End of session — offer ADRs (OPTIONAL, one message)
  Glossary work is done inline. ADRs are the user's call, asked once at the end:
  - If there are noted candidates, list them and ask:
    > "Before we finish — these decisions surfaced and look worth recording (each is
    >  hard to reverse, non-obvious, a real trade-off):
    >    1. <1-line>   2. <1-line>
    >  Want me to record any as ADRs? Reply with the numbers, or 'none'."
  - Append ONLY the ones the user opts into, to decisions.md per domain_model.md
    § ADR format (date + title + 1–3 sentences). Write nothing if the user declines.
  - If no candidate passed the gate, skip this step silently.

STEP 5: Recap
  > "Domain model updated: <N> terms pinned/sharpened, <M> ADRs recorded (of <K> offered).
  >  Glossary: _concept/blueprint/glossary.md. Decisions: _concept/decisions.md."

EMIT  [skaileup-domain-model] completed terms=<n> adrs=<m> topic=<topic|sweep>

CHECKLIST
  - [ ] glossary.md read (or first-term-creates-it noted)
  - [ ] Every challenge sent as a STANDALONE message
  - [ ] Every pinned term has a confirmed 1–2 sentence definition + `_Avoid_` list where synonyms compete
  - [ ] glossary.md contains zero implementation detail
  - [ ] No ADR written mid-session; candidates offered once at end, user opted in per-ADR
  - [ ] Every offered ADR passed all 3 gate tests
  - [ ] ADRs appended (not edited); superseded ones marked, not deleted
  - [ ] No general programming concepts added to the glossary
  - [ ] Recap names both output paths
