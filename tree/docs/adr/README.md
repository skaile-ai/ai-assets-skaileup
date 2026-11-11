---
path: [docs/adr/, docs/adr/<NNNN>-<slug>.md]
summary: the project's decision records, one file per decision
owner: [skaileup]
may_propose: [architecture-datamodel, architecture-system, architecture-techstack, build-branch, build-database, build-implement, build-plan, build-scaffold, concept-brief, concept-glossary, experience-interaction, experience-screen, quality-design, spec-feature]
---

# docs/adr/

Why a hard-to-reverse choice was made, one file per decision, at the project root beside `APP-DESIGN.md` (`tree/protocol/beside-the-tree.md`). It is the folder upstream `domain-modeling` writes and reads, so a grill run with that skill and a skaileup run share one log. A record is written while the work happens and never authored up front; a later reader opens it to learn that a decision was made and why, and the value is the reason, not the template. `skaileup` owns the folder and is the only writer; every other skill that makes a decision proposes it (`tree/proposals/README.md`), so parallel runs never write one path and no two runs pick the same number. A rejected proposal entry is not recorded here: its `reason` in the proposal file is its record.

## Format

One markdown file per decision, `docs/adr/<NNNN>-<slug>.md`: `<NNNN>` four digits, the highest existing number + 1, assigned when `skaileup` promotes the record; `<slug>` a kebab-case phrase of the decision, unique across the folder. A project's records written before skaileup ran stay as they are and count for the numbering.

```md
---
status: accepted          # proposed | accepted | rejected | deprecated | superseded by ADR-<NNNN>
date: 2026-11-11
by: spec-feature          # the skill whose run made the decision
level: product            # product | featureset <slug> | feature <featureset>/<feature>
kind: decision            # decision | pattern
applies_when: ...         # pattern only: one sentence a later feature is matched against
refs: [_concept/05_features/booking/reserve.md]
---

# <Short title of the decision>

<1–3 sentences: the context, what was decided, and why.>

## Considered Options

<optional: each road not taken, with the reason in a clause, when it is worth remembering>

## Consequences

<optional: the downstream effect a reader must know, when it is not obvious>
```

The body is upstream's ADR format; the frontmatter is optional upstream and always written here, and upstream readers ignore the keys they do not know. `status: rejected` means the choice was refused and is recorded so nobody re-litigates it, which is not *Considered Options*: those are the roads not taken inside an accepted decision. A scope decision marked OUT in a feature spec is recorded `status: rejected`. A record without frontmatter reads as `status: accepted`, `level: product`, `kind: decision`.

**Referencing.** A record is cited by its slug as `adr:<slug>` — in a feature's `follows:`, a waived stage's `adr:` in `_concept/01_meta/walkthrough.yaml`, a design candidate's status, a ticket — never by number, because the number is assigned at promotion and a citation written before it must stay valid. `adr:<slug>` resolves to `docs/adr/*-<slug>.md`, else to a pending proposal entry with `target: docs/adr/` and `anchor: adr:<slug>`.

**Proposal entry.** `target: docs/adr/`, `anchor: adr:<slug>`, `payload:` the full markdown record above as a string, with `status: proposed` and no number in it.

A landed record is never edited. To change your mind, write a new record that names the old slug in `refs` and in its body; the owner sets the old record's `status: superseded by ADR-<NNNN>`, the one permitted edit.

## Levels

`level` says how far a record reaches. `product` binds every featureset and feature; `featureset <slug>` binds every feature of that featureset, the slug as in `_concept/05_features/featuresets.md`; `feature <featureset>/<feature>` binds one feature. A record is written at the lowest level that holds everything it binds; work that belongs to no single featureset (the stack, the data model, the brand, the interaction rules, the build's shape) records at `product`.

1. **Read from the top down before asking.** A skill reads every `product` record, then the records at each level down to and including its own scope: a feature run also reads `featureset <its featureset>` and `feature <its featureset>/<its feature>`. Pending proposal entries targeting `docs/adr/` are read with them, as not yet settled. A higher record binds every record below it, and a question a binding record answers is not asked again.
2. **A lower choice never overrides a higher record.** A choice that contradicts one is not proposed as it stands. It goes to the user beside the record it contradicts; when the user accepts it, it is proposed as a new record at the higher record's level that supersedes the old one (`## Format`), so every feature under that level sees the change.

## Patterns

A record of `kind: pattern` generalises what two or more features share (the same entities, actions, screens or floorplans used the same way) into one rule later features follow. `spec-feature` proposes it when its similarity check generalises a match (`tree/05_features/[featureset]/[feature].md § Writing it`): at `featureset` level when every feature it covers sits in one featureset, else at `product`. `applies_when` is the sentence a later run matches a new feature against; each feature that follows the record lists `adr:<slug>` in `follows:`. In the build, a pattern is one shared module: the first ticket that needs it builds it and names `adr:<slug>`, and every later ticket reuses it (`build-plan` cuts them so).

## Writing it

### Proposing (every skill in `may_propose`)

Propose a record the moment a decision passes the three-test gate; skip it when any test fails, because eager logging buries the few decisions that matter.

1. **Hard to reverse** — changing your mind later costs meaningfully.
2. **Surprising without context** — a future reader would wonder why it was done this way.
3. **The result of a real trade-off** — genuine alternatives existed and one was chosen for specific reasons.

Qualifies: architectural shape, integration patterns between subsystems, technology choices with lock-in (database, auth, message bus), boundary and ownership decisions, deliberate deviations from the obvious path, constraints invisible in the code (compliance, latency contracts), non-obvious rejected alternatives. Does not qualify: routine library picks, obvious choices, transient scratch decisions (those stay in the feature's dossier), build concerns that are not themselves such a choice (those go to the spec's parent issue, `tree/protocol/delegation.md § Delegation`).

A decision that passes is one entry of the run's proposal file (`tree/proposals/README.md § Writing it`) in the shape of `## Format`, *Proposal entry*, at the level `## Levels` gives it, and the run cites it as `adr:<slug>` from then on. The slug is checked against `docs/adr/` and the pending entries first; a taken slug gets a more specific one.

### Promoting (`skaileup`)

1. Read every proposal file and take the entries with `target: docs/adr/` and `status: proposed`.
2. Check each against the accepted records per `## Levels`. One that contradicts an accepted record at a higher level goes to the user in one batch beside that record; every other entry is promoted without a batch, because the decision was made in the run that proposed it.
3. **Promote:** take the highest number in `docs/adr/` + 1, write `payload` to `docs/adr/<NNNN>-<slug>.md` with `status: accepted` (or `rejected` when the payload records a refused choice), and set the entry's `status: promoted`, `settled_by: skaileup`, `settled_on`. For a superseding record, set the old record's `status: superseded by ADR-<NNNN>`.
4. **Reject** an entry the user declined at step 2, with the user's `reason`; it takes no record.

A missing folder means nothing has been recorded yet; the first promotion creates it.

## Checks

- Every file is named `<NNNN>-<slug>.md`; numbers and slugs are unique.
- Every record skaileup wrote has the frontmatter of `## Format`; a `featureset` level names a featureset of the roster and a `feature` level a spec at `_concept/05_features/<featureset>/<feature>.md`; every `pattern` has `applies_when`.
- No accepted record contradicts an accepted record at a higher level.
- No landed record was edited, apart from a `status: superseded by ADR-<NNNN>` line; changes are new records that name the old slug.
- Every `adr:<slug>` in `_concept/` resolves per `## Format`, *Referencing*, to a record neither `rejected` nor superseded, or to a pending entry.
- No skill but `skaileup` writes into `docs/adr/`; every proposer declares the proposals `produces`.
