# App archetypes

An archetype is a starting composition: a device and a data weight pick a shell frame, and the frame holds screen floorplans in journey order. An app declares one row as `archetype: <id>` on the `§ Navigation model` line of `APP-DESIGN.md`, or `archetype: none`, which leaves every choice to `P18` and `P22` as before. A declared row is a default, not a rule: its frame and its floorplans hold until a NAV entry in `APP-DESIGN.md` names a departure and why, so a shell or a screen that differs is a recorded decision rather than a quiet override. The `bends` column lists the defaults such an app commonly declines; each one is still a `§ Exceptions` row citing its `DF` id.

The rows are derived from the research cards in `docs/app-archetypes/`, which are not part of this asset; a card changes first, then its row, and `scripts/check.py` fails while the two differ.

| id | device | data weight | organization | primary_surface | shell_frame | journey floorplans | bends |
|---|---|---|---|---|---|---|---|
| `desktop-analytics` | desktop | data-heavy | hybrid | sidebar | `shell-sidebar` | `overview` → `list-report` → `tabbed-tool` → `object-page` | — |
| `desktop-data-admin` | desktop | data-heavy | object-led | sidebar | `shell-sidebar` | `overview` → `list-report` → `object-page` → `wizard` → `settings` | — |
| `desktop-triage-inbox` | desktop | data-heavy | hybrid | sidebar | `shell-sidebar` | `overview` → `master-detail` → `object-page` → `settings` | DF2 |
| `desktop-workbench` | desktop | data-heavy | task-led | none | `shell-dock` | `three-pane` → `mode-editor` → `settings` | — |
| `mobile-companion` | mobile | simple | object-led | bottom-tabs | `shell-mobile-tabs` | `overview` → `list-report` → `object-page` → `settings` | DF11, DF14 |
| `mobile-field-capture` | mobile | data-heavy | object-led | bottom-tabs | `shell-mobile-tabs` | `overview` → `list-report` → `object-page` → `wizard` | DF11 |
| `mobile-guided-hub` | mobile | simple | task-led | none | `none` | `hub-areas` → `wizard` | DF11, DF14 |
| `planning-board` | both | data-heavy | object-led | topbar | `shell-topbar` | `board` → `object-page` → `settings` | DF2 |
| `simple-content-app` | both | simple | task-led | topbar | `shell-topbar` | `reader` → `settings` | DF11 |
| `simple-single-tool` | both | simple | task-led | topbar | `shell-topbar` | `wizard` → `tabbed-tool` → `settings` | DF11 |

`shell_frame: none` is the hub case of `P22`: the hub is the one destination list and no frame is drawn, recorded as an exception in `_concept/07_screens/shell.md`.
