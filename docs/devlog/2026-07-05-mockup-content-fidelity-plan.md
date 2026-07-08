# Mockup Content-Fidelity Implementation Plan (screens render as UI, not as spec documents)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** planned · verified against the CLINICO run (`/Users/matthias/devBench/CLINICO`) 2026-07-05 · sibling of `docs/devlog/2026-07-05-mockup-live-interconnect-plan.md` (navigation targets) — this plan fixes the second root cause of the "mockups read as descriptions, not working prototypes" complaint: **content fidelity**.

**Goal:** Make walkthrough screen pages read as an approximation of the real UI — real tab bars, real tables with plausible sample rows, real dropdowns with short UI-copy labels — instead of spec documents with decorative widgets glued on top. Three coordinated changes: (1) the `experience-screens` authoring skill MUST emit an explicit `elements:` block per screen (today 0 of 43 CLINICO screens have one, so 100% of rendering falls through the auto-slug safety net), (2) the `elements:` schema gains content-carrying shapes (`table` with `columns:`/`sample_rows:`, `tabs`/`list` with `items:`, `input` with `options:`) so renderers can materialize substance, (3) renderers synthesize the primary page from `elements:` and demote the raw spec prose to a collapsed reference panel, while the auto-slug fallback stops turning documentation section headings into on-page widgets and stops using whole action sentences as button labels.

**Architecture:** Same contract-first flow as the sibling plan, layered on top of it: `elements_block.md` v0.2 → **v0.3** (additive content fields), `walkthrough_renderer.md` schema_version 1.1 → **1.2** (new kind rows, auto-slug source-set fix, spec-panel rule), then renderers (static-html reference implementation first), then the authoring skill, then one **combined** migration pass (this plan folds the sibling's Task 11 `mockup-walkthrough-migrate-targets` into a single `mockup-walkthrough-migrate-elements` skill — see Task 10 for the reasoning). The root cause is a two-sided vacuum: `elements_block.md` marks the block fully OPTIONAL and `03_screens/SKILL.md` never mentions it (zero occurrences), so nothing ever authors it; meanwhile `walkthrough_renderer.md` § Auto-slug fallback source set (a) "markdown headings" ingests the fixed spec-template headings (`## Purpose`, `## Route`, …) as widgets, and even an *explicit* block couldn't carry a table today (`list` → "empty list with placeholder `<li>`" per the kind → DOM mapping).

**Tech Stack:** Markdown contracts + skill DSL (per `skaileup/contracts/skill_grammar.md`), YAML frontmatter, Python 3.12 validators (stdlib + PyYAML), Astro/Lit/framework scaffold templates embedded in SKILL.md bodies.

## Verified diagnosis (read before editing — do not re-derive)

| # | Claim | Verified | Evidence |
|---|---|---|---|
| 1 | 0 of 43 CLINICO screens declare `elements:` | ✅ | `grep -l '^elements:'` over `_concept/experience/screens/**/*.md` (excl. `00_layout/`): total=43, matches=0 — auto-slug is the universal path, not the exception |
| 2 | Spec-template headings render as widgets | ✅ | `screen/11_intake/case_admission_list.html` line 423: `<section class="el-region" data-spec-element="purpose">…<h3>Purpose</h3>`, likewise `route`, `what-the-user-sees`, `wireframe`; same in `02_dashboard/dashboard.html`, `04_todos/todo_list.html`, `12_scheduling/appointment_calendar.html` (there `notes` — non-canonical headings get slugged too) |
| 3 | Whole action sentences become labels/ids | ✅ | `data-spec-element="click-aufnehmen-on-an-anmeldung-row"`, `"postpone-submenu-heute-in-einer-woche-anderes-datum"`, `"click-an-empty-slot-or-neuer-termin"`; button text literally `Click "Aufnehmen" on an Anmeldung row`; `<input placeholder="Change Bereich / Falltyp filter">` where the source describes two dropdowns; `Switch tab` → one button where the source names two tabs (Aufzunehmen / Fälle) |
| 4 | Substantive content never renders as markup | ✅ | The two-tab list, filter dropdowns, and sample rows (Lena M., Tom B.) exist only as the ASCII `<pre>` wireframe + `## Information Displayed` bullets; contract § kind → DOM mapping: `list` → "empty list with placeholder `<li>`" — no content path exists even with an explicit block |
| 5 | static-html re-dumps the whole spec as the page | ✅ | `01_b_static-html/SKILL.md` STEP 3 ("Render the screen body markdown … inside a `<section class="screen-body-prose">`"); CLINICO pages carry every spec section (Purpose → Situations) as styled prose below the sparse widget grid |
| 6 | Authoring skill never mentions `elements:` | ✅ | `03_experience/03_screens/SKILL.md` — zero occurrences of `elements`; its MUSTs cover shell-first, user perspective, data entities, `### Wireframe` only. The spec template even mandates a `### UI Elements` prose section — the block's natural twin — but nothing structures it |
| 7 | Heading set confirmed | ✅ | `03_screens/references/screen_spec_template.md`: **Purpose · Route · What the User Sees · Wireframe · Information Displayed · Actions · Situations · UI Elements · Template Data** (last one optional); shell.md adds **Navigation · Layout Areas · Responsive Behaviour**. CLINICO screens follow this set (they omit UI Elements; some add `## Notes`) |

**Where the diagnosis needed extension:**

- **The prose dump is static-html-specific; astro/lit/framework fail *worse*.** Their screen templates (`[...slug].astro` line ~466, lit `screen-view.js` TAG map, framework pages) render **only** the elements grid — no body markdown at all. With no `elements:` block, an astro/lit/framework screen is pure auto-slugged widget soup with the substantive description (wireframe, information, situations) entirely absent. Same root cause (no content path through `elements:`), opposite symptom. The fix converges all four: primary page synthesized from `elements:`, spec available as a collapsed reference panel (which astro/lit/framework gain for the first time).
- **All four contract renderers share the auto-slug bug verbatim** — each SKILL.md's STEP 2/3 restates the contract's fallback including the heading source set. The `01_a_text` variant is the legacy off-contract linked-prototype skill (sibling plan Task 9's divergence note); ironically it has the best content fidelity (seed data, tabs, modals) but implements neither the contract nor `elements:` — untouched here, same non-goal as the sibling plan.
- **Only ~4 headings became widgets per CLINICO screen** (the LLM run didn't slug every heading). Incidental — the contract's source set licenses all `##`/`###` headings; the fix targets the contract, not the observed subset.
- **Sample-data provenance exists upstream.** The authoring skill already reads `_concept/blueprint/datamodel/seed.json` scenarios ("Template Data" section) and screen wireframes already carry invented sample rows (Lena M., Tom B.) — `sample_rows:` has a natural authoring source; renderers never invent data.
- **Migration overlap confirmed.** Sibling Task 11's mechanism is: inventory screens → LLM-extract from `## Actions` prose → emit section-anchored `@@ frontmatter:elements @@` patches + review.md → human ticks → `mockup-feedback-apply` (`apply.py`). Content backfill mutates **the same frontmatter section of the same 43 files** via the same machinery, and its extraction pass (Actions + Information Displayed + Wireframe + What the User Sees) is a strict superset of the target extraction (Actions bullets only). Two skills would emit two conflicting patch sets against one YAML block and force two human review rounds over identical screens → **one combined skill** (Task 10).

## Global Constraints

- **Ordering: after the live-interconnect plan's Tasks 1–2.** This plan's contract bumps are v0.2 → v0.3 (`elements_block.md`) and 1.1 → 1.2 (`walkthrough_renderer.md`), additive-only on top of the sibling's `target:`/`items:` fields. If both plans are executed in one pass, land the bumps as a single v0.3 / 1.2 change and say so in each contract's status header.
- **`items:` is one field, kind-dependent entry shape — reuse, don't reinvent.** The sibling plan introduces `items: [{id?, label, target, icon?}]` on `kind: nav`. This plan extends the *same field* to `tabs` (`{id?, label, target?}` — target optional, tabs may be in-page) and `list` (`{label, target?}` or bare strings). One resolution rule, one auto-slug rule for item ids, no parallel field name.
- **Sample data is illustrative fixture, never invented by renderers.** `sample_rows:`/`items:` content is authored (from seed.json scenarios or the wireframe's own examples) and rendered verbatim. A `table` with `columns:` but no `sample_rows:` renders the header row plus one skeleton row — renderers MUST NOT fabricate rows.
- **Soft-fail rendering, hard-require authoring.** Renderers never hard-fail on a missing/partial `elements:` block (the fallback stays, degraded gracefully per Task 2). The *authoring skill* gets the hard MUST — see Task 9 for the justification.
- **No new `data-spec-*` attributes.** Table rows, tab items, and list items are content *inside* the element's single `data-spec-element` node (nav `items[]` ids from the sibling plan are the one pinned exception). The feedback cluster keeps resolving clicks identically.
- **Renderers stay read-only on sources.** All backfill goes through the combined migration skill (Task 10) with human review.
- **static-html is the reference implementation** — Tasks 4–5 land before astro/lit/framework (Tasks 6–8); its output is the tie-breaker (existing contract rule).
- **Green after every task:** `python3 skaileup/05_mockup-walkthrough/01_b_static-html/validator.py <fixture-site> --fixture minimal` passes wherever fixtures exist; `git diff --stat` limited to the task's Files list.
- **Commits:** conventional-commit style, each ending with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

---

## Reference: the new fields (decided)

**Table content — columns + illustrative rows** (new `kind: table`):

```yaml
elements:
  - id: faelle-table
    kind: table
    label: "Fälle"
    states: [default, loading, empty]
    data_entity: cases
    columns: ["Patient", "Falltyp", "Bereich", "Status", "Aufgenommen"]
    sample_rows:                       # 2-3 rows, authored fixtures — renderers never invent
      - ["Lena M.", "Teilstationär", "Kindergruppe", "Aktiv", "15.06.2026"]
      - ["Tom B.", "Ambulant", "Jugendgruppe", "Aktiv", "03.06.2026"]
    row_target: 11_intake/case_detail  # optional — every row links here (sibling plan's resolution rule)
```

`sample_rows` entries are lists positionally aligned to `columns` (validate `len(row) == len(columns)`). List-of-lists over list-of-dicts: terser to author, no key-drift validation, column order is the render order anyway.

**Tab bar** (new `kind: tabs` — the "Switch tab" case):

```yaml
elements:
  - id: case-tabs
    kind: tabs
    label: "Fälle & Aufnahmen Tabs"
    states: [default]
    items:                             # SAME field as nav items (sibling plan) — target optional here
      - label: "Aufzunehmen"           # first item renders active
      - label: "Fälle"
```

**List with real items** (`kind: list` gains `items:`):

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
      - "Tom B. · geb. 02.09.2010 · Jugendgruppe"   # bare string allowed
```

**Select input** (`kind: input` gains `options:` — the "Change Bereich / Falltyp filter" case becomes two dropdowns):

```yaml
elements:
  - id: filter-bereich
    kind: input
    label: "Bereich"
    states: [default]
    options: ["Alle", "Kindergruppe", "Jugendgruppe"]   # presence ⇒ render <select>
```

**Label rule (contract + authoring):** `label:` is the **on-screen UI copy** — short, extracted from quotes in the prose where present ("Aufnehmen", "Bereich"), never the action sentence. The action sentence belongs in `describes:`.

---

### Task 1: `elements_block.md` v0.3 — content-carrying shapes

**Files:**
- Modify: `skaileup/contracts/elements_block.md`

**Interfaces:**
- Produces: `kind` enum + `table`, `tabs`; fields `columns`, `sample_rows`, `row_target` (kind `table`), `items` extended to kinds `tabs`/`list`, `options` (kind `input`)

- [ ] **Step 1: Bump the status header** to `v0.3 — adds content-fidelity shapes (table/tabs/list items/input options; 2026-07-05 content-fidelity plan)`, noting it layers on v0.2 (live-interconnect).
- [ ] **Step 2: Extend the `kind` enum** with `table` and `tabs` (keep the "prefer proposing an extension over `custom`" note — these two ARE that extension, cite the CLINICO evidence in one line).
- [ ] **Step 3: Extend § Schema and § Field reference:**
  - `columns` — list of strings, required iff `kind: table` (schema-invalid elsewhere).
  - `sample_rows` — list of lists of strings, optional, `table` only; each row `len == len(columns)`; 2–3 rows recommended; MUST be authored fixtures (seed.json scenarios or the wireframe's examples), renderers MUST NOT invent rows.
  - `row_target` — string, optional, `table` only; same `screen_id` grammar and resolution rule as v0.2 `target:` (cross-reference § Navigation targets).
  - `items` — widen the v0.2 definition: on `kind: nav` entries are `{id?, label, target, icon?}` (unchanged); on `kind: tabs` entries are `{id?, label, target?}`; on `kind: list` entries are `{label, target?}` or bare strings. Still schema-invalid on all other kinds.
  - `options` — list of strings, optional, `kind: input` only; presence means the input renders as a select.
- [ ] **Step 4: Add a § Content fidelity section:** the block is how a screen's *substance* (not just its interaction ids) reaches renderers; label rule (short UI copy, never the action sentence — sentence goes in `describes:`); the authored-fixtures rule for `sample_rows`/`items`.
- [ ] **Step 5: Strengthen the optionality language.** Keep "absent block ⇒ auto-slug fallback" (renderers stay tolerant) but replace the bare "The `elements:` block is optional" framing with: optional *for renderers*; the authoring skill (`experience-screens`) is REQUIRED to emit it at depth medium+ — cross-reference Task 9's MUST. The fallback is a safety net for hand-written screens, not a primary path.
- [ ] **Step 6: Update § Examples** with the table + tabs examples from the Reference block above; update § Validation with the new invalid cases (columns on non-table, sample_rows length mismatch, options on non-input, items entry shape per kind) and note the sister-repo validator (`lab/validate-elements-block`, ai-assets-skill-development) must implement v0.3 — cross-repo follow-up tracked with the sibling plan's Task 3 note.
- [ ] **Step 7: Commit.** `feat(contracts): elements_block v0.3 — content-fidelity shapes (table/tabs/items/options)`

---

### Task 2: `walkthrough_renderer.md` 1.2 — render substance, tame the fallback, demote the prose

**Files:**
- Modify: `skaileup/contracts/walkthrough_renderer.md`

**Interfaces:**
- Produces: new/updated kind → DOM rows (`table`, `tabs`, `list`, `input`); rewritten § Auto-slug fallback (heading exclusion + Actions label extraction); new § Spec reference panel; `schema_version: "1.2"`

- [ ] **Step 1: Bump** `schema_version` `"1.1"` → `"1.2"`; extend the Change policy note (additive; feedback cluster pins `^1.0`, coordination check in Task 8's annotate step mirrors the sibling plan's Task 12).
- [ ] **Step 2: kind → DOM mapping — add/rewrite four rows:**

| kind | rendered tag | notes |
|---|---|---|
| `table` | `<table>` | `<thead>` from `columns[]`; one `<tbody>` row per `sample_rows[]` entry (verbatim, escaped); no `sample_rows` → header + one skeleton row; `row_target:` wraps each row's first cell in an `<a>` per § Target resolution |
| `tabs` | `<nav class="tabs">` | one entry per `items[]`, first item active; entries with `target:` render as resolved `<a>`, without as inert `<span class="tab">`; no JS tab switching (fidelity boundary) |
| `list` | `<ul>` | one `<li>` per `items[]` entry (label verbatim; `target:` wraps in `<a>`); empty/absent `items` → single placeholder `<li>` (current behaviour becomes the degenerate case) |
| `input` | `<input>` or `<select>` | `options[]` present → `<select>` with one `<option>` per value; else unchanged |

- [ ] **Step 3: Rewrite § Auto-slug fallback source set (a):**
  - **Exclude the canonical spec-template headings** from widget discovery, case-insensitive: `Purpose`, `Route`, `What the User Sees`, `Wireframe`, `Information Displayed`, `Actions`, `Situations`, `UI Elements`, `Template Data`, plus the shell headings `Navigation`, `Layout Areas`, `Responsive Behaviour`, plus any `# Screen: *` / `# Shell: *` H1. These are documentation structure — they become the `<h2>` skeleton of the spec reference panel (Step 4), never `el-region` widgets. Non-canonical headings (e.g. CLINICO's `## Notes`) stay in the net as `region` candidates — the net stays wide where it might describe a genuine UI zone.
  - **Add source (d): `## Actions` bullets, label-extracted.** Only reachable when `elements:` is absent/partial (rare post-Task 9, must degrade gracefully): for each bullet, the label is the first double-quoted token (`"…"` or `„…“`) when present (e.g. `Aufnehmen`); otherwise the pre-`→` clause with a leading interaction verb (`Click|Change|Select|Switch|Drag|Pick|Open` + optional article) stripped and truncated to ≤ 40 chars. The full bullet goes to the element's `describes:` slot in the manifest, never into the visible label. Kind inference: quoted token or `Click …` → `button`; `Change|Select|Pick …` → `input`; `Switch tab` → `tabs` (items from any bold/quoted tab names in `## What the User Sees`, else two placeholder items).
- [ ] **Step 4: Add § Spec reference panel** (replaces static-html's ad-hoc `screen-body-prose` rule and gives astro/lit/framework a home for content they currently drop): every screen page MUST render the full spec body (all canonical sections, wireframe fence included) inside a **collapsed** `<details class="spec-panel"><summary>View spec</summary>…</details>` placed after the synthesized UI, before the footer. The primary visible page is the `elements:`-synthesized UI; the spec is reference material underneath — never the other way around. Panel content receives no `data-spec-element` attributes (existing body-markdown rule, restated). When a screen has **zero** explicit elements, the panel renders `open` (degraded mode: the spec is all there is) and the renderer appends one `warnings[]` entry `kind: "no_explicit_elements"`.
- [ ] **Step 5: § warnings[].kind enum** gains `no_explicit_elements`. § Manifest schema: `screens[].elements[]` entries gain optional echoed `columns`, `sample_rows`, `items`, `options`, `row_target` (verbatim when declared); document under § Field semantics.
- [ ] **Step 6: Shared MUST/NEVER additions:** `MUST render declared columns/sample_rows/items/options as real DOM content per the kind mapping (no placeholder when content is declared)`; `MUST render the spec body only inside the collapsed spec panel`; `NEVER render a canonical spec-template heading as a widget`; `NEVER fabricate sample data not present in the screen source`.
- [ ] **Step 7: Commit.** `feat(contracts): walkthrough_renderer 1.2 — content synthesis, tamed auto-slug, spec panel`

---

### Task 3: Contract fixtures for the new shapes

**Files:**
- Modify: `skaileup/contracts/tests/elements_block_examples.md`

- [ ] **Step 1: Add valid examples** (3): `table-with-sample-rows` (columns + 2 aligned rows + `row_target`), `tabs-two-items` (one item with `target:`, one without), `input-with-options`.
- [ ] **Step 2: Add invalid examples** (4): `columns-on-list · reason: columns only valid on kind table`; `sample-row-length-mismatch · reason: each sample_rows entry must have len(columns) cells`; `options-on-button · reason: options only valid on kind input`; `items-bad-shape-on-tabs · reason: tabs items require label (target optional)`.
- [ ] **Step 3: Update the header count note** (building on the sibling plan's Task 3 counts) and mirror in `elements_block.md` § Validation; extend the cross-repo follow-up line: sister-repo `lab/validate-elements-block` must implement v0.3 before these pass.
- [ ] **Step 4: Commit.** `test(contracts): elements_block v0.3 fixtures (table/tabs/options)`

---

### Task 4: static-html renderer — reference implementation

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_b_static-html/SKILL.md`
- Modify: `skaileup/05_mockup-walkthrough/01_b_static-html/tests/fixtures/minimal/**` + `tests/expected/minimal/**`

**Interfaces:**
- Consumes: contract §§ from Tasks 1–2
- Produces: screen pages whose primary content is synthesized from `elements:` (real tables/tabs/lists/selects), spec demoted to collapsed panel; `metadata.version` → 0.3.0

- [ ] **Step 1: STEP 2 (Read inputs)** — parse/validate the v0.3 fields (`columns`, `sample_rows` with length check, `items` per-kind shape, `options`, `row_target`); implement the rewritten auto-slug source set (canonical-heading exclusion list verbatim from the contract; Actions label extraction with the quoted-token regex and verb-strip fallback).
- [ ] **Step 2: STEP 3 (Render screens)** — three changes: (a) render the new kind mappings (real `<table>` with thead/tbody, `<nav class="tabs">`, populated `<ul>`, `<select>`), with `row_target`/item `target:` resolved per the sibling plan's § Target resolution; (b) replace the `screen-body-prose` section with the contract's collapsed `<details class="spec-panel">` (open + `no_explicit_elements` warning when the screen has zero explicit elements); (c) drop the "elements grid above prose" layout — explicit elements render in declaration order as the page's main content flow (the authoring order is the layout order, top to bottom per the spec template's UI Elements convention).
- [ ] **Step 3: Inline CSS** — add `.spec-panel` (collapsed-by-default styling), `.tabs` (active/inactive), table styles for element-rendered tables (distinct from the prose-panel table styles); keep the auto-slug group visually distinct (existing dashed style).
- [ ] **Step 4: STEP 4b (manifest)** — echo the new fields; `schema_version = "1.2"`; `metadata.version` → 0.3.0.
- [ ] **Step 5: CHECKLIST additions:** `- [ ] No canonical spec heading appears as an el-region widget`, `- [ ] Every declared table renders sample_rows verbatim as <tbody> rows`, `- [ ] Spec body appears only inside <details class="spec-panel">`, `- [ ] No auto-slugged label exceeds 40 chars or contains an action sentence`.
- [ ] **Step 6: Fixture update.** Extend the minimal fixture's `login.md`/`register.md` (already touched by sibling Task 4) with one `table` element (columns + 2 sample rows) and one `input` with `options:`; add a fixture screen **without** `elements:` whose body uses the canonical headings — expected output shows the open spec panel, `no_explicit_elements` warning, and zero heading-widgets. Regenerate expected HTML + `manifest.json`.
- [ ] **Step 7: Verify** `tests/run_validator.sh` passes (structural checks; the new checks land in Task 5).
- [ ] **Step 8: Commit.** `feat(mockup-walkthrough): static-html synthesizes real UI from elements, spec panel demoted`

---

### Task 5: static-html validator — enforce the invariant

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_b_static-html/validator.py`

**Interfaces:**
- Produces: `check_content_fidelity(site, manifest, report)`; `SCHEMA_VERSION = "1.2"`

- [ ] **Step 1:** `SCHEMA_VERSION = "1.2"`.
- [ ] **Step 2: Add `check_content_fidelity`:** (a) for every manifest element with `sample_rows`, the rendered HTML node carrying its `data-spec-element` contains a `<tbody>` with exactly that many `<tr>`; (b) for every element with `items`/`options`, the node contains one `<li>`/`<option>`/tab entry per declared item; (c) no `data-spec-element` id in the canonical-heading slug set (`purpose`, `route`, `what-the-user-sees`, `wireframe`, `information-displayed`, `actions`, `situations`, `ui-elements`, `template-data`, `navigation`, `layout-areas`, `responsive-behaviour`) appears anywhere in the site; (d) every `screen/**/*.html` contains exactly one `<details class="spec-panel">` and no `<section class="screen-body-prose">`; (e) every screen with zero non-provisional elements has a matching `no_explicit_elements` warning in the manifest.
- [ ] **Step 3:** Run fixture mode against the Task 4 snapshots per `tests/run_validator.sh`; PASS required.
- [ ] **Step 4: Commit.** `feat(mockup-walkthrough): static-html validator enforces content fidelity`

---

### Task 6: astro renderer

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_c_astro/SKILL.md`
- Modify: `skaileup/05_mockup-walkthrough/01_c_astro/validator.py`
- Modify: `skaileup/05_mockup-walkthrough/01_c_astro/tests/fixtures/minimal/**` + `tests/expected/minimal/**`

- [ ] **Step 1: `specs.json` shape** — carry `columns`, `sample_rows`, `items`, `options`, `row_target`, plus a new per-screen `body_html` (rendered spec body for the panel — astro currently drops the body entirely; this is the panel's data source).
- [ ] **Step 2: STEP 2 (Read inputs)** — same parsing/validation/auto-slug rewrite as Task 4 Step 1.
- [ ] **Step 3: Scaffold templates:** extend `[...slug].astro`'s `renderElement` tagMap with the `table`/`tabs` rows and the populated `list`/`select` variants; append the `<details class="spec-panel"><Fragment set:html={screen.body_html} /></details>` block after the elements flow. Same **update-mode caveat** as the sibling plan's Task 6: scaffolded once — extend the `stale_scaffold` grep check to also look for the string `spec-panel`.
- [ ] **Step 4: Manifest** — `schema_version "1.2"`, echoed fields; `metadata.version` → 0.3.0; port the Task 5 checks into `validator.py`; update fixtures/snapshots (mirror Task 4 Step 6).
- [ ] **Step 5: Commit.** `feat(mockup-walkthrough): astro content synthesis + spec panel`

---

### Task 7: lit renderer

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_d_lit/SKILL.md`

- [ ] **Step 1:** `specs.json` + STEP 2: identical additions to Task 6 Steps 1–2 (including `body_html`).
- [ ] **Step 2: `screen-view.js` TAG map** — add `table`/`tabs` entries, populate `list` from `items`, `input` → select when `options`; render the spec panel (`<details>`, light DOM, `unsafeHTML(body_html)`) after the elements flow. Extend the `stale_scaffold` check (grep component source for `spec-panel`).
- [ ] **Step 3:** Manifest `"1.2"` + fields; `metadata.version` → 0.3.0; CHECKLIST gains Task 4 Step 5's four lines; same validator NOTE as the sibling plan (no validator.py on disk — spec the checks, don't author).
- [ ] **Step 4: Commit.** `feat(mockup-walkthrough): lit content synthesis + spec panel`

---

### Task 8: framework renderer + feedback-cluster coordination

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_e_framework/SKILL.md`
- Modify: `skaileup/07_mockup-feedback/01_annotate/tests/fixtures/minimal/**` (only if the check below finds hard-pins)

- [ ] **Step 1: framework SKILL.md** — `specs.json` shape + STEP 3 parsing (as Task 6 Steps 1–2); § Renderer Contract paragraph: route templates render the new kinds per the shared contract mapping and the spec panel from `body_html` (framework-native `<details>` or disclosure component acceptable iff the built static HTML contains the content server-side); `stale_scaffold` mirror; manifest `"1.2"`; `metadata.version` → 0.3.0; CHECKLIST + validator NOTE (no validator.py exists).
- [ ] **Step 2: Annotate compatibility check** (contract change policy, mirrors sibling Task 12): grep `07_mockup-feedback/01_annotate` for assumptions that annotatable nodes are leaf/simple elements — a `table` node now has rich children; the overlay selects on `data-spec-*` so expected result is no code change; refresh annotate fixtures to 1.2-shaped pages so the suite exercises table/tabs/panel DOM.
- [ ] **Step 3: Commit.** `feat(mockup-walkthrough): framework content synthesis + annotate 1.2 coordination`

---

### Task 9: upstream authoring — `experience-screens` MUST emit `elements:`

**Files:**
- Modify: `skaileup/03_experience/03_screens/SKILL.md`
- Modify: `skaileup/03_experience/03_screens/references/screen_spec_template.md`

New projects must never rely on the fallback. The block is authored where the prose is authored — in **STEP 4 (Write screen specs)**, as a new sub-step, exactly where the frontmatter OUTPUT template already lives (the skill's STEP 3/3b shell path gets the sibling plan's Task 10 Step 2 nav treatment; don't duplicate it here).

**Hard MUST, not a soft gate — justification:** the current state *is* the soft-gate outcome. `elements_block.md` says optional, nothing downstream pushes back, and the observed result is 0/43 adoption — the "intentionally wide safety net" became the only path. There is also no enforcement point for a warning at authoring time: the elements-block validator lives in the sister repo and is not wired into target projects, and the renderer runs many phases later (its `no_explicit_elements` warning from Task 2 is the render-time soft echo). So: **hard MUST at depth `medium`/`max`** — consistent with the existing `MUST include a ### Wireframe section … at depth medium or max` precedent — and exempt at `light`/`none` (where wireframes are skipped too and the fallback remains the honest net). The renderer never hard-fails either way (Global Constraints), so the MUST cannot brick a hand-written project.

- [ ] **Step 1: Add STEP 4b — Derive the `elements:` block** (between the spec writing and STEP 5's feedback loop): for each screen just written, derive frontmatter `elements:` from its own sections — every entry in `### UI Elements` and every interactive thing named in `## Actions` and `## Information Displayed` becomes an element with: short `label:` = the on-screen UI copy (the quoted token from the Actions bullet, e.g. "Aufnehmen" — NEVER the action sentence; sentence goes in `describes:`), correct `kind:` (tab bars → `tabs`, row lists → `table` or `list` with `items:`, filters with named options → `input` + `options:`), `data_entity:` from the screen's `data_entities[]`, `target:` per the sibling plan where the bullet names a destination, and `sample_rows`/`items` sourced from seed.json scenarios when present else from the wireframe's own example rows.
- [ ] **Step 2: Add to the MUST list:** `MUST declare an explicit elements: block on every screen spec at depth medium or max, covering every interactive or structural thing named in ### UI Elements, ## Actions, and ## Information Displayed (per contracts/elements_block.md § Content fidelity)`; `NEVER use an action sentence as an element label — labels are on-screen UI copy`.
- [ ] **Step 3: REFERENCES + CHECKLIST:** add `contracts/elements_block.md` to REFERENCES; CHECKLIST gains `- [ ] Every screen spec (depth medium+) has an elements: block whose labels are short UI copy` and `- [ ] Every table/list element with visible sample content in the wireframe carries sample_rows/items`.
- [ ] **Step 4: Update `references/screen_spec_template.md`** — the `### UI Elements` section gains: "Each entry here MUST be mirrored as a structured `elements:` frontmatter entry (see `contracts/elements_block.md`); the prose list is the human-readable view, the frontmatter is the machine-readable one" — same prose-keeps-truth pattern as the sibling plan's Actions/target rule. Add a frontmatter example with one `table` and one `tabs` element.
- [ ] **Step 5: Commit.** `feat(experience): screens skill authors explicit elements blocks (content fidelity)`

---

### Task 10: migration — ONE combined skill (fold sibling Task 11 into `mockup-walkthrough-migrate-elements`)

**Files:**
- Create: `skaileup/05_mockup-walkthrough/00_migrate-elements/SKILL.md`
- Modify: `skaile.yaml` (register `kind: skill`)
- Modify: `docs/devlog/2026-07-05-mockup-live-interconnect-plan.md` (Task 11: one-line supersession note)

**Decision: one combined migration skill, not two.** Verified against sibling Task 11's mechanism, not assumed:

1. **Same patch anchor, same files.** Both backfills emit `@@ frontmatter:elements @@` section-anchored diffs against the same 43 screen files. Two skills = two patch sets mutating one YAML block → `apply.py` ordering conflicts and double drift risk.
2. **Extraction is a superset, not a sibling.** Target extraction parses `## Actions` bullets for destinations; content extraction parses the same bullets for labels/kinds PLUS `## Information Displayed`, `## What the User Sees`, and the wireframe for columns/rows/tabs. Running target extraction separately would re-parse the same bullets and re-ask the human about the same elements.
3. **One human review round.** The review.md checklist is per-screen; a reviewer ticking `case_admission_list` wants to see the whole proposed block (labels + kinds + rows + targets) once, not twice in two sessions.
4. **Neither plan is implemented yet** (both `Status: planned`), so this is a rename/extension of a planned skill, not a breaking change to a shipped one.

- [ ] **Step 1: Author the SKILL.md** (name `mockup-walkthrough-migrate-elements`, `00_` slot — supersedes the sibling plan's `mockup-walkthrough-migrate-targets`; keep its Steps 1–5 mechanism verbatim as the navigation half). Per screen, one synthetic-session pass producing a complete proposed `elements:` block:
  1. **Inventory** (sibling Step 1 unchanged): `screen_id → (title, ## Route, stem words)` lookup.
  2. **Extract elements (LLM-assisted):** from `### UI Elements` (when present), `## Actions` (label = quoted token; kind inference per Task 2 Step 3's rules; `target:` resolution per sibling Step 2), `## Information Displayed` + `## Wireframe` (table candidates: entity rows with named fields → `columns:`; the wireframe's example rows → `sample_rows:`, verbatim, flagged low-confidence when reconstructed from ASCII), `## What the User Sees` (tab names in bold/quotes → `tabs` items). Shell: sibling Step 2's `## Navigation` → `kind: nav` handling unchanged.
  3. **Emit patches:** one `@@ frontmatter:elements @@` diff per screen with the full proposed block; `patches/<sid>.json` + `patches/<sid>.review.md`, low-confidence items (all ASCII-reconstructed sample rows, all unresolved targets) **unticked**.
  4. **CHECKPOINT:** human review → `mockup-feedback-apply` (audit trail for free).
  5. Re-run the project's renderer; confirm `no_explicit_elements` and `unresolved_target` warning counts drop; iterate on leftovers.
- [ ] **Step 2: MUST/NEVER** (sibling Step 2's set, plus): MUST propose short UI-copy labels only (quoted-token rule); MUST copy sample rows verbatim from the source (wireframe/Template Data) — NEVER invent patient names, dates, or values not present in the screen file; NEVER emit a partial block that would shadow auto-slug for the screen's remaining widgets (a partial explicit block suppresses nothing per the contract, but the review.md must state which described widgets were left auto-slugged and why).
- [ ] **Step 3: Register in `skaile.yaml`; no flow wiring** (same reasoning as sibling Step 3: one-time pass, `requires:` exactness would churn every tier flow).
- [ ] **Step 4: Amend the sibling plan doc** — one line under its Task 11 heading: `> Superseded by 2026-07-05-mockup-content-fidelity-plan.md Task 10: the target backfill ships inside the combined mockup-walkthrough-migrate-elements skill (same mechanism, wider extraction).`
- [ ] **Step 5: Commit.** `feat(mockup-walkthrough): migrate-elements skill (combined content + target backfill)`

---

### Task 11: docs — record the intent where the next author will look

**Files:**
- Modify: `docs/devlog/mockup-design.md`
- Modify: `skaileup/05_mockup-walkthrough/DOMAIN.md`

- [ ] **Step 1:** `mockup-design.md` § 6: extend the `elements:` example with a `table` (columns + sample_rows) entry and a dated note: v0.3 makes the block the content channel, the auto-slug fallback is a degradation path (this plan), and the authoring skill now requires the block at medium+. § 4: under the tier table, note that *all* tiers now render declared content (tables/tabs/lists) — the tier ladder differentiates *interactivity*, not *content presence*.
- [ ] **Step 2:** `DOMAIN.md`: one paragraph on the content model — the screen page is synthesized from `elements:`; the spec prose lives in the collapsed spec panel; sample data is authored fixture, never renderer-invented.
- [ ] **Step 3: Commit.** `docs(mockup): record content-fidelity model`

---

## Non-goals

- **Still static — no client-side interactivity.** Tab bars render with a static active state (no JS switching), tables don't sort/filter, selects don't filter lists. `sample_rows`/`items` are illustrative fixtures, not live data. Real state stays the `lit`/`astro`/`framework` tiers' fidelity job per `mockup-design.md` § 4 — the exact boundary the sibling plan drew for navigation ("clickable, no state"); this plan fixes *content presence*, not behaviour.
- **No renderer-invented sample data.** A table without `sample_rows` gets a skeleton row, never fabricated records; realistic data enters only through authoring (seed.json / wireframe) or the human-reviewed migration.
- **No per-row/per-cell annotation targets.** Table rows and list items live inside their element's single `data-spec-element` node — no new `data-spec-*` attributes (nav `items[]` ids from the sibling plan remain the pinned exception).
- **No layout/wireframe-geometry synthesis.** Elements render in declaration order in the content flow; reproducing the wireframe's 2-D zone layout (sidebar-vs-main placement per element) is out of scope — the shell handles chrome, declaration order handles the rest.
- **No text-tier or component-mockup changes** (legacy divergence + link-free-by-design, per the sibling plan's Task 9 and Non-goals).
- **No sister-repo edits** — `lab/validate-elements-block` v0.3 support is named as a follow-up (Tasks 1, 3), not executed here.
- **No flow YAML changes** — the migration skill stays outside `requires:` manifests.
- **No retro-fix of the CLINICO rendered HTML by hand** — CLINICO gets fixed by running Task 10's migration then re-rendering, never by editing `_concept/mockup-walkthrough/**` output.

## Self-review checklist (done while writing this plan)

- **Diagnosis verified, not assumed:** all seven claims re-checked in-file/in-project; the one material divergence found (astro/lit/framework drop the spec content entirely rather than dumping it) is folded into Task 2 Step 4 (`body_html` spec panel) and the Verified-diagnosis extension notes.
- **Sibling-plan coordination explicit:** version bumps stack (v0.2→v0.3, 1.1→1.2), `items:` reused rather than reinvented, migration folded into one skill with an amendment step for the sibling doc, task ordering matches its contract-first / static-html-first convention.
- **Fallback preserved, not deleted:** auto-slug survives as a genuinely degraded path (heading exclusion + label extraction) so hand-written screens without `elements:` still render — the hard requirement lands on the authoring skill, where the vacuum actually is.
- **No new annotation surface:** feedback cluster compatibility handled the same way the sibling plan handles it (Task 8 Step 2 annotate check; no new `data-spec-*`).
