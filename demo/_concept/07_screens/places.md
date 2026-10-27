---
screen_id: places
title: Places
implements:
  - 05_features/places/manage-places.md
floorplan: list-report
posture: sovereign
density: default
regions:
  results: { shows: place, representation: row }
tier_overrides: []
elements:
  - id: add-place
    kind: button
    label: "Add place"
    states: [default, disabled]
    region: page-header
    data_entity: Place
    acceptance_refs: [05_features/places/manage-places.md#AC-manage_places-01]
    describes: "Click \"Add place\" -> a dialog with name, cuisine, walking minutes and website (MOD-1)"
  - id: cuisine-filter
    kind: input
    label: "Cuisine"
    states: [default]
    region: filter-bar
    options: ["All", "Italian", "Asian", "Mediterranean", "Local", "Vegetarian"]
  - id: places-table
    kind: table
    label: "Places"
    states: [default, empty, loading]
    region: results
    data_entity: Place
    columns: ["Name", "Cuisine", "Walk"]
    sample_rows:
      - ["Trattoria da Enzo", "Italian", "4 min"]
      - ["Green Fork", "Vegetarian", "11 min"]
last_updated: 2026-10-25
---

# Screen: Places

### Purpose
Keep the list every poll draws from current. The task is maintaining one object type, so the floorplan is the list-report (SCR-1, OBJ-2).

### Route
`/places`

### Information Displayed
- `results`: one row per Place: name, cuisine, walking minutes, tier 1 (TIER-1). The website sits in a peek, tier 3.
- `filter-bar`: cuisine filter and search, kept in the URL (VIEW-1).

### Actions
- Add place: opens the create dialog (MOD-1, EDIT-1).
- Edit: opens the same dialog.
- Archive: hides the place and shows an undo toast (OBJ-2, EDIT-2 style).

### Situations
- Default: alphabetical.
- Empty: seed scenario `empty`, "No places yet - add the first one" (MSG-2 pattern).
- Error: an inline alert with retry (MSG-1).
- Edge cases: seed scenario `edge_cases`, a 120 character name truncates with the full name in a tooltip (POP-1).

### UI Elements
`add-place`, `cuisine-filter`, `places-table`, each declared in `elements:`.

### Template Data
Seed scenario `populated`: six places from Trattoria da Enzo to Pho 24.
