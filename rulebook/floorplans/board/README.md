---
id: board
kind: screen
summary: "One item set as status columns, list or calendar, with a card drawer"
posture: sovereign
density: default
---

# board — The same items in columns, a list or a calendar

The working view of one object type whose members move through states: projects by status, tasks by stage, applications by phase. The items are the same in every view; a visible view switch changes only how they are laid out, as columns by status (kanban), as a list, or on a calendar by date. A card opens a drawer on the right for reading and triage while the board stays visible behind it. Chosen per `rulebook/rules.md § P18` when the person works the flow of items rather than looking one up; it is a view of the object's index and not a second list of it (`rulebook/rules.md § P8`), so it is reachable as a saved view or a view switch of that index.

## Regions

| region | role | default tier | holds |
|---|---|---|---|
| `shell` | chrome | — | the shell frame's top strip |
| `view-switch` | navigation | — | List · Board · Calendar as a segmented control, the current view marked |
| `filter-bar` | secondary | 2 | search, filter chips, sort or group-by, "n of N" and clear-all |
| `items` | primary | 1 | the items in the current view: columns by status, rows, or days |
| `card-drawer` | secondary | 2 | the selected item's tier-2 facts and its triage actions |

A card, row or calendar chip carries tier 1 only: the name, the one fact the flow turns on (due date), the owner, the status by its column. Tier 3 surfaces in the drawer under a named "More details" disclosure, or in a `peek` popover from the card's info control (`rulebook/rules.md § P21`, `rulebook/rules.md § P2`).

## Posture and density

Sovereign (`rulebook/rules.md § P19`): a long daily surface, so keyboard movement between cards and columns, a persistent "n of N" line and a view that survives reload (`rulebook/rules.md § P23`). Density `default` (`rulebook/rules.md § P20`): one card height per column set, the list view at the same row height as the board's header and toolbar.

## Responsive

- **Wide (≥ 960 px):** `items` fills the width; `card-drawer` is a column of about 320 px at the right that pushes `items` narrower; columns share the rest and the board scrolls horizontally once they no longer fit.
- **Narrow (≤ 640 px):** columns become one column at a time, swiped or chosen from a status tab strip, each card full width; `filter-bar` collapses to a search field and one "Filters" button with the applied count; the list view shows two-line rows; the calendar becomes an agenda of the days that hold items; `card-drawer` becomes a bottom sheet over `items` that closes by swipe, Esc or its close button.
- On wide, a column is 12–25 rem: columns that share the width stop growing at 25 rem and the area right of the last one stays empty; columns that no longer fit keep 12 rem and the board scrolls sideways (Salesforce Lightning Design System 2 — Layout).

## Interaction constraints

- **The drawer reads and triages** (`rulebook/rules.md § P5`, `rulebook/defaults.md § DF2`): preview, move to another status, assign, open. Editing the item opens a dialog or the object's page, unless the app records that its drawer hosts the edit form.
- The open card is in the URL, `?<noun>=<id>`, so a link reproduces the board with the drawer open; a vanished id shows the board's info state, never another item (`rulebook/rules.md § P23`). The current view is in the URL as well.
- Moving a card between columns changes its status through the one editor's status control (`rulebook/rules.md § P4`); drag is never the only way: the drawer and the card menu offer "Move to" for keyboard and touch.
- Columns come from the status values, in the flow order, each with its count and an empty state that says what belongs there (`rulebook/rules.md § P15`); a column is not an object and has no editor.
- The filter bar shows applied filters, "n of N" and one-click clear-all (`rulebook/rules.md § P30`); filters apply to every view.
- Bulk selection is a visible mode with its own bar (`rulebook/rules.md § P25`); creating an item opens the object's create flow (`rulebook/rules.md § P6`), with the new item selected afterwards.

## Sketch

```text
WIDE
+-----------------------------------------------------------+
| shell                                                     |
+-----------------------------------------------------------+
| view-switch [List|Board|Calendar]                         |
| filter-bar  [search] [Owner v] [Due v]  7 of 8  Clear all |
+-------------------------------------------+---------------+
| items                                     | card-drawer   |
|  Planned  In progress  Review   Blocked   |  Title      x |
|  +-----+  +-----+       +-----+  +-----+  |  facts        |
|  |card |  |card |       |card |  |card |<-|  Move to v    |
|  +-----+  +-----+       +-----+  +-----+  |  > More       |
+-------------------------------------------+---------------+

NARROW
+---------------------------+
| shell                     |
| view-switch               |
| filter-bar [search][Filters 2] |
| items  (one status column)|
|  card                     |
|  card                     |
| card-drawer (bottom sheet)|
+---------------------------+
```

## When not to use

- The items are browsed in one table with many sortable columns and no flow: `list-report`.
- One item is the focus and has sections and child collections: `object-page`.
- The user reads a list and edits the selected row beside it: `master-detail`.
- The items have no status or date to arrange them by: `list-report`.
