# App archetypes

An app archetype is a reusable composition a project starts from: a device and a data weight lead to one shell frame, the shell frame holds screen floorplans in journey order, and a short list records which defaults the archetype commonly bends. It is research, not a rule: an archetype is not a `_concept/` part, it is not shipped with the collection, and no skill reads it yet. Each card is reviewed in a throwaway dashboard before anything folds into `rulebook/`; the floorplans, shell frames and postures the cards name are the ones in [`rulebook/floorplans/`](../../rulebook/floorplans/) and the navigation model is the one in [`rulebook/rules.md`](../../rulebook/rules.md) (P18 picks the frame and the floorplans, P22 records the navigation model).

## The matrix

The device axis has two values, desktop and mobile; an archetype that works on both is listed under `both` and appears in both desktop and mobile review.

| | simple | data-heavy |
|---|---|---|
| **desktop** | [simple-content-app](simple-content-app.md) (both), [simple-single-tool](simple-single-tool.md) (both) | [desktop-data-admin](desktop-data-admin.md), [desktop-triage-inbox](desktop-triage-inbox.md), [desktop-workbench](desktop-workbench.md), [desktop-analytics](desktop-analytics.md), [planning-board](planning-board.md) (both) |
| **mobile** | [mobile-companion](mobile-companion.md), [mobile-guided-hub](mobile-guided-hub.md), [simple-content-app](simple-content-app.md) (both), [simple-single-tool](simple-single-tool.md) (both) | [mobile-field-capture](mobile-field-capture.md), [planning-board](planning-board.md) (both) |

## The ten archetypes

| id | device | data | organization | primary_surface → shell_frame | screens in journey order (floorplan) |
|---|---|---|---|---|---|
| [desktop-data-admin](desktop-data-admin.md) | desktop | data-heavy | object-led | sidebar → `shell-sidebar` | overview → list-report → object-page → wizard (create a complex object) → settings |
| [desktop-triage-inbox](desktop-triage-inbox.md) | desktop | data-heavy | hybrid | sidebar → `shell-sidebar` | overview → master-detail (queue) → object-page (canonical home) → settings |
| [desktop-workbench](desktop-workbench.md) | desktop | data-heavy | task-led | none → `shell-dock` | three-pane → mode-editor → settings |
| [desktop-analytics](desktop-analytics.md) | desktop | data-heavy | hybrid | sidebar → `shell-sidebar` | overview (dashboard) → list-report (drill-down) → tabbed-tool (one analysis) → object-page |
| [planning-board](planning-board.md) | both | data-heavy | object-led | topbar → `shell-topbar` | board → object-page (card's page) → settings |
| [simple-content-app](simple-content-app.md) | both | simple | task-led | topbar → `shell-topbar` | reader → settings |
| [simple-single-tool](simple-single-tool.md) | both | simple | task-led | topbar → `shell-topbar` (one destination) | wizard (first-run setup) → tabbed-tool → settings |
| [mobile-companion](mobile-companion.md) | mobile | simple | object-led | bottom-tabs → `shell-mobile-tabs` | overview → list-report (cards) → object-page → settings |
| [mobile-guided-hub](mobile-guided-hub.md) | mobile | simple | task-led | none → no frame, recorded as an exception per P22 | hub-areas (hub → area → walk) → wizard (a longer walk) |
| [mobile-field-capture](mobile-field-capture.md) | mobile | data-heavy | object-led | bottom-tabs → `shell-mobile-tabs` | overview → list-report (cards, work queue) → object-page → wizard (capture, one question per step) |

Across the ten cards every floorplan in `rulebook/floorplans/` appears at least once: shell-sidebar three times, shell-topbar three times, shell-dock once, shell-mobile-tabs twice, and all twelve screen floorplans.

## The card schema

A card is `docs/app-archetypes/<id>.md`: YAML frontmatter between two `---` lines, then a markdown body of at most 60 lines. All frontmatter keys are required.

```yaml
---
id: desktop-data-admin              # equals the filename stem
title: Desktop data admin
device: desktop                     # desktop | mobile | both
data_weight: data-heavy             # simple | data-heavy
project_type: web-app               # web-app | mobile-app (mobile cards: mobile-app, others: web-app)
organization: object-led            # object-led | task-led | hybrid (P22)
primary_surface: sidebar            # sidebar | topbar | tabs | rail+drawer | bottom-tabs | none (P22)
shell_frame: shell-sidebar          # a kind: shell floorplan id, or the literal none
screens:                            # journey order; step counts from 1 without gaps; id is a unique slug [a-z0-9-]+
  - { step: 1, id: home,   floorplan: overview,    posture: sovereign, density: default, task: "see what needs me now" }
  - { step: 2, id: orders, floorplan: list-report, posture: sovereign, density: compact, task: "find and compare orders" }
journey: [home, orders]             # a permutation of screens[].id: every id once
defaults_bend: []                   # [] or a list of { id: DF9, why: "..." }
sources:                            # [] for a stub; 3 to 5 for a researched card
  - { kind: rules, title: "...", url: "https://...", grade: standard, note: "one line: what it settled" }
---
```

Allowed values: `posture` is sovereign, transient or auxiliary; `density` is compact, default or comfortable; a `sources[].kind` is rules, screens or code; a `sources[].grade` is standard, field, heuristic or owner. Every `floorplan` is a directory under `rulebook/floorplans/` whose README has `kind: screen`; `shell_frame` is one whose README has `kind: shell`, or `none`. Posture and density default to the floorplan README's own frontmatter and are changed only with a reason in the body.

The body has a `# <title>` line, then exactly these headings in this order. A stub carries the single line `TODO` under each heading, and as the intro paragraph.

- Intro: one paragraph between the title line and `## Journey`: who uses the app daily and for what, in two or three sentences.
- `## Journey`: a numbered list, one hop per line, screen ids in backticks and the arrow `→`: ``1. `home` → open an order → `order` ``. The last line ends on a completion state or on the sovereign screen.
- `## Why these floorplans`: one bullet per screen, starting with the screen id in backticks and the floorplan in parentheses, then the task phrase from the P18 table in quotes and one clause why: ``- `orders` (list-report): "the index of one navigation: primary object" — rows are compared and acted on``.
- `## What the sources add`: three to six bullets, each one fact that changes a choice and each ending with the source title in parentheses, exactly as written in `sources[].title`.
- `## Narrow`: two to four bullets: what the archetype does on a phone-width viewport, per the chosen floorplans' responsive sections and per any source rule.
- `## Open`: one to three bullets, each starting `**Q1.**`, `**Q2.**` and so on: the questions a reviewer answers in a comment.

Bodies use headings, paragraphs, `-` bullets, `1.` numbered lists, inline code, `**bold**` and `[text](https://…)` links, and nothing else: no tables, no images, no HTML.

## Review comments

The review dashboard is a throwaway Vite app in `.scratch/archetypes/` (gitignored, local to this checkout). Run `npm run dev` there to start it. That command validates the cards, regenerates the pages and serves them at `http://127.0.0.1:3041/`. Each archetype page shows the shell frame and every screen in journey order, with the rulebook preview at 1040 px and 390 px side by side. A comment made with the toolbar records the page route as its target. Its Context reads `<screen id> · Wide|Narrow · <px> — <floorplan>`, which names the screen and the width.

Comments live in `.scratch/archetypes/.data/annotations`. Read them before folding a card into `rulebook/`, with `curl -s 'http://127.0.0.1:3041/__annotations?format=markdown'` while the dashboard runs. Answer each one with `POST /__annotations/resolve` and `{"ids":["<inboxId>"],"status":"implemented"|"rejected","resolution":"<why>"}`. The `annotations_list` tool does not see these comments. It reads `.data/annotations` at the repository root, while the dashboard writes under its own Vite root, so the curl listing is the reader of record.
