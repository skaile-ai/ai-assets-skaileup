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
