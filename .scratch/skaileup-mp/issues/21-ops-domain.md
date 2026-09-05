# 21: The `ops` domain — eight skills nobody owned

**Type:** grilling
**Blocked by:** None (04, 07, 08 resolved)
**Status:** ready

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
