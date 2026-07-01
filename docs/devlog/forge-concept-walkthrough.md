---
title: forge-concept walkthrough investigation
date: 2026-05-09
status: complete
related: docs/devlog/2026-05-07-skill-graph-migration.md (Task 3.0)
---

# forge-concept walkthrough investigation

## TL;DR

forge-concept does **not yet** have working overlay / annotation /
walkthrough code. What it does have is one detailed draft proposal —
`docs/devlog/2026-05-05-bidirectional-spec-visual-loop.md`
— authored by the same team that owns this catalog. The proposal pre-dates
this migration plan and defines exactly the conventions the
`mockup-feedback` skills (Phase 3, Tasks 3A–3B) should adopt.

Phase 3 is therefore **not greenfield**: the data-attribute schema,
overlay protocol, storage layout, and feedback-API shape are already
designed. What remains is execution against that spec.

---

## 1. Existing data attribute conventions

**Implementation status:** none. No `data-spec-*` markup exists in any
`*.ts` / `*.vue` / `*.html` under `forge-concept/app/`, `forge-concept/server/`, or
`forge-concept/_concept/`.

**Spec convention** (from `docs/devlog/2026-05-05-bidirectional-spec-visual-loop.md`
§ Component 1):

```ts
interface SpecRefAttributes {
  "data-spec-screen"?:  string;  // path under _concept/, e.g. "03_screens/auth/login"
  "data-spec-feature"?: string;  // path under _concept/, e.g. "02_features/01_user_auth/auth"
  "data-spec-journey"?: string;  // journey id, e.g. "onboarding"
  "data-spec-element":  string;  // stable id within artifact, e.g. "submit-button"
  "data-spec-route":    string;  // walkthrough route, e.g. "/screen/auth/login"
}
```

**Frontmatter `elements:` block** (spec § 6) is already this catalog's Task
2.0 contract — `contracts/elements_block.md` matches the spec's shape.

**Recommendation:** adopt the `data-spec-*` names verbatim. The contract
`contracts/elements_block.md` already aligns. No new conventions to
invent.

---

## 2. Existing overlay component

**Implementation status:** none. No `AnnotationOverlay.vue`, no overlay
JS bundle, no `data-spec-*` injection in mockup output. `HtmlPreview.vue`
exists but is a generic sandboxed iframe with no annotation logic.

**Spec convention** (§ Component 3):

- Vanilla DOM ES module, ~150 LOC, framework-agnostic.
- Loaded as the last `<script>` in every walkthrough page.
- Communicates with the parent (forge-concept) via `postMessage`.
- Existing `HtmlPreview.vue` already uses
  `sandbox="allow-scripts allow-same-origin"` — sufficient for
  `postMessage` with structured clones. **No CSP changes needed.**
- API:
  ```ts
  interface AnnotationOverlay {
    setMode(mode: "view" | "annotate"): void;
    addAnnotation(input: AnnotationInput): Annotation;
    onAnnotation(handler: (a: Annotation) => void): () => void;
  }
  ```
- Parent ↔ overlay protocol:
  ```ts
  type OverlayMessage =
    | { type: "overlay.ready"; route: string; manifest: SpecManifest }
    | { type: "overlay.annotation"; annotation: AnnotationInput }
    | { type: "overlay.navigate"; route: string };

  type ParentMessage =
    | { type: "parent.setMode"; mode: "view" | "annotate" }
    | { type: "parent.replay"; annotations: Annotation[] };
  ```

**Recommendation:** adopt the runtime + protocol exactly. Build the
overlay bundle as part of `mockup-feedback-annotate` (Task 3A); ship it
as a static `.js` next to the walkthrough output. forge-concept's
`HtmlPreview.vue` is the first consumer; a standalone CLI viewer can
be a second consumer of the same protocol.

---

## 3. Existing annotation capture mechanism

**Implementation status:** none. There is no `server/api/feedback/`
directory in forge-concept (only `mockups/`, `agent/`, `flows/`, etc.).

**Spec convention** (§ Component 4):

- Overlay → parent via `postMessage`.
- Parent forwards via `fetch` to `POST /api/feedback/index.post.ts`.
- Routes to add (proposed, not yet implemented):
  - `GET  /api/feedback`                            — list (filterable)
  - `POST /api/feedback`                            — create annotation
  - `PATCH /api/feedback/[id]`                      — update status
  - `GET  /api/feedback/route-by-screen/[screen]`   — per-screen rollup
  - `POST /api/feedback/process`                    — run feedback skill
- Annotation IDs are **ULIDs** (per spec).
- Domain gate: `requireDomainAccess(event, "skaileup-conceptualization")`.

**Recommendation:** the **producer side** (capture annotations into a
JSON file) lives in `mockup-feedback-annotate`. The **consumer side**
(the API + drawer UI) is forge-concept work, tracked separately in
that repo's spec. The mockup-feedback skill should write annotations
to a file path that forge-concept can serve and watch — see § 4 below
for the agreed layout.

---

## 4. Existing patch / feedback persistence

**Implementation status:** none. `_concept/_feedback/` does not exist
in any project I inspected.

**Spec convention** (§ Component 4 storage layout):

```
_concept/_feedback/
├── sessions/
│   └── <session-id>.json   ← { annotations: Annotation[], createdAt, createdBy }
├── patches/
│   └── <session-id>.json   ← { patches: FeedbackPatch[], proposedAt, status }
└── index.json              ← session list + status rollup
```

Key invariants from the spec:

- `_concept/_feedback/` is **gitignored** (review state is ephemeral).
- Applied patches always land in regular `_concept/` files via
  `saveConceptContent()` and are committed via existing git flow.
- Annotation has `status: "open" | "applied" | "dismissed"`.
- `category: "change" | "add" | "remove" | "question"` drives the
  patch-mapping rules in § Component 5:
  - `change`  → patch `## States` / `## Behavior` of artifact
  - `add`     → new bullet under the appropriate section
  - `remove`  → strikethrough / deletion
  - `question` → `## Open Questions` block (created if absent)
- Patches are **unified diffs** with `propose` vs `apply` modes.

**Reconciliation with this catalog's convention** — Phase 1 introduced
`_feedback/devlog.md` as the **permanent**, committed audit trail
(REFACTOR_MOCKUP.md § 5). The forge-concept spec and the catalog align
on this: ephemeral `sessions/` and `patches/` are gitignored, the
applied patches land in `_concept/` files, and `devlog.md` is the
permanent committed record. No conflict — both layers serve the same
goal at different timescales.

**Recommendation:** adopt the spec's `_concept/_feedback/sessions/` and
`_concept/_feedback/patches/` paths verbatim, plus `devlog.md` as the
catalog's existing permanent zone. Document the
gitignore expectation in the `mockup-feedback-annotate` skill output
contract.

---

## 5. Recommended alignment for the new mockup-feedback skills

### 5a. Adopt verbatim from the spec

| Surface                        | Source                                                      |
|--------------------------------|-------------------------------------------------------------|
| `data-spec-*` attribute names  | Spec § Component 1                                           |
| `elements:` frontmatter block  | Already in `contracts/elements_block.md` (Task 2.0)         |
| Overlay runtime + postMessage  | Spec § Component 3                                           |
| Storage layout (`sessions/`, `patches/`, `index.json`) | Spec § Component 4 |
| Annotation `category` enum + patch-mapping rules | Spec § Component 5                |
| `propose` vs `apply` mode      | Spec § Component 5; matches plan's triage/patch/apply split |
| `provisional` flag for inferred element IDs | Spec § Open Questions Q1            |
| Last-write-wins JSON per session ID | Spec § Open Questions Q5                              |
| Astro-default walkthrough builder | Spec § Open Questions Q3 — matches Task 3C priority      |
| Pixel-anchor fallback for unattributable annotations | Spec § Open Questions Q6        |

### 5b. Map spec → catalog skills

The spec defines **one** routing skill (`skaileup-concept-feedback`).
The migration plan splits it into **four** finer-grained skills. Keep
the four-way split — it composes better in flows and isolates
debug-paths. Mapping:

| Spec (single skill)            | Catalog (four skills)                |
|--------------------------------|--------------------------------------|
| capture                        | `mockup-feedback-annotate` (3A)     |
| group + classify               | `mockup-feedback-triage`  (3B)      |
| propose patches (dry-run)      | `mockup-feedback-patch`   (3B)      |
| apply patches + regen          | `mockup-feedback-apply`   (3B)      |

The spec's `mode: propose | apply` enum collapses into two skills
(`patch` and `apply`) — same semantics, finer granularity.

### 5c. Producer / consumer split

- **The skill is the producer** of the protocol (data-spec markup,
  overlay bundle, JSON file shapes, devlog format).
- **forge-concept is one consumer**: its `pages/walkthrough/index.vue`,
  `FeedbackDrawer.vue`, and `/api/feedback/*` routes are forge-concept's
  responsibility, tracked in its own spec.
- A **CLI / standalone HTML viewer** is a second possible consumer of
  the same protocol — keeps the skill independent of any single host.

### 5d. Open spec questions — reconciled with REFACTOR_MOCKUP.md § 11

Spec § Open Questions lists six items with recommended resolutions. The
catalog's REFACTOR_MOCKUP.md § 11 (Resolved decisions) covers most of the
same ground, sometimes with a refined answer. Where they diverge, **the
catalog's § 11 wins** (it's the catalog-side source of truth).

| Spec Q | Spec recommendation | Catalog § 11 | Reconciled |
|---|---|---|---|
| Q1 element ID stability | required `elements:` frontmatter; provisional IDs flagged | Row 3: hybrid — auto-slug provisional, **promote on first annotation** | Use catalog: auto-slug + promote-on-annotate |
| Q2 patch granularity | line-level diffs everywhere; Hocuspocus-aware queue | Row 4: **section-level for markdown, line-level for JSON** | Use catalog: section-level for `.md`, line-level for `.json` |
| Q3 walkthrough builder default | Astro by default | Row 2: **Astro** | Aligned |
| Q4 overlay packaging | bundle with skill v1, promote later | Row 7: **bundle inline v1; extract `@skaile/annotation-overlay` once API stabilizes** | Aligned (same plan, named package on extraction) |
| Q5 multi-user conflict | last-write-wins JSON per session ULID | Row 9: **out of scope for v1; last-write-wins JSON** | Aligned |
| Q6 unattributable annotations | pixel anchor + nearest `data-spec-route` → `## Open Questions` | (not in § 11) | Use spec |

**Catalog-only additions** the spec doesn't mention but the
mini-plans must respect:

- Row 8: `_feedback/` split — `sessions/` + `patches/` gitignored
  (per-developer evidence); **`applied/` + `devlog.md` committed**
  (audit trail + agent regeneration memory). The spec only describes
  the gitignored half.
- Row 10: skills emit `package.json` + `dev`/`build`/`preview` scripts
  rather than auto-running.
- Row 11: standard-app and complex-app **regenerate walkthrough after
  each `concept-slice` completes** (cumulative stakeholder review).
- Row 13: `mockup-feedback-archive` skill at 500 devlog entries → maps
  to Task 3E `lab/archive`.

These resolutions belong in Task 3A / 3B mini-plans as input contracts —
no further investigation needed.

### 5e. Practical implication for Phase 3 sequencing

Task 3A's mini-plan can be authored immediately (the runtime decision
is **vanilla DOM ES module** per spec § Component 3, settled). Task 3B
is similarly unblocked. Task 3.0's "still-open question" in
REFACTOR_MOCKUP.md § 12 is now resolved.

---

## Sources inspected

- `forge-concept/docs/superpowers/specs/2026-05-05-bidirectional-spec-visual-loop.md`
  (status: draft, author: Matthias Bolz) — primary input.
- `forge-concept/CLAUDE.md` — repo overview, two-root system, paths.
- `forge-concept/app/components/` — confirmed no `AnnotationOverlay.vue`
  or `FeedbackDrawer.vue` exist.
- `forge-concept/app/pages/` — confirmed no `walkthrough/` directory
  exists; only `mockups/index.vue`.
- `forge-concept/server/api/` — confirmed no `feedback/` directory
  exists; only `mockups/`, `agent/`, `flows/`, etc.
- `forge-concept/server/utils/concept-agent.ts` — only mention of
  "overlay" is in a code comment about skill resolution overlays
  (false positive).
- `forge-concept/_concept/` — confirmed no `_feedback/` or
  `07_walkthrough/` directories exist.
- `forge-concept/docs/wireframes.md` — schematic wireframes, no
  walkthrough/annotation surfaces.

The remaining grep hits were either generic mentions ("overlays",
"annotation" in unrelated skill recipes for primevue / tiptap / omp)
or one in `_concept/01_concept/ux_optimization.md` that referred to
"AI panel as persistent right panel (not overlay drawer)" — unrelated
to walkthrough annotation.
