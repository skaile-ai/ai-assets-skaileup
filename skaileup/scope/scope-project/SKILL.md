---
name: skaileup-scope-scope-project
description: "Use when the user starts a new project and no _concept/_meta/scope.yaml exists yet, or when re-scoping (--tier= override). Picks one of mvp / simple-app / standard-app / complex-app from a one-sentence project description and writes _concept/_meta/scope.yaml. First action in the skaileup pipeline; gates which flow runs next."
metadata:
  version: "1.0.0"
  tags:
    - scope
    - tier
    - orchestrator-entry
    - flow-selection
    - skaileup
  stage: alpha
  prerequisites:
    inputs_required:
      - id: project_description
        label: "One-sentence project description"
        type: text
        hint: "Plain English. Example: 'A team todo app with assignees and due-date reminders.'"
    inputs_optional:
      - id: tier_override
        label: "Force a specific tier (skips interview)"
        type: select
        options: [mvp, simple-app, standard-app, complex-app]
        default: null
        hint: "Equivalent to --tier=<name>. Bypasses the decision rule but records what the rule would have picked."
      - id: features_estimate
        label: "Estimated number of distinct user-facing features"
        type: number
        hint: "Skip if you'd rather be asked during the interview."
      - id: multi_user
        label: "Multiple user roles or shared/collaborative state?"
        type: boolean
      - id: persistence
        label: "Data persistence shape"
        type: select
        options: [trivial, structured, external]
      - id: integrations
        label: "External services (comma-separated)"
        type: text
    reads:
      - path: "_concept/_meta/scope.yaml"
        description: "Existing scope (re-scoping case). When present, current values are loaded as defaults."
    produces:
      - path: "_concept/_meta/scope.yaml"
        description: "Authoritative tier + reasoning + signals for this project. Read by every downstream tier flow."
---
