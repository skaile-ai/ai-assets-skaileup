---
name: quality-design
description: "Use when an app is built or adopted and you suspect its design, not its conformance, is what hurts users — scans the code against the rulebook, the glossary and APP-DESIGN.md for shallow screens, overloaded concepts, hidden modes, undeclared representations and tier violations, reports evidenced candidates, then grills the one you pick. Triggers on 'what is wrong with this design', 'find design problems', 'which screens should merge', 'improve the UX of this app', 'design review of the code'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
    - contract:@skaile-ai/app-design-rulebook
  artifacts:
    requires:
      - { id: app-design }
      - { id: glossary }
      - { id: screens }
      - { id: techstack }
      - { id: grounding-findings }
    produces:
      - { id: design-candidates, path: "_concept/11_build/design-candidates.md" }
      - { id: decisions, path: "_concept/10_blueprint/decisions.md" }
  prerequisites:
    files:
      - { path: "APP-DESIGN.md", gate: soft }
      - { path: "_concept/glossary.md", gate: soft }
      - { path: "_concept/07_screens", gate: soft, min_entries: 1 }
      - { path: "_concept/10_blueprint/techstack.md", gate: soft }
      - { path: "_concept/02_grounding/findings", gate: soft }
    inputs_optional:
      - { id: focus, label: "Screens, routes or folders to scan", type: text, hint: "Defaults to the whole app" }
---

# quality-design

Finds where the adopted design costs users something and helps the user decide one change. It reads the code (the roots `_concept/10_blueprint/techstack.md` or `_concept/02_grounding/findings/stack.md` name, else `src/`), changes no application code, and where `APP-DESIGN.md`, the glossary or screen specs are absent it judges against `rulebook/rules.md` and says so. Conformance to decided entries is `quality-interaction`'s; concept-file integrity is `ops-review`'s.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Read the intent** — `tree/11_build/design-candidates.md § Writing it` step 1, with `tree/APP-DESIGN.md § Reading it`. A derive-or-ask step per `tree/README.md § How a skill runs`: a missing input is scoped `concept-reverse` or a rulebook-only scan, never a stop.
2. **Scan in parallel** — step 2 of `tree/11_build/design-candidates.md § Writing it`, one detection pass per kind of `tree/11_build/design-candidates.md § Detection`, on a small, fast model; judging stays here.
3. **Judge into a candidate report** — steps 3–4 of `tree/11_build/design-candidates.md § Writing it`, shaped by `tree/11_build/design-candidates.md § Format`. HTML only when the user asks.
4. **Ask which candidate to pursue** — step 5 of `tree/11_build/design-candidates.md § Writing it`; one batch per rule 2, one candidate per run.
5. **Grill the candidate** — step 6 of `tree/11_build/design-candidates.md § Writing it`. Call the Skill tool with "grilling"; when it is absent, run the same questions inline as one batch.
6. **Design it twice (optional)** — step 7 of `tree/11_build/design-candidates.md § Writing it`; three parallel alternatives and a consequence table, when the user agrees.
7. **Land the result** — step 8 of `tree/11_build/design-candidates.md § Writing it` and `tree/11_build/design-candidates.md § Landing proposals`: `proposed` entries through each owner's node (a term filed as a proposed term per `tree/glossary.md § Where the words live`, then `tree/APP-DESIGN.md § Format`, `tree/07_screens/[screen].md § Format`) and the record per `tree/10_blueprint/decisions.md § Format`.
8. **Report** — step 9 of `tree/11_build/design-candidates.md § Writing it`; claims measured or inferred per rule 8, next steps named by demand.

**Done when** `tree/11_build/design-candidates.md § Checks` holds: the report parses, every candidate cites a `file:line` that passes the citation check, the picked candidate carries its `DR-<n>`, and every landed proposal names `quality-design` as proposer.
