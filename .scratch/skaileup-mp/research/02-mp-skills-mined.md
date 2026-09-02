# 02 — Mining the remaining mattpocock skills

**Ticket:** `.scratch/skaileup-mp/issues/02-mine-remaining-mp-skills.md`
**Map:** `.scratch/skaileup-mp/map.md`
**Branch:** `research/mp-skills-mined` (throwaway, not merged, not pushed)
**Date:** 2026-09-02

## Sources

Primary sources are the installed skills at `/Users/matthias/.agents/skills/` — every
`SKILL.md` and every sibling reference file was read in full. Nothing was truncated, so
upstream `github.com/mattpocock/skills` was not fetched. Contrast skills read from
`/Users/matthias/devBench/SKAILEdev/ai-assets/ai-assets-skaileup/skaileup/`.

`herdr/` and `caveman/` under `~/.agents/skills/` are third-party installs, not part of
the mattpocock collection, and are excluded from every count below.

**The collection, measured.** 25 skills, 25 `SKILL.md` files totalling **1,599 lines**,
plus 22 sibling reference files totalling **1,346 lines** — **2,945 lines in all**.
Mean `SKILL.md` = **64 lines**; median = **71**; **max = 140** (`teach/SKILL.md`).
`skaileup` for comparison: **95 `SKILL.md` files, 25,075 lines**, mean **264 lines**,
max **1,248** (`skaileup/05_mockup-walkthrough/01_d_lit/SKILL.md`).

Per-file line counts (`SKILL.md` unless noted):

| skill | lines | siblings |
|---|---|---|
| `grill-me` · `grill-with-docs` · `wait-what` | 7 each | — |
| `research` | 12 | — |
| `resolving-merge-conflicts` | 14 | — |
| `implement` | 15 | — |
| `handoff` | 16 | — |
| `prototype` | 26 | `LOGIC.md` 67 · `UI.md` 112 |
| `grilling` | 28 | — |
| `tdd` | 38 | `tests.md` 77 · `mocking.md` 59 |
| `wizard` | 44 | `template.sh` 204 |
| `to-questionnaire` | 54 | — |
| `improve-codebase-architecture` | 71 | `HTML-REPORT.md` 123 |
| `domain-modeling` | 74 | `CONTEXT-FORMAT.md` 60 · `ADR-FORMAT.md` 47 |
| `to-spec` | 75 | — |
| `writing-for-agents` | 81 | `SKILL-MECHANICS.md` 22 |
| `code-review` | 87 | — |
| `ask-matt` | 90 | `PHASE-BOUNDARIES.md` 55 |
| `to-tickets` | 105 | — |
| `triage` | 112 | `AGENT-BRIEF.md` 207 · `OUT-OF-SCOPE.md` 105 |
| `codebase-design` | 114 | `DEEPENING.md` 37 · `DESIGN-IT-TWICE.md` 44 |
| `setup-matt-pocock-skills` | 116 | 4 templates, 142 total |
| `wayfinder` | 128 | — |
| `diagnosing-bugs` | 138 | `scripts/hitl-loop.template.sh` 44 |
| `teach` | 140 | 4 format files, 144 total |

---

## Part A — Verdicts

Excluded per the ticket (already slated for absorption): `grilling`, `to-spec`,
`to-tickets`, `research`, and an `ask-matt`-style router. Their dependencies are noted in
§A.1 because they constrain what else must exist.

| skill | verdict | lands in / why |
|---|---|---|
| **`ask-matt/PHASE-BOUNDARIES.md`** | **ABSORB** | Highest-value structural find. `skaileup` hardcodes one of the tree's five answers. → slice-loop contract + orchestrator SOULs |
| **`handoff`** | **ABSORB** | Two rules `skaileup`'s dossiers violate: no duplication, and name the next skills. → `contracts/slice_loop.md` + a portable `-mp` handoff |
| **`triage`** | **ABSORB** | No on-ramp exists for work you didn't create; no memory of rejected scope. → `14_ops` |
| **`wait-what`** | **ABSORB** | 7 lines; no in-conversation corrective exists anywhere in `skaileup`. → meta/global |
| **`to-questionnaire`** | **ABSORB** | Every discovery skill assumes the user holds the answers. → `01_concept` |
| **`writing-for-agents`** | **ABSORB** | The authoring standard for the rewrite (map premise 4). → replaces `CONTRIBUTING.md` + `contracts/skill_grammar.md` |
| **`implement`** | **ABSORB (pattern)** | 15 lines that compose two skills instead of restating them. The template for 16 slice skills → 6 |
| **`grill-me` / `grill-with-docs`** | **ABSORB (pattern)** | 7-line wrappers over a primitive. The mechanism that collapses `skaileup`'s four grill-shaped skills |
| **`setup-matt-pocock-skills`** | **ABSORB (pattern)** | Explore → present → confirm → write, skipping settled sections. → `skaileup-scope-scope-project` |
| **`domain-modeling`** | **ALREADY ABSORBED** | `skaileup/contracts/domain_model.md` (141 lines) is already a faithful port. Verify, don't redo |
| **`diagnosing-bugs`** | **ABSORB (Phase 1) + REFERENCE (skill)** | `skaileup`'s debug pair does the exact thing this skill forbids. → `13_impl-quality` |
| **`codebase-design`** | **REFERENCE + ABSORB (form)** | Domain-neutral (map premise 6), but it is the template for "common domain vocabulary" |
| **`tdd`** | **REFERENCE** | Named in map premise 6. `-mp`'s implement skill calls it by name |
| **`code-review`** | **REFERENCE** | Named in map premise 6. Note the deliberate divergence in §B.6 |
| **`prototype`** | **REFERENCE** | Named in map premise 6. One idea worth borrowing (§B.9) |
| **`wizard`** | **REFERENCE** | Artifact is a bash script, nothing to do with `_concept/`. `impl-build-*` should call it by name |
| **`resolving-merge-conflicts`** | **REFERENCE** | `skaileup` has nothing here; `impl-slice-git-finish` should call it by name |
| **`improve-codebase-architecture`** | **REFERENCE (borrow the loop)** | Surveys code, not `_concept/`. Its survey→pick→grill loop belongs in `ops-review` |
| **`wayfinder`** | **REFERENCE** | The tool building `-mp`, not part of the shipped build skillset. Four ideas worth stealing (§B.10) |
| **`teach`** | **SKIP (steal one rule)** | Learning workspace, no fit. Its `./assets/` reuse rule is the fix for 4,540 duplicated mockup lines |

Tally: **9 ABSORB · 1 already-absorbed · 8 REFERENCE · 1 SKIP · 1 split verdict.**

### A.1 — What the five slated skills depend on

Documented only so the absorption tickets don't strand a dependency.

- `grilling` (`grilling/SKILL.md`) depends on nothing. It is the primitive; `grill-me`,
  `grill-with-docs`, `triage` step 4, `wayfinder` steps 1–3, and
  `improve-codebase-architecture` step 3 all call it via the Skill tool.
- `grill-with-docs` calls `grilling` **and** `domain-modeling` — so absorbing `grilling`
  without `domain_model.md` present loses the stateful half.
- `to-spec` (`to-spec/SKILL.md` lines 1–20) requires the issue-tracker + triage-label
  config that `setup-matt-pocock-skills` writes, and explicitly says so ("If not, tell the
  user to run `/setup-matt-pocock-skills`"). `to-tickets` and `code-review` carry the same
  clause. **Three of the five slated skills therefore depend on a setup step `skaileup`
  does not have** — see the `setup-matt-pocock-skills` verdict.
- `to-spec` step 2 also depends on the **seam** vocabulary from `codebase-design`.
- `research` (`research/SKILL.md`, 12 lines) depends on nothing, and is invoked by
  `wayfinder`'s research ticket type.
- `ask-matt` depends on every skill it names, plus `PHASE-BOUNDARIES.md`.

---

## Part B — Structural ideas, in the ticket's priority order

### B.1 The phase-boundary decision tree — the single highest-value find

`ask-matt/PHASE-BOUNDARIES.md` (55 lines) is a five-question ordered tree over five
options — Continue, `/clear`, `/handoff`, Subagent, `/compact`. "Work top to bottom at
the boundary. The first **yes** wins."

1. Can you continue? Yes if the next phase needs this one as a **primary source**, or the
   smart zone (~150k) still fits it. "Continue costs nothing and loses nothing, so rule it
   out before anything else."
2. Is the context irrelevant to what comes next? → `/clear`.
3. Do you need portability (new harness / new directory / a colleague / a mid-phase fork)?
   → `/handoff`. "That list is the whole clause."
4. Can it run AFK? → subagent.
5. Otherwise `/compact` — "the **default, not the first reach**."

**The gap.** `skaileup` hardcodes answer 2 for every boundary in both slice loops:
`skaileup/contracts/slice_loop.md:63` — "`/clear` between every phase. A phase reads ONLY
its predecessor's handoff"; repeated at `skaileup/08_concept-slice/DOMAIN.md:39`,
`skaileup/11_impl-plan/DOMAIN.md:41`,
`skaileup/00_skaileup-orchestrator/skills/skaileup/SKILL.md:221`,
`skaileup/00_skaileup-orchestrator/skills/skaileup-build/SKILL.md:271`,
`skaileup/00_skaileup-orchestrator/agents/skaileup/SOUL.md:126`, and the two slice flow
docs. Seven sites, one answer.

By the tree's own worked example — "Grilling → implementation is the standard yes: the
implementation wants the reasoning verbatim, not a summary of it" — `skaileup`'s
`concept-slice-brainstorm → concept-slice-align` and `impl-plan-brainstorm →
impl-plan-align` hops are *precisely* the case where question 1 answers yes and clearing
is wrong. And the tree names the cost as one-way: "Clear a *relevant* context and you lose
the **why** behind what you built, and no amount of reading the diff back gets it
returned."

**Absorb as:** replace the blanket rule in `contracts/slice_loop.md` with the ordered tree,
and annotate each slice-loop edge with which branch it takes. Phase-boundary edges are
data the flow YAMLs could carry (a `boundary:` key on each edge), which keeps the machine
spine thin while making the judgement explicit. Also absorb the primary/secondary source
table verbatim — it is the reason for the ordering and 4 lines long.

### B.2 `handoff` as the inter-session bridge

`handoff/SKILL.md` is 16 lines including frontmatter. Four rules:

- Save to **the OS temp directory, not the workspace**.
- Include a **"suggested skills" section** naming which skills the next agent should call.
- "**Do not duplicate content already captured in other artifacts** (specs, plans, ADRs,
  issues, commits, diffs). Reference them by path or URL instead."
- Redact secrets. Tailor to the stated purpose of the next session (`argument-hint`).

**The gap is not the file — it is rules 2 and 3.** `skaileup` already has per-phase handoff
files (`_concept/slices/<id>/`, `_implementation/slices/<id>/`, keyed by
`contracts/slice_loop.md`'s "handoff frontmatter keys"), so the mechanism exists. What is
missing is the non-duplication rule: the dossier is "frozen, not deleted" and each phase
file is kept as permanent documentation alongside an `index.md`
(`CLAUDE.md` § Two-Group Architecture; `skaileup/08_concept-slice/DOMAIN.md:39`), which is
exactly the shape that invites each phase to restate its predecessor. Compare `wayfinder`'s
statement of the same rule: "The map is an **index**, not a store… a decision lives in
exactly one place, its ticket, so the map never restates it, only gists it and links"
(`wayfinder/SKILL.md`). Two mp skills independently state the single-source-of-truth rule
for handoff artifacts; `skaileup` states it nowhere.

Rule 2 — "suggested skills" — is the missing half of the router. A handoff that names the
next skills is what lets a fresh `-mp` session resume without the human re-routing.

**Absorb as:** (a) add both rules to `contracts/slice_loop.md`'s handoff frontmatter
contract; (b) a thin `-mp` handoff skill for the portable case (new harness / new directory
/ colleague) that writes to temp, not `_concept/` — because that case, per
`PHASE-BOUNDARIES.md` question 3, is the *only* thing `handoff` is for, and `skaileup`
conflates it with in-repo phase files.

### B.3 `triage` as an on-ramp for work you didn't create

`triage/SKILL.md` (112 lines) + `AGENT-BRIEF.md` (207) + `OUT-OF-SCOPE.md` (105).

The structural claim, stated in `ask-matt/SKILL.md`: "Triage is only for issues **you didn't
create**… Tickets that `/to-tickets` produced are already agent-ready, so **don't triage
them**." That single sentence separates the two on-ramps cleanly, and `skaileup` has no
equivalent distinction.

Three sub-ideas:

1. **A small state machine, not a checklist.** Two category roles (`bug`, `enhancement`) ×
   five state roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`,
   `wontfix`), with declared transitions and the invariant "every triaged issue should carry
   exactly one category role and one state role. If state roles conflict, flag it and ask."
2. **Verify before you grill** (step 3): reproduce the bug / run the PR's tests *before*
   any interview. "A confirmed verification makes a much stronger agent brief."
3. **`.out-of-scope/` as institutional memory.** One file per **concept**, not per issue;
   matching is "by concept similarity, not keyword"; written only when an *enhancement* is
   *rejected* — never when something is closed because it is already implemented, because
   that "would poison the dedup checks with false rejections."

**The gap.** `skaileup`'s only entry points assume you are starting or continuing your own
project (`skaileup-scope-scope-project`, `ops-add-feature`, `ops-reverse-engineer`). The
one triage-shaped thing that exists — `mockup-feedback-triage` — is deliberately narrow
("Deterministic — no LLM", routes stakeholder annotations to concept files). And rejected
scope has no memory: `concept-slice-scope-feature` forces an IN/OUT/DEFER decision per
feature, but that decision is frozen inside one slice dossier, so nothing stops the same
request arriving again as a fresh feature next quarter. `.out-of-scope/` is the missing
durable artifact.

**Absorb as:** a `skaileup-triage` in `14_ops` whose "issue tracker" is `_concept/` itself —
incoming requests route to features/screens/journeys — generalising
`mockup-feedback-triage` rather than replacing it, plus an out-of-scope KB registered in
`contracts/artifacts.yaml` as a durable artifact beside `decisions.md`.

**Also absorb `AGENT-BRIEF.md`'s durability rule**, which is broader than triage:

> "**Do** describe interfaces, types, and behavioral contracts… **Don't** reference file
> paths: they go stale. **Don't** reference line numbers."

`to-tickets` and `to-spec` both restate it ("avoid specific file paths or code snippets:
they go stale fast"), with one carefully-drawn exception — a prototype-derived snippet that
"encodes a decision more precisely than prose can (state machine, reducer, schema, type
shape)". This is the direct antidote to `skaileup`'s path-hardcoding habit (§D.3).

### B.4 `wait-what` as an in-conversation corrective

Whole skill, verbatim (`wait-what/SKILL.md`, 7 lines):

```
---
name: wait-what
description: "Stop. That last message did not land: re-pitch it."
disable-model-invocation: true
---

Wait, I don't understand where you've got to here. Re-pitch that: give me a little bit
of context, talk in ASD-STE100 Simplified Technical English, and use the ubiquitous
language from `CONTEXT.md` (follow `CONTEXT-MAP.md` to the right one if the repo has
more than one).
```

Three moves in one sentence: written in the **user's** voice so the human types it as an
interjection; names a real controlled-English standard (ASD-STE100) instead of "explain
simply"; and pins the re-explanation to the project glossary so the re-pitch does not
invent a third vocabulary.

**The gap.** `skaileup` has approval checkpoints ("MUST wait for explicit human approval
before handing off", `skaileup/01_concept/01_brief/SKILL.md`) but no corrective for a
message that failed to land. This matters *more* in `skaileup` than in mp, because
`skaileup`'s discovery skills interview non-technical stakeholders by design
(`concept-brief`, `concept-goals`, `design-brand-visual` — "Discovers aesthetic direction
through plain-language questions").

**Absorb as:** a 7-line `-mp` skill, identical, with `CONTEXT.md` swapped for
`_concept/blueprint/glossary.md` (`skaileup/contracts/domain_model.md:8`). This is the
cheapest absorb on the list.

### B.5 `writing-for-agents` as the authoring standard for the rewrite

81 + 22 lines. Map premise 4 says bodies are rewritten; this is the rulebook they get
rewritten against. It is also the only mp skill whose *subject* is the collection itself.

The vocabulary it establishes, each a **leading word** used as a token throughout:

- **Context pointer** — "a reference held in the agent's context that names some
  out-of-context material and encodes the condition for reaching it. A skill's description
  is one; a line in `AGENTS.md` naming a doc is the same object." Three pruning rules:
  front-load the leading word, one trigger per branch, cut identity the body already carries.
- **The two loads** — **context load** (always-loaded tokens) vs **cognitive load** (which
  documents exist and when to reach for each; "The human is the index"). Crucially:
  cognitive load is "not a cost to minimise: it is the price of human agency."
- **Information hierarchy** — a three-rung ladder: in-file step → in-file reference →
  disclosed reference. "**Progressive disclosure** is the move down the ladder." The test is
  branching: "inline what every branch needs, and push behind a pointer what only some
  branches reach."
- **Co-location** — "where the ladder decides *how far down* a piece sits, co-location
  decides *what sits beside it*." Distinguished explicitly from duplication: "that repeats
  one meaning in two places; scattering fragments one meaning across many."
- **Sprawl** — "a document simply too long, even when every line is live and unique."
- **Completion criteria** — two properties: **clarity** (can the agent tell done from
  not-done?) and **demand** (how much it requires). Names the failure — **premature
  completion** — and the fix order: "sharpen the bound first (local and cheap); only if it
  is irreducibly fuzzy *and* you observe the rush, hide the later steps."
- **When to split** — by sequence, or (skills only) by invocation.
- **Leading words** — "a compact concept already living in the model's pretraining that the
  agent thinks with while running the document… Repeated as a token, never as a sentence."
  With worked refactors: "fast, deterministic, low-overhead" → *tight*; "a loop you believe
  in" → *red*.
- **Negation** as the failure mode beside it: "steering by prohibition drags the forbidden
  behaviour into context and makes it *more* available… Prompt the **positive**."
- **Pruning** — single source of truth; the **environment** as a source of truth and a
  document that restates it as a **cache** ("Cache what the agent cannot find by looking");
  relevance; **sediment**; and **no-ops** ("an instruction the model already obeys by default
  pays load to say nothing… When a sentence fails, delete the whole sentence rather than trim
  words from it").

`SKILL-MECHANICS.md` (22 lines) carries the mechanical branch: model-invoked vs
user-invoked, and **router skills** — "When user-invoked skills multiply past what you can
remember, that piled-up cognitive load is cured by a **router skill**." That is the
justification for `ask-matt` and, transitively, for the `-mp` router.

**Absorb as:** the replacement for `CONTRIBUTING.md` and `contracts/skill_grammar.md`. Note
the direct conflict: `writing-for-agents` says prompt the positive and treat prohibition as
a last resort; `skaileup`'s grammar mandates a `MUST` / `NEVER` block (§C.4).

### B.6 How `implement` composes `tdd` + `code-review`

`implement/SKILL.md` is **15 lines** including frontmatter. Its body is six sentences:

> Implement the work described by the user in the spec or tickets. Use /tdd where possible,
> at pre-agreed seams. Run typechecking regularly, single test files regularly, and the full
> test suite once at the end. Once done, use /code-review to review the work. Commit your
> work to the current branch.

It states **zero** TDD rules and **zero** review rules. Those live once, in `tdd/SKILL.md`
(38 lines + `tests.md` 77 + `mocking.md` 59) and `code-review/SKILL.md` (87). `tdd` in turn
does the same trick one level down: rather than defining seams, it says "call the Skill tool
with 'codebase-design' for the vocabulary. It is the shared source of the module, interface,
depth, seam, adapter, leverage and locality terms, and **it is a reference to consult, not a
session to run**." Three skills, one definition each, composed at run time.

**The contrast is stark.** `skaileup/12_impl-slice` is **8 skills, 2,094 lines**;
`skaileup/12_impl-slice/02_implement/SKILL.md` alone is **384 lines** and inlines the TDD
loop ("writes failing tests first, implements with TDD Guard"), with `04_test`, `05_recap`,
`06_refactor` as separate skills. mp covers the same ground in `implement` (15) + `tdd` (38)
+ `code-review` (87) = **140 lines across 3 files**, a **15×** difference.

`grill-me` (7 lines: "Call the Skill tool with 'grilling'.") and `grill-with-docs` (7 lines:
"Call the Skill tool twice, for 'grilling' and 'domain-modeling'.") are the same pattern at
its purest: a *named entry point* is a two-line file, not a copy of the thing it names.
`skaileup` has four grill-shaped skills — `concept-slice-brainstorm`, `concept-slice-align`,
`impl-plan-brainstorm`, `impl-plan-align` — each restating the interview
(`08_concept-slice` = 944 lines, `11_impl-plan` = 1,128).

**Absorb as the mechanism for the 16 → 6 slice-cluster target** in map premise 7: one
grilling primitive, one implement composer, and thin named entry points where a distinct
trigger word earns one (per `SKILL-MECHANICS.md`'s "splitting by invocation").

**One deliberate divergence to keep.** `code-review` runs Standards and Spec as **parallel
sub-agents** and then refuses to merge them: "Do **not** merge or rerank findings… Don't pick
a single winner across axes: that's the reranking the separation exists to prevent."
`skaileup`'s `impl-plan-supervised` **sequences** the same two axes ("enforces
spec-compliance review before code-quality review"). Sequencing lets the first axis colour
the second — the exact contamination mp's parallelism prevents. Worth a decision ticket, not
a silent port.

### B.7 How `diagnosing-bugs` insists on a tight feedback loop before theorising

`diagnosing-bugs/SKILL.md` (138 lines) is six phases, and Phase 1 is the skill:

> "**This is the skill.** Everything else is mechanical. If you have a **tight** pass/fail
> signal for the bug (one that goes red on _this_ bug), you will find the cause; bisection,
> hypothesis-testing, and instrumentation all just consume it. If you don't have one, no
> amount of staring at code will save you."

Phase 1 lists **10 ways to construct a loop in preference order** (failing test → curl →
CLI+fixture diff → headless browser → replay a captured trace → throwaway harness →
property/fuzz → bisection harness → differential loop → HITL bash script), then a "Tighten
the loop" section that treats the loop as a product (faster / sharper signal / more
deterministic), then a hard gate:

> "**Completion criterion: a tight loop that goes red** … you can name **one command** …
> that you have **already run at least once** (show the invocation and its output,
> redacted)" — with four checkboxes: red-capable, deterministic, fast, agent-runnable.
> "If you catch yourself reading code to build a theory before this command exists,
> **stop** … **No red-capable command, no Phase 2.**"

Only in Phase 3 does hypothesising start, and then "**3–5 ranked hypotheses** before testing
any of them. Single-hypothesis generation anchors on the first plausible idea." Every
hypothesis must be falsifiable with a stated prediction; "If you cannot state the prediction,
the hypothesis is a vibe."

**The gap is precise and inverted.** `skaileup/13_impl-quality/11_debug-self-verify/SKILL.md`
(305 lines) STEP 1 *interviews for* a hypothesis — "Do you have a current hypothesis about
the cause? If yes, state it with confidence (low/medium/high)" — and STEP 3 branches the
whole protocol on it (`HYPOTHESIS-SPECIFIC` vs `HYPOTHESIS-AGNOSTIC`). It builds a
verification protocol *around* a hypothesis, which is the exact move `diagnosing-bugs`
refuses until a red loop exists. `12_debug-handoff` (314 lines) then packages that
hypothesis for a fresh chat. **619 lines** that never require a reproduction, against mp's
**138** that require nothing else first.

Two more transferable pieces: **tag every debug log with a unique prefix** (`[DEBUG-a4f2]`)
so "cleanup at the end becomes a single grep. Untagged logs survive; tagged logs die"; and
Phase 5's finding-of-last-resort — "**If no correct seam exists, that itself is the
finding** … The codebase architecture is preventing the bug from being locked down", which
is the documented hand-off edge to `improve-codebase-architecture` (`ask-matt/SKILL.md`).

**Absorb as:** Phase 1's ordered loop-construction list and its red-capable completion
criterion, as the gate in front of `-mp`'s debug skill. Keep the skill itself as a
REFERENCE install; absorb the discipline.

### B.8 `codebase-design`'s deep-module vocabulary

`codebase-design/SKILL.md` (114 lines) is what the map means by "a common domain vocabulary
borrowed from the mattpocock skills". Its shape is worth copying independently of its
content — four sections that a vocabulary skill needs and `skaileup` has nowhere:

1. **Glossary with anti-synonyms.** "Use these terms exactly: don't substitute 'component,'
   'service,' 'API,' or 'boundary.'" Seven terms — module, interface, implementation, depth,
   seam, adapter, leverage, locality — each with an explicit *`Avoid:`* line. **Module** is
   "deliberately scale-agnostic: a function, class, package, or tier-spanning slice."
   **Interface** is "everything a caller must know to use the module correctly: the type
   signature, but also invariants, ordering constraints, error modes, required
   configuration, and performance characteristics." **Seam** is credited to Michael Feathers.
2. **Principles as falsifiable tests**, not adjectives: "**The deletion test.** Imagine
   deleting the module. If complexity vanishes, it was a pass-through. If complexity
   reappears across N callers, it was earning its keep." "**One adapter means a hypothetical
   seam. Two adapters means a real one.**" "**The interface is the test surface.**"
3. **Relationships** — five lines stating how the terms compose ("A **Seam** is where a
   **Module**'s **Interface** lives").
4. **Rejected framings** — three entries naming what the vocabulary deliberately is *not*,
   including a rejection of Ousterhout's own definition ("depth as ratio of
   implementation-lines to interface-lines… rewards padding the implementation").

`DEEPENING.md` (37) adds the four dependency categories (in-process / local-substitutable /
remote-but-owned / true-external) that decide how a deepened module is tested, plus
"**replace, don't layer**: Old unit tests on shallow modules become waste once tests at the
deepened module's interface exist; delete them." `DESIGN-IT-TWICE.md` (44) is a parallel
sub-agent pattern: 3+ agents each given a *different design constraint* ("minimise the
interface" / "maximise flexibility" / "optimise for the most common caller" / "ports &
adapters"), then compared on depth, locality and seam placement, ending "Be opinionated: the
user wants a strong read, not a menu."

**Verdict nuance.** REFERENCE the skill (map premise 6 keeps domain-neutral skills global,
and `tdd` already reaches it by name). But **absorb the four-section form** — Glossary with
*Avoid:* lines, Principles as tests, Relationships, Rejected framings — as the template for
`-mp`'s own domain vocabularies. `skaileup` currently spreads its vocabulary across a
414-line `contracts/walkthrough_renderer.md`, a 141-line `domain_model.md`, and 95 skill
bodies that each re-introduce their own terms; none has a Rejected-framings section, which
is the part that actually stops drift.

`DESIGN-IT-TWICE`'s parallel-alternatives pattern has no `skaileup` analogue:
`impl-architecture-templates-select` *scores* seven pre-existing templates but never
designs alternatives.

### B.9 Smaller structural ideas worth naming

- **`prototype` as a kept primary source** (`prototype/SKILL.md` rule 6): "Throwaway is a
  constraint on how the code is written, not a promise to destroy it… commit it to a
  throwaway branch, **out of main**, and leave a context pointer to that branch on the
  implementation issue. The main branch keeps only the validated decision." `skaileup` has
  no out-of-main primary-source concept: its walkthrough mockups *are* prototypes but land
  permanently in `_concept/mockup-walkthrough/`. Worth a decision.
- **`to-questionnaire`'s inversion** (`to-questionnaire/SKILL.md`): "**Grill the send, not
  the subject.** Interview the user only about the _send_, which they can always answer:
  who it goes to, and what they need back. The questions in the document then target the
  **gap**." Every `skaileup` discovery skill assumes the user holds the answers; in an
  agency-shaped pipeline the answers frequently sit with a client or domain expert. Three
  steps, each with an explicit *Done when*.
- **`setup-matt-pocock-skills`'s interview shape**: "Lead each section with the recommended
  answer so the user can accept it in a word. Give a one-line explainer only when the choice
  genuinely branches; **skip the section entirely when exploration already settled it**."
  Three sections, each skippable by evidence. `skaileup-scope-scope-project` asks "2-3
  questions" but does not skip on evidence. It also writes its config into the *target*
  repo (`docs/agents/*.md` + an `## Agent skills` block in whichever of `CLAUDE.md` /
  `AGENTS.md` already exists — "Never create `AGENTS.md` when `CLAUDE.md` already exists").
- **`to-tickets`' wide-refactor exception**: vertical slicing is the rule, but "**Wide
  refactors are the exception**… sequence it as **expand–contract**", with each migrate
  batch its own ticket blocked by the expand, and a shared integration branch when even
  batches can't stay green. `skaileup/11_impl-plan/03_plan-vertical` (349 lines) carries an
  "anti-horizontal-nudge block" with no such escape hatch — a rule with a known
  counterexample and no exception is a rule agents will break silently.
- **`wizard`'s library/stages split**: `template.sh` (204 lines) is a fixed library the
  skill forbids editing — "The library above the `STAGES` marker is identical in every
  wizard; **that consistency is the point: never hand-edit it**" — and the 44-line skill
  authors only the stages. That is a clean statement of the code-vs-prompt boundary
  `skaileup`'s renderers lack (§D.2).

### B.10 `wayfinder` ideas worth stealing even though the skill stays global

- **"The map is an index, not a store."** A decision lives in exactly one place.
- **Fog of war, with a sharp test**: "The test is whether you can state the question
  precisely now, _not_ whether you can answer it now." Ticket when sharp, *Not yet specified*
  when not — "Don't pre-slice the fog into ticket-sized pieces."
- **Out of scope as a permanent map section**, distinct from fog: "Scope, not sharpness,
  lands it here… Out-of-scope work never graduates." Same idea as `triage`'s
  `.out-of-scope/`, at map level — two independent statements of an artifact `skaileup`
  lacks.
- **HITL vs AFK typing on every unit of work**: "A HITL ticket only resolves through that
  live exchange; the agent never stands in for the human's side of it (a grilling agent that
  answers its own questions has broken this)." `skaileup`'s flow YAMLs have no HITL/AFK
  axis; adding one to node metadata would be cheap and would state which nodes a headless
  runner may execute.
- **"Refer by name"**: "A wall of `#42, #43, #44` is illegible; names read at a glance."
  Directly applicable to `skaileup`'s `NN_`-prefixed everything.

---

## Part C — Authoring conventions to copy

### C.1 Line budget, measured

- Every mp `SKILL.md` fits in **140 lines or fewer**, frontmatter included. Mean **64**,
  median **71**.
- Sibling reference files run **22–207** lines. The single largest file in the whole
  collection is a *sibling* (`triage/AGENT-BRIEF.md`, 207), not a SKILL.md — reference
  material is where length is allowed to go.
- **Total collection: 2,945 lines / 25 skills.** `skaileup`: 25,075 lines / 95 skills, plus
  6,041 lines of contracts. `skaileup/05_mockup-walkthrough` alone (4,540 lines, 6 skills)
  is **1.5× the entire mattpocock collection**.

### C.2 What goes in the body, what goes in a sibling, what goes nowhere

The rule is stated in `writing-for-agents/SKILL.md` and observed consistently:

**Body:** the ordered steps, and reference every branch needs. `diagnosing-bugs` keeps all
six phases plus the 10-item loop list inline (138 lines) because every run walks them.
`code-review` keeps the 12 Fowler smells inline (87 lines) because "Often a legitimately
flat peer-set (every rule of a review on one rung), which is a fine arrangement, not a
smell."

**Sibling:** material only *some* branches reach. The clearest case is `prototype` (26
lines): the skill's entire body is a branch selector — "**'Does this logic / state model
feel right?'** → LOGIC.md … **'What should this look like?'** → UI.md" — plus six shared
rules. `LOGIC.md` (67) and `UI.md` (112) are never both loaded. Same in `codebase-design`
(114 body; `DEEPENING.md` and `DESIGN-IT-TWICE.md` reached only when deepening or exploring
alternatives), `triage` (112 body; the brief format and the KB format each fire on one
outcome), `tdd` (38 body; examples in `tests.md`, mocking in `mocking.md`), and
`setup-matt-pocock-skills` (116 body; four issue-tracker templates of which exactly one is
ever written).

**Nowhere:** the environment. "The **environment** is a source of truth too (`package.json`
scripts, config files, the directory layout, `--help` output), and a document that restates
it is a **cache**… Cache what the agent cannot find by looking… Leave the one-file,
one-command lookups to the environment, where they cannot go stale." No mp skill lists the
repo's file tree, its test command, or its config shape. `implement` says "Run typechecking
regularly" and lets the agent find how.

### C.3 Frontmatter minimalism, and `disable-model-invocation`

Across all 25 mp `SKILL.md` files, exactly **four keys** appear:

| key | occurrences |
|---|---|
| `name` | 25 |
| `description` | 25 |
| `disable-model-invocation` | 14 |
| `argument-hint` | 2 |

Frontmatter is **4–6 lines**. There is no `version`, no `stage`, no `tags`, no `metadata:`
block, no `artifacts:`, no `prerequisites:`, no `parameters:`, no `reads:`/`produces:`
manifest. Compare: `skaileup/01_concept/01_brief/SKILL.md` has **87 lines of frontmatter in
a 289-line file (30%)**; `skaileup/04_product-spec/01_features/SKILL.md` **74 / 329 (22%)**.
Map premise 3 already keeps `contracts/artifacts.yaml` as the machine spine — which means
the per-skill `artifacts:`/`prerequisites:` blocks are a **cache of the registry** in
`writing-for-agents`' sense, and can be deleted from bodies without losing the machine layer.

**`disable-model-invocation: true` marks a skill user-invoked.** 14 of 25 mp skills set it:
`ask-matt`, `grill-me`, `grill-with-docs`, `handoff`, `implement`,
`improve-codebase-architecture`, `setup-matt-pocock-skills`, `teach`, `to-questionnaire`,
`to-spec`, `to-tickets`, `triage`, `wait-what`, `wayfinder`. The 11 model-invoked ones are
exactly those another skill must reach or the agent must fire on its own: `grilling`,
`domain-modeling`, `codebase-design`, `tdd`, `code-review`, `prototype`, `research`,
`diagnosing-bugs`, `wizard`, `writing-for-agents`, `resolving-merge-conflicts`.

Per `SKILL-MECHANICS.md`, the trade is explicit: a description is "permanent context load in
exchange for discoverability", while `disable-model-invocation: true` costs "zero context
load, but it spends cognitive load: you are the index." The rule — "Pick model-invocation
only when the agent must reach the skill on its own, or another skill must" — is a directly
applicable filter for `-mp`. **All 95 `skaileup` skills are model-invoked**, so all 95
descriptions sit in context permanently; the flow YAMLs and orchestrator already route most
of them, meaning most of that load buys nothing.

Note the corollary that motivates the router: "Shared reference that two user-invoked skills
both need can live in neither: with no descriptions, neither can fire the other. Push it to
a plain file outside the skill system." That is the argument for `-mp`'s `contracts/` to
stay plain files rather than becoming skills.

### C.4 The voice: constraints without a MUST/NEVER DSL

**Measured: zero occurrences of uppercase `MUST`, `NEVER`, or `ALWAYS` across all 25 mp
`SKILL.md` files and all 22 sibling files — 2,945 lines, zero.** The only bolded imperatives
are lowercase and rare: `**must**` once in `triage/SKILL.md`, and five `**Do**` / `**Don't**`
pairs in `triage/AGENT-BRIEF.md`.

`skaileup` mandates the opposite: `contracts/skill_grammar.md` lists `MUST` / `NEVER` as DSL
keywords, and every skill carries a block —
`skaileup/05_mockup-walkthrough/01_c_astro/SKILL.md` has 9 MUSTs and 4 NEVERs, plus a
20-item CHECKLIST and three `EMIT` lines.

The five devices mp uses instead:

1. **Declarative statement of consequence.** "If you have a tight pass/fail signal… you will
   find the cause… If you don't have one, no amount of staring at code will save you."
   (`diagnosing-bugs`) — states the physics, not a prohibition.
2. **A named gate with a stop.** "If you catch yourself reading code to build a theory before
   this command exists, **stop**… No red-capable command, no Phase 2."
   (`diagnosing-bugs`) — one stop, placed at the one boundary that matters, rather than a
   block of nine.
3. **Checkbox completion criteria** where exhaustiveness is the point. Only three files use
   them: `diagnosing-bugs` (12), `triage/AGENT-BRIEF.md` (15), `to-tickets` (4). Against
   `skaileup`'s CHECKLIST-per-skill convention, checkboxes are the exception, not the format.
4. **"Done when" as an inline sentence.** `to-questionnaire`: "Done when you know who the
   recipient is and what they know that the user doesn't." `wizard`: "**Done when:** every
   stage traces to concrete instructions a stranger could follow." Three files use this.
5. **Positive restatement instead of prohibition**, which the skills practise and
   `writing-for-agents` names: "steering by prohibition drags the forbidden behaviour into
   context and makes it *more* available… Prompt the **positive**." Where mp does prohibit,
   it explains the cost in the same breath — `handoff`: "Do not duplicate content already
   captured in other artifacts… **Reference them by path or URL instead.**" Prohibition plus
   the positive target, in one sentence.

The register is also *conversational and second-person* — "You don't remember every skill,
so ask." (`ask-matt`), "Wait, I don't understand where you've got to here." (`wait-what`),
"Be aggressive. Be creative. Refuse to give up." (`diagnosing-bugs`) — which is what lets a
constraint land as a sentence rather than a table row.

**Direct conflict to resolve for `-mp`:** map premise 4 currently says "Prose ~80 lines + a
short `MUST`/`NEVER` block". `writing-for-agents` argues against the block. The evidence
here says drop it and keep the four devices above; if a hard guardrail is genuinely
unphraseable positively, `writing-for-agents` allows it — "even then, pair it with the
positive target."

### C.5 `ask-matt`: a multi-skill flow documented in prose, no YAML

`ask-matt/SKILL.md` is **90 lines** and documents the relationships among **23 skills** with
no graph, no YAML, no node ids. Its structure:

- **Six named regions** as `##` sections: *The main flow: idea → ship* · *On-ramps* ·
  *Codebase health* · *Vocabulary underneath* · *Phase boundaries* · *Standalone*, plus a
  one-line *Precondition*. The taxonomy itself is stated in the opening line — "A **flow**
  is a path through the skills. Most paths run along one **main flow**, and two **on-ramps**
  merge onto it. Everything else is standalone, or a vocabulary layer that runs underneath."
- **The main flow is 3 numbered steps**, and branches are written as prose questions:
  "**Branch: can you settle every question in conversation?**", "**Branch: is this a
  multi-session build?** — **Yes** → … **No** → …". Both arms of every branch are stated,
  which is precisely what a YAML `router` node encodes — in one line each.
- **Every skill entry states when to reach for it *and* when not to**, usually by contrast
  with its nearest neighbour: "`/grill-me` … Reach for it when you are **not working in a
  working directory**… If you are in a working directory, use `/grill-with-docs` instead: it
  runs the same interview and leaves a paper trail, so it is strictly the better one."
  Disambiguation between confusable skills is the router's main work, and prose does it in a
  clause where a graph cannot do it at all.
- **Composition is stated inline**: "`/implement` builds each issue by driving `/tdd`
  internally (one red-green slice at a time), then closes out by running `/code-review`."
- **Non-obvious negative edges get a sentence**: "Tickets that `/to-tickets` produced are
  already agent-ready, so **don't triage them**"; "Looping the map straight into
  `/implement` skips that collapse and throws the linked detail away."
- **A *Context hygiene* subsection** carries the constraint no graph can express: "Keep steps
  1–3 in **one unbroken context window** (don't compact or clear until after `/to-tickets`)."

**Could prose replace flow YAMLs for the human-facing case? Yes — and it already does in
`skaileup`.** Every flow directory already ships a `.md` beside its `.flow.yaml`
(`skaileup/flows/appbuilder-mvp/appbuilder-mvp.md` etc., per `CLAUDE.md` § Flows), and map
premise 3 keeps the YAMLs because *`forge-concept` reads them at runtime*. So the split is
already there: **YAML for the engine, prose for the human.** The finding is that `ask-matt`
proves one 90-line prose document can cover 23 skills' worth of routing — which means `-mp`
needs **one** router document, not one `.md` per flow. Two things prose carries that the
YAML cannot: the "reach for X not Y" disambiguation, and the context-hygiene constraint
spanning several nodes.

Concretely for `-mp`: keep `.flow.yaml` for the engine; replace the per-flow `.md` files
with a single `ask-skaileup`-style router at ~90–120 lines (more skills than mp, but the
same shape), and delete the flow prose docs it subsumes.

### C.6 What would directly shrink a 1,133-line skill

Against `skaileup/05_mockup-walkthrough/01_c_astro/SKILL.md` — 51 lines frontmatter, 1,082
body — in descending order of lines recovered:

| # | Move | mp source | ≈ lines |
|---|---|---|---|
| 1 | Move the 436 in-fence lines (7 verbatim file bodies: `package.json`, `astro.config.mjs`, `tailwind.config.mjs`, `Shell.astro`, `index.astro`, `[...slug].astro`, `[id].astro`, lines 598–981) into a real scaffold directory the skill copies | `wizard`'s `template.sh`: "never hand-edit it" | **≈436** |
| 2 | Delete the `## ROLE / READS / WRITES / REFERENCES` block (lines 314–354) — it restates `contracts/artifacts.yaml` and the frontmatter above it | "a document that restates [the environment] is a **cache**" | **≈41** |
| 3 | Delete the 20-item `## CHECKLIST` — `validator.py` already runs every item, and item 20 is literally "Validator exits 0" | same | **≈22** |
| 4 | Replace the 13-line `MUST`/`NEVER` block with 3–4 prose constraints stating the consequence | zero MUST/NEVER in 2,945 mp lines | **≈9** |
| 5 | Delete the three `EMIT` lines and the `## Overview` section that restates the `description` | "Cut identity the body already carries." | **≈15** |
| 6 | Fold `## Error handling` (lines 1063–1089, incl. a `warnings[].kind` enum) into `contracts/walkthrough_renderer.md`, which is already the shared contract | single source of truth | **≈27** |
| 7 | Push the `specs.json` shape (lines 185–313, 129 lines) to a sibling `SPECS-JSON.md` — only the generate branch reads it | `prototype`'s LOGIC/UI split | **≈129 out of body** |

Items 1–6 alone remove **≈550 lines** without losing a single instruction; item 7 moves
another 129 off the top rung. What remains is roughly **200 lines of actual steps** — still
above mp's 140 ceiling, which is the signal that the five renderers should collapse toward
the map's ~6-skill mockup target rather than each carrying its own scaffold.

---

## Part D — What inflates the skaileup skills

Habits, each with a measurement. Skills skimmed: `skaileup/01_concept/01_brief/SKILL.md`
(289), `skaileup/05_mockup-walkthrough/01_c_astro/SKILL.md` (1,133),
`skaileup/04_product-spec/01_features/SKILL.md` (329).

**D.1 — A fixed ~10-section template applied whether or not a section has content.**
Frequency across the 95 skills: `## Overview` 79 · `## When to Use` 63 · `## When NOT to
Use` 60 · `## Prerequisites` 50 · `## Common Mistakes` 55 · `## Context Budget` 39 · `##
Depth Behavior` 30 · `## Integration` 29 · `## Standalone Mode` 24. `concept-brief` and
`product-spec-features` carry an identical heading spine — *Overview · When to Use · When
NOT to Use · Prerequisites · Context Budget · Standalone Mode · Depth Behavior · Common
Mistakes · Research Mode · Integration*. `## Overview` in both restates the `description`
verbatim; `## When to Use` restates the description's trigger list. mp has no fixed spine:
`prototype` has 2 sections, `handoff` has none, `diagnosing-bugs` has 8 — each document's
headings come from its own content.

**D.2 — Verbatim file bodies inlined as prompt.** `01_c_astro/SKILL.md` carries **436 lines
inside code fences** (38% of the file), of which lines 598–981 are seven complete source
files the agent is told to write out. `wizard` solves the identical problem by shipping
`template.sh` as a file and forbidding edits above the marker. And this content is
duplicated: the five walkthrough renderers total **4,540 lines** for the same four inputs,
the same `data-spec-*` contract, and the same `manifest.json` schema — differing, per the
skill's own Overview, only in `renderer:` — while a **414-line** `contracts/walkthrough_renderer.md`
already exists to hold what they share. `teach`'s rule is the fix, stated for lessons:
"Reuse is the default, not the exception… never inline code a future lesson would duplicate."

**D.3 — Hardcoded paths in the body.** `01_c_astro`'s READS/WRITES block alone names ~30
literal paths, and the `MUST` block names `astro.config.mjs`, `tailwind.config.mjs`,
`specs.json` and `global.css` again. `triage/AGENT-BRIEF.md`, `to-tickets` and `to-spec` all
state the counter-rule ("**Don't** reference file paths: they go stale"), with a single
narrow exception for a decision-encoding snippet.

**D.4 — Frontmatter as a second copy of the registry.** 87 lines (30%) in `concept-brief`,
74 (22%) in `product-spec-features` — `artifacts:`, `prerequisites.inputs_optional:`,
`prerequisites.reads:`, `produces:`, `parameters:`, `tags:`, `version:`, `stage:`. The
`artifacts` ids duplicate `contracts/artifacts.yaml`; the `reads`/`produces` paths duplicate
`contracts/concept_structure.md`. mp uses four keys, 4–6 lines.

**D.5 — Three overlapping instruction registers in one file.** `01_c_astro` runs prose
Overview → a DSL `ROLE/READS/WRITES/REFERENCES` block → `STEP 1..8` → `MUST`/`NEVER` →
`CHECKLIST` → `EMIT`, with the same facts appearing in two or three of them (the astro
config constraints appear in the STEP 4 code fence, in the `MUST` block, and in the
CHECKLIST). Note the DSL is not even uniformly applied: only **4 of 95** skills carry a
`## MUST / NEVER` heading and only 4 a `## CHECKLIST`, so the grammar is a cost most skills
pay in `skill_grammar.md` and few actually use.

**D.6 — Restated boilerplate about the collection itself.** `## Context Budget` (39 skills),
`## Standalone Mode` (24), `## Depth Behavior` (30) and `## Integration` (29) describe how
the collection works, not what this skill does. In mp that material lives once, in
`ask-matt` and `PHASE-BOUNDARIES.md`, both of which the human reads and the skills do not
carry.

---

## Part E — Recommended follow-on tickets

1. **Phase-boundary tree replaces the blanket `/clear`** — rewrite `contracts/slice_loop.md`
   and annotate each slice-loop edge with its branch. Blocks the slice-cluster consolidation.
   (§B.1)
2. **Adopt `writing-for-agents` as the authoring contract**, retiring `skill_grammar.md` and
   `CONTRIBUTING.md`; settle the `MUST`/`NEVER` conflict with map premise 4 explicitly. Blocks
   every rewrite ticket. (§B.5, §C.4)
3. **The composition pattern** — one grilling primitive + one implement composer + thin named
   entry points, as the concrete mechanism for 16 slice skills → 6. (§B.6)
4. **Add the missing on-ramp**: `-mp` triage + an out-of-scope KB registered in
   `artifacts.yaml`. (§B.3)
5. **Three cheap absorbs** that need no design work: `wait-what` (7 lines), portable
   `handoff` (16), `to-questionnaire` (54). (§B.2, §B.4, §B.9)
6. **Debug gate**: put `diagnosing-bugs` Phase 1 in front of `-mp`'s debug skill; the current
   619-line pair inverts the discipline. (§B.7)
7. **One router, not one doc per flow** — a ~90–120 line `ask-skaileup` replacing the per-flow
   `.md` files, with `.flow.yaml` kept for the engine. (§C.5)
8. **Verify, don't rebuild, `domain_model.md`** — `domain-modeling` is already ported;
   confirm the glossary and ADR artifacts are actually written by the skills that claim to.
