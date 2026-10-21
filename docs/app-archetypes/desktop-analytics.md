---
id: desktop-analytics
title: Desktop analytics
device: desktop
data_weight: data-heavy
project_type: web-app
organization: hybrid
primary_surface: sidebar
shell_frame: shell-sidebar
screens:
  - { step: 1, id: home, floorplan: overview, posture: sovereign, density: default, task: "see how the business is doing today" }
  - { step: 2, id: campaigns, floorplan: list-report, posture: sovereign, density: default, task: "drill down to the campaigns behind a number" }
  - { step: 3, id: analysis, floorplan: tabbed-tool, posture: sovereign, density: default, task: "analyse one campaign across views" }
  - { step: 4, id: campaign, floorplan: object-page, posture: sovereign, density: default, task: "read one campaign in full" }
journey: [home, campaigns, analysis, campaign]
defaults_bend: []
sources:
  - { kind: rules, title: "Cloudscape — static dashboard", url: "https://cloudscape.design/patterns/general/service-dashboard/static-dashboard/", grade: standard, note: "Dashboard areas top to bottom, a seven-item limit and parent and child dashboards." }
  - { kind: rules, title: "PatternFly — dashboard design guidelines", url: "https://www.patternfly.org/patterns/dashboard/design-guidelines/", grade: standard, note: "Card kinds, ranking before placement, equal-width columns and a height cap for growing cards." }
  - { kind: screens, title: "Dashboard Design Patterns catalogue", url: "https://dashboarddesignpatterns.github.io/patterns.html", grade: heuristic, note: "Hierarchical versus parallel page structure and the stratified layout, with labelled screenshots." }
  - { kind: code, title: "shadcn/ui dashboard-01 registry entry", url: "https://ui.shadcn.com/r/styles/new-york-v4/dashboard-01.json", grade: heuristic, note: "Runnable block order of cards, chart and table, with the container breakpoints and the row drawer." }
  - { kind: code, title: "AG Grid finance demo", url: "https://www.ag-grid.com/example-finance/", grade: heuristic, note: "A viewport-height grid with sparkline cells; source in the ag-grid-demos repo." }
---

# Desktop analytics

A marketing analyst or campaign manager opens this app every morning to see how spend and results are moving, then follows one number down to the campaigns behind it. They compare campaigns in a table, study one campaign across several views, and read its full record when a figure needs explaining.

## Journey

1. `home` → follow "View all campaigns" on a metric card → `campaigns`
2. `campaigns` → open the analysis of one campaign from its row → `analysis`
3. `analysis` → open the full record from the analysis header → `campaign`
4. `campaign` → follow the "Overview" breadcrumb → `home`

## Why these floorplans

- `home` (overview): "the landing screen that answers "what needs me now" with the next actionable rows" — the day starts here, with a block per kind of waiting work and a link into the filtered list.
- `campaigns` (list-report): "the index of one `navigation: primary` object: overview strip, filter bar, table or cards" — the drill-down target holds the rows behind a number, to compare and sort.
- `analysis` (tabbed-tool): "a single-column tool with a tab list, a shared filter row and an overlay detail" — one campaign is read through sibling views that share one date range.
- `campaign` (object-page): "one object with a header, key facts, sections and child collections; the home of a complex object" — the full record, with ad sets and spend as child collections.

## What the sources add

- A dashboard runs top to bottom as an overview area (page actions, status), a data area (charts, then lists) and a support area, with at most seven items in a chart or list; `home` follows that order (Cloudscape — static dashboard).
- A parent dashboard carries the key insights and a child dashboard the insights for one set of resources, so `home` stays the parent and `analysis` is the child view of one campaign (Cloudscape — static dashboard).
- Each card holds one metric or a group of closely related metrics, ranked before placement because the ranking becomes the stacking order on one column; columns are equal width (four at 1200–1400 px, 16 px gutters) and a growing events card gets a four-row height cap with scroll (PatternFly — dashboard design guidelines).
- The journey is a hierarchical structure (abstract overview, then detail pages), while the tabs inside `analysis` are a parallel structure reached by tab links, and a stratified layout puts the highest-level figures on top (Dashboard Design Patterns catalogue).
- Block order is metric cards (1, 2, then 4 columns by container width), one interactive area chart whose 90/30/7-day toggle becomes a select on a narrow card and presets 7 days on mobile, then the data table, whose row detail opens in a right drawer (a bottom drawer on mobile) (shadcn/ui dashboard-01 registry entry).
- The grid fills the viewport height minus header and margin, sparklines sit in a table column at a 42 px row height, and font and grid spacing shrink at 720 px instead of the table turning into cards (AG Grid finance demo).

## Narrow

- `home` stacks into one column in ranked order; the time-range control folds into a select with a short default range, and a data-heavy chart gives way to a link into `analysis`, since touch handles dense charts poorly.
- `campaigns` turns the table into cards with a two-column strip, a bottom bulk bar and a bottom-sheet peek; `analysis` keeps only the search field in its filter row and moves the rest into a "Filters · n" bottom sheet, with the detail overlay full-screen.
- `campaign` stacks its header, shows facts in a two-column grid and scrolls the section navigation sideways; the sidebar becomes a drawer at 767 px and below, with the pinned destinations in a bottom pill.

## Open

- **Q1.** The `overview` floorplan carries no totals, counters or charts, yet every source opens a dashboard with metric cards and a trend chart. Keep `overview` and add a metrics region for this archetype, give `home` its own dashboard floorplan, or let the overview strip of `campaigns` carry the figures?
- **Q2.** `tabbed-tool` is described as a small lookup tool without an object hierarchy, while `analysis` studies one campaign with a chart per tab. Should `analysis` stay a screen of its own, or become the tab set of the `campaign` object page?
- **Q3.** Cloudscape prefers a static layout when the order of items matters, as it does for monitoring a campaign, and warns against mixing static and configurable items. Is `home` static, with a fixed block order, or may people hide and reorder cards?
