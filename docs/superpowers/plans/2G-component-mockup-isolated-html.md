# Task 2G — `component-mockup-isolated-html` Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This is a **mini-plan** — a sub-plan of `docs/superpowers/plans/2026-05-07-skill-graph-migration.md` (Phase 2, Task 2G).

**Goal:** Author the `component-mockup-isolated-html` skill — a low-friction component visualizer that emits one standalone HTML file per component declared in `experience/components/*.md`, embeds tokens from `design/tokens.json` as inline CSS custom properties (no external CSS, no JS, no build), and renders every declared variant × state combination side-by-side in a labeled grid. Output target: `_concept/component-mockup/isolated-html/<component>.html`. Files must be openable directly via `file://`.

**Architecture:**
- A single `SKILL.md` authored under `component-mockup/isolated-html/` (the directory does NOT exist at plan time — see Pre-flight PF-5; the first authoring task creates it). The skill DSL body owns the rendering procedure and references the rendered-HTML contract verbatim.
- A small `validator.py` (alongside SKILL.md) that takes a generated `_concept/component-mockup/isolated-html/` directory and verifies: (a) one HTML file per source component, (b) every CSS variable referenced in inline `style=`/`<style>` declarations is also defined in the inline `:root { --token-* }` block, (c) all declared variants × states from the source component frontmatter are present as labeled cells in the rendered grid, (d) no external `<link rel="stylesheet">`, no `<script src=>`, no framework runtime markers (zero-build invariant).
- A fixture component under `component-mockup/isolated-html/tests/fixtures/<name>/` plus an expected-output snapshot the validator self-tests against.
- Rendering technology decision: **stdlib-only Python string templating** with `html.escape`, `pathlib`, `json`, and `PyYAML` for frontmatter parsing — same choice as Task 2F (`walkthrough-mockup-static-html`). Rationale recorded in PF-8.
- Deterministic output ordering (alpha by component file stem; variants and states in source order from frontmatter, with `default` first if present) so re-renders produce stable diffs.

**Tech Stack:** Markdown (skill DSL per `contracts/skill_grammar.md`), YAML frontmatter (per `contracts/asset_frontmatter.md`), Python 3.12+ for the validator (`PyYAML` + stdlib `json`/`pathlib`/`html`/`re`). Produced HTML uses CSS custom properties only — no JS, no framework, no build.

---

## Pre-flight

- [ ] **PF-1: Confirm cwd is repo root.**

  Run: `pwd`
  Expected: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`

- [ ] **PF-2: Confirm git working tree status.**

  Run: `git status -sb`
  Expected: branch matches the Phase 2 working branch; no uncommitted changes that would conflict with new files under `component-mockup/isolated-html/`.

- [ ] **PF-3: Confirm sibling skill exists for tone/structure reference.**

  Run: `test -r component-mockup/storybook/orchestrator/SKILL.md && echo OK`
  Expected: `OK`. The `component-mockup-storybook` skill is the **sister** skill (high-fi catalog vs. this skill's static-no-build approach). This skill must NOT duplicate its responsibilities — see Boundary section below.

- [ ] **PF-4: Confirm all source documents are readable.**

  Run:
  ```
  test -r REFACTOR_MOCKUP.md && \
  test -r SKILL_GRAPH.md && \
  test -r CONTRIBUTING.md && \
  test -r contracts/asset_frontmatter.md && \
  test -r contracts/frontmatter.md && \
  test -r contracts/skill_grammar.md && \
  test -r design/brand-visual/references/tokens_schema.md && \
  echo OK
  ```
  Expected: `OK`.

- [ ] **PF-5: Verify the target directory state.**

  Run: `ls component-mockup/`
  Expected output (at plan time) is exactly: `DOMAIN.md  storybook/`. **Note:** the parent plan stub assumes Phase 1 scaffolded `component-mockup/isolated-html/`, but it did NOT. The first authoring task (Task 1 below) creates the directory. If `isolated-html/` already exists with content when execution begins, run `ls component-mockup/isolated-html/` to verify it's empty before overwriting.

- [ ] **PF-6: Inspect the existing `experience/components/` SKILL.md to confirm the components-frontmatter shape.**

  Run: `head -50 experience/components/SKILL.md`
  Expected: skill exists at `experience/components/SKILL.md` (already migrated in Phase 1, name `experience-components`). Note its **output path** is `_concept/experience/screens/components/<name>.md` (not `_concept/experience/components/`). This skill MUST read from that path. See "Pinned component frontmatter shape" below for the canonical structure.

- [ ] **PF-7: Skim sister skill for tone alignment.**

  Run: `wc -l component-mockup/storybook/orchestrator/SKILL.md`
  Expected: > 0. Skim the frontmatter (`metadata.prerequisites`, `tags`, `parameters.depth`), `Overview`, `Prerequisites`, `Workflow` ordering, and the `When NOT to Use` section. This skill should sit **next** to it stylistically (same depth of body, same `prerequisites` form, same `EMIT` cadence) but differ in scope — see Boundary section below.

- [ ] **PF-8: Decide rendering technology.**

  **Decision: stdlib-only Python string templating** using `html.escape`, `pathlib`, `json`, `re`, and `PyYAML` (already a repo dependency for frontmatter parsing). No Jinja, no Mako, no build tool.

  Rationale: (1) the produced HTML is **zero-build by acceptance criterion**, but the renderer that *generates* the HTML runs at skill-execution time and never ships in the output — its dependencies don't bleed through; (2) Task 2F (`walkthrough-mockup-static-html`) made the same choice — consistency across the mockup-renderer family wins; (3) the templates are small (one page template, one variant-grid section template, one inline-style block template), so 3-line `format()` substitution is cheaper than a templating-engine dependency; (4) every other validator in this repo uses stdlib + PyYAML. Record this decision verbatim in the SKILL.md `Overview` section so future component-mockup variant authors stay consistent.

- [ ] **PF-9: Read the load-bearing source sections (mandatory before Task 1).**

  - `REFACTOR_MOCKUP.md` § 1 (component vs. application mocking — audience, unit, contract), § 3 (component-mockup tiers — confirms storybook vs. isolated-html boundary), § 9 (tier composition — confirms isolated-html targets simple-app), § 13 (summary — three-cluster layout).
  - `SKILL_GRAPH.md` § 4 (concept-group artefact flow — confirms input set: components + tokens), § 7 (workspace zones — confirms `_concept/component-mockup/` is permanent output zone).
  - `CONTRIBUTING.md` § "SKILL.md Format" + § "Naming Conventions" (path-based name = `component-mockup-isolated-html`).
  - `contracts/asset_frontmatter.md` § "Skill — SKILL.md" + the `metadata.prerequisites` schema.
  - `contracts/skill_grammar.md` — full DSL.
  - `contracts/frontmatter.md` § "experience/screens/\<group\>/\<screen\>.md" — for context only; component frontmatter is NOT defined there. The canonical component frontmatter comes from `experience/components/SKILL.md` Step 5 — see "Pinned component frontmatter shape" below.
  - `design/brand-visual/references/tokens_schema.md` — full file. The canonical `tokens.json` shape is pinned there. See "Pinned tokens-inlining strategy" below.
  - `component-mockup/storybook/orchestrator/SKILL.md` — sibling skill, used for stylistic alignment only (its content is **not** authoritative for this skill).

---

## Authoritative spec excerpts

### From `REFACTOR_MOCKUP.md` § 3 — component-mockup tier table (verbatim)

| Skill | Use when |
|---|---|
| `component-mockup-storybook` | Standard/complex apps with shared component library |
| `component-mockup-isolated-html` | mvp/simple apps where Storybook is overkill |

**`component-mockup-isolated-html`** (verbatim):
- Reads `experience/components/*.md` and `design/tokens.json`
- Produces `_concept/component-mockup/isolated-html/<component>.html`
- One file per component, no JS, no build, no framework
- Useful early in design before committing to a component library

### From parent plan Task 2G — acceptance criteria (verbatim)

- Standalone HTML page per component, no framework, no build
- Shows all variants/states declared in component frontmatter
- Embeds `tokens.json` values inline (no external CSS load)

### From `REFACTOR_MOCKUP.md` § 9 — tier composition (component-mockup row, verbatim)

```
                                        mvp  simple  standard  complex
   component-mockup-storybook                          ✓         ✓
   component-mockup-isolated-html             ✓
```

This skill targets **simple-app**. The bundle composition for `simple-app` (Task 2H) will install this skill.

### Boundary against `component-mockup-storybook` (sister skill)

| Aspect | `component-mockup-isolated-html` (this) | `component-mockup-storybook` (sibling) |
|---|---|---|
| Tier | mvp / simple-app | standard-app / complex-app |
| Output | `<component>.html` per component, openable via `file://` | full Storybook 8 site under `_concept/experience/4_storybook/` |
| Build | none | runs `storybook dev` / `storybook build` |
| Interactivity | none (static grid) | controls panel, knobs, args |
| Framework dependency | none | tech-stack-aware (resolves from `impl-architecture/templates/`) |
| Scope | one HTML per component, all variants × states in a labeled grid | three-layer (components + screens + journeys) |
| Audience | early-design quick reference | design-system + dev review |

This skill MUST NOT emit Storybook stories, MUST NOT depend on a tech stack, and MUST NOT consume `experience/screens/*.md` (that's a screen-level concern).

---

## Pinned component frontmatter shape (the input contract)

> **Source:** `experience/components/SKILL.md` Step 5 (verbatim). This is the canonical shape this skill consumes. The shape is NOT in `contracts/frontmatter.md` — that file documents screen frontmatter, not component frontmatter. If the executing agent finds drift between `experience/components/SKILL.md` and this excerpt, **stop and flag** before continuing.

```yaml
---
pattern: data_table
library_component: PrimeVue DataTable
used_in:
  - experience/screens/02_dashboard/overview.md
  - experience/screens/03_tasks/task_list.md
data_entities: [task, user]
last_updated: YYYY-MM-DD
---

# Component: Data Table

## Purpose
...

## Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| ... |

## Variants
- **Default:** full table with pagination, sorting, filtering
- **Compact:** reduced padding, smaller font, no row hover
- **Selectable:** checkbox column, bulk action bar appears on selection

## States
- **Loading:** skeleton rows matching column count
- **Empty:** empty state component with message
- **Error:** error banner above table with retry action
- **Populated:** normal data display

## Anatomy
~~~text
┌─────────────────────────────────────────┐
│ ASCII wireframe                         │
└─────────────────────────────────────────┘
~~~
```

### Fields this skill consumes (and how)

| Field / Section | Source | Used by this skill |
|---|---|---|
| `pattern` (frontmatter) | YAML | Page title prefix + grouping in body |
| `library_component` (frontmatter) | YAML | Sub-title note ("rendered as: PrimeVue DataTable") — informational only, no actual library resolution |
| `used_in` (frontmatter) | YAML | Optional "Used in" footer linking back to screen specs |
| `data_entities` (frontmatter) | YAML | Optional metadata footer |
| `last_updated` (frontmatter) | YAML | Footer timestamp |
| `## Purpose` (body) | Markdown H2 section | Rendered as `<p>` under page title |
| `## Variants` (body) | Markdown H2 with `- **Name:** description` bullets | Each `**Name:**` becomes a column header in the variant × state grid |
| `## States` (body) | Markdown H2 with `- **Name:** description` bullets | Each `**Name:**` becomes a row label in the variant × state grid |
| `## Anatomy` (body, optional) | fenced `~~~text` block | Rendered as `<pre>` under the grid |

### Constraint: this skill does NOT consume the `elements:` block

The `elements:` block (Task 2.0 contract) is screen-level — it lives on `experience/screens/<group>/<screen>.md`, not on component files. This skill operates on components and MUST NOT read `elements:`. The executing agent MUST verify this in Task 2's frontmatter parser tests.

### What if a component file lacks `## Variants` or `## States`?

- Missing `## Variants`: render a single-column grid with header `default`.
- Missing `## States`: render a single-row grid with row label `default`.
- Missing both: render a single cell labeled `default × default` (still a labeled grid; preserves the contract).

---

## Pinned tokens-inlining strategy

> **Source:** `design/brand-visual/references/tokens_schema.md` (verbatim shape). If `design/tokens.json` does NOT yet exist in a project where the skill runs, the skill MUST emit a hard error pointing the user at `brand-visual` (mirrors the storybook sibling's hard gate).

### Token shape (verbatim from `tokens_schema.md`)

```json
{
  "colors": {
    "primary": "#6366f1",
    "secondary": "#0ea5e9",
    "accent": "#f59e0b",
    "background": "#0f172a",
    "surface": "#1e293b",
    "text": "#f8fafc",
    "text_muted": "#94a3b8",
    "border": "#334155",
    "error": "#ef4444",
    "success": "#22c55e",
    "warning": "#f59e0b"
  },
  "fonts": { "heading": "...", "body": "...", "mono": "..." },
  "radius": "8px",
  "mode": "dark",
  "spacing_base": "8px",
  "shadows": { "sm": "...", "md": "...", "lg": "..." },
  "atmosphere": { "type": "...", "description": "..." },
  "tailwind": { "--color-primary": "#...", ... }
}
```

If `design/tokens.json` does not exist at plan time, the executing agent MUST flag this for confirmation. The skill should propose the minimal shape `{colors, fonts, radius, mode, spacing_base}` as a fallback if the user confirms greenfield.

### Flattening rule: dotted JSON path → `--token-<segments-joined-by-hyphen>`

| JSON path | CSS variable |
|---|---|
| `colors.primary` | `--token-colors-primary` |
| `colors.text_muted` | `--token-colors-text-muted` (underscore → hyphen) |
| `fonts.heading` | `--token-fonts-heading` |
| `radius` | `--token-radius` |
| `spacing_base` | `--token-spacing-base` |
| `shadows.sm` | `--token-shadows-sm` |
| `atmosphere.type` | `--token-atmosphere-type` |
| `tailwind.--color-primary` | **passthrough** (already a CSS var name): emit as `--color-primary` directly inside `:root { ... }` |

**Naming convention rules (pinned, MUST be preserved):**

1. Prefix is always `--token-` for nested-path variables (so they don't collide with the `tailwind:` block's variables, which are passed through as-is).
2. Path segments are joined with single hyphens.
3. Underscores within a path segment become single hyphens (`text_muted` → `text-muted`).
4. Camel-case segments (none expected per the schema, but defensive) become kebab via lowercase + hyphen-before-capital.
5. Object values that aren't strings (e.g., `atmosphere`, `shadows`) are flattened recursively. If a leaf value is non-string, it MUST be JSON-stringified and embedded as a CSS string (e.g., `--token-atmosphere: '{"type":"radial_gradient",...}'`) — but the renderer SHOULD only emit string-leaf variables; non-string leaves are skipped with a warning to keep CSS valid.
6. The `tailwind:` block is emitted **after** the flattened tree so that any same-named override wins (Tailwind block authoritative for production-aligned values).

**Embedding placement:** all variables are emitted inside a single `<style>...</style>` block in the document `<head>`, scoped to `:root { ... }`. No external `<link rel="stylesheet">` is permitted.

---

## Pinned rendered-HTML contract

Each generated file MUST conform to the following shape (this is the contract every component HTML page MUST satisfy; the validator enforces it):

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Component: {{ pattern_human }} — {{ component_stem }}</title>
  <style>
    :root {
      /* flattened tokens (see Pinned tokens-inlining strategy) */
      --token-colors-primary: #6366f1;
      --token-colors-text: #f8fafc;
      /* ...all tokens, then tailwind passthrough block last... */
      --color-primary: #6366f1;
      --color-foreground: #f8fafc;
      --radius: 0.5rem;
    }
    /* base reset + grid layout, all vars referenced are defined above */
    body { font-family: var(--token-fonts-body); color: var(--token-colors-text); background: var(--token-colors-background); margin: 0; padding: 24px; }
    .grid { display: grid; gap: 16px; grid-template-columns: 120px repeat(var(--cols), 1fr); align-items: start; }
    .grid-header, .grid-row-label { color: var(--token-colors-text-muted); font-size: 12px; text-transform: uppercase; }
    .cell { border: 1px solid var(--token-colors-border); border-radius: var(--token-radius); padding: 12px; background: var(--token-colors-surface); }
  </style>
</head>
<body>
  <header>
    <h1>Component: {{ pattern_human }}</h1>
    <p class="subtitle">{{ purpose_paragraph }}</p>
    <p class="meta">Library mapping: {{ library_component }} · Last updated: {{ last_updated }}</p>
  </header>

  <section class="variant-state-grid" style="--cols: {{ n_variants }};">
    <!-- top-left empty cell -->
    <div></div>
    <!-- column headers: variants -->
    <div class="grid-header">{{ variant_1 }}</div>
    <div class="grid-header">{{ variant_2 }}</div>
    ...
    <!-- row 1 -->
    <div class="grid-row-label">{{ state_1 }}</div>
    <div class="cell" data-variant="{{ variant_1 }}" data-state="{{ state_1 }}">
      <!-- placeholder rendering of the component for variant_1 × state_1 -->
    </div>
    <div class="cell" data-variant="{{ variant_2 }}" data-state="{{ state_1 }}">...</div>
    ...
  </section>

  <section class="anatomy">
    <h2>Anatomy</h2>
    <pre>{{ anatomy_ascii }}</pre>
  </section>

  <footer>
    <h2>Used in</h2>
    <ul>
      <li><a href="../../experience/screens/02_dashboard/overview.md">02_dashboard/overview</a></li>
    </ul>
  </footer>
</body>
</html>
```

### Variant × state grid shape (pinned)

- **Layout:** CSS Grid, `grid-template-columns: 120px repeat(N, 1fr)` where `N = number of variants`.
- **Top-left cell:** empty (the corner where row labels meet column headers).
- **Column headers:** one per variant, in source order from `## Variants`. If the frontmatter has no variants section, render a single column labeled `default`.
- **Row labels:** one per state, in source order from `## States`. If no states section, render a single row labeled `default`. If a state named `default` exists, it is rendered first regardless of source order.
- **Cells:** every variant × state combination has exactly one `<div class="cell">` element. The cell carries `data-variant="{name}"` and `data-state="{name}"` attributes for traceability (NOT `data-spec-*` — those are walkthrough-renderer attributes; this skill is component-isolated).
- **Cell body:** placeholder rendering — for v1, the cell renders the component name + variant + state as a small swatch using token-driven styles. The actual component visual is a best-effort approximation derived from `pattern` + `library_component` (e.g., a `data_table` pattern renders a tiny mock table; a `status_badge` renders a span with token color). Pattern-to-mock mapping is documented in `references/pattern_mocks.md` (see Task 7).
- **Anatomy:** if `## Anatomy` exists in the source, render it after the grid as a `<pre>` block (preserves the ASCII wireframe).

### Self-containment invariants (validator enforces)

- No `<link rel="stylesheet" href=...>` element anywhere.
- No `<script>` element anywhere (neither inline nor `src`-loaded).
- No `<img>` referencing an external URL (relative paths to local assets only, with a warning).
- Every CSS variable referenced inside any `style="..."` attribute or inside the `<style>` block (matched by `var(--...)`) MUST be defined inside the `:root { ... }` block emitted by the token inliner. Undefined references are validator-fatal.

---

## Output-file naming (pinned)

| Source | Output |
|---|---|
| `_concept/experience/screens/components/data_table.md` | `_concept/component-mockup/isolated-html/data_table.html` |
| `_concept/experience/screens/components/status_badge.md` | `_concept/component-mockup/isolated-html/status_badge.html` |
| `_concept/experience/screens/components/empty_state.md` | `_concept/component-mockup/isolated-html/empty_state.html` |

Rule: file stem is preserved verbatim (lowercase + underscore per `experience-components` Step 5). Output extension is `.html`. No nesting; all files sit flat under `_concept/component-mockup/isolated-html/`.

> **Note** that the source path is `_concept/experience/screens/components/<name>.md` (per the existing `experience-components` skill's `produces:` block), NOT `_concept/experience/components/`. The executing agent MUST confirm this by reading `experience/components/SKILL.md` Step 5 before wiring up the input parser.

---

## Naming verification (per CONTRIBUTING.md)

- The directory under repo root is `component-mockup/isolated-html/`.
- Per CONTRIBUTING.md path-based naming: `component-mockup/isolated-html/SKILL.md` → `name: component-mockup-isolated-html`. Path with `/` replaced by `-`. **Confirmed.**
- The `name:` field in SKILL.md frontmatter MUST be exactly `component-mockup-isolated-html` (kebab-case, matches the parent directory chain).

---

## File targets

All paths absolute under repo root `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/`:

- **Create:** `component-mockup/isolated-html/SKILL.md` — the skill manifest + DSL body
- **Create:** `component-mockup/isolated-html/validator.py` — the output validator
- **Create:** `component-mockup/isolated-html/references/pattern_mocks.md` — pattern-to-mock-rendering registry
- **Create:** `component-mockup/isolated-html/references/tokens_inlining.md` — flattening + naming rules (referenced from SKILL.md REFERENCES section)
- **Create:** `component-mockup/isolated-html/tests/fixtures/minimal/component.md` — minimal fixture component
- **Create:** `component-mockup/isolated-html/tests/fixtures/minimal/tokens.json` — minimal fixture tokens
- **Create:** `component-mockup/isolated-html/tests/fixtures/minimal/expected.html` — snapshot of expected rendered output
- **Create:** `component-mockup/isolated-html/tests/test_validator.py` — pytest covering parser, inliner, renderer, validator

---

## Tasks (step ordering: input parser → variant/state expansion → token inliner → HTML renderer → validator/tests last)

### Task 1: Scaffold skill directory + minimal SKILL.md frontmatter

**Files:**
- Create: `component-mockup/isolated-html/SKILL.md`

- [ ] **Step 1: Create the directory.**

  Run: `mkdir -p component-mockup/isolated-html/{references,tests/fixtures/minimal}`
  Verify: `ls component-mockup/isolated-html/` shows `references/  tests/`.

- [ ] **Step 2: Write SKILL.md frontmatter ONLY (body comes in Task 8).**

  Place at `component-mockup/isolated-html/SKILL.md`:

  ```yaml
  ---
  name: component-mockup-isolated-html
  description: "Use when components are specced and an mvp/simple-app team needs a quick visual reference without a Storybook build. Renders one standalone HTML file per component showing all variants × states in a token-driven grid; no JS, no framework, openable via file://."
  metadata:
    version: '1.0.0'
    tags:
      - 'components'
      - 'mockup'
      - 'isolated'
      - 'static-html'
      - 'tokens'
      - 'no-build'
      - 'low-fidelity'
      - 'simple-app'
    stage: alpha
    source: NEW
    parameters:
      depth:
        type: enum
        values: [none, light, medium, max]
        default: medium
    prerequisites:
      files:
        - path: '_concept/experience/screens/components'
          gate: hard
          description: 'Component specs required — one HTML output per component spec.'
          min_entries: 1
        - path: '_concept/discovery/brand/tokens.json'
          gate: hard
          description: 'Design tokens required to embed CSS variables inline.'
      produces:
        - path: '_concept/component-mockup/isolated-html'
          description: 'One standalone HTML file per component, openable via file://.'
  ---
  ```

- [ ] **Step 3: Verify frontmatter parses as valid YAML.**

  Run: `python3 -c "import yaml; yaml.safe_load(open('component-mockup/isolated-html/SKILL.md').read().split('---')[1])"`
  Expected: no exception.

- [ ] **Step 4: Commit.**

  ```bash
  git add component-mockup/isolated-html/SKILL.md
  git commit -m "scaffold: component-mockup-isolated-html SKILL.md frontmatter"
  ```

### Task 2: Author the input parser (component frontmatter + body sections)

**Files:**
- Create: `component-mockup/isolated-html/scripts/parse_component.py`

- [ ] **Step 1: Write failing test for `parse_component_md` happy path.**

  Place at `component-mockup/isolated-html/tests/test_parse_component.py`:

  ```python
  from pathlib import Path
  from scripts.parse_component import parse_component_md

  FIXTURE = """---
  pattern: data_table
  library_component: PrimeVue DataTable
  used_in: [experience/screens/02_dashboard/overview.md]
  data_entities: [task]
  last_updated: 2026-05-07
  ---

  # Component: Data Table

  ## Purpose
  Sortable, filterable, paginated table.

  ## Variants
  - **Default:** full table
  - **Compact:** reduced padding

  ## States
  - **Loading:** skeleton rows
  - **Empty:** empty state
  - **Populated:** normal data
  """

  def test_parses_frontmatter_and_sections(tmp_path):
      f = tmp_path / "data_table.md"
      f.write_text(FIXTURE)
      result = parse_component_md(f)
      assert result.pattern == "data_table"
      assert result.library_component == "PrimeVue DataTable"
      assert result.variants == ["Default", "Compact"]
      assert result.states == ["Loading", "Empty", "Populated"]
      assert "Sortable" in result.purpose
      assert result.stem == "data_table"
  ```

  Run: `cd component-mockup/isolated-html && python3 -m pytest tests/test_parse_component.py -v`
  Expected: ImportError / module-not-found.

- [ ] **Step 2: Implement `parse_component.py`.**

  Build a `Component` dataclass with: `stem, pattern, library_component, used_in, data_entities, last_updated, purpose, variants, states, anatomy`. Parser logic:
  - Split on `^---$` to extract YAML frontmatter (use PyYAML `safe_load`).
  - Find each H2 section (`^## (Purpose|Variants|States|Anatomy)$`) by regex.
  - For Variants/States: extract `- **NAME:** description` bullets via `re.findall(r"^\s*-\s*\*\*([^:]+):\*\*", body, re.M)`.
  - For Anatomy: capture content of the first fenced `~~~text` block.
  - Default sentinels: missing variants → `["default"]`; missing states → `["default"]`.
  - Move `default` to position 0 if it appears later in the list.

- [ ] **Step 3: Run test until green.**

  Run: `cd component-mockup/isolated-html && python3 -m pytest tests/test_parse_component.py -v`
  Expected: PASS.

- [ ] **Step 4: Add edge-case tests (missing sections, anatomy block, weird whitespace) and iterate.**

- [ ] **Step 5: Commit.**

  ```bash
  git add component-mockup/isolated-html/scripts/parse_component.py component-mockup/isolated-html/tests/test_parse_component.py
  git commit -m "feat(isolated-html): component frontmatter + section parser"
  ```

### Task 3: Author the variant × state expander

**Files:**
- Create: `component-mockup/isolated-html/scripts/expand_grid.py`

- [ ] **Step 1: Write failing test.**

  ```python
  from scripts.expand_grid import expand
  def test_cartesian_with_default_first():
      cells = expand(variants=["Default","Compact"], states=["Loading","Default","Populated"])
      # default state moved to position 0
      assert cells[0] == ("Default","Default")
      assert cells[1] == ("Compact","Default")
      assert len(cells) == 6
  ```

  Run: `python3 -m pytest tests/test_expand_grid.py -v`
  Expected: ImportError.

- [ ] **Step 2: Implement `expand_grid.py` (small pure function returning list of `(variant, state)` tuples in row-major order with `default` first).**

- [ ] **Step 3: Run test green.**

- [ ] **Step 4: Commit.**

### Task 4: Author the token inliner

**Files:**
- Create: `component-mockup/isolated-html/scripts/inline_tokens.py`
- Create: `component-mockup/isolated-html/references/tokens_inlining.md` (the rules table from "Pinned tokens-inlining strategy")

- [ ] **Step 1: Write failing test for the flattening rule.**

  ```python
  from scripts.inline_tokens import flatten_to_css_vars
  def test_flatten_basic():
      tokens = {
          "colors": {"primary": "#6366f1", "text_muted": "#94a3b8"},
          "radius": "8px",
          "tailwind": {"--color-primary": "#6366f1", "--radius": "0.5rem"}
      }
      vars = flatten_to_css_vars(tokens)
      assert "--token-colors-primary: #6366f1;" in vars
      assert "--token-colors-text-muted: #94a3b8;" in vars
      assert "--token-radius: 8px;" in vars
      # tailwind block passes through, last (so it can override)
      passthrough_idx = vars.index("--color-primary: #6366f1;")
      flattened_idx = vars.index("--token-colors-primary: #6366f1;")
      assert passthrough_idx > flattened_idx
  ```

- [ ] **Step 2: Implement `flatten_to_css_vars(tokens) -> list[str]`** following the rules table in `references/tokens_inlining.md`. Skip non-string leaves with a warning.

- [ ] **Step 3: Add `render_root_block(vars) -> str`** that wraps the variable list in `:root { ... }`.

- [ ] **Step 4: Run tests green.**

- [ ] **Step 5: Commit.**

### Task 5: Author the HTML renderer (orchestrates parser + expander + inliner)

**Files:**
- Create: `component-mockup/isolated-html/scripts/render_component_html.py`
- Create: `component-mockup/isolated-html/references/pattern_mocks.md` (registry of pattern → cell-body mock HTML snippets)

- [ ] **Step 1: Write failing test for `render_html(component, tokens) -> str`.**

  ```python
  from scripts.render_component_html import render_html
  def test_renders_grid_and_inline_style(minimal_component, minimal_tokens):
      html = render_html(minimal_component, minimal_tokens)
      assert "<!doctype html>" in html.lower()
      assert "<style>" in html
      assert "--token-colors-primary" in html
      assert 'data-variant="Default"' in html
      assert 'data-state="Default"' in html
      # zero-build invariants
      assert "<link" not in html.lower() or "stylesheet" not in html.lower()
      assert "<script" not in html.lower()
  ```

- [ ] **Step 2: Implement the renderer** using stdlib `string.Template` or f-strings. Pull token block from `inline_tokens`, grid cells from `expand_grid`, and emit the page per the pinned rendered-HTML contract. Pattern-to-mock mapping comes from `references/pattern_mocks.md` (start with: `data_table`, `status_badge`, `card`, `form`, `empty_state`, `confirm_dialog`, plus a fallback `generic` swatch).

- [ ] **Step 3: Run tests green.**

- [ ] **Step 4: Commit.**

### Task 6: Author the orchestrator entrypoint

**Files:**
- Create: `component-mockup/isolated-html/scripts/run.py`

- [ ] **Step 1: Implement `run(components_dir, tokens_path, out_dir)`** that:
  1. Globs `components_dir/*.md` (excluding `_*.md`).
  2. Loads `tokens_path` JSON (hard-fail with actionable message if missing).
  3. For each component: parse → render → write `<stem>.html` to `out_dir`.
  4. Emit a one-line summary per file.

- [ ] **Step 2: Smoke test on the fixture.**

  Run from repo root:
  ```
  python3 component-mockup/isolated-html/scripts/run.py \
    --components component-mockup/isolated-html/tests/fixtures/minimal \
    --tokens component-mockup/isolated-html/tests/fixtures/minimal/tokens.json \
    --out /tmp/imc_smoke
  ls /tmp/imc_smoke/*.html
  ```
  Expected: at least one HTML file present.

- [ ] **Step 3: Commit.**

### Task 7: Build the fixture + snapshot the expected output

**Files:**
- Create: `component-mockup/isolated-html/tests/fixtures/minimal/component.md`
- Create: `component-mockup/isolated-html/tests/fixtures/minimal/tokens.json`
- Create: `component-mockup/isolated-html/tests/fixtures/minimal/expected.html`

- [ ] **Step 1: Author the minimal fixture component** (file stem `button.md`, pattern `generic`, two variants, three states, one anatomy block).

- [ ] **Step 2: Author a minimal tokens.json** matching the schema in `tokens_schema.md` (drop `atmosphere` if it complicates the test).

- [ ] **Step 3: Generate `expected.html`** by running the orchestrator once, then commit the output verbatim as the snapshot.

- [ ] **Step 4: Add a snapshot test** that re-runs the renderer and asserts `actual == expected.html` byte-for-byte.

- [ ] **Step 5: Commit.**

### Task 8: Author the validator

**Files:**
- Create: `component-mockup/isolated-html/validator.py`

- [ ] **Step 1: Write failing tests for each invariant** (one test per: file-per-component, all CSS vars defined, every variant×state cell present, no `<link>`/`<script>`, no external `<img>`).

- [ ] **Step 2: Implement the validator.**
  - Walk `_concept/component-mockup/isolated-html/*.html`.
  - For each, parse the inline `<style>` block, extract all `--*` definitions inside `:root { ... }`, and all `var(--*)` references in the document.
  - Assert references ⊆ definitions.
  - Assert exactly one `<div class="cell">` per variant × state (using `data-variant` + `data-state` attributes) by cross-referencing the source component file.
  - Assert no banned elements.
  - Exit code 0 on success, non-zero with line numbers on failure (mirror `contracts/scripts/validator_lib.py` pattern).

- [ ] **Step 3: Run validator on the snapshot.** Expected: exit 0.

- [ ] **Step 4: Mutate the snapshot (e.g., reference an undefined var) and confirm validator reports the violation.**

- [ ] **Step 5: Commit.**

### Task 9: Author the SKILL.md DSL body

**Files:**
- Modify: `component-mockup/isolated-html/SKILL.md`

- [ ] **Step 1: Append the SKILL.md body** following `contracts/skill_grammar.md`. Sections in order:
  - `# Component-Mockup — Isolated HTML`
  - `## Overview` — paraphrase the goal + record the stdlib-Python rendering decision (verbatim from PF-8 rationale).
  - `## When to Use` / `## When NOT to Use` (mvp/simple-app yes; standard-app+ → use `component-mockup-storybook`).
  - `## Prerequisites` — table mirroring `experience/components/SKILL.md` style with hard gates on components dir + tokens.json.
  - `## Boundary` — the storybook-vs-isolated-html table from the "Authoritative spec excerpts" section above.
  - `ROLE` line.
  - `READS` — `_concept/experience/screens/components/*.md`, `_concept/discovery/brand/tokens.json`.
  - `WRITES` — `_concept/component-mockup/isolated-html/<component>.html`.
  - `REFERENCES` — `component-mockup/isolated-html/references/tokens_inlining.md`, `component-mockup/isolated-html/references/pattern_mocks.md`, `contracts/skill_grammar.md`, `design/brand-visual/references/tokens_schema.md`.
  - `MUST` lines:
    - `MUST embed all tokens.json values as CSS custom properties inside a single :root block in the document <head>`
    - `MUST emit one HTML file per component, named <stem>.html under _concept/component-mockup/isolated-html/`
    - `MUST render every variant × state combination from the source component frontmatter as exactly one labeled grid cell`
    - `MUST run validator.py on every output and fix violations before completing the skill`
  - `NEVER` lines:
    - `NEVER emit <link rel=stylesheet>, <script>, or any external CSS/JS reference in produced HTML`
    - `NEVER consume the elements: block — that's screen-level; this skill operates on components`
    - `NEVER hardcode token values — always read from tokens.json and flatten via the pinned rule`
    - `NEVER add framework-specific code (React, Vue, Lit, Svelte) — output is plain HTML + inline CSS only`
  - `STEP 1..6` — parser → expander → inliner → renderer → write → validate.
  - `RUN python3 component-mockup/isolated-html/scripts/run.py ...` example.
  - `EMIT [component-mockup-isolated-html] started run_id=<uuid>` cadence.
  - `CHECKLIST` — six items mirroring the MUST list.

- [ ] **Step 2: Validate frontmatter + grammar.**

  Run: `python3 contracts/scripts/validate_skill_rules.py component-mockup/isolated-html/SKILL.md` (or whatever lint helper Phase 1 introduced — the executing agent should discover the right command).

- [ ] **Step 3: Commit.**

### Task 10: End-to-end smoke + plan-document review

- [ ] **Step 1: Run the orchestrator on the fixture and validate.**

  ```
  python3 component-mockup/isolated-html/scripts/run.py \
    --components component-mockup/isolated-html/tests/fixtures/minimal \
    --tokens component-mockup/isolated-html/tests/fixtures/minimal/tokens.json \
    --out /tmp/imc_e2e
  python3 component-mockup/isolated-html/validator.py /tmp/imc_e2e
  open /tmp/imc_e2e/button.html  # sanity check by eye
  ```
  Expected: validator exit 0; file opens directly in a browser via `file://` and shows the variant × state grid.

- [ ] **Step 2: Run the full pytest suite for this skill.**

  Run: `cd component-mockup/isolated-html && python3 -m pytest tests/ -v`
  Expected: all green.

- [ ] **Step 3: Verify naming integrity.**

  Run: `grep '^name:' component-mockup/isolated-html/SKILL.md`
  Expected: `name: component-mockup-isolated-html`.

- [ ] **Step 4: Cross-check the parent plan acceptance criteria.**

  Confirm verbatim:
  - [x] Standalone HTML page per component, no framework, no build
  - [x] Shows all variants/states declared in component frontmatter
  - [x] Embeds `tokens.json` values inline (no external CSS load)

- [ ] **Step 5: Commit final state and request plan-document review.**

---

## Definition of done

- `component-mockup/isolated-html/SKILL.md` exists, has frontmatter `name: component-mockup-isolated-html`, and a DSL body covering ROLE/READS/WRITES/REFERENCES/MUST/NEVER/STEP/CHECKLIST.
- `component-mockup/isolated-html/validator.py` exits 0 on the snapshot fixture and non-zero on a deliberately broken mutation of it.
- The orchestrator (`scripts/run.py`) renders one HTML file per component in the fixture; every file is openable via `file://` with no errors in the browser console.
- All CSS variables referenced in any rendered HTML are defined in the `:root { ... }` block of the same file.
- No `<link>`, `<script>`, or external resource references appear in any produced HTML.
- Snapshot test passes byte-for-byte.
- Pytest suite under `component-mockup/isolated-html/tests/` is fully green.
- The skill's `metadata.version` is `1.0.0`, `stage: alpha`, and the path-based naming rule is satisfied.
- The skill explicitly does **not** read the screen-level `elements:` block.
- Boundary against `component-mockup-storybook` is documented in the SKILL.md `## Boundary` section.

---

## Open questions / flags for the executing agent

1. **`design/tokens.json` location.** The pinned schema (`tokens_schema.md`) lives under `design/brand-visual/references/`, but the actual runtime path used by `experience-components/SKILL.md` is `_concept/discovery/brand/tokens.json`. The parent plan stub says `design/tokens.json`. The executing agent SHOULD confirm the canonical runtime path with the user and update the SKILL.md `prerequisites.files[].path` accordingly. Default in this plan: `_concept/discovery/brand/tokens.json` (matches the sibling `component-mockup-storybook` skill).
2. **Components directory path.** Parent plan stub says `experience/components/*.md`, but `experience/components/SKILL.md` writes to `_concept/experience/screens/components/<name>.md`. Plan defaults to the latter (matches `experience-components` `produces:`); flag for confirmation.
3. **Pattern-to-mock fidelity.** The placeholder cell renderings (`pattern_mocks.md`) are intentionally low-fi — they convey shape, not pixel parity. If the user wants higher-fi previews, the right path is `component-mockup-storybook`, not this skill. Confirm with the user before adding effort here.
4. **Bundle wiring.** Task 2H will wire `component-mockup-isolated-html` into `bundles/simple-app.bundle.yaml`. Out of scope for this mini-plan; flag it as a downstream dependency.
