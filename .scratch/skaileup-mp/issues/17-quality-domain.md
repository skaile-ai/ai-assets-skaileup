# 17: The `quality` domain — 13 skills, and which of them still have a job

**Type:** grilling
**Blocked by:** None (07 resolved)
**Status:** ready

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
