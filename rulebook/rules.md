# Rules

The invariants an app's `APP-DESIGN.md` adopts, then the tunable heuristics. Each rule has an id, a statement, one clause of why, and a source with a strength grade (`README.md § Strength grades`). A decided entry in the app wins over the rule it cites (`README.md`); an entry that removes an obligation is an exception.

An **object** is a noun the user manages (OOUX), including a derived object the UI shows but no table stores (an inbox item computed from deadlines); an **attribute** is one of its fields; a **surface** is the UI container an editor is hosted in; a **host** is a surface or page that mounts an object type's editor. Every object type has four axes, recorded where its term lives in `_concept/glossary.md`:

- `navigation: primary | contextual | none` — `primary` has its own navigation entry and index (P8); `contextual` is reached through a parent or a workspace; `none` is never navigated to;
- `lifecycle: independent | owned-by <Term> | link` — `owned-by` is deleted with its parent; `link` joins two objects and carries attributes of its own;
- `origin: user | system | derived` — `system` is generated or imported and read-only to users; `derived` is computed, not stored;
- `operations:` a subset of `create · read · edit · delete · archive` — the default permitted operations, narrowed by role in feature permissions.

An object with its own navigation entry and index is `navigation: primary`, whatever its field count.

## Invariants

### P1 — Canonical home

Every attribute has one semantic owner, the object it belongs to, and one canonical home, that object's detail view, where it is shown in full and where its editing behaviour is defined. An attribute that belongs to a relationship (a role on a membership, a price on an order line) lives on the `lifecycle: link` object, not on either side. The canonical home is where a link to the object lands; it is not the only place the attribute may be edited, since approved hosts edit through the same editor (P4).

*Why:* one owner keeps two screens from disagreeing, and approved hosts keep users from having to navigate home before acting. *Source:* OOUX; Fiori object handling (`standard`); owner and host kept apart by owner decision, 2026-10-21 (`owner`).

### P2 — Representations

Everywhere else an object appears as a declared *representation* — `row` (list or table), `card`, `chip` (inline reference), `peek` (hover or side preview) — each a fixed subset of attributes, the same subset on every screen, and each links to the canonical home. A representation is defined once per object type and reused; two screens rendering the same object with different subsets is a second, undeclared representation.

*Why:* an object that looks different on each screen reads as a different object. *Source:* OOUX; CLINICO and weiterbildungsplaner `APP-DESIGN.md` (`field`).

### P3 — Redundancy test

Repetition is legitimate when it is a representation (P2), a breadcrumb or page title naming the current object, an aggregate of children (count, sum, status rollup) that links to them, or one editor hosted in several approved places (P4). It is redundant when:

- the same attribute appears twice within one viewport (header and body, card and sidebar);
- the *editing behaviour* of an attribute — its validation, labels or write path — is implemented more than once, so two hosts can disagree (several hosts of one editor are not this);
- a derived value (status, deadline, total) is computed in more than one place, so two screens can disagree — or computed once and *stored*, so it goes stale when its inputs change (a generated invitation text that keeps the old date); two or more mutually exclusive state flags (`isLoading` and `isError`) stand for one status value;
- a screen exists only to show a subset another screen already shows, with no task of its own.

*Why:* redundancy is a defect when it can drift, not when it is repeated. *Source:* OOUX; React *Choosing the State Structure* (`standard`); owner decision, 2026-10-21, on duplicated behaviour vs several hosts (`owner`); generated-text staleness in weiterbildungsplaner (`field`).

### P4 — One editor per object type

Each object type has one editor component: one field set, one validation schema, one set of labels and help texts, one write path. Page, dialog, drawer, popover and inline control are *hosts* for that editor; the host supplies chrome (title, close, where the primary action sits), never fields. The hosts an editor may have are the approved task entry points listed per object type in the app's object map; a host not listed there is a finding. Partial editors (one section of a complex object) are slices of the same component, not re-implementations. What is flagged is a second implementation of the editing behaviour, never a second host.

*Why:* a type written by several components drifts in fields, rules and wording. *Source:* CLINICO OBJ-2 and weiterbildungsplaner OBJ-3 (`field`); several approved hosts, one behaviour: owner decision, 2026-10-21 (`owner`).

### P5 — Edit-surface ladder

Choose the least interruptive surface the task fits; move up only when a criterion forces it.

| surface | use when | move up when |
|---|---|---|
| inline (click-to-edit, autosave) | one scalar attribute, valid on its own, edited often (status, title, assignee, date) | the change needs other fields, review, or is costly to undo |
| popover | 2–3 tightly coupled fields (date range, time and timezone, picker with search), H2 | more fields, or the user needs to see the result in context |
| dialog | one self-contained object or section within the dialog field limit (H1), one step, no need to read the page behind it; every confirmation | the user must reference or copy from the background, or the form grows sections or child rows |
| drawer / side panel | reading and triage while the list or page behind stays readable — preview, assign, act on the next row | the task is an edit form: a drawer hosts an edit form only when the app records that decision |
| dialog or drawer with URL (`?<noun>=<id>`) | as the rows above, but the open object must be linkable, shareable or survive reload (P23) | the object has child collections or several sections |
| page (object page) | `navigation: primary` object with sections, child collections, multi-step or long work, drafts, deep links, collaboration | — |

Hard limits: no dialog on top of a dialog — a confirmation raised from an open editor replaces the editor's footer or content in place rather than stacking (P7 decides *whether* to confirm, this decides *where*); no tabs or wizard inside a dialog; an error or a feature announcement is never a dialog. A surface choice is per *editing task*, so one object can be edited inline for its status, in a dialog for its contact data and on its page for everything else — all through the one editor of P4. On a narrow viewport a dialog that holds fields becomes full-screen or a bottom sheet (H11).

*Why:* every extra layer costs context and focus. *Source:* Primer Dialog; Fiori; Smashing decision tree; Cloudscape (`standard`); CLINICO SURF-2, SURF-3 and weiterbildungsplaner SURF-1 (`field`).

### P6 — Create

Creation uses the same editor in *create mode* (P4). A simple object — a flat form within the dialog limit — opens a dialog or drawer, then the user stays in context. A complex object — one with sections or child collections, so its home is an object page — gets a quick-create dialog asking only the required fields, then navigates to the new object's page. "Add" (attach an existing object) is a picker, never the create editor; a picker offers "create new" when the object may not exist yet, which opens the editor in create mode and selects the result.

*Why:* one editor in two modes keeps create and edit from drifting. *Source:* Primer Saving (redirecting); CLINICO and weiterbildungsplaner (`field`).

### P7 — Delete and destructive actions

Confirmation scales with cost: undo (P15 says where it appears) for cheap, reversible deletes, within the undo window (H7); a confirm dialog naming the object and its consequences (children, links, with counts) for irreversible ones, its buttons saying what happens ("Delete room" / "Keep"), none of them the default. Whether an object's delete removes its `owned-by` children or is refused is stated in the confirmation. One confirm component, app-wide.

*Why:* confirmation fatigue hides the one irreversible action. *Source:* NN/g Confirmation dialogs; GitLab messaging (`standard`); CLINICO OBJ-10 and weiterbildungsplaner OBJ-8 (`field`).

### P8 — One index per primary object

Each `navigation: primary` object has one list screen with filter, sort, search and, where the scale warrants, saved views. A second list of the same objects is a saved view or a filter of the first, not another screen with its own columns and row actions.

*Why:* two lists of one object drift in columns and actions. *Source:* Fiori; weiterbildungsplaner FIND-4 (`field`).

### P9 — Global search finds nouns

One search entry point, reachable from every screen, searching every `navigation: primary` object type; results are grouped by type, each result a `row` representation that opens the canonical home. A full results page carries the filters; where each index already carries them, the group ends in "all results in <list>" opening that index filtered.

*Why:* users look for a noun, not for the screen that holds it. *Source:* Solomon; Setproduct (`standard`); CLINICO FIND-1..FIND-5 and weiterbildungsplaner FIND-1 (`field`).

### P10 — Command palette finds and does

The palette (Cmd/Ctrl-K) lists navigation targets, objects and *actions*, ranked in the order H8 gives: context first, so on an object's page its actions rank above global ones. Every palette action also exists in the visible UI — the palette accelerates and is never the only path — and shows its shortcut where one exists. Search and palette are one component in small apps (search is a mode of the palette) and side by side when search is a core feature. Single-key shortcuts never fire while an input has focus or a dialog is open.

*Why:* the palette serves experts without hiding anything from novices. *Source:* Solomon; Setproduct (`standard`); CLINICO FIND-5 and weiterbildungsplaner FIND-2, FIND-6 (`field`).

### P11 — One action registry

Every action (create, edit, archive, assign, export…) is defined once with label, icon, permission, availability rule and shortcut, and that definition feeds buttons, row menus, bulk actions, the palette and shortcuts; shortcuts live only there. Labels follow one verb set: *Create* (new), *Add* (attach existing), *Edit*/*Save*, *Delete*, *Remove* (detach), written in the UI language.

*Why:* an action defined twice gets two labels and two availability rules. *Source:* Solomon (`standard`); CLINICO NAV-2, BTN-14 and weiterbildungsplaner BTN-4 (`field`).

### P12 — Navigation from objects

In an object-led or hybrid app (P22), primary navigation lists the indexes of `navigation: primary` objects (P8) and the few cross-object workspaces (inbox, dashboard, calendar) that have a task of their own; `contextual` objects are reached through their parent. A top-level entry per feature or per settings page is a menu of the file system, not of the product. Settings are one entry. This rule sets the shape; the concrete destination list is `_concept/07_screens/shell.md`'s, derived under this rule and P22.

*Why:* people navigate to things they manage, not to features. *Source:* OOUX; Fiori (`standard`); CLINICO NAV-3 and weiterbildungsplaner NAV-1 (`field`).

### P13 — One noun per object

Each object and attribute has one user-facing name, taken from the project's glossary where one exists, and used unchanged in navigation, page titles, editor labels, representations, palette entries and messages. A field labelled three ways across three editors is one finding, not three. No implementation noun (record, payload, job) is shown raw.

*Why:* two names for one thing read as two things. *Source:* Johnson & Henderson; NN/g Top-10 mistakes (inconsistency) (`standard`); CLINICO LANG-2 and weiterbildungsplaner LANG-2, LANG-5 (`field`).

### P14 — One save model per form

Explicit *Save* for forms and declarative controls (text fields, checkbox groups, radios, multi-selects); autosave for imperative controls (switches, segmented controls) and P5's inline rung, with an inline "saving / saved" state and an inline error with retry that stays until the value is saved. One form uses one model and does not mix both. Leaving with unsaved changes asks — in-app for in-app navigation, `beforeunload` for the browser — and only when something would be lost; a dialog that can hold unsaved changes does not close on a backdrop click and does not close while a write is in flight. Save stays enabled on an invalid form and names what is missing next to the field, unless the app records the disabled-until-valid choice with a visible reason.

*Why:* a mixed model leaves the person guessing what has been saved. *Source:* Primer Saving; GitLab Saving; Cloudscape unsaved changes (`standard`); CLINICO EDIT-2..EDIT-4 and weiterbildungsplaner EDIT-1, EDIT-3, MOD-5 (`field`).

### P15 — Messages by channel

A result visible on the page needs no message; a success that is not visible is a toast; an error or blocking condition is an inline alert where it applies, with a way to recover, staying until resolved — not a toast, not a dialog; an announcement is a contextual hint where the feature lives, not a dialog; an empty state says what belongs there and offers the first action. A toast carries no action other than P7's undo, and that undo stays reachable by keyboard — otherwise it goes inline.

*Why:* a message the person cannot act on, or that disappears, is noise. *Source:* GitLab messaging (`standard`); CLINICO MSG-2, MSG-5 (`field`).

### P16 — Popups by purpose

A tooltip is short plain text, opens on hover *and* keyboard focus, holds nothing needed to finish the task and nothing clickable; the native `title` attribute fails the focus part and the touch part. A popover opens on click and may hold links, actions, the fields of P5's popover rung or a `peek` (P2). A dropdown menu holds actions or one choice, at most H9 items; once it needs search, filters or multi-select it is a popover or a dialog with Save and Cancel.

*Why:* a hint that exists only on hover is invisible to keyboard and touch users. *Source:* NN/g Tooltip guidelines; GitLab messaging (`standard`); CLINICO POP-1 and weiterbildungsplaner POP-1 (`field`).

### P17 — Buttons say what they do

A button carries a text label; the icon is optional and leads. Icon-only is for repeated, universally known actions in toolbars and rows (close, previous/next, reload, overflow), always with an accessible name and a tooltip (P16), and not for a view's primary or create action. One primary button per view or dialog, the rest of lower emphasis; destructive buttons use the error colour and sit apart from benign ones. Labels are active verbs from P11's verb set, with the object where unclear — "OK" and "Yes" say nothing about what happens. A dialog's footer reads destructive action left, then cancel, then the one primary at the right.

*Why:* a label that names the effect prevents the wrong click. *Source:* NN/g Icon usability, Proximity of consequential options; Carbon button usage; Primer Saving (`standard`); CLINICO MOD-2, BTN-11, BTN-12 and weiterbildungsplaner MOD-1, BTN-1, BTN-3 (`field`).

### P18 — Floorplan selection

A shell frame is chosen once for the app; a screen floorplan is chosen for each screen. Both come from `floorplans/` in this rulebook and are recorded (the frame in `_concept/07_screens/shell.md`, the floorplan in each screen's spec), with a deviation recorded as an exception. The choice follows the task, the object axes and the navigation model (P22), not habit. A screen that fits none is a signal to add a floorplan (`README.md § Adding or retiring`), not to draw an unnamed layout. An app may start from a row of `archetypes.md`, recorded as `archetype:` in `APP-DESIGN.md § Navigation model`; the row's frame and floorplans are its defaults until a NAV entry departs from them.

**Shell frames** — the regions that persist around every screen:

| id | fits |
|---|---|
| `shell-sidebar` | desktop-first apps with more than about five destinations or grouped ones; sovereign work; the sidebar collapses to a rail or drawer on narrow screens |
| `shell-topbar` | a few flat destinations, content first, light tools; the bar folds into a menu on narrow screens |
| `shell-mobile-tabs` | phone-first apps with three to five destinations within thumb reach; a "more" tab for the rest |
| `shell-dock` | desktop-native tools with resizable docked panes, toolbar and status bar |

**Screen floorplans** — one per screen, filling the frame's work area:

| id | fits |
|---|---|
| `list-report` | the index of one `navigation: primary` object: overview strip, filter bar, table or cards (P8, P30) |
| `object-page` | one object with a header, key facts, sections and child collections; the home of a complex object (P1, P6) |
| `master-detail` | browsing a list with the selected item's detail beside it; triage and edit-next |
| `three-pane` | a source rail, a work area and a management drawer; working across several sources |
| `overview` | the landing screen that answers "what needs me now" with the next actionable rows |
| `wizard` | a guided, linear task with independent steps, done rarely (P31) |
| `settings` | grouped configuration with section or tab navigation; not for domain objects |
| `board` | the same items in columns or switchable views (kanban, calendar, list) with a card drawer |
| `reader` | consuming content: filters, a list or tree and a reading pane |
| `mode-editor` | one artefact edited in several modes, with a visible mode menu (P25) |
| `hub-areas` | a phone-sized hub of tiles leading to areas and guided walks; few areas, task-led |
| `tabbed-tool` | a single-column tool with a tab list, a shared filter row and an overlay detail |

Responsive layout is the floorplan's: each floorplan declares how it folds on a narrow viewport, and a screen follows that transformation unless it records another.

*Why:* a layout chosen from a catalogue is previewable, reviewable and reusable; one drawn per screen is none of these. *Source:* devBench layout survey of 21 projects (`field`); SAP Fiori floorplans (`standard`); the catalogue and the shell-frame/screen split: owner decision, 2026-10-21 (`owner`).

### P19 — Declared posture

Each screen and surface declares one posture. **Sovereign**: a long, daily work surface, optimised for people who stay — density at or above the app's default (P20), keyboard accelerators, a persistent status or context line, no wizard for routine work. **Transient**: comes, does one job, leaves — one view, labelled buttons with full verbs, no nested dialog or tab, Esc and Enter work, the last values are remembered. **Auxiliary**: a supporting view beside the work — small, yields space to the host, reads and triages (a drawer or side panel). A mismatch (a sovereign surface styled like a wizard, a dialog styled like a mini-app) is one finding. Posture sets defaults for who uses a screen how often; it never lowers accessibility.

*Why:* how often and how long people use a surface decides its density and input. *Source:* Cooper *About Face*, application posture (`standard`; read via a text mirror, not the 4th edition); posture as usage context, never a reason to lower accessibility: owner decision, 2026-10-21 (`owner`).

### P20 — Density

A screen declares one density — `compact`, `default` or `comfortable` — and a table or list uses one density tier throughout. Header, toolbar, batch bar and pagination use the same size token as the rows; the tallest tier is for rows that hold two lines; a toolbar shows at most H4 actions before an overflow menu; no table sits inside a table or a cramped container; labels truncate before data does. The pixel values are the app's design system's, adopted as H3.

*Why:* mixed row heights make a dense screen read as noise. *Source:* Carbon data table guidelines (`standard`; read to about line 300 of 392).

### P21 — Information tiers

Every attribute of an object has a default tier, recorded once per object in the app's information hierarchy, with a sparse per-screen override and its task reason. **Tier 1** is what identifies the object and what a task decides on: it is always visible, in the region the screen's floorplan marks primary (title, header, row, card). **Tier 2** is context for the task: visible in the floorplan's secondary regions or sections of the object's own screen, and not in rows by default. **Tier 3** is detail on request: shown only in a peek, a popover or a disclosure that has a named, keyboard- and touch-accessible entry point, never in a row. Information the primary task needs is promoted whatever its default tier. This policy is the default; an attribute the app shows against it is recorded in `§ Exceptions`.

The tier-rendering policy table the app keeps, filled with these defaults:

| tier | default visibility | emphasis | permitted disclosure surfaces |
|---|---|---|---|
| 1 | always, in the primary region | strongest weight and size; the value above its label | row, card, page header, title |
| 2 | always on the object's own screen, in secondary regions or sections | normal | detail section, side panel, facts block, expandable row |
| 3 | on request only | muted, labelled | peek, popover, named disclosure |

*Why:* "appears in a row" is not "is primary"; a tier says why information is shown and what its disclosure costs. *Source:* tier defaults, the rendering policy and tier 3 as a default with recorded exceptions: owner decision, 2026-10-21 (`owner`).

### P22 — Navigation model

The app records one navigation model: `organization: object-led | task-led | hybrid` and `primary_surface: sidebar | topbar | tabs | rail+drawer | bottom-tabs | none`. The shell holds one destination list, from which every navigation surface (sidebar, rail, drawer, tab bar, palette entries, shortcut hints) is rendered; no surface keeps a second list. The shell frame of P18 realises the primary surface, and every value maps to a frame: `sidebar` takes `shell-sidebar`, or `shell-dock` when the app is a desktop-native tool with docked panes (P18) and the nav-pane's top section is the destination list; `rail+drawer` takes `shell-sidebar`; `topbar` and `tabs` take `shell-topbar`; `bottom-tabs` takes `shell-mobile-tabs`; `none` takes `shell-dock`, the one-workspace tool whose tree is the content. A phone-sized hub (`hub-areas`) has no navigation surface and no frame in P18 realises it, so it records its frame as an exception. Where the model is still a fallback — the app groups destinations by feature set because nobody decided — the shell says so visibly, so the fallback is not mistaken for the design.

*Why:* an unrecorded navigation model is re-decided by every screen. *Source:* navigation model as a recorded choice: owner decision, 2026-10-21 (`owner`); CLINICO NAV-2 and weiterbildungsplaner NAV-1 (`field`).

### P23 — View state is restorable

For sovereign work screens, the state a person sets up — filters, sort, selected tab, pagination, search term, selected item — survives navigating away and back, and a reload. It lives in the URL (the query carries only deviations from the default, and the selected object as `?<noun>=<id>`) or is persisted per user; a shared link reproduces the view. An unknown or vanished id opens the page's info state, never another object. Transient surfaces start fresh.

*Why:* losing the view on every round trip makes work surfaces expensive to use. *Source:* Tognazzini State; Shneiderman history (`standard`); weiterbildungsplaner FIND-3, CLINICO NAV-12 and the devBench survey's `?node=` and `?view=` (`field`).

### P24 — Disclosure depth

A screen discloses at most H6 levels beyond its first. The common task is completable at the first level with sane defaults; the control that opens the next level is visible and named for what it holds; an overflow menu named "More", "Tools" or "…" never holds unrelated verbs — groups are named. A staged flow (wizard) is for steps that are mostly independent; steps that need each other sit on one screen. Tier 3 information (P21) is reached through its named entry point.

*Why:* more than two levels of disclosure loses people. *Source:* NN/g Progressive disclosure; NN/g Top-10 mistakes (junk drawers); Ousterhout *overexposure* (`standard`).

### P25 — Modes are visible

Every persistent mode — edit mode, bulk selection, filter scope, active tool, "view as" — shows an indicator at the place of action, makes its scope explicit (which row, cell or section is editable), exits in one step, and does not survive navigation silently. Per-action scope or hold-to-activate is preferred to a lasting mode. A shortcut keeps its meaning in every context. A mode switch for a whole screen (the `mode-editor` floorplan) is a visible menu, never a hidden gesture.

*Why:* the same input with a different invisible result causes errors after any interruption. *Source:* Raskin *The Humane Interface*; NN/g Top-10 mistakes (poor feedback); Tognazzini (`standard`).

### P26 — Latency feedback

Feedback is proportional to the wait, with thresholds adopted as H5. An instantaneous response needs none; a longer asynchronous action shows an immediate indicator on the control or region; a wait beyond about a second shows a skeleton or spinner in the region that is loading, not a blocking page spinner; a wait beyond about ten seconds shows determinate progress when the work is measurable and honest indeterminate feedback, with cancel or background, when it is not. Status is accurate (no fake progress); an optimistic update rolls back visibly on failure. Each data region shows exactly one of loading, content, empty or error at a time, and one failing region never blanks its siblings. This rule carries loading states; P14 carries save feedback.

*Why:* an unexplained wait reads as a broken app. *Source:* NN/g Top-10 mistakes; Laws of UX (Doherty threshold); Nielsen response-time limits (`standard`); CLINICO MSG-1 and weiterbildungsplaner MSG-3 (`field`).

### P27 — Concept purpose and integrity

The app keeps an inventory of its *interaction concepts*, each a name, a one-line purpose, an operational principle of at most three steps that shows the purpose fulfilled, and the concepts it `depends_on`. Every navigation entry and major feature maps to one concept; one with no purpose is a candidate for removal. A concept whose purpose needs "and" is checked for overloading (a status that is both workflow state and archive flag), and two concepts with one purpose are checked for redundancy; both are prompts to look, not proofs. A concept behaves the same on every host, with exceptions named. A silent cascade (an action that triggers another) is visible, announced and reversible, and a concept is not reachable without the concept it depends on.

*Why:* conceptual defects cost the most to change and cause most real user problems. *Source:* Jackson *The Essence of Software*; Johnson & Henderson (`standard`); the "and" test is a prompt (`heuristic`).

### P28 — Reset states its scope

A control named Default, Reset or Restore says what it resets (this field, this section, everything) and what is lost, and is placed where it visibly belongs to that scope — on the tab for a tab's reset, on the panel for the whole panel's.

*Why:* an unbounded reset is a destructive action in disguise. *Source:* Tognazzini Defaults (`standard`).

### P29 — No cross-screen memory

A step that asks the user to enter or verify a value shows the source that value depends on on the same screen (a peek, a side reference, an inline summary); data the system already knows is not typed again.

*Why:* working memory is the most expensive store in the interface. *Source:* Nielsen heuristic 6; Shneiderman golden rule 8; Tognazzini Anticipation (`standard`).

### P30 — Overview, filter, detail

A collection or dashboard screen shows an overview (counts, status, summary) before its rows. Rows carry the attributes a person needs to *decide*, tier 1 (P21), not only to identify; the applied filters and sort are visible with "n of N" and a one-click clear-all; row-to-detail is on demand (peek or detail) and never the only way to compare. The first column, row title or card heading is the name a person uses; ids, codes and GUIDs are secondary (a later column, the peek, a tooltip) and coded values are expanded to labels. Where people act on sets, history and extract (export, copy) are available.

*Why:* people scan the whole before they narrow it, and a row that cannot be decided on forces a click per item. *Source:* Shneiderman visual information-seeking mantra; Victor *Magic Ink*; NN/g Top-10 mistakes (meaningful identifier first) (`standard`); the overview rule of CLINICO NAV-9 (`field`).

### P31 — Closure

A multi-step flow shows its position (step n of m), allows backward movement without losing data, and ends on a completion state that says what was created or changed and offers the next task.

*Why:* people need to know a task is finished, and what comes next. *Source:* Shneiderman golden rule 4; Laws of UX (goal-gradient) (`standard`).

## Heuristics

Values practitioners use that sources do not fix. None is enforced until the app adopts a value in `APP-DESIGN.md`; the adopting entry names the `H` id, and a check measures against the adopted value only. Strength is the strength of the evidence for the value, not of the rule it serves.

| id | heuristic | range / default | source | strength |
|---|---|---|---|---|
| H1 | dialog field limit: fields in one dialog form, one step (P5) | ~12–16; no collection default, the app picks. Earlier guidance said ~8 | CLINICO SURF-2 (~16); weiterbildungsplaner SURF-1 (~12) | `field` (diverges) |
| H2 | popover field limit (P5) | 2–3 coupled fields | CLINICO POP-2; weiterbildungsplaner POP-2 | `field` |
| H3 | density row heights (P20): compact · default · comfortable | 32 · 40 · 48 px; 64 px only for two-line rows; header, toolbar, batch bar and pagination match the row; values follow the app's design system | Carbon data table | `standard` |
| H4 | toolbar actions before overflow (P20) | ≤ 5 | Carbon data table | `standard` |
| H5 | latency thresholds (P26): instantaneous · indicator · progress | 0.1 s · 1 s · 10 s; an alternative reading is 0.4 s · 2 s · 10 s | Nielsen response-time limits; NN/g Top-10 mistakes; Laws of UX (Doherty) | `standard` |
| H6 | disclosure depth budget (P24): levels beyond the first | ≤ 2 | NN/g Progressive disclosure | `standard` |
| H7 | undo window for a reversible delete, including a child row (P7) | 5–10 s, default 10 s; or none where no history store exists | CLINICO EDIT-6 (10 s); weiterbildungsplaner EDIT-4 (none) | `field` (diverges) |
| H8 | palette ranking order (P10) | current object's actions · the page's actions · global actions · destinations · objects; ties keep that order | CLINICO FIND-5; weiterbildungsplaner FIND-2; Solomon | `field` |
| H9 | items in a dropdown menu (P16) | ≤ ~8, destructive item last after a separator | CLINICO POP-3 | `heuristic` |
| H10 | validation timing (P14) | on blur and on submit; debounce live checks ~500 ms | GitLab delayed feedback | `standard` |
| H11 | narrow-viewport breakpoint where a dialog with fields goes full-screen (P5) | ≤ 640 px; shell breakpoints (768, 992) are the shell's | CLINICO MOD-6 | `heuristic` |
| H12 | key facts in an object page header (P21, `object-page`) | 3–5 | Fiori object page | `standard` |

## Sources

Short names used above. A source read through a mirror or only in part is flagged in the rule that cites it.

- OOUX / ORCA — Sophia Prater, [A List Apart](https://alistapart.com/article/ooux-a-foundation-for-interaction-design/).
- NN/g — [Icon Usability](https://www.nngroup.com/articles/icon-usability/); [Tooltip Guidelines](https://www.nngroup.com/articles/tooltip-guidelines/); [Confirmation Dialogs](https://www.nngroup.com/articles/confirmation-dialog/); [Proximity of Consequential Options](https://www.nngroup.com/articles/proximity-consequential-options/); [Top 10 Application-Design Mistakes](https://www.nngroup.com/articles/top-10-application-design-mistakes/); [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/); [Ten Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/).
- Primer (GitHub) — [Saving](https://primer.style/product/ui-patterns/saving/); [Dialog guidelines](https://primer.style/product/components/dialog/guidelines).
- GitLab Pajamas — [Choosing a messaging pattern](https://design.gitlab.com/patterns/choosing-a-messaging-pattern); [Saving and feedback](https://design.gitlab.com/patterns/saving-and-feedback).
- Cloudscape — [Communicating unsaved changes](https://cloudscape.design/patterns/general/unsaved-changes/).
- Carbon — [Button usage](https://v10.carbondesignsystem.com/components/button/usage/); [Data table guidelines](https://www.carbondesignsystem.com/building-blocks/core/components/data-table/guidelines).
- SAP Fiori — [Object Handling](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/best-practices/global-patterns/object-handling/manage-objects); [Object Page](https://www.sap.com/design-system/fiori-design-web/v1-145/page-types/floorplans/object-page).
- Solomon — [Designing Command Palettes](https://solomon.io/designing-command-palettes/); Setproduct — [Command palette, 8 states](https://www.setproduct.com/blog/command-palette-ui-design-guide).
- Smashing (Friedman) — [Modal vs. Separate Page decision tree](https://www.smashingmagazine.com/2026/03/modal-separate-page-ux-decision-tree/).
- Jackson — [The Essence of Software](https://essenceofsoftware.com/); Johnson & Henderson — [Conceptual Models in a Nutshell](https://boxesandarrows.com/conceptual-models-in-a-nutshell/).
- Shneiderman — [Eight Golden Rules](https://www.cs.umd.edu/users/ben/goldenrules.html); [The Eyes Have It](https://hci.stanford.edu/courses/cs448b/papers/shneiderman96eyes.pdf).
- Tognazzini — [First Principles of Interaction Design](https://asktog.com/atc/principles-of-interaction-design/).
- Cooper *About Face* (application posture, via a [text mirror](https://flylib.com/books/en/2.153.1.43/1/)); Raskin *The Humane Interface*; Victor [Magic Ink](https://worrydream.com/MagicInk/); Laws of UX [lawsofux.com](https://lawsofux.com/); Ousterhout *A Philosophy of Software Design*; React [Choosing the State Structure](https://react.dev/learn/choosing-the-state-structure).
- Field: the `APP-DESIGN.md` files of CLINICO and weiterbildungsplaner (entry ids as cited) and the devBench layout survey of 21 projects. `owner` rows cite the owner's decisions of 2026-10-21, which are not outside evidence.
