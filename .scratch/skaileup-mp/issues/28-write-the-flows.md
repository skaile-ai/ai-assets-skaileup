# 28: Write the four flow YAMLs

**Type:** task
**Blocked by:** None — 23, 25, 26 all resolved 2026-09-05 (every node skill now exists)
**Status:** ready

## Question

Ticket 10 decided the flow list and every node graph. Nothing writes them. This ticket writes
`flows/<id>/<id>.flow.yaml` for the four survivors and deletes nothing (the old repo keeps its
17 untouched):

- `appbuilder-mvp` — 9 nodes
- `appbuilder-standard` — 27 nodes
- `skaileup-concept-only` — 14 nodes
- `skaileup-concept-reverse` — 9 nodes

Node graphs, ordering and phase assignments are in
[10: Flows and tiers](10-flows-and-tiers.md) § The four flows — read it rather than
re-deriving.

Shape rules ticket 10 fixed, all of which `scripts/check.py` (ticket 16) should enforce:

- **Keys kept:** `id`, `version`, `name`, `description`, `meta.icon`,
  `meta.onboarding.{input_style,placeholder,fields}`, `globals.research_depth`, `requires`,
  `entry`, `nodes`, `edges`.
- **Keys deleted:** `meta.category`, `globals.{approval_mode,subagent_mode,verbosity}`,
  `globals.concept_depth`, every `${...}` interpolation, all `data.parameters`, `data.writes`.
- **Node kinds:** `skill` + `group` only. No `sub-flow`, no `router`.
- **Three group nodes per flow** (conceptualization / implementation / review) carrying
  `data.phase` and geometry, **and** `data.phase` on every skill node — written from one
  table so the two cannot disagree.
- **Edges:** `type: flow` only. The host reads no other type
  (`run.post.ts:62`, `flow-extended-state.ts:48`).
- **`requires:`** exact — the flow's own node skills plus the contracts they read, no `flow:`
  refs, no extras.
- **The per-feature loop is a one-line comment** at the loop's first node; it lives in the
  skill bodies, not the graph.
- `input_style`: `repo` for `concept-reverse`, `structured` for the other three.

Also in scope: the two harness edits ticket 10 ruled inside this map —
`forge-concept/tests/integration/skaileup-flows.test.ts:29-36,38` and
`forge-concept/templates/dev/skaile.yaml:10-15` both name flows and skills that no longer
exist. Coordinate with **29**, which runs the result.

## Answer

_(pending)_
