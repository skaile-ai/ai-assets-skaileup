# 27: Every skill's gates are invisible to the only reader

**Type:** task
**Blocked by:** ticket 16's ADR-0007 path sweep committing (done in-tree, not yet committed)
**Status:** ready once that commit lands

## Question

Graduated from ticket 22, which hit this while re-ruling the iron laws and could not resolve it
there: 22 owns a contract, this owns eight skills and the template that told them what to write.

**No `-mp` skill's `prerequisites` are read by anything.** Two independent breaks, each
sufficient on its own.

### 1. The block is at the root; the reader looks under `metadata:`

`workspaces/packages/workspaces/resolver/src/parser.ts:45-46`:

```ts
const fm = parseSkillFrontmatter(content);
const meta = fm.metadata ?? {};
const prerequisites = meta.prerequisites ?? {};
```

`parseSkillFrontmatter` is a raw YAML parse of the fence — no normalisation, no root-level
fallback; the whole file has two `fm.` reads. `grep -rn "^metadata:" skills/` returns **0 hits**:
all eight skills put `artifacts:` and `prerequisites:` at the root. The old collection nests them
(`ai-assets-skaileup/skaileup/03_experience/03_screens/SKILL.md:20,38`) and so does the resolver's
own fixture (`resolver/tests/parser.test.ts:6-11`).

Verified against the **deployed** artifact, not just source: `forge-concept`'s
`node_modules/@skaile/workspaces@0.48.1/dist/chunk-GXC3TYMQ.js`, `parseSkillRequirements` —
identical line.

Same break for the artifact edges: `discovery/src/requires-graph.ts:236-238` returns early on
`if (!metadata) return;`.

So `parseSkillRequirements` returns `empty` for every `-mp` skill and `satisfied` is vacuously
`true`.

### 2. The paths carry no `_concept/` prefix

`validator.ts:81` does `path.join(projectDir, req.path)`, and `projectDir` is `getProjectRoot()`
(`requirements.get.ts:51`) — the *project* root, not `_concept/`. Every old-repo declaration
carries the prefix (`_concept/experience/features`; `resolver/tests/validator.test.ts:34`); no
`-mp` declaration does. Fixing (1) alone leaves every path resolving one level too high.

### Where the convention was fixed wrong

`docs/skill-template.md:13-17` shows both blocks at the root of its fence and states
*"`artifacts.requires[].id + gate` — hard gates the flow engine enforces"*. Ticket 01's own
research had it right and the template did not carry it over
(`ai-assets-skaileup/.scratch/skaileup-mp/research/01-machine-layer-public-api.md:357`, branch
`research/machine-layer-api`: *"`metadata.prerequisites.files[]` … READ — hard/soft gates"*).

Every skill written since inherited it. The template is part of the fix, not a follow-up.

## Why this is blocked, and on what

**Fixing the nesting turns eight dead gates into live ones — four of them wrong.** The four
mockup skills still declare pre-0007 paths (`experience/screens`, `discovery/brand/tokens.json`,
`experience/journeys/stories.yaml`, `blueprint/techstack.md`), several **hard**. Repair the
nesting first and `mockup-storybook` blocks on a file ADR 0007 abolished and nothing writes.

Ticket 14 fixed exactly this bug class once — a hard gate on `design/tokens.json` that could never
pass — and the tree moved again underneath the repair. Do not make it three times.

Ticket 16 owns the path sweep and has it **done but uncommitted** in the `-mp` tree, interleaved
with live sessions. Verified 2026-09-05: all four mockup skills now declare ADR 0007 paths
(`07_screens`, `04_journeys/stories.yaml`, `03_brand/tokens.json`, `05_features`,
`10_blueprint/techstack.md`, `09_mockup/walkthrough`, `09_mockup/feedback/sessions`), so the
hazard is discharged the moment that commit lands — but not before. This ticket starts then.

## What to decide while doing it

- **`artifacts.requires[].gate` is read by nothing** — `requires-graph.ts:236-249` takes `r.id`
  only; `_shared.ts:36` declares the enum and stops. Five of `spec-feature`'s ten gate
  declarations are in a block whose `gate:` key no code has ever read. Keep it as documentation,
  or drop it and leave `id` alone?
- **A `soft` gate has no rendering anywhere.** `validator.ts:149` excludes soft entries from
  `satisfied`; they are reported in `files[]` and never warned on. The one route that would fetch
  that report (`forge-concept/server/api/flows/nodes/[nodeId]/requirements.get.ts`) has **zero
  callers**, and the UI panel labelled "Hard gates" (`GateInfo.vue:37-43`) is fed by *flow edges*
  (`flow-extended-state.ts:47-50`), not file gates. If `soft` is to mean anything to a human, the
  skill body has to say it — which is ADR 0008's rule, applied to the soft half.
- **Law 3's escape hatch has a machine form nothing declares.** `validator.ts:74-79` treats any
  path in `overrides.skip_checks` as present, fed from flow-node `data.overrides`
  (`requirements.get.ts:52`). `-mp` has no flows yet and `flow.schema.json` is deleted, so
  whether "unless the user explicitly skipped brand" survives as a declarable thing is
  **ticket 10's**, once flows exist.

## Scope

Eight `SKILL.md` files, `docs/skill-template.md`, and a `scripts/check.py` rule so it cannot
regress — the failure mode is silent (`satisfied: true` on an unmet gate), which is exactly
ticket 16's stated bar for what earns a check.
