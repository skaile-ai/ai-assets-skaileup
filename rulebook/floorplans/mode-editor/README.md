---
id: mode-editor
kind: screen
summary: Edit one artefact in several modes chosen from a visible mode menu
posture: sovereign
density: compact
---

# mode-editor — Mode editor

Serves a long work session on one artefact that is edited in more than one way — here a project plan edited as plan, tasks or billing — with an outline to navigate it and a results panel that answers "is it still right". Chosen when one object is worked in distinct modes that share one outline and one results panel, per `rulebook/rules.md § P18`; the modes are a visible menu in the header, never a hidden gesture (`rulebook/rules.md § P25`).

## Regions

| region | role | default tier | holds |
|---|---|---|---|
| `shell` | chrome | — | the thin frame strip of the app's shell frame |
| `header` | chrome | — | outline toggle, the artefact title as h1, the mode menu, help, settings, account |
| `mode-menu` | navigation | — | the modes of this artefact as a visible control; the active one marked |
| `tree` | navigation | — | the artefact's outline (phases, tasks); selecting a node scopes the content |
| `content` | primary | 1 | the editor of the selected node in the active mode, under a scope line naming mode and node |
| `results` | secondary | 2 | derived output of the current state: totals, checks, warnings; read-only |
| `studio-drawer` | tertiary | 3 | auxiliary views opened on request — activity, comments — with its own view switch |

Tier 3 surfaces only in `studio-drawer`, opened by the named "Studio" control in the content's scope line (`rulebook/rules.md § P21`, `rulebook/rules.md § P24`).

## Posture and density

Sovereign: a daily work surface with keyboard accelerators, a persistent scope line and no wizard for routine work (`rulebook/rules.md § P19`). Compact density, one tier throughout the tables in `content` (`rulebook/rules.md § P20`). The active mode, selected node and drawer view live in the URL (`?mode=`, `?node=`) so a reload or a shared link reproduces the view and the mode never survives navigation silently (`rulebook/rules.md § P23`, `rulebook/rules.md § P25`).

## Responsive

- **Wide (≥ 960 px):** `tree`, `content` and `results` side by side under the `header`; `studio-drawer` is an overlay from the right.
- **641–959 px:** `tree` leaves the grid and becomes an overlay from the left, opened by the outline toggle in the header; `results` stacks under `content`.
- **Narrow (≤ 640 px):** as 641–959 px, and the `mode-menu` moves to its own full-width row of the header, every mode still visible; `studio-drawer` becomes a bottom sheet over the content.

## Interaction constraints

- Modes are visible: the `mode-menu` always shows the active mode, and `content` repeats it in its scope line with the node being edited; leaving a mode is choosing another one, one step (`rulebook/rules.md § P25`).
- `content` is the only editing region. `results` and `studio-drawer` read and triage; an edit started from either opens a dialog or switches the mode, never an inline form in the drawer (`rulebook/defaults.md` § DF2, `rulebook/rules.md § P5`).
- The mode menu lists a handful of modes; an overflow named "More" holds none of them (`rulebook/rules.md § P24`).
- The editor in each mode is the object's one editor or a slice of it (`rulebook/rules.md § P4`); switching mode keeps unsaved changes or asks first (`rulebook/rules.md § P14`).
- Help, settings and account live in the `header`; they are not repeated in the shell strip.

## Sketch

```text
wide (≥ 960)
+--------------------------------------------------------------------+
| shell                                                              |
+--------------------------------------------------------------------+
| header  [≡] Website relaunch — plan   [Plan|Tasks|Billing]  [?][⚙][AR] |
+-------------+--------------------------------+---------------------+
| tree        | content                        | results             |
|  1 Discovery|  Mode Plan · editing 2 Design  |  118 h of 140 h     |
|  2 Design   |                      Studio ▸  |  - no assignee      |
|    Wireframe|  Phase name  [ Design      ]   |  - overdue          |
|    Route A  |  Owner       [ Ana Reyes   ]   |                     |
|  3 Build    |  Due date    [ 28 Oct      ]   |                     |
+-------------+--------------------------------+---------------------+
mode-menu is the [Plan|Tasks|Billing] group in the header;
studio-drawer overlays from the right when "Studio" is opened

narrow (≤ 640)
+------------------------+
| shell                  |
+------------------------+
| header  [≡] Title [?][AR]  |
| [Plan | Tasks | Billing]   |   <- mode-menu on its own row
+------------------------+
| content                |
|  Mode Plan · Studio ▸  |
|  fields ...            |
+------------------------+
| results (stacked)      |
+------------------------+
tree = overlay from the left; studio-drawer = bottom sheet
```

## When not to use

- The artefact has one way of being edited and the screen is a form: use `object-page`.
- The modes are a stored status the user moves items through, not ways of editing: use `board`.
- The work is across several sources with a management drawer: use `three-pane`.
- The user only reads the artefact: use `reader`.
