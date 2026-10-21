---
id: mobile-companion
title: Mobile companion
device: mobile
data_weight: simple
project_type: mobile-app
organization: object-led
primary_surface: bottom-tabs
shell_frame: shell-mobile-tabs
screens:
  - { step: 1, id: home, floorplan: overview, posture: sovereign, density: default, task: "see what needs me now" }
  - { step: 2, id: parcels, floorplan: list-report, posture: sovereign, density: default, task: "find my parcels" }
  - { step: 3, id: parcel, floorplan: object-page, posture: sovereign, density: default, task: "check one parcel" }
  - { step: 4, id: settings, floorplan: settings, posture: transient, density: default, task: "change app preferences" }
journey: [home, parcels, parcel, settings]
defaults_bend:
  - { id: DF11, why: "a phone has no Cmd/Ctrl-K; search is the top bar's search icon opening a full-screen palette, and the shortcut half of the default does not apply" }
  - { id: DF14, why: "touch has no hover; every tab and action carries its text label, so no tooltip is needed" }
sources:
  - { kind: rules, title: "Apple HIG — Tab bars", url: "https://developer.apple.com/design/human-interface-guidelines/tab-bars", grade: standard, note: "tab bar is for navigation not actions, stays visible when going deeper, keeps empty tabs, avoids overflow" }
  - { kind: rules, title: "Apple HIG — Settings", url: "https://developer.apple.com/design/human-interface-guidelines/settings", grade: standard, note: "few settings, only infrequent ones; task options stay on the screen they affect" }
  - { kind: rules, title: "Android Developers — Canonical layouts", url: "https://developer.android.com/develop/adaptive-apps/guides/canonical-layouts", grade: standard, note: "feed is one column at compact width; list-detail shows one pane; supporting content goes below or into a bottom sheet" }
  - { kind: code, title: "Konsta UI — kitchen sink Tabbar page", url: "https://github.com/konstaui/konsta/blob/master/kitchen-sink/react/pages/Tabbar.jsx", grade: heuristic, note: "runnable fixed bottom tab bar with icon and label slots and bottom padding that clears it" }
  - { kind: screens, title: "Mobbin — Mobile settings screens", url: "https://mobbin.com/explore/mobile/screens/settings-preferences", grade: heuristic, note: "shipped phone settings screens: grouped rows, switches, top bar, bottom sheets" }
---

# Mobile companion

A person who keeps a phone-sized view of things they already own, such as the parcels they expect, and opens it several times a day. They check what needs attention now, find one parcel, read where it stands, and rarely change a preference.

## Journey

1. `home` → tap the Parcels tab → `parcels`
2. `parcels` → tap a parcel card → `parcel`
3. `parcel` → go back, then open Settings from the tab bar → `settings`
4. `settings` → change a preference, tap Save, then tap the Home tab → `home`

## Why these floorplans

- `home` (overview): "the next actionable rows" — the first screen answers what needs attention and each row is one tap from its parcel.
- `parcels` (list-report): "overview strip, filter bar, table or cards" — a person finds a parcel among a few dozen, and on a phone the rows are cards.
- `parcel` (object-page): "one object with a header, key facts, sections and child collections" — one parcel with its status, facts and tracking steps.
- `settings` (settings): "grouped configuration with section or tab navigation" — a short list of preferences that is not about parcels.

## What the sources add

- The tab bar only navigates and stays visible while a person goes deeper, so the pushed `parcel` keeps it; an empty tab stays in place and says why it is empty. (Apple HIG — Tab bars)
- Fewer tabs are easier to use, a trailing More tab hides content, and a badge is for critical news only; the Parcels tab carries the one badge, for parcels that need attention. (Apple HIG — Tab bars)
- Filter, sort and view options live on `parcels` itself, not in `settings`, and settings hold only general, rarely changed options. (Apple HIG — Settings)
- At compact width a feed is one scrolling column of equal cards, list-detail shows the list or the detail but not both, and supporting content sits below the main content or in a bottom sheet. (Android Developers — Canonical layouts)
- The work area needs bottom padding that clears the fixed tab bar and the safe-area inset, so the last card is not hidden behind it. (Konsta UI — kitchen sink Tabbar page)
- Shipped phone settings screens, named "Settings List" and "Settings Page", carry the Switch, Top Navigation Bar and Bottom Sheet tags: grouped rows under a top bar, a toggle in the row, and multi-choice settings picked in a bottom sheet. (Mobbin — Mobile settings screens)

## Narrow

- The phone is the design target: the column is the viewport, the top bar and the tab bar are fixed, the tab bar hides while the keyboard is up, and at 960 px and wider the app stays one centred column of at most 480 px.
- `home` is one column of two-line rows whose tap target is the row; `parcels` shows cards, a two-column overview strip, a scrolling saved-views row and a bottom-sheet peek.
- `parcel` stacks its header, makes the primary action full width, shows facts in two columns and lets the section tabs scroll sideways.
- `settings` turns its section list into a tab strip or one select, and the Save bar sticks to the bottom edge with a full-width Save.

## Open

- **Q1.** With three destinations the shell has no More tab, yet its rules put Settings in More. Should Settings take the third tab, or sit behind an avatar in the top bar so the tab bar keeps room for a later object tab?
- **Q2.** Android's canonical layouts name a plain card feed for phones; the tabled `parcels` floorplan adds an overview strip and a filter bar above the cards. Do these earn their height at 390 px for a person with a few dozen parcels?
- **Q3.** The Material 3 canonical-layouts page returned no text, so the Android Developers page stands in for it. Is one Android source enough for the compact-width rules, or should a second platform source be added?
