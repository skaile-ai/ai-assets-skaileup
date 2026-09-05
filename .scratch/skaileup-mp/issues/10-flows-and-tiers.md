# 10: Flows and tiers

**Type:** grilling
**Blocked by:** 18, 21 (01, 06, 07, 08, 17 resolved)
**Status:** blocked

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

_(pending)_

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
