---
title: "ops-project-overview"
description: "Use when starting a multi-product meta-concept and the discovery section does not exist yet. Generates discovery/ covering ecosystem brief, unified goals, and competitive positioning."
sidebar:
  label: "ops-project-overview"
---

:::note[Skill manifest]
**Name:** `ops-project-overview`
**Stage:** alpha · **Version:** 0.1.0
**Tags:** meta-concept, discovery, brief, goals, comparable, ecosystem, umbrella
**Source:** [`skaileup/ops/project-overview/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/ops/project-overview/SKILL.md)
:::


# Project Concept: Overview

Generate the discovery layer of a multi-product umbrella concept.

## Prerequisites

Read the meta-concept contract before proceeding:

- `contracts/meta-concept-contract/CONTRACT.md`

## Process

### Step 1: Gather Context

Read the following to understand the ecosystem:

- The shell repo's `CLAUDE.md` (project structure, submodules, conventions)
- Each subsystem's `CLAUDE.md` (what it is, who it serves)
- The `_devlog/DEVLOG.md` (recent evolution, architectural decisions)
- Any existing per-subsystem `_concept/` directories (for vision continuity)

### Step 2: Write brief.md

Produce `_concept/discovery/brief.md` with:

1. **Frontmatter** per the contract schema (`elevator_pitch`, `audience`, `problem`, `hero_flow`, `comparable_products`, `subsystem_count`)
2. **Vision** — what the ecosystem is and why it exists as a multi-product system
3. **Who It Serves** — all user personas across all subsystems (with which subsystem serves each)
4. **What Problem It Solves** — the unified problem statement
5. **Hero Flow** — the most important cross-product journey
6. **Subsystem Summary** — brief table of all subsystems (name, type, audience, one-liner)
7. **Complexity Assessment** — why this is a multi-product ecosystem, not a monolith

### Step 3: Write goals.md

Produce `_concept/discovery/goals.md` with:

1. **Success Criteria** — ecosystem-level (not per-subsystem)
2. **Current Scope** — what's being built now
3. **Constraints** — cross-cutting constraints that affect all subsystems
4. **Timeline** — high-level milestones

### Step 4: Write comparable.md

Produce `_concept/discovery/comparable.md` with:

1. **Comparable ecosystems** — not individual apps, but platforms/ecosystems that solve similar problems
2. **What to borrow / what to avoid** per comparable
3. **Key Insight** — what unique position the ecosystem occupies

### Step 5: Write or reference identity.md

If a brand identity already exists in a subsystem's `_concept/`, write a reference pointer.
If no brand identity exists yet, produce a brief identity document.

## Output Quality

- Each file must have valid YAML frontmatter per the contract
- `last_updated` must be today's date
- Vision and goals must be ecosystem-level, not just aggregated per-subsystem descriptions
- The brief must make sense to someone who has never seen any of the subsystem concepts

## Iron Laws

- Read existing subsystem concepts before writing — do not contradict established vision
- Do not duplicate per-subsystem feature lists in the brief — summarize at capability level
- Ask the user to confirm the elevator pitch before writing the remaining files

