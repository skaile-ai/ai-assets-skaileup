# 0022 — Shared artifact contracts and proposed entries

**Status:** accepted

Supersedes the `writers` key and the "conditional file carries `writers: []`" choice of
[ADR 0017](0017-the-instruction-tree-mirrors-the-artifact-tree.md), and the single-writer
rules of [ADR 0014](0014-the-glossary-is-a-root-file.md) (glossary) and
[ADR 0015](0015-interaction-decisions-live-in-app-design.md) (`APP-DESIGN.md`) as far as they
forbid anyone else to add to the file. `experience-interaction` stays the only skill that
confirms entries in `APP-DESIGN.md`; `concept-glossary` the only one in the glossary.

## Context

Re-entry was "hand back and re-run", never "ask and record" (U3). A skill that met a missing
term or an unspecified object could only stop and name the owner. Facts had several homes
(U9): decisions lived in `APP-DESIGN.md` *Why* lines, in `decisions.md` (one writer), in
dossiers and in `agent_notes:`; `answers.json` claimed to be "the one record" while only
onboarding wrote it. The two critics differed on mechanism — a central answers file with
`proposed` entries (fable) or answers at their semantic home with shared artifact contracts
(sol); the owner chose the second.

Deletion tests (U15) showed `decisions.md` with one writer and `agent_notes:` earned nothing.

## Decision

**Ownership is declared on every tree node:**

```yaml
owner: [concept-glossary]   # skills whose `produces` resolve here; [] when nothing generates it
may_propose: []             # skills that may append `proposed` entries; disjoint from owner
```

`owner` keeps the exact semantics `writers` had for the `produces` cross-check. `may_propose`
names skills of this collection and repeats no owner.

**A proposed entry** is an entry a non-owner appends to the owner's artifact, marked
`status: proposed`, with `proposed_by`, `proposed_on` and its source (an evidence reference or
the user's words). It adds and never edits a confirmed entry. The owner reviews it with the
user and promotes it (drops the marker) or rejects it, recording the rejection in the decision
record. Each node's `## Format` holds the per-artifact shape. Nested skill calls are not relied
on; a proposal is a file write.

**Answers live at their semantic home.** Open questions carry stable ids. Dossiers keep
interview history and rejected options and link to records. `answers.json` is onboarding
intake only; no later skill reads it as the record of a decision.

**One append-only decision record**, open to every authoring skill: `id · date · by · decision
· options rejected · consequence · refs`. `agent_notes:` is deleted.

**Proposers named so far** (later tickets complete the list): every authoring skill → glossary;
`spec-feature` and `experience-screen` → datamodel; `experience-screen` and `quality-design`
→ `APP-DESIGN.md`; `experience-screen` → shell; `spec-feature` → screens.

## Consequences

- `check.py` requires `owner` and `may_propose` on every node; a missing owner or an unknown or
  duplicated proposer fails.
- `ops-review` reports `proposed` entries that have waited too long.
- Approval is tied to revision, as before: a later substantive edit clears `approved:`.
- Nothing is migrated and no `writers` alias is kept: the owner chose a clean slate.
