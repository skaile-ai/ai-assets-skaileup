---
id: planning-board
title: Planning board
device: both
data_weight: data-heavy
project_type: web-app
organization: object-led
primary_surface: topbar
shell_frame: shell-topbar
screens:
  - { step: 1, id: board, floorplan: board, posture: sovereign, density: default, task: "move tasks through their stages" }
  - { step: 2, id: task, floorplan: object-page, posture: sovereign, density: default, task: "work on one task" }
  - { step: 3, id: settings, floorplan: settings, posture: transient, density: default, task: "change board and account preferences" }
journey: [board, task, settings]
defaults_bend:
  - { id: DF2, why: "A planning board's card drawer is a work space: people change status, assignee and due date there without leaving the board, so the drawer hosts those quick edits while sections and child rows stay on the task page." }
sources:
  - { kind: rules, title: "Salesforce Lightning Design System — Layout", url: "https://www.lightningdesignsystem.com/2e1ef8501/p/33e9af-layout", grade: standard, note: "Board columns 12 to 25 rem, 2/3 and 1/3 record and workspace layouts, master-detail from 1024 px." }
  - { kind: rules, title: "Atlassian Design System — Layout usage", url: "https://atlassian.design/components/navigation-system/layout/usage", grade: standard, note: "Panel beside the main area, overlay at 1024 px and below, panel versus modal, slot and tab order." }
  - { kind: rules, title: "Android Developers — Canonical layouts", url: "https://developer.android.com/develop/adaptive-apps/guides/canonical-layouts", grade: standard, note: "Supporting pane split 70/30 expanded, 50/50 medium, below or bottom sheet compact; the Material 3 supporting-pane page rendered empty, so this page stands in." }
  - { kind: code, title: "Refine — CRM application template", url: "https://refine.dev/core/templates/crm-application/", grade: heuristic, note: "Enterprise-flagged template, so read for which screens a kanban app ships, not for reuse." }
  - { kind: screens, title: "SaaS Interface — Boards design examples", url: "https://saasinterface.com/pages/boards/", grade: heuristic, note: "Free page lists 45 shipped board screens (ClickUp, Attio, Fibery and more); thumbnails only, full gallery is paid." }
---

# Planning board

A small team or a solo planner opens the board every day to see where each task stands and to move it to the next stage, on a laptop at the desk or on a phone between meetings. A card opens a drawer for a quick look and a quick change, and the task's own page holds the sections, subtasks and history. Settings are visited rarely, to change the board's stages, notifications and account details.

## Journey

1. `board` → open a card, read it in the drawer, choose "Open" → `task`
2. `task` → back to the board → `board`
3. `board` → account menu → `settings`
4. `settings` → Save → `board`

## Why these floorplans

- `board` (board): "the same items in columns or switchable views (kanban, calendar, list) with a card drawer" — people work the flow of tasks through stages, not look one up.
- `task` (object-page): "one object with a header, key facts, sections and child collections; the home of a complex object" — a task with subtasks, notes and history outgrows the drawer.
- `settings` (settings): "grouped configuration with section or tab navigation; not for domain objects" — stages, notifications and account details are configuration, and a task is never configured here.

## What the sources add

- Columns are 12 to 25 rem wide; past the viewport the board scrolls sideways, and when the columns do not fill it they stop at 25 rem and leave the area right of the last column empty; a column header may carry one aggregate of a numeric field (Salesforce Lightning Design System — Layout)
- A record layout is 2/3 main and 1/3 sidebar with the sidebar at least 400 px; its workspace variant puts activity large and related records in the sidebar under a record summary, which is the other order the task page could take (Salesforce Lightning Design System — Layout)
- A panel sits beside the main area and can be collapsed or resized, but at 1024 px and below it becomes an overlay; a modal is for a decision the person must make before going back (Atlassian Design System — Layout usage)
- Slots keep the order top nav, main, panel for tab and reading order, and the grid covers the main area only, never the panel: the card drawer comes after the columns and sits outside the column grid (Atlassian Design System — Layout usage)
- A supporting pane is meaningful only beside its primary content, unlike a list-detail pane; it takes 70/30 at expanded width, 50/50 at medium and goes below the main area or into a bottom sheet at compact, so the card drawer follows the supporting-pane split (Android Developers — Canonical layouts)
- The CRM template gives the sprint kanban, the sales pipeline and the calendar their own destinations beside the dashboard and administration, where the board floorplan makes them views of one index (Refine — CRM application template)

## Narrow

- The board shows one status column at a time, chosen from a status tab strip, with full-width cards; the filter bar collapses to a search field and one "Filters" button. At 390 px two 12 rem columns would leave no margin, which supports one column.
- The card drawer becomes a bottom sheet that closes by swipe, Esc or its close button, which matches the compact rule for a supporting pane and the overlay rule for a panel.
- The top bar folds to brand, menu, search and create; the task page stacks its header and facts into two columns, and settings keep a tab strip or a section select with a sticky Save.

## Open

- **Q1.** The drawer pushes the columns from 960 px in the board floorplan, but Atlassian turns its panel into an overlay at 1024 px and below; should the board overlay between 960 and 1024 px, and should the drawer host quick edits of status, assignee and due date (the bent DF2)?
- **Q2.** The top bar frame is transient and comfortable, while a board that is open all day is sovereign; keep the top bar with a recorded exception for the board, or move such a board to a sidebar frame?
- **Q3.** The Refine template gives kanban and calendar their own destinations and SLDS's workspace layout puts activity ahead of related records; keep one board with a view switch and the fixed object-page order, or split the views and reorder the task page? The Material 3 supporting-pane page loaded as an empty shell, so the Android canonical-layouts page stands in for it; is that enough?
