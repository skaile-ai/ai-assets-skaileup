---
name: experience-interaction
description: "Use when the app's interaction rules are not written down yet — navigation model, where information lives, one editor per object, inline vs dialog vs page, information tiers, saving, messages, popups, buttons, search and command palette — or when a code check has proposed changes to them. Adopts the rulebook's defaults with the user, decides what remains in batches and writes APP-DESIGN.md. Triggers on 'write the app design', 'APP-DESIGN.md', 'when do we use a modal', 'UI rules for this app', 'interaction decisions'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
    - contract:@skaile-ai/app-design-rulebook
  artifacts:
    requires:
      - { id: scope }
    produces:
      - { id: app-design, path: "APP-DESIGN.md" }
      - { id: decisions, path: "_concept/10_blueprint/decisions.md" }
  prerequisites:
    files:
      - { path: "_concept/01_meta/scope.yaml", gate: soft }
      - { path: "_concept/glossary.md", gate: soft }
      - { path: "_concept/10_blueprint/datamodel/", gate: soft }
      - { path: "_concept/04_journeys/stories.yaml", gate: soft }
      - { path: "_concept/02_grounding/findings/interaction.md", gate: soft }
      - { path: "_concept/11_build/interaction.sarif", gate: soft }
      - { path: "APP-DESIGN.md", gate: soft }
---

# experience-interaction

The owner of `APP-DESIGN.md` at the project root: the app's recorded choices against the rulebook — navigation model, object map, information tiers, screen defaults, surfaces, saving, messages, popups, buttons, finding. It decides and records, and writes no screen, no destination list and no code.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Resolve the facts** — `tree/APP-DESIGN.md § Reading it`, then steps 1–2 of `tree/APP-DESIGN.md § Writing it`. An existing `APP-DESIGN.md` is intent: its decided entries stay. Glossary and data model are read when they exist and none is required; object names are never coined here. `_concept/11_build/interaction.sarif` or proposed entries in `APP-DESIGN.md` present mean a re-entry, which jumps to item 5.
2. **Offer the defaults bundle** — `rulebook/defaults.md`, step 3 of `tree/APP-DESIGN.md § Writing it`: one message, accept all or pick DF1–DF15; the adopted ids go on the `defaults:` line, each declined one becomes an exception.
3. **Ask the depth** — step 4 of `tree/APP-DESIGN.md § Writing it` (`sketch · standard · exhaustive`, rule 3 of `tree/README.md § How a skill runs`). `depth` in `scope.yaml` (`tree/01_meta/scope.md`) is the recommendation when present; an answer given where it is absent is recorded there as a `proposed` entry.
4. **Decide in batches, write after each** — `rulebook/rules.md`, steps 5–6 of `tree/APP-DESIGN.md § Writing it` and `tree/APP-DESIGN.md § Format`. Without a user the recommendation carries `[open Qn]`.
5. **Refine, fold in a code check, settle proposals** — step 7 of `tree/APP-DESIGN.md § Writing it` and `tree/11_build/interaction.md § Format` for the `interaction.sarif` fields; step 9 for the entries `experience-screen` and `quality-design` proposed, each promoted or rejected into `tree/10_blueprint/decisions.md`. The verdict file is `quality-interaction`'s and stays as it is; an exception enters the file only on the user's answer.
6. **Carry gaps and trade-offs home** — step 8 of `tree/APP-DESIGN.md § Writing it`: a missing term goes to the glossary as `proposed`, a choice with rejected options to `tree/10_blueprint/decisions.md § Format`. Name the entries a re-entry changed so the screens that read them are re-checked.

**Done when** `tree/APP-DESIGN.md § Checks` holds: every section present, every decided entry citing a rule, heuristic or default id or listed as an exception, every non-`none` object in the object map, every tier-3 attribute behind a peek, popover or named disclosure or an exception, every open question with a stable id and a recommendation, no proposed entry left unsettled, the file written after the last batch, `approved:` set or Open saying why not.
