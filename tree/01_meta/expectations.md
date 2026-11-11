---
path: _concept/01_meta/expectations.md
summary: what the user judges the result by and how they want to work with the agents
owner: [skaileup]
may_propose: []
---

# _concept/01_meta/expectations.md

What the user expects: the result they will judge the product by, and how they want to work with the agents that build it. `skaileup` writes it from one interview when a project has none; the lead applies `## Working together` to every run it sends (`tree/protocol/delegation.md § Delegation`), and `concept-brief` reads `## The result` when it writes the goals. Without it the lead guesses how much to ask: the user answers questions they wanted handled, or finds decisions made that they wanted to make.

## Format

```markdown
---
last_updated: YYYY-MM-DD
approved: YYYY-MM-DD
---

# Expectations

## The result

- **Judged by**: <what the user will judge the product by> (user, YYYY-MM-DD)
- **Quality bar**: <the bar a result has to clear> (user, YYYY-MM-DD)
- **Liked**: <a product, site or screen> — <what about it> (user, YYYY-MM-DD)
- **Disliked**: <a product, site or screen> — <what about it> (user, YYYY-MM-DD)
- **Must not happen**: <an outcome the user would reject the work for> (user, YYYY-MM-DD)

## Working together

| domain | autonomy | source |
|---|---|---|
| concept | user decides | user, YYYY-MM-DD |
| design | lead proposes, user confirms | default |
| architecture | lead proposes, user confirms | default |
| specs | user decides | default |
| build | agent decides and reports | default |
| review | agent decides and reports | default |

- **Review cadence**: per artifact | per stage | at the end (source)
- **Check-ins**: <the points where the lead stops and reports, whatever the cadence> (source)
- **Language**: <the language of the conversation and of the artifacts> (source)
```

`## The result` holds only what the user said: each line ends with its source, `(user, <date>)` or a file the user pointed at, and a kind the user gave nothing for is left out rather than filled in; `Liked`, `Disliked` and `Must not happen` may repeat. A line whose text came from a plan or another agent's document is sourced with that path, `(plan <path>)`, never `(user, …)`. `## Working together` has exactly the six domain rows, each with one autonomy value of `## Reading it`; a row the user left to the recommendation says `default`. The review cadence takes one of its three values.

## Reading it

The lead reads it before every run it sends; without agents, the session running `skaileup` does.

| autonomy | what the lead does with a decision batch from this domain |
|---|---|
| `user decides` | puts the batch to the user unchanged and waits for the answers |
| `lead proposes, user confirms` | puts the batch with its recommendations as one proposal; the user confirms it with one yes or names what to change |
| `agent decides and reports` | answers the batch with its recommendations and lists the choices in the completion summary (`tree/protocol/running.md § How a skill runs`, rule 8) |

`approved:` records the user's yes and nothing else (`tree/README.md § Frontmatter every markdown artifact carries`): an artifact written under `agent decides and reports` carries none until the user has seen it at the review cadence. The cadence says when the lead shows finished artifacts for approval inside a stage of the walk (`tree/01_meta/walkthrough.md`): after each artifact (`per artifact`), at the end of each stage (`per stage`), or once at the end of the walk (`at the end`); each stage's approval happens regardless of the cadence. A check-in is a point where the lead stops and reports even when the cadence would not. The user may change any line at any time; the lead rewrites it with the new source in the same turn.

## Writing it

1. **Resolve the facts, then ask** (`tree/protocol/running.md § How a skill runs`, rule 1). Read `_concept/brief.md` and `_concept/02_grounding/onboarding/answers.json` where they exist, and what the user has said in this session. When the file exists, show it and ask only what the user wants to change.
2. **Ask about the result** in one decision batch (rule 2): what they will judge the product by, the quality bar, references they like and dislike and what about each, and what must not happen. Recommend from the brief and the onboarding answers where they say something; otherwise ask the question open.
3. **Ask how to work together** in a second batch: the autonomy table as one question, recommended as in the format example; the review cadence, recommended `per stage`; the check-ins, recommended after the brief and goals and before the first build commit; the language, recommended as the one the user writes in. The batch offers "accept all defaults".
4. **A user who declines the interview** gets the recommended rows with source `default` and no `## The result` lines; the file is still written, so the lead has a cadence to apply and nothing about the result is invented. A line whose text came from a plan or another agent's document carries that path as its source, `(plan <path>)`, never `(user, …)`.
5. **Show the file, write it after the yes**, with `approved:`.

## Checks

- `## Working together` has the six domain rows, each with one autonomy value and a source; the review cadence is one of `per artifact`, `per stage`, `at the end`; check-ins and language are present.
- Every line of `## The result` ends with its source, and none came from anything but the user.
- `approved:` is present only after the user's yes.
