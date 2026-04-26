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

| Skill | Path | What It Does | When to Use |
|---|---|---|---|
| `skailup-supervised` | `skills/skailup-supervised/` | Orchestrator for the supervised build flow | Starting a supervised implementation session |
| `skailup-supervised-git-prepare` | `skills/skailup-supervised-git-prepare/` | Create feature branch, set up worktree | First step of supervised build |
| `skailup-supervised-brainstorm` | `skills/skailup-supervised-brainstorm/` | Explore approaches, identify trade-offs | After git prep, before planning |
| `skailup-supervised-plan` | `skills/skailup-supervised-plan/` | Write implementation plan with checkpoints | After brainstorming, before coding |
| `skailup-supervised-finish` | `skills/skailup-supervised-finish/` | Finalize branch: squash, clean up, prepare PR | After implementation is complete |

## Notes

- Each skill in this domain is a discrete phase — the orchestrator (`skailup-supervised`) chains them but pauses for human approval between phases.
- The supervised flow is an alternative to `skailup-build` (autonomous). Choose supervised when the change is high-risk, cross-cutting, or the developer wants to review each step.
- Git operations use worktrees by default to avoid disrupting the main working directory.
