---
title: "mockup-component-isolated-html"
description: "Use when components are specced and an mvp/simple-app team needs a quick visual reference without a Storybook build. Renders one standalone HTML file per component showing all variants × states in a token-driven grid; no JS, no framework, openable vi"
sidebar:
  label: "mockup-component-isolated-html"
---

:::note[Skill manifest]
**Name:** `mockup-component-isolated-html`
**Stage:** alpha · **Version:** 1.0.0
**Tags:** components, mockup, isolated, static-html, tokens, no-build, low-fidelity, simple-app
**Source:** [`skaileup/mockup-component/isolated-html/SKILL.md`](https://github.com/skaile-ai/ai-assets-skaileup/blob/main/skaileup/mockup-component/isolated-html/SKILL.md)
:::


# mockup-component — Isolated HTML

## Overview

Renders one standalone HTML page per component spec — variants × states in a
labeled grid, all styling driven by inlined CSS custom properties from
`_concept/discovery/brand/tokens.json`. **No build, no JS, no framework.** Each
output is a single `.html` file openable directly via `file://`. The skill is
the **early-design quick reference** for mvp/simple-app teams; once
component-library decisions are made, switch to `mockup-component-storybook`.

**Rendering technology decision (pinned):** stdlib-only Python string
templating with `html.escape`, `pathlib`, `json`, `re`, and `PyYAML`. No Jinja,
no Mako, no build tool. Same choice as `mockup-walkthrough-static-html` — the
mockup-renderer family is consistent on this point. The renderer's deps run
at skill-execution time and never ship in the produced HTML.

**Pinned input paths (resolved during execution):**

- Components dir: `_concept/experience/screens/components/` — matches the
  `produces:` field of `experience/components/SKILL.md`. (The parent plan stub
  said `experience/components/*.md`; the actual runtime path is the nested one.)
- Tokens path: `_concept/discovery/brand/tokens.json` — the runtime location
  shared with `experience-components` and `mockup-component-storybook`.

If either input is missing, the skill MUST refuse with a clear pointer at the
upstream skill that produces it.

## When to Use

- Components are specced (`_concept/experience/screens/components/*.md` exists).
- Tokens exist (`_concept/discovery/brand/tokens.json`).
- Team is on the **mvp** or **simple-app** tier, OR wants a quick
  pre-Storybook visual reference.
- User asks for "isolated mockup", "static HTML preview", "component sheet",
  "no-build component view".

## When NOT to Use

- Standard-app or complex-app tier — use `mockup-component-storybook` for the
  full 3-layer build with controls, knobs, journeys.
- No component specs yet — run `experience-components` first.
- No tokens.json — run `design-brand-visual` (or equivalent) first.
- Need pixel parity with the production component library — that's
  `mockup-component-storybook`'s job; this skill is intentionally low-fi.

## Prerequisites

| Path                                              | Gate | Purpose                                            |
| ------------------------------------------------- | ---- | -------------------------------------------------- |
| `_concept/experience/screens/components/`         | hard | Source component specs (one HTML output per file). |
| `_concept/discovery/brand/tokens.json`            | hard | Token values to embed as inline CSS variables.     |

## Boundary against `mockup-component-storybook` (sister skill)

| Aspect                | `mockup-component-isolated-html` (this) | `mockup-component-storybook` (sibling)     |
| --------------------- | --------------------------------------- | ------------------------------------------ |
| Tier                  | mvp / simple-app                        | standard-app / complex-app                 |
| Output                | `<component>.html` per component        | full Storybook 8 site under `_concept/experience/4_storybook/` |
| Build                 | none                                    | runs `storybook dev` / `storybook build`   |
| Interactivity         | none (static grid)                      | controls panel, knobs, args                |
| Framework dependency  | none                                    | tech-stack-aware                           |
| Scope                 | one HTML per component                  | components + screens + journeys (3 layers) |
| Audience              | early-design quick reference            | design-system + dev review                 |

This skill MUST NOT emit Storybook stories, MUST NOT depend on a tech stack,
and MUST NOT consume `experience/screens/*.md` (that's a screen-level concern).

---

ROLE mockup-component Isolated-HTML agent — emits one standalone, zero-build HTML page per component spec, with all variants × states in an inlined-token grid.

READS
  _concept/experience/screens/components/*.md   — component specs (pattern, library_component, used_in, ## Variants, ## States, ## Anatomy)
  _concept/discovery/brand/tokens.json          — full token shape; flattened into inline CSS custom properties

WRITES
  _concept/mockup-component/isolated-html/<component>.html — one standalone HTML file per source component (file:// openable)

REFERENCES
  mockup-component/isolated-html/references/tokens_inlining.md   — flattening + naming rules for tokens.json
  mockup-component/isolated-html/references/pattern_mocks.md     — pattern -> cell-body low-fi mock registry
  contracts/skill_grammar.md                                     — DSL keywords used in this body
  design/brand-visual/references/tokens_schema.md                — canonical tokens.json shape

REQUIRES
  hard: _concept/experience/screens/components — directory must contain at least one *.md
  hard: _concept/discovery/brand/tokens.json   — required to inline token CSS variables
  hard: python3 (>= 3.10) with PyYAML

MUST embed all tokens.json values as CSS custom properties inside a single :root block in the document <head>
MUST emit one HTML file per component, named <stem>.html under _concept/mockup-component/isolated-html/
MUST render every variant × state combination from the source component frontmatter as exactly one labeled grid cell
MUST run validator.py on every output and fix violations before completing the skill
MUST preserve deterministic ordering — alpha by component file stem; variants and states in source order with `default` first if present
MUST refuse with a clear, actionable error if components dir or tokens.json is missing — never silently skip

NEVER emit <link rel=stylesheet>, <script>, or any external CSS/JS reference in produced HTML
NEVER consume the elements: block — that's screen-level; this skill operates on components
NEVER hardcode token values — always read from tokens.json and flatten via the pinned rule
NEVER add framework-specific code (React, Vue, Lit, Svelte) — output is plain HTML + inline CSS only
NEVER write to any path outside `_concept/mockup-component/isolated-html/`

EMIT [mockup-component-isolated-html] started run_id=<uuid>

STEP 1: Resolve paths and validate inputs
  - Components dir: `_concept/experience/screens/components/`
  - Tokens path: `_concept/discovery/brand/tokens.json`
  - Output dir: `_concept/mockup-component/isolated-html/`
  - IF components dir is missing or has zero `*.md` files (excluding `_*.md`)
    - HARD FAIL: pointer at `experience-components`
  - IF tokens.json is missing or unparseable
    - HARD FAIL: pointer at `design-brand-visual`
  EMIT [mockup-component-isolated-html] checkpoint phase=inputs_resolved components=<N> tokens_ok=true

STEP 2: Parse each component spec
  - For each `<components_dir>/<stem>.md` (alpha by stem, exclude underscore-prefixed):
    - Parse YAML frontmatter (pattern, library_component, used_in, data_entities, last_updated)
    - Extract `## Purpose` → first paragraph
    - Extract `## Variants` → bullet names (`- **Name:** description`)
    - Extract `## States`   → bullet names
    - Extract `## Anatomy`  → first `~~~text` fenced block (optional)
  - Apply default-first ordering on variants and states
  - Missing `## Variants` → `["default"]`; missing `## States` → `["default"]`

STEP 3: Expand variant × state grid
  - Cartesian: row-major (states are rows, variants are columns)
  - `default` moved to position 0 in both axes (case-insensitive)

STEP 4: Inline tokens
  - Load `tokens.json`
  - Flatten nested keys to `--token-<dotted-path>` (underscores and camelCase → kebab)
  - Append the `tailwind:` block verbatim AFTER the flattened tree (so its overrides win)
  - Emit a single `:root { ... }` declaration inside `<style>` in `<head>`

STEP 5: Render and write HTML
  - For each component: build the page per the pinned rendered-HTML contract
  - Cells receive `data-variant` and `data-state` attributes for traceability
  - Pattern → cell body via `references/pattern_mocks.md` registry; unknown → `generic`
  - Anatomy `<pre>` rendered after the grid when present
  - Write `<out_dir>/<stem>.html`

STEP 6: Validate
  $ python3 mockup-component/isolated-html/validator.py <out_dir> --components <components_dir>
  IF validator exits non-zero
    - Read the violation list, fix the renderer, re-emit, re-validate
    UNTIL validator exits 0
  EMIT [mockup-component-isolated-html] completed run_id=<uuid> components=<N> ok=true

RUN
  python3 mockup-component/isolated-html/scripts/run.py \
    --components _concept/experience/screens/components \
    --tokens    _concept/discovery/brand/tokens.json \
    --out       _concept/mockup-component/isolated-html
  python3 mockup-component/isolated-html/validator.py \
    _concept/mockup-component/isolated-html \
    --components _concept/experience/screens/components

CHECKLIST
  - [ ] One HTML file per source component, named `<stem>.html`
  - [ ] Every output's `:root { ... }` block contains all flattened tokens (and tailwind passthrough last)
  - [ ] Every variant × state combination from frontmatter is present as a `<div class="cell">` with `data-variant` + `data-state`
  - [ ] No `<link rel=stylesheet>`, no `<script>`, no external `<img>` references
  - [ ] `validator.py` exits 0 on the output directory
  - [ ] At least one output file opened in a browser via `file://` and visually verified

## Depth Behavior

| Depth    | Behavior                                                                              |
| -------- | ------------------------------------------------------------------------------------- |
| `none`   | Skip this skill entirely                                                              |
| `light`  | Render only components whose `pattern:` matches a built-in mock; skip generic fallbacks |
| `medium` | Render every component, including generic fallbacks (default)                         |
| `max`    | Same as medium plus include the source `## Anatomy` block as `<pre>` when present     |

## Common Mistakes

| Mistake                                       | What to do instead                                                |
| --------------------------------------------- | ----------------------------------------------------------------- |
| Reading `experience/screens/*.md` directly    | This skill is component-isolated — read only `components/*.md`    |
| Adding a `<script>` for interactivity         | Static-only — escalate to `mockup-component-storybook` if needed  |
| Linking an external stylesheet                | Inline tokens via `:root { ... }`; that's the only style source   |
| Hardcoding `#6366f1`                          | Reference `var(--token-colors-primary)`                           |
| Skipping the validator                        | Always run `validator.py` and fix violations before completing    |

## Integration

- **Called by:** `concept-orchestrator` for mvp / simple-app bundles, or standalone
- **Requires:** `experience-components` output, `design-brand-visual` tokens
- **Sister skill:** `mockup-component-storybook` (for standard-app+ tiers)

