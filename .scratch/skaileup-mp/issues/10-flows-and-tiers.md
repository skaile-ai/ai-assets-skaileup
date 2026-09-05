# 10: Flows and tiers

**Type:** grilling
**Blocked by:** None — 18 and 21 both resolved 2026-09-05
**Status:** resolved

## Question

21 flow YAMLs today; `forge-concept` names 6 of them. Settled in principle: keep the 4 tiers
+ 2 slice loops + 5 shared building blocks (11), reconsider after; and cut tiers 5 → 3
(`mvp` / `standard` / `complex`), folding `simple` into the existing `concept_depth`
parameter and making `cli` a profile rather than a tier.

This ticket can only be worked once the skill inventory exists, because a flow is a graph over
skills that no longer have the same names or boundaries. **Re-blocked 2026-09-05:** 08 resolved,
but the original blocking list (06/07/08) predates the graduation of tickets 17 (`quality`), 18
(`architecture`+`build`) and 21 (`ops`) — three domains whose skills this ticket's graphs must
name. The test pyramid nodes in particular are load-bearing flow nodes (see the note from ticket
07 below) and ticket 17 decides whether they exist.

**Ticket 01's flow facts, which narrow this ticket considerably.** Real contract: the
`<id>.flow.yaml`-in-`<id>/` layout, `id`/`nodes`/`edges`, node kinds `skill|group|sub-flow|router`
(the engine tracks only `skill`), top-level `requires:`, and `data.phase` ∈ {conceptualization,
implementation, review}. Free, because nothing evaluates them: router `condition` strings,
`meta.category` (every branch is dead — all flows land in `skaileup-conceptualization`), `modes`,
`tier_presets`, `artifact_handoff`, `next_flows`, `data.parameters`, `data.writes`, node geometry,
and most of `flow.schema.json`. A large part of the flow YAMLs is decoration.

Note the tension for the renderer-choice question: router `condition` strings are **never
evaluated**, so today's pick-one renderer routing is not actually routing anything.

Decide:

- The final flow list and each one's node graph over the new skills.
- Tier reduction mechanics: what `scope-project` writes into `_concept/_meta/scope.yaml`
  now, and what reads it.
- Whether the 5 shared building blocks survive as sub-flows or whether ~30 skills is small
  enough that the tiers can inline them without duplication.
- How router nodes and `parameters:` express the mockup renderer choice from ticket 06.
- Whether flows stay YAML at all, or whether a prose router (`ask-matt`-style) covers the
  human case and YAML is kept only for the machine consumers ticket 01 identified.
- Names: `forge-concept` hardcodes `appbuilder-{mvp,simple,standard,complex}` and
  `skaileup-slice-{concept,impl}`. Renaming is allowed — record what breaks.

## Answer

**17 flows -> 4, and `tier` retires from the vocabulary: a flow *is* the tier.**

### The unification (Q13/Q17)

`tier` and `flow` have been 1:1 all along -- `scope.yaml.flow_to_run` was the mapping -- so
they collapse into one word. `scope.yaml` records **`flow:`**; the eleven skills that read
`tier` read `flow`; `CONTEXT.md` loses its **Tier** entry and **Flow** absorbs the sizing
sense. The menu *is* the flow list.

This was forced by measurement, not preference. **`appbuilder-standard` and
`appbuilder-complex` reference the identical six sub-flows and differ by exactly eight skill
names** -- `design-brand-voice`, `impl-quality-audit`, `impl-quality-eval-code`,
`mockup-walkthrough-framework`, and the four `ops-project-*`. Every one is deleted by tickets
08/17/06 or ruled out of scope, so after the port `complex` has no content of its own. Keeping
it would have meant either a byte-identical copy under a second name, or inventing scope to
defend a name. With one word there is no place left to record a depth that has no graph.

### The four flows

**`appbuilder-mvp`** (9 nodes, linear, no design layer, no mockup, no data layer):
`concept-scope` -> `concept-onboard` -> `concept-brief` -> `spec-featuresets` ->
`architecture-techstack` | `build-scaffold` -> `build-plan` -> `build-implement` |
`quality-test`

**`appbuilder-standard`** (27 nodes):
*conceptualization* `concept-scope` -> `concept-onboard` -> `concept-brief` ->
`concept-research` -> `design-brand` -> `experience-journeys` -> `spec-featuresets` ->
`experience-behaviors` -> `experience-shell` -> `spec-feature` -> `mockup-walkthrough` ->
`mockup-storybook` -> `mockup-annotate` -> `mockup-feedback` -> `architecture-techstack` ->
`architecture-system` -> `architecture-datamodel`;
*implementation* `build-scaffold` -> `build-database` -> `build-plan` -> `build-implement` ->
`build-branch`;
*review* `quality-test` -> `quality-e2e` -> `quality-review` -> `ops-review` ->
`quality-release`

**`skaileup-concept-only`** (14 nodes): standard's conceptualization half, stopping before
`architecture`, ending at `ops-review`. No `mockup-storybook` -- it authors code, which this
flow does not do.

**`skaileup-concept-reverse`** (9 nodes, the one flow not entering at `concept-scope`):
`concept-reverse` -> `quality-standards` -> `experience-journeys` -> `spec-featuresets` ->
`experience-shell` -> `spec-feature` -> `architecture-system` -> `architecture-datamodel` |
`ops-review`. It **gains `spec-featuresets`**, which it lacks today: without it the
`spec-feature` loop has nothing to iterate over, and screens were the one thing its
`experience-screens` node existed to write.

### Sub-flows die; the flow list is a user-facing menu (Q1)

**New finding this ticket turned on.** `profiles.get.ts:10` turns *every* loaded flow into an
onboarding profile and `OnboardingWizard.vue:41` renders `v-for="(prof, id) in
profilesData.profiles"` **with no filter**. So today's 17 flows are 17 project-start cards,
including `quality-gate`, `architecture`, `impl-build-setup`, `concept-discovery`,
`mockup-feedback` and the three slice flows. The "shared building blocks" were menu pollution.

So **every flow is addressable, and the six building blocks inline into the tiers**, deleting
the `sub-flow` node kind from `-mp` (27 of 175 nodes). The 2026-07 extraction was right for a
graph of 130 skill nodes over 69 skills; at 29 skills the repetition is cheaper than the
indirection. `skaileup-slice-{concept,impl}` die with it -- after ticket 07, slice-concept is
**one node** (`spec-feature`), and a one-node flow is not a graph.

### Three steps in the simpler tier that could not run

Asked to check whether every step is needed at the smaller size, two turned out to be worse
than unneeded:

1. **`appbuilder-mvp`'s mockup node hard-refuses on every run.** `mockup-walkthrough-text`
   gates on `_concept/experience/screens/` holding >=1 screen with `00_layout/shell.md`
   **Required** (`SKILL.md:132,162-163`), stated failure *"No screen specs exist yet -- run
   `screens` first"* (`:124`). `appbuilder-mvp` has **no skill that writes a screen**. The node
   has never been runnable. **Dropped**, not repaired: giving mvp the loop would make it
   standard, and a degrade-to-featuresets mode invents a second renderer to save a node whose
   output nobody looks at before the app exists.
2. **`build-scaffold` would inherit a gate mvp cannot satisfy.** `impl-build-foundation:95-98`
   lists `03_brand/tokens.json` under *"Hard gates (all must exist)"*, and mvp has no brand
   node; ticket 18 merges `foundation` into `build-scaffold`. **The brand step becomes
   conditional** -- apply tokens if present, else stack defaults -- which is ticket 03's rule
   (state the constraint at the step, put a check behind it) rather than frontmatter that
   blocks a whole flow. -> ticket 25.
3. **mvp has no data layer** (no `datamodel`, no `migrate`, no `seed`). **Left out
   deliberately**: `build-scaffold`'s template supplies the ORM default and the schema grows
   inside `build-implement`. Adding two nodes would have been the other defensible answer; the
   lean shape is the one thing separating mvp from standard once `complex` is gone.

### One forced reordering

**The mockup moves after the feature loop.** Ticket 08's W1 made `spec-feature` the sole
writer of screen specs and left `experience-shell` writing only the shell, while
`mockup-walkthrough` renders `screens/**`. In today's order (screens -> mockup -> ... -> slice
loop) the mockup renders one shell and nothing else -- the same defect as mvp's node, seen
from the other side. Also reordered: **`features` before `behaviors`** in both
`appbuilder-standard` and `appbuilder-complex` (the brief found the inversion in two flows,
not the one ticket 08 named), matching `experience-behaviors`' own gate.

### Corrections to the record

Three host facts the brief and two closed tickets had wrong:

- **Routers are live and interactive.** `condition` strings are never evaluated (ticket 01
  right), but the router *node* is real: `route-choice.post.ts` persists the user's pick,
  `computeUnchosenSkips` prunes unchosen branches so the join unblocks,
  `useFlowState.ts:165` exposes it. The routing is **manual, not conditional** -- ticket 06's
  *"not actually routing anything"* understates it. `-mp` still ships **zero routers**: ticket
  06 collapsed the renderer pick-one and Q3 made test levels data, leaving no survivor.
- **Group nodes are load-bearing.** `flow-layout.ts:87-93` draws swimlanes from them and **the
  group's phase overrides the node's own** (`groupPhase.get(n.parentNode) || phaseForNode(n)`);
  `FlowGraph.vue:218` positions lanes from group geometry. So `-mp` keeps **three group nodes
  per flow** *and* declares `data.phase` on every skill node (ticket 04) -- redundant by
  design, written from one table so they cannot disagree.
- **A flow's `requires:` is confirmed live**: `workspaces/core/src/manifest.ts:428-431` reads
  `.flow.yaml` as a whole-doc manifest and turns the block into the catalog entry's deps.
  It stays exact and **loses its `flow:` refs** -- with sub-flows gone there is nothing to
  delegate to, so each manifest is genuinely self-contained rather than
  self-contained-plus-transitive.

### The parameters contradiction, resolved against ticket 17

Ticket 17 specified `quality-test` with `parameters: {levels: [unit]}` per tier; ticket 08
ruled **no `parameters:` blocks**. `data.parameters` has **exactly one live read in the whole
host** -- `parameters.flow` as a sub-flow child-id fallback (`flow-manager.ts:475`,
`shared/flow-extended.ts:52`). **08 wins.** `quality-test` reads `flow` from
`01_meta/scope.yaml` and picks its own levels -- ticket 07's move (tier stops routing, becomes
depth inside the skill) applied one level up. A parameter nothing reads is worse than a skill
body that reads the file, because it looks like configuration. -> ticket 23.

### Decoration deleted

Kept, because they have readers: `globals.research_depth` (-> wizard slider), `meta.icon`,
`meta.onboarding.*`, `name`, `description`, `requires`, `data.phase`, `parentNode`.
Deleted: `globals.{approval_mode,subagent_mode,verbosity}` (0 readers anywhere),
`globals.concept_depth` + its five `${concept_depth}` threads (0 readers -- it dies with
`simple`, since the depth it never expressed is now `flow`, read from `scope.yaml`),
`meta.category` (read at `flow-manager.ts:146-150`, all six values fall through to one
default), and every `${...}` interpolation (**no resolver exists** in either host).

**Flows stay YAML.** The question of a prose router instead is answered by the menu finding:
the flow list is what the wizard renders, so the YAML *is* the human surface on the primary
host. The `skaileup` router skill remains fog, unaffected.

### The per-feature loop stays out of the graph (Q21)

The host honours **exactly one edge type** -- both `run.post.ts:62` and
`flow-extended-state.ts:48` filter `e.type === "flow"`; `optional`, `parallel` and
`review-loop` are inert. And the loop has **never been machine-expressed**:
`appbuilder-standard:11-12` carries it as a comment (*"the slice-loop sub-flow node runs once
per feature; the linear graph below shows one iteration"*). `stepwise`'s self-edge with
`max_iterations: 50` is read by nothing. So the loop lives in the **skill bodies** --
`spec-feature` and `build-implement` each state they run per feature -- with a one-line
comment at the loop's first node. Ticket 12 rejected `boundary:` as edge data on exactly this
ground; `review-loop` is the same bargain with an older name.

### `scope.yaml` and its writer (Q4/Q14)

**`skaileup-scope-scope-project` was owned by no ticket** despite being the 7x entry node, the
most-used skill in the collection, and the sole writer of the artifact this ticket reshaped.
Ruled here: it survives, **renamed `concept-scope`** (a domain prefix like everything else,
and it writes `_concept/`), narrowed to writing `01_meta/scope.yaml` and no longer choosing the
flow -- on the forge-concept path the wizard's profile *is* the flow. It cannot die: the
orchestrator path has no wizard and eleven skills read what it writes. -> ticket 26.

Schema: **`flow` . `project_type` . `reasoning` . `signals` . `chosen_at`**. Dropped
`flow_to_run` (a file naming the flow that wrote it is a cycle), `shape` (folded into
`project_type`), `override` (an override leaving no different value is not data) and
`chosen_by`.

### `cli` demotes to `project_type`, not to a tier (Q5)

`contracts/profiles/*.yaml` has **zero in-body readers** -- `DOMAIN.md:36` claims
`impl-architecture-techstack` reads them; it actually reads `templates/*/TEMPLATE.md`. A live
axis already existed: `project_type: cli-tool` in `onboarding-profile-v1.yaml:18`, read by
`concept-onboard` and `seeds`. **The tier was the duplicate**, and `appbuilder-cli`'s own node
params (`project_type: cli`, `skip_ui_shell: true`) are inert, so it never routed anything
either. `appbuilder-cli` dies. This also hands ticket 18's root-level `profiles/` its first
real reader: `concept-scope` resolves `project_type` -> `profiles/<project_type>.yaml`.

### Variants: two of four survive (Q7)

Kept: **`skaileup-concept-only`** and **`skaileup-concept-reverse`**. Deleted:
**`skaileup-implementation`** (7 nodes, **100% sub-flow + group** -- inlining leaves it a
verbatim copy of the tiers' back half) and **`skaileup-stepwise`** (duplicates `standard` with
different pacing, and pacing is what ticket 12 moved into warm/cold boundaries inside the
skills). Cost: `input_style: freeform` loses its only user, so `-mp` exercises two of the
host's three onboarding styles -- `structured` x3, `repo` for `concept-reverse`.

`concept-only` **gains the `spec-feature` loop** (ticket 08's handoff, F7): without it the flow
writes featuresets and no screens at all, since the loop body is the only screen writer.

### `concept-reverse` nodes its writers rather than calling them (Q22)

Ticket 21 described it as a thin orchestrator that *calls* five writers; the flow also nodes
them today, so doing both runs each twice. **The flow nodes them**; `concept-reverse` keeps
repo discovery, stack detection (`references/detection/`) and confidence grading and writes
only detection output plus grounding. A skill that internally calls five others is invisible to
the host's node-by-node UI and unresumable halfway. -> ticket 26.

### `quality-release` placement (Q15)

**Last node of `appbuilder-standard`, phase `review`**, after the inlined `quality-gate` block.
Not in `mvp` -- an MVP has no goals doc worth grading against.

### What breaks

| site | breakage |
|---|---|
| `forge-concept/tests/integration/skaileup-flows.test.ts:29-36` | `appbuilder-simple`, `appbuilder-complex`, `skaileup-slice-concept`, `skaileup-slice-impl` no longer exist |
| same, `:38` | `concept-goals` no longer exists (ticket 08) -- **already broken before this ticket**, which falsifies the map's own destination line ("that test with one repo URL changed") |
| `forge-concept/templates/dev/skaile.yaml:10-15` | the same six names |
| `test/unit/flow-extended{,-state}.test.ts:14-15,39-40,13,55` | fixtures named `skaileup-slice*` -- synthetic, so they still pass, but the names become fictional |
| 11 skills reading `scope.tier` | field is now `scope.flow`; all eleven are rewritten by tickets 23/25/26, so this is coordination, not breakage |

Newly unexercised in the host, none of it an error: `phaseForNode`'s name-prefix fallback
(every node declares `phase`), `meta.category`, the router machinery, `input_style: freeform`.

**Not a register entry.** Editing the acceptance test's `FLOWS`/`SKILLS` arrays and the dev
template's flow list is an *acceptance-harness* edit, not a change to host behaviour -- the
destination names that test as the acceptance criterion, so keeping it truthful is inside this
map, unlike the behaviour changes deferred to the successor effort.

Graduated **28** (write the four flow YAMLs) and **29** (the acceptance run), which empties the
opt-in/acceptance fog patch.

## Note from ticket 06

**One of the two blockers on this ticket is now resolved, and it changed the flow shape.**

- **The pick-one sibling-node pattern disappears.** `appbuilder-standard.flow.yaml` today
  carries two optional nodes for one decision — `mock-astro` ("Astro Walkthrough Mockup (via
  router)") and `mock-static-fallback` ("Static HTML Walkthrough (router default)"). With one
  `mockup-walkthrough` skill there is **one node**. Check whether any other pick-one in the
  flows has the same shape and can collapse the same way.
- **The renderer choice becomes tier data, which is this ticket's subject.** Default by tier
  (`appbuilder-mvp`/`simple` → `static-html`, `standard`/`complex` → `astro`), override in
  `onboarding.yaml`. If ticket 10 collapses 5 tiers → 3, the defaults table has to move with it.
- **Flow references that die with their skills:** `mockup-walkthrough-text` (7 refs),
  `mockup-walkthrough-framework` (7), `mockup-walkthrough-lit` (1),
  `mockup-component-isolated-html` (2+3), `mockup-walkthrough-migrate-elements`. The
  `skaileup-concept-only` flow's only renderer is `mockup-walkthrough-text` — it needs
  repointing at `mockup-walkthrough`, and that flow is also the one real argument for keeping a
  no-Node component view (see ticket 06's `isolated-html` note).
- **`mockup-feedback.flow.yaml` shrinks from 4 nodes to 2** (annotate | feedback).

## Note from ticket 07

Two consequences land here.

- **Tier stops branching the flows at the slice loop.** `slice_loop.md`'s table routed each
  tier to a different *entry skill* (mvp → `plan-vertical`, simple → `align`,
  standard/complex → `brainstorm`); ticket 07 collapsed each side to one entry skill, so
  tier becomes **depth inside the skill**, not a different node. Together with ticket 06's
  renderer-choice-becomes-data ruling, two of the reasons the flows fan out are gone.
- **The node set shrinks.** 16 slice skills became four — `spec-feature` · `build-plan` ·
  `build-implement` · `build-branch` — and `impl-plan-supervised`, `impl-slice-implement-page`
  and `impl-quality-debug-handoff` have no successor node at all. The test pyramid
  (`quality-test-{unit,integration,e2e}`) stays **flow nodes after the slice** rather than
  calls from inside `build-implement`, so those nodes are load-bearing.

## Note from ticket 17

The `quality` domain resolves to four skills (`quality-review` · `quality-test` ·
`quality-e2e` · `quality-standards`), which changes five flows:

- **`quality-test` takes a level parameter**, `parameters: {levels: [unit]}` /
  `[unit, integration]`. Today's per-tier subsets (`{u}` / `{u,e}` / `{u,i}` / `{u,i,e}`) were
  the argument for merging `test-unit` + `test-integration` in the first place — an arbitrary
  set selected per tier is data. Precedent already in the tree: `q-test-e2e`'s
  `parameters: {mode: '${e2e}'}`.
- **`quality-gate` goes from five nodes to three** — `quality-test` → `quality-e2e` →
  `quality-review`. `q-eval-code`, `q-audit` and `q-ready` have no successor skill here
  (`ready` → ticket 21).
- **`appbuilder-complex` loses `q-eval-code` and `q-audit`** (`:400`, `:411`). It was running
  the same three sub-agents three times over the same code.
- **`skaileup-concept-reverse` loses its `standards-inject` node** (`:113`) — discover only.
- **`skaileup-stepwise`'s `q-ready`** (`:158`) waits on ticket 21's ruling on `ready`.

## Note from ticket 21

The `ops` domain resolves to **one** skill (`ops-review`), plus `concept-reverse` (renamed from
`ops-reverse-engineer`) and `quality-release` (`ops-eval-product`, moved to `quality`). Node
changes, and one repair nobody owned:

- **`quality-gate` loses another node beyond 17's three.** `ops-review` and `ops-sync` merge, so
  `quality-gate.flow.yaml:111` + `:122` collapse to one node, and `:100`'s `ops-trace` folds into
  the same skill. With 17's cut, `quality-gate` is `quality-test` → `quality-e2e` →
  `quality-review` → `ops-review`, and its `q-ready` (17's open item) is answered: `ready` is a
  step inside `ops-review`, not a node.
- **`skaileup-stepwise`'s `q-ready` (`:158`)** — same answer: no node, or repoint at `ops-review`.
  17 left this waiting on 21; it is settled.
- **`skaileup-concept-only:280`** keeps its `ops-review` node, unchanged name.
- **`skaileup-concept-reverse:68`** repoints from `ops-reverse-engineer` to **`concept-reverse`**.
  It is that flow's entry node, and ticket 13 already noted this flow is the one addressable flow
  that does not enter at `scope-project`.
- **`quality-release` has zero flow nodes today** and needs one — a release gate after
  `quality-gate`, grading the whole app against `brief.md` + `goals.md`. `quality-gate.md:21`
  already describes it in prose. This ticket rules it survives; where it runs is yours.
- **`data.phase` for the three:** `ops-review` → `review`, `quality-release` → `review`,
  `concept-reverse` → `conceptualization`.

**The repair nobody owned.** The four out-of-scope `ops-project-*` skills are the **only** `ops-*`
nodes in `appbuilder-complex.flow.yaml` (`:304-344`, edges `:506-523`). Cutting them dangles that
flow's tail, and no ticket claimed the fix — recorded in the map's Out of scope entry, which also
named only two of the four until ticket 21 corrected it.
