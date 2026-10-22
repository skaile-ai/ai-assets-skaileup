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

**Two advisory recipes.** `skaileup-greenfield` starts from an idea and walks the whole
chain, concept to release grade; `skaileup-reverse` starts from an existing repository and
writes the concept out of what the code holds. The onboarding wizard shows these two cards
and nothing else, so a flow that is not a way to start a project has no business being one.
A flow is a recommended order, not a gate and not a size: how deep a project goes is
`depth` in `scope.yaml` (`tree/01_meta/scope.md`), a skill resolves its own inputs instead
of waiting on its predecessor, and `skaileup` reaches any skill directly from the middle of
a project. `quality-design` is on demand and sits in neither graph.

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
|`skaileup-greenfield`|onboard → research → brief → glossary → brand → journeys → datamodel → interaction → behaviors → feature → screen → shell → techstack → system → storybook → feedback → scaffold → database → standards → plan → implement → branch → test → e2e → review → interaction-check → ops-review → release|
|`skaileup-reverse`|reverse → standards → brief → glossary → brand → journeys → datamodel → interaction → shell → feature → screen → techstack → system → interaction-check → ops-review|

`screen` follows `feature` in both flows: `spec-feature` lists the screens a feature needs and
`experience-screen` writes them. `shell` follows the `screen` loop in the greenfield flow,
where it derives the app-shell navigation from the screens the loop wrote, and precedes
`feature` in the reverse flow, where the frame is drawn around the screens the codebase
already has. `interaction` writes `APP-DESIGN.md` at the project root once, before the
feature loop reads it; `interaction-check` hard-gates on it and sits in the review group.
Neither flow has a scope node: `skaileup` writes `flow` into `scope.yaml` when a skill
first needs it.
