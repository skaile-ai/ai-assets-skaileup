---
id: overview
kind: screen
summary: "Landing screen: what needs me now, as the next actionable rows"
posture: sovereign
density: default
---

# overview — What needs me now

The landing screen of an app with work that arrives from several objects. It answers one question, "what needs me now", with blocks of at most four next-actionable rows each, ordered by what is due or waiting on the user, never with totals or charts of the whole. Each block ends in a link into the filtered list-report that holds the rest. Chosen per `rulebook/rules.md § P18` when the screen's task is to start the day rather than to manage one object type; it replaces no index (`rulebook/rules.md § P8`) and carries the overview-before-rows idea of `rulebook/rules.md § P30` as rows that can be decided on, not as counts.

## Regions

| region | role | default tier | holds |
|---|---|---|---|
| `shell` | chrome | — | the shell frame's top strip (title, search, user) |
| `header` | secondary | 2 | page title, the date, the app's one primary action |
| `attention` | primary | 1 | the blocks, one per kind of waiting work, each at most four rows |
| `recent` | secondary | 2 | changes since the last visit, at most four rows |
| `row-peek` | tertiary | 3 | popover on one row: detail the decision does not need |

A row carries the object's tier-1 attributes (title, the one fact that makes it due, its status) and one action; ids, codes and ownership history stay in the `row-peek`, opened from a named "Details" control on the row (`rulebook/rules.md § P21`, `rulebook/rules.md § P24`).

## Posture and density

Sovereign (`rulebook/rules.md § P19`): the screen is opened daily and read in a glance, so it is a quiet, fixed layout in which a block keeps its place from one visit to the next; a block with nothing waiting says so in one line and stays. Density `default` (`rulebook/rules.md § P20`): one row height in every block.

## Responsive

- **Wide (≥ 960 px):** blocks sit in two columns inside `attention`, `recent` in a column to the right or below; `header` is one line.
- **Narrow (≤ 640 px):** one column in the same order — `header`, `attention` blocks, `recent`; each row wraps to two lines (title, then fact and status) and its action becomes the row's tap target; `row-peek` becomes an inline expansion under its row.

## Interaction constraints

- **Read and triage only.** A row's action opens the object's page or its approved dialog (`rulebook/rules.md § P5`); no editor lives on the overview.
- A block shows at most four rows (`rulebook/rules.md § P30`); the rest is one link, "All <objects> due this week", opening the list-report with the filter applied.
- No totals, no counters, no charts: a number answers "how much", not "what next".
- A drawer is not used; a `row-peek` is a popover with a visible, keyboard-reachable entry point.
- Empty blocks state what belongs there (`rulebook/rules.md § P15`); one failing block shows its error and leaves its siblings (`rulebook/rules.md § P26`).

## Sketch

```text
WIDE
+-----------------------------------------------------------+
| shell                                                     |
+-----------------------------------------------------------+
| header          Today, 21 Oct                [ New project ]|
+-----------------------------------+-----------------------+
| attention                         | recent                |
|  Due this week                    |  Mara closed "Logo"   |
|   row  row  row  row   View all > |  Omar added a task    |
|  Waiting on my review             |  Lea sent INV-2041    |
|   row  row             View all > |                       |
|  Invoices to chase                |                       |
|   row  row  row        View all > | row-peek (popover)    |
+-----------------------------------+-----------------------+

NARROW
+---------------------------+
| shell                     |
| header                    |
| attention                 |
|  Due this week            |
|   row (2 lines)  x4       |
|   View all >              |
|  Waiting on my review ... |
| recent                    |
+---------------------------+
```

## When not to use

- The screen lists one object type with filters and sort: `list-report`.
- The screen is a set of tiles into areas or guided walks on a phone: `hub-areas`.
- The screen is for the daily work itself, in columns by status: `board`.
- The user wants figures over time (a report or analytics page): that is a list-report's overview strip or a separate report, not this floorplan.
