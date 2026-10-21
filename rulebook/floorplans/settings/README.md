---
id: settings
kind: screen
summary: "Grouped configuration with section navigation; not for domain objects"
posture: transient
density: default
---

# settings — Grouped configuration

The one place where an app's configuration lives: preferences, workspace defaults, notifications, integrations, billing details. The screen lists its sections, shows one section at a time, and saves per section. Chosen per `rulebook/rules.md § P18` for configuration that belongs to the person or the workspace; a domain object — a client, a project — is never configured here, it has its index and its home (`rulebook/rules.md § P8`, `rulebook/rules.md § P12`). Settings are one entry in primary navigation, however many sections they hold.

## Regions

| region | role | default tier | holds |
|---|---|---|---|
| `shell` | chrome | — | the shell frame's top strip |
| `section-nav` | navigation | — | the sections as a vertical list or a tab list, one marked current |
| `section-header` | secondary | 2 | the section's title, one line saying whom it applies to (you, the workspace) |
| `section-body` | primary | 1 | the section's groups of controls, each group titled |
| `save-bar` | chrome | — | Save and Cancel for a form section, the saved state for an autosaved one |

Tier 3 surfaces as a named disclosure at the end of a group ("Advanced"), never as a section of its own and never as a row beside the main controls (`rulebook/rules.md § P21`, `rulebook/rules.md § P24`).

## Posture and density

Transient (`rulebook/rules.md § P19`): a person arrives with one change in mind, makes it and leaves, so each section is one view with labelled controls and full verbs; Esc leaves a dialog opened from it, Enter submits the open form. Density `default` (`rulebook/rules.md § P20`): one label-to-control rhythm in every section.

## Responsive

- **Wide (≥ 960 px):** `section-nav` is a left column of section names; `section-header` and `section-body` sit to its right; `save-bar` sits under the body.
- **Narrow (≤ 640 px):** `section-nav` becomes a horizontally scrolling tab strip, or a single "Section" select when there are more than five, above the header; one column of controls with labels above fields; `save-bar` sticks to the bottom edge with Save as the full-width primary.

## Interaction constraints

- **One save model per section** (`rulebook/rules.md § P14`): a form section uses explicit Save and Cancel; a section of switches and segmented controls autosaves each change with an inline "saving / saved" state. The two are never mixed in one section, so a toggle for notifications and a text field for a signature live in different sections or different groups with their own save rule stated in the group title.
- Leaving a section with unsaved changes asks once (`rulebook/rules.md § P14`); switching sections counts as leaving.
- A reset names its scope and sits where it belongs: "Reset notifications to defaults" in the notifications section, not in the page footer (`rulebook/rules.md § P28`).
- The current section is in the URL, `?section=<id>`, so a link lands on it (`rulebook/rules.md § P23`).
- Settings hold no domain objects and no object index; a list of users, clients or projects in a section is a link out to the object's own index.
- A destructive action ("Delete workspace") sits in its own group at the end of its section, apart from benign controls, and asks to confirm (`rulebook/rules.md § P7`). No drawer, no wizard: a setup that is done once is `wizard`.

## Sketch

```text
WIDE
+-----------------------------------------------------------+
| shell                                                     |
+----------------+------------------------------------------+
| section-nav    | section-header   Workspace               |
|  Profile       +------------------------------------------+
|  Workspace  <  | section-body                             |
|  Notifications |  Studio name   [____________]            |
|  Integrations  |  Default rate  [____________]            |
|  Billing       |  > Advanced                              |
|                +------------------------------------------+
|                | save-bar                [Cancel] [ Save ]|
+----------------+------------------------------------------+

NARROW
+---------------------------+
| shell                     |
| section-nav (tab strip)   |
| section-header            |
| section-body              |
|  label                    |
|  [ field ]                |
| save-bar  [ Save ]        |
+---------------------------+
```

## When not to use

- The screen manages domain objects (clients, projects, users): `list-report` for the index, `object-page` for one object.
- The task is a one-time guided setup: `wizard`.
- The screen edits one artefact in modes: `mode-editor`.
- The configuration is one control in context (a view's density, a column choice): a popover on that view, not a settings section.
