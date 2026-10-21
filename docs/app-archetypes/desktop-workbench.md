---
id: desktop-workbench
title: Desktop workbench
device: desktop
data_weight: data-heavy
project_type: web-app
organization: task-led
primary_surface: none
shell_frame: shell-dock
screens:
  - { step: 1, id: work, floorplan: three-pane, posture: sovereign, density: default, task: "edit across several sources" }
  - { step: 2, id: editor, floorplan: mode-editor, posture: sovereign, density: compact, task: "edit one plan in several modes" }
  - { step: 3, id: settings, floorplan: settings, posture: transient, density: default, task: "change workspace preferences" }
journey: [work, editor, settings]
defaults_bend: []
sources:
  - { kind: rules, title: "Windows app silhouettes", url: "https://learn.microsoft.com/en-us/windows/apps/design/basics/app-silhouette", grade: standard, note: "an editing app puts a menu bar and command bar over the work area, tight 12 epx margins; Settings uses the left-navigation silhouette" }
  - { kind: rules, title: "WinUI NavigationView", url: "https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/navigationview", grade: standard, note: "settings is one optional pane entry; the pane goes expanded, icon-only, then menu-button at 1008 and 640 px; content margins 24 px, 12 px when minimal" }
  - { kind: code, title: "EUI page template", url: "https://eui.elastic.co/docs/components/templates/page-template/", grade: heuristic, note: "a sticky sidebar that scrolls on its own, a minimum width of 248, a bottom bar inside the page body, and a flip to one column on small breakpoints" }
  - { kind: code, title: "react-resizable-panels", url: "https://github.com/bvaughn/react-resizable-panels", grade: heuristic, note: "min and max sizes, collapse below the minimum, layout saved after the drag ends, separators for the keyboard, larger touch targets" }
  - { kind: screens, title: "VS Code UX guidelines overview", url: "https://code.visualstudio.com/api/ux-guidelines/overview", grade: heuristic, note: "a labelled screenshot of a shipped workbench: activity bar, primary and secondary sidebar, editor groups with a toolbar, a bottom panel and a status bar split into workspace and file scope" }
---

# Desktop workbench

A person who spends the whole day on one workspace uses it: an editor or analyst who switches between several sources, reads each source's surroundings beside the work, and works one plan in a few modes. The app is one window with docked panes, a toolbar and a status bar, so there is no destination list to move through; the tree and the work are the content.

## Purpose

A desktop tool that holds one workspace open for long sessions, where the person edits several sources side by side and the tree of those sources is the content. That fact picks `shell-dock` with no primary surface: there is one workspace and no destination list to choose between, so panes, a toolbar and a status bar replace a sidebar. It also picks `three-pane` as the first screen, because a source rail, a work area and a drawer for each source's surroundings serve many sources without leaving the window. When the app has many objects of different kinds, each with its own index and page, take `desktop-data-admin`, where a sidebar lists the destinations. When the work is clearing a queue of incoming items one by one, take `desktop-triage-inbox`, whose first screen is the queue rather than the sources.

## Example apps

- **VS Code** — source files are the objects and the folder tree is the content; the day runs in `work`, with the explorer, the editor and the panel docked together.
- **DaVinci Resolve** — one video project is edited as cut, colour and audio; the work happens in `editor`, where the mode menu switches between the views of one timeline.
- **Zotero** — a researcher reads and annotates sources from many collections; the day runs in `work`, with the collection tree, the item list and the item pane.

## Journey

1. `work` → open one source's plan for deeper editing → `editor`
2. `editor` → open workspace preferences from the header gear → `settings`
3. `settings` → save one section and close → `work`

## Why these floorplans

- `work` (three-pane): "a source rail, a work area and a management drawer; working across several sources" — one editing surface serves many sources, and the drawer shows each source's surroundings beside the work.
- `editor` (mode-editor): "one artefact edited in several modes, with a visible mode menu (P25)" — one plan is edited as plan, tasks or billing, sharing one outline and one results panel.
- `settings` (settings): "grouped configuration with section or tab navigation; not for domain objects" — workspace preferences are grouped, saved per section and reached rarely.

## What the sources add

- An editing app takes a menu bar and a command bar over the work area and tight 12 epx margins, while a settings page keeps roomy margins and a left section list (Windows app silhouettes).
- Settings is one optional entry in the navigation pane, not a page per topic; the pane steps from expanded to icon-only to a menu button at 1008 and 640 px, and content margins drop from 24 px to 12 px when it is minimal (WinUI NavigationView).
- The sidebar keeps a minimum width of 248, sticks and scrolls on its own, the bottom bar stays inside the page body so it never runs under the sidebar, and everything flips to one column at small breakpoints (EUI page template).
- Each pane takes minimum and maximum sizes and collapses below its minimum; the layout is saved only after the drag ends, and separators are kept because they carry keyboard resizing (react-resizable-panels).
- A shipped workbench has an activity bar that selects the view set of the primary sidebar, editor groups with their own toolbar, a bottom panel that shows one view tab at a time, a secondary sidebar users can drag views into, and a status bar whose left items are workspace-scoped and right items file-scoped (VS Code UX guidelines overview).

## Narrow

- The dock shows one pane at a time below 768 px, switched by a Navigate · List · Detail control, and a tool used mostly at this width moves to `shell-mobile-tabs`.
- `work` keeps the work area alone: the source rail opens as an overlay from the left, the drawer as a bottom sheet, and neither holds an edit form.
- `editor` moves the mode menu to its own full-width row with every mode visible, the outline to an overlay and the results panel under the content.
- `settings` turns its section list into a tab strip or a select when there are more than five sections, and the save bar sticks to the bottom edge.

## Open

- **Q1.** The dock folds to one pane at a time with a segmented control, while `work` folds to a rail overlay and a bottom sheet over the work area. Which one is right at phone width, or is the workbench desktop-only and the phone case a separate app?
- **Q2.** With `primary_surface: none` the app has no destination list, yet `settings` still needs a way in. Should it be one entry at the foot of the nav-pane, as WinUI NavigationView does, or the header gear of the mode editor and the palette only?
- **Q3.** The Clarity app layout page (header, sub-nav, vertical nav) renders only in a browser and could not be read, and the EUI template argues for a sidebar page rather than a dock. VS Code's workbench adds an activity bar, a bottom panel and a status bar that the dock frame does not name. Should `shell-dock` and `work` gain a bottom panel and a status bar with workspace-scoped and file-scoped items, or does the workbench stay at rail, work area and drawer?
