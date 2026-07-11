# Skill Dedup & Token Reduction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove ~1,500+ duplicated lines across the 85-skill collection (22,727 lines) by extracting shared contract files, fix two live bugs (stale "deleted"-dossier prose, wrong feature path), and add CI guards so the duplication cannot regrow.

**Architecture:** Four new files under `skaileup/contracts/` (the `shared-contracts` layer every skill already installs) become the single owners of the walkthrough-renderer contract, the slice-loop lifecycle, the grill question bank, the evaluator skeleton, and shared phase procedures; skills shrink to scaffold + citations. Two new checks in `contracts/scripts/verify_artifacts.py` (restatement n-gram detector, 400-line budget) lock it in. A final caveman-compression pass rewrites prose in the 10 largest skills.

**Tech Stack:** markdown skills DSL (`skaileup/contracts/skill_grammar.md`), Python 3 stdlib + PyYAML validators, pytest.

## Global Constraints

- Repo root: the git worktree containing this file; all paths below are repo-relative; all commands run from repo root.
- After EVERY task: `python3 skaileup/contracts/scripts/verify_artifacts.py` must exit 0 (WARNs allowed, ERRORs not) and `python3 skaileup/flows/_meta/verify_flows.py` must exit 0.
- Flow-verifier tests must stay green: `python3 -m pytest skaileup/flows/_meta/test_verify.py -q`.
- New contract files go in `skaileup/contracts/` — the whole directory is already registered as contract `shared-contracts` in `skaile.yaml` (root: `skaileup/contracts`), so **no `skaile.yaml` change is needed**; each new file MUST be added to the Contents list in `skaileup/contracts/CONTRACT.md`.
- Never change any skill's `name:` frontmatter, any artifact id, or any flow YAML.
- Dedup edits replace text with citations — they must never weaken or change the *semantics* of a MUST/NEVER line, refuse condition, error string, or validator-pinned string.
- Canonical feature path is `_concept/experience/features/<NN_group>/<feature_slug>.md` (per `skaileup/contracts/artifacts.yaml` id `features`, line 158, and `concept_structure.md`). `_concept/product-spec/features/` is a bug wherever it appears.
- Slice dossiers are **frozen, not deleted** (CLAUDE.md § Phase 4; `skaileup/12_impl-slice/07_commit/SKILL.md` L62-71): terminator writes `index.md`, keeps phase handoffs, removes only `progress.yaml`.
- Python code: stdlib + PyYAML only (repo convention, see `verify_artifacts.py` header).
- macOS host: in-place sed is `sed -i ''` (BSD sed).
- Line budget target: ≤400 lines per SKILL.md (WARN, not ERROR).
- Every commit message ends with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

---

### Task 1: Fix stale "dossier is deleted" prose (R0 bug 1)

Four skills still describe the pre-Phase-4 model where the slice dossier is scratch and gets deleted. The correct model (owner: `skaileup/12_impl-slice/07_commit/SKILL.md` L62-71, L107-110): dossier is **frozen** — terminator writes `index.md`, keeps handoffs, removes only `progress.yaml`.

**Files:**
- Modify: `skaileup/08_concept-slice/01_brainstorm/SKILL.md:67-70`
- Modify: `skaileup/11_impl-plan/01_brainstorm/SKILL.md:73-76`
- Modify: `skaileup/11_impl-plan/02_align/SKILL.md:86-89`
- Modify: `skaileup/11_impl-plan/03_plan-vertical/SKILL.md:94-97`
- Test: manual grep (no validator covers prose); `verify_artifacts.py` regression check

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: corrected freeze-lifecycle prose that Task 5's `slice_loop.md § Freeze lifecycle` will later cite (wording below is intentionally consistent with it).

- [ ] **Step 1: Confirm the stale text exists (failing "test")**

Run:
```bash
grep -rn "is deleted by\|deletes the entire" skaileup/08_concept-slice skaileup/11_impl-plan --include=SKILL.md
```
Expected: 4 hits — `08_concept-slice/01_brainstorm/SKILL.md:69`, `11_impl-plan/01_brainstorm/SKILL.md:74`, `11_impl-plan/02_align/SKILL.md:88`, `11_impl-plan/03_plan-vertical/SKILL.md:96-97`.

- [ ] **Step 2: Fix `skaileup/08_concept-slice/01_brainstorm/SKILL.md`**

Replace (exact old text, lines 67-70):
```
The handoff file is consumed by `concept-slice-align`. After the full slice
chain (brainstorm → align → scope-feature → design-feature) commits the
permanent artifacts, `concept-slice-design-feature` deletes the entire
`_concept/slices/<slice_id>/` directory.
```
with:
```
The handoff file is consumed by `concept-slice-align`. After the full slice
chain (brainstorm → align → scope-feature → design-feature) commits the
permanent artifacts, `concept-slice-design-feature` freezes the dossier: it
writes `_concept/slices/<slice_id>/index.md` and keeps the phase handoffs as
permanent per-feature documentation. Nothing is deleted.
```

- [ ] **Step 3: Fix `skaileup/11_impl-plan/01_brainstorm/SKILL.md`**

Replace (exact old text, lines 73-76):
```
The output is `_implementation/slices/<slice_id>/brainstorm.md` — a structured handoff file consumed
by `impl-plan-align`. The `_implementation/slices/<slice_id>/` directory is scratch and is deleted by
`impl-slice/commit` after the slice's atomic commit lands. None of the impl-plan skills
delete the dir themselves.
```
with:
```
The output is `_implementation/slices/<slice_id>/brainstorm.md` — a structured handoff file consumed
by `impl-plan-align`. The `_implementation/slices/<slice_id>/` dossier is durable: `impl-slice-commit`
freezes it after the slice's atomic commit lands — writes `index.md`, keeps the phase handoffs as
permanent documentation, removes only the transient `progress.yaml`. No impl-plan skill deletes
or freezes the dir itself.
```

- [ ] **Step 4: Fix `skaileup/11_impl-plan/02_align/SKILL.md`**

Replace (exact old text, lines 86-89):
```
The output is `_implementation/slices/<slice_id>/align.md` — a structured handoff file consumed
by `impl-plan-plan-vertical`. The `_implementation/slices/<slice_id>/` directory is scratch and
is deleted by `impl-slice/commit` after the slice's atomic commit lands. None of the
impl-plan skills delete the dir themselves.
```
with:
```
The output is `_implementation/slices/<slice_id>/align.md` — a structured handoff file consumed
by `impl-plan-plan-vertical`. The `_implementation/slices/<slice_id>/` dossier is durable:
`impl-slice-commit` freezes it after the slice's atomic commit lands — writes `index.md`, keeps
the phase handoffs as permanent documentation, removes only the transient `progress.yaml`.
No impl-plan skill deletes or freezes the dir itself.
```

- [ ] **Step 5: Fix `skaileup/11_impl-plan/03_plan-vertical/SKILL.md`**

Replace (exact old text, lines 94-97):
```
The output is `_implementation/slices/<slice_id>/plan.md` — a structured handoff file
consumed by `impl-slice/implement`, `impl-slice/test`, and `impl-slice/recap`
in Task 2D. The `_implementation/slices/<slice_id>/` directory is scratch and is deleted
by `impl-slice/commit` after the slice's atomic commit lands.
```
with:
```
The output is `_implementation/slices/<slice_id>/plan.md` — a structured handoff file
consumed by `impl-slice/implement`, `impl-slice/test`, and `impl-slice/recap`.
The `_implementation/slices/<slice_id>/` dossier is durable: `impl-slice-commit` freezes it
after the slice's atomic commit lands — writes `index.md`, keeps the phase handoffs,
removes only the transient `progress.yaml`.
```

- [ ] **Step 6: Verify fix (test passes)**

Run:
```bash
grep -rn "is deleted by\|deletes the entire\|directory is scratch" skaileup/08_concept-slice skaileup/11_impl-plan --include=SKILL.md
python3 skaileup/contracts/scripts/verify_artifacts.py; echo "exit=$?"
python3 skaileup/flows/_meta/verify_flows.py; echo "exit=$?"
```
Expected: zero grep hits; both scripts print `exit=0`.

- [ ] **Step 7: Commit**

```bash
git add skaileup/08_concept-slice/01_brainstorm/SKILL.md skaileup/11_impl-plan/01_brainstorm/SKILL.md skaileup/11_impl-plan/02_align/SKILL.md skaileup/11_impl-plan/03_plan-vertical/SKILL.md
git commit -m "fix(slice-loop): replace stale deleted-dossier prose with Phase-4 freeze model

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Fix `_concept/product-spec/features/` → `_concept/experience/features/` (R0 bug 2)

The producer (`concept-slice-design-feature`) writes `_concept/experience/features/<group>/<slug>.md` (its SKILL.md L70, L126) and the registry pins it (`artifacts.yaml:158`), but the entire `11_impl-plan` consumer cluster reads `_concept/product-spec/features/` — a broken pipeline. Also stale in one `08_concept-slice/04_design-feature` reference file and its tests.

**Files:**
- Modify: `skaileup/11_impl-plan/01_brainstorm/SKILL.md` (lines 3, 37, 42, 96, 105, 131, 137, 167, 169, 217, 260)
- Modify: `skaileup/11_impl-plan/02_align/SKILL.md` (lines 3, 39, 51, 114, 145, 175, 260, 314)
- Modify: `skaileup/11_impl-plan/03_plan-vertical/SKILL.md` (lines 39, 51, 144, 203, 275, 304, 331)
- Modify: `skaileup/11_impl-plan/DOMAIN.md:22`
- Modify: `skaileup/11_impl-plan/03_plan-vertical/validator.py:77` (pinned DoD string)
- Modify: `skaileup/11_impl-plan/02_align/examples/team-todo-comments-align.md:4`
- Modify: `skaileup/11_impl-plan/03_plan-vertical/examples/team-todo-comments-plan.md` (lines 4, 43, 66)
- Modify: `skaileup/11_impl-plan/01_brainstorm/tests/test_impl_plan_brainstorm_validator.py:23`
- Modify: `skaileup/08_concept-slice/04_design-feature/references/feature-portion-rule.md` (lines 11, 28, 34)
- Modify: `skaileup/08_concept-slice/04_design-feature/tests/test_design_feature_validator.py` (lines 27, 50, 79, 91)
- Test: `python3 -m pytest skaileup/11_impl-plan skaileup/08_concept-slice -q`

**Interfaces:**
- Consumes: nothing.
- Produces: canonical path `_concept/experience/features/<group>/<feature_slug>.md` used verbatim by Tasks 5/6 contract text, and validator DoD string `- [ ] \`_concept/experience/features/<group>/<feature_slug>.md\` § Acceptance Criteria all green` that plan.md artifacts must embed.

- [ ] **Step 1: Baseline — run existing validator tests (must pass before the change)**

```bash
python3 -m pytest skaileup/11_impl-plan skaileup/08_concept-slice -q
```
Expected: all collected tests pass (if PyYAML/pytest missing: `pip install pyyaml pytest`). Record the pass count.

- [ ] **Step 2: Write the failing check**

```bash
grep -rn "product-spec/features" skaileup/11_impl-plan skaileup/08_concept-slice | wc -l
```
Expected: ~40 hits (this is the FAIL state; target is 0).

- [ ] **Step 3: Bulk substitute**

```bash
grep -rl "product-spec/features" skaileup/11_impl-plan skaileup/08_concept-slice \
  | xargs sed -i '' 's|product-spec/features|experience/features|g'
```
Note: this rewrites both `_concept/product-spec/features` and bare `product-spec/features` (test fixture strings) — both are intended.

- [ ] **Step 4: Verify zero hits and tests still pass**

```bash
grep -rn "product-spec/features" skaileup/11_impl-plan skaileup/08_concept-slice; echo "hits-exit=$?"
python3 -m pytest skaileup/11_impl-plan skaileup/08_concept-slice -q
python3 skaileup/contracts/scripts/verify_artifacts.py; echo "exit=$?"
python3 skaileup/flows/_meta/verify_flows.py; echo "exit=$?"
```
Expected: `hits-exit=1` (no matches); pytest same pass count as Step 1 (the fixture strings and the validator pin were changed together, so tests stay green); both verifiers `exit=0`.

- [ ] **Step 5: Sanity-check the validator pin specifically**

Confirm `skaileup/11_impl-plan/03_plan-vertical/validator.py` line 77 now reads exactly:
```python
    "- [ ] `_concept/experience/features/<group>/<feature_slug>.md` § Acceptance Criteria all green",
```
and `skaileup/11_impl-plan/03_plan-vertical/SKILL.md` line 304 (the DoD checklist item) reads the identical string — validator pins exact-string match.

- [ ] **Step 6: Commit**

```bash
git add skaileup/11_impl-plan skaileup/08_concept-slice
git commit -m "fix(impl-plan): read features from canonical _concept/experience/features/ path

Producer (concept-slice-design-feature) and registry (artifacts.yaml) pin
experience/features; the impl-plan cluster read the nonexistent
product-spec/features. Fixed in SKILL.md, DOMAIN.md, validator pin, examples,
tests, and the design-feature portion-rule reference.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Create `skaileup/contracts/walkthrough_renderer.md` (Cluster 1, part 1)

Single owner for everything the four walkthrough renderers currently quadruplicate (~600-800 lines total). Content below is lifted verbatim from the anchor skill `skaileup/05_mockup-walkthrough/01_b_static-html/SKILL.md` (L93-170, L421-511, L525-539) and astro's shared error table (L689-701), with `product-spec/features` corrected to `experience/features`.

**Files:**
- Create: `skaileup/contracts/walkthrough_renderer.md`
- Modify: `skaileup/contracts/CONTRACT.md:28` (append one Contents bullet)
- Test: `python3 skaileup/contracts/scripts/verify_artifacts.py` (exit 0); grep checks below

**Interfaces:**
- Consumes: canonical feature path from Task 2.
- Produces: contract sections cited by Task 4 with these exact anchors: `§ data-spec-* attribute table`, `§ screen_id vs screen_path`, `§ kind → DOM tag mapping`, `§ Auto-slug fallback`, `§ Manifest schema`, `§ Field semantics`, `§ warnings[].kind enum`, `§ Shared error handling`, `§ Shared MUST / NEVER`. Manifest `schema_version: "1.0"`.

- [ ] **Step 1: Write the contract file**

Create `skaileup/contracts/walkthrough_renderer.md` with exactly this content:

````markdown
# Walkthrough Renderer Contract

**schema_version: "1.0"** · Owner of everything shared by the four
`mockup-walkthrough-*` renderers: `static-html` (reference implementation),
`astro`, `lit`, `framework`. Each renderer's SKILL.md owns ONLY its
technology-specific scaffold (build setup, templates, config) and cites this
file for the behaviour below. The `mockup-feedback-*` cluster resolves clicks
identically across renderers because of this contract.

**Change policy.** Pinned. Do not change any table, field name, or warning
kind without a coordinated update to `mockup-feedback-annotate` and a
`schema_version` bump.

## data-spec-* attribute table

| DOM location | Attribute | Value | Source |
|---|---|---|---|
| `<body>` of every `screen/<group>/<name>.html` | `data-spec-screen` | screen path stem (e.g. `01_user_auth/login`) | screen file path |
| every annotatable child node (form fields, buttons, links, images, regions, list items, nav items) | `data-spec-element` | element id (kebab-case) | `elements:` entry, or auto-slug |
| same node, when no explicit `elements:` entry exists for it | `data-spec-provisional` | literal string `"true"` | absent in YAML |
| `<body>` of every `journey/<id>.html` | `data-spec-journey` | journey id from stories.yaml | stories.yaml |
| each step link inside `journey/<id>.html` | `data-spec-screen` | the screen-stem of that step's screen | journey step entry |
| `<body>` of `index.html` | `data-spec-index` | literal string `"true"` | (none — site root marker) |

**The renderer MUST NOT add `data-spec-*` attributes outside this table.**
Feedback-annotate ignores unknown ones, but a lean attribute set keeps drift
visible.

## screen_id vs screen_path

Both forms are kept in `manifest.json` so feedback consumers can pick:

- `screen_path`: full repo-relative path with extension, e.g.
  `experience/screens/01_user_auth/login.md`. Used in journey
  `screen_sequence`, in `screens[].screen_path`, and in `source_anchor`s.
- `screen_id`: path stem under `experience/screens/` without `.md`, e.g.
  `01_user_auth/login`. Used in `data-spec-screen`, in the rendered HTML
  filename, and in `screens[].screen_id`.

## kind → DOM tag mapping

| kind | rendered tag | notes |
|---|---|---|
| `input` | `<input>` | with `name="<id>"` and `aria-label="<label>"` |
| `button` | `<button>` | label as inner text |
| `link` | `<a>` | `href="#"` placeholder |
| `image` | `<img>` | `src="#"` placeholder, `alt="<label>"` |
| `text` | `<span>` | label as inner text |
| `region` | `<section>` | label as inner `<h3>` |
| `list` | `<ul>` | empty list with placeholder `<li>` |
| `form` | `<form>` | placeholder; nested inputs not auto-derived |
| `nav` | `<nav>` | placeholder list of links |
| `media` | `<figure>` | `<figcaption>` carries label |
| `custom` | `<div>` | label as inner text; renderable but unstyled |

States beyond `default` are rendered as adjacent `<span class="state-<n>">`
children of the element so visual reviewers can see state coverage.

## Auto-slug fallback

The renderer's portion of the hybrid ID strategy (`elements_block.md`
§ "Hybrid ID strategy"). When a screen file has no `elements:` block, OR has
a partial one, the renderer MUST:

  1. Walk the screen body and identify renderable widgets by source order.
     **Source set:** (a) markdown headings (`##`, `###`), (b) form-field
     lines matching `[label]: input|button|...` pattern, (c) acceptance-
     criteria mentions in body text. (Auto-slug net is intentionally wide;
     explicit ids always win on collision.)
  2. For each widget not present in `elements:` (matched by label-equality,
     case-insensitive), generate an id by:
     - Lowercase the label
     - Replace any non `[a-z0-9]` run with a single `-`
     - Trim leading/trailing `-`
     - If empty (label was e.g. `"…"`), fall back to `<kind>-<n>` where
       `n` is a 1-based counter scoped per-screen-per-kind
       (`button-1`, `button-2`, `input-1`, ...).
     - On collision with another auto-slugged id within the same screen,
       append `-2`, `-3`, ... until unique.
     - Collision with an explicit id: warning `kind: "auto_slug_collision"`
       and the auto-slugged element gets the suffixed id.
  3. Render the node with `data-spec-element="<auto-slugged-id>"` AND
     `data-spec-provisional="true"`.
  4. Append a `warnings[]` entry of `kind: "auto_slugged"` to
     `manifest.json` for each auto-slugged element.
  5. **Never** mutate the source `experience/screens/<group>/<name>.md`
     file. Promotion of provisional ids is `mockup-feedback-triage`'s job.

## Manifest schema

The contract handed to `mockup-feedback-annotate`. Field names pinned exactly.
`<variant>` is the renderer's short name (`static-html`, `astro`, `lit`,
`framework`); `renderer_version` is the renderer SKILL.md's
`metadata.version`.

```json
{
  "schema_version": "1.0",
  "renderer": "mockup-walkthrough-<variant>",
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
      "source": "experience/journeys/stories.yaml#user-signs-in",
      "screen_sequence": [
        "experience/screens/01_user_auth/login.md",
        "experience/screens/02_dashboard/home.md"
      ]
    }
  ],
  "features": [
    {
      "feature_path": "experience/features/01_user_auth/login.md",
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

### Field semantics

- `schema_version`: bump on breaking change. Feedback cluster pins `^1.0`.
- `renderer` / `renderer_version`: identifies which walkthrough variant
  produced the site.
- `generated_at`: ISO-8601 UTC; lets feedback-annotate detect stale renders.
- `source_root`: relative path the screen paths are anchored to (always
  `experience/screens`).
- `screens[].screen_path`: full path with `.md`. Used by feedback-annotate
  when it needs to read the source file.
- `screens[].screen_id`: the path stem `<group>/<name>` (no `.md`); the
  value emitted in `data-spec-screen`.
- `screens[].rendered_html`: site-relative path to the rendered HTML.
- `screens[].elements[].element_id`: the value emitted in
  `data-spec-element`.
- `screens[].elements[].provisional`: `true` when auto-slugged
  (mirrors `data-spec-provisional`).
- `screens[].elements[].source_anchor`: fragment-style pointer back to the
  source file. Explicit ids: `#elements/<element_id>`. Provisional:
  `#auto/<element_id>` (no entry yet in the YAML).
- `journeys[].screen_sequence`: ordered list of screen source paths. Same
  order drives the rendered "Next →" links inside `journey/<id>.html`.
- Sorting: `screens[]` by `screen_path`, `journeys[]` by `journey_id`,
  `features[]` by `feature_path` — deterministic diffs. Write atomically
  (tmp → fsync → rename).

## warnings[].kind enum

`auto_slugged`, `auto_slug_collision`, `missing_layout`, `missing_feature`,
`unknown_element_kind`, `missing_screen`, `missing_screen_sequence`,
`no_journeys`. Renderer-specific additions are allowed and documented in that
renderer's SKILL.md (e.g. astro's `stale_tailwind_config`). Extend cautiously
— the feedback cluster switches on this field.

## Shared error handling

| Condition | Behaviour |
|---|---|
| Malformed YAML in screen file | Fail loudly, exit non-zero, name the offending file |
| Screen in journey but absent on disk | `manifest.warnings[]` `kind: "missing_screen"` + dead-end `<li class="journey-step-missing">` |
| `screen_sequence` absent for a journey | `manifest.warnings[]` `kind: "missing_screen_sequence"`, skip that journey render |
| Zero journeys in `stories.yaml` | Render "No journeys defined", `kind: "no_journeys"` |
| Missing `experience/features/` | Soft gate, `kind: "missing_feature"`, continue; `manifest.features[]` → `[]` |
| Unknown `elements:` kind | Render as `custom`, `kind: "unknown_element_kind"` |
| `layout:` reference to non-existent file | `kind: "missing_layout"`, fall back to the renderer's default shell |
| Auto-slug collision | `kind: "auto_slug_collision"`, suffix auto id with `-2`, `-3`, … |

## Screen-in-multiple-journeys rule

When a screen appears in two or more journeys, each `journey/<id>.html`
retains its own "Next →" link only inside the journey HTML. The screen HTML
itself does NOT embed journey-specific navigation (else screen renders couple
to journey state). Cross-journey continuation is solely owned by
`journey/<id>.html`; the screen's footer may list the journeys it
participates in, linking to the journey pages.

## Shared MUST / NEVER

MUST  emit `data-spec-screen` on every screen `<body>`
MUST  emit `data-spec-element` on every annotatable child node
MUST  emit `data-spec-provisional="true"` on auto-slugged element nodes
MUST  emit `data-spec-journey="<id>"` on every journey `<body>`
MUST  emit `data-spec-index="true"` on `index.html` `<body>`
MUST  write `manifest.json` conforming to `§ Manifest schema` (`schema_version: "1.0"`)
MUST  sort manifest arrays lexicographically (`screens` by `screen_path`, `journeys` by `journey_id`, `features` by `feature_path`)
MUST  HTML-escape every interpolated string (labels, ids, paths, titles) including quotes

NEVER  emit `data-spec-*` attributes outside the pinned table
NEVER  mutate source files (`experience/screens/**`, `experience/journeys/stories.yaml`, `design/tokens.json`, `experience/features/**`) — renderers are read-only on inputs
NEVER  inject journey-step navigation into `screen/**/*.html` — cross-journey continuation lives only in `journey/<id>.html`
NEVER  inline absolute filesystem paths into `manifest.json` — repo-relative paths only
````

- [ ] **Step 2: Register in CONTRACT.md**

In `skaileup/contracts/CONTRACT.md`, after line 28 (`- **\`skill_testing.md\`** — …`), append:
```markdown
- **`walkthrough_renderer.md`** — Shared renderer contract for all `mockup-walkthrough-*` variants: data-spec attribute table, manifest schema v1.0, auto-slug rule, shared error handling and MUST/NEVER.
```

- [ ] **Step 3: Verify**

```bash
grep -c "data-spec" skaileup/contracts/walkthrough_renderer.md
python3 skaileup/contracts/scripts/verify_artifacts.py; echo "exit=$?"
python3 skaileup/flows/_meta/verify_flows.py; echo "exit=$?"
```
Expected: grep count ≥ 15; both `exit=0` (contracts dir is not scanned for artifacts blocks, so no new errors).

- [ ] **Step 4: Commit**

```bash
git add skaileup/contracts/walkthrough_renderer.md skaileup/contracts/CONTRACT.md
git commit -m "feat(contracts): add walkthrough_renderer.md — single owner of the shared renderer contract

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Strip the four walkthrough renderers to scaffold + citation (Cluster 1, part 2)

Replace each renderer's duplicated blocks with a pointer to `contracts/walkthrough_renderer.md`. Renderer-specific rules stay. Expected shrink: static-html 556→~330, astro 761→~600, lit 835→~700, framework 691→~560.

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_b_static-html/SKILL.md` (L86-170, L421-511, L525-539, plus path fix)
- Modify: `skaileup/05_mockup-walkthrough/01_c_astro/SKILL.md` (L84-135, STEP 7 JSON ~L615-676, L689-701, MUST/NEVER block)
- Modify: `skaileup/05_mockup-walkthrough/01_d_lit/SKILL.md` (L124-~180 shared subsections, manifest JSON, MUST/NEVER block)
- Modify: `skaileup/05_mockup-walkthrough/01_e_framework/SKILL.md` (L114-~170 shared subsections, manifest JSON, MUST/NEVER block)
- Modify: any `validator.py` under `skaileup/05_mockup-walkthrough/` containing `product-spec/features` (grep-driven)
- Test: line counts + grep checks + both verifiers

**Interfaces:**
- Consumes: Task 3 section anchors (exact): `§ data-spec-* attribute table`, `§ screen_id vs screen_path`, `§ kind → DOM tag mapping`, `§ Auto-slug fallback`, `§ Manifest schema`, `§ Shared error handling`, `§ Shared MUST / NEVER`.
- Produces: renderer SKILL.md files whose only shared-contract text is the pointer block below (used again verbatim in each file).

The reusable pointer block (inserted in each renderer, with `<variant>` filled in):
```markdown
## Renderer Contract

This renderer implements the shared walkthrough renderer contract —
`contracts/walkthrough_renderer.md` (schema_version "1.0"): data-spec-*
attribute table, screen_id vs screen_path, kind → DOM tag mapping, auto-slug
fallback, manifest schema + field semantics, warnings[].kind enum, shared
error handling, screen-in-multiple-journeys rule, shared MUST/NEVER. Read it
before rendering; it is pinned and MUST NOT be restated here.

Renderer-specific manifest values: `renderer: "mockup-walkthrough-<variant>"`,
`renderer_version:` this SKILL.md's `metadata.version`.
```

- [ ] **Step 1: static-html — replace the Renderer Contract section**

In `skaileup/05_mockup-walkthrough/01_b_static-html/SKILL.md`, delete everything from the line `## Renderer Contract` (L86) up to but NOT including `## Inputs` (L172) — i.e. the attr table, screen_id/screen_path, kind mapping, and auto-slug subsections. Insert the pointer block above with `<variant>` = `static-html`, plus this one anchor-role sentence at its end:
```markdown
static-html is the contract's reference implementation: when a behaviour is
ambiguous, this renderer's output is the tie-breaker.
```

- [ ] **Step 2: static-html — replace the Manifest Schema section**

Delete from the line `## Manifest Schema` (was L421) up to but NOT including `## STEP 6: Validate` (was L513) — the JSON example and `### Field semantics`. Insert:
```markdown
## Manifest Schema

Pinned in `contracts/walkthrough_renderer.md` § Manifest schema (+ § Field
semantics, § warnings[].kind enum). This renderer emits
`renderer: "mockup-walkthrough-static-html"`.
```

- [ ] **Step 3: static-html — split MUST/NEVER into specific-only**

Replace the whole `## MUST / NEVER` section body (was L525-539) with:
```markdown
Shared MUST/NEVER: `contracts/walkthrough_renderer.md` § Shared MUST / NEVER
(data-spec emission, manifest schema + sorting, escaping, no source mutation,
no journey-nav injection, no absolute paths).

MUST  escape via `html.escape(..., quote=True)` specifically (the contract's escape rule, pinned to the stdlib call)
MUST  use only stdlib + PyYAML in the renderer (no Jinja, no Mako, no build tool)

NEVER  include a JS framework, a bundler artefact, or any `<script src="...">` pointing at a non-relative URL — the site is openable as a static set of files
```

- [ ] **Step 4: static-html — drop the now-duplicated multi-journey subsection**

Delete the `### Screen-in-multiple-journeys rule` subsection (was L373-384, inside STEP 4) and replace with the single line:
```markdown
  Screen-in-multiple-journeys rule: see `contracts/walkthrough_renderer.md` § Screen-in-multiple-journeys rule.
```
Keep the two NEVER-style sentences already covered by the contract out (they are in § Shared MUST / NEVER).

- [ ] **Step 5: static-html — REFERENCES + feature-path fix**

In the `REFERENCES` block (was L241-249), add as first line:
```
  contracts/walkthrough_renderer.md     — shared renderer contract (pinned)
```
Then fix paths in this file:
```bash
sed -i '' 's|product-spec/features|experience/features|g' skaileup/05_mockup-walkthrough/01_b_static-html/SKILL.md
```

- [ ] **Step 6: astro — same treatment**

In `skaileup/05_mockup-walkthrough/01_c_astro/SKILL.md`:
1. Delete from `## Renderer Contract` (L84) through the end of the `### Auto-slug fallback` subsection (ends just before the next `##`/`###` heading after L135; keep the astro-specific sentence "There is NO separate top-level `auto_slugged[]` array — `provisional: true` lives on the element" by moving it into the inserted block). Insert the pointer block (`<variant>` = `astro`) plus:
```markdown
Astro-specific: the template emits `data-spec-provisional="true"` where
`element.provisional === true`; there is NO separate top-level
`auto_slugged[]` array — `provisional: true` lives on the element object.
```
2. In STEP 7, delete the JSON example (the fenced ```json block, was ~L623-670) and the two sort/atomic-write sentences after it; keep the step intro and the template-only-fields warning. Insert after the intro:
```markdown
Emit the pinned schema — `contracts/walkthrough_renderer.md` § Manifest
schema — with `renderer: "mockup-walkthrough-astro"`. Sorting + atomic write
per § Field semantics.
```
3. Replace the `### Inherited from static-html (identical behaviour)` heading + table (L689-701) with:
```markdown
### Shared conditions

See `contracts/walkthrough_renderer.md` § Shared error handling.
```
Keep the `### Astro-specific` table unchanged. In the `### warnings[].kind enum` subsection, keep only:
```markdown
Shared enum per `contracts/walkthrough_renderer.md` § warnings[].kind enum;
`stale_tailwind_config` is the only Astro-specific addition.
```
4. In `## MUST / NEVER`, delete these shared lines (now contract-owned): `MUST emit data-spec-screen…`, `MUST emit data-spec-element…`, `MUST emit data-spec-provisional…`, `MUST emit data-spec-journey…`, `MUST emit data-spec-index…`, `MUST write manifest.json conforming…`, `MUST sort manifest arrays lexicographically`, `NEVER emit data-spec-* attributes outside the pinned table`, `NEVER mutate source files…`, `NEVER inject journey-step navigation…`, `NEVER inline absolute filesystem paths in manifest.json`. Insert at the top of the section:
```markdown
Shared MUST/NEVER: `contracts/walkthrough_renderer.md` § Shared MUST / NEVER.
```
Keep all astro-specific lines (`emptyOutDir`, `build.format`, `outDir`, `specs.json`, `global.css`, `getStaticPaths`, `NEVER regenerate astro.config…`, `NEVER create a dist/…`, the `auto_slugged[]` NEVER).
5. Add to REFERENCES: `contracts/walkthrough_renderer.md — shared renderer contract (pinned)`.
6. `sed -i '' 's|product-spec/features|experience/features|g' skaileup/05_mockup-walkthrough/01_c_astro/SKILL.md`

- [ ] **Step 7: lit — same treatment**

In `skaileup/05_mockup-walkthrough/01_d_lit/SKILL.md`: keep the lit-specific light-DOM rationale paragraphs (L102-123 — `createRenderRoot`/shadow-DOM discussion); delete the four shared subsections (`### data-spec-* attribute table` L124 through end of `### Auto-slug fallback` section); insert the pointer block (`<variant>` = `lit`) directly after the light-DOM paragraphs. Replace the manifest JSON example (locate with `grep -n '"schema_version"' …/01_d_lit/SKILL.md`) with the same one-paragraph pointer as astro Step 6.2 (renderer value `mockup-walkthrough-lit`). Apply the same MUST/NEVER split as astro Step 6.4 (delete the 11 shared lines if present verbatim; keep lit-specific ones). Add the REFERENCES line. Run the same `sed` feature-path fix on this file.

- [ ] **Step 8: framework — same treatment**

In `skaileup/05_mockup-walkthrough/01_e_framework/SKILL.md`: keep the framework-specific SSR paragraphs (L106-113 and L234-252 area — built HTML must carry `data-spec-*` server-side); delete the shared subsections (`### data-spec-* attribute table` L114 through end of `### Auto-slug fallback`); insert the pointer block (`<variant>` = `framework`). Replace the manifest JSON example with the pointer paragraph (renderer value `mockup-walkthrough-framework`). Same MUST/NEVER split, same REFERENCES line, same `sed` feature-path fix.

- [ ] **Step 9: Fix any walkthrough validators with the stale feature path**

```bash
grep -rln "product-spec" skaileup/05_mockup-walkthrough/ | xargs -r sed -i '' 's|product-spec/features|experience/features|g'
grep -rn "product-spec" skaileup/05_mockup-walkthrough/; echo "exit=$?"
```
Expected final grep: `exit=1` (no hits).

- [ ] **Step 10: Verify**

```bash
wc -l skaileup/05_mockup-walkthrough/01_b_static-html/SKILL.md skaileup/05_mockup-walkthrough/01_c_astro/SKILL.md skaileup/05_mockup-walkthrough/01_d_lit/SKILL.md skaileup/05_mockup-walkthrough/01_e_framework/SKILL.md
grep -c "kind → DOM" skaileup/05_mockup-walkthrough/*/SKILL.md skaileup/contracts/walkthrough_renderer.md
python3 skaileup/contracts/scripts/verify_artifacts.py; echo "exit=$?"
python3 skaileup/flows/_meta/verify_flows.py; echo "exit=$?"
```
Expected: static-html ≤ 360, astro ≤ 620, lit ≤ 720, framework ≤ 580; `kind → DOM` appears ONLY in the contract (count 0 in each SKILL.md, ≥1 in contract); both verifiers `exit=0`.

- [ ] **Step 11: Commit**

```bash
git add skaileup/05_mockup-walkthrough skaileup/contracts
git commit -m "refactor(walkthrough): renderers cite contracts/walkthrough_renderer.md instead of restating (~500 lines removed)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: Create `skaileup/contracts/slice_loop.md` + promote grill bank (Cluster 2, part 1)

**Files:**
- Create: `skaileup/contracts/slice_loop.md`
- Create (git mv + extend): `skaileup/contracts/grill_bank.md` from `skaileup/11_impl-plan/02_align/references/grill-style.md`
- Modify: `skaileup/contracts/CONTRACT.md` (two Contents bullets)
- Test: `python3 skaileup/contracts/scripts/verify_artifacts.py` exit 0

**Interfaces:**
- Consumes: freeze wording from Task 1; canonical feature path from Task 2.
- Produces: section anchors cited by Task 6: `slice_loop.md` §§ `Tier gate`, `Slug rule`, `Resume-or-fresh`, `Handoff frontmatter`, `Context isolation`, `Freeze lifecycle`; `grill_bank.md` §§ `The 9 Pillars`, `EARS provenance`. Slug regex constant `^[a-z][a-z0-9-]{1,47}$`.

- [ ] **Step 1: Write `skaileup/contracts/slice_loop.md`**

Exact content:

````markdown
# Slice Loop Contract

Shared lifecycle rules for the two per-feature slice loops. Consumed by
`concept-slice-{brainstorm,align,scope-feature,design-feature}`,
`impl-plan-{brainstorm,align,plan-vertical}`, and the `impl-slice-*` chain.
Cite these sections instead of restating them.

## Tier gate

| `scope.yaml` tier | concept-loop entry | impl-loop entry |
|---|---|---|
| `appbuilder-mvp` | (concept loop skipped) | `impl-plan-plan-vertical` |
| `appbuilder-simple` | `concept-slice-align` | `impl-plan-align` |
| `appbuilder-standard` | `concept-slice-brainstorm` | `impl-plan-brainstorm` |
| `appbuilder-complex` | `concept-slice-brainstorm` | `impl-plan-brainstorm` |

Every loop skill MUST refuse when `_concept/_meta/scope.yaml` is missing
(iron_laws § 7) and when `scope.tier` sits outside its row above. Refuse
message format (pinned):

> "[<skill>] tier=<tier> does not run <phase>.
>  <one sentence naming the correct entry skill for that tier>."

## Slug rule

`slice_id` regex: `^[a-z][a-z0-9-]{1,47}$`

Derivation from a human title: lowercase → replace each non-`[a-z0-9]` run
with a single `-` → trim leading/trailing `-` → truncate to 48 chars.
Impl side: `slice_id := feature_slug` verbatim (same regex) — never
re-derived from the title. `feature_slug` resolves by globbing
`_concept/experience/features/*/<feature_slug>.md`; refuse on zero or >1
matches (>1 = slug collision across groups; name the matches, ask).

## Resume-or-fresh

When the phase's target handoff file already exists:

1. NEVER overwrite silently.
2. Ask STANDALONE: "(a) resume — load and refine the existing file, or
   (b) start fresh". Entry-phase skills may offer a `-2`-suffixed new slug
   for (b); every fresh-overwrite requires explicit confirmation before any
   write.
3. On resume: load the existing file, show what would change, ask before
   writing.

When the dossier directory does not exist: `mkdir -p` it.

## Handoff frontmatter

| Side | Keys (all required, this order) |
|---|---|
| concept (`_concept/slices/<id>/`) | `slice_id`, `feature_title`, `phase`, `tier`, `created_at`, `last_updated` |
| impl (`_implementation/slices/<id>/`) | `slice_id`, `feature_title`, `feature_path`, `phase`, `tier`, `created_at`, `last_updated` |

Rules: `phase` = the writing skill's phase name; `created_at` copied from the
predecessor handoff when present, else `now()` (ISO-8601 UTC);
`last_updated` = `now()`; `slice_id` / `feature_title` / `feature_path`
copied VERBATIM from the predecessor — never re-derived.

## Context isolation

`/clear` between every phase. A phase reads ONLY its predecessor's handoff
plus the durable concept artifacts it names — no phase carries the whole
slice in context (dumb-zone guard, ~100k tokens).

## Freeze lifecycle

Slice dossiers are frozen, never deleted. The terminators
(`concept-slice-design-feature`, `impl-slice-commit`) write `index.md` and
keep every phase handoff as permanent per-feature documentation;
`impl-slice-commit` additionally removes the transient `progress.yaml`.
No other loop skill deletes or freezes the dossier.
````

- [ ] **Step 2: Promote and extend the grill bank**

```bash
git mv skaileup/11_impl-plan/02_align/references/grill-style.md skaileup/contracts/grill_bank.md
```
Then edit `skaileup/contracts/grill_bank.md`: change the title line `# impl-plan-align — Grill Style Reference` to `# Grill Bank — shared align-interview reference`, change the first paragraph's opening `The implementation-readiness grill is` to `The align grill (concept and impl side) is`, and append at the end of the file:

```markdown
## Which pillars run on which side

Both aligns run the same seven core pillars — state transitions, boundary
inputs, concurrency, permissions, persistence/recovery, errors,
cross-feature data. `impl-plan-align` adds performance and test seam
(9 total). Use the "Good question" phrasing from the pillar table; adapt the
nouns to the feature. One question per message, wait for the answer
(iron_laws § 9).

## EARS provenance — the one real difference

- `concept-slice-align` GENERATES EARS acceptance criteria from the grill:
  one per in-scope happy-path bullet from brainstorm.md, plus confirmed edge
  cases. This is where EARS lines are born.
- `impl-plan-align` COPIES EARS criteria VERBATIM from the frozen
  `feature.md` into `## Acceptance handoff` — it never re-authors, rewrites,
  or "improves" them.
```

- [ ] **Step 3: Register both in CONTRACT.md**

Append to the Contents list in `skaileup/contracts/CONTRACT.md`:
```markdown
- **`slice_loop.md`** — Shared slice-loop lifecycle: tier gates, slug rule, resume-or-fresh, handoff frontmatter keys, /clear isolation, freeze semantics.
- **`grill_bank.md`** — Shared align-grill question bank (9 pillars, tone, anti-patterns, EARS provenance) for concept-slice-align and impl-plan-align.
```

- [ ] **Step 4: Fix the dangling reference to the moved file**

`skaileup/11_impl-plan/02_align/SKILL.md:133` currently reads:
```
  impl-plan/align/references/grill-style.md                       — interview tone reference + 9 grill pillars
```
Replace with:
```
  contracts/grill_bank.md                                         — grill question bank: tone + 9 pillars + EARS provenance
```

- [ ] **Step 5: Verify + commit**

```bash
test ! -f skaileup/11_impl-plan/02_align/references/grill-style.md && echo moved
grep -rn "grill-style" skaileup/ | grep -v devlog; echo "exit=$?"
python3 skaileup/contracts/scripts/verify_artifacts.py; echo "exit=$?"
python3 skaileup/flows/_meta/verify_flows.py; echo "exit=$?"
git add -A skaileup/contracts skaileup/11_impl-plan
git commit -m "feat(contracts): add slice_loop.md; promote grill bank to contracts/grill_bank.md

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```
Expected: `moved` printed; dangling-ref grep `exit=1`; verifiers `exit=0`.

---

### Task 6: Point the 7 loop skills at slice_loop.md / grill_bank.md (Cluster 2, part 2)

**Files:**
- Modify: `skaileup/08_concept-slice/01_brainstorm/SKILL.md` (REFERENCES, MUST lines 100-101, STEP 2 L125-138)
- Modify: `skaileup/08_concept-slice/02_align/SKILL.md` (REFERENCES, STEPs 3-9 L162-189, STEP 10a L196-208)
- Modify: `skaileup/11_impl-plan/01_brainstorm/SKILL.md` (REFERENCES, MUST L136-137, STEP 2 L164-185)
- Modify: `skaileup/11_impl-plan/02_align/SKILL.md` (REFERENCES, STEPs 4-12 L202-236, STEP 13a L243-252)
- Modify: `skaileup/11_impl-plan/03_plan-vertical/SKILL.md` (REFERENCES, STEP 1 slug/gate lines)
- Modify: `skaileup/08_concept-slice/03_scope-feature/SKILL.md` (REFERENCES line only)
- Modify: `skaileup/08_concept-slice/04_design-feature/SKILL.md` (REFERENCES line only)
- Modify: `skaileup/12_impl-slice/04_test/SKILL.md:29` (hint cites slug rule)
- Test: pytest on both domains + both verifiers

**Interfaces:**
- Consumes: `contracts/slice_loop.md` §§ Tier gate / Slug rule / Resume-or-fresh / Handoff frontmatter / Freeze lifecycle; `contracts/grill_bank.md` §§ The 9 Pillars / EARS provenance (Task 5).
- Produces: nothing new for later tasks (Task 9 edits the same files' write-dance).

The REFERENCES line to add (identical in all 7 loop skills, adjust column alignment to the file's style):
```
  contracts/slice_loop.md                    — tier gates, slug rule, resume-or-fresh, handoff keys, freeze lifecycle
```

- [ ] **Step 1: concept-slice-brainstorm**

In `skaileup/08_concept-slice/01_brainstorm/SKILL.md`:
1. Add the REFERENCES line after the `contracts/skill_grammar.md` line (L88).
2. Replace MUST lines 100-101:
```
MUST  derive slice_id from feature_title via the kebab-case rule (lower → non-alnum→hyphen → strip-trim → max 48 chars) UNLESS slice_id_override is supplied
MUST  refuse to overwrite an existing _concept/slices/<slice_id>/ — ask the user to (a) resume the existing slice, or (b) suffix -2 to the slug
```
with:
```
MUST  derive slice_id per contracts/slice_loop.md § Slug rule UNLESS slice_id_override is supplied
MUST  apply contracts/slice_loop.md § Resume-or-fresh when _concept/slices/<slice_id>/ already exists
```
3. Replace the STEP 2 body from `  - Derive slice_id from feature_title using the kebab-case rule, OR use` (L128) through `      - $ mkdir -p _concept/slices/<slice_id>/` (L138) with:
```
  - Derive slice_id per contracts/slice_loop.md § Slug rule (or slice_id_override;
    validate against the regex there).
  - Apply contracts/slice_loop.md § Resume-or-fresh to _concept/slices/<slice_id>/brainstorm.md
    (offer (a) resume, (b) fresh slice with -2-suffixed slug).
```

- [ ] **Step 2: concept-slice-align**

In `skaileup/08_concept-slice/02_align/SKILL.md`:
1. Add the REFERENCES line, and add below it:
```
  contracts/grill_bank.md                    — grill question bank: tone + pillars + EARS provenance
```
2. Replace STEPs 3-9 (L162-189, the seven per-pillar question steps) with ONE step:
```
STEP 3: Run the grill (one pillar per STANDALONE message)
  Pillars for the concept side (contracts/grill_bank.md § The 9 Pillars —
  use the "Good question" phrasing, adapt nouns to this feature):
    1. State transitions
    2. Boundary inputs
    3. Concurrency
    4. Permissions matrix (build a role × action table; mark unknowns TBD)
    5. Persistence + recovery
    6. Errors
    7. Cross-feature touch points
  Send ONE question per message; wait for each answer (iron_laws § 9). If an
  answer is vague, re-ask the same pillar from a different angle before
  moving on (grill_bank.md § Tone).
```
3. Renumber the following steps (old STEP 10 → STEP 4, 10a → 4a, 11 → 5, 12 → 6, 13 → 7) and update the CHECKLIST wording `All grill questions sent STANDALONE` → `All 7 pillars grilled STANDALONE` (keep every other checklist item byte-identical).
4. Shrink STEP 10a (now 4a) body (old L197-208) to:
```
  Apply contracts/domain_model.md the moment vocabulary/decisions crystallise:
  - TERM pinned → write/update _concept/blueprint/glossary.md (term, 1-2
    sentence definition, `_Avoid_:` list; lazy-create; zero implementation detail).
  - DECISION passing the 3-test gate → append ADR to _concept/decisions.md
    (date + title + 1-3 sentences); failing the gate it stays in
    "## Resolved questions".
  - Never invent a definition or decision the user did not confirm.
```
5. In the MUST at L116, replace:
```
MUST  produce acceptance criteria in EARS format ("WHEN <trigger>, THE <system> SHALL <response>")
```
with:
```
MUST  produce acceptance criteria in EARS format (contracts/acceptance_criteria.md § EARS template); this side GENERATES them (grill_bank.md § EARS provenance)
```
(The § EARS template section is added in Task 9 Step 2 — if executing tasks out of order, do Task 9 Step 2 first.)

- [ ] **Step 3: impl-plan-brainstorm**

In `skaileup/11_impl-plan/01_brainstorm/SKILL.md`:
1. Add the REFERENCES line after L117 (`contracts/skill_grammar.md`).
2. Replace MUST lines 136-137:
```
MUST  set slice_id := feature_slug (raw kebab-case slug, regex ^[a-z][a-z0-9-]{1,47}$) — same rule as concept-slice
MUST  derive the {group} segment of feature_path by globbing _concept/experience/features/*/<feature_slug>.md and refusing if zero or >1 matches
```
with:
```
MUST  set slice_id := feature_slug per contracts/slice_loop.md § Slug rule (verbatim, never re-derived)
MUST  resolve feature_path per contracts/slice_loop.md § Slug rule (glob _concept/experience/features/*/<feature_slug>.md; refuse on zero or >1 matches)
```
3. Replace the STEP 2 re-entry branch (L177-185, from `  - Check whether _implementation/slices/<slice_id>/ already exists.` to `      - $ mkdir -p _implementation/slices/<slice_id>/`) with:
```
  - Apply contracts/slice_loop.md § Resume-or-fresh to
    _implementation/slices/<slice_id>/brainstorm.md.
```

- [ ] **Step 4: impl-plan-align**

In `skaileup/11_impl-plan/02_align/SKILL.md`:
1. REFERENCES: add the slice_loop line (grill_bank line already fixed in Task 5 Step 4).
2. Replace STEPs 4-12 (L202-236, the nine per-pillar question steps) with ONE step:
```
STEP 4: Run the grill (one pillar per STANDALONE message)
  All 9 pillars (contracts/grill_bank.md § The 9 Pillars — use the "Good
  question" phrasing, adapt nouns to this feature):
    1. State transitions          6. Errors
    2. Boundary inputs            7. Cross-feature data
    3. Concurrency                8. Performance
    4. Permissions (role × action matrix, every cell)
    5. Persistence and offline    9. Test seam
  Send ONE question per message; wait for each answer (iron_laws § 9). Skip a
  pillar only when brainstorm.md already answered it — cite that answer in
  "## Decisions made" (grill_bank.md § Anti-patterns).
```
3. Renumber following steps (old 13 → 5, 13a → 5a, 14 → 6, 15 → 7, 16 → 8) and keep the CHECKLIST items byte-identical except `All grill questions sent as STANDALONE messages; each answered before next` → `All 9 pillars grilled STANDALONE; each answered before next`.
4. Shrink STEP 13a (now 5a) body (old L244-252) to the same 7-line domain_model.md citation block as Task 6 Step 2.4, with `_concept/decisions.md` replaced by `_implementation/decisions.md` and `"## Resolved questions"` replaced by `align.md's "## Decisions made"`.

- [ ] **Step 5: impl-plan-plan-vertical + remaining touch-ups**

1. `skaileup/11_impl-plan/03_plan-vertical/SKILL.md`: add the REFERENCES line; in STEP 1 replace
```
  - Resolve feature_slug → feature_path:
    $ ls _concept/experience/features/*/<feature_slug>.md
    Refuse if zero or >1 matches.
  - slice_id := feature_slug (or slice_id_override).
```
with:
```
  - Resolve feature_slug → feature_path and set slice_id := feature_slug
    (or slice_id_override) per contracts/slice_loop.md § Slug rule.
```
2. `skaileup/08_concept-slice/03_scope-feature/SKILL.md` and `skaileup/08_concept-slice/04_design-feature/SKILL.md`: add the REFERENCES line (locate the REFERENCES block with `grep -n "^REFERENCES" <file>`; insert after the `contracts/skill_grammar.md` line).
3. `skaileup/12_impl-slice/04_test/SKILL.md:29`: replace
```
        hint: "Inherited verbatim from upstream phases. Regex ^[a-z][a-z0-9-]{1,47}$."
```
with:
```
        hint: "Inherited verbatim from upstream phases (slug rule: contracts/slice_loop.md)."
```

- [ ] **Step 6: Verify + commit**

```bash
grep -rn '\^\[a-z\]\[a-z0-9-\]{1,47}\$' skaileup --include=SKILL.md
python3 -m pytest skaileup/11_impl-plan skaileup/08_concept-slice -q
python3 skaileup/contracts/scripts/verify_artifacts.py; echo "exit=$?"
python3 skaileup/flows/_meta/verify_flows.py; echo "exit=$?"
git add skaileup/08_concept-slice skaileup/11_impl-plan skaileup/12_impl-slice
git commit -m "refactor(slice-loop): loop skills cite slice_loop.md + grill_bank.md instead of restating

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```
Expected: regex grep hits remain only in frontmatter `hint:` fields of loop entry skills (input validation hints may keep the regex; body restatements gone — acceptable set: `08_concept-slice/01_brainstorm` L40 area, `11_impl-plan/*` frontmatter hints); pytest green; verifiers `exit=0`. Note: the STEP-2 body of `08_concept-slice/01_brainstorm` L129 (`Validate against ^[a-z]...`) was removed in Step 1.3 — confirm no `Validate against ^` remains in any STEP body.

---

### Task 7: Create `skaileup/contracts/evaluator.md` (Cluster 3, part 1)

**Files:**
- Create: `skaileup/contracts/evaluator.md`
- Modify: `skaileup/contracts/CONTRACT.md` (one Contents bullet)
- Test: verifiers exit 0

**Interfaces:**
- Consumes: nothing.
- Produces: sections cited by Task 8: `§ Stance`, `§ Laws`, `§ Scoring`, `§ Verdict grammar`, `§ Flag shape`, `§ Report format`.

- [ ] **Step 1: Write the contract**

Create `skaileup/contracts/evaluator.md` with exactly:

````markdown
# Evaluator Contract

Shared stance and mechanics for every evaluator skill (`ops-eval-concept`,
`ops-eval-feature`, `ops-eval-product`, `impl-quality-eval-code`,
`impl-quality-audit`). Evaluator SKILL.md files own ONLY their dimensions,
deduction tables, weights, and scope-specific process — they cite this file
for everything below.

## Stance

You are an independent evaluator. You were NOT present when the artifact
under evaluation was produced and have never seen the producing
conversation or code session. You only see the artifacts (or the running
app). Approach adversarially: assume defects exist and make the artifact
prove otherwise. Never infer intent — if something is not explicitly
stated, it is missing.

## Laws

MUST  gather ALL evidence silently before scoring — read every input (or
      exercise every flow) first, produce no output during evidence gathering
MUST  quote the exact problematic text (or exact reproduction) in every flag
MUST  provide a specific, actionable resolution for every flag
MUST  write the result file (YAML) BEFORE reporting to the user
NEVER run from the same agent/session that produced the artifact under evaluation
NEVER emit a passing verdict while any blocking flag exists

## Scoring

Each dimension starts at 100; apply the skill's deduction table literally
(every deduction listed, no judgment discounts).
`overall_score` = weighted sum of dimension scores; weights are defined per
skill and must sum to 1.0.

## Verdict grammar

Three tiers, mapped per skill:

| Tier | Canonical names | Meaning |
|---|---|---|
| top | `pass` / `approved` | every dimension ≥ its pass threshold AND zero blocking flags |
| middle | `needs_resolution` / `warn` | any dimension in the warning band OR blocking flags present |
| bottom | `fail` | any dimension below the failure floor OR any critical finding |

## Flag shape

```yaml
- type: <machine-readable kind>
  severity: blocking|warning
  location: <exact path>
  description: <quote the problematic text>
  resolution: <specific action to fix>
```

## Report format

First line: `[<skill-short-name>] <scope, if any> → <verdict> (overall: <n>/100)`
(passing runs may use `✓`, failing runs `✗`, before the bracket).
Second line: dimension scores joined with ` · `.
Then, when not passing:

```
Blocking issues (<n>):
1. [<type>] <location>
   "<quoted text>"
   → <resolution>
```

Close with: `Re-run <skill> after resolving blocking issues.`
````

- [ ] **Step 2: Register in CONTRACT.md**

Append to the Contents list:
```markdown
- **`evaluator.md`** — Shared evaluator skeleton: independent adversarial stance, evidence-before-scoring laws, verdict grammar, flag shape, report-line format.
```

- [ ] **Step 3: Verify + commit**

```bash
python3 skaileup/contracts/scripts/verify_artifacts.py; echo "exit=$?"
python3 skaileup/flows/_meta/verify_flows.py; echo "exit=$?"
git add skaileup/contracts/evaluator.md skaileup/contracts/CONTRACT.md
git commit -m "feat(contracts): add evaluator.md — shared evaluator stance, laws, verdict grammar

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: Slim the four evaluator skills (Cluster 3, part 2)

**Files:**
- Modify: `skaileup/14_ops/05_eval-concept/SKILL.md` (L73-100)
- Modify: `skaileup/14_ops/06_eval-feature/SKILL.md` (stance block ~L68-73, laws ~L84-91)
- Modify: `skaileup/14_ops/07_eval-product/SKILL.md` (stance block ~L64-69, corresponding laws)
- Modify: `skaileup/13_impl-quality/02_eval-code/SKILL.md` (L73-78 laws subset, STEP 4 L107-118)
- Test: verifiers + grep

**Interfaces:**
- Consumes: `contracts/evaluator.md` sections (Task 7); `skaileup/13_impl-quality/03_audit/references/analysis_checklists.md` (existing, sections `§ Logic & Runtime`, `§ UI/UX & Accessibility`, `§ Security & Data Integrity`).
- Produces: nothing for later tasks.

Each skill keeps: its dimensions + deduction tables, its weights, its verdict thresholds, its scope-specific MUST/NEVER (e.g. eval-feature's "MUST actually interact with the running app"), its result-file path. Each skill loses: the generic stance paragraph and the six generic laws.

- [ ] **Step 1: eval-concept**

In `skaileup/14_ops/05_eval-concept/SKILL.md`, replace lines 73-78:
```
You are an independent evaluator. You were NOT present during conceptualization.
You only see the artifacts. Determine whether `_concept/` is complete and clear
enough for an implementation team to build from without ambiguity.

Approach adversarially: assume gaps exist and prove completeness.
Never infer intent. If something is not explicitly stated, it is missing.
```
with:
```
Stance + laws: contracts/evaluator.md (§ Stance, § Laws). Job here: determine
whether `_concept/` is complete and clear enough for an implementation team
to build from without ambiguity.
```
Then replace the MUST/NEVER block (L93-100):
```
MUST read all artifacts silently before scoring
MUST quote the exact problematic text in every flag description
MUST provide a specific actionable resolution for every flag
MUST write eval-concept.yaml before reporting to user
MUST apply all scoring deductions listed in each dimension
NEVER infer intent — unstated means missing
NEVER approve (verdict: pass) with any blocking flags
NEVER run from the same agent that ran the conceptualization pipeline
```
with:
```
Generic evaluator laws: contracts/evaluator.md § Laws (result file:
_concept/eval-concept.yaml).
MUST apply all scoring deductions listed in each dimension
```
Also: STEP 2's flag YAML block (L157-163) duplicates `evaluator.md § Flag shape` — replace the fenced YAML with `Flag shape: contracts/evaluator.md § Flag shape.` Keep STEP 3 (weights `0.4/0.35/0.25`), STEP 4 (thresholds 80/60), and the STEP 6 report skeleton (it instantiates § Report format — keep, it carries skill-specific dimension names). Add to the top of the body (after the `# Eval Concept …` heading's `## Overview`): a REFERENCES-style line is not present in this skill's DSL — instead ensure the Overview cites the contract as shown above.

- [ ] **Step 2: eval-feature**

In `skaileup/14_ops/06_eval-feature/SKILL.md`, replace the stance paragraph:
```
You are an independent evaluator. You receive a feature group name and a running app URL.
Determine whether the implementation matches what the concept specified.

You are adversarial: find failures, not passing tests.
You were NOT present during implementation. You have never seen the code.
You only see the spec and the running app.
```
with:
```
Stance + laws: contracts/evaluator.md (§ Stance, § Laws; result file:
_implementation/eval-feature/{group}.yaml). You receive a feature group name
and a running app URL. Job here: does the implementation match what the
concept specified?
```
Then in its MUST/NEVER block, DELETE only these generic lines (keep every app-interaction-specific line):
```
MUST provide specific revision_instructions if verdict is not approved
MUST write the JSON file before reporting
NEVER run from the same agent that implemented the feature
```
and insert in their place:
```
Generic evaluator laws: contracts/evaluator.md § Laws (resolution field here
is named revision_instructions).
```
Keep: `MUST actually interact with the running app…`, `MUST test every acceptance criterion…`, `MUST check regressions…`, `NEVER mark a criterion as pass without verifying it in the browser`, `NEVER approve if journey is not completable end-to-end`.

- [ ] **Step 3: eval-product**

In `skaileup/14_ops/07_eval-product/SKILL.md`, replace the stance paragraph:
```
You are a product evaluator and design critic. All individual features have been approved.
Evaluate the product as a whole: does it achieve the goals in the brief, do the journeys
work together as a coherent experience, and is the design actually good?

You are NOT re-checking individual acceptance criteria. You are checking what feature
testing cannot reveal: whether the sum of parts makes a coherent product.
```
with:
```
Stance + laws: contracts/evaluator.md (§ Stance, § Laws; result file per this
skill's WRITES). All individual features are approved. Job here: the whole —
brief goals achieved, journeys coherent together, design actually good. NOT
re-checking individual acceptance criteria — checking what feature testing
cannot reveal.
```
Then locate its MUST/NEVER block (`grep -n "^MUST\|^NEVER" skaileup/14_ops/07_eval-product/SKILL.md`) and apply the same split as Step 2: delete lines that are verbatim instances of `evaluator.md § Laws` (silent-read-all, quote-exact, specific-resolution, write-before-report, never-same-agent, never-pass-with-blocking), insert `Generic evaluator laws: contracts/evaluator.md § Laws.`, keep product-specific lines untouched.

- [ ] **Step 4: eval-code — cite audit checklists instead of re-listing auditors**

In `skaileup/13_impl-quality/02_eval-code/SKILL.md`, replace STEP 4 (L107-118):
```
STEP 4: Dispatch three parallel sub-agents (scope=full only).

Sub-agent A — Logic Auditor:
Read all source files. Look for: - Null/undefined dereference without guards - Off-by-one errors in loops and array access - async/await misuse (missing await, swallowed rejections) - Missing error handling at system boundaries (API calls, file I/O, DB) - Data loss paths (update without existence check) - Race conditions in concurrent operations

Sub-agent B — Security Auditor:
Read all source files and dependencies. Look for: - SQL/NoSQL injection vectors - XSS vectors (unsanitized user input in HTML/DOM) - Auth bypass paths (missing auth middleware, broken RBAC) - Insecure direct object references (no ownership check) - Sensitive data in logs, responses, or localStorage - CSRF on state-changing endpoints
Run: `bun audit` or `npm audit` or `pip-audit`

Sub-agent C — UI/UX Code Auditor:
Read frontend source files. Look for: - Interactive elements without accessible labels - Custom interactive elements missing keyboard handlers - Loading states that block UI with no feedback - Error states with no user recovery path - Unguarded form submissions (double-submit possible) - Hardcoded colors/sizes overriding design tokens

All findings use severity: critical | high | medium | low
```
with:
```
STEP 4: Dispatch three parallel sub-agents (scope=full only).

Same auditor trio as impl-quality-audit — checklists owned there:

- Sub-agent A — Logic Auditor: 13_impl-quality/03_audit/references/analysis_checklists.md § Logic & Runtime
- Sub-agent B — Security Auditor: … § Security & Data Integrity. Also run `bun audit` or `npm audit` or `pip-audit`.
- Sub-agent C — UI/UX Code Auditor: … § UI/UX & Accessibility

All findings use severity: critical | high | medium | low

Stance + generic laws for each sub-agent: contracts/evaluator.md (§ Stance, § Laws).
```
Also in its MUST block, keep all six existing lines (they are build-pipeline-specific, none duplicate the contract) and add nothing else.

- [ ] **Step 5: Verify + commit**

```bash
grep -rn "NOT present during" skaileup/14_ops skaileup/13_impl-quality --include=SKILL.md; echo "exit=$?"
wc -l skaileup/14_ops/05_eval-concept/SKILL.md skaileup/14_ops/06_eval-feature/SKILL.md skaileup/14_ops/07_eval-product/SKILL.md skaileup/13_impl-quality/02_eval-code/SKILL.md
python3 skaileup/contracts/scripts/verify_artifacts.py; echo "exit=$?"
python3 skaileup/flows/_meta/verify_flows.py; echo "exit=$?"
git add skaileup/14_ops skaileup/13_impl-quality
git commit -m "refactor(evaluators): four eval skills cite contracts/evaluator.md; eval-code reuses audit checklists

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```
Expected: stance grep `exit=1` (ROLE one-liners may still say "was NOT present" — if a ROLE line matches, that's fine, ROLE lines stay; the check targets the Overview paragraphs, adjust grep to `grep -rn "You were NOT present"` → 0 hits); each file shrank; verifiers `exit=0`.

---

### Task 9: `phase_procedures.md` + cite-don't-restate sweep (Clusters 4+5, part 1)

**Files:**
- Create: `skaileup/contracts/phase_procedures.md`
- Modify: `skaileup/contracts/skill_grammar.md` (§ PROCEDURE — add shared-procedure sentence)
- Modify: `skaileup/contracts/acceptance_criteria.md` (add § EARS template)
- Modify: `skaileup/contracts/CONTRACT.md` (one bullet)
- Modify: `skaileup/08_concept-slice/01_brainstorm/SKILL.md` (STEPs 4-6)
- Modify: `skaileup/08_concept-slice/02_align/SKILL.md` (draft/approve/write steps)
- Modify: `skaileup/11_impl-plan/01_brainstorm/SKILL.md` (STEPs 6-8)
- Modify: `skaileup/11_impl-plan/02_align/SKILL.md` (STEPs 14-16, EARS wording)
- Modify: `skaileup/11_impl-plan/03_plan-vertical/SKILL.md` (STEPs 6-9, EARS wording)
- Modify: `skaileup/14_ops/08_review/SKILL.md:175-184` (golden-principles enumeration)
- Test: pytest on 11_impl-plan/08_concept-slice + verifiers

**Interfaces:**
- Consumes: `slice_loop.md § Handoff frontmatter` (Task 5).
- Produces: procedure names `shared:read_predecessor`, `shared:draft_checkpoint_write`, `shared:emit_lifecycle`; contract section `acceptance_criteria.md § EARS template` (cited by Task 6 Step 2.5).

- [ ] **Step 1: Write `skaileup/contracts/phase_procedures.md`**

Exact content:

````markdown
# Phase Procedures

Shared PROCEDUREs for handoff-writing skills. Invoke from a STEP as
`DO shared:<name>` with indented `key: value` parameter lines
(skill_grammar.md § PROCEDURE). A skill using one MUST list this file in
REFERENCES.

PROCEDURE read_predecessor
  in: predecessor_path, predecessor_skill
  - Open <predecessor_path>; if missing, refuse:
    > "[<skill>] required file <predecessor_path> not found.
    >  Run <predecessor_skill> first."   (iron_laws § 7)
  - Parse frontmatter; copy slice_id, feature_title (+ feature_path on the
    impl side) VERBATIM — never re-derive (slice_loop.md § Handoff frontmatter)
  - Cache the body sections the current phase consumes

PROCEDURE draft_checkpoint_write
  in: artifact_path, checkpoint_id
  - Compose the full artifact in memory: frontmatter per slice_loop.md
    § Handoff frontmatter + the skill's pinned body sections
  - Show the complete draft to the user
  - CHECKPOINT <checkpoint_id>
    > "Approve to write to <artifact_path>, or tell me what to change."
    NEVER write before approval.
  - Write <artifact_path>; verify the file exists and its frontmatter parses
  - If the skill directory has a validator.py:
    $ python3 <skill_dir>/validator.py <artifact_path>
    On non-zero exit: report the validator errors and STOP.

PROCEDURE emit_lifecycle
  in: skill_name, kv_pairs
  - EMIT [<skill_name>] completed <kv_pairs>
  - Walk the skill's CHECKLIST; report any unchecked item instead of
    claiming success
````

- [ ] **Step 2: Extend two existing contracts**

1. `skaileup/contracts/skill_grammar.md`: at the end of the `### PROCEDURE <name>` section (after its example code block, before the `---` separator), append:
```markdown
Shared procedures reused across many skills are defined once in
`contracts/phase_procedures.md` and invoked as `DO shared:<name>` with
indented `key: value` parameter lines. A skill using one MUST list
`contracts/phase_procedures.md` in REFERENCES.
```
2. `skaileup/contracts/acceptance_criteria.md`: append at end of file:
```markdown
---

## EARS template

Canonical EARS acceptance-criterion form — cite this section instead of
restating it:

    WHEN <trigger>, THE SYSTEM SHALL <response>

Variants: `WHILE <state>, THE SYSTEM SHALL <response>` (state-driven);
`IF <unwanted condition>, THEN THE SYSTEM SHALL <response>` (unwanted
behaviour). One observable response per line; every criterion independently
verifiable.
```
3. `skaileup/contracts/CONTRACT.md` Contents list, append:
```markdown
- **`phase_procedures.md`** — Shared handoff procedures (`read_predecessor`, `draft_checkpoint_write`, `emit_lifecycle`) invoked via `DO shared:<name>`.
```

- [ ] **Step 3: Apply the write-dance to concept-slice-brainstorm**

In `skaileup/08_concept-slice/01_brainstorm/SKILL.md`, replace STEPs 4-6 (from `STEP 4: Draft handoff in memory` through the `  - Verify file exists and frontmatter parses` line of STEP 6, keeping the EMIT line after it) with:
```
STEP 4: Finalize
  DO shared:draft_checkpoint_write     (contracts/phase_procedures.md)
    artifact_path: _concept/slices/<slice_id>/brainstorm.md
    checkpoint_id: brainstorm_draft
  Frontmatter: concept-side keys (slice_loop.md § Handoff frontmatter),
  phase: brainstorm.
  Body sections (exact headers):
    ## Feature in one sentence
    ## Who uses it
    ## Trigger
    ## Happy path (3-7 bullets)
    ## Clearly out of scope
    ## Open questions for align
```
Add to REFERENCES: `  contracts/phase_procedures.md              — shared handoff procedures (DO shared:*)`. Keep the EMIT and CHECKLIST unchanged (checklist items still name the 6 frontmatter keys — fine, they instantiate the contract).

- [ ] **Step 4: Apply the write-dance to the other four loop skills**

Same pattern; each retains its section-content rules (they are validator-pinned) and loses only the draft/show/checkpoint/write/verify/validator lines:

1. `skaileup/08_concept-slice/02_align/SKILL.md` — merge old STEPs 11-13 (draft/approval/write, renumbered 5-7 by Task 6) into:
```
STEP 5: Finalize
  DO shared:draft_checkpoint_write     (contracts/phase_procedures.md)
    artifact_path: _concept/slices/<slice_id>/align.md
    checkpoint_id: align_draft
  Frontmatter: concept-side keys (slice_loop.md § Handoff frontmatter),
  phase: align; copy slice_id/feature_title from brainstorm.md (or fresh for
  appbuilder-simple).
  Body sections (exact headers, in order):
    ## Feature recap (one sentence)
    ## Acceptance criteria (EARS)
    ## Edge cases
    ## Error states
    ## Permissions / roles
    ## Unstated assumptions exposed
    ## Resolved questions
    ## Open questions blocking scope-feature
  - `## Acceptance criteria (EARS)` MUST contain ≥ 1 line per
    contracts/acceptance_criteria.md § EARS template.
  - `## Permissions / roles` MUST contain a markdown table with at least
    one role row + an actions header row.
```
2. `skaileup/11_impl-plan/01_brainstorm/SKILL.md` — replace STEPs 6-8 with the DO block (`artifact_path: _implementation/slices/<slice_id>/brainstorm.md`, `checkpoint_id: brainstorm_draft`, `phase: brainstorm`, impl-side 7 keys), keeping verbatim the existing body-section list AND its five content rules (`## App-level summary` … `## Recommended mitigations` bullets, old L226-242). The validator line (old STEP 8 `$ python3 impl-plan/brainstorm/validator.py …`) is covered by the procedure — delete it.
3. `skaileup/11_impl-plan/02_align/SKILL.md` — replace STEPs 14-16 (renumbered 6-8 by Task 6) with the DO block (`artifact_path: _implementation/slices/<slice_id>/align.md`, `checkpoint_id: align_draft`, `phase: align`), keeping verbatim the body-section list and all nine content rules (old L280-296), with old L294-296 changed from
```
  - `## Acceptance handoff` is the EARS criteria from feature.md "## Acceptance
    Criteria" copied VERBATIM. At least one line in "WHEN ..., THE SYSTEM SHALL ..."
    form.
```
to
```
  - `## Acceptance handoff` is the EARS criteria from feature.md "## Acceptance
    Criteria" copied VERBATIM (contracts/acceptance_criteria.md § EARS template;
    grill_bank.md § EARS provenance). ≥ 1 EARS line required.
```
4. `skaileup/11_impl-plan/03_plan-vertical/SKILL.md` — replace STEPs 6-9 (draft/approval/write/validate) with the DO block (`artifact_path: _implementation/slices/<slice_id>/plan.md`, `checkpoint_id: plan_draft`, `phase: plan`), keeping verbatim: the body-section list, the six content rules (old L294-307) including the verbatim anti-horizontal nudge + 5 DoD items, and the empty-cell WARNING sentence from old STEP 9 (append it to the DO block as `  - Validator note: empty UI/Logic/Data cells produce a WARNING (stderr), not a failure; surface it to the user.`). Also update the STEP 5 EARS sentence (old L255-257) — keep as-is except append `(format: contracts/acceptance_criteria.md § EARS template)` after `"## Acceptance Criteria" for appbuilder-mvp)`.
5. Add the `contracts/phase_procedures.md` REFERENCES line to all four files.

- [ ] **Step 5: 14_ops/08_review — cite golden_principles instead of re-enumerating**

In `skaileup/14_ops/08_review/SKILL.md`, replace lines 175-184:
```
- For every applicable rule in contracts/golden_principles.md:
  - Entity IDs: `snake_case`
  - Field names: `snake_case`
  - Enum values: `PascalCase`
  - Relation fields: `_id` suffix
  - Feature groups: sequential, no gaps
  - Screen groups mirror feature group numbers
  - Every feature has at least one requirement
  - All paths in frontmatter resolve to existing files
    See references/checks.md for the complete check table
```
with:
```
- For every applicable rule in contracts/golden_principles.md (entity, field,
  enum, and relation naming; group numbering; requirement coverage;
  frontmatter path resolution). Do not re-enumerate the rules here — the
  contract owns them; references/checks.md has the complete check table.
```

- [ ] **Step 6: Verify + commit**

```bash
python3 -m pytest skaileup/11_impl-plan skaileup/08_concept-slice -q
python3 skaileup/contracts/scripts/verify_artifacts.py; echo "exit=$?"
python3 skaileup/flows/_meta/verify_flows.py; echo "exit=$?"
grep -rn "DO shared:" skaileup --include=SKILL.md | wc -l
git add skaileup/contracts skaileup/08_concept-slice skaileup/11_impl-plan skaileup/14_ops
git commit -m "feat(contracts): phase_procedures.md + cite-don't-restate sweep (EARS, golden principles, write-dance)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```
Expected: pytest green (validators check output files, not SKILL prose); verifiers `exit=0`; `DO shared:` count = 5.

---

### Task 10: CI guards — restatement detector + line budget (Cluster 5, part 2, TDD)

**Files:**
- Modify: `skaileup/contracts/scripts/verify_artifacts.py` (new functions + two `main()` call lines)
- Create: `skaileup/contracts/tests/test_verify_artifacts.py`
- Modify: `.github/workflows/collection-ci.yml` (artifacts job: add pytest)
- Test: `python3 -m pytest skaileup/contracts/tests/ -q`

**Interfaces:**
- Consumes: existing `verify_artifacts.py` structure — `REPO` constant, `main()` with `errors`/`warns` lists, `skill_files = sorted(SKILLS_ROOT.rglob("SKILL.md"))`.
- Produces: functions `_normalize(text) -> list[str]`, `_ngrams(tokens, n=NGRAM_N) -> set[tuple]`, `check_restatements(skill_files, errors)`, `check_line_budget(skill_files, warns)`; constants `NGRAM_N = 8`, `LINE_BUDGET = 400`, `RESTATE_EXEMPT`.

- [ ] **Step 1: Write the failing tests**

Create `skaileup/contracts/tests/test_verify_artifacts.py`:

```python
"""Tests for the dedup guards in contracts/scripts/verify_artifacts.py."""
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_artifacts.py"
spec = importlib.util.spec_from_file_location("verify_artifacts", SCRIPT)
va = importlib.util.module_from_spec(spec)
spec.loader.exec_module(va)


def test_normalize_lowercases_and_strips_punctuation():
    assert va._normalize("MUST sort  all manifest arrays, lexicographically!") == [
        "must", "sort", "all", "manifest", "arrays", "lexicographically"]


def test_ngrams_sliding_window():
    toks = list("abcdefghij")  # 10 tokens → 3 8-grams
    grams = va._ngrams(toks, 8)
    assert ("a", "b", "c", "d", "e", "f", "g", "h") in grams
    assert len(grams) == 3


def _fake_contracts(tmp_path):
    contracts = tmp_path / "contracts"
    contracts.mkdir()
    (contracts / "demo_contract.md").write_text(
        "Renderers must sort all manifest arrays lexicographically "
        "for deterministic diffs across regeneration runs.\n")
    return contracts


def test_restatement_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr(va, "CONTRACTS_DIR", _fake_contracts(tmp_path))
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        "MUST sort all manifest arrays lexicographically for deterministic "
        "diffs across regeneration runs\n")
    errors = []
    va.check_restatements([skill], errors)
    assert len(errors) == 1
    assert "restate" in errors[0] and "SKILL.md:1" in errors[0]


def test_short_citation_not_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr(va, "CONTRACTS_DIR", _fake_contracts(tmp_path))
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        "MUST sort manifest arrays (contracts/walkthrough_renderer.md "
        "§ Shared MUST / NEVER)\n")
    errors = []
    va.check_restatements([skill], errors)
    assert errors == []


def test_code_blocks_in_contracts_excluded(tmp_path, monkeypatch):
    contracts = tmp_path / "contracts"
    contracts.mkdir()
    (contracts / "demo_contract.md").write_text(
        "```\nvalidator pins the exact anti horizontal nudge template "
        "string match here always\n```\n")
    monkeypatch.setattr(va, "CONTRACTS_DIR", contracts)
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        "MUST embed the validator pins the exact anti horizontal nudge "
        "template string match here always\n")
    errors = []
    va.check_restatements([skill], errors)
    assert errors == []  # fenced contract text is exempt (pinned templates)


def test_line_budget_warns_over_400(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text("x\n" * 401)
    warns = []
    va.check_line_budget([skill], warns)
    assert len(warns) == 1 and "401 lines > 400" in warns[0]


def test_line_budget_silent_at_400(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text("x\n" * 400)
    warns = []
    va.check_line_budget([skill], warns)
    assert warns == []
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
python3 -m pytest skaileup/contracts/tests/ -q
```
Expected: collection error / failures with `AttributeError: module 'verify_artifacts' has no attribute '_normalize'`.

- [ ] **Step 3: Implement the guards**

In `skaileup/contracts/scripts/verify_artifacts.py`, add after the `writes_paths` function (before `def main`):

```python
# ── Dedup guards ─────────────────────────────────────────────────────────
import re as _re

CONTRACTS_DIR = REPO / "skaileup" / "contracts"
NGRAM_N = 8
LINE_BUDGET = 400
# Contract files whose text is MEANT to appear in skills (templates, grammar
# examples, fixtures) — exempt from the restatement index.
RESTATE_EXEMPT = {"skill_template.md", "skill_grammar.md", "skill_testing.md"}


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return p.name


def _normalize(text: str) -> list[str]:
    """Lowercase; keep [a-z0-9] token runs only."""
    return _re.findall(r"[a-z0-9]+", text.lower())


def _ngrams(tokens: list[str], n: int = NGRAM_N) -> set[tuple[str, ...]]:
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def _strip_code_blocks(text: str) -> str:
    """Drop fenced ``` blocks — pinned templates are legitimately embedded."""
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            out.append(line)
    return "\n".join(out)


def _contract_ngram_index() -> set[tuple[str, ...]]:
    grams: set[tuple[str, ...]] = set()
    for md in sorted(CONTRACTS_DIR.glob("*.md")):
        if md.name in RESTATE_EXEMPT:
            continue
        grams |= _ngrams(_normalize(_strip_code_blocks(md.read_text())))
    return grams


def check_restatements(skill_files, errors) -> None:
    """ERROR on any MUST/NEVER line that shares an 8-gram with a contract."""
    grams = _contract_ngram_index()
    for sf in skill_files:
        for lineno, line in enumerate(sf.read_text().splitlines(), 1):
            if not line.startswith(("MUST", "NEVER")):
                continue
            if any(g in grams for g in _ngrams(_normalize(line))):
                errors.append(
                    f"[restate] {_rel(sf)}:{lineno}: MUST/NEVER line duplicates "
                    f"contract text (≥{NGRAM_N}-gram match) — cite the contract "
                    f"section instead")


def check_line_budget(skill_files, warns) -> None:
    for sf in skill_files:
        n = len(sf.read_text().splitlines())
        if n > LINE_BUDGET:
            warns.append(f"[budget] {_rel(sf)}: {n} lines > {LINE_BUDGET} — split or compress")
```

Then in `main()`, immediately after the `known_names = set(skills)` line, add:

```python
    # dedup guards
    check_restatements(skill_files, errors)
    check_line_budget(skill_files, warns)
```

- [ ] **Step 4: Run tests — expect PASS; then run the real repo scan**

```bash
python3 -m pytest skaileup/contracts/tests/ -q
python3 skaileup/contracts/scripts/verify_artifacts.py; echo "exit=$?"
```
Expected: 7 tests pass. Repo scan: `exit=0`. If any `[restate]` ERROR fires on a skill line, fix that line by shortening it to the pattern `<MUST|NEVER>  <verb phrase, ≤ 10 words> (<contract file> § <section>)` — e.g. a leftover `MUST  sort all manifest arrays lexicographically (screens by screen_path, journeys by journey_id, features by feature_path) for deterministic diffs` becomes `MUST  sort manifest arrays (contracts/walkthrough_renderer.md § Shared MUST / NEVER)`. Re-run until `exit=0`. `[budget]` WARNs are expected (the large skills are compressed in Task 11) and do not fail the build.

- [ ] **Step 5: Wire pytest into CI**

In `.github/workflows/collection-ci.yml`, replace the artifacts job's last two steps:
```yaml
      - name: Install PyYAML
        run: pip install pyyaml
      - name: Verify artifact registry vs skills
        run: python3 skaileup/contracts/scripts/verify_artifacts.py
```
with:
```yaml
      - name: Install deps
        run: pip install pyyaml pytest
      - name: Verify artifact registry vs skills
        run: python3 skaileup/contracts/scripts/verify_artifacts.py
      - name: Run contracts-script tests
        run: python3 -m pytest skaileup/contracts/tests/ -q
```

- [ ] **Step 6: Full verification + commit**

```bash
python3 -m pytest skaileup/contracts/tests/ skaileup/flows/_meta/test_verify.py -q
python3 skaileup/contracts/scripts/verify_artifacts.py; echo "exit=$?"
python3 skaileup/flows/_meta/verify_flows.py; echo "exit=$?"
git add skaileup/contracts/scripts/verify_artifacts.py skaileup/contracts/tests/test_verify_artifacts.py .github/workflows/collection-ci.yml
git commit -m "feat(ci): restatement n-gram detector (ERROR) + 400-line budget (WARN) in verify_artifacts

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 11: Caveman compression pass (F)

Rewrite skill **prose** to terse imperative style in the 10 largest post-dedup skills. Rules are verbatim law for this task:

- **R1** Drop articles, filler, and hedging in STEP prose ("the", "a", "please", "you should", "in order to", "note that").
- **R2** Sentence pattern: `[thing] [action] [reason]` — e.g. "Screens render in lexicographic order — deterministic diffs."
- **R3** Tables over prose for rubrics, enumerations, option sets.
- **R4** NEVER alter: MUST/NEVER lines, code blocks, error strings, refuse conditions, and ordered sequences where dropped conjunctions would create ambiguity.
- **R5** Keep REFERENCES blocks and YAML frontmatter byte-identical.
- **R6** Target ≤400 lines per skill. R4-protected content is never deleted to hit budget; a file still >400 after full prose compression is acceptable (the budget check is a WARN).

**Files:**
- Modify: `skaileup/14_ops/11_reverse-engineer/SKILL.md` (565 → target ≤400)
- Modify: `skaileup/12_impl-slice/02_implement/SKILL.md` (386 → ≤330)
- Modify: `skaileup/08_concept-slice/04_design-feature/SKILL.md` (351 → ≤300)
- Modify: `skaileup/11_impl-plan/03_plan-vertical/SKILL.md` (post-Task-9 ~300 → ≤270)
- Modify: `skaileup/11_impl-plan/02_align/SKILL.md` (post-Task-9 ~250 → ≤220)
- Modify: `skaileup/14_ops/08_review/SKILL.md` (313 → ≤270)
- Modify: `skaileup/05_mockup-walkthrough/01_b_static-html/SKILL.md` (post-Task-4 ~330 → ≤300)
- Modify: `skaileup/05_mockup-walkthrough/01_c_astro/SKILL.md` (post-Task-4 ~600 → ≤450, config code blocks dominate)
- Modify: `skaileup/05_mockup-walkthrough/01_d_lit/SKILL.md` (post-Task-4 ~700 → ≤500, component code blocks dominate)
- Modify: `skaileup/05_mockup-walkthrough/01_e_framework/SKILL.md` (post-Task-4 ~560 → ≤450)
- Test: per-file `git diff` MUST/NEVER-invariance check + verifiers + pytest

**Interfaces:**
- Consumes: post-dedup file states from Tasks 4, 6, 9.
- Produces: final compressed collection; no downstream consumers.

Worked example — the required style, from `skaileup/14_ops/11_reverse-engineer/SKILL.md` Overview (real current text):

Before:
```markdown
The **reverse-engineer** skill analyzes an existing project repository and
produces a complete `_concept/` directory from it. It is an alternative entry
point to the pipeline: instead of building a concept from user dialog, it reads
source code, configuration, schemas, and documentation to infer what was built,
why, and how.
```
After (R1 + R2 applied; 5 lines → 3):
```markdown
Analyzes existing repo → produces complete `_concept/`. Alternative pipeline
entry: reads source, config, schemas, docs — infers what was built, why, how.
No user dialog.
```

- [ ] **Step 1: Compress `skaileup/14_ops/11_reverse-engineer/SKILL.md`**

Apply R1-R6 to every Overview/When-to-Use/STEP prose paragraph (start with the worked example above, verbatim). Convert the confidence-level bullet list (L95-99) to a table per R3:
```markdown
| Tag | Meaning | Confidence |
|---|---|---|
| `extracted` | read directly from code or config | high |
| `inferred` | reasoned from context or structure | medium |
| `needs_review` | could not be determined reliably | must validate |
```
Then verify invariants:
```bash
git diff -U0 skaileup/14_ops/11_reverse-engineer/SKILL.md | grep -E '^[+-](MUST|NEVER)'; echo "exit=$?"
git diff skaileup/14_ops/11_reverse-engineer/SKILL.md -- | grep -c '^[+-]```'
wc -l skaileup/14_ops/11_reverse-engineer/SKILL.md
```
Expected: MUST/NEVER diff `exit=1` (empty — R4); code-fence diff count 0 unless a fence line moved with unchanged content (inspect manually if >0); ≤400 lines.

- [ ] **Step 2: Compress the five mid-size skills**

For each of `skaileup/12_impl-slice/02_implement/SKILL.md`, `skaileup/08_concept-slice/04_design-feature/SKILL.md`, `skaileup/11_impl-plan/03_plan-vertical/SKILL.md`, `skaileup/11_impl-plan/02_align/SKILL.md`, `skaileup/14_ops/08_review/SKILL.md`: apply R1-R6 to Overview / When-to-Use / When-NOT-to-Use / STEP prose. Do NOT touch (R4): the anti-horizontal nudge block (validator pins exact string), refuse messages in `> "..."` quotes, body-section header lists, DoD items, CHECKLIST lines. After each file run the same three verification commands as Step 1 (MUST/NEVER diff empty; line count at or under its target above).

- [ ] **Step 3: Compress the four walkthrough scaffolds**

Same procedure for `01_b_static-html`, `01_c_astro`, `01_d_lit`, `01_e_framework` under `skaileup/05_mockup-walkthrough/`. R4 protects all fenced config/template/code blocks (astro configs, lit components, next.js setup) and every warning-kind string. Compress only the connecting prose (rendering-decision rationale paragraphs, step intros, edge-case narration already tabled in the contract). Verify per file as in Step 1 with the per-file targets above.

- [ ] **Step 4: Full verification**

```bash
python3 -m pytest skaileup/contracts/tests/ skaileup/flows/_meta/test_verify.py skaileup/11_impl-plan skaileup/08_concept-slice -q
python3 skaileup/contracts/scripts/verify_artifacts.py; echo "exit=$?"
python3 skaileup/flows/_meta/verify_flows.py; echo "exit=$?"
git diff --stat | tail -1
```
Expected: all pytest green; verifiers `exit=0`; the `[budget]` WARN list is shorter than before Task 11 (astro/lit may remain — acceptable per R6).

- [ ] **Step 5: Commit**

```bash
git add skaileup/14_ops skaileup/12_impl-slice skaileup/08_concept-slice skaileup/11_impl-plan skaileup/05_mockup-walkthrough
git commit -m "refactor(skills): caveman compression pass on 10 largest skills (R1-R6; MUST/NEVER + code blocks untouched)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 12: Final sweep and totals

**Files:**
- Modify: none (verification only; fix regressions if any check fails)
- Test: everything

**Interfaces:**
- Consumes: all prior tasks.
- Produces: final state; totals reported to the user.

- [ ] **Step 1: Full verification battery**

```bash
python3 skaileup/contracts/scripts/verify_artifacts.py; echo "exit=$?"
python3 skaileup/flows/_meta/verify_flows.py; echo "exit=$?"
python3 -m pytest skaileup/contracts/tests/ skaileup/flows/_meta/test_verify.py -q
python3 -m pytest skaileup/11_impl-plan skaileup/08_concept-slice -q
python3 docs/scripts/audit.py; echo "exit=$?"
```
Expected: every `exit=0`, all tests pass (the frontmatter audit runs in CI's `audit` job — must stay green since we never touched `name:`/`metadata`; if it flags anything, only prose moved — investigate before committing anything further).

- [ ] **Step 2: Confirm the bugs are dead and dedup held**

```bash
grep -rn "product-spec/features" skaileup/ | grep -v devlog; echo "exit=$?"
grep -rn "deletes the entire\|directory is scratch" skaileup --include=SKILL.md; echo "exit=$?"
grep -rln "kind → DOM" skaileup --include=SKILL.md; echo "exit=$?"
find skaileup -name SKILL.md | xargs wc -l | tail -1
```
Expected: first three greps `exit=1` (no hits); total line count ≤ ~21,000 (from 22,727 — ≥1,500 lines removed).

- [ ] **Step 3: Report totals**

Report to the user: total SKILL.md lines before (22,727) and after, the 4 new + 3 extended contract files, the 2 bug fixes, and the 2 new CI guards. No commit (nothing changed in this task unless a regression was fixed; if one was, commit it with a `fix:` message ending in the standard trailer).

---

## Self-review (performed while drafting — results)

- **Spec coverage:** A1 → Task 1; A2 → Task 2 (+ walkthrough remnants in Task 4 Step 9); B → Tasks 3-4; C → Tasks 5-6; D → Tasks 7-8; E → Tasks 9-10 (procedures, EARS/golden/iron-law citations, restatement detector, line budget, CI wiring); F → Task 11 (rules verbatim, 10 files bounded, worked example from a real file). Verification commands after every task per spec.
- **Placeholder scan:** no TBD/TODO; every replacement block shows actual text; lit/framework edits that could not quote unread interiors are specified as heading-delimited deletions with the exact insertion text and grep-locate commands — no "similar to" without repeated content (the pointer block and MUST/NEVER-split line lists are restated or explicitly enumerated at each use).
- **Name consistency:** contract filenames (`walkthrough_renderer.md`, `slice_loop.md`, `grill_bank.md`, `evaluator.md`, `phase_procedures.md`) and section anchors are identical between the producing task's Interfaces block and every consuming step; guard function names (`check_restatements`, `check_line_budget`, `_normalize`, `_ngrams`, `NGRAM_N`, `LINE_BUDGET`) match between Task 10's tests and implementation; the Task 2 validator pin string matches SKILL.md L304 wording exactly.
- **Ordering note:** Task 6 Step 2.5 cites `acceptance_criteria.md § EARS template`, created in Task 9 Step 2 — flagged inline; executing in plan order leaves a dangling citation for two tasks, which is harmless (markdown reference), or execute Task 9 Step 2 early.
