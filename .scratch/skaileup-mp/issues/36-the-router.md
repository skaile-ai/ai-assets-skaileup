# 36: The router — the last absorbed skill with no body

**Type:** grilling
**Blocked by:** None — graduated from the map's fog 2026-09-06
**Status:** ready

## Question

Graduated from the **five absorbed skills' bodies** fog patch, which is down to one. Ticket 08
placed three (`research` and `to-questionnaire` became steps inside `concept-research` and
`concept-onboard`; `to-spec` became `spec-feature`), and **ticket 26 closed `grilling`** — it
turned out to be a global mp install, not a `-mp` asset. What is left is the **router**, named
`skaileup` by ticket 04 and never written.

Measured: `-mp` ships **29 skills and no router**. `concept-scope` — the closest candidate,
and the entry point of every flow — contains **no routing, triage or intake language at all**.

Two things want it, and they do not want the same thing:

- **Ticket 13's intake rule.** 13 refused a triage *skill* but kept the rule, and it has to
  live somewhere: for work the collection did not create, call the global `/triage`, then
  enter at `spec-feature` (a new or changed feature) or `build-plan` (a defect against built
  code). `CONTEXT.md` is glossary-only, so it cannot be there. It is currently written down
  **only in this map**.
- **An `ask-matt`-style front door** (premise 6) — "I have a thing to do, which skill?" for
  someone driving the collection outside a host.

And one thing makes it arguably redundant: **in forge-concept the flow choice is the host's,
not a skill's.** The user picks a profile in `OnboardingWizard.vue`, and the profile key *is*
the flow id (`profiles.get.ts`); `-mp` ships six `profiles/*.yaml`. A router that picks a flow
would be re-deciding what the host already asked. That leaves the router's real territory as
the **non-host** case and the **mid-project** case — someone already inside `_concept/` who
does not know which skill comes next.

So: **does `-mp` ship a `skaileup` router skill, and what is its job?**

1. **Yes, as an intake router** — carries ticket 13's rule and the entry points, for work
   arriving from outside a flow. Redundant inside forge-concept, load-bearing outside it.
2. **Yes, as a "what next" skill** — reads `_concept/01_meta/scope.yaml` and the tree, says
   which skill is next. Overlaps the flow graph, which already encodes exactly that.
3. **No skill; the rule lands in prose** — `README.md` or `contracts/`, and the collection
   keeps 29 skills.

Whichever wins, ticket 13's sentence stops living only in a wayfinder map.

## Answer

_(pending)_
