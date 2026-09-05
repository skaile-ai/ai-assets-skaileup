# 23: Port the `quality` domain — write the 5 skills

**Type:** task
**Blocked by:** None (17, 21 resolved)
**Status:** claimed (2026-09-05, parallel port sessions)

## Question

Nothing to decide — ticket 17 settled the shape, this writes it. Same relation 14 has to 06
and 19 has to 07.

**Unblocked 2026-09-05 by ticket 21**, which merged `ready` into `ops-review` (so nothing
`ready`-shaped is written here), placed `quality.yaml` at `11_build/review.yaml` and killed
`eval-concept.yaml` with its skill — **and added a fifth skill to this port, `quality-release`.**
See the note from ticket 21 below.

Write five skills into `skills/`, each `SKILL.md` under the 140-line ceiling (ticket 03),
dir name == `name:` exactly (ticket 04), no `MUST`/`NEVER` block, `data.phase` declared by
the flows and not by the name:

- **`quality-review`** — resolves `code-review`'s two missing inputs (fixed point from the
  `commits[]` / `source_files[]` back-links, spec from `05_features/<featureset>/<feature>.md`)
  and calls it by name; refuses when the back-links are empty. Adds the **security** and
  **a11y** axes from `references/checklists.md`, the **AC-ledger honesty check**, "never
  review as the agent that implemented", and `refactor.md` as context so accepted debt is not
  a finding. Build check first, stop on failure. Cites `contracts/evaluator.md § Stance` once
  rather than restating it. Writes `11_build/reviews/<feature_slug>.yaml`
  (`approve` ⇒ zero critical **and** zero high). `needs_changes` emits `diagnosing-bugs`.
  Inherits `code-review`'s anti-merge rule — do not rank the axes into one list.
- **`quality-test`** — `test-unit` + `test-integration` merged, level as a parameter. Hard
  gates on features + `package.json` only; "no data model / no `.env.example` → integration
  does not apply" is a check at the step, not frontmatter. Keeps the What to Test / What NOT
  to Test pyramid tables and the endpoint inventory + test-database three-way choice. **No
  vitest/Vue fences** — read existing tests for conventions.
- **`quality-e2e`** — `test-e2e` essentially intact: `agent-browser`, the platform gate,
  journeys from `stories.yaml`. Flips `.ac.md` Status rows. Screenshots stay beside the tests
  in the codebase; `e2e-test-report.md` does not port.
- **`quality-standards`** — `standards-discover` only, writing
  `02_grounding/standards/{index.yml, <domain>/}` with the `applies_to` + `keywords` schema
  ADR 0007 already documents. Its stale `applies_to: [implement-feature, architecture]`
  example names pre-Phase-1 skills.

## Also in scope — three edits outside the domain

Ticket 17 authorised these and did not make them:

1. **`build-plan` gains the `.ac.md` write** — creates
   `11_build/acceptance-criteria/<featureset>/<feature>.ac.md`, every row `untested`. It is
   already the skill that claims every criterion.
2. **`build-implement` gains the flip** — rows backed by a passing check.
3. **`contracts/acceptance_criteria.md` is rewritten** — off its pre-0007 paths, off the
   deleted `impl-plan-plan-vertical`, and **down to the join**: rows cite `AC-n` plus the
   feature spec, never copy the EARS line verbatim. The derivation guidance stays; the
   duplicated ledger body goes.

Both 1 and 2 are edits to skills that already landed (ticket 19, commit `3b21cfe`).

## Not in scope

`analysis_checklists.md` moves to `skills/quality-review/references/checklists.md`;
`contracts/evaluator.md` is already in `-mp` and is not rewritten here.
`13_impl-quality/contracts/evaluate-contract/CONTRACT.md` does not port.

## Note from ticket 21

**A fifth skill joins this port: `quality-release`** (from `ops-eval-product`, 171 lines). Ticket
17 resolved before ticket 21's note could reach it, so `ops-eval-feature` and `ops-eval-product`
were left owned by nobody; 21 ruled them outright. `ops-eval-feature` dies — its real job was
auditing whether claimed criteria are met, which 17 already gave `quality-review` as the
AC-ledger honesty check, and its *"MUST actually interact with the running app — no static code
inspection"* (`06_eval-feature/SKILL.md:63`) becomes a step there.

**`quality-release` is the release gate over the whole app.** It grades the running application
against `brief.md` + `goals.md` on seven axes (quality, originality, craft, functionality,
performance, accessibility, mobile), and it is **the only skill in the collection that closes the
loop back to the intent the project started from** — that, not its verdict grammar, is what it is
for. Zero flow nodes today (ticket 10 has been told); `quality-gate.md:21` already describes it in
prose. It reads the AC ledger and the coverage matrix, both of which 17 and 21 have now placed
under `11_build/`. Its verdict artifact should follow 17's one-verdict-artifact rule rather than
minting `_implementation/eval-product.yaml`, which resolves to nothing under ADR 0007.

**Two defects in `contracts/evaluator.md`**, which ticket 21 kept (three readers: `ops-review`,
`quality-review`, `quality-release`) but did not edit:

1. **Its header (`:3-5`) names five readers, four of them dead or renamed** —
   `ops-eval-concept`, `ops-eval-feature`, `ops-eval-product` and `impl-quality-eval-code`;
   `impl-quality-audit` was in the header and never read the file at all.
2. **A severity-vocabulary clash.** Ticket 17 pinned `quality-review`'s rule as *"`approve` ⇒
   zero critical **and** zero high"*, but this contract's flag shape (`:52-57`) has only
   `blocking|warning`, and its verdict grammar (`:40-46`) is a three-tier
   `pass`/`needs_resolution`/`fail`. One of the two is wrong, and whoever writes `quality-review`
   hits it at the step that writes the verdict.

Ticket 21's own note to ticket 22 covers a third issue this port should not try to settle: the
contract's six laws are uppercase `MUST`/`NEVER` with nothing enforcing them.

## Note from ticket 10

**One of ticket 17's rulings is overturned, on a fact 17 did not have.**

- **`quality-test` takes no `parameters:` block.** 17 specified
  `parameters: {levels: [unit]}` per tier. `data.parameters` has **exactly one live read in
  the whole host** — `parameters.flow`, a sub-flow child-id fallback
  (`flow-manager.ts:475`, `shared/flow-extended.ts:52`) — and ticket 08 ruled no `parameters:`
  blocks. So the levels would have been silently dropped. **`quality-test` reads `flow` from
  `01_meta/scope.yaml`** and picks its own levels: `appbuilder-mvp` → unit;
  `appbuilder-standard` → unit + integration.
- **`tier` is gone from `scope.yaml`; the field is `flow`.** Ticket 10 unified the two terms.
  Any skill in this cluster reading `scope.tier` reads `scope.flow`, whose values are flow ids
  (`appbuilder-mvp`, `appbuilder-standard`, `skaileup-concept-only`,
  `skaileup-concept-reverse`).
- **`quality-release` is the last node of `appbuilder-standard`**, phase `review`, after
  `ops-review`. It does not appear in `appbuilder-mvp`.
- **`quality-standards` appears in `skaileup-concept-reverse` only** — discover, never inject
  (17's ruling), and no other flow nodes it.
- `quality-test` → `quality-e2e` → `quality-review` → `ops-review` → `quality-release` is the
  review lane, inlined directly into the flow: **`quality-gate` no longer exists as a flow.**

## Answer

**Five skills written, three authorised edits made, both `evaluator.md` defects fixed.**
`scripts/check.py` is green (23 skills, 0 errors). Nothing committed.

### The five

| Skill | Lines / 140 | Notes |
|---|---:|---|
| `quality-review` | 89 | back-link resolution → `code-review`, security + a11y axes, AC honesty check, verdict at `11_build/reviews/<feature_slug>.yaml` |
| `quality-test` | 83 | unit + integration merged, levels read from `scope.flow`, no `parameters:` |
| `quality-e2e` | 72 | `agent-browser`, platform gate, journeys from `stories.yaml`, flips the ledger |
| `quality-standards` | 61 | discover only; no frontmatter gates at all — it reads code, not `_concept/` |
| `quality-release` | 81 | seven axes against `brief.md` + `goals.md`; verdict at `11_build/release.yaml` |

Plus `skills/quality-review/references/checklists.md` (43) and
`skills/quality-release/references/rubrics.md` (62).

### The severity clash — resolved in favour of four levels

`contracts/evaluator.md` § Flag shape now carries **`critical | high | medium | low`, with
*blocking* defined as `critical` or `high`**, and § Verdict grammar restates its three bands
against that boundary. 17's pin (*`approve` ⇒ zero critical and zero high*) stops being a
deviation and becomes a restatement of the contract's own rule, so `quality-review` cites it
instead of pinning it a second time.

Why this way round rather than collapsing `quality-review` to `blocking|warning`:

- **Two jobs, two properties.** The boundary decides the verdict; the *ordering* ranks the
  fix list. A two-value scale does the first and cannot do the second, and every one of the
  three readers emits a ranked findings list.
- **The contract already contradicted itself.** Its bottom band read *"or any critical
  finding"* — a severity its own flag shape had no value for. One of the two halves was
  always going to be edited.
- **Law 6 survives untouched.** *"NEVER emit a passing verdict while any blocking flag
  exists"* still parses word for word, because *blocking* is now defined rather than
  enumerated. The six uppercase laws are ticket 22's and were not touched.
- **The host agrees.** `review-coverage.ts:178-183` reads `findings[].severity` as a free
  string and defaults it to `info`; four levels cost it nothing.

Also fixed: the header now names the three real readers (`ops-review`, `quality-review`,
`quality-release`), and § Report format's `[<type>]` became `[<severity>/<category>]` to
match the new flag shape. The word *tier* was replaced with *band* throughout — ticket 10
retired `tier` from the sizing vocabulary and reusing it for verdict bands re-imports the
confusion.

### The ledger is checkbox lines, not a table

`contracts/acceptance_criteria.md` 253 → 91 lines. Off the pre-0007 paths, off
`impl-plan-plan-vertical`, and down to the join: one row per criterion carrying `AC-n`, a
status marker and the evidence that flipped it; the criterion text lives once, in the feature
spec, cited from frontmatter (`feature_ref`). The ~150 lines of duplicated ledger body (the
Given/When/Then restatement, the Backend AC section, the count-guidelines table calibrated on
the retired tier vocabulary) are gone; the derivation guidance and the EARS template stay.

**One change the ticket did not ask for, on measured evidence.** The ledger's rows are now
**checkbox lines** (`- [PASS] AC-2 — <evidence> · <skill> · <date>`) rather than a markdown
table. The ledger's only machine reader is forge-concept's
`review-coverage.ts:83-92`, which matches `^\s*-\s*\[(PASS|FAIL|x|X| )\]\s*(.+)$` line by
line — **the table shape the old contract specified parses as zero criteria**, and the
coverage page reports every feature as untested with no error anywhere. Same file requires
`feature:` in the ledger's frontmatter: without it the id falls back to the parent directory,
which is the *featureset*, so every feature in a set collapses onto one row.

### Judgment calls a later ticket should know about

1. **`quality-review`'s verdict values are `approved` / `changes-requested`, not
   `approve` / `needs_changes`.** `review-coverage.ts:158-162` accepts exactly
   `approved | changes-requested | pending` and maps anything else to `null` (no verdict
   rendered). 17 pinned the *rule*, and ticket 21 explicitly valued keeping the host's fix to
   a single prefix change — so the tokens follow the reader that exists. `approved` is
   already a canonical top-band name in `evaluator.md`; `changes-requested` was added to the
   middle band's names.
2. **`11_build/reviews/` is a second host change, not just the prefix.** The host walks
   `_implementation/review/` — **singular**. 17 pinned `reviews/` plural and the port follows
   the pin, but the forge-concept fix is therefore `_implementation/review/` →
   `_concept/11_build/reviews/`, not a bare prefix swap. **Register item.**
3. **`quality-release`'s verdict artifact is `11_build/release.yaml`** — one file, named for
   its scope, beside `ops-review`'s `11_build/review.yaml` and `11_build/trace.yaml`. It
   hard-gates `trace.yaml` (it runs after `ops-review`) and refuses on a red row or on any
   feature still at `changes-requested`.
4. **No `package.json` gate anywhere, by force.** `check.py` rejects any
   `prerequisites.files[]` path that does not start with `_concept/` (ADR 0011's blanket
   rule), so the "source code exists" gate could only be declared for a path the validator
   resolves outside the concept. It lives at the step instead, per ADR 0008. Worth knowing:
   `validator.ts:81` joins to the *project* root, so `package.json` would in fact have
   resolved correctly — the collection's own check is stricter than the reader. Not worth a
   ticket on its own; noted in case a later skill needs a real project-root gate.
5. **`quality-test` hard-gates `01_meta/scope.yaml`.** Forced by ticket 10's overturn: with
   no `parameters:` block the skill reads `flow` from `scope.yaml`, so `scope.yaml` is now an
   input rather than a convenience.
6. **The logic checklist did not port.** `analysis_checklists.md` § Sub-agent 1 (Logic &
   Runtime Errors) was dropped, because 17's list of what `quality-review` adds is exhaustive
   and names two axes. Honest caveat: `code-review`'s Standards axis is documented standards
   plus the Fowler smell baseline, and neither catches a missing null check or an unhandled
   rejection. If review quality disappoints in practice, that list is the first thing to
   restore — it is 6 bullets.
7. **`quality-standards` declares no `inputs_required`.** It would have been the first `-mp`
   skill to do so and would have inherited ADR 0011's recorded clash (the input dialog reads
   the hardcoded `_concept/_grounding/<skillId>/input.json`, a path 0007 renamed). It asks at
   the step instead.
8. **`quality-review` hands `code-review` the discovered standards.** One clause in step 3,
   added because it gives `02_grounding/standards/index.yml` its only reader in `-mp` — 17
   killed `standards-inject` on the finding that the artifact's real readers read `index.yml`
   directly, and until this clause nothing in `-mp` read it at all.
9. **`refactor.md` became `slices/<slice_id>/index.md`.** ADR 0005 collapsed the per-phase
   handoffs into one dossier file, so the accepted-debt context 17 asked for is read from the
   frozen index rather than from a file that does not exist here.

### Left undone, deliberately

- **`contracts/artifact_frontmatter.md` and `contracts/feedback_loop.md` are still on
  pre-0007 paths** (`experience/features/`, `_implementation/slices/`). `quality-review`
  cites the first for the `commits[]` / `source_files[]` back-link keys, which are correct;
  only the paths around them are stale. Not this ticket's file — flagging it for 26 or a
  sweep, since ticket 16's sweep evidently did not reach them.
- **`CONTEXT.md` has no words for `finding`, `verdict` or `severity`**, which the three
  verdict skills now use constantly. Left to the session that owns `CONTEXT.md`.
- **No flow nodes.** Ticket 28 wires
  `quality-test → quality-e2e → quality-review → ops-review → quality-release`.
- **`ops-review` is not on disk yet**, so the contract rows and `quality-release`'s step 1
  name a skill that its sibling session is still writing.
