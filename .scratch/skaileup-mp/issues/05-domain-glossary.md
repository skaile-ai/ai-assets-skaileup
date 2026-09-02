# 05: The shared domain vocabulary (CONTEXT.md)

**Type:** grilling
**Blocked by:** 04 (resolved)
**Status:** ready

## Question

The stated goal is "a common domain understanding" taken from the mp skills. mp gets this
from `domain-modeling`: a single `CONTEXT.md` glossary plus ADRs. skaileup spreads the same
job across `contracts/domain_model.md`, `semantic_types.md`, `DOMAIN.md` files per domain,
and 25k lines of prose that each redefine terms locally.

Write `-mp`'s `CONTEXT.md`: the ubiquitous language every skill uses without redefining.
Terms that need pinning down, at minimum:

- **artifact** vs. **asset** vs. **output** — three words for overlapping things today.
- **feature** vs. **featureset** vs. **story** vs. **slice** vs. **screen** vs. **component**.
- **slice** — used for both the per-feature concept dossier and the per-feature impl loop.
- **dossier**, **frozen**, **tier**, **flow**, **profile**, **gate** (hard vs. soft), **seed mode**.
- **concept** vs. **blueprint** vs. **implementation** as tree-level names.
- Where mp's vocabulary is better (**tracer bullet**, **vertical slice**, **frontier**,
  **deep module**, **seam**) and should replace the local term outright.

Decide also: does `-mp` keep per-domain `DOMAIN.md` files, or does one `CONTEXT.md` + ADRs
replace them?

## Answer

_(pending)_
