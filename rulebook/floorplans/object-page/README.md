---
id: object-page
kind: screen
summary: "Work on one object: key facts, sections, child collections, history"
posture: sovereign
density: default
---

# object-page — Object page

The canonical home of one complex object: its sections, child collections and history on one page. Selected for a `navigation: primary` object whose home is a page, `rulebook/rules.md § P1`, with sections or child rows that rule out a dialog, `rulebook/rules.md § P5` and `rulebook/rules.md § P6`. Page order is fixed: header, key facts, sections and child collections, history. The page shows each attribute in full once; its tiers follow `rulebook/rules.md § P21`.

## Regions

| region | role | default tier | holds |
|---|---|---|---|
| `shell` | chrome | — | the shell frame's strip (a screen floorplan fills the frame's work area) |
| `header` | primary | 1 | breadcrumb, object title, status, the one primary action (Edit), overflow for the rest |
| `facts` | secondary | 2 | 3–5 key facts (H12 in `rulebook/rules.md § Heuristics`), value above label; aggregates of children (count, sum) link to them |
| `section-nav` | navigation | — | anchors to the sections below, sticky; the current section is marked |
| `sections` | secondary | 2 | descriptive sections of the object's own attributes, each with its own Edit |
| `child-collections` | secondary | 2 | one section per child collection (tasks, invoices): `row` representations, a Create action each |
| `history` | tertiary | 3 | audit trail and revisions, collapsed behind a named disclosure with its count |

Tier 3 surfaces only in `history`'s named disclosure or in a `peek` on a child row; the header never repeats an attribute the facts show (`rulebook/rules.md § P3`).

## Posture and density

Sovereign: long daily work on one object. Sections edit in place through the object's one editor (`rulebook/rules.md § P4`), the page keeps a dirty guard (`rulebook/rules.md § P14`), and the selected section and scroll position survive reload (`rulebook/rules.md § P23`). Density `default`; child collections use one row tier (`rulebook/rules.md § P20`).

## Responsive

- Wide ≥ 960 px: header and facts in one band (four facts in a row), `sections` side by side, collections full width, `section-nav` sticky under the facts.
- Narrow ≤ 640 px: the header stacks, the primary action takes the full width; facts become a two-column grid; `sections` stack; child rows become two-line items (title and status, then assignee and amount); `section-nav` scrolls horizontally.

## Interaction constraints

- The page, not a drawer, hosts everything with sections, child collections or drafts; a drawer or peek here only reads and triages (`rulebook/rules.md § P5`, `rulebook/defaults.md`).
- Edit hosts, each through the one editor: inline for one scalar (status), the section's Edit for a slice of the editor, the header Edit for the whole object (`rulebook/rules.md § P4`).
- A child row opens its own editor in a dialog or its own page, according to its complexity; Create on a collection uses the dialog of the child type (`rulebook/rules.md § P6`).
- Delete confirms with the child counts the object owns (`rulebook/rules.md § P7`).
- Key facts stay at three to five (H12); more is a section.
- A vanished id shows the page's info state, never another object (`rulebook/rules.md § P23`).

## Sketch

```text
wide
+--------------------------------------------------------------+
| shell                                                        |
+--------------------------------------------------------------+
| header   Projects / Website relaunch                          |
|          Website relaunch  [Active]       [Edit project] [...]|
| facts    Client | Owner | Due date | Estimate                |
| section-nav  Brief | Tasks 8 | Invoices 3 | History          |
| sections    Brief            |  Scope                        |
| child-collections                                            |
|   Tasks     title | assignee | status | estimate  [Create]    |
|   Invoices  number | status | amount              [Create]   |
| history   > History (14 events)                              |
+--------------------------------------------------------------+

narrow
+------------------------+
| shell                  |
| header  title [Active] |
|         [Edit project] |
| facts   2 x 2          |
| section-nav  (scroll)  |
| sections  (stacked)    |
| child-collections      |
|   title          status|
|   assignee     estimate|
| history  > History     |
+------------------------+
```

## When not to use

- The index of the objects, not one: `list-report`.
- A simple object with a flat form inside the dialog limit: a dialog from the list, no page (`rulebook/rules.md § P6`).
- Reading and triaging one item beside its list: `master-detail`.
- A guided, linear task: `wizard`.
