---
name: skaileup-build-supervised
description: Supervised build workflow — human-in-the-loop implementation with git branch management
layer: build
depends_on: [skaileup-discovery, skaileup-experience, skaileup-architecture]
feeds_into: [skaileup-quality]
---

## Purpose

Guided implementation workflow where each phase requires human review before proceeding. Covers the full cycle from git branch preparation through brainstorming, planning, implementation, and branch finalization.

Use this domain when the developer wants structured, step-by-step control over the build process — as opposed to the autonomous `skaileup-build` pipeline.

## Skills

| Skill                             | Path                                      | What It Does                                  | When to Use                                  |
| --------------------------------- | ----------------------------------------- | --------------------------------------------- | -------------------------------------------- |
| `skaileup-supervised`             | `skills/skaileup-supervised/`             | Orchestrator for the supervised build flow    | Starting a supervised implementation session |
| `skaileup-supervised-git-prepare` | `skills/skaileup-supervised-git-prepare/` | Create feature branch, set up worktree        | First step of supervised build               |
| `skaileup-supervised-brainstorm`  | `skills/skaileup-supervised-brainstorm/`  | Explore approaches, identify trade-offs       | After git prep, before planning              |
| `skaileup-supervised-plan`        | `skills/skaileup-supervised-plan/`        | Write implementation plan with checkpoints    | After brainstorming, before coding           |
| `skaileup-supervised-finish`      | `skills/skaileup-supervised-finish/`      | Finalize branch: squash, clean up, prepare PR | After implementation is complete             |

## Notes

- Each skill in this domain is a discrete phase — the orchestrator (`skaileup-supervised`) chains them but pauses for human approval between phases.
- The supervised flow is an alternative to `skaileup-build` (autonomous). Choose supervised when the change is high-risk, cross-cutting, or the developer wants to review each step.
- Git operations use worktrees by default to avoid disrupting the main working directory.
