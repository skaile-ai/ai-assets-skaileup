---
id: three-pane
kind: screen
summary: Work in an editor across several sources, with a management drawer
posture: sovereign
density: default
---

# three-pane — Source rail, work area, management drawer

A workspace for working across several sources: a collapsible rail picks the source, the work area edits it, and a drawer on the right manages what surrounds it (client, invoices, capabilities). Selected when one editing surface serves many sources the person switches between all day, `rulebook/rules.md § P18`, and the surroundings of the source are read and triaged beside the work rather than navigated to, `rulebook/rules.md § P29`. The selected source lives in the URL, `?<noun>=<id>` (`rulebook/rules.md § P23`).

## Regions

| region | role | default tier | holds |
|---|---|---|---|
| `shell` | chrome | — | the shell frame's strip (a screen floorplan fills the frame's work area) |
| `source-rail` | navigation | — | the sources, grouped, current one marked; collapsible to an initials strip; rendered from the app's one destination list or object index (`rulebook/rules.md § P22`) |
| `editor-toolbar` | secondary | 2 | source title, the one primary action (Create), toggles for the rail and the drawer |
| `work-area` | primary | 1 | the editor for the selected source; cells may edit inline through the type's one editor (`rulebook/rules.md § P4`) |
| `management-drawer` | secondary | 2 | the source's context: its owner object's key facts and its child list, with triage actions; tier 3 behind a named disclosure |
| `status-line` | chrome | — | persistent counts and the save state of the work area |

Tier 3 surfaces in `management-drawer`'s named disclosure or a popover on a row there; the rail and the work area never carry it (`rulebook/rules.md § P21`). Capability flags per source switch regions on or off: a source without a management part hides the drawer rather than showing it empty.

## Posture and density

Sovereign: long daily work. The status line is persistent, keyboard accelerators switch sources and move between panes, the rail and drawer states (collapsed, open) persist per user (`rulebook/rules.md § P19`, `rulebook/rules.md § P23`). Density `default`; the work area sets the tier, the rail and the drawer follow it (`rulebook/rules.md § P20`). The drawer is auxiliary: it yields space to the work area and reads and triages only.

## Responsive

- Wide ≥ 960 px: rail (about 230 px), work area and drawer (about 300 px) side by side; the rail collapses to a 52 px strip of initials, the drawer closes to give the work area the width.
- Narrow ≤ 640 px: the work area alone, full width. The rail becomes an overlay panel from the left, opened from the toolbar; the drawer becomes a bottom sheet over the work area, opened from the toolbar; both close on selection or an explicit Close. The status line sticks to the bottom edge. Neither overlay holds an edit form (`rulebook/rules.md § P5`).

## Interaction constraints

- The `management-drawer` reads and triages: look up, assign, act on the next row. Any editing of its objects opens a dialog or their own page; the drawer hosts no edit form unless the app records that decision (`rulebook/rules.md § P5`, `rulebook/defaults.md`).
- Switching the source with unsaved changes in the work area asks first, only when something would be lost (`rulebook/rules.md § P14`).
- The work area is the one editing surface; the same type is not also edited in the drawer (`rulebook/rules.md § P3`, `rulebook/rules.md § P4`).
- A drawer or rail that is collapsed shows its state at the place of action, so a hidden region is never mistaken for a missing one (`rulebook/rules.md § P25`).
- The source list is the index of that object: no second list elsewhere (`rulebook/rules.md § P8`).

## Sketch

```text
wide
+--------------------------------------------------------------+
| shell                                                        |
+-----------------+----------------------------+---------------+
| source-rail     | editor-toolbar  title [Create task] [Drawer]|
|  Projects       +----------------------------+ management-   |
|  > Website...   | work-area                  | drawer        |
|    Brand...     |  Task | Assignee | Status | | Alder & Finch |
|    Packaging... |  ...                      | | Contact, City |
|    Annual...    |  ...                      | | Invoices      |
|                 +----------------------------+ [Create inv.] |
|                 | status-line  8 tasks · saved|               |
+-----------------+----------------------------+---------------+

narrow
+------------------------+
| shell                  |
| editor-toolbar [=] [i] |
| work-area              |
|  task        estimate  |
|  assignee      status  |
| status-line (sticky)   |
+------------------------+
  [=] source-rail   : overlay from the left
  [i] management-drawer : bottom sheet
```

## When not to use

- One list of one object with filters and bulk actions: `list-report`.
- A list with the selected item's detail beside it, no editor: `master-detail`.
- One object with sections and child collections on one page: `object-page`.
- One artefact edited in several modes: `mode-editor`.
- Content to read, not to edit: `reader`.
