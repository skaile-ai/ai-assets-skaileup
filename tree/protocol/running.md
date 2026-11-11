# How a skill runs

## How a skill runs

Every skill binds these rules at its interviewing step by citing `tree/protocol/running.md § How a skill runs`; a node does not restate them.

**The route is the todo list.** On entry the route's numbered items become the first todo items, verbatim and in order; an item that does not apply stays listed as `skip: <reason>`, and **Done when** is the last item. Where the harness has no todo tool, the first message lists them and each later message names the item it is on.

1. **Resolve facts, then ask.** Read existing artifacts in any order, and an optional one only after checking it exists; `_concept/` outranks the conversation, so a disagreement between them is a question for the user. Read the decision records that bind the work before asking (`tree/10_blueprint/decisions.md § Levels`): a question a binding record answers is not asked. Run `concept-reverse` scoped for evidence the code holds; mark inferred facts; batch only what tools cannot settle. A `hard`-gated input that is missing stops the skill in one sentence naming the missing path and the skill that produces it.
2. **One decision batch per message.** At most 7 independently answerable questions on one topic; each with the recommendation first and a one-line consequence; an "accept all defaults" option; questions whose options depend on an unanswered one are deferred to the next batch; a status line precedes the batch. A technical term is explained in parentheses.
3. **Match the user's specificity.** Infer depth from the material supplied; where it matters, ask per artifact how deep to go (`sketch · standard · exhaustive`) and say what each depth produces; a user precise about roles and vague about layout gets precise role questions and a layout proposal.
4. **Sort before asking.** Restate the user's input as a coherent draft (terms, objects, screens, rules) with gaps marked, then ask about the gaps — never a questionnaire first.
5. **Show consequences before commitments** on data, feature and navigation choices: what the user sees, data and permission effects, affected artifacts, reversibility; for expensive choices compare genuinely different alternatives (design-it-twice).
6. **Show the layout when the choice is spatial.** A layout story with neutral placeholders (two floorplans on request, at the `narrow` and `wide` viewports) before the screen is specified.
7. **Record at the semantic home** when you own it, else as an entry of the run's proposal file targeting it (`tree/proposals/README.md`); open questions get stable ids.
8. **Completion summary.** Report the files written or modified with one line each, the key decisions, the cross-references established, then the next steps, named by demand: the skills that own what is still missing. Each claim says how it is known — **measured** (seen in a file, a command's output, the running app) or **inferred** (follows from something measured, and names it); a prediction or unseen cause is a guess and goes under its own `Unverified:` line. A check the agent could run is run, not handed to the user.
