---
title: "lab-improve"
description: "Drive skill improvement through mutation, testing, and iteration"
sourcePath: "ai-assets-dev/lab/improve/SKILL.md"
sidebar:
  label: "lab-improve"
---

:::note[Skill manifest]
**Name:** `lab-improve`
**Stage:** — · **Version:** —
**Tags:** —
:::


# Lab Improve

You are improving a skill through targeted mutations. For each iteration:

1. **Analyze** the current validation report and any learnings
2. **Pick the highest-priority strategy** from the mutation strategy list
3. **Propose a single, focused change** — never multiple changes at once
4. **Articulate your rationale** clearly in the commit message
5. **Apply the change** to the skill's files (SKILL.md, recipes, examples)

Strategy priorities (highest first):

1. Fix failing test cases
2. Incorporate unaddressed corrections from learnings
3. Update outdated patterns (version drift)
4. Strengthen weak test cases (pass but quality < 70)
5. Add learned recipes from approved candidates
6. Improve prompt clarity
7. Add missing examples

Rules:

- Never modify SKILL.md frontmatter (name, metadata, requires)
- Never delete existing test cases
- Prefer small, targeted changes over rewrites
- Always explain why, not just what

