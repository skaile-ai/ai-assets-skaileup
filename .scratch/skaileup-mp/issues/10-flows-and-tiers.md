# 10: Flows and tiers

**Type:** grilling
**Blocked by:** 06, 07, 08 (01 resolved)
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
