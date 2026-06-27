# Flows — How to Read and Write Them

Flows are self-contained execution templates. Each flow file defines a complete,
runnable path through the skill tree for a specific use case (MVP, prototype, concept-only, etc.).

**Pipeline.json is removed.** All skill metadata that was in pipeline.json now lives on
the skill nodes inside each flow. Global agent config lives in `contracts/agent-config.json`.

## Install vs. run

- **A flow is its own install manifest.** Each `<name>.flow.yaml` carries a
  top-level `requires:` block — the contracts its skills read plus every skill
  its nodes run, as scoped asset refs (`kind:@publisher/name`). Installing the
  flow provisions everything it needs: `skaile add flow:<name>` (or install the
  whole collection with `skaile add skill:*`) via the **skaile workspace CLI**.
  The `requires:` set is **exact** — it lists exactly the skills the flow's nodes
  run, no inheritance and no extras. (There are no separate `*.bundle.yaml`
  files; the flow *is* the manifest.)
- **Flows are run two interchangeable ways**, once installed:
  1. the **skaile workspace flow engine** (the flow connector) executes the
     `.flow.yaml` directly (`skaile run flow:<name>`);
  2. **the orchestrator** (`skaileup` / `skaileup-build`) reads the same flow file and
     guides/executes the node graph conversationally — used when there is no flow
     engine, or for a human-in-the-loop run.

  Both follow the identical node graph described below.

---

## Skill Name Convention

Skills are always referenced by their **canonical name** — a flat kebab-case string matching
the `name` field in the skill's `SKILL.md` frontmatter. Never use file paths.

```yaml
# correct
skill: "impl-architecture-datamodel"

# wrong — never use paths
skill: "concept/blueprint/datamodel"
skill: "impl-architecture/skills/30_blueprint/cf_datamodel"
```

The orchestrator resolves names to skill directories by scanning all `SKILL.md` frontmatter
files at startup and building a name→path registry.

### Canonical Skill Registry

| Name                            | Domain                | Description                                             |
| ------------------------------- | --------------------- | ------------------------------------------------------- |
| `concept-brief`             | design    | Project brief, goals, comparable products               |
| `concept-grounding-research`             | concept-grounding-research     | Parallel research mode — domain, competitors, audiences |
| `design-brand-visual`         | design    | Visual identity — colors, fonts, tokens                 |
| `design-brand-voice`     | design    | Communication tone, micro-copy guidelines               |
| `experience-journeys`             | experience   | User journey maps, stories.json, EARS criteria          |
| `product-spec-features`             | experience   | Feature specs in numbered groups                        |
| `experience-behaviors`            | experience   | Behavioral specs (.allium format)                       |
| `experience-screens`              | experience   | Screen specs with component inventories                 |
| `experience-components`           | experience   | Reusable component inventory                            |
| `mockup-walkthrough-text`                 | mockup-walkthrough    | Interactive HTML mockups                                |
| `mockup-component-storybook`            | mockup-component-storybook    | Living Storybook prototype (3-layer)                    |
| `impl-architecture-techstack`            | impl-architecture    | Tech stack selection and reasoning                      |
| `impl-architecture-system`         | impl-architecture    | System architecture, modules, data flow                 |
| `impl-architecture-datamodel`            | impl-architecture    | Data model (stack-aware schema output)                  |
| `ops-reverse-engineer`     | ops | Extract full concept from existing codebase             |
| `ops-add-feature`          | ops | Add/modify feature in live concept                      |
| `ops-review`               | ops | Concept structure audit + gardening                     |
| `ops-eval-concept`         | ops | Concept completeness gate                               |
| `ops-eval-feature`         | ops | Feature implementation gate                             |
| `ops-eval-product`         | ops | Product goal assessment                                 |
| `impl-build-scaffold`             | impl-build        | Project scaffolding                                     |
| `impl-build-foundation`           | impl-build        | Brand tokens, auth config, app shell                    |
| `impl-build-infrastructure`       | impl-build        | Custom backend modules (conditional)                    |
| `impl-build-migrate`              | impl-build        | Database migrations                                     |
| `impl-build-seed`                 | impl-build        | Load seed data scenarios                                |
| `impl-build-implement-feature`    | impl-build        | TDD feature implementation                              |
| `impl-build-docs`          | impl-build        | Sync docs after implementation                          |
| `impl-build-generate`             | impl-build        | Code generation utilities                               |
| `impl-slice-git-prepare`          | impl-build        | Git repo prep for supervised implementation             |
| `impl-plan-brainstorm`           | impl-build        | Structured problem decomposition before planning        |
| `impl-plan-plan-vertical`           | impl-build        | Decomposed implementation plan from concept artifacts   |
| `impl-build-implement-supervised` | impl-build        | Supervised subagent-driven implementation               |
| `impl-slice-git-finish`    | impl-build        | Controlled branch completion (merge/PR/keep/discard) + session prefs |
| `impl-quality-audit`                | impl-quality      | Static code + structure analysis                        |
| `impl-quality-test-e2e`                  | impl-quality      | Browser-based E2E journey testing                       |
| `impl-quality-ready`                | impl-quality      | Pre-flight readiness gate                               |
| `ops-sync`                 | impl-quality      | Cross-reference repair                                  |
| `impl-quality-test-unit`            | impl-quality      | Unit test generation and execution                      |
| `impl-quality-test-integration`     | impl-quality      | Integration test generation and execution               |
| `impl-quality-test-plan`            | impl-quality      | Test plan from features, screens, data model            |
| `impl-quality-standards-discover`   | impl-architecture    | Discover codebase conventions → \_standards/            |
| `impl-quality-standards-inject`     | impl-architecture    | Match standards to requesting skill                     |

---

## Where Flows Live

**All flows live under `skaileup/flows/<id>/<id>.flow.yaml`** — one self-contained,
end-to-end file per flow, each carrying its own `requires:` install manifest. There
are no separate per-domain concept/build flow sets (the old split `concept-*` +
`impl-build/flows/*` model was consolidated). `verify_flows.py` enforces this: any
`*.flow.yaml` outside `skaileup/flows/` is a hard error.

| Kind    | IDs                                                  |
| ------- | ---------------------------------------------------- |
| Tier    | `mvp`, `simple-app`, `standard-app`, `complex-app`   |
| Slice   | `concept-slice`, `impl-slice` (reusable per-feature loops) |
| Variant | `cli-app`, `concept-only`, `reverse-engineer`        |
| Schema  | `contracts/flow.schema.json` (JSON Schema for all flow files) |

### Flow Catalogue

**Tier flows** — chosen by `scope-project`, each end-to-end (concept → impl):

| ID             | Description                                                          |
| -------------- | -------------------------------------------------------------------- |
| `mvp`          | Single feature, trivial persistence — one linear pass                |
| `simple-app`   | Single-user, ≤5 features — linear concept + impl-slice loop          |
| `standard-app` | Multi-user, ≤20 features — high-level concept + concept/impl slice loops |
| `complex-app`  | Multi-product / enterprise — standard-app superset + project-ops + audit |

**Slice loops** — reusable per-feature loops the tier flows inline once per feature:

| ID              | Loop                                                       |
| --------------- | ---------------------------------------------------------- |
| `concept-slice` | brainstorm → align → scope-feature → design-feature        |
| `impl-slice`    | plan → implement → test → recap → refactor → commit        |

**Variant flows** — alternate shapes the scope step routes to:

| ID                 | Description                                                              |
| ------------------ | ----------------------------------------------------------------------- |
| `cli-app`          | CLI tier — no UI/brand/screens/mockups; concept + build + impl-slice + unit/integration |
| `concept-only`     | Full concept package, no implementation — for planning/handoff          |
| `reverse-engineer` | Extract a concept from an existing codebase, then optionally enrich     |

---

## Flow File Structure

```yaml
id: 'standard' # kebab-case, matches filename
version: '2.0.0'
name: 'Standard Implementation' # shown in flow picker UI
description: '...'
metadata:
  tags: [...]
  stage: stable
  icon: '...'
  category: 'full-stack'
globals: # parameters injected into ALL nodes
  research_depth: 'skip'
  approval_mode: 'checkpoint'
  auto_review: false
  subagent_mode: true
  verbosity: 'standard'
tier_presets: # named depth bundles; user selects one at flow start
  quick: { ... }
  standard: { ... }
  thorough: { ... }
artifact_handoff: # (build flows only) artifacts consumed from upstream concept flow
  from_concept:
    - features
    - screens
    - datamodel
    - techstack
    - architecture
    - onboarding-decisions
modes:
  research: { ... } # parallel modes (research, standards)
  standards: { ... }
entry: 'scaffold' # first node to execute
nodes: [...] # skill nodes + visual group containers + router/gate nodes
edges: [...] # directed execution graph
next_flows: # suggested follow-on flows shown at completion
  - id: 'audit'
    domain: 'impl-quality'
    label: 'Audit →'
    hint: 'Run static analysis.'
    artifact_handoff: # (concept flows only) artifacts passed to the next flow
      - features
      - screens
      - datamodel
```

---

## Tier Presets and `depth_from`

### `tier_presets`

Flows that cover multiple domains define named presets mapping each domain to a depth level.
The user selects a preset at flow start (or a custom per-domain override).

```yaml
tier_presets:
  quick:
    concept-grounding-research: none
    design: light
    experience: light
    mockup-walkthrough: none
    mockup-component-storybook: none
    impl-architecture: light
    ops: none
  standard:
    concept-grounding-research: medium
    design: medium
    experience: medium
    mockup-walkthrough: light
    mockup-component-storybook: none
    impl-architecture: medium
    ops: light
  thorough:
    concept-grounding-research: max
    design: max
    experience: max
    mockup-walkthrough: medium
    mockup-component-storybook: max
    impl-architecture: max
    ops: medium
```

Depth levels: `none` | `light` | `medium` | `max`

### `depth_from` on a node

When a skill node sets `depth_from`, the orchestrator reads the current tier for that domain
and passes it into the skill as the `depth` parameter. This lets a single skill produce
shallower or deeper output depending on the chosen preset.

```yaml
- id: 'overview'
  type: 'skill'
  data:
    skill: 'concept-brief'
    depth_from: 'design' # reads tier.design at runtime
```

### `skip_when`

`skip_when` accepts a tier expression string. The orchestrator evaluates it against the
resolved tier map and skips the node entirely when the expression is truthy.

```yaml
skip_when: "tier.experience in ['none', 'light']"
skip_when: "tier.ops == 'none'"
skip_when: "tier.mockup-component-storybook == 'none'"
```

The legacy object form is also accepted for boolean flags:

```yaml
skip_when:
  tier_is: none # skip when the node's own domain tier is 'none'
```

---

## Skill Node — Full Field Reference

```yaml
id: 'datamodel'
type: 'skill'
parentNode: 'g-concept' # visual group container
position:
  x: 840
  y: 200
data:
  # Identity
  skill: 'impl-architecture-datamodel' # canonical skill name (no paths)
  label: 'Data Model' # display label in editor

  # Execution control
  optional: false # orchestrator may skip if user opts out
  parallel_group: '...' # nodes with same group run concurrently
  subagent: true # run in isolated subagent context

  # Tier / depth
  depth_from: 'impl-architecture' # domain whose tier drives output depth
  skip_when: "tier.impl-architecture == 'none'" # skip expression

  # Conditional extension
  extend_when: "artifact.datamodel.status == 'seed-partial'"
  # When true, skill runs in extend mode — updating an existing artifact
  # rather than generating it from scratch.

  # Location
  writes: '3_blueprint/3_datamodel/'
  # The _concept/ subfolder this skill writes to.
  # Used by the orchestrator for gate checks and UI progress display.

  # Prerequisites
  requires:
    - '2_experience/2_features/'
    - '3_blueprint/1_techstack/stack.md'
  # File or folder paths (relative to _concept/) that must exist on disk
  # before this skill can run. Orchestrator checks these before dispatching.
  # Different from edges — edges express preferred order; requires expresses
  # hard blockers (skill will fail or produce garbage without them).

  # Research grounding
  grounding_folder: 'datamodel/'
  # Subfolder within _grounding/ for this skill's research and user_input.json.

  # User inputs
  user_inputs:
    dialog:
      - id: 'field_id'
        label: 'Human-readable label'
        type: 'text | textarea | select | multiselect | boolean | number'
        required: false
        options: []
        default: null
        hint: 'Help text shown in the UI form'
    files:
      - '3_blueprint/3_datamodel/model.json'

  # Feedback loops
  feedback:
    - updates: '2_experience/2_features/**/*.md'
      field: 'data_entities'
      description: 'Sets data_entities[] in each feature file'
  # Upstream files this skill modifies AFTER completing its own writes.
  # See contracts/feedback_loop.md for the full protocol.

  # Runtime parameters
  parameters:
    tdd: true
  # Skill-specific config. Merged over globals (node wins on conflict).
```

---

## Edge Types

| Type          | Meaning                                                                         |
| ------------- | ------------------------------------------------------------------------------- |
| `flow`        | Required sequence — target cannot start until source completes                  |
| `optional`    | Target may be skipped based on user preference or `optional: true` on node      |
| `parallel`    | Source and target can execute concurrently once their own prerequisites are met |
| `review-loop` | Creates an iterative refinement cycle — see Review-Loop Edges section           |

**Edges express preferred execution order. `requires` expresses hard blockers.**
A skill with `requires` checks those paths regardless of which edges reached it.

---

## Node Types

### Skill Nodes

Standard skill execution nodes. Type is `"skill"`. See full field reference above.

### Router Nodes

Router nodes evaluate conditions in order and dispatch to the first matching target.
A `null` target means skip entirely (no downstream node is activated).

```yaml
- id: 'route-prototype'
  type: 'router'
  parentNode: 'g-concept'
  position:
    x: 1360
    y: 200
  data:
    label: 'Prototype Router'
    routes:
      - condition: "tier.mockup-component-storybook in ['medium', 'max']"
        target: 'storybook'
      - condition: "tier.mockup-walkthrough in ['light', 'medium', 'max']"
        target: 'mock'
      - condition: 'default'
        target: null # skip entirely
```

Conditions are evaluated top to bottom. The first matching condition wins.
Use `"default"` as the catch-all last route.

### Gate Nodes

Gate nodes check artifact status before allowing downstream execution.
When the check fails, `on_fail` controls behavior: `"pause-for-human"` surfaces the
error to the user; `"skip"` silently bypasses the downstream path.

```yaml
- id: 'check-features'
  type: 'gate'
  data:
    label: 'Features Gate'
    check: "artifact.features.status in ['draft', 'approved', 'seed']"
    on_fail: 'pause-for-human'
    message: 'Features artifact required before proceeding.'
```

### Sub-flow Nodes

Sub-flow nodes delegate execution to another flow file and return when complete.
The parent flow resumes from the sub-flow node's outgoing edges.

```yaml
- id: 'run-research'
  type: 'sub-flow'
  data:
    flow: 'research-deep'
    domain: 'concept-grounding-research'
    pass_context: true
```

### Group Nodes

Group nodes are visual containers for the canvas editor. They have no execution semantics.
Type is `"group"`. Use `parentNode` on child nodes to associate them with a group.

---

## Review-Loop Edges

Review-loop edges create iterative refinement cycles. After the review node runs,
control returns to the `target` node for another pass. The loop continues until
`exit_condition` is satisfied or `max_iterations` is reached.

```yaml
- id: 'e-review-loop'
  source: 'review'
  target: 'overview'
  type: 'review-loop'
  max_iterations: 2
  exit_condition: 'review.score >= 0.8'
  on_exit_fail: 'pause-for-human'
```

`on_exit_fail` controls what happens when max_iterations is reached without satisfying
`exit_condition`:

- `"pause-for-human"` — surface result to user, require manual decision to continue
- `"continue"` — proceed downstream regardless of score

---

## Artifact Handoff

Concept flows pass named artifacts to implementation flows via `next_flows[].artifact_handoff`.
Implementation flows declare which artifacts they consume via `artifact_handoff.from_concept`.

**Concept flow side** (`next_flows` entry):

```yaml
next_flows:
  - id: 'standard'
    domain: 'impl-build'
    label: 'Implement →'
    hint: 'Scaffold, implement features with TDD, run tests, and verify.'
    artifact_handoff:
      - features
      - screens
      - datamodel
      - techstack
      - architecture
      - onboarding-decisions
```

**Implementation flow side** (top-level):

```yaml
artifact_handoff:
  from_concept:
    - features
    - screens
    - datamodel
    - techstack
    - architecture
    - onboarding-decisions
```

The orchestrator resolves artifact paths from the concept project directory and makes
them available to all nodes in the implementation flow as read-only inputs.
`onboarding-decisions` carries tech-stack and architectural decisions from the onboarding
dialog — implementation nodes reference these for scaffolding and feature dispatch.

---

## Overrides vs. Edge Ordering

Use `data.overrides.skip_checks` only when a node's prerequisite is guaranteed by the flow
but the gate would still fire because the producer is in a parallel branch with no direct
edge to the consumer. Do **not** use overrides as a shortcut to silence gates that represent
real dependencies, and do **not** add skip_checks for paths guaranteed by direct `flow` edges
— edge ordering is sufficient.

| Situation                                                      | Correct approach                                           |
| -------------------------------------------------------------- | ---------------------------------------------------------- |
| Node B depends on Node A's output and A runs first             | Add a `flow` edge A → B. No override needed.               |
| Node B depends on Node A's output; A runs in a parallel branch | Add `skip_checks` for A's output path in B's `overrides`.  |
| Node B depends on the flow entry node's output                 | Add `skip_checks` for the entry output in B's `overrides`. |
| Gate fires but the file will not exist until user uploads it   | Keep the gate; surface the error to the user. Never skip.  |

---

## Globals and Parameter Merging

At runtime, each node receives a merged parameter object:

```
effective_params = globals + node.data.parameters
```

Node parameters win on conflict. `user_inputs` dialog values are also merged in
(from `_grounding/{grounding_folder}/user_input.json` if already collected).

---

## Modes (Parallel Utilities)

`modes.research` and `modes.standards` are not nodes — they run alongside the graph:

- **research** — fires the research skill in parallel after specified trigger nodes. Results go to `_grounding/general/` and `_grounding/{grounding_folder}/`.
- **standards** — fires once after `trigger_after` node when the flow is running against an existing codebase. Results go to `_standards/`.

---

## Standalone Mode

When a skill is invoked directly (no flow, no orchestrator):

1. Skill reads its `requires` from its own SKILL.md frontmatter
2. Checks each path exists in `_concept/`
3. Runs if gates pass; otherwise names the missing prerequisite
4. On completion, suggests next skills using the orchestrator

See `contracts/agent-config.json` for standalone_mode settings.

---

## Writing a New Flow

1. Copy the closest existing flow as a starting point
2. Set `id` (kebab-case, matches filename), `name`, `description`, `meta`
3. Set `version` to `"2.0.0"` for new flows
4. Set `globals` — choose `research_depth`, `approval_mode`, `subagent_mode`
5. Add `tier_presets` — define `quick`, `standard`, `thorough` bundles for each domain the flow touches
6. Configure `modes.research` — which nodes trigger parallel research
7. Add nodes:
   - Every skill node needs at minimum: `skill`, `depth_from` (if tier-driven)
   - Add `skip_when` using tier expressions to make nodes tier-conditional
   - Add `extend_when` for nodes that may operate on existing seed artifacts
   - Add `user_inputs` only for skills that need pre-collection
   - Add `feedback` only for skills that modify upstream files
   - Add `grounding_folder` for skills that save research or user inputs
   - Use router nodes where the flow must branch on tier conditions
8. Add edges — use `parallel` for truly concurrent paths, `optional` for skippable steps
9. Use `review-loop` edges to create iterative refinement cycles
10. Set `entry` to the first node
11. Add `artifact_handoff` to `next_flows` entries (concept flows) or at the top level (build flows)

**Do not** add `overrides.skip_checks` for paths that are guaranteed by direct `flow` edges —
edge ordering is sufficient. Only add `skip_checks` for paths produced by parallel branches
with no direct edge to the consuming node.

---

## Updating an Existing Flow

When a skill changes its `writes`, `requires`, or `user_inputs`:

- Update the node `data` in **every flow** that includes that skill
- Update MIGRATION.md with what changed and why

When adding a new skill to an existing flow:

- Add the node with full metadata including `depth_from` and `skip_when` where appropriate
- Wire edges from its dependencies and to its dependents
- If it has feedback loops, add the `feedback` field

---

## Relationship to SKILL.md

Each skill's `SKILL.md` frontmatter also declares `user_inputs` — this is the
**standalone default**. Flow node `user_inputs` overrides it for that specific flow context
(e.g., a prototype flow may ask fewer questions than a full-product flow).

The `writes`, `requires`, `grounding_folder`, and `feedback` fields on a skill node
should match the skill's SKILL.md Prerequisites and Outputs sections.
If they diverge, the flow takes precedence at runtime; SKILL.md is documentation.
