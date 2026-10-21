---
id: simple-single-tool
title: Simple single tool
device: both
data_weight: simple
project_type: web-app
organization: task-led
primary_surface: topbar
shell_frame: shell-topbar
screens:
  - { step: 1, id: setup, floorplan: wizard, posture: transient, density: comfortable, task: "set the tool up on first run" }
  - { step: 2, id: tool, floorplan: tabbed-tool, posture: sovereign, density: default, task: "look something up across a few views" }
  - { step: 3, id: settings, floorplan: settings, posture: transient, density: default, task: "change preferences" }
journey: [setup, tool, settings]
defaults_bend:
  - { id: DF11, why: "one destination and three tabs leave little for a Cmd/Ctrl-K palette to rank; the top bar keeps a plain search field instead" }
sources:
  - { kind: rules, title: "SAP Fiori — wizard usage", url: "https://www.sap.com/design-system/fiori-design-web/v1-136/ui-elements/wizard/usage", grade: standard, note: "wizard length of 3 to 8 steps, summary screen with Edit per section, footer button order and how the progress bar groups steps when narrow" }
  - { kind: rules, title: "AWS Cloudscape — create resource", url: "https://cloudscape.design/patterns/resource-management/create/", grade: standard, note: "criteria table that separates a single-page form from a multipage wizard by field count, groups and frequency" }
  - { kind: rules, title: "GOV.UK Design System — check answers", url: "https://design-system.service.gov.uk/patterns/check-answers/", grade: standard, note: "one check-answers page before the confirmation, Change links that return to it, Not provided for skipped answers" }
  - { kind: rules, title: "GitLab Pajamas — settings management", url: "https://design.gitlab.com/patterns/settings-management", grade: standard, note: "one save model per form, no navigation entry per settings page, an in-page shortcut to the relevant setting" }
  - { kind: code, title: "Cloudscape demos — multipage create wizard", url: "https://github.com/cloudscape-design/demos/tree/main/src/pages/wizard", grade: heuristic, note: "runnable wizard with four steps ending in Review and create, a submit label that names the effect and a Step n of m label when collapsed" }
---

# Simple single tool

A person who opens one small lookup tool most working days, on a laptop or a phone, to find something across a few views of the same data. The first run walks through a short setup once; after that the tool is the whole app, and its settings are a rare visit.

## Journey

1. `setup` → answer each step, review the summary and confirm → completion state that names what was set up, then "Open the tool" → `tool`
2. `tool` → pick a tab, narrow with the shared filters, open a row in the overlay → `tool`
3. `tool` → open the settings control in the page header → `settings`
4. `settings` → change a section, save it and go back → `tool`

## Why these floorplans

- `setup` (wizard): "a guided, linear task with independent steps, done rarely" — first-run answers are independent and asked once, then reused
- `tool` (tabbed-tool): "a single-column tool with a tab list, a shared filter row and an overlay detail" — the views are siblings of one dataset, not a flow
- `settings` (settings): "grouped configuration with section or tab navigation; not for domain objects" — preferences live in one place that is one entry in the top bar

## What the sources add

- A wizard runs 3 to 8 steps; a task with two steps, or one done daily, gets a plain form instead, so a setup that asks fewer than three things collapses to one page (SAP Fiori — wizard usage)
- The summary screen shows every answer read-only with an Edit button per section, and its button says what it does ("Create"), while Back sits left of Next in the footer and Cancel moves into an overflow when the footer is short (SAP Fiori — wizard usage)
- A single page serves 2 to 15 fields or up to 5 groups; a wizard starts above 16 fields or more than 5 groups and fits infrequent tasks, and fields that have a good default move to an additional-configuration section (AWS Cloudscape — create resource)
- One check-answers page sits right before the confirmation, a Change link returns to it directly instead of replaying later steps, and an optional question left empty reads "Not provided" (GOV.UK Design System — check answers)
- A settings form never mixes manual Save with autosave, and a new settings page gets no navigation entry: the feature page carries an icon-only settings link with the tooltip "Configure in settings" (GitLab Pajamas — settings management)
- The reference wizard has four steps, the last titled "Review and create", a submit button that names its effect, and a help panel that closes when the step changes (Cloudscape demos — multipage create wizard)

## Narrow

- `setup`: the step list folds to one line "Step n of m" with a progress bar, help moves under the fields, and the footer sticks to the bottom with a full-width primary button; Fiori groups the progress steps the same way on phones.
- `tool`: the filter row keeps only search, the other filters open in a bottom sheet from "Filters · n", secondary columns drop from the rows, and the row overlay fills the screen.
- Top bar: it folds to brand, menu button and search; with one destination the menu panel holds only Settings, and `settings` shows its sections as a tab strip, or a "Section" select above five.

## Open

- **Q1.** `tool` is sovereign but sits in `shell-topbar`, whose density is comfortable: should the tool stay sovereign at default density as tabled, or declare the transient posture because it is a lookup opened briefly?
- **Q2.** Cloudscape and Fiori send a short setup to a single page; is the first run really three or more independent steps for this tool, or should `setup` become one form with a summary? No free screens page showed a shipped first-run setup (SaaSUI's onboarding page shows only thumbnails), so which one should the review compare against?
- **Q3.** After the first run, should `setup` stay reachable again, for example as a link at the end of a `settings` section, or never be shown again?
