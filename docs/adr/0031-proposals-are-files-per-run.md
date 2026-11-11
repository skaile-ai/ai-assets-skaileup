# 0031 — Proposals are files, one per run

**Status:** accepted

Amends [ADR 0022](0022-shared-artifact-contracts-and-proposed-entries.md): a proposed entry is no
longer appended to the owner's artifact, and a rejection no longer goes into the decision record.
Amends [ADR 0024](0024-the-glossary-splits-by-kind.md) G4 and G5: a proposed term targets
`_concept/glossary.md` in either mode, no marker lines are written into the project glossary, and
`concept-glossary` writes the words there when it promotes the term. Amends
[ADR 0027](0027-agents-and-levelled-decisions.md) K7: `spec-feature` proposes roster moves instead
of co-owning `featuresets.md`. Amends [ADR 0029](0029-the-concept-is-walked-top-down.md) W4 and
[ADR 0030](0030-the-data-model-is-two-yaml-files-checked-by-skaile-model.md) where they rely on
inline markers (`(proposed by`, a `proposed:` key in `model.yaml`): an artifact is unconfirmed
while an entry targeting it is pending. `owner`, `may_propose` and the one decision record of 0022
stand.

## Context

Under 0022 a proposer appended its entry to the owner's artifact, marked inline: a `status:
proposed` block, a `proposed: { by, on, source }` key, a `(proposed by …)` line. Every proposer
therefore wrote into files it did not own, and `tree/protocol/delegation.md` had to count
`may_propose` as part of a run's write set. Runs the lead wanted to send in parallel — two
`spec-feature` runs on two features, a screen and a feature — almost always shared a proposal
target (the glossary, `model.yaml`, `APP-DESIGN.md`), so they could not go at once, and when a
host ran them anyway, the second write overwrote the first's entries. The markers also spread a
second format through every owner artifact: each node defined its own marker shape, each reader
and gate had to skip or count it, and a rejection had to be copied into `decisions.md`, where it
was rarely the hard-to-reverse choice a record is for.

## Decision

**P1 — One proposal file per proposing run.** A run that proposes anything writes one new file,
`_concept/proposals/<proposed_on>-<proposed_by>-<scope>.yaml` (`<scope>` a kebab slug of what the
run worked on; a second run with the same date, proposer and scope appends `-2`, `-3`), holding
`proposed_by`, `proposed_on`, `scope` and its `entries`. A run never edits another run's file.
Node `tree/proposals/README.md` and `tree/proposals/proposal.schema.json` hold the format.

**P2 — An entry names its target.** Each entry carries `id`, `target` (the project-relative path
of the owner's artifact), `anchor` (where it lands, in the grammar the target node defines),
`payload` (the entry in the target node's own format), `source` and `status: proposed |
promoted | rejected`. The proposer must be listed in the target node's `may_propose`; a glossary
entry targets `_concept/glossary.md` in either mode (a `CONTEXT.md` target resolves to
`tree/glossary.md` too), `APP-DESIGN.md` resolves to `tree/APP-DESIGN.md`. When the target does
not exist yet, the proposer creates nothing there.

**P3 — Only the target's owner settles.** It writes only `status`, `settled_by`, `settled_on` and
`reason` of the entry: the one write into a file it did not create. Promotion writes `payload`
into the artifact at `anchor`, in the artifact's own format. Rejection sets a `reason`; it needs no
decision record. Settled files stay as history.

**P4 — Owner artifacts carry no proposals.** No inline `status: proposed`, `proposed:` key or
`(proposed by …)` text in any owner artifact. A pending entry is unconfirmed: a gate that asked
for "no proposal marker in X" now asks for "no pending entry targeting X". `ops-review` reports an
entry pending for more than 14 days.

**P5 — Parallel runs need disjoint owned paths.** Two runs go at once when the paths they own
are disjoint; `may_propose` no longer counts, because every proposal is a new file.

**P6 — Ownership of the directory.** `tree/proposals/README.md` lists as `owner` every skill named
in some node's `may_propose`, each of which declares `produces: { id: proposals, path:
"_concept/proposals/<date>-<skill>-<scope>.yaml" }`; its `may_propose` is `[]`.

**P7 — The roster.** `concept-brief` becomes the sole owner of `featuresets.md`. `spec-feature`
proposes its roster moves (idea → featureset table, idea → `## Cut`, a new idea from a DEFER), and
`concept-brief` promotes them without a further user batch, because the user's approval of the
spec covers the move.

## Options rejected

- **Inline keys, kept and merged by the host.** The status quo. Parallel runs still write the same
  file, every owner format keeps a second marker shape, and a merge needs a host that every
  harness does not have.
- **One file per entry.** No collisions either, but a run that proposes ten glossary terms writes
  ten files, the source of a batch is split across them, and the file name has to invent an id
  per entry.
- **One central queue file** (`_concept/proposals.yaml`). Every proposing run appends to the same
  path, which is exactly the collision this decision removes.

## Consequences

- `check.py` drops `proposal-owner-records-decisions` (owners of proposal targets no longer need
  to produce `decisions.md`) and gains `proposer-produces-proposals`: every skill in some
  `may_propose` produces a path under `_concept/proposals/`, and every skill producing there is
  in some `may_propose`. `check_demo` validates every demo proposal file against the schema. A
  skill whose only `produces` entry is its proposal file (`quality-test`) still counts as writing
  no artifact: it keeps `## Steps` and the 100-line ceiling.
- Each target node's `## Format` drops its inline marker shape and states its payload shape and
  anchor grammar instead; gates and `check_concept.py` read pending entries from
  `_concept/proposals/` rather than markers in artifacts.
- `tree/protocol/ownership.md`, `tree/protocol/delegation.md`, `CONTEXT.md` and
  `docs/node-template.md` describe the files; `demo/_concept/proposals/` is the worked example.
- Nothing is migrated: a project with inline markers from before has its owners promote or
  remove them on their next run.
