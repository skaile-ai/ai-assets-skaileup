# 15: Check the flow format against platform's newer flow-execution implementation

**Type:** research
**Blocked by:** None
**Status:** ready

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

_(pending)_
