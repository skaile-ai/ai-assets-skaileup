---
name: quality-interaction
description: "Use when an app's code exists — checks it against the interaction decisions in APP-DESIGN.md entry by entry and type by type (against the rulebook's invariants alone when none is written), counts violations and exemplars per rule, and writes the ordered changes that close them. Triggers on 'check the app against APP-DESIGN.md', 'does the UI follow our patterns', 'interaction review', 'where do we still break the rules'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
    - contract:@skaile-ai/app-design-rulebook
  artifacts:
    requires:
      - { id: app-design }
    produces:
      - { id: interaction-review, path: "_concept/11_build/interaction.sarif" }
  prerequisites:
    files:
      # Soft: without `APP-DESIGN.md` the skill checks the rulebook invariants (P) alone and lists every heuristic and
      # default as unchecked, naming `experience-interaction` as the next step (`tree/11_build/interaction.md § The applicable set`).
      - { path: "APP-DESIGN.md", gate: soft }
      - { path: "_concept/10_blueprint/techstack.md", gate: soft }
      - { path: "_concept/02_grounding/findings/stack.md", gate: soft }
---

# quality-interaction

Checks the app's source against the rules `APP-DESIGN.md` decides and writes `_concept/11_build/interaction.sarif`. The source roots come from the stack — `_concept/10_blueprint/techstack.md`, else `_concept/02_grounding/findings/stack.md`, else the repository's own layout (`src/`, or `app/` + `server/`). It judges conformance and nothing else: it changes no application code and does not edit `APP-DESIGN.md`, which `experience-interaction` owns. A finding is measured at a `file:line`, or it is not one.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Read the intent** — `tree/APP-DESIGN.md § Reading it` when `APP-DESIGN.md` exists, then step 1 of `tree/11_build/interaction.md § Writing it`, which builds the applicable set (`tree/11_build/interaction.md § The applicable set`) from `rulebook/rules.md` and `rulebook/defaults.md`: every invariant not excepted, the heuristics the app adopted, its decided entries. A decided entry replaces the default of the rules it cites; Exceptions are not reported; `[open Qn]` entries are judged by their recommendation. Without `APP-DESIGN.md` the set is the invariants alone, every heuristic and default is `unchecked` and the report names `experience-interaction` as the next step. Several apps in one repo is a question for the user.
2. **Take the census and walk the entries** — `tree/02_grounding/findings/interaction.md § Where UI sits per stack` for where UI sits and how citations are checked; steps 2–3 of `tree/11_build/interaction.md § Writing it`, which include the tier checks and the duplicated-behaviour check. Evidence passes that only collect run in parallel on a small, fast model; classifying and judging stay in this session.
3. **Record, count, order** — steps 4–6 of `tree/11_build/interaction.md § Writing it` (one finding per cause, severity, class), counts per `tree/11_build/interaction.md § Counting`. Counts come from a script or `jq` over the file, never from typing.
4. **Check the citations** — step 7 of `tree/11_build/interaction.md § Writing it`; a failing citation is fixed or the finding dropped before anything is written.
5. **Write the verdict** — `tree/11_build/interaction.md § Format`, level mapping from `tree/11_build/README.md § SARIF levels`, step 8 of `tree/11_build/interaction.md § Writing it`. The file replaces the previous run's whole. Show the `underReview` results and the questions to the user; an answer that changes an entry reaches `APP-DESIGN.md` through `experience-interaction`, and `build-plan` reads the `open` changes.
6. **Report** — step 9 of `tree/11_build/interaction.md § Writing it`: score table, changes in order, unchecked rules, unread regions, questions.

**Done when** `tree/11_build/interaction.md § Checks` holds: `_concept/11_build/interaction.sarif` is valid SARIF 2.1.0, every `fail` result cites a `file:line` the citation check passes, every rule is scored or listed as unchecked, every violation is covered by a change or carries an `underReview` suppression, and the unread regions are named.
