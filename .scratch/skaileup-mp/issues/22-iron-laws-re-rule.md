# 22: The iron laws describe a pipeline that no longer runs

**Type:** grilling
**Blocked by:** None (07, 08, 09, 19 resolved)
**Status:** resolved

## Question

Graduated from ticket 19, which hit the contradiction while writing `spec-feature` and did not
resolve it. Ticket 09 kept `contracts/iron_laws.md` (119 lines) on the argument that its gates
are **machine-enforced** — `requires`/`prerequisites` are the checks behind the prose, so it is
not the `MUST`/`NEVER` skill-body prose ticket 03 removed. That argument now has to be re-made
against what the collection actually became.

**Six of the nine laws are stale, and one is stale in a way that matters.**

### The substantive contradiction: laws 3 and 4 vs `spec-feature`

- **Law 3 (`:27-32`)** — `experience/screens/` requires `discovery/brand/tokens.json`, "unless
  the brand step was explicitly skipped by the user".
- **Law 4 (`:36-40`)** — `experience/screens/` requires `blueprint/datamodel/model.json`.
- **`spec-feature` (`skills/spec-feature/SKILL.md:9-10,17`)** declares `brand-tokens` and
  `datamodel` as **`gate: soft`**, and does not list `tokens.json` in `prerequisites.files` at all.

Ticket 08's W1 boundary put screen specs inside the per-feature loop, so `spec-feature` writes
`07_screens/` before `10_blueprint/` necessarily exists. Ticket 19 resolved that by demoting both
gates to soft — a ruling the contract still denies. **One of the two is wrong.** Either the laws
are amended to match the loop, or `spec-feature`'s gates are wrong and the port needs a fix.
This is the ticket's real question; the rest is bookkeeping.

### The bookkeeping: every path in laws 1–5 predates ADR 0007

| law | says | ADR 0007 |
|---|---|---|
| 1 | `discovery/brief.md` | `brief.md` (root file) |
| 2 | `blueprint/datamodel/`, `experience/features/` | `10_blueprint/datamodel/`, `05_features/` |
| 3 | `experience/screens/`, `discovery/brand/tokens.json` | `07_screens/`, `03_brand/tokens.json` |
| 4 | `experience/screens/`, `blueprint/datamodel/model.json` | `07_screens/`, `10_blueprint/datamodel/model.json` |
| 5 | `experience/screens/` | `07_screens/` |

**Law 5 also names a skill that does not exist** — "the `mock` skill". The mockup domain ported
as `mockup-walkthrough` / `mockup-storybook` (tickets 06, 14). **Law 6 names `ready`**, whose
survival is open in ticket 17 — so this ticket should not settle law 6 ahead of it.

### The reader question underneath

**`iron_laws.md` has zero in-body readers in `-mp`.** Its only mention is
`contracts/README.md:14,47`, which ticket 19 found stale wholesale. Ticket 09's bar was
in-body reads, and by that bar this file fails it — what carries the gates today is
`prerequisites.files[].gate` in each skill's frontmatter, read by
`workspaces/resolver/src/parser.ts:58-69`. So the file explains gates it does not enforce.

Decide:

- **Do laws 3 and 4 survive at all**, given the per-feature loop writes screens first? If they
  do, `spec-feature` is wrong. If they don't, what replaces "screens shouldn't be generic"?
- **Is a prose file explaining gates worth keeping** when the gates live in frontmatter and
  nothing reads the prose? Ticket 09 kept it as machine-enforced; that premise no longer holds
  in the form it was stated.
- **Laws 7, 8, 9 are not path-bound** (verify prerequisites · never overwrite without approval ·
  questions are standalone messages). They read as agent-behaviour rules, closer to
  `agent_patterns.md` (9 in-body readers) than to a gate contract. Do they belong there?
- Same for the **Rationalization Defense** and **Red Flags** tables (`:87-119`, 33 of the 119
  lines) — three of their rows name deleted skills or the pre-0007 tree.

Ticket 16 owns "every written path resolves to a real top-level entry" and will catch the table
above mechanically. **It cannot catch laws 3 and 4** — those are a live disagreement between two
things that both parse.

## Note from ticket 17

**Law 6 names `ready`, and `ready` does not survive the `quality` domain.** Ticket 17 rules
that it is an `ops` skill by ticket 04's line (it reads only `_concept/`, declares
`Never load: Source code`, and writes nothing) and hands merge-or-keep to ticket 21 — so law 6
may end up naming a skill that was folded into `ops-eval-concept`, or no skill at all.

This is the same failure ticket 19 found in laws 3 and 4: a law pinned to a pipeline position
rather than to a check. Note that `ready` is one of **four** things checking `_concept/`
cross-reference integrity today (with `ops-eval-concept`, `ops-review` and `audit` Phase 2,
the last of which 17 deletes), which makes "the law names a skill" the weaker half of the
problem — the stronger half is that the gate it names had three other implementations.

## Note from ticket 21

**Law 6's `ready` is settled, and the settlement makes the law's problem worse, not better.**
Ticket 17 ruled `ready` out of `quality` and handed merge-or-keep here via 21; **21 merged it into
`ops-review`**. So law 6 names a skill that does not exist under any domain — and the check it
names now has *one* implementation where it had four (`ready`, `ops-eval-concept`, `ops-review`,
`audit` Phase 2, the last three of which 17 and 21 deleted or merged). That is the stronger half
17 identified: the law was pinned to a skill name while the gate it describes had three other
implementations.

**A second file with the same defect, found while ruling `evaluator.md`.**
`contracts/evaluator.md:20-31` carries **six uppercase `MUST`/`NEVER` laws with no machine behind
them** — no validator, no frontmatter gate, nothing that fires. Ticket 09's carve-out from ticket
03's amendment was explicitly for `iron_laws` + `golden_principles` *as machine-enforced gates*;
these do not qualify, and one of them (*"NEVER run from the same agent/session that produced the
artifact"*) is a genuine guardrail that ticket 03 would want expressed as a named failure with a
check behind it. The file survives ticket 21 on three readers (`ops-review`, `quality-review`,
`quality-release`); the shape of its laws is yours, since it is the same question you are asking
of `iron_laws.md`.

---

## Resolution

**`contracts/iron_laws.md` is deleted. Recorded as ADR 0008 — "A gate lives at the step it
binds; no file collects gates."** ADR 0004's `iron_laws` clause is superseded in place.

### Laws 3 and 4 — neither side was wrong; the laws named the wrong step

The ticket framed this as laws-vs-`spec-feature`, one of which must be wrong. Neither is.
**Both dependencies survive; both moved downstream, and both are already gated where they
moved to.** A screen *spec* is prose plus an `elements:` block and consumes no tokens —
*rendering* consumes them, and `mockup-walkthrough:15` and `mockup-storybook:15` both hard-gate
`tokens.json` already. A screen spec becomes buildable at `build-plan`, which is where the data
model is gated (`:16`). So laws 3 and 4 were right about the dependency and wrong about which
step it binds — and re-cutting them writes down nothing that isn't already declared. That is
the argument that killed the file rather than amended it.

### Why the file goes rather than gets rewritten

Three findings, in order of weight.

1. **The collection's own vocabulary already forbids the genre.** `CONTEXT.md` defines
   **Gate** as *"a precondition on running a skill… Every gate is one or the other, **stated at
   the step it binds**."* A central register of gates is what that sentence rules out. This was
   settled at ticket 05 and nobody had applied it here.
2. **Ticket 09's machine-enforced premise fails twice over, not once.** The ticket had it half
   right — the prose does not enforce the gates. Neither does the frontmatter:
   `parseSkillRequirements` reads `fm.metadata ?? {}` with no root fallback
   (`resolver/src/parser.ts:45-46`, identical in the deployed `@skaile/workspaces@0.48.1`
   bundle) and **no `-mp` skill has a `metadata:` key**; separately, `validator.ts:81` joins
   against the *project* root and no `-mp` path carries the `_concept/` prefix. Ticket 19's
   demotion of two gates to soft changed nothing observable, because `spec-feature`'s two
   *hard* gates are equally unenforced. → **ticket 27**.
3. **The reader evidence is a completed experiment, not a mid-port count.** Zero in-body
   readers in `-mp`; and across the old collection's 95 skills over the file's whole life, the
   six path laws were cited **zero times** — every one of the 84 references named law 7, 8 or 9.
   The half that was cited is the half no `gate:` field can hold; the half `gate:` can express
   is the half nobody ever cited.

### Law by law

| law | disposition |
|---|---|
| 1 brief | already live — `spec-feature:15`, `build-branch:10` hard-gate `brief.md` |
| 2 features → datamodel | no writer in `-mp` → requirement on **25**'s datamodel writer |
| 3 tokens → screens | binds at **render**; already hard in both mockup skills |
| 4 datamodel → screens | binds at **plan** (`build-plan:16`); residue to **25** |
| 5 screens → mockups | already live twice with `min_entries: 1` — only `mock` was a phantom name |
| 6 readiness | second clause already satisfied by `build-plan:13-16` + `build-implement:13-15`; `ready` itself is **21**'s |
| 7 verify prerequisites | already `agent_patterns.md:8-20` |
| 8 no overwrite without approval | already at its steps — `spec-feature:78-79`, `mockup-feedback:19-21`, `build-implement:51-53` |
| 9 standalone questions | already `agent_patterns.md:48-68`, with the worked example |

**Correction to the brief:** it reports law 8 as needing a home because `agent_patterns:135`
covers input values only. It does not need one — all three writers state it at their step
already; the brief's line numbers for those sites are slightly off, the substance is right.

### Both tables die with the file

The Rationalization Defense is **the pre-ADR-0003 form of a `MUST`/`NEVER` block** — a
constraint stated centrally, away from its step, defended against a reader who was never given
a reason. Its one load-bearing row (spec compliance before quality review, `:98`/`:115`)
already lives at `build-implement:35-39`; `:97`/`:116` restate law 9 a third and fourth time;
`:94` points at a `prototype` **flow** that has never existed in this collection.

### The ruling is narrow, and the two other zero-reader contracts survive

`agent_patterns.md` and `golden_principles.md` both have **0 in-body readers in `-mp`** today —
so reader count alone was never the bar, or ADR 0004 keeps two files that fail it. The
distinguishing evidence is that `-mp` holds **8 of ~30 skills**: their readers are *unbuilt*,
where `iron_laws`' were a completed experiment. Both are **kept on notice**, using the
disposition `evaluator.md` already carries in `contracts/README.md` — a row naming the tickets
whose skills would read it, dying with them if they do not arrive. That pattern has paid off
once already: `evaluator.md` was kept on it and ticket 17 then found it four readers.

- **`agent_patterns.md`** → **26** (port the concept side). Five stale sites go with it: `:11` gates on
  flow-node `requires`, `:27` reads `user_inputs.dialog`, `:28` names
  `_grounding/{folder}/user_input.json` where the resolver reads `<skillId>/input.json`
  (`validator.ts:110`), `:179` is the 4-status protocol ticket 07 deleted, `:217` is a pre-0007
  techstack path.
- **`golden_principles.md`** → **25** (writes the datamodel) and **26** (writes `ops-review`). Ticket 16 routed this here and its evidence
  inverts the expected answer: `lint_concept.py` *was* the machine ADR 0004 meant, it is now
  deleted, and it **contradicted** the contract it supposedly enforced (`:13,23` fixes
  snake_case in the semantic layer; the linter demanded PascalCase against the *derived* PostXL
  schema, one of four formats per `concept_structure.md:183-187`). **The content is sound and
  the reader was wrong** — the inverse of `iron_laws`. Deleting 112 lines that ticket 16 just
  independently confirmed correct, on a reader count taken mid-port, would make ticket 25
  re-derive entity/field/enum conventions from scratch.

### What is removed without replacement

**Nothing in `-mp` says a screen spec written before the data model gets revisited when it
lands.** That is what law 4 actually protected. `build-plan:16`'s soft gate looks like the
meeting point and is not one: soft entries are excluded from `satisfied` (`validator.ts:149`),
never warned on, and the single route that would fetch the report
(`forge-concept/.../requirements.get.ts`) has **zero callers** — the UI panel labelled "Hard
gates" (`GateInfo.vue:37-43`) is fed by flow edges, not file gates. **A soft gate is not a
surface.** Handed to **25** as a named requirement on the datamodel writer, bundled with law 2;
until 25 lands the loss is real and unmitigated. This is the one thing this ticket takes away.

### Changes landed

`-mp`: `contracts/iron_laws.md` deleted · `docs/adr/0008-gates-live-at-the-step-they-bind.md`
added · `docs/adr/0004` gains a partial-supersession note (ticket 19's precedent with 0006 —
append, never edit the decision text) · `contracts/README.md` loses the `iron_laws` row and its
`golden_principles` row gains the kept-on-notice wording, which also makes its "Thirteen files"
sentence true. `scripts/check.py` green: 8 skills, 0 errors. Nothing in CI referenced the file.

Committed on `-mp` `main`, not pushed. Four files only — a ticket-18 and a ticket-21 session are
live in the same tree with uncommitted work.

### Handed off

- **27** (new): the frontmatter-shape repair — eight skills, `docs/skill-template.md`, and a
  `check.py` rule. **Blocked on ticket 16's ADR-0007 path sweep committing** — done in-tree,
  not yet committed — because fixing the
  nesting first turns four dead gates into live wrong ones (`mockup-storybook` would block on
  `discovery/brand/tokens.json`, which ADR 0007 abolished and nothing writes). Ticket 14 fixed
  this bug class once already and the tree moved underneath it.
- **25**: two requirements on the datamodel writer — a hard gate on `05_features` with
  `min_entries: 1` (law 2's machine form, exactly as `build-plan:13` states it), and the
  re-check of screen specs written before the datamodel (law 4's residue). Plus
  `golden_principles.md` on notice.
- **26** (port the concept side): `agent_patterns.md` on notice with its five stale sites, and
  `golden_principles.md`'s second candidate reader — ticket 21 put `ops-review` in this port.

### Questions this surfaced for other tickets

- **`docs/skill-template.md:13-17` is the origin of the frontmatter bug and states the opposite
  of the truth** — both blocks at the root of its fence, and *"`artifacts.requires[].id + gate`
  — hard gates the flow engine enforces"* when `requires-graph.ts:236-249` reads `id` only.
  Every skill written since inherited it. Folded into 27 rather than left as a doc nit.
- **`artifacts.requires[].gate` is decoration in both repos.** No code has ever read it. Whether
  it stays as documentation is 27's to settle.
- **Law 3's escape hatch has a machine form nothing declares** — `validator.ts:74-79` honours
  `overrides.skip_checks` from flow-node `data.overrides`, but `-mp` has no flows and
  `flow.schema.json` is deleted. Whether "unless brand was explicitly skipped" survives as a
  declarable thing is **ticket 10's**, once flows exist.
