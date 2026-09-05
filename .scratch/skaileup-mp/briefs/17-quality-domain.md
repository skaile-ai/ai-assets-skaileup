# Brief — 17: The `quality` domain (13 skills / 2,833 lines)

Evidence for the grilling session. **Nothing here is a resolution.** Where the evidence is
one-sided it is stated as a finding with the quotes attached; the decision is still the human's.

Sources: `skaileup/13_impl-quality/*/SKILL.md`, `skaileup/flows/` (18 flows),
`skaileup/contracts/`, `~/.agents/skills/{code-review,tdd,diagnosing-bugs,implement,handoff,improve-codebase-architecture}`.

---

## The 13

Flow counts are **direct node references**. `quality-gate` is a sub-flow consumed by
`appbuilder-standard`, `appbuilder-complex` and `skaileup-implementation`, so a node in it
reaches three more flows transitively — the "(+3 via quality-gate)" note marks that.

| # | Skill | Lines | Flows referencing | Reads | Writes | Zero-flow |
|---|---|---:|---|---|---|:-:|
| 01 | `test-plan` | 312 | **0** | `_concept/` brief, features, stories.yaml, screens, model.json, seed.json, behaviors/*.allium | `_concept/testing/test_plan.md` | **YES** |
| 02 | `eval-code` | 134 | 1 — `appbuilder-complex` (`q-eval-code`) | `package.json`, `_concept/blueprint/techstack.md`, `_concept/_standards/index.yml` (soft) | `_implementation/eval-code.yaml` | |
| 03 | `audit` | 189 | 1 — `appbuilder-complex` (`q-audit`) | source tree, `_concept/**/*.md` (opt) | `audit-report.md` (opt-in export only) | |
| 04 | `test-unit` | 241 | 4 — `quality-gate`(+3), `appbuilder-mvp`, `appbuilder-simple`, `appbuilder-cli` | features (hard), techstack (hard), `package.json` (hard), existing tests, src; `test_plan.md`+`stories.yaml` optional | test files in-tree | |
| 05 | `test-integration` | 310 | 2 — `quality-gate`(+3), `appbuilder-cli` | features, `model.json`, `seed.json`, `.env.example` (all hard), API routes, existing tests; `test_plan.md` optional | integration test files + test infra | |
| 06 | `test-e2e` | 259 | 2 — `quality-gate`(+3), `appbuilder-simple` | brief, features, stories.yaml, screens, model.json, seed.json (all hard) | `e2e-screenshots/**`, `e2e-test-report.md` (opt), **flips `_implementation/acceptance_criteria/*.ac.md` rows** | |
| 07 | `ready` | 162 | 2 — `quality-gate`(+3), `skaileup-stepwise` | `_concept/` features, screens, model.json, feature_map.json, tokens.json, techstack.md, storybook (soft) | **nothing** — body says `WRITES (none — read-only audit skill)` | |
| 08 | `standards-discover` | 174 | 1 — `skaileup-concept-reverse` | target codebase; techstack (opt) | `_concept/_standards/{domain}/*.md` + `index.yml` | |
| 09 | `standards-inject` | 108 | 1 — `skaileup-concept-reverse` | `_concept/_standards/index.yml` | **nothing** — `No files written — returns matched standards as context to caller` | |
| 10 | `standards-sync` | 128 | **0** | `_standards/index.yml`, `cf__shared/profiles.json` | profile standards / `_concept/_standards/` | **YES** |
| 11 | `debug-self-verify` | 305 | **0** | `_debug/<id>/context.md`, `package.json`, `pyproject.toml`, slice `plan.md` | `_debug/<id>/protocol.md`, `_debug/<id>/context.md` | **YES** |
| 12 | `debug-handoff` | 314 | **0** (deleted by ticket 07) | `context.md`, `protocol.md`, git log | `_debug/<id>/handoff.md` | **YES** |
| 13 | `review-feature` | 197 | 2 — `quality-gate`(+3), `skaileup-slice-impl` | feature spec (hard), `.ac.md`, slice dossier plan/recap/refactor, `git show commits[]`, `source_files[]` | `_implementation/review/<slug>.yaml` | |

**Zero-flow list verified: exactly four** — `test-plan`, `standards-sync`, `debug-self-verify`,
`debug-handoff`. No fifth. Grepped every `*.flow.yaml` in all 18 flow directories for each of the
13 `impl-quality-*` names; the four above return nothing but `.md` doc prose.

### Who actually reads what these 13 write

Measured by in-body reference outside the producing skill, ticket 09's bar (a `requires:`
line or a `DOMAIN.md` mention is a citation, not a reader).

| Artifact | In-body readers |
|---|---|
| `_implementation/eval-code.yaml` | **1** — `skaileup-build` STEP 9: `READ \_implementation/eval-code.yaml after completion`, then branches on `verdict = "fail"` / `"warn"`. The only genuinely consumed verdict in the domain. |
| `_concept/testing/test_plan.md` | **2, both Optional** — `test-unit` and `test-integration` list it in `reads:` and mark it `Optional` in the Context Budget. Neither has a step that branches on it. |
| `_concept/_standards/index.yml` | **2** — `eval-code` (soft consume) and `review-feature` (a `NEVER` clause: `never pad findings with style nits contradicting … (_concept/_standards/)`). **Neither goes through `standards-inject`.** |
| `_implementation/review/<slug>.yaml` | **0.** `ops-trace` is the natural consumer and reads `_implementation/eval-feature/*.yaml`, not `review/`. |
| `audit-report.md` | **0** — opt-in export. `evaluate-contract` points at a different path (`_quality/audit-report.md`); `_quality/` appears nowhere in `concept_structure.md`. |
| `impl-readiness` (`ready`) | **0**, and nothing is written anyway — frontmatter declares `produces: impl-readiness` while the body says `WRITES (none)`. |
| `_debug/<id>/protocol.md`, `context.md`, `handoff.md` | **0** outside the debug pair itself. |
| `.ac.md` ledger (written by `test-e2e`) | Real — `ops-trace` reads `_implementation/acceptance_criteria/**/*.ac.md`; 3 producers. |

---

## Q1 — The three `standards-*` skills

### `standards-inject` has zero in-body callers

The ticket's premise is that it is "a loader called at the start of other skills". Grepped
`standards-inject` across the whole collection. **Every hit outside its own directory:**

```
contracts/flows.md:92                    (table row — ticket 09: flows.md has 0 readers, deleted)
contracts/asset_frontmatter.md:338       inject_skill: standards-inject   (a flow-schema example)
contracts/flow.schema.json:88            "inject_skill": { ... }
contracts/agent-config.json:20           "inject_skill": "standards-inject"
flows/skaileup-concept-reverse/*.yaml    (1 flow node + requires + edge)
flows/skaileup-concept-reverse/*.md      (2 doc-prose lines)
13_impl-quality/DOMAIN.md:23,33,46       (ticket 05: all 16 DOMAIN.md die)
08_standards-discover/SKILL.md:169       - **Pairs with:** cf_standards_inject (consumer)
```

**Not one skill body calls it.** Zero of 95. The `standards-discover` line is a `Pairs with:`
citation in an `## Integration` section, not a step.

### The wrapping mechanism it depends on is in a block ticket 15 already declared dead

`DOMAIN.md` claims `standards-inject (wraps every skill call)`. The wiring for that is
`agent-config.json`'s `standards.inject_skill` and the `modes:` block in `flow.schema.json`:

```yaml
modes:
  standards:
    enabled: false
    skill: standards-discover
    inject_skill: standards-inject
    trigger_after: scaffold
```

**No flow declares a `modes:` block at all** (`grep -n "^modes:" flows/*/*.flow.yaml` → empty),
and ticket 15 recorded that `modes`/`tier_presets`/`artifact_handoff` "have no reader anywhere".
So the automatic-injection story rests entirely on machine keys nothing reads, and the manual
story rests on skill bodies that never call it.

### It writes nothing

> `## Outputs` — `No files written — returns matched standards as context to caller`

A skill with zero callers, zero writes, and a body that is a match algorithm over a YAML index
is, on this collection's own machine layer, a read.

### The index schema is internally contradictory

`standards-discover` writes:

```yaml
standards:
  - path: api/route_naming.md
    domain: api
    keywords: [routing, rest, endpoints]
    applies_to: [implement-feature, architecture]
```

`standards-inject`'s matching algorithm keys on exactly those two fields:

> `1. Check if requesting_skill_id in standard.applies_to → strong match`
> `2. Check keyword overlap between standard.keywords and skill.keywords → ranked match`

But `13_impl-quality/contracts/standards-contract/CONTRACT.md` pins a different `index.yml`:

```yaml
standards:
  - path: api/rest.md
    scope: backend
    auto_discovered: true
```

No `keywords`, no `applies_to`. **A contract-conformant index cannot be matched by the loader.**
Separately, `applies_to: [implement-feature, architecture]` names two skills that no longer exist
under those names (pre-Phase-1 naming).

### `standards-sync` — what it does that `discover` doesn't, and why no flow runs it

Sync is the **bidirectional project↔profile** direction; discover is one-way codebase→project.
Its Context Budget is:

> **Must read:** `_concept/_standards/index.yml`, `cf__shared/profiles.json`

- **`profiles.json` does not exist anywhere in the repo** (`find . -name profiles.json` → nothing).
- **`cf__shared/` does not exist either** — the whole path prefix is dead (it is the pre-migration
  name for `contracts/`; `standards-inject` and `standards-discover` still cite `cf__shared/iron_laws.md`
  and `cf__shared/agent_patterns.md` too).
- The `profiles/` that *does* exist is six project-type YAMLs (`web-app`, `cli-tool`, …) which
  ticket 09 moved out of `contracts/` to the repo root as *project-type* data. Ticket 05 additionally
  retired "profile" as a word for tech-stack presets (→ **template**). Sync's target is gone twice over.
- Its own body: "this is an **optional quality-phase step**". The one flow that touches standards
  (`skaileup-concept-reverse`) runs `discover → inject` and stops.

### Contract layer, for the record

Two evaluator contracts coexist: `contracts/evaluator.md` (69 lines, live — `eval-code` cites it
in-body at STEP 4) and `13_impl-quality/contracts/evaluate-contract/CONTRACT.md` (203 lines,
**zero `requires:` declarations anywhere**; the only in-body mention is `review-feature`'s
`if absent, the inline stance below applies`). The latter's skill table is stale on three rows:
`_quality/audit-report.md` (path exists nowhere), `_concept/4_testing/test_plan.md` (old numbering),
and `compile-validators` (moved to `ai-assets-skill-development`).

---

## Q2 — `test-unit` / `test-integration` / `test-e2e`

### Shared pipeline vs level-specific

`test-unit` (241) and `test-integration` (310) are the same five-phase machine:

| Phase | `test-unit` | `test-integration` |
|---|---|---|
| 1 | Discover Test Environment — *Sub-agent 1: Test Framework Detection*, *Sub-agent 2: Feature-to-Source Mapping* | Discover Integration Environment — *Sub-agent 1: API & Database Inventory*, *Sub-agent 2: Test Infrastructure* |
| 2 | Generate Test Files | Generate Test Infrastructure |
| 3 | Verify Tests Run | Generate Integration Tests |
| 4 | Present Report | Run Tests |
| 5 | — | Present Report |

Both: "read 2-3 existing test files to learn conventions"; both hard-gate on `package.json` +
`_concept/experience/features/`; both take `test_plan.md` as Optional; both end in a
Feature/File/Tests/Covered table plus an issues table; both carry a near-identical
`## Common Mistakes` grid.

Genuinely level-specific:
- **unit** — the *What to Test* table (composables / utils / API handlers / store / validators),
  mocking discipline, and the rule that a browser/DB-needing AC is noted rather than forced.
- **integration** — endpoint inventory table, test-DB strategy (separate DB vs transaction
  rollback), auth helper, per-seed-scenario matrix, data-integrity/constraint tests derived from
  `model.json`, cross-feature flows from entity relationships, `.env.example` hard gate.
- **e2e** — a different *tool*, not a different level: `agent-browser` install + `uname -s`
  platform gate, journeys derived from `stories.yaml` stories, screenshots per step, three
  responsive breakpoints, DB record validation, and **the only one of the three that writes an
  `_implementation/` artifact** (flips `.ac.md` Criteria Status rows, stamped
  `Updated by: impl-quality-test-e2e`).

### How the flows actually wire them — the decisive evidence

`quality-gate` runs all three strictly sequentially, none optional:

```yaml
entry: q-test-unit
edges:
  - {source: q-test-unit,        target: q-test-integration, type: flow}
  - {source: q-test-integration, target: q-test-e2e,          type: flow}
  - {source: q-test-e2e,         target: q-ready,             type: flow}
```

But the standalone tiers each take a **different subset**:

| Flow | unit | integration | e2e |
|---|:-:|:-:|:-:|
| `appbuilder-mvp` | ✓ | — | — |
| `appbuilder-simple` | ✓ | — | ✓ |
| `appbuilder-cli` | ✓ | ✓ | — |
| `quality-gate` (→ standard, complex, implementation) | ✓ | ✓ | ✓ |

`appbuilder-mvp` states it in a comment: *"Per SKILL_GRAPH § 6 appbuilder-mvp column: only
impl-quality-test-unit; no…"*. `appbuilder-cli` labels its section
*"--- Quality (unit + integration, no E2E) ---"*.

So today the level set is `{u}`, `{u,e}`, `{u,i}`, `{u,i,e}` — an arbitrary per-tier subset, which
is what a set-valued parameter looks like. And the flow layer **already parameterises one of them**:
`q-test-e2e` carries `parameters: {mode: '${e2e}'}` (required | optional), threaded from the parent.

**The counter-evidence is in the frontmatter, not the prose.** The three carry different hard gates
that forge-concept reads: integration hard-gates on `model.json` + `.env.example`; e2e hard-gates on
`stories.yaml` + `seed.json` + `agent-browser` + a Linux/Darwin platform check. One node means one
frontmatter — either the union of gates (which blocks `appbuilder-mvp`, whose project may have no
database) or no gate at all. That cost is in the machine layer ticket 01 declared live, not in prose.

---

## Q3 — `ready` and ticket 04's `quality`/`ops` line

**Confirmed from source: `ready` never touches `src/`.** Its entire read-set is `_concept/`
(features, screens, `model.json`, `feature_map.json`, `tokens.json`, `techstack.md`, plus a soft
storybook check). Its Context Budget lists `Never load: Source code`. Its body:

> `WRITES`
> `(none — read-only audit skill, output is the report shown to user)`
>
> `NEVER modify any \_concept/ files — this is a read-only audit`

By ticket 04's rule — *`quality` checks `src/`, `ops` checks `_concept/`* — `ready` is `ops`,
without ambiguity.

### It is not the only skill doing this check

`ops-eval-concept` (description): *"checks every feature has acceptance criteria, screen specs,
data model coverage, and a clear brief. Gate: pre-impl."*
`ready` (description): *"Checks each feature for concept doc, screen spec, data model entry,
brand tokens, and tech stack."*

`ops-eval-concept`'s Completeness deduction table:

```
- Every feature appears in ≥1 screen spec
- Every screen references ≥1 feature
- model.json has entities for every feature that creates or reads persistent data
Deductions:
- Orphaned feature (no screen): −5 each
- Orphaned screen (no feature): −5 each
- Missing data entity for data-creating feature: −10 each
```

Same inspection, different verdict grammar (0-100 score vs per-feature ready/not-ready) and a
different gate position (pre-impl vs pre-E2E).

And `ready`'s own routing table sends both neighbours away:

> `## When NOT to Use`
> `- You want to audit concept structure health — use **review** instead`  (= `ops-review`)
> `- You want to audit source code — use **audit** instead`

That makes **four** things checking `_concept/` cross-reference integrity: `ready`,
`ops-eval-concept`, `ops-review` (writes `_concept/quality.yaml`), and `audit` STEP 3 — where
`audit`'s own checklist file admits the redundancy:

> `## Structure Integrity Checks`
> `Only when \`_concept/\` exists. Subset of \`review\` (mechanical checks only).`

`ready` alone contributes: per-feature verdict + a **remediation command naming the exact skill**
that fills each gap, and the E2E gate position (`skaileup-stepwise` and `quality-gate` both run
it immediately before/after e2e).

---

## Q4 — The debug pair vs `~/.agents/skills/diagnosing-bugs`

Ticket 02's claim — skaileup's debug pair "does the exact thing this skill forbids" — **holds, and
the conflict is sharper than the ticket states.** Four separate collisions:

### 1. Hypothesis before loop — the named forbidden move

`diagnosing-bugs` Phase 1:

> **This is the skill.** Everything else is mechanical. […]
> If you catch yourself reading code to build a theory before this command exists, **stop:
> jumping straight to a hypothesis is the exact failure this skill prevents.** No red-capable
> command, no Phase 2.

`debug-self-verify` STEP 1, third interview question, asked **before any command is inventoried**:

> Send Q3 as a STANDALONE message (optional):
> `> "Do you have a current hypothesis about the cause? If yes, state it with confidence (low/medium/high)."`

STEP 2 only then inventories commands; STEP 3 branches on the answer:

> `IF user provided a hypothesis with confidence ≥ medium`
> `  - Mode: HYPOTHESIS-SPECIFIC. The protocol verifies the cause is fixed`

The order is inverted: skaileup elicits the hypothesis first and lets it *shape* the loop;
`diagnosing-bugs` builds the loop first and forbids hypothesising without one. `debug-handoff` is
worse — its schema has a mandatory `## Current Hypothesis` section with a mandatory confidence
tier (`MUST state hypothesis confidence as exactly one of: low / medium / high`), so the whole
artifact is organised around the thing Phase 1 defers.

### 2. The protocol need never have been run

`diagnosing-bugs` completion criterion:

> Phase 1 is done when the loop is **tight** and **red-capable**: you can name **one command**
> […] that you have **already run at least once** (show the invocation and its output, redacted)

`debug-self-verify` STEP 7 runs `validator.py` on the *markdown shape*, then:

> `CHECKPOINT protocol_review`
> `> "Verification protocol ready at _debug/<id>/protocol.md. Run it now, or save for later?"`

"Save for later" is an accepted terminal state. The skill can complete having executed nothing.

### 3. The red signal is optional in the schema *and* in the validator

Protocol schema:

> `- **Expected output (still-broken):** \`<literal string or regex, fenced>\` *(optional)*`

`validator.py`:

```
REQUIRED_STEP_BULLETS = [ ... "- **Expected output (success):**", ... ]
# (the `- **Expected output (still-broken):**` bullet is optional)
```

Against:

> - [ ] **Red-capable**: it drives the actual bug code path and asserts the **user's exact symptom**,
>   so it can go red on this bug and green once fixed. Not "runs without erroring"; it must be able
>   to _catch this specific bug_.

A protocol validates green with no red signal at all. Compounding it, STEP 4 orders steps
`lint / format → typecheck → unit test → integration test → e2e` — a generic suite ordering.
Lint and typecheck cannot go red on a behavioural bug; they are the "runs without erroring" the
global skill names as the failure mode.

### 4. HITL — skaileup forbids what the global skill provides

`debug-self-verify`: `NEVER block waiting for human-in-the-loop verification — the protocol must
be machine-runnable end to end`.
`diagnosing-bugs` loop menu, item 10: *"**HITL bash script.** Last resort. If a human must click,
drive _them_ with `scripts/hitl-loop.template.sh` so the loop is still structured."* — the global
install ships that script.

### What `debug-self-verify` has that `diagnosing-bugs` does not

1. A **durable artifact** with a pinned schema and a machine validator (`_debug/<id>/protocol.md`).
   `diagnosing-bugs` keeps the loop in-session; it names a command, it does not persist a document.
2. The `_debug/<id>/` **workspace zone** with a shared `context.md`, so `self-verify` and `handoff`
   do not re-interview the user.
3. **Interview mechanics** — Iron Laws § 9 standalone-question discipline.
4. An **escalation pointer** other skills can emit: `review-feature` on `needs_changes` emits
   `next=impl-quality-debug-self-verify hint="…escalate to impl-quality-debug-handoff after two failed attempts"`.

### What `diagnosing-bugs` has that neither skaileup skill has

Minimisation (Phase 2, "every remaining element is load-bearing"); 3–5 **ranked falsifiable**
hypotheses with stated predictions (Phase 3); tagged `[DEBUG-a4f2]` instrumentation with a grep-based
cleanup (Phase 4); regression test at a **correct seam**, and *"if no correct seam exists, that
itself is the finding"* (Phase 5); the six-item cleanup checklist (Phase 6); a Redact section; a
perf branch; a reproduction-rate strategy for non-deterministic bugs; and the ten-way menu of loop
constructions. `debug-self-verify` covers **one** of `diagnosing-bugs`' six phases (a partial
Phase 5/6), and inverts its Phase 1.

Note also `~/.agents/skills/handoff` (16 lines) — a global install that already writes a
cold-resume handoff doc to the OS temp dir, redacts secrets, and *"Do not duplicate content already
captured in other artifacts […] Reference them by path or URL instead."* That is `debug-handoff`'s
314 lines in three sentences. Ticket 07 already deleted it; ticket 12 already ruled `handoff` does
not become a skaileup skill.

---

## Q5 — `eval-code` · `audit` · `review-feature` vs the global `code-review`

### First: all three run the same three sub-agents from the same file

`eval-code` STEP 4:

> Dispatch three parallel sub-agents (scope=full only).
> **Same auditor trio as impl-quality-audit — checklists owned there:**
> - Sub-agent A — Logic Auditor: `13_impl-quality/03_audit/references/analysis_checklists.md § Logic & Runtime`
> - Sub-agent B — Security Auditor: … `§ Security & Data Integrity`
> - Sub-agent C — UI/UX Code Auditor: … `§ UI/UX & Accessibility`

`review-feature` STEP 2:

> Three check passes (analysis_checklists.md)
> - Pass 1 — Logic & Runtime Errors (§ Sub-agent 1) …
> - Pass 2 — Security & Data Integrity (§ Sub-agent 3) …
> - Pass 3 — UI/UX & Accessibility (§ Sub-agent 2) …

That shared file is **64 lines**, of which the three checklists are 18 bullets total:

```
## Sub-agent 1: Logic & Runtime Errors
- Incorrect conditionals, off-by-one errors
- Missing null/undefined checks
- Race conditions in async code
- Unhandled promise rejections
- Missing error boundaries
- Incorrect type assumptions
```

Against `code-review`'s standards axis, which carries the Fowler smell baseline in full — twelve
named smells, each *what it is → how to fix*, with two binding rules the skaileup checklists have
no equivalent of:

> - **The repo overrides.** A documented repo standard always wins; where it endorses something
>   the baseline would flag, suppress the smell.
> - **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"),
>   never a hard violation. Like any standard here, skip anything tooling already enforces.

And `appbuilder-complex` runs `q-eval-code` → `q-audit` back to back — **the same trio twice in
sequence**, then a third time inside the `quality-gate` sub-flow's optional `q-review-feature`.

### Per skill: adds vs restates

**`eval-code` (134)**

*Adds, and `code-review` has none of it:*
- Build verification as a hard stop before any analysis: `lint → typecheck → build`;
  `MUST stop immediately if build fails — do not continue to sub-agents`.
- Test-suite execution with pass/fail/coverage capture, and a stop on failure.
- A `scope` parameter (`scaffold` = build+lint+types | `feature` = +unit tests | `full` = +analysis).
- A machine verdict artifact with a pinned rule (`pass` / `warn` / `fail`) — **the only artifact in
  this domain with a real reader**: `skaileup-build` STEP 9 branches on it.

*Restates:* the trio, which it explicitly borrows rather than owns.

*Framing note:* build+test is not `code-review`'s job in the mp model either. mp's `implement`
(15 lines) says *"Run typechecking regularly, single test files regularly, and the full test suite
once at the end. Once done, use /code-review to review the work."* — build/test belongs to the
implement step; ticket 07 put `tdd` + `code-review` inside `build-implement`.

**`audit` (189)**

*Adds:*
- **Whole-repo scope with no fixed point.** `code-review` is diff-scoped by construction
  (`git diff <fixed-point>...HEAD`, and it refuses on an empty diff). A no-diff, whole-tree pass is
  a genuinely different scope.
- The `_concept/` structure-integrity check (STEP 3) — but see below.
- An interactive offer-fixes loop (`Fix each issue one at a time / Show diff for each fix`).
- A four-tier severity taxonomy + report template.

*Restates:* the trio; and its structure check is self-declared redundant —
`analysis_checklists.md`: *"Only when `_concept/` exists. **Subset of `review` (mechanical checks
only)**."* Also: `~/.agents/skills/improve-codebase-architecture` (71 lines) already occupies the
whole-repo, no-fixed-point scan niche, with a sharper method (deepening opportunities, the deletion
test, hot-spot scoping from `git log`) and a `codebase-design` vocabulary.

*Lacks vs `code-review`:* no spec axis, no standards-source discovery, no smell baseline.

**`review-feature` (197)**

*Adds — and this is the strongest case in the trio:*
- **The fixed point comes from the pipeline, not the user.** `code-review` step 1: *"Whatever the
  user said is the fixed point […] If they didn't specify one, ask for it."* `review-feature`
  resolves it from `commits[]` + `source_files[]` back-links written into feature frontmatter by
  `impl-slice-commit`, and refuses when they are empty.
- **The spec source is likewise resolved, not asked for.** `code-review` step 2 ends:
  *"If nothing is found, ask the user where the spec is. If they say there isn't one, the **Spec**
  sub-agent will skip and report 'no spec available'."* `review-feature` always has
  `_concept/experience/features/<group>/<slug>.md`.
- **The AC cross-check** (STEP 3 / a `MUST`): *"any criterion with Status pass whose assertion the
  code visibly cannot satisfy is a finding (severity ≥ high, ac_ref set)"* — auditing the ledger's
  own honesty. Nothing in `code-review` does this.
- Reads `refactor.md` so **accepted debt is context, not a finding**.
- A validated YAML verdict with a pinned rule (`approve` ⇒ zero critical AND zero high).

*Restates:* the trio again; and the adversarial stance **three times over** — once in
`contracts/evaluator.md § Stance`, once in `evaluate-contract/CONTRACT.md`, and once inlined into
the skill body under the header *"inline minimal stance — applies even if evaluate-contract is not
installed"*.

*Lacks vs `code-review`:* the two-axis separation and its anti-merge rule —
*"Do **not** merge or rerank findings, because the two axes are deliberately separate"* /
*"Don't pick a single winner across axes: that's the reranking the separation exists to prevent."*
`review-feature` merges logic/security/ui-ux and spec findings into one severity-ranked list, which
is the collapse `code-review` exists to block.

### The reduction, stated plainly

Everything in these three about **how to look at code** is `code-review`'s, and better specified
(12 named smells with fixes vs 18 generic bullets; repo-overrides-baseline; skip-what-tooling-
enforces; per-sub-agent 400-word caps for context hygiene). What survives contact is not
review technique but three non-review capabilities:

1. `eval-code`'s build/test gate + machine verdict (which the mp model puts in the implement step);
2. `audit`'s whole-repo, no-fixed-point scope (contested by `improve-codebase-architecture`);
3. `review-feature`'s **resolution of `code-review`'s two missing inputs** — the fixed point and the
   spec — from `_concept/` and the slice dossier, plus the AC-ledger honesty check.

Item 3 is exactly ticket 07's `implement` mechanism inverted: not "restate the review", but
"hand `code-review` the two things it has to ask a human for".

---

## Q6 — `test-plan`

**Produces:** `_concept/testing/test_plan.md` — a markdown plan (explicitly not code:
*"Writing test code instead of a plan → This skill produces a markdown plan, not executable tests"*),
with per-feature Happy Path / Error States / Edge Cases / Permissions scenarios, a scenario→seed-scenario
mapping table, and a coverage summary with `AC` / `AC✓` columns plus an **Uncovered Acceptance
Criteria** table.

**Does anything read it?** Two skills, both marking it `Optional`:

- `test-unit` — `reads: _concept/testing/test_plan.md` / Context Budget row `| _concept/testing/test_plan.md | Optional |`
- `test-integration` — identical pattern.

Neither has a workflow step that branches on its presence or absence. **No hard reader; zero flows
run the producer.** Everything else that names it is a citation: `concept_structure.md`'s tree
comment, `artifacts.yaml`'s registry entry (ticket 09 deleted the file), `DOMAIN.md` (ticket 05
deletes all 16), and `evaluate-contract`'s stale row pointing at `_concept/4_testing/test_plan.md`.

**Its distinctive job already has a live home.** AC traceability is carried by
`_implementation/acceptance_criteria/<group>/<slug>.ac.md` — three producers
(`impl-plan-plan-vertical`, `impl-slice-test`, `impl-quality-test-e2e`), with `test-e2e` flipping
per-criterion rows pass/fail and stamping itself, and a real downstream reader in `ops-trace`.
`test-plan`'s `AC` / `AC✓` columns are the same accounting, upstream, unread.

**Ticket 04 side:** reads only `_concept/`, writes only into `_concept/`. It never sees `src/`.

---

## Also found

- **`agents/quality/{agent.yaml,SOUL.md}`** exists in this domain. Ticket 12: no `agents/` in `-mp`.
- **Dead path prefix `cf__shared/`** is still cited in-body by `standards-inject` (×2),
  `standards-discover` (×2) and `standards-sync` (×2). No such directory exists.
- **Two evaluator contracts.** `contracts/evaluator.md` (69 lines, live, cited by `eval-code`)
  vs `13_impl-quality/contracts/evaluate-contract/CONTRACT.md` (203 lines, zero `requires:` from
  any skill, three stale paths). Ticket 09's bar leaves the second with no reader.
- **`ready`'s frontmatter lies about its output**: `produces: impl-readiness` vs body `WRITES (none)`.
  Under ticket 01, frontmatter `artifacts` is machine-read.
- **mp coverage of this ground:** `code-review` (87), `tdd` (38), `diagnosing-bugs` (138),
  `implement` (15), `handoff` (16), `improve-codebase-architecture` (71), `codebase-design` (114).
  Nothing in mp covers test *generation* from specs (`test-unit`/`test-integration`), browser E2E,
  or standards discovery. `tdd` explicitly pushes refactoring out of the loop and into review:
  *"Refactoring is not part of the loop. It belongs to the review stage (see the `code-review` skill)."*

---

## Open tensions

1. **Is `standards-inject` a contract, a frontmatter field, or nothing?** It has zero in-body
   callers, writes zero files, and the auto-wrap mechanism it depends on (`modes.standards.inject_skill`)
   lives in a block ticket 15 found has no reader in any host. If it is not a skill, is
   "read `_concept/_standards/index.yml` and apply what matches" a line in `agent_patterns.md`, a
   line in the skill template, or does the whole standards idea go with it — noting the only two
   in-body readers of the *artifact* (`eval-code`, `review-feature`) already read it directly?

2. **Does the standards idea survive `discover` alone?** `sync`'s two targets (`profiles.json`,
   `cf__shared/`) do not exist, and ticket 05 retired the word "profile" for exactly this sense.
   One survivor writing an index with a schema its own contract contradicts — is that one skill or
   zero, and if one, who fixes the `applies_to`/`keywords` vs `scope`/`auto_discovered` split?

3. **Three test nodes or one node with a level set?** The flows already select arbitrary subsets
   per tier (`{u}` / `{u,e}` / `{u,i}` / `{u,i,e}`) and already parameterise e2e's `mode`. But one
   node means one frontmatter, and the three hard-gate on different files — integration on
   `model.json` + `.env.example`, e2e on `stories.yaml` + `seed.json` + `agent-browser` + a platform
   check. Does the gate cost land on the union (blocking mvp) or the intersection (no gate)? And is
   e2e a *level* at all, given it is the only one that uses a browser and the only one that writes
   an `_implementation/` artifact?

4. **`ready` is `ops` by ticket 04's line, but it is also the fourth skill checking the same thing.**
   `ops-eval-concept` scores the same completeness matrix, `ops-review` writes `_concept/quality.yaml`
   from it, and `audit` STEP 3 does a self-described "subset of review". Does `ready` move to `ops`,
   or does it merge into `ops-eval-concept` — and if it merges, what happens to the two things only
   it has: the remediation command per gap, and the position as the gate immediately before e2e?

5. **Does anything of the debug pair survive `diagnosing-bugs`?** The conflict is not a nuance —
   `debug-self-verify` elicits the hypothesis before the loop exists, can complete without ever
   running the protocol, and its validator makes the red signal optional. Its four genuine additions
   are all *artifact and interview mechanics*, not diagnosis. Is a persisted `_debug/<id>/protocol.md`
   worth a skill when `diagnosing-bugs` says the loop is "one command […] already run at least once"?

6. **`eval-code` · `audit` · `review-feature` → how many?** Their review technique is `code-review`'s,
   thinner. What is left is three unrelated capabilities: a build/test gate with a machine verdict
   (which ticket 07's model puts inside `build-implement`), a whole-repo scan (contested by
   `improve-codebase-architecture`), and a resolver that hands `code-review` the fixed point and the
   spec it otherwise asks a human for. Is that three skills, one skill, or one paragraph inside
   `build-implement`? And does the AC-ledger honesty check — the one thing no global skill does —
   belong here or with `ops-trace`, which already reads the ledger?

7. **`test-plan` — is it deletable, or is a plan-before-code step something the map wants back?**
   Zero flows, two Optional readers, and its AC accounting already lives in `.ac.md` with three
   producers and a real consumer. But nothing else in the collection asks "what should we test"
   *before* implementation. Is that a gap the flows chose, or one they never noticed?

8. **The same trio runs three times in one flow.** `appbuilder-complex` does `q-eval-code` → `q-audit`
   → `quality-gate` (which contains an optional `q-review-feature`) — the same three sub-agents over
   the same code, three times. Is that redundancy the reason to collapse, or is the intended answer
   one auditor invoked at three scopes (slice diff / feature back-links / whole repo)?


---

## Post-08 delta — recon pass, 2026-09-05

Everything above predates ticket 08 (resolved 2026-09-05, ADR 0007). This section
was gathered after, against the renumbered tree and the ported skills. Where the two
halves disagree, this one is later. Still evidence only — nothing here is a ruling.

Evidence only. Paths relative to `ai-assets-skaileup/skaileup/` unless noted. "Callers" excludes
`contracts/flows.md` (0 readers, t09), `contracts/artifacts.yaml` (unreachable, t01) and
`13_impl-quality/DOMAIN.md` (dies, t05).

### Per-skill table

| # | skill | lines | flow refs (flow : node) | writes | reads | named by (in-body) |
|---|---|---|---|---|---|---|
| 01 | `test-plan` | 312 | **0** | `_concept/testing/test_plan.md` (`01_test-plan/SKILL.md:229,296`) | features · stories.yaml · screens · model.json · seed.json · `behaviors/*.allium` (`:112-119`) | `07_mockup-feedback/03_patch/SKILL.md:190,245,268`; `04_apply/SKILL.md:108` (both collapse into one `mockup-feedback`, ticket 06) |
| 02 | `eval-code` | 134 | `appbuilder-complex:400` (`q-eval-code`) | `_implementation/eval-code.yaml` (`:71`) | package.json · `techstack.md` · `_concept/_standards/index.yml` (`:65-68`) | `13_review-feature/SKILL.md:69`; `contracts/evaluator.md:4` |
| 03 | `audit` | 189 | `appbuilder-complex:411` (`q-audit`) | `audit-report.md` at repo root, opt-in (`:88,179`) | package.json · `src/` · **`_concept/**/*.md`** (`:85`) | `13_review-feature/SKILL.md:68,193`; `02_eval-code/SKILL.md:109`; `contracts/evaluator.md:5` |
| 04 | `test-unit` | 241 | `quality-gate:48` · `appbuilder-mvp:204` · `appbuilder-cli:168` · `appbuilder-simple:223` | test files under `src/` (fm `produces: src`) | features · techstack · package.json · existing tests · `test_plan.md` *(Optional, `:98`)* | **none** |
| 05 | `test-integration` | 310 | `quality-gate:58` · `appbuilder-cli:179` | test files under `src/` | features · model.json · seed.json · techstack · `.env.example` · `test_plan.md` *(Optional, `:107`)* | **none** |
| 06 | `test-e2e` | 259 | `quality-gate:68` · `appbuilder-simple:234` | `e2e-screenshots/**`, `e2e-test-report.md`, flips `.ac.md` Status rows (`:135-137`) | brief · features · stories.yaml · screens · model.json · seed.json | `12_impl-slice/04_test/validator.py:273` (`AC_UPDATERS`, **executable**); `contracts/acceptance_criteria.md:250` |
| 07 | `ready` | 162 | `quality-gate:79` (`q-ready`) · `skaileup-stepwise:158` (`q-ready`, `phase: review`) | **`WRITES (none — read-only audit skill)`** `07_ready/SKILL.md:116` — but frontmatter declares `produces: impl-readiness` (`:32`) | **only `_concept/`**: features · screens · model.json · feature_map.json · tokens.json · techstack.md · storybook pages (`:106-113`) | **none** |
| 08 | `standards-discover` | 174 | `skaileup-concept-reverse:102` | `_concept/_standards/{domain}/*.md` + `index.yml` (`:148-149`) | target codebase path (user input); `_concept/05_techstack/stack.md` (`:78` — **path does not exist in today's tree**) | `contracts/asset_frontmatter.md:337`; `contracts/concept_structure.md:254` |
| 09 | `standards-inject` | 108 | `skaileup-concept-reverse:113` | **nothing** — `"No files written — returns matched standards as context to caller"` (`:96`) | `_concept/_standards/index.yml` + matched files | `contracts/asset_frontmatter.md:338` (`inject_skill:`) |
| 10 | `standards-sync` | 128 | **0** | profile standards / `_concept/_standards/` + index.yml | `index.yml` · **`cf__shared/profiles.json`** (`:72,88` — `find . -name profiles.json` returns **nothing**; the dir is `contracts/profiles/*.yaml`) | **none** |
| 11 | `debug-self-verify` | 305 | **0** — self-declared: *"This skill is **not** wired into any `flows/*.flow.yaml` yet"* (`:77-78`) | `_debug/<id>/protocol.md`, `_debug/<id>/context.md` | `_debug/<id>/context.md` · package.json · pyproject.toml · `_implementation/slices/<id>/plan.md` | `13_review-feature/SKILL.md:117,176,196`; `flows/quality-gate/quality-gate.md:20` |
| 12 | `debug-handoff` | 314 | **0** | `_debug/<id>/handoff.md`, `context.md` | context.md · protocol.md · slice plan | `13_review-feature/SKILL.md:117,176`; `11_debug-self-verify/SKILL.md:80,290` |
| 13 | `review-feature` | 197 | `quality-gate:89` (`q-review-feature`, `optional: true`) · `skaileup-slice-impl:149` (`i-review-feature`) | `_implementation/review/<slug>.yaml` — *"the ONLY file this skill writes"* (`:87`) | feature spec + `commits[]`/`source_files[]` back-links · `.ac.md` · slice plan/recap/refactor · `git show` | `14_ops/12_trace/SKILL.md:70` |

**Counts (raw, no conclusion drawn).** Zero flow refs: **`test-plan`, `standards-sync`, `debug-self-verify`, `debug-handoff`** (matches t07:145). Zero in-body callers: **`test-unit`, `test-integration`, `ready`, `standards-sync`** (`test-e2e`'s one caller is *code*, not prose). Zero of both: **`standards-sync`** alone. Note the pair: `test-unit`/`test-integration` sit on flows but nothing names them, and both read `test_plan.md` as **Optional** — its only writer is on no flow.

### quality/ops boundary cases

Ticket 04's line: `quality` checks `src/`, `ops` checks `_concept/`.

| skill | inspects | verdict per ticket 04's line |
|---|---|---|
| `eval-code` · `test-unit` · `test-integration` · `review-feature` | `src/` only (build/tests/diffs) | clean `quality` |
| `test-e2e` | the **running app** — `agent-browser` vs a dev server (`06_test-e2e/SKILL.md:171,193,195`) | neither side — a third thing; reads `_concept/` only as the oracle |
| **`audit`** | **both.** Phase 1 sub-agents read `src/`; **Phase 2 "Structure Integrity"** reads `_concept/`: *"Check cross-reference integrity (features <-> screens) · Check for orphaned files · Check frontmatter compliance · Check for stale files"* (`03_audit/SKILL.md:127-131`) | **boundary case.** Phase 2 is `ops-review`'s job verbatim — its description: *"scans completeness, cross-reference integrity, golden principle compliance, and entropy"* (`14_ops/08_review/SKILL.md:3`). `audit`'s own body says so: *"You want to audit the `_concept/` structure — use **review** instead"* (`:52`) — while doing it anyway in Phase 2 |
| **`ready`** | **`_concept/` only.** Every path in `READS` is under `_concept/` (`07_ready/SKILL.md:106-113`); `NEVER load: Source code` (`:90`) | **plausibly ticket 21's** (`ops`). Its own "When NOT to Use" routes concept-health to `review` and code to `audit` (`:71-72`), leaving it as *feature-completeness-in-`_concept/`* |
| **`standards-discover`** | an **external** codebase (`target_path` user input), writes into `_concept/` | **neither.** Not this project's `src/`; the artifact is grounding. Ticket 08 already gave it a home at `02_grounding/standards/` (`-mp contracts/concept_structure.md:41-43`) |
| **`standards-inject`** / **`standards-sync`** | nothing / `_standards/` ↔ a profile file that does not exist | **neither.** Not inspections at all |
| **`debug-self-verify`** | a **bug** — writes to `_debug/<id>/`, a root outside both `_concept/` and `src/` (`11_debug-self-verify/SKILL.md:88-97`) | **neither.** `_debug/` has no entry in ticket 08's eleven-folder tree |
| `test-plan` | `_concept/` in, `_concept/` out (`_concept/testing/test_plan.md`) | **boundary case** — pure concept-side authoring wearing a `quality` name |

### Ticket 12 / `debug-handoff`

Deleted, and the citation is in **ticket 07, not 12**: `issues/07-implementation-side-consolidation.md:129`
— *"**`impl-quality-debug-handoff` (314 lines) is deleted** — zero flow references, `-mp` has no
`agents/`, and ticket 12 already ruled that `handoff` does not become a skill."* Ticket 12 itself
(`issues/12-phase-boundary-policy.md:135-138`) explicitly **declines** to rule and hands it on.

**Still referenced after deletion**, 4 live sites in surviving-or-undecided skills:
`13_review-feature/SKILL.md:117` (a `MUST`: *"escalating to impl-quality-debug-handoff after two
failed fix attempts"*) · `:176` (the `EMIT next=` pointer) · `11_debug-self-verify/SKILL.md:80`
(*"The user wants to **escalate** … → use `impl-quality/debug-handoff`"*) · `:~290`, inside the
**Failure Exit Conditions** section of the protocol schema `validator.py` enforces.

`review-feature` survives on two flows. Its needs_changes path currently terminates in a deleted skill.

### The `standards-*` cycle

`_concept/_standards/index.yml` is written by **`standards-discover`** (`08:99,149`) and by
**`standards-sync`** in the `profile_to_project` direction (`10:102`). It is read by
`standards-inject` (`09:47`), `standards-sync` (`10:87`), and — the only reader outside the
trio — **`eval-code`** (`02:45,68`, soft). `review-feature` cites the *folder* as a
counter-authority for style nits (`13:122`) but does not read the index.

`standards-inject`'s five workflow steps (`09:64-70`) are the five steps of
`contracts/agent_patterns.md:96-104` **§ Pattern: Standards Injection**, in the same order,
including the "no error if no standards exist" clause. Ticket 09 kept `agent_patterns.md`
(9 in-body readers). Nothing else in the collection invokes `standards-inject` by name except
`contracts/asset_frontmatter.md:338`'s `inject_skill:` key — and ticket 09 **deleted**
`asset_frontmatter.md` (0 in-body readers).

Ticket 08's tree has a home: `-mp contracts/concept_structure.md:41-43` —
`02_grounding/standards/{index.yml, <domain>/}`. So the artifact survives ADR 0007 unchanged;
what has no declared home is `_debug/` and `testing/`.

### The three inspection outputs (ticket 08 → 17)

Ticket 08 (`issues/08-concept-side-consolidation.md:153-155`) hands 17 the placement of
`quality.yaml`, `eval-concept.yaml`, `testing/test_plan.md` under `11_build/`.
**`11_build/` in the landed tree holds only `slices/<slice_id>/` and `decisions.md`**
(`-mp contracts/concept_structure.md:80-82`) — none of the three has an entry yet.

| path | writer | readers |
|---|---|---|
| `_concept/quality.yaml` | **`ops-review`** — `14_ops/08_review/SKILL.md:121,214`, enforced by `14_ops/08_review/validator.py:34` (`v.must("write _concept/quality.yaml after every run")`) | `00_skaileup-orchestrator/skills/skaileup/SKILL.md:344`; `.../agents/skaileup-conceptualize/SOUL.md:64`; `14_ops/08_review/SKILL.md:99,117` (previous score) |
| `_concept/eval-concept.yaml` | **`ops-eval-concept`** — `14_ops/05_eval-concept/SKILL.md:88,163`, enforced by `14_ops/05_eval-concept/validator.py:14` | `00_skaileup-orchestrator/skills/skaileup/SKILL.md:38,102,294,297`; `.../skaileup-build/SKILL.md:39,109` — a **hard gate**: *"concept must pass eval-concept"* |
| `_concept/testing/test_plan.md` | `impl-quality-test-plan` (`01:229`) | `04_test-unit/SKILL.md:40,98` (Optional) · `05_test-integration/SKILL.md:47,107` (Optional) |

Bearing on "does the placement break anyone":
- **Two of the three are written by `ops` skills**, not `quality` skills — ticket 21's domain.
- Both non-`test-plan` readers are the **orchestrator** (`00_skaileup-orchestrator`), whose port is
  still in the map's "Not yet specified" fog (the router).
- `13_impl-quality/contracts/evaluate-contract/CONTRACT.md` names two of the three at **different
  paths**: `_quality/quality.yaml` + `_quality/audit-report.md` (`:21`) and
  `_concept/4_testing/test_plan.md` (`:24`) — neither matches the writers.
- `_implementation/eval-code.yaml` and `_implementation/review/<slug>.yaml` are *also* "findings
  about work" but were **not** in ticket 08's list of three.

### Overlaps

**`code-review` (global, `~/.claude/skills/code-review/SKILL.md`)** — two axes, both against a
**diff from a user-supplied fixed point**: *"**Standards**: does the code conform to this repo's
documented coding standards? **Spec**: does the code faithfully implement the originating issue /
spec?"*, run as *"**parallel sub-agents** so they don't pollute each other's context"*. Standards
carries a fixed **12-smell Fowler baseline** with the rule *"**The repo overrides.**"* and
*"**Always a judgement call.**"*. No security axis, no UI/UX axis, no artifact written.

**`audit`** — *"ROLE Static Code Auditor — analyzes codebase **without running it**"* (`:80`);
whole-repo, no diff, no fixed point: *"STEP 1: Verify source exists"* then three sub-agents
**Logic & Runtime / UI-UX & Accessibility / Security & Data Integrity** (`:114-119`), then
Phase 2 `_concept/` structure integrity, then **Phase 4: Offer Fixes** — *"Would you like me to
fix any of these issues?"* (`:164-170`). The only one of the four that **edits code**.

**`eval-code`** — *"Build verification **always runs first** — if it fails, stop immediately"*
(`:56-57`); the analysis is optional tail: *"Sub-agent analysis only runs for `full` scope"*.
Its verdict is a **gate**: *"pass: build clean AND tests pass AND no critical/high findings"*
(`:123`). Its three sub-agents are explicitly **not its own**: *"Same auditor trio as
impl-quality-audit — checklists owned there"* (`:109`, pointing at
`03_audit/references/analysis_checklists.md`, 64 lines).

**`review-feature`** — scope is **one feature's back-links**: *"MUST scope the review to
`commits[]` diffs + `source_files[]` contents; files outside that set get at most a one-line
boundary note, never findings"* (`:111`). Two axes none of the others has: *"MUST cross-check the
`.ac.md` … any criterion with Status pass whose assertion the code visibly cannot satisfy is a
finding"* (`:113`) and *"NEVER review as the same agent/context that implemented the slice"*
(`:119`). Runs *"all three check passes from `analysis_checklists.md`"* (`:112`) — **the same
64-line file `audit` and `eval-code` use**.

So: **three skills share one checklist file**; the distinguishing axes are scope (repo /
build+repo / one feature's diff), whether a fixed point exists (`code-review`, `review-feature`),
whether an artifact is written (`eval-code` + `review-feature` always, `audit` opt-in,
`code-review` never), and whether it may edit (`audit` only). `review-feature:68-71` already draws
three of these lines itself.

### Stack-specific boilerplate in the test trio

Measured on body lines (after frontmatter):

| skill | body | fenced lines | what the fences are |
|---|---|---|---|
| `test-unit` | 196 | 47 (**24%**) — 22 `typescript`, 25 plain | one vitest/Vue template (`:138-159`, *"// Example for vitest + Vue/Nuxt"*) + a report table mock (`:197-221`) |
| `test-integration` | 260 | 105 (**40%**) — 67 `typescript`, 38 plain | `beforeAll/afterEach/afterAll` DB setup (`:157-172`), an `asUser(role)` auth helper (`:175-181`), an endpoint-inventory table mock (`:127-134`) |
| `test-e2e` | 195 | **0** | none — but the whole STEP block is `agent-browser` CLI invocations (`:171,193,195,206`) and a `hard: agent-browser` gate (`:145`) with a platform check *"agent-browser only supports Linux, WSL, and macOS"* (`:167`) |

Non-fence coupling: `test-unit:109-118` enumerates runners/configs, ending *"Recommend adding
vitest (for Nuxt/Vue) or jest"*; its stack-neutral core is the two tables at `:173-187`
(**What to Test** / **What NOT to Test** — the actual pyramid instruction). `test-integration`'s
neutral core is Phase 1's endpoint inventory + the "test database strategy" three-way choice
(`:141-145`). Rough split: unit ≈ 25% boilerplate, integration ≈ 40%, e2e 0% fenced but ~100%
coupled to one binary.

### Open questions for the human

1. **`standards-sync` is the domain's only skill with zero flows and zero callers — and it reads a
   file that does not exist** (`cf__shared/profiles.json`, `10:72,88`). Does anything justify
   porting it, or is the profile↔project sync a feature that was never wired?
2. **`standards-inject` restates `agent_patterns.md:96-104` step for step.** Ticket 09 kept that
   contract. Its only non-flow reference is a key in `asset_frontmatter.md`, which ticket 09
   deleted. If it is a contract section rather than a skill, what happens to its
   `skaileup-concept-reverse:113` flow node — deleted, or replaced by discover-only?
3. **`test-plan` writes the only artifact two flow-mounted skills read, and is on no flow.** Is
   the plan a real artifact or a step inside the test skills? If it stays, ticket 08's `11_build/`
   has no `testing/` entry yet — and `test-plan` reads *and* writes `_concept/` only, which puts a
   `quality`-named skill entirely on the `ops` side of ticket 04's line.
4. **`audit` Phase 2 is `ops-review`.** `audit:52` sends the user to `review` for exactly the work
   `audit:127-131` then performs. Does `audit` lose Phase 2 (making it clean `quality`), or does
   ticket 21 lose it from `ops-review`?
5. **`ready` reads nothing but `_concept/` and writes nothing.** Is it a `quality` skill at all, an
   `ops` skill (ticket 21), or a gate expression inside a flow? Note the flow disagrees with the
   skill about *when* it runs: the skill says *"Use **before** E2E testing"* (`07_ready:66`) but
   `quality-gate.flow.yaml:73-82` places `q-ready` **after** `q-test-e2e`, labelled *"Release Ready"*.
6. **`review-feature`'s `needs_changes` branch terminates in a deleted skill** (`:117,176`) and
   `debug-self-verify`'s own failure-exit schema does too. If `debug-self-verify` also goes, what
   does `review-feature` emit — `diagnosing-bugs` by name, nothing, or a flow edge?
7. **`_debug/<id>/` has no entry in ADR 0007's eleven-folder tree.** Any surviving debug skill needs
   a home or a different artifact. Is a per-bug workspace a twelfth top-level folder, a subfolder of
   `11_build/`, or not an artifact at all?
8. **Ticket 08 handed 17 three paths, two of which `ops` writes** (`ops-review` → `quality.yaml`,
   `ops-eval-concept` → `eval-concept.yaml`) and whose only readers are the **orchestrator**, whose
   port is unspecified. Does 17 rule on artifacts it does not own, or hand two of them to 21?
   And why are `_implementation/eval-code.yaml` and `_implementation/review/<slug>.yaml` — same
   "findings about work" argument — not in the list?
9. **Three skills share one 64-line checklist file** (`03_audit/references/analysis_checklists.md`)
   and a 69-line `contracts/evaluator.md` stance. If `audit`/`eval-code`/`review-feature` merge,
   does the checklist become `references/` of the survivor, or a contract? If they do not merge,
   what stops the survivor set from being `code-review` + a scope parameter?
10. **`test-e2e` inspects a *running app*, not `src/` or `_concept/`.** Ticket 04's two-way line
    does not have a slot for it. Does the line need a third case, or is "the running app" `src/`?
11. **`test-unit`/`test-integration` are 25%/40% stack boilerplate for one stack (vitest + Vue/Nuxt +
    a JS ORM), while `impl-architecture/templates/template-*` already carry stack facts.** If they
    become one skill with a level parameter, where do the vitest snippets live — `references/<level>/`,
    the templates, or nowhere?
12. **Dead pointers found while reading** — do these have to be resolved here or by ticket 16?
    `test-unit:69` and `test-plan:81` route to a skill named **`verify`** that does not exist
    (`grep '^name:.*verify'` finds only `debug-self-verify`); `standards-discover:78` reads
    `_concept/05_techstack/stack.md` (real path `_concept/blueprint/techstack.md`);
    `test-plan:112,119` reads `experience/behaviors/*.allium`, and ticket 08 killed `.allium`;
    `ready`'s `produces: impl-readiness` names an artifact the body never writes.
