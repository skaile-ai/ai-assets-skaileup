# 16: CI and validation — what replaces the DSL validators

**Type:** grilling
**Blocked by:** None (09 resolved)
**Status:** resolved

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

**Nothing ports. One script replaces all seven, and its first run found six defects no
ticket had noticed.**

`scripts/check.py` (447 lines) + `scripts/test_check.py` (28 cases) + one GitHub Actions
job. Landed `e1fbfb4` on `-mp` `main`, not pushed. `python3 scripts/check.py` →
`8 skill(s) · 0 flow(s) · 0 error(s)`.

### 1. Which validators port: none of them

Seven scripts, and the brief was right that the ticket's own list omitted one
(`docs/scripts/audit.py`, which is CI job #1). Each dies for its own reason, and only one
of the seven is a close call:

| script | why it does not port |
|---|---|
| `verify_artifacts.py` + its pytest | validates `artifacts.yaml`, which ticket 09 deleted; its restatement detector scans `MUST`/`NEVER` lines ticket 03 removed |
| `validate_skill_rules.py` | is the DSL enforcement path; ticket 03 removed the DSL and 09 deleted its spec. Called by nothing — zero refs in CI, the hook, or any SKILL.md |
| `audit.py` | gates on `stage` and `tags`, which ticket 01 showed nothing reads, and on `stage: stable ⇒ validator.py`, whose premise ticket 14 removed. Its one live field, `version`, is check 2 of the new script |
| `lint_concept.py` | see §4 |
| `ac_lib.py` | see §5 |
| `validator_lib.py` | see §3 |
| `verify_flows.py` | **its rules survive; the file cannot.** Its three hard dependencies are all things `-mp` removed deliberately: `skaile.yaml`'s `assets:` block (absent by ticket 11's design, so its contract check inverts from a guard into a blanket failure), a hardcoded 17-flow registry, and the two-level `skaileup/contracts/` layout. Rewritten, not lifted |
| `pre-commit` | see §6 |

### 2. What the one script checks

Only checks whose failure mode is **silent**. A loud failure needs no validator.

**Skills.** `name:` == directory character for character · `version:` present · `SKILL.md`
≤ 140 lines (ticket 03's ceiling, a hard fail — a warning in a repo with no installed hook
is a no-op) · every `prerequisites.files[].path` starts at a real top-level entry of the
artifact tree · every cited `contracts/<file>` exists.

**Contracts.** Same citation check over the contracts themselves.

**Flows.** `id` == directory == filename stem · top-level `name:` present (satisfies
platform's `validateFlow` and forge-concept's loader at once) · unique node ids · no
dangling edge endpoints · no self-loops · every node declares `data.phase` in the
three-value enum · every `data.skill` resolves to a real `skills/<name>/` · `parentNode`
resolves to a group node · router targets resolve to node ids · `requires:` skill-set
exactly equals the node-skill set and flow-set exactly equals the sub-flow targets ·
`contract:` refs resolve to `contracts/<name>.md` on disk.

**The legal top-level set is parsed out of `contracts/concept_structure.md`'s fenced
tree, not restated in the script.** Renaming a directory in the contract renames it in the
check; the two cannot drift. A test pins that.

**`requires:` exactness earns its place despite having no runtime reader for *exactness*.**
The brief posed this as a house rule failing ticket 09's machine-reader bar. It is not:
`requires` drives transitive install, so a **missing** entry means the skill is never
installed and forge-concept then runs the node with a generic prompt while
`requirements.get.ts` reports `satisfied: true`. That is a live silent failure. Only the
*extra*-entry half is house discipline, and it is kept because a manifest that over-declares
stops being readable as the flow's dependency set.

### 3. `flow.schema.json` is deleted, not narrowed

Ticket 15 said "narrowed or not at all"; this is the ticket that executes it, and the answer
is not at all. `-mp/contracts/flow.schema.json` was byte-identical to the stale 434-line
original: it invented a `gate` node kind (0 uses) and a `review-loop` edge type (1 use,
already a no-op), required `position` on all five node kinds that nothing reads, and was
`additionalProperties: false` at 27 sites against a `z.looseObject` runtime — so it would
have rejected workspaces' own `metadata:` spelling.

Its one live asset was the `data.phase` enum, the only machine check anywhere of ticket 04's
every-node-declares-phase rule (`flow-phases.test.ts:50` pins that forge-concept silently
swallows `phase: "banana"`). That enum is four lines of Python.

**The decisive argument is not size but expressiveness.** The sharpest flow rule — an edge
without `type: "flow"` orders nothing — is a property of the *graph*, not of any node or edge
shape, so no JSON Schema can state it. Hence the check is **reachability from `entry` along
flow-typed edges**, not "every edge has a `type`": one assertion that subsumes the untyped
edge, the `review-loop` no-op, an `optional`-only path, and a genuinely disconnected
subgraph. Ticket 15 handed over four cheap checks; three are in, and the fourth is replaced
by the stronger form. Seven tests cover it.

### 4. `lint_concept.py`: refused, and it takes ticket 09's justification with it

Two independent disqualifications, either sufficient.

**It validates a target project, so nothing here can run it.** Every other validator checks
the collection's own files. `lint_concept.py` needs a `_concept/` that exists only in
someone else's repo; its only invocations today are two prose lines, in an orchestrator
skill and a `SOUL.md`, both files `-mp` does not have.

**Its model half is a category error.** `check_model` / `check_seed` / the entity half of
`check_cross_references` open `postxl-schema.json` and demand PascalCase models, camelCase
fields and `Id` suffixes — the exact inverse of `golden_principles.md:13,23`, which mandates
snake_case in the semantic layer and calls `postxl-schema.json` **derived**. `model.json`,
the file the contract calls canonical, appears nowhere in the linter. That is a
PostXL-shaped check inside a template-agnostic collection, and it is sharper now than the
brief could state: `concept_structure.md:183-187` makes `postxl-schema.json` one of **four**
formats chosen by `techstack.md`. Same category error ticket 06 used to kill the `framework`
renderer.

The structure/frontmatter/cross-reference half survives as **prose steps inside an `ops-`
skill** — a 140-line skill can carry it — which is **ticket 21's** to place, not this one's.

**Consequence stated rather than swallowed:** ticket 09 kept `golden_principles.md` on the
argument that a machine reads it, and `lint_concept.py` *was* that machine. That
justification is now gone. → **ticket 22**, which is re-ruling exactly this class of file.

### 5. `ac_lib.py`: refused, and follows the ledger to ticket 17

Live code, dead owners. Both callers are skills ticket 07 collapsed; the EARS regex ticket 09
kept `acceptance_criteria.md` for lives in two *other* files ticket 07 also deleted, and
matches only the `WHEN…SHALL` form; and ticket 19 already found the acceptance-criteria
ledger **has no home in ADR 0007 and does not port**, handing it to ticket 17. So the checker
question is downstream of a ledger question that is not this ticket's.

**Ticket 09's shrink was aimed at the wrong half** — it kept `acceptance_criteria.md` "shrunk
to the EARS grammar", which is precisely the section no code reads, while the ledger
structure is what `ac_lib` actually validated. If the contract survives ticket 17, it should
shrink to the ledger. The dangling `contracts/scripts/ac_lib.py` citation is repaired here
(the new citation check flagged it); the contract's shape is left to 17.

### 6. `validator_lib.py`: refused — and per-skill validators are not a standing cost

The brief framed this as "~20 skills' fate" and ticket 03's promise that a guardrail survives
"as a named failure with a check behind it". Ticket 14 already answered it in practice, and
`-mp` had silently converged: **all three shipped `validator.py` files are self-contained**,
none imports `validator_lib`, and two of the three live in `references/<renderer>/` as a
*step of the skill*. A validator ships only where a skill has a mechanical artifact to check
— today three of eight skills, not eight of eight. `audit.py`'s `stage: stable ⇒ validator.py`
rule dies with the premise.

### 7. Actions, one job, now — and no hook

The house pattern measured across eight repos: GitHub Actions, per-repo, hand-rolled, and
**no active git hook anywhere**. The old repo's hook was never installed in this checkout
(`.git/modules/.../hooks/` holds only `.sample` files), two of its four gates are dead, and a
third duplicates `audit.py` verbatim. No hook ports.

**Now, not when the collection is populated** — the two sibling asset collections run no CI
at all and that was the live precedent for waiting, but the checker is not speculative: its
first run had ten real defects to report, and a hook only fires for people who install it.
`.github/workflows/ci.yml` is one job: `check.py`, then `pytest scripts/test_check.py`.

Layout: **root `scripts/`**. `flows/_meta/` is out because the script is no longer the flows'
— it spans both trees and the flow half needs the skill half's output to resolve `data.skill`.

### 8. The sweep, and what it turned up

The first run reported the **ten stale `prerequisites.files[].path` entries** ticket 19
predicted, and **six dangling contract citations nobody had counted** — three of which appear
in no brief and no ticket: `acceptance_criteria.md` → `contracts/scripts/ac_lib.py`,
`elements_block.md` → `contracts/frontmatter.md` (ticket 09 renamed it to
`artifact_frontmatter.md`) and → `contracts/tests/elements_block_examples.md` (a fixture that
never ported). **The citation check paid for itself on its first run**, which is the
strongest evidence for it: it was the one check added beyond the ticket's four questions.

Repaired: all ten prerequisite paths and the body prose behind them, across the four mockup
skills · `domain_model.md`'s four glossary paths and its phantom `skaileup-domain-model`
skill, which is now the globally-installed `domain-modeling` (ticket 02 ported its content
into this contract; the collection ships no skill of its own, because *where the artifacts
land* is the only skaileup-specific part) · `contracts/README.md`, stale wholesale — it still
described the old repo's `cf/`+`saxe/`, `scripts/` and `DOMAIN.md` — rewritten as an index of
the thirteen survivors, and it records what is deliberately absent · the two `elements_block`
citations, whose Validation section now states plainly that no validator ships for the block
because the two renderers already reject what they cannot render.

`evaluator.md` was found to have **zero readers in `-mp`** while writing that index. Not ruled
— its readers are the `quality` and `ops` skills tickets 17 and 21 are writing — but recorded
in the README as kept against them.

### 9. The `mockup-feedback` journey branch — ruled, but not by this session

Ticket 13 handed over a `journey` branch that could not resolve (`04_journeys/` holds one
`stories.yaml`, so no `04_journeys/<value>.md` can exist). This session's recommendation was
to drop `journey` and keep `feature`. **A concurrent session had already ruled the opposite
split, on better evidence**: `journey` routes to the whole of `stories.yaml` (the value names
a journey *within* the file, so patching addresses a section, not a path), and **`feature` is
the branch that dies** — the overlay's `resolveTarget` emits `element/screen/journey/route/
provisional` and `walkthrough_renderer.md` declares no `data-spec-feature` attribute, so
`feature` was routing a key no renderer produces. Left as they ruled it; this ticket did only
the path half it was handed — `triage.py`'s two constants and the whole fixture tree moved to
ADR 0007 names, with their new `test-routing` case green afterwards.

### Accepted residue

- **Four files are entangled with a live concurrent session** (`mockup-annotate/SKILL.md`,
  `mockup-feedback/SKILL.md`, `triage.py`, and the feedback fixtures) — they carry both this
  ticket's path sweep and that session's in-flight work, so they are **left uncommitted** for
  it to land. The path fixes are in the working tree and `check.py` is green on it, but they
  are not in `e1fbfb4`.
- **`mockup-annotate/validator.py` still sits at the skill root**, not under `references/`,
  inconsistent with ticket 14's own ruling. Recommended for the move and approved, then **not
  done**: the concurrent session has that exact file open, and moving it plus its two
  invocation paths under a live editor risks more than the tidiness is worth. One `git mv` and
  two path edits whenever that session lands.
- **The flow half has no live subject.** `flows/` is empty, so `test_check.py`'s 28 cases are
  the only thing exercising it. The reachability model in particular (group nodes excluded as
  containers, routers conferring reachability without an edge) is asserted against synthetic
  flows; **ticket 10 should expect to adjust it** when the real flow set lands.
- The acceptance test remains as weak as the brief measured — five shallow assertions,
  self-skipping unless SSH to the old repo resolves. Strengthening it is a forge-concept edit
  the map rules out of scope, and it is **why the collection needs a checker of its own**
  rather than an argument for changing it here.

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
