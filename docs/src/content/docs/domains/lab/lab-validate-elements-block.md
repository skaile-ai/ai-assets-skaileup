---
title: "lab-validate-elements-block"
description: "Use when validating the `elements:` block in screen frontmatter or example fixtures. Returns 0 for valid, non-zero with line numbers for invalid."
sidebar:
  label: "lab-validate-elements-block"
---

:::note[Skill manifest]
**Name:** `lab-validate-elements-block`
**Stage:** alpha · **Version:** 0.1.0
**Tags:** validation, elements, frontmatter, screens, lab
**Source:** [`ai-assets/lab/validate-elements-block/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/ai-assets/lab/validate-elements-block/SKILL.md)
:::


# Validate Elements Block

ROLE  Validates `elements:` blocks in YAML frontmatter against the schema in `contracts/elements_block.md`.

READS
  tests/elements_block_examples.md         — default fixture set with 3 valid + 3 invalid examples
  ? experience/screens/**/*.md             — screen markdown files passed as CLI argument

WRITES
  stdout                                   — pass/fail report; no files written

REFERENCES
  contracts/elements_block.md              — schema being enforced
  contracts/scripts/validator_lib.py       — Validator class used for report formatting

MUST  report `<path>:<line>: <message>` for every invalid element
MUST  exit 0 iff every example matches its declared `expect:` (fixture mode), or every element passes (screen mode)
NEVER  call an LLM — validation is purely structural

STEP 1: Resolve target
  - If `sys.argv[1]` is supplied, use it; otherwise default to `tests/elements_block_examples.md`.
  - Distinguish fixture mode (file contains `<!-- example: ... -->` sentinels) from screen mode (a single screen markdown file).

STEP 2: Run schema checks
  - In fixture mode: extract each example block via the sentinel comment, parse the YAML, run `_validate_elements(parsed['elements'])`, and assert the verdict matches the declared `expect:`.
  - In screen mode: parse the file's YAML frontmatter; if `elements:` is absent or `[]`, return success (the field is optional); else run `_validate_elements(fm['elements'])`.
  - For each violation, record `(line_offset_in_source_file, message)`.

STEP 3: Print summary and exit
  - Print every violation in `<path>:<line>: <message>` form.
  - Exit 0 if all expectations are satisfied; exit 1 otherwise.

CHECKLIST
  - [ ] Target file resolves and is readable
  - [ ] In fixture mode, all 6 examples are discovered via the sentinel comments
  - [ ] Every violation report includes the source-file line number
  - [ ] Exit code is 0 iff all expectations match

