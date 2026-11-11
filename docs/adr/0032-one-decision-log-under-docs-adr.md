# 0032 — One decision log under docs/adr/

**Status:** accepted

Supersedes the two decision logs `_concept/10_blueprint/decisions.md` and
`_concept/11_build/decisions.md` and their nodes. Amends
[ADR 0022](0022-shared-artifact-contracts-and-proposed-entries.md) ("one append-only decision
record, open to every authoring skill") and [ADR 0023](0023-two-advisory-flows.md) ("`decisions.md`
opens to every authoring skill"): the record is one file per decision, owned by `skaileup`, and
every other skill proposes. Amends [ADR 0027](0027-agents-and-levelled-decisions.md) K4 and K5 in
where a record lives and how it is cited: levels, kinds and patterns stand unchanged in meaning,
the record is a file under `docs/adr/` and is cited by slug. Amends
[ADR 0029](0029-the-concept-is-walked-top-down.md): a waive is backed by an ADR, cited by slug.
Amends [ADR 0031](0031-proposals-are-files-per-run.md) where it keeps "the one decision record of
0022": the record is now the folder `docs/adr/`, and an ADR-grade decision reaches it as a
proposal entry.

## Context

A project kept two append-only logs inside `_concept/`, numbered `DR-<n>` each in its own
sequence, plus whatever `docs/adr/` it already had for architecture. The global
`domain-modeling` skill, which hosts grill the concept with, writes to `docs/adr/<NNNN>-<slug>.md`
and never reads `decisions.md`, so a project that used both had two decision logs that did not
know about each other, and `tree/APP-DESIGN.md` had to list both as neighbours. Every authoring
skill co-owned the design log (eight owners, one file): parallel runs appended to the same path,
which [ADR 0031](0031-proposals-are-files-per-run.md) removed everywhere else. A `DR-<n>` was
taken at write time, so two parallel runs picked the same number. The build log also collected
`DONE_WITH_CONCERNS` notes, which were seldom the hard-to-reverse choice a record is for.

## Decision

**A1 — One record per file, at the project root.** A decision lives at
`docs/adr/<NNNN>-<slug>.md`, the layout of upstream `domain-modeling`'s ADR format, so both write
and read one folder. The body is upstream's (title, 1–3 sentences, optional `## Considered
Options` and `## Consequences`); skaileup always adds frontmatter `status`, `date`, `by`,
`level`, `kind`, `applies_when` (patterns only) and `refs`, which upstream ignores. Node:
`tree/docs/adr/README.md`, a project-root artifact like `APP-DESIGN.md`
(`tree/protocol/beside-the-tree.md`).

**A2 — Cited by slug, never by number.** A record is referenced as `adr:<slug>`, e.g. a feature's
`follows: [adr:booking-slots-are-hourly]` or a waived stage's `adr:` in `walkthrough.yaml`. The
reference resolves to `docs/adr/*-<slug>.md`, else to a pending proposal entry with
`target: docs/adr/` and `anchor: adr:<slug>`. The number is assigned later, so a citation written
before promotion stays valid after it.

**A3 — `skaileup` owns, everyone else proposes.** The node's `owner` is `[skaileup]`; its
`may_propose` lists every skill that used to own the design log plus the architecture and build
skills. A proposer writes an ADR-grade decision as one entry of its run's proposal file
(`tree/proposals/README.md`): `payload` the full markdown record with `status: proposed` and no
number. `skaileup` promotes: takes the highest existing number + 1, writes the file, sets the
entry's status. Promotion is mechanical, with no user batch, unless the record contradicts an
accepted record at a higher level; that one goes to the user.

**A4 — Levels, kinds, patterns and the three-test gate stand.** Their rules move unchanged in
meaning into the new node (`§ Levels`, `§ Patterns`, `§ Writing it`). Superseding is a new record
naming the old slug; the owner sets the old one's `status: superseded by ADR-<NNNN>`, the one
permitted edit.

**A5 — Build concerns go to the tracker.** A `build-*` run's `DONE_WITH_CONCERNS` no longer
appends to a log: the receiver posts the concerns as a comment on the spec's parent issue and
repeats them under `Concerns:`; only an ADR-grade choice among them becomes a proposal entry.

## Options rejected

- **Keep `_concept/10_blueprint/decisions.md`, mirror it into `docs/adr/`.** Two copies of one
  decision drift, and the upstream grill still reads only one of them.
- **Keep the log, open it to upstream by a pointer.** Upstream expects one file per decision; a
  single log would need every upstream read to learn a second format.
- **Number at write time.** Parallel proposers would pick the same number; a slug is unique by
  construction and the number becomes a promotion detail.
- **Let each skill write its own ADR file directly.** No collisions on paths, but the
  contradiction check against higher levels would run in every skill, and nothing would hold the
  numbering.

## Consequences

- The two `decisions.md` nodes under `tree/10_blueprint/` and `tree/11_build/` are deleted; no alias, no
  migration. `ops-review` reports an existing `_concept/10_blueprint/decisions.md` or
  `_concept/11_build/decisions.md` as one finding: move the ADR-grade records to `docs/adr/`,
  drop the rest.
- Every skill that produced `{ id: decisions, … }` drops it and declares the proposals `produces`
  (rule `proposer-produces-proposals`); `skaileup`'s route gains the promotion pass.
- `DR-<n>` references become `adr:<slug>`: a feature's `follows:`, `walkthrough.py waive --adr`,
  a design candidate's status, a slice plan's citations.
- `tree/protocol/delegation.md` routes `DONE_WITH_CONCERNS` to the spec's parent issue.
- `check.py` accepts the root-artifact node `tree/docs/adr/README.md` and resolves `follows:` by
  slug; `demo/docs/adr/` is the worked example.
