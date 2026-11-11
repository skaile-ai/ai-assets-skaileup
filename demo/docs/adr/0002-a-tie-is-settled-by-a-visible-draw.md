---
status: accepted
date: 2026-10-25
by: spec-feature
level: feature polls/draw-pick
kind: decision
refs: [_concept/05_features/polls/draw-pick.md, _concept/04_journeys/stories.yaml]
---

# A tie is settled by one visible random draw

When places tie for the most votes at closing, the app draws one of them at random and shows the draw to every member, with no second voting round (journey `run_a_lunch_poll`, `AC-run_a_lunch_poll-04`).

## Considered Options

- A runoff vote: drags the decision out, the thing the product removes.
- The organizer decides: brings the loudest-voice problem back.

## Consequences

The pick is always final at the deadline; `draw-pick` needs a stored draw so a reload shows the same result.
