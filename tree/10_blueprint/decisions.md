---
path: _concept/10_blueprint/decisions.md
summary: design-time decision records, append-only
owner: [spec-feature, architecture-datamodel]
may_propose: []
---

# _concept/10_blueprint/decisions.md

The one append-only record of why a hard-to-reverse design choice was made, written while the work happens and never authored up front. A future reader opens it to learn that a decision was made and why; the value is the reason, not the template. Every authoring skill appends here: a skill that starts appending declares `{ id: decisions, path: "_concept/10_blueprint/decisions.md" }` in its `metadata.artifacts.produces` and joins `owner:` of this node in the same change, because the gate requires the owner list to equal the producers. Today those are `spec-feature` and `architecture-datamodel`. `_concept/11_build/decisions.md` is the build-time twin with the same format and gate (`tree/11_build/decisions.md`). Rejections of `proposed` entries are recorded here too (`tree/README.md § Ownership`).

## Format

Append-only. One record per decision, with a stable id `DR-<n>` (next integer, never reused):

```md
## DR-<n> — <short title of the decision>

- **Date**: <ISO-8601 date>
- **By**: <skill name that appended it>
- **Decision**: <1–3 sentences: the context, what was decided, and why.>
- **Options rejected**: <each road not taken, with the reason in a clause; `none` when there was no real alternative.>
- **Consequence**: <the downstream effect a reader must know: what is now easier, harder or fixed.>
- **Refs**: <artifacts, entry ids, journeys or evidence the decision rests on>
- **Status**: <optional; `accepted` when absent>
```

The seven fields are `id · date · by · decision · options rejected · consequence · refs`; the id is the heading. `Status` is the one optional line: `accepted | rejected | superseded by DR-<m>`. `rejected` means the choice was refused and is recorded so nobody re-litigates it, which is not *Options rejected*: those are the roads not taken inside an accepted decision. Scope decisions marked OUT in a feature spec, and rejections of `proposed` entries, are recorded with `Status: rejected`.

The fields map onto [MADR 4.0.0](https://adr.github.io/madr/) so a reader who knows that format needs no legend: **Decision** is *Decision Outcome*, **Options rejected** is *Considered Options*, **Consequence** is *Consequences*, **Refs** is *More Information*, **Status** is `status`, **By** and **Date** are the `deciders` and `date` fields. The file stays one append-only log rather than MADR's one file per decision.

A landed record is never edited. To change your mind, append a record that names the old one in **Refs** and in its **Decision**, and add `Status: superseded by DR-<m>` to the old record; that line is the one permitted edit.

## Writing it

Append an entry the moment a decision passes the three-test gate; skip it when any test fails, because eager logging buries the few decisions that matter.

1. **Hard to reverse** — changing your mind later costs meaningfully.
2. **Surprising without context** — a future reader would wonder why it was done this way.
3. **The result of a real trade-off** — genuine alternatives existed and one was chosen for specific reasons.

Qualifies: architectural shape, integration patterns between subsystems, technology choices with lock-in (database, auth, message bus), boundary and ownership decisions, deliberate deviations from the obvious path, constraints invisible in the code (compliance, latency contracts), non-obvious rejected alternatives. Does not qualify: routine library picks, obvious choices, transient scratch decisions (those stay in the feature's dossier).

Reading it is a one-line habit: any skill working in an area reads the existing entries that touch it; a missing file means nothing has been recorded yet.

## Checks

- Every record has `DR-<n>`, a date, a `By` skill, a decision, options rejected, a consequence and refs; ids are unique and ascending.
- No existing record was edited, apart from a `Status: superseded by DR-<m>` line; changes are new records that name the old one.
- Every skill that appends has the file in its `produces` and a place in this node's `owner:`.
