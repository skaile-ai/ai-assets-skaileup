---
name: lab
description: "Skill-on-skill: validate · judge · improve · learn · compile-validators · compile-bundle"
metadata:
  stage: alpha
  type: domain
---

# lab

Applies skills to skills themselves: validate, judge, improve, learn, compile validators, and compile bundles for the skill catalog. Phase 1 stub — see SKILL_GRAPH.md §1.

## Skills

- **lab-validate** (`validate/`) — Executes test cases from a skill's test manifest in Docker containers and produces a validation report.
- **lab-judge** (`judge/`) — LLM-as-judge quality scoring for generated code against recipe specifications.
- **lab-improve** (`improve/`) — Drives skill improvement through mutation, testing, and iteration.
- **lab-learn** (`learn/`) — Analyzes skill usage observations and extracts patterns, corrections, and test cases.
- **lab-report** (`report/`) — Generates structured validation and improvement reports with trend analysis.
- **lab-compile-validators** (`compile-validators/`) — Compiles MUST/NEVER/CHECKLIST rules from `SKILL.md` files into fast deterministic Python `validator.py` scripts.
- **lab-compile-bundle** (`compile-bundle/`) — Syncs `bundles/*.bundle.yaml` with `flows/*.flow.yaml` by adding any missing `skill:` entries. Additive only — never removes user-added entries. Run after modifying a flow.
- **lab-validate-elements-block** (`validate-elements-block/`) — Validates the `elements:` block in screen frontmatter or example fixtures; returns 0 for valid, non-zero with line numbers for invalid.

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.
