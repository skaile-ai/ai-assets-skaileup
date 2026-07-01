# Skill Graph Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the `ai-assets-skaileup` catalog from its current 14-domain `skaileup-*` shape into the proposed two-group structure (Concept + Implementation + Meta) with vertical-slice loops, agent-driven scoping, and a three-cluster mockup system with bidirectional sync.

**Architecture:**
- **Phase 1** (mechanical, one session): rename/move domains, scaffold new dirs with stub DOMAIN.md, bulk-update path references. No new behavior. Result: clean substrate, PR-ready.
- **Phase 2** (skill authoring, multi-session): write the ~30 new SKILL.md files plus flows + bundles. Each sub-task gets its own dedicated mini-plan written just-in-time.
- **Phase 3** (engineering, multi-session): annotation overlay + section-diff generator + devlog reader; build the remaining walkthrough renderers; ship `lab/compile-bundle` and `lab/archive`.

**Tech Stack:**
- Markdown + YAML frontmatter (SKILL.md format per `asset_frontmatter` contract)
- Bash + Bun (skaile CLI, bulk file operations)
- Git on the `ai-assets-skaileup` repo (separate from the parent skaile-dev shell)
- Astro/Lit/Next/Nuxt for walkthrough renderers (Phase 3)

**Source documents** (read these before starting any task):
- `SKILL_GRAPH.md` — the target organization, tier flows, workspace zones
- `REFACTOR_MOCKUP.md` — the mockup three-cluster split + bidirectional sync design
- `CONTRIBUTING.md` — the per-skill authoring rules (naming, requires placement, etc.)
- `skaileup-contracts/contracts/asset_frontmatter.md` — frontmatter schema
- `skaileup-contracts/contracts/skill_grammar.md` — SKILL.md DSL
- This plan

---

## Pre-flight (run once, at the start of every session that picks this up)

- [ ] **Step 0.1: Verify working directory**

```bash
cd /mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup
pwd
```

Expected: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`

- [ ] **Step 0.2: Verify clean working tree**

```bash
git status --short
```

Expected: empty output (or only the four untracked workspace files: `.gitignore`, `.skaile/`, `skaile.yaml`, plus any in-progress work).

- [ ] **Step 0.3: Verify on the right branch**

```bash
git branch --show-current
```

Expected: `refactor/skill-graph` (Phase 1 will create this if missing).

- [ ] **Step 0.4: Read the source documents**

Read in order: `SKILL_GRAPH.md`, `REFACTOR_MOCKUP.md`, `CONTRIBUTING.md`. Skim `skaileup-contracts/contracts/asset_frontmatter.md` (or `contracts/asset_frontmatter.md` after migration) for frontmatter rules.

- [ ] **Step 0.5: Verify required tooling is available**

```bash
for cmd in git bun gh sed grep find xargs; do
  command -v $cmd >/dev/null && echo "OK $cmd" || echo "MISSING $cmd"
done
```

Expected: 7 OK lines. If `gh` is missing, the final PR step (1.15.6) needs manual PR creation.

---

## Naming convention (used throughout the plan)

Every skill's `name:` follows the pattern of its **path under the repo root** with `/` replaced by `-`:

| Path | `name:` |
|---|---|
| `concept/brief/SKILL.md` | `concept-brief` |
| `concept/grounding/onboard/SKILL.md` | `concept-grounding-onboard` |
| `design/brand-visual/SKILL.md` | `design-brand-visual` |
| `experience/screens/SKILL.md` | `experience-screens` |
| `impl-architecture/techstack/SKILL.md` | `impl-architecture-techstack` |
| `impl-architecture/templates/template-postxl/SKILL.md` | `impl-architecture-templates-template-postxl` (or shortened to `template-postxl` — see Task 1.11) |
| `component-mockup/storybook/SKILL.md` | `component-mockup-storybook` |

This rule is mechanical: skill author runs `dirname $(realpath SKILL.md) | sed 's|/|-|g'` from repo root. The migration tables in subsequent tasks all follow this rule.

**Exception — base orchestrator skills:** the skills inside `skaileup/skills/` keep their short names (`skaileup`, `skaileup-build`) instead of the path-based form (`skaileup-skills-skaileup`, `skaileup-skills-skaileup-build`). The base orchestrator is the catalog's entry point; doubled prefixes would be awkward. Only `skaileup/scope/scope-project/` follows path-based naming (`name: skaileup-scope-scope-project` — note no shortening for sub-clusters of the base).

---

# PHASE 1 — Mechanical Reorganization

**Goal:** catalog directory structure matches the proposal in `SKILL_GRAPH.md`; new domain dirs exist as scaffolded shells with stub `DOMAIN.md`; every existing skill is moved to its new home; every internal path reference is updated; SKILL_GRAPH/CONTRIBUTING/README cross-references are correct. **No new skill content.**

**Scope:** ~14 task groups, ~70-140 verification steps, ~1 day of focused work.

**Branch policy:** all work commits to `refactor/skill-graph`; commit boundaries match task boundaries; no force-push.

**Result at end of Phase 1:** the catalog is structurally the target shape but the new skills don't exist yet. The old skills work exactly as before — this phase changes packaging, not semantics.

---

## Per-task ancillary-content rule (applies to Tasks 1.3 – 1.12)

Every existing `skaileup-*` source domain may contain, in addition to its `skills/`:
- `DOMAIN.md` — disposition decided per task (move, merge into new DOMAIN.md, or discard)
- `agents/` — move to corresponding new domain's `agents/` subdir
- `contracts/` — either move to the corresponding new domain's `contracts/` OR promote to top-level `contracts/` if shared
- `CHANGELOG.md` — move to corresponding new domain root
- `docs/` — move to corresponding new domain's `docs/`
- `flows/` — move to corresponding new domain's `flows/`
- `<name>.bundle.yaml` (at domain root) — `git rm` (Phase 2 Task 2H rebuilds bundles from flows)

**Each Task in 1.3–1.12 MUST:**
1. After `git mv`-ing the `skills/`, list the source domain root: `ls -la skaileup-X/`
2. Per the bullets above, move or remove every remaining file/dir
3. Run `find skaileup-X -type f` and verify empty before final `rm -rf`
4. Only then commit

If a task's individual steps below don't enumerate every ancillary item, the rule above takes precedence. Do not silently `rm -rf` content that hasn't been deliberately handled.

---

## Task 1.0: Branch + worktree setup

**Files:**
- (no file changes)

- [ ] **Step 1.0.1: Create the refactor branch (if missing)**

```bash
git rev-parse --verify refactor/skill-graph >/dev/null 2>&1 || git checkout -b refactor/skill-graph
git checkout refactor/skill-graph
git branch --show-current
```

Expected: `refactor/skill-graph`

- [ ] **Step 1.0.2: Confirm parent skaile-dev shell is on a coherent ref**

```bash
git -C /mnt/localvault/workBench/SKAILE/skaile-dev-matthias rev-parse HEAD 2>/dev/null
```

Expected: a SHA (or "fatal: not a git repository" if the shell is not a repo — this is fine, the shell isn't versioned).

- [ ] **Step 1.0.3: Snapshot the current skill count for later verification**

```bash
find . -name "SKILL.md" -not -path "*/.skaile/*" | wc -l > /tmp/skill-count-before
find . -name "CONTRACT.md" -not -path "*/.skaile/*" | wc -l >> /tmp/skill-count-before
find . -name "DOMAIN.md" -not -path "*/.skaile/*" | wc -l >> /tmp/skill-count-before
cat /tmp/skill-count-before
```

Record the three numbers. Phase 1 verification (Task 1.13) will require the same counts (no skills lost in migration).

---

## Task 1.1: Update .gitignore for new workspace zones

**Files:**
- Create: `.gitignore` (currently untracked; commit it as part of this task)

- [ ] **Step 1.1.1: Read existing .gitignore**

```bash
cat .gitignore
```

Expected:
```
node_modules/
.skaile/sessions/
*.log
.env
.env.local
```

- [ ] **Step 1.1.2: Append new zones**

Edit `.gitignore` to add at the bottom:

```
# Slice-loop scratch (deleted on commit)
_slice/

# Per-developer feedback evidence (committed: applied/, devlog.md only)
_feedback/sessions/
_feedback/patches/
```

- [ ] **Step 1.1.3: Verify**

```bash
grep -q "^_slice/$" .gitignore && grep -q "^_feedback/sessions/$" .gitignore && echo OK
```

Expected: `OK`

- [ ] **Step 1.1.4: Stage + commit (along with the other untracked workspace files only if intentional)**

```bash
git add .gitignore
git commit -m "$(cat <<'EOF'
chore: ignore _slice/ scratch and _feedback/ private zones

Per the SKILL_GRAPH workspace-zones design, _slice/ holds per-slice
scratch (deleted on commit) and _feedback/{sessions,patches} hold
private per-developer evidence. The committed parts (_feedback/applied/
and _feedback/devlog.md) are explicit allow-listed by skill authors.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
git log -1 --oneline
```

Expected: one new commit "chore: ignore _slice/ scratch ..."

---

## Task 1.2: Create new top-level domain skeleton

**Files:**
- Create: `concept/DOMAIN.md`, `design/DOMAIN.md`, `product-spec/DOMAIN.md`, `experience/DOMAIN.md`, `concept-slice/DOMAIN.md`
- Create: `component-mockup/DOMAIN.md`, `walkthrough-mockup/DOMAIN.md`, `mockup-feedback/DOMAIN.md`
- Create: `impl-architecture/DOMAIN.md`, `impl-plan/DOMAIN.md`, `impl-slice/DOMAIN.md`, `impl-build/DOMAIN.md`, `impl-quality/DOMAIN.md`
- Create: `ops/DOMAIN.md`, `lab/DOMAIN.md`, `contracts/DOMAIN.md`
- Each new domain needs `skills/` empty subdir (created on first SKILL.md move)

- [ ] **Step 1.2.1: Create domain directories**

```bash
for d in concept design product-spec experience concept-slice \
         component-mockup walkthrough-mockup mockup-feedback \
         impl-architecture impl-plan impl-slice impl-build impl-quality \
         ops lab contracts; do
  mkdir -p "$d/skills"
done
ls -d concept design product-spec experience concept-slice \
       component-mockup walkthrough-mockup mockup-feedback \
       impl-architecture impl-plan impl-slice impl-build impl-quality \
       ops lab contracts
```

Expected: all 16 directories listed.

- [ ] **Step 1.2.2: Generate stub DOMAIN.md for each new domain**

For each domain, create a stub `DOMAIN.md` with this template (substitute `{NAME}` and `{DESCRIPTION}`):

```yaml
---
name: {NAME}
description: "{DESCRIPTION}"
metadata:
  stage: alpha
  type: domain
---

# {Title}

{1-2 paragraphs of purpose. See SKILL_GRAPH.md for context.}

## Skills

(Populated as skills are migrated/authored.)

## Cross-references

- See `../SKILL_GRAPH.md` for the catalog-level view.
- See `../REFACTOR_MOCKUP.md` if this domain is a mockup cluster.
```

Use the descriptions from `SKILL_GRAPH.md` § 1 verbatim. For example:
- `concept`: "brief · goals · comparable"
- `design`: "brand-identity · tokens · voice · inspiration"

Write all 16 stubs in this step.

- [ ] **Step 1.2.3: Verify stubs are well-formed**

```bash
for f in concept design product-spec experience concept-slice \
         component-mockup walkthrough-mockup mockup-feedback \
         impl-architecture impl-plan impl-slice impl-build impl-quality \
         ops lab contracts; do
  test -f "$f/DOMAIN.md" || echo "MISSING: $f/DOMAIN.md"
  grep -q "^name: $f$" "$f/DOMAIN.md" || echo "BAD NAME: $f/DOMAIN.md"
done
echo "done"
```

Expected: just `done` — no MISSING or BAD NAME lines.

- [ ] **Step 1.2.4: Commit**

```bash
git add concept design product-spec experience concept-slice \
        component-mockup walkthrough-mockup mockup-feedback \
        impl-architecture impl-plan impl-slice impl-build impl-quality \
        ops lab contracts
git commit -m "feat: scaffold new top-level domains per SKILL_GRAPH proposal

Adds 16 empty domain directories with stub DOMAIN.md files. No skill
content yet. Subsequent commits in this branch migrate existing skaileup-*
skills into these new homes per the migration map in SKILL_GRAPH.md § 9.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

Expected: commit succeeds, working tree clean.

---

## Task 1.2b: Reconcile `skaileup/` base orchestrator domain

The existing `skaileup/` base domain (orchestrator + base agents) **stays at the
top level** but its inner skill/agent dirs need (a) the `skailup-` typo prefix
fixed and (b) frontmatter `name:` updated to the new naming convention. Plus the
new `skaileup/scope/` cluster gets scaffolded for Phase 2's `scope-project` skill.

**Files (likely):**
- `skaileup/skills/skailup/` → `skaileup/skills/skaileup/` (typo fix)
- `skaileup/skills/skailup-build/` → `skaileup/skills/skaileup-build/` (typo fix)
- `skaileup/agents/skailup/` → `skaileup/agents/skaileup/`
- `skaileup/agents/skailup-conceptualize/` → `skaileup/agents/skaileup-conceptualize/`
- New: `skaileup/scope/DOMAIN.md` (stub) and `skaileup/scope/scope-project/.placeholder`

- [ ] **Step 1.2b.1: Inventory current contents**

```bash
ls skaileup/
ls skaileup/skills/ 2>/dev/null
ls skaileup/agents/ 2>/dev/null
ls skaileup/flows/ 2>/dev/null
ls skaileup/contracts/ 2>/dev/null
```

Capture the actual subdir names — some may differ from the assumed list above.

- [ ] **Step 1.2b.2: Rename `skailup-*` → `skaileup-*` (typo fix) under skills/ and agents/**

```bash
for dir in skaileup/skills/skailup* skaileup/agents/skailup*; do
  if [ -d "$dir" ]; then
    new=$(echo "$dir" | sed 's|skailup|skaileup|')
    git mv "$dir" "$new"
  fi
done
ls skaileup/skills/ skaileup/agents/ 2>/dev/null
```

- [ ] **Step 1.2b.3: Update frontmatter `name:` to drop `skailup-` typo**

Per the base-orchestrator naming exception (top of plan):
- `name: skailup` → `name: skaileup`
- `name: skailup-build` → `name: skaileup-build`

(Short names — these are the catalog entry-point skills, exempt from path-based naming.)

For agents in `skaileup/agents/`:
- `name: skailup` → `name: skaileup` (the base agent)
- `name: skailup-conceptualize` → `name: skaileup-conceptualize`

- [ ] **Step 1.2b.4: Scaffold `skaileup/scope/`**

```bash
mkdir -p skaileup/scope/scope-project
cat > skaileup/scope/DOMAIN.md <<'EOF'
---
name: skaileup-scope
description: "Project-size scoping — interviews user, picks tier, drives flow selection."
metadata:
  stage: alpha
  type: domain
---

# skaileup/scope

Phase 2 will author `scope-project` here. See `docs/devlog/2026-05-07-skill-graph-migration.md` Task 2A.
EOF
touch skaileup/scope/scope-project/.placeholder
```

- [ ] **Step 1.2b.5: Verify**

```bash
test -f skaileup/scope/DOMAIN.md && echo "scope DOMAIN.md OK"
ls skaileup/skills/ skaileup/agents/ 2>/dev/null | grep -c skailup
```

Expected: `scope DOMAIN.md OK` and grep count `0` (no remaining `skailup` typo dirs).

- [ ] **Step 1.2b.6: Commit**

```bash
git add -A
git commit -m "refactor: reconcile skaileup/ base domain — fix typos, scaffold scope/

Renamed skailup-* → skaileup-* under skills/ and agents/ (typo fix).
Updated name: frontmatter accordingly. Scaffolded skaileup/scope/ for
the Phase 2 scope-project skill.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 1.3: Migrate `skaileup-grounding` → `concept/grounding/`

**Source:** `skaileup-grounding/skills/{onboard, research, seeds}/`
**Target:** `concept/grounding/{onboard, research, seeds}/` (kept as a sub-cluster of concept/)

**Files:**
- Move: `skaileup-grounding/DOMAIN.md` → `concept/grounding/DOMAIN.md`
- Move: `skaileup-grounding/skills/skailup-grounding-onboard/` → `concept/grounding/onboard/`
- Move: `skaileup-grounding/skills/skailup-grounding-research/` → `concept/grounding/research/`
- Move: `skaileup-grounding/skills/skailup-grounding-seeds/` → `concept/grounding/seeds/`
- Move: `skaileup-grounding/contracts/` → preserve under new home or migrate to top-level `contracts/`
- Update: `name:` frontmatter in each migrated SKILL.md (drop `skailup-` prefix; e.g. `skailup-grounding-onboard` → `concept-grounding-onboard`)

- [ ] **Step 1.3.1: Move directory structure with `git mv`**

```bash
mkdir -p concept/grounding
git mv skaileup-grounding/DOMAIN.md concept/grounding/DOMAIN.md
git mv skaileup-grounding/skills/skailup-grounding-onboard concept/grounding/onboard
git mv skaileup-grounding/skills/skailup-grounding-research concept/grounding/research
git mv skaileup-grounding/skills/skailup-grounding-seeds concept/grounding/seeds
ls concept/grounding/
```

Expected: `DOMAIN.md  onboard  research  seeds`

- [ ] **Step 1.3.2: Move grounding's contracts dir if present**

```bash
if [ -d skaileup-grounding/contracts ]; then
  git mv skaileup-grounding/contracts concept/grounding/contracts
fi
```

- [ ] **Step 1.3.3: Update name: frontmatter for the three skills**

For each SKILL.md, change the `name:` field. The new naming convention drops the `skailup-` prefix and uses the new domain hierarchy:

| Old `name:` | New `name:` |
|---|---|
| `skailup-grounding-onboard` | `concept-grounding-onboard` |
| `skailup-grounding-research` | `concept-grounding-research` |
| `skailup-grounding-seeds` | `concept-grounding-seeds` |

Use the Edit tool to change `name:` in each file. Keep all other frontmatter unchanged.

- [ ] **Step 1.3.4: Verify renames**

```bash
for skill in onboard research seeds; do
  grep -q "^name: concept-grounding-$skill$" concept/grounding/$skill/SKILL.md \
    && echo "OK $skill" || echo "FAIL $skill"
done
```

Expected: three `OK` lines.

- [ ] **Step 1.3.5: Remove now-empty source dir**

```bash
rmdir skaileup-grounding/skills 2>/dev/null
rmdir skaileup-grounding 2>/dev/null
test ! -d skaileup-grounding && echo "removed"
```

Expected: `removed`

- [ ] **Step 1.3.6: Commit**

```bash
git add -A
git commit -m "refactor: migrate skaileup-grounding → concept/grounding/

Moved all three skills (onboard, research, seeds) under concept/ as a
sub-cluster. Renamed name: frontmatter from skailup-grounding-* to
concept-grounding-*. Path references updated in Task 1.13.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 1.4: Migrate `skaileup-discovery` (split into `concept/` and `design/`)

**Migration:**
- `skaileup-discovery/skills/skailup-discovery-brief/` → `concept/brief/`
- `skaileup-discovery/skills/skailup-discovery-brand-visual/` → `design/brand-visual/`
- `skaileup-discovery/skills/skailup-discovery-brand-voice/` → `design/brand-voice/`
- `skaileup-discovery/DOMAIN.md` → discard (purpose is split between concept and design)

**Name renames:**
| Old | New |
|---|---|
| `skailup-discovery-brief` | `concept-brief` |
| `skailup-discovery-brand-visual` | `design-brand-visual` |
| `skailup-discovery-brand-voice` | `design-brand-voice` |

- [ ] **Step 1.4.1: Move with git mv**

```bash
git mv skaileup-discovery/skills/skailup-discovery-brief concept/brief
git mv skaileup-discovery/skills/skailup-discovery-brand-visual design/brand-visual
git mv skaileup-discovery/skills/skailup-discovery-brand-voice design/brand-voice
```

- [ ] **Step 1.4.2: Update name: frontmatter for all three**

Use Edit tool. Replace each `name:` per the rename table above. Keep description and metadata unchanged.

- [ ] **Step 1.4.3: Decide what happens to skaileup-discovery/DOMAIN.md**

Read the contents:

```bash
cat skaileup-discovery/DOMAIN.md
```

Most of its content describes work now split between `concept/` and `design/`. Either:
- Distribute the relevant paragraphs into `concept/DOMAIN.md` and `design/DOMAIN.md` stubs, OR
- Discard if the stubs already cover the content.

Pick one. Document the decision in the commit message.

- [ ] **Step 1.4.4: Remove empty source dir**

```bash
rm -rf skaileup-discovery
test ! -d skaileup-discovery && echo "removed"
```

- [ ] **Step 1.4.5: Verify**

```bash
test -f concept/brief/SKILL.md && grep -q "^name: concept-brief$" concept/brief/SKILL.md && echo "concept-brief OK"
test -f design/brand-visual/SKILL.md && grep -q "^name: design-brand-visual$" design/brand-visual/SKILL.md && echo "design-brand-visual OK"
test -f design/brand-voice/SKILL.md && grep -q "^name: design-brand-voice$" design/brand-voice/SKILL.md && echo "design-brand-voice OK"
```

Expected: three OK lines.

- [ ] **Step 1.4.6: Commit**

```bash
git add -A
git commit -m "refactor: split skaileup-discovery → concept/brief + design/brand-{visual,voice}

[document the DOMAIN.md disposition decision in the body]

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 1.5: Migrate `skaileup-experience` (split into `product-spec/` + `experience/`)

**Migration:**
- `skaileup-experience/skills/skailup-experience-features/` → `product-spec/features/`
- `skaileup-experience/skills/skailup-experience-journeys/` → `experience/journeys/`
- `skaileup-experience/skills/skailup-experience-behaviors/` → `experience/behaviors/`
- `skaileup-experience/skills/skailup-experience-screens/` → `experience/screens/`
- `skaileup-experience/skills/skailup-experience-screens-technical/` → `experience/screens-technical/`
- `skaileup-experience/skills/skailup-experience-components/` → `experience/components/`

**Name renames:** drop `skailup-experience-` prefix, prepend with new domain (`product-spec-` or `experience-`):

| Old | New |
|---|---|
| `skailup-experience-features` | `product-spec-features` |
| `skailup-experience-journeys` | `experience-journeys` |
| `skailup-experience-behaviors` | `experience-behaviors` |
| `skailup-experience-screens` | `experience-screens` |
| `skailup-experience-screens-technical` | `experience-screens-technical` |
| `skailup-experience-components` | `experience-components` |

- [ ] **Step 1.5.1: Move directories**

```bash
git mv skaileup-experience/skills/skailup-experience-features product-spec/features
git mv skaileup-experience/skills/skailup-experience-journeys experience/journeys
git mv skaileup-experience/skills/skailup-experience-behaviors experience/behaviors
git mv skaileup-experience/skills/skailup-experience-screens experience/screens
git mv skaileup-experience/skills/skailup-experience-screens-technical experience/screens-technical
git mv skaileup-experience/skills/skailup-experience-components experience/components
```

- [ ] **Step 1.5.2: Update name: frontmatter (six files)**

Use Edit per the rename table.

- [ ] **Step 1.5.3: Verify**

```bash
for path_n in "product-spec/features:product-spec-features" \
              "experience/journeys:experience-journeys" \
              "experience/behaviors:experience-behaviors" \
              "experience/screens:experience-screens" \
              "experience/screens-technical:experience-screens-technical" \
              "experience/components:experience-components"; do
  path="${path_n%%:*}"
  name="${path_n##*:}"
  grep -q "^name: $name$" "$path/SKILL.md" && echo "OK $name" || echo "FAIL $name"
done
```

Expected: six OK lines.

- [ ] **Step 1.5.4: Clean up source dir + commit**

```bash
rm -rf skaileup-experience
git add -A
git commit -m "refactor: split skaileup-experience → product-spec + experience

features/ moved to product-spec/ (functional spec is product concern).
journeys, behaviors, screens, components moved to experience/ (UX concern).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 1.6: Migrate `skaileup-architecture` + `skaileup-datamodel` → `impl-architecture/`

**Migration:**
- `skaileup-architecture/skills/skailup-architecture-techstack/` → `impl-architecture/techstack/`
- `skaileup-architecture/skills/skailup-architecture-system/` → `impl-architecture/system/`
- `skaileup-datamodel/skills/skailup-datamodel/` → `impl-architecture/datamodel/`

**Name renames:**
| Old | New |
|---|---|
| `skailup-architecture-techstack` | `impl-architecture-techstack` |
| `skailup-architecture-system` | `impl-architecture-system` |
| `skailup-datamodel` | `impl-architecture-datamodel` |

- [ ] **Step 1.6.1: Move**

```bash
git mv skaileup-architecture/skills/skailup-architecture-techstack impl-architecture/techstack
git mv skaileup-architecture/skills/skailup-architecture-system impl-architecture/system
git mv skaileup-datamodel/skills/skailup-datamodel impl-architecture/datamodel
```

- [ ] **Step 1.6.2: Update name: frontmatter (three skills)**
- [ ] **Step 1.6.3: Verify** (mirror Step 1.5.3)
- [ ] **Step 1.6.4: Cleanup + commit**

```bash
rm -rf skaileup-architecture skaileup-datamodel
git add -A
git commit -m "refactor: merge skaileup-architecture + skaileup-datamodel → impl-architecture

datamodel is an implementation-architecture concern (drives migrations and
schema), not a separate top-level domain. Consolidated under impl-architecture/.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 1.7: Migrate mockup domains → three new clusters

**Migration:**
- `skaileup-concept-mockup/skills/skailup-concept-mockup/` → `walkthrough-mockup/text/`
- `skaileup-concept-storybook/skills/*` → consolidate into `component-mockup/storybook/`
  (Six existing sub-skills: `setup`, `types`, `components`, `pages`, `journeys`, plus the orchestrator. Phase 1 KEEPS them as separate skills but renames them; Phase 2 may consolidate.)

**Name renames:**
| Old | New |
|---|---|
| `skailup-concept-mockup` | `walkthrough-mockup-text` |
| `skailup-concept-storybook` | `component-mockup-storybook` |
| `skailup-concept-storybook-setup` | `component-mockup-storybook-setup` |
| `skailup-concept-storybook-types` | `component-mockup-storybook-types` |
| `skailup-concept-storybook-components` | `component-mockup-storybook-components` |
| `skailup-concept-storybook-pages` | `component-mockup-storybook-pages` |
| `skailup-concept-storybook-journeys` | `component-mockup-storybook-journeys` |

- [ ] **Step 1.7.1: Move concept-mockup**

```bash
git mv skaileup-concept-mockup/skills/skailup-concept-mockup walkthrough-mockup/text
rm -rf skaileup-concept-mockup
```

- [ ] **Step 1.7.2: Move concept-storybook (preserve sub-skills)**

```bash
mkdir -p component-mockup/storybook
git mv skaileup-concept-storybook/skills/skailup-concept-storybook component-mockup/storybook/orchestrator
# Move each sub-skill
for sub in setup types components pages journeys; do
  if [ -d skaileup-concept-storybook/skills/skailup-concept-storybook-$sub ]; then
    git mv skaileup-concept-storybook/skills/skailup-concept-storybook-$sub component-mockup/storybook/$sub
  fi
done
rm -rf skaileup-concept-storybook
```

- [ ] **Step 1.7.3: Update name: frontmatter** (use the rename table)

- [ ] **Step 1.7.4: Verify**

```bash
test -f walkthrough-mockup/text/SKILL.md && echo "text OK"
test -f component-mockup/storybook/orchestrator/SKILL.md && echo "storybook orch OK"
for sub in setup types components pages journeys; do
  if [ -f component-mockup/storybook/$sub/SKILL.md ]; then echo "$sub OK"; fi
done
```

- [ ] **Step 1.7.5: Commit**

```bash
git add -A
git commit -m "refactor: migrate mockup domains to three-cluster shape (Phase 1)

skailup-concept-mockup → walkthrough-mockup/text (renamed only)
skailup-concept-storybook → component-mockup/storybook/{orchestrator,setup,types,...}

Phase 2 will consolidate the storybook sub-skills if appropriate, and add
component-mockup-isolated-html, walkthrough-mockup-{static-html,lit,astro,framework}
and the entire mockup-feedback cluster. Phase 1 preserves existing structure.

See REFACTOR_MOCKUP.md for the full design.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 1.8: Migrate `skaileup-concept-ops` → `ops/`

**Migration:** every skill under `skaileup-concept-ops/skills/` moves to `ops/<skill>/`.

**Name renames:** drop `skailup-` prefix; the rest stays (most are already short like `skailup-review`, `skailup-add-feature`).

| Old | New |
|---|---|
| `skailup-review` | `ops-review` |
| `skailup-eval-concept` | `ops-eval-concept` |
| `skailup-eval-feature` | `ops-eval-feature` |
| `skailup-eval-product` | `ops-eval-product` |
| `skailup-add-feature` | `ops-add-feature` |
| `skailup-concept-ops-sync` | `ops-sync` |
| `skailup-reverse-engineer` | `ops-reverse-engineer` |
| `skailup-project-overview` | `ops-project-overview` |
| `skailup-project-subsystem-map` | `ops-project-subsystem-map` |
| `skailup-project-integration` | `ops-project-integration` |
| `skailup-project-review` | `ops-project-review` |

- [ ] **Step 1.8.1: List existing concept-ops skills**

```bash
ls skaileup-concept-ops/skills/
```

Use this output to validate the rename table — if there are skills not in the table, add rows.

- [ ] **Step 1.8.2: Move all skills**

```bash
for skill in $(ls skaileup-concept-ops/skills/); do
  newname="${skill#skailup-}"  # strip "skailup-" prefix
  case "$skill" in
    skailup-concept-ops-sync) newname="sync" ;;
  esac
  git mv "skaileup-concept-ops/skills/$skill" "ops/$newname"
done
ls ops/
```

- [ ] **Step 1.8.3: Move ops contracts (if any)**

```bash
if [ -d skaileup-concept-ops/contracts ]; then
  git mv skaileup-concept-ops/contracts ops/contracts
fi
```

- [ ] **Step 1.8.4: Update name: frontmatter per rename table**
- [ ] **Step 1.8.5: Cleanup + commit**

```bash
rm -rf skaileup-concept-ops
git add -A
git commit -m "refactor: migrate skaileup-concept-ops → ops/ (cross-cutting domain)

ops/ now holds all cross-cutting meta-operations: review, sync, eval-*,
add-feature, reverse-engineer, project-*. These run against any concept
artifact, not as part of the linear pipeline.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 1.9: Migrate `skaileup-build` → `impl-build/` + `impl-slice/` (stubs) + `impl-plan/` (stubs)

This is the most complex migration. The current `skaileup-build/` has:
- One-time skills: `scaffold`, `foundation`, `infrastructure`, `migrate`, `seed`, `generate`, `docs` → to `impl-build/`
- The slice-loop skill: `feature` (and sub-skill `feature-page`) → split to `impl-slice/implement` (stub for now); rest of slice loop (test, recap, refactor, commit) NOT created in Phase 1
- Build contracts: `implementation-contract`, `subagent_dispatch` → `impl-build/contracts/`
- Build flows: `superpowers.flow.yaml` → `impl-build/flows/`

**Phase 1 ONLY does the moves + renames. New skills (recap, refactor, commit) are Phase 2.**

| Old | New |
|---|---|
| `skailup-build-scaffold` | `impl-build-scaffold` |
| `skailup-build-foundation` | `impl-build-foundation` |
| `skailup-build-infrastructure` | `impl-build-infrastructure` |
| `skailup-build-migrate` | `impl-build-migrate` |
| `skailup-build-seed` | `impl-build-seed` |
| `skailup-build-generate` | `impl-build-generate` |
| `skailup-build-docs` | `impl-build-docs` |
| `skailup-build-feature` | `impl-slice-implement` |
| `skailup-build-feature-page` | (merged into `impl-slice-implement` — Phase 2; keep as `impl-slice-implement-page` for Phase 1) |

- [ ] **Step 1.9.1: Move one-time skills to impl-build/**

```bash
for skill in scaffold foundation infrastructure migrate seed generate docs; do
  src="skaileup-build/skills/skailup-build-$skill"
  if [ -d "$src" ]; then
    git mv "$src" "impl-build/$skill"
  fi
done
ls impl-build/
```

- [ ] **Step 1.9.2: Move feature → impl-slice/implement**

```bash
git mv skaileup-build/skills/skailup-build-feature impl-slice/implement
# The nested feature-page sub-skill stays as a child until Phase 2
```

- [ ] **Step 1.9.3: Move build contracts**

```bash
mkdir -p impl-build/contracts
if [ -f skaileup-build/contracts/subagent_dispatch.md ]; then
  git mv skaileup-build/contracts/subagent_dispatch.md impl-build/contracts/subagent_dispatch.md
fi
if [ -d skaileup-build/contracts/implementation-contract ]; then
  git mv skaileup-build/contracts/implementation-contract impl-build/contracts/implementation-contract
fi
```

- [ ] **Step 1.9.4: Move build flows**

```bash
if [ -d skaileup-build/flows ]; then
  mkdir -p impl-build/flows
  git mv skaileup-build/flows/* impl-build/flows/
fi
```

- [ ] **Step 1.9.5: Update name: frontmatter for the seven impl-build skills**

Per the table, `skailup-build-X` → `impl-build-X`.

- [ ] **Step 1.9.6: Update name: frontmatter for impl-slice-implement**

`skailup-build-feature` → `impl-slice-implement` in the SKILL.md frontmatter.

The nested `feature-page` skill: rename frontmatter to `impl-slice-implement-page` (Phase 2 may merge or split further).

- [ ] **Step 1.9.7: Handle ancillary content (agents, CHANGELOG, docs)**

Before the cleanup `rm`, inspect what's left:

```bash
ls -la skaileup-build/
```

For each remaining item, decide:
- `agents/skailup-implement` → `git mv skaileup-build/agents/skailup-implement impl-build/agents/skaileup-implement` (then rename frontmatter to `impl-build-implement` or fold into `impl-slice/implement` per Phase 2 decision)
- `CHANGELOG.md` → `git mv skaileup-build/CHANGELOG.md impl-build/CHANGELOG.md`
- `docs/` → `git mv skaileup-build/docs impl-build/docs`
- `flows/` → already moved in Step 1.9.4
- `contracts/` → already moved in Step 1.9.3

- [ ] **Step 1.9.8: Verify only empty dir remains, then cleanup + commit**

```bash
find skaileup-build -type f | head
```

Expected: empty (no files left). If files remain, decide their disposition before continuing.

```bash
rm -rf skaileup-build
git add -A
git commit -m "refactor: split skaileup-build → impl-build (one-time) + impl-slice/implement

One-time project-setup skills (scaffold, foundation, infrastructure, migrate,
seed, generate, docs) moved to impl-build/. The per-feature skill 'feature'
moved to impl-slice/implement. Phase 2 will add the rest of the slice loop:
recap, refactor, commit, plus impl-plan/{align, plan-vertical}.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 1.10: Migrate `skaileup-build-supervised` → `impl-plan/` + merged into `impl-slice/`

**Migration:**
- `skailup-supervised-brainstorm` → `impl-plan/brainstorm/` (rename to `impl-plan-brainstorm`)
- `skailup-supervised-plan` → `impl-plan/plan-vertical/` (rename to `impl-plan-plan-vertical`)
- `skailup-supervised-git-prepare` → merged into `impl-slice/commit/` (Phase 2 — for Phase 1, move to `impl-slice/git-prepare/` as a stub)
- `skailup-supervised-finish` → merged into `impl-slice/commit/` (Phase 2 — for Phase 1, move to `impl-slice/finish/` as a stub)
- `skailup-supervised` (orchestrator) → move to `impl-plan/supervised/` (the orchestrator stays as a per-slice supervised flow entry)

- [ ] **Step 1.10.1: Move skills**

```bash
git mv skaileup-build-supervised/skills/skailup-supervised-brainstorm impl-plan/brainstorm
git mv skaileup-build-supervised/skills/skailup-supervised-plan impl-plan/plan-vertical
git mv skaileup-build-supervised/skills/skailup-supervised-git-prepare impl-slice/git-prepare
git mv skaileup-build-supervised/skills/skailup-supervised-finish impl-slice/finish
git mv skaileup-build-supervised/skills/skailup-supervised impl-plan/supervised
```

- [ ] **Step 1.10.2: Update name: frontmatter**

| Old | New |
|---|---|
| `skailup-supervised-brainstorm` | `impl-plan-brainstorm` |
| `skailup-supervised-plan` | `impl-plan-plan-vertical` |
| `skailup-supervised-git-prepare` | `impl-slice-git-prepare` |
| `skailup-supervised-finish` | `impl-slice-finish` |
| `skailup-supervised` | `impl-plan-supervised` |

- [ ] **Step 1.10.3: Cleanup + commit**

```bash
rm -rf skaileup-build-supervised
git add -A
git commit -m "refactor: migrate skaileup-build-supervised → impl-plan + impl-slice

brainstorm + plan promoted to impl-plan/ (so all flows can use them, not
just the supervised variant). git-prepare + finish moved to impl-slice/
as stubs; Phase 2 will consolidate them into impl-slice/commit.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 1.11: Migrate `skaileup-quality` → `impl-quality/` + promote stack profiles

**Migration:**
- `skaileup-quality/skills/skailup-quality-*` → `impl-quality/<skill>/`
- `skaileup-quality/profiles/skailup-tech-stack-*` → `impl-architecture/templates/<stack>/`

**Name renames** (drop `skailup-quality-` prefix and replace with `impl-quality-`; for tech-stack, drop `skailup-tech-stack-`):

| Old | New |
|---|---|
| `skailup-quality-test-plan` | `impl-quality-test-plan` |
| `skailup-quality-test-unit` | `impl-quality-test-unit` |
| `skailup-quality-test-integration` | `impl-quality-test-integration` |
| `skailup-quality-test-e2e` | `impl-quality-test-e2e` |
| `skailup-quality-eval-code` | `impl-quality-eval-code` |
| `skailup-quality-audit` | `impl-quality-audit` |
| `skailup-quality-ready` | `impl-quality-ready` |
| `skailup-quality-standards-discover` | `impl-quality-standards-discover` |
| `skailup-quality-standards-inject` | `impl-quality-standards-inject` |
| `skailup-quality-standards-sync` | `impl-quality-standards-sync` |
| `skailup-tech-stack-nextjs-shadcn` | `template-nextjs-shadcn` |
| `skailup-tech-stack-nextjs-radix` | `template-nextjs-radix` |
| `skailup-tech-stack-nuxt-primevue` | `template-nuxt-primevue` |
| `skailup-tech-stack-nuxt-minimal` | `template-nuxt-minimal` |
| `skailup-tech-stack-nuxt-ui` | `template-nuxt-ui` |
| `skailup-tech-stack-postxl` | `template-postxl` |

- [ ] **Step 1.11.1: Move quality skills**

```bash
for skill in test-plan test-unit test-integration test-e2e \
             eval-code audit ready \
             standards-discover standards-inject standards-sync; do
  src="skaileup-quality/skills/skailup-quality-$skill"
  if [ -d "$src" ]; then
    git mv "$src" "impl-quality/$skill"
  fi
done
```

- [ ] **Step 1.11.2: Move stack profiles to impl-architecture/templates/**

```bash
mkdir -p impl-architecture/templates
for profile in $(ls skaileup-quality/profiles/ 2>/dev/null); do
  newname="${profile#skailup-tech-stack-}"
  newname="template-${newname}"
  git mv "skaileup-quality/profiles/$profile" "impl-architecture/templates/$newname"
done
ls impl-architecture/templates/
```

- [ ] **Step 1.11.3: Update name: frontmatter for ALL moved skills (~16 files)**

Use Edit per the rename table.

- [ ] **Step 1.11.4: Handle ancillary content (agents, CHANGELOG, docs, root bundle.yaml)**

```bash
ls -la skaileup-quality/
```

For each remaining item:
- `skaileup-quality.bundle.yaml` (or similar) → `git rm` (Phase 2 Task 2H rebuilds bundles from flows)
- `agents/` → `git mv skaileup-quality/agents impl-quality/agents`
- `CHANGELOG.md` → `git mv skaileup-quality/CHANGELOG.md impl-quality/CHANGELOG.md`
- `docs/` → `git mv skaileup-quality/docs impl-quality/docs`
- `contracts/` → `git mv skaileup-quality/contracts impl-quality/contracts`

- [ ] **Step 1.11.5: Verify clean + commit**

```bash
find skaileup-quality -type f
```

Expected: empty.

```bash
rm -rf skaileup-quality
git add -A
git commit -m "refactor: migrate skaileup-quality → impl-quality + promote templates

Quality skills moved to impl-quality/. Stack profiles promoted from
skaileup-quality/profiles/ to impl-architecture/templates/ — they drive
scaffold/foundation/migrate/seed/feature, so they belong with architecture
not quality. Templates renamed: skailup-tech-stack-X → template-X.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 1.12: Migrate `skaileup-lab` → `lab/` + `skaileup-contracts` → `contracts/`

- [ ] **Step 1.12.1: Move lab**

```bash
git mv skaileup-lab/skills/skailup-lab-compile-validators lab/compile-validators
# If there are other lab skills, move them similarly
for skill in $(ls skaileup-lab/skills/ 2>/dev/null); do
  newname="${skill#skailup-lab-}"
  if [ ! -d "lab/$newname" ]; then
    git mv "skaileup-lab/skills/$skill" "lab/$newname"
  fi
done
rm -rf skaileup-lab
```

- [ ] **Step 1.12.2: Move contracts**

The `skaileup-contracts/` dir is mostly already where it should be — it's renamed to `contracts/` and its content moves up.

```bash
# The new top-level contracts/ dir already has a stub DOMAIN.md from Task 1.2
# Move skaileup-contracts content into it
git mv skaileup-contracts/contracts/* contracts/
git mv skaileup-contracts/scripts contracts/scripts || true
git mv skaileup-contracts/docs contracts/docs || true
# Discard or merge the skaileup-contracts/DOMAIN.md and README.md
# (the new contracts/DOMAIN.md was created in Task 1.2 with proper content)
rm -rf skaileup-contracts
```

- [ ] **Step 1.12.3: Update name: frontmatter for moved lab skills**

- [ ] **Step 1.12.4: Update name: frontmatter for moved contracts** 

Each `CONTRACT.md` should have `name: <contract-name>` matching its filename stem (no prefix).

- [ ] **Step 1.12.5: Verify**

```bash
test -d lab/compile-validators && echo "lab OK"
test -f contracts/iron_laws.md && echo "contracts OK"
test ! -d skaileup-lab && echo "skaileup-lab gone"
test ! -d skaileup-contracts && echo "skaileup-contracts gone"
```

- [ ] **Step 1.12.6: Commit**

```bash
git add -A
git commit -m "refactor: migrate skaileup-lab + skaileup-contracts → lab/ + contracts/

Final domain renames in the migration map. Contracts now at top-level
contracts/ (the reference layer every skill reads).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 1.13: Bulk update path references throughout the repo

After all moves, every SKILL.md body, CONTRACT.md, validator.py, etc. that mentioned old paths (`skaileup-build/`, `skaileup-quality/`, etc.) needs updating.

- [ ] **Step 1.13.1: Survey what references remain**

```bash
grep -rln 'skaileup-\(build\|quality\|architecture\|datamodel\|grounding\|discovery\|experience\|concept-mockup\|concept-storybook\|concept-ops\|build-supervised\|lab\|contracts\)' \
  --exclude-dir=__pycache__ --exclude="*.pyc" . 2>/dev/null > /tmp/refs-to-update.txt
wc -l /tmp/refs-to-update.txt
head -20 /tmp/refs-to-update.txt
```

Expected: a list of files to update. Probably 30-100 files.

- [ ] **Step 1.13.2: Build the rename map in two passes**

The rename has two distinct concerns that must be applied in order:
1. **Skill-name renames** (`skailup-build-feature` → `impl-slice-implement`) — applied first, since these are unambiguous string substitutions
2. **Path renames** (`skaileup-build/skills/skailup-build-feature/` → `impl-slice/implement/`) — applied second, since they may overlap with skill names

Create `/tmp/rename-pass1-skills.sed` with the skill-name renames:

```sed
# Skill name renames (drop skailup- typo prefix, prepend new domain)
s|skailup-grounding-onboard|concept-grounding-onboard|g
s|skailup-grounding-research|concept-grounding-research|g
s|skailup-grounding-seeds|concept-grounding-seeds|g
s|skailup-discovery-brief|concept-brief|g
s|skailup-discovery-brand-visual|design-brand-visual|g
s|skailup-discovery-brand-voice|design-brand-voice|g
s|skailup-experience-features|product-spec-features|g
s|skailup-experience-journeys|experience-journeys|g
s|skailup-experience-behaviors|experience-behaviors|g
s|skailup-experience-screens-technical|experience-screens-technical|g
s|skailup-experience-screens|experience-screens|g
s|skailup-experience-components|experience-components|g
s|skailup-architecture-techstack|impl-architecture-techstack|g
s|skailup-architecture-system|impl-architecture-system|g
s|skailup-datamodel|impl-architecture-datamodel|g
s|skailup-concept-mockup|walkthrough-mockup-text|g
s|skailup-concept-storybook-setup|component-mockup-storybook-setup|g
s|skailup-concept-storybook-types|component-mockup-storybook-types|g
s|skailup-concept-storybook-components|component-mockup-storybook-components|g
s|skailup-concept-storybook-pages|component-mockup-storybook-pages|g
s|skailup-concept-storybook-journeys|component-mockup-storybook-journeys|g
s|skailup-concept-storybook|component-mockup-storybook|g
s|skailup-concept-ops-sync|ops-sync|g
s|skailup-add-feature|ops-add-feature|g
s|skailup-eval-concept|ops-eval-concept|g
s|skailup-eval-feature|ops-eval-feature|g
s|skailup-eval-product|ops-eval-product|g
s|skailup-review|ops-review|g
s|skailup-reverse-engineer|ops-reverse-engineer|g
s|skailup-project-overview|ops-project-overview|g
s|skailup-project-subsystem-map|ops-project-subsystem-map|g
s|skailup-project-integration|ops-project-integration|g
s|skailup-project-review|ops-project-review|g
s|skailup-build-feature-page|impl-slice-implement-page|g
s|skailup-build-feature|impl-slice-implement|g
s|skailup-build-scaffold|impl-build-scaffold|g
s|skailup-build-foundation|impl-build-foundation|g
s|skailup-build-infrastructure|impl-build-infrastructure|g
s|skailup-build-migrate|impl-build-migrate|g
s|skailup-build-seed|impl-build-seed|g
s|skailup-build-generate|impl-build-generate|g
s|skailup-build-docs|impl-build-docs|g
s|skailup-supervised-brainstorm|impl-plan-brainstorm|g
s|skailup-supervised-plan|impl-plan-plan-vertical|g
s|skailup-supervised-git-prepare|impl-slice-git-prepare|g
s|skailup-supervised-finish|impl-slice-finish|g
s|skailup-supervised|impl-plan-supervised|g
s|skailup-quality-test-plan|impl-quality-test-plan|g
s|skailup-quality-test-unit|impl-quality-test-unit|g
s|skailup-quality-test-integration|impl-quality-test-integration|g
s|skailup-quality-test-e2e|impl-quality-test-e2e|g
s|skailup-quality-eval-code|impl-quality-eval-code|g
s|skailup-quality-audit|impl-quality-audit|g
s|skailup-quality-ready|impl-quality-ready|g
s|skailup-quality-standards-discover|impl-quality-standards-discover|g
s|skailup-quality-standards-inject|impl-quality-standards-inject|g
s|skailup-quality-standards-sync|impl-quality-standards-sync|g
s|skailup-tech-stack-nextjs-shadcn|template-nextjs-shadcn|g
s|skailup-tech-stack-nextjs-radix|template-nextjs-radix|g
s|skailup-tech-stack-nuxt-primevue|template-nuxt-primevue|g
s|skailup-tech-stack-nuxt-minimal|template-nuxt-minimal|g
s|skailup-tech-stack-nuxt-ui|template-nuxt-ui|g
s|skailup-tech-stack-postxl|template-postxl|g
s|skailup-lab-compile-validators|lab-compile-validators|g
```

Add lines for any skill names not yet covered (use `ls` of the now-moved directories to confirm coverage).

Create `/tmp/rename-pass2-paths.sed` with the path renames (after Pass 1 has cleaned the skill names, only directory paths remain):

```sed
# Path renames — directories only (skill-name segments already fixed by Pass 1)
s|skaileup-grounding/skills/concept-grounding-|concept/grounding/|g
s|skaileup-grounding/skills/|concept/grounding/|g
s|skaileup-grounding/contracts/|concept/grounding/contracts/|g
s|skaileup-grounding/|concept/grounding/|g
s|skaileup-discovery/skills/concept-brief/|concept/brief/|g
s|skaileup-discovery/skills/design-brand-visual/|design/brand-visual/|g
s|skaileup-discovery/skills/design-brand-voice/|design/brand-voice/|g
s|skaileup-experience/skills/product-spec-features/|product-spec/features/|g
s|skaileup-experience/skills/experience-journeys/|experience/journeys/|g
s|skaileup-experience/skills/experience-behaviors/|experience/behaviors/|g
s|skaileup-experience/skills/experience-screens-technical/|experience/screens-technical/|g
s|skaileup-experience/skills/experience-screens/|experience/screens/|g
s|skaileup-experience/skills/experience-components/|experience/components/|g
s|skaileup-architecture/skills/impl-architecture-techstack/|impl-architecture/techstack/|g
s|skaileup-architecture/skills/impl-architecture-system/|impl-architecture/system/|g
s|skaileup-datamodel/skills/impl-architecture-datamodel/|impl-architecture/datamodel/|g
s|skaileup-datamodel/|impl-architecture/datamodel/|g
s|skaileup-concept-mockup/skills/walkthrough-mockup-text/|walkthrough-mockup/text/|g
s|skaileup-concept-mockup/|walkthrough-mockup/|g
s|skaileup-concept-storybook/skills/component-mockup-storybook-|component-mockup/storybook/|g
s|skaileup-concept-storybook/skills/component-mockup-storybook/|component-mockup/storybook/|g
s|skaileup-concept-storybook/|component-mockup/storybook/|g
s|skaileup-concept-ops/skills/ops-|ops/|g
s|skaileup-concept-ops/contracts/|ops/contracts/|g
s|skaileup-concept-ops/|ops/|g
# NOTE: longer prefixes MUST come before shorter prefixes that share them.
# `skaileup-build-supervised` rules go BEFORE `skaileup-build` rules so the
# build-supervised paths aren't rewritten as `impl-build-supervised`.
s|skaileup-build-supervised/skills/impl-plan-|impl-plan/|g
s|skaileup-build-supervised/skills/impl-slice-|impl-slice/|g
s|skaileup-build-supervised/|impl-plan/|g
s|skaileup-build/skills/impl-slice-implement-page/|impl-slice/implement/impl-slice-implement-page/|g
s|skaileup-build/skills/impl-slice-implement/|impl-slice/implement/|g
s|skaileup-build/skills/impl-build-|impl-build/|g
s|skaileup-build/contracts/|impl-build/contracts/|g
s|skaileup-build/flows/|impl-build/flows/|g
s|skaileup-build/|impl-build/|g
s|skaileup-quality/skills/impl-quality-|impl-quality/|g
s|skaileup-quality/profiles/template-|impl-architecture/templates/template-|g
s|skaileup-quality/|impl-quality/|g
s|skaileup-lab/skills/lab-|lab/|g
s|skaileup-lab/|lab/|g
s|skaileup-contracts/contracts/|contracts/|g
s|skaileup-contracts/scripts/|contracts/scripts/|g
s|skaileup-contracts/docs/|contracts/docs/|g
s|skaileup-contracts/|contracts/|g
```

- [ ] **Step 1.13.3: Dry-run BOTH passes on one file**

```bash
sample=$(head -1 /tmp/refs-to-update.txt)
echo "Testing on: $sample"
sed -f /tmp/rename-pass1-skills.sed "$sample" > /tmp/sample-pass1.txt
sed -f /tmp/rename-pass2-paths.sed /tmp/sample-pass1.txt > /tmp/sample-final.txt
diff "$sample" /tmp/sample-final.txt | head -60
```

Expected: a coherent diff showing skill names + paths updated. **Visually inspect for double-substitution**: any path with `concept/concept/` or `impl-build/impl-build/` is a bug — fix the sed map and re-run.

- [ ] **Step 1.13.4: Apply BOTH passes globally**

```bash
xargs -a /tmp/refs-to-update.txt sed -i -f /tmp/rename-pass1-skills.sed
xargs -a /tmp/refs-to-update.txt sed -i -f /tmp/rename-pass2-paths.sed
```

- [ ] **Step 1.13.5: Verify no old references remain**

```bash
grep -rEln 'skaileup-(build|quality|architecture|datamodel|grounding|discovery|experience|concept-mockup|concept-storybook|concept-ops|build-supervised|lab|contracts)|skailup-' \
  --include="*.md" --include="*.py" --include="*.yaml" --include="*.json" \
  --exclude-dir=__pycache__ \
  --exclude="MIGRATION.md" --exclude="README.md" \
  . 2>/dev/null
```

Expected: empty (or only matches in MIGRATION.md / README.md historical sections, which are intentional).

If matches remain, inspect each — they typically fall into one of three buckets:
1. A skill name not covered by the rename map (add a line to `pass1-skills.sed`, re-run)
2. A path pattern not covered (add a line to `pass2-paths.sed`, re-run)
3. An intentional historical reference (leave alone, add to the `--exclude` list if the file is documentational)

- [ ] **Step 1.13.6: Verify no double-substitutions**

```bash
grep -rEln '(concept/concept|impl-build/impl-build|impl-quality/impl-quality|impl-architecture/impl-architecture|ops/ops|lab/lab)' \
  --include="*.md" --include="*.py" --include="*.yaml" --include="*.json" . 2>/dev/null
```

Expected: empty. If matches found, investigate and fix manually.

- [ ] **Step 1.13.7: Commit**

```bash
git add -A
git commit -m "refactor: bulk-update path references after domain renames

Every READS/WRITES/REFERENCES line and validator.py path that mentioned
old skaileup-X paths now points to the new location. Two-pass sed:
pass 1 renames skill names, pass 2 renames directory paths. Historical
mentions in MIGRATION.md and README.md preserved.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 1.14: Update top-level docs

The migration changes the canonical names. The repo's user-facing docs need updating.

**Files:**
- Modify: `README.md` (domain table)
- Modify: `CLAUDE.md` (catalog overview)
- Modify: `CONTRIBUTING.md` (examples now use new naming)
- Modify: `SKILL_GRAPH.md` (already mostly written for new naming, but verify no stale `skailup-*` refs)
- Modify: `REFACTOR_MOCKUP.md` (verify alignment)

- [ ] **Step 1.14.1: Update README.md domain table**

Replace the current 14-row table (with `skaileup-*` names) with the new layout:

```markdown
## Top-level layout

### Concept
| Domain | Purpose |
|---|---|
| [`concept/`](concept/DOMAIN.md) | Project brief, goals, comparable apps |
| [`design/`](design/DOMAIN.md) | Brand identity, tokens, voice |
| [`product-spec/`](product-spec/DOMAIN.md) | Feature specs + acceptance criteria |
| [`experience/`](experience/DOMAIN.md) | Journeys, behaviors, screens, components |
| [`concept-slice/`](concept-slice/DOMAIN.md) | Per-feature concept loop (big apps) |
| [`component-mockup/`](component-mockup/DOMAIN.md) | Storybook + isolated HTML |
| [`walkthrough-mockup/`](walkthrough-mockup/DOMAIN.md) | text · static-html · lit · astro · framework |
| [`mockup-feedback/`](mockup-feedback/DOMAIN.md) | Annotation → patch loop |

### Implementation
| Domain | Purpose |
|---|---|
| [`impl-architecture/`](impl-architecture/DOMAIN.md) | Techstack, system, datamodel, templates |
| [`impl-plan/`](impl-plan/DOMAIN.md) | Brainstorm, align, plan-vertical, supervised |
| [`impl-slice/`](impl-slice/DOMAIN.md) | Per-slice loop: implement → test → recap → refactor → commit |
| [`impl-build/`](impl-build/DOMAIN.md) | One-time: scaffold, foundation, migrate, seed, ... |
| [`impl-quality/`](impl-quality/DOMAIN.md) | Tests, audit, ready, standards, debug |

### Meta
| Domain | Purpose |
|---|---|
| [`ops/`](ops/DOMAIN.md) | Cross-cutting: review, sync, eval, add-feature, project-* |
| [`lab/`](lab/DOMAIN.md) | Skill-on-skill: validate, improve, compile-validators |
| [`contracts/`](contracts/DOMAIN.md) | Reference layer (every skill reads) |
```

Update the lineage section to add: "Phase 1 of the SKILL_GRAPH proposal applied 2026-05-XX (this branch)."

- [ ] **Step 1.14.2: Update CLAUDE.md**

Replace the `## Structure` ASCII tree with the new layout. Replace `## Naming Convention` to reflect the new naming (no more `skaileup-*` vs `skailup-*` distinction; the new convention is just kebab-case with no `skaileup-` prefix).

- [ ] **Step 1.14.3: Verify CONTRIBUTING.md examples**

Check all skill names in CONTRIBUTING.md examples — they should already be generic (e.g., `my-skill`), so likely no changes needed. If any existing skaileup-* names appear, update them.

- [ ] **Step 1.14.4: Verify SKILL_GRAPH.md**

```bash
grep -n 'skaileup-\|skailup-' SKILL_GRAPH.md | grep -v "Migration map"
```

Expected: empty (or only refs inside the migration map, which are correct).

- [ ] **Step 1.14.5: Commit**

```bash
git add README.md CLAUDE.md CONTRIBUTING.md SKILL_GRAPH.md REFACTOR_MOCKUP.md
git commit -m "docs: update top-level docs for Phase 1 catalog reorganization

README.md, CLAUDE.md updated with new domain layout. CONTRIBUTING.md
examples verified. SKILL_GRAPH.md and REFACTOR_MOCKUP.md confirmed
consistent with the executed migration.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 1.15: Final verification + Phase 1 PR-ready commit

- [ ] **Step 1.15.1: Verify skill counts haven't dropped**

```bash
find . -name "SKILL.md" -not -path "*/.skaile/*" | wc -l
find . -name "CONTRACT.md" -not -path "*/.skaile/*" | wc -l
find . -name "DOMAIN.md" -not -path "*/.skaile/*" | wc -l
cat /tmp/skill-count-before
```

Expected: SKILL.md count >= original (we may have unchanged or gained DOMAIN.md stubs). CONTRACT.md count = original. DOMAIN.md count > original (added 16 stubs).

- [ ] **Step 1.15.2: Verify every SKILL.md has a name: matching its parent dir or domain pattern**

Write a verification script:

```bash
for skill_md in $(find . -name "SKILL.md" -not -path "*/.skaile/*"); do
  dir=$(dirname "$skill_md")
  parent_name=$(basename "$dir")
  declared_name=$(grep -E "^name: " "$skill_md" | head -1 | awk '{print $2}')
  if [ -z "$declared_name" ]; then
    echo "MISSING NAME: $skill_md"
  fi
done
```

Expected: empty output. Every SKILL.md must have an explicit `name:`.

- [ ] **Step 1.15.3: Run the catalog scanner via skaile CLI**

```bash
# From parent skaile-dev shell
cd /mnt/localvault/workBench/SKAILE/skaile-dev-matthias
bun -C skaile-agent-framework/cli run cli --help 2>&1 | head -3
```

If the CLI is buildable: `bun -C skaile-agent-framework/cli run cli list 2>&1 | head -50`

The list output should show all migrated skills under their new names. Validate spot-check 3-5 skills.

- [ ] **Step 1.15.4: Make sure typecheck passes on the parent agent-framework (no impact expected)**

```bash
cd /mnt/localvault/workBench/SKAILE/skaile-dev-matthias/skaile-agent-framework/core
bun run typecheck
```

Expected: no errors.

- [ ] **Step 1.15.5: Final review commit (or amend prior)**

If anything was missed (likely a stray reference), add a final commit. Otherwise nothing to do.

- [ ] **Step 1.15.6: Push branch + open PR**

```bash
cd /mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup
git push -u origin refactor/skill-graph
# Then via gh CLI:
gh pr create --title "refactor: phase 1 — skill graph reorganization (mechanical)" --body "$(cat <<'EOF'
## Summary

Phase 1 of the SKILL_GRAPH refactor. Mechanical only — no new behavior.

- 14 `skaileup-*` domains migrated to the two-group structure (Concept + Implementation + Meta)
- ~50 SKILL.md files moved to new homes, names updated to drop `skailup-` prefix
- ~6 stack profiles promoted from `skaileup-quality/profiles/` to `impl-architecture/templates/`
- New empty domain dirs scaffolded: `concept-slice/`, `impl-slice/`, `impl-plan/`, `component-mockup/`, `walkthrough-mockup/`, `mockup-feedback/`
- Bulk path-reference update across READS/WRITES/REFERENCES sections + validator.py imports
- Workspace zone gitignores: `_slice/`, `_feedback/sessions/`, `_feedback/patches/`
- Top-level docs (README, CLAUDE, CONTRIBUTING, SKILL_GRAPH, REFACTOR_MOCKUP) updated

## Test plan

- [ ] All SKILL.md files have valid `name:` matching new convention
- [ ] No remaining `skaileup-*` or `skailup-*` references in skill bodies (except migration history in MIGRATION.md and README.md)
- [ ] `skaile list` from CLI lists every skill under new names
- [ ] CONTRIBUTING.md examples reference only new naming
- [ ] No regression in agent-framework/core typecheck

## What's NOT in this PR

- New skill content (concept-slice/*, impl-slice/{recap,refactor,commit}, impl-plan/{align,plan-vertical}, scope-project, mockup-feedback-*, walkthrough-mockup-{static-html,lit,astro,framework}, component-mockup-isolated-html, lab/compile-bundle, lab/archive)
- Any flow.yaml or bundle.yaml authoring
- Annotation overlay JS or section-diff engine
- forge-concept investigation

These are Phase 2 and Phase 3 of the migration plan
(see `docs/devlog/2026-05-07-skill-graph-migration.md`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Expected: PR URL printed.

---

# PHASE 2 — Skill authoring

**Goal:** every skill in the new catalog has a fully-written `SKILL.md` plus validator. Flows + bundles for the four tier sizes work end-to-end on top of `walkthrough-mockup-static-html`.

**Scope:** ~30 new skills, 6 flows, 6 bundles. Multi-week, multi-session.

**Critical:** **each task below is a STUB.** Before executing a Phase 2 task, write a dedicated mini-plan in `docs/devlog/<task-id>-<skill-name>.md` using the writing-plans skill. The mini-plan will:
1. Read the relevant section of `SKILL_GRAPH.md` and `REFACTOR_MOCKUP.md`.
2. Define the skill's I/O contract (READS, WRITES, REFERENCES).
3. Draft acceptance criteria — what does "this skill works" look like?
4. Decompose authoring into 5-15 minute steps with TDD-style verification.

The stubs below give you the inputs, outputs, dependencies, and acceptance criteria. They are NOT executable as-is.

---

## Task 2.0: Author `contracts/elements_block.md` (NEW frontmatter contract)

**Why first:** the `elements:` block is consumed by every walkthrough renderer (Phase 2H, Phase 3) and the entire feedback loop (Phase 3). It MUST exist before any walkthrough or feedback skill is authored.

**Files:**
- Create: `contracts/elements_block.md`
- Modify: `contracts/asset_frontmatter.md` (extend the screen frontmatter section to reference `elements_block.md`)
- Create: `lab/validate-elements-block/SKILL.md` (a small validator skill)

**Spec source:** `REFACTOR_MOCKUP.md` § 6 (the `elements:` block)

**Acceptance criteria:**
- The contract documents the schema (id, kind, label, states, optional fields)
- The contract describes the auto-slug + provisional-promotion hybrid strategy
- A test file `tests/elements_block_examples.md` shows three valid + three invalid examples
- The validator returns 0 for valid examples and non-zero with line numbers for invalid

**Sub-plan blocker:** none — author this first in Phase 2.

---

## Task 2A: Author `scope-project` skill

**Location:** `skaileup/scope/scope-project/SKILL.md`

**Inputs (READS):**
- (none — this is the orchestrator's first action)
- Optional: `_concept/_meta/scope.yaml` (re-scoping)

**Outputs (WRITES):**
- `_concept/_meta/scope.yaml` with: `tier`, `reasoning`, `flow_to_run`

**References:**
- `SKILL_GRAPH.md` § 3 (tier behavior table) — verbatim decision rule
- `contracts/iron_laws.md`

**Acceptance criteria:**
- Given a one-sentence project description, the skill picks one of: `mvp`, `simple-app`, `standard-app`, `complex-app`
- Outputs are deterministic for the same inputs (modulo LLM jitter)
- Writes a valid YAML to `_concept/_meta/scope.yaml`
- Surfaces the chosen tier and reasoning to the user before committing
- Allows override via `--tier=` argument

**Sub-plan blocker:** none — this skill has no skill dependencies. Author first.

---

## Task 2B: Author `concept-slice/*` cluster (4 skills)

**Skills:**
- `concept-slice-brainstorm` — sparring on what the feature is
- `concept-slice-align` — grill-me style interview, surfaces edge cases
- `concept-slice-scope-feature` — what's IN and OUT for this feature
- `concept-slice-design-feature` — writes feature's portion of `product-spec/features/<feature>.md`, `experience/screens/<feature>/*.md`, `walkthrough-mockup/<tier>/<feature>.*`

**Inputs / Outputs:**
See SKILL_GRAPH § 4 (concept group artifact flow, concept-slice section) for the per-skill input/output contract.

**Acceptance criteria:**
- The four skills compose: brainstorm → align → scope-feature → design-feature, each consuming the previous output via `_slice/concept/<id>/<phase>.md`
- design-feature writes ONLY this feature's portion of the relevant artifacts (does not modify other features)
- Each skill writes to `_slice/concept/<id>/<phase>.md` first, only commits to permanent artifacts on completion
- design-feature deletes `_slice/concept/<id>/` on success (mirrors `impl-slice/commit`)

**Sub-plan blocker:** scope-project should exist (so the slice has a tier context).

---

## Task 2C: Author `impl-plan/{align, plan-vertical}` (2 skills)

**Skills:**
- `impl-plan-align` — grill-me style interview before implementation begins
- `impl-plan-plan-vertical` — vertical-slice decomposition, embeds testing strategy

**Inputs / Outputs:**
See SKILL_GRAPH § 5.2 (per-slice impl loop, brainstorm/align/plan-vertical phases).

**Note:** `impl-plan-brainstorm` already exists (migrated from `skaileup-build-supervised`). Verify its current SKILL.md aligns with the new naming, refresh content if needed.

**Acceptance criteria:**
- align reads existing concept artifacts + the slice scope, writes `_slice/impl/<id>/align.md`
- plan-vertical reads align + concept, writes `_slice/impl/<id>/plan.md` containing:
  - vertical decomposition (UI + logic + data for ONE slice)
  - testing strategy (how to verify slice is done)
  - explicit anti-horizontal nudge (the prompt resists "first all UI, then all logic")

**Sub-plan blocker:** scope-project, concept-slice cluster.

---

## Task 2D: Author `impl-slice/{recap, refactor, commit}` (3 skills)

**Skills:**
- `impl-slice-recap` — explain what was built + draw a diagram (mandatory)
- `impl-slice-refactor` — force-simplify, "smallest improvement?", AI defaults to adding complexity
- `impl-slice-commit` — atomic commits + delete `_slice/impl/<id>/` scratch

**Note:** `impl-slice-implement` already exists (migrated from `skailup-build-feature` in Phase 1 Task 1.9). `impl-slice-test` does NOT exist yet — Phase 1 doesn't carve a separate test skill out of the build-feature skill. Task 2D should ALSO create `impl-slice-test` from scratch (the per-slice usability feedback loop, distinct from `impl-quality/test-*`).

**Acceptance criteria:**
- recap writes `_slice/impl/<id>/recap.md` containing: feature flow explanation + an ASCII diagram
- refactor proposes 1-3 minimal changes that preserve behavior, asks the user to approve before applying
- commit makes atomic git commits AND deletes `_slice/impl/<id>/` (mirrors concept-slice/design-feature)

**Sub-plan blocker:** concept-slice (so commit knows what to clean), impl-plan/* (so the slice has handoff files to delete).

---

## Task 2E: Author `impl-quality/debug-{self-verify, handoff}` (2 skills)

**Skills:**
- `impl-quality-debug-self-verify` — "let AI figure out HOW to verify this is fixed"
- `impl-quality-debug-handoff` — describe state + tried-things for the next agent

**Acceptance criteria:**
- self-verify produces a verification protocol the AI can run autonomously (test commands, expected outputs, success criteria)
- handoff produces a markdown summary suitable for pasting into a new chat that contains: bug description, attempts so far, current hypothesis, what to try next

**Sub-plan blocker:** none — these are general-purpose, can be authored anytime.

---

## Task 2F: Author `walkthrough-mockup-static-html` (the contract anchor)

**Location:** `walkthrough-mockup/static-html/SKILL.md`

**Why first among walkthrough skills:** establishes the input contract. Other walkthrough variants (lit, astro, framework) just have to honor the same contract. Static-html has no build dependency, so it's the simplest place to validate the contract.

**Inputs:**
- `experience/screens/*.md`
- `experience/journeys/stories.json`
- `design/tokens.json`
- `product-spec/features/*.md`

**Outputs:**
- `_concept/walkthrough-mockup/static-html/` containing:
  - `index.html` (router/menu)
  - `screen/<group>/<name>.html` (one file per screen)
  - `journey/<id>.html` (one file per journey)
  - `manifest.json` (mapping rendered elements → source files)
  - Every rendered DOM node carries `data-spec-screen` + `data-spec-element` attributes

**Acceptance criteria:**
- Generated site is openable as a static set of files (no build, no JS framework)
- Clicking a `journey` link walks through screens in order
- All `data-spec-*` attributes resolve to existing source files
- `manifest.json` is parseable by mockup-feedback-annotate (Phase 3)

**Sub-plan blocker:** none, but Phase 3 builds on this — author thoroughly.

---

## Task 2G: Author `component-mockup-isolated-html`

**Location:** `component-mockup/isolated-html/SKILL.md`

**Inputs:**
- `experience/components/*.md`
- `design/tokens.json`

**Outputs:**
- `_concept/component-mockup/isolated-html/<component>.html` (one file per component)

**Acceptance criteria:**
- Standalone HTML page per component, no framework, no build
- Shows all variants/states declared in component frontmatter
- Embeds tokens.json values inline (no external CSS load)

**Sub-plan blocker:** none.

---

## Task 2H: Author flows + bundles (mvp, simple-app, standard-app, complex-app, slice flows)

**Files (10 total):**
- `flows/mvp.flow.yaml`, `bundles/mvp.bundle.yaml`
- `flows/simple-app.flow.yaml`, `bundles/simple-app.bundle.yaml`
- `flows/standard-app.flow.yaml`, `bundles/standard-app.bundle.yaml`
- `flows/complex-app.flow.yaml`, `bundles/complex-app.bundle.yaml`
- `flows/concept-slice.flow.yaml`, `bundles/concept-slice.bundle.yaml`
- `flows/impl-slice.flow.yaml`, `bundles/impl-slice.bundle.yaml`

**Acceptance criteria:**
- Each tier flow composes the slice flows rather than inlining their phases (per SKILL_GRAPH § 6)
- Each bundle declares exactly the dependencies the flow's nodes reference (no extras)
- Bundles inherit: simple-app → mvp; standard-app → simple-app; complex-app → standard-app
- Tier compositions match SKILL_GRAPH § 6 tier-composition table exactly
- Flow YAML validates against `contracts/flows.md` schema

**Sub-plan blocker:** all the new skills referenced by these flows must exist (Tasks 2A–2G). Author last among Phase 2.

---

## Task 2I: (Optional, leverage) Author `lab/compile-bundle`

**Why optional:** the bundles in 2H can be written by hand. But once `lab/compile-bundle` exists, the bundles in 2H can be generated from the flows, eliminating drift.

**Inputs:**
- `flows/<name>.flow.yaml`

**Outputs:**
- `bundles/<name>.bundle.yaml` (with explicit dependency list derived from the flow's node graph)

**Sub-plan blocker:** Tasks 2H bundles done by hand first to establish ground truth; compile-bundle then reproduces them.

---

# PHASE 3 — Feedback loop engineering + remaining tiers

**Goal:** bidirectional sync (annotation → patch → devlog) end-to-end on `walkthrough-mockup-static-html`. Plus build the remaining walkthrough tiers (`lit`, `astro`, `framework`). Plus `lab/compile-bundle` and `lab/archive` for catalog hygiene.

**Scope:** ~10 tasks, real engineering (not just markdown), multi-week.

**Critical pre-task:** Task 3.0 must run first — it's the forge-concept investigation that's been the open question since the start.

---

## Task 3.0: forge-concept walkthrough investigation

**Goal:** find out whether forge-concept (the assistant Nuxt SPA) already has overlay / annotation / walkthrough code that the mockup-feedback skills should align with or absorb.

**Steps:**

- [ ] **Step 3.0.1: Locate forge-concept**

```bash
ls /mnt/localvault/workBench/SKAILE/skaile-dev-matthias/forge/ 2>/dev/null
```

Expected: directories including `forge-concept/` (or similar). If absent, search for it:

```bash
find /mnt/localvault/workBench/SKAILE -type d -name "forge-concept*" 2>/dev/null | head
```

- [ ] **Step 3.0.2: Search for annotation / overlay / walkthrough patterns**

```bash
cd /mnt/localvault/workBench/SKAILE/skaile-dev-matthias/forge/forge-concept 2>/dev/null || \
  cd $(find /mnt/localvault/workBench/SKAILE -type d -name "forge-concept" | head -1)
grep -rli "annotation\|walkthrough\|data-spec-\|overlay" --include="*.ts" --include="*.vue" --include="*.md" . 2>/dev/null | head -30
```

- [ ] **Step 3.0.3: Read top hits and document findings in `docs/devlog/forge-concept-walkthrough.md`**

What to capture:
- Existing data attribute conventions (`data-spec-*`? Different?)
- Existing overlay component (Vue? Web component? Vanilla?)
- Existing annotation capture mechanism (IndexedDB? localStorage? POST endpoint?)
- Existing patch/feedback persistence
- Recommended alignment for the new mockup-feedback skills

- [ ] **Step 3.0.4: Update REFACTOR_MOCKUP.md § 12 to resolve the still-open question**

If forge-concept has working code: align the skill specs to its conventions.
If forge-concept has no related code: document that and treat as greenfield.

- [ ] **Step 3.0.5: Commit findings**

```bash
git add docs/devlog/forge-concept-walkthrough.md REFACTOR_MOCKUP.md
git commit -m "research: forge-concept walkthrough investigation

Documents existing annotation/overlay code in forge-concept (if any) and
how the mockup-feedback skills should align. Resolves the last open
question in REFACTOR_MOCKUP.md.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 3A: Build `mockup-feedback-annotate` (annotation overlay)

**This is real engineering, not skill authoring.**

**Components to build:**
1. **Overlay JS bundle** (vanilla or lit, per Task 3.0 decision)
   - Captures clicks on elements with `data-spec-element` attributes
   - Resolves the click target up the DOM to the nearest `data-spec-screen`
   - Shows an annotation popover (text input + submit)
   - Posts the annotation to the in-page handler
2. **In-page handler:**
   - Writes annotations to `_feedback/sessions/<sid>.json` (via fetch to a dev-server endpoint, or download-as-file)
3. **The skill itself** (`mockup-feedback/annotate/SKILL.md`):
   - Inputs: walkthrough output dir
   - Outputs: walkthrough with overlay injected, OR mocked dev-server endpoint
   - References: the overlay bundle and handler

**Sub-plan blocker:** Task 3.0 (forge-concept findings dictate runtime).

**Acceptance criteria:**
- User clicks an element on a walkthrough page, types a comment, submits
- A new annotation appears in `_feedback/sessions/<sid>.json` with `{target, comment, timestamp}` and a precise target ref
- Provisional IDs are flagged in the annotation
- Works on `walkthrough-mockup-static-html` output

---

## Task 3B: Build `mockup-feedback-{triage, patch, apply}` (3 skills)

Each is a separate sub-plan.

**Triage:**
- Reads `_feedback/sessions/<sid>.json`
- Classifies each annotation: bug / copy / layout / scope / out-of-scope
- Routes to the right artifact path (which file owns this concern)
- Outputs `_feedback/triage/<sid>.json`
- Prompts user to promote provisional IDs (per hybrid strategy)

**Patch:**
- Reads triage output
- For each item: generates a section-level diff to the target file (if markdown) or line-level diff (if JSON)
- Outputs `_feedback/patches/<sid>.json` (proposed diffs, not applied)
- Surfaces the diffs to the user for approval

**Apply:**
- Reads approved patches
- Applies each diff atomically with git
- Appends an entry to `_feedback/devlog.md` per the §5 format
- Records `_feedback/applied/<sid>.json` (audit trail)

**Sub-plan blocker:** Task 3A (annotate must produce session JSONs first).

---

## Task 3C: Build `walkthrough-mockup-{lit, astro, framework}`

Each renderer skill must honor the same input contract as `walkthrough-mockup-static-html` (Task 2F) and emit `data-spec-*` attributes.

**Sub-plan per skill** with:
- Build target (Lit web components / Astro islands / Next or Nuxt per stack profile)
- Same I/O contract as static-html
- Acceptance: feedback loop from Task 3A works on its output

**Astro is the priority** since it's the standard-app default.

**Sub-plan blocker:** Task 3A complete, so the loop can be tested end-to-end on each renderer.

---

## Task 3D: Build `lab/compile-bundle`

**Inputs:** `flows/<name>.flow.yaml`
**Outputs:** `bundles/<name>.bundle.yaml`

**Acceptance:** the generated bundle matches the hand-authored bundles from Task 2H (regenerate them and `git diff` should be empty).

**Sub-plan blocker:** flows from Task 2H must exist.

---

## Task 3E: Build `lab/archive` (devlog rollup)

**Inputs:** `_feedback/devlog.md`
**Outputs:** `_feedback/devlog.archive/<YYYY-Q[1-4]>.md` (rollup) + truncated `_feedback/devlog.md`

**Trigger:** when `_feedback/devlog.md` exceeds 500 entries.

**Sub-plan blocker:** Task 3B-apply must exist (it writes the devlog this skill rolls up).

---

## Task 3F: End-to-end test of feedback loop

**Goal:** verify the full loop works on a sample project.

**Steps:**
1. Author a tiny sample concept (1 feature, 2 screens) under `_test/sample-project/`.
2. Run `walkthrough-mockup-static-html` on it.
3. Run `mockup-feedback-annotate` to inject the overlay.
4. Manually click an element, add an annotation, submit.
5. Run `triage` → `patch` → `apply`.
6. Verify the screen.md was patched, devlog entry appended.
7. Re-run walkthrough — verify the agent reads the devlog and the patched element renders correctly.

**Acceptance:** all steps complete without manual intervention beyond the click + annotation.

---

## Task 3G: Migrate hand-authored bundles → auto-generated from flows

After `lab/compile-bundle` (Task 3D) is verified:

1. Generate bundles from flows.
2. `git diff` should match the hand-authored bundles.
3. Replace hand-authored bundles with generated ones in the repo.
4. Add a CI hook that fails if `lab/compile-bundle` produces a different output than what's committed.

**Sub-plan blocker:** Task 3D + 3F.

---

# Resumability / how to pick this up in a new session

**Each Task in Phase 1 is a single atomic commit.** If a session ends mid-task (working tree dirty, no commit yet), the next session has two recovery options:

**Option A — Discard partial work and restart the task** (recommended):

```bash
cd /mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup
git status --short
# If dirty:
git stash
# Verify clean:
git status --short
# Identify the last completed task:
git log --oneline | head -10
# Resume at the next task in the plan, starting from Step N.1
```

**Option B — Inspect the partial state and finish manually**: only do this if the partial work represents nontrivial decisions (e.g. DOMAIN.md disposition in Task 1.4) that you don't want to redo. Walk the task's steps from the partial state; verify each step before commit.

**Source of truth for "what's done":**

1. `git log --oneline | head -20` shows committed task progress. The commit message header (`refactor: split skaileup-discovery → ...`) maps to a task ID by inspection.
2. The plan's checkboxes (`- [ ]` → `- [x]`) are NOT updated by Phase 1 execution — too brittle. Trust git log.

For Phase 2 and Phase 3, each task is its own mini-plan. Track sub-plan completion in `docs/devlog/<task-id>-<skill-name>.md`'s checkboxes per the writing-plans skill's checkbox convention.

---

# Rollback procedure

If Phase 1 produces a broken state:

```bash
cd /mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup
git checkout main
git branch -D refactor/skill-graph
```

This discards all Phase 1 work. The repo returns to pre-migration state.

If you want to roll back a single Phase 1 task without discarding the whole branch:

```bash
git log --oneline | head -10
# Find the SHA before the bad task
git reset --hard <good-sha>
```

⚠ Only do this BEFORE pushing to remote.

---

# Conventions for executing this plan

- One task = one commit. No squashing within Phase 1.
- Use the commit message templates in this plan verbatim — they document intent for future readers.
- Always run verification steps before commit. If a verification fails, fix the issue (don't skip).
- If you discover a missing migration (a skill not covered by Tasks 1.3-1.12), document it in a new sub-task in this plan and add it to the next commit.
- Use `git mv` over `mv` so git tracks the rename properly (preserves history).

---

# Out-of-scope explicitly

The following are NOT covered by this plan and require separate planning:

- Updating consumer repos (`skaile-dev` shell, `forge-concept`, etc.) that reference the old skaileup-* paths
- Bumping CHANGELOG.md per domain (left as Phase 1.5 if needed)
- Running `lab/compile-validators` against the renamed skills (skill bodies haven't changed semantically; defer to Phase 2)
- Performance / size optimization of the catalog
- Documentation site (Starlight) regeneration

These can be opened as follow-up issues after Phase 1 ships.
