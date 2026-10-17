# 0012 — Five foreign skills, called one way; what came from pstack and Pocock

**Status:** accepted

## Context

The collection was read against two outside libraries, pstack (`cursor/plugins/pstack`
0.15.6) and Matt Pocock's `skills` (main @ `d81f3a1`); the comparison is
`/Users/matthias/devBench/agent-tests/skill-libraries-pstack-vs-mattpocock-2026-10.md`. It
showed the collection already is a Pocock-style pipeline: `build-plan` is `to-tickets`
adapted, `build-implement` leans on `tdd` and `code-review`, `spec-feature` runs `grilling`,
`skaileup` sends intake to `triage`, `quality-review` hands failures to `diagnosing-bugs`, and
`CONTEXT.md` plus this directory are the glossary and decision records Pocock keeps. Migration
premise 6 ("absorb, don't fork") is why those five stay foreign. The one file still in the old
style was `contracts/agent_patterns.md` (225 lines): bold prohibitions in capitals, an
`orchestrator` the glossary bans, and patterns for a `READS` block, `globals.verbosity`,
`modes.research` and `prog-expert-*` skills, none of which exist in this collection's hosts.

The dependency on the five foreign skills was declared nowhere, and calls to them were phrased
five different ways ("with `tdd`", "the global `grilling` skill", "the globally installed
`/triage`", …). Nothing distinguished a skill the model can call from one only the human can
run, and nothing in [`scripts/check.py`](../../scripts/check.py) could notice a misnamed or
missing one.

## Decision

**The five external skills stay global, and are listed once.** Vendoring them breaks premise 6
and the `domain-skill` naming (`tdd` has no domain). The list is `EXTERNAL_SKILLS` in
`scripts/check.py`; the axis is the upstream frontmatter, and hard or soft follows Pocock's
ADR 0001:

| skill | axis | dependency | without it |
|---|---|---|---|
| `tdd` | model | hard | `build-implement` stops and names it |
| `code-review` | model | hard | `build-implement` / `quality-review` stop and name it |
| `grilling` | model | soft | `spec-feature` runs the rounds itself |
| `diagnosing-bugs` | model | soft | `quality-review` hands the failure to the user |
| `triage` | user | soft | `skaileup` says intake was not triaged and goes on |

- **One phrasing, gate-enforced.** An operative call reads `Call the Skill tool with "<name>"`
  (`twice, for "<a>" and "<b>"` for two). A user-axis skill is an instruction to the human —
  `skaileup` tells the user to run `/triage`. `SKILL_TOOL_CALL_RE` fires on a name that is
  neither a collection skill nor in `EXTERNAL_SKILLS`, and on a Skill-tool call to a user-axis
  skill; `BARE_SLASH_SKILL_RE` fires on a bare `/name` for a collection or model-axis skill.
  Both are house rules (`rep.house`). The rule is written down in
  [`docs/skill-template.md`](../skill-template.md).
- **Section citations resolve.** `CONTRACT_SECTION_RE` checks every `` `contracts/<file> §
  <Section>` `` citation against a heading equal to it or to `Pattern: <Section>` — an
  intrinsic error, the same class as a missing contract file.
- **Steps are the todo list** (pstack). A new pattern in
  [`contracts/agent_patterns.md`](../../contracts/agent_patterns.md): the numbered steps become
  the first todo items verbatim, an inapplicable step stays as `skip: <reason>`, **Done when**
  is last.
- **Evidence label** (pstack), in two places only: `contracts/evaluator.md § Stance` (a finding
  is measured or inferred, or it is not a finding) and the Completion Summary pattern (a guess
  goes under its own `Unverified:` line). No label-to-severity mapping.
- **Design red flags** (both libraries) in
  [`skills/architecture-system/references/design-red-flags.md`](../../skills/architecture-system/references/design-red-flags.md),
  screened at step 4: shallow module, information leakage, temporal decomposition,
  pass-through, then design it twice. A single reader, so a reference, not a contract.
- **No principles layer.** pstack's 24 `principle-*` skills are build discipline this
  collection delegates to `tdd`/`code-review`; its own rules live in contracts and the gate,
  and 24 more directories would break the nine domains (ADR 0002).
- **README skill index.** [`README.md`](../../README.md) `## Skills` lists every skill; when
  that heading is present, `SKILLS_HEADING_RE` turns a missing skill into a house-rule error,
  read with the same `SKILL_PATH_RE` as the phantom-name check.

### Not adopted, and why

- Pocock plugin manifest / changesets — this collection ships via `skaile.yaml`; no host reads `version`.
- Pocock `handoff.md` session states — ADR 0005's warm/cold boundaries and `STATUS:` cover it.
- pstack `unslop` — no evidence of sloppy stakeholder artifacts, and no two step-readers.
- pstack `reflect` / Pocock `retro` — improving the collection from transcripts is a separate effort.
- pstack "never block on the human" — on the concept side the approval steps are the product.
- pstack `create-verification-skill` — `quality-e2e` / `quality-release` already drive the real app.
- pstack router/playbook layer — the flow graph is the playbook (ADR 0010); `skaileup` answers once.
- pstack multi-model `arena` — model fan-out is a harness capability this collection does not assume.
- Rewriting `evaluator.md § Laws` out of its imperative form — a restyle with no behaviour change.

### What landed differently from the plan

- `SKILL_TOOL_CALL_RE` is matched over the body with line wraps folded to spaces, not the raw
  body, so a call wrapped across lines is still checked.
- `contracts/agent_patterns.md` dropped its `---` separators and shortened the worked
  example's **Why** line to fit 120 lines.
- The README `does` cells are short plain-words summaries, not first clauses of the
  descriptions, because every description opens with "Use when …".
- House-rule findings print with the same `ERROR` prefix as intrinsic ones; only the tier
  heading above them differs.

## Consequences

- A sixth external skill is an edit to `EXTERNAL_SKILLS` plus a row in the table above; a call
  to an unlisted one fails the gate.
- The phrasing rule is CI-enforced: a bare `/tdd` or a Skill-tool call to `triage` turns the
  run red, and renaming a contract heading leaves its `§` citations red until they follow.
- The principles-layer question is closed; reopening it means answering the naming and
  nine-domain objections above, not just the value of the rules.
- A skill added without a README row fails the gate.
