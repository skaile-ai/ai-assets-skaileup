---
id: mobile-field-capture
title: Mobile field capture
device: mobile
data_weight: data-heavy
project_type: mobile-app
organization: object-led
primary_surface: bottom-tabs
shell_frame: shell-mobile-tabs
screens:
  - { step: 1, id: home, floorplan: overview, posture: sovereign, density: default, task: "see today's jobs and what needs me now" }
  - { step: 2, id: jobs, floorplan: list-report, posture: sovereign, density: default, task: "work through my job queue" }
  - { step: 3, id: job, floorplan: object-page, posture: sovereign, density: default, task: "read one job on site" }
  - { step: 4, id: capture, floorplan: wizard, posture: transient, density: comfortable, task: "capture findings one question per step" }
journey: [home, jobs, job, capture]
defaults_bend:
  - { id: DF11, why: "a phone has no Cmd/Ctrl-K chord; the top bar's search icon opens the palette and page actions still rank first" }
sources:
  - { kind: rules, title: "SAP Fiori — worklist floorplan usage", url: "https://www.sap.com/design-system/fiori-design-web/v1-136/page-types/floorplans/work-list/usage", grade: standard, note: "a worklist is for processing items: sticky status tabs with counts, return to the list after finishing, phones get a reduced app" }
  - { kind: rules, title: "SAP Fiori for Android — canonical layouts", url: "https://www.sap.com/design-system/fiori-design-android/v26-4/foundations/adaptive-layout/canonical-layouts", grade: standard, note: "one pane on compact and medium windows, two from expanded; panes stack rather than shrink" }
  - { kind: rules, title: "GOV.UK Design System — question pages", url: "https://design-system.service.gov.uk/patterns/question-pages/", grade: standard, note: "one question per page with back link, heading and Continue; a short 'Question n of m' caption beats a step list" }
  - { kind: screens, title: "Dynamics 365 Field Service mobile UX", url: "https://www.microsoft.com/en-us/dynamics-365/blog/it-professional/2023/10/27/transform-technician-experience-with-the-new-field-service-mobile-ux/", grade: heuristic, note: "shipped technician app: three bottom tabs, booking rows with the deciding facts, fixed bottom action, tasks with progress" }
  - { kind: code, title: "Konsta UI — Tabbar", url: "https://konstaui.com/react/tabbar", grade: heuristic, note: "runnable bottom tab bar: fixed to the bottom edge, safe-area padding, labels off unless asked for" }
---

# Mobile field capture

A technician or inspector works through the day's assigned jobs on site, one hand free, in short sessions between locations. They open the app to see what is due next, read one job's facts and record findings as they go. The queue is long and data-heavy, but each visit shows one job and one question at a time.

## Journey

1. `home` → open "All jobs due today" → `jobs`
2. `jobs` → tap a job card → `job`
3. `job` → "Start capture" → `capture`
4. `capture` → "Save findings" on the summary step → completion state "Findings saved" → `jobs`

## Why these floorplans

- `home` (overview): "the landing screen that answers "what needs me now" with the next actionable rows" — a technician starts the day with the next due jobs, not totals.
- `jobs` (list-report): "the index of one `navigation: primary` object" — the queue is the one list of jobs, shown as cards with status views.
- `job` (object-page): "one object with a header, key facts, sections and child collections" — a job carries site facts, tasks and earlier findings that a dialog cannot hold.
- `capture` (wizard): "a guided, linear task with independent steps" — findings are asked one question per step, with a summary and a completion state (P31).

## What the sources add

- A worklist offers status views such as Open, In process and Completed as a sticky tab bar with an item count on each tab, so `jobs` takes its `saved-views` in that shape (SAP Fiori — worklist floorplan usage).
- After the last step the app returns to the list, removes the processed item or moves it to a completed view, and confirms with a toast; the completion state of `capture` therefore leads back to `jobs` (SAP Fiori — worklist floorplan usage).
- Windows up to the medium class keep one pane and panes stack instead of shrinking, so `job` stays one column in the shell's 480 px column even on a tablet in portrait (SAP Fiori for Android — canonical layouts).
- A question page holds one question, a back link, a heading and a "Continue" button; "Question 3 of 9" as a caption replaces a full step list, and an "I do not know" answer is offered where valid (GOV.UK Design System — question pages).
- The shipped technician app lists bookings with customer, incident type, address, start time and status per row, and fixes the "Edit Status" button to the bottom of the booking; `jobs` rows and the `job` primary action follow that (Dynamics 365 Field Service mobile UX).
- The tab bar is fixed to the bottom edge with a safe-area padding below the content, and labels are off by default, so the shell sets them on (Konsta UI — Tabbar).

## Narrow

- Phone width is the design case: the 1040 px view is the same one column, at most 480 px wide and centred, between a fixed top bar and the bottom tab bar.
- `jobs` shows cards with the title, status and two or three facts; `saved-views` scroll sideways, the filter bar wraps and the peek is a bottom sheet. The worklist guidance for phones is a reduced app, not a squeezed table, and these cards are that reduced form.
- `job` stacks its header, takes a full-width primary action, shows facts in two columns and scrolls `section-nav` sideways; child rows become two-line items.
- `capture` folds the step list into one line, "Step 3 of 5 · Team", with a progress bar and a full-width primary button in a sticky footer; the tab bar hides while the keyboard is up.

## Open

- **Q1.** The P18 table gives the wizard to tasks "done rarely", yet a technician captures findings many times a day, which P19 keeps away from wizards. Keep `capture` as a wizard with one question per step (GOV.UK), or make it an inline findings section on `job`?
- **Q2.** The shell keeps the tab bar visible on a pushed screen and the wizard sticks its footer to the bottom edge, which stacks two bars on a phone. Hide the tab bar during `capture`, and label the primary "Continue" (GOV.UK) or "Next"?
- **Q3.** Fiori and the Field Service app treat a queue of work to process as a worklist, apart from the list-report for finding items in a large set. Is a status-tabbed list-report enough for `jobs`, or should the rulebook gain a worklist floorplan?
