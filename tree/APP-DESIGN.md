---
path: APP-DESIGN.md
summary: the app's interaction choices against the rulebook — objects, tiers, surfaces
owner: [experience-interaction]
may_propose: []
---

# APP-DESIGN.md

`APP-DESIGN.md` sits at the project root — the directory holding `_concept/` — the one project-root artifact. It is the per-app record of choices against the rulebook (`rulebook/rules.md`): which rules, defaults and heuristics the app adopts, adapts or declines, and what the rulebook leaves to the app — navigation model, object map, information tiers, screen defaults, surfaces, saving, messages, finding. `experience-interaction` owns it, every screen, shell and feature skill reads it, and `quality-interaction` checks the source against it. A missing or contradictory entry is re-decided differently in every screen.

It holds *decisions*; findings, plans and questions stay in the output of the run that raised them, and rules stay in the rulebook, cited by id, never copied. It repeats none of its neighbours:

- `_concept/glossary.md` — what things are called (the nouns) and each object's axes (`navigation`, `lifecycle`, `origin`, `operations`);
- `_concept/03_brand/identity.md` — how it looks and sounds;
- `_concept/07_screens/shell.md` — the shell frame and the concrete destination list;
- `_concept/10_blueprint/decisions.md` — the records of choices that had rejected options;
- `docs/adr/` — decisions of architecture.

`build-scaffold` writes a line in the project's root `AGENTS.md` that points coding agents here, creating the file when it creates the project. In a project that existed before scaffolding the skills leave `CLAUDE.md` and `AGENTS.md` alone, and the plan says the link is missing.

## Reading it

Each reader opens the file at its first step, as intent, before judging anything:

- screen and feature skills (`spec-feature`, `experience-screen`) — take each editing task's host from the object map's editor cell, each attribute's tier from § Information hierarchy, posture and density from § Screen defaults. A screen that needs a host the map lacks is handed back to `experience-interaction`; the screen spec does not invent one.
- `experience-shell` — derives the destination list under § Navigation model and takes messages, editing and dialog patterns from the entries instead of deciding them.
- `ops-review` — checks screen specs against the entries.
- `quality-interaction`, `quality-design` — check the app's source against the entries.
- `build-plan` — reads the verdict at `_concept/11_build/interaction.sarif` (format: `tree/11_build/interaction.md`), not the file itself.

How a reader applies what it reads:

- A decided entry wins over the rule it cites (`rulebook/README.md`). Code that deviates is one finding, filed under the entry with the rule tagged (`MOD-2 / P5`), counted once.
- A deviation listed in § Exceptions is not reported.
- An `[open Qn]` entry is judged by its recommendation, and the finding is tagged `[Qn]`.
- Tier 3 appears only in a peek, a popover or a named disclosure unless § Exceptions records otherwise (`rulebook/rules.md § P21`); a heuristic is measured against the value § Adopted heuristics names, and not at all while none is adopted.
- An entry that removes a rule's obligation without being listed as an exception is reported once, as a question for § Open, and neither followed nor overruled in silence.
- An entry whose *Why* the code contradicts (the stated fact is false) is reported once, as a question for § Open with the evidence; the entry stays as written until the user answers.
- Where to look: navigation model → § Navigation model; where an object lives, is listed, edited, created, deleted and shown → § Objects; what is shown at which weight → § Information hierarchy; layout posture and density → § Screen defaults; everything else → the section named for the topic.

## Format

````markdown
---
app: <name>
updated: YYYY-MM-DD
approved: YYYY-MM-DD
rulebook: rulebook/rules.md
defaults: DF1–DF15 except DF8
companions: { glossary: _concept/glossary.md, visual: _concept/03_brand/identity.md, shell: _concept/07_screens/shell.md, decisions: _concept/10_blueprint/decisions.md }
---
# App design – <name>
## Context
Studio of 8; roles owner and designer; Nuxt UI; depth `standard`. [inferred] marks a fact taken from findings, not confirmed.
## Navigation model
organization: hybrid · primary_surface: sidebar
- **NAV-1 Primary entries: Project, Client, Invoice, and the Inbox workspace.** *Rules:* P12, P22.
## Objects
| id | object | home | index | editor (task → host) | create | delete | representations |
|---|---|---|---|---|---|---|---|
| OBJ-1 | Project | page | list-report | status: inline · contact: dialog · all: page | quick-create dialog → page | confirm naming tasks | row(name, status, due) · chip(name) · peek(+client, owner) |
| OBJ-2 | Task | n/a (Project section) | n/a | all: dialog | dialog | undo, H7 | row(title, assignee, status) |
## Information hierarchy
| object | attribute | tier | per-screen override (task reason) |
|---|---|---|---|
| Project | name · status · due date | 1 | board: owner → 1 (triage by owner) |
| Project | budget code | 3 | |

| tier | default visibility | emphasis | disclosure surfaces |
|---|---|---|---|
| 3 | on request | muted, labelled | peek, popover, named disclosure |
- **TIER-1 Tier policy as the rulebook states it.** *Rules:* P21.
## Screen defaults
| id | floorplan | posture | density |
|---|---|---|---|
| SCR-1 | list-report | sovereign | compact |
## Surfaces
- **SURF-1 A drawer reads and triages; editing opens a dialog or the page.** as DF2. *Rules:* P5.
## Modals
- **MOD-1 One dialog component owns busy lock and dirty guard.** as DF7. *Rules:* P5, P14.
## Popups
- **POP-1 Tooltips open on hover and focus; no `title=`.** as DF14. *Rules:* P16.
## Editing
- **EDIT-1 Dialogs hold at most 12 fields.** *Why:* three flat editors reach 11–12. *Rules:* P5; H1.
## Messages
- **MSG-1 Write errors on a page are inline alerts with retry.** *Rules:* P15.
## Buttons
- **BTN-1 Create actions carry a text label.** *Rules:* P17.
- **LANG-1 Verbs: Create · Add · Edit · Save · Delete · Remove, in the UI language; nouns from the glossary.** *Rules:* P11, P13.
## Find
- **FIND-1 Search is a mode of the Cmd/Ctrl-K palette.** as DF11. *Rules:* P9, P10.
## View state and disclosure
- **VIEW-1 Filters, sort and the selected item live in the URL on index screens.** *Rules:* P23; DF8.
## Feedback
- **FBK-1 Latency thresholds 0.1 s · 1 s · 10 s; one state per data region.** *Rules:* P26; H5; DF13.
## Interaction concepts
| id | purpose | operational principle | depends_on | refs |
|---|---|---|---|---|
| CON-1 Approval | a client signs off a deliverable | a designer requests approval; the client approves; the project moves on | — | NAV-1, Inbox |
## Adopted heuristics
| H id | adopted value | reason |
|---|---|---|
| H1 | 12 | see EDIT-1 |
## Exceptions
| deviation | rule id | reason |
|---|---|---|
| Budget code shown in a row | P21 | finance scans it daily, tier 3 outside a peek |
## Open
| id | question | options | recommendation |
|---|---|---|---|
| Q1 | Undo window for a deleted task? | 10 s · none | 10 s: cheap to build and recovers slips |
## Changelog
- YYYY-MM-DD · experience-interaction · adopted the defaults bundle
````

`approved:` is the universal approval field (`tree/README.md § Frontmatter every markdown artifact carries`): the date the user signed the file off, set beside `updated:`. A write the user has not approved moves `updated:` and leaves `approved:` at its last value.

- **Sections** appear in this order, every one present: a section the interview has not reached holds `Not decided — see Q<n>` and a § Open row. Entries are one line each, not hard-wrapped, so a diff shows one decision per line. Budget about 100–200 lines at `standard` depth.
- **Ids** are `PREFIX-n`, never reused; a revised decision keeps its id, a dropped one is struck through in § Changelog, not renumbered. Table rows carry their id in the first cell and are decided entries like any other.

| prefix | section | records | cites |
|---|---|---|---|
| NAV | Navigation model | which objects earn a primary entry, deep links | P12, P22 |
| OBJ | Objects | one row per object with `navigation` ≠ `none`; `n/a` where a cell does not apply (a read-only object has no editor) | P1, P2, P4, P6–P8 |
| TIER | Information hierarchy | tier policy changes and tier calls that need a reason | P21 |
| SCR | Screen defaults | posture and density per floorplan | P18–P20 |
| SURF · MOD · POP | Surfaces · Modals · Popups | the surface ladder's local thresholds, dialog behaviour, tooltip, popover, menu | P5, P7, P14, P16, P17 |
| EDIT · MSG | Editing · Messages | save model, create flow, delete confirmation; channels and empty states | P6, P7, P14, P15 |
| BTN · LANG | Buttons | button hierarchy, labels, the action registry; the verb set | P11, P13, P17 |
| FIND | Find | search, palette, shortcuts, list filters | P8–P11 |
| VIEW | View state and disclosure | restorable state, disclosure depth, visible modes | P23–P25 |
| FBK | Feedback | latency feedback, one state per region | P26 |
| CON | Interaction concepts | name, purpose, operational principle, dependencies | P27 |

- **Entry shape:** one bullet — imperative, applicable in a pull request without opening a source: `- **EDIT-1 Title.** the decision. *Why:* one line. *Rules:* P5, P14 adapt; DF5; H1. [open Q3]`. `adapt` after a rule id marks an entry that changes the rule's form and keeps its obligation; an adapted rule is not an exception. A rule adopted unchanged needs no entry.
- **Defaults** the app adopts are one entry each, in the section its rule belongs to, worded `as DF<n>` plus any local value; a declined default is a § Exceptions row citing its `DF` id, and `defaults:` in the frontmatter names the adopted ids.
- **Citations** are ids (`P5`, `H1`, `DF4`) and, where a section is meant, inline code such as `rulebook/rules.md § P5`. A decided entry whose cell, attribute or value rests on an unanswered question ends with `[open Qn]`; the § Open row stands alone — question, options, recommendation and its reason — because the person who answers it may never see the run that raised it.
- **Code locations** are not tracked here: violations, exemplars and fix sites live in `interaction.sarif`, where a re-run keeps them current. A code contract (the action registry's `id`, `label`, `icon`, `shortcut`, `scope`, `available`, `run`) sits in the BTN entry that owns it, as a short block in the stack's syntax.
- **Loading** belongs to § Feedback; responsive behaviour is the floorplan's § Responsive plus the shell's breakpoints, and is not written here.

## Writing it

`experience-interaction` is the only writer; any other skill with something to say records it in its own output and leaves the file as it is. Object names come from the glossary and the data model and are never coined here: two names for one object split every later entry that cites it.

1. **Resolve facts first** (`tree/README.md § How a skill runs`, rule 1). Read, in any order and none required: an existing `APP-DESIGN.md` as intent (§ Reading it: decided entries and exceptions are settled), `_concept/glossary.md` for the objects and their axes (`tree/glossary.md § Format`; a word on `_Avoid_` is renamed to its term), `_concept/10_blueprint/datamodel/model.json` for attributes, `_concept/04_journeys/stories.yaml` for roles and tasks, `_concept/07_screens/` for screens, and `_concept/02_grounding/findings/interaction.md`. Where the code holds evidence and no findings exist, run `concept-reverse` scoped to interaction. Without a glossary the object list comes from the data model, else the findings or the brief, and § Open asks for `concept-glossary` to pin the names.
2. **Sort before asking** (rule 4). Draft every section from what exists: one object-map row per object with `navigation` ≠ `none`, tiers proposed from the attributes, a floorplan per screen, interaction concepts from the glossary's operational principles. Mark each inferred entry `[inferred]`; ask only about gaps.
3. **Offer the defaults bundle** — one message offering to adopt `rulebook/defaults.md § Defaults`, DF1–DF15, at once: accept all, or pick. Each adopted default becomes an entry citing its id; each declined one becomes an § Exceptions row with its reason. A re-run offers only the ids not yet answered.
4. **Ask the depth** (rule 3): `sketch` writes § Context, § Navigation model, the object map for `navigation: primary` objects, the defaults and § Open, and every other section holds `Not decided` with its row; `standard` writes every section for every object with `navigation` ≠ `none`, tiers for primary objects, and the heuristics the batches settle; `exhaustive` adds tiers and per-screen overrides for every object, screen defaults per floorplan, the interaction concepts and every heuristic with its reason. Without a user, `standard` is recorded in § Context.
5. **Decide in batches** (rule 2). What remains after the bundle goes in batches by topic, each question with the recommendation first and a one-line consequence: the `rulebook/defaults.md § Decisions, not defaults` choices; the navigation model and primary surface; the heuristics to adopt (`rulebook/rules.md § Heuristics`); then the per-object calls (home, hosts, tiers) in the order that changes a screen's surface first. Without a user, the recommendation is written with `[open Qn]` on the entry and a stand-alone § Open row.
6. **Write after every batch**: create the file in the shape of § Format, or update it in place, leaving decided entries as written — flipping one needs the user's answer. Each write adds one § Changelog line and sets `updated:`. A rejected rule or accepted deviation goes to § Exceptions only on the user's answer. When the user says yes to the file in words, set `approved:` in the same write; an edit after that leaves it at its last value until the user says yes again.
7. **Refine in place.** On an existing `APP-DESIGN.md`, a request about one entry changes that entry alone and adds a § Changelog line; no interview reruns. A re-entry after a code check reads `_concept/11_build/interaction.sarif` (`tree/11_build/interaction.md § Format`): each proposed exception and each question in it is asked in the next batch as a new `Qn`; a yes to an exception enters § Exceptions, no answer becomes the § Open row `keep as exception?`. The verdict file is `quality-interaction`'s and stays as it is.
8. **Carry gaps and trade-offs to their homes.** A term the glossary lacks is appended there as a `proposed` entry (`tree/README.md § Ownership`) and the step carries on with it. A substantive choice with rejected options — hard to reverse, surprising without context — becomes a decision record (`tree/10_blueprint/decisions.md § Writing it`) and the entry cites its `DR-<n>`.

The completion summary (`tree/README.md § How a skill runs`, rule 8) says which entries a re-entry changed, so the screens that read them are re-checked.

## Checks

- Every section of § Format is present; a section not yet decided says so and has an § Open row.
- Every decided entry cites a `P`, `H` or `DF` id, or is a § Exceptions row.
- Every object in the glossary with `navigation` ≠ `none` has an object-map row (`n/a` cells allowed).
- Every attribute in the tier table has a tier; every tier-3 attribute shown outside a peek, a popover or a named disclosure has an § Exceptions row.
- Every adopted heuristic names its `H` id and value; § Navigation model has both `organization` and `primary_surface`.
- Every open question has a stable `Q<n>` id and a recommendation, and every `[open Qn]` entry has its row.
- The file was written after the last batch, carries `updated:`, and `approved:` is set — or § Open says why the user has not yet signed off.
