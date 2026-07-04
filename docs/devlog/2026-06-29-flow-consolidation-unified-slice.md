# Flow consolidation + unified `skaileup-slice` block

**Status:** executed 2026-06-30 · **Date:** 2026-06-29

> **Naming note (2026-07-04):** flow ids in this record use the **current** names.
> The merged code-build flow, called `skaileup-impl` at the time, is now
> **`skaileup-implementation`**; the start-in-the-middle flow, then
> `skaileup-implementation`, is now **`skaileup-stepwise`**. `skaileup-impl-standalone`
> was a pre-consolidation predecessor (never renamed) and is left verbatim — so
> sentences like "delete the gate; rename standalone → `skaileup-implementation`"
> describe the original `skaileup-impl` target under its present name.

> Executed: flow YAMLs, `skaile.yaml`, `verify_flows.py` (+ tests), scope-project
> routing (validator/SKILL/decision-rule/tests/example), all flow `.md` docs,
> `contracts/flows.md`, `docs/` reference + domain pages, root `CLAUDE.md`, and
> the read-or-generate notes on the three arch skills. `verify_flows.py` reports
> 12 flows consistent; flow + scope-project test suites pass.

## Problem

Every flow shares the same tail — `build-setup → impl-slice loop → quality`. They
differ only in the **concept front-half**: where the concept comes from. That front-half
axis is currently spread across **three near-duplicate impl-side flows** plus two slice
building blocks that the start-in-the-middle flow stitches together by hand.

Concept-source axis today:

| Concept source | Flow | Redundancy |
|---|---|---|
| Built fully up-front, linear | `appbuilder-mvp` / `simple` / `cli` | — |
| Built up-front + per-feature loop | `appbuilder-standard` / `complex` | — |
| Concept only, no build | `skaileup-concept-only` | — |
| From existing code | `skaileup-reverse-engineer` | — |
| **Pre-existing / handed-off** | **`skaileup-implementation`** (gate node) | ⬅ dup of standalone |
| **None → generate tech subset** | **`skaileup-impl-standalone`** | ⬅ dup of impl |
| Grown just-in-time per feature | `skaileup-stepwise` | interleaves full concept-slice by hand |

Three problems:
1. `skaileup-implementation` and `skaileup-impl-standalone` differ **only** by a precondition gate.
2. `skaileup-stepwise` reimplements "concept then build per feature" by wiring the
   two slice blocks together with a `review-loop` edge — duplicating what a single block
   should own.
3. The two slice blocks (`concept-slice`, `impl-slice`) are always consumed as a pair;
   nothing names the pair.

## Decisions

### 1. Unified `skaileup-slice` block (the core change)

Rename and compose the two per-feature loops:

- `skaileup-concept-slice` → **`skaileup-slice-concept`**
- `skaileup-impl-slice` → **`skaileup-slice-impl`**
- **new parent** **`skaileup-slice`** = `sub-flow(slice-concept) → sub-flow(slice-impl)`

`skaileup-slice-concept` gains a **concept-needs check** driven by a
`concept_depth: full | just-in-time | skip` global:

- **`full`** — run all four phases (brainstorm → align → scope-feature → design-feature):
  the complete per-feature concept design. (Today's `concept-slice` behaviour.)
- **`just-in-time`** — for this feature, detect which canonical concept artifacts are
  **missing or insufficient**, surface the open questions to the user, and write **only
  the minimal** versions needed to build it (this feature's behavior + key screens + data
  needs). No brand/journeys/mockups unless the feature truly needs them. Concept becomes a
  **by-product of building**, accreting into `_concept/` feature by feature.
- **`skip`** — concept already exists up-front (linear tiers); slice-concept no-ops and
  the slice runs impl only.

This is the mechanism for "start in the middle": concept is created on a need-to-know
basis *inside the slice*, by `slice-concept` checking for and building the basic concept
files on demand with the user — not by a separate front-loaded pass.

Both `skaileup-slice-concept` and `skaileup-slice-impl` stay standalone-runnable for
testability; `skaileup-slice` is the normal entry for per-feature work.

### 2. Delete `skaileup-implementation`; rename `skaileup-impl-standalone` → `skaileup-implementation`

The gate is the only difference. Make the architecture skills idempotent —
**read existing concept if present, else generate the minimal tech subset** — and one flow
covers both the handoff case and the code-only case. The merged flow becomes *the* code
build flow: `(arch read-or-generate) → build → skaileup-slice(concept_depth: skip) → quality`.

### 3. Rename `skaileup-reverse-engineer` → `skaileup-concept-reverse`

It sits on the concept axis (produces a concept *from existing code*). **Flow only** —
keep the skill `ops-reverse-engineer`, the `ops-project-*` skills, and all artifact ids
unchanged; only the flow id / directory / `name` / `requires` self-ref change.

### 4. Rewire the consumers

| Flow | Before | After |
|---|---|---|
| `appbuilder-standard` / `complex` | two nodes: `concept-slice-loop` + `impl-slice-loop` | one node: `skaileup-slice` (`concept_depth: full`) |
| `appbuilder-simple` / `cli` | `impl-slice-loop` | `skaileup-slice-impl` (or `skaileup-slice` w/ `concept_depth: skip`) |
| `appbuilder-mvp` | inline impl-slice steps | unchanged (too small to delegate) |
| `skaileup-stepwise` | thin foundation + interleaved concept-slice ⇄ impl-slice via `review-loop` | thin foundation + loop over `skaileup-slice` (`concept_depth: just-in-time`) |

The result: the difference between the two incremental flows becomes crisp —
`appbuilder-standard` = full per-feature concept design *then* build; `implementation` =
concept fragments grown *inside* the slice, only what each feature needs.

## Resulting flow set

- **Blocks:** `skaileup-slice` (parent), `skaileup-slice-concept`, `skaileup-slice-impl`
- **Pipelines:** `appbuilder-{mvp,simple,standard,complex,cli}`, `skaileup-concept-only`,
  `skaileup-concept-reverse`, `skaileup-implementation` (merged), `skaileup-stepwise` (lean)
- **Removed:** `skaileup-implementation` gate flow (folded into the renamed `impl`)

Net: 12 flows → 12 (gate flow deleted −1; `skaileup-slice` parent added +1;
`impl-standalone` renamed into `skaileup-implementation`; slices + reverse renamed). The
*impl-side* variants collapse 3 → 2 (`skaileup-implementation`, `skaileup-stepwise`),
which was the redundancy this targeted; the flow count is flat because the unified
parent is itself a new flow.

## Open design questions

- `concept_depth: skip` vs. just pointing simple/cli at `skaileup-slice-impl` directly —
  pick one convention so there's a single way to "impl-only a slice".
- Where the concept-needs check lives: extend `concept-slice-brainstorm` /
  `concept-slice-scope-feature`, or a small new `slice-concept-detect` step. Prefer
  extending existing skills to avoid a new asset.
- `flow.schema.json` `next_flows[].domain` enum still uses Phase-0 vocabulary; unaffected
  but worth a pass when touching schema.

## Touch list (when executed — NOT done here)

**Rename `skaileup-impl-standalone` → `skaileup-implementation`** (after deleting the gate flow):
- `skaileup/flows/skaileup-impl-standalone/` → `skaileup/flows/skaileup-implementation/` (dir + both files)
- flow `id` / `name` / requires self-ref; `.md` doc
- `skaile.yaml` (drop old `skaileup-implementation` entry, repoint)
- `skaileup/flows/_meta/verify_flows.py` (impl-only allow-list)
- `skaileup/flows/index.md` (merge the two rows)
- make arch skills idempotent: `impl-architecture-{techstack,system,datamodel}` SKILL.md

**Rename `skaileup-reverse-engineer` → `skaileup-concept-reverse`** (flow only):
- `skaileup/flows/skaileup-reverse-engineer/` → `.../skaileup-concept-reverse/` (dir + 2 files)
- flow `id`/`name`/requires; `skaile.yaml`; `verify_flows.py`; `flows/index.md`
- `scope-project` example `examples/skaileup-reverse-engineer.scope.yaml` + decision-rule
- orchestrator `agents/skaileup/SOUL.md`, `skills/skaileup/SKILL.md` routing refs
- docs site: `docs/src/content/docs/**` (mental-model, flows-and-bundles, ops, meta-group)
- **do NOT** touch skill `ops-reverse-engineer` or `_implementation`/`_concept` artifact ids

**Unified slice** (`concept-slice`→`slice-concept`, `impl-slice`→`slice-impl`, new `skaileup-slice`):
- rename both flow dirs + files + ids/names/requires self-refs
- new `skaileup/flows/skaileup-slice/` (parent: two sub-flow nodes + `concept_depth` global)
- `skaile.yaml`, `verify_flows.py` (+ `deferred_skills.yaml` if referenced), `flows/index.md`
- every consumer flow's sub-flow nodes + `requires` flow-refs:
  `appbuilder-{simple,standard,complex,cli}`, `skaileup-implementation`, `skaileup-stepwise`
- `concept_depth` handling in `concept-slice-brainstorm` / `concept-slice-scope-feature`
- contracts: `artifacts.yaml` slice ids, `concept_structure.md`, `flows.md`
- root `CLAUDE.md` (Flows + Two-Group sections), `docs/` Starlight pages
