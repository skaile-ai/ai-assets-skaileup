---
id: simple-content-app
title: Simple content app
device: both
data_weight: simple
project_type: web-app
organization: task-led
primary_surface: topbar
shell_frame: shell-topbar
screens:
  - { step: 1, id: reader, floorplan: reader, posture: sovereign, density: default, task: "read articles one after another" }
  - { step: 2, id: settings, floorplan: settings, posture: transient, density: default, task: "change reading preferences" }
journey: [reader, settings]
defaults_bend:
  - { id: DF11, why: "two destinations need no palette; the reader filters its own list, so the top bar keeps a plain search field instead of a Cmd/Ctrl-K layer" }
sources:
  - { kind: rules, title: "Apple HIG — Sidebars", url: "https://developer.apple.com/design/human-interface-guidelines/sidebars", grade: standard, note: "a sidebar holds at most two levels; a deeper hierarchy gets a content list between the sidebar and the detail" }
  - { kind: rules, title: "Apple HIG — Tab bars", url: "https://developer.apple.com/design/human-interface-guidelines/tab-bars", grade: standard, note: "on iPhone a few destinations belong in a visible tab bar, not behind a More overflow" }
  - { kind: rules, title: "Android — Canonical layouts", url: "https://developer.android.com/develop/adaptive-apps/guides/canonical-layouts", grade: standard, note: "list-detail shows both panes only at expanded width; narrower windows show list or detail with Back returning to the list, and the open item survives a resize" }
  - { kind: code, title: "GitHub Primer — PageLayout", url: "https://primer.style/product/components/page-layout/", grade: heuristic, note: "runnable header/content/pane/sidebar regions with a 256 px pane minimum, persisted pane width and a full-screen sidebar below 768 px" }
  - { kind: screens, title: "Mobbin — Mobile settings screens", url: "https://mobbin.com/explore/mobile/screens/settings-preferences", grade: heuristic, note: "shipped settings screens tag preferences with Switch and Bottom Sheet elements, not long forms" }
---

# Simple content app

People who read a stream of documents each day — a client's briefs, a knowledge base, a news list — open this app to find one document, read it through and move to the next. They use it on a laptop or a phone, change a reading preference rarely, and leave again.

## Journey

1. `reader` → choose Settings in the top bar → `settings`
2. `settings` → change a reading preference → `reader`

## Why these floorplans

- `reader` (reader): "consuming content: filters, a list or tree and a reading pane" — the task is reading one document after another, with the list and the open document side by side.
- `settings` (settings): "grouped configuration with section or tab navigation; not for domain objects" — reading preferences are configuration of the person, not objects.

## What the sources add

- List-detail shows list and detail together only at expanded width; at medium and compact width one pane shows and Back returns to the list, so the reader's overlay on narrow follows the platform rule (Android — Canonical layouts).
- A resize keeps the open item: narrowing with both panes keeps the detail and hides the list, widening from detail-only selects the item in the list, and widening from list-only shows a placeholder detail (Android — Canonical layouts).
- A sidebar holds at most two levels of hierarchy; a deeper tree needs a content list between the sidebar and the detail, which is the reader's tree → list → pane order (Apple HIG — Sidebars).
- On iPhone a tab bar stays visible, avoids overflow tabs and keeps empty sections reachable with an explanation; a menu panel hides the destinations until it is opened (Apple HIG — Tab bars).
- A pane has a 256 px minimum width and may be resizable with the width persisted per user; a sidebar can cover the full viewport like a dialog below 768 px (GitHub Primer — PageLayout).
- Mobbin's mobile settings gallery tags notification screens with the Switch element and an "Appearance Settings" screen with the Bottom Sheet element, so reading preferences suit short switch or choice groups that autosave, without a long form (Mobbin — Mobile settings screens).

## Narrow

- The top bar folds to brand · menu · search · create; the two destinations sit in the menu panel, with Settings last or in the account menu.
- `reader` becomes one column: filters collapse into one "Filters · n applied" disclosure above the tree and list, and the open document is a full-width overlay whose close returns to the list with the row still selected.
- `settings` turns its section list into a tab strip, or a single select above five sections, with labels above fields and a save bar stuck to the bottom edge.
- Back closes the reader overlay first and only then leaves the screen, as list-detail does on Android; the open document stays in the URL so a reload reopens it.

## Open

- **Q1.** The shell-topbar frame is transient and comfortable, but `reader` is sovereign and the user stays in it all day. Should the app record this as an exception, or does a reader app with a client → project tree belong in `shell-sidebar`?
- **Q2.** On a phone Apple recommends a visible tab bar for a few destinations, while shell-topbar hides them behind a menu. For two destinations (Reader, Settings), should the mobile case use `shell-mobile-tabs` instead?
- **Q3.** Android names a feed (a single scrolling column of cards that becomes a grid) as the layout for news and social content. For "read articles one after another", should the reader keep its list + pane, or open the list as a card feed on wide and narrow alike?
