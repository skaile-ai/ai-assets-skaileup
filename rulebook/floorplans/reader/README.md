---
id: reader
kind: screen
summary: "Read documents: filter, pick from a tree or list, read in a pane"
posture: sovereign
density: default
---

# reader — Reader

Serves people who consume content rather than edit it: they narrow a set of documents with filters, pick one from a tree or list, and read it beside the list. Chosen when the screen's task is reading and comparing items one after the other and the item is long-form, per `rulebook/rules.md § P18`; the list is one index of the object (`rulebook/rules.md § P8`) and the open document is its canonical home shown in a pane (`rulebook/rules.md § P1`).

## Regions

| region | role | default tier | holds |
|---|---|---|---|
| `shell` | chrome | — | the thin frame strip of the app's shell frame |
| `filters` | secondary | 2 | filter groups (select, checkboxes, range) and the "n of N" count with clear-all |
| `tree` | navigation | — | the hierarchy the documents live in (client → project) with counts; selecting a node scopes the list |
| `list` | primary | 1 | one row per document: title first, type and date; tier-1 attributes only |
| `reader` | primary | 1 | the open document: title, context line, body |
| `doc-info` | tertiary | 3 | revision, word count, last editor, created date |

Tier 3 surfaces only in `doc-info`, a popover opened by the named "Document info" control in the reader header (`rulebook/rules.md § P21`, `rulebook/rules.md § P24`); never in a list row.

## Posture and density

Sovereign: people stay in the screen and move document to document, so the selected document, filters and tree scope survive navigation and reload (`rulebook/rules.md § P23`), and arrow keys move the selection (`rulebook/rules.md § P19`). Default density; the reader body keeps a comfortable line length (about 64 characters) rather than the list's density (`rulebook/rules.md § P20`).

## Responsive

The archetype's own thresholds are 1100 px and 760 px. They map onto the catalogue's two: wide is ≥ 960 px, narrow is ≤ 640 px, and the 641–959 px band behaves like the archetype's middle step.

- **Wide (≥ 960 px):** three columns — `filters`, then `tree` over `list`, then `reader`; the reader is persistent.
- **641–959 px:** `reader` leaves the grid and becomes an overlay panel from the right with a close control; `filters` and `tree`/`list` stay as two columns. Selecting a row opens the overlay, close returns to the list with the row still selected.
- **Narrow (≤ 640 px):** one column. `filters` collapse into a single "Filters · n applied" disclosure above the list; the reader is a full-width overlay.

## Interaction constraints

- The reader pane and its overlay form are read-only: they show the document and never host an edit form. Editing opens the document's own page or dialog (`rulebook/rules.md § P5`, `rulebook/defaults.md`).
- The overlay is a drawer in the sense of `rulebook/defaults.md` § DF2: it reads, it does not edit; a document linkable by `?document=<id>` survives reload (`rulebook/rules.md § P23`).
- Selecting a tree node or a filter changes the list only, never the open document, unless that document leaves the set, in which case the reader shows an empty state, not another document.
- Row actions are few (open, copy link); bulk selection is not part of this floorplan.

## Sketch

```text
wide (≥ 960)
+----------------------------------------------------------------+
| shell                                                          |
+----------+-----------------+-----------------------------------+
| filters  | tree            | reader                            |
|  client  |  Brightway  2   |  Website relaunch — brief         |
|  type    |   > Website     |  Brightway Dental · Brief · 14 Oct|
|  updated |  Moss & Co. 2   |  [Document info]  <- doc-info     |
|  8 of 8  +-----------------+  Goal ...                         |
|          | list            |  Scope ...                        |
|          |  > Brief 14 Oct |  Deliverables ...                 |
|          |    Note  12 Oct |  Timeline ...                     |
+----------+-----------------+-----------------------------------+

narrow (≤ 640)
+------------------------+      +------------------------+
| shell                  |      | reader            [x]  |
+------------------------+      |  Website relaunch      |
| filters · 2 applied v  |      |  Brightway · Brief     |
+------------------------+      |  Goal ...              |
| tree                   |      |  Scope ...             |
|  Brightway 2           |      |  (overlay over list)   |
+------------------------+      +------------------------+
| list                   |
|  > Website — brief     |
|    Kickoff notes       |
+------------------------+
```

## When not to use

- The user edits the item as the main task: use `master-detail` (edit-next) or `object-page`.
- The items are short records scanned by many columns: use `list-report`.
- There is no list or hierarchy to choose from, one long document only: use `object-page`.
- The items move through states in columns: use `board`.
