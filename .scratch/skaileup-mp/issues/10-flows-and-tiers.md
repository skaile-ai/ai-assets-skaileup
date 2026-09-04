# 10: Flows and tiers

**Type:** grilling
**Blocked by:** 08 (01, 06, 07 resolved)
**Status:** blocked

## Question

21 flow YAMLs today; `forge-concept` names 6 of them. Settled in principle: keep the 4 tiers
+ 2 slice loops + 5 shared building blocks (11), reconsider after; and cut tiers 5 → 3
(`mvp` / `standard` / `complex`), folding `simple` into the existing `concept_depth`
parameter and making `cli` a profile rather than a tier.

This ticket can only be worked once the skill inventory exists (tickets 06/07/08), because a
flow is a graph over skills that no longer have the same names or boundaries.

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
