---
name: skaileup
description: "Use when no flow is running and the next skill is unclear — work arriving from outside the collection, or a `_concept/` tree opened cold. Triggers on 'which skill', 'what do I run next', 'where do I start', 'I have a bug report', 'a feature was requested'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    produces: []
---

# skaileup

The collection's front door: it names the one skill to run next and stops there. It writes no artifact and enters no flow — a router that also did the work would be a second place where a skill's job is defined.

It answers only where nothing else does. **Which flow** a project is sized by, and its project type, belong to `concept-scope` (`tree/01_meta/scope.md`). **What runs after a skill completes** belongs to `tree/README.md § How a skill runs`, which every skill already follows. What is left is the two cold cases below. Paths are the tree's: read `tree/README.md` once per session.

## Steps

1. **Pick the door.** Two cases, told apart by where the work came from:

   | | door |
   |---|---|
   | Work the collection did not create — a request, a bug report, a feature ask | step 2 |
   | A `_concept/` tree opened with nothing running and no skill just finished | step 3 |

   Anything else is not this skill's. A flow is dispatching, or a skill just completed and suggested its own successors; routing it again would give the user two answers from two sources, and no way to tell which is stale.

2. **Intake — triage first, then one entry point.** Tell the user to run `/triage` before choosing; it is user-invoked, so this skill cannot call it. It decides whether the item is worth doing at all, and that judgement is not this collection's to make: skaileup builds what a project has decided to build. Without it, say that intake was not triaged and go on.

   What survives triage enters at exactly one of two skills:

   | the item | enter at |
   |---|---|
   | A capability the product does not have, or one whose behaviour changes | `spec-feature` |
   | A defect in code already built — the spec was right, the code is not | `build-plan` |

   The line between them is whether the specification was wrong. A defect whose fix changes what the product promises is a changed capability, not a bug, and goes to `spec-feature`; sending it to `build-plan` gets the code corrected against a spec that still describes the old promise.

3. **Cold start — read the sizing, then compare each flow node's `produces` with the tree.** In order, stopping at the first that answers:

   1. **No `_concept/01_meta/scope.yaml`** — the project is unsized, so no flow is chosen and no order exists to walk. `concept-scope` is next, and nothing else can be. The file's format is `tree/01_meta/scope.md`.
   2. **A `flow:` in that file** — open `flows/<flow>/<flow>.flow.yaml` and visit its flow nodes along the `type: flow` edges from `entry`, in edge order. For each flow node read its skill's `metadata.artifacts.produces` — that list is the flow node's output, so no skill body needs reading to learn what it leaves behind. A flow node is **done** when every path in its list is present in `_concept/`: a file path exists, a directory path is non-empty, and a path with a placeholder (`<slug>.md`) has at least one match. The first flow node that is not done is the answer. A flow node whose list is empty writes nothing under `_concept/` and cannot be told apart by the tree, so it is skipped. Read the graph and the lists each time, because the flow file holds the sequence and each skill holds its own output, and a router that recites either from memory becomes wrong the first time one moves.
   3. **A `flow:` naming no such file** — say so plainly rather than guessing a neighbour, because a wrong flow re-sizes every skill after it.

4. **Answer with one name and its evidence.** Name a single skill, and the sentence that chose it: which file was absent, which flow node's `produces` path was missing, which door the work came in through. A list of candidates hands the decision back, and the user came here because they did not have it.

**Done when** the user has one skill name and can see what chose it.
