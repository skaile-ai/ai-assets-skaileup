---
name: experience-interaction
description: "Use when the glossary and the data model exist and the app's interaction rules are not written down yet — where information lives, one editor per object, inline vs modal vs page, saving, messages, popups, buttons, search and command palette — or when a code check has proposed changes to them. Decides the rules per object type with the user and writes APP-DESIGN.md. Triggers on 'write the app design', 'APP-DESIGN.md', 'when do we use a modal', 'UI rules for this app', 'interaction decisions'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: glossary }
      - { id: journeys }
      - { id: datamodel }
    produces:
      - { id: app-design, path: "APP-DESIGN.md" }
  prerequisites:
    files:
      - { path: "_concept/glossary.md", gate: soft }
      - { path: "_concept/10_blueprint/datamodel/", gate: soft }
      - { path: "_concept/04_journeys/stories.yaml", gate: soft }
      - { path: "_concept/02_grounding/findings/interaction.md", gate: soft }
      - { path: "_concept/11_build/interaction.sarif", gate: soft }
      - { path: "APP-DESIGN.md", gate: soft }
---

# experience-interaction

The one writer of `APP-DESIGN.md` at the project root: where each object lives, which surface edits what, how saving, messages, popups and buttons work, how people find and trigger things. It runs after the glossary and the data model and before any screen is specified; it decides and records, and writes no screen, no navigation and no code.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Read the ground** — `tree/APP-DESIGN.md § Reading it`, then step 1 of `tree/APP-DESIGN.md § Writing it`. An existing `APP-DESIGN.md` is intent: its decided entries stay. `_concept/02_grounding/findings/interaction.md` present means a retrofit; `_concept/11_build/interaction.sarif` present means a re-entry, which jumps to item 5.
2. **Classify the objects and decide the global rules** — `tree/APP-DESIGN.md § Patterns` (P1–P17, object classes), steps 2–4 of `tree/APP-DESIGN.md § Writing it`. Object names come from the model and glossary and are never coined here; a concept neither names goes back to `concept-glossary`.
3. **Ask in rounds** — `tree/APP-DESIGN.md § Decision catalogue`, step 5 of `tree/APP-DESIGN.md § Writing it`; the agenda is the catalogue's ⚖ rows first. At most five questions per round, one message each (`tree/README.md § How a skill runs`); without a user the contested calls carry `[open Qn]`.
4. **Write `APP-DESIGN.md` after every round** — `tree/APP-DESIGN.md § Format`, step 6 of `tree/APP-DESIGN.md § Writing it`. Each write adds a Changelog line and sets `updated:`; `approved:` moves only on the user's yes.
5. **Fold in a code check** — `tree/11_build/interaction.md` for the `interaction.sarif` fields, step 7 of `tree/APP-DESIGN.md § Writing it`. The verdict file is `quality-interaction`'s and stays as it is; an exception enters Exceptions only on the user's answer.
6. **Hand off** — step 8 of `tree/APP-DESIGN.md § Writing it`: `spec-feature` applies the OBJ `task → surface` rows and hands back a screen whose surface the floorplan lacks; `experience-shell` derives the navigation and takes MSG, EDIT and MOD from the entries. Say which rows a re-entry changed.

**Done when** `tree/APP-DESIGN.md § Checks` holds: every rule P1–P17 decided with a reason, every non-system type in the floorplan, every contested decision answered or an `[open Qn]` entry with a stand-alone Open row, the file written after the last round, `approved:` set or Open saying why not.
