# 0019 — Skills resolve facts, not files

**Status:** accepted

Supersedes the chronological read-direction table in `tree/README.md` (replaced by an
ownership rule, [ADR 0022](0022-shared-artifact-contracts-and-proposed-entries.md)). Amends
[ADR 0013](0013-a-skill-declares-what-it-produces.md): the flow-walking producer check becomes
a flow-free one. [ADR 0008](0008-gates-live-at-the-step-they-bind.md) stands — a gate still
lives at the step it binds — but this record narrows which gates may be hard. Amends
[ADR 0007](0007-one-numbered-artifact-tree.md) only in that the numbering order is a place in
the tree, no longer an order of reading.

## Context

Composability is blocked at invocation (U1; both critics graded it a blocker). Nearly every
concept skill hard-gates `brief.md`, `glossary.md` and `scope.yaml`, so a skill cannot run on
an inbox screen that already exists in code unless the whole upstream chain ran first. When a
gate fails, `tree/README.md` stopped the run and routed the user along the flow's edges. The
router `skaileup` named a door (a flow), not the inputs of what the user wanted. "From the
middle" meant running the reverse flow from its head. Four places enforced order at once: flow
chains, `prerequisites.files` hard gates, the read-direction table, and flow-order prose in
skill bodies.

The checker confirmed the structure was brittle (U16): a hard gate nobody produces passes
today (ADR 0013), and the `artifacts.requires` graph is cyclic (datamodel → techstack →
features → app-design → datamodel), so it cannot be read as a dependency graph.

## Decision

**A skill resolves facts, not files.** At each step it reads what exists, in any order (an
optional artifact only after checking it exists), pulls scoped code evidence with
`concept-reverse` where the code holds the answer, marks inferred facts as inferred, and
batch-asks only what tools cannot settle. `tree/README.md § How a skill runs` states this once
and the nodes that interview bind it at their step.

**Hard gates only where a machine-read format is consumed.** `model.json` gates
`build-database`; `APP-DESIGN.md` gates `quality-interaction`. Every other gate is soft, and
the node carries a derive-or-ask step in its place. Each input is declared once as a fact, an
enrichment or an install dependency; `artifacts.requires` is not a dependency graph.

**The router is demand-driven.** Input is a want (an artifact, a screen, a question); output is
the producing skill plus its inputs, each marked `present`, `derivable` (a findings file) or
`ask`. It asks for `flow`, `project_type` and `depth` lazily. See [ADR 0023](0023-two-advisory-flows.md).

**The read-direction table becomes an ownership rule:** read anything, write only what you own
through the owner's contract, add to someone else's artifact only as a `proposed` entry.

**`scripts/check.py` replaces the producer check ADR 0013 deferred.** Instead of walking a
flow's edges, it requires that every hard gate is produced by some skill's `produces` or is a
root prerequisite.

## Consequences

- About twenty skills lose a hard gate; their nodes gain a derive-or-ask step.
- A user can ask for one screen, one glossary term or one decision on a repo with no
  `_concept/` and get a batch of questions, not "run X first".
- Flow edges no longer carry correctness: removing a flow edge cannot unblock or block a skill.
- `scripts/check.py` fails a hard gate nobody produces (`hard-gate-has-producer`); `ops-review` stays on `_concept/` and does not repeat it.
- Existing flows keep working as advisory recipes; no host change is assumed.
