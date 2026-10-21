# Defaults

Rules that CLINICO and weiterbildungsplaner, two apps by different teams on different domains, derived independently and identically. Each default implements an invariant of `rules.md` in one concrete form and cites the entries that carry it in those projects (`field` evidence, `README.md § Strength grades`).

The defaults are one bundle. `experience-interaction` offers it as "adopt all defaults" in a single question, and the app records one `defaults:` line in its `APP-DESIGN.md` frontmatter naming the adopted ids. A default the app declines is one row in `§ Exceptions` citing its `DF` id and the reason, and is left off that line; a default the app adopts needs no entry of its own, except where the app adds a value of its own. What the projects decided differently is not here but under `## Decisions, not defaults`.

## Defaults

### DF1 — Surface ladder: inline, popover, dialog, page

Edit on the lowest rung that fits the task: inline for one scalar, a popover for two or three coupled fields, a dialog for one self-contained form in one step, a page for anything with sections or child rows. A dialog that needs the page behind it for reference is a page.

*Implements:* P5, P6. *Field evidence:* CLINICO SURF-2; weiterbildungsplaner SURF-1.

### DF2 — A drawer reads and triages, never edits

A drawer or side panel lists, previews and triages rows; any editing opens a dialog or the object's page.

*Implements:* P5. *Field evidence:* CLINICO SURF-3 (the only drawer is the inbox panel); weiterbildungsplaner SURF-1 (slideover only for read-and-triage panels).

### DF3 — No dialog over a dialog; a confirmation replaces the footer in place

A confirmation or scope question raised inside an open editor swaps the editor's footer for the question; it never opens a second layer. A confirmation raised from a page, with no dialog under it, is the app's one confirm dialog.

*Implements:* P5, P7. *Field evidence:* CLINICO MOD-4; weiterbildungsplaner MOD-3, MOD-4.

### DF4 — Footer order: destructive left, cancel, one primary right

A dialog footer reads `[Delete] ··· [Cancel] [Primary]`: the destructive action apart on the left, cancel next, the one filled primary at the right. A read-only dialog has only Close.

*Implements:* P17, P5. *Field evidence:* CLINICO MOD-2; weiterbildungsplaner MOD-1.

### DF5 — A dirty dialog asks before closing, in place

A dialog with unsaved input never closes silently: Esc, the close control and Cancel swap the footer to "discard changes?" with a keep-editing choice focused first, and a backdrop click does nothing. A clean dialog closes at once. A full-page form with unsaved changes asks before in-app navigation and before closing the tab.

*Implements:* P14. *Field evidence:* CLINICO MOD-3, EDIT-4; weiterbildungsplaner MOD-2, EDIT-3.

### DF6 — Busy lock

A dialog that is running a request cannot be dismissed meanwhile; a failure stays in the footer or beside the field.

*Implements:* P14. *Field evidence:* CLINICO MOD-1 (close and Esc disabled while a write is in flight); weiterbildungsplaner MOD-5.

### DF7 — One shared dialog component, one confirm component

Every editor and picker dialog is one app-wide dialog component that owns modality, width, the busy lock, the dirty guard and the footer slot; every confirmation without a dialog under it is one confirm component whose body names the effect and whose primary says what happens. Raw library dialogs are kept for display-only overlays (palette, keyboard help).

*Implements:* P5, P7. *Field evidence:* CLINICO MOD-1; weiterbildungsplaner MOD-1, MOD-4.

### DF8 — An object is reachable by `?<noun>=<id>`

An existing object that opens in a dialog is addressed on its page by a query key named for the noun: opening sets it, closing removes it, reload re-opens it, Back closes it, and an unknown id opens the page's info state, never another object. The key is built in one function. A dialog for a transient thing (confirm, picker) has no key.

*Implements:* P5, P9, P23. *Field evidence:* CLINICO MOD-5, NAV-12; weiterbildungsplaner MOD-6, FIND-3.

### DF9 — One editor per type; hosts supply chrome

Each object type has one editor component with a `create`/`update` mode; page, dialog and section hosts supply title, close and the place of the commit button, never fields. The editor reports `dirty` and `submit`; the host owns the guard and the write boundary.

*Implements:* P4, P6. *Field evidence:* CLINICO OBJ-2; weiterbildungsplaner OBJ-3.

### DF10 — Representations are declared once per type

Each object type declares its `row`, `card`, `chip` and `peek` subsets once, one component each, and every screen that shows the type reuses them; each links to the type's home through one link-building function.

*Implements:* P2. *Field evidence:* CLINICO `docs/app-design/objects.md`; weiterbildungsplaner OBJ-2, OBJ-6, OBJ-10.

### DF11 — Search is a Cmd/Ctrl-K palette that ranks page actions first

Search is a mode of the command palette, reachable from every screen by a visible trigger and the shortcut. On an object's page the palette lists that page's actions above global actions, then destinations, then objects, and shows each action's shortcut; every palette action also exists in the visible UI.

*Implements:* P9, P10. *Field evidence:* CLINICO FIND-1, FIND-5; weiterbildungsplaner FIND-1, FIND-2, FIND-5.

### DF12 — One registry feeds every navigation and action surface

Destinations are defined once and render the sidebar, the rail, the mobile drawer, the tab bar and the palette; actions are defined once (label, icon, shortcut, availability) and render buttons, menus, the palette and shortcuts. No surface keeps a second list.

*Implements:* P11, P22. *Field evidence:* CLINICO NAV-2, BTN-14; weiterbildungsplaner BTN-4.

### DF13 — A page-state component with exactly one state per data region

Every data region is one page-state component showing exactly one of loading, content, empty or error (and, where the app has them, denied or no-match); one failing region never blanks the page or its siblings, and an error offers retry.

*Implements:* P15, P26. *Field evidence:* CLINICO MSG-1; weiterbildungsplaner MSG-3.

### DF14 — Tooltip on hover and focus; `title=` is banned

Every hover hint is a tooltip component that opens on hover and on keyboard focus; the native `title` attribute is not used. Nothing needed to finish a task lives only in a tooltip. An icon-only button's tooltip and accessible name are one string.

*Implements:* P16, P17. *Field evidence:* CLINICO POP-1; weiterbildungsplaner POP-1.

### DF15 — Shortcuts are suppressed while a dialog is open or an input has focus

A single-key shortcut does not fire while a dialog, drawer or palette is open or a text field, select or editable region has focus; the one chord that opts in to typing (Save) is named. Every shortcut comes from the action registry (DF12) and is shown beside its action.

*Implements:* P10, P11. *Field evidence:* CLINICO FIND-2, FIND-6; weiterbildungsplaner FIND-6, BTN-4.

## Decisions, not defaults

Choices the two projects made differently, each legitimately. The app decides each one and records the choice in its own entry; the options are what to offer, and the heuristic row carries any value.

| decision | options seen | carried by |
|---|---|---|
| dialog field limit | about 12 (weiterbildungsplaner, three flat Stammdaten editors of 11–12 fields); about 16 (CLINICO). Earlier guidance said about 8 | `H1` in `rules.md § Heuristics` |
| delete of a child row | an inline undo bar for about 10 s, nothing confirmed (CLINICO); immediate, no confirm and no undo because no history store exists (weiterbildungsplaner) | `H7`; rule `P7` |
| write errors on a page | an inline alert with retry that stays until resolved, a toast only for a row action with no host (CLINICO, `P15`); an error toast built by one function, input kept, the triggering button as the retry (weiterbildungsplaner, recorded there as an exception to `P15`) | none: an entry under messages names the choice |
| create button: icon-only or labelled | an icon-only filled "new" button with a tooltip and accessible name at every width (CLINICO, an exception to `P17`); a text label on create actions, icon-only reserved for repeated universal actions (weiterbildungsplaner, `P17`) | none: an entry under buttons names the choice |
| autosave scope | autosave for imperative controls only, never mixed into a form (CLINICO); two decided paths on one detail page, a save bar for scalar fields and instant writes for status, child collections and notes, the path readable at each control (weiterbildungsplaner, recorded there as an exception to `P14`) | none: an entry under editing names the choice |
