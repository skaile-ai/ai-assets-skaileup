# 0008 — A gate lives at the step it binds; no file collects gates

**Status:** accepted

Supersedes the `iron_laws` clause of [ADR 0004](0004-contracts-earn-their-place.md).

## Context

`contracts/iron_laws.md` (119 lines) was the collection's register of non-negotiable
preconditions: nine numbered laws, plus a Rationalization Defense table and a Red Flags
table. ADR 0004 kept it against ADR 0003's deletion of `MUST`/`NEVER` skill-body prose, on
one argument — *these document machine-enforced gates, which is exactly the "check behind a
named failure" ADR 0003 asks for.* The file's own header states the same premise: *"Skills
enforce these via their `requires` field… This document explains the WHY behind each gate."*

ADR 0007 moved the pipeline out from under it. Six of the nine laws name pre-0007 paths, and
two of those are not merely stale but **contradicted**: laws 3 and 4 gate `experience/screens/`
on brand tokens and on the data model, while `spec-feature` writes screen specs inside the
per-feature loop, before `10_blueprint/` exists, and declares both as `gate: soft`. Law 5
names a `mock` skill that has never existed in either repo; law 6 names a `ready` skill absent
from `-mp`.

Three facts decided it.

**The dependencies did not disappear — they moved.** A screen *spec* is prose plus an
`elements:` block and consumes no tokens; *rendering* consumes them, and
`mockup-walkthrough` and `mockup-storybook` both hard-gate `tokens.json` already. A screen
spec becomes buildable at `build-plan`, which is where the data model is gated. Laws 3 and 4
were not wrong about the dependency, only about which step it binds — and both steps already
declare it.

**The machine-enforced premise fails twice over.** The prose enforces nothing, and neither
does the frontmatter as `-mp` currently writes it: `parseSkillRequirements` reads
`fm.metadata ?? {}` with no root-level fallback
(`workspaces/packages/workspaces/resolver/src/parser.ts:45-46`, identical in the deployed
`@skaile/workspaces@0.48.1` bundle), and **no `-mp` skill has a `metadata:` key** — all eight
put `artifacts:` and `prerequisites:` at the root. `validator.ts:81` joins each path against
the *project* root, and no `-mp` declaration carries the `_concept/` prefix. So every `-mp`
skill's gates are invisible to the only reader. That is a separate defect with its own
ticket; it is recorded here because ADR 0004's argument rests on the reader it breaks.

**The register genre is already ruled out by the collection's own vocabulary.**
`CONTEXT.md` defines **Gate** as *"a precondition on running a skill. Hard refuses to
proceed; soft warns and continues. Every gate is one or the other, **stated at the step it
binds**."* A central register of gates is the thing that sentence forbids.

The reader evidence is consistent with all three. `iron_laws.md` has **zero in-body readers**
in `-mp`, and in the old collection's 95 skills over the file's whole life the six path laws
were cited **zero times** — every one of the 84 references named law 7, 8 or 9. The half that
was cited is the half no `gate:` field can hold; the half `gate:` can express is the half
nobody ever cited.

## Decision

**A gate is declared in `prerequisites.files[]` at the skill it binds, and stated in that
skill's body at the step it binds. No file collects gates.**

**`contracts/iron_laws.md` is deleted.** Law by law:

| law | disposition |
|---|---|
| 1 no concept work without a brief | already live — `spec-feature:15`, `build-branch:10` hard-gate `brief.md` |
| 2 no data model without features | no writer in `-mp` yet → a requirement on the datamodel writer (ticket 25) |
| 3 no screens without brand tokens | re-cut to bind at **render** — already hard in `mockup-walkthrough:15`, `mockup-storybook:15` |
| 4 no screens without data model | re-cut to bind at **plan** — `build-plan:16`; the residue goes to ticket 25 |
| 5 no mockups without screen specs | already live, twice, with `min_entries: 1` — only the skill's name was phantom |
| 6 no implementation without readiness | its own second clause — "or by checking these paths directly" — is already satisfied by `build-plan:13-16` and `build-implement:13-15`; the `ready` skill is ticket 21's |
| 7 verify prerequisites first | already in `agent_patterns.md:8-20` (Read-Context-First) |
| 8 no overwriting without approval | already at its steps — `spec-feature:78-79`, `mockup-feedback:19-21`, `build-implement:51-53` |
| 9 questions are standalone messages | already in `agent_patterns.md:48-68`, with the worked example |

**Both tables die with the file.** The Rationalization Defense is the pre-ADR-0003 form of a
`MUST`/`NEVER` block — a constraint stated centrally, away from its step, defended against a
reader who was never given a reason. Its only load-bearing row (spec compliance before
quality review) already lives at `build-implement:35-39`; two more rows restate law 9 a third
and fourth time, and one points at a `prototype` *flow* that has never existed.

**The ruling is narrow: it kills a gate register, not every zero-reader contract.**
`agent_patterns.md` and `golden_principles.md` also have zero in-body readers in `-mp` today.
Both survive, on evidence rather than taste: `-mp` holds 8 of ~30 skills, so their readers are
**unbuilt, not absent**, where `iron_laws`' were a completed experiment — 95 skills over the
file's whole life, zero citations of the six path laws. `agent_patterns` had 15 citing skills
in the old collection; `golden_principles`' rules were independently confirmed correct while
its supposed machine reader was deleted (below).

Each is **kept on notice**, the disposition `evaluator.md` already carries in
`contracts/README.md`: a row that states it has no reader in this repo yet, names the tickets
whose skills would read it, and dies with them if they do not arrive. That pattern has already
paid off once — `evaluator.md` was kept on it and ticket 17 then found it four readers.

## Consequences

- **ADR 0004's `iron_laws` clause no longer holds.** Its `golden_principles` clause loses its
  stated ground too — ticket 16 deleted `lint_concept.py`, which *was* the machine ADR 0004
  meant, and found that it **inverted** the contract it supposedly enforced
  (`golden_principles.md:13,23` fixes snake_case in the semantic layer; the linter demanded
  PascalCase against the *derived* PostXL schema, one of four formats per
  `concept_structure.md:183-187`). The content was right and the reader was wrong — the inverse
  of `iron_laws`, where the content went stale under the pipeline. So the file is kept on
  notice against **ticket 25** (the datamodel writer) and **ticket 26** (`ops-review`),
  not kept on ADR 0004's argument.
- **One thing is removed without replacement.** Nothing in `-mp` says a screen spec written
  before the data model gets revisited when it lands, and `build-plan:16`'s soft gate is not
  a surface: soft entries are excluded from `satisfied` (`validator.ts:149`), and the one
  route that would render them (`forge-concept/server/api/flows/nodes/[nodeId]/requirements.get.ts`)
  has no callers. The requirement is handed to ticket 25; until it lands the loss is real.
- `contracts/README.md` loses its `iron_laws` row, and its `golden_principles` row gains the
  kept-on-notice wording. Ticket 16 rewrote that file wholesale, so its count sentence is
  correct after this deletion rather than before it: **14 contracts → 13**.
- `scripts/check.py` (ticket 16) is green after the deletion — nothing in CI referenced the
  file.
