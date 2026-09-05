# 21: The `ops` domain — eight skills nobody owned

**Type:** grilling
**Blocked by:** None (04, 07, 08 resolved)
**Status:** resolved

## Question

Graduated from ticket 08, which found the gap the same way ticket 07 found 17 and 18: the
map's tickets covered the mockup domains (06/14), the slice loops (07), the concept half (08),
the contracts (09), quality (17) and architecture/build (18) — and `14_ops/` fell between them.

`14_ops/` holds **12 skills**. Four are already out of scope (the multi-product umbrella:
`project-overview`, `project-subsystem-map`, `project-integration`, `project-review` — ruled
out by ticket 09 on the same argument as `15_demo`). The other **eight, 2,207 lines**, are
owned by no ticket:

| skill | lines | flow refs |
|---|---|---|
| `ops-reverse-engineer` | 621 | 1 |
| `ops-add-feature` | 316 | **0** |
| `ops-review` | 307 | 2 |
| `ops-sync` | 289 | 1 |
| `ops-trace` | 184 | 1 |
| `ops-eval-concept` | 181 | **0** |
| `ops-eval-product` | 171 | **0** |
| `ops-eval-feature` | 138 | **0** |

Ticket 13 only *adds* to this domain (a triage on-ramp); ticket 18 mentions these skills once,
as `PLANS.md` readers.

Decide:

- The surviving set, and for each of the eight: merge / step-inside-another / dies.
- **The three `eval-*` are on zero flows** and total 490 lines. Ticket 09 kept
  `contracts/evaluator.md`; check whether it has a reader left after this ticket rules.
- **`ops-review` and `ops-sync` against each other.** Ticket 08 removed `concept.yaml`
  (the artifact-status manifest) — `ops-review` writes `quality.yaml`, `ops-sync` repairs
  cross-references. Both inspect a tree that just changed shape.
- **`ops-trace`** walks feature → slice → commits → code via `slice_ref` frontmatter written
  on freeze. Ticket 07 kept that back-link; confirm it still has a writer.
- Where `ops-*` sits against the global `code-review` and `diagnosing-bugs` installs, the
  same question ticket 17 asks of `quality`.
- Ticket 04's `quality`/`ops` line is the artifact under inspection: `quality` checks `src/`,
  `ops` checks `_concept/`. Ticket 08 moved the inspection *outputs* under `11_build/` — check
  that does not move the skills across the line.

## Note from ticket 08

Two are already settled at the boundary, because they touch the tree ticket 08 redrew:

- **`ops-add-feature` is `spec-feature` entered on an existing project**, not a third writer
  into `05_features/`. It declared `produces: _concept/experience/features` alongside
  `product-spec-features` and `concept-slice-design-feature`; ticket 08 left one writer per
  artifact, and adding a feature to a live project is the same job as specifying one.
- **`ops-reverse-engineer` re-points** to `experience-shell` plus a `spec-feature` loop. It was
  the terminal-node consumer of `experience-screens`, which ticket 08 narrowed to the shell.

Everything else in the eight is open.

## Answer

**8 skills / 2,207 lines (2,908 with sidecars) → 1 skill in `ops`, 1 renamed out of it, 1 handed
to `quality`, 5 dead.** The domain's own line — ticket 04's *"`quality` checks `src/`, `ops`
checks `_concept/`"* — turned out to place only two of the eight, and the ruling below is mostly
the consequence of applying it honestly to the other six.

| | |
|---|---|
| **`ops-review`** | ← `ops-review` + `ops-sync` + `ops-trace` + `ready` (from 17) + `audit` Phase 2 (from 17). Writes `11_build/review.yaml` + `11_build/trace.yaml` |
| **`concept-reverse`** | ← `ops-reverse-engineer`. Thin orchestrator + `references/detection/` |
| **`quality-release`** | ← `ops-eval-product`. Leaves `ops`; port text to ticket 23 |
| **dies** | `ops-sync` · `ops-trace` · `ops-eval-concept` · `ops-eval-feature` · `ops-add-feature` |

### 1. `ops-review` absorbs four skills, because four skills were checking one tree

`ops-review` and `ops-sync` were **596 lines with one difference, and `ops-sync` states it
itself** — *"safer than `review`'s gardening mode because every change is previewed"*
(`09_sync/SKILL.md:52-54`). Review STEP 4 (`:200-210`) is sync steps 2–3 (`:112-127`), check for
check. Preview-before-writing is a step, not a domain boundary.

ADR 0007 then took two of `ops-sync`'s three remaining jobs. Its **group-alignment check
(`:161-171`) matches a shape that no longer exists** — `features/<NN_group>/` against
`screens/<NN_group>/`, while 0007 groups features by `<featureset>` and screens by
`<feature_slug>` with no prefix below the first level. And **the feature↔screen drift it
repairs is largely unreachable under W1**: ticket 08 made `spec-feature` sole writer of both
trees, and its step 7 registers both directions in one pass, so divergence was a two-writer
artefact. What genuinely survives is deletion drift, manual-edit drift, and the
`feature_map.json` ↔ `data_entities:` half, whose two writers ticket 08 left separate.

**`ops-trace` folds in.** *"Is this feature actually built"* is the same audit one root down, and
under ADR 0007 `11_build/` is inside the tree `ops-review` already inspects — the merge that
made ticket 04's line blurry is the same merge that makes this fold correct. Its back-link
survives (`-mp/skills/build-implement/SKILL.md:55-59` writes slice ref, SHAs and source files),
but **its evidence set shrinks to three sources of four**: ticket 19 left the `.ac.md` ledger
homeless (17 has now placed it at `11_build/acceptance-criteria/`, so it returns), and
`eval-feature/*.yaml` dies below. What it reads is feature frontmatter, dossiers, the ledger and
`git ls-files`. **Its singular `slice_ref` assertion is wrong and is fixed in the fold** — ticket
19 decoupled `slice_id` from `feature_slug`, so one feature has N slices and Direction 1 is a
one-to-many join, not a lookup.

**`ready` merges in** (handed here by ticket 17). By ticket 04's line it is not close: every
`READS` path is under `_concept/`, its Context Budget declares *"Never load: Source code"*, its
body declares *"WRITES (none — read-only audit skill)"*. Its per-gap **remediation command naming
the exact skill** is not a feature of a skill — it is how findings should be reported, so every
`ops-review` finding names the skill that fixes it. The **gate-position disagreement 17 carried
across is not a conflict**: `07_ready:66` says *"before E2E testing"*, `quality-gate.flow.yaml:73-82`
places it after under *"Release Ready"* — that is ticket 10 choosing where a node sits, not two
statements about the skill.

**And `audit` Phase 2** — 17 asked whether `ops-review` keeps the `_concept/` structure-integrity
work `audit` was doing in parallel. Yes. `audit:52` already sent users to `review` for it, and
`analysis_checklists.md` calls Phase 2 *"Subset of `review` (mechanical checks only)"* before
doing it anyway.

**Size is the accepted risk.** ~900 source lines into ticket 03's 140 ceiling. Ticket 03 measured
44% of the collection mechanically removable before any rewriting, and these four overlap heavily
by construction — but if it does not fit, the fallback is `references/checks.md`, and failing that
a split back into `ops-review` (tree integrity) and `ops-trace` (build coverage), which is the
seam this ruling crossed.

### 2. The three `ops-eval-*`: one dies, one dies, one leaves the domain

**`ops-eval-concept` dies — 181 lines with zero callers of any kind.** Not zero flow nodes: zero.
Its only mention collection-wide is `contracts/evaluator.md:3`, a list of who reads the contract.
Its job — score `_concept/` completeness against a deduction table — is what `ops-review` writes a
verdict for, and it was one of **four** implementations of that check.

**`ops-eval-feature` dies.** Its real job was auditing whether claimed criteria are actually met,
and ticket 17 gave that to `quality-review` as the **AC-ledger honesty check** — *"any criterion
with Status `pass` whose assertion the code visibly cannot satisfy is a finding"*. What is left is
the discipline *"MUST actually interact with the running app — no static code inspection"*
(`06_eval-feature/SKILL.md:63`), which is a step in `quality-review`, not a skill.

**`ops-eval-product` survives as `quality-release`, in the `quality` domain.** It inspects the
running app, which is the wrong side of ticket 04's line, and **it is the only skill in the
collection that closes the loop back to `brief.md` + `goals.md`** — a release gate grading the
whole app on seven axes against the intent it started from. Zero flow nodes today is ticket 10's
to fix, not evidence it is dead; `quality-gate.md:21` already describes it in prose. Its port text
goes to **ticket 23** with 17's other four.

**Ticket 17 resolved before this note could reach it**, which is how these two ended up owned by
nobody: ticket 21 ruled they leave `ops` and left the merge to 17; 17 built `quality-review` from
`review-feature` + parts of `eval-code`/`audit` and never saw them. Ruled outright here rather
than bounced back to a closed ticket.

### 3. `ops-add-feature` dies into about four lines of `spec-feature`

Ticket 08 already re-pointed it: adding a feature to a live project is the same job as specifying
one, and 08 left one writer per artifact. Four things were genuinely not covered there, and only
one of them is worth carrying:

- **The cascade dies** (STEP 5 `:246-268` + 162 lines of `references/cascade_rules.md`). It
  propagates one feature's change across `04_journeys/`, `techstack.md`, `architecture.md`,
  `datamodel/*` and `07_screens/`, each write conditional on prior existence — which is exactly
  the multi-writer pattern ticket 08 dissolved. What replaces it is **naming which skill to
  re-run**, not re-running it from inside `spec-feature`.
- **The impact assessment survives as a grill step** (STEP 3 `:231-243`). `spec-feature` grills
  about the feature; this grills the concept about the blast radius, and it is the honest
  replacement for the cascade: it emits which of the five artifacts need their owner re-run.
- **The already-built tail dies as a branch** (STEP 7 `:288-292`). Ticket 13's intake rule already
  routes a new-or-changed feature to `spec-feature` and a defect to `build-plan`; the tail is one
  line naming `build-plan` when the project is built.
- **The inline self-quality-gate dies** (STEP 6 `:270-278`) — it was running `ops-review`'s checks
  inside a writer.
- **One line is carried that ticket 08's re-point did not catch:** *"Preserve existing `screens:`
  and `data_entities:` arrays"* (`:257`) — a data-loss guard on the refinement branch
  `spec-feature` already has.

**316 lines → ~4.** Its only live caller was `SOUL.md:113`, the orchestrator routing table ticket
13 replaced.

### 4. `ops-reverse-engineer` becomes a thin orchestrator, and leaves `ops`

621 lines that split (per the brief's block-by-block read) into ~90 genuine procedure, ~210
stack-specific detection detail, ~120 restating other skills' output templates, ~130 ticket-03
boilerplate, and 80 frontmatter. **Ticket 02's mechanism applied literally**: it keeps Steps 1, 2
and 9 — validate, repo discovery, and the `extracted`/`inferred`/`needs_review` confidence
grading that is its own invention — and **calls** `concept-brief`, `architecture-techstack`,
`architecture-datamodel`, `design-brand`, `experience-shell` and the `spec-feature` loop instead
of restating their templates. Ticket 08's re-point removed Steps 5 and 8 mechanically; **Steps 4,
6 and 7 write `10_blueprint/` and `03_brand/`, whose writers ticket 08 left in place**, so they go
the same way.

**The detection recipes are the one thing no other skill owns** — only this skill reads source to
infer a stack — so the four blocks become `references/detection/{techstack,datamodel,brand,screens}.md`
under the skill. ~90-line `SKILL.md` + ~210 lines of references.

**Renamed to `concept-reverse`.** It *writes* `_concept/`, it does not inspect it, so ticket 04's
line never covered it; every other writer in the collection is named for what it writes; and its
flow is already `skaileup-concept-reverse`. Also fixed in the port: the **structural defect at
`:339-368`**, two `##` headings and a 23-line fence sitting inside the workflow between Steps 5
and 6, a mis-levelled tail of Step 5's template.

### 5. `ops` survives as a one-skill domain — and ticket 04's line is now blurred

Nine domains stand. **A domain is a name segment, not a folder** (ticket 04's flat tree; ticket 05
deleted all 16 `DOMAIN.md`), so a one-skill domain costs nothing structural, and ticket 04 already
established that a prefix is mandatory regardless — a bare `review` collides with the global
install — so the only question was *which* prefix. Dissolving `ops` into `quality` would reopen
ticket 04's domain set from a ticket that does not own it, and would have pushed a naming decision
into a ticket that was live at the time.

**Recorded as a live tension rather than resolved:** ADR 0007 folded `_implementation/` into
`11_build/`, so *"`quality` checks `src/`, `ops` checks `_concept/`"* no longer separates cleanly —
the merged `ops-review` reads the build half and `git ls-files`. Ticket 17 hit the same line from
the other side (`ready` and `test-plan` were `quality`-named skills entirely on the `ops` side;
`quality-standards` reads an external codebase and writes grounding). The line still sorts every
skill correctly; it just no longer sorts them by a property of the *tree*. Whoever revisits ticket
04 starts here.

**Name kept.** `quality-review` and `ops-review` are not a collision — they are ticket 04's line
stated in the names: one reviews the code, one reviews the tree, and the domain prefix is the only
thing that differs because the artifact under inspection is the only thing that differs.

### 6. Where the outputs land — ticket 17's placement wins over this ticket's first answer

This ticket initially minted a twelfth root, `12_review/`, on the argument that
`review-coverage.ts:135-146` **unions three files by feature id** (`trace.yaml`,
`acceptance_criteria/**/*.ac.md`, `review/<feature>.yaml`) so they are one artifact kind. **17's
`11_build/` placement is better on that same argument**: all three were under `_implementation/`,
and ADR 0007 renames `_implementation/` → `11_build/`, so the host's fix stays a **single prefix
change** and becomes the identity rename 0007 already implies, rather than a re-homing. No twelfth
root.

- **`11_build/trace.yaml`** — filename unchanged; the host reads that name.
- **`11_build/review.yaml`** — the merged `ops-review`'s verdict, ex-`_concept/quality.yaml`.
- **`eval-concept.yaml` needs no home.** The skill dies.

**The one accepted oddity:** `skaileup-concept-only` runs `ops-review`, so a concept-only project
grows an `11_build/` holding nothing but a review. The alternatives are worse — a twelfth root for
one file, against 0007's *"adding a kind renumbers what follows"*; or a fourth root file beside
`brief`/`goals`/`comparable`, which are inputs, mixing a report in among them. **`01_meta/` is
ruled out on 0007's own read direction** (*"reads from anywhere earlier, writes only into the
folder it owns"*): a report on folders 01–10 written into 01 is backwards.

### 7. `contracts/evaluator.md` survives, on a basis 17 could not have had

17 kept it on *"four in-body readers, three of them ticket 21's `ops-eval-*`"*. **All three of
those are gone.** The conclusion survives its own reasoning: the readers are now **`ops-review`**
(it absorbed `ops-eval-concept`'s scoring when it took `ready`), **`quality-review`** and
**`quality-release`** — three skills writing verdict artifacts that share a stance, a verdict
grammar and a flag shape, which is what ticket 09's bar exists for.

Two defects found while checking, handed to **ticket 23** rather than fixed here:

1. Its header (`:3-5`) names five readers, **four of them dead or renamed**.
2. 17 pinned `quality-review`'s rule as *"`approve` ⇒ zero critical **and** zero high"* — a
   severity vocabulary this contract does not have; its flag shape is `blocking|warning`
   (`:52-57`). One of the two is wrong.

To **ticket 22**: its six laws are uppercase `MUST`/`NEVER` with **no machine behind them**, which
is not the carve-out ticket 09 made — that was for `iron_laws` + `golden_principles` as
machine-enforced gates. Same shape of question as law 6.

`references/cascade_rules.md` (162 lines) needs no ruling — it dies with `ops-add-feature`.

### Handed off

- **Ticket 10** — node changes across four flows, and the `appbuilder-complex` dangle nobody
  owned. See the note filed there.
- **Ticket 16** — `contracts/frontmatter.md:161,171`, `concept_structure.md:55,285` and
  `acceptance_criteria.md:251` name `ops-reverse-engineer`, `ops-review` and `ops-trace` at
  pre-0007 paths; `12_trace/SKILL.md:57,62,68,69,106` and `07_eval-product/SKILL.md:43,109,114`
  cross-name skills this ruling deletes.
- **Ticket 22** — `evaluator.md`'s unenforced laws; law 6's `ready` is answered (it is a step
  inside `ops-review`, so the law names a skill that no longer exists either way).
- **Ticket 23** — `quality-release`'s port text, and `evaluator.md`'s two defects.

### Register (forge-concept, deferred)

Two existing entries change; no new constraint.

- **`phaseForSkill`'s hardcoded names** (`shared/flow-phases.ts:23-24`) matched `ops-eval*`,
  `ops-review` and `ops-sync`. After this ruling **only `ops-review` still exists** — the other
  three names are dead, and `ops-review`'s lane (`review`) is still right. Inert either way while
  `-mp` declares `data.phase` per node.
- **The review surface degrades less than recorded.** The register called it *"the sharpest entry
  here, because it degrades a feature rather than merely constraining a choice"*. With
  `11_build/` chosen over a new root, the fix is **`_implementation/` → `_concept/11_build/`** —
  one prefix across `review-coverage.ts:109,122,130` and `review.vue:21-22` — plus
  `findConceptPath`'s `experience/features/<NN_group>/` → `05_features/<featureset>/`.

## Note from ticket 17

Three things arrive from the quality domain.

**1. `ready` (162 lines) leaves `quality` — merge or keep is yours.** By ticket 04's line it is
not close: every path in its `READS` is under `_concept/`, its Context Budget says
`Never load: Source code`, and its body says `WRITES (none — read-only audit skill)`. It is
the **fourth** thing checking `_concept/` cross-reference integrity, alongside
`ops-eval-concept` (whose deduction table scores the same completeness matrix, differing only
in verdict grammar — 0-100 score vs per-feature ready/not-ready), `ops-review`, and `audit`
Phase 2 (which 17 deletes). Its own *"When NOT to Use"* routes concept-health to `review` and
source to `audit`, leaving it as feature-completeness-in-`_concept/`.

Two things only it has, which a merge must carry or consciously drop:
- a **remediation command naming the exact skill** that fills each gap;
- its **gate position** — and the flow and the skill disagree about what that is:
  `07_ready/SKILL.md:66` says *"Use **before** E2E testing"* while
  `quality-gate.flow.yaml:73-82` places `q-ready` **after** `q-test-e2e`, labelled
  *"Release Ready"*.

Also: its frontmatter declares `produces: impl-readiness` while the body writes nothing —
and under ticket 01, frontmatter `artifacts` is machine-read.

**2. Two of ticket 08's three placements are yours, not 17's.** `_concept/quality.yaml` is
written by `ops-review` (enforced by its `validator.py:34`) and `_concept/eval-concept.yaml`
by `ops-eval-concept` (`validator.py:14`, and a **hard gate** — the orchestrator's
*"concept must pass eval-concept"*). Neither has an entry in ADR 0007's `11_build/`, which
today holds only `slices/` and `decisions.md`. 17 ruled on the third (`testing/test_plan.md`
needs no entry — the producer dies) and on its own (`11_build/reviews/<feature_slug>.yaml`).

Worth knowing when you place them: ticket 08's list of three was drawn on the artifact's
*shape*, which is why `_implementation/eval-code.yaml` and `_implementation/review/<slug>.yaml`
— the same "findings about work" — were not in it. Drawn on the **writer**, the split is two
here and one in 17. Both of your two are read **only by the orchestrator**, whose port is
still in the map's fog.

**3. `audit` Phase 2 was doing `ops-review`'s job in parallel, and 17 deletes it.**
`03_audit/SKILL.md:127-131` checks cross-reference integrity, orphaned files, frontmatter
compliance and stale files — `ops-review`'s description verbatim — while `audit:52` sends the
user to `review` for exactly that. `analysis_checklists.md` admits it: *"Subset of `review`
(mechanical checks only)"*. So nothing is lost by the deletion **provided `ops-review` keeps
that work**; confirm rather than assume.

`contracts/evaluator.md` survives ticket 09's bar largely on your three `ops-eval-*` readers —
17 adds `quality-review` as the fourth. `13_impl-quality/contracts/evaluate-contract/CONTRACT.md`
does not port (zero `requires:` anywhere, three stale paths).
