---
app: Lunch Roulette
updated: 2026-10-25
approved: 2026-10-25
rulebook: rulebook/rules.md
defaults: DF1–DF15 except DF8
companions: { glossary: _concept/glossary.md, visual: _concept/03_brand/identity.md, shell: _concept/07_screens/shell.md, decisions: _concept/10_blueprint/decisions.md }
---
# App design – Lunch Roulette
## Context
Teams of 4 to 15; roles organizer and member; Nuxt UI on a phone first; depth `standard`. DF8 is declined, see Exceptions.
## Navigation model
organization: object-led · primary_surface: topbar · archetype: none
- **NAV-1 Primary entries: Polls and Places. A Vote is never an entry; it lives inside its Poll.** *Why:* members open the app to vote, and a Vote has no meaning outside its Poll. *Rules:* P12, P22.
- **NAV-2 The app opens on Polls, with the open poll first.** *Why:* the hero journey starts there. *Rules:* P22.
## Objects
| id | object | home | index | editor (task → host) | create | delete | representations |
|---|---|---|---|---|---|---|---|
| OBJ-1 | Poll | page | list-report | title, deadline: dialog · close: inline | dialog | n/a (closed polls stay) | row(title, status, closes, pick) · chip(title) · peek(+organizer, votes) · page |
| OBJ-2 | Place | n/a (a row in Places) | list-report | all: dialog | dialog | archive, undo H7 | row(name, cuisine, walk) · chip(name) · card(+website) |
| OBJ-3 | Vote | n/a (a Poll section) | n/a | choose place: inline | inline | n/a (moved, never deleted) | row(member, place) |
## Information hierarchy
| object | attribute | tier | per-screen override (task reason) |
|---|---|---|---|
| Poll | title · status · closes at · pick | 1 | |
| Poll | organizer · vote count | 2 | |
| Poll | created at | 3 | |
| Place | name · cuisine · walking minutes | 1 | poll: walking minutes → 2 (members compare by name first) |
| Place | website | 3 | |
- **TIER-1 Tier policy as the rulebook states it.** *Rules:* P21.
## Screen defaults
| id | floorplan | posture | density |
|---|---|---|---|
| SCR-1 | list-report | sovereign | default |
| SCR-2 | object-page | sovereign | default |
## Surfaces
- **SURF-1 No drawer anywhere; the peek of a Poll row is a popover that reads only.** *Why:* the app has two destinations and a phone has no room for a drawer. *Rules:* P5; DF2.
## Modals
- **MOD-1 Create and edit dialogs are 480 px wide and hold at most four fields.** *Rules:* P5, P14; DF7.
## Popups
- **POP-1 Tooltips open after 500 ms on hover and on focus; touch uses a visible label instead.** *Rules:* P16; DF14.
## Editing
- **EDIT-1 A dialog saves with its one primary button; a dirty dialog asks before it closes.** *Rules:* P14; DF5.
- **EDIT-2 A Vote saves the moment it is chosen, with an undo toast for ten seconds.** *Why:* ten seconds of work must not need a Save button. *Rules:* P14 adapt; H7.
## Messages
- **MSG-1 Errors on a page are inline alerts with a retry; a refused vote names the reason ("Voting closed at 12:30").** *Rules:* P15.
- **MSG-2 An empty Poll list says "No polls yet - hungry?" and offers Open poll.** *Rules:* P15 (proposed by experience-screen, 2026-10-25)
## Buttons
- **BTN-1 Create actions carry a text label: "Open poll", "Add place".** *Rules:* P17.
- **LANG-1 Verbs: Open · Vote · Close · Draw · Add · Edit · Archive. Nouns from the glossary: Poll, Place, Vote, Pick.** *Rules:* P11, P13.
## Find
- **FIND-1 The palette lists open Polls first, then Places, then destinations.** *Rules:* P9, P10; DF11.
## View state and disclosure
- **VIEW-1 The selected status view and the sort of Polls live in the URL.** *Rules:* P23.
## Feedback
- **FBK-1 The Draw is the one deliberate delay: 2.5 s, skippable with Esc; every other action answers within 1 s.** *Rules:* P26; H5; DF13.
## Interaction concepts
| id | purpose | operational principle | depends_on | refs |
|---|---|---|---|---|
| CON-1 Draw | settles a tie without a second poll | the poll closes with tied places; the app draws one at random and shows it to everyone | OBJ-1, OBJ-2 | FBK-1, draw-pick |
## Adopted heuristics
| H id | adopted value | reason |
|---|---|---|
| H1 | 4 | see MOD-1 |
| H12 | 4 | a Poll page shows four key facts |
## Exceptions
| deviation | rule id | reason |
|---|---|---|
| A Poll is reachable by its page path, not by `?poll=<id>` | DF8 | the path already carries the selection and the app has no drawer |
## Open
| id | question | options | recommendation |
|---|---|---|---|
| Q1 | May a Member remove a Vote without choosing another Place? | allow · move only | move only: one Vote per Member is the counting rule |
## Changelog
- 2026-10-25 · experience-interaction · adopted the defaults bundle except DF8
