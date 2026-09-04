# Brief: 08 — Concept-side consolidation

Evidence only. Nothing here resolves the ticket; the questions stay open for the grill.

Measured on branch `wayfinder/map`, `skaileup/` as of 2026-09-05.

---

## 0. Count correction

The ticket header says **21 skills**; its own bullet list names **15**, and the tree
holds **15**. Adding the four `08_concept-slice/` skills (which ticket 07 folded into
`spec-feature`, and which the "Note from ticket 07" makes part of this ticket's
boundary) gives **19**. There is no 21st and 20th skill under these domains.

| set | SKILL.md files | SKILL.md lines | sibling files | sibling lines |
|---|---|---|---|---|
| `01_concept` | 6 | 1,742 | 4 | — |
| `02_design` | 3 | 817 | 6 | — |
| `03_experience` | 5 | 1,492 | 6 | — |
| `04_product-spec` | 1 | 329 | 5 | — |
| `08_concept-slice` | 4 | 944 | many (examples/) | — |
| **total** | **19** | **5,324** | — | **4,338** |

Concept half = **9,662 lines** all-in, vs the implementation half's 4,166 that ticket 07
took to 4 skills.

---

## 1. The 19 skills

`flows` column counts distinct `.flow.yaml` files with a node running the skill
(`requires:` entries excluded — every flow that runs a skill also lists it, so counting
both doubles). Sub-flows are named where the reference is indirect.

| name | lines | flows referencing (node) | writes | flag |
|---|---|---|---|---|
| `concept-brief` | 289 | 5 — `appbuilder-mvp`, `appbuilder-cli`, `appbuilder-simple`, `skaileup-stepwise`, `concept-discovery` (→ standard, complex, concept-only) | `discovery/brief.md`, `discovery/goals.md`, `discovery/comparable.md` | — |
| `concept-goals` | 207 | 1 — `concept-discovery` only, node `optional: true` | `discovery/goals.md` | single flow; writes a file `concept-brief` already wrote |
| `concept-comparable` | 210 | 1 — `concept-discovery` only, node `optional: true` | `discovery/comparable.md` | single flow; writes a file `concept-brief` already wrote |
| `concept-grounding-onboard` | 403 | 1 — `skaileup-concept-only` | `_grounding/onboarding/profile.yaml`, `_grounding/onboarding/decisions.yaml` | single flow (and ticket 05 merges both files into `onboarding.yaml`) |
| `concept-grounding-research` | 364 | 1 — `skaileup-concept-only` | 7 files in `_grounding/research/` + `_grounding/step/{step}/`, `_grounding/findings/index.md`, `_grounding/findings/*.png` | single flow |
| `concept-grounding-seeds` | 269 | 1 — `skaileup-concept-only` | `_concept/concept.yaml` | single flow |
| `design-brand-visual` | 313 | 4 — `appbuilder-simple`, `appbuilder-standard`, `appbuilder-complex`, `skaileup-concept-only` | `discovery/brand/identity.md`, `tokens.json`, `brandbook.html`, `references/` | — |
| `design-brand-voice` | 282 | 2 — `appbuilder-complex` (required), `skaileup-concept-only` (`optional: true`) | `discovery/brand/behavioral.md`, `discovery/brand/copy_guidelines.md` | **`behavioral.md` has zero readers collection-wide** |
| `design-inspiration` | 222 | 3 — `appbuilder-standard`, `appbuilder-complex`, `skaileup-concept-only` — **`optional: true` in all three** | `_grounding/research/design-inspiration.md` | **writes hyphen, every reader spells underscore** — see §4 |
| `experience-journeys` | 317 | 5 — `appbuilder-simple`, `-standard`, `-complex`, `skaileup-concept-only`, `skaileup-concept-reverse` | `experience/journeys/stories.yaml` | — |
| `experience-behaviors` | 281 | 3 — `appbuilder-standard` (opt), `appbuilder-complex` (req), `skaileup-concept-only` (opt) | `experience/behaviors/<group>.allium` | 4 real downstream readers (`impl-architecture-system`, `-datamodel`, `impl-quality-test-plan`, `experience-screens-technical`) |
| `experience-screens` | 352 | 5 — `appbuilder-simple`, `-standard`, `-complex`, `skaileup-concept-only`, `skaileup-concept-reverse` | `experience/screens/00_layout/shell.md`, `experience/screens/<NN_group>/<screen>.md`, + feedback write into `experience/features/**/*.md` (`screens:`) | **sole writer of `shell.md`, sole concept-side writer of `elements:`** |
| `experience-screens-technical` | 252 | 1 — `skaileup-concept-only`, `optional: true` | enriches `experience/screens/**` in place; same two paths as `experience-screens` | **`do_not_invoke: true` + "not registered in any flow" — but it IS in a flow** |
| `experience-components` | 290 | 3 — `appbuilder-standard` (req), `appbuilder-complex` (req), `skaileup-concept-only` (opt) | `experience/screens/components/<name>.md` | **its only two readers are both skills ticket 06 killed** |
| `product-spec-features` | 329 | 6 — `appbuilder-mvp`, `-cli`, `-simple`, `-standard`, `-complex`, `skaileup-concept-only` | `experience/features/<NN_group>/<feature>.md` | most-referenced skill in the set |
| `concept-slice-brainstorm` | 177 | 1 — `skaileup-slice-concept` | `slices/{id}/brainstorm.md` | ticket 07: → `spec-feature` |
| `concept-slice-align` | 226 | 1 — `skaileup-slice-concept` | `slices/{id}/align.md`, `blueprint/glossary.md`, `decisions.md` | ticket 07: → `spec-feature` |
| `concept-slice-scope-feature` | 189 | 1 — `skaileup-slice-concept` | `slices/{id}/scope-feature.md` | ticket 07: → `spec-feature` |
| `concept-slice-design-feature` | 352 | 1 — `skaileup-slice-concept` | `experience/features/{group}/{slug}.md`, `experience/screens/{feature_slug}/{screen}.md`, `mockup-walkthrough/{tier}/{slug}.{ext}`, `slices/{id}/index.md` | ticket 07: → `spec-feature` |

**Zero-flow skills: none.** Every one of the 19 is on at least one flow node. The
ticket-06/07/09 pattern shows up here in a different shape — not *unreferenced skills*
but **unread artifacts** and **one self-declared-dead skill that is nevertheless wired**:

1. `design-brand-voice` → `brand/behavioral.md`: **zero readers** anywhere in the 95-skill
   collection. `copy_guidelines.md` has one reader, and it is a table default value in
   `experience-components` line 192 (`| empty_message | string | from copy_guidelines |`) —
   prose, not a read step.
2. `experience-components` → `experience/screens/components/`: readers are
   `mockup-component-isolated-html` (**dropped by ticket 06**) and `mockup-walkthrough-text`
   (**dropped by ticket 06**). Neither survivor (`static-html`, `astro`) nor
   `mockup-component-storybook` reads the directory. **Zero surviving readers.**
3. `design-inspiration` → `_grounding/research/design-inspiration.md`: all four
   readers spell the file `design_inspiration.md` with an underscore. **Zero readers at
   the path it writes.** Evidence in §4.
4. `experience-screens-technical` carries `metadata.do_not_invoke: true` and a body banner
   reading *"it is **not registered in any flow** and will not be dispatched by the
   orchestrator. Do not use it in production pipelines."* — while sitting on
   `skaileup-concept-only.flow.yaml:230`. Nothing in forge-concept reads `do_not_invoke`;
   the only documentation of the key is `contracts/asset_frontmatter.md`, which ticket 09
   deleted.

---

## 2. `goals` / `comparable` as skills vs flags of `brief`

### What `concept-brief` already writes

`concept-brief` (`01_brief/SKILL.md:141-143`) declares three outputs:

```
WRITES
_concept/discovery/brief.md — elevator pitch, audience, problem, hero flow
_concept/discovery/goals.md — success criteria, constraints, deadlines
_concept/discovery/comparable.md — similar apps with lessons learned
```

Its STEP 1 interview is seven questions; two of them are the whole light pass:

```
5. Are there apps that do something similar?
6. What does success look like? Any constraints or deadlines?
```

STEP 2 then emits `goals.md` as *"Success criteria, constraints, deadlines, known
limitations."* and `comparable.md` as *"For each comparable app: - What it does well -
What to borrow - What to avoid"* — one line of guidance each.

### What the two focused skills add

`concept-goals` (207 lines) adds a **five-question interview** the brief does not run
(`02_goals/SKILL.md:123-129`), a **structured frontmatter contract**
(`primary_outcome` / `kpis[]` / `constraints[]` / `non_goals[]`), and four `##` sections.
Its genuinely-new material over the brief is: measurable KPIs, **explicit non-goals**,
leading-vs-lagging metrics at `max` depth, and the rule *"MUST tie every success criterion
back to the brief's problem or hero flow"*. The brief writes none of that.

`concept-comparable` (210 lines) adds: **3-6 comparables with a direct/indirect/adjacent
mix**, a per-app borrow **and** avoid, an explicit **positioning gap** in frontmatter,
and one rule that has no analogue in the brief — *"MUST distill, not duplicate,
`_grounding/research/competitors.md` when it exists"*. The brief in fact has the opposite
rule: *"NEVER invent comparable products if the user has not mentioned any."*

### They are already parameterised, in two places at once

Both skills already declare the flag the ticket asks about:

```yaml
  parameters:
    depth:
      type: enum
      values: [none, light, medium, max]
      default: medium
```

and both document `none` as *"Skip — rely on the light goals.md / comparable.md from
concept-brief"*. So the "depth flag" already exists inside each skill.

Separately, `concept-discovery.flow.yaml` gates them at the node:

```yaml
  - id: goals
    data:
      skill: concept-goals
      label: 'Concept Goals (per parent: optional | required)'
      optional: true
      parameters:
        mode: '${goals}'
  - id: comparable
    data:
      skill: concept-comparable
      optional: true
```

with `globals.goals: optional` and edges `brief --optional--> goals --optional-->
comparable`. Only `skaileup-concept-only` overrides it (`parameters: goals: required`);
`appbuilder-standard` and `appbuilder-complex` both pass `parameters: {}`.

Two mechanical facts about that wiring:

- The node passes `mode`, the skill declares `depth`. **Nothing consumes `mode`.**
- Per ticket 01, `metadata.parameters` is not in forge-concept's read-set at all; a grep
  of `forge-concept/{shared,server}` for a `metadata`/frontmatter `parameters` reader
  returns nothing. So the `depth` enum **and** the node `parameters` block are both
  documentation. The skill-vs-flag choice is an authoring question with no machine
  consequence either way.
- Ticket 15's rule bites here: the engine takes dependencies from
  `edges.filter(e => e.type === "flow")`. Both discovery edges are `type: optional`, so
  **neither the goals nor the comparable node orders anything today** — `concept-discovery`
  is, to the engine, three unordered nodes.

---

## 3. `screens` vs `screens-technical` vs `components` vs `spec-feature`

### Exactly what each writes

| skill | path written | shape |
|---|---|---|
| `experience-screens` | `experience/screens/00_layout/shell.md` | app shell — nav, sidebar, header, breakpoints |
| `experience-screens` | `experience/screens/<NN_group>/<screen>.md` | full spec: Purpose, Route, What the User Sees, ASCII Wireframe, Information Displayed, Actions, Situations, UI Elements, Template Data — **plus the `elements:` block** |
| `experience-screens` | `experience/features/<NN_group>/<feature>.md` | feedback write: `screens:` list into feature frontmatter |
| `experience-screens-technical` | same two screen paths, "enriches in place" | adds component inventories; only skill that reads `behaviors/*.allium` for surfaces |
| `experience-components` | `experience/screens/components/<name>.md` | one file per shared component: props, variants, states, a11y |
| `concept-slice-design-feature` (→ `spec-feature`) | `experience/screens/{feature_slug}/{screen_slug}.md` | **a stub** |

### The collision is a directory-shape collision, not a content one

`experience-screens` groups screens by **featureset**: `screens/<NN_group>/<screen>.md`.
`concept-slice-design-feature` groups them by **feature**, and says so as a hard rule
(`04_design-feature/SKILL.md:246-249`):

> Target path: `_concept/experience/screens/<feature_slug>/<screen>.md`
> (the FIRST segment under `screens/` MUST be `<feature_slug>`; if `<group>` differs from
> `<feature_slug>` in scope-feature.md, use `<feature_slug>` for the screen dir per
> path-segment rule.)

Its STEP 1 collision check scans `experience/screens/**/*.md` for *another slice* owning
the slug. It cannot see that `experience-screens` already wrote the same screen under
`01_group/`, because that path holds no slug segment. **The two writers are invisible to
each other's guard.**

And in `appbuilder-standard` they both run, in this order:

```
features → screens → components → mockups → feedback → architecture → build-setup → slice-loop
```

where `slice-loop` is `flow: skaileup-slice` with `parameters: concept_depth: full`,
which delegates to `skaileup-slice-concept` → `concept-slice-design-feature`. Same in
`appbuilder-complex`. So today, standard and complex projects end with **screens in both
shapes**: filled ones under `screens/<NN_group>/`, stubs under `screens/<feature_slug>/`.

### `design-feature` writes a stub and names `experience-screens` as its completer

`04_design-feature/SKILL.md:256-258`, verbatim:

> Body: a short stub naming the screen and its purpose. **Detailed composition is the job
> of `experience-screens` later** — this skill writes only the slot.

It also writes no `elements:` block at all (`grep elements` on that file: zero hits), and
omits `layout:` when `shell.md` does not exist. `elements:` is ticket 06's kept block with
9 readers, and `experience-screens` is the only concept-side writer of it. So a project
built purely through the slice loop today produces screens the surviving renderers cannot
render into widgets.

### Does the whole-app pass have a real user? — the ticket-07 test

**Yes, on three counts, and one of them is structural.**

1. **`00_layout/shell.md` has exactly one writer: `experience-screens`.** Eleven skills
   read it — both surviving renderers (`mockup-walkthrough-astro:46`,
   `-static-html`), `mockup-component-storybook-{setup,pages,orchestrator}`,
   `impl-build-foundation:50`, `experience-components` (listed **Required**), and
   `concept-slice-design-feature` itself, which references it only to decide whether to
   *omit* `layout:`. The shell is by definition cross-feature; a per-feature loop cannot
   produce it. `experience-screens-technical` is the only other writer and is
   `do_not_invoke`.
2. **Two flows run `experience-screens` with no concept-side loop at all:**
   `skaileup-concept-only` (13 concept skills, no slice sub-flow) and
   `skaileup-concept-reverse` — where `experience-screens` is the terminal node after
   `ops-reverse-engineer` → journeys → system → datamodel. Reverse-engineering an existing
   repo has no feature backlog to loop over; the screens are derived from code that already
   exists.
3. **`appbuilder-simple` runs `experience-screens` and delegates only
   `skaileup-slice-impl`** (impl side), never `skaileup-slice-concept`. In simple tier,
   `experience-screens` is the only screen writer that exists.

Counter-evidence on (3): ticket 07 ruled *"Tier stops gating entry and becomes depth
inside the skill — with one entry skill per side there is nothing left to route to."*
If simple-tier feature work enters `spec-feature` like everything else, (3) dissolves.
(1) and (2) do not.

### `components` writes inside the screens tree, and the renderers glob it

`experience/screens/components/<name>.md` sits under `screens/`. Every renderer globs
`experience/screens/**/*.md`, and `mockup-walkthrough-astro:371` excludes exactly one
subdirectory: *"Glob `experience/screens/**/*.md` (excluding `00_layout/`); sort"*.
`components/` is not excluded — component specs are globbed as screens. `static-html` and
`mockup-component-storybook-components` (`READS _concept/experience/screens/**/*.md`)
carry the same glob with no exclusion at all.

---

## 4. `research` (absorbed from mp) vs `concept-grounding-research`

They are not the same kind of object.

**mp `research`** — `~/.agents/skills/research/SKILL.md`, **12 lines**, frontmatter of two
keys. The whole body:

> Spin up a **background agent** to do the research, so you keep working while it reads.
> Its job:
> 1. Investigate the question against **primary sources** (official docs, source code,
>    specs, first-party APIs), not a secondary write-up of them. Follow every claim back
>    to the source that owns it.
> 2. Write the findings to a single Markdown file, citing each claim's source.
> 3. Save it where the repo already keeps such notes; match the existing convention, and
>    if there is none, put it somewhere sensible and say where.

It is a **dispatch pattern with three rules and no fixed output**: any question, one file,
location inferred from the repo. Ticket 02 records it as depending on nothing.

**`concept-grounding-research`** — 364 lines + three `references/` templates
(`competitor_template.md`, `persona_template.md`, `design_inspiration_template.md`). It is
a **fixed-output producer**: seven named files under `_grounding/research/` (`domain`,
`competitors`, `audiences`, `design-inspiration`, `patterns`, `colors-fonts`,
`behavioral-patterns`), plus `_grounding/step/{step}/*.md`, `_grounding/findings/index.md`
and screenshots. Its rules are the opposite kind — *"MUST always produce
design-inspiration.md — even if other sections are thin"*, *"NEVER use generic personas
('busy professional')"*, *"MUST save screenshots to `_grounding/findings/` when browser
tool is available"*.

The overlap is the sourcing discipline (cite evidence, don't invent competitor features);
the difference is that one has no schema and one is nothing but schema. Ticket 04 already
fixed the absorbed skill's name as `concept-*` on the collision argument (a bare `research`
clobbers the global mp install at the same path).

**Path-spelling break, and its blast radius.** Two skills write
`_grounding/research/design-inspiration.md` (hyphen): `concept-grounding-research:139` and
`design-inspiration:107`. Four skills read `_grounding/research/design_inspiration.md`
(underscore): `design-brand-visual:143`, `experience-screens:135`,
`experience-screens-technical:96`, `mockup-walkthrough-text:168`. The migration note is
still sitting in `concept-grounding-research:362`:

> Underscore filenames (`design_inspiration.md`) → hyphenated (`design-inspiration.md`)
> (prefer new)

— the writers migrated, the readers never did. `concept-grounding-research/references/
design_inspiration_template.md:3` still points at a third path,
`_grounding/general/design_inspiration.md`. The same split exists for
`colors-fonts.md` / `colors_fonts.md` (`design-brand-visual:144` reads the underscore).

---

## 5. `brand-voice` and `inspiration`

### `design-brand-voice` — 282 lines, 2 flows

Writes `discovery/brand/behavioral.md` and `discovery/brand/copy_guidelines.md`. Node is
`optional: true` in `skaileup-concept-only`, `optional: false` in `appbuilder-complex`.
It is absent from `appbuilder-simple` and `appbuilder-standard` entirely.

Downstream readers, complete list:

- `behavioral.md` — **none**. The only file in the collection mentioning it is
  `02_brand-voice/SKILL.md` itself. `impl-build-foundation` reads `identity.md` and
  `tokens.json`, not `behavioral.md`. `contracts/concept_structure.md:107` documents the
  path; no skill consumes it.
- `copy_guidelines.md` — one mention outside the writer:
  `03_experience/05_components/SKILL.md:192`, inside a props table:
  `| empty_message | string | from copy_guidelines | Message when no data |`.
  Not a read step, not in its Context Budget, not in its `prerequisites`.

Its dependency shape is also inverted against the flows: it requires
`_concept/experience/features/**/*.md` and reads `experience/screens/**/*.md` as
*"all user-facing states that need copy"*, yet in `appbuilder-complex` its node sits at
line 146 — **before** `features` (190) and `screens` (201).

### `design-inspiration` — 222 lines, 3 flows, `optional: true` in all three

Writes one file, into a **grounding** path, not a design one:
`_grounding/research/design-inspiration.md`. Its own body says it *deepens* what
`concept-grounding-research` wrote: *"IF `_concept/_grounding/research/design-inspiration.md`
exists, read it — deepen it"* and *"MUST deepen an existing design-inspiration.md rather
than discarding it"*. Same relationship `concept-goals` has to `concept-brief`, one
domain over.

Its gate is `_concept/discovery/brand/tokens.json` (hard) — so it runs after brand-visual
and constrains references to the already-chosen palette. And per §4, every reader of the
artifact it writes is looking at a different filename.

`design-brand-visual` (313 lines, 4 flows, `optional: false` everywhere) is the only
skill in `02_design` whose outputs have broad live readership: `tokens.json` is read by
20 skills, `identity.md` by 9.

---

## 6. `features` + featureset grouping under ticket 04

**What the rename touches.**

- The skill name: `product-spec-features` → `spec-features` under ticket 04's
  `product-spec` → `spec` domain rename. **Ticket 07 named its merged concept-loop skill
  `spec-feature`.** The two differ by one character.
- The artifact path stays `_concept/experience/features/` — `features` is in the
  `experience` domain's *tree* while the skill moves to the `spec` domain's *name*. Today
  the same split already exists (`product-spec-features` writes into `experience/`).
- **`feature group` → `featureset`** is CONTEXT.md's straight rename
  (`_Avoid_: feature group, group, epic, module`), and the map records the word appears
  **0 times** today. Measured here: `group` as the grouping noun appears in
  `04_product-spec/01_features/SKILL.md` at lines 3, 30, 73, 82, 133, 144, 150, 153,
  186, 189, 191, 207, 259, 274, 304 — fifteen sites in one skill.
- The **`<NN_group>` path token** is the live carrier. Files using it:
  `04_product-spec/{DOMAIN.md,01_features/SKILL.md,01_features/CLI.md,
  01_features/references/feature_template.md}`, `03_experience/{DOMAIN.md,
  03_screens/SKILL.md,03_screens/CLI.md,03_screens/references/screen_spec_template.md,
  04_screens-technical/SKILL.md}`, `14_ops/{10_add-feature/*, 11_reverse-engineer/SKILL.md,
  12_trace/SKILL.md}`, `05_mockup-walkthrough/00_migrate-elements/SKILL.md`, and
  `contracts/concept_structure.md`.
- The skill enforces the prefix as a rule: *"MUST organize features in numbered group
  folders (01_user_auth, 02_dashboard, etc.)"* and *"Create numbered group folders using
  NN_ prefix (no letter prefix)"*, with a Common Mistakes row against `A_01_` legacy
  names. Ticket 04's *"no `NN_` anywhere — order lives in the flow graph"* was stated
  about the **collection** tree. Whether it reaches the **artifact** tree is not settled
  by any resolved ticket; the artifact tree has no flow graph to carry order.
- Third writer into the same tree: `ops-add-feature` declares
  `produces: _concept/experience/features` — so after ticket 07 there are three
  (`spec-features`, `spec-feature`, `ops-add-feature`).

---

## 7. The concept-side `_concept/` output tree

Every path the 19 skills write. This is now the only record — ticket 09 deleted
`artifacts.yaml`, and `contracts/concept_structure.md` (the prose tree) is a survivor
but predates tickets 05/07.

```
_concept/
├── concept.yaml                                   concept-grounding-seeds
├── decisions.md                                   concept-slice-align (inline ADRs)
│
├── _grounding/
│   ├── onboarding/profile.yaml                    concept-grounding-onboard  ┐ ticket 05
│   ├── onboarding/decisions.yaml                  concept-grounding-onboard  ┘ → onboarding.yaml
│   ├── research/domain.md                         concept-grounding-research
│   ├── research/competitors.md                    concept-grounding-research
│   ├── research/audiences.md                      concept-grounding-research
│   ├── research/design-inspiration.md             concept-grounding-research + design-inspiration
│   ├── research/patterns.md                       concept-grounding-research
│   ├── research/colors-fonts.md                   concept-grounding-research
│   ├── research/behavioral-patterns.md            concept-grounding-research
│   ├── step/{step}/*.md                           concept-grounding-research
│   ├── findings/index.md                          concept-grounding-research
│   └── findings/*.png                             concept-grounding-research
│
├── discovery/
│   ├── brief.md                                   concept-brief
│   ├── goals.md                                   concept-brief (light) · concept-goals (deep)
│   ├── comparable.md                              concept-brief (light) · concept-comparable (deep)
│   └── brand/
│       ├── identity.md                            design-brand-visual
│       ├── tokens.json                            design-brand-visual
│       ├── brandbook.html                         design-brand-visual
│       ├── references/                            design-brand-visual
│       ├── behavioral.md                          design-brand-voice      ← 0 readers
│       └── copy_guidelines.md                     design-brand-voice      ← 1 prose mention
│
├── experience/
│   ├── journeys/stories.yaml                      experience-journeys
│   ├── features/<NN_group>/<feature>.md           product-spec-features
│   │                                              + concept-slice-design-feature ({group}/{slug})
│   │                                              + experience-screens (feedback: screens[])
│   ├── screens/00_layout/shell.md                 experience-screens ONLY
│   ├── screens/<NN_group>/<screen>.md             experience-screens (+ screens-technical, in place)
│   ├── screens/<feature_slug>/<screen>.md         concept-slice-design-feature  ← second shape
│   ├── screens/components/<name>.md               experience-components   ← 0 surviving readers
│   └── behaviors/<group>.allium                   experience-behaviors
│
├── mockup-walkthrough/<tier>/<feature_slug>.<ext> concept-slice-design-feature (stub)
│
├── slices/<slice_id>/                             ticket 05/07 → dossiers/<feature_slug>/
│   ├── brainstorm.md                              concept-slice-brainstorm  ┐
│   ├── align.md                                   concept-slice-align       │ ticket 07:
│   ├── scope-feature.md                           concept-slice-scope-feature│ one file
│   └── index.md                                   concept-slice-design-feature (freeze) ┘
│
└── blueprint/glossary.md                          concept-slice-align (inline)
```

**Not written by these 19, but in the same tree** (context for redrawing it):
`_meta/scope.yaml` (`skaileup-scope-scope-project`), `_seeds/` (user), `_standards/`
(`impl-quality-standards-discover`), `quality.yaml` (`ops-review`), `prototype/storybook/`
(mockup), `_feedback/` (mockup), `testing/test_plan.md`, `blueprint/{techstack,
architecture,datamodel/}`.

Path facts worth carrying into the redraw:

- `_grounding/onboarding/` vs the `user_input.json` paths several skills actually read:
  `concept-brief`, `concept-goals` and `product-spec-features` read
  `_concept/_grounding/overview/user_input.json` and `_grounding/features/user_input.json`,
  while `concept_structure.md` documents `_grounding/onboarding/inputs/overview.json` and
  `concept-grounding-research` reads `_grounding/onboarding/inputs/overview.json`. Three
  spellings for one file.
- `design-inspiration` is a `design-*` skill writing into `_grounding/`.
- Both renderers read tokens as `design/tokens.json` (`astro:323`, `static-html:160`),
  a fourth path for `discovery/brand/tokens.json`.
- `experience/screens/components/` is a non-screen artifact inside the screens tree.

---

## 8. mattpocock skills that map onto this half

The `implement`-shaped find for the concept side, checked against `~/.agents/skills`
(28 dirs; `herdr`/`caveman` are third-party, excluded).

| mp skill | lines | maps onto | evidence |
|---|---|---|---|
| **`to-questionnaire`** | 54 | `01_concept` discovery skills | Ticket 02 already verdicted it **ABSORB → `01_concept`**: *"Every discovery skill assumes the user holds the answers."* Its rule is the inversion — **"Grill the send, not the subject."** Interview the user only about *who the recipient is* and *what you need back*; the questions then target the gap. `concept-brief` STEP 1, `concept-goals` STEP 2 and `concept-comparable` STEP 2 all interview the user directly about facts the user may not hold (KPIs, competitor pricing, compliance constraints). No skaileup skill has an async-handoff artifact. |
| **`grilling`** | 28 | `concept-slice-align`'s whole job | Global install called by name (ticket 07). `grill-me` (7 lines) and `grill-with-docs` (7 lines: *"Call the Skill tool twice, for 'grilling' and 'domain-modeling'"*) are the 7-line-wrapper pattern — the concept-side analogue of `implement`. |
| **`domain-modeling`** | 74 | `concept-slice-align`'s inline `glossary.md` + `decisions.md` writes | Already ported to `contracts/domain_model.md`. `concept-slice-align` is the only concept skill that writes both; under ticket 07 that behaviour moves into `spec-feature`, which could name the skill instead of restating it. |
| **`research`** | 12 | `concept-grounding-research` | §4. Different object, not a replacement. |
| **`to-spec`** | 75 | already claimed by ticket 07 as `spec-feature` | Its **seam** step and its *"Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching"* rule are the concept-side hooks. |
| **`wait-what`** | 7 | none in this half | Ticket 02: ABSORB → meta/global. Its body already assumes `CONTEXT.md` + `CONTEXT-MAP.md`. |
| `triage` · `handoff` · `teach` · `wayfinder` · `ask-matt` | — | not concept-side | ticket 02 routes them elsewhere (`14_ops`, slice-loop contract, meta). |

Nothing in mp maps onto `screens`, `components`, `journeys`, `behaviors` or `brand-*` —
mp has no artifact-tree of its own, so the whole `experience`/`design` half has no
upstream analogue. The `implement`-style collapse mechanism (a short skill that *names*
another skill) is available for `grilling` and `domain-modeling` only.

---

## Open tensions

Places where the evidence points two ways. Sharpest form of each, for the human.

1. **`experience-screens` writes `shell.md` and `elements:`; `spec-feature` writes
   neither.** So the whole-app pass is not "the tier-simple alternative to the loop" —
   it holds two artifacts the loop structurally cannot produce (a cross-feature shell,
   and the renderer block the loop's stub omits). Does `spec-feature` absorb `screens`
   and grow a "shell + elements" mode it runs once, or does a whole-app skill survive
   and the two agree a **single** directory shape? Either answer costs something the
   other keeps.

2. **The two screen writers disagree on the directory, not the content.**
   `screens/<featureset>/<screen>.md` vs `screens/<feature_slug>/<screen>.md`.
   `design-feature`'s own rule is *"the FIRST segment under `screens/` MUST be
   `<feature_slug>`"*, and its collision check is blind to the other shape. Which shape
   is `-mp`'s? (Answering this settles §6's `<NN_group>` question at the same time, since
   `screens/` mirrors `features/`.)

3. **`design-feature` says the whole-app pass finishes its work.** *"Detailed composition
   is the job of `experience-screens` later — this skill writes only the slot."* Read
   one way this proves `experience-screens` is load-bearing; read the other it proves the
   loop was never a second writer, only a first draft — and the merge is a
   sequencing fix, not a skill deletion. Which reading is `-mp`'s?

4. **`goals`/`comparable` are already flags — twice — and neither flag is read by
   anything.** `depth: [none,light,medium,max]` in frontmatter, `optional: true` +
   `parameters` on the node, `metadata.parameters` in no code path, and both discovery
   edges typed `optional` so the engine orders nothing. Is "make them flags" therefore a
   no-op that changes only where 417 lines of prose live — and if so, does the prose live
   inside `concept-brief` (pushing it back over the 140-line ceiling ticket 03 set, from
   the 80 the prototype achieved) or in `references/`?

5. **`design-brand-voice`'s artifacts have no readers, but its content is the only
   place UX copy rules exist.** Zero readers of `behavioral.md`, one prose mention of
   `copy_guidelines.md`, and its node runs *before* the features and screens it declares
   as hard inputs. Is that a skill to delete, a skill to re-order, or a `references/` file
   that `spec-feature` and `build-implement` cite when writing copy?

6. **`experience-components` survives ticket 06 or dies with it.** Both its readers
   (`mockup-component-isolated-html`, `mockup-walkthrough-text`) were deleted by ticket 06;
   the surviving renderers glob its directory as if the files were screens
   (`screens/**/*.md`, only `00_layout/` excluded). Does a component catalogue have a
   reader in `-mp` — `mockup-storybook`, `build-foundation` — or is "shared UI pattern"
   a section inside `shell.md` and the tech-stack template?

7. **`design-inspiration` deepens a file it does not share a filename with.** Two writers
   spell it with a hyphen, four readers with an underscore, one template with a third path.
   Is `design-inspiration` a separate skill, a `depth` of `concept-research` (the same
   shape `goals` has to `brief`, one domain over), or does it disappear into
   `brand-visual`'s reference gathering — and does the fix land in the writers or the
   readers?

8. **`experience-screens-technical` is a skill that says it does not exist.**
   `do_not_invoke: true`, a banner reading "not registered in any flow", and a node in
   `skaileup-concept-only`. No code reads the flag; the contract documenting it is
   deleted. Does it port as `screens` at `depth: max`, does it port as the reader of
   `behaviors/*.allium` that `experience-screens` lacks, or does it not port?

9. **`spec-features` and `spec-feature` differ by one character.** Ticket 04 renames
   `product-spec-features` → `spec-features`; ticket 07 named the merged loop
   `spec-feature`. Both are `name:` values, and ticket 01 established `name:` is the whole
   identity — install path, flow `data.skill`, `produced_by`, grounding key. Is a
   one-character difference between two live contract keys acceptable, or does one rename?

10. **Ticket 04's "no `NN_` anywhere" was ruled about the collection tree; the artifact
    tree has fifteen `NN_group` sites in one skill and thirteen files carrying the token.**
    The collection got flat because the flow graph carries order. `_concept/experience/
    features/` has no flow graph. Does `featureset` keep an ordering prefix, or does the
    artifact tree go flat too and lose priority ordering?

11. **`concept-grounding-*` is three skills on one flow.** All three appear only in
    `skaileup-concept-only` — 1,036 lines reachable from exactly one of seventeen flows,
    and ticket 05 already merges two of `onboard`'s three output files. Is grounding one
    skill, three, or a `depth` of the discovery entry point?
