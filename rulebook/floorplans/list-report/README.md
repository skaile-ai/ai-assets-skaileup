---
id: list-report
kind: screen
summary: Find, compare and act on many objects of one primary type
posture: sovereign
density: default
---

# list-report — List report

The index of one `navigation: primary` object: an overview first, then the applied filters, then rows a person can decide on. Selected when the screen is the one list of an object type, `rulebook/rules.md § P8`, and its parts follow `rulebook/rules.md § P30`: overview, filter, detail on demand. A second list of the same object is a saved view of this screen, never another screen.

## Regions

| region | role | default tier | holds |
|---|---|---|---|
| `shell` | chrome | — | the shell frame's strip (a screen floorplan fills the frame's work area) |
| `page-header` | primary | 1 | object-type title, the one primary action (Create), at most one low-emphasis action |
| `saved-views` | navigation | — | named views of this index (all, mine, needs review) with counts; the current one is marked |
| `overview-strip` | secondary | 2 | counts or status roll-ups of the whole set; each tile is a filter shortcut |
| `filter-bar` | secondary | 2 | search, filter chips, sort, "n of N" and a one-click clear-all |
| `results` | primary | 1 | table (wide) or cards (narrow) of `row` representations: title first, the tier-1 attributes a decision needs |
| `bulk-bar` | secondary | 2 | actions on the selected set (at most H4 before overflow), selection count, clear selection |
| `peek` | tertiary | 3 | tier-3 attributes and the link to the canonical home |

Tier 3 never appears in a row: it surfaces in the `peek`, opened from a labelled control on each row (`rulebook/rules.md § P21`).

## Posture and density

Sovereign: people stay on an index. Keyboard row navigation and selection, restorable view state (filters, sort, selected view and page live in the URL, `rulebook/rules.md § P23`), a persistent "n of N" line. Density `default`; `compact` suits indexes read all day, and one tier holds throughout the table (`rulebook/rules.md § P20`, `rulebook/rules.md § Heuristics` H3).

## Responsive

- Wide ≥ 960 px: all regions stacked as listed; `results` is a table with sticky header.
- Narrow ≤ 640 px: the table becomes cards in the same row order, each card a `card` representation (title, status, two or three tier-1 facts); the `overview-strip` becomes a two-column grid; `saved-views` scrolls horizontally; `filter-bar` wraps with the search field first; the `bulk-bar` becomes a bottom bar; the `peek` becomes a bottom sheet.
- The `overview-strip` tiles follow the width of their container, not the viewport: one column, then two, then four (shadcn/ui dashboard-01 registry entry).

## Interaction constraints

- A row opens the object's canonical home (page), or a `peek` for a quick look; the peek and any side panel read and triage only, editing opens a dialog or the page (`rulebook/rules.md § P5`, `rulebook/defaults.md`).
- Inline edit is allowed for one scalar a person changes often (status, assignee) on a row; everything else goes through the object's editor in a dialog or its page (`rulebook/rules.md § P4`).
- Create opens the editor in create mode: a dialog for a simple object, a quick-create dialog then the object page for a complex one (`rulebook/rules.md § P6`).
- Bulk actions appear only while rows are selected, show the selection count and exit in one step (`rulebook/rules.md § P25`).
- Row-to-detail is never the only way to compare: tier-1 columns suffice to decide (`rulebook/rules.md § P30`).
- The overview shows before rows; an empty result says what belongs here and offers Create (`rulebook/rules.md § P15`).

## Sketch

```text
wide
+--------------------------------------------------------------+
| shell                                                        |
+--------------------------------------------------------------+
| page-header   Projects                        [Create project]|
| saved-views   All 10 | My projects 3 | Needs review 2        |
| overview-strip [Active 5] [In review 2] [Due 14d 3] [Hold 1] |
| filter-bar    (search) [Status x] [Owner] [Client]  7 of 10  |
| results   [ ] Project | Client | Status | Due | Owner | Tasks|
|           [x] Packaging series ... ... ... ................ i|
|           [ ] Brand refresh   ... ... ... ................ i |
| bulk-bar  2 selected  [Assign] [Change status] [Export]      |
+--------------------------------------------------------------+
                                           peek (on i, tier 3)

narrow
+------------------------+
| shell                  |
| page-header [Create]   |
| saved-views  (scroll)  |
| overview-strip  2 x 2  |
| filter-bar             |
| results                |
|  +------------------+  |
|  | Packaging series |  |
|  | client  status   |  |
|  +------------------+  |
| bulk-bar (bottom)      |
+------------------------+
```

## When not to use

- One object with sections and child collections: `object-page`.
- Browsing a list with the selected item's detail beside it, edit-next work: `master-detail`.
- The same items in columns or switchable views: `board`.
- A landing screen answering "what needs me now": `overview`.
