---
name: skaileup-concept-meta
description: 'Operating on concepts as a whole — quality review, feature extension, reverse engineering, concept evaluation, and multi-product umbrella concepts. Works across all _concept/ artifact types.'
type: domain
building_blocks:
  contracts: 'n/a — to be populated after skill migration.'
  docs: 'n/a — to be populated after skill migration.'
  skills: 'Concept review, feature extension, reverse engineering, evaluation, project overview, subsystem mapping, integration architecture, and project review skills.'
  tools: 'n/a'
stage: alpha
---

# skaileup-concept-meta

Operating on concepts as a whole — quality review, feature extension, reverse engineering, concept evaluation, and multi-product umbrella concepts. Works across all `_concept/` artifact types. Unlike domain-specific skills that produce a single artifact type, concept-meta skills read and reason over the full concept structure.

Skills will be moved into this domain during the architecture reorganization (Phase 5.2+).

## Building Blocks

| Folder    | Purpose                      |
| --------- | ---------------------------- |
| `skills/` | Invocable skills (see below) |

## Skills (target)

| Skill                        | Purpose                                                                            |
| ---------------------------- | ---------------------------------------------------------------------------------- |
| `skaileup-review/`           | Quality review of the full concept — consistency, completeness, and coherence      |
| `skaileup-add-feature/`      | Extends an existing concept with a new feature across all relevant artifact layers |
| `skaileup-reverse-engineer/` | Produces a structured concept from an existing codebase or product                 |
| `skaileup-eval-concept/`     | Evaluates the overall concept against golden principles and iron laws              |
| `skaileup-eval-feature/`     | Evaluates a specific feature spec for quality and feasibility                      |
| `skaileup-eval-product/`     | Evaluates the product concept against market and user fit criteria                 |
| `skaileup-project-overview/` | Generates a high-level project overview across all concept artifacts               |
| `skaileup-subsystem-map/`    | Maps subsystems, modules, and their dependencies across the concept                |
| `skaileup-integration-arch/` | Designs integration architecture between subsystems or external services           |
| `skaileup-project-review/`   | Full project review spanning concept, implementation, and quality artifacts        |

## Conventions

- Skills in this domain operate on a fully or partially populated `_concept/` directory; they do not produce initial artifacts.
- `skaileup-review` and `skaileup-eval-*` skills are non-destructive; they produce evaluation reports, not concept edits.
- `skaileup-add-feature` and `skaileup-reverse-engineer` modify or create `_concept/` content and should be run with an explicit project target.
