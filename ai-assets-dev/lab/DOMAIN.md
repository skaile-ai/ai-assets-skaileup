---
name: lab
description: "Skill-on-skill: validate · judge · improve · learn · compile-validators · compile-bundle"
metadata:
  stage: alpha
  type: domain
---

# lab

Applies skills to skills themselves: validate, judge, improve, learn, compile validators, and compile bundles for the skill collection.

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

- `docs/devlog/SKILL_GRAPH.md` — collection-level view.
- `../skaileup/contracts/` — contracts consumed by narrow validators.
