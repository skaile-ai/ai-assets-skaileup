---
path: APP-DESIGN.md
summary: the app's interaction decisions — where objects live, editing, saving, finding
owner: [experience-interaction]
may_propose: []
---

# APP-DESIGN.md

`APP-DESIGN.md` sits at the project root — the directory holding `_concept/` — beside `_concept/`, the one project-root artifact. It records how this app applies the rulebook in § Patterns: where each object lives, which surface edits what, how saving, messages, popups and buttons work, how people find and trigger things. Coding agents and reviewers cite its ids (`MOD-2`) instead of re-deriving a rule, so a missing or contradictory entry is re-decided differently in every screen.

It holds *decisions*; findings, plans and questions stay in the output of the run that raised them. It repeats none of its neighbours:

- `_concept/glossary.md` — what things are called (the nouns);
- `_concept/03_brand/identity.md` — how it looks and sounds;
- `_concept/07_screens/shell.md` — the concrete navigation;
- `docs/adr/` — decisions of architecture.

`build-scaffold` writes a line in the project's root `AGENTS.md` that points coding agents here, creating the file when it creates the project. In a project that existed before scaffolding the skills leave `CLAUDE.md` and `AGENTS.md` alone, and the plan says the link is missing.

## Format

```markdown
---
app: <name>
updated: YYYY-MM-DD
approved: YYYY-MM-DD
rulebook: tree/APP-DESIGN.md § Patterns
companions: { visual: _concept/03_brand/identity.md, glossary: _concept/glossary.md, shell: _concept/07_screens/shell.md, adr: docs/adr/ }
---
# App design – <name>
## Context              scale, roles, UI stack – the facts the decisions rest on
## Objects              floorplan table, representations, entity-page entries
## Surfaces             SURF
## Modals               MOD
## Popups               POP
## Editing              EDIT
## Messages             MSG
## Buttons              BTN
## Search and commands  FIND
## Navigation           NAV
## Language             LANG
## Exceptions           table: id · entry or rule · exception · reason
## Open                 table: id · question · recommendation
## Changelog            one line per write: date · skill or person · what changed
```

`approved:` is the universal approval field (`tree/README.md § Frontmatter every markdown artifact carries`): the date the user signed the file off, set beside `updated:`. A write the user has not approved moves `updated:` and leaves `approved:` at its last value.

A section with nothing decided yet is left out; whoever fills it later inserts it in this order. Entries are one line each, not hard-wrapped, so a diff shows one decision per line. Budget about 100–200 lines; a floorplan table that outgrows it moves to `docs/app-design/objects.md` and § Objects links it.

§ Objects holds, in order: the floorplan table (one row per type users act on — a `system` type users only read is left out; class from § Patterns, plus `simple` or `complex` for core and supporting types), the representations table (`row`, `card`, `chip`, `peek` with their field subsets), per type its `task → surface` list and palette actions, then the OBJ entries. Table rows are decided entries like any other: a row resting on an unanswered question ends with `[open Qn]`, and a single cell resting on one carries it in the cell (`change [open Q1]`).

§ Language holds the verb set (create / add / edit / save / delete / remove, in the UI language) and points at `_concept/glossary.md` for the nouns; it lists no nouns itself, so the glossary stays their one home. § Navigation holds the rule — which objects earn a primary entry, how deep links work (P12, P9) — and not the concrete navigation, which `_concept/07_screens/shell.md` carries.

| area | decides | rules |
|---|---|---|
| OBJ | per type: class, home, index, editor, create, delete, representations, in search, editing tasks and their surfaces; entity-page anatomy; edit model of a page | P1, P2, P4–P8 |
| SURF | the edit-surface ladder and its local thresholds; what a drawer may host | P5 |
| MOD | footer layout, dismissal while dirty, stacking, linkable dialogs, narrow viewports | P5, P7, P14 |
| POP | tooltip, popover, dropdown menu, peek | P16, P2 |
| EDIT | save model, unsaved changes, validation and disabled Save, create flow, confirm vs undo | P14, P6, P7 |
| MSG | toast vs inline alert vs nothing, announcements, empty states | P15 |
| BTN | icon vs text, hierarchy, placement, labels, destructive styling, action registry | P17, P11 |
| FIND | search entry and scope, results page, palette content and order, shortcuts, list filters | P8–P11 |
| NAV | the navigation rule: which objects earn a primary entry, deep links | P12, P9 |
| LANG | the verb set; nouns come from the glossary | P13, P11 |

### Entries

One bullet per decision — imperative, applicable in a pull request without opening a source:

```markdown
- **MOD-2 Dirty dialogs ask before closing, in place.** <the rule>. *Why:* <one line: app fact or source>. *Ref:* `path/from/repo/root.vue:12-30`. *Rules:* P5, P14 adapt. [open Q3]
- **MOD-3 No modal over a modal.** <the rule>; two dialogs still stack it (change). *Ref:* none yet. *Change:* `path/to/a.vue:234`, `path/to/b.vue:241`. *Rules:* P5, P7.
```

- **Ids** are `AREA-n`, never reused. A revised decision keeps its id; a dropped one is struck through in § Changelog, not renumbered.
- **Ref** is the exemplar a fix copies; `Ref: none yet` when the code has none. A deviation the code still has is marked `(change)` in the rule text and its sites go in a `*Change:*` field after *Ref* — `*Change:* path/a.vue:12, path/b.vue:40` — not explained; past three sites, the count and the first site — the rest are in the findings. A deviation that is an absence (a missing query parameter) has no site; the rule text names what is missing.
- **Rules** names the rules the entry applies; `adapt` after a rule id when the entry changes the rule's form (P5's ~8 fields become ~12). An adapted rule is not an exception.
- **Code contracts** sit in the entry that owns them, as a short code block in the stack's syntax: the editor shape (`mode`, section subset, events) under the OBJ entry, the action registry entry (`id`, `label`, `icon`, `shortcut`, `scope`, `available`, `run`) under BTN.
- **§ Exceptions** holds rejected rules and accepted deviations from an entry, each with its reason.
- **Status:** an entry is decided unless it carries `[open Qn]`; the question and its recommended answer are in § Open. A § Open row stands alone — question, options, recommendation and its reason — because the person who answers it may never see the run that raised it; an empty § Open says "No open questions." A rule adopted unchanged is decided by adoption and needs no question; `[open Qn]` marks an entry that rests on a question asked and not yet answered.

## Patterns

The rulebook the interaction skills apply. Each rule has an id (`P1`…`P17`) so a finding, an entry or a plan step can cite it in one token. An **object** is a noun the user manages (OOUX) — including a *derived* object the UI shows but no table stores (an inbox item computed from deadlines); an **attribute** is one of its fields; a **surface** is the UI container an editor is hosted in. Every object has one **class**:

- `core` — users reach it from navigation or search and maintain it in its own right (it has an index, P8);
- `supporting` — reached only through other objects, but with a life of its own (shared, linked from several parents);
- `child` — exists only inside one parent and dies with it;
- `junction` — a relationship carrying attributes of its own;
- `system` — created by the app or an import, its fields read-only to users (mails received, logs, derived objects).

An object with its own nav entry and index is `core`, whatever its field count. The rules are defaults: a decided entry in the app's `APP-DESIGN.md` takes precedence over the rule it cites.

### P1 — Canonical home

Every attribute has exactly one home: the detail view of the object that owns it. That is where it is shown in full and where it is edited. An attribute that belongs to a relationship (a role on a membership, a price on an order line) lives on the junction object, not on either side.

### P2 — Representations

Everywhere else an object appears as a declared *representation* — `row` (list/table), `card`, `chip` (inline reference), `peek` (hover or side preview) — each a fixed subset of attributes, the same subset on every screen, and each links to the canonical home. A representation is defined once per object type and reused; two screens rendering the same object with different subsets is a second, undeclared representation.

### P3 — Redundancy test

Repetition is legitimate when it is a representation (P2), a breadcrumb or page title naming the current object, or an aggregate of children (count, sum, status rollup) that links to them. It is redundant when:

- the same attribute appears twice within one viewport (header and body, card and sidebar);
- the same attribute is *editable* in more than one place (breaks P1);
- a derived value (status, deadline, totals) is computed in more than one place, so two screens can disagree — or computed once and *stored*, so it goes stale when its inputs change (a generated invitation text that keeps the old date);
- a screen exists only to show a subset another screen already shows, with no task of its own.

### P4 — One editor per object type

Each object type has one editor component: one field set, one validation schema, one set of labels and help texts. Page, drawer and modal are *hosts* for that editor; the host supplies chrome (title, close, primary action placement), never fields. Partial editors (one section of a complex object) are slices of the same component, not re-implementations.

### P5 — Edit-surface ladder

Choose the least interruptive surface the task fits; move up only when a criterion forces it.

| surface | use when | move up when |
|---|---|---|
| inline (click-to-edit, autosave) | one scalar attribute, valid on its own, edited often (status, title, assignee, date) | the change needs other fields, review, or is costly to undo |
| popover | 2–3 tightly coupled fields (date range, time + timezone, picker with search) | more fields, or the user needs to see the result in context |
| modal | one self-contained object or section, ≤ ~8 fields, one step, no need to read the page behind it; destructive confirmations | the user must reference or copy from the background, or the form grows sections |
| drawer / side panel | medium form while the list or page behind stays readable — triage row by row, edit-next | the object has child collections or several sections |
| modal or drawer with URL (`?item=<id>`) | as either row above, but the open item must be linkable, shareable or survive reload | the object has child collections or several sections |
| page (object page) | core object with sections, child collections, multi-step or long work, drafts, deep links, collaboration | — |

Hard limits: no modal on top of a modal — a confirmation raised from an open editor replaces the editor's footer or content in place rather than stacking (P7 decides *whether* to confirm, this decides *where*); no tabs or wizard inside a modal; an error or a feature announcement is never a modal. A surface choice is per *editing task*, so one object can be edited inline for its status, in a modal for its contact data and on its page for everything else — all through the one editor of P4.

### P6 — Create

Creation uses the same editor in *create mode*. Simple objects: modal or drawer, then stay in context. Complex objects: a quick-create modal asking only the required fields, then navigate to the new object's page. "Add" (attach an existing object) is a picker, never the create editor.

### P7 — Delete and destructive actions

Confirmation scales with cost: undo (P15 says where it appears) for cheap, reversible deletes; confirm dialog naming the object and its consequences (children, links) for irreversible ones, its buttons saying what happens ("Delete room" / "Keep"), none of them the default. One confirm component, app-wide.

### P8 — One index per core object

Each core object has one list screen with filter, sort, search and saved views. A second list of the same objects is a saved view or a filter of the first, not another screen with its own columns and row actions.

### P9 — Global search finds nouns

One search entry point, reachable from every screen, searching every core object type; results grouped by type, each result a `row` representation that opens the canonical home. A full results page carries the filters.

### P10 — Command palette (Cmd/Ctrl-K) finds and does

It lists navigation targets, objects and *actions*. Context first: on an object's page its actions rank above global ones. Every palette action also exists in the visible UI — the palette accelerates and is never the only path — and shows its shortcut where one exists. Search and palette are one component in small apps (search is a mode of the palette) and side by side when search is a core feature.

### P11 — One action registry

Every action (create, edit, archive, assign, export…) is defined once with label, icon, permission, availability rule and shortcut, and that definition feeds buttons, row menus, bulk actions, the palette and shortcuts. Labels follow one verb set: *Create* (new), *Add* (attach existing), *Edit*/*Save*, *Delete*, *Remove* (detach).

### P12 — Navigation from objects

Primary navigation lists core objects (their P8 indexes) and the few cross-object workspaces (inbox, dashboard, calendar) that have a task of their own; supporting objects are reached through their parent. A top-level entry per feature or per settings page is a menu of the file system, not of the product. This rule sets the shape; the concrete navigation is `_concept/07_screens/shell.md`'s, and `experience-shell` derives it under this rule.

### P13 — One noun per object

Each object and attribute has one user-facing name, taken from `_concept/glossary.md` where one exists, and used unchanged in navigation, page titles, editor labels, representations, palette entries and messages. A field labelled three ways across three editors is one P13 finding, not three.

### P14 — One save model per form

Explicit *Save* for forms and declarative controls (text fields, checkbox groups, radios, multi-selects); autosave for imperative controls (switches, segmented controls) and P5's inline rung, with an inline "saving / saved" state and an inline error with retry that stays until the value is saved. One form uses one model and does not mix both. Leaving with unsaved changes asks — in-app for in-app navigation, `beforeunload` for the browser — and only when something would be lost; a dialog that can hold unsaved changes does not close on a backdrop click.

### P15 — Messages by channel

A result visible on the page needs no message; a success that is not visible is a toast; an error or blocking condition is an inline alert where it applies, with a way to recover, staying until resolved — not a toast, not a modal; an announcement is a contextual hint where the feature lives, not a modal; an empty state says what belongs there and offers the first action. A toast carries no action other than P7's undo, and that undo stays reachable by keyboard — otherwise it goes inline.

### P16 — Popups by purpose

A tooltip is short plain text, opens on hover *and* keyboard focus, holds nothing needed to finish the task and nothing clickable — the native `title` attribute fails the focus part. A popover opens on click and may hold links, actions, the fields of P5's popover rung or a `peek` (P2). A dropdown menu holds actions or one choice; once it needs search, filters or multi-select it is a dialog with Save and Cancel.

### P17 — Buttons say what they do

A button carries a text label; the icon is optional and leads. Icon-only is for repeated, universally known actions in toolbars and rows (close, previous/next, reload, overflow), always with an accessible name and a tooltip (P16), and not for a view's primary or create action. One primary button per view or dialog, the rest of lower emphasis; destructive buttons use the error colour and sit apart from benign ones. Labels are active verbs from P11's verb set, with the object where unclear — "OK" and "Yes" say nothing about what happens.

## Decision catalogue

The agenda for the interview that fills the file. Each row is one decision `APP-DESIGN.md` should hold, with the default the cited source gives. ⚖ marks rows where sources disagree: these are the questions worth the user's time, because without a recorded choice two developers pick two answers. Rows without ⚖ are offered as "take the default?" and batched. The `id` is the suggested entry id in its area; an existing file's ids win. `P<n>` cites § Patterns.

### Objects and entity pages (OBJ)

| id | decision | research default | alternatives / conflict | source |
|---|---|---|---|---|
| OBJ-1 | floorplan per object type: home, index, editor, create, delete, representations, in search | core types get an object page, simple types a dialog | — | P1/P2/P4/P8; Fiori object handling |
| OBJ-2 | entity page anatomy | header with title, status, 3–5 key facts, primary action + overflow menu; sections with anchor navigation; child collections as tables inside their section | tabs instead of anchors when sections are heavy and independent | Fiori object page |
| OBJ-3 | edit model on the entity page | one edit mode at a time, one save per page or form | section-wise edit; whole-page draft (Fiori draft handling) | Primer Saving (placement); Fiori draft handling |

### Surfaces and modals (SURF, MOD)

| id | decision | research default | alternatives / conflict | source |
|---|---|---|---|---|
| SURF-1 | edit-surface ladder with local thresholds | inline → popover → modal (≤ ~8 fields) → drawer → page | the field limit is app-specific | P5; Fiori; Smashing decision tree |
| SURF-2 ⚖ | may a drawer host create/edit forms? | yes for triage and edit-next while the list stays readable (P5) | **Primer: side sheets not for create/edit forms, use a page** | P5; Primer Dialog |
| MOD-1 | modal anatomy | title required; × always visible; body scrolls; footer: primary rightmost, Cancel left of it, auxiliary (Delete) on the left | — | Primer Dialog, Primer Saving |
| MOD-2 | dismissal while dirty | backdrop does not dismiss a dialog that can hold unsaved changes; Esc/×/Cancel ask before discarding; ask only when something would be lost; no "don't ask again" | — | Primer Dialog (backdrop); Cloudscape unsaved changes |
| MOD-3 ⚖ | stacking | no modal over a modal; a confirmation replaces the footer | **Primer allows two nested dialogs with correct focus return** | P5; Primer Dialog |
| MOD-4 ⚖ | deep-linkable modals | modal/drawer with `?item=<id>` when the item must be linkable | **Primer: if it needs a link, prefer a page – a dimmed page loses context** | P5; Primer Dialog |
| MOD-5 | content limits | single column; no tabs, wizard or side navigation inside; not for errors or announcements | — | Primer Dialog; Smashing |
| MOD-6 | narrow viewports | centred dialog becomes full-screen or a bottom sheet | which of the two | Primer Dialog |

### Popups (POP)

| id | decision | research default | alternatives / conflict | source |
|---|---|---|---|---|
| POP-1 | tooltip | short plain text; opens on hover *and* keyboard focus; holds no information needed to finish the task; not interactive; used consistently or not at all | — | NN/g Tooltip guidelines; GitLab messaging |
| POP-2 | popover | opens on click (not hover, focus or load); may hold links, actions, 2–3 coupled fields or an object preview; Esc/outside click closes | — | GitLab messaging; P5 |
| POP-3 | dropdown menu | a list of actions or single choices only; once it gains search, filters or multi-select it is a dialog with Save/Cancel | — | Primer Saving (dropdown accessibility) |
| POP-4 | peek / hover card | preview of an object (`peek` representation) linking to the home; tap/click opens it on touch | hover-only preview | P2; NN/g (tooltips unavailable on touch) |

### Editing and saving (EDIT)

| id | decision | research default | alternatives / conflict | source |
|---|---|---|---|---|
| EDIT-1 | save model per control type | explicit save for forms and declarative controls (text, checkbox group, radio, native select, multi-select); autosave for imperative controls (switch, segmented control, single-select menu); one model per form | autosave whole long forms (GitLab: per input, not whole forms) | Primer Saving; GitLab Saving |
| EDIT-2 | autosave feedback | inline "Saving…" / "Saved" near the control; a failure is an inline alert with retry that stays until saved, not a toast | — | GitLab Saving |
| EDIT-3 | unsaved changes on leave | in-app confirm for in-app navigation, `beforeunload` for browser actions, only when dirty | — | Cloudscape; Primer Saving; GitLab safety measure |
| EDIT-4 ⚖ | invalid or unchanged form: disable Save? | **Primer: keep Save enabled** – disabled buttons cannot be focused and are hard to read; validate on submit | disable until required fields are filled (common, Nuxt UI default) | Primer Saving (state) |
| EDIT-5 | create flow | simple: modal, stay in context; complex: quick-create with required fields, then go to the new object's page | — | P6; Primer Saving (redirecting) |
| EDIT-6 ⚖ | delete: confirm or undo | confirm only consequential, irreversible actions; name the object and its consequences; buttons say what happens ("Delete room" / "Keep"), no default on the destructive button; typed confirmation only for the rarest | **undo toast (P7, NN/g favour undo) vs GitLab: toasts cannot hold actions accessibly, undo goes inline** | NN/g Confirmation dialogs; GitLab messaging; P7 |
| EDIT-7 | validation timing | at field on blur and on submit; debounce live checks ~500 ms | — | GitLab delayed feedback |

### Messages (MSG)

The GitLab decision tree is the most complete source and orders the questions: does this message need to exist at all → result of the user's action → system condition → feature discovery → explanation → empty → catch-up later.

| id | decision | research default | source |
|---|---|---|---|
| MSG-1 | result visible on the page | show nothing, or a brief state on the control (check on the copy button) | GitLab messaging |
| MSG-2 | success not visible | toast, without actions | GitLab messaging |
| MSG-3 | errors and blocking conditions | inline alert with a recovery path, stays until resolved; not a toast, not a modal | GitLab messaging; P5 |
| MSG-4 | announcements | no notice, or a contextual hint where the feature lives; banner last; not a modal | GitLab messaging |
| MSG-5 | empty states | say what belongs here and offer the first action | GitLab messaging |

### Buttons (BTN)

| id | decision | research default | alternatives / conflict | source |
|---|---|---|---|---|
| BTN-1 | icon or text | text label, icon optional and leading; only home, print and search icons are near-universal | — | NN/g Icon usability |
| BTN-2 | when icon-only is allowed | repeated, universally known actions in dense toolbars and rows (close, search, previous/next, overflow ⋯); always `aria-label` plus a tooltip on hover and focus; not for the view's primary or create action | — | NN/g Icon usability; NN/g Tooltip guidelines |
| BTN-3 | hierarchy | one primary per view or dialog; secondary/ghost for the rest; toolbars and rows use low emphasis | — | Carbon button usage; Primer Saving (appearance) |
| BTN-4 ⚖ | placement | dialogs: bottom right, Cancel left of primary | **page forms: Primer bottom-left with Cancel right of Save**; many systems mirror dialogs | Primer Saving, Primer Dialog |
| BTN-5 | labels | active verb, plus the object where unclear ("Save profile"); no "OK", "Yes", "Done"; verb set from LANG | — | Primer Saving (text); NN/g Confirmation dialogs; P11 |
| BTN-6 | destructive actions | error colour; kept apart from benign actions | — | NN/g Proximity of consequential options |
| BTN-7 | action registry | every action defined once (label, icon, shortcut, availability) and rendered as button, menu item, palette entry and shortcut | — | P11 |

### Search and commands (FIND)

| id | decision | research default | alternatives / conflict | source |
|---|---|---|---|---|
| FIND-1 | central search entry | one entry point on every screen, in a fixed place (header or sidebar), with a shortcut | — | P9; Solomon |
| FIND-2 | search scope and results | every core object type, results grouped by type, each result opens the canonical home; recents when the query is empty | — | P9; Solomon; Setproduct (8 states) |
| FIND-3 | full results page | yes when search is a core feature (filters live there) | none in small apps | P9 |
| FIND-4 | search vs command palette | one component in small apps (search is a mode of the palette); separate when search is core | — | P10; Solomon |
| FIND-5 | palette content and order | context actions of the current object first, then navigation, objects, global actions; every entry also exists in the visible UI; shows its shortcut | — | P10; Solomon |
| FIND-6 | shortcuts | defined in the action registry; shown in palette and tooltips; single-key shortcuts do not fire inside inputs `[INFERENCE]` | — | P11; Solomon |
| FIND-7 | list search and filters | one filter bar component per index; saved views only when the scale warrants them | — | P8 |

### Navigation and language (NAV, LANG)

| id | decision | research default | source |
|---|---|---|---|
| NAV-1 | primary navigation rule | core object indexes plus workspaces with a task of their own; supporting objects through their parent; settings under one entry. The concrete navigation is `_concept/07_screens/shell.md`'s | P12 |
| NAV-2 | deep links | every object home has a URL; search results and chips link there | P9; P2 |
| LANG-1 | vocabulary | one noun per object from `_concept/glossary.md`; one verb set (create / add / edit / save / delete / remove, in the UI language) | P13; P11 |

Not catalogued: loading states, responsive layout and motion — visual or component concerns for `_concept/03_brand/identity.md` and the components themselves.

### Sources

- OOUX / ORCA — Sophia Prater, [A List Apart](https://alistapart.com/article/ooux-a-foundation-for-interaction-design/), [ooux.com](https://ooux.com/resources/introducing-orca-the-third-diamond-in-your-ux-process)
- NN/g — [Icon Usability](https://www.nngroup.com/articles/icon-usability/); [Tooltip Guidelines](https://www.nngroup.com/articles/tooltip-guidelines/); [Confirmation Dialogs](https://www.nngroup.com/articles/confirmation-dialog/); [Modal & Nonmodal Dialogs](https://www.nngroup.com/articles/modal-nonmodal-dialog); [Proximity of Consequential Options](https://www.nngroup.com/articles/proximity-consequential-options/)
- Primer (GitHub) — [Saving](https://primer.style/product/ui-patterns/saving/); [Dialog guidelines](https://primer.style/product/components/dialog/guidelines)
- GitLab Pajamas — [Choosing a messaging pattern](https://design.gitlab.com/patterns/choosing-a-messaging-pattern); [Saving and feedback](https://design.gitlab.com/patterns/saving-and-feedback)
- Cloudscape (AWS) — [Communicating unsaved changes](https://cloudscape.design/patterns/general/unsaved-changes/)
- Carbon — [Button usage](https://v10.carbondesignsystem.com/components/button/usage/)
- SAP Fiori — [Object Handling](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/best-practices/global-patterns/object-handling/manage-objects); [Object Page](https://www.sap.com/design-system/fiori-design-web/v1-145/page-types/floorplans/object-page); [Draft Handling](https://www.sap.com/design-system/fiori-design-web/v1-145/foundations/best-practices/global-patterns/object-handling/draft-handling)
- Sam Solomon — [Designing Command Palettes](https://solomon.io/designing-command-palettes/); Setproduct — [Command palette, 8 states](https://www.setproduct.com/blog/command-palette-ui-design-guide)
- Vitaly Friedman — [Modal vs. Separate Page decision tree](https://www.smashingmagazine.com/2026/03/modal-separate-page-ux-decision-tree/); Ryan Neufeld — [Modal vs Page framework](https://uxplanet.org/modal-vs-page-a-decision-making-framework-34453e911129); [PatternFly inline edit](https://v5-archive.patternfly.org/components/inline-edit/design-guidelines)

## Reading it

Each reader opens the file at its first step, as intent, before judging anything:

- `spec-feature` — each screen takes the surface of each editing task from the OBJ `task → surface` rows. A screen that needs a surface the floorplan lacks is handed back to `experience-interaction`; the screen spec does not invent one.
- `experience-shell` — derives the navigation under the NAV rule and takes MSG, EDIT and MOD patterns from the entries instead of deciding them.
- `ops-review` — checks screen specs against the entries.
- `quality-interaction` — checks the app's source against the entries.
- `build-plan` — reads the verdict at `_concept/11_build/interaction.sarif` (format: `tree/11_build/interaction.md`), not the file itself.

How a reader applies what it reads:

- A decided entry replaces the default of the rules it cites. Code that deviates is one finding, filed under the entry with the rule tagged (`MOD-2 / P5`), counted once.
- A deviation listed in § Exceptions is not reported.
- An `[open Qn]` entry is judged by its recommendation, and the finding is tagged `[Qn]`.
- An entry that removes a rule's obligation without being listed as an exception is reported once, as a question for § Open, and neither followed nor overruled in silence.
- An entry whose *Why* or *Ref* the code contradicts (the cited line says otherwise, the stated fact is false) is reported once, as a question for § Open with the evidence; the entry stays as written until the user answers.

## Writing it

`experience-interaction` is the only writer. It creates the file and keeps every section; any other skill that has something to say about the file records it in its own output and leaves the file as it is. Object names come from `_concept/10_blueprint/datamodel/model.json` and `_concept/glossary.md` and are never coined here: two names for one object would split every later entry that cites it.

### Procedure (experience-interaction)

1. **Read the ground.** Open an existing `APP-DESIGN.md` first as intent (§ Reading it): its decided entries and exceptions are settled and later steps draft only what it lacks. Then `_concept/10_blueprint/datamodel/model.json` (without it, the glossary's nouns and the brief carry the object list), `_concept/glossary.md`, and `_concept/04_journeys/stories.yaml` for roles and the tasks each journey performs (without it, the brief's audience and hero flow). Without `_concept/glossary.md` the object list comes from `_concept/02_grounding/findings/datamodel.md`, else from the schema and census the findings or the code give, and § Open gets one row asking for `concept-glossary` and the data-model step to pin the names. Where `_concept/02_grounding/findings/interaction.md` exists the app is a retrofit: every decision it records and grades is recommended as it stands wherever it passes the rule, so the file renames and fixes what the code does rather than redesigns it. Where `_concept/11_build/interaction.sarif` exists, this is a re-entry: go to step 7.
2. **Classify the objects.** One row per object the model or glossary names, with its class (`core`, `supporting`, `child`, `junction`, `system`, as defined in § Patterns), `simple` or `complex` for core and supporting types, and the roles that edit it (one line when the app has one role). A word on the glossary's `_Avoid_` list is renamed to its term. A concept the files do not name is not appended here: name it and hand back, and the flow re-enters `concept-glossary`, which pins it before this step goes on. A `system` type users only read is listed once and leaves the later tables.
3. **Decide the global rules.** For each of `P1`–`P17`: `adopt`, `adapt` with the adapted wording, or `reject`, each with a one-line reason grounded in this app's size, users and UI stack. An adaptation keeps the rule's obligation and changes its form; one that removes the obligation is a `reject` and is written as one, because it lands in § Exceptions.
4. **Draft each type's floorplan.** One row per non-system type: index · canonical home · editor · create flow · delete confirmation · representations with their field subsets · in search. Under it, per type, its editing tasks as `task → surface` and its palette actions. In a retrofit mark each cell `as-is` or `change`.
5. **Ask in rounds.** Everything above is a draft until the user has answered the decisions a reasonable maintainer could make the other way, taken from § Decision catalogue: the ⚖ rows and the core and supporting types' calls first, those that change a screen's surface before the rest. A round is at most five questions, each its own message (`tree/README.md § How a skill runs`), each with the recommendation first and its reason; the rows without ⚖ go as one "take these defaults?" message. Open questions already in § Open come first. Without a user, the ⚖ rows and the core and supporting types' calls are written as the recommendation with `[open Qn]` on the entry, and each question is a § Open row that stands alone: question, options, recommendation and why. The defaults without ⚖ are written as decided, and one § Open row asks the user to sign off the file. New questions take the next number after the highest `Qn` the file has ever used, § Changelog included.
6. **Write `APP-DESIGN.md` after every round**, not once at the end: create it in the shape of § Format, or update it in place, leaving decided entries as written — flipping one needs the user's answer. Decisions become entries in their area (§ Format, Entries); the floorplan and representations go to § Objects; a rejected rule or accepted deviation goes to § Exceptions only on the user's answer. Each write adds one § Changelog line and sets `updated:`. When the user says yes to the file in words, set `approved:` in the same write; an edit after that leaves it at its last value until the user says yes again.
7. **Fold in a code check.** Where `_concept/11_build/interaction.sarif` exists (`tree/11_build/interaction.md`), read its `fail` results as the violations, `runs[0].properties.changes` as the `(change)` candidates, the results carrying an `underReview` suppression as the proposed exceptions and `runs[0].properties.questions` as questions. Mark the entries they name `(change)` with their sites (past three sites, the count and the first), and ask each proposed exception and question in the next round, as new `Qn`: a yes to an exception enters § Exceptions, no answer becomes the § Open row `keep as exception?`. The verdict file is `quality-interaction`'s and stays as it is.
8. **Hand off.** Name what reads the file next: `spec-feature` applies the OBJ `task → surface` rows to every screen and hands a screen that needs a surface the floorplan lacks back to this skill; `experience-shell` derives the navigation under § Navigation and takes MSG, EDIT and MOD from the entries. Say which rows a re-entry changed, so those screens are re-checked.

## Checks

- Every rule `P1`–`P17` has a decision with a reason, and every non-system type has a floorplan row.
- Every contested decision is answered, or is an `[open Qn]` entry with a stand-alone § Open row.
- The file was written after the last round, carries `updated:`, and `approved:` is set — or § Open says why the user has not yet signed off.
- Every `Ref` and `Change` site passes the citation check in `tree/02_grounding/findings/interaction.md § Verifying citations`, like any artifact.
