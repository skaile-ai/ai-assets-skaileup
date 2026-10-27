# Demo workspace: Lunch Roulette

A small fictional app, a team lunch planner: an organizer opens a poll, members vote on
places, the app announces the pick and draws a tie. The folder is a complete workspace
filled the way the skills of this collection would fill it, so a UI that renders a concept
has something real on every page.

- `_concept/`: the numbered tree `01_meta … 11_build`, one file per part the nodes of `tree/`
  describe, with a `proposed` scope entry, a `proposed` glossary term and data-model field, a
  rejected decision record, and a review with open findings.
- `APP-DESIGN.md` (with one proposed entry) and `CONTEXT.md` sit beside `_concept/`.
- `skaile.yaml` is a valid workspace config: a `url` source for this collection (unpinned, so its
  `main`) and every flow, contract and skill as a dependency.

**Left out:** `_concept/09_mockup/storybook/`, the mockup stage's Vue Storybook package. It is a
full npm package with its own dependencies and does not belong in a fixture. The mockup pages
of a host show their empty state. A few optional or whole-app parts (extra research files,
slice dossiers, `release.yaml`, `interaction.sarif`) are left out too; `DEMO_NOT_SHIPPED` in
`scripts/check.py` lists each with its reason.

**Keeping it true:** `python scripts/check.py` validates the demo. Every file maps to a node of
`tree/`, markdown frontmatter follows `tree/frontmatter.schema.json`, and `model.json`,
`seed.json`, `scope.yaml`, `stories.yaml`, `trace.yaml` and the brand tokens validate against
their schemas. A change to a node's format, a skill's `produces` or a schema updates this folder
in the same PR.

**Used by skaile-forge:** its dev launcher copies everything here except `README.md` and
`skaile.yaml` into its dev workspace and writes its own `skaile.yaml`, whose source is the
absolute path of the local checkout of this collection, so an edit to a skill applies at once.
