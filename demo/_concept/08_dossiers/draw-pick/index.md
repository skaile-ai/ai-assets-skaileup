---
status: frozen
last_updated: 2026-10-25
---

# Dossier - draw-pick

## Framing
The product is named after this feature. A tie among the most-voted Places is common in a team of five to ten, and a second round of voting is what the chat thread does today.

## Similar features
Compared before the grill with every spec and idea in the roster on entities, actions, screens and floorplans; no pattern record existed yet.
- `vote-on-place` - shares Poll, Vote and the `poll` screen; both change what every Member sees on an open Poll. Generalised: `DR-3`, a `featureset polls` pattern; `vote-on-place.md` lists it in `follows:` in this run's write set.
- `create-poll` - shares Poll and the `poll` screen. Kept separate: it opens a Poll on an Organizer's action; this one closes it at the deadline with no actor.
- idea `deadline-reminders` - shares the deadline. Kept separate: it notifies before the deadline; this one decides at it.

## Round 1 - what is a tie?
The user settled: a tie is two or more Places with the same highest Vote count. A Place one Vote behind is not drawn. Rejected: drawing among the top three Places regardless of counts, because it throws away what the team voted.

## Round 2 - who sees the Draw?
Every Member sees it, live if they have the Poll open and as a replay otherwise. Rejected: showing only the Pick, because the visible Draw is what makes the result feel fair (`brief.md`).

## Round 3 - empty poll
A Poll with no Votes closes without a Pick. Rejected: drawing among all Places, because it invents a decision nobody made.

## Links forward
- Spec: [`05_features/polls/draw-pick.md`](../../05_features/polls/draw-pick.md) and its `## Scope`
- Screens: [`07_screens/poll.md`](../../07_screens/poll.md)
- Decisions: `DR-2`, `DR-3` in [`10_blueprint/decisions.md`](../../10_blueprint/decisions.md)
