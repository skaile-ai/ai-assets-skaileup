# 21: The `ops` domain — eight skills nobody owned

**Type:** grilling
**Blocked by:** None (04, 07, 08 resolved)
**Status:** claimed (session 642cdbe2)

## Question

Graduated from ticket 08, which found the gap the same way ticket 07 found 17 and 18: the
map's tickets covered the mockup domains (06/14), the slice loops (07), the concept half (08),
the contracts (09), quality (17) and architecture/build (18) — and `14_ops/` fell between them.

`14_ops/` holds **12 skills**. Four are already out of scope (the multi-product umbrella:
`project-overview`, `project-subsystem-map`, `project-integration`, `project-review` — ruled
out by ticket 09 on the same argument as `15_demo`). The other **eight, 2,207 lines**, are
owned by no ticket:

| skill | lines | flow refs |
|---|---|---|
| `ops-reverse-engineer` | 621 | 1 |
| `ops-add-feature` | 316 | **0** |
| `ops-review` | 307 | 2 |
| `ops-sync` | 289 | 1 |
| `ops-trace` | 184 | 1 |
| `ops-eval-concept` | 181 | **0** |
| `ops-eval-product` | 171 | **0** |
| `ops-eval-feature` | 138 | **0** |

Ticket 13 only *adds* to this domain (a triage on-ramp); ticket 18 mentions these skills once,
as `PLANS.md` readers.

Decide:

- The surviving set, and for each of the eight: merge / step-inside-another / dies.
- **The three `eval-*` are on zero flows** and total 490 lines. Ticket 09 kept
  `contracts/evaluator.md`; check whether it has a reader left after this ticket rules.
- **`ops-review` and `ops-sync` against each other.** Ticket 08 removed `concept.yaml`
  (the artifact-status manifest) — `ops-review` writes `quality.yaml`, `ops-sync` repairs
  cross-references. Both inspect a tree that just changed shape.
- **`ops-trace`** walks feature → slice → commits → code via `slice_ref` frontmatter written
  on freeze. Ticket 07 kept that back-link; confirm it still has a writer.
- Where `ops-*` sits against the global `code-review` and `diagnosing-bugs` installs, the
  same question ticket 17 asks of `quality`.
- Ticket 04's `quality`/`ops` line is the artifact under inspection: `quality` checks `src/`,
  `ops` checks `_concept/`. Ticket 08 moved the inspection *outputs* under `11_build/` — check
  that does not move the skills across the line.

## Note from ticket 08

Two are already settled at the boundary, because they touch the tree ticket 08 redrew:

- **`ops-add-feature` is `spec-feature` entered on an existing project**, not a third writer
  into `05_features/`. It declared `produces: _concept/experience/features` alongside
  `product-spec-features` and `concept-slice-design-feature`; ticket 08 left one writer per
  artifact, and adding a feature to a live project is the same job as specifying one.
- **`ops-reverse-engineer` re-points** to `experience-shell` plus a `spec-feature` loop. It was
  the terminal-node consumer of `experience-screens`, which ticket 08 narrowed to the shell.

Everything else in the eight is open.

## Answer

_(pending)_

## Note from ticket 17

Three things arrive from the quality domain.

**1. `ready` (162 lines) leaves `quality` — merge or keep is yours.** By ticket 04's line it is
not close: every path in its `READS` is under `_concept/`, its Context Budget says
`Never load: Source code`, and its body says `WRITES (none — read-only audit skill)`. It is
the **fourth** thing checking `_concept/` cross-reference integrity, alongside
`ops-eval-concept` (whose deduction table scores the same completeness matrix, differing only
in verdict grammar — 0-100 score vs per-feature ready/not-ready), `ops-review`, and `audit`
Phase 2 (which 17 deletes). Its own *"When NOT to Use"* routes concept-health to `review` and
source to `audit`, leaving it as feature-completeness-in-`_concept/`.

Two things only it has, which a merge must carry or consciously drop:
- a **remediation command naming the exact skill** that fills each gap;
- its **gate position** — and the flow and the skill disagree about what that is:
  `07_ready/SKILL.md:66` says *"Use **before** E2E testing"* while
  `quality-gate.flow.yaml:73-82` places `q-ready` **after** `q-test-e2e`, labelled
  *"Release Ready"*.

Also: its frontmatter declares `produces: impl-readiness` while the body writes nothing —
and under ticket 01, frontmatter `artifacts` is machine-read.

**2. Two of ticket 08's three placements are yours, not 17's.** `_concept/quality.yaml` is
written by `ops-review` (enforced by its `validator.py:34`) and `_concept/eval-concept.yaml`
by `ops-eval-concept` (`validator.py:14`, and a **hard gate** — the orchestrator's
*"concept must pass eval-concept"*). Neither has an entry in ADR 0007's `11_build/`, which
today holds only `slices/` and `decisions.md`. 17 ruled on the third (`testing/test_plan.md`
needs no entry — the producer dies) and on its own (`11_build/reviews/<feature_slug>.yaml`).

Worth knowing when you place them: ticket 08's list of three was drawn on the artifact's
*shape*, which is why `_implementation/eval-code.yaml` and `_implementation/review/<slug>.yaml`
— the same "findings about work" — were not in it. Drawn on the **writer**, the split is two
here and one in 17. Both of your two are read **only by the orchestrator**, whose port is
still in the map's fog.

**3. `audit` Phase 2 was doing `ops-review`'s job in parallel, and 17 deletes it.**
`03_audit/SKILL.md:127-131` checks cross-reference integrity, orphaned files, frontmatter
compliance and stale files — `ops-review`'s description verbatim — while `audit:52` sends the
user to `review` for exactly that. `analysis_checklists.md` admits it: *"Subset of `review`
(mechanical checks only)"*. So nothing is lost by the deletion **provided `ops-review` keeps
that work**; confirm rather than assume.

`contracts/evaluator.md` survives ticket 09's bar largely on your three `ops-eval-*` readers —
17 adds `quality-review` as the fourth. `13_impl-quality/contracts/evaluate-contract/CONTRACT.md`
does not port (zero `requires:` anywhere, three stale paths).
