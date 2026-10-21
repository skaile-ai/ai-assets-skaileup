---
path: _concept/05_features/<featureset>/<feature>.md
summary: one feature's permanent spec — scope line, permissions, acceptance criteria
owner: [spec-feature]
may_propose: [experience-screen]
---

# _concept/05_features/<featureset>/<feature>.md

One feature, from a sentence to a spec somebody can build. It is the one record of who may do what and of what was considered in or out; `experience-behaviors`, the seed, scaffolding and the build ledger cite it, so none restates it. `spec-feature` writes it, one feature per run, and adds the feature's row to the roster in the same run; the flow draws that node once because iteration is not something a flow edge can express, so the repetition lives in the skill. It lists the screens the feature uses and writes none of them: a screen is `experience-screen`'s artifact.

## Format

```yaml
---
priority: must-have | nice-to-have
roles: [admin, member, guest]   # or [all_users]
permissions:                    # role → allowed actions; the one record, no body table
  admin: [create, read, update, delete]
  member: [read, update]
story_refs: []                  # journey ids from stories.yaml that motivated this feature
screens:                        # screens this feature uses; one entry per screen file
  - path: 07_screens/<screen>.md
  - { path: 07_screens/<screen>.md, status: proposed, proposed_by: experience-screen, proposed_on: YYYY-MM-DD }
data_entities: []               # model names from 10_blueprint/datamodel/model.json, e.g. [User, Session]
last_updated: YYYY-MM-DD
---
```

`permissions:` takes its roles from `_concept/05_features/featuresets.md`'s vocabulary and is the only place grants are written (`tree/05_features/README.md § Permissions`). Body, in order: `## Scope` — the IN / OUT / DEFER line with a one-line rationale per item; the acceptance criteria. `data_entities` is the one feature↔entity join, each name copied from the models in `_concept/10_blueprint/datamodel/model.json` (format: `tree/10_blueprint/datamodel/model.md`); `screens:` (a plain entry is confirmed; a `proposed` one came from `experience-screen` and waits for this skill's next run) and `story_refs` follow `tree/05_features/README.md § Links in both directions`.

Criteria are cited by id (`AC-<story-id>-<nn>`), never retyped; the id grammar and the table of sources to derive them from are in `tree/04_journeys/stories.md`. A criterion the grill adds that no story carries takes `AC-<feature_slug>-<nn>`.

### Slug

`feature_slug` matches `^[a-z][a-z0-9-]{1,47}$`: lowercase the title, replace each run of non-`[a-z0-9]` with one `-`, trim `-` at both ends, truncate to 48. The same derivation names a slice's `slice_id` from the slice's own title (`tree/11_build/slices/README.md`). A feature slug names three things at once — this file, its roster row and `_concept/08_dossiers/<feature_slug>/` — and resolves by globbing `05_features/*/<feature_slug>.md`. Zero matches means the spec was never written; two matches means two featuresets claim the slug, so list both and ask which one this is. A slug that already exists is a resume: load what is there, show what would change, and write after the user agrees — overwriting silently discards the reasoning a dossier holds.

## Writing it

Numbering is the run's order; steps 2, 6 and 9 hand to the nodes they name at the moment they say.

1. **Resolve the feature and its slug.** Take a one-sentence title, derive `feature_slug` as above, and place it in exactly one featureset. A glob that already resolves is a refinement of an existing spec: load it and say so before asking anything, so the user answers against what is written rather than from memory. Carry its existing `screens:` array through untouched — screens were linked by other runs, and a rewritten spec that drops it silently unlinks the feature from its screens.
2. **Grill.** Call the Skill tool with "grilling" against this feature. If it is not installed, run the rounds yourself: one frontier of unsettled questions per message, each with a recommended answer. The ground the frontier has to cover before it can be empty: what the feature *is* and who triggers it, the happy path, state transitions, boundary inputs, concurrency, a role × action permissions table, persistence and recovery, error states, and the other features this one touches. The flow in `_concept/01_meta/scope.yaml` (format: `tree/01_meta/scope.md`) sets the depth — `appbuilder-mvp` settles the happy path and permissions in a round or two; `appbuilder-standard`, `skaileup-concept-only` and `skaileup-concept-reverse` work the tree until the frontier is genuinely empty. Read `_concept/brief.md`, `_concept/04_journeys/stories.yaml`, `_concept/06_behaviors/<featureset>.md` where it exists, and any sibling spec the feature touches first: `grilling` makes finding facts your job, and asking the user something the tree already says spends the round you needed for a real question. With no journeys and no data model the interview carries both loads, so ask where the feature sits in a journey rather than assuming it stands alone. Open the feature dossier `_concept/08_dossiers/<feature_slug>/index.md` as the grill starts and append to it as its node says (`tree/08_dossiers/[feature_slug]/index.md`); an `open` dossier already there is an interrupted run, so load it and continue.
3. **Use the glossary's words; pin decisions as they pass the gate.** Name every concept in the grill by its term in `_concept/glossary.md` (format: `tree/glossary.md`) — a synonym from the `_Avoid_` list is renamed to the term, not adopted. Entity names are read, never coined: from `_concept/10_blueprint/datamodel/model.json` when it exists, else from the glossary. A concept with no term stops the interview: name it and hand back, and the flow re-enters `concept-glossary`, which pins it before this feature goes on. A choice that passes the three-test gate is appended to `_concept/10_blueprint/decisions.md` (format and gate: `tree/10_blueprint/decisions.md`) while the interview is running, because the reasoning is in the room only then.
4. **Draw the scope line.** Walk every edge case and open question the grill surfaced and put each one IN, OUT or DEFER with a one-line rationale. IN items become acceptance criteria; the whole line becomes the spec's `## Scope` section, the one record of what was considered, and the dossier links to it rather than copying it. A DEFER names the feature or slice that will pick it up, or it is an OUT wearing a friendlier word. An OUT that clears the decisions gate is appended to `_concept/10_blueprint/decisions.md` with Status `rejected`, because a refusal that binds the whole design stays invisible to the next feature unless it is logged where that feature reads.
5. **Write the feature spec** at `05_features/<featureset>/<feature_slug>.md` in the format above. Cite criteria from `stories.yaml` by id; one the feature needs that its journeys lack stops the write and hands back to `experience-journeys`. Set `data_entities` from `model.json`; an entity the model lacks stops the write and hands back to `architecture-datamodel`, and with no `model.json` the same hand-back applies when the flow has that node, otherwise leave the list empty and name entities by glossary term. Every criterion traces to something the user confirmed in the grill — an invented one reads exactly like a real one to the implementer, and gets built.
6. **Add the roster row**, per `tree/05_features/featuresets.md § Writing it`: the row with the priority the grill's first batch settled, a new featureset when none fits, and any role the grill named that the roster lacks.
7. **List the screens the feature uses.** For each screen the scope line put IN that already exists at `07_screens/<screen>.md`, add it to `screens:` and append a proposed entry (`{ path: 05_features/<featureset>/<feature_slug>.md, status: proposed, proposed_by: spec-feature, proposed_on: <date> }`) to that screen's `implements:`, so the link holds in both directions (`tree/05_features/README.md § Links in both directions`) while the screen's owner stays its only writer. A screen that does not exist yet is named for the user to create with `experience-screen`, which reads this feature and proposes the link back into `screens:`; this skill's write set carries no screen file.
8. **Show the whole write set and the blast radius, then write.** An existing file gets its diff shown and its own answer — the user's earlier edits are the case this catches. Beside the diffs, name which already-written artifacts this feature just invalidated and whose owner has to re-run: `04_journeys/stories.yaml` when it introduces a flow no story covers, `10_blueprint/techstack.md` for a new dependency, `architecture.md` for a new module or protocol, `10_blueprint/datamodel/` for new entities or fields, and `07_screens/shell.md` when it adds a top-level destination, and `experience-screen` for a screen the feature changes. Naming the owner is the whole of it — this skill edits none of them, and a cascade that reaches into five trees is the multi-writer tangle one writer per artifact exists to avoid. When the project is already built, `build-plan` is the next command: the feature is specified, not planned.
9. **Freeze the feature dossier**, per `tree/08_dossiers/[feature_slug]/index.md`.

## Checks

- The spec, its roster row and the frozen dossier are on disk.
- Every `screens:` entry names a screen file that exists and whose `implements:` names this feature, as a confirmed or a proposed entry.
- `permissions:` is the only place grants appear.
- Every acceptance criterion is an id traced to the user's confirmation in the grill; every IN item has one.
