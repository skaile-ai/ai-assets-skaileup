---
last_updated: 2026-10-24
approved: 2026-10-24
---

# Glossary — Lunch Roulette

Words: `GLOSSARY.md` (split mode, `tree/glossary.md § Where the words live`).

## The decision

**Poll** (`poll`):
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
- kind: object
- part-of: poll
- purpose: records what each Member wants, so the Pick rests on counted choices.
- principle: a Member picks a Place → the Vote is counted → the Member may move it until the Poll closes.
- navigation: contextual
- lifecycle: owned-by Poll
- origin: user
- operations: create · read · edit · delete

**Pick** (`pick`):
- kind: state
- part-of: poll
- purpose: names the one Place the team goes to.

**Draw** (`draw`):
- kind: event
- part-of: poll
- purpose: settles a tie without a second Poll and without anyone deciding.

## The places and the people

**Place** (`place`):
- kind: object
- purpose: keeps the team's options in one list, so every Poll starts from real choices.
- principle: a Member adds a Place once → every later Poll offers it → a Place nobody wants any more is archived.
- navigation: primary
- lifecycle: independent
- origin: user
- operations: create · read · edit · archive

**Member** (`member`):
- kind: role
- purpose: identifies who voted and what they eat.

**Organizer** (`organizer`):
- kind: role
- is-a: member
- purpose: carries a Poll from open to closed.

## Relations

- poll · opened-by · organizer
- poll · has-many · vote
- poll · ends-in · pick
- vote · cast-by · member
- vote · for · place
- draw · breaks-tie-in · poll
