# 30: The post-port contract sweep — what four ports found and none owned

**Type:** task
**Blocked by:** None — 23, 24, 25, 26 all resolved 2026-09-05
**Status:** resolved

## Question

Nothing to decide. Four port sessions (23, 24, 25, 26) each hit the same class of defect from a
different side and none of them owned the file: a contract or a landed skill still describing
the collection as it was before ADR 0007, before ticket 24's atoms, or before a skill that this
migration deleted. Ticket 16 owned the path sweep and its commit `e63316c` **did not reach
these** — that is the finding, not a reproach: the sweep ran before the ports existed, so the
files with no reader yet had nothing to pull them into scope.

Every item below was **measured by a port session at the step it bound**, and each names its
finder.

### Contracts still on the pre-0007 tree

1. **`contracts/artifact_frontmatter.md` is wholly pre-0007** — `discovery/brief.md`,
   `experience/features/<group>/`, `_implementation/slices/`. Found independently by **23** and
   **26**.
2. **`contracts/feedback_loop.md`** — same, found by **23**.
3. **`contracts/seed_data.md`** carries `blueprint/` paths, found by **25**.

### Contracts disagreeing with each other or with a landed skill

4. **`artifact_frontmatter.md` omits `tech_stack_skill` entirely** (found by **25**) — the field
   `architecture-techstack` writes and `build-scaffold` + `build-database` read.
5. **`feature_map.json` vs `feature-map.json`** — `artifact_frontmatter.md` and
   `concept_structure.md` disagree on the separator (**25**). One is wrong; the landed
   `architecture-datamodel` picked one and that is the tiebreaker.
6. **`contracts/README.md`'s "no reader yet" rows for `golden_principles.md` and `evaluator.md`
   are now false** (**26**) — `ops-review` reads both, `quality-review` and `quality-release`
   read `evaluator.md`. The rows exist to put an unread contract on notice; leaving them stale
   defeats ticket 09's own mechanism.

### Landed skills naming things that no longer exist

7. **`skills/mockup-storybook` still *derives* three atoms that ticket 24 made 7/7**
   (`story_extension`, `component_library`, `icon_library`) **and points at `build-foundation`,
   a skill ticket 25's merge means will never exist.** Found by **24** and confirmed by **25**;
   a two-line fix each, belonging to whoever ports last, which is this ticket.
8. **`skills/mockup-walkthrough` step 1 uses unnumbered `_grounding/` and `_meta/`** (**26**).
9. **`skills/mockup-walkthrough`'s `05_features/**/*.md` glob catches
   `05_features/featuresets.md`** as a phantom manifest feature (**26**) — ticket 26 created that
   file, so the glob was correct until this week. One line.

### Also in scope

- **Re-run the sweep, do not just fix the list.** The nine items are what four sessions happened
  to trip over; the same grep that finds them (`grep -rn 'discovery/\|experience/\|_implementation/\|blueprint/' contracts/ skills/`,
  minus legitimate `10_blueprint/` and `11_build/`) will find whatever the ports did not touch.
  Report the full result, not just these nine.
- `scripts/check.py` and `scripts/test_check.py` stay green.

## Not in scope

**The `11_build/review.yaml` vs `11_build/reviews/<slug>.yaml` near-collision** — that is
ticket 31, and it is a naming decision, not a sweep. Do not rename either file here; if the
sweep touches a line mentioning one of them, leave the name as it stands.

## Answer

**All nine fixed; the re-run found eleven more sites in the same class, and one of them was a
live bug.** 32 files touched, `check.py` green (29 skills · 4 flows · 0 errors),
`test_check.py` 31/31, and all five runnable test harnesses pass.

### The nine

1. **`contracts/artifact_frontmatter.md`** — rewritten onto 0007. Every section heading is now
   a real path (`brief.md`, `02_grounding/research/*`, `03_brand/`, `04_journeys/`,
   `05_features/<featureset>/`, `07_screens/`, `10_blueprint/`). Also fixed while in there:
   the scope note pointed at `asset_frontmatter.md`, deleted by ticket 09 — it now points at
   `docs/skill-template.md`; `design_inspiration.md` → `design-inspiration.md` (the contract's
   own hyphen rule); the dead writers `impl-slice-commit` / `ops-reverse-engineer` / `ops-trace`
   became `build-implement` / `concept-reverse` / `ops-review`; `stories.yaml` was labelled a
   JSON file and shown as JSON, now YAML. Three sections were **added** rather than swept,
   because the rename would otherwise strand a landed writer that cites this file for "the
   frontmatter shapes": `goals.md` and `comparable.md` (`concept-brief` writes all three root
   files) and `07_screens/shell.md` (`experience-shell`). Both `06_behaviors/` and
   `comparable.md` carry only `last_updated` — inventing fields no skill writes would have
   re-created the defect this ticket exists to close.
2. **`contracts/feedback_loop.md`** — rewritten onto 0007, and every "when the X skill" heading
   re-pointed at the landed writer (`experience-journeys`, `spec-featuresets`, `spec-feature`,
   `architecture-datamodel`, `experience-behaviors`, `build-implement`, `ops-review`). The
   `.allium` branch is gone: `experience-behaviors` writes markdown state tables per 0007.
   Dropped the `## Event Emission` section — its only content was a pointer to
   `docs/OBSERVABILITY.md`, which does not exist in `-mp` and is now referenced nowhere.
3. **`contracts/seed_data.md`** — `blueprint/datamodel/seed.json` → `10_blueprint/…`, and the
   "How Skills Use Scenarios" headings re-pointed (`mock`→ the two renderers, `screens`→
   `spec-feature`, `e2e`→`quality-e2e`, `datamodel`→`architecture-datamodel`,
   `scaffold`→`build-database`). "The stack translator" is gone; the per-ORM layout lives in
   each template's `## Seed` section, which is where ticket 24 put it.
4. **`tech_stack_skill`** — added to `§ 10_blueprint/techstack.md` with a paragraph naming its
   readers (`build-scaffold`, `build-database`), the `custom` branch, and the rule that legal
   values are the directory names under `templates/`.
5. **`feature-map.json` wins.** Tiebreaker checked as instructed: the landed
   `architecture-datamodel` writes `feature-map.json` at three sites, `ops-review` reads that
   spelling, and `concept_structure.md` already agreed. `artifact_frontmatter.md` (1 site) and
   `feedback_loop.md` (3 sites) were the outliers and now match. No contract file was renamed.
6. **`contracts/README.md`** — the `golden_principles.md` row was the stale one; it now names
   its three in-body readers (`architecture-datamodel`, `experience-behaviors`, `ops-review`)
   and records that ADR 0008's notice is discharged. **The `evaluator.md` row was already
   correct** — it names `quality-review`, `quality-release` and `ops-review`; a port session had
   fixed it. Half of item 6 was not what it looked like.
7. **`skills/mockup-storybook`** — both fixes. Step 1 is now "resolve the stack and read its
   atoms by name", listing seven atoms under `metadata.atoms` and taking `component_library:
   null` / `icon_library: null` as stated branches rather than gaps to ask about — the same
   idiom `build-scaffold` landed with. The derivation table (`Vue SFC` → `.vue`, …) is gone.
   The `build-foundation` sentence now says an app's own Storybook is ordinary build work
   behind the template's `## Storybook Config`, which is what `build-scaffold` already says.
8. **`skills/mockup-walkthrough` step 1** — `_grounding/` → `02_grounding/`, `_meta/` →
   `01_meta/`.
9. **The `featuresets.md` phantom** — `05_features/**/*.md` → `05_features/*/*.md`, one level,
   with the reason at the step. Same treatment for `07_screens/**/*.md` (excluding
   `00_layout/`) → `07_screens/*/*.md`, which drops the reserved root `shell.md` by shape
   instead of by an exclusion naming a directory 0007 abolished.

### What the re-run turned up beyond the nine

The ticket's own grep, minus the legitimate hits, is now **empty but for one intentional line**
(`concept_structure.md:7`, "There is no sibling `_implementation/`"). Widening it to the rest of
the pre-0007 vocabulary (`product-spec/`, `design/tokens.json`, `00_layout/`, `_feedback/`,
`_standards/`, `_seeds/`, `mockup-component/`) found these, all fixed:

- **`contracts/walkthrough_renderer.md` — 26 sites, wholly pre-0007.** The largest find, and it
  had gone unnoticed because ticket 16's sweep landed on the skills and their fixtures, not on
  the contract they read. Screen paths, the manifest example, target resolution, the app-shell
  case and the NEVER-mutate line all carried `experience/screens/`; the group segment under
  `07_screens/` is a feature slug now, so the derived-nav label rule strips hyphens as well as
  underscores.
- **`contracts/elements_block.md` — 9 sites.** Same paths, plus a pointer at
  `experience-screens` and a file that does not exist
  (`skaileup/03_experience/03_screens/SKILL.md`), plus a "hard MUST at depth `medium`/`max`"
  written in vocabulary ADR 0003 and ticket 10 both retired. Now: `spec-feature` is the sole
  writer, and the obligation is stated as the author's.
- **`contracts/agent_patterns.md` — 5 sites, only one of which the narrow grep saw.**
  `_concept/_standards/index.yml`, `_grounding/general/`, `_grounding/{grounding_folder}/`, the
  `blueprint/techstack.md` read in Expert Discovery, and `impl-build-implementation-expert-*`
  (a name from the old collection; the templates' own `## Expert Skills` sections say
  `prog-expert-*` 7/7). The `grounding_folder` flow-node field it depended on exists nowhere in
  `-mp`.
- **`contracts/domain_model.md:16`** — "Like `_grounding/` and `_standards/`" → `02_grounding/`.
- **`skills/mockup-walkthrough/references/*/validator.py` — a live bug, not a stale string.**
  Both validators default `--source-root` to `experience/screens` and derive
  `project_root = source_root.parent.parent` "since source_root is typically
  `<project>/experience/screens`". Under 0007 the screens root is **one** segment
  (`07_screens`), so the default resolved one level too high and every
  `data-spec-screen source missing` check silently pointed outside the project. The
  static-html harness relies on that default; reverting the fix reproduces three failures, so
  the check was inert against any real 0007 tree. Fixed in both, with the comment rewritten.
- **`skills/mockup-walkthrough/references/astro/specs-json.md` — 10 sites** in the pre-resolved
  data shape the astro templates read.
- **Both walkthrough fixture trees** were entirely pre-0007 — `design/tokens.json`,
  `experience/journeys/stories.json`, `experience/screens/`, `product-spec/features/` — and the
  SKILL.md tells a reader the snapshot "is what correct output looks like". Moved to
  `03_brand/`, `04_journeys/stories.yaml`, `07_screens/`, `05_features/`, with the manifests,
  screen sources and both harnesses' `--source-root` updated. Ticket 14's finding that "every
  renderer hard-gated on `design/tokens.json`, which nothing writes" was fixed in the skills and
  left standing in the fixtures. Group directories (`00_auth`) kept, matching ticket 16's
  precedent in the feedback fixtures.
- **`mockup-annotate`'s two `manifest.json` files — 32 sites each**, missed by `e63316c` which
  updated the HTML beside them.
- **`mockup-feedback`'s apply fixtures** still had `_feedback/` as a sibling root while ticket
  16 had already moved their concept half to `07_screens/`. Now `concept/09_mockup/feedback/`,
  which is also the shape the skill actually invokes `apply.py` with (two roots, the feedback
  one nested inside the concept one).
- **Four `manifest.json` warning strings** naming `00_layout/shell.md` in prose.
- **`skills/mockup-storybook/references/scaffold.md`** — `discovery/brief.md` and
  `07_screens/00_layout/shell.md`.
- **`skills/architecture-{techstack,system}`** cite `artifact_frontmatter.md § blueprint/…`;
  both section citations moved with the headings.

### For the forge-concept register

Ticket 26 recorded that the host hardcodes `_concept/_grounding/<skillId>/input.json`
(`validator.ts:107`), a directory 0007 abolished, and that nothing breaks because **no skill
body names that path**. Two sites did name it, and both are now off it:
`contracts/agent_patterns.md` (three sites, spelling it `_grounding/{grounding_folder}/user_input.json`
— wrong directory *and* wrong filename, so it disagreed with the host as well as with 0007) and
`skills/README.md:6`, which listed it as the fourth role a skill name plays. Both now describe
the persisted answers the collection actually owns
(`02_grounding/onboarding/answers.json`) and say the dialog path is the host's on both ends.
**This strengthens the existing register entry rather than adding one** — the constraint is
unchanged, but "no skill body names it" was true only after this sweep.

### Left undone, deliberately

- **`docs/examples/`** — `mockup-walkthrough-astro/{SKILL.md,references/specs-json.md}` and
  `concept-brief/SKILL.md` carry 14 pre-0007 paths. They are ticket 03's frozen before/after
  worked examples, outside the grep's named scope, and their README says they are "examples,
  not live skills". But `skills/mockup-walkthrough` now supersedes one of them outright, so a
  reader copying path shapes from `docs/examples/` gets the old tree. **Worth a decision:
  re-sweep them, or delete the astro example now that the real skill exists.**
- **`docs/adr/*`** — five ADRs mention pre-0007 paths. They are dated records of what was true
  when the decision was made; rewriting them would destroy the thing they are for.
- **`scripts/test_check.py:141`** constructs `_concept/experience/screens` on purpose, to assert
  `check.py` rejects a path outside the tree. Correct as it stands.
- **`templates/README.md`** names `impl-build-foundation` / `-seed` / `-generate` — deliberate
  references to *deleted* skills, explaining where absorbed content came from. Also read-only
  for this ticket.
- **`11_build/review.yaml` vs `11_build/reviews/<slug>.yaml`** — untouched, per `## Not in
  scope`. Two lines mentioning them were swept around without renaming either.
- **`flows/`** — untouched; a sibling session owns it. No contract file was renamed or deleted,
  so its `requires:` blocks are unaffected.
