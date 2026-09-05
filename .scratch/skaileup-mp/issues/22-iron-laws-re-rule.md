# 22: The iron laws describe a pipeline that no longer runs

**Type:** grilling
**Blocked by:** None (07, 08, 09, 19 resolved)
**Status:** in-progress

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
