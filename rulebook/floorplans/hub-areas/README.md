---
id: hub-areas
kind: screen
summary: Phone hub of task tiles leading to areas and short guided walks
posture: transient
density: comfortable
---

# hub-areas — Hub, areas and guided walks

Serves a phone-sized, task-led app with a handful of jobs: the user lands on a hub of tiles named for what they want to do, enters an area that lists what that job concerns, and starts a short guided walk when the job has steps. Chosen when the app's navigation model is `task-led` with few areas and the posture is transient (`rulebook/rules.md § P22`, `rulebook/rules.md § P19`), per `rulebook/rules.md § P18`. It is three frames of one flow — hub, area, walk — not three separate floorplans.

## Regions

| region | role | default tier | holds |
|---|---|---|---|
| `shell` | chrome | — | the thin frame strip of the app's shell frame |
| `hub-tiles` | primary | 1 | one tile per task: label first, one line of status or count; four to six tiles |
| `area-head` | navigation | — | back to the hub and the area's title |
| `area-body` | primary | 1 | the scrolling column of the area: rows or cards with tier-1 attributes |
| `peek` | tertiary | 3 | detail on one row — due date, contact, city — opened by that row's info control |
| `area-foot` | secondary | 2 | the one primary action of the area, which starts the walk |
| `walk-head` | navigation | — | close and the position "step n of m" with a progress bar |
| `walk-step` | primary | 1 | one step: the value to enter or check, with the source it depends on shown beside it |
| `walk-foot` | secondary | 2 | Back and the one primary action, Next or the final verb |

Tier 3 surfaces only in `peek`, reached through an info control on a row that carries an accessible name (`rulebook/rules.md § P21`, `rulebook/rules.md § P24`).

## Posture and density

Transient: the user comes, does one job and leaves, so every frame is one view with labelled buttons that carry the full verb, no nested dialog or tabs, Esc and Back work, and the last values are remembered (`rulebook/rules.md § P19`). Comfortable density: touch targets of at least 44 px and rows of two lines (`rulebook/rules.md § P20`). View state is not restored across visits; the app starts at the hub (`rulebook/rules.md § P23`).

## Responsive

The frames are phone-sized by design; the floorplan transforms by how many it shows at once.

- **Wide (≥ 960 px):** the hub, an area and a walk sit side by side as phone frames of about 340 px, which is how a review or a tablet-in-landscape shows the whole flow. In use, one frame fills the viewport at a time.
- **641–959 px:** the frames wrap, two per row.
- **Narrow (≤ 640 px):** one frame fills the width and the viewport. Moving down the flow replaces the frame; Back returns to the previous one. `area-foot` and `walk-foot` stay pinned to the bottom edge within reach of the thumb.

## Interaction constraints

- A walk follows `rulebook/rules.md § P31`: it shows "step n of m", moves back without losing data, and ends on a completion state that names what was created and offers the next task.
- A walk is for steps that are mostly independent; steps that need each other sit on one screen (`rulebook/rules.md § P24`).
- Each walk step shows the source its value depends on on the same screen rather than asking the user to remember it (`rulebook/rules.md § P29`).
- No frame is a drawer. `peek` reads only; editing happens in the walk or on the object's own page (`rulebook/defaults.md` § DF2).
- The hub holds tasks, not file-system entries: a tile per feature or settings page is a finding (`rulebook/rules.md § P12`).

## Sketch

```text
wide (≥ 960): three phone frames, left to right
+-------------------------------------------------------------------------+
| shell                                                                   |
+-------------------------------------------------------------------------+
| hub-tiles          | area-head  < Send invoice | walk-head x  Step 2 of 3 |
|  [Log time ]       | area-body                 | walk-step                |
|  [Check    ]       |  INV-1042  €6,400 Overdue |  Check the amount        |
|  [Send inv.]       |  INV-1047  €2,150 Draft   |  Client  Moss & Co.      |
|  [Add client]      |  (peek on i)              |  Amount  [ €2,150.00 ]   |
|                    | area-foot [Start: send]   | walk-foot [Back][Next]   |
+--------------------+---------------------------+--------------------------+

narrow (≤ 640): one frame at a time
+------------------------+   +------------------------+
| shell                  |   | walk-head x Step 2 / 3 |
+------------------------+   | walk-step              |
| hub-tiles              |   |  Check the amount      |
|  [Log time][Check ]    |   |  source + field        |
|  [Send   ][Add    ]    |   | walk-foot [Back][Next] |
+------------------------+   +------------------------+
```

## When not to use

- The app has many destinations or sovereign, long sessions: use `shell-sidebar` or `shell-topbar` with `list-report` and `object-page`.
- The task is one guided flow with no hub or areas: use `wizard`.
- The app is phone-first but object-led with three to five destinations: use `shell-mobile-tabs`.
- The screen shows a collection with filter and sort: use `list-report`.
