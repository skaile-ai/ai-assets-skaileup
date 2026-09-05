# 08: Concept-side consolidation

**Type:** grilling
**Blocked by:** None (04, 12 resolved)
**Status:** resolved

## Question

The concept half is 21 skills across four domains, and it's the half the user said should
"mainly stay the same" — so the question is pruning and clarity, not restructuring.

- `01_concept/`: `brief` · `goals` · `comparable` · `grounding/{onboard,research,seeds}`
- `02_design/`: `brand-visual` · `brand-voice` · `inspiration`
- `03_experience/`: `journeys` · `behaviors` · `screens` · `screens-technical` · `components`
- `04_product-spec/`: `features`

Decide:

- Which survive as skills vs. become `depth`/`optional` parameters of a neighbour.
  (`goals` and `comparable` are already described as optional passes over what `brief`
  writes lightly — is that two extra skills or two flags?)
- `screens` vs. `screens-technical` vs. `components` — three skills writing into the same
  `experience/screens/` tree. One skill, or three?
- Where the absorbed `research` skill lands relative to `grounding/research`.
- Whether `brand-voice` and `inspiration` earn their own skills.
- How `features` and the featureset grouping are named after ticket 04.
- What the concept-side `_concept/` output tree looks like once domains are renamed — this
  is what `artifacts.yaml` encodes, so changes here ripple into ticket 09.

## Answer

**19 skills → 9, and the artifact tree becomes one numbered root.**

### The surviving nine

`concept-brief` · `concept-onboard` · `concept-research` · `design-brand` ·
`experience-journeys` · `experience-behaviors` · `experience-shell` · `spec-featuresets` ·
`spec-feature`.

- **`concept-brief`** absorbs `concept-goals` and `concept-comparable` as a deep step, prose
  to `references/`. Both were already flags — twice (`depth:` in frontmatter, `optional:`
  + `parameters` on the node) — and **neither flag is read by anything**: `metadata.parameters`
  is in no forge-concept code path, and both discovery edges are `type: optional`, which
  ticket 15 proved orders nothing. What they genuinely add over the brief (KPIs, explicit
  non-goals, the positioning gap) survives as the deep step. Cost accepted: the flow node was
  the only real UI affordance for asking for a deep pass, and it goes.
- **`concept-onboard`** = `concept-grounding-onboard` + `concept-grounding-seeds` + mp's
  `to-questionnaire` as a step. When an answer belongs to someone who is not in the room, it
  writes `02_grounding/onboarding/questions.md` and continues rather than blocking.
- **`concept-research`** = `concept-grounding-research` + `design-inspiration` + mp's
  `research`. mp's dispatch discipline (background agent, primary sources, cite every claim)
  becomes its method — the part skaileup lacks; the seven fixed outputs stay its schema;
  `design-inspiration` becomes a depth step, gated on `tokens.json` as today. It was never a
  `design-*` skill: it writes into `_grounding/`.
- **`design-brand`** (was `design-brand-visual`). `design-brand-voice` does not port:
  `behavioral.md` has **zero readers collection-wide** and dies; copy guidelines become an
  optional section of `identity.md`, which has nine readers and actually runs.
- **`experience-behaviors`** keeps the skill and the artifact — four real downstream readers —
  and **drops `.allium`** for markdown state tables. Its grammar file, `references/allium-subset.md`,
  is cited at `02_behaviors/SKILL.md:95` as *"the constructs you may use"* and **does not
  exist**; the directory holds `SKILL.md` alone. Shipping a DSL whose spec is a dangling
  citation is the debt ticket 03 cleared when it found `EMIT` was read by no code.
- **`experience-shell`** is `experience-screens` narrowed to the one artifact a per-feature
  loop structurally cannot produce: `07_screens/shell.md`, plus the shared-UI-pattern section
  that `experience-components` used to hold.
- **`spec-featuresets`** (was `product-spec-features`) — renamed off `spec-features` because a
  one-character difference between two live `name:` contract keys (ticket 01: install path,
  flow `data.skill`, `produced_by`, grounding key) is a trap. Its product is the grouping;
  `spec-feature`'s is one feature.
- **`spec-feature`** (ticket 07) becomes the **sole writer of screen specs** and of the
  `elements:` block, and absorbs `experience-screens-technical`'s one unique capability —
  reading `06_behaviors/` for surfaces. A skill whose whole delta is "read one more input" is
  a step, not a skill.

### Dies

`concept-goals` · `concept-comparable` · `concept-grounding-seeds` · `design-brand-voice` ·
`design-inspiration` · `experience-screens-technical` · `experience-components` · the four
`concept-slice-*` (ticket 07).

`experience-components` dies on evidence: **both its readers were deleted by ticket 06**, and
it writes *inside* `07_screens/`, which every surviving renderer globs as
`screens/**/*.md` excluding only `00_layout/` — component specs are currently **rendered as
screens**. The machine-readable component inventory already lives in `elements:`.

### The screens boundary — W1

The brief's correction stands (`experience-screens` cannot collapse: sole writer of
`shell.md`, 11 readers), but the answer is not "two writers agree a shape". **The loop owns
screens; the whole-app skill owns only the cross-feature artifact.** One writer per artifact,
and the collision problem disappears rather than being papered over — today the two writers
are invisible to each other's guard, because `screens/<NN_group>/` holds no slug segment for
`design-feature`'s scan to find. Consequence handed to ticket 10: `skaileup-concept-only` and
`skaileup-concept-reverse` have no loop today and must run `spec-feature` per feature.

### The tree — one root, numbered at the first level only

```
_concept/  brief.md · goals.md · comparable.md
  01_meta/ 02_grounding/ 03_brand/ 04_journeys/ 05_features/ 06_behaviors/
  07_screens/ 08_dossiers/ 09_mockup/ 10_blueprint/ 11_build/
```

- **One root.** `_implementation/` is absorbed as `11_build/`. `_concept/` stays because
  **forge-concept resolves the literal string in four source sites** — `project.ts:112`,
  `artifact-contract.ts:187-188` and `:208-209`, `api/concepts/[...name].post.ts:43` — so a
  neutral root (`.skaile/`, `_project/`) is a forge-concept edit, which the map rules out.
  The root keeps its underscore: there it marks pipeline-owned against app-owned.
- **Numbered first level, nothing below.** `AppSidebar.vue:332-338` sorts `localeCompare` on
  the raw name, directories before files — **the filename is the only ordering mechanism the
  tree has**. And the host already implements the other half: `NN_` is stripped before display
  in three components (`SidebarFileItem.vue:204`, `AppHeader.vue:194`,
  `GroundingBrowser.vue:376`). Number what the collection fixes; leave what the project grows
  (`<featureset>`, `<feature_slug>`) unnumbered — priority already lives upstream as the story
  stage. This reverses ADR 0002 at one level and is not a contradiction: 0002 removed `NN_`
  because the flow graph carried order; the artifact tree has no flow graph. Recorded as
  **ADR 0007**.
- **Sequence is dependency order, not the flows'.** `appbuilder-complex` runs `behaviors`
  (line 179) before `features` (line 190) while `behaviors`' own gate reads *"when features
  are approved"* — the flow is wrong; ticket 10 fixes it.
- **`concept.yaml` dies** — a manifest of artifact slots and status, the same object ticket 09
  deleted one level up. Status is derivable from whether the file exists.
- **`_seeds/` and `_standards/` become `02_grounding/{seeds,standards}/`**: grounding is
  defined by where a thing came from (outside), machinery by what reads it (the pipeline).
- **The mockup family's five top-level names collapse to `09_mockup/`**, and the renderer
  leaves the path — ticket 06 moved that choice into onboarding, so a path segment records it
  twice and leaves a stale tree beside the new one on re-render.
- **Filenames are hyphenated, one path per artifact.** Fixes three live splits:
  `design-inspiration.md` (2 writers) vs `design_inspiration.md` (4 readers) vs a template
  pointing at a third path; `colors-fonts`/`colors_fonts`; and `user_input.json` at three
  spellings. Free in `-mp` — nothing is written yet.
- **No `parameters:` blocks on the concept side.** Each skill reads tier from
  `01_meta/scope.yaml` and states in prose what changes at each tier, at the step it binds.

### Also settled

- **Decision records:** one append-only `10_blueprint/decisions.md` (design-time) and
  `11_build/decisions.md` (build-time), not a numbered ADR directory — that is the
  *collection's* shape, not a project's. `spec-feature` **names** `domain-modeling` rather
  than restating it (ticket 07's `implement` mechanism, applied to the concept side).
- **`CONTEXT.md` gains one line:** the root directory name is fixed by the host and is not the
  vocabulary word.
- **`contracts/concept_structure.md` rewritten** to this tree (434 → 202 lines): the
  `concept.yaml` manifest, the legacy-path compatibility table, and the ten-row
  `step/`-subfolder table all go — the last replaced by one rule, *the subfolder is the
  skill's `name:`*.

### Handed off

- **Ticket 10 (flows):** `concept-only` / `concept-reverse` need a `spec-feature` loop; the
  `behaviors`-before-`features` order is wrong; the discovery sub-flow loses two nodes.
- **Ticket 16 (validators):** every path a skill writes resolves to a real top-level entry.
- **Ticket 17 (quality):** placement of the inspection outputs — `quality.yaml`,
  `eval-concept.yaml`, `testing/test_plan.md` — which are findings about work, not the work,
  and belong under `11_build/`.
- **Ticket 19:** writes `spec-feature` against this boundary.
- **Ticket 21 (new):** the `ops` domain. Found while checking a path — `14_ops/` is 12 skills
  and **no ticket owns 8 of them** (2,207 lines; four on zero flows). Settled here only at the
  boundary: `ops-add-feature` is `spec-feature` entered on an existing project, not a third
  writer into `05_features/`; `ops-reverse-engineer` re-points to `experience-shell` plus a
  `spec-feature` loop.

## Note from ticket 07

Ticket 07 moved the per-feature concept loop into one skill, **`spec-feature`**, and that
skill **writes screen specs** — `_concept/experience/features/<group>/<slug>.md` *and*
`_concept/experience/screens/<slug>/<screen>.md`, as `design-feature` does today. So the
`screens` question in this ticket is no longer "one skill or three" in isolation:

- **`experience-screens` now has to justify itself against `spec-feature`.** Ticket 07's
  ruling is that it covers screens *not* reached by a feature loop — the whole-app pass. If
  that pass has no real user, `experience-screens` collapses into `spec-feature` here rather
  than surviving as a second writer into the same tree.
  **Corrected 2026-09-05 (brief 08, re-verified) — that test is already passed, so do not
  re-run it here.** `experience-screens` is the **sole writer of `00_layout/shell.md`**
  (`03_screens/SKILL.md:151` *"MUST write 00_layout/shell.md before any individual screen
  specs"*, `:205` `OUTPUT …/shell.md`) and the **sole concept-side writer of the `elements:`
  block** — the only `elements:` writer across `01_`–`04_` and `08_`. `design-feature` is a
  **reader**: its single mention omits `layout` when shell.md is absent
  (`04_design-feature/SKILL.md:255`). Eleven skills read `shell.md`, including both surviving
  renderers and `build-foundation`. A cross-feature app shell is **structurally unproducible by
  a per-feature loop**, so the whole-app pass has a real user and `experience-screens` does not
  collapse. What is still open is therefore the *boundary*, not the survival:
  **absorb-with-a-shell-mode vs survive-with-one-directory-shape** — and whichever shape wins
  also settles `<NN_group>/` vs flat featuresets, since `screens/` mirrors `features/`.
- `screens-technical` and `components` write into the same tree and inherit the same test.

Also settled by ticket 07 and not open here: the concept-side working directory is
**`_concept/dossiers/<feature_slug>/`** (ticket 05 made `slice` impl-only), one file, frozen
by `spec-feature`. And `grilling` is a global install called by name — no skill in `-mp`
re-teaches the interview, which is what collapsed four grill-shaped skills to zero.
