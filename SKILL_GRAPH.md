# Skill Graph

Proposed organization for the catalog: two top-level groups (**Concept** and
**Implementation**) plus a small meta layer. Project complexity is **scoped by
the agent** at session start, then expressed as a flow + bundle pair. Both
sides — concept and implementation — support a **vertical-slice loop** for
larger apps where the whole product is too big to design or build in one pass.

---

## 1. Top-Level Layout

```
skaileup/                      base orchestrator: routes user, runs flows
  scope/                       NEW — interviews user, picks size tier
                               writes _concept/_meta/scope.yaml
flows/                         mvp · simple-app · standard-app · complex-app
                               + slice flows: concept-slice · impl-slice
bundles/                       matching bundles for every flow

CONCEPT
  concept/                     brief · goals · comparable
  design/                      brand-identity · tokens · voice · inspiration
  product-spec/                features · acceptance criteria
  experience/                  journeys · behaviors · screens · components
  component-mockup/            components in isolation (see REFACTOR_MOCKUP.md):
                               component-mockup-storybook
                               component-mockup-isolated-html
  walkthrough-mockup/          clickable application:
                               walkthrough-mockup-{text, static-html, lit,
                                                   astro★, framework}
                               (★ default for standard-app)
  mockup-feedback/             annotation → patch loop:
                               mockup-feedback-{annotate, triage, patch, apply}
                               + bidirectional sync via references + devlog
  concept-slice/               NEW — per-feature concept loop (big apps only):
                               brainstorm · align · scope-feature ·
                               design-feature  (writes one feature's portion
                               of product-spec + experience + walkthrough-mockup)

IMPLEMENTATION
  impl-architecture/           techstack · system · datamodel · templates/
  impl-plan/                   brainstorm · align · plan-vertical · supervised
                               (testing-strategy is part of plan output)
  impl-slice/                  per-slice impl loop — runs N times:
                               implement · test · recap · refactor · commit
                               (scratch handoffs in _slice/<id>/)
  impl-build/                  one-time / project-level only:
                               scaffold · foundation · infrastructure
                               migrate · seed · generate · docs
  impl-quality/                test-{plan,unit,integration,e2e}
                               eval-code · audit · ready · standards-*
                               debug-{self-verify, handoff}

META
  ops/                         review · sync · eval · add-feature
                               reverse-engineer · project-* (cross-cutting)
  lab/                         validate · judge · improve · learn
                               compile-validators · compile-bundle
  contracts/                   shared reference layer (every skill reads)
```

---

## 2. Pipeline Overview

```
                    user input  /  existing repo
                              │
                              ▼
                    ╔═════════════════════╗
                    ║    skaileup-base    ║
                    ╚══════════╤══════════╝
                               │
                               ▼
                    ┌──────────────────────────┐
                    │ skaileup/scope/          │   2-3 questions:
                    │   scope-project          │   how many features?
                    │                          │   single user / multi-user?
                    │   ► writes               │   integrations?
                    │     _concept/_meta/      │
                    │     scope.yaml           │   ► picks tier:
                    │     {tier, flow}         │     mvp · simple-app ·
                    └────────────┬─────────────┘     standard-app · complex-app
                                 │
                                 │  (user can override)
                                 ▼
                    ┌──────────────────────────────────┐
                    │  flows/<tier>.flow.yaml          │
                    │  bundles/<tier>.bundle.yaml      │  ◄ install only
                    └───────────────┬──────────────────┘    what tier needs
                                    │
              ┌─────────────────────┴──────────────────────────┐
              ▼                                                ▼
   ╔═══════════════════════════╗                  ╔══════════════════════════╗
   ║          CONCEPT          ║                  ║      IMPLEMENTATION      ║
   ╚═══════════════════════════╝                  ╚══════════════════════════╝
   ┌───────────────────────┐                      ┌──────────────────────────┐
   │ concept/              │                      │ impl-architecture/       │
   │ design/               │                      │ impl-plan/               │
   │ product-spec/         │                      │ impl-build/  one-time    │
   │ experience/           │                      ├──────────────────────────┤
   │ mockup/               │                      │ impl-slice/  PER-SLICE   │
   ├───────────────────────┤                      │   loop, big apps         │
   │ concept-slice/        │                      │   ↻                      │
   │   PER-SLICE loop,     │                      ├──────────────────────────┤
   │   big apps only       │                      │ impl-quality/            │
   │   ↻                   │                      └──────────────────────────┘
   └───────────────────────┘                               │
              │                                            │
              └──────────────────────┬─────────────────────┘
                                     ▼
                  ┌────────────────────────────────┐
                  │            META                │
                  │  ops/   review,sync,eval,...   │
                  │  lab/   validate,improve,...   │
                  │  contracts/   reference layer  │
                  └────────────────────────────────┘
```

**Two slice loops, same shape on both sides** — concept and implementation
each have their own per-feature iteration cluster. Big apps slice both;
small apps skip slicing on one or both sides.

---

## 3. Tier behavior — what the agent does at each size

Scope is the agent's first decision. The four tiers differ in whether they
slice the concept side, the implementation side, both, or neither.

```
              concept side             implementation side       supervision
              ─────────────            ─────────────────────     ──────────
mvp           linear, minimal          single impl-slice         autonomous
              (no design slicing)      (skip recap, refactor)

simple-app    linear, full             N × impl-slice            autonomous
              (one pass through all    (full slice loop)
              features upfront)

standard-app  linear high-level +      N × impl-slice            mostly autonomous,
              N × concept-slice        (full slice loop +        plan checkpoint
              (per-feature design)      recap mandatory)         per slice

complex-app   linear high-level +      N × impl-slice            HITL — supervised
              N × concept-slice        (full slice loop +        plan + brainstorm
              + project-overview       audit between slices)     + align per slice
```

**Decision rule** the `scope-project` skill follows (order matters — enterprise check sits above the multi-user/feature-count branch so that a multi-user enterprise app does not short-circuit to `standard-app`):

```
if features ≤ 1 and persistence trivial:        → mvp
elif features ≤ 5 and single-user:              → simple-app
elif multi-product or enterprise integration:   → complex-app
elif features ≤ 20 or multi-user:               → standard-app
else:                                           → complex-app   # explicit fall-through (large but unclassified)
```

`multi-product or enterprise integration` is satisfied when `signals.persistence == "external"` OR `len(signals.integrations) >= 2`.

User can override at any time by re-running `scope-project --tier=<name>`.

---

## 4. Concept Group — artifact flow

For **mvp** and **simple-app**, concept runs **linearly** (one pass, no slicing):

```
   user prompt
        │
        ▼
   ┌──────────────────┐                 ┌──────────────────┐
   │ concept/brief    │ ──► brief.md ──►│ design/brand-    │ ──► identity.md
   │  (+goals,        │     goals.md    │   visual         │     tokens.json
   │   comparable)    │                 │                  │
   └──────────────────┘                 └────────┬─────────┘
        │                                        │
        │      ┌──────────────────┐              │
        ├─────►│ experience/      │ ──► stories.json
        │      │   journeys       │
        │      └────────┬─────────┘
        │               │
        ▼               ▼
   ┌──────────────────────────────┐
   │ product-spec/features        │ ──► features/<NN>/*.md
   │   (reads brief + journeys)   │     (acceptance criteria,
   │                              │      data needs)
   └────────┬─────────────────────┘
            │
            ▼
   ┌──────────────────┐  ┌──────────────────┐
   │ experience/      │  │ experience/      │
   │   behaviors      │  │   screens        │ ──► screens/<NN>/*.md
   │   (optional)     │  │   (uses tokens)  │
   └──────────────────┘  └────────┬─────────┘
                                  │
                                  ▼   ┌─────────────────────────────┐
                                  └──►│ component-mockup-* +        │
                                      │ walkthrough-mockup-<tier>   │
                                      │ (one mockup variant per     │
                                      │  vertical slice; section-   │
                                      │  level patches via mockup-  │
                                      │  feedback ↻)                │
                                      └─────────────────────────────┘
```

See `REFACTOR_MOCKUP.md` for the full mockup-cluster design — three
clusters (component / walkthrough / feedback), the bidirectional sync
contract (references + devlog), and the per-slice file-granularity rule.

For **standard-app** and **complex-app**, concept runs in a **two-pass shape**:

```
   PASS 1 — high-level only (project-wide):
       brief + goals + comparable + brand + journeys
       (the "grand scheme" — features at a coarse level only)
            │
            ▼
   PASS 2 — for each feature, run concept-slice loop:
```

```
   pick next feature from product-spec/features/ (high-level)
            │
            ▼
   ┌──────────────────────────┐   writes _slice/concept/<id>/brainstorm.md
   │ concept-slice/brainstorm │   sparring on what this feature is
   └────────┬─────────────────┘   ───── /clear ─────
            ▼
   ┌──────────────────────────┐   writes _slice/concept/<id>/align.md
   │ concept-slice/align      │   ★ AI interviews user about this feature
   │   ★ surfaces edge cases, │   ★ acceptance criteria become explicit
   │     unstated rules       │
   └────────┬─────────────────┘   ───── /clear ─────
            ▼
   ┌──────────────────────────┐   writes _slice/concept/<id>/scope.md
   │ concept-slice/           │   what's IN, what's OUT for this feature
   │   scope-feature          │   ★ prevents scope creep mid-design
   └────────┬─────────────────┘   ───── /clear ─────
            ▼
   ┌──────────────────────────┐   appends to:
   │ concept-slice/           │     product-spec/features/<feature>.md
   │   design-feature         │     experience/screens/<feature>/*.md
   │                          │     mockup/<tier>/<feature>.*
   │                          │     datamodel: only this feature's entities
   └────────┬─────────────────┘
            │
            └────────► hand off to impl-slice (or loop to next feature)
```

**Why this shape:** instead of designing all 20 features upfront (and
discovering halfway through that feature 3 changes feature 1's screens),
big apps design one feature at a time, *immediately* hand it to
implementation, and learn from delivery before designing the next.

**Per-screen card pattern** — every screen carries its own mockup variants:

```
   experience/screens/login.md                          ← screen spec (single source)
   _concept/walkthrough-mockup/text/login.txt           ← ASCII wireframe
   _concept/walkthrough-mockup/static-html/login.html   ← zero-build HTML
   _concept/walkthrough-mockup/lit/login.ts             ← Lit web component
   _concept/walkthrough-mockup/astro/login.astro        ← Astro page (default tier)
   _concept/component-mockup/storybook/Login.stories.ts ← Storybook entry

   shared filename stem ⇒ traceability is mechanical
   data-spec-screen + data-spec-element on rendered DOM ⇒ feedback loop hooks
```

---

## 5. Implementation Group — orchestration

The implementation side has **two phases**: a one-time **project setup** and a
repeating **per-slice loop**. The slice loop is where vertical slicing happens
— each pass cuts UI + logic + data for one feature, with context resets
between phases backed by scratch markdowns in `_slice/impl/<id>/`.

### 5.1 Project setup (runs once)

```
   concept frozen (features + screens + journeys + tokens)
            │
            ▼
   ┌──────────────────────────┐
   │ impl-architecture/       │  reads features + techstack
   │   techstack-decide       │  → architecture.md, model.json,
   │   templates/<stack>/     │    seed.json, feature_map.json
   │   system                 │
   │   datamodel              │  templates/<stack>/ exposes the same
   └────────┬─────────────────┘  contract used by every impl-build/* skill:
            │                     scaffold_command, build_command,
            ▼                     package_manager, migrate_tool, ...
   ┌──────────────────────────┐
   │ impl-build/   ONE-TIME   │  reads templates/<stack>/
   │   scaffold ──┐           │
   │   foundation ┘           │  Project-level only — these never run
   │   infrastructure         │  again unless the stack changes.
   │   migrate · seed         │
   │   generate (PostXL only) │
   └──────────────────────────┘
```

### 5.2 Per-slice impl loop (runs once per feature, repeats N times)

```
   pick next feature (from product-spec, or just-produced concept-slice)
            │
            ▼
   ┌──────────────────────────┐   writes _slice/impl/<id>/brainstorm.md
   │ impl-plan/brainstorm     │   sparring · multi-method · idea space
   └────────┬─────────────────┘   ───── /clear ─────
            ▼
   ┌──────────────────────────┐   writes _slice/impl/<id>/align.md
   │ impl-plan/align          │   AI interviews user (grill-me style)
   │   ★ shared understanding │   ★ surfaces unstated assumptions
   └────────┬─────────────────┘   ───── /clear ─────
            ▼
   ┌──────────────────────────┐   writes _slice/impl/<id>/plan.md
   │ impl-plan/plan-vertical  │   ★ vertical decomposition
   │   ★ trims AI from        │     UI + logic + data for this slice
   │     horizontal default   │   ★ defines testing strategy
   └────────┬─────────────────┘   ───── /clear ─────
            ▼
   ┌──────────────────────────┐   reads plan.md
   │ impl-slice/implement     │   codes the slice end-to-end
   │   (page + logic +        │   verifies against testing strategy
   │    schema if needed)     │   from plan
   └────────┬─────────────────┘
            ▼
   ┌──────────────────────────┐   short feedback loops on usability:
   │ impl-slice/test          │   too many buttons? too much text?
   │  (NOT impl-quality/test) │   does it feel awkward to use?
   └────────┬─────────────────┘   ────────────
            ▼
   ┌──────────────────────────┐   writes _slice/impl/<id>/recap.md
   │ impl-slice/recap         │   ★ MANDATORY — explain the flow
   │   ★ produces a diagram   │     so the user keeps the overview
   │   ★ skipping it = losing │     after 5+ iterations
   │     decision authority   │
   └────────┬─────────────────┘
            ▼
   ┌──────────────────────────┐   ★ AI defaults to ADDING complexity
   │ impl-slice/refactor      │     so refactor is FORCED, not optional
   │   ★ smallest improvement?│   "could a new dev follow this without
   │   ★ preserve behavior,   │    mental jumps?"
   │     improve structure    │
   └────────┬─────────────────┘
            ▼
   ┌──────────────────────────┐   atomic commits
   │ impl-slice/commit        │   ★ deletes _slice/impl/<id>/ scratch
   │                          │     (truth lives in code; stale planning
   │                          │      docs confuse future iterations)
   └────────┬─────────────────┘
            │
            └────────► loop back to "pick next feature"

   ─── if stuck mid-slice ──►  impl-quality/debug/self-verify  or
                               impl-quality/debug/handoff
```

### 5.3 Quality gates (run between slices, or at release)

```
   ┌──────────────────────────┐
   │ impl-quality/            │
   │   test-plan              │   defines test inventory
   │   test-unit              │
   │   test-integration       │
   │   test-e2e (← stories)   │
   │   eval-code              │   iron_laws + golden_principles
   │   audit                  │   full review
   │   ready                  │   release gate
   │   standards-{discover,   │
   │     inject, sync}        │
   │   debug/                 │   ───────────────────
   │     self-verify          │   "let AI figure out HOW to verify
   │                          │    this is fixed" — frees user from
   │                          │    being the test loop
   │     handoff              │   "describe state + tried-things
   │                          │    for the next agent" — pair with
   │                          │    a /clear and new chat
   └──────────────────────────┘
```

---

## 6. Flows × Bundles (tier-named)

Each flow is paired with a bundle of identical name. The bundle lists exactly
the skills the flow runs — no more, no less.

```
$ skaile add bundle:simple-app          # install skills the flow needs
$ skaile run flow:simple-app            # execute the flow
```

```
flows/                                              bundles/
├── concept-slice.flow.yaml   ◄── pair ──►        ├── concept-slice.bundle.yaml
│                                                  │   per-feature concept loop
├── impl-slice.flow.yaml      ◄── pair ──►        ├── impl-slice.bundle.yaml
│                                                  │   per-feature impl loop
├── mvp.flow.yaml             ◄── pair ──►        ├── mvp.bundle.yaml
├── simple-app.flow.yaml      ◄── pair ──►        ├── simple-app.bundle.yaml
├── standard-app.flow.yaml    ◄── pair ──►        ├── standard-app.bundle.yaml
├── complex-app.flow.yaml     ◄── pair ──►        ├── complex-app.bundle.yaml
└── custom.flow.yaml          ◄── pair ──►        └── custom.bundle.yaml
```

The two slice flows are **building blocks**. Tier flows compose them:

```
mvp.flow.yaml:
   scope-project ─► linear concept ─► impl-build/scaffold ─►
   impl-slice (1 iteration, no recap, no refactor) ─► done

simple-app.flow.yaml:
   scope-project ─► linear concept ─► impl-build setup ─►
   loop: impl-slice ─► done (when all features built)

standard-app.flow.yaml:
   scope-project ─► high-level concept (brief, brand, journeys) ─►
   impl-build setup ─►
   loop: concept-slice ─► impl-slice ─► done

complex-app.flow.yaml:
   scope-project ─► high-level concept ─► project-overview ─►
   impl-build setup ─►
   loop: concept-slice ─► impl-slice (supervised plan) ─►
        impl-quality/audit (every slice) ─► done
```

### Tier composition

```
                            mvp  simple  standard  complex
                            ────────────────────────────────
   skaileup/scope/scope     ✓    ✓       ✓         ✓
   ───────────────────────────────────────────────────────
   concept/brief            ✓    ✓       ✓         ✓
   concept/goals                         ✓         ✓
   concept/comparable                    ✓         ✓
   design/brand-visual           ✓       ✓         ✓
   design/brand-voice                              ✓
   design/inspiration                    ✓         ✓
   product-spec/features    ✓    ✓       ✓         ✓
   experience/journeys           ✓       ✓         ✓
   experience/behaviors                  (opt)     ✓
   experience/screens            ✓       ✓         ✓
   experience/components                 ✓         ✓
   walkthrough-mockup-text      ✓
   walkthrough-mockup-static-html      ✓
   walkthrough-mockup-lit                          (alt for embedded)
   walkthrough-mockup-astro                        ✓ (default)
   walkthrough-mockup-framework                                    ✓
   component-mockup-isolated-html      ✓
   component-mockup-storybook                      ✓               ✓
   mockup-feedback-annotate                        ✓               ✓
   mockup-feedback-triage                          ✓               ✓
   mockup-feedback-patch                           ✓               ✓
   mockup-feedback-apply                           ✓               ✓
   ───────────────────────────────────────────────────────
   concept-slice/brainstorm                        ✓
   concept-slice/align                   ✓         ✓
   concept-slice/scope-feature           ✓         ✓
   concept-slice/design-feature          ✓         ✓
   ───────────────────────────────────────────────────────
   impl-arch/techstack      ✓    ✓       ✓         ✓
   impl-arch/templates-select ✓  ✓       ✓         ✓   ← cluster selector (Phase 3)
                                                          picks one of impl-arch/templates/template-{postxl,nextjs-radix,
                                                          nextjs-shadcn,nuxt-minimal,nuxt-primevue,nuxt-ui,sveltekit-minimal}
   impl-arch/system                      ✓         ✓
   impl-arch/datamodel           ✓       ✓         ✓
   impl-plan/brainstorm                  ✓         ✓
   impl-plan/align               ✓       ✓         ✓
   impl-plan/plan-vertical  ✓    ✓       ✓         ✓
   impl-plan/supervised                            ✓
   impl-build/scaffold      ✓    ✓       ✓         ✓
   impl-build/foundation         ✓       ✓         ✓
   impl-build/infra                      (opt)     ✓
   impl-build/migrate            ✓       ✓         ✓
   impl-build/seed               ✓       ✓         ✓
   impl-build/docs               ✓       ✓         ✓
   impl-slice/implement     ✓    ✓       ✓         ✓
   impl-slice/test               ✓       ✓         ✓
   impl-slice/recap              ✓       ✓         ✓
   impl-slice/refactor                   ✓         ✓
   impl-slice/commit        ✓    ✓       ✓         ✓
   ───────────────────────────────────────────────────────
   impl-quality/unit        ✓    ✓       ✓         ✓
   impl-quality/integ.                   ✓         ✓
   impl-quality/e2e              ✓       ✓         ✓
   impl-quality/eval-code                          ✓
   impl-quality/audit                              ✓
   impl-quality/ready                    ✓         ✓
   impl-quality/debug/* (on demand — invoked when stuck)
   ───────────────────────────────────────────────────────
   ops/review                            ✓         ✓
   ops/sync                              ✓         ✓
   ops/project-*                                   ✓
```

Bundles inherit: `simple-app` includes `mvp`, `standard-app` includes
`simple-app`, `complex-app` includes `standard-app`. Each bundle file
lists only its *additions*.

### Bundle-from-flow generation

A `lab/compile-bundle` skill walks a flow's node graph and emits the matching
`<name>.bundle.yaml`. Run on every flow change to prevent drift between what
the flow executes and what the bundle installs.

---

## 7. Workspace Zones — three lifetimes

The slice loops only work if scratch handoffs don't pollute permanent state.
Three filesystem zones with distinct lifetimes:

```
   ┌─────────────────────────┬───────────┬──────────────────────────────┐
   │ Zone                    │ Lifetime  │ Contents                     │
   ├─────────────────────────┼───────────┼──────────────────────────────┤
   │ _concept/               │ permanent │ Product spec — features,     │
   │                         │           │ screens, datamodel, brand    │
   │ _concept/_meta/         │ permanent │ scope.yaml (chosen tier)     │
   │ _implementation/        │ permanent │ PLANS.md, progress.json,     │
   │                         │           │ decisions.md                 │
   ├─────────────────────────┼───────────┼──────────────────────────────┤
   │ _slice/concept/<id>/    │ per-slice │ concept-slice scratch:       │
   │                         │ (deleted) │   brainstorm.md align.md     │
   │                         │           │   scope.md                   │
   │                         │           │ ► deleted by concept-slice/  │
   │                         │           │   design-feature on commit   │
   ├─────────────────────────┼───────────┼──────────────────────────────┤
   │ _slice/impl/<id>/       │ per-slice │ impl-slice scratch:          │
   │                         │ (deleted) │   brainstorm.md align.md     │
   │                         │           │   plan.md recap.md           │
   │                         │           │ ► deleted by impl-slice/     │
   │                         │           │   commit                     │
   ├─────────────────────────┼───────────┼──────────────────────────────┤
   │ _feedback/              │ permanent │ mockup-feedback loop state — │
   │   sessions/<sid>.json   │ gitignore │ raw annotations              │
   │   patches/<sid>.json    │ gitignore │ proposed diffs               │
   │   applied/<sid>.json    │ committed │ audit trail of applied       │
   │   devlog.md             │ committed │ append-only narrative log    │
   │                         │           │ (agent reads on regenerate,  │
   │                         │           │  filtered by mentioned-path) │
   │   devlog.archive/       │ committed │ rollups every 500 entries    │
   └─────────────────────────┴───────────┴──────────────────────────────┘
```

**Why scratch is deleted on commit:** truth lives in code (impl-slice) or in
`_concept/` artifacts (concept-slice) after a slice ships. Stale planning
docs in the working tree confuse future AI iterations. Previous slice docs
survive in git history.

**Why context resets are safe:** every slice phase reads from the prior
phase's scratch file rather than from chat history. After each phase, the
user runs `/clear` (or starts a new chat) — the next phase loads the handoff
file and continues. The Dumb Zone (~100k tokens for most agents) is avoided
because no single phase carries the whole slice in context.

---

## 8. Cross-Cutting (Meta layer)

```
   ops/                            ← operates on artifacts
     review            audit a frozen concept
     sync              repair broken cross-references
     eval-concept      verdict: pass / needs_resolution / fail
     add-feature       cascade a new feature through stories→features→screens→data
     reverse-engineer  bootstrap _concept/ from existing code
     project-overview  multi-product summary
     project-subsystem-map
     project-integration
     project-review

   lab/                            ← operates on skills themselves
     validate          Docker-isolated test runs
     judge             LLM-scored quality
     improve           mutated variants, iteration loop
     learn             real-world observations → patterns
     report            structured trends across runs
     compile-validators (MUST/NEVER/CHECKLIST → validator.py)
     compile-bundle     (flow.yaml → bundle.yaml)

   contracts/                      ← reference layer (every skill reads)
     concept_structure   canonical _concept/ + _implementation/ paths
     iron_laws           non-negotiable cross-cutting constraints
     golden_principles   naming + modeling discipline
     semantic_types      stack-independent data types
     feedback_loop       bidirectional cross-reference protocol
     frontmatter         YAML field requirements
     plans               PLANS.md structure
     seed_data           scenario format
     acceptance_criteria EARS format
     wireframe_conv.     ASCII wireframe vocabulary
     skill_grammar       MUST/NEVER/STEP DSL
     agent_patterns      communication style
```

---

## 9. Migration map (current → proposed)

| Current domain / skill | Proposed location |
|---|---|
| `skaileup` (base) | `skaileup/` (gains a new `scope/` cluster) |
| `skaileup-grounding` | `concept/grounding/` (keeps onboard, research, seeds together — Phase 1 conservative; future Phase may promote `onboard/` to `concept/onboard/` once usage patterns are clearer) |
| `skaileup-discovery` | split: brief→`concept/`, brand-*→`design/` |
| `skaileup-experience` | split: features→`product-spec/`, journeys+behaviors+screens+components→`experience/` |
| `skaileup-architecture` | `impl-architecture/{techstack,system,templates}` |
| `skaileup-datamodel` | `impl-architecture/datamodel/` |
| `skaileup-concept-mockup` | `walkthrough-mockup-text` |
| `skaileup-concept-storybook` | `component-mockup-storybook` (consolidates 6 sub-skills) |
| **NEW** | `component-mockup-isolated-html` |
| **NEW** | `walkthrough-mockup-{static-html, lit, astro, framework}` |
| **NEW** | `mockup-feedback-{annotate, triage, patch, apply}` |
| **NEW** | `_feedback/` workspace zone (sessions, patches, applied, devlog.md) |
| **NEW** | `elements:` frontmatter block on screens (with provisional-ID promotion) |
| `skaileup-concept-ops` | `ops/` (review, sync, eval, add-feature, reverse-engineer, project-*) |
| `skaileup-build` (one-time skills) | `impl-build/` |
| `skaileup-build/skills/feature` | **split** → `impl-slice/{implement,test,refactor,commit}` |
| `skaileup-build/skills/feature/feature-page` | merged into `impl-slice/implement` |
| `skaileup-build-supervised/brainstorm` | **promoted** → `impl-plan/brainstorm` |
| `skaileup-build-supervised/plan` | **renamed** → `impl-plan/plan-vertical` |
| `skaileup-build-supervised/git-prepare` | merged into `impl-slice/commit` |
| `skaileup-build-supervised/finish` | merged into `impl-slice/commit` |
| `skaileup-quality` | `impl-quality/` |
| `skaileup-quality/profiles/*` | **promoted** → `impl-architecture/templates/` |
| `skaileup-lab` | `lab/` (+ `lab/compile-bundle/` new) |
| `skaileup-contracts` | `contracts/` (unchanged) |
| **NEW** | `skaileup/scope/scope-project` (interview + tier picker) |
| **NEW** | `concept-slice/{brainstorm, align, scope-feature, design-feature}` |
| **NEW** | `impl-plan/align` (grill-me style deep interview) |
| **NEW** | `impl-slice/recap` (explain + diagram, mandatory) |
| **NEW** | `impl-quality/debug/{self-verify, handoff}` |
| **NEW** | `flows/{concept-slice, impl-slice, mvp, simple-app, standard-app, complex-app}.flow.yaml` |
| **NEW** | matching `bundles/*.bundle.yaml` |

---

## Legend

```
   ╔══╗  base / orchestrator           ──►  artifact flow
   ┌──┐  individual skill              ◄──  reverse / fed-back artifact
   │..│  optional / variant skill      ?    optional input
   ────  group / domain boundary       ║    contract reference (cross-cutting)
   ↻     loop (slice repeats)          ★    critical / non-skippable
```
