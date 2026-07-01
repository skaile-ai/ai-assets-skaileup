# Task 2F — `walkthrough-mockup-static-html` Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This is a **mini-plan** — a sub-plan of `docs/devlog/2026-05-07-skill-graph-migration.md` (Phase 2, Task 2F).

**Goal:** Author the `walkthrough-mockup-static-html` skill — the contract anchor among walkthrough renderers. It consumes the screen-frontmatter `elements:` block (pinned by Task 2.0) and produces a zero-build, openable static HTML walkthrough at `_concept/walkthrough-mockup/static-html/`. Every rendered DOM node carries `data-spec-screen` + `data-spec-element` attributes (and `data-spec-provisional="true"` when the id was auto-slugged) so the Phase 3 mockup-feedback cluster can resolve clicks back to source artefacts. Output also includes a `manifest.json` index keyed for `mockup-feedback-annotate`.

**Architecture:**
- A single SKILL.md authored under `walkthrough-mockup/static-html/` (Phase 1 directory; create if absent — see Pre-flight). The skill DSL body owns the rendering procedure and references the rendered-HTML contract verbatim.
- A small Python `validator.py` (alongside SKILL.md) that takes a generated `_concept/walkthrough-mockup/static-html/` directory and verifies: (a) all `data-spec-*` attributes resolve to existing source files, (b) `manifest.json` matches the pinned schema, (c) every screen-link inside `journey/<id>.html` resolves, (d) no JS framework was emitted (zero-build invariant).
- A fixture project under `walkthrough-mockup/static-html/tests/fixtures/<name>/` plus an expected-output snapshot the validator self-tests against.
- Rendering technology decision: **stdlib-only Python string templating** with `html.escape` and a thin `_render_*` helper module embedded inline in the skill body. Rationale recorded in Task 1.
- The skill emits a deterministic ordering (alpha by group, then alpha by file stem) so re-renders produce stable diffs.

**Tech Stack:** Markdown (skill DSL per `contracts/skill_grammar.md`), YAML frontmatter (per `contracts/asset_frontmatter.md`), Python 3.12+ for the validator (`PyYAML`, stdlib `json`/`pathlib`/`html` only). No JS frameworks, no build step, no npm/bun dependency in the produced site.

---

## Pre-flight

- [ ] **PF-1: Confirm cwd is repo root.**

  Run: `pwd`
  Expected: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`

- [ ] **PF-2: Confirm git working tree status.**

  Run: `git status -sb`
  Expected: branch matches the Phase 2 working branch; no uncommitted changes that would conflict with new files under `walkthrough-mockup/static-html/`.

- [ ] **PF-3: Confirm Task 2.0 mini-plan exists (this skill consumes its schema).**

  Run: `test -r docs/devlog/2.0-elements-block-contract.md && echo OK`
  Expected: `OK`. If missing, **STOP** — Task 2.0 is the contract anchor; this skill cannot pin its renderer behaviour without it.

  Then: confirm the contract artefacts produced by Task 2.0 are present:

  Run: `ls contracts/elements_block.md tests/elements_block_examples.md lab/validate-elements-block/SKILL.md 2>&1`
  Expected: all three exist. If any are missing, the executing agent SHOULD escalate before proceeding — the renderer contract is unstable without them.

- [ ] **PF-4: Confirm all source documents are readable.**

  Run:
  ```
  test -r REFACTOR_MOCKUP.md && \
  test -r SKILL_GRAPH.md && \
  test -r CONTRIBUTING.md && \
  test -r contracts/asset_frontmatter.md && \
  test -r contracts/frontmatter.md && \
  test -r contracts/skill_grammar.md && \
  test -r contracts/iron_laws.md && \
  test -r contracts/scripts/validator_lib.py && \
  echo OK
  ```
  Expected: `OK`.

- [ ] **PF-5: Verify the target directory.**

  Run: `ls walkthrough-mockup/`
  Expected output includes at least `DOMAIN.md`, `text/`, `skills/`. **Note:** at the time of this plan, `walkthrough-mockup/static-html/` does NOT exist (despite the parent plan stub assuming Phase 1 scaffolded it). The first authoring task creates it. If `static-html/` already exists with content, `ls walkthrough-mockup/static-html/` to verify it's empty before overwriting.

- [ ] **PF-6: Verify the existing `walkthrough-mockup-text` skill for tone/structure reference.**

  Run: `wc -l walkthrough-mockup/text/SKILL.md`
  Expected: > 0. Skim its frontmatter and section ordering (`Overview`, `Technology Stacks`, etc.) — this skill should sit **next** to it stylistically: same depth of body, same level of detail in `prerequisites`, same citation style.

- [ ] **PF-7: Read the load-bearing source sections (mandatory before Task 1).**

  - `docs/devlog/2.0-elements-block-contract.md` — entire file. The pinned `elements:` schema and the renderer contract section are authoritative for this skill.
  - `REFACTOR_MOCKUP.md` § 4 (walkthrough tiers — shared input contract), § 6 (`elements:` block + renderer MUST list + hybrid ID strategy), § 7 (workspace zones — `_feedback/` lives outside this skill but `_concept/walkthrough-mockup/static-html/` is the output zone), § 9 (tier composition — confirms static-html targets simple-app), § 10 step 3 (build order rationale).
  - `SKILL_GRAPH.md` § 4 (concept-group artefact flow — confirms input set), § 7 (workspace zones).
  - `CONTRIBUTING.md` § "SKILL.md Format" + § "Naming Conventions" (path-based name = `walkthrough-mockup-static-html`).
  - `contracts/asset_frontmatter.md` § "Skill — SKILL.md" + the `metadata.prerequisites` schema.
  - `contracts/skill_grammar.md` — full DSL.
  - `contracts/frontmatter.md` § "experience/screens/<group>/<screen>.md" — the screen frontmatter shape this skill consumes.
  - `walkthrough-mockup/text/SKILL.md` — sibling skill, used for stylistic alignment only (its content is **not** authoritative for this skill).

- [ ] **PF-8: Decide rendering technology.**

  **Decision: stdlib-only Python string templating** using `html.escape`, `pathlib`, and `json`. No Jinja, no Mako, no build tool.

  Rationale: (1) the produced site is **zero-build by acceptance criterion**, but the renderer that *generates* the site runs at skill-execution time and never ships in the output — its dependencies don't bleed through; (2) every other validator/generator script in this repo uses stdlib + PyYAML (see `contracts/scripts/validator_lib.py`, `experience/screens/validator.py`); consistency wins; (3) the templates are small (one shell template, one screen template, one journey template, one index template), so a 3-line `format()` substitution is cheaper than a templating-engine dependency. Record this decision verbatim in the SKILL.md `Overview` section so the next walkthrough variant author knows.

---

## Authoritative spec excerpts

### From `REFACTOR_MOCKUP.md` § 4 — shared input contract

```
input  = ( experience/screens/*.md
         , experience/journeys/stories.json
         , design/tokens.json
         , product-spec/features/*.md )

output = a routed site at _concept/walkthrough-mockup/<tier>/
         with /screen/<group>/<name> and /journey/<id> routes
         + every rendered DOM node carries data-spec-* attributes
```

### From `REFACTOR_MOCKUP.md` § 6 + Task 2.0 — renderer MUST list

Walkthrough renderers MUST emit:
- `data-spec-screen="<screen-path>"` on the screen root
- `data-spec-element="<element-id>"` on every annotatable node
- `data-spec-provisional="true"` when the id was auto-slugged (no explicit `elements:` entry)

### From `REFACTOR_MOCKUP.md` § 6 — hybrid ID strategy (verbatim)

1. Initial render: walkthrough auto-slugs IDs from labels/text. Marks all IDs `provisional`.
2. First annotation on a provisional element: `mockup-feedback-triage` prompts to promote the ID to explicit. The promoted ID gets written into the screen's `elements:` frontmatter via patch.
3. Subsequent renders use the promoted ID, no longer provisional. Future regeneration of the screen preserves the ID.

This skill implements step 1. Steps 2–3 are owned by `mockup-feedback-triage` (Phase 3) and are out of scope here.

### From parent plan Task 2F — outputs (verbatim)

Outputs at `_concept/walkthrough-mockup/static-html/`:
- `index.html` (router/menu)
- `screen/<group>/<name>.html` (one file per screen)
- `journey/<id>.html` (one file per journey)
- `manifest.json` (mapping rendered elements → source files)
- Every rendered DOM node carries `data-spec-screen` + `data-spec-element` attributes

### From parent plan Task 2F — acceptance criteria (verbatim)

- Generated site is openable as a static set of files (no build, no JS framework)
- Clicking a `journey` link walks through screens in order
- All `data-spec-*` attributes resolve to existing source files
- `manifest.json` is parseable by mockup-feedback-annotate (Phase 3)

---

## Pinned `manifest.json` schema (this plan's contract for Phase 3)

This schema is the **contract handed to `mockup-feedback-annotate`** in Phase 3. It MUST NOT change without coordinated updates to that mini-plan. Field names are pinned exactly:

```json
{
  "schema_version": "1.0",
  "renderer": "walkthrough-mockup-static-html",
  "renderer_version": "0.1.0",
  "generated_at": "2026-05-07T12:34:56Z",
  "source_root": "experience/screens",
  "screens": [
    {
      "screen_path": "experience/screens/01_user_auth/login.md",
      "screen_id": "01_user_auth/login",
      "rendered_html": "screen/01_user_auth/login.html",
      "implements": ["experience/features/01_user_auth/login.md"],
      "data_entities": ["User"],
      "layout": "experience/screens/00_layout/shell.md",
      "elements": [
        {
          "element_id": "submit-button",
          "kind": "button",
          "label": "Sign in",
          "states": ["default", "loading", "disabled", "error"],
          "provisional": false,
          "source_anchor": "experience/screens/01_user_auth/login.md#elements/submit-button"
        }
      ]
    }
  ],
  "journeys": [
    {
      "journey_id": "user-signs-in",
      "rendered_html": "journey/user-signs-in.html",
      "source": "experience/journeys/stories.json#user-signs-in",
      "screen_sequence": [
        "experience/screens/01_user_auth/login.md",
        "experience/screens/02_dashboard/home.md"
      ]
    }
  ],
  "features": [
    {
      "feature_path": "product-spec/features/01_user_auth/login.md",
      "rendered_screens": ["experience/screens/01_user_auth/login.md"]
    }
  ],
  "warnings": [
    {
      "kind": "auto_slugged",
      "screen_path": "experience/screens/02_dashboard/home.md",
      "element_id": "kpi-card-1",
      "message": "No elements: block in screen frontmatter; auto-slugged 1 element."
    }
  ]
}
```

**Field semantics:**
- `schema_version`: bump on breaking change. Phase 3 pins `^1.0`.
- `renderer` / `renderer_version`: identifies which walkthrough variant produced the site. Future Lit/Astro variants emit the same shape with their own `renderer` value.
- `generated_at`: ISO-8601 UTC; lets feedback-annotate detect stale renders.
- `source_root`: relative path the screen paths are anchored to (always `experience/screens` for this skill).
- `screens[].screen_id`: the path stem `<group>/<name>` (no `.md`); this is the value used in `data-spec-screen` if a path-based id is needed (see Open Questions on stable id format).
- `screens[].elements[].element_id`: the value emitted in `data-spec-element` on rendered DOM nodes.
- `screens[].elements[].provisional`: `true` when auto-slugged (mirrors `data-spec-provisional`).
- `screens[].elements[].source_anchor`: a fragment-style pointer back to the source file. For explicit ids, the fragment is `#elements/<element_id>`; for provisional ids the fragment is `#auto/<element_id>` (no entry yet in the YAML).
- `journeys[].screen_sequence`: ordered list of screen source paths the journey walks through. Same order is used by the rendered "Next →" links inside `journey/<id>.html`.
- `warnings[]`: machine-readable; `kind` is one of `auto_slugged`, `missing_layout`, `missing_feature`, `unknown_element_kind` (extend cautiously — Phase 3 will switch on this field).

**Rendered-HTML contract (which `data-spec-*` attribute appears on which DOM node):**

| DOM location | Attribute | Value | Source |
|---|---|---|---|
| `<body>` of every `screen/<group>/<name>.html` | `data-spec-screen` | screen path stem (e.g. `01_user_auth/login`) | screen file path |
| every annotatable child node (form fields, buttons, links, images, regions, list items, nav items) | `data-spec-element` | element id (kebab-case) | `elements:` entry, or auto-slug |
| same node, when no explicit `elements:` entry exists for it | `data-spec-provisional` | literal string `"true"` | absent in YAML |
| `<body>` of every `journey/<id>.html` | `data-spec-journey` | journey id from stories.json | stories.json |
| each step link inside `journey/<id>.html` | `data-spec-screen` | the screen-stem of that step's screen | journey step entry |
| `<body>` of `index.html` | `data-spec-index` | literal string `"true"` | (none — site root marker) |

The renderer MUST NOT add `data-spec-*` attributes that are not in this table; Phase 3's annotate skill ignores unknown ones, but a lean attribute set keeps drift visible.

---

## Auto-slug fallback (this skill's portion of the hybrid ID strategy)

When a screen file has no `elements:` block, OR has a partial one (some renderable widgets are not listed), this skill MUST:

1. Walk the screen's body and identify renderable widgets (form inputs declared in the screen markdown, buttons named in acceptance criteria, links, images named via `![alt](src)`, top-level headings as regions, etc.).
2. For each widget not present in `elements:` (matched by label-equality, case-insensitive), generate an id by:
   - Lowercase the label
   - Replace any non `[a-z0-9]` run with a single `-`
   - Trim leading/trailing `-`
   - If the resulting id is empty (e.g. label was `"…"`), fall back to `<kind>-<n>` where n is a 1-based counter scoped per-screen-per-kind (`button-1`, `button-2`, `input-1`, ...).
   - If the auto-slugged id collides with another auto-slugged id within the same screen, append `-2`, `-3`, ... until unique. (Explicit ids take precedence; collisions with explicit ids are an error reported in `warnings[]` with `kind: "auto_slug_collision"` and the element gets the suffixed id.)
3. Render the node with `data-spec-element="<auto-slugged-id>"` AND `data-spec-provisional="true"`.
4. Append a `warnings[]` entry of `kind: "auto_slugged"` to `manifest.json` for each auto-slugged element.
5. **Never** mutate the source `experience/screens/<group>/<name>.md` file. Promotion of provisional ids is `mockup-feedback-triage`'s job in Phase 3.

This procedure mirrors step 1 of the hybrid ID strategy from REFACTOR_MOCKUP.md § 6.

---

## Step ordering rule

Execute strictly in this order; do NOT reorder:

1. **Skeleton & frontmatter first** (Task 1) — locks the skill's name, dependencies, and prerequisites contract before any rendering logic. Catches naming/dependency mistakes early.
2. **Input parser second** (Task 2) — read screens, journeys, tokens, features into normalised in-memory objects. Independent of any HTML output. Testable on its own.
3. **Screen renderer third** (Task 3) — converts one parsed screen into one HTML file with the pinned `data-spec-*` attributes. Includes auto-slug fallback. Testable per-screen.
4. **Journey linker fourth** (Task 4) — reads stories.json, emits `journey/<id>.html` files that link sequentially through screens. Depends on screen renderer for the link targets.
5. **Index + manifest emitter fifth** (Task 5) — produces `index.html` (router/menu) and `manifest.json` (the Phase 3 contract). Depends on all prior tasks.
6. **Validator sixth** (Task 6) — TDD: fixture project → expected snapshot → validator that compares. Authored last because it validates the *whole pipeline* end-to-end.

The reason: a renderer authored before its inputs are normalised will couple parsing concerns into HTML emission and tests will be hard to write. The validator goes last because it tests the full contract — partial validators are easy to game.

---

## File targets (absolute paths)

- **Create:** `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/walkthrough-mockup/static-html/SKILL.md`
- **Create:** `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/walkthrough-mockup/static-html/validator.py`
- **Create:** `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/walkthrough-mockup/static-html/tests/fixtures/minimal/experience/screens/00_auth/login.md` (and 1-2 other input files in this fixture)
- **Create:** `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/walkthrough-mockup/static-html/tests/fixtures/minimal/experience/journeys/stories.json`
- **Create:** `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/walkthrough-mockup/static-html/tests/fixtures/minimal/design/tokens.json`
- **Create:** `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/walkthrough-mockup/static-html/tests/fixtures/minimal/product-spec/features/00_auth/login.md`
- **Create:** `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/walkthrough-mockup/static-html/tests/expected/minimal/manifest.json` (snapshot)
- **Create:** `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/walkthrough-mockup/static-html/tests/expected/minimal/screen/00_auth/login.html` (snapshot — small)
- **Create:** `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/walkthrough-mockup/static-html/tests/expected/minimal/journey/sign-in.html` (snapshot)
- **Create:** `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/walkthrough-mockup/static-html/tests/expected/minimal/index.html` (snapshot)
- **Create:** `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup/walkthrough-mockup/static-html/tests/run_validator.sh` (one-liner that exercises the validator end-to-end against the fixture)

---

## Task 1: Author SKILL.md skeleton + frontmatter

**Files:**
- Create: `walkthrough-mockup/static-html/SKILL.md`

- [ ] **Step 1.1: Create the directory if missing.**

  Run: `mkdir -p walkthrough-mockup/static-html && ls -d walkthrough-mockup/static-html`
  Expected: `walkthrough-mockup/static-html`.

- [ ] **Step 1.2: Confirm naming.**

  Per `CONTRIBUTING.md` § "Naming Conventions" the path is `walkthrough-mockup/static-html/SKILL.md`, so the `name:` field MUST be `walkthrough-mockup-static-html`. Verify in Step 1.4.

- [ ] **Step 1.3: Author frontmatter.**

  Use the schema from `contracts/asset_frontmatter.md` § "Skill — SKILL.md". Pin these fields:

  ```yaml
  ---
  name: walkthrough-mockup-static-html
  description: "Use when stakeholders need a clickable static HTML walkthrough of the application — zero build, no JS framework, openable directly in a browser. Generates one HTML file per screen and per journey, plus a manifest.json that the mockup-feedback cluster reads to resolve clicks back to source artefacts. Best for simple-app tier."
  metadata:
    version: "0.1.0"
    tags: [walkthrough, mockup, static-html, zero-build, simple-app, frontend, prototype, data-spec]
    stage: alpha
    requires:
      - contract:elements-block
    prerequisites:
      files:
        - path: "experience/screens"
          gate: hard
          description: "Screen specs are the primary input — one file rendered per screen"
          min_entries: 1
        - path: "experience/journeys/stories.json"
          gate: hard
          description: "Journey definitions drive the journey/<id>.html sequencing"
        - path: "design/tokens.json"
          gate: hard
          description: "Brand tokens injected as CSS variables in the rendered shell"
        - path: "product-spec/features"
          gate: soft
          description: "Feature files are linked from manifest.json for traceability; absence is recorded as a warning, not a failure"
          min_entries: 1
      reads:
        - path: "experience/screens/00_layout/shell.md"
          description: "Optional shared layout reference; if present, used as the wrapping shell for every screen"
      produces:
        - path: "_concept/walkthrough-mockup/static-html"
          description: "Generated static site: index.html, screen/<group>/<name>.html, journey/<id>.html, manifest.json"
  ---
  ```

  Note: `requires:` declares `contract:elements-block` so Phase 2's contract (Task 2.0) is auto-installed. The contract id `elements-block` matches Task 2.0's pinned name (verify in Step 1.4 against `contracts/elements_block.md` once it exists).

- [ ] **Step 1.4: Verify frontmatter.**

  Run: `python -c "import yaml; yaml.safe_load(open('walkthrough-mockup/static-html/SKILL.md').read().split('---')[1])"`
  Expected: no exception.

  Run: `grep '^name:' walkthrough-mockup/static-html/SKILL.md`
  Expected: `name: walkthrough-mockup-static-html` (path-based, matches CONTRIBUTING.md § Naming Conventions).

- [ ] **Step 1.5: Stub the body sections (do not fill yet).**

  Add the following section headers under the frontmatter (content filled in subsequent tasks):

  ```
  # Walkthrough Mockup — Static HTML

  ## Overview
  ## Renderer Contract
  ## Inputs
  ## Outputs
  ## ROLE / READS / WRITES / REFERENCES
  ## STEP 1: Read inputs
  ## STEP 2: Render screens
  ## STEP 3: Render journeys
  ## STEP 4: Emit index.html and manifest.json
  ## STEP 5: Validate
  ## MUST / NEVER
  ## CHECKLIST
  ```

- [ ] **Step 1.6: Commit.**

  ```
  git add walkthrough-mockup/static-html/SKILL.md
  git commit -m "feat(walkthrough-mockup-static-html): scaffold skill (frontmatter + section headers)"
  ```

---

## Task 2: Input parser section

**Files:**
- Modify: `walkthrough-mockup/static-html/SKILL.md` — fill `## Inputs` and `## STEP 1: Read inputs`

- [ ] **Step 2.1: Document the four input shapes.**

  Under `## Inputs`, list each input with its expected shape (cite contracts inline):

  - `experience/screens/<group>/<screen>.md` — frontmatter per `contracts/frontmatter.md` § "experience/screens/<group>/<screen>.md", optionally extended with `elements:` per `contracts/elements_block.md`. Body markdown is **not** parsed for layout — only frontmatter + flat element listing drive the render. (Open question: is body parsed? See Open Questions.)
  - `experience/journeys/stories.json` — array of journey objects; each has `id`, `title`, `screen_sequence: [<screen_path>, ...]`, `description`. (Confirm format from existing stories.json schema; if undocumented, surface in Open Questions.)
  - `design/tokens.json` — token tree (e.g. `{"color": {"primary": "#..."}, "spacing": {...}}`). Tokens are flattened into CSS custom properties on the wrapping shell `<style>` block. (Format details: refer to `contracts/golden_principles.md` if it pins a token shape; otherwise treat as opaque key-value tree.)
  - `product-spec/features/<NN>/<feature>.md` — used only for `manifest.json#features`; not rendered as HTML directly.

- [ ] **Step 2.2: Author STEP 1 in the skill body.**

  Use DSL from `contracts/skill_grammar.md`. The step describes the parsing procedure verbatim (no code, just procedure):

  ```
  STEP 1: Read inputs
    - Glob experience/screens/**/*.md, sort lexicographically by path.
    - For each screen: parse YAML frontmatter; extract implements[], data_entities[], layout, elements[] (default to []).
    - Validate elements[] against contracts/elements_block.md (delegate to lab/validate-elements-block if present; otherwise emit a warning).
    - Read experience/journeys/stories.json. Validate each journey has id + screen_sequence.
    - Read design/tokens.json. Flatten one level deep into CSS custom properties.
    - Glob product-spec/features/**/*.md, sort lexicographically. Build a feature -> screens map by inverting screens[].implements.
    - Build a normalised in-memory model: { screens: [...], journeys: [...], tokens: {...}, features: [...] }.
  ```

- [ ] **Step 2.3: Note edge cases.**

  Record (in the body under STEP 1) the handling for:
  - Screen file with malformed YAML → fail loudly, exit non-zero (no partial render).
  - Screen referenced from a journey but absent on disk → record `manifest.warnings[]` with `kind: "missing_screen"` AND skip rendering that journey step (link becomes a dead-end placeholder, not a 404).
  - `elements:` entry referencing a `kind` outside the (still-open) enum → render with `data-spec-element` set, but record a warning `kind: "unknown_element_kind"`.
  - Layout reference (`layout:`) pointing to a non-existent file → warning `missing_layout`, fall back to a built-in default shell.

- [ ] **Step 2.4: Commit.**

  ```
  git add walkthrough-mockup/static-html/SKILL.md
  git commit -m "feat(walkthrough-mockup-static-html): document input parser + edge cases"
  ```

---

## Task 3: Screen renderer section

**Files:**
- Modify: `walkthrough-mockup/static-html/SKILL.md` — fill `## STEP 2: Render screens`, `## Renderer Contract`

- [ ] **Step 3.1: Author the renderer contract section.**

  Under `## Renderer Contract`, paste the rendered-HTML contract table from this plan (the `data-spec-*` table). This is the **public contract** of this skill — every other walkthrough variant in Phase 3 will reference it.

- [ ] **Step 3.2: Author STEP 2 — per-screen render procedure.**

  ```
  STEP 2: Render screens
    For each parsed screen (in lexicographic order):
      - Determine output path: _concept/walkthrough-mockup/static-html/screen/<group>/<name>.html
      - Compute screen_id = path stem under experience/screens/ (e.g. "01_user_auth/login").
      - Open the wrapping shell (default or layout-driven). Inject tokens.json as CSS custom properties.
      - Set <body data-spec-screen="<screen_id>">.
      - For each element in screen.elements:
          - Render an HTML node appropriate to its kind (button -> <button>, input -> <input>, link -> <a>, image -> <img>, region -> <section>, list -> <ul>, form -> <form>, nav -> <nav>, media -> <figure>, custom -> <div>, text -> <span>).
          - Emit data-spec-element="<element.id>".
          - If element was auto-slugged (no explicit elements: entry matched), also emit data-spec-provisional="true".
          - Render label as visible text (escaped via html.escape).
          - For each state in element.states beyond "default", render a small toggle (<details> or visually hidden marker) with class "state-<name>" so visual reviewers can see state coverage.
      - For widgets discoverable in the screen but absent from elements[], apply auto-slug per the "Auto-slug fallback" procedure documented above and emit them at the bottom of <main> in a "<!-- auto-slugged -->" group (so the source ordering vs. auto-slugged ordering is visually distinct).
      - Add a footer linking back to index.html.
      - Write the file UTF-8, LF.
  ```

- [ ] **Step 3.3: Document escape rules.**

  MUST escape via `html.escape(..., quote=True)` when emitting any value derived from frontmatter or stories.json into HTML attributes or text. Surface as a `MUST` line in the skill body:

  ```
  MUST escape every label, id, screen_path, journey_id with html.escape(..., quote=True) before substitution into HTML
  NEVER trust frontmatter strings; they may contain quotes, angle brackets, or unicode that breaks the document
  ```

- [ ] **Step 3.4: Commit.**

  ```
  git add walkthrough-mockup/static-html/SKILL.md
  git commit -m "feat(walkthrough-mockup-static-html): pin screen renderer contract + escape rules"
  ```

---

## Task 4: Journey linker section

**Files:**
- Modify: `walkthrough-mockup/static-html/SKILL.md` — fill `## STEP 3: Render journeys`

- [ ] **Step 4.1: Author STEP 3 — journey rendering.**

  ```
  STEP 3: Render journeys
    For each journey in stories.json:
      - Determine output path: _concept/walkthrough-mockup/static-html/journey/<journey_id>.html
      - Set <body data-spec-journey="<journey_id>">.
      - Render <h1>journey.title</h1> + escaped description.
      - Render <ol> of steps: each <li> contains:
          - a "Step <n>: <screen_label>" heading
          - a <a href="../screen/<group>/<name>.html" data-spec-screen="<screen_id>">Open screen</a>
          - a "Next →" link to the next step's screen (or to index.html on the last step)
      - The "click a journey link walks through screens in order" acceptance criterion is honoured by the in-screen "back to journey" link injected in Step 2 (add to that step: when a screen is part of a journey, the screen footer also includes a "Continue journey →" link that opens the next screen in sequence; if a screen appears in multiple journeys, render a list).
      - Write the file UTF-8, LF.
  ```

- [ ] **Step 4.2: Document the "screen-in-multiple-journeys" rule.**

  Add a NEVER + STEP note: when a screen appears in two or more journeys, each journey's `screen/<group>/<name>.html` retains its own "Continue journey →" link only inside the journey HTML. The screen HTML itself does not embed journey-specific navigation (else screen renders couple to journey state). Cross-journey continuation is solely owned by `journey/<id>.html`.

- [ ] **Step 4.3: Commit.**

  ```
  git add walkthrough-mockup/static-html/SKILL.md
  git commit -m "feat(walkthrough-mockup-static-html): journey linker + multi-journey rules"
  ```

---

## Task 5: Index + manifest emitter section

**Files:**
- Modify: `walkthrough-mockup/static-html/SKILL.md` — fill `## STEP 4: Emit index.html and manifest.json`

- [ ] **Step 5.1: Author STEP 4 — index.html.**

  ```
  STEP 4a: Emit index.html
    - <body data-spec-index="true">.
    - Render two sections:
        - "Screens" — flat list grouped by <group>, each entry linking to screen/<group>/<name>.html
        - "Journeys" — flat list, each entry linking to journey/<id>.html
    - Embed a "Generated <timestamp>" footer.
  ```

- [ ] **Step 5.2: Author STEP 4 — manifest.json.**

  ```
  STEP 4b: Emit manifest.json
    - Build the object using the pinned schema (see SKILL.md § "Manifest Schema" — paste the schema from this plan into the skill body so Phase 3 readers see it inline).
    - schema_version = "1.0".
    - generated_at = current UTC ISO-8601.
    - Sort screens[] and journeys[] lexicographically for deterministic diffs.
    - Write atomic: write to manifest.json.tmp, fsync, rename to manifest.json.
  ```

  In the SKILL.md body, also paste the full `manifest.json` schema from this plan (under a "## Manifest Schema" sub-section) so future readers don't have to chase the plan document.

- [ ] **Step 5.3: Author the MUST/NEVER block.**

  Hard constraints to surface as `MUST` / `NEVER` lines in the skill body:

  ```
  MUST emit data-spec-screen on every screen <body>
  MUST emit data-spec-element on every annotatable child node
  MUST emit data-spec-provisional="true" on auto-slugged element nodes
  MUST write manifest.json that conforms to the pinned schema (schema_version: "1.0")
  MUST sort all manifest arrays lexicographically (screens by screen_path, journeys by journey_id, features by feature_path) for deterministic diffs
  MUST escape every interpolated string via html.escape(..., quote=True)

  NEVER include a JS framework, a bundler artefact, or any <script src=...> pointing at a non-relative URL — the site is openable as a static set of files
  NEVER mutate source files (experience/screens/**, experience/journeys/stories.json, design/tokens.json, product-spec/features/**) — this skill is read-only on its inputs
  NEVER emit data-spec-* attributes outside the pinned table — Phase 3 ignores unknown ones, but lean attribute sets keep drift visible
  NEVER inline absolute paths from the developer's filesystem into manifest.json (use repo-relative paths only)
  ```

- [ ] **Step 5.4: Author the CHECKLIST block.**

  ```
  CHECKLIST
    - [ ] _concept/walkthrough-mockup/static-html/index.html exists
    - [ ] _concept/walkthrough-mockup/static-html/manifest.json exists and parses as JSON
    - [ ] manifest.schema_version == "1.0"
    - [ ] One screen/<group>/<name>.html per screen file under experience/screens
    - [ ] One journey/<id>.html per journey in stories.json
    - [ ] Every <body> in screen/**/*.html has data-spec-screen
    - [ ] Every annotatable node in screen/**/*.html has data-spec-element
    - [ ] Every auto-slugged element node also has data-spec-provisional="true"
    - [ ] No <script src="http..."> or non-relative resource URL appears in any output file
    - [ ] Validator (walkthrough-mockup/static-html/validator.py) exits 0 on the produced site
  ```

- [ ] **Step 5.5: Commit.**

  ```
  git add walkthrough-mockup/static-html/SKILL.md
  git commit -m "feat(walkthrough-mockup-static-html): index + manifest schema + MUST/NEVER + checklist"
  ```

---

## Task 6: Validator + fixture (TDD)

**Files:**
- Create: `walkthrough-mockup/static-html/validator.py`
- Create: `walkthrough-mockup/static-html/tests/fixtures/minimal/...` (input project)
- Create: `walkthrough-mockup/static-html/tests/expected/minimal/...` (expected snapshot)
- Create: `walkthrough-mockup/static-html/tests/run_validator.sh`

- [ ] **Step 6.1: Build the minimal fixture project.**

  Lay out under `walkthrough-mockup/static-html/tests/fixtures/minimal/`:

  - `experience/screens/00_auth/login.md` — frontmatter with `implements: [product-spec/features/00_auth/login.md]`, `data_entities: [User]`, and a complete `elements:` block (3 elements: email-input, password-input, submit-button — copy from REFACTOR_MOCKUP.md § 6 example).
  - `experience/screens/00_auth/register.md` — frontmatter with NO `elements:` block (intentional, exercises auto-slug).
  - `experience/journeys/stories.json` — one journey `sign-in` with `screen_sequence: ["experience/screens/00_auth/login.md"]`.
  - `design/tokens.json` — minimal: `{"color": {"primary": "#0ea5e9"}, "spacing": {"sm": "8px"}}`.
  - `product-spec/features/00_auth/login.md` — minimal frontmatter + one acceptance criterion.

  These files are committed inputs; the validator runs the skill against them and compares outputs.

- [ ] **Step 6.2: Generate the expected snapshot once, manually.**

  Run the skill (or a hand-crafted reference render) against the fixture, capture the output into `walkthrough-mockup/static-html/tests/expected/minimal/`. Snapshot files:

  - `index.html`
  - `screen/00_auth/login.html`
  - `screen/00_auth/register.html` (contains `data-spec-provisional="true"` on its auto-slugged elements)
  - `journey/sign-in.html`
  - `manifest.json` (with `generated_at` field stripped or pinned to a constant; see Step 6.4)

  These snapshots are reviewed by hand once and committed.

- [ ] **Step 6.3: Author `validator.py`.**

  Reuse `contracts/scripts/validator_lib.py` for report formatting (`Validator` class, `must`/`never`/`checklist`). The validator's responsibilities:

  1. **Argv:** `python validator.py <site-root> [--fixture <fixture-name>]`. Default `<site-root>` = `_concept/walkthrough-mockup/static-html`.
  2. **Site-root mode** (no `--fixture`): structural checks only.
     - `index.html`, `manifest.json` exist.
     - `manifest.json` parses; `schema_version` is `"1.0"`; required top-level keys present.
     - Every `screens[].rendered_html` resolves to an existing file; that file's `<body>` has `data-spec-screen` matching `screens[].screen_id`.
     - Every `screens[].elements[].element_id` appears as a `data-spec-element` value somewhere in the rendered HTML.
     - `data-spec-screen` values resolve back to source screen files (relative to a `--source-root` arg, default `experience/screens`).
     - Every `journeys[].rendered_html` exists; its `<body>` has `data-spec-journey`; every step link's `data-spec-screen` value is in the rendered screens set.
     - No `<script src="http`, no `<script src="//"`, no `<link rel="stylesheet" href="http"` — zero-build invariant.
  3. **Fixture mode** (`--fixture minimal`): also compares each generated file byte-for-byte (or after a deterministic normalisation pass, e.g. stripping `generated_at`) against `tests/expected/<fixture>/`.
  4. **Exit code:** 0 if all checks pass; 1 with a `<file>:<line>: <message>` violation report otherwise.
  5. Use Python stdlib only (`json`, `pathlib`, `re`, `html.parser`) plus PyYAML for parsing screen frontmatter.

- [ ] **Step 6.4: Make outputs deterministic for snapshot tests.**

  In the validator, before comparing `manifest.json` to the expected snapshot, replace the runtime `generated_at` value with the literal string `"<pinned>"`. The expected snapshot stores `"generated_at": "<pinned>"`. This avoids snapshot churn while still asserting the field's presence.

- [ ] **Step 6.5: Author `run_validator.sh` (one-liner harness).**

  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  cd "$(dirname "$0")"
  # 1. Render against the fixture (the executing skill does this in production; in tests we drive it manually).
  # 2. Run validator in fixture mode.
  python ../validator.py rendered/minimal --fixture minimal --source-root fixtures/minimal/experience/screens
  ```

  Note: the actual rendering step is owned by the skill's STEPs 1-4 — this script assumes the renderer has already populated `walkthrough-mockup/static-html/tests/rendered/minimal/`. The skill execution writes there during tests; the validator only reads.

- [ ] **Step 6.6: Verify the validator exits 0 against the expected snapshot.**

  Run: `bash walkthrough-mockup/static-html/tests/run_validator.sh && echo "exit=$?"`
  Expected: `exit=0`. If the renderer hasn't been run yet, copy `tests/expected/minimal/` into `tests/rendered/minimal/` for the bootstrap and verify that the validator passes against the snapshot itself (this proves the validator is internally consistent before the renderer is wired up).

- [ ] **Step 6.7: Sanity-check by mutating one expected file.**

  Temporarily delete `data-spec-screen` from `tests/expected/minimal/screen/00_auth/login.html` (in a copy under `tests/rendered/minimal/`). Re-run the validator; expect `exit=1` with a violation report pointing at the missing attribute. Revert.

- [ ] **Step 6.8: Sanity-check the auto-slug fallback.**

  Confirm that `tests/expected/minimal/screen/00_auth/register.html` contains at least one node with both `data-spec-element="..."` AND `data-spec-provisional="true"`, and that `tests/expected/minimal/manifest.json` has a corresponding `warnings[]` entry of `kind: "auto_slugged"` for the register screen.

- [ ] **Step 6.9: Commit.**

  ```
  git add walkthrough-mockup/static-html/validator.py walkthrough-mockup/static-html/tests/
  git commit -m "test(walkthrough-mockup-static-html): minimal fixture + validator + snapshot"
  ```

---

## Task 7: Cross-link from `walkthrough-mockup/DOMAIN.md`

**Files:**
- Modify: `walkthrough-mockup/DOMAIN.md` — append a Skills row for `walkthrough-mockup-static-html`

- [ ] **Step 7.1: Append to DOMAIN.md `## Skills` section.**

  Add a one-line entry pointing at `static-html/SKILL.md` with a one-sentence description matching the SKILL.md `description:` field's first sentence.

- [ ] **Step 7.2: Commit.**

  ```
  git add walkthrough-mockup/DOMAIN.md
  git commit -m "docs(walkthrough-mockup): list static-html in DOMAIN.md"
  ```

---

## Definition of Done

- [ ] `walkthrough-mockup/static-html/SKILL.md` exists with `name: walkthrough-mockup-static-html` (matching its parent directory per CONTRIBUTING.md), declares `contract:elements-block` in `requires:`, and follows the SKILL.md DSL (ROLE, READS, WRITES, REFERENCES, MUST, NEVER, STEP 1-4, CHECKLIST).
- [ ] SKILL.md body includes the rendered-HTML contract table (which `data-spec-*` attribute on which DOM node), the auto-slug fallback procedure, and the `manifest.json` schema inline.
- [ ] `walkthrough-mockup/static-html/validator.py` is invocable in two modes (site-root, fixture) and uses stdlib + PyYAML only.
- [ ] `walkthrough-mockup/static-html/tests/fixtures/minimal/` contains a runnable input project (one screen with explicit `elements:`, one screen without — exercising auto-slug — one journey, one feature, one tokens file).
- [ ] `walkthrough-mockup/static-html/tests/expected/minimal/` snapshot matches the validator's expectations (manifest schema_version 1.0, all `data-spec-*` attributes present, auto-slugged register screen flagged).
- [ ] `bash walkthrough-mockup/static-html/tests/run_validator.sh` exits 0.
- [ ] Mutating any expected file (e.g. removing `data-spec-screen`) makes the validator exit 1 with a line-numbered violation report.
- [ ] `walkthrough-mockup/DOMAIN.md` lists this skill.
- [ ] All commits land cleanly on the working branch (Tasks 1, 2, 3, 4, 5, 6, 7 = 7 commits).
- [ ] No JS framework, no bundler artefact, no absolute filesystem path appears in any output file.
- [ ] Manifest schema is byte-for-byte identical to the schema pinned in this plan; if it diverges, this plan and the Phase 3 mockup-feedback-annotate plan must be updated together.

---

## Open Questions / Ambiguities

These were surfaced during planning rather than guessed. The executing agent SHOULD confirm or escalate before locking in:

1. **`kind` and `states` enums** — inherited from Task 2.0. REFACTOR_MOCKUP.md § 6 only shows examples; Task 2.0 proposed a v0.1 enum but flagged it open. This skill must follow whatever Task 2.0 publishes; if Task 2.0 widens the enum after this skill ships, bump this skill's `metadata.version` and update the kind→DOM-tag mapping in STEP 2.

2. **Body markdown vs. frontmatter-only** — when a screen file has a body section (e.g. acceptance criteria, layout notes), should the renderer emit body content as visible markdown-rendered HTML inside the screen page, or only render the elements declared in frontmatter? The parent plan does not specify. Recommended: emit the frontmatter-driven element grid as the primary content, plus a small `<details>` block with the markdown body underneath (rendered via stdlib — no extra dep — using a minimal markdown subset). Confirm with the user.

3. **`stories.json` schema** — the parent plan's input list cites `experience/journeys/stories.json` but the schema isn't published in `contracts/frontmatter.md`. Some assumptions used here (`id`, `title`, `screen_sequence`, `description`) are reasonable but unverified. The executing agent should `cat experience/journeys/stories.json` (if any example exists in the repo) before authoring STEP 3 and surface mismatches.

4. **`tokens.json` flattening rule** — depth-1 flattening is assumed (`color.primary` → `--color-primary`). If tokens are nested deeper (`color.brand.primary.50`), the rule needs to extend (joined with `-` per level). Confirm against `design/tokens.json` once a representative example exists.

5. **`screen_id` vs. screen path** — the manifest uses `screen_path` (full path with `.md`) AND `screen_id` (the path stem without `.md`). The renderer emits `data-spec-screen="<screen_id>"` (stem form). If Phase 3 mockup-feedback-annotate prefers full paths, both forms are kept in the manifest so it can pick. Document this duality in the manifest schema section.

6. **Layout shell** — when `layout: experience/screens/00_layout/shell.md` is present, do we read the layout file's body and use it as a literal HTML wrapper, or just inherit its `tokens` reference? The conservative interpretation: read the layout file's frontmatter for any meta (e.g. nav structure declared as elements), and use a built-in shell template otherwise. Surface for review.

7. **Auto-slug source** — when no `elements:` block exists, what determines what gets auto-slugged? The parent plan and REFACTOR_MOCKUP.md § 6 say "auto-slug IDs from labels/text", but don't pin where the labels come from. Reasonable sources: (a) markdown headings, (b) form-field-style markdown lines (e.g. `- Email: <input>`), (c) acceptance criteria mentioning UI elements. This plan assumes (a) + (b); confirm. The hybrid ID strategy is robust enough that a wider auto-slug net is fine — explicit ids always win.

8. **Where `_concept/walkthrough-mockup/static-html/` lives at run time** — the skill writes there, but for tests under `walkthrough-mockup/static-html/tests/`, the working directory is the fixture root, not the repo root. The validator must be path-agnostic. Confirm via run_validator.sh.

9. **Fixture-mode rendering** — in this plan, Task 6.2 says "generate the expected snapshot once, manually". A future improvement: have the validator drive a render-then-compare in one go (validator imports the renderer module). For Task 2F MVP, manual snapshot is fine; flag for Phase 3 promotion.

10. **`requires:` entry for `contract:elements-block`** — Task 2.0's contract artefact is `contracts/elements_block.md`. Whether the asset-manager registers this as `contract:elements-block` (kebab from filename) or `contract:elements_block` depends on whether contracts are produced by `CONTRACT.md` files (not `.md` files in the contracts dir). Verify by running `skaile list contracts` (or grepping `contracts/` for `CONTRACT.md`) once Task 2.0 ships. If the contract isn't formally an asset, drop it from `requires:` and document the dependency in the body's `REFERENCES` block instead.

---

## Notes for the executing agent

- Do not skip Pre-flight. Reading Task 2.0's mini-plan in full is mandatory — the renderer contract section is authoritative.
- The skill body should be **dense and reference-style**, not narrative. Match the tone of `walkthrough-mockup/text/SKILL.md` and `experience/screens/SKILL.md`.
- All seven tasks should land as seven separate commits. Atomicity makes review and rollback straightforward.
- If Task 2.0's contract drifts mid-execution (e.g. the `kind` enum is closed and one of the kinds in the fixture is dropped), STOP and escalate — don't paper over schema drift.
- The validator is the gate: a generated site that passes the validator is, by definition, ready for Phase 3 to consume. Be ruthless about coverage.
- Commit hygiene: stage only files relevant to each commit. `git add walkthrough-mockup/static-html/` (with the trailing slash) is acceptable per task; never `git add -A`.
