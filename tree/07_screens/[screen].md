---
path: _concept/07_screens/<screen>.md
summary: one screen on its own — floorplan, region bindings, tier overrides, elements
owner: [experience-screen]
may_propose: [spec-feature, quality-design]
---

# _concept/07_screens/<screen>.md

One screen, described on its own: the floorplan it is laid out in, what each region shows, how it deviates from the app's information tiers, what a person does there, and the elements the walkthrough and the build anchor to. A screen belongs to no feature: it names the feature files it realises in `implements:`, and a feature names its screens back (`tree/05_features/README.md § Links in both directions`). The walkthrough renders the floorplan's geometry from the region bindings and the body in a collapsed "View spec" panel, the annotator and feedback pass anchor to `elements:`, and the build slices implement against it. `experience-screen` owns the file; `mockup-feedback` edits it only as human-approved patches (`### Patching (mockup-feedback)`), which is no proposal and no ownership; `spec-feature` and `quality-design` propose entries only.

## Format

```yaml
---
screen_id: inbox                 # equals the filename stem; ^[a-z][a-z0-9-]{1,47}$; `shell` is reserved
title: Inbox
implements:                      # feature files this screen realises; [] when it is described from code with no feature
  - 05_features/<featureset>/<feature>.md
floorplan: master-detail         # a floorplan id of kind `screen` under rulebook/floorplans/
posture: sovereign               # sovereign | transient | auxiliary
density: compact                 # compact | default | comfortable
regions:                         # floorplan region id (its README § Regions) -> what this screen puts there
  list: { shows: <glossary term id>, representation: row }
  detail: { shows: <glossary term id>, representation: peek }   # master-detail: the detail never replaces the object's page
tier_overrides:                  # sparse: only deviations from APP-DESIGN.md § Information hierarchy
  - { object: <term id>, attribute: <name>, tier: 1, region: list, reason: "<why>" }
elements: []                     # see tree/07_screens/README.md
last_updated: YYYY-MM-DD
---
```

- `screen_id` is the identity every other artifact uses: a `target:` in an `elements:` block, `data-spec-screen` in the walkthrough, a feature's `screens:` path, a prototype directory. Rename a screen and each of them follows, or the link dangles.
- `implements:` entries are plain strings when confirmed. A proposed entry is `{ path: 05_features/<fs>/<f>.md, status: proposed, proposed_by: spec-feature, proposed_on: YYYY-MM-DD }`; `experience-screen` confirms it by writing the plain string, and a proposed entry counts for the cross-link until then.
- A `### Open` bullet from `quality-design` ends with `(proposed by quality-design, YYYY-MM-DD)` and names its `DC-<n>`; `experience-screen` settles it like any `### Open` bullet and records a rejection in `_concept/10_blueprint/decisions.md`, so it is not proposed again.
- `floorplan` is the id of a screen floorplan, never of a shell frame; `posture` and `density` default to the app's `APP-DESIGN.md § Screen defaults` row for that floorplan, else to the floorplan README's own frontmatter. Both keys are always written, so the screen reads alone; a value that differs from its default carries a `# reason` comment on the line.
- `regions` keys are region ids from the floorplan's `§ Regions` (`rulebook/floorplans/<id>/README.md`). `shows` is a glossary term id, `representation` one of the object's representations from `APP-DESIGN.md § Objects` (`row`, `card`, `chip`, `peek`, `page`). A region that holds only controls or a status line (`toolbar`, `activity-strip`) stays unbound and its content goes under `### Information Displayed`; the `shell` region is never bound.
- `tier_overrides` rows name an object by glossary term id, an attribute of it, the tier it takes on this screen, the region it appears in and the task reason. A screen with no deviation writes `tier_overrides: []`.
- An element may carry `region: <floorplan region id>`, which the walkthrough uses to place its label inside that region of the frame (`tree/07_screens/README.md § Schema`).

Body: `# Screen: <Title>`, then these sections, in this order, under these exact headings (the renderer recognises them case-insensitively):

1. `### Purpose` — what the user accomplishes here, and the task that decided the floorplan.
2. `### Route` — the path, e.g. `/inbox`, or `Not applicable` where the project has none.
3. `### Information Displayed` — what data appears per region, its glossary term and its tier; a tier-3 attribute names the peek, popover or disclosure that holds it.
4. `### Actions` — what the user can do, naming the destination screen id for each action that leaves; an edit names the host the `APP-DESIGN.md § Objects` editor cell gives.
5. `### Situations` — the states this screen is in (default, loading, error, empty, success), one bullet each; mention the seed scenarios `empty` and `edge_cases` here.
6. `### UI Elements` — the catalogue of functional elements; each is declared in `elements:`.
7. `### Template Data` — reference the seed's `populated` scenario (`tree/10_blueprint/datamodel/seed.md`); say "Not applicable" when no scenario fits.
8. `### Open` — only while a choice waits for an owner: one bullet per question, `- Q-<screen_id>-<n>: <question> — Recommendation: <option> — <one-line consequence>`; `ops-review` reports a bullet without the `Recommendation:` label as an open question with no recommendation.

## Writing it

### Specifying (experience-screen)

1. **Resolve the facts** (`tree/README.md § How a skill runs`, rule 1). Read, in any order and none required: `_concept/02_grounding/findings/screens.md` for the entry on this screen; where the code holds the screen and the findings do not, run `concept-reverse` scoped to `screens` with the screen's paths. Read the features that name it (`_concept/05_features/`, `screens:`), `_concept/glossary.md` for the objects it shows, `_concept/10_blueprint/datamodel/model.json` for their attributes, `APP-DESIGN.md` per `tree/APP-DESIGN.md § Reading it`, and `_concept/07_screens/shell.md` for the frame. A screen is writable with none of them; what is missing becomes a question in step 3 or a `proposed` entry in step 6.
2. **Sort before asking** (rule 4). Restate what exists as a draft: purpose, route, the objects it shows, what a person does, the states. Mark inferred facts `[inferred]` and the gaps as gaps. Where the user asks to see the layout first, take step 5 before going on.
3. **Batch-ask what the evidence leaves open** (`tree/README.md § How a skill runs`, rules 2 and 3): the screen's task, the floorplan, posture and density where the defaults do not settle them, and tier calls that deviate. Without a user, write each recommendation with its `### Open` bullet instead.
4. **Choose the floorplan** with `rulebook/rules.md § P18` and the `kind: screen` floorplan READMEs: the task, the object axes and the navigation model decide, not habit. Posture and density come from the `APP-DESIGN.md § Screen defaults` row for the floorplan, else from the floorplan README. Where a floorplan has no row, or `APP-DESIGN.md` is absent, the rulebook defaults decide (`rulebook/defaults.md`) and the choice is appended to `APP-DESIGN.md § Screen defaults` as a proposed row (`tree/APP-DESIGN.md § Format`), creating the file with only that entry when it is absent (`tree/README.md § Ownership`); the completion summary names `experience-interaction` as the owner who settles it. A screen that fits no floorplan is a signal to add one (`rulebook/README.md § Adding or retiring`); a screen never draws an unnamed layout.
5. **Prototype when the choice is spatial** (rule 6): offer `tree/09_mockup/prototypes/[screen]/a.md` before specifying, two variants on request; the user's pick fixes `floorplan:` and `regions:`.
6. **Bind regions and settle tiers.** Bind each object-holding region of the chosen floorplan (`§ Regions`) to a glossary term and a representation from `APP-DESIGN.md § Objects`. Take every attribute's tier from `APP-DESIGN.md § Information hierarchy` and write `tier_overrides` only for a deviation, each with its task reason, checked against `rulebook/rules.md § P21`: tier 3 stays behind a peek, popover or named disclosure, so an override that lifts it into a row is an exception for `APP-DESIGN.md § Exceptions`, not an override. A term the glossary lacks becomes a `proposed` glossary entry (`tree/glossary.md § Format`) and the screen uses its id; an attribute the model lacks becomes a proposed field (`tree/10_blueprint/datamodel/model.md`). An editing task whose host the object map lacks is appended to `APP-DESIGN.md § Objects` as a proposed row, creating the file when it is absent, and the completion summary names `experience-interaction` as its owner: the screen does not invent a host.
7. **Write the body and the `elements:` block** per `tree/07_screens/README.md`, covering every interactive or structural thing under `### UI Elements`, `### Actions` and `### Information Displayed` — a screen without the block renders as an auto-slugged guess. Where `06_behaviors/<featureset>.md` exists, let its transitions drive the screen: what a transition exposes is a data requirement, what triggers it a user action, its `requires` guard a state-dependent element; each error state the screen lists becomes an acceptance criterion in the feature that implements it, proposed there rather than written here.
8. **Register the cross-link** (`tree/05_features/README.md § Links in both directions`): each `implements:` entry whose feature does not list this screen gets a `proposed` entry in that feature's `screens:`, `{ path: 07_screens/<screen>.md, status: proposed, proposed_by: experience-screen, proposed_on: YYYY-MM-DD }`, so a screen nothing links to is not lost from its feature.

### Patching (mockup-feedback)

After the user approves the review file, `mockup-feedback` applies the approved patches to this file, each anchored to one heading or to an `elements:` id promotion, and writes nothing else into it (`tree/09_mockup/feedback/README.md § Patch scope`). It creates, renames and deletes no screen and leaves `implements:` as it is; `experience-screen` re-checks a patched screen at its next run.

## Checks

- `screen_id` equals the filename stem and matches `^[a-z][a-z0-9-]{1,47}$`; the stem is not `shell`.
- `floorplan` names a directory under `rulebook/floorplans/` whose README has `kind: screen`; `posture` and `density` are in their enums.
- Every `regions` key is a region id in that floorplan's `§ Regions`, and every `shows` is a glossary term id, `proposed` ones included.
- Every `implements:` entry resolves to a feature file, and that feature's `screens:` names this file or carries the proposed entry.
- Every `tier_overrides` row has a `reason`, and none lifts a tier-3 attribute into a row without an `APP-DESIGN.md § Exceptions` row.
- The `elements:` block covers every interactive or structural thing under `### UI Elements`, `### Actions` and `### Information Displayed`, with `target:` on every action that names a destination screen.
