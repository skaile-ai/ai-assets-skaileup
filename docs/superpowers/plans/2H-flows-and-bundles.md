# Task 2H — Flows + Bundles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This is a **mini-plan** — a sub-plan of `docs/superpowers/plans/2026-05-07-skill-graph-migration.md` (Phase 2, terminal Task 2H).

**Goal:** Author **12 files** — 6 flow YAMLs + 6 bundle YAMLs — that compose every Phase 2 skill into runnable tier pipelines (`mvp`, `simple-app`, `standard-app`, `complex-app`) by reusing two slice flows (`concept-slice`, `impl-slice`). Each tier flow `id` matches `^[a-z][a-z0-9-]*$` (no `flow:` prefix in the file's `id` field). Each bundle declares only the dependencies its flow's nodes reference (no extras), and each tier bundle inherits the previous tier via `bundle:<predecessor>` in its `requires:` list.

**Architecture:**
- Flow YAML conforms to `contracts/flow.schema.json` — top-level fields `id` (kebab, no colon), `name`, `description`, `nodes` (array of `skill` and `group` nodes), `edges` (array of `flow` / `optional` / `parallel` typed edges). Skills are referenced by **canonical name only** — never by file path. The two slice flows (`concept-slice.flow.yaml`, `impl-slice.flow.yaml`) are authored as **standalone composable flows**: each runs the full slice loop end-to-end. Tier flows compose them by chaining their first/last nodes (the JSON schema does not support a `sub-flow` node type at v1, so composition is achieved by **referencing the same skill nodes** in the tier flow's node list, not by referencing a separate flow file).
- Bundle YAML follows the installer's `<name>.bundle.yaml` format described in `CONTRIBUTING.md` § "How the Installer Works": top-level `name`, `description`, `metadata`, and `requires:` list of `kind:name` strings (`skill:<name>` or `bundle:<name>` for inheritance). Each tier bundle's `requires:` is exactly the skill nodes its flow references PLUS `bundle:<predecessor-tier>` (for inheritance). Slice bundles (`concept-slice.bundle.yaml`, `impl-slice.bundle.yaml`) are leaf bundles — they list only the per-slice skills.
- Verification is two-pronged: (a) `jsonschema` validation against `contracts/flow.schema.json` for every flow file; (b) a Python skill-resolution script that walks every flow's `nodes[].data.skill`, looks up each name in the union of `(existing SKILL.md `name:` fields)` ∪ `(planned skill names from Tasks 2.0/2A–2G)`, and refuses on any unresolved reference.

**Tech Stack:** YAML (UTF-8, LF). Python 3.12+ for validators (`PyYAML`, `jsonschema`, stdlib `pathlib`/`re`). No new runtime dependencies introduced.

---

## Pre-flight

Before any authoring step, confirm baseline state.

- [ ] **PF-1: Confirm cwd is repo root.**

  Run: `pwd`
  Expected: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`

- [ ] **PF-2: Confirm git working tree is clean enough.**

  Run: `git status -sb`
  Expected: branch matches the Phase 2 working branch; no uncommitted changes that would conflict with new files under `flows/` and `bundles/`. If unrelated dirty files, stop and clarify with the user.

- [ ] **PF-3: Confirm all 7 prior Phase-2 mini-plans exist and are readable.**

  Run:
  ```bash
  for f in 2.0-elements-block-contract 2A-scope-project 2B-concept-slice-cluster \
           2C-impl-plan-align-vertical 2D-impl-slice-cluster 2E-impl-quality-debug \
           2F-walkthrough-mockup-static-html 2G-component-mockup-isolated-html; do
    test -r "docs/superpowers/plans/${f}.md" && echo "OK $f" || echo "MISSING $f"
  done
  ```
  Expected: 8 lines all starting `OK`. If any `MISSING`, **STOP** — Task 2H is the terminal task of Phase 2; it must not run before its predecessors' mini-plans exist.

- [ ] **PF-4: Confirm `flows/` and `bundles/` dirs exist (or create them as Step 1 of Task 1).**

  Run: `ls -la flows/ bundles/ 2>&1`
  Expected: either (a) both directories exist, or (b) "No such file or directory" for one or both. If absent, the first authoring task creates them (`mkdir -p flows bundles`). The parent plan removed old per-domain `*.bundle.yaml` files in Phase 1; per-tier bundles never existed.

- [ ] **PF-5: Confirm the schema documents are readable.**

  Run:
  ```bash
  test -r contracts/flows.md && \
  test -r contracts/flow.schema.json && \
  test -r CONTRIBUTING.md && \
  test -r SKILL_GRAPH.md && \
  echo OK
  ```
  Expected: `OK`.

- [ ] **PF-6: Confirm all source documents are readable in the order required.**

  The executing agent MUST read each of these once, in this order, before starting Task 1:
  1. **All 7 prior Phase 2 mini-plans** — these define the skills the flows compose:
     - `docs/superpowers/plans/2.0-elements-block-contract.md`
     - `docs/superpowers/plans/2A-scope-project.md`
     - `docs/superpowers/plans/2B-concept-slice-cluster.md`
     - `docs/superpowers/plans/2C-impl-plan-align-vertical.md`
     - `docs/superpowers/plans/2D-impl-slice-cluster.md`
     - `docs/superpowers/plans/2E-impl-quality-debug.md`
     - `docs/superpowers/plans/2F-walkthrough-mockup-static-html.md`
     - `docs/superpowers/plans/2G-component-mockup-isolated-html.md`
  2. `SKILL_GRAPH.md` — § 6 (Flows × Bundles, especially the tier-composition table on lines 437-499 — the SOURCE OF TRUTH for what each tier runs).
  3. `contracts/flows.md` — flow YAML schema and authoring guidance.
  4. `contracts/flow.schema.json` — JSON schema for validation (note: `id` pattern `^[a-z][a-z0-9-]*$`).
  5. Any existing `flows/*.flow.yaml` files for example shape (e.g. `skaileup/flows/prototype.flow.yaml`).
  6. `CONTRIBUTING.md` — § "How the Installer Works" (bundle file format), § "Naming Conventions" (path-based skill names), § "Dependencies (`requires:`)" (bundle's `requires:` shape).
  7. Parent plan stub at `docs/superpowers/plans/2026-05-07-skill-graph-migration.md` lines 1690-1708 (Task 2H constraints).

- [ ] **PF-7: Confirm path-based naming is the rule for ALL skill references in flow nodes.**

  Per `CONTRIBUTING.md` § "Naming Conventions" and verified across Tasks 2A–2G mini-plans, every skill `name:` is its **path under repo root** with `/` replaced by `-`. Therefore every `nodes[].data.skill` string in this task's flow files MUST match this pattern. The base orchestrator at `skaileup/skills/skaileup/SKILL.md` is the documented exception (`name: skaileup`, not `skaileup-skills-skaileup`) — but this task does not reference the base orchestrator; it only references the leaf skills the flows execute.

- [ ] **PF-8: Pre-flight skill-name resolution check (deferred but flagged here).**

  Task 5 of this plan runs a Python script that resolves every skill name referenced in the 6 flows against:
  - **A. Existing SKILL.md `name:` fields** — gathered via `grep -r "^name:" --include=SKILL.md`
  - **B. Planned skill names from Phase 2 mini-plans** — see § "Pinned: Skill Name Registry" below
  Any unresolved reference → script exits 2 → flow author must either (a) wait for the missing skill to be authored, or (b) fix the typo. The risk: existing migrated skills' `name:` fields may have drifted from the path-based pattern. The pre-flight check here surfaces drift before authoring; the Task 5 check enforces it after authoring.

---

## Source-of-Truth Anchors (read before authoring any flow/bundle)

The executing agent MUST internalize these before Task 1:

1. **SKILL_GRAPH.md § 6 tier-composition table (lines 437-499)** — pinned verbatim in this plan below as "Pinned: Tier-Composition Table". This is the contract.
2. **SKILL_GRAPH.md § 6 tier composition prose (lines 411-432)** — describes the *shape* of each tier flow:
   ```
   mvp.flow.yaml:
      scope-project ─► linear concept ─► impl-build/scaffold ─►
      impl-slice (1 iteration, no recap, no refactor) ─► done

   simple-app.flow.yaml:
      scope-project ─► linear concept ─► impl-build setup ─►
      loop: impl-slice ─► done (when all features built)

   standard-app.flow.yaml:
      scope-project ─► high-level concept (brief, brand, journeys) ─►
      impl-build setup ─►
      loop: concept-slice ─► impl-slice ─► done

   complex-app.flow.yaml:
      scope-project ─► high-level concept ─► project-overview ─►
      impl-build setup ─►
      loop: concept-slice ─► impl-slice (supervised plan) ─►
           impl-quality/audit (every slice) ─► done
   ```
3. **SKILL_GRAPH.md § 6 inheritance rule (lines 502-504)**: "Bundles inherit: `simple-app` includes `mvp`, `standard-app` includes `simple-app`, `complex-app` includes `standard-app`. Each bundle file lists only its *additions*."
4. **SKILL_GRAPH.md § 5.2 per-slice impl loop (lines 304-360)** — pins `impl-slice` flow nodes: `implement → test → recap → refactor → commit` (per Task 2D's resolution of the SKILL_GRAPH order).
5. **SKILL_GRAPH.md § 4 concept-slice loop (lines 222-249)** — pins `concept-slice` flow nodes: `brainstorm → align → scope-feature → design-feature`.
6. **Task 2A pinned schema for `_concept/_meta/scope.yaml`** — `flow_to_run` is set to the literal string `"flow:<tier>"` (e.g. `"flow:simple-app"`). The orchestrator parses this `kind:name` string per `CONTRIBUTING.md` § "Dependencies" (the same parser used for `requires:` entries) and resolves it to `flows/<tier>.flow.yaml`. **The flow file's own `id` field is the bare tier name** (`simple-app`), per `flow.schema.json`'s pattern `^[a-z][a-z0-9-]*$` which forbids the colon. This split is intentional and stable; do not propose changes here.

---

## Pinned: Tier-Composition Table (verbatim from SKILL_GRAPH.md § 6, lines 437-499)

This table is the contract for what each tier flow MUST include and exclude. Every cell with `✓` means "this skill node MUST appear in that tier's flow.yaml" (and therefore in its bundle's `requires:`). Every blank cell means "this skill node MUST NOT appear in that tier's flow.yaml". Cells annotated `(opt)` are optional — include the node with `optional: true` and a `skip_when` expression.

```
                            mvp  simple  standard  complex
                            ────────────────────────────────
   skaileup/scope/scope     ✓    ✓       ✓         ✓
   ───────────────────────────────────────────────────────
   concept/brief            ✓    ✓       ✓         ✓
   concept/goals                         ✓         ✓
   concept/comparable                    ✓         ✓
   design/brand-visual           ✓       ✓         ✓
   design/brand-voice                              ✓
   design/inspiration                    ✓         ✓
   product-spec/features    ✓    ✓       ✓         ✓
   experience/journeys           ✓       ✓         ✓
   experience/behaviors                  (opt)     ✓
   experience/screens            ✓       ✓         ✓
   experience/components                 ✓         ✓
   walkthrough-mockup-text      ✓
   walkthrough-mockup-static-html      ✓
   walkthrough-mockup-lit                          (alt for embedded)
   walkthrough-mockup-astro                        ✓ (default)
   walkthrough-mockup-framework                                    ✓
   component-mockup-isolated-html      ✓
   component-mockup-storybook                      ✓               ✓
   mockup-feedback-annotate                        ✓               ✓
   mockup-feedback-triage                          ✓               ✓
   mockup-feedback-patch                           ✓               ✓
   mockup-feedback-apply                           ✓               ✓
   ───────────────────────────────────────────────────────
   concept-slice/brainstorm                        ✓
   concept-slice/align                   ✓         ✓
   concept-slice/scope-feature           ✓         ✓
   concept-slice/design-feature          ✓         ✓
   ───────────────────────────────────────────────────────
   impl-arch/techstack      ✓    ✓       ✓         ✓
   impl-arch/templates      ✓    ✓       ✓         ✓
   impl-arch/system                      ✓         ✓
   impl-arch/datamodel           ✓       ✓         ✓
   impl-plan/brainstorm                  ✓         ✓
   impl-plan/align               ✓       ✓         ✓
   impl-plan/plan-vertical  ✓    ✓       ✓         ✓
   impl-plan/supervised                            ✓
   impl-build/scaffold      ✓    ✓       ✓         ✓
   impl-build/foundation         ✓       ✓         ✓
   impl-build/infra                      (opt)     ✓
   impl-build/migrate            ✓       ✓         ✓
   impl-build/seed               ✓       ✓         ✓
   impl-build/docs               ✓       ✓         ✓
   impl-slice/implement     ✓    ✓       ✓         ✓
   impl-slice/test               ✓       ✓         ✓
   impl-slice/recap              ✓       ✓         ✓
   impl-slice/refactor                   ✓         ✓
   impl-slice/commit        ✓    ✓       ✓         ✓
   ───────────────────────────────────────────────────────
   impl-quality/unit        ✓    ✓       ✓         ✓
   impl-quality/integ.                   ✓         ✓
   impl-quality/e2e              ✓       ✓         ✓
   impl-quality/eval-code                          ✓
   impl-quality/audit                              ✓
   impl-quality/ready                    ✓         ✓
   impl-quality/debug/* (on demand — invoked when stuck)
   ───────────────────────────────────────────────────────
   ops/review                            ✓         ✓
   ops/sync                              ✓         ✓
   ops/project-*                                   ✓
```

**Annotation rule for `impl-quality/debug/*`:** the table says "on demand — invoked when stuck". This means **debug skills are NOT bundled with any tier flow** and are NOT referenced as nodes in any tier flow's graph. They are user-invoked or skill-escalated (per Task 2E's "Open Question 2" — flow integration is deferred). **For this task**: do NOT include `impl-quality-debug-self-verify` or `impl-quality-debug-handoff` in any flow's nodes or any bundle's `requires:`.

---

## Pinned: Skill Name Registry (path-based per CONTRIBUTING.md § Naming Conventions)

Every flow node references a skill by canonical name. The full list of names referenced by the 6 flows in this task is:

### Existing skills (verified via `grep -r "^name:" --include=SKILL.md` at PF time)

These already have a `SKILL.md` with a matching `name:` field as of the migration's Phase 1 / earlier Phase 2 work:

| Canonical name | Source path | Status |
|---|---|---|
| `concept-brief` | `concept/brief/SKILL.md` | existing |
| `concept-grounding-onboard` | `concept/grounding/onboard/SKILL.md` | existing |
| `concept-grounding-research` | `concept/grounding/research/SKILL.md` | existing |
| `concept-grounding-seeds` | `concept/grounding/seeds/SKILL.md` | existing |
| `design-brand-visual` | `design/brand-visual/SKILL.md` | existing |
| `design-brand-voice` | `design/brand-voice/SKILL.md` | existing |
| `experience-journeys` | `experience/journeys/SKILL.md` | existing |
| `experience-behaviors` | `experience/behaviors/SKILL.md` | existing |
| `experience-screens` | `experience/screens/SKILL.md` | existing |
| `experience-components` | `experience/components/SKILL.md` | existing |
| `product-spec-features` | `product-spec/features/SKILL.md` | existing |
| `walkthrough-mockup-text` | `walkthrough-mockup/text/SKILL.md` | existing |
| `component-mockup-storybook` | `component-mockup/storybook/orchestrator/SKILL.md` | existing |
| `impl-architecture-techstack` | `impl-architecture/techstack/SKILL.md` | existing |
| `impl-architecture-system` | `impl-architecture/system/SKILL.md` | existing |
| `impl-architecture-datamodel` | `impl-architecture/datamodel/SKILL.md` | existing |
| `impl-plan-brainstorm` | `impl-plan/brainstorm/SKILL.md` | existing (refreshed by 2C) |
| `impl-plan-plan-vertical` | `impl-plan/plan-vertical/SKILL.md` | existing (refreshed by 2C) |
| `impl-plan-supervised` | `impl-plan/supervised/SKILL.md` | existing |
| `impl-build-scaffold` | `impl-build/scaffold/SKILL.md` | existing |
| `impl-build-foundation` | `impl-build/foundation/SKILL.md` | existing |
| `impl-build-infrastructure` | `impl-build/infrastructure/SKILL.md` | existing |
| `impl-build-migrate` | `impl-build/migrate/SKILL.md` | existing |
| `impl-build-seed` | `impl-build/seed/SKILL.md` | existing |
| `impl-build-docs` | `impl-build/docs/SKILL.md` | existing |
| `impl-slice-implement` | `impl-slice/implement/SKILL.md` | existing |
| `impl-quality-test-unit` | `impl-quality/test-unit/SKILL.md` | existing |
| `impl-quality-test-integration` | `impl-quality/test-integration/SKILL.md` | existing |
| `impl-quality-test-e2e` | `impl-quality/test-e2e/SKILL.md` | existing |
| `impl-quality-eval-code` | `impl-quality/eval-code/SKILL.md` | existing |
| `impl-quality-audit` | `impl-quality/audit/SKILL.md` | existing |
| `impl-quality-ready` | `impl-quality/ready/SKILL.md` | existing |
| `ops-review` | `ops/review/SKILL.md` | existing |
| `ops-sync` | `ops/sync/SKILL.md` | existing |
| `ops-project-overview` | `ops/project-overview/SKILL.md` | existing |
| `ops-project-subsystem-map` | `ops/project-subsystem-map/SKILL.md` | existing |
| `ops-project-integration` | `ops/project-integration/SKILL.md` | existing |
| `ops-project-review` | `ops/project-review/SKILL.md` | existing |

### Planned skills (this Phase 2 — referenced from mini-plans 2.0/2A–2G)

These will be authored by Tasks 2A/2B/2C/2D/2E/2F/2G **before** Task 2H runs (parent plan: "Sub-plan blocker: all the new skills referenced by these flows must exist (Tasks 2A–2G). Author last among Phase 2.").

| Canonical name | Source path (will exist post-Task) | Authoring task |
|---|---|---|
| `skaileup-scope-scope-project` | `skaileup/scope/scope-project/SKILL.md` | 2A |
| `concept-slice-brainstorm` | `concept-slice/brainstorm/SKILL.md` | 2B |
| `concept-slice-align` | `concept-slice/align/SKILL.md` | 2B |
| `concept-slice-scope-feature` | `concept-slice/scope-feature/SKILL.md` | 2B |
| `concept-slice-design-feature` | `concept-slice/design-feature/SKILL.md` | 2B |
| `impl-plan-align` | `impl-plan/align/SKILL.md` | 2C |
| `impl-slice-test` | `impl-slice/test/SKILL.md` | 2D |
| `impl-slice-recap` | `impl-slice/recap/SKILL.md` | 2D |
| `impl-slice-refactor` | `impl-slice/refactor/SKILL.md` | 2D |
| `impl-slice-commit` | `impl-slice/commit/SKILL.md` | 2D |
| `walkthrough-mockup-static-html` | `walkthrough-mockup/static-html/SKILL.md` | 2F |
| `component-mockup-isolated-html` | `component-mockup/isolated-html/SKILL.md` | 2G |

### Skills referenced by the SKILL_GRAPH § 6 table but NOT yet planned in Phase 2

These appear in the tier-composition table but no Phase 2 mini-plan authors them. They will need to either (a) be authored elsewhere (Phase 3 or a follow-on Phase 2 mini-plan) before this task can run, or (b) be marked **OUT OF SCOPE FOR PHASE 2** and excluded from the Phase 2 flows. The decision is documented in "Open Questions" § 1.

| Canonical name (per § 6 row) | Notes |
|---|---|
| `concept-goals` | row "concept/goals" — for standard/complex tiers |
| `concept-comparable` | row "concept/comparable" — for standard/complex tiers |
| `design-inspiration` | row "design/inspiration" — for standard/complex tiers |
| `walkthrough-mockup-lit` | row alt-for-embedded; complex tier (Phase 3) |
| `walkthrough-mockup-astro` | row default for standard tier (Phase 3) |
| `walkthrough-mockup-framework` | row complex tier (Phase 3) |
| `mockup-feedback-annotate` | row standard/complex (Phase 3) |
| `mockup-feedback-triage` | row standard/complex (Phase 3) |
| `mockup-feedback-patch` | row standard/complex (Phase 3) |
| `mockup-feedback-apply` | row standard/complex (Phase 3) |
| `impl-architecture-templates` | row "impl-arch/templates" — Phase 1 promoted templates to a domain dir; whether a single skill exists (`impl-architecture/templates/SKILL.md`) or only sub-template skills (e.g. `template-postxl`) is ambiguous; see "Open Questions" § 2 |

**Resolution rule (this plan):** until the user confirms otherwise, the executing agent MUST treat these "not-yet-planned" skills as **declared-but-unresolvable**. The flow files reference them (so the table is honored), but the verification script at Task 5 SHOULD print warnings (not errors) for these specific names, classifying them as "Phase 3 / out-of-scope" rather than "broken reference". See § "Pinned: Resolution Allowlist" below for the allowlist the script applies.

### Pinned: Resolution Allowlist (script-readable)

The verifier (Task 5) classifies every flow-referenced skill into one of three buckets:

```yaml
# Bucket A: existing — must have a real SKILL.md with matching name:
#   (the verifier greps SKILL.md frontmatter to confirm)
# Bucket B: planned (Phase 2) — must appear in this plan's "Planned skills" table above,
#   AND its mini-plan must exist under docs/superpowers/plans/ (verified by Task 5 step 1)
# Bucket C: deferred (Phase 3 / out-of-scope) — the plan acknowledges a gap; the
#   verifier emits a WARNING (not error) listing them; the user must approve the
#   warning list before this task can be considered "done".
deferred_phase_3:
  - concept-goals
  - concept-comparable
  - design-inspiration
  - walkthrough-mockup-lit
  - walkthrough-mockup-astro
  - walkthrough-mockup-framework
  - mockup-feedback-annotate
  - mockup-feedback-triage
  - mockup-feedback-patch
  - mockup-feedback-apply
  - impl-architecture-templates
```

The verifier reads this list from a YAML file authored alongside the verifier (`flows/_meta/deferred_skills.yaml` — see Task 5).

---

## Pinned: Flow YAML Schema (from `contracts/flow.schema.json` and `contracts/flows.md`)

Required top-level fields (per `flow.schema.json` line 7): `id`, `name`, `nodes`, `edges`. Recommended additional fields: `version`, `description`, `metadata`, `globals`, `entry`.

```yaml
id: '<kebab-case>'             # REQUIRED. Pattern: ^[a-z][a-z0-9-]*$. Matches filename without .flow.yaml.
                               # NOTE: NO COLON ALLOWED. The id is bare ('mvp', not 'flow:mvp').
                               # The kind:name form 'flow:mvp' lives in scope.yaml's flow_to_run field
                               # and in `requires:` entries — never in this `id` field.
version: '2.0.0'               # string; default '1.0' per schema; Phase 2 conventions: '2.0.0'
name: '<human-readable>'       # REQUIRED.
description: '<one-paragraph>'

metadata:                      # OPTIONAL. tags / stage / icon / category / onboarding sub-block.
  tags: [...]
  stage: alpha | beta | stable
  category: full-stack | prototype | concept | cli | maintenance | incremental
  icon: '<icon-id>'

globals:                       # OPTIONAL. parameters injected into ALL nodes.
  research_depth: skip | light | moderate | deep
  approval_mode: checkpoint | auto_approve
  subagent_mode: false | true
  verbosity: brief | standard | detailed

entry: '<node-id>'             # OPTIONAL but RECOMMENDED — first node id to execute.

nodes:                         # REQUIRED. Each item is one of: skill-node | group-node.
                               # NO router-node, gate-node, or sub-flow-node defined in the
                               # canonical schema (flow.schema.json $defs lists only
                               # skill-node and group-node). flows.md mentions router/gate/sub-flow
                               # types in prose but the JSON schema does not enforce them; for
                               # this task, restrict to skill-node and group-node only.
  - id: '<unique-string>'
    type: 'skill'              # const
    parentNode: 'g-concept'    # OPTIONAL — visual group container id
    position: { x: <number>, y: <number> }   # REQUIRED by schema
    data:
      skill: '<canonical-name>'   # REQUIRED. NEVER a path. e.g. 'concept-brief'.
      label: '<human-readable>'
      optional: false
      parallel_group: '<id>'
      subagent: false
      writes: '<_concept/sub/path/>'
      requires: ['<_concept/...>']
      grounding_folder: '<sub>'
      user_inputs: { dialog: [...], files: [...] }
      feedback: [{ updates: '...', field: '...', description: '...' }]
      parameters: { <skill-specific>: <value> }

  - id: 'g-concept'
    type: 'group'
    position: { x: 0, y: 0 }
    style: { width: 1400, height: 400, ... }
    data: { label: 'Concept', phase: 'conceptualization' }

edges:                         # REQUIRED. Each is { id, source, target, type, [label, data] }.
  - id: 'e-<source>-<target>'
    source: '<node-id>'
    target: '<node-id>'
    type: 'flow' | 'optional' | 'parallel'   # default 'flow'
    label: '<short>'
    data: { condition: '<expr>' }            # optional, used for conditional edges

next_flows:                    # OPTIONAL. Suggested follow-on flows shown at completion.
                               # NOTE: the schema's `next_flows[].domain` enum is
                               # ['skaileup-conceptualization','skaileup-implementation','skaileup-evaluate']
                               # which is a Phase-0 vocabulary. This will look outdated; flag
                               # in "Open Questions" § 3. For this task, omit `next_flows`
                               # entirely on tier flows (which are terminal) — slice flows MAY
                               # use it conservatively if needed.
```

**Key constraints derived from `flow.schema.json` and confirmed against existing flows:**
- `id` is bare kebab-case — **no colon**.
- `nodes[].data.skill` is the canonical skill name — **never** a path.
- Edge `type` enum is exactly `flow | optional | parallel` (no `review-loop` even though `flows.md` mentions it — the JSON schema constrains).
- The schema's `additionalProperties: false` on top-level means unknown top-level keys cause validation failure. **Avoid** adding fields not enumerated above.

---

## Pinned: Bundle YAML Schema (derived from `CONTRIBUTING.md` § "How the Installer Works" + § "Dependencies (`requires:`)")

**No JSON schema for bundles exists in `contracts/`** (verified: only `flow.schema.json` is present). The format is therefore inferred from CONTRIBUTING.md's installer-recognized `<name>.bundle.yaml` extension and the `requires:` syntax it documents.

```yaml
# bundles/<tier-or-slice>.bundle.yaml
name: '<tier-name>'                 # REQUIRED. Matches filename without .bundle.yaml.
                                    # Same kebab-case pattern as flow id.
description: '<one-paragraph>'      # REQUIRED.
metadata:
  version: '1.0.0'                  # REQUIRED. Semver.
  tags: [bundle, <tier>, ...]       # ≥2.
  stage: alpha | beta | stable

# The dependency manifest. Each entry is a "kind:name" string per CONTRIBUTING.md § Dependencies.
# Supported kinds: skill | bundle | flow | contract | agent | prompt.
# Bare strings default to kind 'skill' but the convention in this task is to use the
# explicit prefix everywhere for clarity (especially for inheritance).
requires:
  # Inheritance: a tier bundle includes its predecessor's bundle.
  - bundle:<predecessor-tier>       # ONLY for non-mvp tier bundles.
  # Skill dependencies: one entry per skill node referenced by the matching flow.
  - skill:<canonical-name>
  - skill:<canonical-name>
  # Optional: contract: refs that the included skills depend on.
  - contract:<contract-name>        # only if needed.
```

**Bundle inheritance rule (per SKILL_GRAPH § 6 lines 502-504):**
- `mvp.bundle.yaml`: lists every skill its flow uses — no `bundle:` ancestors.
- `simple-app.bundle.yaml`: `requires: [bundle:mvp, skill:<X>, skill:<Y>, ...]` — only its **additions** beyond mvp.
- `standard-app.bundle.yaml`: `requires: [bundle:simple-app, skill:<X>, ...]` — only additions beyond simple-app.
- `complex-app.bundle.yaml`: `requires: [bundle:standard-app, skill:<X>, ...]` — only additions beyond standard-app.

**Slice bundles** (`concept-slice.bundle.yaml`, `impl-slice.bundle.yaml`) are **leaf bundles**. They list the per-slice skills only. Tier bundles do NOT `bundle:concept-slice` or `bundle:impl-slice`; they list the underlying slice skills directly. The slice bundles are consumed when a user runs `skaile run flow:concept-slice` (per SKILL_GRAPH § 6 lines 411-412 "The two slice flows are building blocks"), but for tier bundles' inheritance chain, the slice skills are **inlined** (this avoids transitive bundle resolution surprises and matches the table — the table lists slice skills row-by-row, not as a bundle reference).

**No `additionalProperties: false` enforcement exists** (no schema). However, the executing agent MUST keep bundles minimal — only the keys above. Any drift from the listed shape requires updating CONTRIBUTING.md.

---

## Pinned: Slice Flow Node Lists (the building blocks)

These two slice flows are the composable units. Tier flows compose them by referencing the same skill-node graph as a sub-section. Per Task 2.0/2A–2G mini-plans, the canonical slice phase ordering is:

### `concept-slice.flow.yaml` — full per-feature concept loop (per Task 2B)

```
concept-slice-brainstorm  →  concept-slice-align  →  concept-slice-scope-feature  →  concept-slice-design-feature
```

**Slice flow id:** `concept-slice` (bare, per `^[a-z][a-z0-9-]*$`).

**Slice flow nodes (4):**
| node id | data.skill | edge to next | source mini-plan |
|---|---|---|---|
| `c-brainstorm` | `concept-slice-brainstorm` | `c-align` (flow) | 2B Task 1 |
| `c-align` | `concept-slice-align` | `c-scope-feature` (flow) | 2B Task 2 |
| `c-scope-feature` | `concept-slice-scope-feature` | `c-design-feature` (flow) | 2B Task 3 |
| `c-design-feature` | `concept-slice-design-feature` | (terminal) | 2B Task 4 |

**Entry:** `c-brainstorm`.

**Note on simple-app entry:** Per SKILL_GRAPH § 6 (table row "concept-slice/brainstorm" empty for simple-app, "concept-slice/align" ✓), `simple-app` does not run `brainstorm`. **In `concept-slice.flow.yaml`**, this is captured by leaving `c-brainstorm` as the canonical entry (the slice flow is a building block; ALL its phases are present), and **in the `simple-app.flow.yaml` tier flow**, the composition only references `c-align`/`c-scope-feature`/`c-design-feature` nodes (not `c-brainstorm`). See § "Pinned: Tier-flow composition rule" below.

### `impl-slice.flow.yaml` — full per-feature impl loop (per Tasks 2C + 2D)

The composite per-slice impl loop is `brainstorm → align → plan-vertical → implement → test → recap → refactor → commit`. Tasks 2C own the first three (`impl-plan/*`), Task 2D owns the last five (`impl-slice/*`).

```
impl-plan-brainstorm  →  impl-plan-align  →  impl-plan-plan-vertical  →
impl-slice-implement  →  impl-slice-test  →  impl-slice-recap  →  impl-slice-refactor  →  impl-slice-commit
```

**Slice flow id:** `impl-slice`.

**Slice flow nodes (8):**
| node id | data.skill | edge to next | source mini-plan |
|---|---|---|---|
| `i-brainstorm` | `impl-plan-brainstorm` | `i-align` (flow) | 2C Task 1 |
| `i-align` | `impl-plan-align` | `i-plan-vertical` (flow) | 2C Task 2 |
| `i-plan-vertical` | `impl-plan-plan-vertical` | `i-implement` (flow) | 2C Task 3 |
| `i-implement` | `impl-slice-implement` | `i-test` (flow) | existing (Phase 1) |
| `i-test` | `impl-slice-test` | `i-recap` (flow) | 2D Task 1 |
| `i-recap` | `impl-slice-recap` | `i-refactor` (flow) | 2D Task 2 |
| `i-refactor` | `impl-slice-refactor` | `i-commit` (flow) | 2D Task 3 |
| `i-commit` | `impl-slice-commit` | (terminal) | 2D Task 4 |

**Entry:** `i-brainstorm`.

**Tier-coverage caveat:** Per SKILL_GRAPH § 6, mvp does NOT run impl-plan-align, impl-plan-brainstorm, impl-slice-test, impl-slice-recap, impl-slice-refactor (only impl-plan-plan-vertical + impl-slice-implement + impl-slice-commit). `impl-slice.flow.yaml` is the canonical/full slice flow (used directly by simple-app and standard-app and complex-app); `mvp.flow.yaml` does NOT compose this slice flow — instead it inlines just three impl nodes. See § "Pinned: Tier-flow composition rule".

---

## Pinned: Tier-flow composition rule (per SKILL_GRAPH § 6 prose, lines 411-432)

The four tier flows compose differently. **Each tier flow is a self-contained `*.flow.yaml`** — it does NOT reference the slice flow files (the JSON schema has no `sub-flow` node type in `$defs`). Composition is achieved by **inlining the relevant slice nodes** into the tier flow's `nodes:` list.

### `mvp.flow.yaml`
```
scope-project ─► linear concept (mvp row of § 6 table) ─► impl-build/scaffold ─►
impl-slice (1 iteration, no recap, no refactor) ─► done
```

**Concept phase (mvp row of § 6):** scope-project, concept-brief, product-spec-features, walkthrough-mockup-text, impl-architecture-techstack, impl-architecture-templates (deferred), impl-build-scaffold, impl-slice-implement, impl-slice-commit, impl-quality-test-unit. **No impl-plan/brainstorm** (only `impl-plan-plan-vertical`). **No impl-slice-test/recap/refactor**. **No concept-slice phases**.

### `simple-app.flow.yaml`
```
scope-project ─► linear concept (simple row of § 6 table) ─► impl-build setup ─►
loop: impl-slice (full slice loop) ─► done
```

**Concept phase (simple row):** mvp's concept + design-brand-visual, experience-journeys, experience-screens, impl-architecture-datamodel, walkthrough-mockup-static-html, component-mockup-isolated-html, impl-build-foundation, impl-build-migrate, impl-build-seed, impl-build-docs.
**Impl-plan additions:** impl-plan-align (mvp had only plan-vertical).
**Impl-slice additions:** impl-slice-test, impl-slice-recap, impl-quality-test-e2e.
**No concept-slice phases.**

### `standard-app.flow.yaml`
```
scope-project ─► high-level concept (brief, brand, journeys, ...) ─►
impl-build setup ─►
loop: concept-slice (align→scope-feature→design-feature; NO brainstorm) ─►
      impl-slice (full) ─► done
```

**Concept phase (standard row):** simple-app's concept + concept-goals (deferred), concept-comparable (deferred), design-inspiration (deferred), experience-behaviors (opt), experience-components, component-mockup-storybook, mockup-feedback-* (deferred), walkthrough-mockup-astro (deferred — fall back to walkthrough-mockup-static-html for Phase 2 if astro skill not yet authored).
**Impl-arch additions:** impl-architecture-system.
**Impl-plan additions:** impl-plan-brainstorm.
**Impl-slice additions:** impl-slice-refactor.
**Concept-slice additions:** concept-slice-align, concept-slice-scope-feature, concept-slice-design-feature (NO brainstorm).
**Quality additions:** impl-quality-test-integration, impl-quality-ready.
**Ops additions:** ops-review, ops-sync.

### `complex-app.flow.yaml`
```
scope-project ─► high-level concept ─► project-overview ─►
impl-build setup ─►
loop: concept-slice (full — INCLUDING brainstorm) ─►
      impl-slice (supervised plan) ─►
      impl-quality/audit (every slice) ─► done
```

**Concept phase (complex row):** standard-app's concept + design-brand-voice, walkthrough-mockup-framework (deferred), impl-build-infrastructure (was opt for standard, full for complex).
**Impl-plan additions:** impl-plan-supervised.
**Impl-quality additions:** impl-quality-eval-code, impl-quality-audit.
**Concept-slice additions:** concept-slice-brainstorm.
**Ops additions:** ops-project-overview, ops-project-subsystem-map, ops-project-integration, ops-project-review.

---

## Pinned: scope-project entry rule (per Task 2A pinned schema)

Tier flows are entered by `skaileup-scope-scope-project` (Task 2A) which writes `_concept/_meta/scope.yaml` with `flow_to_run: "flow:<tier>"` (a `kind:name` string per CONTRIBUTING.md). The orchestrator parses this string and dispatches to `flows/<tier>.flow.yaml`. Therefore:
- The first node in EVERY tier flow is `scope-project` (= `skaileup-scope-scope-project`).
- The flow file's `id` is the bare tier name (`mvp`, `simple-app`, etc.).
- The `flow_to_run` value `flow:mvp` (literal string in scope.yaml) refers to this file.
- **The `concept-slice.flow.yaml` and `impl-slice.flow.yaml` slice flows are NOT entered via scope-project** — they are building blocks. A user typically does NOT run them directly in production; they exist for testability of the slice loop and for orchestration debugging.

---

## File Targets

All paths absolute, inside `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`.

**Created (12 primary files):**
- `flows/mvp.flow.yaml`
- `flows/simple-app.flow.yaml`
- `flows/standard-app.flow.yaml`
- `flows/complex-app.flow.yaml`
- `flows/concept-slice.flow.yaml`
- `flows/impl-slice.flow.yaml`
- `bundles/mvp.bundle.yaml`
- `bundles/simple-app.bundle.yaml`
- `bundles/standard-app.bundle.yaml`
- `bundles/complex-app.bundle.yaml`
- `bundles/concept-slice.bundle.yaml`
- `bundles/impl-slice.bundle.yaml`

**Created (verifier scaffolding, 2 files):**
- `flows/_meta/deferred_skills.yaml` — the deferred-allowlist used by Task 5's verifier.
- `flows/_meta/verify_flows.py` — the Python verifier script (jsonschema + skill resolution).

**Modified:** none.

---

## Task 1: Initialize directory structure + scaffolding

- [ ] **Step 1: Create `flows/` and `bundles/` if absent.**

  ```bash
  mkdir -p flows bundles flows/_meta
  ```

  Verify: `ls -la flows/ bundles/ flows/_meta/`
  Expected: three empty (or near-empty) directories.

- [ ] **Step 2: Author `flows/_meta/deferred_skills.yaml`.**

  Content:
  ```yaml
  # flows/_meta/deferred_skills.yaml
  # Skills referenced by SKILL_GRAPH § 6 tier-composition table that have no
  # Phase-2 mini-plan authoring them. The verifier (Task 5) emits warnings
  # (not errors) for these names. Phase 3 must close this list.
  deferred_phase_3:
    - concept-goals
    - concept-comparable
    - design-inspiration
    - walkthrough-mockup-lit
    - walkthrough-mockup-astro
    - walkthrough-mockup-framework
    - mockup-feedback-annotate
    - mockup-feedback-triage
    - mockup-feedback-patch
    - mockup-feedback-apply
    - impl-architecture-templates
  ```

- [ ] **Step 3: Commit scaffolding.**

  ```bash
  git add flows/_meta/deferred_skills.yaml
  git commit -m "feat(flows): scaffold flows/ + bundles/ + deferred-skills allowlist (Task 2H step 1)"
  ```

---

## Task 2: Author the two slice flows + bundles

These are the building blocks; tier flows reference their nodes by inlining. Author and validate them first so tier flows have a confirmed source-of-truth for the inlined node graphs.

### Task 2.1: `flows/concept-slice.flow.yaml`

**Files:**
- Create: `flows/concept-slice.flow.yaml`

- [ ] **Step 1: Write the file with all 4 skill nodes per § "Pinned: Slice Flow Node Lists".**

  Required top-level fields: `id: concept-slice`, `name`, `description`, `nodes`, `edges`, `entry: c-brainstorm`. Set `version: '2.0.0'`, `metadata.tags: [concept-slice, per-feature, slice]`, `metadata.stage: alpha`.

  Nodes (4 skill nodes):
  - `c-brainstorm` → `concept-slice-brainstorm` (entry)
  - `c-align` → `concept-slice-align`
  - `c-scope-feature` → `concept-slice-scope-feature`
  - `c-design-feature` → `concept-slice-design-feature`

  Edges (3 `flow` edges): `c-brainstorm → c-align → c-scope-feature → c-design-feature`.

  Each node MUST have a `position` (`{x, y}`) — pick reasonable values (e.g. `x: <i>*240, y: 200`).

  Each node SHOULD have `data.label`, `data.subagent: false`, and `data.parameters: {}` (empty per-skill defaults).

- [ ] **Step 2: Validate against `contracts/flow.schema.json`.**

  Run:
  ```bash
  python3 -c "
  import json, yaml, sys
  from jsonschema import validate
  schema = json.load(open('contracts/flow.schema.json'))
  data = yaml.safe_load(open('flows/concept-slice.flow.yaml'))
  validate(instance=data, schema=schema)
  print('OK: concept-slice.flow.yaml validates')
  "
  ```
  Expected: `OK: concept-slice.flow.yaml validates`. On failure, fix the YAML and rerun.

- [ ] **Step 3: Commit.**

  ```bash
  git add flows/concept-slice.flow.yaml
  git commit -m "feat(flows): add concept-slice.flow.yaml (Task 2H step 2.1)"
  ```

### Task 2.2: `bundles/concept-slice.bundle.yaml`

**Files:**
- Create: `bundles/concept-slice.bundle.yaml`

- [ ] **Step 1: Write the file with `requires:` listing exactly the 4 skill nodes from `flows/concept-slice.flow.yaml`.**

  Content:
  ```yaml
  name: concept-slice
  description: 'Per-feature concept loop — brainstorm → align → scope-feature → design-feature. Used directly by standard-app/complex-app tier flows; inlined as nodes in their flow files.'
  metadata:
    version: '1.0.0'
    tags: [bundle, concept-slice, per-feature, slice]
    stage: alpha
  requires:
    - skill:concept-slice-brainstorm
    - skill:concept-slice-align
    - skill:concept-slice-scope-feature
    - skill:concept-slice-design-feature
  ```

- [ ] **Step 2: Verify YAML parses.**

  Run: `python3 -c "import yaml; yaml.safe_load(open('bundles/concept-slice.bundle.yaml'))"`
  Expected: no output, exit 0.

- [ ] **Step 3: Verify `requires:` matches the flow's node list.**

  Run:
  ```bash
  python3 - <<'EOF'
  import yaml
  flow = yaml.safe_load(open('flows/concept-slice.flow.yaml'))
  bundle = yaml.safe_load(open('bundles/concept-slice.bundle.yaml'))
  flow_skills = {n['data']['skill'] for n in flow['nodes'] if n['type']=='skill'}
  bundle_skills = {r.split(':',1)[1] for r in bundle['requires'] if r.startswith('skill:')}
  assert flow_skills == bundle_skills, (flow_skills - bundle_skills, bundle_skills - flow_skills)
  print('OK: bundle requires matches flow nodes')
  EOF
  ```
  Expected: `OK: bundle requires matches flow nodes`.

- [ ] **Step 4: Commit.**

  ```bash
  git add bundles/concept-slice.bundle.yaml
  git commit -m "feat(bundles): add concept-slice.bundle.yaml (Task 2H step 2.2)"
  ```

### Task 2.3: `flows/impl-slice.flow.yaml`

**Files:**
- Create: `flows/impl-slice.flow.yaml`

- [ ] **Step 1: Write the file with all 8 skill nodes per § "Pinned: Slice Flow Node Lists".**

  Top-level: `id: impl-slice`, `version: '2.0.0'`, `name: 'Impl Slice'`, `description: '...'`, `metadata.tags: [impl-slice, per-feature, slice]`, `entry: i-brainstorm`.

  Nodes (8 skill nodes), edges (7 `flow` edges chaining them in order: `i-brainstorm → i-align → i-plan-vertical → i-implement → i-test → i-recap → i-refactor → i-commit`).

- [ ] **Step 2: Validate against `flow.schema.json`** (same Python snippet as 2.1 step 2, swapping the path).

  Expected: `OK: impl-slice.flow.yaml validates`.

- [ ] **Step 3: Commit.**

  ```bash
  git add flows/impl-slice.flow.yaml
  git commit -m "feat(flows): add impl-slice.flow.yaml (Task 2H step 2.3)"
  ```

### Task 2.4: `bundles/impl-slice.bundle.yaml`

**Files:**
- Create: `bundles/impl-slice.bundle.yaml`

- [ ] **Step 1: Write the file with `requires:` listing exactly the 8 skill nodes from `flows/impl-slice.flow.yaml`.**

  Content (all 8 skills as `skill:<name>` entries):
  ```yaml
  name: impl-slice
  description: 'Per-feature impl loop — brainstorm → align → plan-vertical → implement → test → recap → refactor → commit. Used directly by simple-app/standard-app/complex-app tier flows; inlined as nodes.'
  metadata:
    version: '1.0.0'
    tags: [bundle, impl-slice, per-feature, slice]
    stage: alpha
  requires:
    - skill:impl-plan-brainstorm
    - skill:impl-plan-align
    - skill:impl-plan-plan-vertical
    - skill:impl-slice-implement
    - skill:impl-slice-test
    - skill:impl-slice-recap
    - skill:impl-slice-refactor
    - skill:impl-slice-commit
  ```

- [ ] **Step 2: Verify YAML + flow/bundle correspondence** (same Python snippet as 2.2 step 3).

  Expected: `OK: bundle requires matches flow nodes`.

- [ ] **Step 3: Commit.**

  ```bash
  git add bundles/impl-slice.bundle.yaml
  git commit -m "feat(bundles): add impl-slice.bundle.yaml (Task 2H step 2.4)"
  ```

---

## Task 3: Author the four tier flows

Each tier flow inlines the relevant slice nodes plus the tier-specific concept and impl-build nodes.

### Task 3.1: `flows/mvp.flow.yaml`

**Files:**
- Create: `flows/mvp.flow.yaml`

- [ ] **Step 1: Write the file per the mvp row of § "Pinned: Tier-Composition Table".**

  Top-level:
  ```yaml
  id: mvp
  version: '2.0.0'
  name: 'MVP'
  description: 'Single-feature, trivial-persistence app. One impl-slice iteration; no recap, no refactor, no concept-slice. Linear concept pipeline.'
  metadata:
    tags: [tier, mvp, fast, single-feature]
    stage: alpha
    category: prototype
  globals:
    research_depth: skip
    approval_mode: checkpoint
    subagent_mode: false
    verbosity: brief
  entry: scope
  ```

  Nodes (linear, no concept-slice, abbreviated impl-slice):
  - `scope` → `skaileup-scope-scope-project` (entry)
  - `brief` → `concept-brief`
  - `features` → `product-spec-features`
  - `mock-text` → `walkthrough-mockup-text` (mvp's mockup variant per § 6 row)
  - `techstack` → `impl-architecture-techstack`
  - `templates` → DEFERRED (`impl-architecture-templates` — see allowlist; emit a node referencing it; verifier will warn)
  - `scaffold` → `impl-build-scaffold`
  - `plan-vertical` → `impl-plan-plan-vertical` (only impl-plan node for mvp)
  - `implement` → `impl-slice-implement`
  - `commit` → `impl-slice-commit`
  - `test-unit` → `impl-quality-test-unit`

  Edges (linear chain): `scope → brief → features → mock-text → techstack → templates → scaffold → plan-vertical → implement → commit → test-unit`.

  **Why no impl-slice-test/recap/refactor:** the table marks them blank for the mvp column. **Why no concept-slice nodes:** the table marks them blank for mvp.

- [ ] **Step 2: Validate against `flow.schema.json`.**

  Run the Python snippet from Task 2.1 step 2 (substituting `flows/mvp.flow.yaml`).
  Expected: `OK: mvp.flow.yaml validates`.

- [ ] **Step 3: Commit.**

  ```bash
  git add flows/mvp.flow.yaml
  git commit -m "feat(flows): add mvp.flow.yaml (Task 2H step 3.1)"
  ```

### Task 3.2: `flows/simple-app.flow.yaml`

**Files:**
- Create: `flows/simple-app.flow.yaml`

- [ ] **Step 1: Write the file per the simple-app column.**

  Top-level: `id: simple-app`, `name: 'Simple App'`, `entry: scope`. Tags include `tier`, `simple-app`. Category: `full-stack`.

  Nodes (linear concept, full impl-slice loop, no concept-slice):
  - `scope` → `skaileup-scope-scope-project`
  - `brief` → `concept-brief`
  - `brand-visual` → `design-brand-visual`
  - `journeys` → `experience-journeys`
  - `features` → `product-spec-features`
  - `screens` → `experience-screens`
  - `mock-static` → `walkthrough-mockup-static-html`
  - `comp-isolated` → `component-mockup-isolated-html`
  - `techstack` → `impl-architecture-techstack`
  - `templates` → DEFERRED
  - `datamodel` → `impl-architecture-datamodel`
  - `scaffold` → `impl-build-scaffold`
  - `foundation` → `impl-build-foundation`
  - `migrate` → `impl-build-migrate`
  - `seed` → `impl-build-seed`
  - `docs` → `impl-build-docs`
  - `i-align` → `impl-plan-align`
  - `i-plan-vertical` → `impl-plan-plan-vertical`
  - `i-implement` → `impl-slice-implement`
  - `i-test` → `impl-slice-test`
  - `i-recap` → `impl-slice-recap`
  - `i-commit` → `impl-slice-commit`
  - `q-test-unit` → `impl-quality-test-unit`
  - `q-test-e2e` → `impl-quality-test-e2e`

  **No** `impl-plan-brainstorm`, `impl-slice-refactor`, `impl-quality-*` integ/audit/eval/ready, `concept-slice-*`, `experience-behaviors`, `experience-components`, `component-mockup-storybook`, mockup-feedback-*, `ops-*`. (Per simple-app column, all blank.)

  Edges: chain concept linearly, then impl-slice loop, then quality tests at end. Use `parallel` edges where appropriate (e.g. mock-static and comp-isolated can run in parallel after `screens`).

- [ ] **Step 2: Validate against the schema.**

- [ ] **Step 3: Commit.**

  ```bash
  git add flows/simple-app.flow.yaml
  git commit -m "feat(flows): add simple-app.flow.yaml (Task 2H step 3.2)"
  ```

### Task 3.3: `flows/standard-app.flow.yaml`

**Files:**
- Create: `flows/standard-app.flow.yaml`

- [ ] **Step 1: Write the file per the standard-app column.**

  Top-level: `id: standard-app`, `category: full-stack`.

  **High-level concept phase** (project-wide, runs once):
  - `scope`, `brief`, `goals` (DEFERRED), `comparable` (DEFERRED), `brand-visual`, `inspiration` (DEFERRED), `journeys`, `behaviors-opt` (`experience-behaviors`, `optional: true`, `skip_when: "tier.experience in ['none','light']"`), `screens`, `components` (`experience-components`), `features`, `mock-static` (or DEFERRED `walkthrough-mockup-astro`), `comp-storybook` (`component-mockup-storybook`), mockup-feedback-* (DEFERRED — 4 nodes).
  - Architecture: `techstack`, `templates` (DEFERRED), `system` (`impl-architecture-system`), `datamodel`.
  - Build: `scaffold`, `foundation`, `migrate`, `seed`, `docs`. `infra` is `(opt)` — include with `optional: true`.

  **Per-feature concept-slice loop** (NO brainstorm — per § 6 standard column):
  - `cs-align` → `concept-slice-align`
  - `cs-scope-feature` → `concept-slice-scope-feature`
  - `cs-design-feature` → `concept-slice-design-feature`

  **Per-feature impl-slice loop (full):**
  - `i-brainstorm` → `impl-plan-brainstorm`
  - `i-align`, `i-plan-vertical`, `i-implement`, `i-test`, `i-recap`, `i-refactor` (NEW for this tier), `i-commit`

  **Quality (post-loop):**
  - `q-test-unit`, `q-test-integration`, `q-test-e2e`, `q-ready` (`impl-quality-ready`)

  **Ops:**
  - `ops-review`, `ops-sync`

  Edges: high-level concept linear with parallel groups; impl-build linear; then loop signal — for now express the per-feature loop as a logical chain in the YAML, with documentation in the `description` that the orchestrator interprets `concept-slice → impl-slice` as iterated per feature. (No `loop` edge type exists in `flow.schema.json`.)

- [ ] **Step 2: Validate.**
- [ ] **Step 3: Commit.**

  ```bash
  git add flows/standard-app.flow.yaml
  git commit -m "feat(flows): add standard-app.flow.yaml (Task 2H step 3.3)"
  ```

### Task 3.4: `flows/complex-app.flow.yaml`

**Files:**
- Create: `flows/complex-app.flow.yaml`

- [ ] **Step 1: Write the file per the complex-app column — superset of standard-app plus complex-only additions.**

  Top-level: `id: complex-app`, `category: full-stack`. Tags include `tier`, `complex-app`, `enterprise`, `multi-product`.

  **Concept additions over standard-app:**
  - `brand-voice` → `design-brand-voice`
  - `mock-framework` → `walkthrough-mockup-framework` (DEFERRED) — alternative to mock-static for embedded contexts
  - `infra` is now non-optional
  - Project-overview: `ops-project-overview`, `ops-project-subsystem-map`, `ops-project-integration`, `ops-project-review`

  **Concept-slice additions:**
  - `cs-brainstorm` → `concept-slice-brainstorm` (now present)
  - cs-align/scope-feature/design-feature already present from standard-app

  **Impl-plan additions:**
  - `i-supervised` → `impl-plan-supervised`

  **Impl-quality additions:**
  - `q-eval-code` → `impl-quality-eval-code`
  - `q-audit` → `impl-quality-audit` (runs every slice — orchestrator semantics, expressed via edge ordering)

  Order the nodes per the prose: `scope-project → high-level concept → project-overview → impl-build setup → loop: concept-slice → impl-slice → impl-quality/audit → done`.

- [ ] **Step 2: Validate.**
- [ ] **Step 3: Commit.**

  ```bash
  git add flows/complex-app.flow.yaml
  git commit -m "feat(flows): add complex-app.flow.yaml (Task 2H step 3.4)"
  ```

---

## Task 4: Author the four tier bundles (with inheritance)

Each tier bundle's `requires:` is exactly the **delta** vs. its predecessor (per SKILL_GRAPH § 6 lines 502-504), plus a `bundle:<predecessor>` line.

### Task 4.1: `bundles/mvp.bundle.yaml`

**Files:**
- Create: `bundles/mvp.bundle.yaml`

- [ ] **Step 1: List every skill referenced by `flows/mvp.flow.yaml` as `skill:<name>` entries.**

  No `bundle:` ancestor (mvp is the root). Pull the skill list directly from `flows/mvp.flow.yaml`'s nodes by running:
  ```bash
  python3 - <<'EOF'
  import yaml
  flow = yaml.safe_load(open('flows/mvp.flow.yaml'))
  print('\n'.join(sorted({"  - skill:" + n['data']['skill'] for n in flow['nodes'] if n['type']=='skill'})))
  EOF
  ```
  Paste the output into the bundle's `requires:` block.

  Content shape:
  ```yaml
  name: mvp
  description: 'Tier bundle for MVP — single-feature, fast prototype.'
  metadata:
    version: '1.0.0'
    tags: [bundle, tier, mvp]
    stage: alpha
  requires:
    - skill:skaileup-scope-scope-project
    - skill:concept-brief
    - skill:product-spec-features
    - skill:walkthrough-mockup-text
    - skill:impl-architecture-techstack
    # - skill:impl-architecture-templates    # DEFERRED: keep as comment; flag in commit msg
    - skill:impl-build-scaffold
    - skill:impl-plan-plan-vertical
    - skill:impl-slice-implement
    - skill:impl-slice-commit
    - skill:impl-quality-test-unit
  ```

- [ ] **Step 2: Verify against the flow's node list.**

  Run the same `flow ↔ bundle` correspondence check as Task 2.2 step 3 (substituting `mvp` paths). Expected: `OK: bundle requires matches flow nodes`.

- [ ] **Step 3: Commit.**

  ```bash
  git add bundles/mvp.bundle.yaml
  git commit -m "feat(bundles): add mvp.bundle.yaml (Task 2H step 4.1)"
  ```

### Task 4.2: `bundles/simple-app.bundle.yaml`

**Files:**
- Create: `bundles/simple-app.bundle.yaml`

- [ ] **Step 1: Compute the delta vs. mvp** by running:
  ```bash
  python3 - <<'EOF'
  import yaml
  mvp = {n['data']['skill'] for n in yaml.safe_load(open('flows/mvp.flow.yaml'))['nodes'] if n['type']=='skill'}
  simple = {n['data']['skill'] for n in yaml.safe_load(open('flows/simple-app.flow.yaml'))['nodes'] if n['type']=='skill'}
  print('Skills to add to simple-app bundle (delta vs mvp):')
  for s in sorted(simple - mvp):
      print(f"  - skill:{s}")
  EOF
  ```

  Content shape:
  ```yaml
  name: simple-app
  description: 'Tier bundle for simple-app — single-user, ≤5 features, full impl-slice loop.'
  metadata:
    version: '1.0.0'
    tags: [bundle, tier, simple-app]
    stage: alpha
  requires:
    - bundle:mvp
    # delta vs mvp (paste from script output):
    - skill:design-brand-visual
    - skill:experience-journeys
    - skill:experience-screens
    - skill:walkthrough-mockup-static-html
    - skill:component-mockup-isolated-html
    - skill:impl-architecture-datamodel
    - skill:impl-build-foundation
    - skill:impl-build-migrate
    - skill:impl-build-seed
    - skill:impl-build-docs
    - skill:impl-plan-align
    - skill:impl-slice-test
    - skill:impl-slice-recap
    - skill:impl-quality-test-e2e
  ```

- [ ] **Step 2: Verify against the flow's node list (delta-aware).**

  ```bash
  python3 - <<'EOF'
  import yaml
  mvp_b = yaml.safe_load(open('bundles/mvp.bundle.yaml'))
  sim_b = yaml.safe_load(open('bundles/simple-app.bundle.yaml'))
  sim_f = yaml.safe_load(open('flows/simple-app.flow.yaml'))

  mvp_skills = {r.split(':',1)[1] for r in mvp_b['requires'] if r.startswith('skill:')}
  sim_delta_skills = {r.split(':',1)[1] for r in sim_b['requires'] if r.startswith('skill:')}
  sim_total_skills = mvp_skills | sim_delta_skills
  flow_skills = {n['data']['skill'] for n in sim_f['nodes'] if n['type']=='skill'}

  assert flow_skills == sim_total_skills, (flow_skills - sim_total_skills, sim_total_skills - flow_skills)
  assert any(r == 'bundle:mvp' for r in sim_b['requires']), 'simple-app must inherit mvp'
  print('OK: simple-app bundle inherits mvp + delta matches flow')
  EOF
  ```
  Expected: `OK: simple-app bundle inherits mvp + delta matches flow`.

- [ ] **Step 3: Commit.**

  ```bash
  git add bundles/simple-app.bundle.yaml
  git commit -m "feat(bundles): add simple-app.bundle.yaml (Task 2H step 4.2)"
  ```

### Task 4.3: `bundles/standard-app.bundle.yaml`

Repeat the same delta-script pattern, predecessor = `simple-app`.

- [ ] **Step 1: Compute delta.**

  ```bash
  python3 - <<'EOF'
  import yaml
  prior = {n['data']['skill'] for n in yaml.safe_load(open('flows/simple-app.flow.yaml'))['nodes'] if n['type']=='skill'}
  cur   = {n['data']['skill'] for n in yaml.safe_load(open('flows/standard-app.flow.yaml'))['nodes'] if n['type']=='skill'}
  print('Delta vs simple-app:')
  for s in sorted(cur - prior):
      print(f"  - skill:{s}")
  EOF
  ```

  Content (template):
  ```yaml
  name: standard-app
  description: 'Tier bundle for standard-app — multi-user / ≤20 features. Adds concept-slice, impl-plan-brainstorm, impl-slice-refactor, full quality suite + ops.'
  metadata:
    version: '1.0.0'
    tags: [bundle, tier, standard-app]
    stage: alpha
  requires:
    - bundle:simple-app
    # delta — paste from script
    - skill:experience-behaviors
    - skill:experience-components
    - skill:component-mockup-storybook
    - skill:impl-architecture-system
    - skill:impl-build-infrastructure
    - skill:impl-plan-brainstorm
    - skill:impl-slice-refactor
    - skill:concept-slice-align
    - skill:concept-slice-scope-feature
    - skill:concept-slice-design-feature
    - skill:impl-quality-test-integration
    - skill:impl-quality-ready
    - skill:ops-review
    - skill:ops-sync
  ```

- [ ] **Step 2: Verify against flow.**

  Same script pattern as 4.2 step 2 (substituting `standard-app`). Expected `OK`.

- [ ] **Step 3: Commit.**

  ```bash
  git add bundles/standard-app.bundle.yaml
  git commit -m "feat(bundles): add standard-app.bundle.yaml (Task 2H step 4.3)"
  ```

### Task 4.4: `bundles/complex-app.bundle.yaml`

- [ ] **Step 1: Compute delta vs standard-app.**

  ```bash
  python3 - <<'EOF'
  import yaml
  prior = {n['data']['skill'] for n in yaml.safe_load(open('flows/standard-app.flow.yaml'))['nodes'] if n['type']=='skill'}
  cur   = {n['data']['skill'] for n in yaml.safe_load(open('flows/complex-app.flow.yaml'))['nodes'] if n['type']=='skill'}
  print('Delta vs standard-app:')
  for s in sorted(cur - prior):
      print(f"  - skill:{s}")
  EOF
  ```

  Content (template):
  ```yaml
  name: complex-app
  description: 'Tier bundle for complex-app — multi-product / enterprise. Supervised plan, audit-per-slice, full ops project-* suite.'
  metadata:
    version: '1.0.0'
    tags: [bundle, tier, complex-app, enterprise]
    stage: alpha
  requires:
    - bundle:standard-app
    # delta — paste from script
    - skill:design-brand-voice
    - skill:concept-slice-brainstorm
    - skill:impl-plan-supervised
    - skill:impl-quality-eval-code
    - skill:impl-quality-audit
    - skill:ops-project-overview
    - skill:ops-project-subsystem-map
    - skill:ops-project-integration
    - skill:ops-project-review
  ```

- [ ] **Step 2: Verify.**
- [ ] **Step 3: Commit.**

  ```bash
  git add bundles/complex-app.bundle.yaml
  git commit -m "feat(bundles): add complex-app.bundle.yaml (Task 2H step 4.4)"
  ```

---

## Task 5: Author the verifier + run end-to-end checks

This task produces the deterministic check that the entire 12-file artefact set is internally consistent and resolves to existing or planned skills.

### Task 5.1: Author `flows/_meta/verify_flows.py`

**Files:**
- Create: `flows/_meta/verify_flows.py`

- [ ] **Step 1: Write a failing test first (TDD)** by listing the assertions the verifier will perform:

  Create a tiny test harness `flows/_meta/test_verify.py` with these cases (the verifier doesn't exist yet so they fail):
  1. `verify_flows.py` exits 0 when run against the 6 happy-path files.
  2. `verify_flows.py` exits 2 when a flow node references a non-existent, non-deferred skill name (`skill: this-does-not-exist`).
  3. `verify_flows.py` exits 0 with WARNING printed when a flow node references a deferred skill (`concept-goals`).
  4. `verify_flows.py` exits 2 when a tier bundle's `requires:` skill set ≠ flow's node skill set ∪ inherited bundles' skills.
  5. `verify_flows.py` exits 2 when any flow file fails `jsonschema` validation against `contracts/flow.schema.json`.

- [ ] **Step 2: Run the failing tests.**

  Run: `pytest flows/_meta/test_verify.py -v`
  Expected: tests fail / error (`verify_flows.py` doesn't exist yet).

- [ ] **Step 3: Implement `verify_flows.py`.**

  ```python
  #!/usr/bin/env python3
  """Verifier for Phase 2 Task 2H artifacts. Exit 0 if all checks pass; 2 on any failure."""
  import json, re, sys, subprocess
  from pathlib import Path

  try:
      import yaml
      import jsonschema
  except ImportError as e:
      print(f"ERROR: missing dep ({e}); pip install pyyaml jsonschema", file=sys.stderr)
      sys.exit(2)

  REPO = Path(__file__).resolve().parents[2]   # …/ai-assets-skaileup
  FLOWS = REPO / "flows"
  BUNDLES = REPO / "bundles"
  SCHEMA = json.load(open(REPO / "contracts/flow.schema.json"))
  DEFERRED = set(yaml.safe_load(open(FLOWS / "_meta/deferred_skills.yaml"))["deferred_phase_3"])

  TIER_FLOWS = ["mvp", "simple-app", "standard-app", "complex-app"]
  SLICE_FLOWS = ["concept-slice", "impl-slice"]
  ALL_FLOWS = TIER_FLOWS + SLICE_FLOWS

  PHASE_2_PLANNED = {
      "skaileup-scope-scope-project",
      "concept-slice-brainstorm", "concept-slice-align",
      "concept-slice-scope-feature", "concept-slice-design-feature",
      "impl-plan-align",
      "impl-slice-test", "impl-slice-recap", "impl-slice-refactor", "impl-slice-commit",
      "walkthrough-mockup-static-html", "component-mockup-isolated-html",
  }

  def gather_existing_skill_names():
      names = set()
      for skill_md in REPO.glob("**/SKILL.md"):
          try:
              fm = skill_md.read_text().split("---")[1]
              data = yaml.safe_load(fm)
              if data and "name" in data:
                  names.add(data["name"])
          except Exception:
              continue
      return names

  def validate_flow(flow_path):
      data = yaml.safe_load(flow_path.read_text())
      jsonschema.validate(instance=data, schema=SCHEMA)
      return data

  def collect_flow_skills(flow_data):
      return {n["data"]["skill"] for n in flow_data["nodes"] if n["type"] == "skill"}

  def collect_bundle_skills(bundle_path):
      data = yaml.safe_load(bundle_path.read_text())
      return data, {r.split(":", 1)[1] for r in data["requires"] if r.startswith("skill:")}, \
             [r.split(":", 1)[1] for r in data["requires"] if r.startswith("bundle:")]

  def main():
      errors = []
      warnings = []

      existing = gather_existing_skill_names()
      knowable = existing | PHASE_2_PLANNED

      # 1. Validate every flow against the JSON schema and collect its skills
      flow_skills = {}
      for fid in ALL_FLOWS:
          fp = FLOWS / f"{fid}.flow.yaml"
          if not fp.exists():
              errors.append(f"missing flow file: {fp}"); continue
          try:
              data = validate_flow(fp)
              flow_skills[fid] = collect_flow_skills(data)
              if data["id"] != fid:
                  errors.append(f"{fp}: id field {data['id']!r} != filename stem {fid!r}")
          except jsonschema.ValidationError as e:
              errors.append(f"{fp}: schema validation failed: {e.message}")

      # 2. Resolve every skill name referenced
      for fid, skills in flow_skills.items():
          for s in sorted(skills):
              if s in knowable:
                  continue
              if s in DEFERRED:
                  warnings.append(f"{fid}: deferred skill referenced: {s}")
              else:
                  errors.append(f"{fid}: unresolved skill: {s}")

      # 3. Verify each tier bundle's requires == flow's node skills (delta-aware via inheritance)
      for tier in TIER_FLOWS:
          bp = BUNDLES / f"{tier}.bundle.yaml"
          if not bp.exists():
              errors.append(f"missing bundle: {bp}"); continue
          data, delta, parents = collect_bundle_skills(bp)

          # Walk inheritance chain to compute effective set
          effective = set(delta)
          stack = list(parents)
          seen = set()
          while stack:
              p = stack.pop()
              if p in seen: continue
              seen.add(p)
              pp = BUNDLES / f"{p}.bundle.yaml"
              if not pp.exists():
                  errors.append(f"{bp}: declares bundle:{p} but file missing"); continue
              pdata, pdelta, pparents = collect_bundle_skills(pp)
              effective |= pdelta
              stack.extend(pparents)

          flow_set = flow_skills.get(tier, set())
          if effective != flow_set:
              missing = flow_set - effective
              extras  = effective - flow_set
              if missing:
                  errors.append(f"{bp}: missing skills (in flow, not bundle): {sorted(missing)}")
              if extras:
                  errors.append(f"{bp}: extra skills (in bundle, not flow): {sorted(extras)}")

          # Inheritance pin
          expected_parent = {"simple-app":"mvp", "standard-app":"simple-app", "complex-app":"standard-app"}
          if tier in expected_parent and expected_parent[tier] not in parents:
              errors.append(f"{bp}: missing required parent bundle:{expected_parent[tier]}")
          if tier == "mvp" and parents:
              errors.append(f"{bp}: mvp must NOT have parent bundles, found {parents}")

      # 4. Slice bundles must be leaves and match their flow nodes
      for sid in SLICE_FLOWS:
          bp = BUNDLES / f"{sid}.bundle.yaml"
          if not bp.exists():
              errors.append(f"missing slice bundle: {bp}"); continue
          data, delta, parents = collect_bundle_skills(bp)
          if parents:
              errors.append(f"{bp}: slice bundle must not inherit (no bundle: entries), found {parents}")
          flow_set = flow_skills.get(sid, set())
          if delta != flow_set:
              errors.append(f"{bp}: requires set {sorted(delta)} != flow nodes {sorted(flow_set)}")

      # Print result
      for w in warnings:
          print(f"WARN: {w}", file=sys.stderr)
      for e in errors:
          print(f"ERROR: {e}", file=sys.stderr)

      if errors:
          print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s)", file=sys.stderr)
          return 2
      print(f"OK: 6 flows + 6 bundles consistent ({len(warnings)} deferred-skill warnings)")
      return 0

  if __name__ == "__main__":
      sys.exit(main())
  ```

- [ ] **Step 4: Run the test harness against the new verifier.**

  Run: `pytest flows/_meta/test_verify.py -v`
  Expected: all 5 tests pass.

- [ ] **Step 5: Run the verifier against the actual 12 files.**

  Run: `python3 flows/_meta/verify_flows.py`
  Expected: prints `OK: 6 flows + 6 bundles consistent (N deferred-skill warnings)` where N matches the count of deferred skills referenced. Exit code 0.

- [ ] **Step 6: Commit verifier + tests.**

  ```bash
  git add flows/_meta/verify_flows.py flows/_meta/test_verify.py
  git commit -m "test(flows): add verify_flows.py + tests (Task 2H step 5)"
  ```

---

## Task 6: Final cross-cutting verification

- [ ] **Step 1: Tree shape.**

  Run: `find flows bundles -type f | sort`
  Expected:
  ```
  bundles/complex-app.bundle.yaml
  bundles/concept-slice.bundle.yaml
  bundles/impl-slice.bundle.yaml
  bundles/mvp.bundle.yaml
  bundles/simple-app.bundle.yaml
  bundles/standard-app.bundle.yaml
  flows/_meta/deferred_skills.yaml
  flows/_meta/test_verify.py
  flows/_meta/verify_flows.py
  flows/complex-app.flow.yaml
  flows/concept-slice.flow.yaml
  flows/impl-slice.flow.yaml
  flows/mvp.flow.yaml
  flows/simple-app.flow.yaml
  flows/standard-app.flow.yaml
  ```

- [ ] **Step 2: Schema validation across all flows.**

  ```bash
  python3 - <<'EOF'
  import json, yaml
  from jsonschema import validate
  schema = json.load(open('contracts/flow.schema.json'))
  for f in ['mvp','simple-app','standard-app','complex-app','concept-slice','impl-slice']:
      validate(yaml.safe_load(open(f'flows/{f}.flow.yaml')), schema)
      print(f'OK: flows/{f}.flow.yaml')
  EOF
  ```
  Expected: 6 lines `OK: …`.

- [ ] **Step 3: Verifier final run.**

  Run: `python3 flows/_meta/verify_flows.py`
  Expected: exit 0; only deferred-skill WARN lines, no ERROR lines.

- [ ] **Step 4: Inheritance-chain visual check.**

  ```bash
  python3 - <<'EOF'
  import yaml
  for tier in ['mvp','simple-app','standard-app','complex-app']:
      data = yaml.safe_load(open(f'bundles/{tier}.bundle.yaml'))
      parents = [r for r in data['requires'] if r.startswith('bundle:')]
      delta_n = sum(1 for r in data['requires'] if r.startswith('skill:'))
      print(f"{tier}: parents={parents}  +{delta_n} skills")
  EOF
  ```
  Expected (illustrative; exact counts depend on flow design):
  ```
  mvp: parents=[]  +N1 skills
  simple-app: parents=['bundle:mvp']  +N2 skills
  standard-app: parents=['bundle:simple-app']  +N3 skills
  complex-app: parents=['bundle:standard-app']  +N4 skills
  ```
  Each tier must have exactly one parent in the right chain.

- [ ] **Step 5: Spot-check `scope-project` is the entry of every tier flow.**

  ```bash
  python3 - <<'EOF'
  import yaml
  for f in ['mvp','simple-app','standard-app','complex-app']:
      data = yaml.safe_load(open(f'flows/{f}.flow.yaml'))
      entry = data.get('entry')
      entry_node = next((n for n in data['nodes'] if n['id']==entry), None)
      assert entry_node and entry_node['data']['skill'] == 'skaileup-scope-scope-project', f"{f} entry wrong"
      print(f"OK: {f} entry = scope-project")
  EOF
  ```
  Expected: 4 `OK: <tier> entry = scope-project` lines.

- [ ] **Step 6: Spot-check slice flows are NOT entered by scope-project.**

  ```bash
  python3 - <<'EOF'
  import yaml
  for f in ['concept-slice','impl-slice']:
      data = yaml.safe_load(open(f'flows/{f}.flow.yaml'))
      entry = data.get('entry')
      entry_node = next((n for n in data['nodes'] if n['id']==entry), None)
      assert entry_node['data']['skill'] != 'skaileup-scope-scope-project', f"{f} should not enter via scope"
      print(f"OK: {f} entry = {entry_node['data']['skill']}")
  EOF
  ```

- [ ] **Step 7: Final commit.**

  ```bash
  git add -A flows/ bundles/
  git commit -m "feat(flows,bundles): finalize Phase 2 tier + slice flows + bundles (Task 2H complete)"
  ```

---

## Definition of Done

- [ ] All 12 primary files exist at the paths listed in § "File Targets" (6 flow YAMLs + 6 bundle YAMLs).
- [ ] All 6 flow files validate against `contracts/flow.schema.json` via `jsonschema`.
- [ ] Each tier flow's `id` field is the bare kebab-case tier name (no `flow:` prefix); each flow file's `id` matches the filename stem.
- [ ] Each tier flow has `entry: <node-id>` pointing to a `skaileup-scope-scope-project` node.
- [ ] Each slice flow has `entry: <node-id>` pointing to its first phase (`concept-slice-brainstorm` or `impl-plan-brainstorm`).
- [ ] Each tier flow's node set EXACTLY matches the corresponding column of SKILL_GRAPH § 6 tier-composition table (with deferred skills marked in commit messages and listed in `deferred_skills.yaml`).
- [ ] Each tier bundle's `requires:` is the **delta** vs. its predecessor, plus `bundle:<predecessor>` (mvp has no predecessor and lists everything).
- [ ] Bundle inheritance chain: `simple-app` → `mvp`; `standard-app` → `simple-app`; `complex-app` → `standard-app`.
- [ ] Each slice bundle is a leaf (no `bundle:` parent) and lists exactly its flow's skill nodes.
- [ ] `flows/_meta/verify_flows.py` exits 0 against the final artefact set, with WARN lines only for the deferred-skill list.
- [ ] `pytest flows/_meta/test_verify.py -v` passes (all 5 cases green).
- [ ] No skill referenced in any flow node resolves to "unknown" (it must be either an existing SKILL.md `name:` or a Phase-2-planned name from `PHASE_2_PLANNED`, or appear in `deferred_skills.yaml`).
- [ ] All commits land on the active migration branch with messages following `feat(flows): / feat(bundles): / test(flows):` prefix convention.
- [ ] No edits to any existing `*.flow.yaml` files in other domains (`skaileup/flows/`, `impl-build/flows/`, `lab/flows/`) — those legacy files are out of scope.

---

## Boundary Clarification

**This task does NOT execute or implement the underlying skills.** Skills are authored in Tasks 2.0/2A–2G. Task 2H authors flow + bundle YAML referencing them.

**This task does NOT generate bundles from flows.** A separate Task 2I proposes a `lab/compile-bundle` skill that walks a flow's node graph and emits the matching bundle. Task 2H bundles are HAND-AUTHORED to establish ground truth; Task 2I will reproduce them.

**This task does NOT wire up Phase 3 work.** Walkthrough renderers (`lit`, `astro`, `framework`), the mockup-feedback cluster, `concept-goals`/`concept-comparable`/`design-inspiration`, and `impl-architecture-templates` are referenced in flows but live in `deferred_skills.yaml`. The verifier WARNs (does not error) on them.

**This task does NOT modify any existing flows.** Legacy flows under `skaileup/flows/`, `impl-build/flows/`, `lab/flows/` are untouched. They will be rationalized in a follow-on cleanup pass post-Phase 2.

---

## Open Questions / Ambiguities

1. **Deferred Phase 3 skills referenced in tier flows.** The SKILL_GRAPH § 6 table marks several skills as required for standard-app and complex-app (e.g. `walkthrough-mockup-astro`, `mockup-feedback-*`, `concept-goals`, `concept-comparable`, `design-inspiration`, `impl-architecture-templates`). None have a Phase-2 mini-plan. **This plan's resolution:** include them as nodes in the tier flows (so the table is honored) but list them in `flows/_meta/deferred_skills.yaml` so the verifier WARNs (not errors). Alternative: prune them from the Phase 2 flows entirely (smaller surface, but deviates from § 6). User decision required: either approve "WARN-only" mode for Phase 2 or instruct the executing agent to prune. Default chosen here: **WARN-only** (preserves table fidelity; deferred skills can be added later without refactoring the flows).

2. **`impl-architecture-templates` ambiguity.** SKILL_GRAPH § 6 has a row "impl-arch/templates ✓ ✓ ✓ ✓" for all four tiers. But CLAUDE.md notes the templates domain promotes specific stack templates (e.g. `template-postxl`) to skills rather than a single `impl-architecture-templates` skill. **Resolution:** treat `impl-architecture-templates` as deferred (placeholder for "the right stack template skill, picked per project"). Phase 3 should resolve this by either (a) adding a single `impl-architecture-templates-pick` skill that selects + delegates, or (b) replacing the row in § 6 with stack-specific entries. Flag for SKILL_GRAPH owner.

3. **`flow.schema.json` `next_flows[].domain` vocabulary.** The schema enum is `['skaileup-conceptualization','skaileup-implementation','skaileup-evaluate']` — Phase 0 vocabulary. The Phase 2 tier flows are TERMINAL (the user starts a fresh flow per project), so this plan **omits `next_flows`** on tier flows. Slice flows MAY use `next_flows` if a sensible value exists in the enum (it does not — flag for schema update). For now, slice flows also omit `next_flows`.

4. **Loop semantics.** Per SKILL_GRAPH § 6 prose, tier flows "loop: concept-slice → impl-slice". The JSON schema has no `loop` edge type (only `flow | optional | parallel`); `flows.md` mentions `review-loop` but it's also absent from the schema. **Resolution (this plan):** express the iteration semantically in the flow's `description` and rely on the orchestrator to interpret "concept-slice → impl-slice → next feature" as iterated per-feature. The flow file itself shows the chain linearly. Open: if the orchestrator team needs a structured `loop_over` field, propose a schema bump in Phase 3.

5. **`router` / `gate` / `sub-flow` node types in `flows.md` vs. `flow.schema.json`.** `flows.md` (the prose contract) describes `router`, `gate`, and `sub-flow` node types — but `flow.schema.json` `$defs` only defines `skill-node` and `group-node`. **Resolution:** this plan restricts to the JSON-schema-enforced types only (skill, group). If a tier flow needs branching (e.g. mvp's "no recap, no refactor" gate), it's expressed by simply not including those nodes — no router needed. Sub-flow composition is achieved by INLINING slice nodes, not by a sub-flow node. Flag for the schema owner: either align `flow.schema.json` to add router/gate/sub-flow definitions, or update `flows.md` to remove the prose describing them.

6. **Quality nodes' position in tier flow graphs.** SKILL_GRAPH § 6 lists quality skills (`impl-quality/*`) per tier but is silent on WHEN in the flow they run (post-loop? per-slice? release gate only?). § 5.3 says "run between slices, or at release". **Resolution:** for `mvp` and `simple-app`, quality nodes run AFTER the impl-slice phase as a final block (linear). For `standard-app` and `complex-app`, `q-audit` runs per-slice (mentioned in § 6 prose for complex), expressed as an edge from `i-commit` to `q-audit` and back to a "next-feature" decision point — but since there is no loop edge type, this is approximate. Flag for orchestrator team: confirm the per-slice-audit semantics, or propose a schema extension.

7. **Whether to author optional `(opt)` nodes with `optional: true` flag** vs. omit them. Two § 6 cells are `(opt)`: `experience/behaviors` for standard-app, `impl-build/infra` for standard-app. **Resolution:** include both with `data.optional: true` and a `skip_when` expression (per `flows.md` § "Tier Presets and `depth_from`"). The bundle's `requires:` lists them anyway (since "the orchestrator may skip" doesn't mean "the bundle doesn't need to install them"). User confirmation requested: alternative is to OMIT optional nodes from bundles to minimize installs.

8. **`mvp` quality skill row.** § 6 marks `impl-quality/unit ✓` for mvp but no other quality skills. The mvp prose says "1 iteration, no recap, no refactor" but doesn't say "no quality". This plan respects the table (only `impl-quality-test-unit` for mvp). Confirm with whoever owns SKILL_GRAPH § 6.

9. **Slice flow standalone runnability.** Both slice flows are documented as "building blocks" (per § 6 line 411-412: "The two slice flows are building blocks. Tier flows compose them"). The `concept-slice.flow.yaml` includes ALL four phases (brainstorm + align + scope-feature + design-feature) — even though simple-app skips brainstorm and complex-app uses all four. This plan's design: the slice flow is canonical (full); tier flows that don't run brainstorm reference only the relevant 3 nodes from this canonical 4-node flow. Alternative considered and rejected: author two variants `concept-slice-full.flow.yaml` and `concept-slice-no-brainstorm.flow.yaml`. Rejected because tier flows already inline nodes (don't reference the slice flow file at runtime), making variants redundant. The canonical 4-node `concept-slice.flow.yaml` is for testability and as a contract anchor.

10. **Position values are arbitrary.** The schema requires `position: {x, y}` on every node but doesn't constrain values. This plan uses simple per-row layouts; visual editors will rearrange. Don't sweat the values — just make them non-overlapping enough to read.
