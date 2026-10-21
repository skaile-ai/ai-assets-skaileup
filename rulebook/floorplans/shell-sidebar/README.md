---
id: shell-sidebar
kind: shell
summary: Grouped destinations in a sidebar, page header and work area for daily work
posture: sovereign
density: default
---

# shell-sidebar — Sidebar shell

The frame for a desktop-first app with more than about five destinations or grouped ones, used all day: a collapsible sidebar holds the one destination list, a page header carries the screen's title and actions, the work area holds the screen floorplan and an optional right slideover holds read-and-triage detail. Selected by `rulebook/rules.md § P18` when the navigation model (`rulebook/rules.md § P22`) is `sidebar` or `rail+drawer`.

## Regions
| region | role | default tier | holds |
|---|---|---|---|
| sidebar | navigation | — | brand, palette trigger, the destination list in named groups, account, collapse control |
| page-header | chrome | — | sidebar toggle · title · badges · actions · toolbar · search · bell · the one create action |
| work-area | primary | 1 | the screen floorplan; scrolls on its own, the frame never scrolls |
| slideover | tertiary | 3 | a peek or triage panel for the selected row, closed until asked |
| bottom-pill | navigation | — | narrow only: the pinned destinations of the same list, optional |
| palette | chrome | — | the `⌘K` overlay: actions, destinations, objects (`rulebook/rules.md § P10`) |

Tier 3 surfaces in the slideover, opened by a named "Quick view" control on a row that works by keyboard and touch, and in popovers anchored to a representation; never in the sidebar or the page header (`rulebook/rules.md § P21`).

## Posture and density
Sovereign (`rulebook/rules.md § P19`): the sidebar, header and a persistent context line stay put, keyboard accelerators are shown beside their destinations and no wizard serves routine work. Density is the app's default (`rulebook/rules.md § P20`); sidebar rows, header controls and the work area's rows use one size token. Sidebar width and the collapsed state persist per user.

Navigation model: realises `primary_surface: sidebar` (expanded) and `primary_surface: rail+drawer` (rail, then drawer). The bottom-pill does not change `primary_surface`; an app whose primary narrow surface is a tab bar uses `shell-mobile-tabs`.

Destination list: one list from `_concept/07_screens/shell.md`, rendered in the sidebar, in the rail, in the drawer (the sidebar element off-canvas), in the bottom-pill (the destinations flagged pinned, at most four plus Menu) and in the palette's destination group. No surface keeps its own copy (`rulebook/rules.md § P22`). Groups are named, one level deep; Settings is one entry (`rulebook/rules.md § P12`).

Palette and shortcuts: the trigger is the search field at the top of the sidebar (a search icon in the page header when the sidebar is not visible); `⌘K` / `Ctrl-K` opens it from every screen. Destination shortcuts are hints beside the entries and come from the action registry (`rulebook/rules.md § P11`); single-key shortcuts never fire while an input has focus or a dialog is open.

## Responsive
- **Wide, ≥ 992 px:** sidebar expanded (labels, groups, shortcut hints), slideover docked at the right and pushing the work area.
- **992 px down to 768 px:** sidebar collapses to an icon rail with tooltips (`rulebook/rules.md § P16`); the slideover becomes an overlay above the work area.
- **Narrow, ≤ 767 px (and at 640 px):** the rail is gone; the sidebar becomes a drawer opened by the page header's toggle, with a scrim. Page header folds to toggle · title · search · create; badges and toolbar move below the title or into an overflow menu. The bottom-pill shows the pinned destinations plus a Menu entry that opens the drawer. The slideover is a full-width bottom sheet.

## Interaction constraints
- The slideover is read and triage only: preview, assign, act on the next row; the object page behind "Open" is where editing happens. A drawer hosts an edit form only when the app records that decision (`rulebook/rules.md § P5`).
- An object with sections or child collections stays a page, never a slideover.
- The sidebar holds destinations only: no actions, no per-feature entries, no entry per settings page (`rulebook/rules.md § P12`).
- The palette is an overlay for finding and doing; it hosts no form and never replaces a visible control (`rulebook/rules.md § P10`).
- One primary button in the page header; the create action there uses the verb set of `rulebook/rules.md § P11`.
- Forbidden: a second destination list (header tabs repeating the sidebar), a stacked dialog over the drawer, a frame-level scrollbar.

## Sketch
```text
wide (>= 992 px)
+-------------+----------------------------------------+-------------+
| sidebar     | page-header  [=] Projects  (12)  /  (!) [+ Create]     |
| [search ^K] +----------------------------------------+ slideover   |
|  Overview   | work-area                              | Quick view  |
|  Projects * |  row  row  row  row  row  row          |  facts      |
|  Tasks      |                                        |  [Open]     |
|  Clients    |                                        |             |
|  ...        |                                        |             |
|  Settings   |                                        |             |
+-------------+----------------------------------------+-------------+
| palette: overlay, centred, over everything                         |

narrow (<= 640 px)
+--------------------------------+
| page-header  [=] Projects [+]  |
+--------------------------------+
| work-area                      |
|  row                           |
|  row                           |
|  ...                           |
|     bottom-pill: ( O P T I M ) |
+--------------------------------+
sidebar = drawer from the left, slideover = bottom sheet
```

## When not to use
- A few flat destinations and light tools, content first: `shell-topbar`.
- A phone-first app with three to five destinations within thumb reach: `shell-mobile-tabs`.
- A desktop-native tool with resizable docked panes, toolbar and status bar: `shell-dock`.
