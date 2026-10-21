---
id: master-detail
kind: screen
summary: Browse a list and read or triage the selected item beside it
posture: sovereign
density: compact
---

# master-detail — Master and detail

A list or tree with the selected item's detail beside it, so a person works down the list without leaving it: triage, read, act on the next row. Selected when the task is browsing and acting on many items of one set and the detail serves reading and triage, not long editing, `rulebook/rules.md § P18`. The selected item is addressed in the URL, `?<noun>=<id>` (the explorer's `?node=` generalised to the noun, `rulebook/rules.md § P23`), so a link reproduces the view; the detail is the object's `peek` grown to a panel, the object's page stays its canonical home (`rulebook/rules.md § P1`).

## Regions

| region | role | default tier | holds |
|---|---|---|---|
| `shell` | chrome | — | the shell frame's strip (a screen floorplan fills the frame's work area) |
| `toolbar` | secondary | 2 | search, filters, the one primary action (Create), the count |
| `list` | primary | 1 | a treegrid or list of `row` representations: sticky header, groups that expand and collapse, the selected row marked |
| `activity-strip` | secondary | 2 | a slim status line under the list: the selected `?<noun>=<id>`, filter state, sync or log lines |
| `detail` | secondary | 2 | the selected item: title and status, 3 key facts, the next actions to triage, links to the canonical home; tier 3 behind a named "More details" disclosure |

Tier 3 in this floorplan surfaces only inside `detail`'s named disclosure (`rulebook/rules.md § P21`); a row never carries it.

## Posture and density

Sovereign, as `list-report`: keyboard navigation up and down the list, Enter selects, the selected id and the expanded groups live in the URL or persist per user (`rulebook/rules.md § P23`). Density `compact` by default for a long list scanned all day; one tier holds across the grid (`rulebook/rules.md § P20`). The detail panel itself is auxiliary: it reads and triages and yields space to the list (`rulebook/rules.md § P19`).

## Responsive

- Wide ≥ 960 px: `list` and `detail` side by side, the detail a fixed-width panel (about 360 px) on the right; the `activity-strip` sits under the list.
- Narrow ≤ 640 px: list, then detail as its own full view. Selecting a row opens the detail with a "Back to list" control; Back restores the list with its scroll position and selection; the `activity-strip` is dropped, its state lives in the URL. Rows become two-line cards (name and status, then date and owner).

## Interaction constraints

- The `detail` reads and triages: assign, change status, act on the next row. Editing opens a dialog or the object's page, never an edit form in the panel, unless the app records that decision (`rulebook/rules.md § P5`, `rulebook/defaults.md`).
- The detail never replaces the page: any object with sections or child collections links to its `object-page` from the panel.
- A second list of the same objects stays a filter or saved view of this one (`rulebook/rules.md § P8`).
- Selection survives reload; an unknown or vanished id opens the panel's info state, never another item (`rulebook/rules.md § P23`).
- Closing or changing the selection never loses unsaved work in a hosted dialog (`rulebook/rules.md § P14`).

## Sketch

```text
wide
+--------------------------------------------------------------+
| shell                                                        |
+--------------------------------------------------------------+
| toolbar  (search) [Status] [Owner] [Create project]  6 items |
+------------------------------------------+-------------------+
| list   Name        | Status | Due | Owner| detail            |
|  v Alder & Finch 2                       | Website relaunch  |
|    > Website relaunch  Active Nov 28 Jon.| Active · Alder... |
|      Journal launch    Draft  Jan 16 Mara| Owner|Due|Tasks   |
|  v Northwind Coffee 2                    | Next tasks        |
|      Brand refresh     Active Nov 12 ... |  ... [Assign]     |
+------------------------------------------+ [Open] [Edit]     |
| activity-strip  ?project=af-0395 · synced| > More details    |
+------------------------------------------+-------------------+

narrow
+------------------------+   +------------------------+
| shell                  |   | shell                  |
| toolbar                |   | < Back to projects     |
| list                   |   | detail                 |
|  Website relaunch      |   |  title        [Active] |
|  Nov 28 · Jonas        |   |  facts                 |
|  Journal launch   ...  | > |  Next tasks            |
|  ...                   |   |  [Open] [Edit]         |
+------------------------+   +------------------------+
```

## When not to use

- Only the index, with filters and bulk actions and no selected item beside it: `list-report`.
- The task is long editing of the selected item: `object-page`, reached from the list.
- A source rail plus an editor plus a management drawer: `three-pane`.
- Reading content with a reading pane and filters: `reader`.
