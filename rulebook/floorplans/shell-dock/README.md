---
id: shell-dock
kind: shell
summary: Title bar, toolbar, docked resizable panes and status bar for native tools
posture: sovereign
density: compact
---

# shell-dock — Dock shell

The frame for a desktop-native tool used for long sessions on one workspace: a title bar and a toolbar on top, resizable docked panes side by side (a navigation tree, the working list or tree, a detail panel) and a status bar below. The window is the frame and never scrolls; each pane scrolls on its own. Selected by `rulebook/rules.md § P18` for tools with docked, resizable panes, a toolbar and a status bar, which is the shape of a desktop-native app or of a web app that imitates one.

## Regions
| region | role | default tier | holds |
|---|---|---|---|
| title-bar | chrome | — | app and workspace name, current screen title, window or account controls |
| toolbar | chrome | — | at most five actions, then an overflow; the palette trigger; view switches |
| nav-pane | navigation | — | the destination list at the top, the object tree of the current destination beneath |
| list-pane | primary | 1 | the working list, table or tree; the screen floorplan lives here |
| detail-pane | secondary | 2 | the selected object's facts and child rows, read-first, in context |
| more-details | tertiary | 3 | a named disclosure inside the detail pane for detail on request |
| status-bar | chrome | — | counts and selection, background work and sync state, the active mode (`rulebook/rules.md § P25`) |
| palette | chrome | — | the `⌘K` overlay: actions, destinations, objects (`rulebook/rules.md § P10`) |

Tier 3 surfaces in the `more-details` disclosure of the detail pane, opened by a named control that works by keyboard and touch, and in tooltips and popovers of the toolbar and rows; never in the list rows, the title bar or the status bar (`rulebook/rules.md § P21`).

## Posture and density
Sovereign (`rulebook/rules.md § P19`): a persistent status line, keyboard accelerators for every toolbar action, no wizard for routine work, the layout restored on the next launch. Density is compact (`rulebook/rules.md § P20`) — rows, the toolbar and the status bar share one size token. Pane widths, tree expansion and the selected node persist per user and the selected object is addressable (`rulebook/rules.md § P23`).

Navigation model: realises `primary_surface: sidebar` when the nav-pane's top section is the destination list, and `primary_surface: none` when the tool has one workspace and the tree is the content. It never realises `topbar`, `tabs`, `bottom-tabs` or `rail+drawer`.

Destination list: one list from `_concept/07_screens/shell.md`, rendered as the top section of the nav-pane and in the palette's destination group; the toolbar carries actions only. No surface keeps its own copy (`rulebook/rules.md § P22`). Settings is one entry (`rulebook/rules.md § P12`).

Palette and shortcuts: the search field in the toolbar is the palette trigger and `⌘K` / `Ctrl-K` opens it from every pane. Every toolbar action shows its shortcut in its tooltip and in the palette, from the action registry (`rulebook/rules.md § P11`); a single-key shortcut never fires while an input has focus or a dialog is open. The status bar shows the hint for the palette.

## Responsive
- **Wide, ≥ 992 px:** nav-pane, list-pane and detail-pane docked side by side with draggable splitters; the list-pane takes the remaining width.
- **768 px up to 991 px:** the panes stay docked at their minimum widths (nav-pane 200 px, detail-pane 260 px); the toolbar shows icons with tooltips beyond the first two labelled actions.
- **Narrow, ≤ 767 px (including 640 px):** one pane at a time, switched by a segmented control (Navigate · List · Detail) under the toolbar; selecting a node in Navigate shows List, selecting a row shows Detail, and Back goes the other way. The toolbar keeps the primary action and an overflow menu; the status bar stays. A dock is a desktop tool, and an app that is mainly used at this width uses `shell-mobile-tabs`.

## Interaction constraints
- The detail pane reads and triages; an edit form opens in a dialog, a popover or the object page, and the pane hosts one only when the app records that decision (`rulebook/rules.md § P5`).
- The detail pane shows tier 2 only by default; tier 3 stays behind `more-details` (`rulebook/rules.md § P24`).
- The nav-pane holds destinations and the object tree for navigation, never actions; the toolbar holds actions and one palette trigger, never destinations (`rulebook/rules.md § P12`).
- At most five toolbar actions before the overflow, whose groups are named (`rulebook/rules.md § Heuristics`, H4).
- A mode (selection, an active tool) shows in the status bar and at the place of action, and ends in one step (`rulebook/rules.md § P25`).
- Forbidden: a second destination list, a wizard for routine work, a window-level scrollbar, panes that hide a splitter's handle.

## Sketch
```text
wide (>= 992 px)
+----------------------------------------------------------------------+
| title-bar   Studio Tracker - Projects                                |
+----------------------------------------------------------------------+
| toolbar  [Create] [Duplicate] [Archive] | view: [list][tree]  [^K]   |
+-------------+---+-----------------------------------+---+------------+
| nav-pane    | | | list-pane                         | | | detail-pane|
|  Overview   | | |  row  row  row  row  row  row     | | |  facts     |
|  Projects * | | |  row  row                         | | |  tasks     |
|  ...        | | |                                   | | | > more-    |
|  tree       | | |                                   | | |   details  |
+-------------+---+-----------------------------------+---+------------+
| status-bar  8 of 12 - 1 selected            synced 2 min ago   ^K    |
+----------------------------------------------------------------------+

narrow (<= 640 px)
+--------------------------------+
| title-bar                      |
| toolbar  [Create]        [...]  |
| [Navigate] [List] [Detail]     |
+--------------------------------+
| list-pane  (one pane at a time)|
|  row / row / row               |
+--------------------------------+
| status-bar  8 of 12            |
+--------------------------------+
```

## When not to use
- Grouped destinations and pages rather than panes: `shell-sidebar`.
- A few flat destinations, content first: `shell-topbar`.
- A phone-first app with three to five destinations: `shell-mobile-tabs`.
- A transient, one-job tool with no persistent trees or status line: `shell-topbar`.
