# 23: Port the `quality` domain — write the 4 skills

**Type:** task
**Blocked by:** 21 (17 resolved)
**Status:** blocked

## Question

Nothing to decide — ticket 17 settled the shape, this writes it. Same relation 14 has to 06
and 19 has to 07.

Blocked by **ticket 21** only for `ready`: 17 ruled it leaves `quality` but handed
merge-or-keep to 21, and 21 also places `quality.yaml` / `eval-concept.yaml`. Nothing else
here waits on it.

Write four skills into `skills/`, each `SKILL.md` under the 140-line ceiling (ticket 03),
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
