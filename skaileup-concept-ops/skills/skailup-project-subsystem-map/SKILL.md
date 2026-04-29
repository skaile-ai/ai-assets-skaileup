---
name: skaileup-project-subsystem-map
description: 'Generate the 2_subsystems/ section of a meta-concept: index of all subsystems with maturity, audience, tech stack, and references to per-subsystem concepts.'
source: MERGED
version: 1.0.0
keywords: [meta-concept, subsystems, map, inventory, maturity, ecosystem]
user_inputs:
  - key: PROJECT_ROOT
    prompt: 'Where is the shell repo root?'
    required: true
reads_from:
  - contracts/meta-concept-contract/CONTRACT.md
  - '{PROJECT_ROOT}/_concept/discovery/'
  - '{PROJECT_ROOT}/CLAUDE.md'
  - '{PROJECT_ROOT}/**/CLAUDE.md'
  - '{PROJECT_ROOT}/**/_concept/'
writes_to:
  - '{PROJECT_ROOT}/_concept/2_subsystems/index.md'
  - '{PROJECT_ROOT}/_concept/2_subsystems/<subsystem>.md'
---

# Project Concept: Subsystem Map

Generate the subsystem inventory for a multi-product umbrella concept.

## Prerequisites

- `discovery/brief.md` must exist (Iron Law 1)
- Read the meta-concept contract: `contracts/meta-concept-contract/CONTRACT.md`

## Process

### Step 1: Discover Subsystems

Scan the shell repo for independent subsystems. A subsystem is any of:

- A git submodule with its own `CLAUDE.md`
- A top-level directory with its own `package.json` or `CLAUDE.md`
- A content directory that is consumed by other subsystems (e.g., `ai-assets/`)
- A shared resource directory that multiple subsystems depend on (e.g., `theme/`, `docs/`)

For each subsystem, determine:

- **Name** — directory name in the shell repo
- **Repo** — the git remote (if submodule) or "shell" if in-repo
- **Path** — relative path from shell repo root
- **Type** — `library`, `application`, `content`, `website`, or `infrastructure`
- **Audience** — who uses this subsystem
- **Tech stack** — primary technologies
- **Maturity** — `concept | prototype | alpha | beta | production`
- **Has concept** — whether a `_concept/` directory exists
- **Concept ref** — path to the `_concept/` directory (if it exists)

### Step 2: Write index.md

Produce `_concept/2_subsystems/index.md` with:

1. **Frontmatter** — `subsystem_count`, `last_updated`
2. **Overview paragraph** — how the subsystems relate as a whole
3. **Subsystem table** — name, type, maturity, audience, one-liner
4. **Dependency graph** — which subsystems depend on which (text-based, not visual)
5. **Concept coverage** — which subsystems have their own `_concept/` and which don't

### Step 3: Write per-subsystem files

For each subsystem, produce `_concept/2_subsystems/<name>.md` with:

1. **Frontmatter** per the contract schema
2. **Purpose** — what this subsystem does and why it's independent
3. **Key Capabilities** — 3-7 bullet points of what it provides
4. **Consumers** — which other subsystems depend on it
5. **Current State** — what's built, what's planned, known gaps
6. **Concept Reference** — if a detailed `_concept/` exists, point to it

### Grouping Rules

If a subsystem contains nested sub-products (e.g., `forge/` contains `chat/`, `tui/`, `project/`, `concept/`), create:

- One file for the parent (`forge.md`) describing the collection
- Individual files only for sub-products that are significant enough to have their own `_concept/`

Shared infrastructure (`theme/`, `docs/`, `_scripts/`) gets a single collective file
(`shared_infrastructure.md`) unless a component is complex enough to warrant its own.

## Output Quality

- Every subsystem in the shell repo must appear in the index
- Maturity assessments must be honest — do not inflate
- Concept references must be valid paths
- Each subsystem file should be readable standalone (no "see index for context")

## Iron Laws

- Do not describe features that belong in the subsystem's own `_concept/`
- Do not invent capabilities — only document what exists
- Ask the user to confirm the subsystem list before writing individual files
