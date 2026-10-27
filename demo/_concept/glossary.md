---
last_updated: 2026-10-24
approved: 2026-10-24
---

# Glossary — Lunch Roulette

The words of a team that decides where to eat lunch together.

## The decision

**Poll** (`poll`):
A lunch decision for one day: a title, a deadline and the places members can vote for.
_Avoid_: Survey, question, event
- kind: object
- is-a: —
- part-of: —
- roles: opened by an Organizer; voted in by Members
- purpose: gives the team one place to settle where to eat and when the answer is due.
- principle: an Organizer opens a Poll → Members vote for Places → at the deadline the Poll closes and names the Pick.
- navigation: primary
- lifecycle: independent
- origin: user
- operations: create · read · edit · archive

**Vote** (`vote`):
One Member's choice of one Place in one Poll; a Member changes it until the deadline.
_Avoid_: Ballot, like, upvote
- kind: object
- part-of: poll
- purpose: records what each Member wants, so the Pick rests on counted choices.
- principle: a Member picks a Place → the Vote is counted → the Member may move it until the Poll closes.
- navigation: contextual
- lifecycle: owned-by Poll
- origin: user
- operations: create · read · edit · delete

**Pick** (`pick`):
The Place a closed Poll landed on.
_Avoid_: Winner, result, decision
- kind: state
- part-of: poll
- purpose: names the one Place the team goes to.

**Draw** (`draw`):
The random choice among Places that tie for most Votes, shown to everyone.
_Avoid_: Coin flip, spin, lottery
- kind: event
- part-of: poll
- purpose: settles a tie without a second Poll and without anyone deciding.

## The places and the people

**Place** (`place`):
A restaurant, canteen or shop the team goes to for lunch, with its cuisine and the walk from the office.
_Avoid_: Restaurant, venue, location
- kind: object
- purpose: keeps the team's options in one list, so every Poll starts from real choices.
- principle: a Member adds a Place once → every later Poll offers it → a Place nobody wants any more is archived.
- navigation: primary
- lifecycle: independent
- origin: user
- operations: create · read · edit · archive

**Member** (`member`):
A person on the team who can vote in Polls.
_Avoid_: User, participant, employee
- kind: role
- purpose: identifies who voted and what they eat.

**Organizer** (`organizer`):
The Member who opened a Poll and may close it early.
_Avoid_: Owner, admin, host
- kind: role
- is-a: member
- purpose: carries a Poll from open to closed.

**Veto** (`veto`):
A Member strikes one Place from a Poll because they cannot eat there.
- status: proposed
- proposed_by: spec-feature
- proposed_on: 2026-10-25
- source: "Aiko cannot eat shellfish; can she remove the sushi place for everyone?" (05_features/polls/vote-on-place.md)
- kind: event

## Relations

- poll · opened-by · organizer
- poll · has-many · vote
- poll · ends-in · pick
- vote · cast-by · member
- vote · for · place
- draw · breaks-tie-in · poll
