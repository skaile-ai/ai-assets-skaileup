---
name: concept-research
description: "Use when a decision needs grounding in something other than the room's opinion — the domain, the competitors, the audience, or the visual references screens will be designed against. Runs after onboarding and before the brief, and again beside any later step that needs grounding. Triggers on 'research this', 'what do competitors do', 'find inspiration', 'who are the users really'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
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
      - { path: "_concept/02_grounding/onboarding/answers.json", gate: soft }
      - { path: "_concept/brief.md", gate: soft }
    inputs_optional:
      - { id: research_scope, label: "What to research", type: multiselect, options: [domain, competitors, audiences, design, patterns, colors, behavioral], hint: "Leave empty for the four defaults" }
---

# concept-research

Fills `02_grounding/research/` with sourced findings other skills design against, and
`02_grounding/findings/` with the raw material behind them. It runs after `concept-onboard` and
before `concept-brief`, and again beside any later step that needs grounding. It writes findings
only: no brief, no features, no tokens.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Scope, dispatch and write the topic files** — `tree/02_grounding/research/README.md`. It names the node for each of the seven files (`domain`, `competitors`, `audiences`, `design-inspiration` by default; `patterns`, `colors-fonts`, `behavioral-patterns` when scoped) and the `step/<skill-name>/` rule.
2. **Catalogue the raw material** — `tree/02_grounding/findings/README.md § Filing raw material (concept-research, design-brand)`, with `step: concept-research`.

**Done when** every file the scope asked for exists, every factual claim in them names its source, and `02_grounding/findings/index.md` accounts for the raw material.
