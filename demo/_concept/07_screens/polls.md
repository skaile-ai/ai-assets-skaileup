---
screen_id: polls
title: Polls
implements:
  - 05_features/polls/create-poll.md
floorplan: list-report
posture: sovereign
density: default
regions:
  results: { shows: poll, representation: row }
  peek: { shows: poll, representation: peek }
tier_overrides: []
elements:
  - id: open-poll
    kind: button
    label: "Open poll"
    states: [default, disabled]
    region: page-header
    data_entity: Poll
    acceptance_refs: [05_features/polls/create-poll.md#AC-run_a_lunch_poll-01]
    describes: "Click \"Open poll\" -> a dialog asks for title, deadline and places (MOD-1)"
  - id: status-views
    kind: tabs
    label: "Poll views"
    states: [default]
    region: saved-views
    items:
      - { id: view-open, label: "Open" }
      - { id: view-closed, label: "Closed" }
  - id: polls-table
    kind: table
    label: "Polls"
    states: [default, empty, loading]
    region: results
    data_entity: Poll
    columns: ["Title", "Status", "Closes", "Pick"]
    sample_rows:
      - ["Friday lunch", "Open", "12:30", "-"]
      - ["Team lunch after the release", "Closed", "Oct 16", "Mezze Garden"]
    row_target: poll
last_updated: 2026-10-25
---

# Screen: Polls

### Purpose
Find the poll of the day and open it, or open a new one. The task is "which polls are running", so the floorplan is the index of the one primary object (SCR-1, NAV-2).

### Route
`/polls`

### Information Displayed
- `results`: one row per Poll, tier 1 only: title, status, closes at, pick (TIER-1, OBJ-1).
- `peek`: organizer and vote count, tier 2, opened from a labelled control on the row (SURF-1).
- `saved-views`: Open and Closed, restored from the URL (VIEW-1).

### Actions
- Open poll: opens the create dialog (MOD-1, EDIT-1) and, on success, lands on `poll`.
- Click a row: goes to `poll`.
- Peek: reads and links to `poll`.

### Situations
- Default: open polls first.
- Loading: a skeleton row per region (FBK-1).
- Empty: seed scenario `empty`, shows MSG-2.
- Error: an inline alert with retry (MSG-1).
- Edge cases: seed scenario `edge_cases`, a 90 character title truncates in the row and shows whole in the peek.

### UI Elements
`open-poll`, `status-views`, `polls-table`, each declared in `elements:`.

### Template Data
Seed scenario `populated`: poll `q1` "Friday lunch" (Open) and `q2` "Team lunch after the release" (Closed, Mezze Garden).
