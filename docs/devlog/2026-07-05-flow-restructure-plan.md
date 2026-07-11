# Flow Restructure Implementation Plan (sub-flows, groups, routers)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract the five flow segments repeated across tier flows into shared, standalone-runnable sub-flows, materialize the comment-only phase headers as `group` nodes with a three-phase taxonomy, and replace the parallel-optional "fallback by label" mockup alternatives with first-match `router` nodes.

**Architecture:** Flows live in `skaileup/flows/<id>/<id>.flow.yaml`, each carrying an exact self-contained `requires:` manifest that the verifier (`skaileup/flows/_meta/verify_flows.py`) enforces against the flow's own nodes. This plan follows the existing `skaileup-slice` precedent: shared segments become new flow files consumed via `sub-flow` nodes (variance threaded through sub-flow node `parameters`, the `concept_depth` pattern), so a parent flow's `requires:` drops the delegated `skill:` refs and adds one `flow:` ref. Group and router node types already exist in `skaileup/contracts/flow.schema.json` but are used by zero flows today; the schema gains one small patch (node-level `phase`) and the verifier gains two structural checks (parentNode resolution, router-target resolution).

**Tech Stack:** flow YAML + JSON Schema (draft-07, `jsonschema`) + Python verifier (`verify_flows.py`) + pytest (`skaileup/flows/_meta/test_verify.py`).

## Global Constraints

- **No new skills, no SKILL.md edits** — only flow YAMLs, `flow.schema.json`, `verify_flows.py`, `test_verify.py`, `skaile.yaml`, flow `.md` docs, `CLAUDE.md`.
- **Five new shared sub-flows, exact ids:** `impl-build-setup`, `architecture`, `mockup-feedback`, `quality-gate`, `concept-discovery` — each a new dir `skaileup/flows/<id>/` with `<id>.flow.yaml` + `<id>.md`, registered in `verify_flows.py` (`SHARED_FLOWS`) and `skaile.yaml` (kind: flow).
- **`requires:` exactness invariant** (verifier-enforced): a flow's `skill:` refs == its node skills exactly; its `flow:` refs == its sub-flow node targets exactly; no inheritance, no extras.
- **Edge id convention:** `e-<source>-<target>` (existing convention, keep it for every new edge).
- **Phase taxonomy, exact values:** `conceptualization` | `implementation` | `review` (aligns with the schema's `next_flows[].domain` enum `skaileup-conceptualization` / `skaileup-implementation` / `skaileup-evaluate`).
- **Deliberately inline (no sub-flow adoption):** `appbuilder-mvp` (minimal tier stays one linear pass), `skaileup-stepwise` (thin-foundation nodes are deliberately partial; gets node-level `phase` tags, no groups), `skaileup-concept-reverse` (all-optional enrichment chain; gets one group only), `skaileup-slice{,-concept,-impl}` (already the loop building blocks; untouched).
- **Green after every task:** `python3 skaileup/flows/_meta/verify_flows.py` exits 0 and `python3 -m pytest skaileup/flows/_meta/test_verify.py` passes at every commit.
- **Group nodes are visual-only** (`contracts/flows.md` § Group Nodes): children keep their absolute `position:` values; group `position`/`style` are cosmetic. Group nodes go at the **top** of the `nodes:` array (canvas renderers require parents before children).
- **Router `routes:` are the authoritative dispatch;** the `optional` edges from a router to its targets are visualization only. Router targets must be node ids in the same flow — so `requires:` is unchanged by routers. (`mockup-walkthrough-text` is not a node in standard/complex, so it cannot be a route target there; the ordered preference is astro → framework (complex only) → static-html, `default` = static-html.)
- **Dependency note:** independent of the dedup plan (`2026-07-05-skill-dedup-plan.md`), but MUST land before the review-spine plan wires new skills into `quality-gate`.
- **Commits:** conventional-commit style, each ending with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

---

## Reference: repeated-segment → sub-flow map (decided)

| Sub-flow | Pipeline | Adopting parents | Variance knobs (globals, threaded via `${...}` like `concept_depth` in `skaileup-slice-concept`) |
|---|---|---|---|
| `impl-build-setup` | scaffold → foundation → infra(opt) → migrate → seed → docs | appbuilder-simple, appbuilder-standard, appbuilder-complex, appbuilder-cli, skaileup-implementation | `infrastructure: skip\|optional\|required` (default `optional`); `data_setup: required\|optional` (default `required`; cli passes `optional` — cli's old migrate∥seed parallelism is given up: both are optional data steps, sequential is semantically equivalent) |
| `architecture` | techstack → templates(opt) → system(opt) → datamodel | appbuilder-simple, appbuilder-standard, appbuilder-complex, appbuilder-cli, skaileup-implementation, skaileup-concept-only | `templates: include\|skip` (default `include`; implementation + concept-only pass `skip`); `system: include\|skip` (default `include`; simple + cli pass `skip`). concept-only's old system∥datamodel parallelism becomes sequential — acceptable, both write `_concept/blueprint/`. |
| `mockup-feedback` | annotate → triage → patch → apply (all optional) | appbuilder-standard, appbuilder-complex | none (block is byte-identical in both parents today) |
| `quality-gate` | test-unit → test-integration → test-e2e → ready → ops-review(opt) → ops-sync(opt) | appbuilder-standard, appbuilder-complex, skaileup-implementation | `e2e: required\|optional` (default `required`; implementation passes `optional`); `ops_tail: include\|skip` (default `include`; implementation passes `skip`). Decision: the ops-review→ops-sync tail IS included, as optional nodes gated by `ops_tail`. appbuilder-simple (unit+e2e only) and appbuilder-cli (unit+integration only) keep their inline quality nodes — they run subsets, not the gate. |
| `concept-discovery` | brief → goals(opt) → comparable(opt) | appbuilder-standard, appbuilder-complex, skaileup-concept-only | `goals: optional\|required` (default `optional`; concept-only passes `required`). appbuilder-{mvp,simple,cli} and skaileup-stepwise run `concept-brief` alone — they stay inline. |

`implementation-contract` is cited only by `impl-build-docs` (per CLAUDE.md § Flows), so it moves into `impl-build-setup`'s `requires:` and is dropped from every parent that listed it only for that skill (simple, standard, complex, cli, implementation).

---

### Task 1: Create the `impl-build-setup` sub-flow

**Files:**
- Create: `skaileup/flows/impl-build-setup/impl-build-setup.flow.yaml`
- Create: `skaileup/flows/impl-build-setup/impl-build-setup.md`
- Modify: `skaileup/flows/_meta/verify_flows.py` (flow registry, currently lines 52–65)
- Modify: `skaile.yaml` (flow assets section, after the `skaileup-concept-reverse` entry ~line 333)
- Test: `skaileup/flows/_meta/test_verify.py`

**Interfaces:**
- Consumes: `contract:@skaile-ai/shared-contracts`, `contract:@skaile-ai/implementation-contract`, skills `impl-build-{scaffold,foundation,infrastructure,migrate,seed,docs}`
- Produces: flow id `impl-build-setup`, installable as `flow:@skaile-ai/impl-build-setup`; globals `infrastructure`, `data_setup`

- [ ] **Step 1: Add failing registration test.** Append to the end of `skaileup/flows/_meta/test_verify.py`:

```python
# ---------------------------------------------------------------------------
# Case 10: shared sub-flows are registered and their flow files exist
# ---------------------------------------------------------------------------
SHARED_SUBFLOWS = [
    "impl-build-setup",
]


@pytest.mark.parametrize("flow_id", SHARED_SUBFLOWS)
def test_shared_subflow_registered(flow_id):
    sys.path.insert(0, str(FLOWS / "_meta"))
    import verify_flows

    assert flow_id in verify_flows.ALL_FLOWS
    assert (FLOWS / flow_id / f"{flow_id}.flow.yaml").exists()
    assert (FLOWS / flow_id / f"{flow_id}.md").exists()
```

- [ ] **Step 2: See it fail.** Run:

```bash
python3 -m pytest skaileup/flows/_meta/test_verify.py -v -k shared_subflow
```

Expected: `1 failed` (AssertionError: `'impl-build-setup' in verify_flows.ALL_FLOWS`).

- [ ] **Step 3: Create the flow file** `skaileup/flows/impl-build-setup/impl-build-setup.flow.yaml`:

```yaml
id: impl-build-setup
version: '2.0.0'
name: 'Impl Build Setup'
description: >-
  Shared one-time build-setup block: scaffold -> foundation ->
  infrastructure(opt) -> migrate -> seed -> docs. Consumed via a sub-flow node
  by appbuilder-simple/-standard/-complex/-cli and skaileup-implementation;
  standalone-runnable for testability. Two globals handle consumer variance
  (threaded to nodes like concept_depth in skaileup-slice-concept):
  infrastructure (skip | optional | required) and data_setup
  (required | optional — cli treats migrate/seed as optional data steps).
meta:
  category: incremental
  tags:
    - shared-block
    - build-setup
  icon: i-heroicons-wrench-screwdriver
requires:
  # Self-contained install manifest: the contracts its skills read + every
  # skill its nodes run (flow node order). Exact — no inheritance, no extras.
  # implementation-contract is cited by impl-build-docs.
  - contract:@skaile-ai/shared-contracts
  - contract:@skaile-ai/implementation-contract
  - skill:@skaile-ai/impl-build-scaffold
  - skill:@skaile-ai/impl-build-foundation
  - skill:@skaile-ai/impl-build-infrastructure
  - skill:@skaile-ai/impl-build-migrate
  - skill:@skaile-ai/impl-build-seed
  - skill:@skaile-ai/impl-build-docs
globals:
  research_depth: skip
  approval_mode: checkpoint
  subagent_mode: false
  verbosity: standard
  # skip | optional | required — consumers override via the sub-flow node's
  # parameters.infrastructure; threaded to the infra-opt node.
  infrastructure: optional
  # required | optional — consumers override via the sub-flow node's
  # parameters.data_setup; threaded to migrate + seed.
  data_setup: required
entry: scaffold
nodes:
  - id: scaffold
    type: skill
    position:
      x: 0
      y: 200
    data:
      skill: impl-build-scaffold
      label: 'Scaffold'
      optional: false
      parameters: {}
  - id: foundation
    type: skill
    position:
      x: 200
      y: 200
    data:
      skill: impl-build-foundation
      label: 'Foundation'
      optional: false
      parameters: {}
  - id: infra-opt
    type: skill
    position:
      x: 400
      y: 200
    data:
      skill: impl-build-infrastructure
      label: 'Infrastructure (per parent: skip | optional | required)'
      optional: true
      parameters:
        mode: '${infrastructure}'
  - id: migrate
    type: skill
    position:
      x: 600
      y: 200
    data:
      skill: impl-build-migrate
      label: 'Migrate'
      optional: false
      parameters:
        mode: '${data_setup}'
  - id: seed
    type: skill
    position:
      x: 800
      y: 200
    data:
      skill: impl-build-seed
      label: 'Seed'
      optional: false
      parameters:
        mode: '${data_setup}'
  - id: docs
    type: skill
    position:
      x: 1000
      y: 200
    data:
      skill: impl-build-docs
      label: 'Build Docs'
      optional: false
      parameters: {}
edges:
  - id: e-scaffold-foundation
    source: scaffold
    target: foundation
    type: flow
  - id: e-foundation-infra-opt
    source: foundation
    target: infra-opt
    type: optional
  - id: e-infra-opt-migrate
    source: infra-opt
    target: migrate
    type: flow
  - id: e-migrate-seed
    source: migrate
    target: seed
    type: flow
  - id: e-seed-docs
    source: seed
    target: docs
    type: flow
```

- [ ] **Step 4: Create the doc** `skaileup/flows/impl-build-setup/impl-build-setup.md`:

```markdown
---
title: "impl-build-setup"
description: "Shared one-time build-setup block: scaffold → foundation → infrastructure(opt) → migrate → seed → docs."
order: 13
---

The **impl-build-setup** flow is the shared one-time build-setup block. The
build-bearing tiers (`appbuilder-simple`, `appbuilder-standard`,
`appbuilder-complex`, `appbuilder-cli`) and `skaileup-implementation` delegate
to it via a **sub-flow node** right after architecture; it is
standalone-runnable (`skaile run flow:impl-build-setup`).

## Pipeline

```
scaffold → foundation → infrastructure? → migrate → seed → docs
```

## Variance knobs

Consumers set these on the sub-flow node's `parameters:` (threaded to nodes
via `${...}`, the `concept_depth` pattern):

| Global | Values | Default | Who overrides |
|---|---|---|---|
| `infrastructure` | `skip` \| `optional` \| `required` | `optional` | simple + cli: `skip`; complex: `required` |
| `data_setup` | `required` \| `optional` | `required` | cli: `optional` (migrate/seed are optional data steps) |

## Install manifest

`impl-build-setup.flow.yaml` carries a top-level `requires:` listing
`shared-contracts`, `implementation-contract` (cited by `impl-build-docs`) and
the six `impl-build-*` skills — everything installed by
`skaile add flow:impl-build-setup`.
```

- [ ] **Step 5: Register in the verifier.** In `skaileup/flows/_meta/verify_flows.py`, replace:

```python
ALL_FLOWS = TIER_FLOWS + SLICE_FLOWS + VARIANT_FLOWS
```

with:

```python
# Shared building blocks (2026-07 flow restructure): repeated tier segments
# extracted into standalone sub-flows, consumed via sub-flow nodes.
SHARED_FLOWS = [
    "impl-build-setup",
]
ALL_FLOWS = TIER_FLOWS + SLICE_FLOWS + VARIANT_FLOWS + SHARED_FLOWS
```

- [ ] **Step 6: Register in `skaile.yaml`.** Change the comment `# ── flows (12) ──` to `# ── flows (13) ──` and append after the `skaileup-concept-reverse` flow entry (keeping two-space indent of sibling entries):

```yaml
  - kind: flow
    name: impl-build-setup
    files:
      - skaileup/flows/impl-build-setup/impl-build-setup.flow.yaml
```

- [ ] **Step 7: See green.** Run:

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -v
```

Expected: `OK: 13 flows consistent — each requires: manifest exactly covers its nodes (0 warning(s))` and all pytest cases pass (incl. `test_shared_subflow_registered[impl-build-setup]`).

- [ ] **Step 8: Commit.**

```bash
git add skaileup/flows/impl-build-setup skaileup/flows/_meta/verify_flows.py skaileup/flows/_meta/test_verify.py skaile.yaml
git commit -m "feat(flows): add shared impl-build-setup sub-flow

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Adopt `impl-build-setup` in the five build-bearing parents

**Files:**
- Modify: `skaileup/flows/appbuilder-simple/appbuilder-simple.flow.yaml`
- Modify: `skaileup/flows/appbuilder-standard/appbuilder-standard.flow.yaml`
- Modify: `skaileup/flows/appbuilder-complex/appbuilder-complex.flow.yaml`
- Modify: `skaileup/flows/appbuilder-cli/appbuilder-cli.flow.yaml`
- Modify: `skaileup/flows/skaileup-implementation/skaileup-implementation.flow.yaml`
- Test: existing `test_verify.py` happy path (the verifier's exact-match rule is the guard; a half-done edit fails it)

**Interfaces:**
- Consumes: `flow:@skaile-ai/impl-build-setup` (new sub-flow node id in every parent: `build-setup`)
- Produces: parents with 6 fewer skill nodes; `requires:` drops 6 `skill:` refs (5 in simple/cli which had no infra... see below) + `contract:@skaile-ai/implementation-contract`, adds 1 `flow:` ref

Each parent edit is one atomic three-part change: (a) `requires:`, (b) `nodes:`, (c) `edges:`. Run the verifier after each parent — it must print `OK: 13 flows consistent` every time.

- [ ] **Step 1: appbuilder-standard.** In `requires:` delete these 7 lines:

```yaml
  - contract:@skaile-ai/implementation-contract
  - skill:@skaile-ai/impl-build-scaffold
  - skill:@skaile-ai/impl-build-foundation
  - skill:@skaile-ai/impl-build-infrastructure
  - skill:@skaile-ai/impl-build-migrate
  - skill:@skaile-ai/impl-build-seed
  - skill:@skaile-ai/impl-build-docs
```

and insert in their place (where the scaffold ref was):

```yaml
  - flow:@skaile-ai/impl-build-setup
```

In `nodes:` delete the six nodes with ids `scaffold`, `foundation`, `infra-opt`, `migrate`, `seed`, `docs` (the whole `# --- Build ---` section) and insert:

```yaml
  # --- Build setup (delegated to the shared impl-build-setup flow) ---
  - id: build-setup
    type: sub-flow
    position:
      x: 4000
      y: 200
    data:
      flow: impl-build-setup
      domain: build
      label: 'One-time build setup'
      pass_context: true
      parameters:
        infrastructure: optional
```

In `edges:` delete the seven edges with ids `e-datamodel-scaffold`, `e-scaffold-foundation`, `e-foundation-infra-opt`, `e-infra-opt-migrate`, `e-migrate-seed`, `e-seed-docs`, `e-docs-slice-loop` and insert:

```yaml
  - id: e-datamodel-build-setup
    source: datamodel
    target: build-setup
    type: flow
  - id: e-build-setup-slice-loop
    source: build-setup
    target: slice-loop
    type: flow
```

- [ ] **Step 2: Verify.** `python3 skaileup/flows/_meta/verify_flows.py` → `OK: 13 flows consistent ... (0 warning(s))`.

- [ ] **Step 3: appbuilder-complex.** Same `requires:` delete/insert as Step 1 (complex lists the identical 7 lines; keep its `meta-concept-contract` line). In `nodes:` delete ids `scaffold`, `foundation`, `infra`, `migrate`, `seed`, `docs` and insert:

```yaml
  # --- Build setup (delegated to the shared impl-build-setup flow) ---
  - id: build-setup
    type: sub-flow
    position:
      x: 5000
      y: 200
    data:
      flow: impl-build-setup
      domain: build
      label: 'One-time build setup (infrastructure required)'
      pass_context: true
      parameters:
        infrastructure: required
```

In `edges:` delete ids `e-datamodel-scaffold`, `e-scaffold-foundation`, `e-foundation-infra`, `e-infra-migrate`, `e-migrate-seed`, `e-seed-docs`, `e-docs-slice-loop` and insert:

```yaml
  - id: e-datamodel-build-setup
    source: datamodel
    target: build-setup
    type: flow
  - id: e-build-setup-slice-loop
    source: build-setup
    target: slice-loop
    type: flow
```

Run the verifier → `OK: 13 flows consistent`.

- [ ] **Step 4: appbuilder-simple.** In `requires:` delete:

```yaml
  - contract:@skaile-ai/implementation-contract
  - skill:@skaile-ai/impl-build-scaffold
  - skill:@skaile-ai/impl-build-foundation
  - skill:@skaile-ai/impl-build-migrate
  - skill:@skaile-ai/impl-build-seed
  - skill:@skaile-ai/impl-build-docs
```

insert `  - flow:@skaile-ai/impl-build-setup` in their place. In `nodes:` delete ids `scaffold`, `foundation`, `migrate`, `seed`, `docs` and insert:

```yaml
  # --- Build setup (delegated to the shared impl-build-setup flow) ---
  - id: build-setup
    type: sub-flow
    position:
      x: 2000
      y: 200
    data:
      flow: impl-build-setup
      domain: build
      label: 'One-time build setup (no infrastructure)'
      pass_context: true
      parameters:
        infrastructure: skip
```

In `edges:` delete ids `e-datamodel-scaffold`, `e-scaffold-foundation`, `e-foundation-migrate`, `e-migrate-seed`, `e-seed-docs`, `e-docs-impl-slice-loop` and insert:

```yaml
  - id: e-datamodel-build-setup
    source: datamodel
    target: build-setup
    type: flow
  - id: e-build-setup-impl-slice-loop
    source: build-setup
    target: impl-slice-loop
    type: flow
```

Run the verifier → `OK: 13 flows consistent`.

- [ ] **Step 5: appbuilder-cli.** Same 6-line `requires:` delete as Step 4, insert `  - flow:@skaile-ai/impl-build-setup`. In `nodes:` delete ids `scaffold`, `foundation`, `migrate`, `seed`, `docs` and insert (the old scaffold/foundation node `parameters` move onto the sub-flow node — `pass_context: true` forwards them):

```yaml
  # --- Build setup (delegated to the shared impl-build-setup flow) ---
  - id: build-setup
    type: sub-flow
    position:
      x: 1200
      y: 200
    data:
      flow: impl-build-setup
      domain: build
      label: 'One-time build setup (headless, data steps optional)'
      pass_context: true
      parameters:
        infrastructure: skip
        data_setup: optional
        project_type: cli
        skip_ui_shell: true
```

In `edges:` delete ids `e-datamodel-scaffold`, `e-scaffold-foundation`, `e-foundation-migrate`, `e-migrate-seed`, `e-foundation-docs`, `e-docs-impl-slice-loop` and insert:

```yaml
  - id: e-datamodel-build-setup
    source: datamodel
    target: build-setup
    type: flow
  - id: e-build-setup-impl-slice-loop
    source: build-setup
    target: impl-slice-loop
    type: flow
```

Run the verifier → `OK: 13 flows consistent`.

- [ ] **Step 6: skaileup-implementation.** In `requires:` delete:

```yaml
  - contract:@skaile-ai/implementation-contract
  - skill:@skaile-ai/impl-build-scaffold
  - skill:@skaile-ai/impl-build-foundation
  - skill:@skaile-ai/impl-build-infrastructure
  - skill:@skaile-ai/impl-build-migrate
  - skill:@skaile-ai/impl-build-seed
  - skill:@skaile-ai/impl-build-docs
```

insert `  - flow:@skaile-ai/impl-build-setup` in their place. In `nodes:` delete ids `scaffold`, `foundation`, `infra-opt`, `migrate`, `seed`, `docs` (the whole `# --- Build setup ---` section) and insert:

```yaml
  # --- Build setup (delegated to the shared impl-build-setup flow) ---
  - id: build-setup
    type: sub-flow
    position:
      x: 600
      y: 200
    data:
      flow: impl-build-setup
      domain: build
      label: 'One-time build setup'
      pass_context: true
      parameters:
        infrastructure: optional
```

In `edges:` delete ids `e-datamodel-scaffold`, `e-scaffold-foundation`, `e-foundation-infra-opt`, `e-infra-opt-migrate`, `e-migrate-seed`, `e-seed-docs`, `e-docs-impl-slice-loop` and insert:

```yaml
  - id: e-datamodel-build-setup
    source: datamodel
    target: build-setup
    type: flow
  - id: e-build-setup-impl-slice-loop
    source: build-setup
    target: impl-slice-loop
    type: flow
```

- [ ] **Step 7: Full green + commit.**

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -q
git add skaileup/flows skaile.yaml
git commit -m "refactor(flows): delegate build setup to impl-build-setup sub-flow

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: `OK: 13 flows consistent`, pytest all pass.

---

### Task 3: Create the `architecture` sub-flow

**Files:**
- Create: `skaileup/flows/architecture/architecture.flow.yaml`
- Create: `skaileup/flows/architecture/architecture.md`
- Modify: `skaileup/flows/_meta/verify_flows.py` (SHARED_FLOWS)
- Modify: `skaile.yaml`
- Test: `skaileup/flows/_meta/test_verify.py` (SHARED_SUBFLOWS list)

**Interfaces:**
- Consumes: `contract:@skaile-ai/shared-contracts`, skills `impl-architecture-{techstack,templates-select,system,datamodel}`
- Produces: flow id `architecture`; globals `templates`, `system`

- [ ] **Step 1: Failing test.** In `test_verify.py`, extend the list to:

```python
SHARED_SUBFLOWS = [
    "impl-build-setup",
    "architecture",
]
```

Run `python3 -m pytest skaileup/flows/_meta/test_verify.py -v -k shared_subflow` → `test_shared_subflow_registered[architecture]` FAILS.

- [ ] **Step 2: Create** `skaileup/flows/architecture/architecture.flow.yaml`:

```yaml
id: architecture
version: '2.0.0'
name: 'Architecture'
description: >-
  Shared architecture block: techstack -> templates-select(opt) -> system(opt)
  -> datamodel. Writes _concept/blueprint/. Consumed via a sub-flow node by
  appbuilder-simple/-standard/-complex/-cli, skaileup-implementation and
  skaileup-concept-only; standalone-runnable for testability. Two globals
  handle consumer variance: templates (include | skip) gates templates-select,
  system (include | skip) gates the system-architecture step.
meta:
  category: concept
  tags:
    - shared-block
    - architecture
    - blueprint
  icon: i-heroicons-cpu-chip
requires:
  # Self-contained install manifest: the shared contract every skill reads +
  # every skill its nodes run (flow node order). Exact — no inheritance, no extras.
  - contract:@skaile-ai/shared-contracts
  - skill:@skaile-ai/impl-architecture-techstack
  - skill:@skaile-ai/impl-architecture-templates-select
  - skill:@skaile-ai/impl-architecture-system
  - skill:@skaile-ai/impl-architecture-datamodel
globals:
  research_depth: light
  approval_mode: checkpoint
  subagent_mode: false
  verbosity: standard
  # include | skip — consumers override via the sub-flow node's parameters;
  # threaded to the templates / arch-system nodes.
  templates: include
  system: include
entry: techstack
nodes:
  - id: techstack
    type: skill
    position:
      x: 0
      y: 200
    data:
      skill: impl-architecture-techstack
      label: 'Tech Stack'
      optional: false
      parameters: {}
  - id: templates
    type: skill
    position:
      x: 200
      y: 200
    data:
      skill: impl-architecture-templates-select
      label: 'Architecture Templates (per parent: include | skip)'
      optional: true
      parameters:
        mode: '${templates}'
  - id: arch-system
    type: skill
    position:
      x: 400
      y: 200
    data:
      skill: impl-architecture-system
      label: 'System Architecture (per parent: include | skip)'
      optional: true
      parameters:
        mode: '${system}'
  - id: datamodel
    type: skill
    position:
      x: 600
      y: 200
    data:
      skill: impl-architecture-datamodel
      label: 'Data Model'
      optional: false
      parameters: {}
edges:
  - id: e-techstack-templates
    source: techstack
    target: templates
    type: optional
  - id: e-templates-arch-system
    source: templates
    target: arch-system
    type: optional
  - id: e-arch-system-datamodel
    source: arch-system
    target: datamodel
    type: flow
```

- [ ] **Step 3: Create** `skaileup/flows/architecture/architecture.md`:

```markdown
---
title: "architecture"
description: "Shared architecture block: techstack → templates-select(opt) → system(opt) → datamodel; writes _concept/blueprint/."
order: 14
---

The **architecture** flow is the shared blueprint block. Six flows delegate to
it via a **sub-flow node** (`appbuilder-simple`, `appbuilder-standard`,
`appbuilder-complex`, `appbuilder-cli`, `skaileup-implementation`,
`skaileup-concept-only`); it is standalone-runnable
(`skaile run flow:architecture`). It writes `_concept/blueprint/` — it belongs
to the **conceptualization** phase even in implementation-led flows.

## Pipeline

```
techstack → templates-select? → system? → datamodel
```

## Variance knobs

| Global | Values | Default | Who overrides |
|---|---|---|---|
| `templates` | `include` \| `skip` | `include` | skaileup-implementation, skaileup-concept-only: `skip` |
| `system` | `include` \| `skip` | `include` | appbuilder-simple, appbuilder-cli: `skip` |

## Install manifest

`architecture.flow.yaml` carries a top-level `requires:` listing
`shared-contracts` and the four `impl-architecture-*` skills.
```

- [ ] **Step 4: Register.** In `verify_flows.py` extend:

```python
SHARED_FLOWS = [
    "impl-build-setup",
    "architecture",
]
```

In `skaile.yaml` bump the comment to `# ── flows (14) ──` and append:

```yaml
  - kind: flow
    name: architecture
    files:
      - skaileup/flows/architecture/architecture.flow.yaml
```

- [ ] **Step 5: Green + commit.**

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -q
git add skaileup/flows skaile.yaml
git commit -m "feat(flows): add shared architecture sub-flow

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: `OK: 14 flows consistent ... (0 warning(s))`.

---

### Task 4: Adopt `architecture` in six parents

**Files:**
- Modify: `skaileup/flows/appbuilder-standard/appbuilder-standard.flow.yaml`
- Modify: `skaileup/flows/appbuilder-complex/appbuilder-complex.flow.yaml`
- Modify: `skaileup/flows/appbuilder-simple/appbuilder-simple.flow.yaml`
- Modify: `skaileup/flows/appbuilder-cli/appbuilder-cli.flow.yaml`
- Modify: `skaileup/flows/skaileup-implementation/skaileup-implementation.flow.yaml` (incl. `entry:`)
- Modify: `skaileup/flows/skaileup-concept-only/skaileup-concept-only.flow.yaml`
- Test: verifier exact-match rule (run after each parent)

**Interfaces:**
- Consumes: `flow:@skaile-ai/architecture` (sub-flow node id in every parent: `architecture`)
- Produces: parents without inline `impl-architecture-*` nodes

- [ ] **Step 1: appbuilder-standard.** `requires:` — delete:

```yaml
  - skill:@skaile-ai/impl-architecture-techstack
  - skill:@skaile-ai/impl-architecture-templates-select
  - skill:@skaile-ai/impl-architecture-system
  - skill:@skaile-ai/impl-architecture-datamodel
```

insert `  - flow:@skaile-ai/architecture` in their place. `nodes:` — delete ids `techstack`, `templates`, `arch-system`, `datamodel` (the `# --- Architecture ---` section) and insert:

```yaml
  # --- Architecture (delegated to the shared architecture flow) ---
  - id: architecture
    type: sub-flow
    position:
      x: 3200
      y: 200
    data:
      flow: architecture
      domain: blueprint
      label: 'Architecture blueprint'
      pass_context: true
      parameters: {}
```

`edges:` — delete ids `e-feedback-apply-techstack`, `e-techstack-templates`, `e-templates-arch-system`, `e-arch-system-datamodel`, `e-datamodel-build-setup` and insert:

```yaml
  - id: e-feedback-apply-architecture
    source: feedback-apply
    target: architecture
    type: flow
  - id: e-architecture-build-setup
    source: architecture
    target: build-setup
    type: flow
```

Verify → `OK: 14 flows consistent`.

- [ ] **Step 2: appbuilder-complex.** Same 4-line `requires:` delete, insert `  - flow:@skaile-ai/architecture`. `nodes:` — delete ids `techstack`, `templates`, `arch-system`, `datamodel`; insert the same sub-flow node block as Step 1 but with `position: {x: 4200, y: 200}` (write it out in full):

```yaml
  # --- Architecture (delegated to the shared architecture flow) ---
  - id: architecture
    type: sub-flow
    position:
      x: 4200
      y: 200
    data:
      flow: architecture
      domain: blueprint
      label: 'Architecture blueprint'
      pass_context: true
      parameters: {}
```

`edges:` — delete ids `e-ops-project-review-techstack`, `e-techstack-templates`, `e-templates-arch-system`, `e-arch-system-datamodel`, `e-datamodel-build-setup`; insert:

```yaml
  - id: e-ops-project-review-architecture
    source: ops-project-review
    target: architecture
    type: flow
  - id: e-architecture-build-setup
    source: architecture
    target: build-setup
    type: flow
```

Verify → OK.

- [ ] **Step 3: appbuilder-simple.** `requires:` — delete the three lines `skill:@skaile-ai/impl-architecture-techstack`, `-templates-select`, `-datamodel`; insert `  - flow:@skaile-ai/architecture`. `nodes:` — delete ids `techstack`, `templates`, `datamodel`; insert:

```yaml
  # --- Architecture (delegated to the shared architecture flow) ---
  - id: architecture
    type: sub-flow
    position:
      x: 1400
      y: 200
    data:
      flow: architecture
      domain: blueprint
      label: 'Architecture blueprint (no system step)'
      pass_context: true
      parameters:
        system: skip
```

`edges:` — delete ids `e-mock-static-techstack`, `e-comp-isolated-techstack`, `e-techstack-templates`, `e-templates-datamodel`, `e-datamodel-build-setup`; insert:

```yaml
  - id: e-mock-static-architecture
    source: mock-static
    target: architecture
    type: flow
  - id: e-comp-isolated-architecture
    source: comp-isolated
    target: architecture
    type: flow
  - id: e-architecture-build-setup
    source: architecture
    target: build-setup
    type: flow
```

Verify → OK.

- [ ] **Step 4: appbuilder-cli.** `requires:` — delete the three lines `skill:@skaile-ai/impl-architecture-techstack`, `-templates-select`, `-datamodel`; insert `  - flow:@skaile-ai/architecture`. `nodes:` — delete ids `techstack`, `templates`, `datamodel`; insert (the old datamodel `note` parameter moves onto the sub-flow node):

```yaml
  # --- Architecture (delegated to the shared architecture flow) ---
  - id: architecture
    type: sub-flow
    position:
      x: 600
      y: 200
    data:
      flow: architecture
      domain: blueprint
      label: 'Architecture blueprint (no system step)'
      pass_context: true
      parameters:
        system: skip
        note: 'Datamodel covers config files, storage schemas, output formats'
```

`edges:` — delete ids `e-features-techstack`, `e-techstack-templates`, `e-templates-datamodel`, `e-datamodel-build-setup`; insert:

```yaml
  - id: e-features-architecture
    source: features
    target: architecture
    type: flow
  - id: e-architecture-build-setup
    source: architecture
    target: build-setup
    type: flow
```

Verify → OK.

- [ ] **Step 5: skaileup-implementation.** `requires:` — delete the three lines `skill:@skaile-ai/impl-architecture-techstack`, `-system`, `-datamodel`; insert `  - flow:@skaile-ai/architecture`. Change `entry: techstack` to `entry: architecture`. `nodes:` — delete ids `techstack`, `arch-system`, `datamodel` (the `# --- Technical concept subset ---` section); insert:

```yaml
  # --- Architecture (read-or-generate; delegated to the shared architecture flow) ---
  - id: architecture
    type: sub-flow
    position:
      x: 0
      y: 200
    data:
      flow: architecture
      domain: blueprint
      label: 'Architecture blueprint (read-or-generate, no templates step)'
      pass_context: true
      parameters:
        templates: skip
        note: 'Read _concept/blueprint/ if present, else generate from a one-line product description'
```

`edges:` — delete ids `e-techstack-arch-system`, `e-arch-system-datamodel`, `e-datamodel-build-setup`; insert:

```yaml
  - id: e-architecture-build-setup
    source: architecture
    target: build-setup
    type: flow
```

Verify → OK.

- [ ] **Step 6: skaileup-concept-only.** `requires:` — delete the three lines `skill:@skaile-ai/impl-architecture-techstack`, `-system`, `-datamodel`; insert `  - flow:@skaile-ai/architecture`. `nodes:` — delete ids `techstack`, `system`, `datamodel` (the `# --- Architecture ---` section); insert:

```yaml
  # --- Architecture (delegated to the shared architecture flow) ---
  - id: architecture
    type: sub-flow
    position:
      x: 2200
      y: 200
    data:
      flow: architecture
      domain: blueprint
      label: 'Architecture blueprint (no templates step)'
      pass_context: true
      parameters:
        templates: skip
```

`edges:` — delete ids `e-screens-techstack`, `e-techstack-system`, `e-techstack-datamodel`, `e-system-mock`, `e-datamodel-mock`, `e-datamodel-review`; insert:

```yaml
  - id: e-screens-architecture
    source: screens
    target: architecture
    type: flow
  - id: e-architecture-mock
    source: architecture
    target: mock
    type: optional
  - id: e-architecture-review
    source: architecture
    target: review
    type: flow
```

- [ ] **Step 7: Full green + commit.**

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -q
git add skaileup/flows
git commit -m "refactor(flows): delegate blueprint pass to architecture sub-flow

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: `OK: 14 flows consistent`, pytest all pass.

---

### Task 5: Create the `mockup-feedback` sub-flow

**Files:**
- Create: `skaileup/flows/mockup-feedback/mockup-feedback.flow.yaml`
- Create: `skaileup/flows/mockup-feedback/mockup-feedback.md`
- Modify: `skaileup/flows/_meta/verify_flows.py`, `skaile.yaml`
- Test: `skaileup/flows/_meta/test_verify.py`

**Interfaces:**
- Consumes: `contract:@skaile-ai/shared-contracts`, skills `mockup-feedback-{annotate,triage,patch,apply}`
- Produces: flow id `mockup-feedback` (no variance knobs — the block is byte-identical in both parents)

- [ ] **Step 1: Failing test.** Extend in `test_verify.py`:

```python
SHARED_SUBFLOWS = [
    "impl-build-setup",
    "architecture",
    "mockup-feedback",
]
```

Run `python3 -m pytest skaileup/flows/_meta/test_verify.py -v -k shared_subflow` → `[mockup-feedback]` FAILS.

- [ ] **Step 2: Create** `skaileup/flows/mockup-feedback/mockup-feedback.flow.yaml` (extracted verbatim from the identical appbuilder-standard/-complex cluster, positions normalized):

```yaml
id: mockup-feedback
version: '2.0.0'
name: 'Mockup Feedback'
description: >-
  Shared mockup-feedback cluster: annotate -> triage -> patch -> apply, all
  optional. Extracted verbatim from the byte-identical block in
  appbuilder-standard and appbuilder-complex; consumed by both via a sub-flow
  node after the mockup renderers. Standalone-runnable for testability.
meta:
  category: prototype
  tags:
    - shared-block
    - mockup-feedback
  icon: i-heroicons-chat-bubble-left-ellipsis
requires:
  # Self-contained install manifest: the shared contract every skill reads +
  # every skill its nodes run (flow node order). Exact — no inheritance, no extras.
  - contract:@skaile-ai/shared-contracts
  - skill:@skaile-ai/mockup-feedback-annotate
  - skill:@skaile-ai/mockup-feedback-triage
  - skill:@skaile-ai/mockup-feedback-patch
  - skill:@skaile-ai/mockup-feedback-apply
globals:
  research_depth: skip
  approval_mode: checkpoint
  subagent_mode: false
  verbosity: standard
entry: feedback-annotate
nodes:
  - id: feedback-annotate
    type: skill
    position:
      x: 0
      y: 200
    data:
      skill: mockup-feedback-annotate
      label: 'Mockup Feedback: Annotate'
      optional: true
      parameters: {}
  - id: feedback-triage
    type: skill
    position:
      x: 200
      y: 200
    data:
      skill: mockup-feedback-triage
      label: 'Mockup Feedback: Triage'
      optional: true
      parameters: {}
  - id: feedback-patch
    type: skill
    position:
      x: 400
      y: 200
    data:
      skill: mockup-feedback-patch
      label: 'Mockup Feedback: Patch'
      optional: true
      parameters: {}
  - id: feedback-apply
    type: skill
    position:
      x: 600
      y: 200
    data:
      skill: mockup-feedback-apply
      label: 'Mockup Feedback: Apply'
      optional: true
      parameters: {}
edges:
  - id: e-feedback-annotate-feedback-triage
    source: feedback-annotate
    target: feedback-triage
    type: optional
  - id: e-feedback-triage-feedback-patch
    source: feedback-triage
    target: feedback-patch
    type: optional
  - id: e-feedback-patch-feedback-apply
    source: feedback-patch
    target: feedback-apply
    type: optional
```

- [ ] **Step 3: Create** `skaileup/flows/mockup-feedback/mockup-feedback.md`:

```markdown
---
title: "mockup-feedback"
description: "Shared mockup-feedback cluster: annotate → triage → patch → apply (all optional)."
order: 15
---

The **mockup-feedback** flow is the shared feedback loop over mockups:
annotate → triage → patch → apply, every step optional. It was byte-identical
in `appbuilder-standard` and `appbuilder-complex`; both now delegate to it via
a **sub-flow node** after the mockup renderers. Standalone-runnable
(`skaile run flow:mockup-feedback`) against an existing
`_concept/mockup-walkthrough/` or `_concept/mockup-component/` tree.

## Pipeline

```
annotate? → triage? → patch? → apply?
```

## Install manifest

`mockup-feedback.flow.yaml` carries a top-level `requires:` listing
`shared-contracts` and the four `mockup-feedback-*` skills.
```

- [ ] **Step 4: Register.** `verify_flows.py`:

```python
SHARED_FLOWS = [
    "impl-build-setup",
    "architecture",
    "mockup-feedback",
]
```

`skaile.yaml`: bump comment to `# ── flows (15) ──`, append:

```yaml
  - kind: flow
    name: mockup-feedback
    files:
      - skaileup/flows/mockup-feedback/mockup-feedback.flow.yaml
```

- [ ] **Step 5: Green + commit.**

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -q
git add skaileup/flows skaile.yaml
git commit -m "feat(flows): add shared mockup-feedback sub-flow

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: `OK: 15 flows consistent ... (0 warning(s))`.

---

### Task 6: Adopt `mockup-feedback` in appbuilder-standard and appbuilder-complex

**Files:**
- Modify: `skaileup/flows/appbuilder-standard/appbuilder-standard.flow.yaml`
- Modify: `skaileup/flows/appbuilder-complex/appbuilder-complex.flow.yaml`
- Test: verifier exact-match rule

**Interfaces:**
- Consumes: `flow:@skaile-ai/mockup-feedback` (sub-flow node id: `feedback`)
- Produces: parents without inline `mockup-feedback-*` nodes

- [ ] **Step 1: appbuilder-standard.** `requires:` — delete:

```yaml
  - skill:@skaile-ai/mockup-feedback-annotate
  - skill:@skaile-ai/mockup-feedback-triage
  - skill:@skaile-ai/mockup-feedback-patch
  - skill:@skaile-ai/mockup-feedback-apply
```

insert `  - flow:@skaile-ai/mockup-feedback` in their place. `nodes:` — delete ids `feedback-annotate`, `feedback-triage`, `feedback-patch`, `feedback-apply` (the `# --- Mockup feedback cluster ---` section) and insert:

```yaml
  # --- Mockup feedback (delegated to the shared mockup-feedback flow) ---
  - id: feedback
    type: sub-flow
    position:
      x: 2400
      y: 200
    data:
      flow: mockup-feedback
      domain: mockup
      label: 'Mockup feedback loop'
      pass_context: true
      parameters: {}
```

`edges:` — delete ids `e-mock-walkthrough-feedback-annotate`, `e-mock-static-fallback-feedback-annotate`, `e-comp-storybook-feedback-annotate`, `e-feedback-annotate-feedback-triage`, `e-feedback-triage-feedback-patch`, `e-feedback-patch-feedback-apply`, `e-feedback-apply-architecture`; insert:

```yaml
  - id: e-mock-walkthrough-feedback
    source: mock-walkthrough
    target: feedback
    type: optional
  - id: e-mock-static-fallback-feedback
    source: mock-static-fallback
    target: feedback
    type: optional
  - id: e-comp-storybook-feedback
    source: comp-storybook
    target: feedback
    type: optional
  - id: e-feedback-architecture
    source: feedback
    target: architecture
    type: flow
```

Verify → `OK: 15 flows consistent`.

- [ ] **Step 2: appbuilder-complex.** Same 4-line `requires:` delete, insert `  - flow:@skaile-ai/mockup-feedback`. `nodes:` — delete ids `feedback-annotate`, `feedback-triage`, `feedback-patch`, `feedback-apply`; insert:

```yaml
  # --- Mockup feedback (delegated to the shared mockup-feedback flow) ---
  - id: feedback
    type: sub-flow
    position:
      x: 2600
      y: 200
    data:
      flow: mockup-feedback
      domain: mockup
      label: 'Mockup feedback loop'
      pass_context: true
      parameters: {}
```

`edges:` — delete ids `e-mock-walkthrough-astro-feedback-annotate`, `e-mock-framework-feedback-annotate`, `e-mock-static-fallback-feedback-annotate`, `e-comp-storybook-feedback-annotate`, `e-feedback-annotate-feedback-triage`, `e-feedback-triage-feedback-patch`, `e-feedback-patch-feedback-apply`, `e-feedback-apply-ops-project-overview`; insert:

```yaml
  - id: e-mock-walkthrough-astro-feedback
    source: mock-walkthrough-astro
    target: feedback
    type: optional
  - id: e-mock-framework-feedback
    source: mock-framework
    target: feedback
    type: optional
  - id: e-mock-static-fallback-feedback
    source: mock-static-fallback
    target: feedback
    type: optional
  - id: e-comp-storybook-feedback
    source: comp-storybook
    target: feedback
    type: optional
  - id: e-feedback-ops-project-overview
    source: feedback
    target: ops-project-overview
    type: flow
```

- [ ] **Step 3: Green + commit.**

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -q
git add skaileup/flows
git commit -m "refactor(flows): delegate mockup feedback to mockup-feedback sub-flow

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: `OK: 15 flows consistent`.

---

### Task 7: Create the `quality-gate` sub-flow

**Files:**
- Create: `skaileup/flows/quality-gate/quality-gate.flow.yaml`
- Create: `skaileup/flows/quality-gate/quality-gate.md`
- Modify: `skaileup/flows/_meta/verify_flows.py`, `skaile.yaml`
- Test: `skaileup/flows/_meta/test_verify.py`

**Interfaces:**
- Consumes: `contract:@skaile-ai/shared-contracts`, skills `impl-quality-test-{unit,integration,e2e}`, `impl-quality-ready`, `ops-review`, `ops-sync`
- Produces: flow id `quality-gate`; globals `e2e`, `ops_tail`

- [ ] **Step 1: Failing test.** Extend in `test_verify.py`:

```python
SHARED_SUBFLOWS = [
    "impl-build-setup",
    "architecture",
    "mockup-feedback",
    "quality-gate",
]
```

Run pytest `-k shared_subflow` → `[quality-gate]` FAILS.

- [ ] **Step 2: Create** `skaileup/flows/quality-gate/quality-gate.flow.yaml`:

```yaml
id: quality-gate
version: '2.0.0'
name: 'Quality Gate'
description: >-
  Shared post-loop quality gate: test-unit -> test-integration -> test-e2e ->
  ready, plus the optional ops tail review -> sync. Consumed via a sub-flow
  node by appbuilder-standard, appbuilder-complex and skaileup-implementation;
  standalone-runnable for testability. Two globals handle consumer variance:
  e2e (required | optional) and ops_tail (include | skip — implementation
  skips the review/sync tail). NOTE: the review-spine plan wires its new
  review skills into this flow — land this plan first.
meta:
  category: maintenance
  tags:
    - shared-block
    - quality
  icon: i-heroicons-shield-check
requires:
  # Self-contained install manifest: the shared contract every skill reads +
  # every skill its nodes run (flow node order). Exact — no inheritance, no extras.
  - contract:@skaile-ai/shared-contracts
  - skill:@skaile-ai/impl-quality-test-unit
  - skill:@skaile-ai/impl-quality-test-integration
  - skill:@skaile-ai/impl-quality-test-e2e
  - skill:@skaile-ai/impl-quality-ready
  - skill:@skaile-ai/ops-review
  - skill:@skaile-ai/ops-sync
globals:
  research_depth: skip
  approval_mode: checkpoint
  subagent_mode: false
  verbosity: standard
  # required | optional — consumers override via the sub-flow node's
  # parameters.e2e; threaded to the q-test-e2e node.
  e2e: required
  # include | skip — consumers override via the sub-flow node's
  # parameters.ops_tail; threaded to ops-review + ops-sync.
  ops_tail: include
entry: q-test-unit
nodes:
  - id: q-test-unit
    type: skill
    position:
      x: 0
      y: 200
    data:
      skill: impl-quality-test-unit
      label: 'Unit Tests'
      optional: false
      parameters: {}
  - id: q-test-integration
    type: skill
    position:
      x: 200
      y: 200
    data:
      skill: impl-quality-test-integration
      label: 'Integration Tests'
      optional: false
      parameters: {}
  - id: q-test-e2e
    type: skill
    position:
      x: 400
      y: 200
    data:
      skill: impl-quality-test-e2e
      label: 'E2E Tests (per parent: required | optional)'
      optional: false
      parameters:
        mode: '${e2e}'
  - id: q-ready
    type: skill
    position:
      x: 600
      y: 200
    data:
      skill: impl-quality-ready
      label: 'Release Ready'
      optional: false
      parameters: {}
  - id: ops-review
    type: skill
    position:
      x: 800
      y: 200
    data:
      skill: ops-review
      label: 'Ops Review (per parent: include | skip)'
      optional: true
      parameters:
        mode: '${ops_tail}'
  - id: ops-sync
    type: skill
    position:
      x: 1000
      y: 200
    data:
      skill: ops-sync
      label: 'Ops Sync (per parent: include | skip)'
      optional: true
      parameters:
        mode: '${ops_tail}'
edges:
  - id: e-q-test-unit-q-test-integration
    source: q-test-unit
    target: q-test-integration
    type: flow
  - id: e-q-test-integration-q-test-e2e
    source: q-test-integration
    target: q-test-e2e
    type: flow
  - id: e-q-test-e2e-q-ready
    source: q-test-e2e
    target: q-ready
    type: flow
  - id: e-q-ready-ops-review
    source: q-ready
    target: ops-review
    type: optional
  - id: e-ops-review-ops-sync
    source: ops-review
    target: ops-sync
    type: optional
```

- [ ] **Step 3: Create** `skaileup/flows/quality-gate/quality-gate.md`:

```markdown
---
title: "quality-gate"
description: "Shared post-loop quality gate: unit → integration → e2e → ready, plus the optional ops review → sync tail."
order: 16
---

The **quality-gate** flow is the shared post-loop quality gate.
`appbuilder-standard`, `appbuilder-complex` and `skaileup-implementation`
delegate to it via a **sub-flow node** after their slice loop; it is
standalone-runnable (`skaile run flow:quality-gate`). `appbuilder-simple`
(unit + e2e) and `appbuilder-cli` (unit + integration) run subsets and keep
their inline quality nodes.

## Pipeline

```
test-unit → test-integration → test-e2e → ready → ops-review? → ops-sync?
```

## Variance knobs

| Global | Values | Default | Who overrides |
|---|---|---|---|
| `e2e` | `required` \| `optional` | `required` | skaileup-implementation: `optional` |
| `ops_tail` | `include` \| `skip` | `include` | skaileup-implementation: `skip` |

## Install manifest

`quality-gate.flow.yaml` carries a top-level `requires:` listing
`shared-contracts`, the four `impl-quality-*` gate skills and the
`ops-review` / `ops-sync` tail.
```

- [ ] **Step 4: Register.** `verify_flows.py`:

```python
SHARED_FLOWS = [
    "impl-build-setup",
    "architecture",
    "mockup-feedback",
    "quality-gate",
]
```

`skaile.yaml`: bump comment to `# ── flows (16) ──`, append:

```yaml
  - kind: flow
    name: quality-gate
    files:
      - skaileup/flows/quality-gate/quality-gate.flow.yaml
```

- [ ] **Step 5: Green + commit.**

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -q
git add skaileup/flows skaile.yaml
git commit -m "feat(flows): add shared quality-gate sub-flow

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: `OK: 16 flows consistent ... (0 warning(s))`.

---

### Task 8: Adopt `quality-gate` in standard, complex, implementation

**Files:**
- Modify: `skaileup/flows/appbuilder-standard/appbuilder-standard.flow.yaml`
- Modify: `skaileup/flows/appbuilder-complex/appbuilder-complex.flow.yaml`
- Modify: `skaileup/flows/skaileup-implementation/skaileup-implementation.flow.yaml`
- Test: verifier exact-match rule

**Interfaces:**
- Consumes: `flow:@skaile-ai/quality-gate` (sub-flow node id: `quality`)
- Produces: parents without inline `impl-quality-test-*` / `impl-quality-ready` / `ops-review` / `ops-sync` nodes (complex keeps its per-slice `q-eval-code` + `q-audit`)

- [ ] **Step 1: appbuilder-standard.** `requires:` — delete:

```yaml
  - skill:@skaile-ai/impl-quality-test-unit
  - skill:@skaile-ai/impl-quality-test-integration
  - skill:@skaile-ai/impl-quality-test-e2e
  - skill:@skaile-ai/impl-quality-ready
  - skill:@skaile-ai/ops-review
  - skill:@skaile-ai/ops-sync
```

insert `  - flow:@skaile-ai/quality-gate` in their place. `nodes:` — delete ids `q-test-unit`, `q-test-integration`, `q-test-e2e`, `q-ready`, `ops-review`, `ops-sync` (the `# --- Quality ---` and `# --- Ops ---` sections) and insert:

```yaml
  # --- Quality gate (delegated to the shared quality-gate flow) ---
  - id: quality
    type: sub-flow
    position:
      x: 7400
      y: 200
    data:
      flow: quality-gate
      domain: quality
      label: 'Quality gate + ops tail'
      pass_context: true
      parameters: {}
```

`edges:` — delete ids `e-slice-loop-q-test-unit`, `e-q-test-unit-q-test-integration`, `e-q-test-integration-q-test-e2e`, `e-q-test-e2e-q-ready`, `e-q-ready-ops-review`, `e-ops-review-ops-sync`; insert:

```yaml
  - id: e-slice-loop-quality
    source: slice-loop
    target: quality
    type: flow
```

Verify → `OK: 16 flows consistent`.

- [ ] **Step 2: appbuilder-complex.** Same 6-line `requires:` delete (keep `impl-quality-eval-code` + `impl-quality-audit`), insert `  - flow:@skaile-ai/quality-gate`. `nodes:` — delete ids `q-test-unit`, `q-test-integration`, `q-test-e2e`, `q-ready`, `ops-review`, `ops-sync` (keep `q-eval-code`, `q-audit`); insert:

```yaml
  # --- Quality gate (delegated to the shared quality-gate flow) ---
  - id: quality
    type: sub-flow
    position:
      x: 9200
      y: 200
    data:
      flow: quality-gate
      domain: quality
      label: 'Quality gate + ops tail'
      pass_context: true
      parameters: {}
```

`edges:` — delete ids `e-q-audit-q-test-unit`, `e-q-test-unit-q-test-integration`, `e-q-test-integration-q-test-e2e`, `e-q-test-e2e-q-ready`, `e-q-ready-ops-review`, `e-ops-review-ops-sync`; insert:

```yaml
  - id: e-q-audit-quality
    source: q-audit
    target: quality
    type: flow
```

Verify → OK.

- [ ] **Step 3: skaileup-implementation.** `requires:` — delete:

```yaml
  - skill:@skaile-ai/impl-quality-test-unit
  - skill:@skaile-ai/impl-quality-test-integration
  - skill:@skaile-ai/impl-quality-test-e2e
  - skill:@skaile-ai/impl-quality-ready
```

insert `  - flow:@skaile-ai/quality-gate` in their place. (After this the flow's `requires:` is exactly `contract:@skaile-ai/shared-contracts` + four `flow:` refs and it has zero skill nodes — that is correct and verifier-clean.) `nodes:` — delete ids `q-test-unit`, `q-test-integration`, `q-test-e2e`, `q-ready` (the `# --- Quality ---` section); insert:

```yaml
  # --- Quality gate (delegated to the shared quality-gate flow; no ops tail) ---
  - id: quality
    type: sub-flow
    position:
      x: 2000
      y: 200
    data:
      flow: quality-gate
      domain: quality
      label: 'Quality gate (e2e optional, no ops tail)'
      pass_context: true
      parameters:
        e2e: optional
        ops_tail: skip
```

`edges:` — delete ids `e-impl-slice-loop-q-test-unit`, `e-q-test-unit-q-test-integration`, `e-q-test-integration-q-test-e2e`, `e-q-test-e2e-q-ready`; insert:

```yaml
  - id: e-impl-slice-loop-quality
    source: impl-slice-loop
    target: quality
    type: flow
```

- [ ] **Step 4: Green + commit.**

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -q
git add skaileup/flows
git commit -m "refactor(flows): delegate post-loop quality to quality-gate sub-flow

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: `OK: 16 flows consistent`.

---

### Task 9: Create the `concept-discovery` sub-flow

**Files:**
- Create: `skaileup/flows/concept-discovery/concept-discovery.flow.yaml`
- Create: `skaileup/flows/concept-discovery/concept-discovery.md`
- Modify: `skaileup/flows/_meta/verify_flows.py`, `skaile.yaml`
- Test: `skaileup/flows/_meta/test_verify.py`

**Interfaces:**
- Consumes: `contract:@skaile-ai/shared-contracts`, skills `concept-brief`, `concept-goals`, `concept-comparable`
- Produces: flow id `concept-discovery`; global `goals`

- [ ] **Step 1: Failing test.** Extend in `test_verify.py`:

```python
SHARED_SUBFLOWS = [
    "impl-build-setup",
    "architecture",
    "mockup-feedback",
    "quality-gate",
    "concept-discovery",
]
```

Run pytest `-k shared_subflow` → `[concept-discovery]` FAILS.

- [ ] **Step 2: Create** `skaileup/flows/concept-discovery/concept-discovery.flow.yaml`:

```yaml
id: concept-discovery
version: '2.0.0'
name: 'Concept Discovery'
description: >-
  Shared discovery block: brief -> goals(opt) -> comparable(opt). The opening
  concept pass of the discovery-bearing flows; consumed via a sub-flow node by
  appbuilder-standard, appbuilder-complex and skaileup-concept-only;
  standalone-runnable for testability. A goals global (optional | required)
  controls whether the goals step may be skipped — concept-only requires it.
meta:
  category: concept
  tags:
    - shared-block
    - discovery
  icon: i-heroicons-document-text
requires:
  # Self-contained install manifest: the shared contract every skill reads +
  # every skill its nodes run (flow node order). Exact — no inheritance, no extras.
  - contract:@skaile-ai/shared-contracts
  - skill:@skaile-ai/concept-brief
  - skill:@skaile-ai/concept-goals
  - skill:@skaile-ai/concept-comparable
globals:
  research_depth: light
  approval_mode: checkpoint
  subagent_mode: false
  verbosity: standard
  # optional | required — consumers override via the sub-flow node's
  # parameters.goals; threaded to the goals node.
  goals: optional
entry: brief
nodes:
  - id: brief
    type: skill
    position:
      x: 0
      y: 200
    data:
      skill: concept-brief
      label: 'Concept Brief'
      optional: false
      parameters: {}
  - id: goals
    type: skill
    position:
      x: 200
      y: 200
    data:
      skill: concept-goals
      label: 'Concept Goals (per parent: optional | required)'
      optional: true
      parameters:
        mode: '${goals}'
  - id: comparable
    type: skill
    position:
      x: 400
      y: 200
    data:
      skill: concept-comparable
      label: 'Comparable'
      optional: true
      parameters: {}
edges:
  - id: e-brief-goals
    source: brief
    target: goals
    type: optional
  - id: e-goals-comparable
    source: goals
    target: comparable
    type: optional
```

- [ ] **Step 3: Create** `skaileup/flows/concept-discovery/concept-discovery.md`:

```markdown
---
title: "concept-discovery"
description: "Shared discovery block: brief → goals(opt) → comparable(opt)."
order: 17
---

The **concept-discovery** flow is the shared opening discovery pass.
`appbuilder-standard`, `appbuilder-complex` and `skaileup-concept-only`
delegate to it via a **sub-flow node**; it is standalone-runnable
(`skaile run flow:concept-discovery`). Tiers that run `concept-brief` alone
(`appbuilder-mvp`, `appbuilder-simple`, `appbuilder-cli`,
`skaileup-stepwise`) keep it inline.

## Pipeline

```
brief → goals? → comparable?
```

## Variance knobs

| Global | Values | Default | Who overrides |
|---|---|---|---|
| `goals` | `optional` \| `required` | `optional` | skaileup-concept-only: `required` |

## Install manifest

`concept-discovery.flow.yaml` carries a top-level `requires:` listing
`shared-contracts` plus `concept-brief`, `concept-goals`, `concept-comparable`.
```

- [ ] **Step 4: Register.** `verify_flows.py`:

```python
SHARED_FLOWS = [
    "impl-build-setup",
    "architecture",
    "mockup-feedback",
    "quality-gate",
    "concept-discovery",
]
```

`skaile.yaml`: bump comment to `# ── flows (17) ──`, append:

```yaml
  - kind: flow
    name: concept-discovery
    files:
      - skaileup/flows/concept-discovery/concept-discovery.flow.yaml
```

- [ ] **Step 5: Green + commit.**

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -q
git add skaileup/flows skaile.yaml
git commit -m "feat(flows): add shared concept-discovery sub-flow

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: `OK: 17 flows consistent ... (0 warning(s))`.

---

### Task 10: Adopt `concept-discovery` in standard, complex, concept-only

**Files:**
- Modify: `skaileup/flows/appbuilder-standard/appbuilder-standard.flow.yaml`
- Modify: `skaileup/flows/appbuilder-complex/appbuilder-complex.flow.yaml`
- Modify: `skaileup/flows/skaileup-concept-only/skaileup-concept-only.flow.yaml`
- Test: verifier exact-match rule

**Interfaces:**
- Consumes: `flow:@skaile-ai/concept-discovery` (sub-flow node id: `discovery`)
- Produces: parents without inline `brief` / `goals` / `comparable` nodes

- [ ] **Step 1: appbuilder-standard.** `requires:` — delete:

```yaml
  - skill:@skaile-ai/concept-brief
  - skill:@skaile-ai/concept-goals
  - skill:@skaile-ai/concept-comparable
```

insert `  - flow:@skaile-ai/concept-discovery` in their place. `nodes:` — delete ids `brief`, `goals`, `comparable`; insert:

```yaml
  # --- Discovery (delegated to the shared concept-discovery flow) ---
  - id: discovery
    type: sub-flow
    position:
      x: 200
      y: 200
    data:
      flow: concept-discovery
      domain: discovery
      label: 'Concept discovery (brief, goals, comparable)'
      pass_context: true
      parameters: {}
```

`edges:` — delete ids `e-scope-brief`, `e-brief-goals`, `e-goals-comparable`, `e-comparable-brand-visual`; insert:

```yaml
  - id: e-scope-discovery
    source: scope
    target: discovery
    type: flow
  - id: e-discovery-brand-visual
    source: discovery
    target: brand-visual
    type: flow
```

Verify → `OK: 17 flows consistent`.

- [ ] **Step 2: appbuilder-complex.** Same 3-line `requires:` delete, insert `  - flow:@skaile-ai/concept-discovery`. `nodes:` — delete ids `brief`, `goals`, `comparable`; insert the same `discovery` node block as Step 1 (position `x: 200, y: 200`, identical YAML). `edges:` — delete ids `e-scope-brief`, `e-brief-goals`, `e-goals-comparable`, `e-comparable-brand-visual`; insert:

```yaml
  - id: e-scope-discovery
    source: scope
    target: discovery
    type: flow
  - id: e-discovery-brand-visual
    source: discovery
    target: brand-visual
    type: flow
```

Verify → OK.

- [ ] **Step 3: skaileup-concept-only.** Same 3-line `requires:` delete, insert `  - flow:@skaile-ai/concept-discovery`. `nodes:` — delete ids `brief`, `goals`, `comparable` (the `# --- Discovery ---` section); insert:

```yaml
  # --- Discovery (delegated to the shared concept-discovery flow) ---
  - id: discovery
    type: sub-flow
    position:
      x: 600
      y: 200
    data:
      flow: concept-discovery
      domain: discovery
      label: 'Concept discovery (goals required)'
      pass_context: true
      parameters:
        goals: required
```

`edges:` — delete ids `e-onboard-brief`, `e-brief-goals`, `e-brief-comparable`, `e-goals-brand-visual`; insert:

```yaml
  - id: e-onboard-discovery
    source: onboard
    target: discovery
    type: flow
  - id: e-discovery-brand-visual
    source: discovery
    target: brand-visual
    type: flow
```

- [ ] **Step 4: Green + commit.**

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -q
git add skaileup/flows
git commit -m "refactor(flows): delegate discovery to concept-discovery sub-flow

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: `OK: 17 flows consistent`.

---

### Task 11: Schema `phase` support + verifier parentNode check (TDD)

**Files:**
- Modify: `skaileup/contracts/flow.schema.json` — skill-node `data` (~line 231, after `parameters`), sub-flow-node `data` (~line 412, after `parameters`), group-node `data.phase` (~line 254)
- Modify: `skaileup/flows/_meta/verify_flows.py` (new structural-check section)
- Test: `skaileup/flows/_meta/test_verify.py`

**Interfaces:**
- Consumes: existing `group-node` / `skill-node` / `sub-flow-node` `$defs`
- Produces: `data.phase` enum `["conceptualization", "implementation", "review"]` on skill, sub-flow, and group nodes; verifier error `node X has parentNode Y which is not a group node`

- [ ] **Step 1: Failing schema test.** Append to `test_verify.py`:

```python
# ---------------------------------------------------------------------------
# Case 11: schema accepts node-level phase; group phase is enum-constrained
# ---------------------------------------------------------------------------
def test_schema_accepts_phase_fields():
    import jsonschema

    schema = json.loads(SCHEMA.read_text())
    flow = {
        "id": "smoke",
        "name": "Smoke",
        "nodes": [
            {"id": "g1", "type": "group", "position": {"x": 0, "y": 0},
             "data": {"label": "Conceptualization", "phase": "conceptualization"}},
            {"id": "s1", "type": "skill", "position": {"x": 0, "y": 0},
             "parentNode": "g1",
             "data": {"skill": "impl-slice-implement", "phase": "implementation"}},
            {"id": "sf1", "type": "sub-flow", "position": {"x": 100, "y": 0},
             "data": {"flow": "quality-gate", "phase": "review"}},
        ],
        "edges": [],
    }
    jsonschema.validate(flow, schema)
    # a bogus phase value must be rejected
    flow["nodes"][0]["data"]["phase"] = "not-a-phase"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(flow, schema)


# ---------------------------------------------------------------------------
# Case 12: dangling parentNode → exit 2
# ---------------------------------------------------------------------------
def test_dangling_parent_node_fails(tmp_path):
    verifier = _build_scratch_repo(tmp_path)
    flow_path = tmp_path / "skaileup" / "flows" / "appbuilder-mvp" / "appbuilder-mvp.flow.yaml"
    data = yaml.safe_load(flow_path.read_text())
    data["nodes"][0]["parentNode"] = "g-does-not-exist"
    flow_path.write_text(yaml.safe_dump(data, sort_keys=False))
    proc = _run(verifier)
    assert proc.returncode == 2
    assert "parentNode" in proc.stderr
    assert "g-does-not-exist" in proc.stderr
```

Run `python3 -m pytest skaileup/flows/_meta/test_verify.py -v -k "phase or dangling"` → both FAIL (first: skill-node `additionalProperties: false` rejects `phase`; second: verifier exits 0).

- [ ] **Step 2: Patch the schema.** In `flow.schema.json`:

(a) In `$defs.skill-node.properties.data.properties`, after the `"parameters"` line, add:

```json
"phase": {
  "type": "string",
  "enum": ["conceptualization", "implementation", "review"],
  "description": "Top-level phase tag for nodes not inside a group (e.g. skaileup-stepwise, whose phases are non-contiguous). Group membership via parentNode takes precedence."
}
```

(b) In `$defs.group-node.properties.data`, replace:

```json
"properties": { "label": { "type": "string" }, "phase": { "type": "string" } }
```

with:

```json
"properties": {
  "label": { "type": "string" },
  "phase": {
    "type": "string",
    "enum": ["conceptualization", "implementation", "review"]
  }
}
```

(c) In `$defs.sub-flow-node.properties.data.properties`, after the `"parameters"` line, add:

```json
"phase": {
  "type": "string",
  "enum": ["conceptualization", "implementation", "review"],
  "description": "Top-level phase this delegated block belongs to."
}
```

Mind the comma placement — each addition follows an existing property.

- [ ] **Step 3: Add the verifier check.** In `verify_flows.py`, add above `main()`:

```python
def check_parent_nodes(fid: str, data: dict, errors: list[str]) -> None:
    """Every parentNode must reference an existing group node in the same flow."""
    group_ids = {n["id"] for n in data.get("nodes", []) if n.get("type") == "group"}
    for n in data.get("nodes", []):
        parent = n.get("parentNode")
        if parent is not None and parent not in group_ids:
            errors.append(
                f"{fid}: node {n['id']!r} has parentNode {parent!r} "
                f"which is not a group node in this flow"
            )
```

and in `main()`, after the section-4/5/6 loop and before `# Print summary`, add:

```python
    # ------------------------------------------------------------------
    # 7. Structural node checks (groups, routers)
    # ------------------------------------------------------------------
    for fid, data in flow_data_by_id.items():
        check_parent_nodes(fid, data, errors)
```

- [ ] **Step 4: Green + commit.**

```bash
python3 -m pytest skaileup/flows/_meta/test_verify.py -q && python3 skaileup/flows/_meta/verify_flows.py
git add skaileup/contracts/flow.schema.json skaileup/flows/_meta
git commit -m "feat(flows): node-level phase in schema + parentNode verifier check

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: all pytest pass; `OK: 17 flows consistent`.

---

### Task 12: Group nodes — appbuilder-standard (full worked example)

**Files:**
- Modify: `skaileup/flows/appbuilder-standard/appbuilder-standard.flow.yaml` (`nodes:` only; `edges:`/`requires:` untouched)
- Test: verifier (schema + parentNode check)

**Interfaces:**
- Consumes: group-node `$def`, `phase` enum from Task 11
- Produces: three group nodes `g-conceptualization` / `g-implementation` / `g-review`; every node carries `parentNode`; every sub-flow node carries `data.phase`

Rule used here and in Tasks 13–14: **architecture belongs to `conceptualization`** (it writes `_concept/blueprint/`); implementation starts at build-setup; quality/ops close-out is `review`.

- [ ] **Step 1: Replace the whole `nodes:` section** of `appbuilder-standard.flow.yaml` with (this is the complete post-Task-10 node set plus groups, parentNode, and sub-flow `phase`; positions unchanged — group geometry is cosmetic):

```yaml
nodes:
  # --- Phase containers (visual; must precede their children) ---
  - id: g-conceptualization
    type: group
    position:
      x: -40
      y: 0
    style:
      width: 3480
      height: 480
    data:
      label: 'Conceptualization'
      phase: conceptualization
  - id: g-implementation
    type: group
    position:
      x: 3960
      y: 0
    style:
      width: 1480
      height: 480
    data:
      label: 'Implementation'
      phase: implementation
  - id: g-review
    type: group
    position:
      x: 7360
      y: 0
    style:
      width: 280
      height: 480
    data:
      label: 'Review'
      phase: review
  # --- Scope ---
  - id: scope
    type: skill
    position:
      x: 0
      y: 200
    parentNode: g-conceptualization
    data:
      skill: skaileup-scope-scope-project
      label: 'Scope Project'
      optional: false
      parameters: {}
  # --- Discovery (delegated to the shared concept-discovery flow) ---
  - id: discovery
    type: sub-flow
    position:
      x: 200
      y: 200
    parentNode: g-conceptualization
    data:
      flow: concept-discovery
      domain: discovery
      label: 'Concept discovery (brief, goals, comparable)'
      pass_context: true
      phase: conceptualization
      parameters: {}
  # --- High-level concept ---
  - id: brand-visual
    type: skill
    position:
      x: 800
      y: 200
    parentNode: g-conceptualization
    data:
      skill: design-brand-visual
      label: 'Brand Visual'
      optional: false
      parameters: {}
  - id: inspiration
    type: skill
    position:
      x: 1000
      y: 200
    parentNode: g-conceptualization
    data:
      skill: design-inspiration
      label: 'Design Inspiration'
      optional: true
      parameters: {}
  - id: journeys
    type: skill
    position:
      x: 1200
      y: 200
    parentNode: g-conceptualization
    data:
      skill: experience-journeys
      label: 'Experience Journeys'
      optional: false
      parameters: {}
  - id: behaviors-opt
    type: skill
    position:
      x: 1400
      y: 200
    parentNode: g-conceptualization
    data:
      skill: experience-behaviors
      label: 'Experience Behaviors (opt)'
      optional: true
      parameters: {}
  - id: features
    type: skill
    position:
      x: 1600
      y: 200
    parentNode: g-conceptualization
    data:
      skill: product-spec-features
      label: 'Product Features'
      optional: false
      parameters: {}
  - id: screens
    type: skill
    position:
      x: 1800
      y: 200
    parentNode: g-conceptualization
    data:
      skill: experience-screens
      label: 'Experience Screens'
      optional: false
      parameters: {}
  - id: components
    type: skill
    position:
      x: 2000
      y: 200
    parentNode: g-conceptualization
    data:
      skill: experience-components
      label: 'Experience Components'
      optional: false
      parameters: {}
  - id: mock-walkthrough
    type: skill
    position:
      x: 2200
      y: 100
    parentNode: g-conceptualization
    data:
      skill: mockup-walkthrough-astro
      label: 'Astro Walkthrough Mockup (falls back to static-html)'
      optional: true
      parallel_group: mockups
      parameters: {}
  - id: mock-static-fallback
    type: skill
    position:
      x: 2200
      y: 200
    parentNode: g-conceptualization
    data:
      skill: mockup-walkthrough-static-html
      label: 'Static HTML Walkthrough (Phase 2 fallback for astro)'
      optional: false
      parallel_group: mockups
      parameters: {}
  - id: comp-storybook
    type: skill
    position:
      x: 2200
      y: 300
    parentNode: g-conceptualization
    data:
      skill: mockup-component-storybook
      label: 'Storybook Components'
      optional: false
      parallel_group: mockups
      parameters: {}
  # --- Mockup feedback (delegated to the shared mockup-feedback flow) ---
  - id: feedback
    type: sub-flow
    position:
      x: 2400
      y: 200
    parentNode: g-conceptualization
    data:
      flow: mockup-feedback
      domain: mockup
      label: 'Mockup feedback loop'
      pass_context: true
      phase: conceptualization
      parameters: {}
  # --- Architecture (delegated to the shared architecture flow) ---
  - id: architecture
    type: sub-flow
    position:
      x: 3200
      y: 200
    parentNode: g-conceptualization
    data:
      flow: architecture
      domain: blueprint
      label: 'Architecture blueprint'
      pass_context: true
      phase: conceptualization
      parameters: {}
  # --- Build setup (delegated to the shared impl-build-setup flow) ---
  - id: build-setup
    type: sub-flow
    position:
      x: 4000
      y: 200
    parentNode: g-implementation
    data:
      flow: impl-build-setup
      domain: build
      label: 'One-time build setup'
      pass_context: true
      phase: implementation
      parameters:
        infrastructure: optional
  # --- Per-feature loop (delegated to the unified slice flow) ---
  - id: slice-loop
    type: sub-flow
    position:
      x: 5200
      y: 200
    parentNode: g-implementation
    data:
      flow: skaileup-slice
      domain: slice
      label: 'Per-feature slice loop (concept then impl, full concept design)'
      pass_context: true
      phase: implementation
      parameters:
        concept_depth: full
  # --- Quality gate (delegated to the shared quality-gate flow) ---
  - id: quality
    type: sub-flow
    position:
      x: 7400
      y: 200
    parentNode: g-review
    data:
      flow: quality-gate
      domain: quality
      label: 'Quality gate + ops tail'
      pass_context: true
      phase: review
      parameters: {}
```

(Note the mockup nodes still carry `parallel_group: mockups` here — Task 16 replaces that mechanism with routers.)

- [ ] **Step 2: Green + commit.**

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -q
git add skaileup/flows/appbuilder-standard
git commit -m "feat(flows): phase group nodes in appbuilder-standard

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: `OK: 17 flows consistent`.

---

### Task 13: Group nodes — complex, simple, mvp, cli

**Files:**
- Modify: `skaileup/flows/appbuilder-complex/appbuilder-complex.flow.yaml`
- Modify: `skaileup/flows/appbuilder-simple/appbuilder-simple.flow.yaml`
- Modify: `skaileup/flows/appbuilder-mvp/appbuilder-mvp.flow.yaml`
- Modify: `skaileup/flows/appbuilder-cli/appbuilder-cli.flow.yaml`
- Test: verifier parentNode check

**Interfaces:** same as Task 12 (group `$def`, phase enum).

For each flow: insert the group-node YAML block at the **top** of `nodes:`, add `parentNode: <group>` to every listed node (same placement as Task 12: directly after the `position:` block), and add `phase:` inside `data:` of every sub-flow node (value = its group's phase). Run the verifier after each file.

- [ ] **Step 1: appbuilder-complex.** Insert at top of `nodes:`:

```yaml
  # --- Phase containers (visual; must precede their children) ---
  - id: g-conceptualization
    type: group
    position:
      x: -40
      y: 0
    style:
      width: 4480
      height: 480
    data:
      label: 'Conceptualization'
      phase: conceptualization
  - id: g-implementation
    type: group
    position:
      x: 4960
      y: 0
    style:
      width: 1480
      height: 480
    data:
      label: 'Implementation'
      phase: implementation
  - id: g-review
    type: group
    position:
      x: 8760
      y: 0
    style:
      width: 680
      height: 480
    data:
      label: 'Review'
      phase: review
```

Membership (add `parentNode:` to each; sub-flow nodes also get `data.phase`):

| Group | Node ids |
|---|---|
| `g-conceptualization` | `scope`, `discovery`, `brand-visual`, `brand-voice`, `inspiration`, `journeys`, `behaviors`, `features`, `screens`, `components`, `mock-walkthrough-astro`, `mock-framework`, `mock-static-fallback`, `comp-storybook`, `feedback`, `ops-project-overview`, `ops-project-subsystem-map`, `ops-project-integration`, `ops-project-review`, `architecture` |
| `g-implementation` | `build-setup`, `slice-loop` |
| `g-review` | `q-eval-code`, `q-audit`, `quality` |

Sub-flow `data.phase`: `discovery`, `feedback`, `architecture` → `conceptualization`; `build-setup`, `slice-loop` → `implementation`; `quality` → `review`.

- [ ] **Step 2: appbuilder-simple.** Insert at top of `nodes:`:

```yaml
  # --- Phase containers (visual; must precede their children) ---
  - id: g-conceptualization
    type: group
    position:
      x: -40
      y: 0
    style:
      width: 1680
      height: 480
    data:
      label: 'Conceptualization'
      phase: conceptualization
  - id: g-implementation
    type: group
    position:
      x: 1960
      y: 0
    style:
      width: 1280
      height: 480
    data:
      label: 'Implementation'
      phase: implementation
  - id: g-review
    type: group
    position:
      x: 4160
      y: 0
    style:
      width: 480
      height: 480
    data:
      label: 'Review'
      phase: review
```

| Group | Node ids |
|---|---|
| `g-conceptualization` | `scope`, `brief`, `brand-visual`, `journeys`, `features`, `screens`, `mock-static`, `comp-isolated`, `architecture` |
| `g-implementation` | `build-setup`, `impl-slice-loop` |
| `g-review` | `q-test-unit`, `q-test-e2e` |

Sub-flow `data.phase`: `architecture` → `conceptualization`; `build-setup`, `impl-slice-loop` → `implementation`.

- [ ] **Step 3: appbuilder-mvp.** Insert at top of `nodes:`:

```yaml
  # --- Phase containers (visual; must precede their children) ---
  - id: g-conceptualization
    type: group
    position:
      x: -40
      y: 0
    style:
      width: 1280
      height: 480
    data:
      label: 'Conceptualization'
      phase: conceptualization
  - id: g-implementation
    type: group
    position:
      x: 1160
      y: 0
    style:
      width: 880
      height: 480
    data:
      label: 'Implementation'
      phase: implementation
  - id: g-review
    type: group
    position:
      x: 1960
      y: 0
    style:
      width: 280
      height: 480
    data:
      label: 'Review'
      phase: review
```

| Group | Node ids |
|---|---|
| `g-conceptualization` | `scope`, `brief`, `features`, `mock-text`, `techstack`, `templates` |
| `g-implementation` | `scaffold`, `plan-vertical`, `implement`, `commit` |
| `g-review` | `test-unit` |

(No sub-flow nodes in mvp — it stays fully inline.)

- [ ] **Step 4: appbuilder-cli.** Insert at top of `nodes:`:

```yaml
  # --- Phase containers (visual; must precede their children) ---
  - id: g-conceptualization
    type: group
    position:
      x: -40
      y: 0
    style:
      width: 880
      height: 480
    data:
      label: 'Conceptualization'
      phase: conceptualization
  - id: g-implementation
    type: group
    position:
      x: 1160
      y: 0
    style:
      width: 1080
      height: 480
    data:
      label: 'Implementation'
      phase: implementation
  - id: g-review
    type: group
    position:
      x: 3160
      y: 0
    style:
      width: 280
      height: 480
    data:
      label: 'Review'
      phase: review
```

| Group | Node ids |
|---|---|
| `g-conceptualization` | `scope`, `brief`, `features`, `architecture` |
| `g-implementation` | `build-setup`, `impl-slice-loop` |
| `g-review` | `q-test-unit`, `q-test-integration` |

Sub-flow `data.phase`: `architecture` → `conceptualization`; `build-setup`, `impl-slice-loop` → `implementation`.

- [ ] **Step 5: Green + commit.**

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -q
git add skaileup/flows
git commit -m "feat(flows): phase group nodes in complex/simple/mvp/cli

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: `OK: 17 flows consistent`.

---

### Task 14: Group nodes — implementation, concept-only, concept-reverse; node phases in stepwise

**Files:**
- Modify: `skaileup/flows/skaileup-implementation/skaileup-implementation.flow.yaml`
- Modify: `skaileup/flows/skaileup-concept-only/skaileup-concept-only.flow.yaml`
- Modify: `skaileup/flows/skaileup-concept-reverse/skaileup-concept-reverse.flow.yaml`
- Modify: `skaileup/flows/skaileup-stepwise/skaileup-stepwise.flow.yaml`
- Test: verifier parentNode check + schema phase enum

**Interfaces:** same as Task 12; plus skill-node `data.phase` for stepwise.

- [ ] **Step 1: skaileup-implementation.** Insert at top of `nodes:`:

```yaml
  # --- Phase containers (visual; must precede their children) ---
  - id: g-conceptualization
    type: group
    position:
      x: -40
      y: 0
    style:
      width: 480
      height: 480
    data:
      label: 'Conceptualization'
      phase: conceptualization
  - id: g-implementation
    type: group
    position:
      x: 560
      y: 0
    style:
      width: 1380
      height: 480
    data:
      label: 'Implementation'
      phase: implementation
  - id: g-review
    type: group
    position:
      x: 1960
      y: 0
    style:
      width: 280
      height: 480
    data:
      label: 'Review'
      phase: review
```

| Group | Node ids |
|---|---|
| `g-conceptualization` | `architecture` |
| `g-implementation` | `build-setup`, `impl-slice-loop` |
| `g-review` | `quality` |

Sub-flow `data.phase`: `architecture` → `conceptualization`; `build-setup`, `impl-slice-loop` → `implementation`; `quality` → `review`.

- [ ] **Step 2: skaileup-concept-only.** Insert at top of `nodes:`:

```yaml
  # --- Phase containers (visual; must precede their children) ---
  - id: g-conceptualization
    type: group
    position:
      x: -40
      y: 0
    style:
      width: 2780
      height: 480
    data:
      label: 'Conceptualization'
      phase: conceptualization
  - id: g-review
    type: group
    position:
      x: 2760
      y: 0
    style:
      width: 280
      height: 480
    data:
      label: 'Review'
      phase: review
```

| Group | Node ids |
|---|---|
| `g-conceptualization` | `scope`, `onboard`, `seeds`, `research`, `discovery`, `brand-visual`, `brand-voice`, `inspiration`, `journeys`, `features`, `behaviors`, `screens`, `screens-technical`, `components`, `architecture`, `mock` |
| `g-review` | `review` |

Sub-flow `data.phase`: `discovery`, `architecture` → `conceptualization`. (No implementation group — this flow builds nothing.)

- [ ] **Step 3: skaileup-concept-reverse.** Insert at top of `nodes:`:

```yaml
  # --- Phase container (visual; must precede its children) ---
  - id: g-conceptualization
    type: group
    position:
      x: -40
      y: 0
    style:
      width: 1280
      height: 480
    data:
      label: 'Conceptualization'
      phase: conceptualization
```

All nine nodes (`reverse-engineer`, `overview`, `subsystem-map`, `standards-discover`, `standards-inject`, `journeys`, `system`, `datamodel`, `screens`) get `parentNode: g-conceptualization`. (Extraction and enrichment both produce concept truth; single phase.)

- [ ] **Step 4: skaileup-stepwise (node-level phases, no groups).** Phases are non-contiguous here — the slice loop weaves concept discovery into building — so tag each node's `data:` with a `phase:` line (skill nodes and the sub-flow node; no group nodes):

| Node id | `data.phase` |
|---|---|
| `scope` | `conceptualization` |
| `brief` | `conceptualization` |
| `techstack` | `conceptualization` |
| `datamodel` | `conceptualization` |
| `scaffold` | `implementation` |
| `foundation` | `implementation` |
| `migrate` | `implementation` |
| `slice-loop` | `implementation` |
| `q-ready` | `review` |

Example (the `scope` node after the edit — apply the same one-line addition to each):

```yaml
  - id: scope
    type: skill
    position:
      x: 0
      y: 200
    data:
      skill: skaileup-scope-scope-project
      label: 'Scope Project'
      optional: false
      phase: conceptualization
      parameters:
        note: 'Asks open questions about shape/size; writes _concept/_meta/scope.yaml'
```

- [ ] **Step 5: Green + commit.**

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -q
git add skaileup/flows
git commit -m "feat(flows): phase groups in impl/concept flows; node phases in stepwise

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: `OK: 17 flows consistent`.

---

### Task 15: Verifier router-target check (TDD)

**Files:**
- Modify: `skaileup/flows/_meta/verify_flows.py` (extend section 7 from Task 11)
- Test: `skaileup/flows/_meta/test_verify.py`

**Interfaces:**
- Consumes: `router-node` `$def` (`data.routes[].target`: node id or `null`)
- Produces: verifier error `router X route targets unknown node Y`

- [ ] **Step 1: Failing test.** Append to `test_verify.py`:

```python
# ---------------------------------------------------------------------------
# Case 13: router route target must be an existing node id (or null) → exit 2
# ---------------------------------------------------------------------------
def test_router_bad_target_fails(tmp_path):
    verifier = _build_scratch_repo(tmp_path)
    flow_path = tmp_path / "skaileup" / "flows" / "appbuilder-mvp" / "appbuilder-mvp.flow.yaml"
    data = yaml.safe_load(flow_path.read_text())
    data["nodes"].append({
        "id": "route-bad",
        "type": "router",
        "position": {"x": 0, "y": 0},
        "data": {
            "label": "Bad Router",
            "routes": [
                {"condition": "stack.astro_available", "target": "no-such-node"},
                {"condition": "default", "target": None},
            ],
        },
    })
    flow_path.write_text(yaml.safe_dump(data, sort_keys=False))
    proc = _run(verifier)
    assert proc.returncode == 2
    assert "route targets unknown node" in proc.stderr
    assert "no-such-node" in proc.stderr
```

Run `python3 -m pytest skaileup/flows/_meta/test_verify.py -v -k router_bad` → FAILS (verifier exits 0: the schema accepts the router, nothing checks targets).

- [ ] **Step 2: Add the check.** In `verify_flows.py`, add below `check_parent_nodes`:

```python
def check_routers(fid: str, data: dict, errors: list[str]) -> None:
    """Every router route target must be null (skip) or an existing node id."""
    node_ids = {n["id"] for n in data.get("nodes", [])}
    for n in data.get("nodes", []):
        if n.get("type") != "router":
            continue
        for route in n.get("data", {}).get("routes", []):
            target = route.get("target")
            if target is not None and target not in node_ids:
                errors.append(
                    f"{fid}: router {n['id']!r} route targets unknown node {target!r}"
                )
```

and extend the section-7 loop in `main()` to:

```python
    # ------------------------------------------------------------------
    # 7. Structural node checks (groups, routers)
    # ------------------------------------------------------------------
    for fid, data in flow_data_by_id.items():
        check_parent_nodes(fid, data, errors)
        check_routers(fid, data, errors)
```

- [ ] **Step 3: Green + commit.**

```bash
python3 -m pytest skaileup/flows/_meta/test_verify.py -q && python3 skaileup/flows/_meta/verify_flows.py
git add skaileup/flows/_meta
git commit -m "feat(flows): verifier check that router targets resolve to node ids

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: all pytest pass; `OK: 17 flows consistent`.

---

### Task 16: Router nodes in appbuilder-standard

**Files:**
- Modify: `skaileup/flows/appbuilder-standard/appbuilder-standard.flow.yaml`
- Test: verifier router check (Task 15) + happy path

**Interfaces:**
- Consumes: `router-node` `$def`; existing skill nodes `mock-walkthrough`, `mock-static-fallback`, `comp-storybook`
- Produces: routers `route-walkthrough` + `route-component`; `parallel_group: mockups` removed; router targets are existing nodes so `requires:` is **unchanged**

Today astro is `optional: true` and static-html is `optional: false` in a shared `parallel_group` — the graph runs BOTH renderers and "falls back" only by label text. The router picks exactly one: first matching condition wins, `default` is the catch-all, `target: null` skips. (`mockup-walkthrough-text` is not in this flow's node/skill set, so it is not a route target — static-html is the terminal fallback here.)

- [ ] **Step 1: Add the router nodes.** Insert into `nodes:` directly after the `components` node:

```yaml
  # --- Mockup renderer routers (first match wins; routes are authoritative) ---
  - id: route-walkthrough
    type: router
    position:
      x: 2100
      y: 100
    parentNode: g-conceptualization
    data:
      label: 'Walkthrough Renderer Router (astro -> static-html)'
      routes:
        - condition: 'stack.astro_available'
          target: mock-walkthrough
        - condition: 'default'
          target: mock-static-fallback
  - id: route-component
    type: router
    position:
      x: 2100
      y: 300
    parentNode: g-conceptualization
    data:
      label: 'Component Renderer Router (storybook or skip)'
      routes:
        - condition: 'stack.storybook_available'
          target: comp-storybook
        - condition: 'default'
          target: null
```

- [ ] **Step 2: Rework the three mockup nodes.** In `mock-walkthrough`, `mock-static-fallback`, and `comp-storybook`: delete the `parallel_group: mockups` line, set `optional: true` on all three (the router now decides which one runs), and update labels:
  - `mock-walkthrough` label → `'Astro Walkthrough Mockup (via router)'`
  - `mock-static-fallback` label → `'Static HTML Walkthrough (router default)'`
  - `comp-storybook` label → `'Storybook Components (via router)'`

- [ ] **Step 3: Rewire edges.** Delete edge ids `e-components-mock-walkthrough`, `e-components-mock-static-fallback`, `e-components-comp-storybook`; insert:

```yaml
  - id: e-components-route-walkthrough
    source: components
    target: route-walkthrough
    type: parallel
  - id: e-components-route-component
    source: components
    target: route-component
    type: parallel
  - id: e-route-walkthrough-mock-walkthrough
    source: route-walkthrough
    target: mock-walkthrough
    type: optional
  - id: e-route-walkthrough-mock-static-fallback
    source: route-walkthrough
    target: mock-static-fallback
    type: optional
  - id: e-route-component-comp-storybook
    source: route-component
    target: comp-storybook
    type: optional
```

(The `e-mock-walkthrough-feedback`, `e-mock-static-fallback-feedback`, `e-comp-storybook-feedback` edges from Task 6 stay as they are.)

- [ ] **Step 4: Green + commit.**

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -q
git add skaileup/flows/appbuilder-standard
git commit -m "feat(flows): router-based mockup renderer selection in appbuilder-standard

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: `OK: 17 flows consistent` (requires unchanged — routers reference existing skill nodes only).

---

### Task 17: Router nodes in appbuilder-complex

**Files:**
- Modify: `skaileup/flows/appbuilder-complex/appbuilder-complex.flow.yaml`
- Test: verifier router check + happy path

**Interfaces:**
- Consumes: existing skill nodes `mock-walkthrough-astro`, `mock-framework`, `mock-static-fallback`, `comp-storybook`
- Produces: routers `route-walkthrough` (astro → framework → static, complex is the only tier with the framework renderer) + `route-component`; `requires:` unchanged

- [ ] **Step 1: Add the router nodes.** Insert into `nodes:` directly after the `components` node:

```yaml
  # --- Mockup renderer routers (first match wins; routes are authoritative) ---
  - id: route-walkthrough
    type: router
    position:
      x: 2300
      y: 100
    parentNode: g-conceptualization
    data:
      label: 'Walkthrough Renderer Router (astro -> framework -> static-html)'
      routes:
        - condition: 'stack.astro_available'
          target: mock-walkthrough-astro
        - condition: 'stack.framework_available'
          target: mock-framework
        - condition: 'default'
          target: mock-static-fallback
  - id: route-component
    type: router
    position:
      x: 2300
      y: 400
    parentNode: g-conceptualization
    data:
      label: 'Component Renderer Router (storybook or skip)'
      routes:
        - condition: 'stack.storybook_available'
          target: comp-storybook
        - condition: 'default'
          target: null
```

- [ ] **Step 2: Rework the four mockup nodes.** In `mock-walkthrough-astro`, `mock-framework`, `mock-static-fallback`, `comp-storybook`: delete the `parallel_group: mockups` line, set `optional: true` on all four, and update labels:
  - `mock-walkthrough-astro` label → `'Astro Walkthrough Mockup (via router)'`
  - `mock-framework` label → `'Framework Walkthrough Mockup (via router)'`
  - `mock-static-fallback` label → `'Static HTML Walkthrough (router default)'`
  - `comp-storybook` label → `'Storybook Components (via router)'`

- [ ] **Step 3: Rewire edges.** Delete edge ids `e-components-mock-walkthrough-astro`, `e-components-mock-framework`, `e-components-mock-static-fallback`, `e-components-comp-storybook`; insert:

```yaml
  - id: e-components-route-walkthrough
    source: components
    target: route-walkthrough
    type: parallel
  - id: e-components-route-component
    source: components
    target: route-component
    type: parallel
  - id: e-route-walkthrough-mock-walkthrough-astro
    source: route-walkthrough
    target: mock-walkthrough-astro
    type: optional
  - id: e-route-walkthrough-mock-framework
    source: route-walkthrough
    target: mock-framework
    type: optional
  - id: e-route-walkthrough-mock-static-fallback
    source: route-walkthrough
    target: mock-static-fallback
    type: optional
  - id: e-route-component-comp-storybook
    source: route-component
    target: comp-storybook
    type: optional
```

(The four `*-feedback` edges from Task 6 stay as they are.)

- [ ] **Step 4: Green + commit.**

```bash
python3 skaileup/flows/_meta/verify_flows.py && python3 -m pytest skaileup/flows/_meta/test_verify.py -q
git add skaileup/flows/appbuilder-complex
git commit -m "feat(flows): router-based mockup renderer selection in appbuilder-complex

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

Expected: `OK: 17 flows consistent`.

---

### Task 18: Flow docs

**Files:**
- Modify: `skaileup/flows/index.md`
- Modify: `skaileup/flows/appbuilder-standard/appbuilder-standard.md`
- Modify: `skaileup/flows/appbuilder-complex/appbuilder-complex.md`
- Modify: `skaileup/flows/appbuilder-simple/appbuilder-simple.md`
- Modify: `skaileup/flows/appbuilder-cli/appbuilder-cli.md`
- Modify: `skaileup/flows/skaileup-implementation/skaileup-implementation.md`
- Modify: `skaileup/flows/skaileup-concept-only/skaileup-concept-only.md`
- Test: none (prose); Starlight renders `docs/` pages from these via autogenerate

(appbuilder-mvp, skaileup-stepwise, skaileup-concept-reverse and the three slice docs need no structural update — their pipelines are unchanged.)

- [ ] **Step 1: index.md — add a shared-blocks section.** After the `## Slice-loop building blocks` section (its table ends with the `skaileup-slice-impl` row), insert:

```markdown
## Shared building blocks

Repeated tier segments extracted into standalone sub-flows (2026-07). Parents
delegate via a **sub-flow node**; variance is threaded through the node's
`parameters:` (the `concept_depth` pattern). All standalone-runnable.

| Flow | Block | Knobs |
|---|---|---|
| [`concept-discovery`](./concept-discovery/) | brief → goals? → comparable? | `goals: optional \| required` |
| [`architecture`](./architecture/) | techstack → templates? → system? → datamodel | `templates`, `system: include \| skip` |
| [`mockup-feedback`](./mockup-feedback/) | annotate? → triage? → patch? → apply? | — |
| [`impl-build-setup`](./impl-build-setup/) | scaffold → foundation → infra? → migrate → seed → docs | `infrastructure: skip \| optional \| required`, `data_setup` |
| [`quality-gate`](./quality-gate/) | unit → integration → e2e → ready → ops-review? → ops-sync? | `e2e: required \| optional`, `ops_tail: include \| skip` |
```

- [ ] **Step 2: index.md — mention phases and routers.** After the intro paragraph (ending `then run it:` + code block), insert:

```markdown
Every flow tags its nodes with a top-level **phase** — `conceptualization`,
`implementation`, `review` — via `group` container nodes (or node-level
`data.phase` where phases are non-contiguous, as in `skaileup-stepwise`).
Pick-one mockup renderers are selected by **router** nodes (first matching
condition wins; `default` is the catch-all; `target: null` skips).
```

- [ ] **Step 3: appbuilder-standard.md.** Replace the pipeline description/diagram in the doc body with:

```markdown
## Pipeline

```
Conceptualization: scope → [concept-discovery] → brand-visual → inspiration? →
                   journeys → behaviors? → features → screens → components →
                   (router: astro | static-html) ∥ (router: storybook | skip) →
                   [mockup-feedback] → [architecture]
Implementation:    [impl-build-setup] → [skaileup-slice] ↻ per feature
Review:            [quality-gate]
```

`[...]` = delegated to a shared sub-flow; each carries its own install
manifest, so this flow's `requires:` lists the sub-flows as `flow:` refs
instead of re-listing their skills.
```

and update any prose that names the old inline nodes (brief/goals/comparable, techstack…datamodel, scaffold…docs, quality/ops chain) to say they are delegated to `concept-discovery`, `architecture`, `impl-build-setup`, `mockup-feedback`, and `quality-gate`.

- [ ] **Step 4: appbuilder-complex.md.** Same treatment; pipeline block:

```markdown
## Pipeline

```
Conceptualization: scope → [concept-discovery] → brand-visual → brand-voice →
                   inspiration? → journeys → behaviors → features → screens →
                   components → (router: astro | framework | static-html) ∥
                   (router: storybook | skip) → [mockup-feedback] →
                   project-ops (overview → subsystem-map → integration → review) →
                   [architecture]
Implementation:    [impl-build-setup infrastructure=required] → [skaileup-slice] ↻
Review:            eval-code → audit (every slice) → [quality-gate]
```
```

- [ ] **Step 5: appbuilder-simple.md, appbuilder-cli.md, skaileup-implementation.md, skaileup-concept-only.md.** Update each doc's pipeline block the same way:

appbuilder-simple.md:

```markdown
## Pipeline

```
Conceptualization: scope → brief → brand-visual → journeys → features → screens →
                   static-html ∥ isolated-html → [architecture system=skip]
Implementation:    [impl-build-setup infrastructure=skip] → [skaileup-slice-impl] ↻
Review:            unit → e2e (inline — simple runs a quality subset, not the gate)
```
```

appbuilder-cli.md:

```markdown
## Pipeline

```
Conceptualization: scope → brief → features(commands) → [architecture system=skip]
Implementation:    [impl-build-setup infrastructure=skip data_setup=optional] →
                   [skaileup-slice-impl] ↻
Review:            unit → integration (inline — cli runs a quality subset, not the gate)
```
```

skaileup-implementation.md:

```markdown
## Pipeline

```
Conceptualization: [architecture templates=skip]  (read-or-generate blueprint)
Implementation:    [impl-build-setup] → [skaileup-slice-impl] ↻ per feature
Review:            [quality-gate e2e=optional ops_tail=skip]
```

This flow is now pure composition: every node is a sub-flow node and its
`requires:` is `shared-contracts` plus four `flow:` refs.
```

skaileup-concept-only.md:

```markdown
## Pipeline

```
Conceptualization: scope → onboard → seeds? ∥ research? → [concept-discovery goals=required] →
                   brand-visual → brand-voice? → inspiration? → journeys → features →
                   behaviors? → screens → screens-technical? → components? →
                   [architecture templates=skip] → text-walkthrough?
Review:            concept review
```
```

- [ ] **Step 6: Commit.**

```bash
git add skaileup/flows
git commit -m "docs(flows): document shared sub-flows, phases, and routers

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 19: CLAUDE.md update + final verification

**Files:**
- Modify: `CLAUDE.md` (§ Flows)
- Test: full verifier + full pytest

**Interfaces:**
- Consumes: everything above
- Produces: repo-level docs reflecting 17 flows; final green run

- [ ] **Step 1: Update the flow listing in CLAUDE.md § Flows.** Replace:

```
... (appbuilder-standard, appbuilder-complex, skaileup-slice{,-concept,-impl},
    skaileup-implementation, skaileup-stepwise, skaileup-concept-only, skaileup-concept-reverse)
```

with:

```
... (appbuilder-standard, appbuilder-complex, skaileup-slice{,-concept,-impl},
    skaileup-implementation, skaileup-stepwise, skaileup-concept-only, skaileup-concept-reverse,
    plus the shared blocks concept-discovery, architecture, mockup-feedback,
    impl-build-setup, quality-gate)
```

- [ ] **Step 2: Add a shared-blocks paragraph.** In CLAUDE.md § Flows, after the paragraph ending `…which dragged in "tier-shape extra" skills a flow never ran.)`, insert:

```markdown
**Shared building blocks (2026-07 restructure).** Five repeated tier segments
are extracted into shared sub-flows — `concept-discovery`, `architecture`,
`mockup-feedback`, `impl-build-setup`, `quality-gate` — consumed via sub-flow
nodes exactly like `skaileup-slice`; consumer variance is threaded through the
sub-flow node's `parameters:` (the `concept_depth` pattern). Flows also tag
every node with a top-level phase (`conceptualization` / `implementation` /
`review`) via `group` container nodes (node-level `data.phase` where phases
are non-contiguous, e.g. `skaileup-stepwise`), and pick-one mockup renderers
are dispatched by `router` nodes (ordered first-match routes, `default`
catch-all, `target: null` = skip) instead of parallel-optional fallback pairs.
The verifier additionally checks that every `parentNode` resolves to a group
node and every router target resolves to a node id.
```

- [ ] **Step 3: Final full verification.**

```bash
python3 skaileup/flows/_meta/verify_flows.py
python3 -m pytest skaileup/flows/_meta/test_verify.py -v
```

Expected: `OK: 17 flows consistent — each requires: manifest exactly covers its nodes (0 warning(s))`, exit 0; pytest: all cases pass, including the 5 `test_shared_subflow_registered[...]` params, `test_schema_accepts_phase_fields`, `test_dangling_parent_node_fails`, `test_router_bad_target_fails`.

- [ ] **Step 4: Final review + commit.** Spot-check the invariants:

```bash
grep -c "kind: flow" skaile.yaml                      # expect 17
grep -rl "parallel_group: mockups" skaileup/flows/    # expect ONLY appbuilder-simple (mock-static ∥ comp-isolated is a true parallel pair, not a pick-one)
grep -rn "implementation-contract" skaileup/flows/*/*.flow.yaml   # expect ONLY impl-build-setup
```

Then:

```bash
git add CLAUDE.md
git commit -m "docs: record flow restructure (shared sub-flows, phases, routers)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Self-review checklist (done while writing this plan)

- **Coverage:** all 5 sub-flows from the spec (create + adopt), groups in 8 flows + node phases in stepwise, routers in the only 2 flows with pick-one alternatives, verifier registration for every new flow id, 2 new verifier checks (parentNode, router targets) TDD'd, schema patch shown as exact JSON, docs + CLAUDE.md + final verify.
- **Placeholder scan:** no "TBD"/"similar to Task N" — every inserted YAML/JSON/Python block is written out; the one intentional repetition (complex's `discovery` node = standard's) is explicitly declared identical with its position stated.
- **Id/ref consistency:** flow ids `impl-build-setup`/`architecture`/`mockup-feedback`/`quality-gate`/`concept-discovery` used identically in dir names, `id:` fields, `SHARED_FLOWS`, `SHARED_SUBFLOWS`, `skaile.yaml`, and `flow:@skaile-ai/<id>` refs; all new edges follow `e-<source>-<target>`; every parent's post-edit `skill:` set equals its remaining node skills (checked per flow in Tasks 2/4/6/8/10 notes); `implementation-contract` lives only in `impl-build-setup` afterwards.
- **Ordering:** sub-flow extraction (Tasks 1–10) precedes groups (11–14) and routers (15–17) so each parent file region is rewritten once per concern; verifier is green after every task.
