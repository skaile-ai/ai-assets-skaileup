# 28: Write the four flow YAMLs

**Type:** task
**Blocked by:** None — 23, 25, 26 all resolved 2026-09-05 (every node skill now exists)
**Status:** resolved

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

**Four files written, node and edge counts exactly as ticket 10 specified, `check.py` green
(29 skills · 4 flows · 0 errors) and `test_check.py` 31/31.**

| flow | skill nodes | groups | edges | entry | `input_style` | contracts in `requires:` |
|---|---|---|---|---|---|---|
| `appbuilder-mvp` | 9 | 3 | 8 | `scope` | `structured` | 8 |
| `appbuilder-standard` | 27 | 3 | 26 | `scope` | `structured` | 13 (all) |
| `skaileup-concept-only` | 14 | 3 | 13 | `scope` | `structured` | 11 |
| `skaileup-concept-reverse` | 9 | 3 | 8 | `reverse` | `repo` | 13 (all) |

Every graph is the linear chain ticket 10 wrote, in its order, with no additions and no
substitutions. Every `data.skill` resolves to a real `skills/<name>/` directory, and the
cover is **exact both ways**: the four flows name 29 distinct skills, the repo holds 29, no
skill is unused and none is a phantom. `appbuilder-standard` runs 27 of them;
`quality-standards` and `concept-reverse` are the two that only `skaileup-concept-reverse`
runs, and `mockup-storybook` is the one only `appbuilder-standard` runs.

`requires:` is exact in both directions and contains no `flow:` refs. Its `contract:` set is
the **union of the contracts the flow's own node skills actually cite**, computed by grepping
`contracts/<file>.md` out of each skill directory rather than asserted — `mvp` drops
`elements_block`, `evaluator`, `golden_principles`, `semantic_types` and `walkthrough_renderer`;
`concept-only` drops `seed_data` and `semantic_types` (it has no data layer).

### What differs from ticket 10, and why

1. **Skill nodes carry no `position`; only the group nodes carry geometry.** This is the one
   shape decision the ticket left implicit and it is load-bearing. `flow-layout.ts` Pass 1
   removes any node with an explicit `position` from the lane computation, and returns early
   with `lanes: []` when nothing is left — so if every node is positioned, the group-phase
   override at `:87-93` that ticket 10 cited as the reason group nodes survive **never runs**.
   Authoring geometry on the skill nodes would have deleted the mechanism the rule exists to
   protect. Groups keep `position` + `style` as the ticket asks; the values are nominal.
2. **`skaileup-concept-only` and `skaileup-concept-reverse` carry an empty `implementation`
   group.** Ticket 28 says three group nodes per flow, so three were written, but neither flow
   has an implementation node. The empty group is inert — `phasesPresent` filters on nodes, so
   it draws no lane, and nothing else reads it. The old repo did the opposite (old
   `skaileup-concept-only` shipped two groups, old `skaileup-concept-reverse` one). Flagged
   rather than deviated from; deleting the two empty groups is a one-line change if wanted.
3. **`quality-standards` is phase `conceptualization` in `concept-reverse`.** Ticket 10 gave
   phases for `ops-review`, `quality-release` and `concept-reverse` but not this one. It runs
   second, reading the repository to understand it, and its old node sat under that flow's
   `g-conceptualization`. `phaseForSkill` would have guessed `review` off the substring
   `quality` — which is exactly why every node declares `phase` explicitly.
4. **`meta.onboarding.placeholder` is omitted from all four.** `OnboardingWizard.vue:94` binds
   it to the freeform textarea only, and `-mp` ships no `freeform` flow, so it has zero readers
   here. `input_style` and `fields` are present on all four.
5. **The impl-side loop comment sits at `build-plan`, not `build-implement`.** The rule is
   "one line at the loop's first node"; `build-plan` is the first node that repeats
   (once per feature, feeding `build-implement` once per slice). The comment names both.
   `spec-feature` carries the concept-side comment in the three flows that have that node.

### Also written

- `flows/README.md` — replaced its "Empty on purpose" paragraph, and removed a dangling link
  to `../contracts/flow.schema.json`, which ticket 16 deleted (`contracts/README.md:33` already
  says so). `check.py`'s citation check does not scan `flows/`, so nothing had caught it.

### The two harness edits (made, not committed) — for ticket 29

Both in `/Users/matthias/devBench/SKAILEdev/forge/forge-concept`, working tree only:

- `tests/integration/skaileup-flows.test.ts` — `REPO` default → `ai-assets-skaileup-mp.git`;
  `FLOWS` → the four; `SKILLS` → `["concept-brief", "concept-scope"]` (`concept-goals` died
  with ticket 08, `concept-scope` is ticket 10's rename of the old entry node); header + array
  comment rewritten.
- `templates/dev/skaile.yaml` — source URL → `-mp`; the six `flow:` deps → the four.

**Ticket 29 needs to know:** the test installs over **SSH from GitHub**, so `-mp` `main` must
be *pushed* before it can pass — everything here is a dirty working tree in both repos. The
suite self-skips when the repo is unreachable, so a missing push reports as a skip, not a
failure; check the `[skaileup-flows] SKIPPED` warning is absent before reading the run as green.
`test/unit/flow-extended{,-state}.test.ts` still uses `skaileup-slice*` fixture names — ticket
10 ruled those synthetic and still passing, left untouched.

### Shape rules `check.py` does not enforce

Verified by hand instead (ad-hoc script, all four flows clean). Every one of these is a silent
failure mode by the script's own bar, so they are candidates for it:

- **No deleted-key check at all** — `meta.category`, `globals.{approval_mode,subagent_mode,
  verbosity,concept_depth}`, `${...}` interpolation, `data.parameters`, `data.writes` all pass
  untouched. `data.parameters` in particular still has a live read (`parameters.flow`), so a
  stray block is not inert.
- **Node kinds** — `check.py` has working branches for `sub-flow` and `router`, so ticket 10's
  ruling that `-mp` ships neither is unenforced.
- **Three group nodes per flow** — unenforced; only `parentNode` → group resolution is checked.
- **Group phase vs node phase** — the "written from one table so they cannot disagree" property
  is exactly what is not checked. Both are validated against the enum independently; a node
  whose `data.phase` contradicts its group's passes, and the group silently wins.
- **`requires:` contract exactness** — skill refs are exact in both directions, but a
  `contract:` ref is only checked for *existence*. A contract the flow's skills never cite, or
  a cited contract left out, passes.
- **Edges `type: flow` only** — caught indirectly: a wrongly-typed edge shows up as an
  unreachable node. A non-flow edge *parallel* to a flow edge passes silently.
- **`version`, `description`, `meta.icon`, `meta.onboarding.*`, `globals.research_depth`,
  `input_style` values** — none are checked. All have live readers in `profiles.get.ts`.

### For the forge-concept register (Out of scope)

Five, all "the host reads it this way":

1. **Authored node geometry disables the swimlanes.** `app/utils/flow-layout.ts:53-64` +
   `:65` — an all-positioned flow returns `lanes: []`, so the group-phase override at `:87-93`
   and the phase lanes are both unreachable. The collection has to *withhold* geometry to get
   the feature. Site of the shape decision above.
2. **Group rects always render at the origin.** `app/components/FlowGraph.vue:214-232` reads
   group positions out of `layout.positions`, which `computeFlowLayout` fills only for
   `renderable` nodes — and a `group` is never renderable, so `pos` is always `undefined`.
   Reachable only in the `lanes.length === 0` branch. Together with (1) this means the group
   `style: {width,height}` ticket 28 mandates has no live reader on either path.
3. **Repo onboarding extras are gated on a hardcoded profile id.**
   `app/components/OnboardingWizard.vue:525` fills `extra` only when
   `selectedProfile === "reverse_engineer"`, but the profile key **is the flow id**
   (`server/api/pipeline/profiles.get.ts`). For `skaileup-concept-reverse` the branch never
   fires: `branch` and `context` are collected from the user and dropped, and only the repo URL
   reaches the flow as `raw_description`.
4. **`meta:` vs `metadata:`.** forge-concept reads `flow.meta.{icon,onboarding}`
   (`profiles.get.ts:33-41`); platform's `validateFlow` declares them under `metadata`
   (`workspaces/.../flow/engine/flow-manifest.ts:62-69`). `-mp` writes `meta:` because
   forge-concept is the host in scope; the schema is a `looseObject`, so platform validates the
   flow and reads no icon.
5. **`placeholder` is freeform-only** (`OnboardingWizard.vue:82-99`), so the key ticket 28 kept
   has no reader for any `-mp` flow.

### Deliberately left undone

- Nothing committed or staged in either repo, per the ticket.
- `contracts/` untouched (ticket 30 is sweeping it concurrently); `skills/`, `templates/`,
  `profiles/` read-only, and no defect found in any of the 27 skills the flows node — every
  `data.skill` resolved first time.
- No rename of `11_build/review.yaml` / `11_build/reviews/<slug>.yaml` (ticket 31).
- `check.py` not extended to cover the gaps above — that is ticket 16's script and its
  scope was set before flows existed; ticket 16's own residue note asked ticket 10 to expect
  an adjustment once real flows landed, and this is the list.
