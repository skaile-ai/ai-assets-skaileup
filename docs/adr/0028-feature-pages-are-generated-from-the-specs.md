# 0028 — Feature pages are generated from the specs

**Status:** accepted

Adds a feature layer to the mockup's Storybook package. Amends
[ADR 0026](0026-the-mockup-stage-is-one-vue-storybook-package.md) D1: the package has six story
layers, and the first, `Features/<featureset>/<feature>`, is generated rather than written.

## Context

The package had five layers (Floorplans, Screens, Entities, App, Journeys) and no feature layer.
A reviewer on `Screens/poll` saw layout but not which feature it serves, why that feature
exists, or which criteria it must meet; the only link back to the spec was a code comment in
the `.vue` file. The purpose already exists in four places, so no new authoring is needed:

- the roster's `outcome` column in `05_features/featuresets.md`;
- the dossier's `## Framing` in `08_dossiers/<slug>/index.md`;
- the spec's `## Scope` and criteria bullets;
- the EARS text in `04_journeys/stories.yaml`.

Copying any of these into story files would add another copy, and a second copy is the one that
drifts.

## Decision

**D1 — One generated `Features/<featureset>/<feature>` canvas story per feature spec.**
`scripts/gen-concept.ts` reads `_concept/` and writes `src/generated/concept.json` and one
`src/features/<featureset>/<feature>.stories.ts` per `05_features/<featureset>/<feature>.md`.
Each story renders the scaffold's `FeatureDoc.vue` with the spec path as its one prop. Both
outputs are gitignored and regenerated from `.storybook/main.ts` on every start and on a change
while `storybook dev` runs, the way `tokens.css` already is. The sidebar lists Features first.

**D2 — The sources are the existing ones.** The page shows the roster outcome, the dossier's
`## Framing`, the spec's `priority`, `permissions:`, `## Scope` and criteria with their EARS
text from `stories.yaml`, and links to the feature's screen and journey stories, joined in both
directions from the spec's `screens:` and the screens' `implements:`. No `## Purpose` section is
added to the feature spec: the roster outcome and the dossier framing already carry it.

**D3 — Screen stories bind through `screenDocs`.** A screen story's `meta` carries
`parameters: { docs: screenDocs('<screen_id>') }`, which puts the screen's `### Purpose` and the
features it implements, with links, on its Docs page. It is the only line that binds a screen
story to its features.

**D4 — Triage routes `features-` story ids to the feature spec.** A note whose story id starts
`features-<featureset>-<feature>--` routes to `05_features/<featureset>/<feature>.md`. The patch
scope is unchanged: a feature spec is `spec-feature`'s artifact, so the note becomes a
`needs_manual` entry quoting what was asked.

## Options rejected

- **Hand-written per-feature docs by `mockup-storybook`.** They drift from the spec.
- **A `## Purpose` section in the spec.** A third copy of what the roster outcome and the
  dossier framing already say.
- **Storybook tags per feature.** CSF tags are static, so they would be a hand copy of
  `implements:`.
- **MDX docs pages.** They are rendered by React, so an annotation on one names no Vue component.

## Consequences

- The scaffold gains two dependencies, `yaml` and `@storybook/addon-links`.
- Features sorts first in the sidebar, ahead of Journeys, App, Screens, Entities and Floorplans.
- `## Framing` is a pinned dossier heading: the generator reads the body under it, so a dossier
  that names it differently shows no Why block.
