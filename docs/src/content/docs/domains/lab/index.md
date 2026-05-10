---
title: "lab"
description: "Skill-on-skill: validate · judge · improve · learn · compile-validators · compile-bundle"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`ai-assets/lab/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/ai-assets/lab/DOMAIN.md)
:::


# lab

Applies skills to skills themselves: validate, judge, improve, learn, compile validators, and compile bundles for the skill catalog. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **lab-validate** (`validate/`) — Executes test cases from a skill's test manifest in Docker containers and produces a validation report.
- **lab-judge** (`judge/`) — LLM-as-judge quality scoring for generated code against recipe specifications.
- **lab-improve** (`improve/`) — Drives skill improvement through mutation, testing, and iteration.
- **lab-learn** (`learn/`) — Analyzes skill usage observations and extracts patterns, corrections, and test cases.
- **lab-report** (`report/`) — Generates structured validation and improvement reports with trend analysis.
- **lab-compile-validators** (`compile-validators/`) — Compiles MUST/NEVER/CHECKLIST rules from `SKILL.md` files into fast deterministic Python `validator.py` scripts.
- **lab-compile-bundle** (`compile-bundle/`) — Syncs `bundles/*.bundle.yaml` with `flows/*.flow.yaml` by adding any missing `skill:` entries. Additive only — never removes user-added entries. Run after modifying a flow. CI guard: `scripts/check-bundles.sh`.
- **lab-archive** (`archive/`) — Rolls up old `_feedback/devlog.md` entries into quarterly archive files when entry count reaches 500. Keeps the 200 most recent in the live devlog. Lossless, idempotent, atomic writes.
- **lab-validate-elements-block** (`validate-elements-block/`) — Validates the `elements:` block in screen frontmatter or example fixtures; returns 0 for valid, non-zero with line numbers for invalid.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.


## Skills in this domain

- [lab-archive](./lab-archive/) — Rolls up old _feedback/devlog.md entries into quarterly archive files when entry count reaches 500. Keeps the 200 most recent entries in the
- [lab-compile-bundle](./lab-compile-bundle/) — Syncs bundles/*.bundle.yaml with flows/*.flow.yaml — adds any missing skill: entries to each bundle's requires: list. Additive only: never r
- [lab-compile-validators](./lab-compile-validators/) — Compiles MUST/NEVER/CHECKLIST rules from SKILL.md files into fast, deterministic Python validators. Run after editing or creating a skill to
- [lab-improve](./lab-improve/) — Drive skill improvement through mutation, testing, and iteration
- [lab-judge](./lab-judge/) — LLM-as-judge quality scoring for generated code against recipe specifications
- [lab-learn](./lab-learn/) — Analyze skill usage observations and extract patterns, corrections, and test cases
- [lab-report](./lab-report/) — Generate structured validation and improvement reports with trend analysis
- [lab-validate](./lab-validate/) — Execute test cases from a skill's test manifest in Docker containers and produce a validation report
- [lab-validate-elements-block](./lab-validate-elements-block/) — Use when validating the `elements:` block in screen frontmatter or example fixtures. Returns 0 for valid, non-zero with line numbers for inv
