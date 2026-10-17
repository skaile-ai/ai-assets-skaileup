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
`type: flow` edges, so `spec-feature`, `build-plan` and `build-implement` state their own
iteration and the graph shows one pass, marked by a comment at the loop's first node.

## Node order

One linear `type: flow` chain per flow. The order encodes the hierarchy: domain language
(brief, glossary) → data model → features → screens → mockups → architecture → build →
quality. Node id = skill without its domain prefix, except `feature` = `spec-feature`,
`featuresets` = `spec-featuresets`, `journeys`/`behaviors`/`shell` = `experience-*`.

|Flow|Order|
|---|---|
|`appbuilder-standard`|scope → onboard → research → brief → glossary → brand → journeys → datamodel → featuresets → behaviors → feature → shell → techstack → system → walkthrough → storybook → annotate → feedback → scaffold → database → standards → plan → implement → branch → test → e2e → review → ops-review → release|
|`appbuilder-mvp`|scope → onboard → brief → glossary → journeys → featuresets → techstack → scaffold → plan → implement → test|
|`skaileup-concept-only`|scope → onboard → research → brief → glossary → brand → journeys → datamodel → featuresets → behaviors → feature → shell → walkthrough → annotate → feedback → ops-review|
|`skaileup-concept-reverse`|scope → reverse → standards → brief → glossary → brand → journeys → datamodel → featuresets → shell → feature → techstack → system → ops-review|

`shell` follows the `feature` loop in every flow that has both: it derives the app-shell
navigation from the screens the loop wrote. `concept-scope` is the entry of all four —
reverse included — and writes the flow id into `scope.yaml`.
