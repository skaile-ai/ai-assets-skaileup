---
id: desktop-data-admin
title: Desktop data admin
device: desktop
data_weight: data-heavy
project_type: web-app
organization: object-led
primary_surface: sidebar
shell_frame: shell-sidebar
screens:
  - { step: 1, id: home, floorplan: overview, posture: sovereign, density: default, task: "see what needs me now" }
  - { step: 2, id: orders, floorplan: list-report, posture: sovereign, density: compact, task: "find and compare orders" }
  - { step: 3, id: order, floorplan: object-page, posture: sovereign, density: default, task: "work on one order" }
  - { step: 4, id: order-create, floorplan: wizard, posture: transient, density: comfortable, task: "create a complex order" }
  - { step: 5, id: settings, floorplan: settings, posture: transient, density: default, task: "change workspace preferences" }
journey: [home, orders, order, order-create, settings]
defaults_bend: []
sources:
  - { kind: rules, title: "SAP Fiori — list report usage", url: "https://www.sap.com/design-system/fiori-design-web/v1-136/page-types/floorplans/list-report-floorplan-sap-fiori-element/usage", grade: standard, note: "Views as a content switch, live filter bar, and grid tables limited to desktop and tablet with a separate reduced app for phones." }
  - { kind: rules, title: "SAP Fiori — object page usage", url: "https://www.sap.com/design-system/fiori-design-web/v1-136/page-types/floorplans/object-page/usage", grade: standard, note: "Anchor bar versus tab bar, table-count and row-count limits per page, and the small-screen dropdown." }
  - { kind: rules, title: "SAP Fiori — wizard usage", url: "https://www.sap.com/design-system/fiori-design-web/v1-136/ui-elements/wizard/usage", grade: standard, note: "Three to eight steps, not for routine tasks, summary with Edit per section, discard popover, and the grouped progress bar on narrow screens." }
  - { kind: rules, title: "Cloudscape — create resource", url: "https://cloudscape.design/patterns/resource-management/create/", grade: standard, note: "Field-count and group-count thresholds that separate a dialog, a single page and a multipage wizard." }
  - { kind: code, title: "Nuxt UI dashboard template — layout", url: "https://raw.githubusercontent.com/nuxt-ui-templates/dashboard/main/app/layouts/default.vue", grade: heuristic, note: "A runnable collapsible, resizable sidebar with search on top, destinations above and utility links pinned below." }
---

# Desktop data admin

Back-office staff run an order system all day: they scan what needs attention, find and compare orders in a long list, work inside each order's page, and now and then create a complex order through a guided flow. They return to the same list and filters many times a day, so the list is compact and the view state survives every round trip.

## Purpose

Staff who work one primary kind of record all day: a long list of orders to filter, compare and act on, with each order holding child collections of its own. Two facts pick the frame and the first screen: the app has more than about five destinations used for sovereign work, so `shell-sidebar` fits better than a top bar, and staff open the app to see which orders are due or stuck, so the first screen is the `overview` of actionable rows rather than a dashboard of totals. Take `desktop-triage-inbox` instead when the day is spent clearing a queue one item at a time with the detail beside the list, and `desktop-analytics` when users mostly read aggregates and drill down only now and then.

## Example apps

- **Shopify admin** — orders and products are the objects; the day runs in `orders` and `order`, and `home` shows what needs attention first.
- **Freight forwarder shipment desk** — a dispatcher filters the day's shipments in `orders` and works each booking's documents, charges and tracking in `order`.
- **Municipal permit office** — building permits are the objects; a clerk checks applications in `orders` and creates a multi-party permit through `order-create`.

## Journey

1. `home` → open "All orders due this week" → `orders`
2. `orders` → open an order row → `order`
3. `order` → back through the breadcrumb, press Create order → `order-create`
4. `order-create` → press Create order on the summary step → completion state "Order created" → open the new order → `order`
5. `order` → open Settings in the sidebar → `settings`
6. `settings` → save a section, open Overview in the sidebar → `home`

## Why these floorplans

- `home` (overview): "the landing screen that answers "what needs me now" with the next actionable rows" — a data admin opens on due and stuck orders, not on totals.
- `orders` (list-report): "the index of one `navigation: primary` object" — orders are filtered, compared and acted on in bulk at compact density.
- `order` (object-page): "one object with a header, key facts, sections and child collections" — an order holds line items, payments and history, so it is a page and never a drawer.
- `order-create` (wizard): "a guided, linear task with independent steps, done rarely" — creating a complex order is infrequent next to viewing orders, and runs transient at comfortable density.
- `settings` (settings): "grouped configuration with section or tab navigation" — workspace preferences only; the order index stays on `orders`.

## What the sources add

- Predefined views such as All, Open and Assigned sit in the content area as a segmented button for up to three views and as a select beyond three, and the filter bar updates live rather than behind a Go button. (SAP Fiori — list report usage)
- Grid tables are supported on desktop and tablet only; for phones Fiori builds a separate app with reduced scope instead of folding the table. (SAP Fiori — list report usage)
- Use the anchor bar for a short order page and switch to tabs when sections hold long tables: at most four grid tables per anchor page, 50 to 200 rows move into their own tab, and over 200 rows navigate to another page. (SAP Fiori — object page usage)
- A wizard has three to eight steps, is wrong for routine work, ends on a summary with an Edit link per section, and asks "Discard this order?" in a small popover on Cancel. (SAP Fiori — wizard usage)
- A flow needs a multipage wizard only above 16 fields or five groups of settings and when input is immutable after creation; below that, a single page serves, and errors are caught at every step and again on the summary. (Cloudscape — create resource)
- The sidebar is collapsible and resizable with a search button on top, main destinations above and Feedback and Help pinned to the bottom edge. (Nuxt UI dashboard template — layout)

## Narrow

- The sidebar becomes a drawer at 767 px and below (an icon rail between 768 and 992 px); the page header folds to toggle, title, search and create, and the slideover becomes a bottom sheet.
- `orders` turns its table into cards in the same row order, the bulk bar into a bottom bar, saved views into a horizontal scroll and the peek into a bottom sheet; `order` stacks its sections with a scrolling section-nav, where Fiori uses a dropdown for the anchor bar.
- `order-create` folds its step list into "Step 3 of 5 · Team" with a progress bar and a sticky full-width primary button; `settings` turns its section-nav into a tab strip, or a select above five sections, with a sticky Save.
- `home` is one column in the order header, attention blocks, recent; a row's action becomes its tap target.

## Open

- **Q1.** The Nuxt dashboard opens on a date-range toolbar, stats and a chart, while the `overview` floorplan shows no totals, counters or charts. Keep rows of what needs attention only, or allow one KPI strip above the attention blocks for admins who watch volume?
- **Q2.** The list-report floorplan sends a complex object to a quick-create dialog and then its page, while Cloudscape reserves a wizard for more than 16 fields or five groups. Does an order cross that line, or should Create open a dialog and then `order`? No free screens page loaded (SaaS Interface lists names behind a paywall), so which shipped admin screen should the review compare against?
- **Q3.** Nuxt keeps settings sub-navigation as toolbar tabs in a centred column capped at `max-w-2xl` (42 rem) and lists its children under the sidebar; the floorplan uses a left section-nav and keeps one Settings entry. Keep the left column at 1040 px?
