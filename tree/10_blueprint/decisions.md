---
path: _concept/10_blueprint/decisions.md
summary: design-time decision records, append-only
writers: [spec-feature]
---

# _concept/10_blueprint/decisions.md

The record of why a hard-to-reverse design choice was made, written while the work happens and never authored up front. A future reader opens it to learn that a decision was made and why; the value is the reason, not the template. `_concept/11_build/decisions.md` is the build-time twin with the same format and gate (`tree/11_build/decisions.md`).

## Format

Append-only. Each entry is tiny:

```md
## <ISO-8601 date> — <short title of the decision>

<1–3 sentences: the context, what was decided, and why.>
```

Optional lines, only when they add real value:

- **Status**: `accepted | rejected | deprecated | superseded by <date/title>`. `rejected` means the choice was refused and is recorded so nobody re-litigates it; it is not the roads not taken inside an accepted decision. Scope decisions marked OUT in a feature spec are recorded with `Status: rejected`.
- **Options considered** — only when the rejected alternatives are worth remembering.
- **Consequences** — only when a non-obvious downstream effect must be flagged.

A landed entry is never edited. To change your mind, add a new entry that supersedes the old one and mark the old one's Status.

## Writing it

Append an entry the moment a decision passes the three-test gate; skip it when any test fails, because eager logging buries the few decisions that matter.

1. **Hard to reverse** — changing your mind later costs meaningfully.
2. **Surprising without context** — a future reader would wonder why it was done this way.
3. **The result of a real trade-off** — genuine alternatives existed and one was chosen for specific reasons.

Qualifies: architectural shape, integration patterns between subsystems, technology choices with lock-in (database, auth, message bus), boundary and ownership decisions, deliberate deviations from the obvious path, constraints invisible in the code (compliance, latency contracts), non-obvious rejected alternatives. Does not qualify: routine library picks, obvious choices, transient scratch decisions (those stay in the feature's dossier).

Reading it is a one-line habit: any skill working in an area reads the existing entries that touch it; a missing file means nothing has been recorded yet.

## Checks

- Every entry has a date and a title.
- No existing entry was edited; changes are new entries with the old one's Status updated.
