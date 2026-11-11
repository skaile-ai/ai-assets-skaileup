---
path: _concept/10_blueprint/decisions.md
summary: design-time decision records, append-only
owner: [architecture-datamodel, concept-brief, concept-glossary, experience-interaction, experience-screen, quality-design, skaileup, spec-feature]
may_propose: []
---

# _concept/10_blueprint/decisions.md

The one append-only record of why a hard-to-reverse design choice was made, written while the work happens and never authored up front. A future reader opens it to learn that a decision was made and why; the value is the reason, not the template. Every authoring skill appends here: a skill that starts appending declares `{ id: decisions, path: "_concept/10_blueprint/decisions.md" }` in its `metadata.artifacts.produces` and joins `owner:` of this node in the same change, because the gate requires the owner list to equal the producers. `_concept/11_build/decisions.md` is the build-time twin with the same format and gate (`tree/11_build/decisions.md`). Rejections of `proposed` entries are recorded here too (`tree/protocol/ownership.md § Ownership`). Each record names the level it binds and whether it is one decision or a pattern later features follow (`## Levels`, `## Patterns`).

## Format

Append-only. One record per decision, with a stable id `DR-<n>` (next integer, never reused):

```md
## DR-<n> — <short title of the decision>

- **Date**: <ISO-8601 date>
- **By**: <skill name that appended it>
- **Level**: product | featureset <slug> | feature <featureset>/<feature>
- **Kind**: decision | pattern
- **Applies when**: <pattern only: one sentence naming the situation a later feature is matched against>
- **Decision**: <1–3 sentences: the context, what was decided, and why.>
- **Options rejected**: <each road not taken, with the reason in a clause; `none` when there was no real alternative.>
- **Consequence**: <the downstream effect a reader must know: what is now easier, harder or fixed.>
- **Refs**: <artifacts, entry ids, journeys or evidence the decision rests on>
- **Status**: <optional; `accepted` when absent>
```

The fields are `id · date · by · level · kind · decision · options rejected · consequence · refs`; the id is the heading, and a `pattern` record adds `Applies when`. `Status` is the one optional line: `accepted | rejected | superseded by DR-<m>`. `rejected` means the choice was refused and is recorded so nobody re-litigates it, which is not *Options rejected*: those are the roads not taken inside an accepted decision. Scope decisions marked OUT in a feature spec, and rejections of `proposed` entries, are recorded with `Status: rejected`.

The fields map onto [MADR 4.0.0](https://adr.github.io/madr/) so a reader who knows that format needs no legend: **Decision** is *Decision Outcome*, **Options rejected** is *Considered Options*, **Consequence** is *Consequences*, **Refs** is *More Information*, **Status** is `status`, **By** and **Date** are the `deciders` and `date` fields. **Level**, **Kind** and **Applies when** have no MADR field. The file stays one append-only log rather than MADR's one file per decision.

A landed record is never edited. To change your mind, append a record that names the old one in **Refs** and in its **Decision**, and add `Status: superseded by DR-<m>` to the old record; that line is the one permitted edit.

## Levels

`Level` says how far a record reaches. `product` binds every featureset and feature; `featureset <slug>` binds every feature of that featureset, the slug as in `_concept/05_features/featuresets.md`; `feature <featureset>/<feature>` binds one feature. A record is written at the lowest level that holds everything it binds; work that belongs to no single featureset (the stack, the data model, the brand, the interaction rules) records at `product`.

1. **Read from the top down before asking.** A skill reads every `product` record, then the records at each level down to and including its own scope: a feature run also reads `featureset <its featureset>` and `feature <its featureset>/<its feature>`. A higher record binds every record below it, and a question a binding record answers is not asked again.
2. **A lower choice never overrides a higher record.** A choice that contradicts one is not written. It goes to the user beside the record it contradicts; when the user accepts it, it is appended as a new record at the higher record's level that supersedes the old one (`## Format`), so every feature under that level sees the change.
3. **Records older than these fields** read as `Level: product` and `Kind: decision`; they are not edited to add them.

## Patterns

A `pattern` record generalises what two or more features share (the same entities, actions, screens or floorplans used the same way) into one rule later features follow. `spec-feature` writes it when its similarity check generalises a match (`tree/05_features/[featureset]/[feature].md § Writing it`): at `featureset` level when every feature it covers sits in one featureset, else at `product`. `Applies when` is the sentence a later run matches a new feature against; each feature that follows the record lists its id in `follows:`. In the build, a pattern is one shared module (`tree/11_build/slices/README.md § Writing it`).

## Writing it

Append an entry the moment a decision passes the three-test gate; skip it when any test fails, because eager logging buries the few decisions that matter.

1. **Hard to reverse** — changing your mind later costs meaningfully.
2. **Surprising without context** — a future reader would wonder why it was done this way.
3. **The result of a real trade-off** — genuine alternatives existed and one was chosen for specific reasons.

Qualifies: architectural shape, integration patterns between subsystems, technology choices with lock-in (database, auth, message bus), boundary and ownership decisions, deliberate deviations from the obvious path, constraints invisible in the code (compliance, latency contracts), non-obvious rejected alternatives. Does not qualify: routine library picks, obvious choices, transient scratch decisions (those stay in the feature's dossier).

Reading follows `## Levels`; a missing file means nothing has been recorded yet.

## Checks

- Every record has `DR-<n>`, a date, a `By` skill, a Level, a Kind, a decision, options rejected, a consequence and refs; ids are unique and ascending.
- A `featureset` level names a featureset of the roster and a `feature` level a spec at `05_features/<featureset>/<feature>.md`; every `pattern` has `Applies when`.
- No accepted record contradicts an accepted record at a higher level.
- No existing record was edited, apart from a `Status: superseded by DR-<m>` line; changes are new records that name the old one.
- Every skill that appends has the file in its `produces` and a place in this node's `owner:`.
