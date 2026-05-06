# Refactor — Component Mocking vs. Application Mocking

**Status:** proposal · decisions applied · supersedes the unified `mockup/`
cluster in `SKILL_GRAPH.md`

**Decisions baked in (from review):**
- Naming: `component-mockup-*`, `walkthrough-mockup-*`, `mockup-feedback-*`
- Default walkthrough tier for `standard-app`: **Astro**
- Patch granularity: **section-level** for markdown, line-level for JSON
- File granularity: **matches the vertical slice** (one feature → one feature.md,
  one screen → one screen.md, one mockup variant per slice → one file)
- Bidirectional sync: **references + devlog combined** (see §5)

---

## 1. Why this refactor

The `SKILL_GRAPH.md` proposal currently treats four mockup tiers (`text`,
`static-html`, `lit`, `storybook`) as fidelity tiers of a single concern.
Session log evidence and the existing `skaileup-concept-storybook` domain
both argue these are **two distinct concerns** with different audiences,
contracts, and feedback loops:

| Aspect | Component mocking | Application mocking |
|---|---|---|
| **Audience** | Component author, designer, dev | Stakeholder, PM, non-technical reviewer |
| **Unit** | One component, all variants | One feature/journey across multiple screens |
| **Tool model** | Catalog (Storybook controls panel) | Routed pages (`/screen/...`, `/journey/...`) |
| **Fidelity progression** | low-fi → high-fi *for one component* | low-fi → high-fi *for a clickable flow* |
| **Feedback shape** | Knobs, controls, design review | Click-to-annotate on flows, patches to specs |
| **Output** | Storybook stories, isolated HTML | Walkthrough site (Astro/Nuxt/Next) |

Treating Storybook as a sibling of `text` and `static-html` collapses this
distinction. Storybook is **the** high-fi component tool — it's not a tier
peer of an ASCII wireframe; it's a different concern entirely.

---

## 2. Proposed shape

Three top-level domains, all flat-named with kebab-case:

```
component-mockup/                      ← components in isolation
  component-mockup-storybook           Storybook 8 (high-fi catalog)
  component-mockup-isolated-html       single component standalone HTML

walkthrough-mockup/                    ← clickable application
  walkthrough-mockup-text              ASCII wireframes (read-only)
  walkthrough-mockup-static-html       zero-build clickable HTML
  walkthrough-mockup-lit               Lit web components, embeddable
  walkthrough-mockup-astro             ★ DEFAULT for standard-app
  walkthrough-mockup-framework         stack-native (Next/Nuxt) via profile

mockup-feedback/                       ← annotation → patch loop
  mockup-feedback-annotate             inject overlay, capture clicks
  mockup-feedback-triage               classify annotations
  mockup-feedback-patch                propose section-level diffs
  mockup-feedback-apply                apply approved + append to devlog
```

### Why three top-level domains, not one with sub-clusters

1. The skaile CLI's catalog refs are `kind:name` (flat). Three short refs
   (`skill:walkthrough-mockup-astro`, `skill:component-mockup-storybook`)
   are clearer than nested `skill:mockup/walkthrough/astro`.
2. Each cluster has a different I/O contract — sibling status makes that
   visible at the catalog level.
3. Each cluster appears in a different position in tier flows.

### Why `mockup-feedback/` is its own cluster

- Same loop applies regardless of walkthrough tier (lit, astro, framework
  could all use the same feedback skills).
- Patch logic needs access to `_concept/` artifacts that the walkthrough
  renderer shouldn't have — separation = security boundary.
- The loop might eventually apply to *deployed* apps (annotate the staging
  URL, not just the mockup). Independence keeps that door open.

---

## 3. Component-mockup tiers

| Skill | Use when |
|---|---|
| `component-mockup-storybook` | Standard/complex apps with shared component library |
| `component-mockup-isolated-html` | mvp/simple apps where Storybook is overkill |

**`component-mockup-storybook`:**
- Reads `experience/components/*.md` and `design/tokens.json`
- Tech-stack aware: resolves addon configuration from
  `impl-architecture/templates/<stack>/`
- Produces `_concept/component-mockup/storybook/` (Storybook 8 site)
- Output is a buildable Storybook with `*.stories.ts` per component variant

**`component-mockup-isolated-html`:**
- Reads `experience/components/*.md` and `design/tokens.json`
- Produces `_concept/component-mockup/isolated-html/<component>.html`
- One file per component, no JS, no build, no framework
- Useful early in design before committing to a component library

---

## 4. Walkthrough-mockup tiers

All five share the **same input contract**:

```
input  = ( experience/screens/*.md
         , experience/journeys/stories.json
         , design/tokens.json
         , product-spec/features/*.md )

output = a routed site at _concept/walkthrough-mockup/<tier>/
         with /screen/<group>/<name> and /journey/<id> routes
         + every rendered DOM node carries data-spec-* attributes
```

| Tier | Build | Interactivity | Best for |
|---|---|---|---|
| `walkthrough-mockup-text` | none | read-only | mvp |
| `walkthrough-mockup-static-html` | none | clickable, no state | simple-app |
| `walkthrough-mockup-lit` | optional | full state, embeddable | standard-app (embedded) |
| `walkthrough-mockup-astro` | yes | islands, full nav | **standard-app default** |
| `walkthrough-mockup-framework` | yes | stack-native | complex-app |

Swapping fidelity = swap the renderer skill. The contract is identical, so
no other artifacts need to change.

---

## 5. Bidirectional sync — references AND devlog

> The annotation → patch loop has two sub-problems that don't overlap.
> Solving both with one mechanism produces awkwardness; using both
> mechanisms in their respective roles is robust.

### The two sub-problems

1. **Resolve target precisely.** When the user clicks a button and types
   "this should be on the right," we need to know exactly which DOM
   element they clicked, which screen owns it, which feature owns the
   screen, which artifact stores the spec. This is a **mechanical mapping**
   problem.

2. **Preserve intent.** The comment "this should be on the right" plus
   the session context (what else did they review? what did the agent
   decide?) is a **prose-shaped** thing that may inform future regenerations
   even after the immediate patch lands.

### Why neither alone works

**References-only** (the `data-spec-*` + `elements:` frontmatter approach
on its own): the patch lands, the comment is consumed, history is gone.
The next time the agent regenerates the screen, it has no record of
*why* the submit button moved. It might revert.

**Devlog-only** (write feedback as prose to a log, agent reads and
infers): the agent reads "user said the button should be on the right"
and has to grep multiple files to figure out which button. Brittle,
error-prone, slow. Doesn't scale past a handful of features.

### Best: both, in different roles

| Role | Mechanism | Lifetime | Format |
|---|---|---|---|
| Resolve target | `data-spec-*` HTML attrs + `elements:` frontmatter | permanent | HTML attrs / YAML |
| Capture annotation | `_feedback/sessions/<sid>.json` | per-session | JSON |
| Compute patch | section-level diff to target file | one-shot | text diff |
| Apply patch | direct file edit | atomic | (file change) |
| **Record intent** | append to `_feedback/devlog.md` | permanent | Markdown |
| **Regeneration memory** | agent reads recent devlog entries | permanent | Markdown |

**The flow:**

```
   walkthrough-mockup-astro renders <screen> with data-spec-* attrs
            │
            ▼
   user clicks element, types annotation in mockup-feedback-annotate
            │
            ▼
   _feedback/sessions/<sid>.json
     [{ target: { screen: "auth/login", element: "submit-button" },
        comment: "should be on the right",
        timestamp: "2026-05-06T19:24:00Z" }, ...]
            │
            ▼
   mockup-feedback-triage classifies → mockup-feedback-patch generates:
            │
            ▼
   experience/screens/auth/login.md  (proposed section-level diff)
     ─ change: "elements" section (move submit-button entry)
     ─ change: "layout notes" section (note rightward placement)
            │
            ▼
   mockup-feedback-apply:
     1. apply diff to login.md
     2. APPEND to _feedback/devlog.md:
        ## 2026-05-06 · session sid · astro walkthrough
        ### experience/screens/auth/login.md
        - submit-button: moved right per stakeholder review
          (target: submit-button, original comment: "should be on the right")
            │
            ▼
   next walkthrough regeneration:
     - reads experience/screens/auth/login.md (current spec)
     - reads _feedback/devlog.md last 30 days
     - knows submit-button is right-side AND why → doesn't revert
```

### Why section-level patches work for markdown

- Spec files are LLM-regenerated frequently. Line-level patches don't
  survive a regeneration cycle — the LLM rewords prose, line numbers
  shift.
- Section-level patches survive because **section headers are stable
  structural units**: `elements:`, `acceptance criteria`, `layout notes`,
  `data_entities`. The agent regenerates content within sections, not the
  section structure itself.
- For JSON files (`tokens.json`, `stories.json`) line-level is fine —
  these are machine-edited and structural.

### Why per-slice file granularity matches this

- One feature → one `features/<feature>.md`. One screen → one
  `screens/<group>/<screen>.md`. One mockup variant for that slice → one
  file under that variant's tier directory.
- Bounded scope per file = small section-diffs = low conflict risk.
- Vertical-slice work writes only the files for *its* slice — never
  touches other slices' files.
- No monolithic `everything.md` that all slices contend over.

### Devlog format

```markdown
# Feedback Devlog

## 2026-05-06 · session abc123 · astro walkthrough
**Reviewer:** stakeholder · **Cumulative scope:** auth, dashboard

### experience/screens/auth/login.md
- submit-button moved to right side per layout convention
  (target: submit-button, comment: "should be on the right")

### product-spec/features/01_auth/login.md
- added acceptance criterion: tab order email → password → submit
  (target: form, comment: "tab order matters for accessibility")

## 2026-05-04 · session xyz789 · static-html walkthrough
...
```

**Read strategy:** when an LLM regenerates an artifact, it reads:
1. The artifact itself (current truth)
2. The most recent N devlog entries that mention this artifact path
3. (NOT the full session JSONs — those are evidence, not memory)

**Why append-only:** changes are never deleted, only superseded. If a
future session reverts an earlier decision, that's just a new devlog
entry. The history stays intact for audit + future agent context.

**Old entries don't bloat regeneration context** because the agent
filters by mentioned-path: it only loads devlog entries that reference
the file being regenerated. With grep-style filtering, even a year of
feedback stays scoped per-artifact.

---

## 6. Frontmatter extension — the `elements:` block

For the references half of the sync to work, walkthrough renderers need
stable IDs. We add an optional `elements:` block to screen frontmatter:

```yaml
---
implements:
  - experience/features/01_user_auth/login.md
data_entities: [User]
layout: experience/screens/00_layout/shell.md
elements:                                  # NEW — optional
  - id: email-input
    kind: input
    label: "Email"
    states: [default, focus, error]
  - id: password-input
    kind: input
    label: "Password"
    states: [default, focus, error]
  - id: submit-button
    kind: button
    label: "Sign in"
    states: [default, loading, disabled, error]
last_updated: 2026-05-06
---
```

Walkthrough renderers MUST emit:
- `data-spec-screen="<screen-path>"` on screen root
- `data-spec-element="<element-id>"` on every annotatable node
- `data-spec-provisional="true"` when the ID was auto-slugged (no explicit
  `elements:` entry)

**Hybrid ID strategy** (auto-slug for fast iteration, promote to explicit
on first annotation):

1. Initial render: walkthrough auto-slugs IDs from labels/text. Marks all
   IDs `provisional`.
2. First annotation on a provisional element: `mockup-feedback-triage`
   prompts to promote the ID to explicit. The promoted ID gets written
   into the screen's `elements:` frontmatter via patch.
3. Subsequent renders use the promoted ID, no longer provisional. Future
   regeneration of the screen preserves the ID.

This avoids upfront tedium AND ID instability across regenerations.

---

## 7. Workspace zones — extension

```
   ┌────────────────────────────┬──────────┬───────────────────────────────┐
   │ Zone                       │ Lifetime │ Contents                      │
   ├────────────────────────────┼──────────┼───────────────────────────────┤
   │ _concept/                  │ permanent│ product spec (existing)       │
   │ _concept/component-mockup/ │ permanent│ Storybook + isolated HTML     │
   │ _concept/walkthrough-mockup│ permanent│ rendered walkthrough sites    │
   │   /<tier>/                 │          │   (regeneratable)             │
   ├────────────────────────────┼──────────┼───────────────────────────────┤
   │ _feedback/                 │ permanent│ NEW zone                      │
   │   sessions/<sid>.json      │ permanent│ raw annotations               │
   │   patches/<sid>.json       │ permanent│ proposed diffs                │
   │   applied/<sid>.json       │ permanent│ audit trail of applied patches│
   │   devlog.md                │ permanent│ append-only narrative log     │
   │                            │          │   (agent reads on regenerate) │
   ├────────────────────────────┼──────────┼───────────────────────────────┤
   │ _slice/                    │ per-slice│ scratch (existing)            │
   └────────────────────────────┴──────────┴───────────────────────────────┘
```

`_feedback/` lives outside `_slice/` because feedback is **product-level
evidence**, not slice-internal scratch. It's permanent and append-only.

---

## 8. Skills inventory — create / rename / move

### New skills (after refactor)

| Skill | Purpose |
|---|---|
| `component-mockup-storybook` | renamed from `skaileup-concept-storybook` (consolidates 6 sub-skills) |
| `component-mockup-isolated-html` | NEW — single-component standalone HTML |
| `walkthrough-mockup-text` | renamed from `skaileup-concept-mockup` |
| `walkthrough-mockup-static-html` | NEW — clickable static HTML site |
| `walkthrough-mockup-lit` | NEW — Lit web components site |
| `walkthrough-mockup-astro` | NEW — Astro islands site (default for standard-app) |
| `walkthrough-mockup-framework` | NEW — stack-native via profile |
| `mockup-feedback-annotate` | NEW — overlay injection + annotation capture |
| `mockup-feedback-triage` | NEW — classify annotations + promote provisional IDs |
| `mockup-feedback-patch` | NEW — section-level diffs |
| `mockup-feedback-apply` | NEW — apply diffs + append to devlog |

### Replaced

| Was | Now |
|---|---|
| `mockup/{text,static-html,lit,storybook}` (in current SKILL_GRAPH) | replaced by the three new clusters above |

---

## 9. Tier composition (replaces `mockup/*` block in SKILL_GRAPH)

```
                                        mvp  simple  standard  complex
                                        ────────────────────────────────
   component-mockup-storybook                          ✓         ✓
   component-mockup-isolated-html             ✓
   ───────────────────────────────────────────────────────────────────
   walkthrough-mockup-text             ✓
   walkthrough-mockup-static-html             ✓
   walkthrough-mockup-lit                              (alt)
   walkthrough-mockup-astro                            ✓ (default)
   walkthrough-mockup-framework                                  ✓
   ───────────────────────────────────────────────────────────────────
   mockup-feedback-annotate                            ✓         ✓
   mockup-feedback-triage                              ✓         ✓
   mockup-feedback-patch                               ✓         ✓
   mockup-feedback-apply                               ✓         ✓
```

Notes:

- **mvp**: text walkthrough only, no component catalog, no feedback. The
  whole thing is small enough that direct edits beat round-trip.
- **simple-app**: clickable static-html walkthrough + low-fi component
  catalog. No feedback yet — spec is small enough that direct edits win.
- **standard-app**: Astro walkthrough (default) + Storybook + full
  feedback loop. Feedback unlocks stakeholder review.
- **complex-app**: stack-native walkthrough that doubles as a real
  prototype + Storybook + feedback. Walkthrough may even ship to
  production.

---

## 10. Migration path

Five-step migration ordered by risk:

1. **Rename only.** `skaileup-concept-mockup` → `walkthrough-mockup-text/`,
   `skaileup-concept-storybook` → `component-mockup-storybook/`. No
   behavior change. Update SKILL_GRAPH.md and CONTRIBUTING.md references.

2. **Define `elements:` frontmatter + write validator.** Add optional
   schema; validator in `lab/`. Existing screens without it keep working.
   Renderers fall back to auto-slug + `data-spec-provisional="true"`.

3. **Build `walkthrough-mockup-static-html`** as the simplest new
   walkthrough variant. It validates the input contract for downstream
   tiers.

4. **Build `mockup-feedback-{annotate, triage, patch, apply}`** end-to-end
   on `static-html`. Includes:
   - `_feedback/` zone setup
   - `_feedback/devlog.md` append protocol
   - section-level diff generation for markdown
   - line-level for JSON
   - hybrid provisional-ID promotion

5. **Build `walkthrough-mockup-{lit, astro, framework}`** in any order.
   Each just has to honor the input contract and emit `data-spec-*`
   attributes.

Step 1 unblocks SKILL_GRAPH cleanup. Steps 2-5 are each their own slice.

---

## 11. Resolved decisions

| # | Question | Decision |
|---|---|---|
| 1 | Naming style | Flat kebab: `component-mockup-storybook`, `walkthrough-mockup-astro`, `mockup-feedback-annotate` |
| 2 | Default walkthrough for standard-app | **Astro** |
| 3 | Element ID strategy | **Hybrid** — auto-slug provisional, promote on first annotation |
| 4 | Patch granularity | **Section-level** for markdown, line-level for JSON |
| 5 | File granularity | **Match the vertical slice** — one feature/screen/mockup variant per file |
| 6 | Bidirectional sync | **References + devlog combined** — references resolve target, devlog records intent |
| 7 | Annotation overlay distribution | **Bundle inline** with each walkthrough skill for v1; extract `@skaile/annotation-overlay` npm package once the API stabilizes |
| 8 | `_feedback/` git policy | **`sessions/` + `patches/` gitignored** (private, per-developer evidence); **`applied/` + `devlog.md` committed** (audit trail + agent regeneration memory) |
| 9 | Multi-user collaboration | **Out of scope for v1.** Last-write-wins JSON on `_feedback/sessions/<sid>.json`. Revisit if needed. |
| 10 | Walkthrough deployability | Skills **emit `package.json` + `dev`/`build`/`preview` scripts** (so any developer can run it); the skills themselves don't auto-run |
| 11 | Walkthrough timing in tier flows | For standard-app and complex-app: **regenerate walkthrough after each `concept-slice` completes** (cumulative stakeholder review) |
| 12 | Component catalog feedback | **Walkthrough-only for v1.** Storybook keeps its own internal review/discuss surface; cross-linkage revisited if asked. |
| 13 | Devlog rollup / archival | **At 500 entries**, run a `mockup-feedback-archive` skill that summarizes older entries into `_feedback/devlog.archive/<YYYY-Q[1-4]>.md`; recent log keeps full detail |

---

## 12. Still missing — needs user input

1. **Existing forge-concept walkthrough work** — is there code in
   forge-concept this should align with or absorb? Need a pointer to the
   existing implementation (path / repo / commit) before step 3 of the
   migration begins. The contract above was designed assuming greenfield;
   if forge-concept already has working overlay or annotation code, the
   skill specs should match its conventions, not invent new ones.

---

## 13. Summary

**Three clusters replace the unified `mockup/`:**

```
                BEFORE                            AFTER
   mockup/                          component-mockup/
     text                             component-mockup-storybook
     static-html                      component-mockup-isolated-html
     lit                            walkthrough-mockup/
     storybook  ──────────►           walkthrough-mockup-text
                                      walkthrough-mockup-static-html
                                      walkthrough-mockup-lit
                                      walkthrough-mockup-astro       ← std default
                                      walkthrough-mockup-framework
                                    mockup-feedback/
                                      mockup-feedback-annotate
                                      mockup-feedback-triage
                                      mockup-feedback-patch
                                      mockup-feedback-apply
```

**Bidirectional sync uses both references and devlog**, in different
roles: references resolve *what* to patch, devlog records *why* it was
patched. Together they survive regeneration AND preserve intent —
neither alone does both.

**File granularity matches the vertical slice**: one feature/screen/
mockup-variant per file, so section-level patches stay small and
slice-isolated.

**`_feedback/devlog.md`** is the new permanent zone the agent reads on
every regeneration, filtered by mentioned-path so context stays small.
