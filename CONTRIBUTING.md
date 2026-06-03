# Skill Repo Creator Guide

How to build a skill repository that installs correctly with the `skaile` CLI.

---

## How the Installer Works

The `skaile` CLI (via `@skaile/asset-manager`) scans a repository by walking every file
recursively and building a catalog from recognized manifest files:

| Filename | Asset kind |
|---|---|
| `SKILL.md` | `skill` |
| `TEMPLATE.md` | `template` |
| `AGENT.md` | `agent` |
| `agent.yaml` | `agent` |
| `CONTRACT.md` | `contract` |
| `MCP.md` | `mcp-server` |
| `CONNECTOR.md` | `connector` |
| `MOUNT.md` | `mount` |
| `<name>.prompt.md` | `prompt` |
| `<name>.bundle.yaml` | `bundle` |
| `<name>.flow.yaml` | `flow` |

Each manifest file produces exactly one catalog entry. Name collisions (same `kind:name`) are
resolved by picking the alphabetically later source path.

**Deploy targets** (project-local):

| Driver | Skill | Agent | Prompt | Contract | Flow |
|---|---|---|---|---|---|
| `claude-code` | `.claude/skills/` | `.claude/agents/` | `.claude/commands/` | `.claude/contracts/` | `.skaile/flows/` |
| `omp` | `.omp/skills/` | `.omp/agents/` | `.omp/prompts/` | `.omp/contracts/` | `.skaile/flows/` |
| `codex` | `.codex/skills/` | `.codex/agents/` | `.codex/rules/` | `.codex/contracts/` | `.skaile/flows/` |

Local repos (declared with `path:` in `skaile.yaml`) are **symlinked**; remote repos (declared
with `url:`) are **copied**. Symlinks update live; copies only update when content changes.

---

## Repository Layout

```
my-skill-repo/
├── skaile.yaml              # Required: declares this repo for the workspace
├── README.md
├── my-domain/               # Domain directory — groups related skills
│   ├── DOMAIN.md            # Optional: domain manifest
│   ├── skills/
│   │   ├── my-skill/
│   │   │   ├── SKILL.md     # Required: skill manifest + prompt
│   │   │   ├── references/  # Optional: files the skill body can reference
│   │   │   └── scripts/     # Optional: helper scripts
│   │   └── my-other-skill/
│   │       └── SKILL.md
│   └── contracts/
│       └── my-contract/
│           └── CONTRACT.md
└── my-other-domain/
    └── ...
```

The scanner walks the entire tree — directory depth and naming of intermediate directories
(like `skills/`) don't affect discovery. Only the manifest filename matters.

---

## skaile.yaml

Every skill repo needs a `skaile.yaml` at its root to be registered in the workspace:

```yaml
# skaile.yaml — in the skill repo root
repositories:
  my-repo-name:
    url: https://github.com/my-org/my-skill-repo
    branch: main    # optional, defaults to main
```

For local development, the workspace `skaile.yaml` can use `path:` instead:

```yaml
# project skaile.yaml — points to local checkout
repositories:
  my-repo-name:
    path: ../my-skill-repo   # relative to the project root
```

With `path:`, assets are symlinked so edits to SKILL.md are immediately reflected.

---

## SKILL.md Format

```yaml
---
name: my-domain-function          # Required. kebab-case. Domain-relative path, NN_ prefixes stripped, / replaced by -.
description: "Use when [trigger]. Describes what the skill does and when to invoke it."
requires:                          # Optional. Root-level. Array of "kind:name" strings.
  - contract:my-contract           # Explicit kind prefix is required.
  - skill:helper-skill             # Bare string defaults to kind "skill".
metadata:
  version: "1.0.0"                 # Required. Semver.
  tags: [tag1, tag2, tag3]         # Required. At least 2–3 searchable tags.
  stage: alpha | beta | stable     # Required.
  prerequisites:                   # Optional. File and input gates.
    files:
      - path: "_concept/brief.md"
        gate: hard                 # hard = block execution; soft = warn and continue
        description: "Why needed"
    reads:
      - path: "_concept/optional.md"
        description: "Optional context"
    produces:
      - path: "_concept/output.md"
        description: "What this skill creates"
---

# Skill Title

ROLE  One-sentence identity — what this skill is and what it owns.

READS
  _concept/brief.md              — required input description
  ? _concept/optional.md         — optional input (? prefix)

WRITES
  _concept/output.md             — what this skill produces

REFERENCES
  my-domain/contracts/my-contract    — relative to the REPO ROOT, not the skill dir

MUST  do the critical thing
NEVER  do the forbidden thing

STEP 1: First step
  - Action here
  - Another action

CHECKLIST
  - [ ] Output written to correct path
  - [ ] Cross-references valid
```

---

## Naming Conventions

### Skill `name:` field

- **Must be kebab-case**: `a-z`, `0-9`, hyphens only. No consecutive hyphens. Max 64 chars.
- **Must be set explicitly** — the CLI uses the directory name as a fallback only when `name:`
  is absent. Always set it to avoid surprises.
- **Convention: domain-relative path with `/` replaced by `-`, after stripping each
  segment's ordering prefix.** Domain and skill folders carry a two-digit run-order prefix
  `NN_` (and `NN_<letter>_` for pick-one alternatives) so an alphabetical listing reads in
  flow order. The prefix is **ordering metadata only** — strip `NN_` / `NN_<letter>_` from
  each path segment, then join the segments with `-`.

  | Skill directory | `name:` |
  |---|---|
  | `01_concept/01_brief/` | `concept-brief` |
  | `02_design/01_brand-visual/` | `design-brand-visual` |
  | `09_impl-architecture/01_techstack/` | `impl-architecture-techstack` |
  | `13_impl-quality/04_test-unit/` | `impl-quality-test-unit` |
  | `05_mockup-walkthrough/01_c_astro/` | `mockup-walkthrough-astro` |
  | `14_ops/08_review/` | `ops-review` |

  Because the number is stripped, **renumbering a folder never changes a `name:`** — so no
  flow, bundle, or `artifacts.yaml` reference is affected by reordering.

- **Exceptions:**
  - `skaileup/` and `skaileup-build/` (base orchestrator skills in
    `00_skaileup-orchestrator/skills/`) keep short names without the path prefix — doubled
    prefixes (`skaileup-skaileup`) would be awkward for the entry-point skill. The
    orchestrator's `scope/`, `skills/`, `agents/`, `flows/` subdirs are structural and are
    **not** numbered.
  - `template-*` assets in `09_impl-architecture/templates/` use the short directory name
    directly (e.g. `template-sveltekit-minimal`) and are **not** numbered — `tech_stack_skill`
    resolves them by directory name at runtime.
  - `contracts/` and `flows/` are reference/system layers, not pipeline steps — not numbered.

### Directory names

- **Skill directories** are `NN_<last-segment>` (or `NN_<letter>_<last-segment>` for
  alternatives), where the stripped last segment is the final part of the path-based `name:`.
  For `name: concept-brief`, the directory is `01_brief/` inside the `01_concept/` domain.
- **Domain directories** are `NN_<domain>`; the stripped `<domain>` is the `domain` tag on the
  catalog entry. Number domains by their first run position in the flows.
- **Alternatives (pick-one sets)** share one slot number and differ by letter: e.g. the
  walkthrough renderers `01_a_text · 01_b_static-html · 01_c_astro · 01_d_lit · 01_e_framework`.

### Naming pitfall: directory name ≠ frontmatter name

If a skill at `concept/brief/` has `name: brief` (just the directory name), the CLI registers
it as `skill:brief` — not `skill:concept-brief`. Any flow or bundle that references
`skill:concept-brief` will fail to resolve it. Always use the full path-based name.

---

## Dependencies (`requires:`)

### Placement

`requires:` is read from either `metadata.requires` (preferred — follows the agentskills.io
convention of putting skaile extensions under `metadata:`) or root-level `requires:` (legacy,
still supported). Pick one — don't declare both.

```yaml
---
name: my-skill
description: "..."
metadata:
  version: "1.0.0"
  requires:                  # preferred — under metadata
    - contract:my-contract
    - skill:helper-skill
---
```

### Format

Each entry must be a `"kind:name"` string. Supported kinds: `skill`, `contract`, `agent`,
`prompt`, `flow`, `bundle`.

```yaml
requires:
  - skill:helper-skill           # explicit kind prefix
  - contract:iron-laws           # contract dependency
  - my-other-skill               # bare string — defaults to kind "skill"
```

A bare string (no `:` separator) defaults to kind `skill`. For contracts and other non-skill
dependencies, always include the explicit kind prefix.

### What happens when you install

`skaile add skill:my-skill` resolves the full dependency graph transitively:
1. Parses the `requires:` field on `my-skill`
2. Looks up each dependency in the catalog
3. Deploys each dependency to the appropriate target directory

Dependencies must be discoverable (present in a registered repository). If a dependency is
not found in any registered repo, the install fails.

---

## Reference Paths in Skill Bodies

When a skill body uses `REFERENCES`, the paths are resolved **relative to the repository
root at the time the agent reads the skill** — not relative to the skill directory.

```
REFERENCES
  my-domain/contracts/my-contract    # relative to repo root
  shared-domain/references/guide.md  # relative to repo root
```

After install, the skill is deployed to `.claude/skills/my-skill/`. The reference files are
**not** automatically deployed alongside it unless they are declared as `contract` or `skill`
assets with their own `CONTRACT.md` / `SKILL.md` manifest files.

**Best practices for references:**

1. **For shared reference material** (contracts, guides): create a proper `CONTRACT.md` or
   `SKILL.md` manifest so the asset is installable and deployable to `.claude/contracts/`.
   Then declare it in `requires:` so it is auto-installed.

2. **For skill-local reference material** (detail docs, templates): put files in the skill's
   `references/` subdirectory. These are included when the skill directory is copied/symlinked.

3. **Avoid path references to files that aren't part of the deployed skill directory.**
   If you reference `../other-skill/guide.md`, that file will not exist in the install target.

---

## Common Mistakes

### 1. Declaring `requires:` in both places

```yaml
# WRONG — declared at root and under metadata, behavior unspecified
requires:
  - contract:my-contract
metadata:
  requires:
    - skill:other-skill

# CORRECT — pick one place (metadata preferred per agentskills.io)
metadata:
  version: "1.0.0"
  requires:
    - contract:my-contract
    - skill:other-skill
```

### 2. Bare string for non-skill dependencies

```yaml
# WRONG — "my-contract" parsed as skill:my-contract, not contract:my-contract
requires:
  - my-contract

# CORRECT
requires:
  - contract:my-contract
```

### 3. Missing `name:` field (directory fallback)

```yaml
# WRONG — if dir is "my-skill-v2", this registers as "skill:my-skill-v2" not "skill:my-skill"
description: "Use when..."
metadata:
  version: "1.0.0"

# CORRECT
name: my-skill
description: "Use when..."
```

### 4. REFERENCES paths that break after install

```
# WRONG — skaileup-contracts/ doesn't exist in the install target
REFERENCES
  skaileup-contracts/contracts/iron_laws.md

# CORRECT — declare the contract as a dependency and use its installed path
requires:
  - contract:iron-laws
```

### 5. Stale domain path references after a rename

When a domain directory is renamed (e.g. `old-domain/` → `new-domain/`), all `REFERENCES`
and `READS` lines in skill bodies pointing to the old path break. Run a bulk find-and-replace
across all SKILL.md files after any domain rename.

---

## Integrity Checklist

Before publishing a skill repository, verify:

- [ ] `skaile.yaml` declares this repository with `url:` (or `path:` for dev)
- [ ] Every `SKILL.md` has `name:` using the domain-relative path convention with `NN_` prefixes stripped (e.g. `concept-brief`, not `01-concept-01-brief` or `brief`)
- [ ] Every `SKILL.md` has `metadata.version:` (semver), `metadata.tags:` (≥2), `metadata.stage:`
- [ ] `requires:` is declared in exactly one place (`metadata.requires:` preferred, root `requires:` legacy)
- [ ] All `requires:` entries use `kind:name` format for non-skill dependencies
- [ ] All `REFERENCES` paths in skill bodies point to files that will exist after install
      (either within the skill's own directory, or to an installable contract asset)
- [ ] No `REFERENCES` paths point to directory names that have been renamed

---

## Registering a Skill Repo in a Workspace

In the project's `skaile.yaml`:

```yaml
repositories:
  # Remote (install by copying)
  skaileup:
    url: https://github.com/skaile-ai/ai-assets-skaileup
    branch: main

  # Local checkout (install by symlink — live updates)
  my-skills:
    path: ../my-skill-repo
```

Then install specific assets:

```bash
skaile add skill:my-domain-function       # install one skill + its requires
skaile add flow:standard-app              # install a flow + all its dependencies
skaile add --global skill:my-skill        # install globally (~/.claude/skills/)
skaile list                               # show installed assets
skaile search skill my-domain             # search catalog
```

---

## Version Bump Rules

| Bump | When |
|---|---|
| **Major** | Breaking change: renamed inputs, removed `produces` paths, renamed skill |
| **Minor** | New inputs, new outputs, new behavior, added `references/` or `scripts/` |
| **Patch** | Typo fixes, improved wording, updated reference content, tag changes |

Update `metadata.version:` in the same commit as the change. Each domain with versioned
assets should maintain a `CHANGELOG.md` at the domain root.
