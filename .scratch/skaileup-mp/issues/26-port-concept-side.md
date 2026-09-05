# 26: Port the concept side — write the 10 skills

**Type:** task
**Blocked by:** None (08, 19, 21 resolved)
**Status:** resolved

## Question

Nothing to decide — tickets 08 and 21 settled the shape, this writes it. Same relation 14 has
to 06, 19 to 07, and 23 to 17. Graduated from the map's *"the port itself, per domain"* fog by
ticket 21, which added two skills to the group and left the concept side as the only sized
domain with no port ticket.

**Ten skills.** Nine from ticket 08 (of which `spec-feature` already landed in ticket 19 and is
not rewritten here), plus two from ticket 21:

| skill | from | note |
|---|---|---|
| `concept-brief` | `concept-brief` + `goals` + `comparable` | ticket 03's worked port (289 → 80) lives in `docs/examples/`; that draft predates ADR 0007 |
| `concept-onboard` | `concept-grounding-onboard` + `seeds` + mp's `to-questionnaire` | writes `02_grounding/onboarding/` |
| `concept-research` | `concept-grounding-research` + `design-inspiration` + mp's `research` | writes `02_grounding/research/` |
| `concept-reverse` | `ops-reverse-engineer` (621 lines) | **ticket 21** — thin orchestrator, see below |
| `design-brand` | `design-brand-visual` | `design-brand-voice` does not port (ticket 08) |
| `experience-journeys` | `experience-journeys` | writes `04_journeys/stories.yaml` |
| `experience-behaviors` | `experience-behaviors` | `.allium` dies; markdown state tables (ticket 08) |
| `experience-shell` | `experience-screens`, narrowed | shell only — the loop owns screens (W1) |
| `spec-featuresets` | `product-spec-features`, narrowed | featureset grouping; `spec-feature` writes the specs |
| `ops-review` | `ops-review` + `sync` + `trace` + `ready` + `audit` Phase 2 | **ticket 21** — see below |

Constraints, all already settled: `SKILL.md` under the **140-line ceiling** (ticket 03), dir name
== `name:` character for character (ticket 04), **no `MUST`/`NEVER` block** — constraints stated
positively at the step they bind — `data.phase` declared by the flows and not by the name, and
**every path written against ADR 0007's tree**, not the pre-0007 one still present in several
contracts (ticket 19 found four; ticket 16 owns the sweep).

## The two skills from ticket 21

**`concept-reverse`** is ticket 02's mechanism carried the whole way: it keeps only Steps 1, 2 and
9 of the old 621-line skill — validate, repo discovery, and the `extracted`/`inferred`/
`needs_review` confidence grading that is its own invention — and **calls** `concept-brief`,
`architecture-techstack`, `architecture-datamodel`, `design-brand`, `experience-shell` and the
`spec-feature` loop rather than restating their output templates. The ~210 lines of stack-specific
detection (Nuxt/Next/Prisma/Drizzle globs, the 8-source ORM priority list, tailwind/CSS-var token
recipes, per-framework page globs) are the one thing no other skill owns and become
`references/detection/{techstack,datamodel,brand,screens}.md`. Fix in the port: the structural
defect at `11_reverse-engineer/SKILL.md:339-368` — two `##` headings and a 23-line fence sitting
inside the workflow between Steps 5 and 6.

**`ops-review`** is four skills merged, ~900 source lines into the 140 ceiling, and ticket 21
flagged this as the port's real risk. It writes **`11_build/review.yaml`** (verdict + score +
findings) and **`11_build/trace.yaml`** (the feature → slice → commits → code matrix). Every
finding **names the skill that fixes it** — that is `ready`'s remediation command, generalised.
The trace half is a **one-to-many join**: ticket 19 decoupled `slice_id` from `feature_slug`, so a
feature has N slices, and the old singular `slice_ref` lookup is wrong. Dead work not to carry:
`ops-sync`'s group-alignment check (matches a shape ADR 0007 removed) and most of its
feature↔screen repair (unreachable once `spec-feature` became sole writer of both trees).

**Fallbacks, in order, if `ops-review` does not fit:** a `references/checks.md`; failing that, a
split back into `ops-review` (concept-tree integrity) and `ops-trace` (build coverage), which is
the seam ticket 21 crossed. Report which one was needed — it is the first real test of whether
the 140 ceiling holds for a merge this size.

## Also in scope

- **~4 lines into the landed `spec-feature`** (ticket 21, from `ops-add-feature`): the
  blast-radius grill emitting which of `04_journeys/`, `techstack.md`, `architecture.md`,
  `datamodel/*` and `07_screens/` need their owner re-run; the *"preserve existing `screens:` and
  `data_entities:` arrays"* data-loss guard on the refinement branch; and one line naming
  `build-plan` when the project is already built. **The cascade itself does not port.**
- **`contracts/grill_bank.md`** (ticket 09, 0 in-body readers) survives only if one of these
  skills reads it at a step. Otherwise delete.

## Answer

**Twelve skills, 926 lines of `SKILL.md`, every one under the ceiling — and `ops-review` did
not need a fallback.** Eleven written new plus the edit into the landed `spec-feature`, on
`-mp` `main`, uncommitted. `scripts/check.py`: 24 skills, 0 errors; `test_check.py` 31 passed.

| skill | lines | writes |
|---|---|---|
| `concept-scope` | 82 | `01_meta/scope.yaml` |
| `concept-brief` | 69 | `brief.md` · `goals.md` · `comparable.md` |
| `concept-onboard` | 74 | `02_grounding/onboarding/{onboarding.yaml,answers.json,questions.md}` |
| `concept-research` | 65 | `02_grounding/research/` · `02_grounding/findings/` |
| `concept-reverse` | 97 | brief trio · `10_blueprint/techstack.md` · `03_brand/` · `02_grounding/findings/{routes,screens,datamodel}.md` |
| `design-brand` | 66 | `03_brand/` |
| `experience-journeys` | 65 | `04_journeys/stories.yaml` |
| `experience-behaviors` | 62 | `06_behaviors/<featureset>.md` |
| `experience-shell` | 67 | `07_screens/shell.md` |
| `spec-featuresets` | 69 | `05_features/featuresets.md` |
| `ops-review` | 107 | `11_build/review.yaml` + `11_build/trace.yaml` |
| `spec-feature` | 90 → 103 | (edited) |

Plus `skills/concept-reverse/references/detection/{techstack,datamodel,brand,screens}.md`
(164 lines) — the globs, the 8-source ORM priority list, the signal→value tables and the
per-framework page globs, which is the one body of knowledge no other skill owns.

### `ops-review`: the ceiling held, at fallback zero

**107 of 140 as a single file.** No `references/checks.md`, no split into `ops-review` +
`ops-trace`. ~900 source lines across four skills compressed without losing a check, and the
reason is worth recording because it is the general answer, not luck: **the four skills were
four implementations of one walk over one tree, and almost all of their bulk was restating
what a contract already owns.** `evaluator.md` owns the stance, the flag shape and the
verdict tiers; `golden_principles.md` owns the naming rules; `artifact_frontmatter.md` owns
the per-type fields; `feedback_loop.md` owns the link protocol; `concept_structure.md` owns
the tree. Twelve steps sequencing those four contracts is the whole skill. Two more sources
of shrink: `ops-sync`'s audit/garden mode split collapsed to one mode with a diff shown
before any repair (ticket 21 was right that "every change is previewed" is a step, not a
boundary), and ticket 21's dead work — group alignment, the feature↔screen repair W1 made
unreachable — simply is not there. **The ceiling is not under pressure from merge size; it is
under pressure from restating contracts.** That is the finding for the remaining ports.

`ops-review` also gives `golden_principles.md` and `evaluator.md` the readers
`contracts/README.md` keeps them on notice for — both are read at a step, so both survive.
Severities use `evaluator.md`'s own `blocking|warning`, not 17's `critical|high`; ticket 23
owns that contract's vocabulary and this port did not pre-empt it.

### Judgment calls

- **`spec-featuresets` writes `05_features/featuresets.md`.** The narrowed skill had no named
  artifact and a skill that writes nothing gives the loop no input. A root file under
  `05_features/` rather than `<featureset>/index.md` keeps it out of `spec-feature`'s
  `05_features/<featureset>/<slug>.md` glob. Added to `concept_structure.md`.
- **`concept-scope` records the flow rather than deriving it.** Ticket 10 stripped flow choice
  because the wizard's profile *is* the flow, but the schema still carries `flow` and the
  orchestrator path has no wizard. Resolved as: the flow is given, this skill writes it down,
  and derives it only where nothing has chosen — with the four-flow table as the whole
  vocabulary.
- **`concept-onboard` confirms `project_type` rather than collecting it.** `concept-scope`
  owns the value; onboard owns the preferences-with-confidence (`locked|preferred|open`), the
  existing-brand answer, `mockup.renderer` (a real reader in `mockup-walkthrough`), the seed
  inventory, and `questions.md` (mp's `to-questionnaire`, aimed at the gap).
- **The seed inventory has no file of its own.** `concept.yaml` died with ADR 0007 and a
  standalone seed manifest would have no reader, so the classification lands in
  `onboarding.yaml`, which eleven skills already read. One line of
  `concept_structure.md` changed.
- **`concept-reverse` writes brief/goals/comparable and the brand.** Ticket 10 names the seven
  nodes that follow it; `concept-brief` and `design-brand` are not among them, so the
  README-derived brief and the theme-derived tokens are its own detection output. Everything
  a following node owns — features, screens, journeys, the model — goes to
  `02_grounding/findings/` as *evidence*, which is what keeps
  `references/detection/{screens,datamodel}.md` load-bearing while the skill writes neither
  tree. The structural defect is gone: no headings and no fences inside the step list.
- **`experience-behaviors` writes markdown transition tables**, per ticket 08. Stated
  positively: a grammar with no parser drifts from what it claims to describe.
- **`experience-shell` names nav targets that do not resolve yet**, because it runs before the
  feature loop writes any screen. Called out at the step; the renderers' `unresolved_target`
  soft-fail already covers it.

### `contracts/grill_bank.md` — dead, and already gone

It is **not in `-mp/contracts/`**; it was never ported. No skill written here reads it, and
wiring one would be dishonest: its **9 pillars are already inlined verbatim at
`spec-feature:42-54`** (state transitions, boundary inputs, concurrency, the role × action
table, persistence, errors, cross-feature data — the pillar list, at the step it binds, which
is exactly ADR 0003's rule), and its other half (tone, anti-patterns, one question at a time)
belongs to the globally-installed `grilling` skill that `spec-feature` calls. Ticket 09
handed it to "the absorbed `grilling` skill"; that skill turned out to be a global install,
not a `-mp` asset, so there is nothing to hand it to. **Closed as dead.**

### `CONTEXT.md`

`tier` was already retired by `ac056b2` — Tier gone, Flow carrying the sizing sense — so that
half needed nothing. The live conflict was elsewhere: **Profile** was defined as "a project's
type" with `_Avoid_: project type`, while ticket 10's pinned schema key is `project_type` and
the assets live at `profiles/<project_type>.yaml`. Split into two entries: **Project type**
(what is being built; the word matches the key the machine reads) and **Profile** (the
collection asset that describes one type). Same move ADR 0005 already made when "tech stack
profile" became **template** — `profile` was carrying two meanings.

### Also changed

- **`profiles/*.yaml` rewritten** (483 → 97 lines). They had zero readers and `concept-scope`
  is the first; wiring a read to them as they stood would have pointed a step at a file
  declaring **an entirely different artifact tree** (`commands/`, `toolchain/`, `data/`) plus
  the dead `artifacts.yaml` registry shape. Trimmed to `profile` · `description` · `version` ·
  `not_grown`, with `prototype` → `mockup`/`mockup-storybook`, and `goals`/`comparable`
  dropped from the exclusions because `concept-brief` writes all three root files in one run,
  so excluding one of them is not actionable.
- **`contracts/concept_structure.md`**: `05_features/featuresets.md`, `11_build/review.yaml`,
  `11_build/trace.yaml`, the seed inventory in `onboarding.yaml`, detection evidence under
  `findings/`. Merged around a concurrent sibling session's edits to the same file.

### For later tickets

1. **`11_build/review.yaml` sits one letter from `11_build/reviews/<feature_slug>.yaml`** —
   ticket 21 pinned the first, ticket 17 the second, and neither saw the other. Not a path
   collision, but a reader scanning `11_build/` cannot tell them apart. Worth a rename ticket.
2. **`contracts/artifact_frontmatter.md` is still wholly on pre-0007 paths** —
   `discovery/brief.md`, `experience/features/<group>/`, `_implementation/slices/`. Six of
   these skills cite it for *shape* and `concept_structure.md` for *paths*, the split ticket
   19 established, but a reader who follows its paths lands off-tree. Ticket 16's sweep
   (`e63316c`) did not reach it. Same for `skills/mockup-walkthrough/SKILL.md` step 1, which
   still says `_grounding/onboarding/onboarding.yaml` and `_meta/scope.yaml` unnumbered while
   its own frontmatter is correct.
3. **`contracts/README.md`'s "no reader in this repo yet" rows for `golden_principles.md` and
   `evaluator.md` are now false** — `ops-review` reads both at a step. Left alone: another
   session owns that file.
4. **`05_features/featuresets.md` is caught by `mockup-walkthrough`'s `05_features/**/*.md`
   glob** and would appear in the manifest as a phantom feature. One line in that skill.

### Register — forge-concept

**One entry moves from latent to live.** ADR 0011 recorded that the input dialog reads its
collected values from `_concept/_grounding/<skillId>/input.json`
(`resolver/src/validator.ts:107`) — a directory ADR 0007 renamed to `02_grounding/` — and that
"the first `-mp` skill with `inputs_optional` inherits the clash". **Six of these skills
declare `inputs_optional`** (`concept-scope`, `concept-brief`, `concept-onboard`,
`concept-research`, `design-brand`, `concept-reverse`, `spec-featuresets`), so the host now
writes into a directory the artifact tree does not have. Nothing breaks, because **no skill
body names that path** — deliberately: each treats dialog answers as inputs that arrive with
the run rather than as a file to read. The workaround is the silence; the fix is the host's.

No other new constraint. `phaseForSkill`'s surviving `ops-review` entry still lands in the
`review` lane, unchanged.

### Deliberately not done

- **No flow YAMLs** — ticket 28's.
- **No `architecture-{techstack,system,datamodel}` or `build-scaffold`** — ticket 25's; these
  skills name them as owners but do not write them.
- **`design-brand-voice` and `experience-components` do not port** — ticket 08's ruling.
- **`contracts/README.md`, `evaluator.md`, `acceptance_criteria.md`, `templates/`,
  `build-plan`, `build-implement`, `quality-*`** — concurrent sibling sessions own them.

## Note from ticket 10

**This ticket gains a twelfth skill, and it is the most-used one in the collection.**

- **`concept-scope`** (renamed from `skaileup-scope-scope-project`) was owned by no ticket
  despite being the entry node of 7 flows and the sole writer of `_concept/01_meta/scope.yaml`.
  Ruled by ticket 10, ported here. It **no longer chooses the flow** — on the forge-concept
  path the wizard's profile *is* the flow (`profiles.get.ts` keys profiles by flow id) — so it
  narrows to writing scope plus resolving `project_type`. It cannot die: the orchestrator path
  has no wizard and eleven skills read what it writes.
  New schema: **`flow` · `project_type` · `reasoning` · `signals` · `chosen_at`**.
  Dropped: `flow_to_run` (a file naming the flow that wrote it is a cycle), `shape` (folded
  into `project_type`), `override`, `chosen_by`. `project_type` resolves against root-level
  `profiles/<project_type>.yaml`, which is where `cli` landed when ticket 10 deleted the
  `appbuilder-cli` flow.
- **`tier` is gone from the vocabulary.** Ticket 10 unified `tier` and `flow` into one word;
  `CONTEXT.md` loses its **Tier** entry and **Flow** absorbs the sizing sense. Every skill that
  read `scope.tier` reads `scope.flow`. **`CONTEXT.md` needs this edit** — flag it if this
  ticket is not the right place.
- **`concept-reverse` nodes its writers, it does not call them.** Ticket 21 described it as a
  thin orchestrator calling five writers, but the flow also nodes them, so doing both runs each
  twice. It keeps repo discovery, stack detection (`references/detection/`) and confidence
  grading, and writes **only detection output plus grounding**; `experience-journeys`,
  `spec-featuresets`, `experience-shell`, `spec-feature`, `architecture-{system,datamodel}` and
  `quality-standards` run as visible flow nodes after it.
- **`spec-feature` carries the per-feature loop statement in its body.** The graph shows one
  iteration; the host honours only `type: flow` edges and has never expressed iteration
  (`appbuilder-standard:11-12` is a comment). Same for `build-implement` on the build side.
- **`spec-feature` is the sole screen writer, and the mockup now runs after it.** In today's
  order the mockup would render one shell and nothing else. `experience-shell` writes
  `07_screens/00_layout/shell.md` and shared patterns only.
- **`concept-onboard` is a node in all four flows, including `appbuilder-mvp`** (which has no
  onboarding node today): `architecture-techstack` and `build-scaffold` both need
  `project_type`, and without the node mvp silently defaults to web-app.
- **`experience-behaviors` runs after `spec-featuresets`**, matching its own gate. Two flows
  had the inversion, not the one ticket 08 named.
