---
id: tabbed-tool
kind: screen
summary: "Single-column tool: tabs over one dataset, shared filters, overlay detail"
posture: sovereign
density: default
---

# tabbed-tool — Tabbed tool

Serves a small, single-purpose tool that people open to look something up: a few tabs over related views of one dataset (projects, tasks, invoices), one filter row shared by all tabs, and a read-only detail that opens over the list. Chosen when the tool has no object hierarchy to navigate and its views are siblings rather than a flow, per `rulebook/rules.md § P18`; each tab is a view of an object's one index and not a second list with its own columns (`rulebook/rules.md § P8`).

## Regions

| region | role | default tier | holds |
|---|---|---|---|
| `shell` | chrome | — | the thin frame strip of the app's shell frame |
| `header` | chrome | — | the tool's title and its settings control |
| `tablist` | navigation | — | the tabs, one per view; the selected tab marked, never more than five |
| `filter-row` | secondary | 2 | search, client, status chips and the "n of N" count, shared by every tab |
| `content` | primary | 1 | the list of the selected tab: rows with tier-1 attributes only; in the empty-state-first variant an empty state with one action |
| `detail-overlay` | secondary | 2 | the selected row's tier-1 and tier-2 facts over the list, with a close control |
| `detail-more` | tertiary | 3 | creation date, budget code, last editor, behind the named "More details" disclosure in the overlay |
| `filter-drawer` | secondary | 2 | the same filters as `filter-row`, opened by the "Filters" button |

Tier 3 surfaces only in `detail-more`, a named disclosure inside the overlay (`rulebook/rules.md § P21`, `rulebook/rules.md § P24`); never in a row.

## Posture and density

Sovereign for a tool that is opened daily and left open: the selected tab, filters and the open row survive reload and sharing (`rulebook/rules.md § P23`), keyboard moves between tabs and rows, and no wizard sits in front of the list (`rulebook/rules.md § P19`). Default density, one tier across all tabs (`rulebook/rules.md § P20`). A tool opened rarely to look one thing up declares the transient posture in its screen spec instead.

## Responsive

- **Wide (≥ 960 px):** one centred column. `filter-row` is visible under the `tablist`; `detail-overlay` is a panel from the right over a dimmed list.
- **641–959 px:** as wide, with tighter tab padding.
- **Narrow (≤ 640 px):** the column fills the width. `filter-row` keeps only the search field; client and status move into `filter-drawer`, a bottom sheet opened by "Filters · n" in the tab row, which also shows the count of applied filters. Secondary columns drop from the rows. `detail-overlay` becomes full-screen.
- **Empty-state-first variant (any width):** when the dataset is large or a query is costly, the tool opens without filters applied. `filter-row` is hidden, `content` shows an empty state that says what belongs there and offers "Open filters" (`rulebook/rules.md § P15`), and `filter-drawer` opens from the right on wide screens. Applying filters returns to the default variant with the list.

## Interaction constraints

- `detail-overlay` and `filter-drawer` read and triage: they show facts and set filters, and host no edit form. Editing a row opens a dialog or the object's own page (`rulebook/rules.md § P5`, `rulebook/defaults.md` § DF2).
- The overlay's open row is addressable as `?<noun>=<id>`, so reload and a shared link reopen it and an unknown id shows an info state (`rulebook/rules.md § P23`).
- Opening a row never leaves the list: Esc and the close control return to it with scroll and selection unchanged.
- A tab is a view of the same data, not a mode with its own editing behaviour; for modes use `mode-editor` (`rulebook/rules.md § P25`).
- Filters apply across all tabs; a filter that has no meaning on a tab is shown disabled with its reason, never silently dropped.

## Sketch

```text
wide (≥ 960)
+--------------------------------------------------+
| shell                                            |
+--------------------------------------------------+
| header  Studio overview                      [⚙] |
+--------------------------------------------------+
| tablist  [Projects] Tasks  Invoices              |
+--------------------------------------------------+
| filter-row  [Search] [Client v] (All)(Active) 8 of 8 |
+--------------------------------------------------+
| content                          | detail-overlay |
|  Website relaunch  Active 12 Dec |  Website relaunch  [x] |
|  Packaging refresh Active 30 Nov |  Client / Status / Due |
|  Menu redesign     On hold       |  [More details v]      |
+--------------------------------------------------+   (overlay appears on row click)

narrow (≤ 640)
+------------------------+   +------------------------+
| header          [⚙]    |   | filter-drawer     [x]  |
| tablist P | T | I      |   |  Client [v]            |
| [Search]   [Filters 1] |   |  Status (All)(Active)  |
| content                |   |  [Show results]        |
|  Website relaunch      |   | (bottom sheet)         |
|  Packaging refresh     |   +------------------------+
+------------------------+
```

## When not to use

- The tabs are modes of one artefact with an outline and a results panel: use `mode-editor`.
- The index is the main work surface with an overview strip, sort and bulk actions: use `list-report`.
- Items move through states in columns: use `board`.
- The user needs the detail beside the list to work through items: use `master-detail`.
