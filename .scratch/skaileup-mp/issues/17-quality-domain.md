# 17: The `quality` domain — 13 skills, and which of them still have a job

**Type:** grilling
**Blocked by:** None (07 resolved)
**Status:** resolved

## Question

Graduated from ticket 07, which held `13_impl-quality` out deliberately: 16 + 13 skills is
more than one session holds, and ticket 07 only needed one thing from this domain — the
list `build-implement` calls by name. **That is settled and not open here: `build-implement`
names `tdd` and `code-review`, nothing else, and the test pyramid stays flow nodes after
the slice.**

The domain is 13 skills / 2,833 lines: `test-plan` · `eval-code` · `audit` · `test-unit` ·
`test-integration` · `test-e2e` · `ready` · `standards-discover` · `standards-inject` ·
`standards-sync` · `debug-self-verify` · `debug-handoff` · `review-feature`.

Ground already fixed elsewhere:

- **Ticket 04** put this in the `quality` domain, and drew the `quality`/`ops` line at the
  artifact under inspection: `quality` checks `src/`, `ops` checks `_concept/`. Some of
  these 13 are on the wrong side of that line — `ready` inspects `_concept/` completeness.
- **Ticket 07 deleted `debug-handoff`** (314 lines, flow-orphaned, ticket 12's handoff).
  **`debug-self-verify` (305, also flow-orphaned) arrives here undecided.**
- **Ticket 02's split verdict** on `diagnosing-bugs`: absorb its Phase 1, and it says
  skaileup's debug pair "does the exact thing this skill forbids". Read that before ruling
  on the debug skills.
- **Four are referenced by zero flows**: `test-plan`, `standards-sync`, `debug-self-verify`,
  `debug-handoff` (now deleted).

Decide:

- The surviving set and, for each of the 13, merge / step-inside-another / dies.
- Whether the three `standards-*` skills are one skill, or a contract plus one skill.
  `standards-inject` (108 lines) is a loader called at the start of other skills — that is
  the shape of a contract, not a skill.
- Whether `test-unit` / `test-integration` / `test-e2e` are three skills or one with a
  level parameter, given ticket 07 made them flow nodes rather than calls.
- Where `ready` lands, given ticket 04's `quality`/`ops` line.
- What survives of the debug pair once `diagnosing-bugs` is a global install called by name.
- `eval-code` · `audit` · `review-feature` against the global `code-review`: what does each
  add that `code-review` does not?

---

## Answer

**13 skills / 2,833 lines → 4: `quality-review` · `quality-test` · `quality-e2e` ·
`quality-standards`.** Nine die. The through-line is ticket 02's mechanism in its sharpest
form: this domain's four globally-installed competitors (`code-review`, `tdd`,
`diagnosing-bugs`, `improve-codebase-architecture` — all four verified present in
`~/.claude/skills/`) already own *how to look at code*, so what survives here is never
review technique. It is the three things a global skill cannot do: **resolve inputs from
`_concept/`**, **carry axes the global skill does not have**, and **write a verdict a flow
can branch on**.

### The surviving four

| name | from | what it is |
|---|---|---|
| `quality-review` | `review-feature` (+ the parts of `eval-code`/`audit` that survive) | Hands `code-review` the two inputs it otherwise asks a human for, then adds what it lacks |
| `quality-test` | `test-unit` + `test-integration` | One test-generation skill, level as a parameter |
| `quality-e2e` | `test-e2e` | Not a level — a different tool, and the only flipper of ledger rows |
| `quality-standards` | `standards-discover` | Reads an existing codebase, writes `02_grounding/standards/` |

### 1. The review trio → one skill

All three dispatch **the same three sub-agents from the same 64-line file**, and
`appbuilder-complex` runs that trio **three times over the same code** (`q-eval-code` →
`q-audit` → `quality-gate`'s optional `q-review-feature`). Against `code-review`'s twelve
named Fowler smells each with a fix, plus *"the repo overrides"* and *"always a judgement
call"*, the 18 generic bullets are the thinner copy. **Everything in these three about how
to look at code is `code-review`'s.**

**`quality-review` is ticket 07's `implement` mechanism inverted.** `implement` (15 lines)
is small because it *names* `tdd` and `code-review` instead of restating them; this skill is
small because it names `code-review` and supplies the two inputs `code-review`'s own body
says it has to ask for — *"Whatever the user said is the fixed point […] If they didn't
specify one, ask for it"* and *"If nothing is found, ask the user where the spec is"*. It
resolves the fixed point from the `commits[]` / `source_files[]` back-links and the spec
from `05_features/<featureset>/<feature>.md`, and refuses when they are empty. On top it
keeps exactly what no global skill has:

- the **security** and **a11y** axes — `code-review` has neither, and that is what
  `analysis_checklists.md` is genuinely for;
- the **AC-ledger honesty check** — *"any criterion with Status `pass` whose assertion the
  code visibly cannot satisfy is a finding"*, auditing the ledger's own truthfulness;
- **never review as the agent that implemented the slice**;
- reading `refactor.md` so accepted debt is context, not a finding;
- a build check first, stopping before analysis if it fails (`eval-code`'s one real
  discipline) and a verdict artifact.

It also inherits `code-review`'s **anti-merge rule**, which `review-feature` violated today
by ranking logic/security/ui-ux and spec findings into one list — the exact collapse the
two-axis separation exists to prevent.

**`audit` dies.** Its whole-repo, no-fixed-point scope is `improve-codebase-architecture`'s
(71 lines, sharper method — deepening opportunities, the deletion test, hot-spot scoping from
`git log`). Its Phase 2 is `ops-review`'s by its own admission twice over: `audit:52` sends
the user to `review` for concept-structure work, and `analysis_checklists.md` calls Phase 2
*"Subset of `review` (mechanical checks only)"* — then Phase 2 does it anyway
(`03_audit/SKILL.md:127-131`). It was also the only skill in the domain that **edits code**
under a review banner.

**`eval-code` dies as a skill, survives as two lines.** Build+test belongs to the implement
step in the model this map adopted — mp's `implement`: *"Run typechecking regularly, single
test files regularly, and the full test suite once at the end. Once done, use /code-review"* —
and ticket 07 already put `tdd` + `code-review` inside `build-implement`. Its `scaffold`-scope
smoke test (build + lint + types, no analysis) is `build-scaffold`'s own done-check →
**ticket 18**. Its verdict artifact — **the only artifact in this domain with a real reader**
— is inherited by `quality-review` (see § 5).

### 2. The test trio → two, split at the tool and not at the level

**`test-unit` + `test-integration` merge.** They are the same five-phase machine (discover
via two sub-agents → generate → verify → report), both hard-gate on `package.json` +
features, both take `test_plan.md` as Optional, both end in the same two tables, both carry a
near-identical Common Mistakes grid. The flows already prove level is **data, not structure**:
today's subsets are `{u}` / `{u,e}` / `{u,i}` / `{u,i,e}` — an arbitrary per-tier selection,
which is what a set-valued parameter looks like — and the flow layer already parameterises
one of the three (`q-test-e2e` carries `parameters: {mode: '${e2e}'}`). Same argument ticket 06
used to move the renderer choice out of two sibling flow nodes and into data. → **ticket 10**
inherits `parameters: {levels: [...]}`.

**The gate cost lands on the intersection, not the union.** One node means one frontmatter,
and integration hard-gates on `model.json` + `.env.example` that `appbuilder-mvp`'s project
may not have. So `quality-test`'s frontmatter gates on features + `package.json` only, and
"no data model or no `.env.example` → the integration level does not apply" is a check **at
the step that needs it** — ticket 03's rule, a constraint stated where it binds rather than a
frontmatter gate that blocks a tier.

**`quality-e2e` stays separate because e2e is not a level.** It is a different *tool*
(`agent-browser`, with a `uname -s` platform gate the other two have no analogue of), it
derives journeys from `stories.yaml` rather than from features, and it is the only one of the
three that writes an artifact outside the codebase. Merging it would drag a platform check
into a skill that mostly does not need a browser.

**The stack boilerplate drops.** `test-unit` is 24% fenced vitest/Vue, `test-integration` 40%
fenced (DB setup, an `asUser(role)` helper). Both bodies already say *"read 2-3 existing test
files to learn conventions"*, and `impl-architecture/templates/template-*` already carry stack
facts — a hard-coded vitest snippet is a third copy that goes stale first. The stack-neutral
core survives: unit's **What to Test / What NOT to Test** pyramid tables, integration's
endpoint inventory and its three-way test-database choice.

### 3. `ready` is not a `quality` skill

By ticket 04's line — `quality` checks `src/`, `ops` checks `_concept/` — this is not close.
Every path in its `READS` is under `_concept/`, its Context Budget says `Never load: Source
code`, and its body says `WRITES (none — read-only audit skill)`. It is also the **fourth**
thing checking `_concept/` cross-reference integrity, alongside `ops-eval-concept` (same
completeness matrix, different verdict grammar), `ops-review`, and `audit` Phase 2 — and its
own *"When NOT to Use"* routes both of its neighbours away.

**This ticket rules only that it leaves `quality`.** Merge-or-keep is **ticket 21**'s, which
owns `ops-eval-concept` and `ops-review`. Carried across with it: the two things only `ready`
has — a **remediation command naming the exact skill** that fills each gap, and its position
as a gate — plus the fact that the flow and the skill **disagree about when it runs**
(`07_ready:66` *"Use before E2E testing"* vs `quality-gate.flow.yaml:73-82`, which places
`q-ready` **after** `q-test-e2e` under the label *"Release Ready"*). Also to **ticket 22**:
iron law 6 names this skill.

### 4. The debug pair dies whole

Ticket 02's verdict holds and is sharper than stated — four collisions, not a nuance:

1. **Hypothesis before the loop.** `diagnosing-bugs` Phase 1: *"jumping straight to a
   hypothesis is the exact failure this skill prevents. No red-capable command, no Phase 2."*
   `debug-self-verify` STEP 1 asks for the hypothesis **with a confidence tier** before STEP 2
   inventories a single command, then branches on it.
2. **The protocol need never have been run.** `diagnosing-bugs` requires one command *"already
   run at least once"*; `debug-self-verify`'s `CHECKPOINT protocol_review` accepts *"save for
   later"* as a terminal state.
3. **The red signal is optional** in both the schema and `validator.py` — so a protocol
   validates green with nothing that can go red, and STEP 4's ordering starts at lint and
   typecheck, which cannot go red on a behavioural bug. That is the *"runs without erroring"*
   failure the global skill names.
4. **HITL.** `debug-self-verify`: *"NEVER block waiting for human-in-the-loop verification"*.
   `diagnosing-bugs` ships `scripts/hitl-loop.template.sh` for exactly that case.

Its four genuine additions are **artifact and interview mechanics, not diagnosis** — and it
covers one of `diagnosing-bugs`' six phases while inverting the first. `_debug/<id>/` has no
entry in ADR 0007's eleven folders, and minting a twelfth for this is the wrong trade; the
same trade ticket 12 already made against `handoff`. **`quality-review`'s `needs_changes`
branch emits `diagnosing-bugs` by name**, which also repairs the four live sites still
pointing at the already-deleted `debug-handoff`. Accepted loss: a persisted `protocol.md`
with a machine validator.

### 5. Standards: three skills → one, and the loader was always a contract

**`standards-inject` dies into `agent_patterns.md`.** Its five workflow steps
(`09:64-70`) are `contracts/agent_patterns.md:96-104 § Standards Injection` step for step, in
the same order, including the no-error-if-empty clause — and ticket 09 already kept that
contract on 9 in-body readers. It has **zero in-body callers out of 95 skills**, writes
nothing, and the auto-wrap that justified it (`modes.standards.inject_skill`) lives in a block
ticket 15 found has **no reader in any host**. The artifact's only two real readers
(`eval-code` → now `quality-review`, and `review-feature`) already read `index.yml` **directly,
never through the loader**. A skill with no callers, no writes, and a body that is a match
algorithm over a YAML index is a read.

**`standards-sync` dies.** Both its inputs are fictional: `cf__shared/profiles.json` does not
exist and neither does the `cf__shared/` prefix, and ticket 05 retired "profile" for exactly
that sense (→ **template**). Its own body calls itself *"an optional quality-phase step"*, and
the one flow that touches standards runs `discover → inject` and stops.

**The index-schema contradiction is already settled and did not need ruling here.** ADR 0007's
landed tree documents `02_grounding/standards/index.yml` as *"fast matching by `applies_to` +
keywords"* (`-mp contracts/concept_structure.md:41-43`) — so `standards-discover`'s schema is
the one that survives and `evaluate-contract`'s `scope`/`auto_discovered` variant dies with
that contract (§ 7). The stale `applies_to: [implement-feature, architecture]` example names
pre-Phase-1 skills and is rewritten at port time.

**Naming.** `quality-standards` reads an **external** codebase and writes grounding, so
ticket 04's two-way line does not cleanly place it. It stays `quality-` because it inspects
source; making it a tenth `concept-` skill would reopen ticket 08. → **ticket 10**:
`skaileup-concept-reverse` loses its `inject` node.

### 6. `test-plan` dies

Zero flows run it, and its two readers (`test-unit`, `test-integration`) both mark it
`Optional` and **neither has a step that branches on its presence**. Its distinctive job — AC
traceability with `AC` / `AC✓` columns — is the same accounting the `.ac.md` ledger does
downstream, with three producers and a real consumer. A second, unread, upstream copy is the
duplication tickets 03 and 09 kept cutting. The pre-implementation "what should we test" is
already carried by the **EARS acceptance criteria in the feature spec** (`spec-feature`) and
the per-slice criteria in `build-plan`. It also read `_concept/` and wrote `_concept/` — a
`quality`-named skill entirely on the `ops` side of ticket 04's line.

This answers one of the three placements ticket 08 handed here: **`testing/` needs no entry
in `11_build/`.**

### 7. Artifacts and contracts

**The acceptance-criteria ledger gets a home, shrunk to the join** — ticket 19 handed this
here after finding `_implementation/acceptance_criteria/` is not a top-level entry in ADR 0007
and declining to mint a twelfth folder. It lands at
**`11_build/acceptance-criteria/<featureset>/<feature>.ac.md`** — under `11_build/`, no new
root. It keeps the one job nothing else does (the per-criterion **status spine** answering
"is this feature actually done") and loses the duplication: today's `Source` column copies the
EARS line **verbatim** out of the spec, so rows become `AC-n` plus a citation into
`05_features/<featureset>/<feature>.md`, never a copy. Ownership moves off deleted skills —
created by **`build-plan`** (already the skill that claims every criterion), flipped by
**`build-implement`** and **`quality-e2e`**, read by `ops-trace`. Not the slice dossier:
ticket 19 decoupled `slice_id` from `feature_slug`, so a per-feature ledger no longer maps
onto one dossier.

**One verdict artifact, not two.** `quality-review` writes
**`11_build/reviews/<feature_slug>.yaml`**, inheriting `_implementation/eval-code.yaml`'s real
reader (the orchestrator's `verdict` branch, `skaileup-build` STEP 9) and `review-feature`'s
per-feature scope, keeping the pinned rule (`approve` ⇒ zero critical **and** zero high).
`_implementation/review/<slug>.yaml` had **0 in-body readers** and `audit-report.md` had 0 —
neither survives as a second file. `quality-e2e`'s screenshots stay in the codebase beside the
tests (test output, not `_concept/` artifacts) and `e2e-test-report.md` dies: opt-in, zero
readers.

**Ticket 08's other two placements go to ticket 21.** `quality.yaml` and `eval-concept.yaml`
are written by `ops-review` and `ops-eval-concept` and read only by the orchestrator, whose
port is still fog. 17 should not place artifacts no surviving `quality` skill writes. Noted
for 21: ticket 08's list of three was drawn on the artifact's *shape*, which is why
`eval-code.yaml` and `review/<slug>.yaml` — the same "findings about work" — were missing
from it; drawn on the *writer*, the split is two for 21 and one for here.

**Contracts.** `contracts/evaluator.md` **survives** — it has four in-body readers and three
of them are ticket 21's `ops-eval-*` skills, so it clears ticket 09's bar independently of
this domain; `quality-review` is the fourth and states the adversarial stance **once**,
by citation. Today `review-feature` states it three times over (contract, sub-contract, and
inlined "in case evaluate-contract is not installed"). **`evaluate-contract/CONTRACT.md` does
not port** — it was never in `-mp`, has zero `requires:` from any skill, and its table is
stale on three rows. **`analysis_checklists.md` becomes
`skills/quality-review/references/checklists.md`** — one skill's material now, not three
skills' shared file, which is the only reason it looked contract-shaped.

### Handed off

- **Ticket 10** — `quality-test` takes `parameters: {levels: [...]}` (precedent:
  `q-test-e2e`'s existing `mode`); `quality-gate` collapses from five nodes to three
  (`quality-test` → `quality-e2e` → `quality-review`), losing `q-eval-code`, `q-audit` and
  `q-ready`; `appbuilder-complex` loses `q-eval-code` + `q-audit` outright;
  `skaileup-concept-reverse` loses its `standards-inject` node; `skaileup-stepwise`'s `q-ready`
  waits on ticket 21.
- **Ticket 16** — the dead pointers found while reading, none of them ruled here:
  `test-unit:69` and `test-plan:81` route to a skill named **`verify`** that does not exist;
  `standards-discover:78` reads `_concept/05_techstack/stack.md` (real path
  `10_blueprint/techstack.md`); `contracts/acceptance_criteria.md` is wholly on pre-0007 paths
  and names `impl-plan-plan-vertical`, a deleted skill; `evaluate-contract`'s three stale
  paths die with the file. Plus the `cf__shared/` prefix, cited in-body six times across the
  three `standards-*` skills, for a directory that has not existed since the migration.
- **Ticket 18** — `eval-code`'s `scaffold` scope (build + lint + types, stop on failure) is
  `build-scaffold`'s done-check, not a skill.
- **Ticket 21** — `ready` (merge into `ops-eval-concept` or keep, carrying the per-gap
  remediation command and the gate-position disagreement); `quality.yaml` and
  `eval-concept.yaml` placement under `11_build/`; whether `ops-review` keeps the
  `_concept/` structure-integrity work `audit` Phase 2 was doing in parallel.
- **Ticket 22** — iron law 6 names `ready`, which does not survive in this domain.
- **The port ticket (23)** — writing the four is execution, not decision. It also carries two
  edits outside its own domain that this ticket authorised but did not make: **`build-plan`
  gains the `.ac.md` write** and **`build-implement` gains the flip**, both against landed
  skills, and `contracts/acceptance_criteria.md` is rewritten off its pre-0007 paths and down
  to the join.

### Register (forge-concept, deferred)

No new entry. The orchestrator's `verdict` branch is the domain's only real reader and the
orchestrator is *ours*, still in the map's fog — a port question, not a host constraint.
