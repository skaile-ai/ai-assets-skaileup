# 0037 — Parallel specs serialise at four points

**Status:** accepted

Amends [ADR 0027](0027-agents-and-levelled-decisions.md) K1 (the delegation protocol's rule on
parallel runs) and K5 (a pattern's shared module in the build), and
[ADR 0036](0036-build-adapters-on-to-tickets-and-implement-spec.md) (the proposal gate of
`build-plan` and `build-implement`, and how integration branches land).

## Context

The protocol allowed parallel runs only on disjoint write sets
(`tree/protocol/delegation.md § Delegation`) and said nothing about several features moving at
once. Per-run proposal files (ADR 0031) made most concept runs disjoint, and ADR 0036 made the
build one integration branch per spec, so several specs can be specified, planned, built and
reviewed side by side. What still collides is shared: an owner settling its pending entries, a
spec planned or built while an entry against something it names is pending, a `pattern` ADR two
specs both build, and the data model two specs both migrate. The lead had no rule for any of
them and would have kept several `implement-spec` frontiers in its own context.

## Decision

1. **Parallel per feature, across features.** `spec-feature`, `experience-behaviors`,
   `experience-screen`, `build-plan`, `build-implement` and `quality-review` run at once for
   different features; each run owns disjoint paths and writes its own proposal file. Two
   `build-plan` runs whose specs share a `follows:` pattern or a `data_entities` entry run one
   after another instead: run at once, neither sees the other's tickets, so both would create
   the shared-module ticket and neither could tell which schema ticket is earlier. The
   two-spec smoke of #27 hit this with `polls/draw-pick` and `places/manage-places` (both name
   `Place`).
2. **Serial point 1 — the promotion pass.** After each parallel wave, every owner with pending
   entries settles them in one run; different owners in parallel, one owner never twice at once;
   `skaileup`'s ADR promotion is part of the pass.
3. **Serial point 2 — the proposal gate.** `build-plan` and `build-implement` stop while a
   pending entry targets the feature's spec, a screen it names, a model entity it names or a
   glossary term it names; the check is a grep of `_concept/proposals/*.yaml`. This widens
   ADR 0036's gate, which named the whole `model.yaml` and no glossary term.
4. **Serial point 3 — a shared pattern.** The first `build-plan` to meet a `kind: pattern` ADR its
   spec follows, with no shared-module ticket yet, creates "Shared module for adr:<slug>" under
   its own parent; every later spec following the ADR makes its first ticket `blocked-by` it, a
   native link across parents.
5. **Serial point 4 — data model migrations.** `architecture-datamodel` promotes model changes
   one run at a time; a spec's schema ticket is `blocked-by` the schema ticket of every earlier
   (parent issue opened first)
   open spec on the same entity; integration branches merge into their base one at a time, each
   rebased on it before its PR is marked ready.
6. **One `implement-spec` per spec.** Each spec builds in its own session and worktree; the
   lead prints one `/build-implement <featureset>/<feature>` run line per spec and owns the
   serial points. Order across specs lives only in the tracker's `blocked-by` edges.

The rules are stated once, in `tree/protocol/delegation.md § Several specs at once`; the lead's
SOUL, `build-plan`, `build-implement`, `tree/docs/adr/README.md § Patterns` and
`tree/10_blueprint/datamodel/README.md` cite it.

## Options rejected

- **Serialise every spec.** Safe and slow; the collisions are at four known points, and the
  rest of the work is disjoint by construction.
- **The lead juggles several frontiers itself.** One context holding several ticket graphs
  loses track of which merger belongs to which spec; separate sessions keep each graph whole.
- **A lock file for shared work.** A second record of what the tracker's `blocked-by` edges
  already hold, and one more file for nobody to clean up.

## Consequences

- A spec that follows a pattern another open spec already ticketed cannot start its build until
  that ticket closes.
- A glossary or model proposal from one spec's run can hold up another spec's plan until the
  promotion pass settles it.
- `build-plan` joins the proposers of `model.yaml` and of the feature spec: both smoke runs of
  #27 met a model field or a criterion id the spec lacked and had nowhere to put it but a
  comment. A gap it proposes holds the build through serial point 2 until its owner settles it.
