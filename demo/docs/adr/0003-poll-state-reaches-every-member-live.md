---
status: accepted
date: 2026-10-25
by: spec-feature
level: featureset polls
kind: pattern
applies_when: a polls feature changes something every Member of the Poll sees - a Vote count, the Draw, the Pick.
refs: [_concept/05_features/polls/vote-on-place.md, _concept/05_features/polls/draw-pick.md, _concept/08_dossiers/draw-pick/index.md, _concept/07_screens/poll.md]
---

# Every member sees a poll's state live, through one channel

The similarity check for `draw-pick` matched `vote-on-place`: both change the open `poll` screen for every Member, the counts as Votes arrive and the Draw at closing. The user chose to generalise: a change to a Poll reaches every Member who has it open as it happens, and everyone else on the next load, through one live channel per Poll, because a result only some Members saw happen reads as rigged, the problem the product removes (`brief.md`).

## Considered Options

- Reuse `vote-on-place` for the Draw: the Draw is no Member's action and has its own permissions.
- Keep them separate: two update paths on one screen, which drift apart the first time one changes.

## Consequences

Counts, the Draw and the Pick arrive the same way; a later polls feature that changes what Members see follows this record instead of adding an update path. The level is the featureset because `places` has no state Members watch together.
