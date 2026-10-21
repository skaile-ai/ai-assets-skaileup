---
id: shell-topbar
kind: shell
summary: Few flat destinations in a top bar, content first, light tools
posture: transient
density: comfortable
---

# shell-topbar — Top bar shell

The frame for an app with a few flat destinations that people visit, do one thing in and leave: one top bar holds the brand, the one destination list, search and the create action, and the whole width below it belongs to the screen. Selected by `rulebook/rules.md § P18` when the navigation model (`rulebook/rules.md § P22`) is `topbar` or `tabs` and there are no more than about six destinations.

## Regions
| region | role | default tier | holds |
|---|---|---|---|
| top-bar | navigation | — | brand · destinations · palette trigger · the one create action · account menu |
| destinations | navigation | — | the destination list, inline in the bar; a menu panel when narrow |
| page-header | chrome | — | title · badges · actions of the current screen; a breadcrumb only below an object |
| work-area | primary | 1 | the screen floorplan, full width, the page scrolls |
| peek | tertiary | 3 | a popover anchored to a row or chip, closed until asked |
| palette | chrome | — | the `⌘K` overlay: actions, destinations, objects (`rulebook/rules.md § P10`) |

Tier 3 surfaces in the peek, opened from a named control on a representation that works by keyboard and touch; never in the top bar or the page header (`rulebook/rules.md § P21`).

## Posture and density
Transient (`rulebook/rules.md § P19`): one view per screen, labelled buttons with full verbs, no tab or dialog nested in a dialog, Esc and Enter work, the last filter values are remembered. Density is comfortable (`rulebook/rules.md § P20`) — larger targets, more air — and a screen that is sovereign records it as an exception or uses `shell-sidebar`. There is no persistent status line.

Navigation model: realises `primary_surface: topbar` (destinations as links in the bar) and `primary_surface: tabs` (the same list as an underline tab strip in a second row under the brand row, for apps whose destinations do not fit one row). It never realises `sidebar`, `rail+drawer`, `bottom-tabs` or `none`.

Destination list: one list from `_concept/07_screens/shell.md`, rendered once in the `destinations` element — as links in the bar, as the tab strip, or as the menu panel when narrow — and in the palette's destination group. No surface keeps its own copy (`rulebook/rules.md § P22`). Settings is one entry, placed last or in the account menu (`rulebook/rules.md § P12`).

Palette and shortcuts: the search button in the top bar is the palette trigger; `⌘K` / `Ctrl-K` opens it from every screen. Shortcut hints come from the action registry (`rulebook/rules.md § P11`) and show in the palette and in tooltips; single-key shortcuts never fire while an input has focus or a dialog is open.

## Responsive
- **Wide, ≥ 960 px:** destinations inline in the bar; brand left, search, create and account right. The work area keeps the app's content width and centres beyond it.
- **Narrow, < 960 px (including 640 px):** the bar folds to brand · menu button · search icon · create. The menu button opens a panel under the bar holding the destination list; a destination closes it. The page header stacks, actions go into an overflow menu after the one primary, and the peek is a bottom sheet.
- **At 640 px and below:** the page header's badges move under the title and the work area loses its side padding.

## Interaction constraints
- The peek is read-only preview; editing happens in a dialog, a popover of two to three coupled fields or the object page (`rulebook/rules.md § P5`). A drawer hosts an edit form only when the app records that decision.
- A dialog that holds fields goes full-screen when narrow (`rulebook/rules.md § Heuristics`, H11).
- The bar holds destinations and the single create action: no per-feature entries, no second row of tools, no tabs that repeat the destinations (`rulebook/rules.md § P12`).
- A screen needing a persistent tree, panes or a status line is a sign the app wants `shell-sidebar` or `shell-dock`, not an extra region here.
- Forbidden: a second destination list, a sticky second bar of filters above the page header, a modal menu on wide.

## Sketch
```text
wide (>= 960 px)
+------------------------------------------------------------------+
| top-bar  [Brand] Overview Projects Tasks Clients ... Settings    |
|                                     [search ^K] [+ Create] (MK)  |
+------------------------------------------------------------------+
| page-header  Projects  (12 active)                  [Export]     |
+------------------------------------------------------------------+
| work-area                                          +-----------+ |
|   row  row  row  row  row  row                     | peek      | |
|   row  row                                         +-----------+ |
+------------------------------------------------------------------+

narrow (<= 640 px)
+--------------------------------+
| top-bar  [Brand] [Menu] (s) [+]|
+--------------------------------+
| destinations (menu panel)      |
|  Overview / Projects / Tasks   |
|  Clients / Invoices / Reports  |
|  Settings                      |
+--------------------------------+
| page-header  Projects  (...)   |
| work-area                      |
|   row / row / row              |
| peek = bottom sheet            |
+--------------------------------+
```

## When not to use
- More than about six destinations, groups, or sovereign daily work: `shell-sidebar`.
- A phone-first app with three to five destinations within thumb reach: `shell-mobile-tabs`.
- A desktop-native tool with resizable docked panes, toolbar and status bar: `shell-dock`.
