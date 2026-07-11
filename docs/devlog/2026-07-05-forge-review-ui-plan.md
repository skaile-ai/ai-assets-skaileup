# Forge-Concept Review UI Implementation Plan (lanes, routes, coverage dashboard)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make forge-concept render and drive the restructured skaileup flows (sub-flow nodes, phase lanes, pick-one router nodes) and add a review/coverage dashboard over `_implementation/` artifacts.

**Architecture:** All flow-shape knowledge lands in a small shared type/util layer (`shared/`) consumed by both the Nitro server (`server/utils/flow-manager.ts` enrichment) and the Vue client (`FlowGraph.vue`, `useFlowState.ts`). Router choices are persisted in the existing flow-session JSON and orchestrated by a new server endpoint that reuses `markNodeSkipped`/`markNodeComplete` — no flow-engine change. The coverage dashboard is a read-only indexer (`server/utils/review-coverage.ts` → `GET /api/review/coverage`) plus a new `app/pages/review.vue`.

**Tech Stack:** Nuxt ^4.3.1 (compatibilityVersion 4, `app/` srcDir, `shared/` dir + `#shared` alias), Vue 3, @nuxt/ui ^4.4.0, Tailwind ^4.1.18, Nitro server routes, bun 1.3.9, vitest ^4.1.0 (`bun --bun vitest run`, unit tests in `test/unit/`, happy-dom, Nitro shims via `test/unit/_setup/nitro-globals.ts`), Playwright for e2e (not required by this plan), `yaml` ^2.8.0 already a dependency, `@skaile/workspaces` ^0.48.1 (`sdk/flow`, `sdk/runner`).

## Global Constraints

- **Target repo:** all code changes land in `/Users/matthias/devBench/SKAILEdev/forge/forge-concept`. This plan file lives in the skaileup collection repo and is the only file written there.
- **Do not patch `node_modules`.** `@skaile/workspaces` `FlowNode.type` union is `"skill" | "group"` only (`node_modules/@skaile/workspaces/dist/factory-assets/connectors/flow/engine/types.d.ts` L32). Widen locally via `shared/flow-extended.ts` and cast at the load boundary; file an upstream issue (Task 13).
- **Dependency (graceful degradation):** phase lanes assume skaileup flows emit `type: group` nodes with `data.phase` per the skaileup `2026-07-05-flow-restructure-plan.md`, and router nodes with `data.routes[]`. When a flow has no groups/phases, synthesize per-node phases from the skill-name heuristic (Task 2). When no router nodes exist, all route UI stays hidden.
- **Dependency (graceful degradation):** the coverage dashboard reads `_implementation/trace.yaml`, `_implementation/acceptance_criteria/**/*.ac.md`, and `_implementation/review/<feature>.yaml` per the skaileup `2026-07-05-perfect-review-plan.md`. Every source is optional: the indexer reports `sources.{trace,acceptanceCriteria,reviews}` flags and renders `unknown` cells instead of erroring when files are absent.
- **No flow-engine changes:** router branch pruning is done with the existing session primitives (`markNodeSkipped`, `markNodeComplete`); the engine already treats `skipped` as satisfying downstream `flow` edges.
- **Note (deviation from spec sketch):** the spec suggested client-side chained `skipNode` calls for unchosen routes, but `server/api/flows/nodes/[nodeId]/skip.post.ts` L41-48 guards with `computeSkippable`, which rejects non-optional nodes. Route pruning therefore goes through one new server endpoint (`POST /api/flows/[flowId]/route-choice`) that skips server-side — still session-only, still no engine change.
- **TDD:** vitest harness already exists (`vitest.config.ts` includes `test/unit/**/*.test.ts`). Write the failing test first in every task. Run with `bun --bun vitest run <file>`.
- **Commits:** one commit per task, message ends with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- All new server endpoints call `requireAuth(event)` (read) or `requireWrite(event)` (mutation), matching `server/api/flows/[flowId]/state.get.ts`.

---

### Task 1: Shared extended flow node types (`sub-flow` + `router`)

**Files:**
- Create: `shared/flow-extended.ts`
- Test: `test/unit/flow-extended.test.ts`

**Interfaces:**
- Consumes: `FlowNode`, `FlowEdge` from `@skaile/workspaces/sdk/flow` (type-only).
- Produces:

```ts
export type ExtendedNodeType = "skill" | "group" | "sub-flow" | "router";
export interface RouteDef { condition: string; target: string | null }
export interface ExtendedFlowNode extends Omit<FlowNode, "type"> { type: ExtendedNodeType; ... }
export function isSkillNode(n): boolean
export function isSubFlowNode(n): boolean
export function isRouterNode(n): boolean
export function subFlowChildId(n): string | null
export function routerRoutes(n): RouteDef[]
export function asExtendedNodes(nodes: FlowNode[]): ExtendedFlowNode[]
```

- [ ] **Step 1: Write the failing test.** Create `test/unit/flow-extended.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import {
  asExtendedNodes,
  isRouterNode,
  isSkillNode,
  isSubFlowNode,
  routerRoutes,
  subFlowChildId,
} from "../../shared/flow-extended";

describe("flow-extended type guards", () => {
  const skill = { id: "n1", type: "skill", data: { skill: "concept-brief" } } as any;
  const group = { id: "g1", type: "group", data: { label: "Concept", phase: "conceptualization" } } as any;
  const subFlow = { id: "sf1", type: "sub-flow", data: { flow: "skaileup-slice", label: "Slice loop" } } as any;
  const subFlowViaParams = { id: "sf2", type: "sub-flow", data: { parameters: { flow: "skaileup-slice-impl" } } } as any;
  const router = {
    id: "r1",
    type: "router",
    data: {
      label: "Pick renderer",
      routes: [
        { condition: "static site", target: "mockup-static" },
        { condition: "skip mockups", target: null },
        { condition: "default", target: "mockup-astro" },
      ],
    },
  } as any;

  it("classifies node types", () => {
    expect(isSkillNode(skill)).toBe(true);
    expect(isSkillNode(group)).toBe(false);
    expect(isSubFlowNode(subFlow)).toBe(true);
    expect(isSubFlowNode(skill)).toBe(false);
    expect(isRouterNode(router)).toBe(true);
    expect(isRouterNode(subFlow)).toBe(false);
  });

  it("resolves sub-flow child id from data.flow, then data.parameters.flow", () => {
    expect(subFlowChildId(subFlow)).toBe("skaileup-slice");
    expect(subFlowChildId(subFlowViaParams)).toBe("skaileup-slice-impl");
    expect(subFlowChildId(skill)).toBe(null);
  });

  it("returns routes in authored order, empty for non-routers", () => {
    expect(routerRoutes(router)).toEqual([
      { condition: "static site", target: "mockup-static" },
      { condition: "skip mockups", target: null },
      { condition: "default", target: "mockup-astro" },
    ]);
    expect(routerRoutes(skill)).toEqual([]);
  });

  it("asExtendedNodes is an identity cast (same array reference)", () => {
    const nodes = [skill, group, subFlow, router];
    expect(asExtendedNodes(nodes)).toBe(nodes);
  });
});
```

- [ ] **Step 2: Run it, confirm failure.** `cd /Users/matthias/devBench/SKAILEdev/forge/forge-concept && bun --bun vitest run test/unit/flow-extended.test.ts` — expect `Cannot find module '../../shared/flow-extended'` (or equivalent resolve error).

- [ ] **Step 3: Implement `shared/flow-extended.ts`** (create the `shared/` directory — Nuxt 4 picks it up natively and exposes `#shared`):

```ts
/**
 * Local widening of @skaile/workspaces flow types.
 *
 * The published FlowNode.type union is only "skill" | "group"
 * (dist/factory-assets/connectors/flow/engine/types.d.ts), but real skaileup
 * flows also carry "sub-flow" (delegated loop, e.g. appbuilder-standard →
 * skaileup-slice) and "router" (pick-one route selection) nodes. We cannot
 * patch node_modules, so we widen locally and cast at the load boundary
 * (server/utils/flow-manager.ts). Upstream issue: see plan Task 13.
 *
 * Shared between Nitro server and Vue client — keep this file dependency-free
 * (type-only imports).
 */
import type { FlowNode } from "@skaile/workspaces/sdk/flow";

export type ExtendedNodeType = "skill" | "group" | "sub-flow" | "router";

/** One pick-one route on a router node. `target: null` means "skip this branch". */
export interface RouteDef {
  condition: string;
  target: string | null;
}

export interface ExtendedFlowNode extends Omit<FlowNode, "type"> {
  type: ExtendedNodeType;
  data?: FlowNode["data"] & {
    /** Sub-flow nodes: id of the delegated flow. */
    flow?: string;
    /** Router nodes: ordered pick-one routes ("default" condition = catch-all). */
    routes?: RouteDef[];
  };
}

export function isSkillNode(n: { type?: string }): boolean {
  return n?.type === "skill";
}

export function isSubFlowNode(n: { type?: string }): boolean {
  return n?.type === "sub-flow";
}

export function isRouterNode(n: { type?: string }): boolean {
  return n?.type === "router";
}

/** Child flow id of a sub-flow node: `data.flow`, falling back to `data.parameters.flow`. */
export function subFlowChildId(n: ExtendedFlowNode): string | null {
  if (!isSubFlowNode(n)) return null;
  const direct = n.data?.flow;
  if (typeof direct === "string" && direct) return direct;
  const viaParams = n.data?.parameters?.flow;
  return typeof viaParams === "string" && viaParams ? viaParams : null;
}

/** Ordered routes of a router node; empty array for anything else. */
export function routerRoutes(n: ExtendedFlowNode): RouteDef[] {
  if (!isRouterNode(n)) return [];
  const routes = n.data?.routes;
  if (!Array.isArray(routes)) return [];
  return routes
    .filter((r): r is RouteDef => r && typeof r.condition === "string")
    .map((r) => ({ condition: r.condition, target: r.target ?? null }));
}

/** Zero-cost cast at the flow-load boundary. */
export function asExtendedNodes(nodes: FlowNode[]): ExtendedFlowNode[] {
  return nodes as unknown as ExtendedFlowNode[];
}
```

- [ ] **Step 4: Run tests green.** `bun --bun vitest run test/unit/flow-extended.test.ts` — expect `4 passed`.

- [ ] **Step 5: Commit.**

```
git add shared/flow-extended.ts test/unit/flow-extended.test.ts
git commit -m "feat(flow): local type extension for sub-flow and router nodes

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Phase inference util (shared, unit-tested)

**Files:**
- Create: `shared/flow-phases.ts`
- Test: `test/unit/flow-phases.test.ts`

**Interfaces:**
- Produces:

```ts
export type Phase = "conceptualization" | "implementation" | "review";
export const PHASE_ORDER: Phase[];
export const PHASE_LABELS: Record<Phase, string>;
export function phaseForSkill(skillId: string | undefined): Phase
export function phaseForNode(node: { id: string; data?: { phase?: string; skill?: string } }): Phase
```

- [ ] **Step 1: Write the failing test** `test/unit/flow-phases.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { PHASE_ORDER, phaseForNode, phaseForSkill } from "../../shared/flow-phases";

describe("phaseForSkill", () => {
  it("maps concept-side skill domains to conceptualization", () => {
    for (const s of [
      "concept-brief",
      "concept-grounding-onboard",
      "design-brand-visual",
      "experience-screens",
      "product-spec-features",
      "mockup-walkthrough-astro",
      "mockup-feedback-triage",
    ]) {
      expect(phaseForSkill(s), s).toBe("conceptualization");
    }
  });

  it("maps impl-* to implementation", () => {
    for (const s of ["impl-build-scaffold", "impl-slice-implement", "impl-architecture-techstack"]) {
      expect(phaseForSkill(s), s).toBe("implementation");
    }
  });

  it("maps quality/eval/review/sync skills to review — including impl-quality-*", () => {
    for (const s of [
      "impl-quality-audit",
      "impl-quality-test-e2e",
      "ops-eval-concept",
      "ops-eval-product",
      "ops-review",
      "ops-sync",
    ]) {
      expect(phaseForSkill(s), s).toBe("review");
    }
  });

  it("defaults unknown skills to conceptualization", () => {
    expect(phaseForSkill("something-else")).toBe("conceptualization");
    expect(phaseForSkill(undefined)).toBe("conceptualization");
  });
});

describe("phaseForNode", () => {
  it("prefers a valid explicit data.phase", () => {
    expect(phaseForNode({ id: "n", data: { phase: "review", skill: "concept-brief" } })).toBe("review");
  });

  it("falls back to the skill heuristic on missing/invalid phase", () => {
    expect(phaseForNode({ id: "n", data: { phase: "banana", skill: "impl-build-scaffold" } })).toBe(
      "implementation",
    );
    // Falls back to node.id when data.skill is absent. impl-slice-test hits the
    // impl- prefix bucket — there is deliberately NO "-test" rule (only the
    // "quality" substring / ops-eval* / ops-review / ops-sync checks map to review).
    expect(phaseForNode({ id: "impl-slice-test", data: {} })).toBe("implementation");
  });
});

it("PHASE_ORDER is stable", () => {
  expect(PHASE_ORDER).toEqual(["conceptualization", "implementation", "review"]);
});
```

- [ ] **Step 2: Run, confirm module-not-found failure.** `bun --bun vitest run test/unit/flow-phases.test.ts`

- [ ] **Step 3: Implement `shared/flow-phases.ts`:**

```ts
/**
 * Phase lanes for flow rendering. Skaileup flows are expected to emit group
 * nodes with data.phase ∈ PHASE_ORDER (skaileup 2026-07-05-flow-restructure-plan);
 * for flows that don't, phaseForSkill synthesizes a phase from the skill-name
 * domain prefix (mirrors inferDomainFromFlow in server/utils/flow-manager.ts,
 * but per-node instead of per-flow).
 */
export type Phase = "conceptualization" | "implementation" | "review";

export const PHASE_ORDER: Phase[] = ["conceptualization", "implementation", "review"];

export const PHASE_LABELS: Record<Phase, string> = {
  conceptualization: "Conceptualization",
  implementation: "Implementation",
  review: "Review",
};

const CONCEPT_PREFIXES = ["concept-", "design-", "experience-", "product-spec-", "mockup-"];

export function phaseForSkill(skillId: string | undefined): Phase {
  const s = (skillId ?? "").toLowerCase();
  // Review bucket first: impl-quality-* must not fall into the impl-* bucket.
  if (s.includes("quality")) return "review";
  if (s.startsWith("ops-eval")) return "review";
  if (s === "ops-review" || s === "ops-sync") return "review";
  if (s.startsWith("impl-")) return "implementation";
  if (CONCEPT_PREFIXES.some((p) => s.startsWith(p))) return "conceptualization";
  return "conceptualization";
}

function isPhase(v: unknown): v is Phase {
  return v === "conceptualization" || v === "implementation" || v === "review";
}

/** Explicit valid data.phase wins; otherwise infer from data.skill (or node id). */
export function phaseForNode(node: {
  id: string;
  data?: { phase?: string; skill?: string };
}): Phase {
  if (isPhase(node.data?.phase)) return node.data.phase;
  return phaseForSkill(node.data?.skill ?? node.id);
}
```

- [ ] **Step 4: Run green, then run the whole unit suite** to catch regressions: `bun --bun vitest run` — expect all existing tests plus the two new files passing.

- [ ] **Step 5: Commit.**

```
git add shared/flow-phases.ts test/unit/flow-phases.test.ts
git commit -m "feat(flow): shared phase inference util for lane rendering

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Pure state synthesis for sub-flow/router nodes

The engine's `computeFlowState` only reports skill nodes (`FlowState.nodes`: "group nodes excluded"). Sub-flow/router node states must be synthesized so the UI can render them. Keep the logic pure and fs-free here; Task 4 wires it into `flow-manager.ts`.

**Files:**
- Create: `server/utils/flow-extended-state.ts`
- Test: `test/unit/flow-extended-state.test.ts`

**Interfaces:**
- Consumes: `FlowDefinition`, `FlowEdge` from `@skaile/workspaces/sdk/flow`; guards from `shared/flow-extended.ts`.
- Produces:

```ts
export interface SyntheticNodeState {
  nodeId: string;
  skillId: string;          // sub-flow: child flow id; router: node id
  label: string;
  status: "not_started" | "available" | "complete" | "skipped";
  optional: boolean;
  canRun: boolean;
  blockers: string[];
  nodeType: "sub-flow" | "router";
  childFlowId: string | null;
  routes: RouteDef[] | null;
}
export function synthesizeExtendedNodeStates(
  flow: FlowDefinition,
  completedIds: ReadonlySet<string>,
  skippedIds: ReadonlySet<string>,
): SyntheticNodeState[]
export function isSubFlowSatisfied(
  childFlow: FlowDefinition | null,
  isSkillComplete: (skillId: string | undefined) => boolean,
): boolean
```

- [ ] **Step 1: Write the failing test** `test/unit/flow-extended-state.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import {
  isSubFlowSatisfied,
  synthesizeExtendedNodeStates,
} from "../../server/utils/flow-extended-state";

const flow = {
  id: "f",
  version: "1.0.0",
  name: "f",
  nodes: [
    { id: "a", type: "skill", data: { skill: "concept-brief" } },
    { id: "sf", type: "sub-flow", data: { flow: "skaileup-slice", label: "Slice loop" } },
    {
      id: "r",
      type: "router",
      data: { label: "Renderer", routes: [{ condition: "default", target: "a" }] },
    },
    { id: "g", type: "group", data: { label: "G" } },
  ],
  edges: [
    { id: "e1", source: "a", target: "sf", type: "flow" },
    { id: "e2", source: "a", target: "r", type: "flow" },
  ],
} as any;

describe("synthesizeExtendedNodeStates", () => {
  it("emits one state per sub-flow/router node, none for skill/group", () => {
    const states = synthesizeExtendedNodeStates(flow, new Set(), new Set());
    expect(states.map((s) => s.nodeId).sort()).toEqual(["r", "sf"]);
  });

  it("blocks on incomplete incoming flow edges", () => {
    const [r, sf] = ["r", "sf"].map(
      (id) => synthesizeExtendedNodeStates(flow, new Set(), new Set()).find((s) => s.nodeId === id)!,
    );
    expect(sf.status).toBe("not_started");
    expect(sf.canRun).toBe(false);
    expect(sf.blockers).toEqual(["a"]);
    expect(r.blockers).toEqual(["a"]);
  });

  it("becomes available when deps complete, complete/skipped from the sets", () => {
    const avail = synthesizeExtendedNodeStates(flow, new Set(["a"]), new Set());
    expect(avail.find((s) => s.nodeId === "sf")!.status).toBe("available");
    expect(avail.find((s) => s.nodeId === "sf")!.canRun).toBe(true);

    const done = synthesizeExtendedNodeStates(flow, new Set(["a", "sf"]), new Set(["r"]));
    expect(done.find((s) => s.nodeId === "sf")!.status).toBe("complete");
    expect(done.find((s) => s.nodeId === "r")!.status).toBe("skipped");
  });

  it("carries childFlowId and routes", () => {
    const states = synthesizeExtendedNodeStates(flow, new Set(), new Set());
    expect(states.find((s) => s.nodeId === "sf")!.childFlowId).toBe("skaileup-slice");
    expect(states.find((s) => s.nodeId === "sf")!.routes).toBe(null);
    expect(states.find((s) => s.nodeId === "r")!.routes).toEqual([
      { condition: "default", target: "a" },
    ]);
  });
});

describe("isSubFlowSatisfied", () => {
  const child = {
    id: "c",
    version: "1",
    name: "c",
    nodes: [
      { id: "s1", type: "skill", data: { skill: "impl-slice-implement" } },
      { id: "s2", type: "skill", data: { skill: "impl-slice-commit", optional: true } },
    ],
    edges: [],
  } as any;

  it("true when every non-optional child skill node is complete on disk", () => {
    expect(isSubFlowSatisfied(child, (s) => s === "impl-slice-implement")).toBe(true);
  });

  it("false when a required child skill is incomplete, or child flow missing", () => {
    expect(isSubFlowSatisfied(child, () => false)).toBe(false);
    expect(isSubFlowSatisfied(null, () => true)).toBe(false);
  });
});
```

- [ ] **Step 2: Run, confirm failure.** `bun --bun vitest run test/unit/flow-extended-state.test.ts`

- [ ] **Step 3: Implement `server/utils/flow-extended-state.ts`:**

```ts
/**
 * Pure state synthesis for the node types the flow engine ignores.
 *
 * computeFlowState() only reports type:"skill" nodes, so sub-flow and router
 * nodes would be invisible to the UI. This module derives their state from
 * the same inputs (edges + completed/skipped sets) without touching the fs,
 * so it stays unit-testable. flow-manager.ts merges the result into
 * EnrichedFlowState.
 */
import type { FlowDefinition } from "@skaile/workspaces/sdk/flow";
import type { RouteDef } from "../../shared/flow-extended";
import {
  asExtendedNodes,
  isRouterNode,
  isSkillNode,
  isSubFlowNode,
  routerRoutes,
  subFlowChildId,
} from "../../shared/flow-extended";

export interface SyntheticNodeState {
  nodeId: string;
  skillId: string;
  label: string;
  status: "not_started" | "available" | "complete" | "skipped";
  optional: boolean;
  canRun: boolean;
  blockers: string[];
  nodeType: "sub-flow" | "router";
  childFlowId: string | null;
  routes: RouteDef[] | null;
}

export function synthesizeExtendedNodeStates(
  flow: FlowDefinition,
  completedIds: ReadonlySet<string>,
  skippedIds: ReadonlySet<string>,
): SyntheticNodeState[] {
  const nodes = asExtendedNodes(flow.nodes);
  const satisfied = (id: string) => completedIds.has(id) || skippedIds.has(id);

  return nodes
    .filter((n) => isSubFlowNode(n) || isRouterNode(n))
    .map((n) => {
      // Same hard-dependency rule the engine applies to skill nodes:
      // every incoming `flow` edge source must be complete or skipped.
      const blockers = flow.edges
        .filter((e) => e.target === n.id && e.type === "flow" && !satisfied(e.source))
        .map((e) => e.source);
      const canRun = blockers.length === 0;

      const status = completedIds.has(n.id)
        ? "complete"
        : skippedIds.has(n.id)
          ? "skipped"
          : canRun
            ? "available"
            : "not_started";

      const childFlowId = subFlowChildId(n);
      return {
        nodeId: n.id,
        skillId: childFlowId ?? n.id,
        label: n.data?.label ?? childFlowId ?? n.id,
        status,
        optional: n.data?.optional ?? false,
        canRun: canRun && status === "available",
        blockers,
        nodeType: isSubFlowNode(n) ? ("sub-flow" as const) : ("router" as const),
        childFlowId,
        routes: isRouterNode(n) ? routerRoutes(n) : null,
      };
    });
}

/**
 * A sub-flow node counts as satisfied when its delegated flow's required
 * skill nodes are all file-complete (same disk-derived rule flow-manager
 * applies to this flow's own skill nodes). Missing child flow → not satisfied.
 */
export function isSubFlowSatisfied(
  childFlow: FlowDefinition | null,
  isSkillComplete: (skillId: string | undefined) => boolean,
): boolean {
  if (!childFlow) return false;
  const required = asExtendedNodes(childFlow.nodes).filter(
    (n) => isSkillNode(n) && !(n.data?.optional ?? false),
  );
  if (required.length === 0) return false;
  return required.every((n) => isSkillComplete(n.data?.skill as string | undefined));
}
```

- [ ] **Step 4: Run green.** `bun --bun vitest run test/unit/flow-extended-state.test.ts` — expect `6 passed`.

- [ ] **Step 5: Commit.**

```
git add server/utils/flow-extended-state.ts test/unit/flow-extended-state.test.ts
git commit -m "feat(flow): synthesize state for sub-flow and router nodes

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Wire extended nodes into `flow-manager.ts` enrichment

**Files:**
- Modify: `server/utils/flow-manager.ts` — `EnrichedNodeState` (L62-83), `EnrichedFlowState` (L85-96), group builder (L461-470), enrichment (L438-518).
- Test: extend `test/unit/flow-extended-state.test.ts` only if new pure logic appears (it shouldn't); this task is verified by typecheck + existing integration tests.

**Interfaces:**
- Produces (additions to the existing exported types — client mirror updated in Task 8):

```ts
export interface EnrichedNodeState extends NodeState {
  // ...existing fields unchanged...
  /** "skill" for engine-reported nodes; "sub-flow"/"router" for synthesized ones. */
  nodeType: "skill" | "sub-flow" | "router";
  /** Sub-flow nodes: id of the delegated flow; null otherwise. */
  childFlowId: string | null;
  /** Sub-flow nodes: whether the delegated flow is installed (clickable). */
  childFlowInstalled: boolean;
  /** Router nodes: ordered pick-one routes; null otherwise. */
  routes: RouteDef[] | null;
}
export interface EnrichedFlowState extends FlowState {
  // ...existing fields unchanged...
  /** Persisted router choices: routerNodeId → chosen target node id (null = skip-all). */
  routeChoices: Record<string, string | null>;
}
```

- [ ] **Step 1: Add imports and type fields.** In `server/utils/flow-manager.ts` add below the existing imports (after L26):

```ts
import type { RouteDef } from "../../shared/flow-extended";
import { asExtendedNodes, isRouterNode, isSubFlowNode } from "../../shared/flow-extended";
import { isSubFlowSatisfied, synthesizeExtendedNodeStates } from "./flow-extended-state";
```

Add the four new fields to `EnrichedNodeState` (after `phase: string | null;` at L82) and `routeChoices: Record<string, string | null>;` to `EnrichedFlowState` (after `skippable: string[];` at L95), exactly as in the Interfaces block above.

- [ ] **Step 2: Derive sub-flow completion before `computeFlowState`.** In `getEnrichedFlowState` (L438), after building `completedIds` (L454) and before `computeFlowState` (L457), insert:

```ts
  // Sub-flow nodes complete when their delegated flow's required skills are
  // file-complete — mirrors the disk-derived completion rule above, so a slice
  // loop finished via the CLI unblocks this flow's downstream nodes.
  const extNodes = asExtendedNodes(flow.nodes);
  for (const n of extNodes) {
    if (!isSubFlowNode(n) || completedIds.has(n.id)) continue;
    const childId = n.data?.flow ?? n.data?.parameters?.flow ?? null;
    const child = typeof childId === "string" ? getFlowById(childId) : null;
    if (isSubFlowSatisfied(child, (s) => isNodeFileComplete(s))) completedIds.add(n.id);
  }
```

- [ ] **Step 3: Include sub-flow/router children in groups.** Replace the group builder's child filter (L467-469):

```ts
      childNodeIds: flow.nodes
        .filter(
          (n) =>
            (n.type === "skill" || isSubFlowNode(n) || isRouterNode(n)) && n.parentNode === g.id,
        )
        .map((n) => n.id),
```

- [ ] **Step 4: Enrich engine nodes with the new fields and append synthetic nodes.** In the `enrichedNodes` map callback (L479-510), extend the returned object (after `phase: ...`):

```ts
      nodeType: "skill" as const,
      childFlowId: null,
      childFlowInstalled: false,
      routes: null,
```

Then, after the `enrichedNodes` array is built and before the final `return` (L512), append:

```ts
  // Synthesized states for the node types the engine ignores (sub-flow, router).
  const synthetic = synthesizeExtendedNodeStates(flow, completedIds, skippedIds);
  for (const s of synthetic) {
    enrichedNodes.push({
      ...s,
      status: s.status as EnrichedNodeState["status"],
      fileCount: 0,
      implStatus: null,
      folder: null,
      folders: [],
      parallelGroup: null,
      parentNode: flow.nodes.find((n) => n.id === s.nodeId)?.parentNode ?? null,
      phase: (flow.nodes.find((n) => n.id === s.nodeId)?.data?.phase as string | undefined) ?? null,
      childFlowInstalled: s.childFlowId ? getFlowById(s.childFlowId) !== null : false,
    });
  }
```

And extend the return object:

```ts
  return {
    ...state,
    nodes: enrichedNodes,
    groups,
    skippable,
    routeChoices: (session?.flowId === flowId ? ((session as any).routeChoices ?? {}) : {}) as Record<
      string,
      string | null
    >,
  };
```

- [ ] **Step 5: Verify.** Run `bun --bun vitest run` (all unit + integration green — `tests/integration/skaileup-flows.test.ts` exercises real flows) and `bunx vue-tsc --noEmit 2>&1 | head -30` (no new errors in touched files; pre-existing unrelated errors, if any, are out of scope — record them in the commit body if present).

- [ ] **Step 6: Commit.**

```
git add server/utils/flow-manager.ts
git commit -m "feat(flow): enrich state with sub-flow/router nodes and route choices

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: Auto-layout util with phase lanes

**Files:**
- Create: `app/utils/flow-layout.ts`
- Test: `test/unit/flow-layout.test.ts`

**Interfaces:**
- Consumes: `ExtendedFlowNode`, `Phase`, `phaseForNode`, `PHASE_ORDER`, `PHASE_LABELS` from `shared/`; edges `{ source, target, type }`.
- Produces:

```ts
export interface LaneRect { phase: Phase; label: string; y: number; height: number }
export interface FlowLayout {
  positions: Map<string, { x: number; y: number }>; // absolute, per renderable node
  lanes: LaneRect[];                                 // empty when no lanes apply
  width: number;
}
export function computeFlowLayout(
  nodes: ExtendedFlowNode[],
  edges: Array<{ source: string; target: string; type: string }>,
  opts?: { nodeWidth?: number; nodeHeight?: number; hGap?: number; rowGap?: number; lanePadding?: number },
): FlowLayout
```

Layout rules (document them in the file header): (1) explicit `node.position` always wins (offset by parent group position, matching current FlowGraph behavior); (2) nodes without positions get `x` from longest-path topological depth over `flow`+`parallel` edges, `y` from their lane (group `data.phase` when the node sits in a phased group, else `phaseForNode`), stacking same-depth same-lane nodes into rows; (3) lanes exist only when ≥2 distinct phases occur; lane order = `PHASE_ORDER`.

- [ ] **Step 1: Write the failing test** `test/unit/flow-layout.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { computeFlowLayout } from "../../app/utils/flow-layout";

const N = (id: string, type: string, data: any = {}, extra: any = {}) =>
  ({ id, type, data, ...extra }) as any;

describe("computeFlowLayout", () => {
  it("respects explicit positions (offset by parent group)", () => {
    const nodes = [
      N("g1", "group", { label: "G" }, { position: { x: 100, y: 50 } }),
      N("a", "skill", { skill: "concept-brief" }, { position: { x: 10, y: 20 }, parentNode: "g1" }),
    ];
    const layout = computeFlowLayout(nodes, []);
    expect(layout.positions.get("a")).toEqual({ x: 110, y: 70 });
    expect(layout.lanes).toEqual([]);
  });

  it("assigns x by topological depth for unpositioned nodes", () => {
    const nodes = [
      N("a", "skill", { skill: "concept-brief" }),
      N("b", "skill", { skill: "concept-goals" }),
      N("c", "skill", { skill: "design-brand-visual" }),
    ];
    const edges = [
      { source: "a", target: "b", type: "flow" },
      { source: "b", target: "c", type: "flow" },
    ];
    const layout = computeFlowLayout(nodes, edges, { nodeWidth: 160, hGap: 60 });
    const [xa, xb, xc] = ["a", "b", "c"].map((id) => layout.positions.get(id)!.x);
    expect(xb).toBe(xa + 220);
    expect(xc).toBe(xb + 220);
  });

  it("splits phases into lanes ordered conceptualization→implementation→review", () => {
    const nodes = [
      N("a", "skill", { skill: "concept-brief" }),
      N("b", "skill", { skill: "impl-build-scaffold" }),
      N("c", "skill", { skill: "impl-quality-audit" }),
    ];
    const edges = [
      { source: "a", target: "b", type: "flow" },
      { source: "b", target: "c", type: "flow" },
    ];
    const layout = computeFlowLayout(nodes, edges);
    expect(layout.lanes.map((l) => l.phase)).toEqual([
      "conceptualization",
      "implementation",
      "review",
    ]);
    const ya = layout.positions.get("a")!.y;
    const yb = layout.positions.get("b")!.y;
    const yc = layout.positions.get("c")!.y;
    expect(ya).toBeLessThan(yb);
    expect(yb).toBeLessThan(yc);
  });

  it("uses group data.phase for member nodes over the skill heuristic", () => {
    const nodes = [
      N("g1", "group", { label: "Build", phase: "implementation" }),
      // concept-named skill inside an implementation-phased group → implementation lane
      N("a", "skill", { skill: "concept-brief" }, { parentNode: "g1" }),
      N("b", "skill", { skill: "impl-quality-audit" }),
    ];
    const layout = computeFlowLayout(nodes, []);
    expect(layout.lanes.map((l) => l.phase)).toEqual(["implementation", "review"]);
    const implLane = layout.lanes.find((l) => l.phase === "implementation")!;
    const ya = layout.positions.get("a")!.y;
    expect(ya).toBeGreaterThanOrEqual(implLane.y);
    expect(ya).toBeLessThan(implLane.y + implLane.height);
  });

  it("stacks same-depth same-lane nodes into rows without overlap", () => {
    const nodes = [
      N("a", "skill", { skill: "concept-brief" }),
      N("b", "skill", { skill: "concept-goals" }),
    ];
    const layout = computeFlowLayout(nodes, []); // both depth 0, same lane
    const pa = layout.positions.get("a")!;
    const pb = layout.positions.get("b")!;
    expect(pa.x).toBe(pb.x);
    expect(pa.y).not.toBe(pb.y);
  });
});
```

- [ ] **Step 2: Run, confirm failure.** `bun --bun vitest run test/unit/flow-layout.test.ts`

- [ ] **Step 3: Implement `app/utils/flow-layout.ts`:**

```ts
/**
 * Deterministic auto-layout for FlowGraph with phase lanes.
 *
 * Rules:
 *  1. Explicit node.position always wins (offset by parent group position —
 *     same semantics FlowGraph.vue applied before this util existed).
 *  2. Unpositioned nodes: x = longest-path topo depth over flow+parallel
 *     edges; y = lane (group data.phase when in a phased group, else
 *     phaseForNode), stacking same-depth same-lane nodes into rows.
 *  3. Lanes render only when ≥2 distinct phases occur; order = PHASE_ORDER.
 */
import type { ExtendedFlowNode } from "../../shared/flow-extended";
import { isRouterNode, isSkillNode, isSubFlowNode } from "../../shared/flow-extended";
import type { Phase } from "../../shared/flow-phases";
import { PHASE_LABELS, PHASE_ORDER, phaseForNode } from "../../shared/flow-phases";

export interface LaneRect {
  phase: Phase;
  label: string;
  y: number;
  height: number;
}

export interface FlowLayout {
  positions: Map<string, { x: number; y: number }>;
  lanes: LaneRect[];
  width: number;
}

interface LayoutOpts {
  nodeWidth: number;
  nodeHeight: number;
  hGap: number;
  rowGap: number;
  lanePadding: number;
}

const DEFAULTS: LayoutOpts = { nodeWidth: 160, nodeHeight: 44, hGap: 60, rowGap: 16, lanePadding: 36 };

const renderable = (n: ExtendedFlowNode) => isSkillNode(n) || isSubFlowNode(n) || isRouterNode(n);

export function computeFlowLayout(
  nodes: ExtendedFlowNode[],
  edges: Array<{ source: string; target: string; type: string }>,
  opts?: Partial<LayoutOpts>,
): FlowLayout {
  const o = { ...DEFAULTS, ...opts };
  const positions = new Map<string, { x: number; y: number }>();

  // ── Pass 1: explicit positions (groups first so children can offset) ──
  const groupPos = new Map<string, { x: number; y: number }>();
  for (const n of nodes) {
    if (n.type === "group" && n.position) groupPos.set(n.id, { ...n.position });
  }
  const unpositioned: ExtendedFlowNode[] = [];
  for (const n of nodes.filter(renderable)) {
    if (n.position) {
      const parent = n.parentNode ? groupPos.get(n.parentNode) : null;
      positions.set(n.id, { x: (parent?.x ?? 0) + n.position.x, y: (parent?.y ?? 0) + n.position.y });
    } else {
      unpositioned.push(n);
    }
  }
  if (unpositioned.length === 0) return { positions, lanes: [], width: 0 };

  // ── Pass 2: longest-path depth over flow+parallel edges (Kahn) ──
  const ids = new Set(unpositioned.map((n) => n.id));
  const depEdges = edges.filter(
    (e) => (e.type === "flow" || e.type === "parallel") && ids.has(e.source) && ids.has(e.target),
  );
  const indeg = new Map<string, number>([...ids].map((id) => [id, 0]));
  for (const e of depEdges) indeg.set(e.target, (indeg.get(e.target) ?? 0) + 1);
  const depth = new Map<string, number>([...ids].map((id) => [id, 0]));
  const queue = [...ids].filter((id) => indeg.get(id) === 0);
  while (queue.length) {
    const id = queue.shift()!;
    for (const e of depEdges.filter((e) => e.source === id)) {
      depth.set(e.target, Math.max(depth.get(e.target)!, depth.get(id)! + 1));
      indeg.set(e.target, indeg.get(e.target)! - 1);
      if (indeg.get(e.target) === 0) queue.push(e.target);
    }
  }

  // ── Pass 3: lane per node (group phase wins over skill heuristic) ──
  const groupPhase = new Map<string, Phase>();
  for (const g of nodes) {
    if (g.type !== "group") continue;
    const p = g.data?.phase;
    if (p === "conceptualization" || p === "implementation" || p === "review")
      groupPhase.set(g.id, p);
  }
  const nodePhase = (n: ExtendedFlowNode): Phase =>
    (n.parentNode && groupPhase.get(n.parentNode)) || phaseForNode(n);

  const phasesPresent = PHASE_ORDER.filter((p) => unpositioned.some((n) => nodePhase(n) === p));
  const laneOf = new Map<Phase, number>(phasesPresent.map((p, i) => [p, i]));

  // ── Pass 4: rows within (lane, depth) cells, then lane heights ──
  const rowIndex = new Map<string, number>();
  const cellCount = new Map<string, number>(); // `${lane}:${depth}` → count
  const laneRows = new Map<number, number>(); // lane → max rows
  for (const n of unpositioned) {
    const lane = laneOf.get(nodePhase(n))!;
    const key = `${lane}:${depth.get(n.id)}`;
    const row = cellCount.get(key) ?? 0;
    cellCount.set(key, row + 1);
    rowIndex.set(n.id, row);
    laneRows.set(lane, Math.max(laneRows.get(lane) ?? 1, row + 1));
  }
  const laneHeight = (lane: number) =>
    o.lanePadding * 2 + (laneRows.get(lane) ?? 1) * (o.nodeHeight + o.rowGap) - o.rowGap;
  const laneY: number[] = [];
  let yCursor = 0;
  for (let i = 0; i < phasesPresent.length; i++) {
    laneY.push(yCursor);
    yCursor += laneHeight(i) + 24;
  }

  const maxDepth = Math.max(...[...depth.values()], 0);
  for (const n of unpositioned) {
    const lane = laneOf.get(nodePhase(n))!;
    positions.set(n.id, {
      x: 40 + depth.get(n.id)! * (o.nodeWidth + o.hGap),
      y: laneY[lane]! + o.lanePadding + rowIndex.get(n.id)! * (o.nodeHeight + o.rowGap),
    });
  }

  const width = 40 + (maxDepth + 1) * (o.nodeWidth + o.hGap);
  const lanes: LaneRect[] =
    phasesPresent.length >= 2
      ? phasesPresent.map((p, i) => ({
          phase: p,
          label: PHASE_LABELS[p],
          y: laneY[i]!,
          height: laneHeight(i),
        }))
      : [];
  return { positions, lanes, width };
}
```

- [ ] **Step 4: Run green.** `bun --bun vitest run test/unit/flow-layout.test.ts` — expect `5 passed`.

- [ ] **Step 5: Commit.**

```
git add app/utils/flow-layout.ts test/unit/flow-layout.test.ts
git commit -m "feat(flow): auto-layout util with phase lanes

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: FlowGraph.vue — lanes, sub-flow chips, router diamonds

**Files:**
- Modify: `app/components/FlowGraph.vue` (template L1-111; script: local `FlowNode` interface L114-127, `nodePositions` L164-186, `skillNodeRects` L208-225, `edgePaths` L228-245, `bounds` L248-270).
- Test: covered by Task 5 unit tests (layout) + manual verification step; SVG rendering itself is verified visually and by existing e2e smoke (`tests/e2e/concepts-index.spec.ts` still passing).

**Interfaces:**
- Props unchanged, but local `FlowNode`/`FlowEdge` types are replaced by `ExtendedFlowNode` + a `condition?: string` edge field.
- New emits: `subFlowClick: [childFlowId: string]`, `routerClick: [nodeId: string]` (alongside existing `nodeClick`).

- [ ] **Step 1: Swap local types for shared ones.** In the `<script setup>` block delete the local `FlowNode` interface (L114-127) and change imports/props:

```ts
import type { ExtendedFlowNode } from "#shared/flow-extended";
import { isRouterNode, isSubFlowNode, subFlowChildId } from "#shared/flow-extended";
import { computeFlowLayout } from "~/utils/flow-layout";

interface FlowEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  /** Router route edges: the route condition (rendered as an edge label). */
  condition?: string;
}

const props = defineProps<{
  nodes: ExtendedFlowNode[];
  edges: FlowEdge[];
  nodeStates: NodeStatus[];
  activeNodeId?: string | null;
  containerHeight?: number;
}>();

const emit = defineEmits<{
  nodeClick: [nodeId: string];
  subFlowClick: [childFlowId: string];
  routerClick: [nodeId: string];
}>();
```

(`NodeStatus` local interface stays as-is.)

- [ ] **Step 2: Replace `nodePositions` with the layout util.** Delete the two-pass position computed (L164-186) and replace with:

```ts
const layout = computed(() => computeFlowLayout(props.nodes, props.edges));
const nodePositions = computed(() => layout.value.positions);
const lanes = computed(() => layout.value.lanes);
```

`groupRects` (L189-205): keep, but only render explicit-position groups when lanes are empty — change its filter to `.filter((n) => n.type === "group" && n.position && lanes.value.length === 0)`.

- [ ] **Step 3: Split renderable nodes three ways.** Replace `skillNodeRects` (L208-225):

```ts
function stateFor(id: string) {
  return props.nodeStates.find((s) => s.nodeId === id);
}
function baseRect(node: ExtendedFlowNode) {
  const pos = nodePositions.value.get(node.id);
  const state = stateFor(node.id);
  return {
    id: node.id,
    label: node.data?.label ?? node.id,
    x: pos?.x ?? 0,
    y: pos?.y ?? 0,
    status: props.activeNodeId === node.id ? "running" : (state?.status ?? "not_started"),
    canRun: state?.canRun ?? false,
    optional: node.data?.optional ?? false,
  };
}
const skillNodeRects = computed(() =>
  props.nodes
    .filter((n) => n.type === "skill")
    .map((n) => ({ ...baseRect(n), skillId: n.data?.skill ?? n.id })),
);
const subFlowRects = computed(() =>
  props.nodes
    .filter((n) => isSubFlowNode(n))
    .map((n) => ({ ...baseRect(n), childFlowId: subFlowChildId(n) })),
);
const routerRects = computed(() =>
  props.nodes.filter((n) => isRouterNode(n)).map((n) => baseRect(n)),
);
```

Update `bounds` (L261) to iterate `[...skillNodeRects.value, ...subFlowRects.value, ...routerRects.value]` instead of only `skillNodeRects.value`, and extend with `maxX = Math.max(maxX, bounds-from-lanes-width)` using `layout.value.width`. Include lane rects in bounds: for each lane, `minY = Math.min(minY, lane.y)`, `maxY = Math.max(maxY, lane.y + lane.height)`.

- [ ] **Step 4: Edge labels for route conditions.** In `edgePaths` (L228-245) also return `condition: edge.condition` and midpoint coordinates:

```ts
    const mx = (x1 + x2) / 2;
    const my = (y1 + y2) / 2;
    return { id: edge.id, path, type: edge.type, condition: edge.condition, mx, my };
```

- [ ] **Step 5: Template additions.** Inside the `<svg>`: lanes *before* group backgrounds; sub-flow chips and router diamonds after skill nodes; edge condition labels after edges:

```html
      <!-- Phase lanes (auto-layout only) -->
      <template v-for="lane in lanes" :key="'lane-' + lane.phase">
        <rect
          :x="-20" :y="lane.y" :width="Math.max(svgWidth, layout.width) + 40" :height="lane.height"
          class="fill-gray-100/50 dark:fill-gray-800/30 stroke-gray-200 dark:stroke-gray-700"
          stroke-width="1" rx="8"
        />
        <text
          :x="-8" :y="lane.y + 16"
          class="fill-gray-400 dark:fill-gray-500 text-[11px] font-bold uppercase"
          style="font-family: system-ui, sans-serif"
        >{{ lane.label }}</text>
      </template>

      <!-- Route condition labels -->
      <text
        v-for="edge in edgePaths.filter((e) => e.condition)"
        :key="'cond-' + edge.id"
        :x="edge.mx" :y="edge.my - 4" text-anchor="middle"
        class="fill-gray-400 dark:fill-gray-500 text-[9px] italic"
        style="font-family: system-ui, sans-serif"
      >{{ edge.condition }}</text>

      <!-- Sub-flow nodes: double-border chip, click selects the child flow -->
      <g
        v-for="node in subFlowRects" :key="node.id"
        :transform="`translate(${node.x}, ${node.y})`" class="cursor-pointer"
        @click="node.childFlowId ? emit('subFlowClick', node.childFlowId) : emit('nodeClick', node.id)"
      >
        <rect :width="nodeWidth" :height="nodeHeight" :rx="6" :class="nodeRectClass(node)" stroke-width="1.5" />
        <rect :x="3" :y="3" :width="nodeWidth - 6" :height="nodeHeight - 6" :rx="4"
          fill="none" class="stroke-gray-300 dark:stroke-gray-600" stroke-width="1" />
        <circle :cx="nodeWidth - 12" :cy="12" r="5" :class="statusDotClass(node.status)" />
        <text :x="10" :y="22" :class="nodeLabelClass(node)" class="text-[12px]"
          style="font-family: system-ui, sans-serif">{{ truncate(node.label, 20) }}</text>
        <text :x="10" :y="36" class="fill-primary-400 text-[9px] underline"
          style="font-family: system-ui, sans-serif">↳ {{ node.childFlowId ?? "flow?" }}</text>
      </g>

      <!-- Router nodes: diamond, click opens route chooser -->
      <g
        v-for="node in routerRects" :key="node.id"
        :transform="`translate(${node.x}, ${node.y})`" class="cursor-pointer"
        @click="emit('routerClick', node.id)"
      >
        <polygon
          :points="`${nodeWidth / 2},0 ${nodeWidth},${nodeHeight / 2} ${nodeWidth / 2},${nodeHeight} 0,${nodeHeight / 2}`"
          :class="nodeRectClass(node)" stroke-width="1.5"
        />
        <text :x="nodeWidth / 2" :y="nodeHeight / 2 + 4" text-anchor="middle"
          :class="nodeLabelClass(node)" class="text-[11px]"
          style="font-family: system-ui, sans-serif">{{ truncate(node.label, 16) }}</text>
      </g>
```

Note: `defineEmits` now assigned to `emit` (Step 1), so update the existing skill-node `@click="$emit('nodeClick', node.id)"` to `@click="emit('nodeClick', node.id)"` for consistency (both work; pick one).

- [ ] **Step 6: Verify.** `bun --bun vitest run` green; `bunx vue-tsc --noEmit 2>&1 | grep FlowGraph` — no errors. Manual: `bun run dev`, open `/concepts`, switch to Graph view with an appbuilder-standard flow installed → sub-flow chip renders with double border; flows without positions get lane layout.

- [ ] **Step 7: Commit.**

```
git add app/components/FlowGraph.vue
git commit -m "feat(graph): render phase lanes, sub-flow chips, router diamonds

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: Route choice — session persistence + server endpoint

**Files:**
- Create: `server/utils/flow-route-choice.ts`, `server/api/flows/[flowId]/route-choice.post.ts`
- Modify: `server/utils/flow-session.ts` (add `routeChoices` to `SessionState` L47-51; add `setRouteChoice` beside `markNodeSkipped` L138)
- Test: `test/unit/flow-route-choice.test.ts`

**Interfaces:**
- Produces:

```ts
// flow-session.ts
export interface SessionState extends BaseSessionState {
  completed: string[];
  skipped: string[];
  outputs?: Record<string, FlowNodeOutput>;
  /** Router pick-one choices: routerNodeId → chosen target node id (null = all branches skipped). */
  routeChoices?: Record<string, string | null>;
}
export async function setRouteChoice(flowId: string, routerNodeId: string, target: string | null): Promise<SessionState>

// flow-route-choice.ts
export function computeUnchosenSkips(flow: FlowDefinition, routerNodeId: string, chosenTarget: string | null): string[]

// API
// POST /api/flows/:flowId/route-choice  body { routerNodeId: string; targetNodeId: string | null }
// → { success: true; routerNodeId: string; chosen: string | null; skipped: string[] }
```

- [ ] **Step 1: Write the failing test** `test/unit/flow-route-choice.test.ts` (pure function only — the endpoint is thin):

```ts
import { describe, expect, it } from "vitest";
import { computeUnchosenSkips } from "../../server/utils/flow-route-choice";

// r routes to a | b | null-skip; both branches converge on join j.
const flow = {
  id: "f",
  version: "1",
  name: "f",
  nodes: [
    {
      id: "r",
      type: "router",
      data: {
        routes: [
          { condition: "path A", target: "a" },
          { condition: "path B", target: "b" },
          { condition: "skip", target: null },
        ],
      },
    },
    { id: "a", type: "skill", data: { skill: "sa" } },
    { id: "a2", type: "skill", data: { skill: "sa2" } },
    { id: "b", type: "skill", data: { skill: "sb" } },
    { id: "j", type: "skill", data: { skill: "sj" } },
  ],
  edges: [
    { id: "e1", source: "r", target: "a", type: "flow" },
    { id: "e2", source: "r", target: "b", type: "flow" },
    { id: "e3", source: "a", target: "a2", type: "flow" },
    { id: "e4", source: "a2", target: "j", type: "flow" },
    { id: "e5", source: "b", target: "j", type: "flow" },
  ],
} as any;

describe("computeUnchosenSkips", () => {
  it("skips the unchosen branch chain but never the join node", () => {
    expect(computeUnchosenSkips(flow, "r", "a").sort()).toEqual(["b"]);
    expect(computeUnchosenSkips(flow, "r", "b").sort()).toEqual(["a", "a2"]);
  });

  it("null choice (skip route) skips every branch, still not the join", () => {
    expect(computeUnchosenSkips(flow, "r", null).sort()).toEqual(["a", "a2", "b"]);
  });

  it("unknown router yields no skips", () => {
    expect(computeUnchosenSkips(flow, "nope", "a")).toEqual([]);
  });
});
```

- [ ] **Step 2: Run, confirm failure**, then implement `server/utils/flow-route-choice.ts`:

```ts
/**
 * Pick-one router branch pruning — session-level, no engine change.
 *
 * Choosing route R on a router marks every *other* route's exclusive
 * downstream chain as skipped (engine semantics: skipped satisfies `flow`
 * edges, so the join node after the branches unblocks). Nodes reachable from
 * the chosen branch (join nodes and beyond) are never skipped.
 */
import type { FlowDefinition } from "@skaile/workspaces/sdk/flow";
import { asExtendedNodes, isRouterNode, routerRoutes } from "../../shared/flow-extended";

/** All node ids reachable from `start` (exclusive) following outgoing edges of any type. */
function reachableFrom(flow: FlowDefinition, start: string): Set<string> {
  const seen = new Set<string>();
  const queue = [start];
  while (queue.length) {
    const id = queue.shift()!;
    for (const e of flow.edges) {
      if (e.source !== id || seen.has(e.target)) continue;
      seen.add(e.target);
      queue.push(e.target);
    }
  }
  return seen;
}

export function computeUnchosenSkips(
  flow: FlowDefinition,
  routerNodeId: string,
  chosenTarget: string | null,
): string[] {
  const router = asExtendedNodes(flow.nodes).find((n) => n.id === routerNodeId);
  if (!router || !isRouterNode(router)) return [];

  const targets = routerRoutes(router)
    .map((r) => r.target)
    .filter((t): t is string => t !== null);

  const keep = new Set<string>();
  if (chosenTarget) {
    keep.add(chosenTarget);
    for (const id of reachableFrom(flow, chosenTarget)) keep.add(id);
  } else {
    // Skip-all: keep only what is reachable *past* the branches — i.e. nodes
    // reachable from ≥2 distinct branch targets (join nodes and beyond).
    const counts = new Map<string, number>();
    for (const t of targets) {
      for (const id of reachableFrom(flow, t)) counts.set(id, (counts.get(id) ?? 0) + 1);
    }
    for (const [id, c] of counts) if (c >= 2) keep.add(id);
  }

  const skips = new Set<string>();
  for (const t of targets) {
    if (t === chosenTarget) continue;
    if (!keep.has(t)) skips.add(t);
    for (const id of reachableFrom(flow, t)) {
      if (!keep.has(id)) skips.add(id);
    }
  }
  return [...skips];
}
```

  **Caveat to encode in a test if flows use it:** with a single-target router plus skip-all, `counts` never reaches 2, so downstream of that lone branch is fully skipped — that is the intended "skip this whole optional segment" semantics.

- [ ] **Step 3: Run green.** `bun --bun vitest run test/unit/flow-route-choice.test.ts` — expect `3 passed`.

- [ ] **Step 4: Session field + helper.** In `server/utils/flow-session.ts` add `routeChoices?: Record<string, string | null>;` to `SessionState` (after `outputs?` L50) and append after `markNodeSkipped` (L148):

```ts
/** Persist a router pick-one choice in the current flow session. */
export async function setRouteChoice(
  flowId: string,
  routerNodeId: string,
  target: string | null,
): Promise<SessionState> {
  const projectDir = getProjectRoot();
  const session = await getOrCreateFlowSession(flowId);
  if (!session.routeChoices) session.routeChoices = {};
  session.routeChoices[routerNodeId] = target;
  const updated = touchSession(session) as SessionState;
  await saveSession(projectDir, updated);
  return updated;
}
```

- [ ] **Step 5: Endpoint** `server/api/flows/[flowId]/route-choice.post.ts` (Nitro auto-imports `getFlowById`, `markNodeComplete`, `markNodeSkipped`, `setRouteChoice`, `requireWrite` from `server/utils/`):

```ts
import { asExtendedNodes, isRouterNode, routerRoutes } from "../../../../shared/flow-extended";
import { computeUnchosenSkips } from "../../../utils/flow-route-choice";

/**
 * POST /api/flows/:flowId/route-choice — resolve a pick-one router node.
 *
 * Body: { routerNodeId: string; targetNodeId: string | null }
 * Persists the choice in the flow session, marks the router complete, and
 * marks every unchosen branch chain skipped (engine treats skipped as
 * satisfied, so downstream join nodes unblock). No flow-engine change.
 */
export default defineEventHandler(async (event) => {
  await requireWrite(event);

  const flowId = getRouterParam(event, "flowId");
  if (!flowId) throw createError({ statusCode: 400, statusMessage: "Missing flowId parameter" });

  const body = await readBody(event);
  if (!body?.routerNodeId) {
    throw createError({ statusCode: 400, statusMessage: "Missing required field: routerNodeId" });
  }
  const routerNodeId: string = body.routerNodeId;
  const targetNodeId: string | null = body.targetNodeId ?? null;

  const flow = getFlowById(flowId);
  if (!flow) throw createError({ statusCode: 404, statusMessage: `Flow "${flowId}" not found` });

  const router = asExtendedNodes(flow.nodes).find((n) => n.id === routerNodeId);
  if (!router || !isRouterNode(router)) {
    throw createError({
      statusCode: 404,
      statusMessage: `Router node "${routerNodeId}" not found in flow "${flowId}"`,
    });
  }
  const validTargets = routerRoutes(router).map((r) => r.target);
  if (!validTargets.includes(targetNodeId)) {
    throw createError({
      statusCode: 400,
      statusMessage: `"${targetNodeId}" is not a route target of "${routerNodeId}"`,
    });
  }

  await setRouteChoice(flowId, routerNodeId, targetNodeId);
  await markNodeComplete(flowId, routerNodeId, {
    label: (router.data?.label as string) ?? routerNodeId,
    status: "complete",
    summary: `Route chosen: ${targetNodeId ?? "skip all branches"}`,
    filesChanged: [],
  });

  const skipped = computeUnchosenSkips(flow, routerNodeId, targetNodeId);
  for (const nodeId of skipped) {
    await markNodeSkipped(flowId, nodeId);
  }

  return { success: true, routerNodeId, chosen: targetNodeId, skipped };
});
```

- [ ] **Step 6: Verify + commit.** `bun --bun vitest run` green, `bunx vue-tsc --noEmit` clean for touched files.

```
git add server/utils/flow-route-choice.ts server/utils/flow-session.ts "server/api/flows/[flowId]/route-choice.post.ts" test/unit/flow-route-choice.test.ts
git commit -m "feat(flow): route-choice endpoint with session-persisted pick-one routing

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: Client — useFlowState route/extended-node support

**Files:**
- Modify: `app/composables/useFlowState.ts` (types L37-73; `skillNodes` L153-155; actions block L244+; exports L414-455)

**Interfaces:**
- Produces (additions):

```ts
interface EnrichedNodeState {
  // ...existing...
  nodeType?: "skill" | "sub-flow" | "router";
  childFlowId?: string | null;
  childFlowInstalled?: boolean;
  routes?: Array<{ condition: string; target: string | null }> | null;
}
interface EnrichedFlowState { /* ...existing... */ routeChoices?: Record<string, string | null> }
// returned from the composable:
routerNodes: ComputedRef<EnrichedNodeState[]>
routeChoices: ComputedRef<Record<string, string | null>>
chooseRoute(routerNodeId: string, targetNodeId: string | null): Promise<boolean>
```

- [ ] **Step 1: Extend the local types.** Add the four optional fields to `EnrichedNodeState` (after `phase: string | null;` L55) and `routeChoices?: Record<string, string | null>;` to `EnrichedFlowState` (after `skippable: string[];` L72) exactly as in the Interfaces block. (Optional fields keep old server responses valid during rolling deploys.)

- [ ] **Step 2: Fix `skillNodes` and add router/sub-flow views.** Replace L152-155:

```ts
  // Only executable skill nodes (synthesized sub-flow/router states excluded;
  // nodeType is absent on older server responses → treat as skill)
  const skillNodes = computed(() =>
    nodes.value.filter((n: EnrichedNodeState) => (n.nodeType ?? "skill") === "skill"),
  );
  const routerNodes = computed(() =>
    nodes.value.filter((n: EnrichedNodeState) => n.nodeType === "router"),
  );
  const routeChoices = computed<Record<string, string | null>>(
    () => flowState.value?.routeChoices ?? {},
  );
```

- [ ] **Step 3: Add the `chooseRoute` action** after `skipNode` (L315):

```ts
  /** Resolve a pick-one router node: persist choice, server skips unchosen branches. */
  async function chooseRoute(routerNodeId: string, targetNodeId: string | null): Promise<boolean> {
    if (!activeFlowId.value) return false;
    try {
      await $fetch(`/api/flows/${activeFlowId.value}/route-choice`, {
        method: "POST",
        body: { routerNodeId, targetNodeId },
      });
      await refreshState();
      return true;
    } catch (e: any) {
      console.error("[flow] Failed to choose route:", e);
      return false;
    }
  }
```

- [ ] **Step 4: Export** `routerNodes`, `routeChoices`, `chooseRoute` from the composable's return object (place beside `skipNode`).

- [ ] **Step 5: Verify + commit.** `bunx vue-tsc --noEmit 2>&1 | grep useFlowState` — clean; `bun --bun vitest run` green.

```
git add app/composables/useFlowState.ts
git commit -m "feat(flow): client route-choice action and extended node views

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 9: Route chooser UI + sub-flow navigation (concepts/index.vue) and sidebar lanes

**Files:**
- Modify: `app/pages/concepts/index.vue` (FlowGraph usage L96-104), `app/components/AppSidebar.vue` (grouped section L56-122; script L374+)

**Interfaces:**
- Consumes: `chooseRoute`, `routeChoices`, `selectFlow` from `useFlowState`; `phaseForNode`, `PHASE_ORDER`, `PHASE_LABELS` from `#shared/flow-phases`.

- [ ] **Step 1: Graph event wiring + route chooser modal.** In `app/pages/concepts/index.vue`, extend the FlowGraph usage (L96-104):

```html
          <FlowGraph
            v-if="viewMode === 'graph' && flowDefinition"
            :nodes="flowDefinition.nodes"
            :edges="flowDefinition.edges"
            :node-states="flow.nodes.value"
            :active-node-id="flow.activeSkillNodeId.value"
            :container-height="480"
            @node-click="onGraphNodeClick"
            @sub-flow-click="onSubFlowClick"
            @router-click="onRouterClick"
          />

          <!-- Route chooser: pick-one router resolution -->
          <UModal v-model:open="routeModalOpen" :title="routeModalRouter?.label ?? 'Choose route'">
            <template #body>
              <div class="space-y-2">
                <p class="text-sm text-gray-500">
                  Pick one route. The other branches will be marked skipped.
                </p>
                <UButton
                  v-for="route in routeModalRouter?.routes ?? []"
                  :key="route.condition"
                  block
                  :color="route.target === chosenFor(routeModalRouter?.nodeId) ? 'primary' : 'neutral'"
                  :variant="route.target === chosenFor(routeModalRouter?.nodeId) ? 'solid' : 'soft'"
                  :icon="route.target === null ? 'i-heroicons-forward' : 'i-heroicons-arrow-right-circle'"
                  :loading="routeChoosing"
                  @click="onChooseRoute(route.target)"
                >
                  {{ route.condition }}
                  <span v-if="route.target === null" class="text-xs opacity-70">(skip)</span>
                </UButton>
              </div>
            </template>
          </UModal>
```

And in the page's `<script setup>` add:

```ts
const routeModalOpen = ref(false);
const routeModalRouterId = ref<string | null>(null);
const routeChoosing = ref(false);

const routeModalRouter = computed(
  () => flow.routerNodes.value.find((n) => n.nodeId === routeModalRouterId.value) ?? null,
);

function chosenFor(routerNodeId: string | undefined): string | null | undefined {
  return routerNodeId ? flow.routeChoices.value[routerNodeId] : undefined;
}

function onRouterClick(nodeId: string) {
  routeModalRouterId.value = nodeId;
  routeModalOpen.value = true;
}

async function onChooseRoute(target: string | null) {
  if (!routeModalRouterId.value) return;
  routeChoosing.value = true;
  const ok = await flow.chooseRoute(routeModalRouterId.value, target);
  routeChoosing.value = false;
  if (ok) routeModalOpen.value = false;
}

function onSubFlowClick(childFlowId: string) {
  flow.selectFlow(childFlowId);
}
```

- [ ] **Step 2: Sidebar lane headers.** In `app/components/AppSidebar.vue` script, add:

```ts
import { PHASE_LABELS, PHASE_ORDER, phaseForNode, type Phase } from "#shared/flow-phases";

/** Lane for a group: its data.phase when valid, else majority phase of its child nodes. */
function groupPhase(group: FlowGroup): Phase {
  if (PHASE_ORDER.includes(group.phase as Phase)) return group.phase as Phase;
  const counts = new Map<Phase, number>();
  for (const n of getGroupNodes(group)) {
    const p = phaseForNode({ id: n.nodeId, data: { phase: n.phase ?? undefined, skill: n.skillId } });
    counts.set(p, (counts.get(p) ?? 0) + 1);
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] ?? "conceptualization";
}

/** Ordered lanes with their groups and done/total across required nodes. */
const lanes = computed(() => {
  const byPhase = new Map<Phase, FlowGroup[]>();
  for (const g of flow.groups.value) {
    const p = groupPhase(g);
    if (!byPhase.has(p)) byPhase.set(p, []);
    byPhase.get(p)!.push(g);
  }
  return PHASE_ORDER.filter((p) => byPhase.has(p)).map((phase) => {
    const groups = byPhase.get(phase)!;
    const nodes = groups.flatMap((g) => getGroupNodes(g)).filter((n) => !n.optional);
    return {
      phase,
      label: PHASE_LABELS[phase],
      groups,
      done: nodes.filter((n) => n.status === "complete").length,
      total: nodes.length,
    };
  });
});
```

- [ ] **Step 3: Render lane headers.** Replace the grouped template's outer `v-for` (L56-61): wrap groups in lanes — only when >1 lane exists, otherwise render exactly as today:

```html
      <template v-if="flow.hasFlow.value && flow.groups.value.length > 0">
        <template v-for="lane in lanes" :key="lane.phase">
          <!-- Lane header (hidden when the flow is single-phase) -->
          <div
            v-if="lanes.length > 1"
            class="flex items-center justify-between px-4 py-1.5 bg-gray-100/80 dark:bg-gray-800/60 border-b border-gray-200/60 dark:border-gray-800/60"
          >
            <span class="text-[10px] font-bold uppercase tracking-widest text-gray-500 dark:text-gray-400">
              {{ lane.label }}
            </span>
            <span class="text-[10px] text-gray-400 tabular-nums">{{ lane.done }}/{{ lane.total }}</span>
          </div>
          <div
            v-for="group in lane.groups"
            :key="group.id"
            class="border-b border-gray-200/60 dark:border-gray-800/60"
          >
            <!-- (existing group header button + group content block, unchanged, moved inside) -->
          </div>
        </template>
      </template>
```

  Move the existing group header `<button>` (L63-88) and group content `<div v-if="isGroupOpen(...)">` (L91-120) inside unchanged.

- [ ] **Step 4: Verify.** `bun --bun vitest run` green; `bunx vue-tsc --noEmit` clean for touched files. Manual: dev server, sidebar shows lane headers with per-lane counts for a phased flow, unchanged rendering for single-phase flows; clicking a router diamond opens the chooser; choosing a route refreshes state and unchosen branch nodes disappear from group lists (they're filtered as `skipped` in `getGroupNodes`).

- [ ] **Step 5: Commit.**

```
git add app/pages/concepts/index.vue app/components/AppSidebar.vue
git commit -m "feat(ui): route chooser modal, sub-flow navigation, sidebar phase lanes

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 10: Coverage indexer (`server/utils/review-coverage.ts` + endpoint)

**Files:**
- Create: `server/utils/review-coverage.ts`, `server/api/review/coverage.get.ts`
- Test: `test/unit/review-coverage.test.ts` (fixture tree in a temp dir)

**Interfaces:**
- Consumes: `getProjectRoot`, `getConceptDir` from `server/utils/project.ts`; `scanImplStatus` from `server/utils/concept-status.ts`; `yaml` package.
- Expected artifact shapes (per skaileup `2026-07-05-perfect-review-plan.md`; every part optional):
  - `_implementation/trace.yaml`: `features: { <id>: { specced, sliced, committed, evaluated, documented: bool, code_refs: string[] } }`, `orphans: [{ path, reason }]`
  - `_implementation/acceptance_criteria/**/*.ac.md`: frontmatter `feature: <id>`; body lines `- [PASS] ...` / `- [FAIL] ...` / `- [ ] ...` (pending)
  - `_implementation/review/<feature>.yaml`: `{ feature, verdict: approved|changes-requested|pending, findings: [{ severity, note }], commits?: string[] }`
- Produces:

```ts
export type CoverageCell = "yes" | "no" | "unknown";
export interface AcCriterion { text: string; status: "pass" | "fail" | "pending"; file: string }
export interface ReviewFinding { severity: string; note: string }
export interface FeatureCoverage {
  feature: string;
  specced: CoverageCell;
  sliced: CoverageCell;
  committed: CoverageCell;
  tested: { cell: CoverageCell; passed: number; failed: number; pending: number };
  evaluated: CoverageCell;
  documented: CoverageCell;
  codeTraced: CoverageCell;
  verdict: "approved" | "changes-requested" | "pending" | null;
  findings: ReviewFinding[];
  acCriteria: AcCriterion[];
  conceptPath: string | null;
  commits: string[];
}
export interface CoverageReport {
  generatedAt: string;
  sources: { trace: boolean; acceptanceCriteria: boolean; reviews: boolean; implStatus: boolean };
  implStatus: { pending: number; implemented: number; tested: number } | null;
  features: FeatureCoverage[];
  orphans: Array<{ path: string; reason: string }>;
}
export function buildCoverageReport(projectRoot: string, conceptDir: string): CoverageReport
// GET /api/review/coverage → CoverageReport
```

- [ ] **Step 1: Write the failing test** `test/unit/review-coverage.test.ts`:

```ts
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, describe, expect, it } from "vitest";
import { buildCoverageReport } from "../../server/utils/review-coverage";

const root = mkdtempSync(join(tmpdir(), "coverage-"));
const impl = join(root, "_implementation");
const concept = join(root, "_concept");
afterAll(() => rmSync(root, { recursive: true, force: true }));

function seed() {
  mkdirSync(join(impl, "acceptance_criteria", "auth"), { recursive: true });
  mkdirSync(join(impl, "review"), { recursive: true });
  mkdirSync(join(concept, "experience", "features", "01_core"), { recursive: true });
  writeFileSync(
    join(impl, "trace.yaml"),
    [
      "features:",
      "  auth:",
      "    specced: true",
      "    sliced: true",
      "    committed: true",
      "    evaluated: false",
      "    documented: true",
      "    code_refs: [server/auth.ts]",
      "  billing:",
      "    specced: true",
      "    sliced: false",
      "    committed: false",
      "    evaluated: false",
      "    documented: false",
      "    code_refs: []",
      "orphans:",
      "  - path: src/legacy.ts",
      "    reason: no feature reference",
      "",
    ].join("\n"),
  );
  writeFileSync(
    join(impl, "acceptance_criteria", "auth", "login.ac.md"),
    "---\nfeature: auth\n---\n\n- [PASS] user can log in\n- [FAIL] lockout after 5 attempts\n- [ ] password reset\n",
  );
  writeFileSync(
    join(impl, "review", "auth.yaml"),
    "feature: auth\nverdict: changes-requested\nfindings:\n  - severity: major\n    note: lockout missing\ncommits: [abc123]\n",
  );
  writeFileSync(
    join(concept, "experience", "features", "01_core", "auth.md"),
    "---\nimpl_status: implemented\n---\n# Auth\n",
  );
}

describe("buildCoverageReport", () => {
  it("degrades gracefully when _implementation/ is absent", () => {
    const report = buildCoverageReport(root, concept);
    expect(report.sources).toEqual({
      trace: false,
      acceptanceCriteria: false,
      reviews: false,
      implStatus: false,
    });
    expect(report.features).toEqual([]);
    expect(report.orphans).toEqual([]);
  });

  it("merges trace, AC results, and review verdicts per feature", () => {
    seed();
    const report = buildCoverageReport(root, concept);
    expect(report.sources.trace).toBe(true);
    expect(report.orphans).toEqual([{ path: "src/legacy.ts", reason: "no feature reference" }]);

    const auth = report.features.find((f) => f.feature === "auth")!;
    expect(auth.specced).toBe("yes");
    expect(auth.evaluated).toBe("no");
    expect(auth.codeTraced).toBe("yes");
    expect(auth.tested).toEqual({ cell: "no", passed: 1, failed: 1, pending: 1 });
    expect(auth.verdict).toBe("changes-requested");
    expect(auth.findings).toEqual([{ severity: "major", note: "lockout missing" }]);
    expect(auth.acCriteria).toHaveLength(3);
    expect(auth.commits).toEqual(["abc123"]);

    const billing = report.features.find((f) => f.feature === "billing")!;
    expect(billing.tested).toEqual({ cell: "unknown", passed: 0, failed: 0, pending: 0 });
    expect(billing.verdict).toBe(null);
  });
});
```

- [ ] **Step 2: Run, confirm failure**, then implement `server/utils/review-coverage.ts`:

```ts
/**
 * Review coverage indexer — read-only aggregation over the target project's
 * _implementation/ review artifacts (skaileup 2026-07-05-perfect-review-plan)
 * plus _concept/ impl_status frontmatter.
 *
 * Every source is optional; missing files degrade to "unknown" cells and a
 * false flag in `sources`, never an error.
 */
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { parse as parseYaml } from "yaml";
import { parseFrontmatter, scanImplStatus } from "./concept-status";

export type CoverageCell = "yes" | "no" | "unknown";

export interface AcCriterion {
  text: string;
  status: "pass" | "fail" | "pending";
  file: string;
}

export interface ReviewFinding {
  severity: string;
  note: string;
}

export interface FeatureCoverage {
  feature: string;
  specced: CoverageCell;
  sliced: CoverageCell;
  committed: CoverageCell;
  tested: { cell: CoverageCell; passed: number; failed: number; pending: number };
  evaluated: CoverageCell;
  documented: CoverageCell;
  codeTraced: CoverageCell;
  verdict: "approved" | "changes-requested" | "pending" | null;
  findings: ReviewFinding[];
  acCriteria: AcCriterion[];
  conceptPath: string | null;
  commits: string[];
}

export interface CoverageReport {
  generatedAt: string;
  sources: { trace: boolean; acceptanceCriteria: boolean; reviews: boolean; implStatus: boolean };
  implStatus: { pending: number; implemented: number; tested: number } | null;
  features: FeatureCoverage[];
  orphans: Array<{ path: string; reason: string }>;
}

const cell = (v: unknown): CoverageCell => (v === true ? "yes" : v === false ? "no" : "unknown");

function safeYaml(path: string): Record<string, any> | null {
  try {
    const parsed = parseYaml(readFileSync(path, "utf-8"));
    return parsed && typeof parsed === "object" ? (parsed as Record<string, any>) : null;
  } catch {
    return null;
  }
}

function walkFiles(dir: string, suffix: string, out: string[] = []): string[] {
  if (!existsSync(dir)) return out;
  try {
    for (const e of readdirSync(dir, { withFileTypes: true })) {
      const p = join(dir, e.name);
      if (e.isDirectory()) walkFiles(p, suffix, out);
      else if (e.isFile() && e.name.endsWith(suffix)) out.push(p);
    }
  } catch {
    /* unreadable dir — treat as empty */
  }
  return out;
}

/** Parse one .ac.md: feature from frontmatter (fallback: parent dir / basename). */
function parseAcFile(path: string, acRoot: string): { feature: string; criteria: AcCriterion[] } {
  const content = readFileSync(path, "utf-8");
  const fm = parseFrontmatter(content);
  const rel = path.slice(acRoot.length + 1);
  const fallback = rel.includes("/") ? rel.split("/")[0]! : rel.replace(/\.ac\.md$/, "");
  const feature = typeof fm?.feature === "string" && fm.feature ? fm.feature : fallback;

  const criteria: AcCriterion[] = [];
  for (const line of content.split("\n")) {
    const m = line.match(/^\s*-\s*\[(PASS|FAIL|x|X| )\]\s*(.+)$/);
    if (!m) continue;
    const marker = m[1]!.toUpperCase();
    criteria.push({
      text: m[2]!.trim(),
      status: marker === "PASS" || marker === "X" ? "pass" : marker === "FAIL" ? "fail" : "pending",
      file: rel,
    });
  }
  return { feature, criteria };
}

/** Locate the concept doc for a feature under experience/features/<NN_group>/. */
function findConceptPath(conceptDir: string, feature: string): string | null {
  const featuresDir = join(conceptDir, "experience", "features");
  const hit = walkFiles(featuresDir, ".md").find((p) => {
    const base = p.split("/").pop()!.replace(/\.md$/, "");
    return base === feature || base.replace(/^\d+_/, "") === feature;
  });
  return hit ? hit.slice(conceptDir.length + 1) : null;
}

export function buildCoverageReport(projectRoot: string, conceptDir: string): CoverageReport {
  const implDir = join(projectRoot, "_implementation");

  // ── trace.yaml ──
  const trace = safeYaml(join(implDir, "trace.yaml"));
  const traceFeatures: Record<string, any> =
    trace?.features && typeof trace.features === "object" ? trace.features : {};
  const orphans = Array.isArray(trace?.orphans)
    ? trace.orphans
        .filter((o: any) => o && typeof o.path === "string")
        .map((o: any) => ({ path: o.path, reason: String(o.reason ?? "") }))
    : [];

  // ── acceptance_criteria/**/*.ac.md ──
  const acRoot = join(implDir, "acceptance_criteria");
  const acFiles = walkFiles(acRoot, ".ac.md");
  const acByFeature = new Map<string, AcCriterion[]>();
  for (const f of acFiles) {
    const { feature, criteria } = parseAcFile(f, acRoot);
    acByFeature.set(feature, [...(acByFeature.get(feature) ?? []), ...criteria]);
  }

  // ── review/<feature>.yaml ──
  const reviewDir = join(implDir, "review");
  const reviewByFeature = new Map<string, Record<string, any>>();
  for (const f of walkFiles(reviewDir, ".yaml")) {
    const doc = safeYaml(f);
    if (!doc) continue;
    const feature =
      typeof doc.feature === "string" && doc.feature
        ? doc.feature
        : f.split("/").pop()!.replace(/\.yaml$/, "");
    reviewByFeature.set(feature, doc);
  }

  // ── feature id union across sources ──
  const featureIds = [
    ...new Set([...Object.keys(traceFeatures), ...acByFeature.keys(), ...reviewByFeature.keys()]),
  ].sort();

  const features: FeatureCoverage[] = featureIds.map((feature) => {
    const t = traceFeatures[feature] ?? null;
    const ac = acByFeature.get(feature) ?? [];
    const review = reviewByFeature.get(feature) ?? null;

    const passed = ac.filter((c) => c.status === "pass").length;
    const failed = ac.filter((c) => c.status === "fail").length;
    const pending = ac.filter((c) => c.status === "pending").length;
    const testedCell: CoverageCell =
      ac.length === 0 ? "unknown" : failed === 0 && pending === 0 ? "yes" : "no";

    const verdictRaw = review?.verdict;
    const verdict =
      verdictRaw === "approved" || verdictRaw === "changes-requested" || verdictRaw === "pending"
        ? verdictRaw
        : null;

    return {
      feature,
      specced: cell(t?.specced),
      sliced: cell(t?.sliced),
      committed: cell(t?.committed),
      tested: { cell: testedCell, passed, failed, pending },
      evaluated: cell(t?.evaluated),
      documented: cell(t?.documented),
      codeTraced:
        t == null ? "unknown" : Array.isArray(t.code_refs) && t.code_refs.length > 0 ? "yes" : "no",
      verdict,
      findings: Array.isArray(review?.findings)
        ? review.findings.map((f: any) => ({
            severity: String(f?.severity ?? "info"),
            note: String(f?.note ?? ""),
          }))
        : [],
      acCriteria: ac,
      conceptPath: findConceptPath(conceptDir, feature),
      commits: Array.isArray(review?.commits) ? review.commits.map(String) : [],
    };
  });

  const implStatus = scanImplStatus(join(conceptDir, "experience", "features"));

  return {
    generatedAt: new Date().toISOString(),
    sources: {
      trace: trace !== null,
      acceptanceCriteria: acFiles.length > 0,
      reviews: reviewByFeature.size > 0,
      implStatus: implStatus !== null,
    },
    implStatus,
    features,
    orphans,
  };
}
```

- [ ] **Step 3: Run green.** `bun --bun vitest run test/unit/review-coverage.test.ts` — expect `2 passed`.

- [ ] **Step 4: Endpoint** `server/api/review/coverage.get.ts`:

```ts
import { requireAuth } from "../../utils/auth";
import { getConceptDir, getProjectRoot } from "../../utils/project";
import { buildCoverageReport } from "../../utils/review-coverage";

/**
 * GET /api/review/coverage — feature-level coverage matrix aggregated from
 * _implementation/{trace.yaml, acceptance_criteria/, review/} and _concept/
 * impl_status frontmatter. All sources optional (see CoverageReport.sources).
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  return buildCoverageReport(getProjectRoot(), getConceptDir());
});
```

- [ ] **Step 5: Verify + commit.** `bun --bun vitest run` green; `curl -s localhost:3000/api/review/coverage` against a dev server (authenticated session cookie) returns JSON with `sources` flags.

```
git add server/utils/review-coverage.ts server/api/review/coverage.get.ts test/unit/review-coverage.test.ts
git commit -m "feat(review): coverage indexer over _implementation review artifacts

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 11: Review dashboard page (`/review`)

**Files:**
- Create: `app/pages/review.vue`
- Modify: `app/components/AppSidebar.vue` (`extraLinks` L572)

**Interfaces:**
- Consumes: `GET /api/review/coverage` → `CoverageReport` (mirror the type locally, matching Task 10 exactly); Nuxt UI 4 components already used in the codebase (`UBadge`, `UButton`, `UIcon`, `USlideover`, `UAlert`).

- [ ] **Step 1: Create `app/pages/review.vue`:**

```vue
<template>
  <div class="max-w-6xl mx-auto py-6 px-4 space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-gray-800 dark:text-gray-100">Review coverage</h1>
        <p class="text-sm text-gray-500">
          Per-feature coverage across spec, slices, commits, tests, evaluation, and code trace.
        </p>
      </div>
      <UButton variant="soft" icon="i-heroicons-arrow-path" size="sm" @click="refresh()">
        Refresh
      </UButton>
    </div>

    <!-- Missing-source hints (graceful degradation) -->
    <UAlert
      v-if="report && !report.sources.trace"
      color="neutral"
      variant="subtle"
      icon="i-heroicons-information-circle"
      title="No trace.yaml found"
      description="_implementation/trace.yaml is missing — spec/slice/commit/trace columns show as unknown. Run the impl-quality trace step to populate it."
    />

    <!-- Coverage matrix -->
    <div v-if="report?.features.length" class="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-800">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 dark:bg-gray-900 text-left text-xs uppercase tracking-wider text-gray-400">
          <tr>
            <th class="px-3 py-2">Feature</th>
            <th v-for="col in columns" :key="col.key" class="px-3 py-2 text-center">{{ col.label }}</th>
            <th class="px-3 py-2 text-center">Verdict</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="f in report.features"
            :key="f.feature"
            class="border-t border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900 cursor-pointer"
            @click="openFeature(f)"
          >
            <td class="px-3 py-2 font-mono text-xs">{{ f.feature }}</td>
            <td v-for="col in columns" :key="col.key" class="px-3 py-2 text-center">
              <template v-if="col.key === 'tested'">
                <UBadge :color="pillColor(f.tested.cell)" variant="subtle" size="sm">
                  {{ testedLabel(f) }}
                </UBadge>
              </template>
              <UBadge v-else :color="pillColor(f[col.key])" variant="subtle" size="sm">
                {{ f[col.key] }}
              </UBadge>
            </td>
            <td class="px-3 py-2 text-center">
              <UBadge v-if="f.verdict" :color="verdictColor(f.verdict)" variant="subtle" size="sm">
                {{ f.verdict }}
              </UBadge>
              <span v-else class="text-gray-400 text-xs">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="report" class="text-center text-gray-400 py-12 text-sm">
      No review artifacts yet — nothing under _implementation/.
    </div>

    <!-- Orphan code panel -->
    <div v-if="report?.orphans.length" class="rounded-lg border border-amber-200 dark:border-amber-900 p-4">
      <h2 class="text-sm font-semibold text-amber-700 dark:text-amber-400 mb-2 flex items-center gap-2">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4" />
        Orphan code ({{ report.orphans.length }})
      </h2>
      <ul class="space-y-1">
        <li v-for="o in report.orphans" :key="o.path" class="text-xs text-gray-600 dark:text-gray-300">
          <span class="font-mono">{{ o.path }}</span>
          <span class="text-gray-400"> — {{ o.reason }}</span>
        </li>
      </ul>
    </div>

    <!-- Per-feature drilldown drawer -->
    <USlideover v-model:open="drawerOpen" :title="selected?.feature ?? ''">
      <template #body>
        <div v-if="selected" class="space-y-6">
          <!-- Acceptance criteria -->
          <section>
            <h3 class="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">
              Acceptance criteria
            </h3>
            <p v-if="!selected.acCriteria.length" class="text-xs text-gray-400">
              No .ac.md files for this feature.
            </p>
            <ul class="space-y-1.5">
              <li v-for="(c, i) in selected.acCriteria" :key="i" class="flex items-start gap-2 text-sm">
                <UIcon :name="acIcon(c.status)" :class="acIconColor(c.status)" class="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span class="text-gray-700 dark:text-gray-200">{{ c.text }}</span>
              </li>
            </ul>
          </section>

          <!-- Review findings -->
          <section>
            <h3 class="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">Findings</h3>
            <p v-if="!selected.findings.length" class="text-xs text-gray-400">No findings recorded.</p>
            <ul class="space-y-2">
              <li v-for="(f, i) in selected.findings" :key="i" class="text-sm">
                <UBadge size="sm" variant="subtle" :color="f.severity === 'major' ? 'error' : 'warning'">
                  {{ f.severity }}
                </UBadge>
                <span class="ml-2 text-gray-700 dark:text-gray-200">{{ f.note }}</span>
              </li>
            </ul>
          </section>

          <!-- Links -->
          <section class="space-y-2">
            <h3 class="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">Links</h3>
            <UButton
              v-if="selected.conceptPath"
              variant="soft" size="sm" icon="i-heroicons-document-text" block
              :to="`/concepts/${selected.conceptPath.replace(/\.md$/, '')}`"
            >
              Concept doc
            </UButton>
            <p v-if="selected.commits.length" class="text-xs text-gray-500">
              Commits:
              <span v-for="c in selected.commits" :key="c" class="font-mono mr-2">{{ c.slice(0, 8) }}</span>
            </p>
          </section>
        </div>
      </template>
    </USlideover>
  </div>
</template>

<script setup lang="ts">
type CoverageCell = "yes" | "no" | "unknown";
interface AcCriterion { text: string; status: "pass" | "fail" | "pending"; file: string }
interface ReviewFinding { severity: string; note: string }
interface FeatureCoverage {
  feature: string;
  specced: CoverageCell;
  sliced: CoverageCell;
  committed: CoverageCell;
  tested: { cell: CoverageCell; passed: number; failed: number; pending: number };
  evaluated: CoverageCell;
  documented: CoverageCell;
  codeTraced: CoverageCell;
  verdict: "approved" | "changes-requested" | "pending" | null;
  findings: ReviewFinding[];
  acCriteria: AcCriterion[];
  conceptPath: string | null;
  commits: string[];
}
interface CoverageReport {
  generatedAt: string;
  sources: { trace: boolean; acceptanceCriteria: boolean; reviews: boolean; implStatus: boolean };
  implStatus: { pending: number; implemented: number; tested: number } | null;
  features: FeatureCoverage[];
  orphans: Array<{ path: string; reason: string }>;
}

const { data: report, refresh } = await useFetch<CoverageReport>("/api/review/coverage");

const columns = [
  { key: "specced", label: "Specced" },
  { key: "sliced", label: "Sliced" },
  { key: "committed", label: "Committed" },
  { key: "tested", label: "Tested" },
  { key: "evaluated", label: "Evaluated" },
  { key: "documented", label: "Documented" },
  { key: "codeTraced", label: "Code-traced" },
] as const;

function pillColor(cellValue: CoverageCell): "success" | "error" | "neutral" {
  if (cellValue === "yes") return "success";
  if (cellValue === "no") return "error";
  return "neutral";
}

function verdictColor(v: string): "success" | "error" | "warning" {
  if (v === "approved") return "success";
  if (v === "changes-requested") return "error";
  return "warning";
}

function testedLabel(f: FeatureCoverage): string {
  const total = f.tested.passed + f.tested.failed + f.tested.pending;
  if (total === 0) return "unknown";
  return `${Math.round((f.tested.passed / total) * 100)}% (${f.tested.passed}/${total})`;
}

function acIcon(status: AcCriterion["status"]): string {
  if (status === "pass") return "i-heroicons-check-circle";
  if (status === "fail") return "i-heroicons-x-circle";
  return "i-heroicons-clock";
}
function acIconColor(status: AcCriterion["status"]): string {
  if (status === "pass") return "text-green-500";
  if (status === "fail") return "text-red-500";
  return "text-gray-400";
}

const drawerOpen = ref(false);
const selected = ref<FeatureCoverage | null>(null);
function openFeature(f: FeatureCoverage) {
  selected.value = f;
  drawerOpen.value = true;
}
</script>
```

- [ ] **Step 2: Sidebar link.** In `app/components/AppSidebar.vue` replace `const extraLinks = computed(() => []);` (L572) with:

```ts
const extraLinks = computed(() => [
  {
    label: "Review coverage",
    icon: "i-heroicons-clipboard-document-check",
    to: "/review",
    active: route.path === "/review",
  },
]);
```

- [ ] **Step 3: Verify.** `bunx vue-tsc --noEmit` clean for the new page; dev server: `/review` renders "No review artifacts yet" against a project without `_implementation/`; seed the Task 10 fixture files into a scratch project (`WORKSPACE_DIR`) and confirm matrix rows, tested % pill, orphan panel, and drilldown drawer.

- [ ] **Step 4: Commit.**

```
git add app/pages/review.vue app/components/AppSidebar.vue
git commit -m "feat(review): coverage dashboard page with drilldown drawer

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 12: StepReview.vue — file list with per-file preview

**Files:**
- Modify: `app/components/StepReview.vue` (whole file — currently a 39-line stub showing only a count; keep the `approve`/`revise` emits and existing props so any future caller stays source-compatible)

**Interfaces:**
- Props: `{ stepId: string; stepName: string; fileCount: number; files?: string[] }` (new optional `files` — concept-relative paths as produced by `EnrichedNodeState.folders` expansion / `StepFileList` conventions).
- Emits unchanged: `approve: []`, `revise: []`.
- Consumes: `GET /api/concepts/<path>` → `{ content: string }`; `MarkdownRenderer` component (`:content` prop).

- [ ] **Step 1: Replace `app/components/StepReview.vue`:**

```vue
<template>
  <div class="max-w-lg mx-auto text-center">
    <div class="flex items-center gap-2 justify-center mb-3">
      <UIcon name="i-heroicons-check-circle" class="w-8 h-8 text-green-500" />
    </div>
    <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-1">{{ stepName }}</h2>
    <p class="text-sm text-gray-500 mb-6">
      Step complete &mdash; {{ effectiveCount }} {{ effectiveCount === 1 ? 'file' : 'files' }} generated. Review the output and approve to continue.
    </p>

    <!-- Generated files with per-file preview toggle -->
    <div v-if="files?.length" class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-2 mb-6 text-left space-y-1">
      <div v-for="file in files" :key="file" class="rounded-md">
        <button
          class="flex items-center gap-2 w-full px-2 py-1.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors"
          @click="togglePreview(file)"
        >
          <UIcon
            :name="openPreviews.has(file) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'"
            class="w-3.5 h-3.5 text-gray-400 flex-shrink-0"
          />
          <UIcon name="i-heroicons-document-text" class="w-4 h-4 flex-shrink-0 text-gray-400" />
          <span class="truncate font-mono text-xs flex-1">{{ file }}</span>
          <NuxtLink
            :to="`/concepts/${file.replace(/\.md$/, '')}`"
            class="text-gray-400 hover:text-primary-500"
            title="Open in editor"
            @click.stop
          >
            <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-3.5 h-3.5" />
          </NuxtLink>
        </button>
        <div
          v-if="openPreviews.has(file)"
          class="mx-2 mb-2 px-3 py-2 max-h-64 overflow-y-auto rounded border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-left"
        >
          <p v-if="previewErrors.has(file)" class="text-xs text-red-400">Failed to load preview.</p>
          <p v-else-if="!previews.has(file)" class="text-xs text-gray-400">Loading…</p>
          <MarkdownRenderer v-else :content="previews.get(file)!" class="prose-sm dark:prose-invert" />
        </div>
      </div>
    </div>

    <!-- Fallback: bare count when the caller passes no file list -->
    <div v-else class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 mb-6">
      <div class="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
        <UIcon name="i-heroicons-document-text" class="w-4 h-4" />
        <span>{{ effectiveCount }} {{ effectiveCount === 1 ? 'file' : 'files' }} in this step</span>
      </div>
      <p class="text-xs text-gray-400 mt-2">Select files in the sidebar to review their contents before approving.</p>
    </div>

    <!-- Actions -->
    <div class="flex gap-2 justify-center">
      <UButton color="primary" icon="i-heroicons-check" @click="$emit('approve')">Approve &amp; Continue</UButton>
      <UButton variant="outline" icon="i-heroicons-sparkles" @click="$emit('revise')">Regenerate with AI</UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  stepId: string;
  stepName: string;
  fileCount: number;
  /** Concept-relative file paths generated by this step (e.g. "discovery/brief.md"). */
  files?: string[];
}>();

defineEmits<{
  approve: [];
  revise: [];
}>();

const effectiveCount = computed(() => props.files?.length ?? props.fileCount);

const openPreviews = ref(new Set<string>());
const previews = ref(new Map<string, string>());
const previewErrors = ref(new Set<string>());

async function togglePreview(file: string) {
  const open = new Set(openPreviews.value);
  if (open.has(file)) {
    open.delete(file);
    openPreviews.value = open;
    return;
  }
  open.add(file);
  openPreviews.value = open;

  if (previews.value.has(file) || previewErrors.value.has(file)) return;
  try {
    const res = await $fetch<{ content: string }>(`/api/concepts/${file.replace(/\.md$/, "")}`);
    const next = new Map(previews.value);
    next.set(file, res.content);
    previews.value = next;
  } catch {
    previewErrors.value = new Set([...previewErrors.value, file]);
  }
}
</script>
```

- [ ] **Step 2: Verify.** `bunx vue-tsc --noEmit` clean. StepReview currently has no call site (grep confirms) — smoke-test it by temporarily rendering `<StepReview step-id="x" step-name="Brief" :file-count="1" :files="['discovery/brief']" />` in `/concepts` (or a scratch page), toggle a preview, confirm markdown renders, then remove the scratch usage.

- [ ] **Step 3: Commit.**

```
git add app/components/StepReview.vue
git commit -m "feat(review): per-file preview toggles in StepReview

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 13: File the upstream type-union issue against @skaile/workspaces

**Files:**
- None in forge-concept (the local workaround shipped in Task 1). Output is a GitHub issue.

- [ ] **Step 1: Draft and file the issue.** Run:

```
gh repo view skaile-ai/workspaces >/dev/null 2>&1 && gh issue create \
  --repo skaile-ai/workspaces \
  --title "flow engine types: FlowNode.type union missing \"sub-flow\" and \"router\"" \
  --body "dist/factory-assets/connectors/flow/engine/types.d.ts declares FlowNode.type as \"skill\" | \"group\", but shipped skaileup flows (appbuilder-standard/-complex) contain type: sub-flow nodes (data.flow = delegated flow id), and the 2026-07-05 flow restructure adds type: router nodes (data.routes: ordered {condition, target}, target: null = skip, condition \"default\" = catch-all). Downstream consumers (forge-concept) must cast around the union. Please widen the union (or add an extensible node-type registry) and document engine semantics: both types are non-executable; sub-flow completion = delegated flow done; router completion = choice recorded. forge-concept ships a local widening in shared/flow-extended.ts as reference."
```

  Expected output: a `https://github.com/skaile-ai/workspaces/issues/<n>` URL. If the repo is inaccessible (`gh repo view` fails), instead paste the same body into the team's tracker and record the link in the final PR description — do not create a report file in either repo.

- [ ] **Step 2: Reference the issue.** Add the issue URL to the doc comment atop `shared/flow-extended.ts` (replace "Upstream issue: see plan Task 13" with the URL) and commit:

```
git add shared/flow-extended.ts
git commit -m "docs(flow): link upstream FlowNode type-union issue

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 14: Final verification sweep

- [ ] **Step 1: Full unit + integration suite.** `cd /Users/matthias/devBench/SKAILEdev/forge/forge-concept && bun --bun vitest run` — all green (expect the 5 new test files: flow-extended, flow-phases, flow-extended-state, flow-layout, flow-route-choice, review-coverage — plus all pre-existing tests).
- [ ] **Step 2: Typecheck.** `bunx vue-tsc --noEmit` — no errors in any touched file (pre-existing unrelated errors, if any, listed and left alone).
- [ ] **Step 3: E2E smoke.** `bun run test:e2e -- tests/e2e/concepts-index.spec.ts tests/e2e/concepts-tree.spec.ts` — the sidebar/graph changes must not break existing specs.
- [ ] **Step 4: Manual end-to-end.** With an appbuilder-standard flow installed (`skaile add flow:appbuilder-standard` in the workspace): graph shows lanes + sub-flow chip + router diamond (when the restructured flows are deployed; with pre-restructure flows, verify the heuristic-lane fallback and that nothing else regressed); route chooser skips unchosen branches (check `.skaile/sessions/<runId>.json` gains `routeChoices` and `skipped` entries); `/review` renders with and without `_implementation/` artifacts.
- [ ] **Step 5: Use superpowers:requesting-code-review / finishing-a-development-branch** to wrap up the branch.

---

## Self-review checklist (done before saving this plan)

- Coverage: all four spec groups (A sub-flow, B lanes, C routers, D dashboard) mapped to Tasks 1-12 + upstream issue (13) + sweep (14).
- No placeholders: every code block is complete and typed against the real files read (flow-manager.ts L14/L62-96/L438-518, FlowGraph.vue L114-245, useFlowState.ts L37-73/L244+, skip.post.ts L41-48 guard, session shape in flow-session.ts, `MarkdownRenderer :content`, `GET /api/concepts/<path>` → `{ content }`, vitest config `test/unit/**`).
- Type-name consistency: `ExtendedFlowNode`/`RouteDef`/`Phase`/`SyntheticNodeState`/`CoverageReport`/`FeatureCoverage` used with identical shapes across server, client mirror, and tests.
- Known deviation documented: server-side route pruning instead of client-chained `skipNode` (Global Constraints, with the L41-48 evidence).
