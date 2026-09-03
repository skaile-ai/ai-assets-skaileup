# 16: CI and validation — what replaces the DSL validators

**Type:** grilling
**Blocked by:** None (09 resolved)
**Status:** ready

## Question

Graduated from the map's "CI and validation" fog patch once ticket 09 resolved. Ticket 09
pushed `contracts/scripts/` out to this ticket deliberately: the validator story is one
decision with `flows/_meta/verify_flows.py`, which lives outside `contracts/`, so deciding it
from inside the contracts folder would have decided half of it.

Ticket 09 changed the ground under every one of these:

- **`verify_artifacts.py` + `tests/test_verify_artifacts.py` are dead on arrival** —
  ticket 09 dropped `artifacts.yaml`, the registry they validate. (`tests/` already deleted.)
- **`validate_skill_rules.py` validates the DSL grammar** (`ROLE`/`READS`/`WRITES`/`EMIT`)
  that ticket 03 removed and ticket 09 deleted the spec for (`skill_grammar.md`).
- **`verify_flows.py` has a future** — ticket 09 kept `flow.schema.json` as the flow
  contract's machine form, and this script is its only validator. **But see ticket 15:**
  if platform's newer flow-execution implementation validates against something else,
  this script may be validating a stale schema.
- **`lint_concept.py` + `validator_lib.py`** check `_concept/` artifacts against
  `golden_principles.md`, which ticket 09 *kept* on exactly that machine-reader argument.
  So this one has a live justification — the question is what it looks like after the
  contracts prune.
- **`ac_lib.py`** is why `acceptance_criteria.md` survived ticket 09 (shrunk to the EARS
  grammar). Same: live, but needs re-pointing.
- **The `pre-commit` hook** wires some subset of the above.

Decide:

1. **Which validators port to `-mp` at all**, given three of them validate deleted things.
2. **Where they live** in ticket 04's flat tree — `contracts/scripts/` no longer exists as a
   concept, and root hoists to `skills/` · `flows/` · `contracts/` · `docs/` (+ `profiles/`
   from ticket 09). A `scripts/` root entry is the obvious answer but has not been ruled.
3. **What runs them.** Today a pre-commit hook. `-mp` is a fresh repo, so CI is a free
   choice — hook, GitHub Actions, or nothing until the collection is populated.
4. **Whether `-mp` needs a validator the old repo lacks**, now that skill identity rests
   entirely on `name:` matching its directory (ticket 04). Nothing checks that today, and
   it is the one invariant that silently breaks every install path, flow `data.skill`
   reference, and grounding path if violated. Strong candidate for the one validator that
   earns its place.

## Answer

_(pending)_
