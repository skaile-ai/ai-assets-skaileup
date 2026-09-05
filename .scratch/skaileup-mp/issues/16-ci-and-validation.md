# 16: CI and validation — what replaces the DSL validators

**Type:** grilling
**Blocked by:** None (09 resolved)
**Status:** claimed

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

## Note from ticket 13

Two things land here, and the first is **not** something a path check can catch.

- **`mockup-feedback`'s journey branch has no target of that shape.** `-mp`'s shipped
  `scripts/triage.py:29-31` resolves `screen > feature > journey` to `<subdir>/<value>.md`.
  Two of the three subdirs are merely stale strings this ticket's path sweep will fix
  (`experience/screens` → `07_screens/`, `experience/features` → `05_features/`). The third
  is different in kind: **`04_journeys/` holds one `stories.yaml`**
  (`contracts/concept_structure.md:53`), so no file of the form `04_journeys/<value>.md` can
  ever exist. Repairing the string leaves a branch that resolves to nothing. It needs a
  ruling — drop the branch, or give journey annotations a real target.
- **`contracts/domain_model.md` is deliberately half-swept.** Ticket 13 fixed only what its
  writer ruling needed — the decision-log paths (`:9`, `:75-76`) and the Status enum. Still
  pre-0007 in that file: the **glossary paths** (`_concept/blueprint/glossary.md` at `:8`,
  `:24`, `:63`, `:67`) and `:133`'s **`skaileup-domain-model` skill, which does not exist and
  carries an old-scheme name.

## Note from ticket 17

Dead pointers found while reading the quality domain. None is ruled by 17 — each is a stale
string a path check should catch:

- `04_test-unit/SKILL.md:69` and `01_test-plan/SKILL.md:81` route the user to a skill named
  **`verify`**. No such skill exists (`grep '^name:.*verify'` finds only `debug-self-verify`,
  which 17 deletes).
- `08_standards-discover/SKILL.md:78` reads `_concept/05_techstack/stack.md`. Real path is
  `10_blueprint/techstack.md` under ADR 0007.
- **`contracts/acceptance_criteria.md` is wholly on pre-0007 paths** and its ownership table
  names `impl-plan-plan-vertical`, a skill ticket 07 deleted. Ticket 17 re-homes the ledger to
  `11_build/acceptance-criteria/<featureset>/<feature>.ac.md`; the rewrite is the port
  ticket's, but the file is a live member of ticket 09's fourteen and is stale today.
- **`cf__shared/` is cited in-body six times** — twice each by `standards-inject`,
  `standards-discover` and `standards-sync`. The prefix has not existed since the migration
  (it is the pre-migration name for `contracts/`). Two of those three skills die; the survivor
  (`quality-standards`) is rewritten anyway, so this is a *pattern* worth a check rather than
  three fixes.
- `13_impl-quality/contracts/evaluate-contract/CONTRACT.md`'s three stale paths
  (`_quality/audit-report.md`, `_quality/quality.yaml`, `_concept/4_testing/test_plan.md`) die
  with the file — it does not port.
