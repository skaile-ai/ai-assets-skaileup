---
id: mobile-guided-hub
title: Mobile guided hub
device: mobile
data_weight: simple
project_type: mobile-app
organization: task-led
primary_surface: none
shell_frame: none
screens:
  - { step: 1, id: hub, floorplan: hub-areas, posture: transient, density: comfortable, task: "pick the job I want to do" }
  - { step: 2, id: walk, floorplan: wizard, posture: transient, density: comfortable, task: "walk through a longer job step by step" }
journey: [hub, walk]
defaults_bend:
  - { id: DF11, why: "a phone hub of four to six task tiles is its own search; a keyboard palette has no trigger on a touch screen" }
  - { id: DF14, why: "touch has no hover; the hint is a visible one-line status on the tile and an info control with an accessible name" }
sources:
  - { kind: rules, title: "Apple HIG — Designing for iOS", url: "https://developer.apple.com/design/human-interface-guidelines/designing-for-ios", grade: standard, note: "settled where controls sit on an iPhone and how people go back" }
  - { kind: rules, title: "GOV.UK — Question pages", url: "https://design-system.service.gov.uk/patterns/question-pages/", grade: standard, note: "settled what one walk step holds, how progress reads and which footer parts are required" }
  - { kind: rules, title: "GOV.UK — Complete multiple tasks", url: "https://design-system.service.gov.uk/patterns/complete-multiple-tasks/", grade: standard, note: "settled how a list of jobs shows status and when a job is not yet startable" }
  - { kind: code, title: "Konsta UI — Toolbar component", url: "https://konstaui.com/react/toolbar", grade: heuristic, note: "settled how a pinned bottom footer is built in a mobile page" }
  - { kind: screens, title: "Mobbin — Add and Create mobile screens", url: "https://mobbin.com/explore/mobile/screens/add-create", grade: heuristic, note: "free category page of shipped mobile Add and Create screens; gallery only, no step counts" }
---

# Mobile guided hub

Someone with a phone in one hand does a handful of recurring jobs, such as logging time, checking an amount or sending an invoice, in a minute or two: pick the job from a hub, then walk through its steps. The hub is the app's one destination list and nothing frames it, so there is no navigation surface and no shell frame; `rulebook/rules.md § P22` maps `none` to the desktop dock and records a phone hub as an exception instead.

## Journey

1. `hub` → open a task tile, scan the rows of its area, press the area's primary action → `walk`
2. `walk` → answer one step at a time, review the summary, press its verb → completion state naming what changed and offering the next task

## Why these floorplans

- `hub` (hub-areas): "a phone-sized hub of tiles leading to areas and guided walks; few areas, task-led" — the user picks a job by name, so tiles are tasks and each area lists what the job concerns
- `walk` (wizard): "a guided, linear task with independent steps, done rarely (P31)" — a longer job is steps that stand alone, with a summary step and a completion state

## What the sources add

- Every question page must include a back link, a page heading and a Continue button, and asks one question per page, so a walk step holds one value or one check with Back always present (GOV.UK — Question pages).
- Progress reads as a caption such as "Question 3 of 9"; an indicator that shows every step and lets people jump back is noticed rarely and does not scale to small screens, and one team removed a 12-step version with no change in completion, so `walk-head` keeps one line and a bar (GOV.UK — Question pages).
- A task list starts with two statuses, Completed and Incomplete, adds "In progress" or "Not yet started" only when research asks for them, and lets people finish tasks in any order, so a tile carries one status line (GOV.UK — Complete multiple tasks).
- A task that cannot start yet shows grey "Cannot start yet" text and no link, so a blocked tile stays visible but cannot be opened (GOV.UK — Complete multiple tasks).
- Controls are easier to reach in the middle or bottom of the display, secondary details should take minimal interaction to reach, and swiping back is expected, so both footers sit at the bottom, `peek` hides behind an info control and Back also answers to a swipe (Apple HIG — Designing for iOS).
- The toolbar example pins its bar with `left-0 sticky bottom-0 w-full mt-auto`, so the footer stays at the bottom edge on a short step and a long step scrolls above it (Konsta UI — Toolbar component).

## Narrow

- The hub-areas frames are phone-sized by design: at 640 px and below one frame fills the viewport, going down the flow replaces the frame, Back returns, and `area-foot` and `walk-foot` stay pinned within thumb reach. At 960 px and above the review shows hub, area and walk side by side as three frames of about 340 px.
- The wizard folds `step-list` into one line, "Step 3 of 5", with a progress bar; `step-help` moves under the step's fields; the primary button is full width in the sticky footer, and touching the step line opens the step list as a sheet.
- The hub has no tab bar, sidebar or drawer to fold: with `shell_frame: none` the `shell` region is only a thin strip, and the missing frame is recorded as an exception (`rulebook/rules.md § P22`).

## Open

- **Q1.** GOV.UK labels the question-page button Continue, while the wizard footer says Next, with the primary action at the right (`rulebook/rules.md § P17`). With a full-width pinned button on a phone, does the side matter, and is the label Continue, Next or the step's own verb?
- **Q2.** Where does a walk stop being the short walk inside hub-areas and become the `wizard` screen: after how many steps, and does only the wizard add the summary step with Edit links? None of the sources opened gives a step limit for a phone walk, and the Mobbin page is a gallery without step counts.
- **Q3.** GOV.UK's task list suits jobs spread over several sessions, but hub-areas restores no view state and starts at the hub (`rulebook/rules.md § P23`). Should a tile show Completed or Incomplete for a half-done walk and resume it, or show only a count and always restart?
