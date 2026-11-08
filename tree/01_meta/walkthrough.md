---
path: _concept/01_meta/walkthrough.yaml
summary: the four concept stages and the user's yes on each — what the build waits for
owner: [skaileup]
may_propose: []
---

# _concept/01_meta/walkthrough.yaml

The state of the concept walk: the four stages `frame` → `look` → `data` → `features`, walked in that order, and the user's decision on each — approved, waived or reopened — with its source. `skaileup` reads it to name the next stage and its producer; `build-scaffold`, `build-database`, `build-plan` and `build-implement` read it through `walkthrough.py gate` before they touch code. It holds only the user's decisions: which artifacts exist, which carry `approved:` and which still hold open markers is computed from the artifacts each time, so the file never restates them. A yes recorded without the user leaves the build running on a concept nobody confirmed.

## Format

```yaml
stages:
  frame:    { status: approved, approved: "2026-11-08", source: "user, 2026-11-08" }
  look:     { status: open }
  data:     { status: open }
  features: { status: waived, dr: DR-7, source: "user, 2026-11-08" }
history:   # append-only
  - { "on": "2026-11-09", stage: look, event: reopened, reason: "user: Kunden under Einstellungen, Kunde switch in the sidebar footer" }
```

`status` ∈ `open | approved | waived`; `event` ∈ `approved | waived | reopened`. An `approved` stage carries `approved` (ISO date) and `source`; a `waived` one carries `dr` (`DR-<n>`) and `source`; a history entry carries `on`, `stage`, `event` and, as they apply, `reason`, `source`, `dr`. `tree/01_meta/walkthrough.schema.json` is the machine-readable form.

The stages, their required checks, the skills that produce them and the checkpoint the user approves on. `skills/skaileup/scripts/walkthrough.py` mirrors this table in `STAGES`.

|stage|required (check)|producing skills, in order|checkpoint|
|---|---|---|---|
|frame|`_concept/01_meta/expectations.md` exists · `_concept/brief.md` approved · `_concept/goals.md` approved · `_concept/glossary.md` exists · `_concept/04_journeys/stories.yaml` exists|skaileup (expectations), concept-onboard?, concept-research?, concept-brief, concept-glossary, experience-journeys|completion summary: pitch, roles, story-map stages|
|look|`_concept/03_brand/identity.md` approved · `_concept/03_brand/brand.tokens.json` exists · `_concept/07_screens/shell.md` approved and contains `navigation: decided` · `APP-DESIGN.md` exists with no `[open Q` in `## Navigation model` · `_concept/09_mockup/storybook/src/app/nav.ts` exists|design-brand, experience-interaction (navigation-model batch), experience-shell, mockup-storybook (App frame)|Storybook `App` story: shell + brand + one pending page per destination|
|data|`_concept/10_blueprint/datamodel/model.yaml` and `seed.yaml` exist · `model.yaml` contains no `proposed:` · `APP-DESIGN.md` `## Objects` has ≥1 `OBJ-` row and neither `## Objects` nor `## Information hierarchy` contains `[open Q` or `(proposed by` · ≥1 directory `_concept/09_mockup/storybook/src/entities/*/`|concept-glossary (object axes), architecture-datamodel, experience-interaction (objects batch), mockup-storybook (entity stories)|Storybook `Entities/<Entity>/*` for every object-map row|
|features|`_concept/05_features/featuresets.md` approved · ≥1 `_concept/05_features/*/*.md` approved · `APP-DESIGN.md` approved · ≥1 `_concept/09_mockup/storybook/src/journeys/*.stories.ts`|experience-behaviors?, spec-feature (loop), experience-screen, mockup-storybook (screens, App, journeys), mockup-feedback|Storybook App + Journeys; a feedback round with no open notes|

"approved" = markdown frontmatter has an `approved:` key (`tree/README.md § Frontmatter every markdown artifact carries`); `?` = optional skill. A check that names `[open Q`, `(proposed by` or `proposed:` fails while that marker is present and reads `open markers`: a stage closes on decided content only.

## Writing it

Only `skills/skaileup/scripts/walkthrough.py` writes the file (python3 with PyYAML, `--root <project>`, default `.`); it validates against `tree/01_meta/walkthrough.schema.json` before every write.

1. **Open the walk.** `walkthrough.py init` writes all four stages `open` and an empty `history` when the file is absent, and leaves an existing file as it is. Concept content already in the project, a template's included, approves nothing.
2. **Read where the walk stands.** `walkthrough.py status` prints one row per stage — its stored status, each required check as `ok`, `missing`, `unapproved` or `open markers`, and the next skill; `walkthrough.py next` prints `<stage>: <skill> → <first failing check>` for the first stage neither approved nor waived, or `build: all stages settled`.
3. **Approve on the user's own yes.** `walkthrough.py approve <stage> --source "user, YYYY-MM-DD"` runs only in the turn that carries the user's explicit yes to that stage's checkpoint. It refuses (exit 2) and lists every blocker while an earlier stage is open or a check of this stage fails.
4. **Waive with a decision record.** `walkthrough.py waive <stage> --dr DR-<n> --source "user, YYYY-MM-DD"` needs a `DR-<n>` the user agreed to, already in `_concept/10_blueprint/decisions.md` (`tree/10_blueprint/decisions.md § Writing it`); it refuses (exit 2) an id the log does not hold. A `depth` the user chose thins what a stage writes and skips no stage; skipping one is this waive.
5. **Reopen on change.** On any user request that changes an approved stage, `walkthrough.py reopen <stage> --reason "<the user's words>"` runs before the concept or the code changes: it sets that stage and every later one `open` and appends one `reopened` event per stage it changed.
6. **Gate the build.** `walkthrough.py gate build` exits 0 once `frame`, `look` and `data` are approved or waived, else 3 naming the open stage and its next skill and check. `walkthrough.py gate feature <featureset>/<feature>` adds that `_concept/05_features/<featureset>/<feature>.md` is approved and each screen id in its frontmatter `screens:` has an approved `_concept/07_screens/<id>.md`.
7. **Guard the project.** `walkthrough.py guard --write` writes the marked `skaileup:walkthrough` section into the project's `AGENTS.md` (else `CLAUDE.md`, else a new `AGENTS.md`), replacing the section when present, so the host's own planning runs `gate build` first.

## Checks

- The file validates against `tree/01_meta/walkthrough.schema.json`.
- Every `approved` stage has an `approved` date and a `source`.
- Every `waived` stage has a `dr` that exists in `_concept/10_blueprint/decisions.md`.
- No stage is approved while an earlier one is `open`.
