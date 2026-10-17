---
path: _concept/07_screens/<feature_slug>/<screen>.md
summary: one screen's spec — body sections, links to its feature, elements block
writers: [spec-feature]
---

# _concept/07_screens/<feature_slug>/<screen>.md

One screen a feature needs. The walkthrough renders its whole body in a collapsed "View spec" panel under the synthesized UI, the annotator and feedback pass anchor to its `elements:`, and the build slices implement against it. `spec-feature` writes it as steps 6–7 of `tree/05_features/[featureset]/[feature].md`; `mockup-feedback` may later patch it, anchored to a heading.

## Format

```yaml
---
implements:                      # the feature file(s) this screen belongs to
  - 05_features/auth/login.md
data_entities: [User]
layout: 07_screens/shell.md
elements: []                     # see tree/07_screens/README.md
last_updated: YYYY-MM-DD
---
```

Body: `# Screen: <Title>`, then these sections, in this order, under these exact headings (the renderer recognises them case-insensitively):

1. `### Purpose` — what the user accomplishes here.
2. `### Route` — the path, e.g. `/verify-email`.
3. `### What the User Sees` — the screen in prose; tab names go here in bold.
4. `### Wireframe` — an ASCII sketch in a fenced `text` block; the panel renders the fence verbatim.
5. `### Information Displayed` — what data appears, and its source entity.
6. `### Actions` — what the user can do, naming the destination screen for each action that leaves.
7. `### Situations` — the states this screen is in (default, loading, error, empty, success), one bullet each; mention the seed scenarios `empty` and `edge_cases` here.
8. `### UI Elements` — the catalogue of functional elements; each is declared in `elements:`.
9. `### Template Data` — reference the seed's `populated` scenario (`tree/10_blueprint/datamodel/seed.md`); say "Not applicable" when no scenario fits.

## Writing it

1. **Write one screen spec per screen the feature needs**, at `07_screens/<feature_slug>/<screen>.md`, naming only screens the scope line put IN. Where `APP-DESIGN.md` exists, each editing surface is the OBJ `task → surface` row of the entity it edits (`tree/APP-DESIGN.md § Reading it`); a surface the floorplan lacks goes back to `experience-interaction`, not invented — without the file the screen chooses and says so. Each carries `implements:` pointing back at the feature file and an `elements:` block per `tree/07_screens/README.md` — the block the walkthrough renderers, the annotator and the feedback pass all read, so a screen without it renders as an auto-slugged guess. Where `06_behaviors/<featureset>.md` exists, let its transitions drive the screen: what a transition exposes is a data requirement, what triggers it a user action, its `requires` guard a state-dependent element. Every error state the screen lists becomes an acceptance criterion in the feature spec.
2. **Register both directions**, per `tree/05_features/README.md § Links in both directions`: the feature's `screens:` lists the files just written and each screen's `implements:` names the feature — a one-directional link is a screen nothing can find from its feature.

## Checks

- `implements:` names the feature file and the feature's `screens:` names this file.
- The `elements:` block covers every interactive or structural thing under `### UI Elements`, `### Actions` and `### Information Displayed`, with `target:` on every action that names a destination screen.
- The slug `shell` is not used as a directory or screen name.
