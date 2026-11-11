# Demo workspace: Lunch Roulette

A small fictional app, a team lunch planner: an organizer opens a poll, members vote on
places, the app announces the pick and draws a tie. The folder is a complete workspace
filled the way the skills of this collection would fill it, so a UI that renders a concept
has something real on every page.

- `_concept/`: the numbered tree `01_meta … 11_build`, one file per part the nodes of `tree/`
  describe, and a review with open findings. Each feature spec names its parent issue
  (`tracker: { issue: 101 }` … `104`) and each acceptance-criteria row its ticket (`#111` …
  `#117`); the issues live in the tracker, not here (ADR 0036).
- `_concept/proposals/`: one file per proposing run. They hold a pending glossary term (`veto`),
  promoted entries (a data-model field, a screen's `implements:` link, two roster ideas and the
  `APP-DESIGN.md` rule MSG-2), and two rejected ones: a scope `depth` and weighted votes for a
  feature spec, each with its reason.
- `APP-DESIGN.md` and the decision log `docs/adr/` (three records, one of them a `pattern` two
  features follow) sit beside `_concept/`. The words live in the root `GLOSSARY.md`
  (split mode, the default: `scope.yaml` names no `glossary`), and `_concept/glossary.md` holds
  only the ontology of the same terms.
- `skaile.yaml` is a valid workspace config: a `url` source for this collection (unpinned, so its
  `main`) and every flow, contract and skill as a dependency.

**Left out:** `_concept/09_mockup/storybook/`, the mockup stage's Vue Storybook package. It is a
full npm package with its own dependencies and does not belong in a fixture. The mockup pages
of a host show their empty state. A few optional or whole-app parts (extra research files,
`release.yaml`, `interaction.sarif`) are left out too; `DEMO_NOT_SHIPPED` in
`scripts/check.py` lists each with its reason.

**Keeping it true:** `python scripts/check.py` validates the demo. Every file maps to a node of
`tree/`, markdown frontmatter follows `tree/frontmatter.schema.json`, `scope.yaml`,
`stories.yaml` and the brand tokens validate against their schemas, and the data
model's `model.yaml` and `seed.yaml` pass `bunx @skaile/model@1 check`. A change to a node's
format, a skill's `produces` or a schema updates this folder in the same PR.

**Used by skaile-forge:** its dev launcher copies everything here except `README.md` and
`skaile.yaml` into its dev workspace and writes its own `skaile.yaml`, whose source is the
absolute path of the local checkout of this collection, so an edit to a skill applies at once.
