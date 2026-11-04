---
path: _concept/11_build/decisions.md
summary: build-time decision records, append-only
owner: []
may_propose: []
---

# _concept/11_build/decisions.md

The build-time ledger of decisions, in the same format and under the same three-test gate as the design-time one (`tree/10_blueprint/decisions.md`). Nothing generates it: the slice and build skills append an entry inline when a hard-to-reverse choice is made during implementation, and a `DONE_WITH_CONCERNS` outcome logs its concerns (trade-offs, deviations, debt incurred) here before the loop advances. Entries are never edited, only superseded.

## Format

The records of `tree/10_blueprint/decisions.md § Format`, `Level` and `Kind` included, with this file's own `DR-<n>` sequence. A feature's `follows:` names design records only, never these.

## Writing it

1. **Read both files from the top down**, per `tree/10_blueprint/decisions.md § Levels`: a design record binds the build records at its level and below.
2. **A build choice that contradicts a design record is not written.** It goes to the user beside the record; when the user accepts it, the design record's `By` skill appends the superseding record to `_concept/10_blueprint/decisions.md`, because only an owner of that file writes there.
3. **Append under the three-test gate** of `tree/10_blueprint/decisions.md § Writing it`, at the record's level and with its kind.

## Checks

- Every record carries the fields of `tree/10_blueprint/decisions.md § Format`; ids are unique and ascending.
- No record contradicts an accepted design record at its level or above.
