# 27: Every skill's gates are invisible to the only reader

**Type:** task
**Blocked by:** None — ticket 16's path sweep landed as `-mp` `e63316c` (2026-09-05)
**Status:** resolved

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

---

## Resolution

**Both breaks repaired at the source, and the template that taught them fixed with them.
Recorded as ADR 0011 — "The machine layer sits under `metadata:`, and its paths carry
`_concept/`."** Landed as `-mp` `5360697`, on top of `e63316c` (ticket 16's sweep, committed
by this session — it was the blocker).

### Proof, against the deployed bundle rather than the source

`parseSkillRequirements` + `validateRequirements` from
`forge-concept/node_modules/@skaile/workspaces@0.48.1`, run over `mockup-walkthrough`:

| | gates parsed | `satisfied` on an empty project |
|---|---|---|
| before | 0 | **`true`** |
| after | 4 (3 hard, 1 soft) | `false` |

That is the whole ticket in one line: the report used to come back green with every gate
unmet, and no error anywhere on the way.

### The four decisions

1. **Nest, don't fix the reader.** One line in `parser.ts` would fix every skill forever, and
   root-level is the Claude-skill shape ADR 0001 chose deliberately — but it means a
   `@skaile/workspaces` release and a forge-concept bump mid-migration, which the map's Notes
   rule out for sequencing. **Register entry added** naming `parser.ts:45-46` as the successor
   effort's cheapest item. `name`/`description`/`version` stay at the root: `discover.ts:705-719`
   normalises root and nested both, so only `prerequisites` and `artifacts` move.
2. **Every path prefixed `_concept/`**, and `check.py` enforces it. Rule 4 could not simply be
   kept — it read the root block and matched the first segment against the tree, so both halves
   of the fix broke it. It now requires the prefix and matches the segment *after* it.
3. **`artifacts.requires[]` keeps `id`, drops `gate:`.** No code has ever read that key, and its
   one reader (`requires-graph.ts:236-249`) takes `id` only, for cycle detection over edges whose
   targets are artifact ids — which are never asset refs, so no cycle can involve them. The
   decisive evidence was not deadness but **divergence**: `build-implement`, `mockup-storybook`
   and `spec-feature` each declared a soft artifact with no matching entry in
   `prerequisites.files[]`, the block that actually gates. Two declarations of one dependency had
   already drifted apart in three of eight skills.
4. **Soft gates keep their declaration and gain a sentence at their step.** A soft gate renders
   nowhere — excluded from `satisfied` (`validator.ts:149`), never warned on, and the one route
   that would report it has no callers. Three needed the prose (`build-plan` on techstack and
   datamodel, `mockup-walkthrough` on features, `spec-feature` on journeys and datamodel); two
   already had it (`mockup-storybook:78`, `mockup-feedback` step 1).

### Also landed

- **`docs/skill-template.md`** — the origin. Its fence showed both blocks at the root and it
  stated *"`artifacts.requires[].id + gate` — hard gates the flow engine enforces"*, the opposite
  of the truth on both counts. The fence now shows the nesting and the prefix; three rules behind
  it cite the reader line for each.
- **`docs/examples/` (both worked examples)** — same repair, plus the pre-0007 paths ticket 16's
  sweep did not reach (`experience/screens`, `design/tokens.json`, `experience/journeys/`). An
  example that models the broken shape is worse than no example. `concept-brief`'s sizing write
  also moved off `_grounding/overview/user_input.json` — a path that is wrong three ways — onto
  `01_meta/scope.yaml`, where the tree puts tier and profile.
- **`CLAUDE.md`** and **ADR 0001**'s frontmatter clause narrowed to point at ADR 0011.
- **ADR 0008's index row was missing from `docs/adr/README.md`** — restored while adding 0011's.
- `check.py` green (8 skills, 0 errors); `test_check.py` 31 passed, up from 28 — one test per new
  rule plus the prefix case.

### Handed to the four remaining port tickets (23, 24, 25, 26)

Write the nesting and the prefix from the start; `check.py` fails the build otherwise. The
template is now correct, so following it is enough. **`inputs_optional` is the one declaration
this ticket could not verify** — no `-mp` skill declares inputs yet, and the first one that does
inherits the clash below.

### Questions this surfaced for other tickets

- **The input dialog's path is hardcoded to a directory ADR 0007 abolished.**
  `validator.ts:107` reads `_concept/_grounding/<skillId>/input.json`; the tree says
  `02_grounding/`. Nothing declares this path — the host owns both ends — so it constrains no
  skill today, and the first skill with `inputs_optional` hits it. Register entry added.
- **`artifacts.produces` is decoration too** (`docs/examples/mockup-walkthrough-astro` carries
  one). `producesIndex` is an optional argument to `validateRequirements` that
  `requirements.get.ts` never passes, so `producedBy` in the report is always `undefined`. Left
  alone here — it is one line in an example — but ticket 26 should not copy it into a live skill
  expecting it to do anything.
