# flows/

One directory per flow: `flows/<id>/<id>.flow.yaml`, with `id: <id>` inside. The loader
keeps a flow only if it has `id`, `nodes` and `edges`; the top-level `requires:` block is
the flow's own install manifest and drives transitive install.

Every skill node (or its group container) declares `data.phase` —
`conceptualization` | `implementation` | `review`. `-mp` does not rely on the name-prefix
fallback in forge-concept's `phaseForNode`, which is why the domain names were free to
change.

The contract has no schema file — it is enforced by [`../scripts/check.py`](../scripts/check.py),
which is the only thing that reads a flow besides the hosts.

**Four flows, and a flow *is* the tier.** `appbuilder-mvp` and `appbuilder-standard` build
an app; `skaileup-concept-only` stops at a specified product; `skaileup-concept-reverse`
starts from an existing repository instead of from scope. There are no sub-flows and no
shared building blocks — every flow the loader finds becomes a card in the onboarding
wizard, so a flow that is not a way to start a project has no business being one.

Each flow carries three group nodes and repeats their `data.phase` on every skill node.
The per-feature loops are **not** in the graph: the host orders nodes only along
`type: flow` edges, so `spec-feature`, `experience-screen`, `build-plan` and `build-implement` state their own
iteration and the graph shows one pass, marked by a comment at the loop's first node.

## Node order

One linear `type: flow` chain per flow. The order encodes the hierarchy: domain language
(brief, glossary) → data model → interaction design → features → screens → mockups →
architecture → build → quality. Node id = skill without its domain prefix, except
`feature` = `spec-feature`, `journeys`/`behaviors`/`screen`/
`shell` = `experience-*`, `interaction` = `experience-interaction` and `interaction-check`
= `quality-interaction`.

|Flow|Order|
|---|---|
|`appbuilder-standard`|scope → onboard → research → brief → glossary → brand → journeys → datamodel → interaction → behaviors → feature → screen → shell → techstack → system → walkthrough → storybook → annotate → feedback → scaffold → database → standards → plan → implement → branch → test → e2e → review → interaction-check → ops-review → release|
|`appbuilder-mvp`|scope → onboard → brief → glossary → journeys → feature → techstack → scaffold → plan → implement → test|
|`skaileup-concept-only`|scope → onboard → research → brief → glossary → brand → journeys → datamodel → interaction → behaviors → feature → screen → shell → walkthrough → annotate → feedback → ops-review|
|`skaileup-concept-reverse`|scope → reverse → standards → brief → glossary → brand → journeys → datamodel → interaction → shell → feature → screen → techstack → system → interaction-check → ops-review|

`screen` follows `feature` in every flow that has it: `spec-feature` lists the screens a
feature needs and `experience-screen` writes them. `shell` follows the `screen` loop in the
two forward flows, where it derives the app-shell navigation from the screens the loop wrote,
and precedes `feature` in the reverse flow, where the frame is drawn around the screens the
codebase already has. `interaction` writes `APP-DESIGN.md` at the
project root once, before the feature loop reads it; `interaction-check` hard-gates on it
and sits in the review group. `appbuilder-mvp` carries neither — it grows no screens — and its `feature` node adds the
roster row for each feature it specifies.
`concept-scope` is the entry of all four — reverse included — and writes the flow id into
`scope.yaml`.
