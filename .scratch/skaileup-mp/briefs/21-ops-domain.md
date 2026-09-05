# Recon: 21 — the `ops` domain

Evidence only, nothing ruled. Paths relative to `ai-assets-skaileup/skaileup/` unless prefixed.
**Ticket 19 resolved mid-recon** (`-mp` `3b21cfe`) — `spec-feature` is **written, 83 lines**, so
the delta below is against real text. Out-of-scope four confirmed present, not analysed; **flag:**
`map.md:395-399` names only two of them while ticket 21 rules four, and all four are the only
`ops-*` nodes in `appbuilder-complex.flow.yaml` (`:304-344`, edges `:506-523`) — cutting them
dangles that flow's tail and no ticket owns the repair.

## Per-skill table
**Ticket's numbers all verified correct** — 621/316/307/289/184/181/171/138, sum 2,207; four on
zero flow nodes. One correction to its framing: sidecars are unmeasured —
`10_add-feature/references/` 284 + `CLI.md` 22, `08_review/references/` 303 + `CLI.md` 33,
`07_eval-product/references/` 59. **Real domain weight 2,908 lines.**
| skill | lines | flow node | writes | reads | named by (excl. `14_ops/DOMAIN.md`, which ticket 05 deletes) |
|---|---|---|---|---|---|
| `ops-reverse-engineer` | 621 | 1 — `skaileup-concept-reverse:68` | `brief`/`goals`/`comparable`, `brand/{identity,tokens}`, `techstack`, `features/`, `screens/`, `datamodel/{model.dbml,model.json,seed.json}` (fm `:20-29`) | repo source only; no `_concept/` reads | `contracts/frontmatter.md:161`; `SOUL.md:114` |
| `ops-add-feature` | 316 | **0** | `features/` + cascades `stories.yaml`, `techstack.md`, `architecture.md`, `datamodel/*`, `screens/` (fm `:39-45`) | brief, all features, 10 optional artifacts, `_implementation/progress.yaml` | `SOUL.md:113`; `04_product-spec/DOMAIN.md:29` (dies) |
| `ops-review` | 307 | 2 — `skaileup-concept-only:280`, `quality-gate:111` | `_concept/quality.yaml` | `_concept/**/*.md`, `model.json`, `feature_map.json`, `PLANS.md` | `contracts/concept_structure.md:55`; `SOUL.md:115`; `12_trace/SKILL.md:68`; `11_reverse-engineer/SKILL.md:353,536`; `05_mockup-walkthrough/DOMAIN.md:31` (dies) |
| `ops-sync` | 289 | 1 — `quality-gate:122` | features + screens frontmatter, `feature_map.json` | features, screens, `model.json`, `feature_map.json` | `12_impl-slice/07_commit/SKILL.md:147` (style citation only); `12_trace/SKILL.md:68` |
| `ops-trace` | 184 | 1 — `quality-gate:100` | `_implementation/trace.yaml` (only file) | features fm (`slice_ref`/`commits`/`source_files`), `slices/*/index.md`, `*.ac.md`, `eval-feature/*.yaml`, `docs/`, `git ls-files` | `contracts/concept_structure.md:285`; `contracts/frontmatter.md:171`; `contracts/acceptance_criteria.md:251`; `07_eval-product/SKILL.md:43,109,114` |
| `ops-eval-concept` | 181 | **0** | `_concept/eval-concept.yaml` | brief, features, screens, `model.json`, journeys, techstack | **`contracts/evaluator.md:3` only** — a list of who reads the contract. No skill body names it. |
| `ops-eval-product` | 171 | **0** | `_implementation/eval-product.yaml` | brief, journeys, `eval-feature/*.yaml`, `trace.yaml`, brand tokens | `contracts/evaluator.md:4`; `12_trace/SKILL.md:57,62`; `quality-gate.md:21` (prose, no node) |
| `ops-eval-feature` | 138 | **0** | `_implementation/eval-feature/{group}.yaml` | features, screens, journeys + **the running app** | `contracts/evaluator.md:4`; `13_impl-quality/13_review-feature/SKILL.md:70`; `12_trace/SKILL.md:69,106`; `07_eval-product/SKILL.md:114` |

### Zero-caller check
- `ops-add-feature`: one live caller — `SOUL.md:113`, the orchestrator routing table ticket 13's
  `ops-triage` replaces. No flow, no contract, no skill body.
- `ops-eval-concept`: **zero callers of any kind.** 181 lines nothing invokes.
- `ops-eval-feature`/`-product`: no flow node, but real in-body callers; with `ops-trace` they form
  a closed cycle entered through one node — `quality-gate`'s `ops-trace`.
- **`contracts/evaluator.md`:** **zero in-body readers in `-mp`** (only `docs/adr/0004` lists it).
  Old repo: 5 named readers, 4 real — `13_impl-quality/02_eval-code/SKILL.md:117` the only
  non-`ops` one, `impl-quality-audit` named in the header and never reading it. Drop the three
  `ops-eval-*` and it survives on `eval-code` alone → ticket 17's call.

### Host coupling nobody has flagged
`forge-concept/shared/flow-phases.ts:24-25` hardcodes four of these names — `s.startsWith("ops-eval")`
and `s === "ops-review" || s === "ops-sync"` → `"review"` lane (tested `flow-phases.test.ts:29-32`).
Ticket 04's per-node `data.phase` makes the fallback unused, but this is the only place the host
knows an `ops-*` name. And `ops-trace`'s output has a host reader: `review.vue:21-22` +
`server/utils/review-coverage.ts:100,112,122,131` read `<projectRoot>/_implementation/{trace.yaml,
acceptance_criteria/,review/}` and `<conceptDir>/experience/features` at literal paths — **all four
moved by ADR 0007.**

## quality/ops boundary cases

Ticket 04's line: `quality` inspects `src/`, `ops` inspects `_concept/`.
| skill | inspects | verdict |
|---|---|---|
| `ops-review` | `_concept/` only — `08_review/SKILL.md:99` Context Budget says **"Never load: Source code"**; `:71` "Auditing source code — use `audit` quality skill instead" | `ops`, states the boundary itself |
| `ops-sync` | `_concept/` frontmatter only; `:69` "For code-level fixes — use `audit`" | `ops`, unambiguous |
| `ops-eval-concept` | `_concept/` artifacts only (`05_eval-concept/SKILL.md:57-63`) | `ops` — but it is an *evaluator*, sharing stance+laws with `impl-quality-eval-code`; the line splits a family |
| `ops-add-feature` | `_concept/`, but **writes** it | neither side — the line is about inspection, this is a writer |
| `ops-reverse-engineer` | reads `src/`, writes `_concept/` | **boundary case** — reads what `quality` owns, writes what `ops` owns |
| `ops-eval-feature` | **the running app** — `:63` "MUST actually interact with the running app — no static code inspection" | **wrong side.** `13_impl-quality/13_review-feature/SKILL.md:70` already points at it; ticket 17 owns `review-feature` |
| `ops-eval-product` | running app + brief + `trace.yaml` | **wrong side**, same argument |
| `ops-trace` | both — features frontmatter **and** `git ls-files` (`12_trace/SKILL.md:36`) | **spans the line by design**; ticket 04 has no answer for a reconciler |

Plausibly ticket 17's: `ops-eval-feature`, `ops-eval-product`; arguably `ops-eval-concept`, the
concept-side twin of `impl-quality-ready` — a skill 17 already flags as on the wrong side of the
same line (`issues/17-quality-domain.md:26`).

## `ops-reverse-engineer` breakdown

622 lines: frontmatter `:1-80`, body `:81-621`, with **121 fenced and 61 table lines**.
| block | lines | what it is |
|---|---|---|
| frontmatter `:1-80` | 80 | tags + 5 `inputs_*` dialog fields (ticket 09 keeps these in frontmatter) |
| Overview · When to/NOT · Prereq · Shared Contracts · Context Budget `:84-146` | 63 | ticket 03 deletes all six |
| Step 1 Validate + Step 2 Repo Discovery `:149-184` | 38 | **irreducible** — the actual procedure |
| Step 3 Overview `:185-235` | 51 | 36 procedure + 15 fence = `brief.md` template; restates `concept-brief` |
| Step 4 Techstack `:236-283` | 48 | 10-row detection table (nuxt/next/prisma/drizzle/…) + `techstack.md` template; restates `impl-architecture-techstack` |
| Step 5 Features `:284-338` | 55 | 12 fence (feature template) + 25-line `data_entities: []` / subagent-dispatch rule |
| `## Description` / `## Key Capabilities` `:339-368` | 30 | **structural defect** — two `##` headings + a 23-line fence sitting *inside* the workflow between Steps 5 and 6; mis-levelled tail of Step 5's template |
| Step 6 Datamodel `:369-420` | 52 | 8-source ORM priority list + type-mapping table; restates `impl-architecture-datamodel` + `contracts/semantic_types.md` |
| Step 7 Brand `:421-489` | 69 | **36 fence lines**; tailwind/CSS-var/token recipes + `identity.md`+`tokens.json` templates; restates `design-brand-visual` |
| Step 8 Screens `:490-533` | 44 | per-framework page globs (Nuxt/Next/Vue/React/Django/Rails) + screen template; restates `experience-screens` |
| Step 9 Confidence `:534-554` | 21 | **irreducible** — `extracted`/`inferred`/`needs_review` grading is this skill's own invention |
| Report · Outputs · Depth · Common Mistakes `:555-621` | 67 | boilerplate; 41 of it table |

Split: **~90 lines genuine procedure** (Steps 1, 2, 9 + the `data_entities` rule) · **~210
stack-specific detection detail** (Steps 4, 6, 7, 8) · **~120 restating other skills' output
templates** · **~130 ticket-03 boilerplate** · 80 frontmatter. Against the 140 ceiling: the four
detection blocks are the obvious `references/detection/{techstack,datamodel,brand,screens}.md`;
the output templates are not `references/` material at all — they belong to the skills that own
those artifacts. Ticket 08's re-point mechanically removes Step 8 and most of Step 5
(`spec-feature` is sole writer of `05_features/`+`07_screens/`, `SKILL.md:20-22`), but **not
Steps 4, 6, 7**, which write `10_blueprint/` and `03_brand/` — writers ticket 08 left in place.

## `ops-add-feature` vs `spec-feature` delta
Against `-mp/skills/spec-feature/SKILL.md` as landed (83 lines, 9 steps).

**Already covered by `spec-feature`:** the modification branch — step 1 *"A glob that already
resolves means this is a refinement of an existing spec: load it and say so before asking
anything"*, step 8 *"An existing file gets its diff shown and its own answer"*; approval-before-write
(step 8 ≈ `add-feature`'s three CHECKPOINTs); bidirectional registration (step 7). **Not** carried:
`add-feature:257` *"Preserve existing `screens:` and `data_entities:` arrays."* **Not in
`spec-feature` at all:**

**1 — the cascade (`add-feature` STEP 5, `:246-268`):**
> "Follow cascade order from references/cascade_rules.md: 1. Journeys → 2. Tech Stack →
> 3. Architecture → 4. Data Model → 5. Screens" … "NEVER cascade to artifacts that don't already exist"

Change propagation over four artifacts `spec-feature` never touches (`04_journeys/`, `techstack.md`,
`architecture.md`, `datamodel/*`), each write conditional on prior existence; 162 lines of
`references/cascade_rules.md` behind it. `spec-feature`'s only writes outside
`05_features/`/`07_screens/`/`08_dossiers/` are `10_blueprint/{glossary,decisions}.md` (step 3).

**2 — impact assessment before any write (STEP 3, `:231-243`, checkpointed):**
> "Journeys: new story / update downstream links · Tech stack: new dependency or no change ·
> Architecture: new module / new integration / no change · Data model: new entities / new fields /
> new relation / no change · Screens: new screen / update existing / no change"

`spec-feature` grills about the feature; this grills the concept about the blast radius.
**3 — the already-built tail (STEP 7, `:288-292`):** *"IF `_implementation/progress.yaml` exists …
'Do you want to implement this feature now, or save it for the next implementation run?' … IF no →
note the feature in PLANS.md as implementation backlog"* — the only build-aware branch. `PLANS.md`
is ticket 18's open call (`issues/18-…:32` names `ops-*` among its readers).

**4 — inline self-quality-gate (STEP 6, `:270-278`):** verifies its own cross-references
bidirectional, entity naming, `seed.json` casing — i.e. runs `ops-review`'s checks.

## `ops-review` / `ops-sync` and the ADR 0007 tree
Overlap is direct: `08_review/SKILL.md:200-210` STEP 4 is the same four checks as
`09_sync/SKILL.md:112-127` Steps 2-3, and `ops-sync:52-54` states the difference itself — *"safer
than `review`'s gardening mode because every change is previewed."* Handoff is one-way
(`ops-review:113` → sync; `ops-sync:78` → review), matching `quality-gate.flow.yaml:152-154`.
`ops-review` also owns frontmatter compliance, golden principles, entropy and the score;
`ops-sync` owns none of those.

**ADR 0007 (`-mp/contracts/concept_structure.md`) changes what "broken cross-reference" means:**
- **`_concept/quality.yaml` is not in the tree.** Root files are `brief`/`goals`/`comparable.md`
  only (`:16-18`); roots are `01_meta`…`11_build`, and `11_build/` holds `slices/<slice_id>/` +
  `decisions.md` (`:90-92`). Same for `eval-concept.yaml`, `eval-feature/{group}.yaml`,
  `eval-product.yaml`, `trace.yaml` — **all five inspection outputs write to deleted paths.**
  Ticket 08 handed the landing site to **ticket 17**, which owns none of the five skills.
- **`ops-sync` Step 5 "Check Group Alignment" (`:161-171`) checks a thing that no longer exists** —
  it matches `features/<NN_group>/` numbers to `screens/<NN_group>/` numbers, while ADR 0007 groups
  features by `<featureset>` and screens by `<feature_slug>` (`:65-73`) with no prefix below the
  first level (`:98-100`). Same collision ticket 08 found in `design-feature`'s scan.
- **The drift `ops-sync` repairs may be unreachable.** W1 makes `spec-feature` sole writer of both
  trees and its step 7 registers both directions in one pass — feature↔screen divergence was a
  two-writer artefact. What survives is deletion and manual-edit drift (`ops-sync:59-64`) and the
  `feature_map.json` ↔ `data_entities:` half, whose two writers ticket 08 left separate.
- **`ops-trace`'s back-link has a writer — but the cardinality flipped.**
  `-mp/skills/build-implement/SKILL.md:55-59` patches the feature spec with slice ref, SHAs and
  source files, so ticket 07's back-link survives. But ticket 19 ruled **`slice_id` is no longer
  `feature_slug` — one dossier per *slice*, several per feature.** `ops-trace` Direction 1 asserts
  one frozen slice dossier per feature row via a singular `slice_ref`
  (`-mp/contracts/artifact_frontmatter.md:138`, `feedback_loop.md:110`), and both still write the
  pre-0007 path `_implementation/slices/<slice_id>/` and still credit the deleted skill
  `impl-slice-commit`.
- **`ops-trace` also lost an input.** Ticket 19: the acceptance-criteria ledger
  `_implementation/acceptance_criteria/<group>/<slug>.ac.md` *"has no home and does not port"* —
  handed to ticket 17. That is one of `ops-trace`'s four evidence sources
  (`12_trace/SKILL.md:33`), and `contracts/acceptance_criteria.md:251` still names `ops-trace` as
  its reader.

## Open questions for the human
1. `ops-eval-concept` has **zero callers of any kind** — 181 lines nothing invokes. What kept it?
2. The three `ops-eval-*` + `ops-trace` are a closed cycle entered through one flow node. Pipeline
   or leftover? And if two inspect the running app, why are they `ops` and not 17's?
3. `contracts/evaluator.md` has zero in-body readers in `-mp`; 21 and 17 each hold half its
   readership and neither is told. Who rules first?
4. **Five inspection outputs have no home in ADR 0007's tree**, handed to a ticket owning none of
   the five skills. Does 21 pick the paths, or 17?
5. `ops-trace` now faces feature→**N** slices, and its `.ac.md` input went to 17 with no
   replacement. Is the matrix still buildable, and by whom?
6. `ops-sync`'s group-alignment check is dead and its feature↔screen half arguably unreachable
   under W1. Is what remains a skill, or `ops-review` STEP 4 with a preview?
7. `ops-add-feature`'s only caller is the `SOUL.md` table **13 replaces**, and `spec-feature`
   already handles refinement. Does the cascade go inside it, become a skill, or die?
8. `ops-reverse-engineer` writes `10_blueprint/` + `03_brand/`, not covered by 08's re-point. Call
   those writers, or keep its own detection recipes?
9. `forge-concept`'s review page reads two literals ADR 0007 moves — is `ops-trace`'s only external
   consumer broken on purpose?
10. `appbuilder-complex.flow.yaml:304-344` dangles once the `project-*` four go, and `map.md` lists
    only two of them as out of scope. Which ticket repairs that flow?
