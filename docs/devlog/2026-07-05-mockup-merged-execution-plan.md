# Mockup Live-Interconnect + Content-Fidelity — Merged Execution Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** planned · this is the reconciled execution order for the two sibling design docs — `docs/devlog/2026-07-05-mockup-live-interconnect-plan.md` (navigation/`target:` fields, 13 tasks) and `docs/devlog/2026-07-05-mockup-content-fidelity-plan.md` (content synthesis/`table`/`tabs`, 11 tasks). Those two docs remain the source of truth for **evidence and rationale** (read them for "why"); this doc is the source of truth for **what to build and in what order** (read this for "what"). Executing this plan supersedes running the two source plans back-to-back.

**Goal:** Deliver both fixes — live navigation and real UI content — in one coherent set of contract/renderer/authoring changes, landing the contract version bumps once (straight to `elements_block.md` v0.3 and `walkthrough_renderer.md` schema_version `1.2`) instead of twice, and running one combined migration/backfill skill instead of two.

**Why merge:** The two source plans were written to layer on each other (their own text says so: content-fidelity's Global Constraints say "if both plans are executed in one pass, land the bumps as a single v0.3/1.2 change"; its Task 10 explicitly supersedes the live-interconnect plan's Task 11). Running them back-to-back would mean two commits bumping the same header field, two migration skills patching the same 43-screen frontmatter block, and two feedback-cluster coordination passes over the same annotate fixtures. Merging removes that duplication without changing scope.

**Architecture:** Same contract-first flow as both source plans: (1) `elements_block.md` gains ALL new fields in one v0.3 bump — `target`, `items` (three flavors: nav/tabs/list), `table` kind with `columns`/`sample_rows`/`row_target`, `input` gains `options`; (2) `walkthrough_renderer.md` gains ALL new behavior in one 1.2 bump — kind→DOM mapping rewrite (link/button/nav/table/tabs/list/input), target resolution, generated app-shell nav, auto-slug fallback narrowing (heading exclusion + quoted-label extraction), collapsed spec-reference panel, narrowed journey-nav rule; (3) renderers implement both concerns together per variant (static-html first, then astro/lit/framework); (4) `experience-screens` authors the full block (targets + content) going forward; (5) one combined migration skill backfills the 43 already-written CLINICO-shaped screens; (6) feedback-cluster coordination and docs land last.

**Tech Stack:** Markdown contracts + skill DSL (`skaileup/contracts/skill_grammar.md`), YAML frontmatter, Python 3.12 validators (stdlib + PyYAML), Astro/Lit/framework scaffold templates embedded in SKILL.md bodies.

## Global Constraints

- **Contract-first, additive-only.** `elements_block.md` v0.1 → **v0.3** directly (skip a separate v0.2 commit); `walkthrough_renderer.md` schema_version `"1.0"` → **`"1.2"`** directly (skip a separate 1.1 commit). No renames, no removals — every field from both source plans is additive.
- **`items:` is one field, kind-dependent entry shape.** `kind: nav` → `{id?, label, target, icon?}`; `kind: tabs` → `{id?, label, target?}`; `kind: list` → `{label, target?}` or bare strings. One resolution rule, one auto-slug-id rule, no parallel field names.
- **Soft-fail rendering, hard-require authoring.** Renderers never hard-fail on missing/partial `elements:` (auto-slug fallback stays as a genuine — now narrower — degradation path). `experience-screens` gets a hard MUST at depth `medium`/`max` (exempt at `light`/`none`, matching the existing `### Wireframe` MUST precedent).
- **Sample data is authored fixture, never renderer-invented.** `sample_rows`/`items` content comes from `seed.json` scenarios or the screen's own wireframe examples; a `table` with `columns` but no `sample_rows` renders the header plus one skeleton row.
- **`target` identity form = `screen_id`** (path stem under `experience/screens/`, e.g. `11_intake/case_admission_form`), matching `data-spec-screen`, rendered filenames, `screens[].screen_id`. Optional `#<element-id>` fragment.
- **Resolution rule:** from `screen/<gA>/<nA>.html`, target `gB/nB` renders `href="../<gB>/<nB>.html"` (+ `#<fragment>` when present); from `index.html`, `href="screen/<gB>/<nB>.html"`. Resolvable iff `experience/screens/<target-sans-fragment>.md` exists in the rendered screen set. Unresolved → `href="#"` + `warnings[]` entry `kind: "unresolved_target"`. A `button` with no `target:` is legal and stays inert — not everything navigates.
- **Auto-slug fallback, narrowed not removed:** exclude the canonical spec-template headings (`Purpose, Route, What the User Sees, Wireframe, Information Displayed, Actions, Situations, UI Elements, Template Data`, shell's `Navigation, Layout Areas, Responsive Behaviour`, any `# Screen: *`/`# Shell: *` H1) from heading-based widget discovery — these become the collapsed spec panel's `<h2>` skeleton, never `el-region` widgets. `## Actions` bullets, when still the only source (rare once Task 11 lands), extract the quoted label token (`"…"`/`„…“`) instead of the whole sentence; full sentence goes to `describes:`.
- **Journey-nav rule narrowed, not removed:** NEVER inject journey-*step* (Next/Prev, journey-ordering) navigation into `screen/**/*.html` — that stays exclusive to `journey/<id>.html`. Screen-intrinsic navigation (resolved `target:` hrefs, the generated app-shell nav) is REQUIRED and is NOT journey-nav.
- **Spec content is reference, not primary content:** the full screen spec body (all canonical sections + wireframe fence) renders inside a collapsed `<details class="spec-panel"><summary>View spec</summary>…</details>` after the synthesized UI. When a screen has zero explicit elements, the panel renders `open` and the renderer emits `warnings[]` `kind: "no_explicit_elements"`.
- **No new `data-spec-*` attributes** beyond the one pinned exception (`nav`/`tabs`/`list` `items[]` entries get their own `data-spec-element`, matching the existing per-item annotation need). The feedback cluster keeps resolving clicks identically otherwise.
- **Renderers stay read-only on sources.** All backfill goes through the migration skill (Task 12) with human review via existing `mockup-feedback-patch`/`apply` machinery — no new mutation path.
- **static-html is the reference implementation** — Tasks 4–5 land before astro/lit/framework (Tasks 6–8); when behavior is ambiguous, static-html's output is the tie-breaker (existing contract rule).
- **Green after every task:** `bash skaileup/05_mockup-walkthrough/01_b_static-html/tests/run_validator.sh` passes wherever it applies; `python3 skaileup/flows/_meta/verify_flows.py` and `python3 -m pytest skaileup/flows/_meta/test_verify.py` stay green throughout (nothing in this plan touches flows, so any failure there is a regression); `git diff --stat` limited to each task's Files list.
- **Commits:** conventional-commit style, each ending with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

---

## Reference: the complete new field set (decided, merged from both source plans)

**In-screen action — one element, one destination** (`kind: link | button | list | image | custom`):

```yaml
elements:
  - id: open-admission-form
    kind: button
    label: "Aufnehmen"                          # on-screen UI copy — never the action sentence
    states: [default]
    target: 11_intake/case_admission_form        # screen_id, optional "#<element-id>" fragment
    describes: "Click \"Aufnehmen\" on an Anmeldung row → opens the admission form"
```

**App-shell / persistent nav** (`kind: nav`, N destinations):

```yaml
elements:
  - id: sidebar-nav
    kind: nav
    label: "Hauptnavigation"
    states: [default]
    items:
      - id: nav-tasks
        label: "Aufgaben"
        target: 20_tasks/task_list
        icon: "✓"
```

**Tab bar** (`kind: tabs`):

```yaml
elements:
  - id: case-tabs
    kind: tabs
    label: "Fälle & Aufnahmen Tabs"
    states: [default]
    items:
      - label: "Aufzunehmen"     # first item renders active; target optional (tabs may be in-page)
      - label: "Fälle"
```

**List with real items** (`kind: list` gains `items`):

```yaml
elements:
  - id: pending-registrations
    kind: list
    label: "Aufzunehmende Anmeldungen"
    states: [default, empty]
    data_entity: registrations
    items:
      - label: "Lena M. · geb. 14.03.2014 · Kindergruppe"
        target: 11_intake/case_admission_form
      - "Tom B. · geb. 02.09.2010 · Jugendgruppe"
```

**Table content** (new `kind: table`):

```yaml
elements:
  - id: faelle-table
    kind: table
    label: "Fälle"
    states: [default, loading, empty]
    data_entity: cases
    columns: ["Patient", "Falltyp", "Bereich", "Status", "Aufgenommen"]
    sample_rows:                        # authored fixtures — renderers never invent
      - ["Lena M.", "Teilstationär", "Kindergruppe", "Aktiv", "15.06.2026"]
      - ["Tom B.", "Ambulant", "Jugendgruppe", "Aktiv", "03.06.2026"]
    row_target: 11_intake/case_detail   # optional — every row links here
```

**Select input** (`kind: input` gains `options`):

```yaml
elements:
  - id: filter-bereich
    kind: input
    label: "Bereich"
    states: [default]
    options: ["Alle", "Kindergruppe", "Jugendgruppe"]   # presence ⇒ render <select>
```

---

### Task 1: `elements_block.md` → v0.3 (one bump, all new fields)

**Files:**
- Modify: `skaileup/contracts/elements_block.md`

**Interfaces:**
- Produces: schema fields `target` (kinds `link|button|list|image|custom`), `items` (kinds `nav|tabs|list`, entry shape per kind), `kind` enum gains `table`, `tabs`; `columns`/`sample_rows`/`row_target` (kind `table`), `options` (kind `input`)

- [ ] **Step 1:** Bump the status header directly to `v0.3 — adds navigation targets + content-fidelity shapes (2026-07-05 merged mockup plan)`.
- [ ] **Step 2:** Extend the `kind` enum with `table` and `tabs` (note: these ARE the "propose an extension over reaching for custom" case the v0.1 note anticipated).
- [ ] **Step 3:** Extend § Schema + § Field reference with every field from the Reference block above: `target` (string, no — `screen_id` + optional `#fragment`; MUST resolve or renderer records `unresolved_target`; valid only on `link|button|list|image|custom`); `items` (list, no — valid on `nav|tabs|list` only, entry shape per kind as specified); `columns` (list of strings, required iff `kind: table`); `sample_rows` (list of lists of strings, optional, `table` only, `len(row) == len(columns)`, authored not invented); `row_target` (string, optional, `table` only, same grammar as `target`); `options` (list of strings, optional, `kind: input` only — presence ⇒ renders as `<select>`).
- [ ] **Step 4:** Add a § Navigation targets section (resolution rule, soft-fail contract, fragment form) AND a § Content fidelity section (the block is the substance channel, not just interaction ids; label rule — `label:` is short on-screen UI copy, the action sentence goes in `describes:`; authored-fixtures rule for `sample_rows`/`items`).
- [ ] **Step 5:** Strengthen the optionality language: keep "absent block ⇒ auto-slug fallback" but note the block is REQUIRED from the authoring skill at depth medium+ (cross-reference Task 11) — the fallback is a safety net for hand-written screens, not the primary path.
- [ ] **Step 6:** Update § Examples with: the promoted example gaining a `target:` button, a `kind: nav` + `items` example, a `kind: tabs` example, a `kind: table` example with `sample_rows`, an `input` + `options` example.
- [ ] **Step 7:** Update § Validation with every new invalid case (target on non-interactive kind, items on non-nav/tabs/list kind, malformed screen_id, columns on non-table, sample_rows length mismatch, options on non-input, items entry shape per kind) and note the sister-repo validator (`lab/validate-elements-block`, `ai-assets-skill-development`) needs a matching v0.3 update — cross-repo follow-up, not executed here.
- [ ] **Step 8: Commit.** `feat(contracts): elements_block v0.3 — navigation targets + content-fidelity shapes`

---

### Task 2: `walkthrough_renderer.md` → schema_version 1.2 (one bump, all new behavior)

**Files:**
- Modify: `skaileup/contracts/walkthrough_renderer.md`

**Interfaces:**
- Produces: rewritten kind → DOM mapping (link/button/nav/table/tabs/list/input); new § Target resolution; new § App-shell navigation; rewritten § Auto-slug fallback; new § Spec reference panel; narrowed journey-nav NEVER; `warnings[].kind` gains `unresolved_target` + `no_explicit_elements`; manifest gains `elements[].target/columns/sample_rows/items/options/row_target` + top-level `app_nav[]`; `schema_version: "1.2"`

- [ ] **Step 1:** Bump `schema_version` `"1.0"` → `"1.2"` directly; extend the Change policy note (additive; feedback cluster pins `^1.0`, verified compatible in Task 9).
- [ ] **Step 2: Rewrite the kind → DOM tag mapping table in full:**

| kind | rendered tag | notes |
|---|---|---|
| `input` | `<input>` or `<select>` | `options[]` present → `<select>` with one `<option>` per value; else unchanged (`name`, `aria-label`) |
| `button` | `<button>`, or `<a class="button">` when `target:` present | label as inner text; with `target:`, resolved relative href per § Target resolution |
| `link` | `<a>` | `href` = resolved `target:`; `href="#"` only as the unresolved/absent fallback (+ `unresolved_target` warning when declared-but-unresolved) |
| `image` | `<img>` | unchanged (`src="#"` placeholder, `alt="<label>"`) |
| `text` | `<span>` | unchanged |
| `region` | `<section>` | unchanged (label as inner `<h3>`) |
| `list` | `<ul>` | one `<li>` per `items[]` entry (label verbatim, `target:` wraps in `<a>`); absent/empty `items` → single placeholder `<li>` (degenerate case) |
| `form` | `<form>` | unchanged |
| `nav` | `<nav>` | list of real links from `items[]` (or the generated app nav, § App-shell navigation); each item its own `data-spec-element` |
| `tabs` | `<nav class="tabs">` | one entry per `items[]`, first item active; entries with `target:` render as resolved `<a>`, without as inert `<span class="tab">`; no JS switching (static fidelity boundary) |
| `table` | `<table>` | `<thead>` from `columns[]`; one `<tbody>` row per `sample_rows[]` (verbatim, escaped); no `sample_rows` → header + one skeleton row; `row_target:` wraps each row's first cell in `<a>` |
| `media` | `<figure>` | unchanged |
| `custom` | `<div>` | unchanged, gains: `target:` present wraps content in `<a>` |

- [ ] **Step 3: Add § Target resolution** — the resolution rule from Global Constraints, verbatim, plus: absent target on a button/form-like action → no warning (inert element is intentional).
- [ ] **Step 4: Add § App-shell navigation** — generated, not authored as prose: (a) if `experience/screens/00_layout/shell.md` frontmatter has a `kind: nav` element with `items:`, it's authoritative — render in every screen page's shell wrapper with resolved hrefs; (b) otherwise derive a default nav, one link per rendered screen grouped by `<group>` (label = dir name, `NN_` stripped, underscores → spaces), element id `app-nav`, `data-spec-provisional="true"`, one `auto_slugged` warning. Record in manifest `app_nav[]`. Lives in the contract (single definition); each renderer implements it in its shell/layout template.
- [ ] **Step 5: Rewrite § Auto-slug fallback source set (a):** exclude the canonical spec-template headings (list them verbatim, per Global Constraints) from widget discovery — case-insensitive, these become the spec panel's `<h2>` skeleton (Step 6), never `el-region` widgets. Non-canonical headings (e.g. a screen's own `## Notes`) stay in the net. **Add source (d):** `## Actions` bullets, label-extracted — reachable only when `elements:` is absent/partial: label = first quoted token (`"…"`/`„…“`) when present, else the pre-`→` clause with a leading interaction verb (`Click|Change|Select|Switch|Drag|Pick|Open` + optional article) stripped, truncated to ≤ 40 chars; full bullet → `describes:`. Kind inference: quoted token/`Click …` → `button`; `Change|Select|Pick …` → `input`; `Switch tab` → `tabs` (items from bold/quoted tab names in `## What the User Sees`, else two placeholder items).
- [ ] **Step 6: Add § Spec reference panel** — every screen page renders the full spec body (all canonical sections + wireframe fence) inside a collapsed `<details class="spec-panel"><summary>View spec</summary>…</details>` after the synthesized UI, before the footer. No `data-spec-element` attributes inside it. Zero explicit elements → panel renders `open` + `warnings[]` `kind: "no_explicit_elements"`.
- [ ] **Step 7: Narrow the journey-nav rule** — restate the shared NEVER as: "NEVER inject journey-*step* navigation (Next/Prev, journey-ordering) into `screen/**/*.html` — that lives only in `journey/<id>.html`. Screen-intrinsic `target:` links and the generated app-shell nav are REQUIRED and are not journey-nav." Add Shared MUSTs: `MUST resolve every declared target: into a relative href (or emit unresolved_target + "#")`; `MUST render declared columns/sample_rows/items/options as real DOM content (no placeholder when content is declared)`; `MUST render the spec body only inside the collapsed spec panel`. Add Shared NEVERs: `NEVER render a canonical spec-template heading as a widget`; `NEVER fabricate sample data not present in the screen source`.
- [ ] **Step 8:** § warnings[].kind enum gains `unresolved_target`, `no_explicit_elements`. § Manifest schema: `screens[].elements[]` gain optional echoed `target`, `columns`, `sample_rows`, `items`, `options`, `row_target`; top-level `app_nav: [{label, target, source}]` (`source` = shell-authoritative path or `"derived"`). Document under § Field semantics.
- [ ] **Step 9: Commit.** `feat(contracts): walkthrough_renderer 1.2 — target resolution, app nav, content synthesis, tamed auto-slug, spec panel`

---

### Task 3: Contract fixtures — one pass, all new shapes

**Files:**
- Modify: `skaileup/contracts/tests/elements_block_examples.md`

- [ ] **Step 1: Add valid examples** (5): `with-target` (button `target:` + link `target:#fragment`), `nav-with-items`, `tabs-two-items` (one with `target`, one without), `table-with-sample-rows` (columns + 2 aligned rows + `row_target`), `input-with-options`.
- [ ] **Step 2: Add invalid examples** (7): `target-on-input`, `items-on-button`, `malformed-target` (`target: /faelle` — URL-style, the exact migration mistake to catch), `columns-on-list`, `sample-row-length-mismatch`, `options-on-button`, `items-bad-shape-on-tabs` (missing `label`).
- [ ] **Step 3:** Update the header count note to "8 valid, 9 invalid" and mirror in `elements_block.md` § Validation; add the cross-repo follow-up line (`lab/validate-elements-block` in `ai-assets-skill-development` must implement v0.3 before these fixtures pass there; this repo's CI is unaffected since the validator ships elsewhere).
- [ ] **Step 4: Commit.** `test(contracts): elements_block v0.3 fixtures (target/items/table/tabs/options)`

---

### Task 4: static-html renderer — reference implementation (nav + content, one pass)

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_b_static-html/SKILL.md`
- Modify: `skaileup/05_mockup-walkthrough/01_b_static-html/tests/fixtures/minimal/**`
- Modify: `skaileup/05_mockup-walkthrough/01_b_static-html/tests/expected/minimal/**`

**Interfaces:**
- Consumes: contract §§ from Tasks 1–2
- Produces: screen pages whose primary content is synthesized from `elements:` (real tables/tabs/lists/selects, live `href`s, generated app-shell nav), spec demoted to a collapsed panel; `metadata.version` → `0.2.0`

- [ ] **Step 1: STEP 2 (Read inputs)** — parse/validate all v0.3 fields (`target`, `items` per-kind shape, `columns`, `sample_rows` with length check, `options`, `row_target`); build the rendered-screen-id set first so targets validate against it; parse `00_layout/shell.md` frontmatter for an authoritative `kind: nav` entry; implement the rewritten auto-slug source set (canonical-heading exclusion list verbatim from the contract; Actions label extraction with the quoted-token regex + verb-strip fallback + kind inference).
- [ ] **Step 2: STEP 3 (Render screens)** — render every kind per the Task 2 mapping table: resolved `<a>`/`<button>` hrefs, real `<table>`(thead/tbody), `<nav class="tabs">`, populated `<ul>`/`<select>`; render the shell's app nav (authoritative `items:` or derived-per-group default with `data-spec-provisional`) in every screen's shell wrapper; replace the `screen-body-prose` section with the contract's collapsed `<details class="spec-panel">` (open + `no_explicit_elements` warning when zero explicit elements); explicit elements render in declaration order as the page's main content flow (drop the "elements grid above prose" layout); all hrefs computed per § Target resolution (relative paths only).
- [ ] **Step 3: Inline CSS** — `.spec-panel` (collapsed by default), `.tabs` (active/inactive), real table styles (distinct from the old prose-table styles), `<select>` styling; keep the auto-slug dashed-border treatment for genuinely auto-slugged nodes.
- [ ] **Step 4: STEP 4b (manifest)** — emit `elements[].target/columns/sample_rows/items/options/row_target` + top-level `app_nav[]`; `schema_version = "1.2"`; `metadata.version` → `0.2.0`.
- [ ] **Step 5: CHECKLIST additions:** `- [ ] Every elements[] entry with a resolvable target renders an <a> whose href resolves to an existing rendered file`; `- [ ] No rendered screen contains href="#" on a node whose manifest element declares a resolved target`; `- [ ] Every screen page contains the app nav (<nav>) with one resolvable href per entry`; `- [ ] No canonical spec heading appears as an el-region widget`; `- [ ] Every declared table renders sample_rows verbatim as <tbody> rows`; `- [ ] Spec body appears only inside <details class="spec-panel">`; `- [ ] No auto-slugged label exceeds 40 chars or contains an action sentence`.
- [ ] **Step 6: Fixture update.** Give the minimal fixture: `login.md`/`register.md` gain a `target:`-bearing link between them (`go-register` / inverse); add one `table` element (columns + 2 sample rows, `row_target`) and one `input` with `options:` to one fixture screen; add a fixture screen with NO `elements:` block using the canonical headings (expect: open spec panel, `no_explicit_elements` warning, zero heading-widgets). Regenerate all expected HTML files + `manifest.json` by hand per the rewritten SKILL.md templates.
- [ ] **Step 7: Verify** `bash tests/run_validator.sh` passes structurally (the new invariant checks land in Task 5, which tightens it).
- [ ] **Step 8: Commit.** `feat(mockup-walkthrough): static-html renders live targets + generated app nav + content synthesis`

---

### Task 5: static-html validator — enforce both invariants

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_b_static-html/validator.py`

**Interfaces:**
- Produces: `check_targets(site, manifest, report)`, `check_content_fidelity(site, manifest, report)`; `SCHEMA_VERSION = "1.2"`; `app_nav` in `TOP_LEVEL_KEYS`

- [ ] **Step 1:** `SCHEMA_VERSION = "1.2"`; add `"app_nav"` to `TOP_LEVEL_KEYS`.
- [ ] **Step 2: Add `check_targets`:** every manifest element with `target` either resolves against the rendered `screen_id` set or has a matching `unresolved_target` warning with the same `element_id`; when resolvable, the node carrying that `data-spec-element` is (or is wrapped by) an `<a>` whose `href` resolves relative to the page's directory to an existing file; an `<a>` whose manifest entry declares a *resolved* target MUST NOT have `href="#"`. Also check every `app_nav[]` entry resolves, and every `screen/**/*.html` contains ≥ 1 `<nav>` with a relative-href `<a>`.
- [ ] **Step 3: Add `check_content_fidelity`:** every element with `sample_rows` → its node's `<tbody>` has exactly that many `<tr>`; every element with `items`/`options` → one `<li>`/`<option>`/tab entry per declared item; no `data-spec-element` id in the canonical-heading slug set (`purpose, route, what-the-user-sees, wireframe, information-displayed, actions, situations, ui-elements, template-data, navigation, layout-areas, responsive-behaviour`) appears anywhere in the site; every `screen/**/*.html` contains exactly one `<details class="spec-panel">` and no `<section class="screen-body-prose">`; every screen with zero non-provisional elements has a matching `no_explicit_elements` warning.
- [ ] **Step 4:** Run fixture mode against the Task 4 snapshots per `tests/run_validator.sh`; PASS required.
- [ ] **Step 5: Commit.** `feat(mockup-walkthrough): static-html validator enforces targets + content fidelity`

---

### Task 6: astro renderer (nav + content, one pass)

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_c_astro/SKILL.md`
- Modify: `skaileup/05_mockup-walkthrough/01_c_astro/validator.py`
- Modify: `skaileup/05_mockup-walkthrough/01_c_astro/tests/fixtures/minimal/**` + `tests/expected/minimal/**`

- [ ] **Step 1: `specs.json` shape** — add `target`, `items`, `columns`, `sample_rows`, `options`, `row_target` on element objects; top-level `app_nav[]`; new per-screen `body_html` (rendered spec body — astro's screen template currently drops the body entirely, so this is the spec-panel's data source). Add template-convenience `href` fields on elements/items (pre-resolved; MUST NOT be copied into `manifest.json`, same pattern as existing `title`/`group` convenience fields).
- [ ] **Step 2: STEP 2 (Read inputs)** — same parsing/validation/auto-slug rewrite as Task 4 Step 1; emit `unresolved_target`/`no_explicit_elements` warnings at derivation time (astro templates receive pre-resolved values, never raw unresolved state).
- [ ] **Step 3: Scaffold templates (init-only files)** — in `[...slug].astro`'s `tagMap`: replace the hardcoded `link: '<a href="#" …'` with `el.href ?? '#'` interpolation; add `table`/`tabs` rows and populate `list`/`select`; append `<details class="spec-panel"><Fragment set:html={screen.body_html} /></details>` after the elements flow; add an app-nav block to `Shell.astro` from `specs.app_nav`. **Update-mode caveat (write into the SKILL.md):** these files are scaffolded once and never touched on update runs — extend the existing `stale_scaffold`-style check (grep `[...slug].astro` for the string `el.href` AND `spec-panel`; either missing → warning `kind: "stale_scaffold"` telling the user to delete the scaffold or port the template).
- [ ] **Step 4: Manifest step** — `schema_version "1.2"`, all new fields from the in-memory model (not specs.json); `metadata.version` → `0.2.0`.
- [ ] **Step 5: validator.py** — port Task 5's `check_targets`/`check_content_fidelity` (share logic by copy, consistent with the two validators' existing sibling structure); update fixtures/snapshots (mirror Task 4 Step 6).
- [ ] **Step 6: Commit.** `feat(mockup-walkthrough): astro renders live targets + app nav + content synthesis (stale_scaffold guard)`

---

### Task 7: lit renderer (nav + content, one pass)

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_d_lit/SKILL.md`

- [ ] **Step 1:** `specs.json` shape + STEP 2 — identical additions to Task 6 Steps 1–2 (including `body_html`, pre-resolved `href`, warnings at derivation).
- [ ] **Step 2: `screen-view.js` TAG map** — replace the hardcoded `href="#"` with `href=${el.href ?? '#'}` for `link`/`button`/`list`/`custom`; add `table`/`tabs` entries; populate `list` from `items`, `input` → select when `options`; render the spec panel (`<details>`, light DOM, `unsafeHTML(body_html)`) and an `app-nav` block (from `specs.app_nav`) in the `<screen-view>` shell region. Extend the `stale_scaffold` check (grep component source for `el.href` and `spec-panel`).
- [ ] **Step 3:** Manifest `schema_version "1.2"` + new fields; `metadata.version` → `0.2.0`; CHECKLIST gains Task 4 Step 5's lines. **Note (no fix, just record):** `lit`'s `validator.py` is referenced by STEP 8 but doesn't exist on disk (pre-existing gap) — add a one-line NOTE that when authored it MUST include the Task 5 checks; do not author it here.
- [ ] **Step 4: Commit.** `feat(mockup-walkthrough): lit renders live targets + app nav + content synthesis`

---

### Task 8: framework renderer (nav + content, one pass)

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_e_framework/SKILL.md`

- [ ] **Step 1:** `specs.json` shape + STEP 3 (Read inputs) — same additions as Task 6 Steps 1–2. Framework delegates its DOM mapping to the shared contract, so most of the change arrives free via Task 2 — add: one § Renderer Contract paragraph stating targets/content are pre-resolved in `specs.json` and route templates interpolate them (framework-native link components — `next/link`, `NuxtLink`, SvelteKit `<a>` — acceptable iff the built static HTML contains a plain resolvable `href` server-side, per the existing data-spec-* invariant); the root layout renders `specs.app_nav`; `stale_scaffold` mirror (grep for `el.href`/`spec-panel` equivalents in the framework's idiom).
- [ ] **Step 2:** Manifest `schema_version "1.2"` + fields; `metadata.version` → `0.2.0`; CHECKLIST additions; same validator NOTE as lit (no `validator.py` on disk — spec the checks, don't author).
- [ ] **Step 3: Commit.** `feat(mockup-walkthrough): framework renders live targets + app nav + content synthesis`

---

### Task 9: feedback-cluster coordination (contract change policy)

**Files:**
- Modify: `skaileup/07_mockup-feedback/03_patch/SKILL.md`
- Modify: `skaileup/07_mockup-feedback/01_annotate/tests/fixtures/minimal/**` + `tests/expected/minimal/**` (only if Step 1 finds hard-pins)

The `walkthrough_renderer.md` change policy requires a coordinated `mockup-feedback-annotate` check on any schema bump; a `table` node now has rich children (rows) instead of being a leaf, so this is worth actually checking, not just noting.

- [ ] **Step 1: Verify annotate compatibility.** Grep `07_mockup-feedback/01_annotate` (overlay JS + validator + fixtures) for `schema_version` handling and any assumption that annotatable nodes are simple/leaf elements or that `<button>` is never `<a>`. Expected: the overlay selects on `data-spec-*` only → no code change needed; refresh the fixtures to 1.2-shaped pages (mirroring Task 4's snapshots) so the suite exercises table/tabs/panel/app-nav DOM.
- [ ] **Step 2: Extend `mockup-feedback-patch`** with a `target-promotion` path (when an annotation expresses navigation intent on an element without `target:`, author an `@@ frontmatter:elements @@` diff adding it — same template family as the existing `provisional-promotion` kind) — one paragraph + one template block.
- [ ] **Step 3: Commit.** `feat(mockup-feedback): 1.2 coordination — annotate fixtures + target-promotion patches`

---

### Task 10: text variant — minimal alignment + divergence flag (unchanged scope from source plan)

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_a_text/SKILL.md`

`01_a_text` is the legacy MIGRATED linked-prototype skill — it implements neither the walkthrough-renderer contract nor `elements:`, ignoring both this task and its sibling. Full realignment is out of scope; this is the minimal forward-reference.

- [ ] **Step 1:** Add a `> **DIVERGENCE NOTE (2026-07-05):**` blockquote under the H1: this skill's body predates the walkthrough-renderer contract and does not implement it; its intended shape is read-only per `mockup-design.md` § 4; full realignment is a separate backlog item.
- [ ] **Step 2:** Add one contract-forward instruction to Phase 4 (Screen Pages): when a screen's `elements:` declares `target:` values (v0.3), render each as `→ opens: <screen_id>` next to the element (this legacy variant already emits real `<a>` links — use them as the href source instead of guessing from prose).
- [ ] **Step 3: Commit.** `docs(mockup-walkthrough): text-variant divergence note + target cross-references`

---

### Task 11: upstream authoring — `experience-screens` MUST emit the full `elements:` block

**Files:**
- Modify: `skaileup/03_experience/03_screens/SKILL.md`
- Modify: `skaileup/03_experience/03_screens/references/screen_spec_template.md`

New projects must never rely on the fallback for either navigation or content. This merges the two source plans' authoring tasks (LI's "author targets" + CF's "author elements") into one STEP, since it's the same block on the same file.

**Hard MUST, not a soft gate — justification:** the current state IS the soft-gate outcome (0/43 CLINICO screens declare `elements:`). There's no authoring-time enforcement point (the elements-block validator lives in the sister repo, not wired into target projects; the renderer's `no_explicit_elements`/`unresolved_target` warnings are a render-time echo, many phases later). So: hard MUST at depth `medium`/`max`, exempt at `light`/`none` — consistent with the existing `MUST include a ### Wireframe section … at depth medium or max` precedent. Renderers never hard-fail either way, so this can't brick a hand-written project.

- [ ] **Step 1: Add a new sub-step (STEP 4b — Derive the `elements:` block)** between the spec-writing step and the feedback-loop registration step: for each screen just written, derive frontmatter `elements:` from its own sections — every entry in `### UI Elements` and every interactive/structural thing named in `## Actions` and `## Information Displayed` becomes an element with: short `label:` = on-screen UI copy (the quoted token from an Actions bullet, e.g. "Aufnehmen" — NEVER the action sentence, which goes in `describes:`); correct `kind:` (tab bars → `tabs`; row lists → `table` or `list` with `items:`; named-option filters → `input` + `options:`); `data_entity:` from the screen's `data_entities[]`; `target:` when the bullet names a destination screen (resolve against sibling screens by title/route/filename-stem, same precedence order the migration skill uses); `sample_rows`/`items` sourced from `seed.json` scenarios when present, else from the wireframe's own example rows.
- [ ] **Step 2: Add to the MUST list:** `MUST declare an explicit elements: block on every screen spec at depth medium or max, covering every interactive or structural thing named in ### UI Elements, ## Actions, and ## Information Displayed, including target: for every action that names a destination screen (per contracts/elements_block.md § Navigation targets and § Content fidelity)`; `NEVER use an action sentence as an element label — labels are on-screen UI copy`.
- [ ] **Step 3: Shell authoring addendum:** when writing `00_layout/shell.md`, the `## Navigation` destination list MUST be mirrored as a `kind: nav` element with `items[].target` in the shell's own frontmatter (contract § App-shell navigation, authoritative case).
- [ ] **Step 4: REFERENCES + CHECKLIST:** add `contracts/elements_block.md` to REFERENCES; CHECKLIST gains `- [ ] Every screen spec (depth medium+) has an elements: block whose labels are short UI copy`, `- [ ] Every action naming a destination screen has a matching target:`, `- [ ] Every table/list element with visible sample content in the wireframe carries sample_rows/items`.
- [ ] **Step 5: Update `references/screen_spec_template.md`** — the `### UI Elements` section gains: "Each entry here MUST be mirrored as a structured `elements:` frontmatter entry (see `contracts/elements_block.md`) — the prose list is the human-readable view, the frontmatter is the machine-readable one." Add a frontmatter example with one `target:`-bearing button, one `table`, and one `tabs` element. Same addendum for `00_layout/shell.md`'s template re: `kind: nav`.
- [ ] **Step 6: Commit.** `feat(experience): screens skill authors structured elements blocks (targets + content)`

---

### Task 12: migration skill — `mockup-walkthrough-migrate-elements` (combined nav + content backfill)

**Files:**
- Create: `skaileup/05_mockup-walkthrough/00_migrate-elements/SKILL.md`
- Modify: `skaile.yaml` (register `kind: skill`)

**Decision: one combined skill**, not a separate targets-only and content-only pass — both would emit conflicting `@@ frontmatter:elements @@` patches against the same 43 screen files' same YAML block, force two human review rounds over identical screens, and target extraction (parsing `## Actions` for destinations) is a strict subset of content extraction (parsing the same bullets for labels/kinds PLUS `## Information Displayed`/`## What the User Sees`/the wireframe for columns/rows/tabs).

- [ ] **Step 1: Author the SKILL.md** (name `mockup-walkthrough-migrate-elements`, `00_` slot — runs before the pick-one renderers, not numbered into the render alternatives). Per screen, one synthetic-session pass producing a complete proposed `elements:` block:
  1. **Inventory:** glob screens (excl. `00_layout/`); build `screen_id → (title, ## Route, filename-stem words)` lookup.
  2. **Extract elements (LLM-assisted):** from `### UI Elements` (when present); `## Actions` (label = quoted token; kind inference per Task 2 Step 5's rules; `target:` resolved by title/route/stem match, in that order, each carrying a confidence note); `## Information Displayed` + `## Wireframe` (table candidates: entity rows with named fields → `columns:`; the wireframe's own example rows → `sample_rows:`, verbatim, flagged low-confidence when reconstructed from ASCII); `## What the User Sees` (bold/quoted tab names → `tabs` items). Shell: `## Navigation`'s ordered destination list → `kind: nav` + `items[].target`.
  3. **Emit patches:** one `@@ frontmatter:elements @@` section-anchored diff per screen with the complete proposed block — exactly the diff dialect `mockup-feedback-patch` documents and `apply.py` parses. Write `patches/<sid>.json` (schema-valid) + `patches/<sid>.review.md`; every low-confidence item (ASCII-reconstructed rows, unresolved targets) **unticked**.
  4. **CHECKPOINT:** human reviews `review.md` (tick/untick/hand-edit), runs `mockup-feedback-apply` (gets the devlog entry + `applied/<sid>.json` audit trail for free).
  5. Re-run the project's walkthrough renderer; confirm `unresolved_target`/`no_explicit_elements` warning counts drop in the fresh `manifest.json`; iterate on leftovers.
- [ ] **Step 2: MUST/NEVER:** MUST route all source mutations through `mockup-feedback-apply`; MUST propose short UI-copy labels only (quoted-token rule); MUST copy sample rows verbatim from the source (wireframe/Template Data) — NEVER invent patient names, dates, or values not present in the screen file; MUST leave unresolvable action bullets/targets untouched (prose stays truth); NEVER guess a target below the stated confidence rules without leaving the review item unticked; NEVER edit rendered HTML; NEVER emit a partial block that silently drops a described widget without noting it in `review.md`.
- [ ] **Step 3:** Register in `skaile.yaml` (`kind: skill`). Do NOT wire into any flow — flows' `requires:` exactness would force churn across tier flows for a one-time pass; running it stays manual/orchestrator-routed (optional follow-up: add as an optional entry node of the `mockup-feedback` sub-flow once the 2026-07 flow restructure lands).
- [ ] **Step 4: Commit.** `feat(mockup-walkthrough): migrate-elements skill (Actions/Information/Wireframe prose → target + content backfill)`

---

### Task 13: docs — record the merged intent where the next author will look

**Files:**
- Modify: `docs/devlog/mockup-design.md`
- Modify: `skaileup/05_mockup-walkthrough/DOMAIN.md`

- [ ] **Step 1:** `mockup-design.md` § 4 (tier table): dated note that "clickable" (static-html's stated interactivity) is now realized by `target:`/`items:` resolution + the generated app-shell nav, and that content presence (tables/tabs/lists) is now uniform across all tiers — the tier ladder differentiates *interactivity*, not *content presence*. § 6: extend the `elements:` example with a `target:` line and a `table` entry.
- [ ] **Step 2:** `DOMAIN.md`: one paragraph covering both — screens are synthesized from `elements:` (interaction + content); journeys are guided tours, not the transport layer; the spec prose lives in the collapsed spec panel; sample data is authored fixture, never renderer-invented.
- [ ] **Step 3: Commit.** `docs(mockup): record merged navigation + content-fidelity model`

---

## Non-goals

- **No client-side state simulation.** Tab bars render with a static active state (no JS switching), tables don't sort/filter, selects don't filter lists. `sample_rows`/`items` are illustrative fixtures, not live data. Real state stays the `lit`/`astro`/`framework` tiers' fidelity job per `mockup-design.md` § 4 — this plan fixes *clickability* and *content presence*, not *behavior*.
- **No conditional/role-based navigation** (e.g. CLINICO's "Sysadmin sees Administration") — `target:` is unconditional; visibility rules stay prose.
- **No renderer-invented sample data** — a table without `sample_rows` gets a skeleton row, never fabricated records.
- **No per-row/per-cell annotation targets** — table rows/list items live inside their element's single `data-spec-element` node (the `nav`/`tabs`/`list` `items[]` per-entry id is the one pinned exception, needed so individual nav/tab/list entries stay annotatable).
- **No layout/wireframe-geometry synthesis** — elements render in declaration order in the content flow; reproducing the wireframe's 2-D zone layout is out of scope.
- **No text-tier rewrite** (Task 10 is minimal alignment only) and **no component-mockup changes** (`isolated-html` is link-free by design; `storybook`'s journeys cluster already mandates real in-UI navigation — no change needed there).
- **No authoring of the missing lit/framework validators** (pre-existing gap; their checks are specified in the SKILL.md CHECKLISTs for when they eventually land).
- **No sister-repo edits** — `lab/validate-elements-block` (`ai-assets-skill-development`) v0.3 support is a named follow-up, not executed here.
- **No flow YAML changes** — the migration skill stays outside `requires:` manifests to avoid tier-flow churn.
- **No retrofitting CLINICO's already-rendered HTML by hand** — it gets fixed by running Task 12's migration against its screen sources, then re-rendering; never by editing `_concept/mockup-walkthrough/**` output directly.

## Supersession note

This merged plan supersedes the individual task lists in `docs/devlog/2026-07-05-mockup-live-interconnect-plan.md` and `docs/devlog/2026-07-05-mockup-content-fidelity-plan.md` for **execution purposes**. Both documents remain as the evidence/rationale record (diagnosis tables, CLINICO citations, design reasoning) and are not rewritten. Do not re-run their task lists independently — this document is what `superpowers:subagent-driven-development` should walk.
