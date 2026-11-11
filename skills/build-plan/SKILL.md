---
name: build-plan
description: "Use when a frozen feature spec needs breaking into buildable work — opens the spec's parent issue, follows the installed to-tickets skill to cut it into tracer-bullet tickets with blocking edges, and creates the criteria ledger naming each criterion's ticket. Triggers on 'plan this feature', 'break it into tickets', 'what do we build first'."
version: "0.3.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
    - skill:@mattpocock/to-tickets#0.1.0
  artifacts:
    requires:
      - { id: features }
      - { id: screens }
      - { id: techstack }
      - { id: datamodel }
      - { id: standards }
      - { id: interaction-review }
      - { id: grounding-findings }
      - { id: walkthrough }
    produces:
      - { id: acceptance-criteria, path: "_concept/11_build/acceptance-criteria/<featureset>/<feature_slug>.ac.md" }
      - { id: proposals, path: "_concept/proposals/<date>-build-plan-<scope>.yaml" }
  prerequisites:
    files:
      # Hard: the spec's criterion ids are machine-joined into the tickets and the ledger;
      # an id cannot be derived from the code, and `spec-feature` writes it.
      - { path: "_concept/05_features", gate: hard, min_entries: 1 }
      - { path: "_concept/01_meta/walkthrough.yaml", gate: soft }
      - { path: "_concept/07_screens", gate: soft, min_entries: 1 }
      - { path: "_concept/10_blueprint/techstack.md", gate: soft }
      - { path: "_concept/10_blueprint/datamodel", gate: soft }
      - { path: "_concept/02_grounding/standards/index.yml", gate: soft }
      - { path: "_concept/11_build/interaction.sarif", gate: soft }
      - { path: "_concept/02_grounding/findings", gate: soft }
---

# build-plan

Turns one frozen feature spec into the tickets that build it: sub-issues of the spec's parent
issue, each with its blocking edges, in the tracker `docs/agents/issue-tracker.md` names. How
to cut them is the installed `to-tickets` skill; this skill opens the parent, hands it the
concept's inputs, records the parent in the spec and creates the ledger. It writes no code.

## Route

Read `tree/protocol/running.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Check the walk** — `tree/01_meta/walkthrough.md § Writing it` (step 6). From the project root run `python3 <skaileup-skill-dir>/scripts/walkthrough.py gate feature <featureset>/<feature>` for the feature being planned. A non-zero exit stops this skill with the script's message and names `skaileup` to continue the walk; a missing `walkthrough.yaml` is the same stop.
2. **Check no proposal is pending against the spec** — `tree/protocol/delegation.md § Several specs at once` (serial point 2): a pending entry (`tree/proposals/README.md § Format`) targeting the spec, a screen it names, a model entity it names or a glossary term it names stops this skill, naming the owner of that target's node to settle it first.
3. **Ensure the parent issue and record it in the spec** — `tree/05_features/[featureset]/[feature].md § Format` (`tracker`). An existing `tracker.issue` is reused. Otherwise create it once (title the feature name, label `spec`, body the spec path, a two-line summary and the ledger path `_concept/11_build/acceptance-criteria/<featureset>/<feature_slug>.ac.md`) and write `tracker: { issue: <n> }` into the spec at once, changing no other key, so a rerun reuses it.
4. **Read the installed `to-tickets` skill and follow it, with the parent issue as its source.** Its quiz runs and nothing is published before the user approves; tickets become sub-issues with native blocked-by edges and the label `ready-for-agent`. Hand it, as pointers: the spec, the screens its `screens:` list names, `_concept/10_blueprint/`, the standards whose `applies_to` names `build-plan` in `_concept/02_grounding/standards/index.yml`, and `_concept/02_grounding/findings/` for what those leave open. Tell it four rules of this collection:
   - each ticket's acceptance criteria list criterion ids from the spec, never their text, and every id is claimed by exactly one ticket;
   - an open change in `_concept/11_build/interaction.sarif` (`tree/11_build/interaction.md`) whose `files` fall in this feature's code joins the ticket owning those files, and one with `kind: systemic` is a prefactoring ticket the dependent tickets are blocked by;
   - each `pattern` in the spec's `follows:` (`tree/docs/adr/README.md § Patterns`) is one shared module, ticketed and linked per serial point 3 of `tree/protocol/delegation.md § Several specs at once`;
   - a schema ticket is `blocked-by` the schema ticket of every earlier open spec touching the same entity, per serial point 4 of that section.

   A cut that passes the three-test gate (a wide refactor sequenced expand–contract, a shared module placed against the obvious seam) is a decision record in the run's proposal file (`tree/docs/adr/README.md § Writing it`: target `docs/adr/`, anchor `adr:<slug>`). A gap the cut finds is proposed in the same file and its ticket left `blocked-by` nothing new, since the proposal gate holds the build: an entity or field the model lacks (`tree/10_blueprint/datamodel/model.md § Format`, *Proposal entry*), an IN item with no criterion id (`tree/05_features/[featureset]/[feature].md § Format`, *Proposal entry*).
5. **Create the criteria ledger** — `tree/11_build/acceptance-criteria/README.md § Creating the ledger`. Every row untested, one per criterion id the spec carries, each naming its ticket.

**Done when** the parent issue exists with one sub-issue per approved ticket, every criterion id in the spec is claimed by exactly one ticket, the spec carries `tracker.issue`, and the ledger holds one untested row per criterion naming its ticket.
