---
id: shell-mobile-tabs
kind: shell
summary: Fixed top bar and bottom tab bar, three to five destinations plus More
posture: transient
density: comfortable
---

# shell-mobile-tabs — Mobile tab shell

The frame for a phone-first app whose few destinations stay within thumb reach: a fixed top bar names the screen and carries its one action, the work area scrolls between the bars and a bottom tab bar switches destinations, with a More tab for the rest. Selected by `rulebook/rules.md § P18` when the navigation model (`rulebook/rules.md § P22`) is `bottom-tabs` and the app has three to five destinations that matter most.

## Regions
| region | role | default tier | holds |
|---|---|---|---|
| top-bar | chrome | — | back or title · badge · search icon · the one create or primary action |
| work-area | primary | 1 | the screen floorplan, one column, the only scrolling region |
| tab-bar | navigation | — | the first destinations of the list as icon + label tabs, then More |
| more-sheet | navigation | — | the remaining destinations of the same list, in a bottom sheet |
| detail-sheet | tertiary | 3 | read-only detail of a row, in a bottom sheet, closed until asked |
| palette | chrome | — | full-screen search and action overlay opened from the top bar's search icon |

Tier 3 surfaces in the detail-sheet, opened by a named "Details" control on the row that works by touch and keyboard; never in the top bar or the tab bar (`rulebook/rules.md § P21`).

## Posture and density
Transient (`rulebook/rules.md § P19`): one view, labelled buttons with full verbs, no nested tab or dialog, the last values remembered when a screen is reopened. Density is comfortable (`rulebook/rules.md § P20`): touch targets of at least 44 px, rows of two lines. Sovereign work (long sessions, dense tables, shortcuts) is not this frame's job.

Navigation model: realises `primary_surface: bottom-tabs` only. It never realises `sidebar`, `topbar`, `tabs`, `rail+drawer` or `none`.

Destination list: one list from `_concept/07_screens/shell.md`. The first four entries render as tabs and the rest, at least two, in the More sheet; with five destinations or fewer there is no More and all of them are tabs. The same list feeds the palette's destination group. No surface keeps its own copy (`rulebook/rules.md § P22`). Settings is one entry and sits in More (`rulebook/rules.md § P12`).

Palette and shortcuts: the search icon in the top bar opens the palette as a full-screen overlay; where a hardware keyboard exists (tablet, desktop), `⌘K` / `Ctrl-K` opens it too. Shortcut hints appear only in the palette and only where a hardware keyboard is detected; shortcuts never fire while an input has focus (`rulebook/rules.md § P10`, `rulebook/rules.md § P11`).

## Responsive
- **Wide, ≥ 960 px:** the app stays one column, at most 480 px wide and centred; the top bar and the tab bar span the column, not the viewport. An app that needs more width is not phone-first: use `shell-sidebar` or `shell-topbar`.
- **Narrow, ≤ 640 px:** the column is the viewport. Top bar fixed at the top, tab bar fixed at the bottom with the safe-area inset added; the tab bar hides while a text field has focus and the on-screen keyboard is up. The sheets fill the width and at most 60 % of the height.
- **Between:** the column stays centred; nothing folds further.

## Interaction constraints
- Sheets read and triage; a form is a full-screen page pushed over the tab's stack or a bottom sheet that fills the screen (`rulebook/rules.md § P5`, `rulebook/rules.md § Heuristics`, H11). A drawer hosts an edit form only when the app records that decision.
- Each tab keeps its own stack, scroll position and filters when the user switches away and back (`rulebook/rules.md § P23`); tapping the active tab returns to its root.
- A pushed screen shows a back control in the top bar; the tab bar stays visible.
- Tabs carry a text label as well as an icon (`rulebook/rules.md § P17`); at most five slots including More.
- More holds destinations only, no actions and no unrelated verbs (`rulebook/rules.md § P24`).
- Forbidden: a hamburger drawer next to the tab bar, a second destination list, navigation that works only by swipe, a dialog on top of a sheet.

## Sketch
```text
wide (>= 960 px): the same column, centred
        +--------------------------------+
        | top-bar   Projects  (s) [Create]|
        +--------------------------------+
        | work-area                      |
        |  Brand refresh        Active   |
        |  Website relaunch     In review|
        |  ...                           |
        | detail-sheet (when open)       |
        +--------------------------------+
        | tab-bar  Overview Projects     |
        |          Tasks Invoices  More  |
        +--------------------------------+

narrow (<= 640 px)
+--------------------------------+
| top-bar   Projects  (s) [Create]|
+--------------------------------+
| work-area                      |
|  card / card / card / card     |
|                                |
| more-sheet: Clients Reports    |
|             Settings           |
+--------------------------------+
| tab-bar  O   P   T   I   More |
+--------------------------------+
```

## When not to use
- More than about five destinations, or sovereign desktop work: `shell-sidebar`.
- A few flat destinations on a desktop-first app: `shell-topbar`.
- A desktop-native tool with docked panes, toolbar and status bar: `shell-dock`.
- A phone-sized hub of tiles leading to areas and guided walks rather than tabs: the `hub-areas` screen floorplan with `primary_surface: none`.
