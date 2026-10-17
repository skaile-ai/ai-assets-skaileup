# 0004 — A contract survives only if it is read in-body

**Status:** superseded by 0017 ([the instruction tree mirrors the artifact tree](0017-the-instruction-tree-mirrors-the-artifact-tree.md))

## Context

28 contract files, 5,663 lines. Reference counts suggested heavy use, but they were inflated
roughly 2.5× by citations: `frontmatter.md` showed 86 references and had 13 real readers.
Deciding on raw counts would have kept three of the largest dead files.

## Decision

**The bar: a reader is a skill that consults the contract at a step in its body.** Naming a
contract under `REQUIRED BACKGROUND` or `REFERENCES` is a citation, not a read — and ADR 0003
deletes both blocks. A contract survives if more than one skill reads it in-body, or a machine
reads it.

**28 files → 14.** Survivors: `iron_laws` · `golden_principles` · `concept_structure` ·
`artifact_frontmatter` · `agent_patterns` · `elements_block` · `walkthrough_renderer` ·
`semantic_types` · `evaluator` · `feedback_loop` · `seed_data` · `domain_model` ·
`acceptance_criteria` · `README`. Plus `flow.schema.json` (machine form of the flow contract).

The related rule for data: **machine-read data lives where forge-concept already reliably
looks** — `SKILL.md` frontmatter, resolved via `name:`. That drops the `artifacts.yaml`
registry, and it keeps `prerequisites.inputs_optional` in frontmatter, because moving it to a
sibling file would cost the same out-of-scope forge-concept edit that reviving the registry
would.

## Consequences

- `flows.md` (588 lines, the largest contract in the layer) had **zero readers** and is gone.
- `frontmatter.md` becomes **`artifact_frontmatter.md`** — the asset/artifact distinction made
  explicit in the filename; `asset_frontmatter.md` is deleted.
- Concept-side frontmatter stays ~15 lines rather than ~4. Accepted cost.
- `profiles/` survives but leaves `contracts/` for the repo root: it is data the skills
  consume, not a contract.
- `iron_laws` and `golden_principles` are **not** in tension with ADR 0003 — that ADR removed
  `MUST`/`NEVER` prose from skill bodies, while these document machine-enforced gates, which
  is exactly the "check behind a named failure" it asks for.

---

**Superseded in part by [ADR 0008](0008-gates-live-at-the-step-they-bind.md)** (2026-09-05).
The `iron_laws` half of the final consequence no longer holds: `contracts/iron_laws.md` is
deleted, and gates are declared in `prerequisites.files[]` at the skill they bind and stated
at the step they bind. The `golden_principles` half is left standing but undecided — 0008
rules on gate registers only. The bar in **Decision** is unchanged; 0008 applies it.
