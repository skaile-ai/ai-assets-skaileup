---
id: desktop-triage-inbox
title: Desktop triage inbox
device: desktop
data_weight: data-heavy
project_type: web-app
organization: hybrid
primary_surface: sidebar
shell_frame: shell-sidebar
screens:
  - { step: 1, id: home, floorplan: overview, posture: sovereign, density: default, task: "see what needs me now" }
  - { step: 2, id: queue, floorplan: master-detail, posture: sovereign, density: compact, task: "work down the ticket queue" }
  - { step: 3, id: ticket, floorplan: object-page, posture: sovereign, density: default, task: "handle one ticket in full" }
  - { step: 4, id: settings, floorplan: settings, posture: transient, density: default, task: "change queue and notification preferences" }
journey: [home, queue, ticket, settings]
defaults_bend:
  - { id: DF2, why: "the queue's detail pane commonly hosts a short reply or note composer, as in PatternFly's primary-detail and the Nuxt inbox, so the pane would edit" }
sources:
  - { kind: rules, title: "Android canonical layouts (list-detail)", url: "https://developer.android.com/develop/adaptive-apps/guides/canonical-layouts", grade: standard, note: "list-detail pane behaviour per width class and how selection survives a resize; stands in for M3's list-detail page, which loads as an empty shell" }
  - { kind: rules, title: "PatternFly primary-detail", url: "https://www.patternfly.org/patterns/primary-detail/design-guidelines/", grade: standard, note: "selected-row state, empty detail state, close affordance and the phone slide-over" }
  - { kind: rules, title: "Atlassian navigation system layout", url: "https://atlassian.design/components/navigation-system/layout/usage", grade: standard, note: "side nav plus panel slots, panel versus modal, panel overlay at 1024 px and below" }
  - { kind: rules, title: "SAP Fiori flexible column layout", url: "https://www.sap.com/design-system/fiori-design-web/v1-136/page-types/page-layouts/flexible-column-layout/usage", grade: standard, note: "list-detail column ratios, no overview page inside a column, phone shows the last column" }
  - { kind: code, title: "Nuxt UI dashboard template inbox page", url: "https://raw.githubusercontent.com/nuxt-ui-templates/dashboard/main/app/pages/inbox.vue", grade: heuristic, note: "runnable inbox: resizable list panel, keyboard selection, slideover below lg" }
---

# Desktop triage inbox

A support or operations team member keeps this open all day: tickets arrive, and the job is to decide the next action on each one and move on. The queue is the daily surface; a ticket opens in full only when it needs a thread, attachments or history. Settings are visited rarely, to tune the queue and notifications.

## Journey

1. `home` → open "All tickets waiting on me" → `queue`
2. `queue` → select a row, assign or change status, take the next row → `queue`
3. `queue` → open the selected ticket in full → `ticket`
4. `ticket` → set the status to resolved; the page offers the next ticket → `queue`
5. `queue` → open Settings in the sidebar → `settings`
6. `settings` → save a section and leave → `home`

## Why these floorplans

- `home` (overview): "the landing screen that answers "what needs me now" with the next actionable rows" — blocks of at most four tickets (waiting on me, due today) each with one action.
- `queue` (master-detail): "browsing a list with the selected item's detail beside it; triage and edit-next" — the person works down rows and reads each one beside the list.
- `ticket` (object-page): "one object with a header, key facts, sections and child collections; the home of a complex object" — thread, attachments and history make a ticket more than a panel can hold.
- `settings` (settings): "grouped configuration with section or tab navigation; not for domain objects" — queue rules and notification preferences, one sidebar entry.

## What the sources add

- When the window narrows with a ticket open, the detail stays and the list hides; widening with only the list shows it beside a placeholder detail, and the selected row stays marked. Back from the detail is handled by the pane, not by app navigation (Android canonical layouts (list-detail)).
- The primary row needs a selected state, and the detail shows an empty state when nothing is selected or several rows are checked; a dismissible detail carries a close icon at its top right, and on a phone the detail slides over the list while the list title stays as the header (PatternFly primary-detail).
- Two-column defaults are 33% to 66% or 66% to 33%, with a splitter for other ratios; an overview page cannot sit inside a column, so `home` stays its own screen and the queue starts from it (SAP Fiori flexible column layout).
- A phone shows only the last column, so a queue that starts with two columns must force the list first; after a resize the list scrolls to the open row, so the person sees which ticket the detail shows (SAP Fiori flexible column layout).
- Slots follow the order top nav, side nav, main, panel, which fixes tab and reading order; the panel holds contextual and tertiary actions, a modal holds a decision that must finish first (such as confirming a resolve), and the panel becomes an overlay at 1024 px and below (Atlassian navigation system layout).
- The list panel defaults to 25% (20% to 30%, resizable) with the reading pane filling the rest; All and Unread tabs and a count sit in the list header, arrow keys move the selection, and below `lg` (1024 px) the detail opens as a slideover. The selected mail is component state, not a URL key (Nuxt UI dashboard template inbox page).

## Narrow

- The sidebar becomes a drawer; the bottom-pill pins Home and Queue plus a Menu entry, and the slideover, where used, is a full-width bottom sheet (`shell-sidebar`).
- `queue` shows the list with two-line rows, then the detail as its own view with "Back to list"; Back restores scroll position and selection, and the activity strip is dropped because the selected `?ticket=<id>` lives in the URL.
- `home` is one column with rows wrapping to two lines; `ticket` stacks its header, shows facts in two columns and scrolls its section navigation sideways.
- `settings` turns its section list into a tab strip, or a "Section" select above five sections, with Save sticking to the bottom edge.

## Open

- **Q1.** PatternFly and the Nuxt inbox let the detail pane host a reply or edit form, while `master-detail` and DF2 keep it to read and triage and send writing to `ticket`. Should the queue's detail carry a short reply composer (declining DF2, as the card records), or only an "Open" link to the ticket?
- **Q2.** The Nuxt inbox gives the list about a quarter of the width and the reading pane the rest, Fiori starts at 33% to 66%, and `master-detail` fixes the detail near 360 px. For tickets read at length, should the queue lean to a wide detail, or stay a wide list with a narrow triage panel for comparing rows? Atlassian and Nuxt also overlay the panel at 1024 px, where the floorplan folds at 960 px.
- **Q3.** No free screens page gave layout facts: SaaS Interface category pages and SaaSFrame inbox frames sit behind a paywall, and M3's list-detail page loads as an empty shell, so Android's page stands in. Is one code template plus four rule pages enough, or should a paid gallery close the gap?
