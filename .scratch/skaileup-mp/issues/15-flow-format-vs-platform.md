# 15: Check the flow format against platform's newer flow-execution implementation

**Type:** research
**Blocked by:** None
**Status:** resolved

## Question

Raised by the user while resolving ticket 09. Ticket 01 established the flow contract from
**forge-concept's** side (`<id>.flow.yaml` in dir `<id>`, `id`+`nodes`+`edges`, top-level
`requires:` drives transitive install). But `platform` has since grown its **own, newer**
flow implementation, and nothing has checked the two against each other:

- `platform/features/09-flow-execution/`
- `platform/schema/flowExecution.model.json`
- migrations `20260412161542_add_flow_execution`, `20260717050118_readd_flow_execution`
- devlogs: `2026-07-22-flows-graph-canvas`, `2026-07-23-flow-editor-structural-editing`,
  `2026-07-23-flow-yaml-cross-scope-picker`, `2026-07-22-flows-live-verify-fixes`

Establish:

1. **What format does platform's flow-execution actually read/write?** Same
   `<id>.flow.yaml` shape, a superset, or a different model entirely
   (`flowExecution.model.json` suggests a DB-backed execution record, which may be
   orthogonal to the authoring format rather than a competitor to it).
2. **Does it supersede forge-concept's reader, or run alongside it?** If `-mp` flows must
   load in both, the contract is the intersection, not either one.
3. **Does the flow editor / graph canvas impose authoring constraints** (node `data.phase`,
   positions, cross-scope refs) that `-mp`'s hand-written flow YAMLs must satisfy?

## Consequences to fold back

- **Ticket 09 Q3** decided *delete `flows.md`, keep `flow.schema.json` as the flow contract's
  machine form*. If platform validates against a different schema, that decision needs
  revisiting — `flow.schema.json` may be stale rather than canonical.
- **Ticket 10 (flows and tiers)** designs the `-mp` flow set on top of whatever this finds.
- The map's acceptance test ("flows load green") is defined against forge-concept's
  integration test; if platform is the newer host, the test target may move.

## Answer

**Platform did not fork the format — there is one schema, in `@skaile/workspaces`, and both
hosts call it.** Platform's `validateFlow` (`backend/libs/session/src/flow-start.service.ts:87`
and two more sites) is the very export forge-concept's loader package ships;
`flowExecution.model.json` is the per-node *execution record*, orthogonal to the authoring
format, as the ticket suspected. **All 17 existing skaileup flows validate green** against it.
No version skew either: 0.48.1 (forge-concept) and 2.0.0 (platform) declare the same fields.

1. **Format** — `{id, name, nodes[], edges[]}`, node `data.skill`, edge `type ∈ flow|parallel|
   optional`, node kinds `skill|group|sub-flow|router`. `z.looseObject` throughout: unknown keys
   pass, `nodes`/`edges` are themselves optional, only `id` + `name` are required.
2. **Alongside, and platform is not a file host** — `loadAllFlows`/`loadFlowsFromDir` have zero
   call sites in platform; flows live in the DB as `filesJson['flow.json']`, imported by hand,
   and org seeding was removed. So the contract is not an intersection. One asymmetry: the
   forge-concept loader requires `id`+`nodes`+`edges`, platform's validator requires `id`+`name`
   — **ship all four**.
3. **Three extra authoring constraints, from platform's editor** — unique node ids, no dangling
   edge endpoints, no self-loops. **Positions are not required** (dagre computes them); the
   engine documents `position` as unused.

**The actual finding is on our side: `contracts/flow.schema.json` is stale, not canonical.** It
invents a `gate` node kind and a `review-loop` edge type that no engine implements (0 and 1 uses
respectively), requires `position` on every node, and is `additionalProperties: false` against a
`looseObject` runtime. It ports narrowed or not at all.

**And the sharpest rule is not platform's:** the engine computes dependencies with
`edges.filter(e => e.type === "flow")` (`engine.ts:118,203,298,334`), so an edge with any other
type — or **no `type`** — orders nothing. Verified: `type=flow` → `blockers:["a"]`; absent /
`review-loop` / `optional` → `canRun:true`. All 153 edges in the collection are typed today, but
nothing checks it, and `skaileup-stepwise`'s one `review-loop` edge is already a no-op.

Also recorded: `data.phase` is a **closed three-value enum** for forge-concept
(`conceptualization | implementation | review`, `shared/flow-phases.ts:31-33`) — ticket 04 got
the precedence right but not the vocabulary; the nine domains name skills, not phases. And
`assetSearchDirs` already covers a flat `<root>/flows/`, so ticket 04's tree needs no host change.

**Consequences:** ticket 09's "keep a machine form" stands but `flow.schema.json` does not port
as-is; ticket 10 authors to the rules in §"Consequences" of the findings; **the acceptance
target does not move** — platform has no disk-loading path, so forge-concept's
`skaileup-flows.test.ts` stays the test and platform importability is a free consequence;
ticket 16 gains four cheap checks (`validateFlow` green · every edge typed · every `type: flow`
endpoint resolves · `phase` in the enum).

Findings: `research/15-flow-format-vs-platform.md`.
