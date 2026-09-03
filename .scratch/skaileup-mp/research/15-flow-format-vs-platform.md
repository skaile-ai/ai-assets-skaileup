# The flow format, checked against platform's flow-execution

Research for ticket `.scratch/skaileup-mp/issues/15-flow-format-vs-platform.md`.
Question: **does platform's newer flow implementation define a different flow format, and
does `-mp` have to satisfy it?**

Every claim is cited `path:line` against the consuming code, or against a run of it.

| alias | path |
|---|---|
| `PF/` | `/Users/matthias/devBench/SKAILEdev/platform/` |
| `WS/` | `/Users/matthias/devBench/SKAILEdev/workspaces/packages/workspaces/` |
| `FC/` | `/Users/matthias/devBench/SKAILEdev/forge/forge-concept/` |
| `SK/` | `/Users/matthias/devBench/SKAILEdev/ai-assets/ai-assets-skaileup/` |

---

## Headline

**Platform did not fork the flow format — it consumes the same one, from the same package.**
The ticket's worry ("platform has its own, newer flow implementation") is half right: platform
has its own *execution and authoring surface*, but its *format* is `@skaile/workspaces`'
`FlowManifestSchema`, the same package forge-concept loads flows with. There is one schema, in
one place, and both hosts point at it.

All **17 existing skaileup flows already validate green** against platform's validator
(run below). The format risk to the map is zero. What the investigation did turn up is a
different and more useful result: **`SK/skaileup/contracts/flow.schema.json` is the odd one
out** — it is stricter than, and in three places contradicts, the only schema anything
actually enforces.

---

## 1. What platform reads and writes

**Storage.** A platform flow is a `flow` ScopedAsset whose definition JSON lives at
`filesJson['flow.json']` (`PF/frontend/src/lib/flow-asset.ts:12`). Definitions arrive by
paste, upload, or the in-app editor; YAML is accepted on import but **normalized to JSON at
store time** (`PF/_devlog/entries/2026-07-23-flow-yaml-cross-scope-picker.md`, "Implications").

**Platform never reads flow files from disk.** `loadAllFlows` / `loadFlowsFromDir` / `loadFlow`
have **zero call sites** in `PF/backend` and `PF/frontend`. It also stopped seeding flows into
orgs (`PF/_devlog/entries/2026-07-22-flow-seed-scope-down.md`): demo flows exist only in the
`acme` fixture, and real orgs start empty. So **`-mp` shipping flow YAMLs on disk does not
reach platform at all** unless a human imports one.

**Shape.** `PF/frontend/src/pages/flows/parts/flow-graph-layout.ts:41` —
`{ id?, name?, version?, nodes[], edges[] }`; node `{ id, type?, position?, data{ skill, version,
label, optional, parameters, phase, parallel_group, approval.mandatory, routes, … } }`; edge
`{ id?, source, target, type? }` where `type ∈ flow | parallel | optional`
(`:31`). Node kinds are `skill | group | sub-flow | router` (`:11`). That is
character-for-character the workspaces engine's `FlowNode` (`WS/factory-assets/connectors/flow/
engine/types.ts:81`) and `EdgeType` (`:42`).

**Validation** is `validateFlow` from `@skaile/workspaces/factory-assets/connectors/flow/engine`
— called at `PF/backend/libs/router-trpc/src/routes/run-group.route.ts:558`,
`PF/backend/libs/capabilities/src/handlers/run-group.handler.ts:109`, and
`PF/backend/libs/session/src/flow-start.service.ts:87`. Not a platform schema: the shared one.

---

## 2. The one schema that is enforced

`WS/factory-assets/connectors/flow/engine/flow-manifest.ts:57` — zod, and every level is
`z.looseObject`, i.e. **unknown keys pass**. Required: `id` (non-empty string) and
`name` (non-empty string) at the top; `id` on each node; `source`+`target` on each edge.
Everything else — `version`, `description`, `metadata`, `globals`, `modes`, `tier_presets`,
`artifact_handoff`, `entry`, and even `nodes`/`edges` themselves — is **optional** (`:57-77`).
The single semantic rule in the whole schema: a node cannot be both `data.optional: true` and
`data.approval.mandatory: true` (`:41-45`).

**No version skew.** forge-concept resolves `@skaile/workspaces@0.48.1`; platform is on `2.0.0`
(`PF/frontend/package.json:60`, `PF/backend/package.json:67`). Diffing 0.48.1's shipped
`flow-manifest.d.ts` against the 2.0.0 source: identical field-for-field, except 2.0.0 adds the
node `data` block with the optional-vs-mandatory refinement. **The format did not move across a
major version bump.** Anything valid for forge-concept is valid for platform.

**Platform adds three graph checks the shared schema lacks** — duplicate node ids, dangling edge
endpoints, self-loops (`PF/frontend/src/pages/flows/parts/flow-graph-validation.ts:24`). Its own
header notes why: `validateFlow` is a shape check with no cycle/dangling/unique-id rules, and the
save path doesn't even run it. Cycles, empty graphs and a missing `entry` are **deliberately not
rejected** (`:19-21`). These three are the only authoring constraints platform imposes beyond
workspaces, and they are ones a sane flow satisfies anyway.

**Positions are not required by anything.** Platform lays out with dagre and only honours a
supplied `position` when both coordinates are finite (`flow-graph-layout.ts:64`,
`:113`); the engine documents `position` as "not used" (`WS/…/types.ts:88`).

**Both node shapes are tolerated.** Platform folds a set of top-level node keys —
`label, skill, version, phase, parallel_group, optional, approval, parameters` — down into `data`
when a flow carries them at the node's top level, with explicit `data` winning
(`flow-graph-layout.ts:69-98`). The workspaces schema likewise allows `skill` at either level
(`flow-manifest.ts:32`). The engine, however, reads **only** `node.data.skill`
(`WS/…/engine.ts:77`), so `data.skill` is the shape to write.

---

## 3. Empirical check: the 17 skaileup flows against platform's validator

Ran `validateFlow` (workspaces 2.0.0 source) over every `SK/skaileup/flows/*/*.flow.yaml`:

```
OK  appbuilder-cli(11n/7e)      OK  appbuilder-complex(30/29)   OK  appbuilder-mvp(14/10)
OK  appbuilder-simple(16/13)    OK  appbuilder-standard(25/20)  OK  architecture(4/3)
OK  concept-discovery(3/2)      OK  impl-build-setup(6/5)       OK  mockup-feedback(4/3)
OK  quality-gate(8/7)           OK  skaileup-concept-only(19/17) OK skaileup-concept-reverse(10/8)
OK  skaileup-implementation(7/3) OK skaileup-slice-concept(4/3) OK  skaileup-slice-impl(13/12)
OK  skaileup-slice(2/1)         OK  skaileup-stepwise(9/10)
```

**17/17 pass.** The existing collection is already platform-importable as-is.

---

## 4. The real finding: `flow.schema.json` is stricter than reality, and wrong in three places

`SK/skaileup/contracts/flow.schema.json` (434 lines, draft-07) is `additionalProperties: false`
at every level (`:8`, `:154`, and ~10 more). Against a `looseObject` runtime that is a strict
*subset* discipline — fine as a house style, but it means the file is a **house rule, not the
contract**, and it has drifted:

| | `flow.schema.json` | what runs |
|---|---|---|
| node kind `gate` | defined, `:required id/type/position/data` | **not a kind** — engine knows `skill \| group \| sub-flow \| router` (`types.ts:81`); platform the same. **0 skaileup flows use it.** |
| edge `type: review-loop` | in the enum | **not an `EdgeType`** (`types.ts:42`). 1 use, in `skaileup-stepwise`. Engine treats it as a non-edge (§5). |
| `position` | **required** on every node | unused by the engine, dagre-computed by platform. Pure hand-authoring tax. |
| `meta:` | the spelling | workspaces says `metadata:` (`flow-manifest.ts:63`). forge-concept reads **both** (`FC/server/utils/flow-manager.ts:146`) but only `meta` elsewhere (`:268`, `:304`). All 17 flows use `meta:`. |
| `requires:`, `next_flows:` | defined | not in the workspaces schema; pass as unknown keys. `next_flows` is read by forge-concept (`flow-manager.ts:53`, `:308`); `requires` drives install (ticket 01). |

So `flow.schema.json` is simultaneously **stricter** (closed objects, required positions) and
**laxer** (invents `gate` and `review-loop`) than the enforced schema. Its `data.phase` enum is
the one place it is *right and the workspaces schema is silent*: see §6.

---

## 5. The sharpest authoring constraint, and it is not platform's

The engine computes dependencies by filtering `edges.filter(e => e.type === "flow")`
(`WS/…/engine.ts:118`, `:203`, `:298`, `:334`). An edge with any other type — or **no `type`
at all** — contributes no dependency. Verified by running `computeFlowState` on a two-node
`a → b` graph:

```
edge.type=flow          b.canRun=false  blockers=["a"]
edge.type=(absent)      b.canRun=true   blockers=[]
edge.type=review-loop   b.canRun=true   blockers=[]
edge.type=optional      b.canRun=true   blockers=[]
```

**An untyped edge is a silently ignored edge.** It draws on both canvases and orders nothing.
All 153 edges across the 17 flows do carry a type (94 `flow`, 52 `optional`, 6 `parallel`,
1 `review-loop`), so the collection is safe today — but nothing checks it, `type` is optional in
every schema in play, and the single `review-loop` edge in `skaileup-stepwise` is **already a
no-op dependency** rather than a loop. This is the one rule `-mp` must not lose, and the
cheapest possible thing for ticket 16 to check.

---

## 6. `data.phase` is a closed three-value vocabulary

Ticket 04 established that `phaseForNode` prefers explicit `data.phase` over the name prefix
(`FC/shared/flow-phases.ts:35-41`) — correct. What it did not record: `isPhase` accepts
**only** `conceptualization | implementation | review` (`:31-33`), and anything else falls back
to the prefix inference. So `-mp`'s nine domains are a *naming* vocabulary; `phase` stays these
three lane labels. `flow.schema.json` gets this right (its `phase` enum). Ticket 10 inherits it.

Other live forge-concept-only reads, none of which platform touches:
`meta.icon` / `meta.onboarding.{input_style,placeholder,fields}` and `globals.research_depth`
drive the onboarding wizard (`FC/server/api/pipeline/profiles.get.ts:28-40`); `entry`,
`next_flows`, `parentNode`, and router `routes` are read in `FC/server/utils/flow-manager.ts`
(`:307`, `:308`, `:494`, `:534`). `modes`, `tier_presets` and `artifact_handoff` have **no
reader in any of the three repos**.

---

## 7. Layout: the flat tree is already supported

`loadAllFlows` walks `assetSearchDirs(root, "flows")`, which covers **both** the flat
`<root>/flows/` and the domain-nested `<root>/<domain>/flows/` layouts, de-duping by flow id
(`WS/…/loader.ts:86-92`). Ticket 04's flat `flows/` at the repo root needs no host change.
`loadFlowsFromDir` accepts `*.flow.yaml`, `*.flow.json` and bare `*.json`, skips `_`-prefixed
files, and **silently discards** any file missing `id`, `nodes`, or `edges` (`:41-63`) — note
that this is a *different* required-set than `validateFlow`'s (`id` + `name`), so a flow with no
`name` loads in forge-concept and is rejected by platform. Keep `name` on every flow.

---

## Answers to the ticket's three questions

1. **Same format.** Platform reads/writes the workspaces `FlowManifestSchema` shape —
   `{id, name, nodes[], edges[]}` with node `data.skill` — from `filesJson['flow.json']`, not a
   superset and not a rival model. `flowExecution.model.json` is the *execution record* (per-node
   status, approvals, inputs), orthogonal to the authoring format, exactly as the ticket
   suspected.
2. **It runs alongside, and it is not a file host.** forge-concept loads flows from disk;
   platform holds them in the DB and never touches disk. The contract is therefore *not* an
   awkward intersection — it is one schema in one package that both call. The only asymmetry
   worth writing down: forge-concept's loader requires `id`+`nodes`+`edges`, platform's
   validator requires `id`+`name`. **Satisfy both: always ship `id`, `name`, `nodes`, `edges`.**
3. **Three extra authoring constraints, all from platform's editor** — unique node ids, no
   dangling edge endpoints, no self-loops. Positions are *not* required (dagre). `data.phase` is
   free-form to platform but a closed three-value enum to forge-concept.

## Consequences to fold back

- **Ticket 09 Q3 stands, with a correction.** Keeping a machine form of the flow contract is
  right, but **`flow.schema.json` as it exists is stale, not canonical** — it defines a node kind
  and an edge type that no engine implements, requires positions nothing uses, and closes objects
  a `looseObject` runtime leaves open. `-mp` should ship a *narrowed* schema that is a true
  subset of `FlowManifestSchema` (drop `gate`, drop `review-loop`, drop required `position`,
  keep the `phase` enum, keep `meta`), or ship none and let ticket 16 assert the four rules that
  actually bite. Either way the 434-line file does not port as-is.
- **Ticket 10** authors against: `id`+`name`+`nodes`+`edges` always; `data.skill` (not top-level
  `skill`); **every dependency edge explicitly `type: flow`**; `data.phase` ∈ the three lanes;
  node kinds `skill | group | sub-flow | router`; `meta.onboarding` + `globals.research_depth`
  if the flow should appear in forge-concept's onboarding wizard. No positions.
- **The acceptance target does not move.** Platform cannot be the host for "flows load green" —
  it has no disk-loading path at all. forge-concept's `tests/integration/skaileup-flows.test.ts`
  stays the test. Platform importability is a *free* consequence of the shared schema, and is
  worth one assertion in ticket 16 rather than a second host.
- **Ticket 16** gains four cheap, high-value checks: `validateFlow` green (catches a missing
  `name`), every edge carries a `type`, every `type: flow` endpoint resolves to a node id, and
  `data.phase` ∈ {conceptualization, implementation, review}.
