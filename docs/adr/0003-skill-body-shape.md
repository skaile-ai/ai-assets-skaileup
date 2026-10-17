# 0003 — 140-line ceiling; constraints at the step they bind

**Status:** superseded by 0015 ([the instruction tree mirrors the artifact tree](0015-the-instruction-tree-mirrors-the-artifact-tree.md))

## Context

Skill bodies ran to 1,133 lines. A custom DSL (`ROLE / READS / WRITES / STEP / EMIT /
CHECKLIST / MUST / NEVER / …`) structured them, and a `MUST`/`NEVER` block collected the
hard rules at the bottom, away from the steps they governed.

Two skills were ported end-to-end to test the replacement shape before committing to it.

## Decision

Prose plus `references/` for the long tail, with a **ceiling of 140 lines including
frontmatter** — the measured maximum of the collection this shape was borrowed from. Both
ports came in under 110 (`concept-brief` 289 → 80, `mockup-walkthrough-astro` 1,133 → 110).

**No `MUST`/`NEVER` block.** Every constraint is stated positively at the step it binds, as
its consequence rather than as a rule; a hard guardrail survives as a **named failure with a
check behind it**.

Dropped as caches of something else: `READS`/`WRITES` (frontmatter and the contracts have
it), `CHECKLIST` (the validator has it), `## Depth Behavior` / `## Standalone Mode` /
`## Context Budget` (they describe the collection, not the skill).

## Consequences

- The DSL loses nothing measurable: `CHECKLIST` restated `validator.py`, `ROLE/READS/WRITES`
  restated frontmatter, and **`EMIT` is read by no code at all**.
- The astro skill's bulk was **duplication of `contracts/walkthrough_renderer.md`**, not
  length — ~200 lines of one step already existed in the contract.
- Collection-wide, **44% (10,784 of 24,646 lines) is mechanically removable** before
  rewriting any prose: frontmatter 18%, code fences 9%, boilerplate sections 16%.
- The template lives in `docs/`, not `contracts/` — no runtime reader.

Template: [`../skill-template.md`](../skill-template.md). Ports:
[`../examples/`](../examples/).
