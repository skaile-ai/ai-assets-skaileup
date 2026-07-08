# Mockup Live-Interconnect Implementation Plan (structured navigation targets)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** planned · verified against the CLINICO run (`/Users/matthias/devBench/CLINICO`) 2026-07-05 · extends `docs/devlog/mockup-design.md` and `docs/devlog/2F-walkthrough-mockup-static-html.md`

**Goal:** Make walkthrough mockups *live and interconnected* instead of page descriptions: give the `elements:` frontmatter schema a structured navigation-target field (`target:` on interactive elements, `items[].target` on `kind: nav`), have every renderer resolve it into a real relative `href` between screen pages, generate the persistent app-shell navigation from the actual screens list, and provide a concrete backfill path for already-authored projects whose navigation intent lives only in `## Actions` prose.

**Architecture:** The fix is a data-model extension, not a renderer bug-fix. Navigation intent already exists in screen sources as prose (`## Actions` bullets literally name their destinations, e.g. CLINICO's `11_intake/case_admission_list.md`: *Click "Aufnehmen" … → opens the admission form*), but `contracts/elements_block.md` has no field to carry it, so `contracts/walkthrough_renderer.md` § kind → DOM tag mapping pins `link` → `href="#"` placeholder and `button`/`nav` to unwired placeholders — and all renderers dutifully emit dead UI. The change flows contract-first: (1) `elements_block.md` v0.2 adds `target:`/`items:`, (2) `walkthrough_renderer.md` schema_version 1.1 adds the target-resolution rule, the generated app-shell nav, and the `unresolved_target` warning kind, (3) each renderer implements it (static-html is the reference implementation and goes first), (4) validators enforce the new invariant, (5) a migration skill turns existing `## Actions` prose into proposed `target:` values via the existing mockup-feedback patch/apply machinery (section-anchored `@@ frontmatter:elements @@` diffs + human review checklist). Journeys stay what they are — *guided tours* — but stop being the only way to move between screens; the pinned "no journey-nav injection into screen HTML" rule is narrowed to journey-*step* (Next/Prev) navigation only.

**Tech Stack:** Markdown contracts + skill DSL (per `skaileup/contracts/skill_grammar.md`), YAML frontmatter, Python 3.12 validators (stdlib + PyYAML), Astro/Lit/framework scaffold templates embedded in SKILL.md bodies.

## Verified diagnosis (read before editing — do not re-derive)

| # | Claim | Verified | Evidence |
|---|---|---|---|
| 1 | `elements:` schema has no destination field | ✅ | `skaileup/contracts/elements_block.md` § Schema — `id, kind, label, states, provisional, describes, data_entity, acceptance_refs` only |
| 2 | Contract pins dead interactivity | ✅ | `skaileup/contracts/walkthrough_renderer.md` § kind → DOM tag mapping (lines 40–54): `link` → `href="#"` placeholder; `button` → label only; `nav` → "placeholder list of links" |
| 3 | Only journey pages get real navigation | ✅ | static-html SKILL.md STEP 4 hardcodes `../screen/<group>/<name>.html` links; contract § Screen-in-multiple-journeys + NEVER (line 220) forbid journey-nav in screen HTML |
| 4 | Same gap in astro/lit/framework | ✅ | `01_c_astro/SKILL.md` line 444 and `01_d_lit/SKILL.md` line 417 hardcode `href="#"` in their scaffolded tag maps; `01_e_framework` delegates to the shared mapping — no target logic anywhere |
| 5 | Shell nav not data-driven | ✅ | CLINICO `shell.md` describes the sidebar in prose/ASCII only; rendered `screen/11_intake/case_admission_list.html` lines 401–409: every sidebar item is `<a href="#" class="nav-item">` |
| 6 | Contradicts design intent | ✅ | `docs/devlog/mockup-design.md` § 4 tier table: static-html interactivity = **"clickable, no state"** |
| 7 | Validators don't check link liveness | ✅ | `01_b_static-html/validator.py` checks manifest shape, data-spec-* attrs, journey-step `data-spec-screen` resolution, zero-build — nothing about screen-page hrefs |

**Where the diagnosis needed extension:**

- **`01_a_text` is not a read-only text renderer.** Its frontmatter says `mockup-walkthrough-text` but the body is the legacy MIGRATED "mock" skill (CDN-stack linked prototype writing to `_concept/mockups/`, *requiring* working `<a href>` links). It implements neither `walkthrough_renderer.md` nor the `elements:` block. Per `mockup-design.md` § 4 the text tier should be read-only ASCII. Task 9 handles the minimal alignment; a full rewrite is out of scope.
- **Component mockups don't need this.** `06_mockup-component/01_a_isolated-html` is single-component scope and explicitly `NEVER emit <link>/<script>` — no navigation model applies. `01_b_storybook/04_journeys` already *mandates* real in-UI navigation ("Sidebar/top bar nav items → navigate to corresponding screen", "NEVER add explicit Next/Prev buttons") — a precedent this plan brings to the walkthrough side, no storybook change needed.
- **The feedback loop has the patch machinery but no prose-to-target path.** `mockup-feedback-patch` already emits section-anchored `@@ frontmatter:elements @@` diffs and a `provisional-promotion` kind; `mockup-feedback-apply` (`apply.py`) applies them. Nothing today parses `## Actions` bullets into `target:` values — Task 11 builds the migration on top of exactly this machinery (synthetic session → patches → review.md → apply).
- **The elements-block schema validator lives in the sister repo** (`lab/validate-elements-block` in `ai-assets-skill-development`; only the fixtures live here). Task 3 updates the fixtures here and records the cross-repo follow-up.
- **`01_d_lit` and `01_e_framework` have no `validator.py` on disk** despite their SKILL.md STEP 8/9 referencing one. This plan specs their target checks in the SKILL.md CHECKLIST; authoring those validators stays a separate backlog item.
- **CLINICO screens carry a `## Route` section** (e.g. `/faelle`) alongside `## Actions` — the migration skill uses both as backfill signals.

## Global Constraints

- **Contract-first, additive-only.** `elements_block.md` goes v0.1 → v0.2 and `walkthrough_renderer.md` schema_version `"1.0"` → `"1.1"` with *additive* fields only — no renames, no removals. The feedback cluster pins `^1.0`, so 1.1 stays consumable; per the contract's change policy the bump still requires the coordinated `mockup-feedback-annotate` check in Task 12.
- **Soft-fail, never hard-fail, on unresolved targets.** A `target:` that doesn't resolve to an existing screen falls back to `href="#"` plus a `warnings[]` entry `kind: "unresolved_target"`. A `button` with *no* `target:` is legal and stays an inert `<button>` — "Submit"-style actions don't navigate.
- **No new `data-spec-*` attributes.** The pinned attribute table is untouched; target wiring changes `href`/DOM shape only, so `mockup-feedback-annotate` keeps resolving clicks identically.
- **Renderers stay read-only on sources.** All `target:` backfill goes through the migration skill (Task 11) with human review — never through a renderer run.
- **Journeys are narrowed, not removed.** The rule becomes: NEVER inject journey-*step* (Next/Prev, journey-specific) navigation into `screen/**/*.html`; screen-intrinsic `target:` links and the generated app-shell nav are *required*. Journey pages keep their sequenced tour role unchanged.
- **`target` identity form = `screen_id`** (path stem under `experience/screens/`, e.g. `11_intake/case_admission_form`), matching `data-spec-screen`, rendered filenames, and `screens[].screen_id` — one canonical id everywhere. Optional `#<element-id>` fragment allowed.
- **static-html is the reference implementation** — land it (Tasks 4–5) before astro/lit/framework; when behaviour is ambiguous its output is the tie-breaker (existing contract rule).
- **Green after every task:** `python3 skaileup/05_mockup-walkthrough/01_b_static-html/validator.py <fixture-site> --fixture minimal` passes wherever fixtures exist; `git diff --stat` limited to the task's Files list.
- **Commits:** conventional-commit style, each ending with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

---

## Reference: the new fields (decided)

**In-screen action — one element, one destination** (`kind: link | button | list | image | custom`):

```yaml
elements:
  - id: open-admission-form
    kind: button
    label: "Aufnehmen"
    states: [default]
    target: 11_intake/case_admission_form      # screen_id, optional "#<element-id>" fragment
```

**App-shell / persistent nav — one element, N destinations** (`kind: nav` only):

```yaml
elements:
  - id: sidebar-nav
    kind: nav
    label: "Hauptnavigation"
    states: [default]
    items:
      - id: nav-tasks            # optional; auto-slugged from label when absent
        label: "Aufgaben"
        target: 20_tasks/task_list
        icon: "✓"                # optional, cosmetic
```

**Why two related fields instead of one:** an action element *is* a single edge (`element → screen`), so a scalar `target:` keeps authoring and validation trivial. A nav element is a *collection* of edges rendered as one `<nav>` node with one stable `data-spec-element` id — flattening it into N sibling `link` elements would break the pinned kind → DOM mapping (`nav` → `<nav>`) and explode the elements list on every screen that embeds the shell. Same resolution rule for both (`items[].target` ≡ `target`), so renderers implement it once.

**Resolution rule (goes in the contract):** from `screen/<gA>/<nA>.html`, target `gB/nB` renders `href="../<gB>/<nB>.html"` (plus `#<fragment>` when present); from `index.html`, `href="screen/<gB>/<nB>.html"`. Resolvable iff `experience/screens/<target-sans-fragment>.md` exists in the rendered screen set.

---

### Task 1: `elements_block.md` v0.2 — add `target:` and `items:`

**Files:**
- Modify: `skaileup/contracts/elements_block.md`

**Interfaces:**
- Produces: schema fields `target` (string, optional, kinds `link|button|list|image|custom`), `items` (list, optional, kind `nav` only, entries `{id?, label, target, icon?}`)

- [ ] **Step 1: Bump the status header** from `v0.1 — open for extension` to `v0.2 — adds navigation targets (2026-07-05 live-interconnect plan)`.
- [ ] **Step 2: Extend § Schema** with the two optional fields (exact YAML comments naming the allowed kinds), and § Field reference with two rows:
  - `target` — string, no — `screen_id` (`<group>/<name>` stem under `experience/screens/`), optional `#<element-id>` fragment; MUST resolve to an existing screen at render time or the renderer records `unresolved_target`; only meaningful on `kind: link | button | list | image | custom` (schema-invalid on `input | text | region | form | media | nav`).
  - `items` — list, no — only on `kind: nav`; each entry has required `label` + `target` (same rules as `target`), optional `id` (kebab-case, auto-slugged from `label` when absent, unique within the element) and `icon`.
- [ ] **Step 3: Add a § Navigation targets section** documenting: the two-field design rationale (scalar edge vs. edge collection, as decided above), the resolution rule, the soft-fail contract ("absence of `target` on a button is not an error — not every action navigates"), and the fragment form.
- [ ] **Step 4: Update § Examples** — extend the promoted example with a `target:` button and add a `kind: nav` + `items:` example (use the shell sidebar shape).
- [ ] **Step 5: Update § Validation** to name the new invalid cases (target on non-interactive kind, items on non-nav kind, malformed screen_id) and note the sister-repo validator (`lab/validate-elements-block` in `ai-assets-skill-development`) must be extended to match — cross-repo follow-up, tracked in Task 3.
- [ ] **Step 6: Commit.** `feat(contracts): elements_block v0.2 — structured navigation targets`

---

### Task 2: `walkthrough_renderer.md` schema_version 1.1 — wire the mapping, generate the shell nav

**Files:**
- Modify: `skaileup/contracts/walkthrough_renderer.md`

**Interfaces:**
- Produces: revised kind → DOM mapping for `link`/`button`/`nav`; new § Target resolution; new § App-shell navigation; `warnings[].kind` + `unresolved_target`; manifest `screens[].elements[].target` + top-level `app_nav[]`; narrowed journey-nav NEVER; `schema_version: "1.1"`

- [ ] **Step 1: Bump** the header `schema_version: "1.0"` → `"1.1"` and extend the Change policy note: additive 1.1 change, feedback cluster pins `^1.0` (verified compatible in Task 12).
- [ ] **Step 2: Rewrite three rows of § kind → DOM tag mapping:**

| kind | rendered tag | notes |
|---|---|---|
| `button` | `<button>`, or `<a class="button">` when `target:` present | label as inner text; with `target:` the resolved relative href per § Target resolution |
| `link` | `<a>` | `href` = resolved `target:` per § Target resolution; `href="#"` **only** as the unresolved/absent fallback (with `unresolved_target` warning when declared-but-unresolved) |
| `nav` | `<nav>` | list of real links from `items[]` (or the generated app nav, § App-shell navigation); each item an `<a>` with resolved href and its own `data-spec-element` (item `id`, auto-slugged when absent) |

  `list` and `custom` gain one sentence each: when `target:` is present, the placeholder `<li>` / `<div>` content is wrapped in an `<a>` with the resolved href (list rows model "click a row → open detail").
- [ ] **Step 3: Add § Target resolution** — the resolution rule from the Reference block above, verbatim, plus: unresolved or dangling target → render `href="#"`, append `warnings[]` `{kind: "unresolved_target", screen_path, element_id, message: "target '<value>' does not resolve to a rendered screen"}`; absent target on `button`/`form`-like actions → no warning, inert element is intentional.
- [ ] **Step 4: Add § App-shell navigation** — the shell nav is *generated, not authored as prose*: (a) if `experience/screens/00_layout/shell.md` frontmatter has an `elements:` entry of `kind: nav` with `items:`, that entry is authoritative — render it in every screen page's shell wrapper with resolved hrefs; (b) otherwise derive a default nav: one link per rendered screen, grouped by `<group>` (group label = group dir name with `NN_` prefix stripped, underscores → spaces), element id `app-nav`, `data-spec-provisional="true"`, one `auto_slugged` warning. Record the result in manifest top-level `app_nav[]`. This logic lives **in the contract** (single definition), each renderer implements it in its shell/layout template — per-renderer divergence here is exactly what produced the CLINICO dead sidebar.
- [ ] **Step 5: Extend § Manifest schema** — `screens[].elements[].target` (optional string, echoed verbatim when declared) and top-level `app_nav: [{label, target, source}]` where `source` is `"experience/screens/00_layout/shell.md#elements/<id>"` or `"derived"`. Extend § Field semantics accordingly. `warnings[].kind` enum gains `unresolved_target`.
- [ ] **Step 6: Narrow the journey rule.** § Screen-in-multiple-journeys and the Shared NEVER line 220 become: "NEVER inject **journey-step** navigation (journey-specific Next/Prev or journey-ordering links) into `screen/**/*.html` — cross-journey continuation lives only in `journey/<id>.html`. Screen-intrinsic navigation (resolved `target:` hrefs, app-shell nav) is REQUIRED and is not journey-nav." Add one Shared MUST: `MUST resolve every declared target: into a relative href per § Target resolution (or emit unresolved_target and fall back to "#")`.
- [ ] **Step 7: Commit.** `feat(contracts): walkthrough_renderer 1.1 — live target resolution + generated app nav`

---

### Task 3: Contract fixtures for the new fields

**Files:**
- Modify: `skaileup/contracts/tests/elements_block_examples.md`

- [ ] **Step 1: Add valid examples** (2): `with-target` — a button with `target: 02_dashboard/home` and a link with fragment `target: 01_user_auth/login#email-input`; `nav-with-items` — a `kind: nav` element with two `items[]` (one with explicit `id`, one relying on auto-slug).
- [ ] **Step 2: Add invalid examples** (3): `target-on-input · reason: target only valid on link|button|list|image|custom`; `items-on-button · reason: items only valid on kind nav`; `malformed-target · reason: target must be a <group>/<name> screen_id stem` (use `target: /faelle` — an URL-style route, the exact mistake migration must catch).
- [ ] **Step 3: Update the header count note** ("3 valid, 3 invalid" → "5 valid, 6 invalid") and mirror the change in `elements_block.md` § Validation.
- [ ] **Step 4: Record the cross-repo follow-up** — add a line to the fixtures header: sister-repo `lab/validate-elements-block/validator.py` must implement the v0.2 rules before these fixtures pass; until then CI in *this* repo is unaffected (validator ships in `ai-assets-skill-development`).
- [ ] **Step 5: Commit.** `test(contracts): elements_block v0.2 fixtures (target/items)`

---

### Task 4: static-html renderer — reference implementation

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_b_static-html/SKILL.md`
- Modify: `skaileup/05_mockup-walkthrough/01_b_static-html/tests/fixtures/minimal/experience/screens/00_auth/login.md` (+ `register.md`)
- Modify: `skaileup/05_mockup-walkthrough/01_b_static-html/tests/expected/minimal/**` (all four HTML files + `manifest.json`)

**Interfaces:**
- Consumes: contract §§ from Tasks 1–2
- Produces: rendered screen pages whose declared targets are live `<a href>` links and whose shell carries the generated nav; `metadata.version` 0.1.0 → 0.2.0

- [ ] **Step 1: STEP 2 (Read inputs)** — extract `target` / `items` when parsing `elements[]`; validate per `elements_block.md` v0.2; build the rendered-screen-id set first so targets can be checked against it; also parse `00_layout/shell.md` frontmatter for an authoritative `kind: nav` entry (§ App-shell navigation case a).
- [ ] **Step 2: STEP 3 (Render screens)** — three changes, written into the step body: (a) elements with resolved `target:` render per the new mapping rows (button → `<a class="button">`, link → real href, list/custom rows wrapped); unresolved declared targets → `href="#"` + `unresolved_target` warning; (b) the shell wrapper renders the app nav per contract § App-shell navigation (authoritative `items:` or derived-per-screen-group default with `data-spec-provisional`), replacing today's prose-only shell treatment; (c) href computation uses the § Target resolution relative-path rule — no absolute paths.
- [ ] **Step 3: STEP 4b (manifest)** — emit `elements[].target` and top-level `app_nav[]`; `schema_version = "1.1"`; bump `metadata.version` to `0.2.0` (flows through `renderer_version`).
- [ ] **Step 4: CHECKLIST additions:** `- [ ] Every elements[] entry with a resolvable target renders an <a> whose href resolves to an existing rendered file`, `- [ ] No rendered screen contains href="#" on a node whose manifest element declares a resolved target`, `- [ ] Every screen page contains the app nav (<nav>) with one resolvable href per entry`.
- [ ] **Step 5: Fixture update.** Give `login.md` a `target:`-bearing element (`- id: go-register, kind: link, label: "Create account", states: [default], target: 00_auth/register`) and `register.md` the inverse; regenerate the four expected HTML files + `manifest.json` (schema_version 1.1, `app_nav` derived) by hand-editing the snapshots per the SKILL.md templates.
- [ ] **Step 6: Verify** `tests/run_validator.sh` still passes against the current validator (structural checks only — the new checks land in Task 5, which tightens it).
- [ ] **Step 7: Commit.** `feat(mockup-walkthrough): static-html renders live targets + generated app nav`

---

### Task 5: static-html validator — enforce the invariant

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_b_static-html/validator.py`

**Interfaces:**
- Produces: new checks `check_targets(site, manifest, report)` + extended `check_manifest_shape` (schema_version "1.1", `app_nav` key)

- [ ] **Step 1:** `SCHEMA_VERSION = "1.1"`; add `"app_nav"` to `TOP_LEVEL_KEYS`.
- [ ] **Step 2: Add `check_targets`:** for every `manifest.screens[].elements[]` with a `target` field: (a) the pre-`#` stem is in the rendered `screen_id` set **or** a matching `warnings[]` entry with `kind == "unresolved_target"` and the same `element_id` exists — else violation; (b) when resolvable, the rendered HTML node carrying that `data-spec-element` is (or is wrapped by) an `<a>` whose `href` — resolved relative to the page's directory — points at an existing file under the site root; (c) an `<a>` carrying a `data-spec-element` whose manifest entry declares a *resolved* target MUST NOT have `href="#"` (the "no orphan placeholder" check).
- [ ] **Step 3: Add app-nav check:** every `manifest.app_nav[]` entry's target resolves to a rendered screen file, and every `screen/**/*.html` contains at least one `<nav>` element (the shell nav) with ≥ 1 relative-href `<a>`.
- [ ] **Step 4:** run fixture mode against the Task 4 snapshots — `python3 validator.py tests/expected/minimal --fixture minimal --cwd tests/fixtures/minimal` style invocation per `tests/run_validator.sh`; PASS required.
- [ ] **Step 5: Commit.** `feat(mockup-walkthrough): static-html validator enforces resolvable targets`

---

### Task 6: astro renderer

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_c_astro/SKILL.md`
- Modify: `skaileup/05_mockup-walkthrough/01_c_astro/validator.py`
- Modify: `skaileup/05_mockup-walkthrough/01_c_astro/tests/fixtures/minimal/**` + `tests/expected/minimal/**` (mirror Task 4's fixture change)

**Interfaces:**
- Consumes: contract 1.1; `specs.json` gains `screens[].elements[].target`, `screens[].elements[].items`, top-level `app_nav[]`

- [ ] **Step 1: `specs.json` shape** — add `target` on element objects, `items` on nav elements, and top-level `app_nav[]` (derived at STEP 2 read time, same rules as the contract; specs.json carries it so the templates stay dumb).
- [ ] **Step 2: STEP 2 (Read inputs)** — same parsing/validation additions as static-html Task 4 Step 1, plus `unresolved_target` warning emission at derivation time (astro templates never see unresolved targets — they receive pre-resolved `href` strings; add `href` as a template-convenience field on elements/items that MUST NOT be copied to `manifest.json`, alongside `title`/`group`).
- [ ] **Step 3: Scaffold templates (init-only files):** in `[...slug].astro`'s `tagMap`, replace `link: '<a href="#" …'` (line 444) with `el.href ?? '#'` interpolation and give `button`/`list`/`custom` the same treatment; add a `Nav` block to `Shell.astro` that renders `specs.app_nav` (Shell imports specs.json). **Update-mode caveat (must be written into the SKILL.md):** these files are scaffolded once and never touched on update runs — projects scaffolded pre-0.2.0 keep dead links until re-scaffolded. Add an update-run check: if `[...slug].astro` does not contain the string `el.href`, append warning `kind: "stale_scaffold"` (astro-specific addition, document next to `stale_tailwind_config`) telling the user to delete the scaffold or port the template.
- [ ] **Step 4: Manifest step** — `schema_version "1.1"`, `elements[].target` + `app_nav[]` from the in-memory model (not specs.json); `metadata.version` → 0.2.0.
- [ ] **Step 5: validator.py** — port Task 5's `check_targets`/app-nav checks (share logic by copy, consistent with the two validators' existing sibling structure); update fixtures/snapshots.
- [ ] **Step 6: Commit.** `feat(mockup-walkthrough): astro renders live targets + app nav (stale_scaffold guard)`

---

### Task 7: lit renderer

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_d_lit/SKILL.md`

**Interfaces:**
- Consumes: contract 1.1; same `specs.json` additions as astro

- [ ] **Step 1: `specs.json` shape + STEP 2** — identical additions to Task 6 Steps 1–2 (pre-resolved `href` convenience field, `app_nav[]`, warnings at derivation).
- [ ] **Step 2: `screen-view.js` TAG map** (line 417 `href="#"`) — `link`/`button`/`list`/`custom` render `href=${el.href ?? '#'}`; add an `app-nav` render block (light DOM, from `specs.app_nav`) to the `<screen-view>` shell region. Same init-only caveat as astro: components are scaffolded once — add the `stale_scaffold` update-run warning (grep component source for `el.href`), documented beside `stale_token_css`.
- [ ] **Step 3: Manifest step** — `schema_version "1.1"` + new fields; `metadata.version` → 0.2.0; CHECKLIST gains the three target/app-nav lines from Task 4 Step 4.
- [ ] **Step 4: Record validator gap.** `mockup-walkthrough/lit/validator.py` is referenced by STEP 8 but does not exist on disk — add a one-line NOTE in STEP 8 that the validator, when authored, MUST include the Task 5 target checks; do not author it in this plan (pre-existing gap, tracked in the improvement backlog).
- [ ] **Step 5: Commit.** `feat(mockup-walkthrough): lit renders live targets + app nav`

---

### Task 8: framework renderer

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_e_framework/SKILL.md`

- [ ] **Step 1:** `specs.json` shape + STEP 3 (Read inputs): same additions as Task 6 Steps 1–2. The framework renderer delegates its DOM mapping to the shared contract, so most of the change arrives free via Task 2 — the SKILL.md needs: (a) one paragraph in § Renderer Contract stating targets are pre-resolved to `href` strings in `specs.json` and route templates interpolate them (framework link components — `next/link`, `NuxtLink`, SvelteKit `<a>` — are acceptable *as long as the built static HTML contains a plain resolvable `href`*, per the existing "data-spec-* server-side" invariant); (b) the root layout renders `specs.app_nav`; (c) `stale_scaffold` update-run warning mirroring astro/lit.
- [ ] **Step 2:** Manifest step: `schema_version "1.1"` + fields; `metadata.version` → 0.2.0; CHECKLIST additions; same validator NOTE as lit (no validator.py exists).
- [ ] **Step 3: Commit.** `feat(mockup-walkthrough): framework renders live targets + app nav`

---

### Task 9: text variant — minimal alignment + divergence flag

**Files:**
- Modify: `skaileup/05_mockup-walkthrough/01_a_text/SKILL.md`

The design-intent text tier (`mockup-design.md` § 4: build none, read-only) renders no HTML links, so *href* resolution does not apply — but the structured target is still valuable as **cross-references**. However, the file on disk is the legacy MIGRATED linked-prototype skill (writes `_concept/mockups/`, ignores `elements:` and the renderer contract entirely).

- [ ] **Step 1:** Add a `> **DIVERGENCE NOTE (2026-07-05):**` blockquote under the H1: this skill's body predates the walkthrough-renderer contract and does not implement it; the tier's intended shape is read-only per mockup-design.md § 4; full realignment is a separate backlog item (do NOT attempt it in this plan).
- [ ] **Step 2:** Add one contract-forward instruction to Phase 4 (Screen Pages): when a screen's `elements:` declares `target:` values (elements_block.md v0.2), render each as `→ opens: <screen_id>` next to the element (and, since this legacy variant *does* emit links, use them as the href source instead of guessing from prose).
- [ ] **Step 3: Commit.** `docs(mockup-walkthrough): text-variant divergence note + target cross-references`

---

### Task 10: upstream authoring — `experience-screens` emits targets

**Files:**
- Modify: `skaileup/03_experience/03_screens/SKILL.md`

New projects should never need migration: the skill that authors `## Actions` prose (its section template around line 235 includes `## Actions`) must author the structured field at the same time.

- [ ] **Step 1:** In the screen-authoring step, add: every `## Actions` bullet that names a destination screen MUST have a matching `elements:` entry with `target:` (the bullet's prose keeps the human-readable arrow form; the frontmatter carries the machine-readable edge). Every screen SHOULD declare its interactive elements explicitly rather than relying on auto-slug.
- [ ] **Step 2:** Shell authoring: when writing `00_layout/shell.md`, the `## Navigation` destination list MUST be mirrored as a `kind: nav` element with `items[].target` in the shell's frontmatter (contract § App-shell navigation case a).
- [ ] **Step 3:** Add both to the skill's MUST list and CHECKLIST; reference `contracts/elements_block.md` § Navigation targets.
- [ ] **Step 4: Commit.** `feat(experience): screens skill authors structured navigation targets`

---

### Task 11: migration skill — `mockup-walkthrough-migrate-targets`

**Files:**
- Create: `skaileup/05_mockup-walkthrough/00_migrate-targets/SKILL.md`
- Modify: `skaile.yaml` (register `kind: skill`)

**Interfaces:**
- Consumes: `experience/screens/**/*.md` (`## Actions` bullets, `## Route`, shell `## Navigation`), `mockup-feedback/schemas/patches.schema.json`
- Produces: `_concept/_feedback/patches/<sid>.json` + `<sid>.review.md` consumable by `mockup-feedback-apply` — the migration is a **synthetic feedback session**, reusing the existing section-anchored patch/apply machinery instead of inventing a second frontmatter-mutation path

This is the CLINICO path: dozens of screens with navigation intent only in prose. Concrete mechanism:

- [ ] **Step 1: Author the SKILL.md** (name `mockup-walkthrough-migrate-targets` — `00_` slot runs before the pick-one renderers; not numbered into the render alternatives). Steps:
  1. **Inventory:** glob screens (excl. `00_layout/`), build `screen_id → (title, ## Route value, filename-stem words)` lookup.
  2. **Extract candidate edges (LLM-assisted):** parse each screen's `## Actions` bullets; for arrow-form bullets (`… → opens/öffnet …`) resolve the named destination against the inventory (title match, route match, stem match — in that order); each resolution carries a confidence note. Shell: parse `## Navigation`'s ordered destination list the same way.
  3. **Emit patches:** for each screen with matches, one `@@ frontmatter:elements @@` section-anchored diff adding (or extending) `elements:` entries with `target:` (and the shell's `kind: nav` + `items:` block) — exactly the diff dialect `mockup-feedback-patch` documents and `apply.py` parses. Write `patches/<sid>.json` (schema-valid) + `patches/<sid>.review.md` with every low-confidence item **unticked**.
  4. **CHECKPOINT:** human reviews `review.md` (tick/untick/hand-edit), then runs `mockup-feedback-apply` — which also gives the devlog entry and `applied/<sid>.json` audit trail for free.
  5. Re-run the project's walkthrough renderer; confirm `unresolved_target` warning count in the fresh `manifest.json`, iterate on leftovers.
- [ ] **Step 2:** MUST/NEVER: MUST route all source mutations through mockup-feedback-apply; MUST leave unresolvable action bullets untouched (prose stays truth); NEVER guess a target below the stated confidence rules without leaving the review item unticked; NEVER edit rendered HTML.
- [ ] **Step 3:** Register in `skaile.yaml` (`kind: skill`). Do **not** wire into any flow — flows' `requires:` exactness would force churn across tier flows for a one-time pass; running it stays manual/orchestrator-routed. (Optional follow-up recorded in the skill body: add it as an optional entry node of the shared `mockup-feedback` sub-flow once the 2026-07 flow restructure lands.)
- [ ] **Step 4: Commit.** `feat(mockup-walkthrough): migrate-targets skill (Actions prose → target: backfill)`

---

### Task 12: feedback-cluster coordination (contract change policy)

**Files:**
- Modify: `skaileup/07_mockup-feedback/03_patch/SKILL.md`
- Modify: `skaileup/07_mockup-feedback/01_annotate/tests/fixtures/minimal/**` + `tests/expected/minimal/**` (only if Step 1 finds hard-pins)

The `walkthrough_renderer.md` change policy requires a coordinated `mockup-feedback-annotate` update on any schema bump.

- [ ] **Step 1: Verify annotate compatibility.** Grep `07_mockup-feedback/01_annotate` (overlay JS + validator + fixtures) for `schema_version` handling and any assumption that annotatable nodes have `href="#"` or that `<button>` is never `<a>`. Expected: overlay selects on `data-spec-*` only → no code change; fixtures embed rendered screen HTML → refresh them to 1.1-shaped pages (mirroring Task 4 snapshots) so the fixture suite exercises the new DOM.
- [ ] **Step 2: Extend `mockup-feedback-patch`** with a `target-promotion` path: when an annotation's body expresses navigation intent on an element without `target:` ("this should open X"), author an `@@ frontmatter:elements @@` diff adding `target:` — same template family as the existing `provisional-promotion` kind. One paragraph + one template block.
- [ ] **Step 3: Commit.** `feat(mockup-feedback): 1.1 coordination — annotate fixtures + target-promotion patches`

---

### Task 13: docs — record the intent where the next author will look

**Files:**
- Modify: `docs/devlog/mockup-design.md`
- Modify: `skaileup/05_mockup-walkthrough/DOMAIN.md`

- [ ] **Step 1:** `mockup-design.md` § 4: under the tier table add a dated note: "clickable" is realized by elements_block v0.2 `target:`/`items:` + walkthrough_renderer 1.1 target resolution and generated app-shell nav (this plan); § 6's `elements:` example gains a `target:` line.
- [ ] **Step 2:** `DOMAIN.md`: one paragraph on the navigation model (targets are screen-intrinsic; journeys are guided tours, not the transport layer).
- [ ] **Step 3: Commit.** `docs(mockup): record live-interconnect navigation model`

---

## Non-goals

- **No client-side state simulation** — real filtering, tab switching, form submission, scenario toggling stay the `lit`/`astro`/`framework` tiers' fidelity job per `mockup-design.md` § 4; `static-html` remains "clickable, **no state**". This plan fixes *clickable* only.
- **No conditional/role-based navigation** (e.g. CLINICO's "Sysadmin sees Administration") — `target:` is unconditional; visibility rules stay prose.
- **No journey-step injection into screens** — the narrowed NEVER stands; journeys remain the guided-tour layer.
- **No text-tier rewrite** (Task 9 flags the legacy divergence only) and **no component-mockup changes** (isolated-html is link-free by design; storybook already navigates through real UI).
- **No authoring of the missing lit/framework validators** (pre-existing gap; checks are spec'd in their SKILL.mds for when they land).
- **No sister-repo edits** — `lab/validate-elements-block` (ai-assets-skill-development) is named as a follow-up, not executed here.
- **No flow YAML changes** — the migration skill stays outside `requires:` manifests to avoid tier-flow churn.

## Self-review checklist (done while writing this plan)

- **Diagnosis verified, not assumed:** every claim in the table above was re-read in-file; the two divergences found (legacy text variant, storybook precedent) are folded into Tasks 9 and the Non-goals.
- **Contract-first ordering:** Tasks 1–3 (contracts + fixtures) precede all renderer tasks; static-html (4–5) precedes astro/lit/framework (6–8), matching the reference-implementation rule.
- **Pinned-contract discipline:** schema bump 1.0 → 1.1 with the mandated `mockup-feedback-annotate` coordination (Task 12); no new `data-spec-*` attributes anywhere.
- **Init-only scaffold trap handled:** astro/lit/framework update runs can't silently miss the new templates — `stale_scaffold` warnings added in Tasks 6–8.
- **Migration is concrete:** synthetic session → `@@ frontmatter:elements @@` patches → human-ticked review.md → existing `apply.py`; no new mutation machinery.
