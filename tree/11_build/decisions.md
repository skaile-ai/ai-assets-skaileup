---
path: _concept/11_build/decisions.md
summary: build-time decision records, append-only
writers: []
---

# _concept/11_build/decisions.md

The build-time ledger of decisions, in the same format and under the same three-test gate as the design-time one (`tree/10_blueprint/decisions.md`). Nothing generates it: the slice and build skills append an entry inline when a hard-to-reverse choice is made during implementation, and a `DONE_WITH_CONCERNS` outcome logs its concerns (trade-offs, deviations, debt incurred) here before the loop advances. Entries are never edited, only superseded.
