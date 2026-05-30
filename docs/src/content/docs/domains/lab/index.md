---
title: "lab"
description: "Skill-on-skill: validate · judge · improve · learn · compile-validators · compile-bundle"
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [`ai-assets-dev/lab/DOMAIN.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/ai-assets-dev/lab/DOMAIN.md)
:::


# lab

Applies skills to skills themselves: validate, judge, improve, learn, compile validators, and compile bundles for the skill catalog.

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

## Narrow validators pattern

`lab/validate` is the general skill validator — runs Docker-isolated test cases from a test
manifest schema. **Narrow validators** (e.g. `validate-elements-block`, future
`validate-frontmatter`, `validate-cross-references`) are focused validators for a specific
contract with a bounded, deterministically checkable schema. Both live in `lab/` and follow
the same zero-side-effect, exit-code contract (0 = valid, non-zero = violations with line
numbers).

Create a narrow validator when:
- A contract has a closed schema that can be checked without LLM judgment.
- The check runs in CI or as a pre-commit hook.
- Deterministic pass/fail is more useful than a quality score.

Planned: `validate-frontmatter` (SKILL.md schema compliance), `validate-cross-references`
(READS/REFERENCES paths resolve to real files in the installed skill graph).

## Cross-references

- `docs/devlog/SKILL_GRAPH.md` — catalog-level view.
- `../skaileup/contracts/` — contracts consumed by narrow validators.


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
