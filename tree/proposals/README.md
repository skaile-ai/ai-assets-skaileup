---
path: [_concept/proposals/, _concept/proposals/<date>-<skill>-<scope>.yaml]
summary: one file per run that proposes entries to artifacts other skills own
owner: [architecture-datamodel, architecture-system, architecture-techstack, concept-brief, concept-glossary, concept-onboard, concept-research, concept-reverse, experience-behaviors, experience-interaction, experience-journeys, experience-screen, experience-shell, mockup-feedback, mockup-storybook, quality-design, quality-test, spec-feature]
may_propose: []
---

# _concept/proposals/

Every entry a skill offers to an artifact it does not own, one file per run that proposes anything (`tree/protocol/ownership.md § Ownership`). The proposing run writes a new file and never edits another run's, so runs that go in parallel never write the same path; the target's owner reads the entries aimed at its artifact, settles each, and the file stays as the history of what was offered and what became of it. An entry written into the owner's artifact instead would be a second writer on one file, and two parallel runs would overwrite each other.

## Format

One YAML file per proposing run, `_concept/proposals/<proposed_on>-<proposed_by>-<scope>.yaml`: the date, the proposing skill's `name:`, and a kebab slug of what the run worked on (a feature `<featureset>-<feature>`, a screen id, a topic), with `/` turned into `-`. A second run with the same date, proposer and scope appends `-2`, `-3` to the stem. Validate against `tree/proposals/proposal.schema.json` before writing, after turning YAML dates into ISO text (`tree/README.md § Frontmatter every markdown artifact carries`).

```yaml
proposed_by: spec-feature          # skill of this collection, listed in each target node's may_propose
proposed_on: 2026-11-11            # YYYY-MM-DD
scope: booking-reserve             # the slug in the file name
entries:
  - id: p1                         # unique within the file; cited as <file-stem>#p1
    target: _concept/10_blueprint/datamodel/model.yaml   # project-relative path of the owner's artifact
    anchor: entities.Booking.fields.slot                 # where it lands, in the grammar of the target node's ## Format
    payload: { type: datetime, required: true }          # the entry in the target node's own format: a YAML value, or a markdown string
    source: "_concept/05_features/booking/reserve.md § Data; user: 'a booking has a slot'"
    status: proposed               # proposed | promoted | rejected
    settled_by: architecture-datamodel   # the next three only from the target's owner, when it settles
    settled_on: 2026-11-12
    reason: ""                     # required when rejected
```

`target` resolves to its node like any `_concept/` path. A glossary entry targets `_concept/glossary.md` in either glossary mode (`concept-glossary` moves the words into the project glossary when it promotes); a `CONTEXT.md` target resolves to `tree/glossary.md` as well, `APP-DESIGN.md` to `tree/APP-DESIGN.md`. An entry with `status: promoted` or `rejected` carries `settled_by` and `settled_on`; a rejected one carries a non-empty `reason`.

## Writing it

### Proposing (every owner of this directory)

1. Collect what the run would add to artifacts it does not own. For each, read the target node: the run's skill is listed in its `may_propose`, and the node's `## Format` gives the payload shape and the anchor grammar.
2. Write one new file named as above, one entry per addition, each `status: proposed`, with its evidence reference or the user's words as `source`. An entry adds and never edits a confirmed entry of the target.
3. Write nothing into the target artifact, and create no target that does not exist yet: the owner's first run creates it and settles the entries waiting for it.

### Settling (the owner of the target)

1. Before writing the artifact, read every file here and take the entries whose `target` is this artifact and whose `status` is `proposed`.
2. Review them with the user in the run's batch (`tree/protocol/running.md § How a skill runs`), unless the target node's `## Format` names an approval that already covers them.
3. **Promote:** write `payload` into the artifact at `anchor`, in the artifact's own format and with no proposal marker, then set the entry's `status: promoted`, `settled_by` and `settled_on`.
4. **Reject:** set `status: rejected`, `settled_by`, `settled_on` and the user's or the evidence's `reason`. The reason stays here; a rejection takes no decision record.
5. Change nothing else in the file: those four fields are the one write an owner makes into a file it did not create.

## Checks

- Every file validates against `tree/proposals/proposal.schema.json`, and its name is `<proposed_on>-<proposed_by>-<scope>` with an optional `-<n>`.
- Every entry's `target` resolves to a node whose `may_propose` lists `proposed_by`.
- No owner artifact holds a proposal or a proposal marker; an artifact counts as confirmed only while no entry targeting it is `proposed`.
- An entry still `proposed` after 14 days is reported by `ops-review`.
