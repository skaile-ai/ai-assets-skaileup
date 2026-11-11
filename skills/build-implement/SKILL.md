---
name: build-implement
description: "Use when a feature spec has its tickets and is ready to build — builds the whole spec on one integration branch by following the installed implement-spec skill on the spec's parent issue, one test-first implementer per ticket, and opens a draft PR that closes the parent. Triggers on 'build this feature', 'implement the spec', 'start building', 'land the tickets'."
version: "0.3.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
    - skill:@mattpocock/implement-spec#^0.1
    - skill:@mattpocock/tdd#^0.1
  artifacts:
    requires:
      - { id: features }
      - { id: screens }
      - { id: standards }
      - { id: walkthrough }
    produces:
      - { id: proposals, path: "_concept/proposals/<date>-build-implement-<scope>.yaml" }
  prerequisites:
    files:
      # Hard: the feature spec's `tracker.issue` names the parent issue whose sub-issues are the
      # tickets this skill builds; `build-plan` writes it, and no ticket exists without it.
      - { path: "_concept/05_features", gate: hard, min_entries: 1 }
      - { path: "_concept/01_meta/walkthrough.yaml", gate: soft }
      - { path: "_concept/07_screens", gate: soft, min_entries: 1 }
      - { path: "_concept/02_grounding/standards/index.yml", gate: soft }
      - { path: "_concept/10_blueprint/openapi.yaml", gate: soft }
      - { path: "_concept/10_blueprint/asyncapi.yaml", gate: soft }
---

# build-implement

Builds one feature spec and lands it on its own integration branch. The work is the spec's
tickets: the sub-issues of its parent issue, cut by `build-plan`. How to build them is the
installed `implement-spec` skill, whose implementers call the Skill tool with "tdd"; this
skill gates the run, hands `implement-spec` its inputs and does not restate it. Both have to
be installed: this skill stops and names the missing one rather than improvising a build loop.
It writes nothing under `_concept/` but its proposal file: the issue, its tickets and the
pull requests that close them are the build's record.

Read `tree/protocol/running.md` once per session. This skill runs in the session agent's own
context, never in a delegate: `implement-spec` starts subagents, and a delegate cannot.

## Steps

1. **Check the walk.** `tree/01_meta/walkthrough.md § Writing it` (step 6): from the project
   root run `python3 <skaileup-skill-dir>/scripts/walkthrough.py gate feature <featureset>/<feature>`.
   A non-zero exit stops this skill with the script's message and names `skaileup` to continue
   the walk; a missing `walkthrough.yaml` is the same stop.
2. **Check no proposal is pending against the spec** (serial point 2 of
   `tree/protocol/delegation.md § Several specs at once`). A pending entry in
   `_concept/proposals/` (`tree/proposals/README.md § Format`) targeting this spec, a screen it
   names, a model entity it names or a glossary term it names stops this skill, naming the
   target's owner (the `owner:` of its node) to settle it first: a build against an artifact
   about to change is built against the wrong thing.
3. **Resolve the parent issue.** The spec's frontmatter `tracker.issue`
   (`tree/05_features/[featureset]/[feature].md § Format`) is its number, in the tracker
   `docs/agents/issue-tracker.md` names. No `tracker` key, or
   `gh api repos/{owner}/{repo}/issues/<n>/sub_issues` returns no ticket, stops this skill and
   names `build-plan`: a spec with no tickets has no task graph to build.
4. **Gather the context pointers.** The spec, the screens its `screens:` list names
   (`_concept/07_screens/<screen>.md`), the standards whose `applies_to` names `build-implement`
   in `_concept/02_grounding/standards/index.yml`, and, where they exist,
   `_concept/10_blueprint/openapi.yaml` and `asyncapi.yaml`, whose operations a handler matches
   at the path, method and payload they document. These are pointers for the implementers,
   never pasted content. Confirm with the user, in one batch, the seams `tdd` asks about for
   every ticket on the frontier: an implementer subagent cannot reach the user.
5. **Read the installed `implement-spec` skill and follow it, with the spec's parent issue.**
   Tell it the integration branch is `spec/<featureset>-<feature>`, cut from the branch checked
   out (`build/<app-slug>` where `build-branch` opened one), and that the draft PR from it
   targets that base with `Closes #<parent>` and a `Closes #<ticket>` line per ticket in its
   body; GitHub honours those lines only on the default branch, so against another base the
   parent and tickets are closed with `gh issue close` when the PR merges. Each implementer
   subagent calls the Skill tool with "tdd" for its ticket, with the pointers of step 4. Leave
   out `implement-spec`'s own code review: `quality-review` reviews the integration branch from
   a context that did not write it. Before the PR is marked ready, the integration branch
   rebases on its base, and integration branches merge into that base one at a time (serial
   point 4 of `tree/protocol/delegation.md § Several specs at once`).
6. **Record what the build decided.** A hard-to-reverse choice made while building is a
   decision record in the run's proposal file (`tree/docs/adr/README.md § Writing it`: target
   `docs/adr/`, anchor `adr:<slug>`); other concerns are one comment on the parent issue
   (`tree/protocol/delegation.md § Delegation`). A spec, screen or ledger edited to match the
   code stops being what the code is checked against: the build reads them and writes none.

**Done when** every ticket's work is merged into `spec/<featureset>-<feature>`, the draft PR
from it closes the parent issue and its tickets, and the implementer worktrees are gone.
