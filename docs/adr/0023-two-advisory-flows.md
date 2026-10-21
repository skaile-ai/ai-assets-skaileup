# 0023 — Two advisory flows

**Status:** accepted

Supersedes the tier-as-flow part of [ADR 0002](0002-flat-tree-and-nine-domains.md) and
[ADR 0007](0007-one-numbered-artifact-tree.md): the statements that order lives in the flow
graph, and that choosing a flow sizes the project. Builds on
[ADR 0019](0019-scoped-fact-resolution.md), which removes the gates that made the chain
mandatory.

## Context

A flow was the unit that sized a project and the carrier of order. In practice (U15) three of
the four flows — `appbuilder-mvp`, `appbuilder-standard`, `skaileup-concept-only` — were
prefixes of one chain, each a longer or shorter run of the same skills, and
`skaileup-concept-reverse` was the only "from the middle" door. Tier (`mvp`, `standard`,
`concept-only`) and flow id were the same choice, so changing depth meant changing the graph.
Under ADR 0019 skills no longer hard-gate their inputs; a strictly linear chain overstates
what the flows enforce.

The deletion test also finds skills that only route or only list: `concept-scope` is one yaml
plus a pointer, and `spec-featuresets` holds a roster that grows from the features anyway.

## Decision

**Two advisory recipes:** `skaileup-greenfield` and `skaileup-reverse`. Each lists the skills a
project of that kind usually runs, in a suggested order; none gates anything. Flow nodes keep
`data.phase`, which the host reads.

**Tier becomes `depth`** in `scope.yaml`, alongside `flow`, `project_type` and the signals.
Depth sizes how much each skill produces; it is asked per artifact where it matters
([ADR 0019](0019-scoped-fact-resolution.md)).

**`skaileup` owns `scope.yaml`.** `concept-scope` is deleted: the router asks for `flow`,
`project_type` and `depth` lazily, at the moment a skill needs one, and writes the file.

**`spec-featuresets` is deleted.** The featureset roster grows from `spec-feature`, which
absorbs it. The findings / intent split and the independence of the roster stay.

**`decisions.md` opens to every authoring skill** ([ADR 0022](0022-shared-artifact-contracts-and-proposed-entries.md)).

## Consequences

- The skill count is 33 again: 31 remaining, plus `experience-screen` and `quality-design`.
- The onboarding wizard shows two cards.
- The scope node and `skaileup` change owner; `concept-scope` leaves every `requires` and
  every flow.
- [INFERENCE] The host treats a flow as advisory when no skill carries a hard gate. If it
  hard-stops on a missing upstream node, both flows keep the full chain and the router is the
  only middle entry.
- Nothing is migrated: the owner chose a clean slate, with no legacy path.
