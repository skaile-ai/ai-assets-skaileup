---
name: concept-research
description: "Use when a decision needs grounding in something other than the room's opinion — the domain, the competitors, the audience, or the visual references screens will be designed against; run it once for the project and again beside any step that needs more. Triggers on 'research this', 'what do competitors do', 'find inspiration', 'who are the users really'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: scope }
      - { id: onboarding-answers }
    produces:
      - { id: research-domain, path: "_concept/02_grounding/research/domain.md" }
      - { id: research-competitors, path: "_concept/02_grounding/research/competitors.md" }
      - { id: research-audiences, path: "_concept/02_grounding/research/audiences.md" }
      - { id: research-design-inspiration, path: "_concept/02_grounding/research/design-inspiration.md" }
      - { id: research-patterns, path: "_concept/02_grounding/research/patterns.md" }
      - { id: research-colors-fonts, path: "_concept/02_grounding/research/colors-fonts.md" }
      - { id: research-behavioral-patterns, path: "_concept/02_grounding/research/behavioral-patterns.md" }
      - { id: research-step, path: "_concept/02_grounding/research/step/<skill-name>/" }
      - { id: grounding-findings, path: "_concept/02_grounding/findings/" }
  prerequisites:
    files:
      - { path: "_concept/01_meta/scope.yaml", gate: soft }
      - { path: "_concept/02_grounding/onboarding/answers.json", gate: soft }
      - { path: "_concept/brief.md", gate: soft }
    inputs_optional:
      - { id: research_scope, label: "What to research", type: multiselect, options: [domain, competitors, audiences, design, patterns, colors, behavioral], hint: "Leave empty for the four defaults" }
---

# concept-research

Fills `02_grounding/research/` with sourced findings other skills design against, and
`02_grounding/findings/` with the raw material behind them. It runs once for the project and
again beside any step that needs more grounding. It writes findings only: no brief, no
features, no tokens.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Pick the depth, scope, dispatch and write the topic files** — `tree/02_grounding/research/README.md`. It maps `depth` from `scope.yaml` to the research depth (asked when absent, per `tree/01_meta/scope.md`) and names the node for each of the seven files (`domain`, `competitors`, `audiences`, `design-inspiration` by default; `patterns`, `colors-fonts`, `behavioral-patterns` when scoped) and the `step/<skill-name>/` rule.
2. **Catalogue the raw material** — `tree/02_grounding/findings/README.md § Filing raw material (concept-research, design-brand)`, with `step: concept-research`.

**Done when** every file the scope asked for exists, every factual claim in them names its source, and `02_grounding/findings/index.md` accounts for the raw material.
